-- Migration 013: authoritative product-scoped dependency ledger v1
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS product_dependency_edges_v1 (
    dependency_edge_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    dependency_ref TEXT NOT NULL,
    dependent_ref TEXT NOT NULL,
    authority TEXT NOT NULL CHECK (authority IN ('deterministic','accepted','declared','inferred')),
    revision TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0,1)),
    recorded_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_product_dependency_edges_scope
ON product_dependency_edges_v1(product_id, revision, active, dependency_ref);
