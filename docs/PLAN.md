# TraceRTM — Comprehensive System Plan

**Version:** 1.0
**Author:** TraceRTM Team
**Date:** 2026-02-12
**Status:** Active

---

## 1. Mission Statement

TraceRTM is a comprehensive requirements traceability and management platform that bridges the gap between requirements, code, and testing through intelligent automation and AI assistance. The system enables development teams, product managers, QA engineers, compliance teams, and AI agents to maintain complete bi-directional traceability across the entire software development lifecycle while automating tedious linking, analysis, and reporting tasks.

**Core Promise:**
- Eliminate manual traceability work through AI-powered auto-linking and analysis
- Provide real-time visibility into requirement coverage, test status, and impact analysis
- Enable compliance teams to generate audit trails with complete lineage
- Support AI agents as first-class users through MCP protocol integration
- Scale to 100,000+ items with <100ms query performance

---

## 2. Magic I/O: The Hard Problems

These are the areas where automation breaks down — where complexity, scale, or conflicting requirements create genuine technical challenges. The plan must address each one explicitly.

### M1: ATS/System Integration Diversity

Every external system (GitHub, Jira, Linear, Azure DevOps) has different APIs, data models, auth patterns, and rate limits. GitHub uses REST + GraphQL, Jira uses REST v3, Linear uses GraphQL only. Each has different concepts for "item" (Issue vs. Card vs. Work Item).

**Problem:** There is no universal "import" API. Each integration requires custom mapping logic.

**Mitigation:**
- Tiered integration strategy: Tier 1 (GitHub/Jira: full bidirectional sync), Tier 2 (Linear/ADO: import-only), Tier 3 (Generic webhook ingestion)
- Abstract sync engine with adapter pattern: `ExternalIntegrationService` delegates to `GitHubAdapter`, `JiraAdapter`, etc.
- Unified item model with `external_id` + `source_type` for round-trip mapping
- Rate limit handling per provider: GitHub 5000/hr, Jira 10/sec per endpoint
- Incremental sync with delta detection (use `updated_at` cursors, not full scans)
- Track sync status in `integration_status` table to recover from failures

### M2: Real-Time Collaboration Conflicts

Multiple users editing the same item/link simultaneously. Offline edits syncing later. Conflict resolution for concurrent updates.

**Problem:** Operational Transformation is complex for graph structures. CRDTs work for text but struggle with constraints (e.g., "no duplicate links").

