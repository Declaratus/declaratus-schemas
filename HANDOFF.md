# Phase A1 handoff

Phase A1 shipped 2026-05-12. This file is read at the start of any session that picks up Phase A2 (or evolves v0.1 toward v0.2). Archived to `docs/handoffs/PHASE-A1.md` when Phase A2 starts in earnest.

## Shipped this phase

- `schemas/v0/changeset.schema.json` at v0.1.0. Draft 2020-12. Compiles under ajv.
- Five sanitized synthetic examples in `examples/`, covering every shape primitive.
- `docs/CHAT-USAGE.md` and `docs/SCHEMA-VERSIONING.md`.
- `v0.1.0` annotated tag, pushed.
- Repo flipped to public.
- Schema `$id` URL resolves: https://raw.githubusercontent.com/Declaratus/declaratus-schemas/v0.1.0/schemas/v0/changeset.schema.json

## What v0.1.0 covers

Top-level: `schema_version`, `platform`, `changeset_id` required. `source`, `board`, `summary`, `modifications`, `new_tasks`, `field_updates`, `field_options`, `decisions`, `pending_external_actions` optional.

Primitives that work end-to-end against the synthetic examples:

- `modifications.body` actions: `append`, `replace_line`, `replace_section`, `rewrite_section`.
- `field_updates`: flat `{issue, field, value}` bulk-table triples with optional `derivation_hint`.
- `field_options`: declarative full-desired-state, with a `migration` block for renames and a `requires_worksheet` flag for operator CSV handoff.
- `decisions`: controlled state enum (`open`, `lean-pursue`, `lean-defer`, `resolved`, `deferred`, `superseded`), with `if/then` enforcing `resolution` when state is `resolved`.
- `new_tasks`: full creation shape, accepted by the schema but emitted as `pending_external_action target=plynth-create` by the v0.1 applier.
- Cross-references: `decisions.affects` pairs with `modifications.decisions_resolved`.

## Open backlog for v0.2

Tracked as `v0.2-candidate` labeled issues. Read these in order if revisiting the schema:

- [#2 replace_line: substring vs anchored/regex variant](https://github.com/Declaratus/declaratus-schemas/issues/2)
- [#3 BodyMutation: applier behavior when target section doesn't exist](https://github.com/Declaratus/declaratus-schemas/issues/3)
- [#4 pending_external_actions.target: graduate free-form to registered enum](https://github.com/Declaratus/declaratus-schemas/issues/4)
- [#5 modifications.decisions_resolved: auto-transition Decision.state, or two operations?](https://github.com/Declaratus/declaratus-schemas/issues/5)
- [#6 NewTask.dependencies.external: split structured from prose, or keep free-form?](https://github.com/Declaratus/declaratus-schemas/issues/6)
- [#7 field_updates: nested-by-issue form when row count >= 300](https://github.com/Declaratus/declaratus-schemas/issues/7)
- [#8 Operator-prose field naming: note vs why vs context vs rationale](https://github.com/Declaratus/declaratus-schemas/issues/8)
- [#9 Modifications can't carry non-status field changes; split is awkward](https://github.com/Declaratus/declaratus-schemas/issues/9)
- [#10 Audit operator-prose fields: required vs optional vs lint-only](https://github.com/Declaratus/declaratus-schemas/issues/10)

Headline v0.2 capability is #5: mendrik owns issue creation directly, removing the plynth round-trip for `new_tasks`.

## Consumer impact

`mendrik` (private repo, stub) vendors from `schemas/v0/changeset.schema.json` at the v0.1.0 tag when Phase A2 starts. Vendoring rules and the `DECLARATUS_SCHEMAS_VERSION` pin pattern are documented in `docs/SCHEMA-VERSIONING.md`.

`eyrl` (private repo, stub) does not consume this schema directly; it consumes `inspection-report.schema.json` once that ships (not in v0.1).

## Next phase prereqs

Phase A2 needs:

1. mendrik repo populated past stub: CLI skeleton with `apply` and `validate` subcommands, GraphQL/REST clients copy-adapted from plynth.
2. Pydantic models hand-written from the v0.1.0 schema, with the congruence test asserting model-accepts-everything-schema-accepts.
3. Backend support for GitHub Projects v2 only; Linear is gated on plynth's Linear support (separate workstream).

The three private hand-translated fixtures (not in this repo) are the Phase A2 acceptance signal: mendrik apply runs them end-to-end against their respective boards.

## Handoff convention going forward

- HANDOFF.md at the repo root, written at phase exit.
- When the next phase starts, this file moves to `docs/handoffs/PHASE-A1.md` and the root file becomes the new phase's handoff.
- Open backlog items at phase exit go to GitHub Issues with a `vX.Y-candidate` label, not into the handoff doc body. The doc links the milestone view.
- The plan file at `~/.claude/plans/lets-package-all-this-twinkling-sprout.md` carries a "Position YYYY-MM-DD" line at the top, updated at each phase boundary.
