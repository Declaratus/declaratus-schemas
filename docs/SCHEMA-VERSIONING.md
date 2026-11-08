# Schema versioning

The schemas in this repo evolve under a two-level versioning scheme. Consumer tools and chat projects pin to a specific version; this doc says how that works and when bumps happen.

## Two levels

**Directory prefix = major version.** `schemas/v0/` holds the entire v0 line. A v1 line ships under `schemas/v1/` when (and only when) backward-incompatible shape changes outpace what can be expressed via additive minor bumps. v0 and v1 coexist in the repo across the transition period.

**Document `schema_version` field = minor + patch.** Every document carries `schema_version: "0.1.2"` at its top level. Applier rejects documents whose `schema_version` falls outside the range the schema in `schemas/v0/` accepts.

The combination: tooling pinned to `v0.1.0` of this repo gets v0 shapes at the v0.1.0 maturity; pinned to `v0.2.0` gets the same shapes with additions; pinned to `v1.0.0` gets the next major.

## `$id` URLs are always tagged

```
https://raw.githubusercontent.com/Declaratus/declaratus-schemas/v0.1.0/schemas/v0/changeset.schema.json
```

Tagged ref (`v0.1.0`), not `main`. Two reasons:

- Chat projects attach schemas by URL. A `main`-pinned URL would shift under the chat without warning. Tagged refs let a chat session reproduce the same emission shape weeks later.
- CI in consumer tools fetches schemas during the congruence test. A tagged ref makes CI reproducible.

When you bump a schema, tag the repo (`git tag v0.2.0 && git push --tags`), then update consuming tools and chat projects to the new URL.

## Envelope policy (additive vs bump)

Derived from plynth's [dry-run JSON stability policy](https://github.com/Declaratus/plynth/blob/main/docs/dry-run-json.md); same rules for the same reasons.

**Additive change — minor bump, no major bump:**

- New optional property on an existing object.
- New value added to an open enum (e.g., a new `Color` would be additive only if Color were open; the current eight-value Color enum is closed, so adding a value IS breaking).
- New top-level optional block.

Consumers that ignore unknown keys keep working.

**Breaking change — major bump:**

- Renaming a property.
- Removing a property.
- Tightening a type (`string` → `string + enum`).
- Changing required-fields list.
- Changing the semantics of an existing property without renaming.

Bump the major (`schemas/v0/` → `schemas/v1/`) and keep v0 published until consumers migrate.

## What the version on a document means

`schema_version: "0.1.0"` on a changeset means: "I was authored against the v0.1.0 schema." The applier loads `schemas/v0/changeset.schema.json` from whatever version of this repo it has vendored, then checks the document's `schema_version` against the schema's accepted range.

Compatibility rule:

- A v0.1.0 schema accepts documents with `schema_version` in `[0.1.0, 0.2.0)` — same minor line.
- A v0.2.0 schema accepts documents with `schema_version` in `[0.1.0, 0.3.0)` — current and one prior minor, because additive changes are forward-compatible.
- A v1.0.0 schema accepts only `1.x.x` documents. v0 documents go through a migration shim (not yet specified — design when needed).

## v0.1.0 contract notes

These are clarifications of what v0.1.0 already publishes. They do not change
the schema, and `tests/test_changeset_contract.py` pins them.

- **`board.target`.** All five examples spell GitHub.com as `https://github.com`.
  Consumers should treat that spelling, the bare `github.com`, and
  `https://api.github.com` as the same host, and map them to their API roots
  themselves.
- **`Decision.resolution`.** When `state` is `resolved`, the schema requires the
  `resolution` key to be present as a string. An empty string is valid in v0.1.
  Consumers that check presence should not also require it to be non-empty.
- **`pattern` engines.** With default, non-multiline ECMA-262 regular
  expression semantics, `$` matches only at the end of the value. Python's
  `re`, used by the `jsonschema` package, also lets `$` match before one final
  newline. Python `jsonschema` therefore accepts `changeset_id: "demo\n"`,
  while the same pattern under default, non-multiline ECMA-262 regex semantics
  does not. Multiline mode changes the latter result; this is not a claim
  about every validator or an Ajv integration test. Authors should not end
  identifiers with a newline. Consumers using different validation and model
  engines should make their compatibility choice explicit. Other patterned
  fields and other engines are outside the parity established by these tests.

Requiring a non-empty `resolution` or universally rejecting previously accepted
trailing-newline identifiers would tighten acceptance. Under the breaking-change
policy, that requires a new major contract under `schemas/v1/`, with a new major
tag and `$id`. Keep v0 published unchanged and document migration explicitly;
neither a v0.1 patch nor an additive v0.2 release should silently tighten it.

## Consumer pinning

Each tool repo (`mendrik`, `eyrl`) pins a single version constant:

```python
# src/mendrik/schemas/__init__.py
DECLARATUS_SCHEMAS_VERSION = "0.1.0"
```

A unit test asserts:

1. The vendored `schemas/v0/changeset.schema.json` matches the version (hash check or `$id`-tag check).
2. The hand-written Pydantic model accepts every example in `examples/`.
3. The Pydantic model rejects a known-invalid fixture.

Pattern lifted from plynth's `DRY_RUN_JSON_SCHEMA_VERSION` + `test_api_call_estimate_keys_and_total`. Same logic, different schema family.

## Vendoring

Consumer tools vendor a copy of the schemas into `src/<tool>/schemas/` at the pinned version, rather than fetching at runtime. Reasons:

- Air-gapped applier runs work.
- A breaking change in this repo can't break a tool already published.
- Tool upgrade is a deliberate act (bump the constant, re-run the congruence test, ship).

The vendored copy is whatever was at the tag named by `DECLARATUS_SCHEMAS_VERSION`. Don't edit the vendored copy.

## What gets bumped together

The version applies to every schema file in `schemas/v0/`. If only the changeset schema changes, all schemas still tag at the new version. This keeps the URL pattern (`v0.X.Y/schemas/v0/<any-name>.schema.json`) coherent. Unchanged schemas in a release just retain their prior content.

## Lifecycle of v0

| Version | State | Notes |
|---|---|---|
| 0.0.1 | deprecated | Phase 0 stub; applier rejects. |
| 0.1.x | current | Designed in Phase A1 against three real change-doc shapes (per-issue body amendments, multi-wave reconciliation, tabular bulk backfill). |
| 0.2.x | planned | Will close the new_tasks creation gap (applier owns creation instead of delegating to plynth). |
| 1.0.0 | not planned | Open until a breaking change is forced. |

## When a major bump happens

If and when v1 is needed, the procedure:

1. Branch the schemas under `schemas/v1/` with the new shape.
2. Keep `schemas/v0/` published unchanged.
3. Tag the release `v1.0.0`.
4. Add a migration tool to `mendrik` that converts v0 documents to v1 documents (the migration shim).
5. Each consumer tool bumps its `DECLARATUS_SCHEMAS_VERSION` constant on its own timeline.
6. Sunset v0 at least two minor versions of `mendrik` later, never sooner.

No v0/v1 dual-publishing of the same document — pick a version per document and stick to it.
