-- TraceRTM Database Schema Reference
-- This file shows the complete schema created by migrations
-- DO NOT execute this file directly - use alembic migrations instead

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Projects table
CREATE TABLE projects (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(255) UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_name ON projects(name);

-- Items table
CREATE TABLE items (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'todo',
    priority INTEGER NOT NULL DEFAULT 0,
    parent_id VARCHAR(255) REFERENCES items(id) ON DELETE SET NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Items indexes
CREATE INDEX idx_items_project_id ON items(project_id);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_priority ON items(priority);
CREATE INDEX idx_items_parent_id ON items(parent_id);
CREATE INDEX idx_items_deleted_at ON items(deleted_at);
CREATE INDEX idx_items_project_status ON items(project_id, status);
CREATE INDEX idx_items_project_type ON items(project_id, type);

-- Full-text search indexes
CREATE INDEX idx_items_title_trgm ON items USING gin (title gin_trgm_ops);
CREATE INDEX idx_items_description_trgm ON items USING gin (description gin_trgm_ops);

-- Links table (NOTE: links table does NOT have project_id column - it's inferred from items)
CREATE TABLE links (
    id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    target_id VARCHAR(255) NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Links indexes (NOTE: links table uses source_id/target_id, not source_item_id/target_item_id)
CREATE INDEX idx_links_source_id ON links(source_id);
CREATE INDEX idx_links_target_id ON links(target_id);
CREATE INDEX idx_links_link_type ON links(link_type);
CREATE INDEX idx_links_source_target ON links(source_id, target_id);
CREATE INDEX idx_links_deleted_at ON links(deleted_at);

-- Agents table
CREATE TABLE agents (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    agent_metadata JSONB NOT NULL DEFAULT '{}',
    last_activity_at VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agents indexes
CREATE INDEX idx_agents_project_id ON agents(project_id);
CREATE INDEX idx_agents_project_status ON agents(project_id, status);

-- Agent events table
CREATE TABLE agent_events (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    item_id VARCHAR(255) REFERENCES items(id) ON DELETE SET NULL,
    event_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent events indexes
CREATE INDEX idx_agent_events_project_id ON agent_events(project_id);
CREATE INDEX idx_agent_events_agent_id ON agent_events(agent_id);
CREATE INDEX idx_agent_events_item_id ON agent_events(item_id);
CREATE INDEX idx_agent_events_project_agent ON agent_events(project_id, agent_id);
CREATE INDEX idx_agent_events_project_type ON agent_events(project_id, event_type);

-- ============================================================================
-- CHANGE TRACKING (from migration 001)
-- ============================================================================

CREATE TABLE change_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    record_id UUID NOT NULL,
    project_id UUID,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_change_log_processed ON change_log(processed) WHERE processed = FALSE;
CREATE INDEX idx_change_log_table ON change_log(table_name);
CREATE INDEX idx_change_log_record_id ON change_log(record_id);
CREATE INDEX idx_change_log_project_id ON change_log(project_id);
CREATE INDEX idx_change_log_changed_at ON change_log(changed_at);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers to all tables
CREATE TRIGGER update_projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_items_updated_at
BEFORE UPDATE ON items
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_links_updated_at
BEFORE UPDATE ON links
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at
BEFORE UPDATE ON agents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_events_updated_at
BEFORE UPDATE ON agent_events
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Change tracking triggers
CREATE OR REPLACE FUNCTION log_item_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO change_log (table_name, operation, record_id, project_id)
    VALUES (
        'items',
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        COALESCE(NEW.project_id, OLD.project_id)
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER item_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON items
FOR EACH ROW EXECUTE FUNCTION log_item_change();

CREATE OR REPLACE FUNCTION log_link_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO change_log (table_name, operation, record_id, project_id)
    VALUES (
        'links',
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        COALESCE(NEW.project_id, OLD.project_id)
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER link_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON links
FOR EACH ROW EXECUTE FUNCTION log_link_change();

-- ============================================================================
-- USEFUL QUERIES
-- ============================================================================

-- Full-text search on items
-- SELECT * FROM items WHERE title % 'search term' ORDER BY similarity(title, 'search term') DESC;

-- Find all links for an item
-- SELECT * FROM links WHERE source_item_id = 'item_id' OR target_item_id = 'item_id';

-- Count items by view
-- SELECT view, COUNT(*) FROM items WHERE deleted_at IS NULL GROUP BY view;

-- Recent agent activity
-- SELECT a.name, ae.event_type, ae.created_at
-- FROM agent_events ae
-- JOIN agents a ON ae.agent_id = a.id
-- ORDER BY ae.created_at DESC
-- LIMIT 10;

-- Traceability matrix (items linked to requirements)
-- SELECT
--   i1.title as requirement,
--   i2.title as implementation,
--   l.link_type
-- FROM links l
-- JOIN items i1 ON l.target_item_id = i1.id
-- JOIN items i2 ON l.source_item_id = i2.id
-- WHERE i1.view = 'requirements';