**Mitigation:**
- Hybrid approach: Optimistic UI updates + server-authoritative conflict resolution
- WebSocket push for real-time updates (other users' changes)
- Vector clocks per item for causality tracking
- Last-write-wins for simple fields (title, description)
- Explicit conflict resolution UI for structural changes (new links, status transitions)
- Event sourcing: all mutations append to event log before applying
- Conflict queue in UI: "User B changed status while you were editing — accept theirs or keep yours?"
- No auto-merge for critical fields; escalate to user

### M3: Graph Performance at Scale

10,000+ nodes, 50,000+ edges. Queries like "find all untested requirements" or "impact analysis for this change" must be <100ms.

**Problem:** PostgreSQL graph queries (recursive CTEs) degrade at scale. Neo4j is fast but adds operational complexity. In-memory graphs lose persistence.

**Mitigation:**
- Hybrid storage: PostgreSQL for items/links (ACID, transactions), Neo4j for graph analytics (optional)
- Materialized views for common queries: `untested_requirements_mv`, `coverage_by_feature_mv`
- Refresh strategy: incremental (trigger-based) for hot paths, nightly batch for analytics
- In-memory graph cache (NetworkX) per project, invalidated on mutation
- Query optimization: denormalize link counts (`incoming_count`, `outgoing_count` on items)
- Pagination + cursor-based navigation for large result sets
- Index strategy: compound indexes on `(project_id, type, status)`, `(source_item_id, target_item_id, link_type)`
- Partition by project for multi-tenancy isolation

### M4: AI Hallucination in Auto-Linking

LLM suggests links between items based on semantic similarity. High recall (finds most valid links) but low precision (many false positives).

**Problem:** "Requirement FR-123: User authentication" might link to 20 different code files, but only 3 are actually implementing auth. False positives waste user time reviewing bad suggestions.

**Mitigation:**
- Multi-signal scoring model: (a) semantic similarity (embeddings), (b) keyword overlap, (c) graph distance (already linked items nearby), (d) historical acceptance rate (learn from user feedback)
- Confidence threshold: only surface suggestions >70% confidence
- Explainability: show *why* the link was suggested (e.g., "Both mention 'JWT token validation'")
- User feedback loop: thumbs up/down on suggestions → retrain scoring model
- Batch suggestion UI: review 10 suggestions at once, accept/reject with checkboxes
- Incremental learning: store accepted/rejected links as training data
- Fallback: if precision drops below 50%, disable auto-suggest and alert

### M5: BDD Execution Ambiguity

Gherkin scenarios written in natural language. Mapping "Given user is logged in" to actual test setup code is non-trivial.

**Problem:** No standard for executable specifications. Cucumber uses step definitions (code), but TraceRTM needs to *generate* test code from scenarios or *link* existing tests.

**Mitigation:**
- Hybrid approach: (a) AI-assisted step definition generation (LLM writes boilerplate test code from Gherkin), (b) Manual linking to existing test functions
- Parse Gherkin into structured AST: `Scenario → [Step{type, text, args}]`
- Step library: reusable step definitions with parameter templates (e.g., "Given user {username} is logged in" → `login_user(username)`)
- Execution modes: (a) Dry-run (validate step definitions exist), (b) Live run (execute against test environment)
- Coverage tracking: which Gherkin scenarios have executable step definitions vs. manual tests vs. no tests
- Validation: flag scenarios with ambiguous steps (e.g., "user clicks the button" — which button?)

### M6: Compliance Audit Scale

FDA 21 CFR Part 11 requires complete audit trails: who changed what, when, why. For 100,000 items × 50 revisions each = 5 million audit records.

**Problem:** Naive event sourcing (store every mutation as immutable event) creates massive storage and query complexity.

**Mitigation:**
- Tiered audit storage: (a) Hot (last 90 days): PostgreSQL, indexed, fast queries. (b) Warm (90 days–2 years): S3/MinIO as Parquet files, indexed by date. (c) Cold (>2 years): Glacier/archival
- Blockchain anchor: daily merkle root of all events → immutable timestamp proof
- Aggregate audit queries: "Show me all changes to requirement FR-123" → load from hot tier first, fall back to warm
- Prune non-critical events after retention period (e.g., "viewed item" logs expire after 1 year)
- Compliance export: on-demand generation of audit CSV for specific date range
- Tamper detection: verify blockchain anchor matches stored events

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  React SPA (Vite) · Desktop App (Tauri) · CLI · AI Agents (MCP)   │
└────────────┬────────────────────────────────────────────────────────┘
             │
             │ REST API / WebSocket / MCP Protocol
             │
┌────────────▼────────────────────────────────────────────────────────┐
│                      API GATEWAY (Caddy)                            │
│  Routing · TLS · Rate Limiting · Auth Middleware                   │
└────┬───────────────────────────────────────────────────────┬────────┘
     │                                                        │
     │                                                        │
┌────▼────────────────────────────┐         ┌────────────────▼────────┐
│   PYTHON BACKEND (FastAPI)      │         │   GO BACKEND (Echo)     │
│                                  │         │                         │
│ • FastMCP Server (50+ tools)     │         │ • High-performance      │
│ • AI Services (LLM integration)  │         │   graph queries         │
│ • Import/Export                  │         │ • Metrics collection    │
│ • Auto-linking                   │         │ • Code indexing         │
│ • Quality scoring                │         │ • gRPC services         │
│ • Workflow orchestration         │         │                         │
└────┬────────────────────────────┘         └────────────────┬────────┘
     │                                                        │
     └──────────────────┬───────────────────────────────────┘
                        │
            ┌───────────▼───────────┐
            │   DATA LAYER          │
            │                       │
            │ PostgreSQL (relational│
            │   items, links, users)│
            │                       │
            │ Neo4j (graph analytics│
            │   optional, perf)     │
            │                       │
            │ Redis (cache, sessions│
            │   pub/sub)            │
            │                       │
            │ NATS (event bus,      │
            │   async processing)   │
            └───────────┬───────────┘
                        │
            ┌───────────▼───────────┐
            │  INFRASTRUCTURE       │
            │                       │
            │ Temporal (workflows,  │
            │   sagas, long-running)│
            │                       │
            │ S3/MinIO (file storage│
            │   exports, backups)   │
            │                       │
            │ Prometheus + Grafana  │
            │   (metrics, alerts)   │
            └───────────────────────┘
```

### Service Communication

- **REST API:** Primary interface for CRUD operations, synchronous queries
- **WebSocket:** Real-time collaboration updates, live notifications
- **gRPC:** Backend-to-backend communication (Python ↔ Go) for performance-critical operations
- **MCP Protocol:** AI agent tool invocation (stdio transport for local, HTTP for remote)
- **Event Bus (NATS):** Async workflows (import processing, batch exports, scheduled analytics)

### Data Flow Example: Auto-Link Suggestion

1. User creates new requirement → POST /items → Python backend
2. Python backend: Save to PostgreSQL, publish `item.created` event to NATS
3. Auto-link service (async worker) consumes event
4. Call AI service → generate embeddings → query vector similarity
5. Score candidates (hybrid model: embeddings + keywords + graph distance)
6. Store suggestions in `link_suggestions` table (status=pending)
7. Publish `suggestions.ready` event → WebSocket → UI notification
8. User reviews suggestions → PATCH /links/suggestions/{id}/accept → create link

---

## 4. Data Schema (Core Tables)

### Core Traceability Tables

```sql
-- Items: Universal traceable entity (requirements, code, tests, etc.)
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,  -- requirement, code_file, test_case, feature, etc.
    status VARCHAR(50),  -- draft, active, implemented, tested, deprecated
    priority VARCHAR(20),  -- p0, p1, p2, p3
    external_id VARCHAR(255),  -- GitHub issue #, Jira key, etc.
    source_type VARCHAR(50),  -- github, jira, linear, manual
    metadata JSONB,  -- extensible properties
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    INDEX idx_items_project_type (project_id, type),
    INDEX idx_items_project_status (project_id, status),
    INDEX idx_items_external (external_id, source_type)
);

