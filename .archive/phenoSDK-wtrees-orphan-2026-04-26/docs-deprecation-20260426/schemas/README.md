# Schema Snapshot Workflow

The files under `schemas/` capture the reference database schema that backs
pheno-sdk deployments. Keep these artefacts current whenever Supabase
migrations land so the automated checks (`make schema-verify`) remain
trustworthy.

## Updating the snapshot

1. Ensure you have Supabase credentials exported (or a `DB_URL`) that matches
   the environment you want to snapshot.
2. From the repository root run:

```bash
make schema-sync
```

This delegates to `scripts/migrate_schema.py`, which refreshes
`schemas/generated/schema_snapshot.json` and the associated metadata file.

## Verifying changes

Before pushing, confirm the snapshot is coherent:

```bash
make schema-verify
```

The validator checks the snapshot hash, metadata, and lightweight Pydantic
definitions in `schemas/definitions/`.

Commit the updated JSON files alongside any migration scripts so CI stays in
lockstep with the live database.
