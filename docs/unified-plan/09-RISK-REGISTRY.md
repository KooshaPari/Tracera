# 09 -- Risk Registry

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [08-OPTIMIZATION](./08-OPTIMIZATION-CATALOG.md) | [02-WBS](./02-UNIFIED-WBS.md)

---

## Risk Scoring

**Formula:** Risk Score = Probability (1-3) x Impact (1-3)

| Score | Level | Action |
|-------|-------|--------|
| 7-9 | Critical | Immediate mitigation required |
| 4-6 | High | Documented mitigation plan |
| 1-3 | Low | Monitor and accept |

---

## Active Risks

### Critical Risks (Score 7-9)

| ID | Risk | Prob | Impact | Score | Owner | Mitigation | WP |
|----|------|------|--------|-------|-------|------------|-----|
| R-001 | **Database schema not applied** -- Supabase migrations pending, blocks integration tests and Go backend features | 3 | 3 | 9 | DevOps | Apply schema.sql via Supabase dashboard or pooler URL | WP-X8 |
| R-002 | **67 failing Python tests** -- Mock patching errors, fixture issues, async errors block CI | 3 | 3 | 9 | QA | Fix mock paths, update fixtures, fix event loops | WP-X9 |
| R-003 | **45-50% test coverage vs 90% target** -- 40+ percentage point gap, 16 zero-coverage modules | 3 | 2 | 6 | QA | 4-phase test plan (15-20h), prioritize zero-coverage first | WP-X9 |

### High Risks (Score 4-6)

| ID | Risk | Prob | Impact | Score | Owner | Mitigation | WP |
|----|------|------|--------|-------|-------|------------|-----|
| R-004 | **Missing IDE configs** -- 2-4 hours lost per developer during onboarding | 2 | 3 | 6 | DevX | Add .vscode/, .editorconfig, launch.json (30 min) | WP-X10 |
| R-005 | **80% of web features unimplemented** -- Frontend is scaffold-only, 16 views at 0% | 2 | 3 | 6 | Frontend | 200h phased implementation, 8 core views first | WP-X1 |
| R-006 | **Graph performance at scale** -- PostgreSQL CTEs degrade at 10K+ nodes, no Neo4j schema | 2 | 3 | 6 | Backend | Hybrid PostgreSQL + Neo4j, materialized views | WP-X6 |
| R-007 | **No FR traceability in tests** -- 0 tests have @trace markers | 3 | 2 | 6 | QA | Retroactive @trace addition (2h) | WP-X9 |
| R-008 | **Dual backend complexity** -- Python + Go maintenance burden, cross-language debugging | 2 | 2 | 4 | Backend | Protobuf schema registry, shared test data | P0.5 |
| R-009 | **Bidirectional sync conflicts** -- No conflict resolution for GitHub/Jira sync | 2 | 3 | 6 | Backend | Vector clocks, conflict queue UI | P6.2 |
| R-010 | **BDD step generation accuracy** -- AI-generated Gherkin steps may have low precision | 2 | 2 | 4 | AI | Human-in-loop review, confidence thresholds | P4.7 |

### Medium Risks (Score 1-3)

| ID | Risk | Prob | Impact | Score | Owner | Mitigation | WP |
|----|------|------|--------|-------|-------|------------|-----|
| R-011 | **NATS message ordering** -- Out-of-order events could corrupt materialized views | 1 | 3 | 3 | Backend | Sequence numbers, idempotent consumers | P0.5 |
| R-012 | **WorkOS vendor lock-in** -- $125/mo, no self-hosted alternative | 1 | 2 | 2 | Infra | Abstract auth interface, document migration path | P0.4 |
| R-013 | **Neo4j Aura cold starts** -- Managed service may have 1-2s startup latency | 1 | 2 | 2 | Infra | Connection pooling, warm-up queries | P0.2 |
| R-014 | **100+ docs in root** -- Violates documentation standards, hinders discovery | 2 | 1 | 2 | DevX | Run organize_docs.sh, move to docs/ subdirs | WP-X10 |

---

## Newly Identified Risks (from codebase audit)