-- Links: Bi-directional typed relationships
CREATE TABLE links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    graph_id VARCHAR(255) REFERENCES graphs(id) ON DELETE CASCADE,
    source_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    target_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL,  -- implements, tests, depends_on, traces_to, etc.
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE (source_item_id, target_item_id, link_type),
    INDEX idx_links_source (source_item_id),
    INDEX idx_links_target (target_item_id),
    INDEX idx_links_type (project_id, link_type)
);

-- Features: High-level product features
CREATE TABLE features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),  -- planned, in_progress, completed, deprecated
    progress_percentage INT DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
    parent_feature_id UUID REFERENCES features(id),  -- for sub-features
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Test Cases: BDD scenarios, unit tests, integration tests
CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50),  -- unit, integration, e2e, manual, bdd
    scenario_text TEXT,  -- Gherkin or plain text
    status VARCHAR(50),  -- pending, passing, failing, skipped
    last_run_at TIMESTAMPTZ,
    execution_time_ms INT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- External Links: Links to external systems (GitHub PRs, Jira tickets, etc.)
CREATE TABLE external_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    external_type VARCHAR(50) NOT NULL,  -- github_issue, github_pr, jira_ticket, etc.
    external_id VARCHAR(255) NOT NULL,
    url TEXT,
    status VARCHAR(50),
    last_synced_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (item_id, external_type, external_id)
);
```

### Collaboration & Events

```sql
-- Events: Audit trail + event sourcing
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,  -- item.created, link.deleted, status.changed, etc.
    aggregate_type VARCHAR(50) NOT NULL,  -- item, link, project, user
    aggregate_id UUID NOT NULL,
    user_id UUID REFERENCES users(id),
    payload JSONB NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_events_aggregate (aggregate_type, aggregate_id),
    INDEX idx_events_type (event_type),
    INDEX idx_events_time (occurred_at DESC)
);

-- Notifications: User-facing alerts
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link_url TEXT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_notifications_user (user_id, read, created_at DESC)
);

-- Webhooks: Outbound event notifications
CREATE TABLE webhook_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    secret TEXT,
    event_types VARCHAR(50)[] NOT NULL,  -- Array of subscribed event types
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### AI & Automation

```sql
-- Agent Sessions: Track multi-agent workflows
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_type VARCHAR(50) NOT NULL,  -- import, analysis, workflow
    status VARCHAR(50) NOT NULL,  -- running, completed, failed
    metadata JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Agent Events: Per-agent actions within session
CREATE TABLE agent_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
    agent_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_agent_events_session (session_id, occurred_at)
);

-- Workflow Runs: Temporal workflow execution tracking
CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_type VARCHAR(100) NOT NULL,
    workflow_id VARCHAR(255) NOT NULL,  -- Temporal workflow ID
    status VARCHAR(50) NOT NULL,
    input JSONB,
    output JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    INDEX idx_workflow_runs_type (workflow_type, status)
);
```

---

## 5. Phased WBS with DAG Dependencies

### Phase 0: Foundation (COMPLETE ✅)

**Status:** Infrastructure, database, auth, core models all operational

| Task ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| P0.1 | Project scaffold (monorepo, configs, tooling) | ✅ Complete | Go + Python + TS, process-compose, Makefile |
| P0.2 | PostgreSQL schema (Alembic migrations) | ✅ Complete | 50+ tables, indexes, constraints |
| P0.3 | Core models (Item, Link, Project, User) | ✅ Complete | SQLAlchemy + GORM, full CRUD |
| P0.4 | Authentication (WorkOS SSO) | ✅ Complete | OAuth2, JWT tokens, RBAC |
| P0.5 | API scaffolding (FastAPI + Echo routers) | ✅ Complete | 200+ endpoints, OpenAPI docs |
| P0.6 | Frontend base (React + Vite) | ✅ Complete | Zustand state, React Query, Storybook |
| P0.7 | Dev environment (process-compose) | ✅ Complete | 10+ services, hot reload, health checks |

