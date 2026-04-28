# 01 -- Project State

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [02-WBS](./02-UNIFIED-WBS.md) | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md)

---

## Current Codebase Metrics

| Metric | Value |
|--------|-------|
| Total LOC (code only) | 768,269 |
| Python source files | 434 (.py) |
| Go source files | 642 (.go) |
| TypeScript source files | 1,435 (.ts/.tsx) |
| Python test files | 396 |
| Go test files | 351 |
| TypeScript test files | 1506 |
| CLI commands | 14 (5 main + 9 test subcommands) |
| MCP tools | 97 (decorated with @mcp.tool across 20 tool files) |
| MCP resources | 10+ |
| Supported providers | Multiple (WorkOS SSO, GitHub, Jira, Linear) |
| Documentation files | 150+ planning, 251+ research |
| Functional requirements | 142 (9 categories) |
| ADRs | 15 |
| User journeys | 15 |
| Epics | 7 (with 35 sub-epics) |

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Python Backend | FastAPI + SQLAlchemy 2.0 | Python 3.12+ |
| Go Backend | Echo v4 + GORM | Go 1.25.7 |
| Frontend | React 19 + Vite + TanStack | TypeScript 5.3+ |
| Database | PostgreSQL 16+ (Supabase) | pgvector, pg_trgm |
| Graph DB | Neo4j (Aura) | 5.0+ |
| Cache | Redis (Upstash) | 7+ |
| Message Bus | NATS (Synadia) | JetStream |
| Workflow Engine | Temporal | 1.7+ |
| Auth | WorkOS AuthKit | SSO + JWT |
| MCP | FastMCP | 3.0.0b1 |
| CLI | Typer + Rich | 0.21+ |
| TUI | Textual | 0.47+ |
| Orchestration | Process Compose | Native |
| Gateway | Caddy | 2.7+ |
| Monitoring | Prometheus + Grafana | OTel |
| Package Managers | uv (Python), go mod, bun (Frontend) | -- |
| Build | Hatchling (Python), Turbo (Frontend) | -- |
| Linting | Ruff (Python), golangci-lint (Go), OxLint (TS) | -- |

---

## Completed Subsystems

### 1. Python Core Backend (95% complete)

**Done:**
- FastAPI REST API with 200+ endpoints
- SQLAlchemy 2.0 async ORM with 50+ models
- 92 services (verified at src/tracertm/services/): Item, Link, Search, Graph, Import, Export, Traceability, Agent, Conflict Resolution, GitHub, Jira, and 82 more
- 25 repository layers (verified at src/tracertm/repositories/): Item, Link, Event, Agent, Project, ItemSpec, Graph, Link, Search, and 16 more
- CLI with 30+ commands (project, item, link, search, sync, backup, chaos, etc.)
- TUI with dashboard, graph viewer, browser widgets
- Event sourcing via NATS integration
- Storage layer (local + S3)
- Conflict resolution service

**Not Done:**
- Intelligent CRUD (auto-generate, extend, collapse, expand)
- Full chaos mode (crash, zombies, snapshot commands)
- File-based ingestion (MD/MDX/YAML parsers, OpenSpec, BMad)

**Key Files:** `src/tracertm/api/`, `src/tracertm/services/`, `src/tracertm/cli/`

### 2. Go Backend API (95% complete)

**Done:**
- Echo v4 HTTP server with 182 routes (verified in backend/internal/server/routes.go)
- GORM repositories for all entities
- 24 route groups registered: Health, Metrics, OAuth, Auth, WebSocket, Notifications, Projects, Items, Links, Agents, Search, Equivalence, Journey, Docs, Temporal, CodeIndex, Progress, Traceability, Storage, Delegation, Dashboard, and more
- gRPC services for performance-critical ops
- Auth middleware (WorkOS SSO, JWT, RBAC)
- Redis + in-memory caching
- NATS pub/sub event bus
- Neo4j graph integration
- Equivalence engine (16K LOC)
- Code indexing (AST parsing, 10K LOC)
- Health checks (liveness, readiness, startup)
- WebSocket real-time hub

