# 08 -- Optimization Catalog

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [09-RISK-REGISTRY](./09-RISK-REGISTRY.md) | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md)

---

## Quick Wins (< 3 hours each)

| ID | Category | Item | Effort | Impact | WP | Status |
|----|----------|------|--------|--------|----|----|
| QW-001 | DevX | Add `.vscode/settings.json` + `extensions.json` | 30min | 2-4h saved per dev | WP-X10 | ✅ Done |
| QW-002 | DevX | Add `.vscode/launch.json` debugger configs | 20min | 80% less debugging friction | WP-X10 | ✅ Done |
| QW-003 | DevX | Add `.editorconfig` | 5min | Consistent formatting | WP-X10 | ✅ Done |
| QW-004 | DevX | Add PR template | 5min | Standardized PRs | WP-X10 | ✅ Done |
| QW-005 | Quality | Fix 67 failing Python tests | 3h | 100% pass rate | WP-X9 | In Progress |
| QW-006 | Ops | Apply Supabase DB migrations | 2h | Unblock integration tests | WP-X8 | ✅ Done |
| QW-007 | Ops | Initialize Neo4j schema | 30min | Unblock graph tests | WP-X8 | ✅ Done |
| QW-008 | Quality | Add FR traceability markers to tests | 2h | Spec traceability | WP-X9 | In Progress |

---

## Performance Optimizations (PERF)

| ID | Item | Current | Target | WP | Priority | Status |
|----|------|---------|--------|----|----------|--------|
| PERF-001 | Graph query caching (Redis) | Implemented | <50ms cached | P2.6 | P1 | ✅ Implemented |
| PERF-002 | Materialized view refresh | No views | <5s incremental | WP-X6 | P1 | Not Started |
| PERF-003 | Bulk import batch sizing | Basic batching | 1000/batch with streaming | P3.3 | P2 | Partial |
| PERF-004 | PostgreSQL query plan analysis | Ad-hoc | EXPLAIN ANALYZE on all slow queries | P0.2 | P1 | Not Started |
| PERF-005 | Frontend bundle size reduction | ~300KB | <200KB with code splitting | WP-X1 | P2 | Not Started |
| PERF-006 | WebSocket message batching | Implemented | 50ms batch window | P6.1 | P2 | ✅ Implemented |
| PERF-007 | Embedding computation batch | Sequential | Batch 50 items at once | P1.5 | P1 | Not Started |
| PERF-008 | Graph rendering virtualization | All nodes | React Flow virtualization (10K+) | WP-X1 | P1 | Not Started |
| PERF-009 | gRPC connection pooling | Basic gRPC | Pool of 10 connections | P0.5 | P2 | Partial |
| PERF-010 | NATS JetStream consumer prefetch | Implemented | Prefetch 100 messages | P0.5 | P2 | ✅ Implemented |
| PERF-011 | Cursor pagination (backend) | Offset-based | Cursor-based (2x faster) | WP-X7 | P1 | ✅ Implemented |
| PERF-012 | pgvector HNSW index | IVFFlat | HNSW for <100ms similarity search | P1.5 | P1 | Not Started |

---

## Robustness Enhancements (ROB)

| ID | Item | Current | Target | WP | Priority | Status |
|----|------|---------|--------|----|----------|--------|
| ROB-001 | Circuit breaker per external service | ✅ Implemented | 3-state breaker (closed/open/half-open) | P6.3 | P1 | ✅ Implemented |
| ROB-002 | Retry with exponential backoff | ✅ Implemented | Exponential backoff + jitter | P6.3 | P1 | ✅ Implemented |
| ROB-003 | Rate limiting (API) | ✅ Implemented | Sliding window + adaptive throttle | FR-INFRA-008 | P1 | ✅ Implemented |
| ROB-004 | Graceful shutdown handlers | Partial | Drain connections, flush queues | P0.5 | P2 | Partial |
| ROB-005 | Health check dependency cascade | ✅ Implemented | Check all downstream services | P0.7 | P2 | ✅ Implemented |
| ROB-006 | Dead-letter queue for NATS | ✅ Configured | Monitor + alert on DLQ depth | P0.5 | P1 | ✅ Configured |
| ROB-007 | Database connection pool tuning | Default | Pool size = 20, overflow = 10 | P0.2 | P2 | Not Started |
| ROB-008 | Webhook delivery retry budget | Infinite | Max 5 retries, exponential backoff | P6.5 | P1 | Partial |
| ROB-009 | Input validation on all endpoints | ✅ Implemented | Comprehensive validation middleware | P0.5 | P1 | ✅ Implemented |
| ROB-010 | Conflict detection in agent sync | ✅ Implemented | ConflictDetector + conflict queue | P6.3 | P1 | ✅ Implemented |
| ROB-011 | Idempotency keys for mutations | ✅ Implemented | UUID-based idempotency helpers | P3.1 | P2 | ✅ Implemented |
| ROB-012 | Timeout budgets for algorithms | Partial | 30s timeout, abort + partial result | P2.6 | P1 | Partial |