**Dependencies:** None (bootstrap phase)

---

### Phase 1: Discovery & Capture (75% Complete)

**Goal:** Import requirements from external systems, parse specifications, auto-link items

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P1.1 | GitHub import (issues, PRs via GraphQL) | P0.3, P0.5 | ✅ Complete | — |
| P1.2 | Jira import (REST API v3, incremental sync) | P0.3, P0.5 | ✅ Complete | — |
| P1.3 | Linear import (GraphQL, issue sync) | P0.3, P0.5 | 🚧 Partial | ~10 min |
| P1.4 | Specification parser (Markdown, ReqIF, Word) | P0.3 | ✅ Complete | — |
| P1.5 | AI embedding generation (OpenAI/Anthropic) | P1.4 | ✅ Complete | — |
| P1.6 | Auto-link suggestion engine (semantic + keywords) | P1.5 | ✅ Complete | — |
| P1.7 | User feedback loop (accept/reject suggestions) | P1.6 | ✅ Complete | — |
| P1.8 | Commit linking (Git hooks → link code changes) | P1.1 | ✅ Complete | — |
| P1.9 | Deduplication (hash-based, prevent duplicate imports) | P1.1, P1.2, P1.3 | 🚧 Partial | ~5 min |

**Critical Path:** P1.1 → P1.4 → P1.5 → P1.6 → P1.7 (serial)
**Parallel Work:** P1.2, P1.3 can run alongside P1.1

**Remaining Work:**
- Complete Linear integration (P1.3: adapter, sync service, mapping)
- Enhance deduplication (P1.9: cross-source duplicate detection)

---

### Phase 2: Qualification & Analysis (60% Complete)

**Goal:** Score requirement quality, analyze graph, detect issues, track coverage

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P2.1 | Requirement quality scoring (EARS, completeness) | P1.4 | ✅ Complete | — |
| P2.2 | Graph cycle detection (find circular dependencies) | P0.3 | ✅ Complete | — |
| P2.3 | Critical path analysis (longest dependency chain) | P2.2 | ✅ Complete | — |
| P2.4 | Dependency analysis (transitive closure) | P0.3 | ✅ Complete | — |
| P2.5 | Coverage matrix generation (requirements × tests) | P0.3 | ✅ Complete | — |
| P2.6 | Impact analysis (change propagation prediction) | P2.4 | 🚧 Partial | ~8 min |
| P2.7 | Orphan detection (unlinked items) | P0.3 | ✅ Complete | — |
| P2.8 | Graph validation (integrity checks, constraint enforcement) | P0.3 | ✅ Complete | — |
| P2.9 | Shortest path queries (any node to any node) | P0.3 | 🚧 Partial | ~5 min |

**Critical Path:** P2.4 → P2.6 (impact analysis needs dependency graph)
**Parallel Work:** P2.1, P2.2, P2.5 are independent

**Remaining Work:**
- Complete impact analysis (P2.6: forward/backward propagation, confidence scores)
- Optimize shortest path (P2.9: in-memory graph cache, batch queries)

---

### Phase 3: Application & Tracking (85% Complete)

**Goal:** Full CRUD for items/links, status workflows, progress tracking

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P3.1 | Item CRUD endpoints (create, read, update, delete) | P0.3, P0.5 | ✅ Complete | — |
| P3.2 | Link CRUD endpoints (create, read, delete) | P0.3, P0.5 | ✅ Complete | — |
| P3.3 | Bulk operations (batch create, batch update) | P3.1, P3.2 | ✅ Complete | — |
| P3.4 | Status workflow engine (state machine, transitions) | P3.1 | ✅ Complete | — |
| P3.5 | Progress tracking (feature completion %) | P3.1 | ✅ Complete | — |
| P3.6 | Feature management (create, assign items to features) | P3.1 | ✅ Complete | — |
| P3.7 | Search & filter (full-text, faceted, pagination) | P3.1 | ✅ Complete | — |
| P3.8 | History tracking (audit trail, change log) | P3.1 | ✅ Complete | — |
| P3.9 | Undo/redo support (event sourcing-based) | P3.8 | ⏸️ Deferred | ~15 min |

**Critical Path:** P3.1 → P3.4 → P3.5 (serial)
**Parallel Work:** P3.2, P3.6, P3.7 are independent

**Remaining Work:**
- Implement undo/redo (P3.9: requires event replay, UI controls)

---

### Phase 4: Verification & Validation (40% Complete)

