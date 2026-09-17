-- 0010_product_model.sql (Postgres) — WP-07: Product-first graph semantics
-- Equivalent to SQLite 009_product_model.sql
-- Adds product identity layer above existing SWEE graph.
-- Backward compatible: existing nodes/edges untouched.
--
-- Tables added:
--   product_nodes  — product/capability/obligation/target identity
--   product_edges  — relationships between product nodes
-- Columns added:
--   swee_nodes.product_node_id — nullable FK linking SWEE nodes to the product layer

-- ──────────────────────────────────────────────────────────────────────
-- Product nodes — intent kinds: product, capability, obligation, target
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_nodes (
    id                  TEXT PRIMARY KEY,
    product_id          TEXT NOT NULL,
    intent_kind         TEXT NOT NULL
                        CHECK (intent_kind IN ('product', 'capability', 'obligation', 'target')),
    title               TEXT NOT NULL,
    description         TEXT DEFAULT '',
    status              TEXT NOT NULL DEFAULT 'accepted'
                        CHECK (status IN ('accepted', 'deferred', 'retired')),
    baseline_revision   INTEGER NOT NULL DEFAULT 1,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_product_nodes_product ON product_nodes(product_id);
CREATE INDEX IF NOT EXISTS idx_product_nodes_kind    ON product_nodes(intent_kind);

-- ──────────────────────────────────────────────────────────────────────
-- Product edges — directed relationships between product nodes
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_edges (
    id          BIGSERIAL PRIMARY KEY,
    source_id   TEXT NOT NULL REFERENCES product_nodes(id),
    target_id   TEXT NOT NULL REFERENCES product_nodes(id),
    edge_type   TEXT NOT NULL CHECK (edge_type IN (
                    'product_has_capability',
                    'capability_satisfies_obligation',
                    'obligation_bound_to_target',
                    'observation_covers_capability'
                )),
    weight      DOUBLE PRECISION DEFAULT 1.0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(source_id, target_id, edge_type)
);

CREATE INDEX IF NOT EXISTS idx_product_edges_source ON product_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_product_edges_target ON product_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_product_edges_type   ON product_edges(edge_type);

-- ──────────────────────────────────────────────────────────────────────
-- Cross-layer link: SWEE nodes → product nodes (nullable, backward compat)
-- ──────────────────────────────────────────────────────────────────────
ALTER TABLE swee_nodes ADD COLUMN IF NOT EXISTS product_node_id TEXT REFERENCES product_nodes(id);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_product ON swee_nodes(product_node_id);
