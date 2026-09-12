-- Adds the columns PgStore queries against problems.
ALTER TABLE problems ADD COLUMN IF NOT EXISTS project_id TEXT NOT NULL DEFAULT 'unassigned';
ALTER TABLE problems ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ NULL;
CREATE INDEX IF NOT EXISTS idx_problems_project_id ON problems(project_id);
CREATE INDEX IF NOT EXISTS idx_problems_deleted_at ON problems(deleted_at);
