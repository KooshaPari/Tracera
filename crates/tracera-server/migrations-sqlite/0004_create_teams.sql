-- SQLite-dialect teams table (mirrors PG migration 0004).
-- TEXT[] (Postgres array) → TEXT (JSON-encoded array in SQLite).
CREATE TABLE IF NOT EXISTS teams (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    members     TEXT NOT NULL DEFAULT '[]',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

INSERT OR IGNORE INTO teams (id, name, description) VALUES
    ('team-1', 'Platform Team',  'Core platform engineering'),
    ('team-2', 'Product Team',   'Product feature development'),
    ('team-3', 'Security Team',  'Security and compliance');
