-- Agent Coordination System Database Schema Extensions
-- PostgreSQL 14+

-- Agent Locks table (for optimistic and pessimistic locking)
CREATE TABLE IF NOT EXISTS agent_locks (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    lock_type VARCHAR(50) NOT NULL,  -- optimistic, pessimistic
    version BIGINT NOT NULL DEFAULT 1,
    expire_at TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lock_item ON agent_locks(item_id);
CREATE INDEX idx_lock_agent ON agent_locks(agent_id);
CREATE INDEX idx_lock_expire ON agent_locks(expire_at);
CREATE INDEX idx_lock_item_agent ON agent_locks(item_id, agent_id);

-- Agent Teams table
CREATE TABLE IF NOT EXISTS agent_teams (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    roles JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_team_project ON agent_teams(project_id);
CREATE INDEX idx_team_name ON agent_teams(project_id, name);

-- Agent Team Memberships table
CREATE TABLE IF NOT EXISTS agent_team_memberships (
    id VARCHAR(255) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL REFERENCES agent_teams(id) ON DELETE CASCADE,
    agent_id VARCHAR(255) NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, agent_id)
);

CREATE INDEX idx_membership_team ON agent_team_memberships(team_id);
CREATE INDEX idx_membership_agent ON agent_team_memberships(agent_id);

-- Item Versions table (for conflict detection)
CREATE TABLE IF NOT EXISTS item_versions (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    version BIGINT NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    changes JSONB NOT NULL,
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, version)
);

CREATE INDEX idx_version_item ON item_versions(item_id);
CREATE INDEX idx_version_hash ON item_versions(current_hash);
CREATE INDEX idx_version_item_version ON item_versions(item_id, version DESC);

