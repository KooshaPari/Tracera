-- Create code_entities table for indexing code entities
CREATE TABLE IF NOT EXISTS code_entities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    entity_type varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    full_name varchar(1024) NOT NULL,
    description text,
    file_path varchar(1024),
    line_number integer,
    end_line_number integer,
    column_number integer,
    code_snippet text,
    language varchar(50),
    signature text,
    return_type varchar(255),
    parameters jsonb,
    metadata jsonb,
    indexed_at timestamp NOT NULL DEFAULT now(),
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp
);

-- Create code_entity_relationships table
CREATE TABLE IF NOT EXISTS code_entity_relationships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    source_id uuid NOT NULL REFERENCES code_entities(id) ON DELETE CASCADE,
    target_id uuid NOT NULL REFERENCES code_entities(id) ON DELETE CASCADE,
    relation_type varchar(255) NOT NULL,
    metadata jsonb,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_code_entities_project_id ON code_entities(project_id);
CREATE INDEX IF NOT EXISTS idx_code_entities_entity_type ON code_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_code_entities_language ON code_entities(language);
CREATE INDEX IF NOT EXISTS idx_code_entities_deleted_at ON code_entities(deleted_at);
CREATE INDEX IF NOT EXISTS idx_code_entity_relationships_project_id ON code_entity_relationships(project_id);
CREATE INDEX IF NOT EXISTS idx_code_entity_relationships_source_id ON code_entity_relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_code_entity_relationships_target_id ON code_entity_relationships(target_id);
