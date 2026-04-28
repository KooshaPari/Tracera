# TraceRTM Codebase Entity Map

**Generated:** 2026-02-12
**Purpose:** Comprehensive mapping of all major code entities/artifacts for FR/ADR/US documentation

---

## Architecture Overview

TraceRTM is a multi-layer traceability management system with:

- **Python Backend** (FastAPI) - REST API, business logic, MCP server
- **Go Backend** (Echo) - High-performance services, graph operations, real-time features
- **React Frontend** (TypeScript) - Web, desktop (Electron), and mobile apps
- **MCP Server** - AI agent integration via Model Context Protocol

---

## 1. Core Domain Entities

### 1.1 Data Models (`src/tracertm/models/`)

**Primary Entities:**
- `item.py` - Core traceability item (requirements, features, tests)
- `link.py` - Relationships between items
- `specification.py` - Formal requirements specifications
- `project.py` - Project/workspace container
- `graph.py` - Graph representation of traceability network
- `feature.py` - Feature tracking
- `adr.py` - Architecture Decision Records
- `contract.py` - Contract specifications

**Testing & Execution:**
- `test_case.py` - Individual test cases
- `test_suite.py` - Test suite grouping
- `test_run.py` - Test execution records
- `test_coverage.py` - Coverage tracking
- `execution.py` - Execution configurations
- `execution_config.py` - Execution environment configs

**Integration & External:**
- `integration.py` - External tool integrations
- `github_app_installation.py` - GitHub App integration
- `github_project.py` - GitHub project sync
- `linear_app.py` - Linear integration
- `webhook_integration.py` - Webhook configurations
- `external_link.py` - External resource links

**AI & Automation:**
- `agent.py` - AI agent definitions
- `agent_session.py` - Agent execution sessions
- `agent_checkpoint.py` - Agent state checkpoints
- `agent_event.py` - Agent lifecycle events
- `agent_lock.py` - Agent coordination locks
- `codex_agent.py` - Code analysis agents

**Graph & Analysis:**
- `graph_node.py` - Graph node representation
- `graph_snapshot.py` - Point-in-time graph snapshots
- `graph_change.py` - Graph change tracking
- `edge_type.py` - Link type definitions
- `node_kind.py` - Item type definitions
- `node_kind_rule.py` - Type validation rules
- `graph_type.py` - Graph classification

**Quality & Process:**
- `requirement_quality.py` - Requirement quality metrics
- `problem.py` - Issue/problem tracking
- `scenario.py` - Test scenarios
- `process.py` - Workflow process definitions
- `workflow_run.py` - Workflow execution
- `workflow_schedule.py` - Scheduled workflows

**System & Infrastructure:**
- `user.py` - User accounts
- `account.py` - Organization accounts
- `account_user.py` - Account membership
- `event.py` - System event log
- `notification.py` - User notifications
- `view.py` - Saved views/filters
- `item_view.py` - Item display configurations
- `item_spec.py` - Item type specifications
- `blockchain.py` - Immutable audit trail
- `base.py` - SQLAlchemy base models
- `types.py` - Custom type definitions

---

## 2. Business Logic Services (`src/tracertm/services/`)

### 2.1 Core Traceability Services

**Graph & Analysis:**
- `graph_service.py` - Graph CRUD operations
- `graph_analysis_service.py` - Graph metrics and analysis
- `graph_validation_service.py` - Graph consistency validation
- `graph_snapshot_service.py` - Point-in-time snapshots
- `graph_report_service.py` - Graph reporting
- `cycle_detection_service.py` - Circular dependency detection
- `dependency_analysis_service.py` - Dependency impact analysis
- `critical_path_service.py` - Critical path identification
- `shortest_path_service.py` - Shortest path algorithms

**Link Management:**
- `link_service.py` - Link CRUD operations
- `auto_link_service.py` - Automatic link suggestions
- `commit_linking_service.py` - Git commit linking
- `traceability_service.py` - Core traceability logic
- `traceability_matrix_service.py` - Traceability matrix generation
- `advanced_traceability_service.py` - Advanced traceability features
- `advanced_traceability_enhancements_service.py` - Enhanced traceability

