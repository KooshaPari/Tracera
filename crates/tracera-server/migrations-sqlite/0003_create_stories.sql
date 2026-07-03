-- SQLite-dialect stories table (mirrors PG migration 0003).
CREATE TABLE IF NOT EXISTS stories (
    id           TEXT    PRIMARY KEY,
    sprint_id    TEXT,
    title        TEXT    NOT NULL,
    description  TEXT    NOT NULL DEFAULT '',
    status       TEXT    NOT NULL DEFAULT 'open',
    story_points INTEGER,
    created_at   TEXT    NOT NULL,
    updated_at   TEXT    NOT NULL
);
