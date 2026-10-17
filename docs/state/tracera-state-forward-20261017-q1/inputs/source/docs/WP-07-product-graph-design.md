# WP-07: Product-First Graph Semantics — Design Document

> **Status:** Draft  
> **Author:** Jcode (automated)  
> **Date:** 2026-09-16  
> **Work Package:** WP-07 — Implement product-first graph semantics with migration

---

## 1. Problem Statement

The existing SWEE (Software Engineering Evidence) graph encodes code-level relationships (source files, tests, commits, etc.) but has no concept of *product intent*. Product managers and engineering leads need to express:

- What the product is and what it should do (**capabilities**)
- What constraints or acceptance criteria must hold (**obligations**)
- What measurable outcomes define success (**targets**)
- How these product concepts relate to the implementation evidence already in the graph

WP-07 adds a **product identity layer** that sits above the SWEE graph without disturbing existing data or queries.

---

## 2. Current Schema (Baseline)

### SQLite (`migrations-sqlite/0008_swee_graph.sql`)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `swee_nodes` | `id INTEGER PK`, `type TEXT`, `name TEXT`, `metadata TEXT` | Graph nodes (30 types via NodeKind) |
| `swee_edges` | `id INTEGER PK`, `source_id FK`, `target_id FK`, `type TEXT`, `weight REAL` | Directed edges (32 types via EdgeKind) |
| `swee_node_labels` | `id INTEGER PK`, `node_id FK`, `label TEXT`, `namespace TEXT` | Full-text searchable labels |

### Postgres (`migrations-postgres/0007_swee_graph.sql`)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `swee_nodes` | `id BIGSERIAL PK`, `node_type TEXT`, `label TEXT`, `metadata JSONB` | Graph nodes |
| `swee_edges` | `id BIGSERIAL PK`, `edge_type TEXT`, `source_id FK`, `target_id FK`, `confidence DOUBLE` | Directed edges |

### Rust Types (`crates/tracera-server/src/swee/`)

- **NodeKind** — 30 variants (Requirement, Specification, Design, SourceFile, Module, Class, Function, Test, TestSuite, Commit, PullRequest, Branch, Issue, Epic, Story, Task, Bug, Sprint, Release, Build, Deployment, Evidence, Problem, Incident, ChangeRequest, Person, Team, Environment, Artifact, Metric)
- **EdgeKind** — 32 unique string variants mapping to 35 semantic definitions (Implements, Specifies, Designs, Contains, DependsOn, Calls, Extends, Tests, Covers, BelongsTo, etc.)

---

## 3. Product Hierarchy Types

### 3.1 Concept Model

```
Product ──has──▶ Capability ──satisfies──▶ Obligation ──bound_to──▶ Target
                                                                  │
                                        Observation ──covers──▶ ──┘
```

Four new `intent_kind` discriminators, each mapping to a distinct role:

| Kind | Purpose | Maps to SWEE | Example |
|------|---------|--------------|---------|
| **product** | Top-level identity; the thing being built | New `product_nodes` table (standalone) | "Tracera v2" |
| **capability** | What the product can do | Links to SWEE `Requirement` nodes | "Real-time trace graph" |
| **obligation** | What must be true (acceptance criteria) | Links to SWEE `Test` / `Evidence` nodes | "Graph query < 200ms p99" |
| **target** | Measurable outcome / SLO | Links to SWEE `Metric` nodes | "99.9% uptime" |

### 3.2 Why a Separate Table?

Product nodes differ from SWEE nodes in three ways:

1. **Identity scope** — A product node is scoped by `product_id` (a logical product identifier), whereas SWEE nodes are scoped by the codebase.
2. **Lifecycle** — Product nodes have `status` (accepted/deferred/retired) and `baseline_revision` for versioning. SWEE nodes do not.
3. **Traversal boundary** — Product graph traversal must be bounded and cycle-safe (see §5). Mixing product and SWEE nodes in one table would complicate cycle detection and budget enforcement.