---

## UX Enhancements (UX)

| ID | Item | Current | Target | WP | Priority |
|----|------|---------|--------|----|----------|
| UX-001 | CLI progress bars for long operations | Text output | Rich progress bars with ETA | P3.3 | P2 |
| UX-002 | TUI keyboard shortcuts help panel | None | `?` shows keybindings | TUI | P2 |
| UX-003 | Auto-complete for CLI commands | Basic Typer | Custom completions for item IDs, projects | CLI | P3 |
| UX-004 | Error messages with actionable suggestions | Stack traces | "Did you mean?" + fix suggestions | P0.5 | P1 |
| UX-005 | Graph zoom/pan controls in TUI | None | Arrow keys + scroll for graph view | TUI | P2 |
| UX-006 | Dark/light theme toggle (Web) | Light only | System-preference detection | WP-X1 | P2 |
| UX-007 | Export format preview | Direct export | Preview before export | P5.5 | P3 |
| UX-008 | Batch operation confirmation | No confirm | "About to modify 47 items. Continue?" | P3.3 | P2 |
| UX-009 | Real-time search-as-you-type | Submit-based | Debounced live search (300ms) | P3.7 | P2 |
| UX-010 | Graph node tooltips with metadata | None | Hover shows type, status, links | WP-X1 | P2 |
| UX-011 | Onboarding wizard for new projects | Manual | Step-by-step project setup | P8.1 | P3 |
| UX-012 | Keyboard shortcut palette (Web) | None | Cmd+K command palette | WP-X1 | P2 |

---

## Developer Experience (DX)

| ID | Item | Current | Target | WP | Priority |
|----|------|---------|--------|----|----------|
| DX-001 | Go tooling overhaul (gofumpt, golangci) | gofmt only | gofumpt + strict golangci config | WP-X10 | P1 |
| DX-002 | Shared conftest.py for Python tests | Duplicated | Single conftest with fixtures | WP-X9 | P1 |
| DX-003 | Test subdirectory organization | Flat | unit/, integration/, e2e/ subdirs | WP-X9 | P2 |
| DX-004 | Architecture boundary enforcement | Tach config | Import-linter + tach strict mode | WP-X10 | P2 |
| DX-005 | Makefile consolidation | 604 lines | Reduce to essential targets | WP-X10 | P3 |
| DX-006 | Hot reload for Go backend | Manual restart | Air with optimized watch patterns | P0.7 | P2 |
| DX-007 | Pre-commit hook standardization | Partial | pre-commit-config.yaml enforced | WP-X10 | P2 |
| DX-008 | Test data factories | Minimal | Testing factories for all models | WP-X9 | P1 |
| DX-009 | API client generation from OpenAPI | Manual | Auto-generated TypeScript client | WP-X1 | P2 |
| DX-010 | Storybook component coverage | Minimal | All UI components in Storybook | WP-X1 | P3 |

---

## Operations Enhancements (OPS)

| ID | Item | Current | Target | WP | Priority |
|----|------|---------|--------|----|----------|
| OPS-001 | Database backup automation | Manual | Hourly automated backups (RPO <1h) | P0.2 | P1 |
| OPS-002 | Log aggregation pipeline | Scattered | Centralized Loki + Promtail | P0.7 | P2 |
| OPS-003 | Alert routing (PagerDuty/Slack) | None | Critical alerts to Slack | P0.7 | P2 |
| OPS-004 | Canary deployment automation | Manual | 5% canary with auto-rollback | P0.7 | P2 |
| OPS-005 | Database migration rollback testing | None | Test rollback in CI before deploy | P0.2 | P1 |
| OPS-006 | Cost monitoring dashboard | None | Per-service cost tracking | P0.7 | P3 |
| OPS-007 | Runbook documentation | None | Runbooks for top 10 incidents | P8.7 | P2 |
| OPS-008 | Load test baseline in CI | Manual | k6 smoke test in every PR | P0.7 | P2 |
| OPS-009 | SLO/SLI definition | None | Define SLOs for critical paths | P0.7 | P1 |
| OPS-010 | Distributed tracing (OTel) | Partial | End-to-end trace context | P0.7 | P1 |

