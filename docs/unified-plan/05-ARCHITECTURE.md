# 05 -- Architecture

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [04-REQUIREMENTS](./04-REQUIREMENTS.md) | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md)

---

## ADR Summary (15 ADRs)

| ADR | Title | Status | Decision |
|-----|-------|--------|----------|
| ADR-0001 | TraceRTM v2 Architecture | Accepted | Layered transformation: spec-driven + BDD + MCP + visual UI |
| ADR-0002 | FastMCP Integration | Accepted | FastMCP 3.0.0+ (production-ready) for AI-native MCP tooling |
| ADR-0003 | Gherkin/BDD Parser | Accepted | `gherkin-official` parser + `pytest-bdd` execution |
| ADR-0004 | Graph Visualization | Accepted | React Flow (xyflow) for component-based nodes |
| ADR-0005 | Test Strategy | Accepted | 80% min coverage, pytest/testify/vitest |
| ADR-0006 | Deployment Architecture | Accepted | Vercel (frontend) + Fly.io (backend) + Neon/Supabase (DB) + MinIO S3 |
| ADR-0007 | Database Architecture | Accepted | PostgreSQL 16+ with pgvector, pg_trgm, uuid-ossp extensions |
| ADR-0008 | Real-Time Collaboration | Accepted | NATS JetStream (pub/sub + durable subscriptions) + WebSocket hub (Go) |
| ADR-0009 | Authentication Strategy | Accepted | WorkOS SSO + JWT (15min access) + refresh tokens (7d HttpOnly) + RBAC |
| ADR-0010 | Multi-Language Backend | Accepted | Python (FastAPI) + Go (Echo v4 + gRPC); shared PostgreSQL + Redis + NATS |
| ADR-0011 | Frontend Framework | Accepted | React 19 + Vite + TanStack Router + Zustand + Radix UI + OxLint |
| ADR-0012 | Code Quality Enforcement | Accepted | Ruff (Python) + golangci-lint (Go) + OxLint (TS) + architecture enforcement |
| ADR-0013 | AI Agent Coordination | Accepted | Claude Opus 4.6 + Sonnet 4.5, BMM methodology, multi-agent swarms |
| ADR-0014 | Graph Data Structure | Accepted | PostgreSQL CTEs (persistent) + NetworkX (Python analysis) + custom Go algorithms |
| ADR-0015 | Import/Export Strategy | Accepted | GitHub/Jira GraphQL+webhooks (full sync), Linear/CSV (import), webhook triggers |

---

## System Architecture Layers

```
                    +-----------------------+
                    |    Client Layer       |
                    | CLI | TUI | Web | MCP |
                    +----------+------------+
                               |
                    +----------v------------+
                    |    API Gateway         |
                    |  Caddy v2 (port 4000)  |
                    +---+--------+----------+
                        |        |
               +--------v--+  +-v-----------+
               | Python API |  | Go API      |
               | (FastAPI)  |  | (Echo v4)   |
               +-----+------+ +------+------+
                     |               |
               +-----v---------------v------+
               |    Service Layer            |
               | Business Logic (92 svc)     |
               +-----+---------------+------+
                     |               |
               +-----v------+ +-----v------+
               | Repository | | Repository |
               |(SQLAlchemy2)|(pgx v5)     |
               +-----+------+ +-----+------+
                     |               |
          +----------v------+--------v-----+
          | PostgreSQL 16+  | Neo4j (opt)  |
          | (SSOT + pgvec)  | (graph DB)   |
          +-----------------+-------------+
                     |
          +----------v-----+-------+-------+
          | NATS | Redis | MinIO| Vault |
          | PubSub Cache S3   Secrets  |
          +-----------------------------+
```

**Key Decisions:**
- **Dual backend**: Python (FastAPI) for AI/MCP/CLI; Go (Echo v4) for high-throughput APIs and graph algorithms (ADR-0010)
- **Hybrid graph**: PostgreSQL CTEs for persistent queries, NetworkX (Python) for complex analysis, custom Go for bulk operations (ADR-0014)
- **SSOT**: PostgreSQL 16+ is canonical source; materialized views refresh within 5s for eventual consistency
- **Event-driven**: NATS JetStream for pub/sub with durable subscriptions, KV store, request/reply, dead-letter queue (ADR-0008)
- **92+ microservices**: Specialized services for requirements, testing, analytics, webhooks, chaos, performance, blockchain, etc.
- **Infrastructure stack**: Process Compose (local), native PostgreSQL/Redis/Neo4j/NATS (no Docker required)

