-- TraceRTM Database Schema
-- PostgreSQL 14+

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";          -- Full-text search with trigrams
CREATE EXTENSION IF NOT EXISTS "vector";           -- pgvector for semantic search (optional)

-- Profiles table (WorkOS user profiles - no Supabase dependency)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Legacy Supabase auth.users.id (deprecated, kept for migration compatibility)
    auth_id UUID UNIQUE,
    -- WorkOS user ID (primary identifier)
    workos_user_id TEXT NOT NULL UNIQUE,
    -- WorkOS organization ID
    workos_org_id TEXT,
    -- Additional WorkOS IDs for future use
    workos_ids JSONB DEFAULT '{}',
    -- User profile information
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    avatar_url TEXT,
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_profiles_auth_id ON profiles(auth_id);
CREATE INDEX idx_profiles_workos_user_id ON profiles(workos_user_id);
CREATE INDEX idx_profiles_workos_org_id ON profiles(workos_org_id);
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_deleted_at ON profiles(deleted_at);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_deleted_at ON projects(deleted_at);

-- Items table (Features, Code, Tests, APIs, etc.)
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,  -- feature, code, test, api, database, etc.
    status VARCHAR(50) NOT NULL DEFAULT 'todo',  -- todo, in_progress, done, blocked
    priority INTEGER DEFAULT 50,
    metadata JSONB DEFAULT '{}',
    search_vector tsvector,                     -- Full-text search vector
    embedding vector(384),                       -- pgvector embedding for semantic search (384 dimensions)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Standard indexes
CREATE INDEX idx_items_project_id ON items(project_id);
CREATE INDEX idx_items_project_type ON items(project_id, type);
CREATE INDEX idx_items_project_status ON items(project_id, status);
CREATE INDEX idx_items_deleted_at ON items(deleted_at);

-- Search indexes
CREATE INDEX idx_items_search_vector ON items USING GIN(search_vector);
CREATE INDEX idx_items_embedding ON items USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);

-- Trigger to automatically update search_vector on insert/update
CREATE OR REPLACE FUNCTION items_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', coalesce(NEW.title, '') || ' ' || coalesce(NEW.description, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER items_search_vector_trigger
    BEFORE INSERT OR UPDATE ON items
    FOR EACH ROW
    EXECUTE FUNCTION items_search_vector_update();

-- Links table (60+ link types across 12 categories)
CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- depends_on, implements, tests, blocks, etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_links_source_id ON links(source_id);
CREATE INDEX idx_links_target_id ON links(target_id);
CREATE INDEX idx_links_type ON links(type);
CREATE INDEX idx_links_deleted_at ON links(deleted_at);

-- Agents table (for 1-1000 concurrent agents)
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',  -- active, idle, error
    metadata JSONB DEFAULT '{}',
    last_activity_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_agents_project_id ON agents(project_id);
CREATE INDEX idx_agents_project_status ON agents(project_id, status);
CREATE INDEX idx_agents_deleted_at ON agents(deleted_at);

-- Events table (for event sourcing and audit trail)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,  -- item, link, project, agent
    entity_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- created, updated, deleted
    data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',  -- Additional context (user_id, source, ip, etc.)
    version INTEGER NOT NULL DEFAULT 1,  -- Event version for optimistic locking
    causation_id UUID,  -- ID of the command/event that caused this event
    correlation_id UUID,  -- ID to correlate related events across services
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_project_id ON events(project_id);
CREATE INDEX idx_events_entity_id ON events(entity_id);
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_events_entity_version ON events(entity_id, version);
CREATE INDEX idx_events_correlation_id ON events(correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX idx_events_causation_id ON events(causation_id) WHERE causation_id IS NOT NULL;

-- Agent tasks table (for task queue and coordination)
CREATE TABLE IF NOT EXISTS agent_tasks (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, assigned, running, completed, failed, canceled
    priority INTEGER NOT NULL DEFAULT 1,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_tasks_project_id ON agent_tasks(project_id);
CREATE INDEX idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX idx_agent_tasks_priority ON agent_tasks(priority);
CREATE INDEX idx_agent_tasks_project_status ON agent_tasks(project_id, status);
CREATE INDEX idx_agent_tasks_project_priority ON agent_tasks(project_id, priority);