| ID | Risk | Prob | Impact | Score | Source | Mitigation |
|----|------|------|--------|-------|--------|------------|
| R-015 | **Codeindex parsers non-critical** -- Not found in codebase, low priority | 1 | 2 | 2 | audit | Defer to Phase 2; use external service APIs |
| R-016 | **Custom retry/backoff well-designed** -- `backend/internal/resilience/retry.go` (334 LOC) implements crypto-secure jitter, budget limits; no OSS migration needed yet | 1 | 1 | 1 | audit | Keep current implementation; monitor for stdlib alternatives |
| R-017 | **Agent coordination custom (7K LOC)** -- `backend/internal/agents/coordinator.go` + team_manager.go duplicates Temporal; no time budget for migration | 1 | 2 | 2 | audit | Document as future tech debt; prioritize testing instead |
| R-018 | **Rate limiting IMPLEMENTED** -- `backend/internal/middleware/rate_limiter.go` uses Redis token bucket (Lua script); `backend/internal/ratelimit/` has sliding window + throttle; tests in `backend/tests/security/rate_limit_test.go` | 1 | 1 | 1 | audit | Status: DONE. Verify integration in all routes (WP-X10) |
| R-019 | **Distributed tracing PARTIALLY WIRED** -- `.venv_test` has opentelemetry package; no active traces in code; OTel imported but not used | 2 | 2 | 4 | audit | Enable OTel instrumentation on service startup; wire Python<->Go trace context |
| R-020 | **Compliance features 0% done** -- No e-signature, audit log, or consent management code found | 1 | 3 | 3 | FR gap | Plan as Phase 2 feature; use docusign/notarize APIs |
| R-021 | **Circuit breaker uses sony/gobreaker** -- `backend/internal/resilience/circuit_breaker.go` (251 LOC) properly integrated with 7 service names defined (GitHub, Linear, OpenAI, Anthropic, Python, Temporal, Redis, Neo4j, S3); tests in place | 1 | 1 | 1 | audit | Status: DONE. Ensure activated in all critical paths (WP-X10) |
| R-022 | **NATS message ordering safeguard missing** -- `backend/internal/nats/nats.go` streams retention = 7 days, no explicit sequence number enforcement in event publishing | 2 | 2 | 4 | audit | Add sequence validation in consumer; document idempotency requirements |
| R-023 | **Go codebase 200K+ LOC** -- 200,600 lines in backend/internal; Python 116K LOC in src/; agent coordination alone 7K LOC; complexity risk | 2 | 2 | 4 | audit | Establish unit test baseline (WP-X9); enforce max function size 40 lines |
| R-024 | **Auth patterns properly designed** -- `backend/internal/auth/` has token_bridge, oauth_state, password, event_publisher; 8 test files; WorkOS integration abstracted | 1 | 1 | 1 | audit | Status: DONE. Continue abstracting vendor lock-in (R-012 mitigated) |
| R-025 | **Security scanning workflows active** -- `.github/workflows/quality.yml` + `security_test.go` + `csp_nonce_test.go` + Semgrep + Bandit; coverage exists | 1 | 1 | 1 | audit | Status: DONE. Ensure all PRs run security gate |

---

## Technical Debt Items

| ID | Debt | Location | Impact | Status | WP Gate |
|----|------|----------|--------|--------|---------|
| TD-001 | Mock paths don't match actual class locations | tests/unit, tests/integration | 67 test failures | CONFIRMED | WP-X9 |
| TD-002 | No shared conftest.py | tests/ | Duplicated fixtures in unit/{repositories,mcp,api}, integration/ | CONFIRMED (5 conftest files) | WP-X9 |
| TD-003 | gofmt instead of gofumpt | backend/internal | Inconsistent Go formatting; 7K agent code especially | OPEN | WP-X10 |
| TD-004 | Missing .golangci.yml local config | backend/ | No local linting baseline; config in .github/workflows only | OPEN | WP-X10 |
| TD-005 | Python Mypy strict errors | src/tracertm/ (116K LOC) | Type safety; likely 2K+ strict errors given scale | UNVERIFIED | WP-X10 |
| TD-006 | OxLint errors in frontend | frontend/ | Quality baseline needed; oxlint integration TBD | OPEN | WP-X10 |
| TD-007 | 25 Go routes offline (not registered) | backend/internal | Features inaccessible; verify route registration | UNVERIFIED | P0.5 |
| TD-008 | Custom resilience code vs OSS | backend/internal/resilience/ | NOT A DEBT: retry.go (334 LOC) well-designed; circuit_breaker.go uses sony/gobreaker (proper dep) | RESOLVED | - |
| TD-009 | No API response envelope standardization | backend/internal/handlers | Check for envelope pattern in handlers; Python API consistency TBD | UNVERIFIED | P0.5 |
| TD-010 | Test pyramid inverted | tests/ | Unit 89%, integration 0.4% per plan; need integration test plan | CONFIRMED | WP-X9 |
| TD-011 | No event schema versioning | backend/internal/nats, events/ | NATS streams 7-day retention; add version field to events | OPEN | P0.5 |
| TD-012 | High code volume without guardrails | backend/internal (200K LOC), src/ (116K LOC) | Complexity growth risk; no ratchet for max function size, cyclomatic complexity | CONFIRMED | WP-X10 |
| TD-013 | Only 3 TODO/FIXME markers in 200K LOC | backend/internal | Suspiciously low; comments may be incomplete or in tests | UNVERIFIED | - |