---

## Atomic Architecture (16-View Multi-View PM)

TraceRTM uses an atomic decomposition approach where requirements are broken into swappable atoms:

**Atom Hierarchy:**
- **Level 0: ATOM** -- Capability primitive (~115 atoms total)
- **Level 1: MOLECULE** -- 2-5 atoms composed
- **Level 2: ORGANISM** -- 3-10 molecules
- **Level 3: TEMPLATE** -- Bounded context
- **Level 4: PRODUCT** -- Concrete configuration

**16 Views:**
Feature, Code, Wireframe, API, Test, Database, Deployment, Metrics, Compliance, Task, Dependency, Risk, Timeline, Resource, Decision, Artifact

**Cascading Updates:** Changes propagate across all 16 views via event sourcing. NATS pub/sub broadcasts updates. Materialized views refresh incrementally (5s window).

---

## Data Contracts

### Core Entity Model

```
Account (1) ---> (*) Project (1) ---> (*) Item ---> (*) Link ---> (1) Item
                                        |
                                        +---> (*) TestCase, TestSuite, TestRun
                                        +---> (*) Specification, ADR, Contract
                                        +---> (*) Problem, Process, Scenario
                                        +---> (*) Execution, ExecutionConfig
                                        +---> (*) ExternalLink, Integration
                                        +---> (*) Graph, GraphNode, GraphChange
                                        +---> (*) WorkflowRun, WorkflowSchedule
                                        +---> (*) Agent, AgentSession, AgentEvent
                                        +---> (*) Blockchain, VersionBlock, Baseline
```

### Key Entity Types

**Item Views:** Requirement, Feature, Epic, Story, Bug, Task, ADR, Specification, TestCase, Process, Problem, Scenario

**Link Types:** traces_to, implements, verifies, depends_on, parent_of, related_to, conflicts_with, derives_from, decomposed_by, refined_by

**Item Status:** Draft -> Review -> Approved -> Implemented -> Verified -> Archived

**Test Types:** Unit, Integration, E2E, Contract, Property-Based, Security, Performance, Accessibility

**TestCase Relations:** Traces to Requirement, verifies Link, covers Feature, validates Specification

**Advanced Models:**
- Blockchain (hash-chained events for audit trail)
- Graph (multi-view graph structure with snapshots)
- Integration (GitHub, Jira, Linear, Webhook)
- Execution (workflow/agent execution records)
- Specification (structured specs with constraints)

---

## SSOT Architecture

**Strong Consistency (ACID):** PostgreSQL canonical tables
**Eventual Consistency:** Materialized views refresh within 5s

**Materialized Views:**
1. Traceability matrix (bidirectional)
2. Impact analysis (recursive CTEs, depth=10)
3. Coverage analysis (req-to-test mapping)
4. Dependency graph (for graph algorithms)

**Performance Targets:**
- SSOT queries: <10ms (simple), <100ms (complex joins)
- View queries: <50ms (traceability, coverage), <100ms (impact, dependency)

---

## Key Architectural Patterns

### Pattern 1: Dual Backend Communication (ADR-0010)

Python (FastAPI) and Go (Echo v4) backends communicate via shared data layer:
- **Python services (92+)**: FastAPI REST, MCP server, AI/ML, CLI, TUI, data transformations
- **Go services**: High-throughput APIs, graph algorithms, gRPC, WebSocket hub, bulk operations
- **Shared layer**: PostgreSQL (primary), Redis (cache), NATS (events), protobuf (typed contracts)
- **Inter-service protocol**: gRPC for typed calls, HTTP for REST fallback, NATS pub/sub for events

### Pattern 2: Event Sourcing via NATS JetStream (ADR-0008)

All state changes emit events to NATS for reliable, distributed coordination:
- **Durable subscriptions**: Guaranteed delivery with consumer groups (failed messages retained)
- **KV Store**: Distributed state coordination, feature flags, locks
- **Request/Reply pattern**: Synchronous RPC-style calls over NATS
- **Dead-letter queue**: Capture and analyze failed message processing
- **Example streams**: item-created, link-added, test-run-completed, integration-synced

### Pattern 3: Multi-Signal Auto-Linking (implicit FR-DISC-004)

