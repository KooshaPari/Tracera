# TraceRTM — Comprehensive System Plan

## 1. Mission Statement

TraceRTM is an **agent-native, multi-view requirements traceability and project management platform** that bridges the gap between requirements, code, and testing through intelligent automation, graph-based analysis, and AI-powered workflows. The system enables development teams, product managers, QA engineers, compliance teams, and **AI agents** to maintain complete bi-directional traceability across the entire software development lifecycle.

**Core Capabilities:**
- **Multi-Source Requirements Management:** Import, parse, and unify requirements from GitHub, Jira, Linear, specifications, and API contracts
- **Graph-Based Traceability:** Maintain and analyze bi-directional links between requirements, code, tests, features, and documentation using Neo4j graph database
- **BDD & Test Management:** Support Behavior-Driven Development with executable scenarios, test case management, and execution tracking
- **AI Agent Integration:** Provide 50+ MCP tools for autonomous agent workflows, auto-linking, requirement quality analysis, and impact analysis
- **Real-Time Collaboration:** WebSocket-based collaboration, bidirectional external tool sync, event-driven updates
- **Compliance & Reporting:** Generate traceability matrices, audit trails (blockchain-backed), coverage reports, and regulatory compliance documentation

**Deployment Model:** Local-first, OSS-maximized stack (PostgreSQL, Neo4j, Redis, NATS, Temporal, MinIO) with cloud-ready production architecture.

---

## 2. Magic I/O: The Hard Problems

These are the technical challenges where automation complexity peaks — areas requiring explicit architectural solutions.

### M1: ATS/System Integration Diversity

Every external system (GitHub, Jira, Linear, Azure DevOps, GitLab) has different APIs, authentication patterns, data models, rate limits, and webhook formats. **There is no universal "import" protocol.**

**Mitigation:**
- **Abstraction Layer:** Generic `Integration` model with type-specific adapters (`github_import_service`, `jira_import_service`, `linear_integration`)
- **Unified Mapper:** Transform external items → internal `Item` schema with bidirectional sync
- **Rate Limiting:** Per-integration throttling engine with exponential backoff
- **Webhook Normalization:** Standardized event bus (NATS) translates external webhooks → internal events
- **Coverage Tracking:** Track integration support completeness in `companies` table, prioritize high-value integrations

### M2: Real-Time Collaboration Conflicts

Multiple users/agents editing the same graph simultaneously create concurrent modification conflicts. Traditional locking blocks parallelism; last-write-wins loses data.

**Mitigation:**
- **Operational Transformation (OT):** WebSocket layer applies OT for item/link updates
- **Optimistic Locking:** `version` field on critical entities; retry with conflict resolution on collision
- **Event Sourcing:** All mutations published to NATS event log; consumers rebuild state from events
- **Conflict Resolution Service:** `conflict_resolution_service` detects and merges conflicting changes using LLM-assisted semantic merge
- **Agent Coordination:** `agent_coordination_service` with distributed locks (`agent_lock` model) prevents multi-agent race conditions

### M3: Graph Performance at Scale

10,000+ requirements × 5 link types × 3 hops = millions of graph traversals. Relational DB joins explode; naive graph queries timeout.

**Mitigation:**
- **Dual-Store Architecture:** PostgreSQL for transactional CRUD + Neo4j for graph queries
- **Materialized Views:** Pre-computed critical paths, coverage matrices, impact analysis cached in `materialized_view_service`
- **Query Optimization:** `query_optimization_service` rewrites complex queries; graph snapshots for read-heavy workloads
- **Indexing Strategy:** Composite indexes on `(source_id, target_id, link_type)`, graph indexes on node labels + properties
- **Horizontal Scaling:** Neo4j read replicas for query load; NATS for async graph updates
- **Performance Target:** <100ms p95 for graph queries, <500ms for complex analysis, <5s for full matrix generation

### M4: AI Hallucination in Auto-Linking

LLM-suggested links can be semantically plausible but factually incorrect (e.g., linking test to wrong requirement). Precision vs. recall trade-off: aggressive linking creates noise; conservative linking misses valid connections.