-- Conflict Records table
CREATE TABLE IF NOT EXISTS conflict_records (
    id VARCHAR(255) PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    conflicting_agents JSONB NOT NULL,  -- array of agent IDs
    conflict_type VARCHAR(50) NOT NULL,  -- concurrent_modification, version_mismatch, lock_timeout
    resolution_strategy VARCHAR(50) NOT NULL,  -- last_write_wins, agent_priority, manual, merge, first_wins
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, resolved, failed
    conflict_data JSONB DEFAULT '{}',
    resolved_by VARCHAR(255),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conflict_item ON conflict_records(item_id);
CREATE INDEX idx_conflict_status ON conflict_records(resolution_status);
CREATE INDEX idx_conflict_item_status ON conflict_records(item_id, resolution_status);
CREATE INDEX idx_conflict_created ON conflict_records(created_at DESC);

-- Distributed Operations table
CREATE TABLE IF NOT EXISTS distributed_operations (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- batch_update, coordinated_analysis, multi_agent_task
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, failed, cancelled
    participant_ids JSONB NOT NULL,  -- array of agent IDs
    coordinator_id VARCHAR(255) NOT NULL,
    target_items JSONB DEFAULT '[]',  -- array of item IDs
    operation_data JSONB DEFAULT '{}',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operation_project ON distributed_operations(project_id);
CREATE INDEX idx_operation_status ON distributed_operations(status);
CREATE INDEX idx_operation_coordinator ON distributed_operations(coordinator_id);
CREATE INDEX idx_operation_project_status ON distributed_operations(project_id, status);

-- Operation Participants table
CREATE TABLE IF NOT EXISTS operation_participants (
    id VARCHAR(255) PRIMARY KEY,
    operation_id VARCHAR(255) NOT NULL REFERENCES distributed_operations(id) ON DELETE CASCADE,
    agent_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ready',  -- ready, working, completed, failed
    assigned_items JSONB DEFAULT '[]',  -- array of item IDs
    result JSONB DEFAULT '{}',
    error TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(operation_id, agent_id)
);

CREATE INDEX idx_participant_operation ON operation_participants(operation_id);
CREATE INDEX idx_participant_agent ON operation_participants(agent_id);
CREATE INDEX idx_participant_status ON operation_participants(status);

-- Agent Coordination Metrics table (for monitoring and analytics)
CREATE TABLE IF NOT EXISTS agent_coordination_metrics (
    id VARCHAR(255) PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,  -- locks_acquired, conflicts_detected, operations_completed
    metric_value NUMERIC NOT NULL,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_agent ON agent_coordination_metrics(agent_id);
CREATE INDEX idx_metrics_type ON agent_coordination_metrics(metric_type);
CREATE INDEX idx_metrics_recorded ON agent_coordination_metrics(recorded_at DESC);

-- Function to cleanup expired locks
CREATE OR REPLACE FUNCTION cleanup_expired_locks() RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_locks WHERE expire_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to detect version conflicts
CREATE OR REPLACE FUNCTION detect_version_conflict(
    p_item_id VARCHAR(255),
    p_expected_version BIGINT
) RETURNS JSONB AS $$
DECLARE
    current_version BIGINT;
    conflict_info JSONB;
BEGIN
    SELECT version INTO current_version
    FROM item_versions
    WHERE item_id = p_item_id
    ORDER BY version DESC
    LIMIT 1;

    IF NOT FOUND THEN
        current_version := 0;
    END IF;

    IF current_version != p_expected_version - 1 THEN
        conflict_info := jsonb_build_object(
            'has_conflict', true,
            'expected_version', p_expected_version,
            'current_version', current_version,
            'message', 'Version mismatch detected'
        );
    ELSE
        conflict_info := jsonb_build_object(
            'has_conflict', false,
            'current_version', current_version
        );
    END IF;

    RETURN conflict_info;
END;
$$ LANGUAGE plpgsql;

-- Function to get agent priority from team roles
CREATE OR REPLACE FUNCTION get_agent_priority(p_agent_id VARCHAR(255)) RETURNS INTEGER AS $$
DECLARE
    max_priority INTEGER := 0;
    membership_record RECORD;
BEGIN
    FOR membership_record IN
        SELECT m.team_id, m.role_name, t.roles
        FROM agent_team_memberships m
        JOIN agent_teams t ON m.team_id = t.id
        WHERE m.agent_id = p_agent_id
    LOOP
        -- Extract priority from role JSON
        -- This assumes roles JSONB structure like: {"role_name": {"priority": 5}}
        DECLARE
            role_priority INTEGER;
        BEGIN
            role_priority := (membership_record.roles->membership_record.role_name->>'priority')::INTEGER;
            IF role_priority > max_priority THEN
                max_priority := role_priority;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            CONTINUE;
        END;
    END LOOP;

    RETURN max_priority;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to all coordination tables
CREATE TRIGGER update_agent_locks_updated_at BEFORE UPDATE ON agent_locks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_teams_updated_at BEFORE UPDATE ON agent_teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_team_memberships_updated_at BEFORE UPDATE ON agent_team_memberships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conflict_records_updated_at BEFORE UPDATE ON conflict_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_distributed_operations_updated_at BEFORE UPDATE ON distributed_operations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_operation_participants_updated_at BEFORE UPDATE ON operation_participants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for active locks summary
CREATE OR REPLACE VIEW active_locks_summary AS
SELECT
    agent_id,
    COUNT(*) as lock_count,
    COUNT(DISTINCT item_id) as unique_items,
    MIN(expire_at) as earliest_expiry,
    MAX(expire_at) as latest_expiry,
    SUM(CASE WHEN lock_type = 'optimistic' THEN 1 ELSE 0 END) as optimistic_locks,
    SUM(CASE WHEN lock_type = 'pessimistic' THEN 1 ELSE 0 END) as pessimistic_locks
FROM agent_locks
WHERE expire_at > CURRENT_TIMESTAMP
GROUP BY agent_id;

-- View for pending conflicts
CREATE OR REPLACE VIEW pending_conflicts AS
SELECT
    cr.*,
    iv.version as current_version,
    iv.agent_id as last_modifier
FROM conflict_records cr
LEFT JOIN LATERAL (
    SELECT version, agent_id
    FROM item_versions
    WHERE item_id = cr.item_id
    ORDER BY version DESC
    LIMIT 1
) iv ON true
WHERE cr.resolution_status = 'pending'
ORDER BY cr.created_at DESC;

-- View for operation progress
CREATE OR REPLACE VIEW operation_progress AS
SELECT
    do.id,
    do.project_id,
    do.type,
    do.status,
    do.coordinator_id,
    COUNT(op.id) as total_participants,
    SUM(CASE WHEN op.status = 'completed' THEN 1 ELSE 0 END) as completed_participants,
    SUM(CASE WHEN op.status = 'failed' THEN 1 ELSE 0 END) as failed_participants,
    SUM(CASE WHEN op.status = 'working' THEN 1 ELSE 0 END) as working_participants,
    ROUND(100.0 * SUM(CASE WHEN op.status = 'completed' THEN 1 ELSE 0 END) / COUNT(op.id), 2) as completion_percentage,
    do.created_at,
    do.started_at,
    do.completed_at
FROM distributed_operations do
LEFT JOIN operation_participants op ON do.id = op.operation_id
GROUP BY do.id, do.project_id, do.type, do.status, do.coordinator_id, do.created_at, do.started_at, do.completed_at;

-- Comments for documentation
COMMENT ON TABLE agent_locks IS 'Stores locks acquired by agents on items for coordinated access';
COMMENT ON TABLE agent_teams IS 'Defines teams of agents with role-based permissions';
COMMENT ON TABLE agent_team_memberships IS 'Links agents to teams with specific roles';
COMMENT ON TABLE item_versions IS 'Tracks version history of items for conflict detection';
COMMENT ON TABLE conflict_records IS 'Records detected conflicts and their resolution status';
COMMENT ON TABLE distributed_operations IS 'Manages distributed operations across multiple agents';
COMMENT ON TABLE operation_participants IS 'Tracks individual agent participation in distributed operations';
COMMENT ON TABLE agent_coordination_metrics IS 'Stores metrics for monitoring agent coordination system';

COMMENT ON COLUMN agent_locks.lock_type IS 'Type of lock: optimistic (version-based) or pessimistic (exclusive)';
COMMENT ON COLUMN conflict_records.resolution_strategy IS 'Strategy for resolving conflicts: last_write_wins, agent_priority, manual, merge, first_wins';
COMMENT ON COLUMN distributed_operations.type IS 'Type of distributed operation: batch_update, coordinated_analysis, multi_agent_task';