Intelligent link suggestions via four signals:
- **Embedding similarity**: Semantic search using pgvector (cosine distance)
- **Keyword matching**: TF-IDF indexing via PostgreSQL full-text search (pg_trgm)
- **Graph proximity**: Common ancestors/descendants in traceability graph
- **User feedback**: Learn from manual link corrections
- **Confidence threshold**: >0.7 to surface suggestion; user can confirm or reject

### Pattern 4: Hybrid Graph Storage (ADR-0014)

Three graph implementations optimized for different access patterns:
- **PostgreSQL CTEs**: Persistent stored queries, simple parent/child traversal, materialized views
- **NetworkX (Python)**: Complex analysis (SCC, critical path, cycle detection, impact analysis)
- **Custom Go algorithms**: Bulk operations, parallel graph reduction, performance-critical batch processing

### Pattern 5: Tiered Integration (ADR-0015)

Three tiers for external system connectivity:
- **Full (bidirectional)**: GitHub (OAuth + GraphQL + webhooks), Jira (API + webhooks) with conflict resolution
- **Import-only**: Linear (GraphQL), CSV (file upload) with incremental sync
- **Webhook-driven**: Inbound webhooks (from GitHub/Jira), outbound webhooks (status changes to external systems)

### Pattern 6: Progressive Disclosure in UI

Three tiers of information complexity:
- **Summary View**: Dashboard, key metrics, risk heatmap
- **Detail View**: Full item properties, relationships, history
- **Trace View**: Complete audit trail, evidence artifacts, proof of verification

### Pattern 7: Feature Flag & Chaos Mode

Runtime configuration without code changes:
- **Feature flags**: Toggle features per workspace (auth method, advanced analytics, chaos mode)
- **Chaos mode**: Inject failures, delays, network partition simulation for resilience testing
- **Atom-level control**: Enable/disable at granular (single capability) level

---

## Security Architecture (ADR-0009)

**Authentication Flow:**
```
User -> WorkOS SSO (Google/Microsoft/SAML/Okta)
     -> JWT access token (15min) + refresh token (7d, HttpOnly, secure)
     -> Session stored in Redis with TTL

Agent -> OAuth Device Flow -> API Key (scoped) -> JWT
     -> Rate-limited via Redis (per-key tracking)
```

**Authorization Model:**
- **RBAC with role hierarchy:** Admin > Manager > Editor > Viewer
- **Project-level isolation:** Users scoped to specific projects/accounts
- **Row-level security (RLS):** PostgreSQL policies enforce data visibility
- **API key scoping:** Restrict to read-only, write-only, or specific endpoints
- **Workspace isolation:** Data encrypted per workspace in Vault

**Data Protection:**
- **In transit:** TLS 1.3 (enforced on all connections)
- **At rest:** AES-256 via Vault (envelope encryption with key rotation)
- **Secrets management:** HashiCorp Vault for API keys, OAuth credentials, database passwords
- **Audit trail:** Hash-chained blockchain model ensures tamper-proof event log
- **Session security:** HttpOnly, Secure, SameSite=Strict cookies; no localStorage for tokens

---

## Deployment Architecture (ADR-0006)

**Production Stack:**

| Component | Service | Details |
|-----------|---------|---------|
| Frontend | Vercel | SPA + CDN, edge functions, automatic HTTPS |
| Python Backend | Fly.io | Docker container, auto-scaling, health checks |
| Go Backend | Fly.io | Docker container, high-throughput routes |
| Database | Neon or self-hosted PostgreSQL | 16+, pgvector, pg_trgm extensions |
| Graph DB | Neo4j Aura (optional) | Managed graph queries, cypher support |
| Cache | Upstash Redis | Serverless, auto-scaling, pub/sub |
| Messaging | Synadia NATS | Managed JetStream, durable queues |
| Storage | AWS S3 or MinIO | Object storage for artifacts, exports |
| Secrets | HashiCorp Vault | Managed or self-hosted, key rotation |
| Monitoring | Prometheus + Grafana | Metrics scrape, visualization, alerting |

**Development Stack:**
- **Orchestration:** Process Compose v1.2+ (native, not Docker)
- **Reverse Proxy:** Caddy v2 with auto-reload (port 4000 → backends)
- **Services:** Native binaries (PostgreSQL, Redis, Neo4j, NATS, MinIO, Vault)
- **Backend servers:** Air (Go rebuild on file change), uvicorn --reload (Python)
- **Frontend:** Vite dev server with HMR
- **No Docker required:** All services run natively on macOS/Linux