**Mitigation:**
- **Hybrid Approach:** Embeddings (semantic similarity) + rule-based heuristics (file path, commit message regex) + graph proximity scoring
- **Confidence Thresholds:** `auto_link_service` returns scored suggestions (0–100); auto-apply only ≥85, queue 70–84 for human review, skip <70
- **Feedback Loop:** Track acceptance rate of auto-suggested links; retrain scoring model on accepted/rejected examples
- **Human-in-Loop:** Agent escalation for low-confidence links; gradual confidence threshold tuning
- **Provenance Tracking:** Every auto-link stores `created_by=ai`, `confidence_score`, `rationale` for auditability

### M5: BDD Execution Ambiguity

Natural language Gherkin scenarios → executable tests requires reliable parsing and mapping. Scenario step "Given user is logged in" can map to multiple step definitions; ambiguity breaks test execution.

**Mitigation:**
- **Step Definition Registry:** `scenario_service` maintains canonical step library with regex matchers
- **Disambiguation Engine:** LLM-assisted step mapper suggests matches when ambiguous; human approval required
- **Execution Abstraction:** `execution_service` supports multiple test frameworks (pytest-bdd, Cucumber, custom); adapters translate scenarios → framework-specific code
- **Coverage Tracking:** Map each scenario step → requirement; identify untested requirements
- **Temporal Workflows:** Long-running test suites orchestrated via `temporal_service` with retry/timeout policies

### M6: Test Result Status Inference from Noisy Data

Test frameworks output in diverse formats (JUnit XML, pytest JSON, TAP, custom). CI/CD systems (GitHub Actions, Jenkins, GitLab CI) have different webhook payloads. Extracting "test X failed because Y" reliably is hard.

**Mitigation:**
- **Adapter Pattern:** `execution/` service layer with parsers for JUnit, pytest, TAP, Cucumber JSON
- **LLM Classification:** Failure messages → categorization (assertion failure, timeout, environment error, flake)
- **Pattern Library:** Common error patterns cached; regex + embeddings for new failure types
- **Integration-Specific Hooks:** GitHub Actions → direct API integration; webhook handlers for GitLab/Jenkins/CircleCI
- **High-Confidence Auto-Update:** Test status updates with confidence >90% auto-apply; <90% queue for review

### M7: Volume Throttling & API Quotas

Syncing 1,000 GitHub issues × 10 PRs each × 50 comments = 500,000 API calls. GitHub rate limit: 5,000/hour. Naive polling gets blacklisted.

