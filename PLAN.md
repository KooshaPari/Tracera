# TracerTM — Implementation Plan

**Project**: TracerTM (Requirements Traceability Matrix)
**Document Version**: 1.0
**Last Updated**: 2026-03-27
**Status**: Active

Phased Work Breakdown Structure with DAG dependencies. Tasks have explicit predecessors;
no cycles. Effort is stated in agent terms (tool calls / parallel subagent batches).

Extended planning detail (magic I/O, milestone criteria) lives in `docs/PLAN.md`.

---

## Phase Overview

```
Phase 1: Foundation & Core RTM        [P1.*]  -- Q2 2026
Phase 2: Graph & Impact Analysis      [P2.*]  -- Q3 2026
Phase 3: Collaboration & PM           [P3.*]  -- Q4 2026
Phase 4: Compliance & Governance      [P4.*]  -- Q1 2027
Phase 5: Agent & MCP Integration      [P5.*]  -- Q1 2027
Phase 6: Observability & Hardening    [P6.*]  -- Q2 2027
```

---

## Phase 1: Foundation & Core RTM

**Goal**: Deployable system with requirement CRUD, RTM matrix, code linking, and test
coverage linking. Multi-tenant RBAC in place.

### Task Table

| Task ID | Description                                 | Depends On      | Effort        |
|---------|---------------------------------------------|-----------------|---------------|
| P1.1    | PostgreSQL schema (requirements, users,     | —               | 5 tool calls  |
|         | organizations, projects, links, audit_log)  |                 |               |
| P1.2    | Go backend: RBAC middleware + JWT auth      | P1.1            | 8 tool calls  |
| P1.3    | Go backend: requirement CRUD endpoints      | P1.2            | 6 tool calls  |
| P1.4    | Go backend: code link endpoints             | P1.3            | 5 tool calls  |
| P1.5    | Go backend: test coverage link endpoints    | P1.3            | 5 tool calls  |
| P1.6    | Go backend: GitHub webhook ingestion        | P1.4            | 6 tool calls  |
| P1.7    | Python: code annotation parser              | P1.4            | 4 tool calls  |
| P1.8    | Python: pytest/Jest test result ingestion   | P1.5            | 4 tool calls  |
| P1.9    | Frontend: RTM matrix view                   | P1.3, P1.4, P1.5| 10 tool calls |
| P1.10   | Frontend: requirement CRUD forms            | P1.3            | 6 tool calls  |
| P1.11   | Frontend: auth (login, OAuth2, JWT refresh) | P1.2            | 6 tool calls  |
| P1.12   | Atlas migrations: baseline schema           | P1.1            | 2 tool calls  |
| P1.13   | Unit + integration tests: Go backend        | P1.3–P1.6       | 8 tool calls  |
| P1.14   | Unit + integration tests: Python            | P1.7, P1.8      | 4 tool calls  |
| P1.15   | Frontend: component tests (Vitest)          | P1.9, P1.10     | 4 tool calls  |
| P1.16   | E2E tests: Playwright (matrix, auth, CRUD)  | P1.9–P1.11      | 6 tool calls  |
| P1.17   | CI: quality gate workflow                   | P1.13–P1.16     | 3 tool calls  |
| P1.18   | Documentation: 00_START_HERE.md, API ref    | P1.17           | 3 tool calls  |

### Phase 1 DAG (text)

```
P1.1
 ├── P1.12
 └── P1.2
      ├── P1.3
      │    ├── P1.4 ──── P1.6 ──── (P1.13)
      │    │    └── P1.7 ────────── (P1.14)
      │    ├── P1.5 ──── P1.8 ────── (P1.14)
      │    └── P1.9 (also needs P1.4, P1.5)
      │         └── P1.16
      ├── P1.10 ── P1.16
      └── P1.11 ── P1.16
P1.13 + P1.14 + P1.15 ── P1.17 ── P1.18
```

### Phase 1 Exit Criteria

- All FR-RTM-001 through FR-RTM-004 pass acceptance tests.
- All FR-LINK-001 through FR-LINK-003 pass acceptance tests.
- All FR-TEST-001 through FR-TEST-003 pass acceptance tests.
- RTM matrix loads <2 s with 1 000 seeded requirements.
- Go backend test coverage >= 80 %.
- Python test coverage >= 80 %.
- CI quality gate green.

---

