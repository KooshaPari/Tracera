# ADR-SWEE-001: Typed graph schema for the unified SWE-E evidence model

- **Status**: Accepted
- **Date**: 2026-08-30
- **Authors**: KooshaPari
- **Supersedes**: none
- **Related**: `store.rs:136-151` (current `TraceLink`), `migrations/0005_create_trace_links.sql`, `FEATURE_INVENTORY.md:273-282` (graph endpoints)

## Context

Tracera traces requirements through design, source, test, build, deployment, and incident evidence. The current graph is modelled ad-hoc across three layers:

1. A flat `trace_links` table (`store.rs:136-151`) with opaque `TEXT` source/target IDs and a free-form `relationship` string.
2. In-memory `CoverageMatrixRequest`/`CoverageMatrixResponse` structs (`main.rs:258-277`) that discard graph structure after each request.
3. Per-domain SQL tables (`evidence`, `stories`, `sprints`, `teams`, `problems`) with no shared identity or edge model.

This creates: no schema enforcement (any string is a valid node/edge type), no unified identity across ingest sources (GitHub issues vs Jira stories), and no governance gate for adding new types. The SWE-E (Software Engineering Evidence) model must unify all traceable entities into a single typed graph backed by a relational store.

## Decision drivers

1. **Type safety**: reject invalid node/edge-type combinations at write time.
2. **SQL backing**: remain queryable via Postgres and SQLite through the existing `Store` trait.
3. **Backward compatibility**: existing tables must function throughout the migration.
4. **Governance**: every type must be registered in a manifest auditable against ADRs.

## Decision

### Node taxonomy — 30 node types

Stored in a **unified `graph_nodes` table** with a `node_type` discriminator column.

| #   | Node Type        | Notes                                                   |
| --- | ---------------- | ------------------------------------------------------- |
| 1   | `requirement`    | Functional/non-functional requirement                   |
| 2   | `specification`  | Design/architectural spec document                      |
| 3   | `design`         | UI/UX design artefact                                   |
| 4   | `source_file`    | Individual source file                                  |
| 5   | `module`         | Crate, package, or library boundary                     |
| 6   | `class`          | Struct, class, or trait definition                      |
| 7   | `function`       | Method, function, or closure                            |
| 8   | `test`           | Individual test case                                    |
| 9   | `test_suite`     | Test grouping (e.g. `cargo test` target)                |
| 10  | `commit`         | Git commit                                              |
| 11  | `pull_request`   | GitHub/GitLab merge request                             |
| 12  | `branch`         | Git branch or tag                                       |
| 13  | `issue`          | GitHub Issue or Jira ticket                             |
| 14  | `epic`           | Parent work-unit grouping stories                       |
| 15  | `story`          | User story — supersedes `stories` table                 |
| 16  | `task`           | Sub-task under a story                                  |
| 17  | `bug`            | Defect record                                           |
| 18  | `sprint`         | Iteration container — supersedes `sprints` table        |
| 19  | `release`        | Versioned release (semver tag)                          |
| 20  | `build`          | CI/CD build execution                                   |
| 21  | `deployment`     | Deployment event to an environment                      |
| 22  | `evidence`       | Generic evidence artefact — supersedes `evidence` table |
| 23  | `problem`        | ITIL problem record — supersedes `problems` table       |
| 24  | `incident`       | Production incident or outage                           |
| 25  | `change_request` | RFC or change advisory record                           |
| 26  | `person`         | Contributor, author, or assignee                        |
| 27  | `team`           | Organisational team — supersedes `teams` table          |
| 28  | `environment`    | Target deployment environment                           |
| 29  | `artifact`       | Generic binary or package output                        |
| 30  | `metric`         | Observed measurement or SLO data point                  |

### Edge taxonomy — 35 edge types

Stored in a **unified `graph_edges` table** with an `edge_type` discriminator column.

| #   | Edge Type         | Source → Target                 | Meaning                        |
| --- | ----------------- | ------------------------------- | ------------------------------ |
| 1   | `implements`      | `requirement` → `source_file`   | Source satisfies a requirement |
| 2   | `specifies`       | `specification` → `requirement` | Spec elaborates a requirement  |
| 3   | `designs`         | `design` → `requirement`        | Design covers a requirement    |
| 4   | `contains`        | `module` → `class`              | Module owns a class/trait      |
| 5   | `contains`        | `class` → `function`            | Class owns a method/function   |
| 6   | `contains`        | `module` → `function`           | Module-level free function     |
| 7   | `depends_on`      | `module` → `module`             | Crate/package dependency       |
| 8   | `calls`           | `function` → `function`         | Runtime call edge              |
| 9   | `extends`         | `class` → `class`               | Inheritance or trait impl      |
| 10  | `tests`           | `test` → `source_file`          | Test exercises source          |
| 11  | `covers`          | `test` → `requirement`          | Test validates requirement     |
| 12  | `belongs_to`      | `test` → `test_suite`           | Test belongs to suite          |
| 13  | `authored_by`     | `commit` → `person`             | Commit author                  |
| 14  | `touches`         | `commit` → `source_file`        | Commit modifies file           |
| 15  | `targets`         | `pull_request` → `branch`       | PR targets branch              |
| 16  | `merges_from`     | `pull_request` → `branch`       | PR merges feature branch       |
| 17  | `fixes`           | `pull_request` → `issue`        | PR fixes an issue              |
| 18  | `resolves`        | `pull_request` → `bug`          | PR resolves a bug              |
| 19  | `supersedes`      | `pull_request` → `pull_request` | PR replaces earlier PR         |
| 20  | `references`      | `issue` → `commit`              | Issue references commit        |
| 21  | `blocks`          | `issue` → `issue`               | Blocking dependency            |
| 22  | `parent_of`       | `epic` → `story`                | Epic contains stories          |
| 23  | `parent_of`       | `story` → `task`                | Story decomposes into tasks    |
| 24  | `in_sprint`       | `story` → `sprint`              | Story assigned to sprint       |
| 25  | `owned_by`        | `story` → `team`                | Story assigned to team         |
| 26  | `linked_to`       | `story` → `issue`               | Cross-system link              |
| 27  | `derived_from`    | `evidence` → `commit`           | Evidence produced by commit    |
| 28  | `observed_in`     | `evidence` → `deployment`       | Evidence from a deployment     |
| 29  | `triggered_by`    | `incident` → `problem`          | Incident triggers problem      |
| 30  | `correlates_with` | `problem` → `incident`          | Bidirectional correlation      |
| 31  | `impacts`         | `issue` → `requirement`         | Issue threatens requirement    |
| 32  | `released_in`     | `source_file` → `release`       | File shipped in release        |
| 33  | `deployed_to`     | `release` → `environment`       | Release deployed to env        |
| 34  | `built_from`      | `build` → `commit`              | Build triggered by commit      |
| 35  | `emitted_by`      | `metric` → `build`              | Metric observed during build   |

