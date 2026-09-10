-- 0003_create_stories.sql (Postgres)
CREATE TABLE IF NOT EXISTS stories (
    id           TEXT PRIMARY KEY,
    sprint_id    TEXT REFERENCES sprints(id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    description  TEXT,
    status       TEXT NOT NULL DEFAULT 'backlog',
    priority     TEXT,
    assignee_id  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS stories_sprint_idx ON stories (sprint_id);
