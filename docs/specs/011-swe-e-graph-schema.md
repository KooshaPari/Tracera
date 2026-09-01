# 011 — SWE-E Graph Schema Specification

| Field          | Value                                                 |
| -------------- | ----------------------------------------------------- |
| **Spec ID**    | TRACERA-SPEC-011                                      |
| **Status**     | Draft                                                 |
| **Version**    | 2.0                                                   |
| **Date**       | 2026-08-30                                            |
| **Owner**      | Tracera Core Team                                     |
| **Applies to** | Graph engine, memory distillation pipeline, query API |

---

## 1. Purpose

Tracera's Software Engineering Environment (SWE-E) models the entire lifecycle of software delivery — from organizational governance through code generation to production telemetry — as a single, queryable property graph. This specification defines the canonical node types, edge types, storage schemas, query API, and performance targets that every Tracera component must adhere to.

---

## 2. Design Principles

| #   | Principle                            | Rationale                                                                 |
| --- | ------------------------------------ | ------------------------------------------------------------------------- |
| P1  | **Immutable facts, append-only log** | Every state change is a new graph mutation; nothing is overwritten.       |
| P2  | **Typed edges carry semantics**      | Edges are first-class citizens with properties, not bare arcs.            |
| P3  | **Dual-storage parity**              | SQLite (embedded/CI) and PostgreSQL (cluster) expose identical semantics. |
| P4  | **Sub-millisecond single-hop reads** | Hot-path lookups complete in < 1 ms p99.                                  |
| P5  | **Bitemporal support**               | Every node/edge carries `valid_from`/`valid_to` for historical replay.    |

---

## 3. Node Types (30)

Each node maps to a row in the `nodes` table, differentiated by `node_kind`. Required properties are marked with `*`.

### 3.1 Organizational & Planning (5)

| #   | Kind               | Required Properties                        | Description                            |
| --- | ------------------ | ------------------------------------------ | -------------------------------------- |
| 1   | `AgentNode`        | `id*`, `name*`, `model`, `status`          | AI/human agent in the SWE-E            |
| 2   | `TeamNode`         | `id*`, `name*`, `members[]`                | Cross-functional team                  |
| 3   | `OrganizationNode` | `id*`, `name*`, `tier`                     | Hierarchical org unit                  |
| 4   | `SpecNode`         | `id*`, `title*`, `version`, `status`       | Design spec tracked through governance |
| 5   | `GovernanceNode`   | `id*`, `policy_name*`, `enforcement_level` | Gate or policy enforced on mutations   |

### 3.2 Work Management (3)

| #   | Kind           | Required Properties                          | Description                |
| --- | -------------- | -------------------------------------------- | -------------------------- |
| 6   | `WorkItemNode` | `id*`, `title*`, `kind`, `priority`, `state` | Unit of planned work       |
| 7   | `SprintNode`   | `id*`, `name*`, `start_date*`, `end_date*`   | Time-boxed iteration       |
| 8   | `ReleaseNode`  | `id*`, `version*`, `channel`, `status`       | Shipped or planned release |

### 3.3 Source Control & Code (5)

| #   | Kind           | Required Properties                              | Description              |
| --- | -------------- | ------------------------------------------------ | ------------------------ |
| 9   | `CodeArtifact` | `id*`, `repo*`, `path*`, `language`, `loc`       | File or module in a repo |
| 10  | `CommitNode`   | `id*` (SHA), `author*`, `message*`, `timestamp*` | Git commit               |
| 11  | `BranchNode`   | `id*`, `name*`, `repo*`, `head_sha*`             | Git branch               |
| 12  | `PRNode`       | `id*`, `number*`, `repo*`, `title*`, `state`     | Pull/merge request       |
| 13  | `ReviewNode`   | `id*`, `reviewer*`, `pr_id*`, `decision`         | Code review              |

### 3.4 Quality & Testing (3)

