-- Verified replay-v2 provenance. Revert with:
-- DROP TABLE IF EXISTS benchmark_runs;
CREATE TABLE IF NOT EXISTS benchmark_runs (
    run_id           TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL,
    attempt_id       TEXT NOT NULL,
    schema_version   TEXT NOT NULL,
    replay_hash      TEXT NOT NULL UNIQUE,
    outcome_sha256   TEXT NOT NULL,
    key_id           TEXT NOT NULL,
    signature_digest TEXT NOT NULL,
    status           TEXT NOT NULL,
    metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at       TIMESTAMPTZ NOT NULL,
    updated_at       TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_benchmark_runs_created_at
    ON benchmark_runs (created_at);