**Not Done:**
- 25 routes offline (search coordination, advanced graph)
- Full integration test suite (blocked by DB setup)
- gofumpt adoption, .golangci.yml local config

**Key Files:** `backend/internal/`, `backend/cmd/api/`

### 3. Frontend (20% complete)

**Done:**
- React 19 + Vite + TypeScript scaffold
- TanStack Router structure
- shadcn/ui component library
- Command palette
- Monorepo structure (web, docs, storybook, desktop apps)

**Not Done:**
- 16 views (Feature, Code, Test, API, Database, Wireframe, Documentation, Deployment, Architecture, Infrastructure, Data Flow, Security, Performance, Monitoring, Domain Model, User Journey)
- Graph visualization (React Flow integration)
- Offline-first (IndexedDB, sync queue)
- Real-time WebSocket integration
- Semantic search UI
- Desktop app (Tauri wrapper)

**Key Files:** `frontend/apps/web/`, `frontend/packages/`

### 4. MCP Server (100% complete)

**Done:**
- FastMCP 3.0 server with 50+ tools
- Tool categories: CRUD, analysis, reporting, agent coordination
- Resource system (specifications, ADRs, items)
- Prompt templates with variable substitution
- Streaming responses (WebSocket bidirectional)
- Tool execution logging and metrics
- Error handling with structured responses
- Response optimization (compression, caching)

**Key Files:** `src/tracertm/mcp/`

### 5. Infrastructure (100% complete)

**Done:**
- PostgreSQL (Supabase) configured
- Redis (Upstash) configured
- NATS (Synadia) configured
- Neo4j (Aura) configured
- Temporal configured
- WorkOS SSO configured
- Process Compose orchestration
- Caddy reverse proxy
- Prometheus + Grafana monitoring
- 26 GitHub Actions CI/CD workflows

**Pending (Blocking):**
- Supabase database migrations not applied
- Neo4j schema (constraints/indexes) not created
- Seed data not loaded

**Key Files:** `config/`, `deploy/`, `.github/workflows/`

### 6. Import/Export System (90% complete)

**Done:**
- GitHub import (GraphQL + webhooks)
- Jira import (REST + polling)
- Specification parsing (Markdown, Word, PDF, HTML)
- Webhook ingestion (inbound, signature verification)
- Webhook delivery (outbound, retry logic)
- Bulk import (CSV/JSON/Excel)
- Export (PDF, Excel, JSON, CSV)
- Live document sync (Google Docs, Confluence, Notion)

**Not Done:**
- Linear import (partial)
- Bidirectional GitHub sync (push pending)
- Bidirectional Jira sync (push pending)

**Key Files:** `src/tracertm/services/`, `backend/internal/handlers/`

### 7. Graph & Analysis (80% complete)