| #   | Kind            | Required Properties                                        | Description          |
| --- | --------------- | ---------------------------------------------------------- | -------------------- |
| 14  | `TestNode`      | `id*`, `name*`, `suite_path`, `kind`                       | Individual test case |
| 15  | `TestSuiteNode` | `id*`, `name*`, `framework`, `file_path`                   | Collection of tests  |
| 16  | `TestRunNode`   | `id*`, `test_id*`, `commit_sha*`, `status*`, `duration_ms` | Test execution       |

### 3.5 CI/CD & Deployment (5)

| #   | Kind              | Required Properties                            | Description        |
| --- | ----------------- | ---------------------------------------------- | ------------------ |
| 17  | `BuildNode`       | `id*`, `system`, `status*`, `commit_sha*`      | CI build           |
| 18  | `PipelineNode`    | `id*`, `name*`, `provider`, `stages[]`         | CI/CD pipeline     |
| 19  | `DeployNode`      | `id*`, `environment*`, `version*`, `status*`   | Deployment event   |
| 20  | `EnvironmentNode` | `id*`, `name*`, `kind`, `provider`             | Target environment |
| 21  | `ContainerNode`   | `id*`, `image*`, `tag`, `digest`, `size_bytes` | Container artifact |

### 3.6 Observability (5)

| #   | Kind            | Required Properties                                       | Description            |
| --- | --------------- | --------------------------------------------------------- | ---------------------- |
| 22  | `MetricNode`    | `id*`, `name*`, `value*`, `timestamp*`, `labels{}`        | Time-series data point |
| 23  | `LogNode`       | `id*`, `source*`, `level*`, `message*`, `timestamp*`      | Structured log entry   |
| 24  | `TraceSpanNode` | `id*`, `trace_id*`, `span_id*`, `operation*`, `start_us*` | Distributed-trace span |
| 25  | `AlertNode`     | `id*`, `name*`, `severity*`, `fired_at*`                  | Monitoring alert       |
| 26  | `IncidentNode`  | `id*`, `title*`, `severity*`, `opened_at*`                | Production incident    |

### 3.7 Knowledge & Memory (4)

| #   | Kind                 | Required Properties                                     | Description                  |
| --- | -------------------- | ------------------------------------------------------- | ---------------------------- |
| 27  | `ResearchDocNode`    | `id*`, `title*`, `authors[]`, `url`                     | External research document   |
| 28  | `MemoryNode`         | `id*`, `kind`, `content*`, `confidence`, `source_ids[]` | Distilled memory             |
| 29  | `DecisionRecordNode` | `id*`, `title*`, `status`, `context`                    | Architecture Decision Record |
| 30  | `DependencyNode`     | `id*`, `name*`, `version_req`, `kind`, `ecosystem`      | External package             |

---

## 4. Edge Types (35)

