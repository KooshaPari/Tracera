-- Persistent trace-links table.
-- Each record captures a directed edge between two artifact IDs with
-- relationship kind and confidence score.  Populated by the real ingest
-- pipeline (GitHub / Jira) in addition to the in-memory coverage-matrix API.
CREATE TABLE IF NOT EXISTS trace_links (
    id           TEXT PRIMARY KEY,
    source_id    TEXT        NOT NULL,
    target_id    TEXT        NOT NULL,
    relationship TEXT        NOT NULL,
    confidence   DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    source       TEXT        NOT NULL DEFAULT 'manual',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_trace_links_source ON trace_links (source_id);
CREATE INDEX IF NOT EXISTS ix_trace_links_target ON trace_links (target_id);
