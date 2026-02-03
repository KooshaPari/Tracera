-- 049: problems + problem_activities
CREATE TABLE IF NOT EXISTS problems (
    id VARCHAR(255) PRIMARY KEY,
    problem_number VARCHAR(50) UNIQUE NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    resolution_type VARCHAR(50),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    tags VARCHAR[],
    impact_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    urgency VARCHAR(20) NOT NULL DEFAULT 'medium',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    affected_systems VARCHAR[],
    affected_users_estimated INTEGER,
    business_impact_description TEXT,
    rca_performed BOOLEAN NOT NULL DEFAULT false,
    rca_method VARCHAR(50),
    rca_notes TEXT,
    rca_data JSONB,
    root_cause_identified BOOLEAN NOT NULL DEFAULT false,
    root_cause_description TEXT,
    root_cause_category VARCHAR(50),
    root_cause_confidence VARCHAR(20),
    rca_completed_at TIMESTAMPTZ,
    rca_completed_by VARCHAR(255),
    workaround_available BOOLEAN NOT NULL DEFAULT false,
    workaround_description TEXT,
    workaround_effectiveness VARCHAR(50),
    permanent_fix_available BOOLEAN NOT NULL DEFAULT false,
    permanent_fix_description TEXT,
    permanent_fix_implemented_at TIMESTAMPTZ,
    permanent_fix_change_id VARCHAR(255),
    known_error_id VARCHAR(255),
    knowledge_article_id VARCHAR(255),
    assigned_to VARCHAR(255),
    assigned_team VARCHAR(255),
    owner VARCHAR(255),
    closed_by VARCHAR(255),
    closed_at TIMESTAMPTZ,
    closure_notes TEXT,
    target_resolution_date TIMESTAMPTZ,
    problem_metadata JSONB NOT NULL DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_problems_problem_number ON problems (problem_number);
CREATE INDEX IF NOT EXISTS idx_problems_project_id ON problems (project_id);
CREATE INDEX IF NOT EXISTS idx_problems_status ON problems (status);
CREATE INDEX IF NOT EXISTS idx_problems_project_status ON problems (project_id, status);
CREATE INDEX IF NOT EXISTS idx_problems_project_priority ON problems (project_id, priority);
CREATE INDEX IF NOT EXISTS idx_problems_project_impact ON problems (project_id, impact_level);
CREATE INDEX IF NOT EXISTS idx_problems_assigned_to ON problems (assigned_to);
CREATE INDEX IF NOT EXISTS idx_problems_category ON problems (category);
CREATE INDEX IF NOT EXISTS idx_problems_known_error_id ON problems (known_error_id);
CREATE INDEX IF NOT EXISTS idx_problems_deleted_at ON problems (deleted_at);

CREATE TABLE IF NOT EXISTS problem_activities (
    id VARCHAR(255) PRIMARY KEY,
    problem_id VARCHAR(255) NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    from_value VARCHAR(255),
    to_value VARCHAR(255),
    description TEXT,
    performed_by VARCHAR(255),
    activity_metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_problem_activities_problem_id ON problem_activities (problem_id);

-- 050: processes + process_executions
CREATE TABLE IF NOT EXISTS processes (
    id VARCHAR(255) PRIMARY KEY,
    process_number VARCHAR(50) UNIQUE NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    purpose TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    category VARCHAR(100),
    tags VARCHAR[],
    version_number INTEGER NOT NULL DEFAULT 1,
    is_active_version BOOLEAN NOT NULL DEFAULT true,
    parent_version_id VARCHAR(255) REFERENCES processes(id) ON DELETE SET NULL,
    version_notes TEXT,
    stages JSONB,
    swimlanes JSONB,
    bpmn_xml TEXT,
    bpmn_diagram_url VARCHAR(500),
    inputs JSONB,
    outputs JSONB,
    triggers JSONB,
    exit_criteria VARCHAR[],
    owner VARCHAR(255),
    responsible_team VARCHAR(255),
    expected_duration_hours INTEGER,
    sla_hours INTEGER,
    activated_at TIMESTAMPTZ,
    activated_by VARCHAR(255),
    deprecated_at TIMESTAMPTZ,
    deprecated_by VARCHAR(255),
    deprecation_reason TEXT,
    related_process_ids VARCHAR[],
    process_metadata JSONB NOT NULL DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_processes_process_number ON processes (process_number);
CREATE INDEX IF NOT EXISTS idx_processes_project_id ON processes (project_id);
CREATE INDEX IF NOT EXISTS idx_processes_status ON processes (status);
CREATE INDEX IF NOT EXISTS idx_processes_project_status ON processes (project_id, status);
CREATE INDEX IF NOT EXISTS idx_processes_project_category ON processes (project_id, category);
CREATE INDEX IF NOT EXISTS idx_processes_is_active ON processes (is_active_version);
CREATE INDEX IF NOT EXISTS idx_processes_owner ON processes (owner);
CREATE INDEX IF NOT EXISTS idx_processes_category ON processes (category);
CREATE INDEX IF NOT EXISTS idx_processes_deleted_at ON processes (deleted_at);

CREATE TABLE IF NOT EXISTS process_executions (
    id VARCHAR(255) PRIMARY KEY,
    process_id VARCHAR(255) NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    execution_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_stage_id VARCHAR(255),
    completed_stages VARCHAR[],
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    initiated_by VARCHAR(255),
    completed_by VARCHAR(255),
    trigger_item_id UUID,
    context_data JSONB NOT NULL DEFAULT '{}',
    result_summary TEXT,
    output_item_ids VARCHAR[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_process_executions_process_id ON process_executions (process_id);
CREATE INDEX IF NOT EXISTS idx_process_executions_status ON process_executions (status);
CREATE INDEX IF NOT EXISTS idx_process_executions_execution_number ON process_executions (execution_number);