## Phase 2: Graph & Impact Analysis

**Goal**: Neo4j-backed dependency graph, interactive visualization, impact analysis,
and critical path computation.

**Prerequisite**: Phase 1 complete.

### Task Table

| Task ID | Description                                   | Depends On       | Effort       |
|---------|-----------------------------------------------|------------------|--------------|
| P2.1    | Neo4j schema: nodes (Requirement), edges      | P1.1             | 3 tool calls |
|         | (depends_on, blocks, relates_to, supersedes)  |                  |              |
| P2.2    | Go backend: Neo4j sync job (Postgres → Neo4j) | P2.1, P1.3       | 6 tool calls |
| P2.3    | Go backend: graph query endpoints             | P2.2             | 5 tool calls |
|         | (neighbors, descendants, impact_set)          |                  |              |
| P2.4    | Go backend: critical path algorithm           | P2.3             | 4 tool calls |
| P2.5    | Go backend: circular dependency detection     | P2.3             | 3 tool calls |
| P2.6    | Go backend: risk scoring endpoint             | P2.4, P2.5       | 3 tool calls |
| P2.7    | Frontend: interactive dependency graph        | P2.3             | 10 tool calls|
|         | (zoom, pan, node filter, edge labels)         |                  |              |
| P2.8    | Frontend: impact analysis panel               | P2.4, P2.7       | 5 tool calls |
| P2.9    | Frontend: critical path highlight             | P2.4, P2.7       | 3 tool calls |
| P2.10   | Unit tests: graph algorithms                  | P2.4, P2.5, P2.6 | 5 tool calls |
| P2.11   | Integration tests: Neo4j sync correctness     | P2.2             | 4 tool calls |
| P2.12   | E2E tests: graph visualization                | P2.7–P2.9        | 4 tool calls |

### Phase 2 DAG (text)

```
P2.1
 └── P2.2
      └── P2.3
           ├── P2.4 ── P2.6 ── P2.8
           │    └── P2.9 (needs P2.7)
           ├── P2.5 ── P2.6
           └── P2.7 ── P2.8, P2.9, P2.12
P2.10, P2.11 parallel after respective task deps
```

### Phase 2 Exit Criteria

- FR-GRAPH-001 through FR-GRAPH-004 pass acceptance tests.
- Impact analysis query <100 ms for graphs with 500 nodes.
- Circular dependency detection catches all cycles in test suite.
- Neo4j and PostgreSQL stay consistent after 1 000 create/update operations.

---

## Phase 3: Collaboration & Project Management

**Goal**: Real-time WebSocket collaboration, Kanban board, sprint planning, comments.

**Prerequisite**: Phase 1 complete. Phase 2 optional (graph panel reuses graph endpoints).

### Task Table

| Task ID | Description                                      | Depends On        | Effort        |
|---------|--------------------------------------------------|-------------------|---------------|
| P3.1    | Go backend: WebSocket hub (per-project pool)     | P1.2              | 8 tool calls  |
| P3.2    | Go backend: NATS fan-out to WebSocket clients    | P3.1, P1.6 (NATS) | 5 tool calls  |
| P3.3    | Go backend: comments API (CRUD + threading)      | P1.3              | 5 tool calls  |
| P3.4    | Go backend: Kanban state machine endpoints       | P1.3              | 4 tool calls  |
| P3.5    | Go backend: sprint endpoints (create, assign,    | P3.4              | 5 tool calls  |
|         | burn-down, velocity)                             |                   |               |
| P3.6    | Frontend: Kanban board (drag-and-drop)           | P3.4              | 8 tool calls  |
| P3.7    | Frontend: real-time presence indicators          | P3.1, P3.2        | 4 tool calls  |
| P3.8    | Frontend: comment thread component               | P3.3              | 5 tool calls  |
| P3.9    | Frontend: sprint planning panel                  | P3.5              | 5 tool calls  |
| P3.10   | Frontend: burn-down chart                        | P3.5, P3.9        | 3 tool calls  |
| P3.11   | Unit tests: WebSocket hub, NATS fan-out          | P3.1, P3.2        | 4 tool calls  |
| P3.12   | Integration tests: comment threading             | P3.3              | 3 tool calls  |
| P3.13   | E2E tests: concurrent editing scenario           | P3.6, P3.7, P3.8  | 5 tool calls  |

### Phase 3 DAG (text)