Therefore, product nodes live in their own `product_nodes` table, linked to SWEE nodes via a nullable `product_node_id` FK on `swee_nodes`.

---

## 4. New Edge Types

### 4.1 Product Edge Taxonomy

| Edge Type | Source Kind | Target Kind | Description |
|-----------|-------------|-------------|-------------|
| `product_has_capability` | product | capability | Product declares a capability |
| `capability_satisfies_obligation` | capability | obligation | Capability fulfills an obligation |
| `obligation_bound_to_target` | obligation | target | Obligation references a measurable target |
| `observation_covers_capability` | (any) | capability | An observation/evidence covers a capability |

### 4.2 Cross-Layer Links

Product-to-SWEE links use the `product_node_id` FK on `swee_nodes`:

```
product_nodes(id)  ←──  swee_nodes.product_node_id
```

This allows queries like:

```sql
-- Find all SWEE nodes linked to a specific capability
SELECT sn.* FROM swee_nodes sn
JOIN product_nodes pn ON sn.product_node_id = pn.id
WHERE pn.intent_kind = 'capability'
  AND pn.product_id = 'tracera-v2';
```

---

## 5. Schema Migration

### 5.1 New Tables

#### `product_nodes`

```sql
CREATE TABLE IF NOT EXISTS product_nodes (
    id                  TEXT PRIMARY KEY,         -- UUID
    product_id          TEXT NOT NULL,             -- logical product identifier
    intent_kind         TEXT NOT NULL              -- 'product'|'capability'|'obligation'|'target'
                        CHECK (intent_kind IN ('product','capability','obligation','target')),
    title               TEXT NOT NULL,
    description         TEXT DEFAULT '',
    status              TEXT NOT NULL DEFAULT 'accepted'
                        CHECK (status IN ('accepted','deferred','retired')),
    baseline_revision   INTEGER NOT NULL DEFAULT 1,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
```

#### `product_edges`

```sql
CREATE TABLE IF NOT EXISTS product_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   TEXT NOT NULL REFERENCES product_nodes(id),
    target_id   TEXT NOT NULL REFERENCES product_nodes(id),
    edge_type   TEXT NOT NULL CHECK (edge_type IN (
                    'product_has_capability',
                    'capability_satisfies_obligation',
                    'obligation_bound_to_target',
                    'observation_covers_capability'
                )),
    weight      REAL DEFAULT 1.0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_id, target_id, edge_type)
);
```

### 5.2 ALTER on Existing Table

```sql
-- Link SWEE nodes to product layer (nullable for backward compat)
ALTER TABLE swee_nodes ADD COLUMN product_node_id TEXT REFERENCES product_nodes(id);
CREATE INDEX IF NOT EXISTS idx_swee_nodes_product ON swee_nodes(product_node_id);
```

### 5.3 Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| `product_nodes` | `idx_product_nodes_product` | `product_id` | Filter by product |
| `product_nodes` | `idx_product_nodes_kind` | `intent_kind` | Filter by kind |
| `product_edges` | `idx_product_edges_source` | `source_id` | Outbound traversal |
| `product_edges` | `idx_product_edges_target` | `target_id` | Inbound traversal |
| `product_edges` | `idx_product_edges_type` | `edge_type` | Filter by edge type |
| `swee_nodes` | `idx_swee_nodes_product` | `product_node_id` | Cross-layer join |

---

## 6. Bounded Traversal Algorithm

### 6.1 Requirements

- Must not infinite-loop on cycles (product graphs can have bidirectional obligations)
- Must be responsive (bounded time even on large graphs)
- Must report when truncation occurred

### 6.2 Algorithm: Budget-Limited BFS

