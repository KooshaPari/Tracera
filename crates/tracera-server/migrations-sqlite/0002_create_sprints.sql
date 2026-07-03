-- SQLite-dialect sprints table (mirrors PG migration 0002).
CREATE TABLE IF NOT EXISTS sprints (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    goal       TEXT NOT NULL DEFAULT '',
    start_date TEXT NOT NULL,
    end_date   TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'planned',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
