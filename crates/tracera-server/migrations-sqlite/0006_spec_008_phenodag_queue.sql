-- Spec 008 P1: phenodag fleet-queue schema (tasks, agents, claims).
-- SQLite port of migrations/0006_spec_008_phenodag_queue.sql

CREATE TABLE IF NOT EXISTS tasks (
    id              TEXT PRIMARY KEY,
    status          TEXT NOT NULL CHECK (status IN ('ready', 'in_progress', 'done', 'failed', 'blocked')),
    assigned_agent  TEXT,
    updated_at      TEXT
);

CREATE TABLE IF NOT EXISTS agents (
    id              TEXT PRIMARY KEY,
    status          TEXT NOT NULL DEFAULT 'idle' CHECK (status IN ('active', 'idle', 'stale')),
    last_heartbeat  TEXT,
    last_seen       TEXT
);

CREATE TABLE IF NOT EXISTS claims (
    task_id         TEXT PRIMARY KEY,
    agent_id        TEXT NOT NULL,
    claimed_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_agent);
CREATE INDEX IF NOT EXISTS idx_agents_last_hb ON agents(last_heartbeat);
