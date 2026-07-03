-- Restore evidence table dropped in Python→Rust migration.
-- Mirrors src/tracertm/api/routers/evidence.py EvidenceItem model.
CREATE TABLE IF NOT EXISTS evidence (
    id          TEXT PRIMARY KEY,
    artifact_id TEXT        NOT NULL,
    kind        TEXT        NOT NULL,
    url         TEXT        NOT NULL,
    metadata    JSONB       NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
