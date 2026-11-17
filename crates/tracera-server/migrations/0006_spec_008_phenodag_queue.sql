-- Spec 008 P1: phenodag fleet-queue schema (tasks, agents, claims).
--
-- Minimal schema derived from phenodag v0.3.0 (Go). Adds three tables used by
-- the atomic-claim / heartbeat / lifecycle operations ported in this PR.
--
-- See: docs/specs/008-phenodag-absorption.md (P1)
-- Source: github.com/KooshaPari/phenodag/blob/main/phenodag.go (schema)

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
