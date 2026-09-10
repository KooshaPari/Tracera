-- 0005_create_trace_links.sql (Postgres)
CREATE TABLE IF NOT EXISTS trace_links (
    id           TEXT PRIMARY KEY,
    source_id    TEXT NOT NULL,
    target_id    TEXT NOT NULL,
    relationship TEXT NOT NULL,
    confidence   DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS trace_links_source_idx ON trace_links (source_id);
CREATE INDEX IF NOT EXISTS trace_links_target_idx ON trace_links (target_id);
