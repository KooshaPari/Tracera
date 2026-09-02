-- Migration 0008: SWEE Graph Schema (SQLite)
-- Creates the core graph tables for software engineering event encoding.

-- ──────────────────────────────────────────────────────────────────────
-- Nodes
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS swee_nodes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT    NOT NULL,          -- e.g. 'query', 'filter', 'join', 'aggregate'
    name        TEXT    NOT NULL,
    metadata    TEXT    DEFAULT '{}',      -- JSON blob for extensible properties
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_swee_nodes_type       ON swee_nodes(type);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_name       ON swee_nodes(name);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_created_at ON swee_nodes(created_at);

-- ──────────────────────────────────────────────────────────────────────
-- Edges
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS swee_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   INTEGER NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    target_id   INTEGER NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    type        TEXT    NOT NULL,          -- e.g. 'flow', 'dependency', 'causation'
    weight      REAL    NOT NULL DEFAULT 1.0,
    metadata    TEXT    DEFAULT '{}',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_swee_edges_source_id ON swee_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_swee_edges_target_id ON swee_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_swee_edges_type      ON swee_edges(type);
CREATE INDEX IF NOT EXISTS idx_swee_edges_created_at ON swee_edges(created_at);

-- Unique constraint to prevent duplicate directed edges.
CREATE UNIQUE INDEX IF NOT EXISTS idx_swee_edges_unique_pair
    ON swee_edges(source_id, target_id, type);

-- ──────────────────────────────────────────────────────────────────────
-- Node labels (supports full-text search / tagging)
-- ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS swee_node_labels (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id     INTEGER NOT NULL REFERENCES swee_nodes(id) ON DELETE CASCADE,
    label       TEXT    NOT NULL,
    namespace   TEXT    NOT NULL DEFAULT 'default'
);

CREATE INDEX IF NOT EXISTS idx_swee_node_labels_node_id   ON swee_node_labels(node_id);
CREATE INDEX IF NOT EXISTS idx_swee_node_labels_label     ON swee_node_labels(label);
CREATE INDEX IF NOT EXISTS idx_swee_node_labels_namespace ON swee_node_labels(namespace);

-- FTS5 virtual table for full-text search on node labels.
CREATE VIRTUAL TABLE IF NOT EXISTS swee_node_labels_fts USING fts5(
    label,
    namespace,
    content='swee_node_labels',
    content_rowid='id'
);

-- Triggers to keep FTS in sync with the labels table.
CREATE TRIGGER IF NOT EXISTS swee_node_labels_ai AFTER INSERT ON swee_node_labels BEGIN
    INSERT INTO swee_node_labels_fts(rowid, label, namespace)
    VALUES (new.id, new.label, new.namespace);
END;

CREATE TRIGGER IF NOT EXISTS swee_node_labels_ad AFTER DELETE ON swee_node_labels BEGIN
    INSERT INTO swee_node_labels_fts(swee_node_labels_fts, rowid, label, namespace)
    VALUES ('delete', old.id, old.label, old.namespace);
END;

CREATE TRIGGER IF NOT EXISTS swee_node_labels_au AFTER UPDATE ON swee_node_labels BEGIN
    INSERT INTO swee_node_labels_fts(swee_node_labels_fts, rowid, label, namespace)
    VALUES ('delete', old.id, old.label, old.namespace);
    INSERT INTO swee_node_labels_fts(rowid, label, namespace)
    VALUES (new.id, new.label, new.namespace);
END;
