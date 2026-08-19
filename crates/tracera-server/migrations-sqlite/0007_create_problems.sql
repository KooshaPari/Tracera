-- Restore problems table for ITIL problem-management domain.
-- SQLite port of migrations/0007_create_problems.sql
-- Uses TEXT instead of JSONB, INTEGER instead of BOOLEAN, TEXT instead of TIMESTAMPTZ.

CREATE TABLE IF NOT EXISTS problems (
    id                      TEXT PRIMARY KEY,
    project_id              TEXT        NOT NULL,
    problem_number          TEXT        NOT NULL UNIQUE,
    title                   TEXT        NOT NULL,
    description             TEXT,
    status                  TEXT        NOT NULL DEFAULT 'open',
    resolution_type         TEXT,
    category                TEXT,
    sub_category            TEXT,
    tags                    TEXT        NOT NULL DEFAULT 'null',
    impact_level            TEXT        NOT NULL DEFAULT 'medium',
    urgency                 TEXT        NOT NULL DEFAULT 'medium',
    priority                TEXT        NOT NULL DEFAULT 'medium',
    rca_performed           INTEGER     NOT NULL DEFAULT 0,
    root_cause_identified   INTEGER     NOT NULL DEFAULT 0,
    workaround_available    INTEGER     NOT NULL DEFAULT 0,
    permanent_fix_available INTEGER     NOT NULL DEFAULT 0,
    assigned_to             TEXT,
    assigned_team           TEXT,
    owner                   TEXT,
    known_error_id          TEXT,
    created_at              TEXT        NOT NULL,
    updated_at              TEXT        NOT NULL,
    deleted_at              TEXT
);

CREATE INDEX IF NOT EXISTS ix_problems_project_status
    ON problems (project_id, status);
CREATE INDEX IF NOT EXISTS ix_problems_project_priority
    ON problems (project_id, priority);
CREATE INDEX IF NOT EXISTS ix_problems_project_impact
    ON problems (project_id, impact_level);
CREATE INDEX IF NOT EXISTS ix_problems_assigned_to
    ON problems (assigned_to);
CREATE INDEX IF NOT EXISTS ix_problems_category
    ON problems (category);
CREATE INDEX IF NOT EXISTS ix_problems_deleted_at
    ON problems (deleted_at);