**Item Management:**
- `item_service.py` - Item CRUD operations
- `item_spec_service.py` - Item type specifications
- `specification_service.py` - Requirements specs management
- `feature_service.py` - Feature tracking
- `adr_service.py` - ADR management
- `contract_service.py` - Contract management
- `scenario_service.py` - Test scenario management

### 2.2 Search & Query Services

- `search_service.py` - Full-text search
- `query_service.py` - Query builder
- `query_optimization_service.py` - Query performance optimization
- `drill_down_service.py` - Interactive drill-down analysis
- `view_service.py` - Saved view management
- `view_registry_service.py` - View type registry

### 2.3 Import/Export & Integration Services

**Import:**
- `import_service.py` - Generic import framework
- `github_import_service.py` - GitHub issue import
- `jira_import_service.py` - Jira import
- `ingestion_service.py` - Data ingestion pipeline
- `stateless_ingestion_service.py` - Stateless ingestion
- `integration_sync_processor.py` - Integration sync

**Export:**
- `export_service.py` - Export framework
- `export_import_service.py` - Combined export/import
- `documentation_service.py` - Documentation generation

**External Integrations:**
- `external_integration_service.py` - Integration orchestration
- `github_project_service.py` - GitHub project sync
- `sync_service.py` - Sync coordination
- `webhook_service.py` - Webhook delivery
- `api_webhooks_service.py` - API webhook management

### 2.4 Analytics & Metrics Services

**Analytics:**
- `advanced_analytics_service.py` - Advanced analytics
- `spec_analytics_service.py` - Specification analytics
- `impact_analysis_service.py` - Change impact analysis
- `requirement_quality_service.py` - Requirement quality scoring

**Metrics & Performance:**
- `metrics_service.py` - System metrics
- `stats_service.py` - Statistics aggregation
- `performance_service.py` - Performance monitoring
- `performance_optimization_service.py` - Performance tuning
- `performance_tuning_service.py` - Advanced tuning
- `benchmark_service.py` - Benchmarking

**Progress Tracking:**
- `progress_service.py` - Progress tracking
- `progress_tracking_service.py` - Enhanced progress tracking
- `trace_service.py` - Trace analysis

### 2.5 AI & Agent Services

**Agent Coordination:**
- `agent_coordination_service.py` - Multi-agent orchestration
- `agent_monitoring_service.py` - Agent health monitoring
- `agent_performance_service.py` - Agent performance tracking
- `agent_metrics_service.py` - Agent metrics collection

**AI Tools:**
- `ai_service.py` - AI/ML service orchestration
- `ai_tools.py` - AI utility functions

### 2.6 Infrastructure Services

**Data Management:**
- `cache_service.py` - Caching layer
- `storage_service.py` - File storage (S3)
- `materialized_view_service.py` - Materialized view refresh
- `event_service.py` - Event bus
- `event_sourcing_service.py` - Event sourcing

**Operations:**
- `bulk_service.py` - Bulk operations
- `bulk_operation_service.py` - Enhanced bulk ops
- `concurrent_operations_service.py` - Concurrency control
- `checkpoint_service.py` - Checkpoint/restore
- `purge_service.py` - Data cleanup
- `repair_service.py` - Data repair utilities

**Monitoring & Debugging:**
- `chaos_mode_service.py` - Chaos engineering
- `verification_service.py` - Data verification
- `graph_validation_service.py` - Graph consistency checks
- `conflict_resolution_service.py` - Conflict resolution
- `file_watcher_service.py` - File system monitoring

**Workflow & Execution:**
- `temporal_service.py` - Temporal workflow integration
- `execution/` - Test execution services
- `recording/` - Session recording
- `agents/` - Agent runtime services

**Security & Auth:**
- `workos_auth_service.py` - WorkOS authentication
- `user_repository.py` - User management
- `notification_service.py` - Notification delivery
- `security_compliance_service.py` - Security compliance

**Backend Integration:**
- `grpc_client.py` - gRPC client for Go backend
- `token_bridge.py` - Token sharing between backends
- `plugin_service.py` - Plugin system
- `tui_service.py` - TUI backend services

**Project Management:**
- `project_backup_service.py` - Project backup/restore
- `history_service.py` - Change history
- `status_workflow_service.py` - Status workflow engine
- `visualization_service.py` - Data visualization

---

## 3. REST API Endpoints (`src/tracertm/api/`)

### 3.1 API Routers (`src/tracertm/api/routers/`)

