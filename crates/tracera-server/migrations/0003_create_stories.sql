-- Restore stories table dropped in Python→Rust migration.
-- Mirrors src/tracertm/api/routers/sdlc_pm.py Story model.
CREATE TABLE IF NOT EXISTS stories (
    id           TEXT PRIMARY KEY,
    sprint_id    TEXT,
    title        TEXT        NOT NULL,
    description  TEXT        NOT NULL DEFAULT '',
    status       TEXT        NOT NULL DEFAULT 'open',
    story_points BIGINT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