### SQL backing

Two relational tables with `CHECK` constraints enforce valid types:

```sql
CREATE TABLE graph_nodes (
    id          TEXT PRIMARY KEY,
    node_type   TEXT NOT NULL CHECK (node_type IN (
        'requirement','specification','design','source_file','module',
        'class','function','test','test_suite','commit','pull_request',
        'branch','issue','epic','story','task','bug','sprint','release',
        'build','deployment','evidence','problem','incident',
        'change_request','person','team','environment','artifact','metric'
    )),
    label       TEXT NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE graph_edges (
    id          TEXT PRIMARY KEY,
    edge_type   TEXT NOT NULL CHECK (edge_type IN (
        'implements','specifies','designs','contains','depends_on',
        'calls','extends','tests','covers','belongs_to','authored_by',
        'touches','targets','merges_from','fixes','resolves','supersedes',
        'references','blocks','parent_of','in_sprint','owned_by',
        'linked_to','derived_from','observed_in','triggered_by',
        'correlates_with','impacts','released_in','deployed_to',
        'built_from','emitted_by'
    )),
    source_id   TEXT NOT NULL REFERENCES graph_nodes(id),
    target_id   TEXT NOT NULL REFERENCES graph_nodes(id),
    confidence  DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    source      TEXT NOT NULL DEFAULT 'manual',
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_graph_edges_source ON graph_edges (source_id);
CREATE INDEX ix_graph_edges_target ON graph_edges (target_id);
CREATE INDEX ix_graph_nodes_type  ON graph_nodes (node_type);
CREATE INDEX ix_graph_edges_type  ON graph_edges (edge_type);
```

Backward compatibility: SQL **view aliases** map the existing `trace_links` table into `graph_edges`; the `Store` trait gains `upsert_node`/`upsert_edge` methods alongside existing domain methods.

A **schema manifest** (`docs/governance/schema/graph_schema.json`) enumerates every registered type with source/target constraints. CI asserts the manifest matches the `CHECK` constraints.

## Consequences

### Positive

- **Type-safe traversal**: blast-radius, confidence, and coverage-matrix use validated types.
- **Cross-system joins**: GitHub issues, Jira stories, commits, and evidence share a common identity layer.
- **Governance auditability**: manifest is the single source of truth for ADR reviews.
- **Incremental migration**: existing tables work unchanged; dual-write populates graph tables.

### Negative

- **Migration effort**: two new tables, migration scripts, and dual-write logic for Postgres + SQLite.
- **Performance overhead**: `CHECK` constraints add minor write cost; mitigated by indexes.
- **Coordination**: downstream consumers (`tracera-edge`, `tracertm-mcp`, frontend) must adopt new types or keep using `trace_links`.

### Neutral

- `trace_links` remains read-compatible; `graph_edges` is additive.
- The 30/35 type counts are initial; the evolution policy governs additions.

## Schema evolution policy

1. **Additive only**: new types may be appended via migration. Removal requires a new ADR.
2. **Manifest-first**: edit the manifest, then add a migration `CHECK` value, then CI asserts alignment.
3. **Deprecation window**: deprecated types retain `CHECK` support for ≥2 release cycles (~8 weeks) before a removal ADR.
4. **Backward-compatible views**: legacy query patterns are preserved as SQL views during deprecation.
5. **ADR governance**: any type-count change requires a new ADR or update to this ADR, reviewed under `docs/governance/policy/adr_index.md`.

## References

- `crates/tracera-server/src/store.rs:80-195` — current domain types
- `crates/tracera-server/migrations/0005_create_trace_links.sql` — existing edge table
- `crates/tracera-server/src/main.rs:258-277` — coverage-matrix request/response
- `FEATURE_INVENTORY.md:273-282` — graph/analysis endpoint catalogue
- `docs/governance/policy/ADR-SERVER-001-endpoint-regression-audit.md` — tier-2 graph endpoints
