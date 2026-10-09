-- Canonical project graph imported through /api/v1/import. Distinct from product intent and ingest traces.
CREATE TABLE canonical_projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE canonical_items (
    project_id TEXT NOT NULL REFERENCES canonical_projects(id) ON DELETE CASCADE,
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    view TEXT NOT NULL,
    item_type TEXT NOT NULL,
    status TEXT NOT NULL,
    description TEXT,
    version BIGINT,
    PRIMARY KEY (project_id, id)
);
CREATE TABLE canonical_links (
    project_id TEXT NOT NULL REFERENCES canonical_projects(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    link_type TEXT NOT NULL,
    PRIMARY KEY (project_id, source_id, target_id, link_type),
    FOREIGN KEY (project_id, source_id) REFERENCES canonical_items(project_id, id) ON DELETE CASCADE,
    FOREIGN KEY (project_id, target_id) REFERENCES canonical_items(project_id, id) ON DELETE CASCADE
);
CREATE INDEX canonical_links_target ON canonical_links(project_id, target_id);