**Goal:** Test management, execution tracking, coverage reporting

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P4.1 | Test case model (BDD scenarios, unit tests) | P0.3 | ✅ Complete | — |
| P4.2 | Test suite management (group tests, run subsets) | P4.1 | ✅ Complete | — |
| P4.3 | Gherkin parser (parse .feature files into AST) | P4.1 | ✅ Complete | — |
| P4.4 | Test execution tracking (status, duration, logs) | P4.1 | 🚧 Partial | ~10 min |
| P4.5 | Coverage aggregation (link tests → requirements) | P4.1, P2.5 | ✅ Complete | — |
| P4.6 | Validation reporting (compliance audit format) | P4.5 | ⏸️ Deferred | ~10 min |
| P4.7 | BDD step definition generator (AI-assisted) | P4.3 | ⏸️ Deferred | ~20 min |
| P4.8 | Test result ingestion (JUnit XML, pytest JSON) | P4.4 | 🚧 Partial | ~8 min |
| P4.9 | Graph validation scheduler (daily integrity checks) | P2.8 | ⏸️ Deferred | ~5 min |

**Critical Path:** P4.1 → P4.3 → P4.7 (BDD workflow)
**Parallel Work:** P4.2, P4.4, P4.5 are independent

**Remaining Work:**
- Complete test execution tracking (P4.4: real-time status updates, failure analysis)
- Build validation reporting (P4.6: FDA/ISO compliance templates)
- Implement BDD code generation (P4.7: LLM-based step definition creation)
- Enhance test result ingestion (P4.8: support more formats, detect flaky tests)
- Schedule graph validation (P4.9: cron job, alert on failures)

---

### Phase 5: Reporting & Analytics (80% Complete)

**Goal:** Traceability matrices, dashboards, metrics, exports

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P5.1 | Traceability matrix generation (requirements × tests) | P2.5 | ✅ Complete | — |
| P5.2 | Coverage report UI (visualize gaps) | P5.1 | ✅ Complete | — |
| P5.3 | Analytics dashboard (charts, KPIs) | P0.6 | ✅ Complete | — |
| P5.4 | Metrics service (Prometheus integration) | P0.7 | ✅ Complete | — |
| P5.5 | Export to PDF (traceability reports) | P5.1 | ✅ Complete | — |
| P5.6 | Export to Excel (matrices, item lists) | P5.1 | ✅ Complete | — |
| P5.7 | Custom report builder (user-defined queries) | P3.7 | ⏸️ Deferred | ~15 min |
| P5.8 | Scheduled reports (email delivery, weekly digests) | P5.5, P5.6 | ⏸️ Deferred | ~10 min |
| P5.9 | Graph visualization (interactive canvas, D3/Cytoscape) | P0.6 | ✅ Complete | — |

**Critical Path:** P5.1 → P5.2 → P5.5 (serial report generation)
**Parallel Work:** P5.3, P5.4, P5.9 are independent

**Remaining Work:**
- Build custom report builder (P5.7: SQL query UI, template library)
- Implement scheduled reports (P5.8: cron jobs, email integration)

---

### Phase 6: Collaboration & Integration (50% Complete)

**Goal:** Real-time collaboration, external system sync, webhooks, AI chat

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P6.1 | WebSocket server (real-time updates) | P0.5 | ✅ Complete | — |
| P6.2 | Conflict resolution UI (handle concurrent edits) | P6.1 | 🚧 Partial | ~15 min |
| P6.3 | Bidirectional sync (GitHub: push changes back) | P1.1 | 🚧 Partial | ~20 min |
| P6.4 | Bidirectional sync (Jira: update ticket status) | P1.2 | 🚧 Partial | ~20 min |
| P6.5 | Webhook system (outbound event notifications) | P3.8 | ✅ Complete | — |
| P6.6 | Webhook ingestion (receive external events) | P6.5 | ✅ Complete | — |
| P6.7 | AI chat assistant (conversational interface) | P0.6 | 🚧 Partial | ~10 min |
| P6.8 | Notification service (in-app, email, Slack) | P3.8 | ✅ Complete | — |
| P6.9 | Activity feed (per-project, per-user) | P3.8 | ✅ Complete | — |

**Critical Path:** P6.1 → P6.2 (conflict resolution needs WebSocket)
**Parallel Work:** P6.3, P6.4, P6.5, P6.7, P6.8, P6.9 are independent

**Remaining Work:**
- Complete conflict resolution UI (P6.2: vector clocks, merge strategies)
- Finish bidirectional sync (P6.3, P6.4: push status changes, update external IDs)
- Enhance AI chat assistant (P6.7: context-aware responses, multi-turn conversations)

---

### Phase 7: AI & Automation (70% Complete)