**Core Resources:**
- `items.py` - Item CRUD endpoints (`/items`)
- `specifications.py` - Specification endpoints (`/specifications`)
- `features.py` - Feature endpoints (`/features`)
- `adrs.py` - ADR endpoints (`/adrs`)
- `contracts.py` - Contract endpoints (`/contracts`)
- `item_specs.py` - Item type spec endpoints (`/item-specs`)

**Integration:**
- `integrations.py` - Integration management (`/integrations`)
- `github.py` - GitHub integration (`/github`)
- `oauth.py` - OAuth flows (`/oauth`)
- `websocket.py` - WebSocket connections (`/ws`)
- `blockchain.py` - Blockchain audit trail (`/blockchain`)

**AI & Chat:**
- `agent.py` - Agent management (`/agents`)
- `chat.py` - AI chat interface (`/chat`)
- `mcp.py` - MCP server control (`/mcp`)

**System:**
- `auth.py` - Authentication (`/auth`)
- `health.py` - Health checks (`/health`)
- `health_canary.py` - Canary health (`/health/canary`)
- `execution.py` - Test execution (`/execution`)
- `notifications.py` - Notifications (`/notifications`)
- `quality.py` - Quality metrics (`/quality`)
- `errors.py` - Error handling

### 3.2 API Handlers (`src/tracertm/api/handlers/`)

- `auth.py` - Auth business logic
- `items.py` - Item handlers
- `links.py` - Link handlers
- `integrations.py` - Integration handlers
- `github.py` - GitHub handlers
- `webhooks.py` - Webhook handlers
- `websocket.py` - WebSocket handlers
- `chat.py` - Chat handlers
- `oauth.py` - OAuth handlers
- `device.py` - Device code flow
- `health.py` - Health check logic

### 3.3 Middleware (`src/tracertm/api/middleware/`)

- `auth.py` - Authentication middleware
- `authentication_middleware.py` - Enhanced auth
- `cors.py` - CORS configuration
- `logging.py` - Request logging
- `error_handling.py` - Error handling
- `cache_headers_middleware.py` - Cache headers

### 3.4 Configuration (`src/tracertm/api/config/`)

- `startup.py` - Application startup
- `rate_limiting.py` - Rate limiting config

### 3.5 Client SDKs (`src/tracertm/api/`)

- `client.py` - Python SDK
- `sync_client.py` - Synchronous client
- `http_client.py` - HTTP client utilities

---

## 4. MCP Server (`src/tracertm/mcp/`)

### 4.1 MCP Tools (`src/tracertm/mcp/tools/`)

**Core Operations:**
- `core_tools.py` - Core MCP tools
- `items.py` - Item management tools
- `items_optimized.py` - Optimized item tools
- `links.py` - Link management tools
- `graph.py` - Graph query tools
- `traceability.py` - Traceability tools
- `specifications.py` - Specification tools
- `projects.py` - Project management tools

**Advanced Features:**
- `optional_features.py` - Optional/experimental features
- `feature_demos.py` - Feature demonstrations
- `bmm_workflows.py` - BMAD workflow tools
- `design_ingest_migration.py` - Design ingestion
- `streaming.py` - Streaming responses

**Infrastructure:**
- `base.py` - Base tool classes
- `base_async.py` - Async tool base
- `param.py` - Parameter definitions
- `params/` - Parameterized tool modules
- `response_optimizer.py` - Response optimization
- `auth_config_db.py` - Auth/config/DB tools
- `_load.py` - Tool loading utilities

### 4.2 MCP Resources (`src/tracertm/mcp/resources/`)

MCP resources for agent context (schemas, templates, documentation)

### 4.3 MCP Infrastructure (`src/tracertm/mcp/`)

**Server Core:**
- `server.py` - MCP server definition
- `core.py` - Core MCP instance
- `registry.py` - Tool/resource registry
- `middleware.py` - MCP middleware

**Integration:**
- `api_client.py` - REST API client
- `http_transport.py` - HTTP transport
- `cli_integration.py` - CLI integration
- `workflow_executor.py` - Workflow execution

**Performance:**
- `cache.py` - MCP caching
- `query_optimizer.py` - Query optimization
- `token_manager.py` - Token management
- `database_adapter.py` - DB adapter
- `database_manager.py` - DB connection pooling