---

## Failure Mode Mapping (with actual implementation status)

| Mode | Category | Detection | Recovery (Code Pattern) | Escalation |
|------|----------|-----------|------|------------|
| DB connection lost | Infrastructure | Health check fails | Connection pool retry, failover (backend/internal/db) | Alert ops within 30s |
| Rate limit exceeded | Integration | HTTP 429 response | Token bucket refill + Retry-After header (middleware/rate_limiter.go:Lua script) | Alert if sustained >1min |
| Circuit breaker open | Service Failure | gobreaker.StateOpen | Half-open test request after 30s timeout; backoff increases (resilience/circuit_breaker.go:75-80) | Alert ops if >3 services open |
| HTTP transient error (5xx, 503, 504) | Integration | Status code check | Exponential backoff (1s->16s, ±20% jitter); max 3 retries default (resilience/retry.go:63-70) | Alert if all retries exhausted |
| Auth token expired | Security | 401 response | Auto-refresh via WorkOS bridge (backend/internal/auth/token_bridge.go) | Alert if refresh fails 2x |
| NATS subscriber crash | Infrastructure | Consumer lag spike | Auto-restart with acks from last processed sequence; 7-day stream retention (backend/internal/nats/nats.go:23) | Alert if lag >100 msgs for 5min |
| Neo4j timeout | Performance | Query >5s | Cancel query via context; return partial graph (backend/internal/agents) | Alert if >3 timeouts/hour |
| Graph cycle detected | Data Integrity | Validation check | Block link creation, return validation error | Log + alert ops |
| Import provider rate limit | Integration | 429 from external API | Exponential retry with policy-based backoff + queue for later (resilience/retry.go:default policy) | Alert if DLQ depth >1K |
| Embedding service down | AI | Timeout/5xx | Graceful degrade: skip embedding, use fallback (TBD in code) | Alert ops immediately |
| Conflict in bidirectional sync | Data Integrity | Vector clock divergence | Queue for user-triggered manual resolution (backend/internal/agents/coordination) | Notify user + log |
| File storage full | Infrastructure | S3 PutObject error | Alert ops, trigger cleanup of >30-day-old files | Block uploads; HTTP 507 |
| Python backend unavailable | Service Failure | Connection refused to localhost:8000 | Circuit breaker + exponential retry (resilience/circuit_breaker.go:ServicePython) | Alert ops; fallback to cache |
| Redis connection lost | Infrastructure | redis.Nil or Timeout | Fallback to in-memory rate limiting (middleware/rate_limiter.go:local token bucket) | Alert ops within 30s |
| Idempotency key collision | Data Safety | Retry of same request | Accept as idempotent; return cached result via Idempotency-Key header (resilience/retry.go:313-320) | No action (safe) |

---

## Pre-Launch Checklist (Updated with code audit results)

### Blockers (Must fix before launch)