| #   | Kind             | Source → Target           | Key Properties                    |
| --- | ---------------- | ------------------------- | --------------------------------- |
| 1   | `ASSIGNED_TO`    | WorkItem → Agent          | `assigned_at`, `unassigned_at`    |
| 2   | `BELONGS_TO`     | Agent → Team              | `joined_at`, `role`               |
| 3   | `REPORTS_TO`     | Team → Organization       | `effective_date`                  |
| 4   | `GOVERNS`        | Governance → WorkItem     | `policy_id`, `enforced_at`        |
| 5   | `REQUIRES_SPEC`  | WorkItem → Spec           | `required_at`                     |
| 6   | `PARENT_OF`      | WorkItem → WorkItem       | —                                 |
| 7   | `IN_SPRINT`      | WorkItem → Sprint         | `planned_at`, `completed_at`      |
| 8   | `SHIPS_IN`       | WorkItem → Release        | `target_release`                  |
| 9   | `MODIFIES`       | Commit → CodeArtifact     | `diff_stats`                      |
| 10  | `PARENT_COMMIT`  | Commit → Commit           | —                                 |
| 11  | `HEAD_OF`        | Commit → Branch           | `set_at`                          |
| 12  | `SUBMITTED_FOR`  | Branch → PR               | `submitted_at`                    |
| 13  | `TARGETS`        | PR → Branch               | —                                 |
| 14  | `AUTHORED_BY`    | PR → Agent                | `created_at`                      |
| 15  | `REVIEWS`        | Review → PR               | `submitted_at`                    |
| 16  | `DECIDED_BY`     | Review → Agent            | —                                 |
| 17  | `USES_TEST`      | TestSuite → Test          | —                                 |
| 18  | `EXECUTES`       | TestRun → Test            | —                                 |
| 19  | `TRIGGERED_BY`   | TestRun → Commit          | `trigger_type`                    |
| 20  | `BLOCKED_BY`     | TestRun → Build           | —                                 |
| 21  | `BUILT_FROM`     | Build → Commit            | `trigger_type`                    |
| 22  | `IN_PIPELINE`    | Build → Pipeline          | `stage`                           |
| 23  | `DEPLOYS`        | Deploy → Build            | `approved_by`                     |
| 24  | `DEPLOYED_TO`    | Deploy → Environment      | `region`, `strategy`              |
| 25  | `RUNS_IN`        | Container → Environment   | `replica_count`                   |
| 26  | `EMITS_METRIC`   | TraceSpan → Metric        | `correlation_id`                  |
| 27  | `LINKED_TRACE`   | Log → TraceSpan           | —                                 |
| 28  | `FIRING_ON`      | Alert → Metric            | `condition_expr`                  |
| 29  | `CAUSED_BY`      | Incident → Alert          | `detected_at`                     |
| 30  | `RELATED_TO`     | Incident → Commit         | `association`                     |
| 31  | `CITES`          | Spec → ResearchDoc        | —                                 |
| 32  | `DISTILLED_FROM` | Memory → _(any)_          | `distillation_algo`, `confidence` |
| 33  | `DEPENDS_ON`     | CodeArtifact → Dependency | `version_constraint`              |
| 34  | `DECIDED_DURING` | DecisionRecord → Sprint   | `decided_at`                      |
| 35  | `IMPLEMENTS`     | WorkItem → Spec           | —                                 |

---

## 5. SQL Schema

### 5.1 SQLite (Embedded / CI)

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT    NOT NULL,
    node_kind   TEXT    NOT NULL,
    properties  TEXT    NOT NULL DEFAULT '{}',
    valid_from  INTEGER NOT NULL DEFAULT (unixepoch('now')),
    valid_to    INTEGER,
    created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
    PRIMARY KEY (id, node_kind, valid_from)
) STRICT;

CREATE INDEX idx_nodes_kind   ON nodes (node_kind);
CREATE INDEX idx_nodes_valid  ON nodes (valid_from, valid_to);

CREATE TABLE IF NOT EXISTS edges (
    id          TEXT    NOT NULL,
    edge_kind   TEXT    NOT NULL,
    source_id   TEXT    NOT NULL,
    source_kind TEXT    NOT NULL,
    target_id   TEXT    NOT NULL,
    target_kind TEXT    NOT NULL,
    properties  TEXT    NOT NULL DEFAULT '{}',
    valid_from  INTEGER NOT NULL DEFAULT (unixepoch('now')),
    valid_to    INTEGER,
    created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
    PRIMARY KEY (id, edge_kind, valid_from)
) STRICT;

CREATE INDEX idx_edges_source ON edges (source_id, source_kind);
CREATE INDEX idx_edges_target ON edges (target_id, target_kind);
CREATE INDEX idx_edges_src_kind ON edges (source_id, edge_kind);
CREATE INDEX idx_edges_tgt_kind ON edges (target_id, edge_kind);