**Observability:**
- `metrics.py` - MCP metrics
- `metrics_endpoint.py` - Metrics HTTP endpoint
- `telemetry.py` - Telemetry collection
- `logging_config.py` - Logging setup
- `test_monitoring.py` - Test monitoring
- `db_benchmark.py` - DB benchmarking

**Utilities:**
- `auth.py` - Authentication
- `error_handlers.py` - Error handling
- `bmm_utils.py` - BMAD utilities
- `__main__.py` - CLI entry point

---

## 5. Go Backend (`backend/`)

### 5.1 HTTP Handlers (`backend/internal/handlers/`)

**Authentication:**
- `auth_handler.go` - Auth orchestration
- `auth_handler_endpoints.go` - Auth HTTP endpoints
- `auth_handler_session.go` - Session management
- `auth_handler_persistence.go` - Auth persistence
- `auth_handler_types.go` - Auth types

**Core Features:**
- `agent_handler.go` - Agent management
- `agent_coordination_handlers_test.go` - Agent coordination
- `ai_handler.go` - AI/ML endpoints
- `code_index_handler.go` - Code indexing
- `chaos_handler.go` - Chaos mode

**Data & Graph:**
- `graph_handler.go` - Graph operations
- `traceability_handler.go` - Traceability operations
- `storage_handler.go` - Storage operations
- `search_handler.go` - Search endpoints
- `equivalence_handler.go` - Equivalence relations

**Integration:**
- `github_handler.go` - GitHub integration
- `linear_handler.go` - Linear integration
- `figma_handler.go` - Figma integration
- `webhook_handler.go` - Webhook delivery
- `websocket_handler.go` - WebSocket hub

**Testing & Quality:**
- `test_handler.go` - Test execution
- `journey_handler.go` - User journey tracking
- `metrics_handler.go` - Metrics API
- `health_handler.go` - Health checks

**Utilities:**
- `binder.go` - Request binding
- `response.go` - Response helpers
- `middleware.go` - Handler middleware

### 5.2 Services (`backend/internal/services/`)

Go service layer for business logic (mirrors Python services where performance critical)

### 5.3 Database (`backend/internal/database/`)

- Database connection pooling
- Migration management
- Query builders

### 5.4 Graph Operations (`backend/internal/graph/`)

- Graph storage (Neo4j)
- Graph algorithms
- Event-driven graph updates

### 5.5 Infrastructure (`backend/internal/`)

**Core:**
- `config/` - Configuration management
- `auth/` - Authentication/authorization
- `middleware/` - HTTP middleware
- `server/` - HTTP server setup

**Data:**
- `repository/` - Data access layer
- `models/` - Domain models
- `db/` - Database utilities
- `cache/` - Redis caching
- `storage/` - S3 storage

**Integration:**
- `grpc/` - gRPC services
- `websocket/` - WebSocket hub
- `nats/` - Event bus
- `temporal/` - Workflow engine
- `clients/` - External clients

**Features:**
- `agents/` - Agent runtime
- `features/` - Feature flags
- `workflows/` - Workflow definitions
- `traceability/` - Traceability logic
- `integration/` - External integrations
- `search/` - Search indexing
- `codeindex/` - Code indexing
- `embeddings/` - Vector embeddings
- `journey/` - User journey tracking
- `equivalence/` - Equivalence relations

**Operations:**
- `metrics/` - Metrics collection
- `tracing/` - Distributed tracing
- `health/` - Health checks
- `profiling/` - Performance profiling
- `sentry/` - Error tracking
- `ratelimit/` - Rate limiting
- `resilience/` - Circuit breakers
- `tx/` - Transaction management

**Security:**
- `oauth/` - OAuth implementation
- `vault/` - Secrets management
- `sessions/` - Session management

**Testing:**
- `testutil/` - Test utilities

**Tools:**
- `pagination/` - Pagination utilities
- `validation/` - Input validation
- `uuidutil/` - UUID utilities
- `env/` - Environment utilities
- `preflight/` - Preflight checks

**UI:**
- `storybook/` - Storybook integration
- `docservice/` - Documentation service
- `docindex/` - Document indexing
- `figma/` - Figma integration
- `realtime/` - Real-time updates
- `adapters/` - UI adapters
- `cliproxy/` - CLI proxy
- `autoupdate/` - Auto-update service