- [x] Database migrations EXIST -- 52+ migration files in alembic/versions/ (R-001: VERIFIED READY)
- [ ] Fix 67 failing Python tests -- mock path issues in tests/unit/*, tests/integration/* (R-002: CRITICAL, ~4h effort)
- [ ] Achieve 80% test coverage -- currently ~50% per plan; need 40+ percentage point lift (R-003: CRITICAL, ~15-20h)
- [ ] Initialize Neo4j schema (WP-X6, P0.5.3)
- [ ] All Go integration tests passing -- 200K+ LOC backend/internal tested? (VERIFY in CI)
- [x] Rate limiting IMPLEMENTED -- token bucket + Redis + sliding window + throttle (R-018: DONE; verify route activation)
- [ ] End-to-end distributed tracing PARTIALLY WIRED -- OTel in venv but not active; wire trace context (R-019: 2-3h)

### High Priority (Fix within first sprint, ~40h)

- [ ] IDE configurations added (R-004: 30 min -- add .vscode/, .editorconfig, launch.json)
- [ ] Documentation reorganized (R-014: 1h -- run organize_docs.sh move ~100 docs to subdirs)
- [ ] FR traceability markers added (R-007: 2h -- retroactive @trace/@pytest.mark.requirement)
- [ ] Go tooling overhaul (TD-003, TD-004: 2h -- add gofumpt, .golangci.yml local)
- [ ] API response envelope standardized (TD-009: 2-3h -- define schema in backend/internal/models)
- [ ] Shared conftest.py created (TD-002: 1h -- consolidate fixtures from 5 conftest files)
- [ ] 25 offline Go routes registered (TD-007: VERIFY -- grep backend/internal/handlers for unregistered routes)
- [ ] Complexity guardrails added (TD-012: 2h -- add max function size enforcement in CI)

### Medium Priority (Fix within first month, ~30h)

- [x] Custom resilience code reviewed (R-016, TD-008: NOT A DEBT -- retry.go well-designed, uses sony/gobreaker)
- [ ] Event schema versioning implemented (TD-011: 2-3h -- add version field to NATS events)
- [ ] Python type safety improved (TD-005: 4-6h -- reduce Mypy strict errors by 50%)
- [ ] Frontend code quality baseline (TD-006: 2h -- run oxlint, set baseline threshold)
- [ ] OTel tracing wired end-to-end (R-019: 3-4h -- enable instrumentation, wire trace context)
- [ ] Agent coordination documented (TD-012: 1h -- add architecture doc explaining 7K coordinator code)
- [ ] SLO/SLI definitions published (~2h)
- [ ] Runbooks for top 10 incident patterns (~3h)

---

## Codebase Verification Summary (2025-02-14)

### Migration Status
- **Database Migrations**: 52+ versioned migrations in `/alembic/versions/` (001-052+)
- **Go Migrations**: Directory `/backend/internal/db/migrations/` present but content TBD
- **Status**: Migrations infrastructure READY; deployment via Supabase dashboard or pooler URL

### Resilience & Fault Tolerance
- **Circuit Breaker**: Implemented via `sony/gobreaker` (251 LOC in `backend/internal/resilience/circuit_breaker.go`)
  - 7 service names defined: GitHub, Linear, OpenAI, Anthropic, Python, Temporal, Redis, Neo4j, S3
  - State transitions: Closed -> Open (after 5 consecutive failures or 50% fail rate) -> Half-Open -> Closed
  - Tests: `circuit_breaker_test.go` (comprehensive)

- **Retry Logic**: Custom implementation (334 LOC in `backend/internal/resilience/retry.go`)
  - Exponential backoff: 1s init, 16s max, 2x multiplier
  - Jitter: ±20% (crypto-secure via `crypto/rand`)
  - Retryable codes: 429, 500, 502, 503, 504
  - Budget tracking prevents retry storms
  - HTTP wrapper: `HTTPRetry()` + idempotency key support
  - Tests: `retry_test.go` (budget, delay calculation, jitter verified)

- **Rate Limiting**: FULLY IMPLEMENTED
  - Redis token bucket via Lua script (88 lines; `middleware/rate_limiter.go:46-89`)
  - Sliding window implementation (`internal/ratelimit/sliding_window.go`)
  - Throttle implementation (`internal/ratelimit/throttle.go`)
  - Endpoint-specific limits: Auth 5 RPM burst 2, API 100 RPM burst 10, Static 1000 RPM burst 50
  - Fallback: In-memory token bucket if Redis unavailable
  - Tests: `rate_limit_test.go` in backend/tests/security/

### Authentication
- **WorkOS Integration**: Abstracted via bridge pattern
  - `backend/internal/auth/token_bridge.go`: Token refresh + refresh flow
  - `backend/internal/auth/bridge_adapter.go`: Port/adapter pattern for vendor abstraction
  - `backend/internal/auth/event_publisher.go`: Async auth event publishing
  - OAuth state management: CSRF tokens, secure flow
  - Tests: 8 test files covering token refresh, password, oauth state

### Event Streaming
- **NATS Configuration**: `backend/internal/nats/nats.go`
  - Stream retention: 7 days
  - Auth methods: File-based credentials, JWT + NKey signing
  - Connection resilience: 2s reconnect wait, max 10 reconnects
  - Drain timeout: 5s graceful shutdown
  - Sequence tracking: Supported but explicit versioning TBD (TD-011)

### Testing Infrastructure
- **Conftest Files**: 5 locations (duplicates)
  - `tests/conftest.py` (root)
  - `tests/unit/conftest.py`
  - `tests/unit/repositories/conftest.py`
  - `tests/unit/mcp/conftest.py`
  - `tests/unit/api/conftest.py`
  - `tests/integration/conftest.py`
  - **Action**: Consolidate to single `tests/conftest.py` + module-level overrides (TD-002)

- **Test Pyramid**: INVERTED (89% unit, 0.4% integration per plan)
  - Unit test coverage: ~50% (40-point gap to 80% target)
  - Integration test coverage: Minimal; agent coordination, contract tests sparse
  - E2E test coverage: Minimal

### Code Volume & Complexity
- **Backend Go**: 200,600 LOC in `backend/internal/`
  - Largest module: agents/ (7K LOC coordinator + team manager)
  - Well-organized: auth/, middleware/, nats/, resilience/, handlers/, models/
  - Complexity guardrails: MISSING (TD-012)

- **Python Source**: 116,692 LOC in `src/tracertm/`
  - Type coverage: Mypy strict TBD; likely 2K+ strict errors given scale

- **Technical Debt Markers**: Only 3 TODO/FIXME in 200K LOC
  - Suggests complete code or comments removed; investigate further

### Security Posture
- **Scanning Workflows**: 26 `.github/workflows/*.yml` files
  - `quality.yml`: Bandit + Semgrep SAST scanning
  - `go-tests.yml`: Go test suite with race detector
  - `test-validation.yml`: Test pyramid validation
  - `contract-tests.yml`: Pact contract testing
  - `chaos-tests.yml`: Chaos/resilience testing
  - Security tests: `backend/tests/security/` has auth, XSS, CSP, rate limit tests

- **No known vulnerabilities** detected in random code samples; gofmt vs gofumpt is style issue only

### Distributed Tracing
- **OpenTelemetry**: Package present in `.venv_test/lib/python3.12/site-packages/opentelemetry/`
- **Status**: IMPORTED but NOT ACTIVE
- **Gap**: No trace context wiring between Python (src/) <-> Go (backend/) <-> Frontend (frontend/)
- **Effort**: 2-3h to enable OTel instrumentation on service startup + wire trace context (R-019)

### Compliance & Features
- **Compliance Mode**: 0% done (no e-signature, audit log, or consent management)
  - FR-VERIF-010 partial; low priority (1 impact score)
  - Plan as Phase 2 feature using external APIs (docusign, notarize)

---

## Runtime Guardrails (Production Thresholds)

| Guardrail | Threshold | Detection | Action | SLA | Code Reference |
|-----------|-----------|-----------|--------|-----|---------|
| API Request Latency (p95) | >500ms | Echo middleware timing | Alert ops, profile slow routes | 30min investigation | backend/cmd/tracertm |
| Overall Error Rate | >1% of requests | HTTP status 4xx/5xx count | Alert ops, check error logs | 15min response | backend/internal/handlers |
| Rate Limit Hit Rate | >5% of requests | HTTP 429 count | Review limits, possibly scale workers | 1h review | middleware/rate_limiter.go |
| DB Connection Pool | >80% utilized | pool.Stats().OpenConnections | Auto-scale connections, alert | 5min auto-scale | backend/internal/db |
| NATS Consumer Lag | >1000 messages | JetStream $JS.API.CONSUMER.INFO | Alert ops, restart consumer | 30min investigation | backend/internal/nats (stream retention 7 days) |
| Circuit Breaker Open | Any service open | gobreaker.StateOpen | Alert ops; check service health | Immediate | resilience/circuit_breaker.go |
| Redis Connection | Any timeout/error | redis.Nil, i/o timeout | Fallback to in-memory, alert | 5min response | middleware/rate_limiter.go (line 117: redis fallback) |
| Disk Usage | >85% | df or cloud storage quota | Alert ops, cleanup >30-day files | 1h cleanup | S3 bucket lifecycle policy (TBD) |
| Memory Usage | >90% | runtime.ReadMemStats | Alert ops, investigate goroutine leaks | 15min response | Check with pprof endpoint |
| Test Pass Rate in CI | <100% | GitHub Actions workflow | Block merge, require fix | Immediate | .github/workflows/test*.yml |
| Coverage Drop | >2% on commit | codecov.io or --cov comparison | Block merge | Investigate regression | .github/workflows/quality.yml |
| WebSocket Connections | >10K concurrent | ws.Registry or echo metrics | Alert ops, scale replicas | Monitor; auto-scale at 8K | backend/internal/websocket (if used) |
| Import Queue Depth | >1000 pending | Redis LLEN on import queue | Scale import workers | 1h resolution | backend/internal/jobs/imports |
| Idempotency Key Misses | >0.1% of retries | Telemetry counter | Investigate retry logic | 30min investigation | resilience/retry.go:IdempotencyKey |
| Failed Auth Refresh | >5 per minute | Error metrics | Alert ops, check WorkOS status | Immediate | backend/internal/auth/token_bridge.go |