**Cost Estimate (MVP, ~1000 users):**
- Frontend: ~$20/mo (Vercel)
- Python Backend: ~$12/mo (Fly.io shared-cpu-1x)
- Go Backend: ~$12/mo (Fly.io shared-cpu-1x)
- Database: ~$30/mo (Neon with auto-scaling)
- Redis: ~$10/mo (Upstash serverless)
- NATS: ~$15/mo (Synadia managed)
- Monitoring: ~$0-20/mo (Prometheus + Grafana Cloud)
- **Total: ~$100-120/month**

---

## CI/CD Architecture

Comprehensive GitHub Actions pipeline covering all aspects of quality assurance:

**Core Pipelines:**
- `ci-cd.yml` -- Main orchestrator: lint, typecheck, build, unit tests
- `go-tests.yml` -- Go test suite with race detection and coverage
- `python-tests.yml` -- Python pytest with coverage reports
- `contract-tests.yml` -- API contract tests (Consumer-Driven Contract)

**Advanced Testing:**
- `chaos-tests.yml` -- Network partition, latency injection, failure scenarios
- `load-test.yml` -- k6 load tests (1000+ concurrent users)
- `performance-regression.yml` -- Memory, CPU, latency tracking vs baseline
- `security-scan.yml` -- SAST (Semgrep), dependency audit (pip-audit, npm audit), secret detection (gitleaks)

**UI/Integration:**
- `chromatic.yml` -- Visual regression tests via Storybook
- `schema-validation.yml` -- OpenAPI schema validation
- `component-tests.yml` -- React component integration tests (vitest)

**Deployment:**
- `canary-deploy.yml` -- Deploy to canary environment, traffic shifting
- `deployment-rollback.yml` -- Automated rollback on health check failure
- `e2e-tests.yml` -- End-to-end tests against production-like environment

**Triggers:** On PR, on push to main, scheduled (nightly), manual dispatch
**Parallelism:** Up to 8 concurrent jobs for speed
**Artifacts:** Test reports, coverage reports, performance baselines, SBOMs

---

## Microservices Layer (92+ Services)

TraceRTM employs a microservice-oriented architecture with 92+ specialized services, organized by domain:

**Core Traceability Services:**
- `item_service`, `link_service`, `project_service` -- CRUD operations
- `traceability_service`, `advanced_traceability_service` -- Trace queries, impact analysis
- `graph_service`, `graph_change_service` -- Graph construction, versioning
- `link_type_service`, `edge_type_service` -- Link/edge type management

**Testing & Verification:**
- `test_case_service`, `test_suite_service`, `test_run_service` -- Test management
- `test_coverage_service` -- Coverage analysis and tracking
- `execution_service`, `execution_config_service` -- Execution environment config

**Requirements & Specifications:**
- `requirement_service` -- Requirement CRUD and properties
- `specification_service` -- Structured spec management
- `adr_service` -- Architecture Decision Records
- `contract_service` -- Smart contract definitions
- `problem_service`, `process_service`, `scenario_service` -- Advanced modeling

**Analytics & Insights:**
- `advanced_analytics_service`, `advanced_traceability_enhancements_service` -- Deep analysis
- `agent_analytics_service`, `agent_performance_service` -- Agent metrics
- `benchmark_service`, `chaos_mode_service` -- Performance profiling

**Integration & External Systems:**
- `integration_service` -- GitHub, Jira, Linear, Webhook management
- `api_webhooks_service` -- Inbound/outbound webhook handling
- `auto_link_service` -- Intelligent link discovery
- `bulk_import_service`, `bulk_operation_service` -- Batch operations
- `commit_linking_service` -- GitHub commit traceability

**AI & Agents:**
- `ai_service`, `ai_tools` -- Claude integration, tool definitions
- `agent_coordination_service` -- Multi-agent swarms, BMM
- `agent_monitoring_service`, `agent_metrics_service` -- Agent observability
- `agent_checkpoint_service` -- Checkpoint/restore for agent state
- `codex_agent_service` -- Domain-specific agent persona

**Data Management:**
- `cache_service` -- Redis caching layer
- `blockchain_service` -- Hash-chained audit trail
- `checkpoint_service`, `workflow_run_service`, `workflow_schedule_service` -- Workflow persistence
- `notification_service` -- Email, webhook notifications

