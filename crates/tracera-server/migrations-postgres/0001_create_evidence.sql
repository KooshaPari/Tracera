-- 0001_create_evidence.sql (Postgres)
-- SWEE/SDLC tables — Postgres-flavoured, schema-equivalent to SQLite migrations.
CREATE TABLE IF NOT EXISTS evidence (
    id           TEXT PRIMARY KEY,
    artifact_id  TEXT NOT NULL,
    kind         TEXT NOT NULL,
    url          TEXT NOT NULL,
    metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS evidence_created_at_idx ON evidence (created_at);