**Events:**
- `events/` - Event handling
- `progress/` - Progress tracking

**Infrastructure:**
- `infrastructure/` - Infrastructure setup

---

## 6. Frontend Applications (`frontend/apps/`)

### 6.1 Web App (`frontend/apps/web/`)

**Structure:**
- `src/components/` - React components
- `src/features/` - Feature modules
- `src/pages/` - Page components
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utility libraries
- `src/api/` - API clients
- `src/graph/` - Graph visualization
- `src/__tests__/` - Test suites

**Key Feature Areas:**
- Requirement management UI
- Graph visualization
- Test management
- Integration dashboards
- AI chat interface
- Real-time collaboration
- Mobile-responsive views

### 6.2 Desktop App (`frontend/apps/desktop/`)

Electron wrapper for web app with:
- Native system integration
- Local file system access
- Offline capabilities
- Native notifications

### 6.3 Storybook (`frontend/apps/storybook/`)

Component documentation and development environment

### 6.4 Documentation (`frontend/apps/docs/`)

User documentation site

---

## 7. Data Schemas (`src/tracertm/schemas/`)

Pydantic schemas for API validation:

- `item.py` - Item DTOs
- `link.py` - Link DTOs
- `specification.py` - Specification DTOs
- `item_spec.py` - Item spec DTOs
- `integration.py` - Integration DTOs
- `auth.py` - Auth DTOs
- `agent.py` - Agent DTOs
- `execution.py` - Execution DTOs
- `test_case.py` - Test case DTOs
- `test_suite.py` - Test suite DTOs
- `test_run.py` - Test run DTOs
- `test_coverage.py` - Coverage DTOs
- `event.py` - Event DTOs
- `webhook.py` - Webhook DTOs
- `chat.py` - Chat DTOs
- `problem.py` - Problem DTOs
- `process.py` - Process DTOs
- `account.py` - Account DTOs
- `spec_analytics.py` - Analytics DTOs

---

## 8. Data Access Layer (`src/tracertm/repositories/`)

Repository pattern for data access:

- `item_repository.py` - Item CRUD
- `link_repository.py` - Link CRUD
- `specification_repository.py` - Specification CRUD
- `project_repository.py` - Project CRUD
- `integration_repository.py` - Integration CRUD
- `github_app_repository.py` - GitHub App CRUD
- `github_project_repository.py` - GitHub project CRUD
- `agent_repository.py` - Agent CRUD
- `execution_repository.py` - Execution CRUD
- `event_repository.py` - Event CRUD
- `blockchain_repository.py` - Blockchain CRUD
- `account_repository.py` - Account CRUD
- `item_spec_repository.py` - Item spec CRUD
- Plus 20+ additional repositories

---

## 9. Feature Organization by Functional Area

### 9.1 Discovery & Capture

**Features:**
- Import from external systems (GitHub, Jira, Linear)
- Specification parsing
- Auto-link suggestion
- Commit linking
- Webhook ingestion

**Components:**
- Import services (GitHub, Jira)
- Ingestion pipeline
- Auto-link service
- Commit linking service
- Webhook service

**APIs:**
- `POST /integrations/{type}/import`
- `POST /specifications/parse`
- `POST /links/auto-suggest`
- `POST /webhooks`

**MCP Tools:**
- `import_from_github`
- `parse_specification`
- `suggest_links`

### 9.2 Qualification & Analysis

**Features:**
- Requirement quality scoring
- Graph analysis (cycles, critical path, dependencies)
- Impact analysis
- Coverage analysis
- Traceability matrix generation

**Components:**
- Requirement quality service
- Graph analysis service
- Cycle detection service
- Critical path service
- Dependency analysis service
- Impact analysis service
- Coverage tracking

**APIs:**
- `GET /items/{id}/quality`
- `GET /graph/analyze`
- `GET /graph/cycles`
- `GET /graph/critical-path`
- `POST /analysis/impact`
- `GET /coverage/matrix`

**MCP Tools:**
- `analyze_requirement_quality`
- `detect_cycles`
- `find_critical_path`
- `analyze_impact`
- `generate_traceability_matrix`

### 9.3 Application & Tracking

**Features:**
- Item CRUD
- Link management
- Status workflow
- Progress tracking
- Test execution
- Feature tracking