**Infrastructure & Tools:**
- `mcp_server_tools` (implicit) -- Model Context Protocol tools
- `import_export_service` -- Bidirectional sync
- `event_service`, `event_bus` -- Event publication
- `user_service`, `account_service` -- User/account management

**Location:** `/src/tracertm/services/` (Python) + distributed Go services

---

## Technology Decision Matrix

| Decision | Chosen | Alternatives Rejected | Rationale |
|----------|--------|----------------------|-----------|
| Python framework | FastAPI 0.115+ | Flask, Django | Async native, type hints, auto-docs (Pydantic), <5ms overhead |
| Go framework | Echo v4 | Gin, Fiber | Middleware system, context propagation, built-in WebSocket, active maintenance |
| Python version | 3.12+ | 3.10, 3.11 | Async generators, per-interpreter GIL (parallelism), pattern matching |
| Go version | 1.25.7+ | 1.23, 1.24 | Iterator improvements, memory efficiency, latest stdlib |
| Frontend | React 19 + Vite | Next.js, Vue, Svelte | SPA (no SSR needed), large ecosystem, React Flow support, OxLint |
| State mgmt | Zustand | Redux, MobX, Jotai | Simple API, no boilerplate, TypeScript support, tiny bundle (2KB) |
| Routing | TanStack Router | React Router, Remix | Type-safe params, lazy loading, search params API |
| Graph viz | React Flow | Sigma.js, Cytoscape, D3 | Component-based nodes, virtualization (1000s nodes), drag-drop |
| Database | PostgreSQL 16+ | MongoDB, Neo4j-only | ACID transactions, CTEs (graph queries), pgvector (semantic), full-text search |
| Graph DB | Neo4j Aura (optional) | ArangoDB, DGraph | Cypher language, mature ecosystem, managed cloud option |
| ORM (Python) | SQLAlchemy 2.0 | Tortoise ORM, Pydantic ORM | Async support, complex joins, SQLAlchemy 2.0 has better async ergonomics |
| SQL Driver (Go) | pgx v5 | database/sql, lib/pq | Prepared statements, connection pooling, pgvector support |
| Auth | WorkOS + JWT | Auth0, Firebase Auth, Keycloak | Enterprise SSO, SAML/OIDC, $125/mo, scoped API keys |
| Messaging | NATS JetStream | Kafka, RabbitMQ, Redis Streams | Lightweight (<50MB), JetStream (durable), KV store, request/reply, cost-effective |
| Workflow engine | Temporal SDK | Hatchet, Inngest, custom | Workflow as code, saga pattern, activity retries, durable timers |
| MCP Server | FastMCP 3.0+ | mcp-server-stdlib, custom | Production-ready, Anthropic-maintained, tool definitions, prompt templates |
| Desktop | Tauri | Electron, PyQt | 3-8MB bundle vs 150-200MB, native OS integration, Rust backend |
| Cache | Redis (Upstash) | Memcached, Valkey | Serverless (pay-per-use), sorted sets, streams, pub/sub, TTL |
| Linting (Python) | Ruff | Pylint, Flake8 | 100-200x faster, built in 2+ linters (pydocstyle, pyupgrade, isort), Rust-based |
| Linting (Go) | golangci-lint | gofmt, go vet | Configurable, 50+ linters, runs in parallel, fast |
| Linting (TS) | OxLint | ESLint, Biome | Rust-based (10x faster), type-aware, no config needed by default |
| Testing (Python) | pytest 8+ | unittest, nose2 | Fixtures, parametrize, plugins, clear assertion messages |
| Testing (Go) | testify/assert + testcontainers | testing/T only | Clear API, container isolation for integration tests |
| Testing (Frontend) | Vitest + React Testing Library | Jest, Cypress, Playwright | Vite-native (faster), DOM testing (not implementation details), clear assertions |
| Secrets mgmt | HashiCorp Vault | AWS Secrets Manager, 1Password | Self-hosted option, dynamic secrets, key rotation, audit logs |
| Monitoring | Prometheus + Grafana | Datadog, New Relic | Open-source, self-hosted, Grafana Cloud optional, cost-effective |
| Deployment | Vercel + Fly.io + Neon | Railway, Render, PlanetScale | Best-in-class for SPA, containers, serverless DB; Docker support everywhere |
| CI/CD | GitHub Actions | GitLab CI, CircleCI | Native GitHub integration, matrix builds, reasonable pricing, good ecosystem |
