-- Add missing index for projects.deleted_at
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects(deleted_at);