**Components:**
- Item service
- Link service
- Status workflow service
- Progress service
- Execution services
- Feature service

**APIs:**
- `GET/POST/PUT/DELETE /items`
- `GET/POST/DELETE /links`
- `PUT /items/{id}/status`
- `GET /progress`
- `POST /execution/run`

**MCP Tools:**
- `create_item`
- `update_item`
- `create_link`
- `execute_tests`
- `track_progress`

### 9.4 Verification & Validation

**Features:**
- Test management
- Test execution
- Coverage tracking
- Verification reports
- Graph validation

**Components:**
- Test case/suite/run models
- Execution services
- Coverage service
- Verification service
- Graph validation service

**APIs:**
- `POST /tests/execute`
- `GET /coverage`
- `POST /verification/run`
- `GET /graph/validate`

**MCP Tools:**
- `run_test_suite`
- `check_coverage`
- `validate_graph`

### 9.5 Reporting & Analytics

**Features:**
- Traceability matrix
- Analytics dashboards
- Custom reports
- Metrics tracking
- Progress reports

**Components:**
- Traceability matrix service
- Advanced analytics service
- Spec analytics service
- Metrics service
- Stats service
- Report generation

**APIs:**
- `GET /reports/traceability-matrix`
- `GET /analytics/dashboard`
- `POST /reports/custom`
- `GET /metrics`

**MCP Tools:**
- `generate_matrix`
- `get_analytics`
- `export_report`

### 9.6 Collaboration & Integration

**Features:**
- Real-time collaboration (WebSocket)
- External tool sync (GitHub, Jira, Linear)
- Webhooks
- AI chat assistant
- Notifications

**Components:**
- WebSocket hub
- Sync service
- Integration services
- Webhook service
- Chat service
- Notification service

**APIs:**
- `WS /ws`
- `POST /integrations/{type}/sync`
- `POST /webhooks`
- `POST /chat/message`
- `GET /notifications`

**MCP Tools:**
- `sync_with_github`
- `send_notification`

### 9.7 AI & Automation

**Features:**
- AI-powered requirement analysis
- Auto-link suggestions
- Agent coordination
- Workflow automation
- Code analysis

**Components:**
- AI service
- Agent coordination service
- Agent monitoring service
- Auto-link service
- Workflow executor
- Code index service

**APIs:**
- `POST /ai/analyze`
- `POST /agents/coordinate`
- `POST /workflow/execute`

**MCP Tools:**
- `analyze_with_ai`
- `coordinate_agents`
- `execute_workflow`

---

## 10. Integration Points

### 10.1 External Integrations

**GitHub:**
- Models: `github_app_installation`, `github_project`
- Services: `github_import_service`, `github_project_service`
- Handlers: `github_handler.py` (Python), `github_handler.go` (Go)
- API: `/github/*`

**Jira:**
- Services: `jira_import_service`
- Integration type in `integration` model

**Linear:**
- Models: `linear_app`
- Handlers: `linear_handler.go`

**Figma:**
- Handlers: `figma_handler.go`
- Services: `figma/` (Go)

**WorkOS (Auth):**
- Services: `workos_auth_service`
- Handlers: `auth_handler.go`

### 10.2 Internal Integrations

**Python ↔ Go:**
- gRPC: `grpc_client.py`, `internal/grpc/` (Go)
- Token bridge: `token_bridge.py`
- Shared Redis cache

**Database:**
- Python: SQLAlchemy + Alembic
- Go: GORM + Atlas
- Shared Postgres schema

**Event Bus:**
- NATS for async events
- Python: `event_service`, `event_sourcing_service`
- Go: `internal/nats/`

**Workflow Engine:**
- Temporal for long-running workflows
- Python: `temporal_service`
- Go: `internal/temporal/`

**Graph Database:**
- Neo4j for graph storage
- Go: `internal/graph/`
- Python: Graph service wrappers

---

## 11. Testing Infrastructure

### 11.1 Python Tests

- `src/tracertm/tests/` - Unit/integration tests
- `tests/` - Additional test suites
- pytest + pytest-asyncio

### 11.2 Go Tests

- `backend/internal/*/\*_test.go` - Unit tests
- `backend/e2e/` - E2E tests
- `backend/tests/` - Integration tests
- Go standard testing + testify