```
P1.2 ──► P3.1 ──► P3.2 ──► P3.7 ──► P3.13
P1.3 ──► P3.3 ──► P3.8 ──► P3.13
P1.3 ──► P3.4 ──► P3.5 ──► P3.9 ──► P3.10
                  P3.4 ──► P3.6 ──► P3.13
P3.11, P3.12 parallel after respective deps
```

### Phase 3 Exit Criteria

- FR-COLLAB-001 through FR-COLLAB-003 pass acceptance tests.
- FR-PM-001 through FR-PM-003 pass acceptance tests.
- WebSocket message delivery <100 ms latency (p95) under 100 concurrent connections.
- Kanban drag-and-drop state transitions persist correctly.
- Concurrent edit scenario: two clients editing same requirement results in correct
  last-write-wins resolution without data loss.

---

## Phase 4: Compliance & Governance

**Goal**: Specification verification dashboard, audit logs, SLSA attestations, and
compliance export.

**Prerequisite**: Phase 1 complete.

### Task Table

| Task ID | Description                                    | Depends On       | Effort       |
|---------|------------------------------------------------|------------------|--------------|
| P4.1    | Go backend: audit log schema + write path      | P1.1             | 4 tool calls |
| P4.2    | Go backend: specification verification engine  | P1.3–P1.5        | 8 tool calls |
|         | (orphaned req, orphaned test, coverage check)  |                  |              |
| P4.3    | Go backend: compliance report export           | P4.2             | 4 tool calls |
|         | (JSON, CSV, HTML)                              |                  |              |
| P4.4    | Go backend: custom governance policy DSL       | P4.2             | 6 tool calls |
| P4.5    | CI: SLSA attestation workflow (cosign)         | P1.17            | 3 tool calls |
| P4.6    | CI: SBOM generation (syft)                     | P4.5             | 2 tool calls |
| P4.7    | Frontend: spec verification dashboard          | P4.2             | 6 tool calls |
| P4.8    | Frontend: audit log viewer                     | P4.1             | 4 tool calls |
| P4.9    | Frontend: compliance report download           | P4.3             | 2 tool calls |
| P4.10   | Unit tests: verification engine                | P4.2             | 5 tool calls |
| P4.11   | Integration tests: audit log completeness      | P4.1             | 3 tool calls |

### Phase 4 DAG (text)

```
P1.1 ──► P4.1 ──► P4.8
P1.3–P1.5 ──► P4.2 ──► P4.3 ──► P4.9
                        P4.2 ──► P4.4
                        P4.2 ──► P4.7
P1.17 ──► P4.5 ──► P4.6
P4.10, P4.11 parallel after respective deps
```

### Phase 4 Exit Criteria

- FR-VERIFY-001 through FR-VERIFY-003 pass acceptance tests.
- Spec verification report identifies all orphaned items in test dataset.
- Compliance export produces valid JSON/CSV/HTML for a 500-requirement project.
- SLSA attestation attached to release artifact and verified via `cosign verify`.
- Audit log captures all create/update/delete events with user and timestamp.

---

## Phase 5: Agent & MCP Integration

**Goal**: FastMCP server exposing TracerTM tools to AI agents; agent coordination support.

**Prerequisite**: Phase 1 complete. Phase 4 recommended (verification tool requires P4.2).

### Task Table

| Task ID | Description                                      | Depends On  | Effort       |
|---------|--------------------------------------------------|-------------|--------------|
| P5.1    | Python MCP server scaffold (FastMCP 2.14)        | P1.3        | 4 tool calls |
| P5.2    | MCP tool: get_requirement                        | P5.1        | 2 tool calls |
| P5.3    | MCP tool: get_coverage_matrix                    | P5.1, P1.5  | 2 tool calls |
| P5.4    | MCP tool: run_spec_verification                  | P5.1, P4.2  | 3 tool calls |
| P5.5    | MCP tool: link_requirement_to_code               | P5.1, P1.4  | 2 tool calls |
| P5.6    | MCP tool: search_requirements                    | P5.1, P1.3  | 2 tool calls |
| P5.7    | MCP server: auth (JWT propagation to Go API)     | P5.1, P1.2  | 3 tool calls |
| P5.8    | MCP server: rate limiting (per-agent token)      | P5.7        | 2 tool calls |
| P5.9    | Unit tests: all MCP tool functions               | P5.2–P5.6   | 4 tool calls |
| P5.10   | Integration tests: MCP server ↔ Go API           | P5.7, P5.8  | 3 tool calls |
| P5.11   | Documentation: MCP tool catalog                  | P5.2–P5.6   | 2 tool calls |

