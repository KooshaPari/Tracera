-- Restore problems table for ITIL problem-management domain.
-- Mirrors the Problem domain struct added in store.rs (recovery from the
-- Python `src/tracertm/models/problem.py` model, deleted in PR-554 and
-- originally authored in commit 2ece64691f).
--
-- ITIL lifecycle: open -> in_investigation -> pending_workaround | known_error
-- -> awaiting_fix -> closed.  Resolution classification is captured separately
-- once a problem reaches the closed state.
--
-- This migration is the production-tier companion to the in-memory SQLite
-- CREATE TABLE that lives inside `make_sqlite_store` in main.rs (test only).
-- Both backends (PgStore, SqliteStore) consume the same Rust `Problem` struct.
CREATE TABLE IF NOT EXISTS problems (
    id                      TEXT        PRIMARY KEY,
    -- Postgres-side foreign key is to projects(id); mirrors the Python
    -- `ForeignKey("projects.id", ondelete="CASCADE")`.  Application layer is
    -- responsible for UUID format validation; we store TEXT to match the
    -- `project_id: String` field on the Rust Problem struct.
    project_id              TEXT        NOT NULL,
    problem_number          TEXT        NOT NULL UNIQUE,
    title                   TEXT        NOT NULL,
    description             TEXT,
    status                  TEXT        NOT NULL DEFAULT 'open',
    resolution_type         TEXT,
    category                TEXT,
    sub_category            TEXT,
    tags                    JSONB       NOT NULL DEFAULT 'null'::jsonb,
    impact_level            TEXT        NOT NULL DEFAULT 'medium',
    urgency                 TEXT        NOT NULL DEFAULT 'medium',
    priority                TEXT        NOT NULL DEFAULT 'medium',
    rca_performed           BOOLEAN     NOT NULL DEFAULT FALSE,
    root_cause_identified   BOOLEAN     NOT NULL DEFAULT FALSE,
    workaround_available    BOOLEAN     NOT NULL DEFAULT FALSE,
    permanent_fix_available BOOLEAN     NOT NULL DEFAULT FALSE,
    assigned_to             TEXT,
    assigned_team           TEXT,
    owner                   TEXT,
    known_error_id          TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at              TIMESTAMPTZ
);

-- Indexes mirror the Python model's __table_args__ indexes (where still
-- relevant after collapsing the Rust port to the minimum viable column set).
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