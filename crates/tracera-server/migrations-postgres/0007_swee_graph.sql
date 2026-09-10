-- 0007_swee_graph.sql (Postgres) — equivalent to SQLite 0008
-- Postgres uses SERIAL/BIGSERIAL for auto-increment, JSONB for metadata.
CREATE TABLE IF NOT EXISTS swee_nodes (
    id          BIGSERIAL PRIMARY KEY,
    node_type   TEXT NOT NULL,
    label       TEXT NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS swee_nodes_node_type_idx ON swee_nodes (node_type);

CREATE TABLE IF NOT EXISTS swee_edges (
    id          BIGSERIAL PRIMARY KEY,
    edge_type   TEXT NOT NULL,
    source_id   BIGINT NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    target_id   BIGINT NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    confidence  DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS swee_edges_source_idx ON swee_edges (source_id);
CREATE INDEX IF NOT EXISTS swee_edges_target_idx ON swee_edges (target_id);