**Goal:** AI analysis, agent coordination, MCP server, workflow automation

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P7.1 | FastMCP server scaffold (50+ tools) | P0.5 | ✅ Complete | — |
| P7.2 | MCP tools: CRUD operations (create_item, update_link, etc.) | P7.1 | ✅ Complete | — |
| P7.3 | MCP tools: Analysis (detect_cycles, analyze_impact, etc.) | P7.1, P2.2, P2.6 | ✅ Complete | — |
| P7.4 | MCP tools: Reporting (generate_matrix, export_report) | P7.1, P5.1 | ✅ Complete | — |
| P7.5 | Agent coordination service (multi-agent workflows) | P7.1 | ✅ Complete | — |
| P7.6 | AI-powered analysis (natural language queries) | P7.1 | ✅ Complete | — |
| P7.7 | Workflow automation (Temporal workflows) | P0.7 | 🚧 Partial | ~20 min |
| P7.8 | Code indexing (AST parsing, symbol extraction) | P1.8 | 🚧 Partial | ~15 min |
| P7.9 | AI review assistant (suggest improvements to requirements) | P7.6 | ⏸️ Deferred | ~15 min |

**Critical Path:** P7.1 → P7.2 → P7.3 → P7.4 (serial tool development)
**Parallel Work:** P7.5, P7.6, P7.7, P7.8 are independent

**Remaining Work:**
- Complete Temporal workflows (P7.7: long-running imports, scheduled analytics)
- Finish code indexing (P7.8: support more languages, LSP integration)
- Build AI review assistant (P7.9: quality suggestions, best practice recommendations)

---

### Phase 8: Documentation & Onboarding (30% Complete)

**Goal:** User guides, API docs, tutorials, sample projects

| Task ID | Description | Depends On | Status | Est. Wall Clock |
|---------|-------------|------------|--------|-----------------|
| P8.1 | User guide (getting started, core workflows) | P3.1 | 🚧 Partial | ~15 min |
| P8.2 | API documentation (OpenAPI, interactive examples) | P0.5 | ✅ Complete | — |
| P8.3 | MCP tool reference (auto-generated from schemas) | P7.1 | ✅ Complete | — |
| P8.4 | Video tutorials (onboarding, key features) | P8.1 | ⏸️ Deferred | ~30 min |
| P8.5 | Sample projects (pre-configured demo data) | P3.6 | ⏸️ Deferred | ~20 min |
| P8.6 | Migration guide (from other tools: Jira, Azure DevOps) | P1.1, P1.2 | ⏸️ Deferred | ~10 min |
| P8.7 | Admin guide (deployment, configuration, troubleshooting) | P0.7 | 🚧 Partial | ~15 min |
| P8.8 | Contributing guide (developer setup, PR workflow) | P0.1 | ⏸️ Deferred | ~10 min |

**Critical Path:** P8.1 → P8.4 (tutorials need core guide first)
**Parallel Work:** P8.2, P8.3, P8.5, P8.6, P8.7, P8.8 are independent

**Remaining Work:**
- Complete user guide (P8.1: advanced workflows, troubleshooting)
- Create video tutorials (P8.4: screen recordings, voice-over)
- Build sample projects (P8.5: demo datasets, common scenarios)
- Write migration guides (P8.6: export from Jira → import to TraceRTM)
- Finish admin guide (P8.7: production deployment, scaling, backups)
- Add contributing guide (P8.8: code conventions, testing requirements)

---

## 6. DAG Visualization (High-Level)

```
P0 (Foundation) ──┬── P1 (Discovery) ──┬── P2 (Analysis) ──┬── P5 (Reporting)
                  │                     │                   │
                  │                     └── P4 (V&V) ───────┤
                  │                                          │
                  ├── P3 (Tracking) ────────────────────────┤
                  │                                          │
                  ├── P6 (Collaboration) ───────────────────┤
                  │                                          │
                  ├── P7 (AI & Automation) ─────────────────┤
                  │                                          │
                  └── P8 (Documentation) ───────────────────┘
                                                             │
                                                             └── MVP Launch
```

### Dependency Details

- **P1 depends on P0:** Import services need database + API layer
- **P2 depends on P1:** Analysis needs imported data
- **P3 depends on P0:** CRUD operations need core infrastructure
- **P4 depends on P1, P2:** Testing needs items + coverage analysis
- **P5 depends on P2, P4:** Reporting aggregates analysis + test results
- **P6 depends on P1, P3:** Collaboration needs data + CRUD
- **P7 depends on P0, P1, P2:** AI needs infrastructure + data + analysis
- **P8 depends on all:** Documentation written after features implemented

---

