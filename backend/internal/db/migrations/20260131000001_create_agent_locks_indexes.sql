-- Ensure cleanup query is indexed
CREATE INDEX IF NOT EXISTS idx_lock_expire ON agent_locks (expire_at);