CREATE TABLE IF NOT EXISTS memory_nodes (
    node_id     TEXT    PRIMARY KEY,
    kind        TEXT    NOT NULL,
    confidence  REAL    NOT NULL DEFAULT 0.5,
    content     TEXT    NOT NULL,
    source_ids  TEXT    NOT NULL DEFAULT '[]',
    created_at  INTEGER NOT NULL DEFAULT (unixepoch('now')),
    updated_at  INTEGER NOT NULL DEFAULT (unixepoch('now'))
) STRICT;

CREATE INDEX idx_mem_kind ON memory_nodes (kind);
CREATE INDEX idx_mem_conf ON memory_nodes (confidence DESC);
```

### 5.2 PostgreSQL (Cluster)

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE TYPE node_kind AS ENUM (
    'agent','team','organization','spec','governance',
    'work_item','sprint','release','code_artifact','commit',
    'branch','pr','review','test','test_suite','test_run',
    'build','pipeline','deploy','environment','container',
    'metric','log','trace_span','alert','incident',
    'research_doc','memory','decision_record','dependency'
);

CREATE TYPE edge_kind AS ENUM (
    'assigned_to','belongs_to','reports_to','governs',
    'requires_spec','parent_of','in_sprint','ships_in',
    'modifies','parent_commit','head_of','submitted_for',
    'targets','authored_by','reviews','decided_by',
    'uses_test','executes','triggered_by','blocked_by',
    'built_from','in_pipeline','deploys','deployed_to',
    'runs_in','emits_metric','linked_trace','firing_on',
    'caused_by','related_to','cites','distilled_from',
    'depends_on','decided_during','implements'
);

CREATE TABLE IF NOT EXISTS nodes (
    id          UUID        NOT NULL,
    kind        node_kind   NOT NULL,
    properties  JSONB       NOT NULL DEFAULT '{}',
    valid_from  TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to    TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, kind, valid_from)
) PARTITION BY RANGE (valid_from);

CREATE INDEX idx_nodes_kind      ON nodes (kind);
CREATE INDEX idx_nodes_props_gin ON nodes USING GIN (properties);

CREATE TABLE IF NOT EXISTS edges (
    id          UUID        NOT NULL DEFAULT uuid_generate_v4(),
    kind        edge_kind   NOT NULL,
    source_id   UUID        NOT NULL,
    source_kind node_kind   NOT NULL,
    target_id   UUID        NOT NULL,
    target_kind node_kind   NOT NULL,
    properties  JSONB       NOT NULL DEFAULT '{}',
    valid_from  TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to    TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, kind, valid_from)
) PARTITION BY RANGE (valid_from);

CREATE INDEX idx_edges_source ON edges (source_id, source_kind);
CREATE INDEX idx_edges_target ON edges (target_id, target_kind);
CREATE INDEX idx_edges_props_gin ON edges USING GIN (properties);

CREATE TABLE IF NOT EXISTS memory_nodes (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    kind        TEXT        NOT NULL CHECK (kind IN ('fact','pattern','rule','episodic')),
    confidence  DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    content     TEXT        NOT NULL,
    source_ids  UUID[]      NOT NULL DEFAULT '{}',
    embedding   VECTOR(768),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_mem_embedding ON memory_nodes USING ivfflat (
    embedding vector_cosine_ops WITH (lists = 100)
);
```

---

## 6. Cypher-like Query API

Tracera exposes a Cypher-inspired query language compiled to SQL.

### 6.1 Syntax

```
MATCH (a:AgentNode)-[:ASSIGNED_TO]->(w:WorkItemNode)
WHERE w.properties.state = 'in_progress'
  AND a.properties.name = $agent_name
RETURN a, w
ORDER BY w.created_at DESC
LIMIT 25
```

### 6.2 Supported Clauses