```
function bounded_traverse(start_id, max_depth, max_nodes):
    visited = set()
    queue = [(start_id, 0)]
    result = []
    truncated = false

    while queue is not empty AND len(visited) < max_nodes:
        node_id, depth = queue.pop_front()

        if node_id in visited:
            continue                    -- cycle detection
        if depth > max_depth:
            truncated = true
            continue                    -- depth budget exceeded

        visited.add(node_id)
        result.append(node_id)

        for edge in outgoing_edges(node_id):
            if edge.target_id not in visited:
                queue.append((edge.target_id, depth + 1))

    return TraversalResult {
        nodes: result,
        truncated: truncated OR len(visited) >= max_nodes,
        visited_count: len(visited),
        budget_remaining: max_nodes - len(visited)
    }
```

### 6.3 Recommended Defaults

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `max_depth` | 10 | Product hierarchies rarely exceed 5 levels |
| `max_nodes` | 1000 | Prevents runaway queries on dense graphs |

### 6.4 Truncation Reporting

Every traversal response includes:

```json
{
  "nodes": [...],
  "truncated": true,
  "visited_count": 1000,
  "budget_remaining": 0,
  "truncation_reason": "max_nodes"
}
```

Truncation reasons: `max_depth`, `max_nodes`, or `timeout`.

---

## 7. Migration Safety

### 7.1 Backward Compatibility

- **No existing columns are modified or dropped.** The ALTER only adds a nullable column.
- **No existing data is touched.** Existing `swee_nodes` rows have `product_node_id = NULL`.
- **Existing queries are unaffected.** All new tables are additive.
- **Rust types are unchanged.** No source files are modified in this WP.

### 7.2 Rollback Path

SQLite does not support `ALTER TABLE DROP COLUMN` prior to 3.35.0. Rollback strategy:

1. **Postgres:** `ALTER TABLE swee_nodes DROP COLUMN product_node_id;` then drop new tables.
2. **SQLite:** Rebuild the database from the pre-migration backup. Since `product_node_id` is nullable and no code references it yet, a "soft rollback" is simply ignoring the column.
3. **Application-level:** The Rust code added in subsequent WPs should check for column existence before querying.

### 7.3 Parity Check Queries

After migration, run these to verify both databases match:

```sql
-- Check product_nodes table exists and is empty
SELECT COUNT(*) FROM product_nodes;  -- expected: 0

-- Check product_edges table exists and is empty
SELECT COUNT(*) FROM product_edges;  -- expected: 0

-- Check product_node_id column exists on swee_nodes
-- SQLite:  PRAGMA table_info(swee_nodes);  -- look for product_node_id
-- Postgres: SELECT column_name FROM information_schema.columns
--           WHERE table_name = 'swee_nodes' AND column_name = 'product_node_id';

-- Verify no NULL product_node_id issues (should all be NULL initially)
SELECT COUNT(*) FROM swee_nodes WHERE product_node_id IS NOT NULL;  -- expected: 0
```

---

## 8. Migration Files

| Database | File | Sequence |
|----------|------|----------|
| SQLite | `migrations-sqlite/009_product_model.sql` | After 0008_swee_graph.sql |
| Postgres | `migrations-postgres/0010_product_model.sql` | After 0009_seed_swiftride.sql |

---

## 9. Open Questions

1. **Should product nodes be soft-deletable?** Currently `status = 'retired'` is the lifecycle endpoint. If we need audit trail, add `deleted_at TIMESTAMPTZ NULL` later.
2. **Cross-product edges?** The current schema scopes edges within a single `product_id`. If two products share an obligation, the same `product_nodes` row can serve both via `product_id` filtering, or we may need cross-product edge types in a future WP.
3. **FTS on product nodes?** Should `product_nodes.title` and `product_nodes.description` get FTS5/`tsvector` indexes? Deferred to WP-08 unless requested.

---

## 10. Related Documents

- `docs/governance/ADR-SWEE-001-graph-schema-design.md` — Original SWEE graph ADR
- `crates/tracera-server/src/swee/mod.rs` — Rust types for SWEE graph
- `crates/tracera-server/src/swee/node_kind.rs` — 30 NodeKind variants
- `crates/tracera-server/src/swee/edge_kind.rs` — 32 EdgeKind variants