## 7. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Graph query performance degrades at scale (>10K nodes)** | Medium | High | Materialized views, in-memory cache, Neo4j fallback, pagination |
| **AI auto-linking has low precision (<50%)** | Medium | High | Multi-signal scoring, confidence thresholds, user feedback loop, explainability |
| **External API rate limits block sync** | High | Medium | Incremental sync, exponential backoff, queue-based processing, cache external data |
| **WebSocket connection instability** | Medium | Medium | Auto-reconnect, message replay, offline support with local cache |
| **Database migration failures in production** | Low | High | Blue-green deployment, schema versioning, rollback procedures, pre-flight validation |
| **LLM API costs exceed budget** | Medium | Medium | Prompt optimization, caching embeddings, local models for simple tasks, cost monitoring |
| **Compliance audit trail storage growth** | High | Medium | Tiered storage (hot/warm/cold), blockchain anchors, retention policies, compression |
| **Multi-tenancy data isolation breach** | Low | Critical | Row-level security, project_id in all queries, audit access patterns, penetration testing |
| **Temporal workflow state corruption** | Low | High | Workflow versioning, deterministic execution, saga pattern for rollback, monitoring |
| **Real-time collaboration conflicts cause data loss** | Medium | High | Event sourcing, conflict queue UI, user decision, no auto-merge for critical fields |

---

## 8. Tech Stack Summary

| Component | Technology | Rationale | ADR Reference |
|-----------|-----------|-----------|---------------|
| **API Framework (Python)** | FastAPI | High performance async, OpenAPI auto-generation, Pydantic validation | ADR-0001 |
| **API Framework (Go)** | Echo | Ultra-fast routing, middleware support, minimal overhead | ADR-0010 |
| **Database** | PostgreSQL | ACID, jsonb, full-text search, mature | ADR-0007 |
| **Graph Store** | Neo4j (optional) | Graph-native queries, Cypher language, performance at scale | ADR-0014 |
| **Cache** | Redis | Distributed caching, pub/sub, session storage | ADR-0007 |
| **Event Bus** | NATS | Lightweight, high throughput, pub/sub + queue groups | ADR-0001 |
| **Workflows** | Temporal | Saga pattern, long-running workflows, durable execution | ADR-0001 |
| **Frontend** | React + Vite | Component model, fast dev server, TypeScript support | ADR-0011 |
| **State Management** | Zustand | Simple API, TypeScript-first, minimal boilerplate | ADR-0011 |
| **Server Data** | React Query | Caching, invalidation, optimistic updates, auto-retry | ADR-0011 |
| **Styling** | Tailwind CSS | Utility-first, fast iteration, consistent design system | ADR-0011 |
| **Real-Time** | WebSocket | Bidirectional, low latency, native browser support | ADR-0008 |
| **AI Protocol** | FastMCP | Model Context Protocol v2.14, 50+ tools, stdio/HTTP transports | ADR-0002 |
| **Auth** | WorkOS | SSO, OAuth 2.0, RBAC, multi-tenant isolation | ADR-0009 |
| **Observability** | Prometheus + Grafana | Metrics, dashboards, alerting | ADR-0012 |
| **Tracing** | OpenTelemetry | Distributed tracing, span correlation | ADR-0012 |
| **Storage** | S3/MinIO | Object storage for exports, backups, file uploads | ADR-0015 |
| **Testing (Python)** | pytest | Fixture model, coverage integration, plugin ecosystem | ADR-0005 |
| **Testing (Go)** | Testify | Assertions, mocking, suite organization | ADR-0005 |
| **Testing (TS)** | Vitest | Fast, Vite-native, Jest-compatible API | ADR-0005 |
| **E2E Testing** | Playwright | Cross-browser, reliable, code generation | ADR-0005 |
| **BDD Parser** | Gherkin (behave) | Standard syntax, wide adoption, tooling support | ADR-0003 |
| **Visualization** | D3 + Cytoscape.js | Force-directed layouts, interactive graph exploration | ADR-0004 |
| **Package Manager** | bun | Fast installs, drop-in npm replacement | CLAUDE.md |
| **Process Orchestration** | process-compose | Native (no Docker), YAML config, health checks | CLAUDE.md |
| **Deployment (Local)** | Native services | PostgreSQL, Redis, Caddy as native processes | CLAUDE.md |
| **Deployment (Prod)** | Kubernetes | Container orchestration, scaling, self-healing | ADR-0006 |

---

## 9. Implementation Priorities (MVP Scope)

### Must-Have for MVP (Q1 2026)

- ✅ **P0 Foundation:** Database, auth, core API, dev environment
- ✅ **P1.1, P1.2:** GitHub + Jira import
- ✅ **P1.6, P1.7:** Auto-link suggestions with feedback
- ✅ **P2.1, P2.2, P2.5:** Quality scoring, cycle detection, coverage matrix
- ✅ **P3.1–P3.8:** Full CRUD, workflows, search, history
- ✅ **P4.1–P4.3, P4.5:** Test models, Gherkin parser, coverage aggregation
- ✅ **P5.1, P5.2, P5.5, P5.6:** Traceability matrix, reports, export
- ✅ **P6.1, P6.5, P6.6, P6.8, P6.9:** WebSocket, webhooks, notifications
- ✅ **P7.1–P7.6:** MCP server, 50+ tools, agent coordination, AI analysis
- 🚧 **P8.1, P8.2, P8.3:** User guide, API docs, MCP reference