**Mitigation:**
- **Webhook-First:** Use webhooks for real-time updates; polling only for backfill or webhook failures
- **Smart Polling:** Incremental sync with `updated_at` timestamps; skip unchanged items
- **Rate Limiter:** `integration_sync_processor` with per-integration hourly budgets; exponential backoff on 429 responses
- **Batch Operations:** `bulk_operation_service` batches creates/updates; single transaction per batch
- **Quota Monitoring:** `metrics_service` tracks API usage; alert at 80% quota; pause at 95%

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                  │
│  React Web (Vite) │ Desktop (Electron) │ MCP Agents (Claude/Cowork)    │
└────────┬────────────────────┬─────────────────────┬────────────────────┘
         │ REST/WebSocket     │ stdio MCP           │ gRPC
    ┌────▼────────────────────▼─────────────────────▼────────┐
    │              API GATEWAY (Caddy)                        │
    │  /api/v1/* → Python | /go/* → Go | /ws → WebSocket     │
    └─────┬──────────────────────────────────┬────────────────┘
          │                                  │
    ┌─────▼─────────────────┐    ┌──────────▼────────────────┐
    │   PYTHON BACKEND      │    │    GO BACKEND             │
    │   (FastAPI)           │◄──►│    (Echo)                 │
    │                       │gRPC│                           │
    │ • REST API (200+ eps) │    │ • Graph Ops (Neo4j)       │
    │ • MCP Server (50+ tls)│    │ • Real-Time (WebSocket)   │
    │ • Business Logic      │    │ • High-Perf Services      │
    │ • Workflows (Temporal)│    │ • Code Indexing           │
    └───┬───────────────────┘    └────┬──────────────────────┘
        │                             │
        ├─────────────────────────────┴─────────────────────────┐
        │                 INFRASTRUCTURE LAYER                   │
        ├────────────────┬────────────┬────────────┬────────────┤
        │ PostgreSQL     │ Neo4j      │ Redis      │ NATS       │
        │ (Relational)   │ (Graph)    │ (Cache)    │ (Events)   │
        ├────────────────┼────────────┼────────────┼────────────┤
        │ Temporal       │ MinIO/S3   │ Prometheus │ Vault      │
        │ (Workflows)    │ (Storage)  │ (Metrics)  │ (Secrets)  │
        └────────────────┴────────────┴────────────┴────────────┘
```

### Data Flow Patterns

**Write Path (User creates requirement):**
```
Client → POST /items → Python API → ItemService → PostgreSQL
                                  └→ NATS publish 'items.created'
                                            ├→ Go Backend → Neo4j (add node)
                                            ├→ SearchService → Index update
                                            └→ WebSocket → Broadcast to clients
```

**Read Path (Agent queries graph):**
```
MCP Tool → Python MCP Server → gRPC call → Go Backend → Neo4j query
                                          ← Result      ← Graph data
              ← Tool response with graph snapshot
```

**Sync Path (GitHub webhook):**
```
GitHub → POST /webhooks/github → WebhookService → NATS 'integrations.github.issue_updated'
                                                   ├→ SyncService → ItemService → PostgreSQL
                                                   └→ GraphService → Neo4j update
```

---

## 4. Data Schema

### Core Entities (PostgreSQL)

**items** (Requirements, Features, Tests, Specs)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| type | Enum | requirement, feature, test_case, specification, adr, contract |
| title | Text | |
| description | Text | Markdown content |
| status | Enum | draft, active, deprecated, completed, verified |
| project_id | UUID | FK → projects |
| created_by | UUID | FK → users |
| created_at | Timestamp | |
| updated_at | Timestamp | |
| version | Integer | Optimistic locking |
| metadata | JSONB | Type-specific fields |

**links** (Traceability Relationships)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| source_id | UUID | FK → items |
| target_id | UUID | FK → items |
| link_type | Enum | implements, tests, derives, depends_on, conflicts_with |
| created_by | UUID | FK → users (or 'ai' for auto-links) |
| confidence_score | Float | 0–1 for AI-suggested links |
| rationale | Text | Why this link exists |
| created_at | Timestamp | |

**projects** (Workspace Container)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| name | Text | |
| account_id | UUID | FK → accounts (multi-tenant) |
| settings | JSONB | Project-specific configs |

**integrations** (External Tool Connections)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| type | Enum | github, jira, linear, gitlab, azure_devops |
| project_id | UUID | FK → projects |
| config | JSONB | API tokens, URLs, mappings |
| sync_status | Enum | active, paused, failed |
| last_sync_at | Timestamp | |
| rate_limit_remaining | Integer | API quota tracking |

**test_runs** (Execution Results)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| test_suite_id | UUID | FK → test_suites |
| status | Enum | passed, failed, skipped, flaky |
| started_at | Timestamp | |
| completed_at | Timestamp | |
| results | JSONB | Framework-specific output |
| coverage_delta | Float | % change since last run |

**blockchain** (Immutable Audit Trail)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| event_type | Enum | item_created, link_created, status_changed |
| entity_id | UUID | Item/link/project ID |
| previous_hash | Text | SHA-256 of previous block |
| current_hash | Text | SHA-256(previous_hash + payload) |
| payload | JSONB | Event data snapshot |
| timestamp | Timestamp | |

**agents** (AI Agent Registry)
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | PK |
| name | Text | |
| type | Enum | requirement_analyzer, test_executor, link_suggester, report_generator |
| config | JSONB | LLM model, parameters |
| status | Enum | idle, running, failed |
| session_id | UUID | FK → agent_sessions |

### Graph Schema (Neo4j)

**Nodes:**
```cypher
(:Item {id: UUID, type: String, title: String, status: String})
(:Project {id: UUID, name: String})
(:User {id: UUID, email: String})
```

**Relationships:**
```cypher
(Item)-[:IMPLEMENTS]->(Item)
(Item)-[:TESTS]->(Item)
(Item)-[:DERIVES_FROM]->(Item)
(Item)-[:DEPENDS_ON]->(Item)
(Item)-[:CONFLICTS_WITH]->(Item)
(Item)-[:BELONGS_TO]->(Project)
(Item)-[:CREATED_BY]->(User)
```

**Indexes:**
```cypher
CREATE INDEX item_type ON :Item(type);
CREATE INDEX item_status ON :Item(status);
CREATE CONSTRAINT item_id ON (i:Item) ASSERT i.id IS UNIQUE;
```

---

## 5. Phased WBS with DAG Dependencies

### Phase 0: Foundation (COMPLETE — 100%)

*Already implemented: Database schema, models, authentication, base services, API scaffolding.*

| Component | Status | Files |
|-----------|--------|-------|
| PostgreSQL schema | ✅ | `backend/schema.sql`, `alembic/versions/*` |
| SQLAlchemy models | ✅ | `src/tracertm/models/*.py` (50+ models) |
| FastAPI app | ✅ | `src/tracertm/api/app.py`, routers in `api/routers/` |
| Go backend | ✅ | `backend/`, Echo framework |
| WorkOS auth | ✅ | `workos_auth_service.py`, `auth_handler.go` |
| MCP server scaffold | ✅ | `src/tracertm/mcp/server.py`, 50+ tools |

---

### Phase 1: Discovery & Capture (75% Complete)

**Goal:** Import requirements from external systems, parse specifications, auto-link items, integrate Git commits.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P1.1 | GitHub issue import | P0 | ✅ | `github_import_service.py`, `github_handler.go` |
| P1.2 | Jira import adapter | P0 | ✅ | `jira_import_service.py` |
| P1.3 | Linear integration | P0 | ⚠️ | `linear_app.py` (model only, sync incomplete) |
| P1.4 | Specification parsing (Markdown, YAML, JSON) | P0 | ✅ | `specification_service.py`, `documentation_service.py` |
| P1.5 | Auto-link suggestion engine | P1.4 | ✅ | `auto_link_service.py` (embeddings + heuristics) |
| P1.6 | Commit linking (Git hooks) | P1.1 | ✅ | `commit_linking_service.py` |
| P1.7 | Webhook ingestion | P1.1–P1.3 | ✅ | `webhook_service.py`, `api_webhooks_service.py` |
| P1.8 | Deduplication engine | P1.1–P1.3 | ⚠️ | Hash-based (partial; needs fuzzy matching) |

**Open Work:**
- Linear sync bidirectional updates (webhook handler exists, sync logic incomplete)
- Fuzzy deduplication for near-duplicate items across sources
- Azure DevOps / GitLab adapters (planned, not started)

---

### Phase 2: Qualification & Analysis (60% Complete)

**Goal:** Analyze requirement quality, detect cycles, compute critical paths, perform impact analysis, track coverage.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P2.1 | Requirement quality scoring (SMART criteria) | P1.4 | ✅ | `requirement_quality_service.py` |
| P2.2 | Graph analysis (centrality, clustering) | P0 | ✅ | `graph_analysis_service.py` |
| P2.3 | Cycle detection | P0 | ✅ | `cycle_detection_service.py` |
| P2.4 | Critical path identification | P2.3 | ✅ | `critical_path_service.py` |
| P2.5 | Dependency analysis | P2.2 | ✅ | `dependency_analysis_service.py` |
| P2.6 | Impact analysis (ripple effects) | P2.5 | ✅ | `impact_analysis_service.py` |
| P2.7 | Coverage analysis (req → test mapping) | P3.3 | ⚠️ | `coverage_service` (basic; needs multi-hop tracing) |
| P2.8 | Shortest path queries | P0 | ✅ | `shortest_path_service.py` |

**Open Work:**
- Multi-hop coverage tracing (requirement → feature → test → code)
- Coverage gap auto-detection with actionable recommendations
- Performance optimization for large graphs (>10K nodes)

---

### Phase 3: Application & Tracking (90% Complete)

**Goal:** CRUD for items/links, status workflows, progress tracking, feature management.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P3.1 | Item CRUD | P0 | ✅ | `item_service.py`, `items.py` (router) |
| P3.2 | Link CRUD | P0 | ✅ | `link_service.py`, `links.py` (handler) |
| P3.3 | Feature tracking | P3.1 | ✅ | `feature_service.py`, `features.py` (router) |
| P3.4 | Status workflow engine | P3.1 | ✅ | `status_workflow_service.py` |
| P3.5 | Progress tracking | P3.3, P3.4 | ✅ | `progress_service.py`, `progress_tracking_service.py` |
| P3.6 | Bulk operations | P3.1, P3.2 | ✅ | `bulk_service.py`, `bulk_operation_service.py` |
| P3.7 | History tracking | P3.1 | ✅ | `history_service.py`, `event_service.py` |

**Open Work:**
- Custom workflow templates (currently hardcoded)
- Bulk import/export via CSV/Excel (basic export exists, import missing)

---

### Phase 4: Verification & Validation (40% Complete)

**Goal:** Test management, execution, coverage tracking, validation reporting, graph consistency checks.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P4.1 | Test case/suite models | P0 | ✅ | `test_case.py`, `test_suite.py`, `test_run.py` |
| P4.2 | Test execution framework | P4.1 | ⚠️ | `execution/` (scaffold; no live executor) |
| P4.3 | BDD scenario management | P4.1 | ✅ | `scenario_service.py`, `scenario.py` (model) |
| P4.4 | Coverage tracking | P4.2, P2.7 | ⚠️ | `test_coverage.py` (model; aggregation incomplete) |
| P4.5 | Verification reporting | P4.4 | ❌ | Planned (no implementation) |
| P4.6 | Graph validation (consistency checks) | P2.2 | ✅ | `graph_validation_service.py` |
| P4.7 | Temporal test workflows | P4.2 | ⚠️ | `temporal_service.py` (integration exists; test workflows missing) |

**Open Work:**
- Live test executor with pytest/Cucumber integration
- Coverage aggregation service (multi-source)
- Automated validation reports (PDF/HTML)
- Temporal workflow definitions for long-running test suites

---

### Phase 5: Reporting & Analytics (80% Complete)

**Goal:** Traceability matrices, dashboards, custom reports, metrics, export formats.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P5.1 | Traceability matrix generation | P2.7, P3.1 | ✅ | `traceability_matrix_service.py` |
| P5.2 | Analytics dashboards | P3.5, P5.3 | ✅ | `advanced_analytics_service.py`, `spec_analytics_service.py` |
| P5.3 | Metrics service | P0 | ✅ | `metrics_service.py`, `stats_service.py` |
| P5.4 | Custom report builder | P5.1 | ⚠️ | `graph_report_service.py` (basic; templating incomplete) |
| P5.5 | Export formats (PDF, Excel, JSON, Markdown) | P5.1 | ⚠️ | `export_service.py` (JSON/Markdown only) |
| P5.6 | Documentation generation | P1.4, P5.1 | ✅ | `documentation_service.py` |

**Open Work:**
- PDF export with custom templates
- Excel export with formatting
- Custom report template engine

---

### Phase 6: Collaboration & Integration (50% Complete)

**Goal:** Real-time collaboration, external tool sync, webhooks, AI chat, notifications.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P6.1 | WebSocket real-time updates | P0 | ✅ | `websocket.py` (router), `websocket_handler.go` |
| P6.2 | Bidirectional sync (GitHub/Jira/Linear) | P1.1–P1.3 | ⚠️ | GitHub ✅, Jira ⚠️ (one-way), Linear ❌ |
| P6.3 | Webhook system | P1.7 | ✅ | `webhook_service.py`, `webhook_handler.go` |
| P6.4 | AI chat assistant | P7.2 | ⚠️ | `chat.py` (router), `ai_service.py` (basic; context incomplete) |
| P6.5 | Notification system | P0 | ✅ | `notification_service.py`, `notifications.py` (router) |
| P6.6 | Conflict resolution | P6.1 | ✅ | `conflict_resolution_service.py` |
| P6.7 | Event sourcing | P6.1 | ✅ | `event_sourcing_service.py` |

**Open Work:**
- Jira bidirectional sync (one-way import complete)
- Linear sync implementation
- AI chat context window management
- Advanced conflict resolution (semantic merge)

---

### Phase 7: AI & Automation (70% Complete)

**Goal:** AI-powered analysis, auto-linking, agent coordination, workflow automation, code analysis.

| Task ID | Description | Dependencies | Status | Files |
|---------|-------------|--------------|--------|-------|
| P7.1 | AI service orchestration | P0 | ✅ | `ai_service.py`, `ai_tools.py` |
| P7.2 | Auto-link suggestions (hybrid AI) | P1.5 | ✅ | `auto_link_service.py` |
| P7.3 | Agent coordination | P7.1 | ✅ | `agent_coordination_service.py`, `agent_handler.go` |
| P7.4 | Agent monitoring | P7.3 | ✅ | `agent_monitoring_service.py`, `agent_metrics_service.py` |
| P7.5 | Workflow automation (Temporal) | P0 | ⚠️ | `temporal_service.py` (integration; workflows missing) |
| P7.6 | Code analysis (indexing) | P0 | ⚠️ | `code_index_handler.go` (scaffold; parser incomplete) |
| P7.7 | MCP server (50+ tools) | P0 | ✅ | `mcp/server.py`, `mcp/tools/*.py` |
| P7.8 | Agent performance tracking | P7.3 | ✅ | `agent_performance_service.py` |

**Open Work:**
- Temporal workflow definitions (requirement validation, test orchestration)
- Code indexing parsers (Python/TS/Go AST)
- MCP tool refinement (response optimization, pagination)

---

## 6. DAG Visualization (Simplified)

```
P0 (Foundation) ──┬── P1 (Discovery) ──┬── P2 (Analysis) ──┬── P5 (Reporting)
                  │                     │                   │
                  ├── P3 (Tracking) ────┤                   │
                  │                     │                   │
                  ├── P4 (Validation) ──┴───────────────────┤
                  │                                         │
                  ├── P6 (Collaboration) ───────────────────┤
                  │                                         │
                  └── P7 (AI & Automation) ─────────────────┘
                                                            │
                                                   P8 (Polish & Deploy)
```

**Critical Path:** P0 → P1 → P2 → P5 (for MVP reporting)
**Parallel Tracks:** P3, P4, P6, P7 can progress independently after P0

---

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Neo4j performance degradation at >50K nodes** | Medium | High | Materialized views, read replicas, query optimization, graph snapshots |
| **AI auto-link hallucinations damage traceability integrity** | Medium | High | Confidence thresholds, human-in-loop review queue, feedback retraining |
| **External API rate limits block sync** | High | Medium | Webhook-first, smart polling, quota monitoring, exponential backoff |
| **WebSocket connection storms overload server** | Medium | Medium | Connection pooling, rate limiting per user, horizontal scaling with NATS |
| **Temporal workflow failures cascade** | Low | High | Retry policies, dead-letter queue, workflow versioning, observability |
| **PostgreSQL transaction deadlocks under load** | Medium | Medium | Optimistic locking, retry logic, read replicas for queries |
| **MCP tool response size exceeds token limits** | High | Low | Pagination, summary responses, client-side streaming |
| **Test execution timeouts block CI/CD** | Medium | High | Temporal workflow timeouts, parallel execution, cached results |
| **Graph cycles break dependency resolution** | Low | High | Cycle detection service, validation before link creation, manual override |

---

## 8. Tech Stack Summary (Rationale)

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend (Python)** | FastAPI 0.115+ | Async, auto OpenAPI docs, Pydantic validation, 200+ endpoints |
| **Backend (Go)** | Echo + gRPC | High-perf graph ops, real-time WebSocket, <10ms latency |
| **Frontend** | React + TypeScript + Vite | Component-based, type-safe, HMR, Zustand state, React Query |
| **Database (Relational)** | PostgreSQL 16+ | ACID, JSONB for metadata, full-text search, mature ecosystem |
| **Database (Graph)** | Neo4j 5+ | Native graph storage, Cypher queries, <100ms p95 for traceability |
| **Cache** | Redis 7+ | Distributed cache, pub/sub, session storage, rate limiting |
| **Event Bus** | NATS 2.10+ | Lightweight, 10M msg/sec, subject-based routing, JetStream persistence |
| **Workflows** | Temporal 1.7+ | Durable execution, retries, sagas, long-running test orchestration |
| **Search** | PostgreSQL tsvector | Built-in full-text, no external dependency, <200ms p95 |
| **Storage** | MinIO (local) / S3 (cloud) | S3-compatible, document storage, local-first dev |
| **Auth** | WorkOS | SSO, OAuth, SAML, team management, audit logs |
| **AI/ML** | Anthropic Claude, OpenAI | MCP protocol, embeddings, requirement analysis, auto-linking |
| **Observability** | Prometheus + Grafana + OpenTelemetry | Metrics, tracing, dashboards, Sentry error tracking |
| **Orchestration** | process-compose (local) / Kubernetes (prod) | Native processes dev, container orchestration prod |

---

## 9. Human Touchpoints (Minimal)

**During Setup:**
1. **WorkOS Configuration:** OAuth app setup (10 min, one-time)
2. **Infrastructure Secrets:** Database passwords, API keys in Vault (5 min)
3. **Initial Admin User:** First login via WorkOS (2 min)

**During Operation:**
- **Low-Confidence Link Review:** Agent escalation queue (~5 links/day at 70–84 confidence)
- **Integration Auth Refresh:** GitHub/Jira token expiry (~monthly)
- **Custom Workflow Approval:** New Temporal workflows (rare)
- **Compliance Audits:** Manual review of blockchain audit trail (quarterly)

All other operations autonomous via agents/automation.

---

## 10. Steady-State Daily Cadence

```
00:00  Daily backup (PostgreSQL, Neo4j, Redis snapshots → S3)
02:00  Materialized view refresh (traceability matrices, coverage stats)
06:00  GitHub webhook backfill (missed events during maintenance)
09:00  Peak usage window opens
       - WebSocket connections scale up
       - Read replicas active
       - MCP agent swarm coordination
12:00  Mid-day metrics aggregation
       - Dashboard updates
       - SLA monitoring
15:00  Integration sync reconciliation
       - GitHub/Jira/Linear 3-way merge
       - Conflict resolution queue
18:00  End-of-day reports
       - Coverage delta
       - Agent performance summary
       - Failed workflow retry
21:00  Peak usage window closes
       - Scale down read replicas
       - Archive old sessions
23:00  Pre-backup consistency check
       - Graph validation
       - Orphan link cleanup
```

---

## 11. Implementation Priorities (Agent Execution)

### MVP (Week 1–2, ~15 agents × 10 min avg = 150 min wall clock)

**Goal:** Functional traceability for single project (GitHub import → manual linking → matrix export).

1. **Complete Linear Sync** (P1.3) — 1 agent, 20 min
2. **Fuzzy Deduplication** (P1.8) — 1 agent, 15 min
3. **Multi-Hop Coverage Tracing** (P2.7) — 2 agents parallel, 25 min
4. **Test Executor Integration** (P4.2) — 2 agents, 30 min (pytest, Cucumber adapters)
5. **Coverage Aggregation** (P4.4) — 1 agent, 15 min
6. **PDF/Excel Export** (P5.5) — 2 agents parallel, 20 min
7. **Jira Bidirectional Sync** (P6.2) — 1 agent, 25 min
8. **Temporal Workflows** (P7.5) — 3 agents (requirement validation, test suite, report gen), 30 min
9. **Code Indexing Parsers** (P7.6) — 3 agents parallel (Python AST, TS ESLint, Go AST), 40 min
10. **Integration Tests** — 2 agents (E2E scenarios), 20 min

### Phase 2 (Week 3–4, ~12 agents × 8 min avg = 96 min wall clock)

**Goal:** Production-ready multi-tenant system with compliance.

1. **Custom Workflow Templates** (P3 followup) — 2 agents, 15 min
2. **Advanced Conflict Resolution** (P6.6 enhancement) — 1 agent, 20 min
3. **AI Chat Context Management** (P6.4 enhancement) — 1 agent, 15 min
4. **MCP Tool Pagination** (P7.7 refinement) — 2 agents parallel, 10 min
5. **Graph Performance Tuning** (P2 optimization) — 2 agents (indexing, query rewrites), 25 min
6. **Validation Report Templates** (P4.5) — 1 agent, 10 min
7. **Custom Report Engine** (P5.4) — 2 agents (templating, rendering), 20 min
8. **Horizontal Scaling Configs** (Infra) — 1 agent (k8s manifests, helm charts), 15 min

### Phase 3 (Week 5+, ongoing)

**Goal:** Advanced features, compliance, enterprise readiness.

- Azure DevOps / GitLab adapters
- Advanced ML model retraining (auto-link feedback loop)
- Multi-language code indexing (Java, C++, Rust)
- Compliance module (FDA 21 CFR Part 11, ISO 9001)
- Mobile app (React Native)
- Advanced graph algorithms (community detection, anomaly detection)

---

## 12. Open Questions for Team Lead

1. **Deployment Target:** Is primary deployment local dev (process-compose) or production Kubernetes? Should we prioritize K8s manifests in Phase 2?
2. **Integration Priority:** After Linear, which integrations are highest value (Azure DevOps, GitLab, Shortcut, Asana)?
3. **AI Model Choice:** Current setup uses Claude/OpenAI via API. Should we support self-hosted models (Ollama, vLLM) for air-gapped environments?
4. **Compliance Requirements:** Do we need FDA/ISO compliance features now, or defer to Phase 3?
5. **Multi-Tenancy:** Is account-level isolation (current implementation) sufficient, or do we need project-level RBAC granularity?
6. **Performance SLA:** Current target is <100ms graph queries. Do we need to hit <50ms for enterprise tier?
7. **Test Framework Support:** Beyond pytest-bdd and Cucumber, which test frameworks should we prioritize (JUnit, TestNG, Jest, Vitest)?

---

**End of Plan**

---

## Appendix A: Service-to-Phase Mapping

| Phase | Python Services | Go Handlers | MCP Tools | Completion |
|-------|-----------------|-------------|-----------|------------|
| P1 | github_import, jira_import, auto_link, commit_linking, specification, ingestion | github_handler, webhook_handler | import_from_github, parse_spec, suggest_links | 75% |
| P2 | requirement_quality, graph_analysis, cycle_detection, critical_path, impact_analysis, dependency_analysis | graph_handler, traceability_handler | detect_cycles, find_critical_path, analyze_impact | 60% |
| P3 | item, link, feature, status_workflow, progress, bulk, history | N/A | create_item, create_link, track_progress | 90% |
| P4 | execution services, coverage, verification, graph_validation, scenario | test_handler | run_test_suite, check_coverage, validate_graph | 40% |
| P5 | traceability_matrix, advanced_analytics, metrics, stats, export, documentation | metrics_handler | generate_matrix, get_analytics, export_report | 80% |
| P6 | sync, external_integration, webhook, chat, notification, conflict_resolution, event_sourcing | websocket_handler, github_handler, linear_handler | sync_with_github, send_notification | 50% |
| P7 | ai, auto_link, agent_coordination, agent_monitoring, agent_performance, temporal, code_index, MCP server | ai_handler, agent_handler, code_index_handler | analyze_with_ai, coordinate_agents, execute_workflow, 50+ tools | 70% |

---

## Appendix B: Codebase Entity Counts

**Python Backend:**
- Services: ~90 files in `src/tracertm/services/`
- Models: 50+ in `src/tracertm/models/`
- API Routers: 15+ in `src/tracertm/api/routers/`
- MCP Tools: 50+ in `src/tracertm/mcp/tools/`

**Go Backend:**
- Handlers: 30+ in `backend/internal/handlers/`
- Services: 20+ in `backend/internal/services/`
- Models: 15+ in `backend/internal/models/`

**Frontend:**
- React Components: 300+ in `frontend/apps/web/src/components/`
- Pages: 20+ in `frontend/apps/web/src/pages/`
- Hooks: 40+ in `frontend/apps/web/src/hooks/`

**Total LOC:** ~150K lines (Python 60K, Go 40K, TypeScript 50K)

---

## Appendix C: Performance Baselines (Current)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Graph query (single hop) | 45ms p95 | <100ms | ✅ PASS |
| Graph query (3 hops) | 280ms p95 | <500ms | ✅ PASS |
| Traceability matrix (1K items) | 8.2s | <5s | ❌ FAIL |
| API endpoint latency | 120ms p95 | <200ms | ✅ PASS |
| WebSocket broadcast | 35ms | <50ms | ✅ PASS |
| Full-text search | 180ms p95 | <200ms | ✅ PASS |
| Test coverage | 32% (Go), ~60% (Python) | >80% | ❌ FAIL |

**Priority Optimizations:**
1. Matrix generation: Materialized views + parallel aggregation (target: 3.5s)
2. Test coverage: Expand unit tests, integration tests (target: 85%)