---

## Design Enhancements (DE)

| ID | Item | Current | Target | WP | Priority |
|----|------|---------|--------|----|----------|
| DE-001 | Consistent API response envelope | Mixed | `{data, meta, errors}` envelope | P0.5 | P1 |
| DE-002 | API versioning strategy | None | URL prefix `/api/v2/` | P0.5 | P2 |
| DE-003 | Event schema versioning | None | Schema registry with backward compat | P0.5 | P2 |
| DE-004 | Database audit trigger | Manual events | PostgreSQL audit triggers | P0.2 | P2 |
| DE-005 | Feature flag cleanup | None | Quarterly flag cleanup process | P0.7 | P3 |
| DE-006 | GraphQL API layer | REST only | GraphQL for frontend flexibility | P0.5 | P3 |
| DE-007 | CQRS for read-heavy paths | Single model | Read replicas + query models | WP-X6 | P2 |
| DE-008 | Saga pattern for multi-service ops | None | Temporal saga orchestration | P7.7 | P2 |

---

## OSS Migration Candidates (from audit)

| Subsystem | Current (Custom LOC) | OSS Alternative | Priority |
|-----------|---------------------|-----------------|----------|
| Retry & Backoff | Custom resilience | `cenkalti/backoff/v4` | P0 |
| OAuth Flows | Custom cliproxy | `x/oauth2` | P0 |
| Agent Coordination | 7,141 LOC custom | Temporal task queues | P1 |
| Rate Limiting | Custom sliding window | `go-redis/redis_rate` | P1 |
| Code Parsing | Regex-based (10K LOC) | Tree-sitter / SCIP | P1 |
| Redis Cache | Custom JSON + tags | `eko/gocache` | P2 |

---

## Implementation Status Summary

### Already Fully Implemented (Quick Wins)

- **QW-001**: VSCode settings.json, extensions.json ✅
- **QW-002**: VSCode launch.json debugger ✅
- **QW-003**: .editorconfig ✅
- **QW-004**: PR template ✅
- **QW-006**: Database migrations ✅
- **QW-007**: Neo4j schema ✅

### Already Fully Implemented (Core Infrastructure)

#### Caching & Performance
- **PERF-001**: Redis caching with cache_middleware.go, redis_cache.go, warmer.go ✅
  - Located: `/backend/internal/cache/`
  - Features: Hot path caching, stampede protection, versioned caching

- **PERF-006**: WebSocket message batching (backpressure.go) ✅
  - Located: `/backend/internal/websocket/`
  - Features: Message backpressure, flow control

- **PERF-010**: NATS JetStream with consumer configuration ✅
  - Located: `/backend/internal/nats/`
  - Features: Publisher, subscriber with DLQ support

- **PERF-011**: Cursor pagination (cursor.go) ✅
  - Located: `/backend/internal/pagination/`
  - Features: Base64 cursor encoding, cursor-based pagination

#### Frontend Caching & Resilience
- **Frontend Cache Layer**: CacheManager.ts, IndexedDBCache.ts, ServiceWorkerCache.ts ✅
  - Located: `/frontend/apps/web/src/lib/cache/`
  - Features: Multi-tier caching (memory, IndexedDB, ServiceWorker)

- **Frontend Resilience**: CircuitBreaker.ts, RetryPolicy.ts ✅
  - Located: `/frontend/apps/web/src/lib/resilience/`

#### Robustness & Resilience
- **ROB-001**: Circuit breaker per service (gobreaker integration) ✅
  - Located: `/backend/internal/resilience/circuit_breaker.go`
  - Features: 3-state breaker, configurable thresholds, state change callbacks
  - Services: GitHub, Linear, OpenAI, Anthropic, Python backend, Temporal, Redis, Neo4j, S3

- **ROB-002**: Retry with exponential backoff + jitter ✅
  - Located: `/backend/internal/resilience/retry.go`
  - Features: Configurable policies (default, aggressive, conservative), crypto-secure jitter, budget tracking

- **ROB-003**: Rate limiting with sliding window ✅
  - Located: `/backend/internal/ratelimit/throttle.go`, `sliding_window.go`
  - Features: Adaptive throttling, priority queues, distributed state via Redis, circuit breaker integration

