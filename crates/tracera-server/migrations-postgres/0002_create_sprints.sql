-- 0002_create_sprints.sql (Postgres)
CREATE TABLE IF NOT EXISTS sprints (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    goal         TEXT,
    starts_at    TIMESTAMPTZ NOT NULL,
    ends_at      TIMESTAMPTZ NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
