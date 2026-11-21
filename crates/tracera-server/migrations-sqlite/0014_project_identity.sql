-- Canonical project identity shared by problems, product observations/baselines,
-- SWEE nodes and generic items. Additive only: existing rows are backfilled by
-- their existing scope identifiers, so no public route or response shape changes.

CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    metadata    TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC, id ASC);

-- Backfill from every existing scope. INSERT OR IGNORE makes reruns and
-- mixed-version writes safe; choosing the earliest timestamp preserves stable
-- creation times across scopes.
INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT p.project_id, p.project_id, NULL, '{}', p.created_at, p.updated_at
FROM problems p
WHERE p.project_id IS NOT NULL AND p.project_id <> '';

INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT i.project_id, i.project_id, NULL, '{}',
       COALESCE(json_extract(i.document, '$.createdAt'), strftime('%Y-%m-%dT%H:%M:%fZ','now')),
       COALESCE(json_extract(i.document, '$.updatedAt'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
FROM items i
WHERE i.project_id IS NOT NULL AND i.project_id <> '';

INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT json_extract(s.metadata, '$.project_id'), json_extract(s.metadata, '$.project_id'), NULL, '{}', s.created_at, s.updated_at
FROM swee_nodes s
WHERE json_extract(s.metadata, '$.project_id') IS NOT NULL
  AND json_extract(s.metadata, '$.project_id') <> '';

INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT b.product_id, b.product_id,
       'Canonical product baseline scope',
       json_object('kind','product','baseline',b.baseline),
       strftime('%Y-%m-%dT%H:%M:%fZ','now'),
       strftime('%Y-%m-%dT%H:%M:%fZ','now')
FROM product_observation_baselines b
WHERE b.product_id IS NOT NULL AND b.product_id <> '';

INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT o.product_id, o.product_id,
       'Canonical product observation scope', '{"kind":"product"}',
       strftime('%Y-%m-%dT%H:%M:%fZ','now'),
       strftime('%Y-%m-%dT%H:%M:%fZ','now')
FROM product_observations o
WHERE o.product_id IS NOT NULL AND o.product_id <> '';

-- Future writes register the same identity automatically. Triggers only fire
-- for real persisted rows, so discovery never invents placeholder projects.
CREATE TRIGGER IF NOT EXISTS projects_from_problems AFTER INSERT ON problems
WHEN NEW.project_id IS NOT NULL AND NEW.project_id <> ''
BEGIN
    INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
    VALUES (NEW.project_id, NEW.project_id, NULL, '{}', NEW.created_at, NEW.updated_at);
END;

CREATE TRIGGER IF NOT EXISTS projects_from_items AFTER INSERT ON items
WHEN NEW.project_id IS NOT NULL AND NEW.project_id <> ''
BEGIN
    INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
    VALUES (NEW.project_id, NEW.project_id, NULL, '{}',
            COALESCE(json_extract(NEW.document, '$.createdAt'), strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            COALESCE(json_extract(NEW.document, '$.updatedAt'), strftime('%Y-%m-%dT%H:%M:%fZ','now')));
END;

CREATE TRIGGER IF NOT EXISTS projects_from_swee_nodes AFTER INSERT ON swee_nodes BEGIN
    INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
    SELECT json_extract(NEW.metadata, '$.project_id'), json_extract(NEW.metadata, '$.project_id'),
           NULL, '{}', NEW.created_at, NEW.updated_at
    WHERE json_extract(NEW.metadata, '$.project_id') IS NOT NULL
      AND json_extract(NEW.metadata, '$.project_id') <> '';
END;

CREATE TRIGGER IF NOT EXISTS projects_from_product_baselines AFTER INSERT ON product_observation_baselines
WHEN NEW.product_id IS NOT NULL AND NEW.product_id <> ''
BEGIN
    INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
    VALUES (NEW.product_id, NEW.product_id, 'Canonical product baseline scope',
            json_object('kind','product','baseline',NEW.baseline),
            strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'));
END;

CREATE TRIGGER IF NOT EXISTS projects_from_product_observations AFTER INSERT ON product_observations
WHEN NEW.product_id IS NOT NULL AND NEW.product_id <> ''
BEGIN
    INSERT OR IGNORE INTO projects (id, name, description, metadata, created_at, updated_at)
    VALUES (NEW.product_id, NEW.product_id, 'Canonical product observation scope',
            '{"kind":"product"}', strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'));
END;

-- Read-only scope resolution view shared by product, baseline, SWEE and item rows.
CREATE VIEW IF NOT EXISTS project_scopes AS
SELECT 'problem' AS source_kind, id AS source_id, project_id AS project_id FROM problems WHERE deleted_at IS NULL
UNION ALL
SELECT 'item', id, project_id FROM items
UNION ALL
SELECT 'swee_node', CAST(id AS TEXT), json_extract(metadata, '$.project_id')
  FROM swee_nodes WHERE json_extract(metadata, '$.project_id') IS NOT NULL
UNION ALL
SELECT 'product_baseline', product_id || ':' || baseline, product_id FROM product_observation_baselines
UNION ALL
SELECT 'product_observation', product_id || ':' || observation_id, product_id FROM product_observations;
