-- Restore teams table dropped in Python→Rust migration.
-- Mirrors src/tracertm/api/routers/org_intel.py Team model.
-- Seeds the 3 default teams that the Python backend served from its empty-store fallback.
CREATE TABLE IF NOT EXISTS teams (
    id          TEXT PRIMARY KEY,
    name        TEXT        NOT NULL,
    description TEXT        NOT NULL DEFAULT '',
    members     TEXT[]      NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO teams (id, name, description) VALUES
    ('team-1', 'Platform Team',  'Core platform engineering'),
    ('team-2', 'Product Team',   'Product feature development'),
    ('team-3', 'Security Team',  'Security and compliance')
ON CONFLICT (id) DO NOTHING;
