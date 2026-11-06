-- AgilePlus governance ingestion provenance (SPEC-009, amended 2026-11-02).
-- Mirrors migrations-sqlite/0011_agileplus_ingest.sql.
CREATE TABLE IF NOT EXISTS agileplus_ingest_keys (
    idempotency_key   TEXT PRIMARY KEY,
    body_fingerprint  TEXT NOT NULL,
    ingestion_id      TEXT NOT NULL,
    ingested_at       TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS agileplus_revisions (
    agileplus_id  TEXT PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    revision      BIGINT NOT NULL,
    node_id       TEXT NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agileplus_revisions_type
    ON agileplus_revisions(entity_type);