### Phase 5 DAG (text)

```
P1.3 ──► P5.1
           ├── P5.2 ──► P5.9
           ├── P5.3 ──► P5.9
           ├── P5.4 (needs P4.2) ──► P5.9
           ├── P5.5 ──► P5.9
           └── P5.6 ──► P5.9
P1.2 ──► P5.7 ──► P5.8 ──► P5.10
P5.9 + P5.10 ──► P5.11
```

### Phase 5 Exit Criteria

- All MCP tools return correct responses in integration test suite.
- Agent can link a requirement to a code file via MCP tool and see it reflected in RTM.
- Rate limiting enforced: >100 req/min from single agent returns 429.
- MCP tool catalog published in `docs/`.

---

## Phase 6: Observability & Hardening

**Goal**: Production-grade observability, performance baselines, load testing, security audit.

**Prerequisite**: Phases 1–3 complete.

### Task Table

| Task ID | Description                                         | Depends On          | Effort        |
|---------|-----------------------------------------------------|---------------------|---------------|
| P6.1    | Go backend: OTel instrumentation (spans, metrics)   | P1.17               | 5 tool calls  |
| P6.2    | Python: OTel instrumentation                        | P1.17               | 3 tool calls  |
| P6.3    | Grafana: provisioned dashboards (latency, coverage) | P6.1, P6.2          | 4 tool calls  |
| P6.4    | Prometheus alerts: SLA thresholds                   | P6.1                | 3 tool calls  |
| P6.5    | Load tests: k6 suite (RTM matrix, graph, WebSocket) | P2.7, P3.1          | 5 tool calls  |
| P6.6    | Performance baselines: document p50/p95/p99         | P6.5                | 2 tool calls  |
| P6.7    | Security audit: govulncheck, bandit, semgrep         | P1.17               | 3 tool calls  |
| P6.8    | Security hardening: remediate all high/critical     | P6.7                | variable      |
| P6.9    | Chaos tests: network partition, Neo4j unavailable   | P6.5                | 4 tool calls  |
| P6.10   | Production deployment runbook                       | P6.3, P6.6, P6.8    | 3 tool calls  |

### Phase 6 DAG (text)

```
P1.17 ──► P6.1 ──► P6.3 ──► P6.10
                   P6.1 ──► P6.4
P1.17 ──► P6.2 ──► P6.3
P1.17 ──► P6.7 ──► P6.8 ──► P6.10
P2.7 + P3.1 ──► P6.5 ──► P6.6 ──► P6.10
                          P6.5 ──► P6.9
```

### Phase 6 Exit Criteria

- Go backend p95 API latency <200 ms under 1 000 req/s load.
- WebSocket broadcast p95 <100 ms under 1 000 concurrent connections.
- Zero high/critical security findings from audit tools.
- Grafana dashboards show green SLA indicators for all services.
- Chaos test: system recovers within 30 s after Neo4j restart.

---

## Cross-Phase Dependency Summary

```
P1 (Foundation) ──► P2 (Graph)
P1 (Foundation) ──► P3 (Collaboration)
P1 (Foundation) ──► P4 (Compliance)
P1 (Foundation) ──► P5 (MCP/Agent) ── needs P4.2
P1 + P2 + P3   ──► P6 (Hardening)
```

P2, P3, P4, P5 can begin in parallel once P1 exits. P6 requires P2 and P3.

---

## FR Coverage Matrix

| Phase | Functional Requirements Covered                              |
|-------|--------------------------------------------------------------|
| P1    | FR-RTM-001–004, FR-LINK-001–003, FR-TEST-001–003, FR-AUTH-001–004 |
| P2    | FR-GRAPH-001–004                                             |
| P3    | FR-COLLAB-001–003, FR-PM-001–003                             |
| P4    | FR-VERIFY-001–003, FR-COMPLY-001–002                         |
| P5    | FR-MCP-001–005                                               |
| P6    | FR-OBS-001–003, FR-PERF-001–003                              |

---

*See `docs/PLAN.md` for extended planning detail including Magic I/O analysis, milestone
decision gates, and rollback procedures.*
