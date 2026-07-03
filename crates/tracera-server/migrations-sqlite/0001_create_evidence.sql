-- SQLite-dialect evidence table (mirrors PG migration 0001).
-- JSONB → TEXT (SQLite stores JSON as text), TIMESTAMPTZ → TEXT (ISO-8601).
CREATE TABLE IF NOT EXISTS evidence (
    id          TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    kind        TEXT NOT NULL,
    url         TEXT NOT NULL,
    metadata    TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
