-- Restore sprints table dropped in Python→Rust migration.
-- Mirrors src/tracertm/api/routers/sdlc_pm.py Sprint model.
CREATE TABLE IF NOT EXISTS sprints (
    id         TEXT PRIMARY KEY,
    name       TEXT        NOT NULL,
    goal       TEXT        NOT NULL DEFAULT '',
    start_date TIMESTAMPTZ NOT NULL,
    end_date   TIMESTAMPTZ NOT NULL,
    status     TEXT        NOT NULL DEFAULT 'planned',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
