# Using these schemas from a Claude chat project

The schemas in `schemas/v0/` are designed for two consumers:

- **Deterministic tools** (`mendrik`, `eyrl`) validate documents with Pydantic `extra="forbid"`. Strict.
- **LLMs in chat** attach the JSON Schema as a project reference and read its `description` fields as soft prompts when emitting YAML.

This file is about the second case.

## Attach the schema

In a Claude project, add the changeset schema as a reference resource via its tagged raw URL:

```
https://raw.githubusercontent.com/Declaratus/declaratus-schemas/v0.1.0/schemas/v0/changeset.schema.json
```

Always pin to a tag (`v0.1.0`), never `main`. See [SCHEMA-VERSIONING.md](SCHEMA-VERSIONING.md) for why.

The same pattern works for the sibling schemas in this repo once they ship: `inspection-report.schema.json`, `portfolio-registry.schema.json`, `portfolio-rollup.schema.json`.

## Authoring flow

```
brainstorm in chat
  → narrative markdown (the human-readable change doc)
  → structured YAML changeset alongside
  → commit both to the per-board repo under .mendrik/changesets/<id>.{md,yaml}
  → mendrik validate --changeset <file> (schema + model checks; no API calls)
  → mendrik apply --dry-run  (resolved plan JSON)
  → human review
  → mendrik apply --apply
  → board state + pending_external_actions report
```

The narrative markdown and the YAML are separate artifacts. The markdown is for humans; the YAML is for the applier. They reference the same underlying intent.

## What to put where

| Intent | Goes in |
|---|---|
| Per-issue body amendment | `modifications[].body[]` |
| Bulk per-issue field assignment (10+ rows) | `field_updates[]` |
| Single-issue status change paired with a comment | `modifications[].status` + `modifications[].comment` |
| New issue to create | `new_tasks[]` (applier defers to plynth in v0.1) |
| Single-select field recolor or new option | `field_options[]` (declarative full state — read the warning) |
| "Operator does this out-of-band" | `pending_external_actions[]` |
| Choice between alternatives | `decisions[]` |

## When chat-emits YAML, do this

- **Cite the source.** Put the markdown filename in `source.document` and a one-paragraph `source.rationale`. Multi-wave reconciliations use `source.origin_dates: {wave_name: date}`.
- **Write `why:` prose on every modification.** Not for the applier; for the human reading the apply report. One sentence is fine.
- **Prefer `field_updates` over `modifications.status` for tabular Status changes.** `modifications` is for richer bundles (body + status + comment + decisions_resolved).
- **Quote dates and date-times for Mendrik.** Its PyYAML loader turns bare dates/timestamps into Python `date`/`datetime` objects, which fail the schema's string validation. It does not silently convert YAML into JSON. Write `"2026-05-11"` or `"2026-05-11T12:00:00Z"`.
- **Quote mapping keys intended as string labels.** For example, use `source.origin_dates: {"1": "2026-05-11"}`. JSON object keys are strings; bare `1` becomes a YAML integer key and Mendrik rejects it during model validation.
- **Write identifiers as single-line quoted strings.** `changeset_id: "my-change"` avoids YAML interpreting values such as `123`, `true`, or `null` as non-string types, and avoids the trailing newline added by a `|` block.
- **Use the canonical option names.** "Tier 1 — Visibility" matches the board option exactly. "Tier 1" alone works (applier resolves by prefix), but exact match is unambiguous.
- **Don't omit options in `field_options[].desired_options`.** GraphQL `updateProjectV2Field` deletes any omitted option (and its item values). The schema's required `migration` block exists for renames, not implicit deletions.
- **One source of truth per decision.** A `decision` block names the choice; a `modification` that closes it references the ID via `decisions_resolved: [...]`. Don't restate the resolution in both places.

`DateLike` checks lexical shape, not calendar validity: even `"2026-99-99"`
matches the published pattern. Schema-valid does not imply all consumer semantics
or successful execution. Mendrik also checks the model (including decision
references); live board resolution happens during `apply --dry-run`. See the
[v0.1.0 contract notes](SCHEMA-VERSIONING.md#v010-contract-notes).

## Public / private boundary

If the chat project is attached to the public Declaratus org schemas, the changeset YAML you author in that chat MUST be sanitized:

- No internal hostnames in `board.target`.
- No internal product names in `summary`, `source.rationale`, or `why:` prose.
- No client / engagement codes anywhere.

Internal-board changesets live in internal-host repos and stay there. The schema URL is the only artifact that crosses the boundary.

## Worked examples

The [examples/](../examples/) directory has five sanitized synthetic changesets covering every shape primitive:

- `minimal-changeset.example.yaml` — smallest valid
- `body-amendments.example.yaml` — every BodyMutation action
- `bulk-backfill.example.yaml` — flat field_updates and field_options with migration
- `decisions-block.example.yaml` — every Decision.state value
- `new-tasks.example.yaml` — new_tasks with dependencies and sources

Start from the closest example and modify. Don't author from scratch.
