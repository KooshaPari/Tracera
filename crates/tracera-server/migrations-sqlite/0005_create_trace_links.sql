-- SQLite-dialect trace_links table (mirrors PG migration 0005).
CREATE TABLE IF NOT EXISTS trace_links (
    id           TEXT    PRIMARY KEY,
    source_id    TEXT    NOT NULL,
    target_id    TEXT    NOT NULL,
    relationship TEXT    NOT NULL,
    confidence   REAL    NOT NULL DEFAULT 1.0,
    source       TEXT    NOT NULL DEFAULT 'manual',
    created_at   TEXT    NOT NULL,
    updated_at   TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_trace_links_source ON trace_links (source_id);
CREATE INDEX IF NOT EXISTS ix_trace_links_target ON trace_links (target_id);