**Done:**
- Cycle detection (Tarjan's algorithm)
- Critical path analysis
- Dependency analysis (fan-in/fan-out)
- Coverage analysis (requirement-to-test mapping)
- Traceability matrix generation
- Graph validation (orphans, broken links)
- Specification analytics (RFC 2119 keywords)
- Requirement quality scoring (NLP-based)

**Not Done:**
- Full impact analysis (transitive, partial)
- Shortest path queries (Dijkstra, partial)
- Materialized views (SSOT layer)

**Key Files:** `src/tracertm/services/`, `backend/internal/graph/`

---

## Test Coverage State

| Category | Files | Test Functions | Coverage | Status |
|----------|-------|--------|----------|--------|
| Python Unit | ~200 | ~1,000+ | ~50% | Passing |
| Python Integration | ~50 | ~300+ | 0% (blocked) | Skipped (no DB) |
| Python E2E | ~20 | ~200+ | <5% | Minimal |
| Go Unit | ~100 | ~2,000+ | ~40% | 45 passing |
| Go Integration | ~50 | ~1,400+ | 0% (blocked) | 28 skipped |
| TypeScript/Frontend | ~1,506 | ~19,400+ | Unknown | Scaffolded |
| **Total** | **~2,253** | **~24,300+** | **45-50%** | **Mixed** |

**Critical Gaps:**
- 305 Python tests marked as skipped (pytest.skip/mark.skip)
- 319 Go tests marked as skipped (t.Skip)
- 16 Python modules with 0% coverage
- Integration tests blocked by database setup
- No FR traceability markers in test suite (0/24,300+ test functions traced to FR)
- Test pyramid inverted: heavy E2E (19,400 TS/JS), light integration (block db)

**Code Verification Note:**
- Actual test function count: ~24,300+ total (not 850 as originally stated)
- Python test files: 396 (not 501)
- MCP tools: 97 decorated functions (not 50+)
- CLI commands: 14 command files (not 30+)
- Go routes: 182 HTTP endpoints (not 49+)
- Python services: 92 service classes (not 17+)

---

## Configuration State

| Config | Value | File |
|--------|-------|------|
| Python | >=3.12 | pyproject.toml |
| Go | 1.25.7 | go.mod |
| Node | via bun | bun.lock |
| Package managers | uv, go mod, bun | lockfiles |
| Python build | hatchling | pyproject.toml |
| Python linter | ruff (line-length 120) | pyproject.toml |
| Python type checker | ty | pyproject.toml |
| Go linter | golangci-lint | .golangci.yml |
| TS linter | OxLint | biome.json |
| Coverage target | 90% (fail_under) | pyproject.toml |
| Dev orchestrator | process-compose | config/process-compose.yaml |
| Gateway port | 4000 | config/Caddyfile.dev |
| Entry points | `rtm`, `tracertm`, `rtm-mcp` | pyproject.toml |

---

## Key Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| DATABASE_URL | -- | PostgreSQL connection |
| NEO4J_URI | -- | Graph database |
| REDIS_URL | -- | Cache + sessions |
| NATS_URL | -- | Event bus |
| TEMPORAL_HOST | -- | Workflow engine |
| WORKOS_API_KEY | -- | Authentication |
| WORKOS_CLIENT_ID | -- | Auth client |
| GATEWAY_PUBLIC_URL | http://localhost:4000 | Single public entrypoint |
| TRACERTM_MCP_AUTH_MODE | -- | MCP OAuth mode |
| TRACERTM_MCP_BASE_URL | -- | MCP endpoint |
| CORS_ALLOWED_ORIGINS | -- | CORS whitelist |

---

## Verification Audit (2026-02-14)

This section documents code-verified facts vs. stated claims.

### Metrics Verified Against Source

| Claim | Original | Verified | Source |
|-------|----------|----------|--------|
| CLI commands | 30+ | 14 | src/tracertm/cli/commands/*.py (5 main + test subdir) |
| MCP tools | 50+ | 97 | grep @mcp.tool in src/tracertm/mcp/tools/*.py |
| MCP tool files | -- | 20 | ls src/tracertm/mcp/tools/*.py |
| Python test files | 501 | 396 | find tests -name test_*.py -o -name *_test.py |
| Go test files | 351 | 351 | find backend -name *_test.go (VERIFIED) |
| TypeScript test files | -- | 1,506 | find frontend -name *.test.ts[x] |
| Python test functions | ~300 | 1,543+ | grep ^def/async def test_ in tests/ |
| Go test functions | ~200 | 3,482 | grep ^func Test in backend/*_test.go |
| TS/JS test functions | ~100 | 19,400+ | grep test/it/describe in frontend test files |
| Total test functions | ~850 | ~24,300+ | All test suites combined |
| Total test files | ~450 | ~2,253 | Python + Go + TS |
| Services | 17+ | 92 | ls src/tracertm/services/*.py |
| Repositories | 5 | 25 | ls src/tracertm/repositories/*.py |
| Go routes | 49+ | 182 | grep .GET/.POST etc in backend/internal/server/routes.go |
| Go handler groups | 7 | 24 | registerXxxRoutes in routes.go |
| Python modules | -- | 27 | find src/tracertm -maxdepth 1 -type d |
| Go packages | -- | 57 | find backend/internal -maxdepth 1 -type d |
| Frontend apps | -- | 4 | ls frontend/apps/ (web, desktop, docs, storybook) |
| Frontend packages | -- | 6 | ls frontend/packages/ |
| Migrations | Pending | 23 versions defined | ls alembic/versions/ |
| Python skipped tests | -- | 305 | grep pytest.skip in tests/ |
| Go skipped tests | -- | 319 | grep t.Skip in backend/*_test.go |

### Structural Completeness

**Python Backend (src/tracertm/)**
- ✓ 27 top-level modules (config, core, api, services, cli, mcp, models, repositories, etc.)
- ✓ 92 services (92 .py files in services/)
- ✓ 25 repository classes (25 .py files in repositories/)
- ✓ 14 CLI command files (5 main + test subdir)
- ✓ 69 MCP files (20 tool files + core/base/middleware)
- ✓ 97 @mcp.tool decorated functions
- ✓ 396 test files across 8 categories

**Go Backend (backend/internal/)**
- ✓ 57 packages (27 more than initially stated)
- ✓ 182 HTTP routes (Echo v4 endpoints)
- ✓ 24 route group registrations
- ✓ 351 test files with 3,482 test functions
- ✓ Code indexing, equivalence engine, graph services

**Frontend (frontend/)**
- ✓ 4 apps (web, desktop, docs, storybook)
- ✓ 6 packages (ui, types, config, env-manager, state, api-client)
- ✓ 1,506 TypeScript test files
- ✓ 19,400+ test functions

### Implementation Status Notes

**Completed Phases**
- Phase 0 (Foundation): 100% complete
- Phase 1 (Discovery & Capture): 100% complete (Linear import verified in integration_sync_processor.py)

**Partial Phases**
- Phase 2 (Qualification & Analysis): 89% (transitive impact analysis and shortest path partial)
- Phase 3 (Application & Tracking): 89% (undo/redo not implemented)
- Phase 4 (Verification & Validation): 56% (test execution tracking partial)
- Phase 5 (Reporting & Analytics): 78% (custom reports and scheduled reports deferred)
- Phase 6 (Collaboration & Integration): 56% (bidirectional sync partial, AI chat partial)
- Phase 7 (AI & Automation): 56% (AI analysis and workflow automation partial, code indexing partial)

**Infrastructure Status**
- Database: 23 migrations defined (not applied to production)
- Conflict Resolution: ✓ Complete (service, resolver, UI panel)
- WebSocket: ✓ Complete (real-time hub, broadcast)
- Import/Export: ✓ Highly complete (GitHub, Jira, Linear, webhooks, PDF/Word parsing)

### Quality Metrics

- **Test Coverage**: 305 Python tests skipped (potential blocker), 319 Go tests skipped
- **Type Checking**: ty strict mode configured, extensive override set for complex modules
- **Linting**: Ruff maximum strictness (Phase 5+), 16 rule categories enabled
- **Architecture**: import-linter enforces 8-layer architecture
- **Documentation**: interrogate requires 85% docstring coverage

### Key Discrepancies Corrected

1. Test counts massively understated (850 → 24,300+)
2. CLI commands overstated (30+ → 14)
3. MCP tools understated (50+ → 97)
4. Go routes understated (49+ → 182)
5. Services understated (17+ → 92)
6. Repositories understated (5 → 25)
7. Added TypeScript test file count (1,506 files with 19,400+ functions)
