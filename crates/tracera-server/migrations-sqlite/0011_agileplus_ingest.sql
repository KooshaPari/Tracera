-- AgilePlus governance ingestion provenance (SPEC-009, amended 2026-11-02).
--
-- agileplus_ingest_keys is the idempotency ledger: one row per consumed
-- X-Idempotency-Key. The body fingerprint lets a replay with different content
-- fail as a conflict instead of being mistaken for the same request.
CREATE TABLE IF NOT EXISTS agileplus_ingest_keys (
    idempotency_key   TEXT PRIMARY KEY,
    body_fingerprint  TEXT NOT NULL,
    ingestion_id      TEXT NOT NULL,
    ingested_at       TEXT NOT NULL
);

-- agileplus_revisions is the accepted-revision ledger: stale or duplicate
-- revisions are rejected before any node is written.
CREATE TABLE IF NOT EXISTS agileplus_revisions (
    agileplus_id  TEXT PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    revision      INTEGER NOT NULL,
    node_id       TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agileplus_revisions_type
    ON agileplus_revisions(entity_type);