| Clause                        | Description                                       |
| ----------------------------- | ------------------------------------------------- |
| `MATCH`                       | Pattern-matching on nodes/edges with type filters |
| `WHERE`                       | Predicate filters using JSON property access      |
| `RETURN`                      | Project fields or aggregates                      |
| `ORDER BY` / `LIMIT` / `SKIP` | Sorting and pagination                            |
| `OPTIONAL MATCH`              | Left-join semantics                               |
| `MERGE`                       | Create-or-match (idempotent inserts)              |
| `CREATE` / `SET`              | Insert or update nodes/edges                      |

### 6.3 Example: Failing Tests for a Commit

```cypher
MATCH (c:CommitNode {id: $sha})<-[:TRIGGERED_BY]-(tr:TestRunNode)
WHERE tr.properties.status = 'failed'
MATCH (tr)-[:EXECUTES]->(t:TestNode)
RETURN t.properties.name, tr.properties.failure_reason
ORDER BY t.properties.name
```

### 6.4 Compilation Pipeline

```
Cypher source → AST → Logical plan → SQL plan → Prepared statement → Result set
```

---

## 7. Memory Distillation Pipeline

### 7.1 Extraction Triggers

| Trigger              | Pattern                                                | Memory Kind |
| -------------------- | ------------------------------------------------------ | ----------- |
| Repeated failure     | Same test fails ≥ 3 times across commits by same agent | `pattern`   |
| Successful fix       | Commit fixes alert → incident resolved in 30 min       | `fact`      |
| Governance violation | Work item bypasses gate                                | `rule`      |
| Episodic replay      | Sprint retrospective summarizing outcomes              | `episodic`  |

### 7.2 Confidence Scoring

```
confidence = base_score * recency_factor * source_diversity * corroboration
```

| Factor             | Range  | Description                         |
| ------------------ | ------ | ----------------------------------- |
| `base_score`       | [0, 1] | Inherent signal strength            |
| `recency_factor`   | [0, 1] | Exponential decay: `exp(-λ * days)` |
| `source_diversity` | [0, 1] | Distinct source nodes (log-scaled)  |
| `corroboration`    | [1, 2] | Independent confirmations (capped)  |

Memories with `confidence < 0.1` after 90 days are archived. Re-scored nightly.

---

## 8. Performance Targets

| Metric                         | Target                    |
| ------------------------------ | ------------------------- |
| Single-hop node lookup         | < 0.5 ms p99              |
| Single-hop edge traversal      | < 1 ms p99                |
| 3-hop pattern match (Cypher)   | < 10 ms p99               |
| Bulk insert (10k nodes)        | < 200 ms                  |
| Memory distillation job        | < 5s per 10k source nodes |
| Concurrent read throughput     | > 50k queries/sec         |
| Write throughput (mixed edges) | > 5k writes/sec           |

---

## 9. Migration & Compatibility

| Rule | Description                                                 |
| ---- | ----------------------------------------------------------- |
| M1   | Forward-only migrations; no destructive ALTER in production |
| M2   | New `node_kind`/`edge_kind` values are additive             |
| M3   | SQLite schema is reference; PostgreSQL additions are opt-in |
| M4   | Schema version tracked in `_schema_version` table           |

---

## 10. Acceptance Criteria

| #     | Criterion                                                           |
| ----- | ------------------------------------------------------------------- |
| AC-01 | All 30 node types defined with required properties                  |
| AC-02 | All 35 edge types defined with source/target constraints            |
| AC-03 | SQLite schema compiles and passes all migration tests               |
| AC-04 | PostgreSQL schema compiles with enums, partitions, GIN indexes      |
| AC-05 | Cypher queries compile to valid SQL for all clause types            |
| AC-06 | Single-hop lookup < 0.5 ms p99 on reference dataset                 |
| AC-07 | Memory distillation produces valid MemoryNode instances             |
| AC-08 | Confidence scoring formula implemented and unit-tested              |
| AC-09 | Bitemporal queries return correct historical snapshots              |
| AC-10 | Dual-storage parity verified (SQLite ↔ PostgreSQL semantics match) |

---

_End of Spec 011 — TRACERA-SPEC-011 v2.0_
