# declaratus-schemas

JSON Schema contracts for authors and tools working with project-lifecycle documents.
The shipped [changeset schema](schemas/v0/changeset.schema.json) uses JSON Schema
Draft 2020-12 and accepts the `0.1.x` document version line.

## Start with a changeset

1. Copy the [minimal synthetic changeset](examples/minimal-changeset.example.yaml)
   as an authoring starting point.
2. Keep `schema_version` in the `0.1.x` line, for example `"0.1.0"`. The schema
   requires `schema_version`, `platform`, and `changeset_id`; `0.0.1` is deprecated
   and rejected by this schema.
3. Validate the document shape against the changeset schema with a Draft 2020-12
   validator. For chat reference setup and authoring guidance, see
   [CHAT-USAGE](docs/CHAT-USAGE.md).

Use the version-pinned `v0.1.0` reference URL when attaching or consuming the schema:

```text
https://raw.githubusercontent.com/Declaratus/declaratus-schemas/v0.1.0/schemas/v0/changeset.schema.json
```

See [SCHEMA-VERSIONING](docs/SCHEMA-VERSIONING.md) for tag pinning, document versions,
and consumer vendoring.

## Worked examples

The [examples directory](examples/) contains five synthetic changesets:

- [Minimal changeset](examples/minimal-changeset.example.yaml): required envelope
  fields and one body amendment.
- [Body amendments](examples/body-amendments.example.yaml): the four body mutation
  action shapes.
- [Bulk backfill](examples/bulk-backfill.example.yaml): field updates, field options,
  and migration declarations.
- [Decisions](examples/decisions-block.example.yaml): decision states and references
  from modifications.
- [New tasks](examples/new-tasks.example.yaml): task declarations, dependencies, and
  pending external actions.

## Scope and status

Only `changeset.schema.json` ships today. Three sibling schemas are planned:
`inspection-report.schema.json`, `portfolio-registry.schema.json`, and
`portfolio-rollup.schema.json`.

This repository provides document contracts and examples. Schema validation checks
document shape; it does not execute changes, resolve live board references, or prove
that a consumer implements an accepted operation. For example, the schema accepts
`platform: linear`, while its description limits v0.1.x applier support to
`github_projects`. The `new_tasks` shape is also accepted, but its description
documents deferred creation rather than direct creation by the v0.1 applier.