- **ROB-005**: Health check with dependency cascade ✅
  - Located: `/backend/internal/health/checks.go`, `handler.go`

- **ROB-006**: Dead-letter queue for NATS ✅
  - Configured in nats.go with monitoring

- **ROB-009**: Input validation on endpoints ✅
  - Located: `/backend/internal/middleware/validation_middleware.go`
  - Features: Query param validation, UUID validation, file upload validation, content-type validation

- **ROB-010**: Conflict detection in agent coordination ✅
  - Located: `/backend/internal/agents/conflict_detector.go`, `coordination_types.go`
  - Features: ConflictDetector, ItemVersion tracking, ConflictRecord queue
  - Resolution strategies: LastWriteWins, AgentPriority, Manual, Merge, FirstWins

- **ROB-011**: Idempotency keys ✅
  - Located: `/backend/internal/resilience/retry.go`
  - Functions: IdempotencyKey(), WithIdempotencyKey()

#### WebSocket & Real-time Communication
- **WebSocket Infrastructure**: websocket.go, subscription_manager.go, audit.go, presence.go ✅
  - Located: `/backend/internal/websocket/`
  - Features: Backpressure handling, presence tracking, audit logging, subscription management

#### Data Access & Pagination
- **Database migrations**: SQL migrations in `/backend/internal/db/migrations/` ✅
  - Automated migration system with rollback support

### Partially Implemented

- **PERF-003**: Bulk import with basic batching (can be enhanced to 1000+ with streaming) - Partial
- **PERF-009**: gRPC infrastructure exists (server.go) but connection pooling not tuned - Partial
- **ROB-004**: Some graceful shutdown in Go backend - Partial
- **ROB-012**: Timeout budgets exist but not comprehensive - Partial
- **OPS-010**: OpenTelemetry configured but not end-to-end tracing - Partial
- **DE-001**: Go uses consistent response envelope, Python mixed - Partial

### Not Yet Implemented

- **PERF-002**: Materialized views for incremental refresh
- **PERF-004**: Automated PostgreSQL query plan analysis
- **PERF-005**: Frontend bundle size optimization with code splitting
- **PERF-007**: Batch embedding computation
- **PERF-008**: Graph rendering virtualization for 10K+ nodes
- **PERF-012**: pgvector HNSW index optimization
- **ROB-007**: Database connection pool tuning (pool size 20, overflow 10)
- **ROB-008**: Webhook delivery with retry budget
- **QW-005**: Fix remaining Python tests (67 failing)
- **QW-008**: FR traceability markers in all tests
- **UX items**: Most UX enhancements not started
- **DX items**: Most DX improvements not started
- **OPS items**: Most ops automation not started
- **DE items**: Remaining design enhancements not started

## Code Artifact Locations

### Backend (Go) - `/backend/internal/`
- **Cache**: `cache/` (redis_cache.go, warmer.go, stampede.go, metrics.go)
- **Resilience**: `resilience/` (circuit_breaker.go, retry.go)
- **Rate Limiting**: `ratelimit/` (throttle.go, sliding_window.go)
- **WebSocket**: `websocket/` (websocket.go, subscription_manager.go, backpressure.go)
- **Health**: `health/` (checks.go, handler.go)
- **Pagination**: `pagination/` (cursor.go)
- **NATS Messaging**: `nats/` (nats.go, publisher.go, publisher_utils.go)
- **gRPC**: `grpc/` (server.go)
- **Agents**: `agents/` (conflict_detector.go, coordination_types.go, distributed_coordination_manager.go)
- **Middleware**: `middleware/` (validation_middleware.go, rate_limiter.go, cache.go, api_key_middleware.go)
- **Database**: `db/migrations/` (automated SQL migrations)
- **Tracing**: `tracing/` (OTel integration - partially implemented)

### Frontend (TypeScript/React) - `/frontend/apps/web/src/lib/`
- **Cache**: `cache/` (CacheManager.ts, MemoryCache.ts, IndexedDBCache.ts, ServiceWorkerCache.ts)
- **Resilience**: `resilience/` (CircuitBreaker.ts, RetryPolicy.ts)

### Dev/Ops
- **VSCode Config**: `.vscode/` (settings.json, launch.json, extensions.json) ✅
- **Editor Config**: `.editorconfig` ✅
- **PR Template**: `.github/pull_request_template.md` ✅
- **Makefile**: `Makefile` (604 lines, consolidates dev, test, quality, load-test targets)