### Phase 2 Features (Q2 2026)

- **P1.3, P1.9:** Linear import, deduplication
- **P2.6, P2.9:** Impact analysis, shortest path queries
- **P4.4, P4.8:** Test execution tracking, result ingestion
- **P6.2, P6.3, P6.4:** Conflict resolution, bidirectional sync
- **P7.7, P7.8:** Temporal workflows, code indexing

### Phase 3 Features (Q3 2026)

- **P3.9:** Undo/redo support
- **P4.6, P4.7, P4.9:** Validation reporting, BDD code generation, scheduled validation
- **P5.7, P5.8:** Custom report builder, scheduled reports
- **P6.7:** AI chat assistant
- **P7.9:** AI review assistant
- **P8.4–P8.8:** Video tutorials, sample projects, migration/admin guides

---

## 10. Success Metrics (6-Month Targets)

| Metric | Target | Measurement | Current Status |
|--------|--------|-------------|----------------|
| **Traceability Coverage** | >85% of requirements linked | (linked items / total items) × 100 | 🔍 TBD (post-MVP) |
| **Query Performance** | p95 <100ms for graph queries | Prometheus histogram | ✅ 45ms avg (Phase 4) |
| **User Adoption** | >80% of team using weekly | Active sessions per week | 🚀 Pre-launch |
| **MCP Tool Usage** | >50 agent tool calls/day | MCP metrics service | ✅ 120+ calls/day (dev) |
| **Test Coverage** | >80% overall, >90% critical | Coverage aggregation service | ✅ 85% Python, 32% Go, 78% TS |
| **Auto-Link Accuracy** | >75% precision | Manual validation sample | 🔍 TBD (post-MVP) |
| **Time Savings** | 60% reduction in manual linking | Before/after time tracking | 🔍 TBD (user study) |

---

## 11. Open Questions & Decisions Needed

### Technical Decisions

1. **Neo4j vs. PostgreSQL for graph queries:** Continue hybrid approach or fully commit to Neo4j for all analytics?
   - **Current:** PostgreSQL primary, Neo4j optional for large-scale queries
   - **Decision:** Keep hybrid (reduce operational complexity)

2. **Event sourcing scope:** Event-source all mutations or only critical ones?
   - **Current:** Event log for audit trail, not full CQRS
   - **Decision:** Pragmatic event sourcing (audit + replay for critical paths)

3. **AI model choice:** Claude Opus vs. GPT-4 for auto-linking?
   - **Current:** Claude Opus via Anthropic API
   - **Decision:** Stick with Claude (better for reasoning, longer context)

### Product Decisions

4. **Free vs. paid tiers:** What features are free, what requires subscription?
   - **Proposal:** Free (up to 1K items, 1 project), Pro ($29/mo per user, unlimited), Enterprise (custom pricing, SSO, SLA)

5. **Target market:** Developer tools vs. regulated industries (FDA, aerospace)?
   - **Proposal:** Dual market (PLG for dev teams, enterprise sales for regulated)

6. **Integration priority:** Azure DevOps vs. GitLab vs. Bitbucket next?
   - **Proposal:** Azure DevOps (enterprise demand), then GitLab (open-source)

---

## 12. Next Steps (Immediate Actions)

### Week 1 (2026-02-12 to 2026-02-19)

1. **Complete P1.3 (Linear import):** Build LinearAdapter, sync service, test on sample data
2. **Finish P2.6 (Impact analysis):** Forward/backward propagation, confidence scores, UI
3. **Start P4.4 (Test execution tracking):** Real-time status updates, failure logs
4. **Polish P8.1 (User guide):** Complete getting started, add troubleshooting section

### Week 2-4 (February)

5. **Launch MVP beta:** Invite 10 pilot users (internal + friendly companies)
6. **Collect feedback:** Weekly interviews, async Slack channel, analytics dashboard
7. **Iterate on auto-link precision:** A/B test scoring models, tune thresholds
8. **Complete P6.2 (Conflict resolution):** Vector clocks, merge UI, test with concurrent edits

### Q2 2026 (April-June)

9. **Scale testing:** Load test with 100K items, optimize queries, tune caching
10. **Enterprise features:** SSO (Okta, Azure AD), advanced RBAC, audit exports
11. **Bidirectional sync:** Complete P6.3, P6.4 (push changes back to GitHub/Jira)
12. **Marketing launch:** Product Hunt, HN, dev conferences, case studies

---

**End of Plan**
