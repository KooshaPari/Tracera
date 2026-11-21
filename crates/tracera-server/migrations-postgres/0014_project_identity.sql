-- Canonical project identity shared by problems, product observations/baselines,
-- SWEE nodes and generic items. Additive only: existing rows are backfilled by
-- their existing scope identifiers, so no public route or response shape changes.

CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at DESC, id ASC);

INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT p.project_id::text, p.project_id::text, NULL, '{}'::jsonb, p.created_at, p.updated_at
FROM problems p
WHERE p.project_id IS NOT NULL
ON CONFLICT (id) DO NOTHING;

INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT i.project_id, i.project_id, NULL, '{}'::jsonb,
       COALESCE((i.document::jsonb->>'createdAt')::timestamptz, now()),
       COALESCE((i.document::jsonb->>'updatedAt')::timestamptz, now())
FROM items i
WHERE i.project_id IS NOT NULL AND coalesce(length(i.project_id), 0) > 0
ON CONFLICT (id) DO NOTHING;

INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT s.metadata->>'project_id', s.metadata->>'project_id', NULL, '{}'::jsonb, s.created_at, s.updated_at
FROM swee_nodes s
WHERE s.metadata->>'project_id' IS NOT NULL
  AND coalesce(length(s.metadata->>'project_id'), 0) > 0
ON CONFLICT (id) DO NOTHING;

INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT b.product_id, b.product_id, 'Canonical product baseline scope',
       jsonb_build_object('kind','product','baseline',b.baseline), now(), now()
FROM product_observation_baselines b
WHERE b.product_id IS NOT NULL AND coalesce(length(b.product_id), 0) > 0
ON CONFLICT (id) DO NOTHING;

INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
SELECT DISTINCT o.product_id, o.product_id, 'Canonical product observation scope',
       '{"kind":"product"}'::jsonb, now(), now()
FROM product_observations o
WHERE o.product_id IS NOT NULL AND coalesce(length(o.product_id), 0) > 0
ON CONFLICT (id) DO NOTHING;


CREATE OR REPLACE FUNCTION projects_register_problem() RETURNS trigger AS $$
BEGIN
    IF NEW.project_id IS NOT NULL AND coalesce(length(NEW.project_id), 0) > 0 THEN
        INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
        VALUES (NEW.project_id::text, NEW.project_id::text, NULL, '{}'::jsonb, NEW.created_at, NEW.updated_at)
        ON CONFLICT (id) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS projects_from_problems ON problems;
CREATE TRIGGER projects_from_problems AFTER INSERT ON problems
FOR EACH ROW EXECUTE FUNCTION projects_register_problem();

CREATE OR REPLACE FUNCTION projects_register_item() RETURNS trigger AS $$
BEGIN
    IF NEW.project_id IS NOT NULL AND coalesce(length(NEW.project_id), 0) > 0 THEN
        INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
        VALUES (NEW.project_id, NEW.project_id, NULL, '{}'::jsonb,
                COALESCE((NEW.document::jsonb->>'createdAt')::timestamptz, now()),
                COALESCE((NEW.document::jsonb->>'updatedAt')::timestamptz, now()))
        ON CONFLICT (id) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS projects_from_items ON items;
CREATE TRIGGER projects_from_items AFTER INSERT ON items
FOR EACH ROW EXECUTE FUNCTION projects_register_item();

CREATE OR REPLACE FUNCTION projects_register_swee_node() RETURNS trigger AS $$
BEGIN
    IF NEW.metadata->>'project_id' IS NOT NULL AND coalesce(length(NEW.metadata->>'project_id'), 0) > 0 THEN
        INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
        VALUES (NEW.metadata->>'project_id', NEW.metadata->>'project_id', NULL, '{}'::jsonb, NEW.created_at, NEW.updated_at)
        ON CONFLICT (id) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS projects_from_swee_nodes ON swee_nodes;
CREATE TRIGGER projects_from_swee_nodes AFTER INSERT ON swee_nodes
FOR EACH ROW EXECUTE FUNCTION projects_register_swee_node();

CREATE OR REPLACE FUNCTION projects_register_product() RETURNS trigger AS $$
BEGIN
    IF NEW.product_id IS NOT NULL AND coalesce(length(NEW.product_id), 0) > 0 THEN
        INSERT INTO projects (id, name, description, metadata, created_at, updated_at)
        VALUES (NEW.product_id, NEW.product_id, 'Canonical product scope',
                jsonb_build_object('kind','product'), now(), now())
        ON CONFLICT (id) DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS projects_from_product_baselines ON product_observation_baselines;
CREATE TRIGGER projects_from_product_baselines AFTER INSERT ON product_observation_baselines
FOR EACH ROW EXECUTE FUNCTION projects_register_product();

DROP TRIGGER IF EXISTS projects_from_product_observations ON product_observations;
CREATE TRIGGER projects_from_product_observations AFTER INSERT ON product_observations
FOR EACH ROW EXECUTE FUNCTION projects_register_product();

CREATE OR REPLACE VIEW project_scopes AS
SELECT 'problem'::text AS source_kind, id::text AS source_id, project_id::text AS project_id FROM problems WHERE deleted_at IS NULL
UNION ALL
SELECT 'item', id, project_id FROM items
UNION ALL
SELECT 'swee_node', id::text, metadata->>'project_id' FROM swee_nodes WHERE metadata->>'project_id' IS NOT NULL
UNION ALL
SELECT 'product_baseline', product_id || ':' || baseline, product_id FROM product_observation_baselines
UNION ALL
SELECT 'product_observation', product_id || ':' || observation_id, product_id FROM product_observations;