### 11.3 Frontend Tests

- `frontend/apps/web/src/__tests__/` - Component/integration tests
- Vitest + React Testing Library
- Storybook for component testing

---

## 12. Documentation & Configuration

### 12.1 API Documentation

- OpenAPI specs in `openapi/`
- Auto-generated from FastAPI
- Swagger UI at `/docs`

### 12.2 Database Schema

- `backend/schema.sql` - Main schema
- `backend/schema.hcl` - Atlas HCL
- `alembic/` - Python migrations
- `backend/internal/database/migrations/` - Go migrations

### 12.3 Configuration Files

- `pyproject.toml` - Python project config
- `backend/go.mod` - Go dependencies
- `frontend/package.json` - Node dependencies
- `docker-compose.yml` - Local dev stack
- `Makefile`, `Taskfile.yml` - Task automation

---

## 13. Key Workflows

### 13.1 Requirement Import Workflow

1. **Trigger:** User initiates GitHub import
2. **API:** `POST /integrations/github/import`
3. **Handler:** `github.py:import_issues()`
4. **Service:** `github_import_service.py:import_from_github()`
5. **Repository:** `item_repository.py:create_batch()`
6. **Event:** Publish `items.imported` to NATS
7. **Graph:** `graph_service.py:add_nodes()`
8. **Search:** `search_indexer` indexes new items

### 13.2 Traceability Analysis Workflow

1. **Trigger:** User requests impact analysis
2. **API:** `POST /analysis/impact`
3. **Service:** `impact_analysis_service.py:analyze_impact()`
4. **Graph Query:** Query Neo4j via Go backend gRPC
5. **Analysis:** Traverse graph, calculate metrics
6. **Cache:** Store results in Redis
7. **Response:** Return impact report

### 13.3 AI-Assisted Linking Workflow

1. **Trigger:** Agent requests auto-link
2. **MCP Tool:** `suggest_links(item_id)`
3. **Service:** `auto_link_service.py:suggest_links()`
4. **AI:** Call embeddings service for semantic similarity
5. **Graph:** Query candidate links from graph
6. **Ranking:** Score and rank suggestions
7. **Response:** Return top N suggestions
8. **Apply:** Agent creates links via `create_link` tool

### 13.4 Test Execution Workflow

1. **Trigger:** User runs test suite
2. **API:** `POST /execution/run`
3. **Handler:** `execution.py:run_tests()`
4. **Workflow:** Temporal workflow for long-running execution
5. **Execution:** Go backend test runner
6. **Results:** Store in `test_run` model
7. **Coverage:** Update coverage metrics
8. **Traceability:** Update test→requirement links
9. **Notification:** Notify user of completion

---

## 14. Summary Statistics

**Total Services (Python):** ~90 services
**Total Models:** 50+ models
**Total API Endpoints:** ~200+ endpoints
**Total MCP Tools:** ~50+ tools
**Total Go Handlers:** ~30+ handlers
**Total React Components:** 300+ components

**Primary Functional Areas:**
1. Discovery & Capture (6 major features)
2. Qualification & Analysis (8 major features)
3. Application & Tracking (7 major features)
4. Verification & Validation (5 major features)
5. Reporting & Analytics (6 major features)
6. Collaboration & Integration (7 major features)
7. AI & Automation (6 major features)

**Technology Stack:**
- **Backend:** Python (FastAPI), Go (Echo)
- **Frontend:** React, TypeScript, Vite
- **Database:** PostgreSQL, Neo4j
- **Cache:** Redis
- **Events:** NATS
- **Workflows:** Temporal
- **Search:** Custom indexing
- **Storage:** S3-compatible
- **Auth:** WorkOS
- **AI:** MCP protocol, embeddings

---

## Usage Notes

This map provides the foundation for:

1. **Functional Requirements (FR):** Map features to components
2. **Architecture Decision Records (ADR):** Document design choices
3. **User Stories (US):** Link user needs to implementation
4. **API Documentation:** Complete endpoint reference
5. **Developer Onboarding:** Understand system structure
6. **Impact Analysis:** Trace feature dependencies
7. **Test Planning:** Identify coverage gaps

Each entity listed has corresponding source files in the codebase. Use this map as an index to dive deeper into specific areas.
