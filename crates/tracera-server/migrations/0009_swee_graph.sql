-- Migration 0009: SWEE Graph Schema (PostgreSQL)
-- Creates the core graph tables for software engineering event encoding.
-- Uses JSONB for metadata and GIN indexes for efficient queries.

BEGIN;

-- ──────────────────────────────────────────────────────────────────────
-- Nodes
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS swee_nodes (
    id          BIGSERIAL PRIMARY KEY,
    type        VARCHAR(128)  NOT NULL,
    name        TEXT          NOT NULL,
    metadata    JSONB         NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_swee_nodes_type       ON swee_nodes(type);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_name       ON swee_nodes(name);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_created_at ON swee_nodes(created_at);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_metadata   ON swee_nodes USING gin(metadata);

-- ──────────────────────────────────────────────────────────────────────
-- Edges
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS swee_edges (
    id          BIGSERIAL PRIMARY KEY,
    source_id   BIGINT        NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    target_id   BIGINT        NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    type        VARCHAR(128)  NOT NULL,
    weight      DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    metadata    JSONB         NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT chk_no_self_loop CHECK (source_id <> target_id)
);

CREATE INDEX IF NOT EXISTS idx_swee_edges_source_id ON swee_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_swee_edges_target_id ON swee_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_swee_edges_type      ON swee_edges(type);
CREATE INDEX IF NOT EXISTS idx_swee_edges_created_at ON swee_edges(created_at);
CREATE INDEX IF NOT EXISTS idx_swee_edges_metadata  ON swee_edges USING gin(metadata);

-- Unique constraint to prevent duplicate directed edges.
CREATE UNIQUE INDEX IF NOT EXISTS idx_swee_edges_unique_pair
    ON swee_edges(source_id, target_id, type);

-- Partial index for high-weight edges (useful for hot-path queries).
CREATE INDEX IF NOT EXISTS idx_swee_edges_high_weight
    ON swee_edges(source_id, target_id)
    WHERE weight >= 0.8;

-- ──────────────────────────────────────────────────────────────────────
-- Node labels (supports full-text search / tagging)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS swee_node_labels (
    id          BIGSERIAL PRIMARY KEY,
    node_id     BIGINT        NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    label       TEXT          NOT NULL,
    namespace   VARCHAR(128)  NOT NULL DEFAULT 'default'
);

CREATE INDEX IF NOT EXISTS idx_swee_node_labels_node_id   ON swee_node_labels(node_id);
CREATE INDEX IF NOT EXISTS idx_swee_node_labels_label     ON swee_node_labels(label);
CREATE INDEX IF NOT EXISTS idx_swee_node_labels_namespace ON swee_node_labels(namespace);

-- GIN index for full-text search on labels.
CREATE INDEX IF NOT EXISTS idx_swee_node_labels_fts
    ON swee_node_labels USING gin(to_tsvector('english', label));

-- Materialised view for graph statistics (refresh on schedule or trigger).
CREATE MATERIALIZED VIEW IF NOT EXISTS swee_graph_stats AS
SELECT
    n.type                                          AS node_type,
    count(DISTINCT n.id)                            AS node_count,
    count(DISTINCT e.id)                            AS edge_count,
    avg(e.weight)                                   AS avg_edge_weight,
    max(e.created_at)                               AS last_edge_at
FROM swee_nodes n
LEFT JOIN swee_edges e ON e.source_id = n.id OR e.target_id = n.id
GROUP BY n.type;

CREATE UNIQUE INDEX IF NOT EXISTS idx_swee_graph_stats_type
    ON swee_graph_stats(node_type);

COMMIT;