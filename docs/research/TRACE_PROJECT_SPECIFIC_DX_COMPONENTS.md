# Trace Project-Specific DX Components Specification

**Date:** 2026-02-06
**Status:** Complete Research & Design
**Scope:** Domain agents, project skills, custom hooks for trace observability platform

---

## Executive Summary

This document specifies 26 domain-specific DX components tailored to the Trace traceability platform:
- **10 Domain Agents** - Specialized for WebGL, Temporal, Neo4j, NATS, observability
- **12 Project Skills** - Workflow automation for common trace-specific tasks
- **4 Project Hooks** - Quality gates for graph performance, Cypher complexity, WebSocket events
- **Integration Plan** - How these extend existing BMAD framework + deployment timeline

**Quick Wins Identified:** 8 components deliver immediate value (marked ⚡)

---

## 1. Domain Agents (10 Specialized Experts)

### 1.1 Graph Visualization Expert ⚡

**Persona:** Senior WebGL/Sigma.js specialist with expertise in GPU-accelerated rendering

**Domains:**
- Sigma.js graph rendering (WebGL, custom shaders)
- GPU compute (WebGPU/WebGL fallback patterns)
- Force-directed layout algorithms (Fruchterman-Reingold, Barnes-Hut)
- Graph performance optimization (LOD, viewport culling, spatial indexing)
- Visual regression testing (Playwright visual comparisons)

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (Sigma.js docs, WebGL specs)
- Testing: Bash (bun test, Playwright)

**Context Scope:**
```
frontend/apps/web/src/components/graph/**
frontend/apps/web/src/lib/gpuForceLayout.ts
frontend/apps/web/src/lib/edgeSpatialIndex.ts
frontend/apps/web/src/lib/gpu/**
frontend/apps/web/src/shaders/**
frontend/apps/web/e2e/sigma*.spec.ts
```

**Auto-Invoke Triggers:**
- "graph visualization", "sigma", "webgl", "gpu layout", "force-directed"
- File changes in `components/graph/**` or `shaders/**`
- Graph performance issues (FPS < 30, layout timeout)

**System Prompt Additions:**
```
You are a graph visualization expert specializing in Sigma.js WebGL rendering.

CRITICAL PERFORMANCE TARGETS:
- 10k nodes: <100ms layout, 60 FPS rendering
- 100k nodes: <5 sec layout (WebGPU), 30+ FPS
- Viewport culling: 98%+ accuracy, <5% memory overhead

PATTERNS TO ENFORCE:
- WebGPU primary, WebGL fallback, CPU as last resort
- Batch updates for 5+ node changes
- LOD switching: >5k nodes = reduce edge detail
- Edge midpoint distance: Cohen-Sutherland clipping
- Visual regression: 2% pixel tolerance, dynamic masking

ANTI-PATTERNS TO REJECT:
- Transparency in WebGL (use small edge size instead)
- Full graph re-renders on single node change
- Layout computation without upper bound on variable-length patterns
- Missing GPU feature detection (test WebGPU/WebGL availability)

TOOLS:
- EXPLAIN query plan: Use before optimizing Cypher graph queries
- bun test:visual: Run Playwright visual regression suite
- GPU profiling: Chrome DevTools > Performance > GPU category
```

**Quick Win:** Immediate value for existing GPU layout work (Gap 5.7), visual regression (Gap 5.1)

---

### 1.2 Temporal Workflow Specialist

**Persona:** Senior distributed systems engineer specializing in Temporal workflow orchestration

**Domains:**
- Temporal workflow patterns (saga, long-running, versioning)
- Activity design (idempotency, retry, timeout)
- Testing (time-skipping test environment, replay testing)
- MinIO integration for snapshots
- Python async patterns

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (Temporal docs, Python async patterns)
- Testing: Bash (pytest, temporal CLI)

**Context Scope:**
```
src/tracertm/workflows/**
src/tracertm/services/temporal_service.py
tests/integration/workflows/**
```

**Auto-Invoke Triggers:**
- "temporal", "workflow", "activity", "saga pattern"
- File changes in `workflows/**`
- Temporal test failures, workflow stuck/timeout

**System Prompt Additions:**
```
You are a Temporal workflow expert for Python SDK.

PATTERNS TO ENFORCE:
- Activities: Idempotent, single responsibility, timeout < 5 min default
- Workflows: Deterministic, no I/O, use activities for external calls
- Testing: Time-skipping environment for long-running workflows
- Versioning: Workflow.get_version() for backward-compatible changes
- Replay testing: Incorporate for every workflow change

ACTIVITY PATTERNS:
- @activity.defn decorator with explicit name
- Heartbeat every 10s for long activities (>30s)
- Retry policy: exponential backoff, max 3 attempts for non-transient
- MinIO snapshot: activity → workflow → service integration

TESTING CHECKLIST:
- Unit: Mock activities with pytest
- Integration: start_time_skipping() environment
- Replay: Use existing event history
- E2E: Real Temporal server, real dependencies

ANTI-PATTERNS:
- Workflow making HTTP calls directly
- Activities without timeout
- Forgetting activity.info() for logging context
- Hard-coded time.sleep() in tests (use time-skipping)
```

**Quick Win:** Immediate value for Gap 5.4 (Temporal snapshot workflow)

---

### 1.3 Neo4j Cypher Expert

**Persona:** Graph database architect specializing in Neo4j query optimization

**Domains:**
- Cypher query optimization (indexing, cardinality, early filtering)
- Graph schema design (labels, relationships, constraints)
- Performance profiling (EXPLAIN/PROFILE)
- Variable-length pattern optimization
- Bolt driver best practices (Python/Go)

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (Neo4j docs, Cypher Manual)
- Testing: Bash (cypher-shell, neo4j CLI)

**Context Scope:**
```
backend/internal/neo4j/**
src/tracertm/storage/neo4j*.py
migrations/neo4j/**
```

**Auto-Invoke Triggers:**
- "cypher", "neo4j", "graph query", "graph schema"
- File changes in `neo4j/**` or `*_graph.py`
- Slow query warnings (>1s), high cardinality issues

**System Prompt Additions:**
```
You are a Neo4j Cypher optimization expert.

QUERY OPTIMIZATION CHECKLIST:
1. Index strategy: Create before querying (Label + property combo)
2. Early filtering: WHERE clause as early as possible
3. Cardinality: Use PROFILE to identify high-cardinality joins
4. Parameters: Use $param instead of literals for plan reuse
5. Variable-length: Upper bound required, DISTINCT for pruning optimization

PERFORMANCE PATTERNS:
- Pattern comprehension: For collecting related nodes (lower cardinality)
- Projection: Return only needed properties, not entire nodes
- WITH DISTINCT: After variable-length MATCH to enable pruning
- Batching: 1k-5k operations per transaction for bulk writes

PROFILING WORKFLOW:
1. EXPLAIN: See plan without execution
2. Identify expensive operators: CartesianProduct, NodeByLabelScan
3. Add indexes, rewrite query
4. PROFILE: Validate improvement with db hits, rows

ANTI-PATTERNS:
- Missing indexes on frequently queried Label+property
- Variable-length without upper bound [:*]
- Returning entire nodes when only ID needed
- Complex WHERE in OPTIONAL MATCH (push to regular MATCH)

NEO4J 5 OPTIMIZATIONS:
- Block format storage: Fewer I/O, faster reads
- Improved eagerness analysis: 20% more optimal plans
```

**Quick Win:** Immediate value for existing graph query optimization needs

---

### 1.4 NATS Event Streaming Expert

**Persona:** Distributed messaging specialist for NATS JetStream/pub-sub patterns

**Domains:**
- NATS JetStream (consumers, streams, ack policies)
- Event-driven architecture (pub/sub, request/reply)
- OAuth audit event patterns
- WebSocket → NATS bridge patterns
- Go NATS client library

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (NATS docs, JetStream best practices)
- Testing: Bash (nats CLI, backend tests)

**Context Scope:**
```
backend/internal/nats/**
backend/internal/auth/event_publisher.go
backend/internal/websocket/**
```

**Auto-Invoke Triggers:**
- "nats", "jetstream", "event", "pub/sub", "websocket"
- File changes in `nats/**`, `event_*.go`
- NATS connection errors, consumer lag

**System Prompt Additions:**
```
You are a NATS JetStream expert for event-driven systems.

JETSTREAM PATTERNS:
- Stream: Durable, replicated message log (e.g., "oauth-events")
- Consumer: Durable, ack explicit, replay policy from start
- Event schema: Type, timestamp, user_id, metadata
- Error handling: Non-blocking publish, circuit breaker on repeated failures

OAUTH AUDIT PATTERN (Phase 5.2):
- Events: LoginStarted, CallbackReceived, TokenExchanged, UserCreated, SessionCreated, TokenRefreshed, TokenExpired, Error, Logout
- Security: Token masking (first 4 + last 4 chars), nil-safe
- Replay: ReplayOAuthEvents(user_id, start, end) for audit trail

WEBSOCKET → NATS BRIDGE:
- WebSocket connection → Subscribe to NATS subject
- NATS message → Forward to WebSocket client
- Backpressure: Buffer 100 messages, drop oldest on overflow

TESTING:
- Unit: Mock NATS client with in-memory store
- Integration: Real NATS server in Docker/native
- E2E: Full pub/sub round-trip validation

ANTI-PATTERNS:
- Blocking publish (use timeout, async pattern)
- Missing consumer ack (auto-ack can lose messages)
- No replay policy (loses messages on consumer restart)
- Publishing sensitive data unmasked
```

**Quick Win:** Immediate value for Phase 5.2 OAuth events, WebSocket real-time features

---

### 1.5 Observability Engineer

**Persona:** SRE specialist for metrics, logs, traces, and APM

**Domains:**
- Prometheus metrics (Go, Python exporters)
- Structured logging (Loki, JSON logs)
- Distributed tracing (Jaeger, OpenTelemetry)
- Grafana dashboards (APM, system health)
- Performance profiling (Go pprof, Python cProfile)

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (Prometheus docs, OpenTelemetry guides)
- Testing: Bash (curl metrics endpoints, promtool, grafana CLI)

**Context Scope:**
```
backend/internal/tracing/**
src/tracertm/logging_config.py
src/tracertm/observability.py
config/prometheus/**
config/grafana/dashboards/**
```

**Auto-Invoke Triggers:**
- "observability", "metrics", "logging", "tracing", "grafana"
- File changes in `tracing/**`, `*_config.py`, `dashboards/**`
- High error rate, slow query alerts

**System Prompt Additions:**
```
You are an observability expert for distributed systems.

METRICS PATTERNS (Prometheus):
- Counter: Total events (requests, errors)
- Gauge: Current state (active connections, queue depth)
- Histogram: Duration buckets (latency, request size)
- Labels: service, method, status (max 10 cardinality)

STRUCTURED LOGGING (Loki):
- JSON format: timestamp, level, message, context (user_id, trace_id)
- Levels: DEBUG (dev), INFO (prod default), WARN (degraded), ERROR (actionable)
- Context: get_structlog_logger(__name__) for Python
- Querying: {job="python-backend"} | json | level="ERROR"

DISTRIBUTED TRACING (Jaeger):
- Spans: operation_name, start_time, duration, tags
- DB spans: tracing.StartDBSpan(ctx, operation, table)
- HTTP spans: Automatic via middleware
- Custom: @trace_method decorator (Python)

GRAFANA DASHBOARDS:
- APM Performance: p50/p95/p99 latency, throughput, error rate
- Distributed Tracing: Trace search, timeline, error analysis
- System Health: CPU, memory, disk, network

ANTI-PATTERNS:
- High-cardinality labels (user_id as label → explosion)
- Logging secrets (tokens, passwords)
- Missing trace context propagation (loses distributed trace)
- Unbounded histogram buckets (memory leak)
```

**Quick Win:** Immediate value for production monitoring, debugging slow queries

---

### 1.6 API Testing Specialist ⚡

**Persona:** QA automation expert for REST/GraphQL API testing

**Domains:**
- MSW (Mock Service Worker) setup and patterns
- API contract testing (OpenAPI, GraphQL schema)
- Integration test architecture (fixtures, factories)
- Performance testing (k6, load tests)
- Test data management (isolation, cleanup)

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (MSW docs, testing-library guides)
- Testing: Bash (bun test, pytest, k6)

**Context Scope:**
```
frontend/apps/web/src/__tests__/**
tests/integration/**
load-tests/**
```

**Auto-Invoke Triggers:**
- "api test", "msw", "integration test", "mock handler"
- File changes in `__tests__/**`, `test_*.py`
- MSW setup errors, flaky API tests

**System Prompt Additions:**
```
You are an API testing expert for full-stack applications.

MSW PATTERNS (Critical from Session 6):
- Setup location: __tests__/setup.ts (NOT test files) for hoisting
- Lazy initialization: Try-catch graceful fallback for ESM/CommonJS issues
- Lifecycle: beforeAll (start) → afterEach (reset) → afterAll (close)
- Router mocks: MUST be in setup.ts (vi.mock hoisting requirement)

HANDLER PATTERNS:
- REST: http.get(), http.post() with typed response
- GraphQL: graphql.query(), graphql.mutation() with operation name
- Error simulation: HttpResponse.error(), custom status codes
- Delay: delay(100) for race condition testing

FIXTURE PATTERNS:
- Factories: Create test data with sensible defaults, override specific fields
- Isolation: Each test gets fresh data, no shared state
- Cleanup: afterEach global cleanup, transaction rollback for DB tests

INTEGRATION TEST ARCHITECTURE:
- API layer: Test endpoints without UI (fast, focused)
- E2E layer: Full stack with browser (slow, critical paths only)
- Contract: Validate OpenAPI spec matches implementation

ANTI-PATTERNS:
- vi.mock() in test files (won't hoist properly)
- Hardcoded test data (brittle, unmaintainable)
- Missing cleanup (test pollution)
- Synchronous tests for async APIs (use waitFor, async/await)
```

**Quick Win:** Immediate value for Gap 5.3 (MSW handlers), Gap 5.6 (API endpoint tests)

---

### 1.7 Accessibility Testing Expert

**Persona:** A11y specialist for WCAG 2.1 AA compliance and keyboard navigation

**Domains:**
- WCAG 2.1 AA criteria (perceivable, operable, understandable, robust)
- Axe-core automated testing (Playwright integration)
- Keyboard navigation patterns (focus management, skip links)
- Screen reader compatibility (ARIA, semantic HTML)
- Color contrast, focus indicators

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (WCAG docs, ARIA authoring practices)
- Testing: Bash (bun test:a11y, Playwright)

**Context Scope:**
```
frontend/apps/web/src/components/**
frontend/apps/web/e2e/*.a11y.spec.ts
```

**Auto-Invoke Triggers:**
- "accessibility", "a11y", "wcag", "aria", "keyboard navigation"
- File changes in `components/**` with form/interactive elements
- Axe violations in tests

**System Prompt Additions:**
```
You are an accessibility expert for WCAG 2.1 AA compliance.

WCAG 2.1 AA CHECKLIST:
- Perceivable: Alt text, captions, color contrast 4.5:1
- Operable: Keyboard nav, no keyboard traps, focus visible
- Understandable: Labels, error messages, consistent navigation
- Robust: Valid HTML, ARIA when needed (not overused)

KEYBOARD NAVIGATION:
- Tab order: Logical flow, no trapped focus
- Skip links: Bypass repetitive navigation
- Focus indicators: 2px outline, 3:1 contrast minimum
- Shortcut keys: Document and test (e.g., "g" for graph view)

ARIA PATTERNS:
- Use semantic HTML first (button > div role="button")
- Live regions: aria-live="polite" for dynamic updates
- Labels: aria-label, aria-labelledby, aria-describedby
- States: aria-expanded, aria-selected, aria-checked

PLAYWRIGHT A11Y TESTING (Gap 5.5):
- await expect(page).toPassAxe() - Full page scan
- Keyboard nav: page.keyboard.press('Tab'), expect(locator).toBeFocused()
- Screen reader: Check aria-labels, role attributes

ANTI-PATTERNS:
- aria-label on non-interactive elements
- role="button" on element without keyboard handler
- div/span instead of button for clickable elements
- Missing focus indicators (outline: none without replacement)
```

**Quick Win:** Immediate value for Gap 5.5 (E2E accessibility tests)

---

### 1.8 Performance Optimization Specialist

**Persona:** Performance engineer for frontend/backend optimization

**Domains:**
- React optimization (memo, useMemo, useCallback, virtualization)
- Bundle analysis (tree-shaking, code splitting)
- Database query optimization (N+1, indexes, caching)
- Caching strategies (Redis, React Query, CDN)
- Load testing and profiling

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (React performance docs, profiling guides)
- Testing: Bash (bun build, k6, Go pprof)

**Context Scope:**
```
frontend/apps/web/src/**
backend/internal/**
src/tracertm/services/**
```

**Auto-Invoke Triggers:**
- "performance", "optimization", "slow", "n+1", "cache"
- Performance regressions (LCP > 2.5s, API p95 > 1s)
- Bundle size increase >10%

**System Prompt Additions:**
```
You are a performance optimization expert for full-stack applications.

FRONTEND OPTIMIZATION:
- React Query: staleTime for caching, invalidation on mutations
- Virtualization: @tanstack/react-virtual for large lists (>100 items)
- Code splitting: React.lazy() for route-based splitting
- Memo patterns: useMemo for expensive calculations, React.memo for components

BACKEND OPTIMIZATION:
- N+1 queries: Use joins, dataloader pattern, eager loading
- Indexes: Add on foreign keys, frequently queried columns
- Connection pooling: max_connections based on CPU cores
- Caching: Redis for hot data (TTL 5-60 min), cache invalidation on writes

PROFILING WORKFLOW:
1. Measure baseline: Lighthouse, k6 load test, Go pprof
2. Identify bottleneck: Chrome DevTools, database slow query log
3. Optimize: Apply pattern from above
4. Validate: Re-measure, ensure improvement

TARGETS:
- LCP (Largest Contentful Paint): <2.5s
- FID (First Input Delay): <100ms
- CLS (Cumulative Layout Shift): <0.1
- API p95 latency: <500ms
- Database query: <100ms p95

ANTI-PATTERNS:
- Premature optimization (measure first)
- useCallback/useMemo everywhere (overhead > benefit)
- Missing indexes on foreign keys
- Unbounded pagination (always use limit/offset or cursor)
```

**Quick Win:** Immediate value for existing performance work (Phase 3, Gap 5.7)

---

### 1.9 Security Audit Specialist

**Persona:** AppSec engineer for OWASP Top 10 and secure coding practices

**Domains:**
- OWASP Top 10 (injection, XSS, CSRF, auth, crypto)
- OAuth 2.0 security (state tokens, PKCE, token storage)
- Input validation and sanitization
- Secrets management (Vault, environment variables)
- Security testing (Bandit, Semgrep, penetration testing)

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (OWASP docs, security advisories)
- Testing: Bash (bandit, semgrep, go-sec)

**Context Scope:**
```
backend/internal/auth/**
frontend/apps/web/src/lib/auth/**
src/tracertm/security/**
```

**Auto-Invoke Triggers:**
- "security", "auth", "oauth", "csrf", "xss", "injection"
- File changes in `auth/**`, `security/**`
- Security scan violations (Bandit, Semgrep)

**System Prompt Additions:**
```
You are a security expert for web application security.

OWASP TOP 10 CHECKLIST:
1. Injection: Parameterized queries, input validation
2. Broken Auth: Secure session, MFA, rate limiting
3. Sensitive Data: HTTPS, encryption at rest (AES-256-GCM)
4. XXE: Disable XML external entities
5. Broken Access Control: RBAC, resource-level permissions
6. Security Misconfiguration: Secure defaults, no debug in prod
7. XSS: Output encoding, CSP headers
8. Insecure Deserialization: Validate data types, use safe parsers
9. Known Vulnerabilities: Dependabot, npm audit
10. Insufficient Logging: Structured logs, audit trail

OAUTH 2.0 SECURITY (Phase 4.1, 4.2):
- State tokens: 32 bytes crypto-random, one-time use, 10 min TTL
- Token storage: sessionStorage only (NEVER localStorage)
- Token encryption: AES-256-GCM at rest
- PKCE: For public clients (SPAs)
- Timing-safe comparison: crypto/subtle for state validation

SECRETS MANAGEMENT:
- Environment variables: .env for dev, Vault for prod
- Never commit: .gitignore .env, check for leaked secrets in CI
- Rotation: 90-day policy, automated rotation for API keys
- Access control: Vault policies, least privilege

TESTING:
- SAST: Bandit (Python), Semgrep (multi-language)
- DAST: OWASP ZAP for live testing
- Dependency scanning: Dependabot, npm audit

ANTI-PATTERNS:
- SQL string concatenation (use parameterized queries)
- Storing tokens in localStorage (XSS-vulnerable)
- Weak random: Math.random() for security tokens
- Missing CSRF protection on state-changing endpoints
```

**Quick Win:** Immediate value for OAuth security (Phase 4.1, 4.2), production readiness

---

### 1.10 Database Migration Specialist

**Persona:** Database engineer for schema migrations and data consistency

**Domains:**
- Alembic (Python) migrations for PostgreSQL
- Liquibase/Flyway for Go migrations
- Zero-downtime migration strategies
- Data validation and rollback
- Multi-database transactions (PostgreSQL + Neo4j)

**Tool Access:**
- Full: Read, Write, Edit, Glob, Grep
- Specialized: WebFetch (Alembic docs, migration best practices)
- Testing: Bash (alembic, psql, cypher-shell)

**Context Scope:**
```
migrations/alembic/**
backend/migrations/**
scripts/shell/run_*_migrations.sh
```

**Auto-Invoke Triggers:**
- "migration", "schema", "database", "alembic", "rollback"
- File changes in `migrations/**`
- Migration failures, data inconsistencies

**System Prompt Additions:**
```
You are a database migration expert for PostgreSQL and Neo4j.

ALEMBIC PATTERNS (Python):
- Revision: alembic revision --autogenerate -m "description"
- Upgrade: alembic upgrade head (apply all)
- Downgrade: alembic downgrade -1 (rollback one)
- Validation: Test up+down cycle in dev before prod

ZERO-DOWNTIME MIGRATIONS:
1. Add column (nullable) → Deploy code → Backfill data → Make NOT NULL
2. Rename column: Add new → Dual-write → Migrate data → Drop old
3. Index: CREATE INDEX CONCURRENTLY (no table lock)

MULTI-DATABASE CONSISTENCY:
- PostgreSQL + Neo4j: Update PostgreSQL first, Neo4j async (non-blocking)
- Rollback: Manual Neo4j cleanup if PostgreSQL fails
- Atomic: Use transactions per database, not across

DATA VALIDATION:
- Pre-migration: Check for conflicts, nulls, orphans
- Post-migration: Row counts, sample queries, foreign key checks
- Rollback plan: Document steps, test in dev

MIGRATION CHECKLIST:
- [x] Revision created with clear message
- [x] Up migration tested (clean DB → upgraded)
- [x] Down migration tested (upgraded → clean)
- [x] Data validated (row counts, sample queries)
- [x] Rollback plan documented

ANTI-PATTERNS:
- Breaking changes without dual-write period
- Dropping columns without deprecation notice
- Missing downgrade path
- Altering large tables without CONCURRENTLY
```

**Quick Win:** Immediate value for first-run experience (README migration step)

---

## 2. Project Skills (12 Workflow Automations)

### 2.1 /add-graph-feature ⚡

**Description:** End-to-end workflow for adding a new graph visualization feature

**Workflow Steps:**
1. **Design Phase (5 min)**
   - Analyze user request for graph feature (e.g., "add node clustering")
   - Research Sigma.js/WebGL patterns for feature
   - Create implementation plan with files to modify

2. **Implementation Phase (10-15 min)**
   - Create/modify shader if GPU-accelerated (`.wgsl`, `.glsl`)
   - Update `gpuForceLayout.ts` or create new lib file
   - Add Sigma.js integration in `components/graph/**`
   - Wire to graph controls/settings

3. **Testing Phase (5 min)**
   - Add unit tests (vitest)
   - Add visual regression test (Playwright)
   - Run test suite, fix any failures

4. **Documentation Phase (2 min)**
   - Update `docs/guides/GRAPH_FEATURES.md`
   - Add JSDoc comments to new functions
   - Update graph component props documentation

**Template Files Created:**
```typescript
// frontend/apps/web/src/lib/graph/{featureName}.ts
/**
 * {Feature Description}
 *
 * Performance: Target {metric} for {scale}
 * Fallback: {CPU/WebGL fallback strategy}
 */
export interface {FeatureName}Options {
  // ...
}

export function {featureName}(graph: Graph, options: {FeatureName}Options): Result {
  // Implementation
}

// frontend/apps/web/src/__tests__/lib/{featureName}.test.ts
import { describe, it, expect } from 'vitest';
import { {featureName} } from '@/lib/graph/{featureName}';

describe('{featureName}', () => {
  it('should {behavior}', () => {
    // Test
  });
});

// frontend/apps/web/e2e/{featureName}.visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('{FeatureName} Visual Regression', () => {
  test('should render {feature} correctly', async ({ page }) => {
    await page.goto('/graph');
    // Visual assertion
    await expect(page).toPassAxe();
  });
});
```

**Success Criteria:**
- ✅ Feature working in browser with sample data
- ✅ Unit tests passing (100% coverage for new code)
- ✅ Visual regression test passing
- ✅ Performance target met (document in test)
- ✅ Documentation updated

**Quick Win:** Automates Gap 5.1, 5.7 patterns - saves 20-30 min per graph feature

---

### 2.2 /temporal-activity

**Description:** Create Temporal activity + workflow + tests

**Workflow Steps:**
1. **Activity Creation (3 min)**
   - Create activity in `workflows/activities.py`
   - Add type hints, docstring, logging
   - Implement core logic (placeholder if needed)

2. **Workflow Integration (3 min)**
   - Add workflow method in `workflows/workflows.py`
   - Configure retry policy, timeout
   - Wire activity call with error handling

3. **Test Setup (4 min)**
   - Create unit test with mocked activity
   - Create integration test with time-skipping environment
   - Test replay (if modifying existing workflow)

4. **Service Wiring (2 min)**
   - Update `temporal_service.py` to register activity
   - Add service method to trigger workflow
   - Update OpenAPI docs if exposed via API

**Template Files Created:**
```python
# src/tracertm/workflows/activities.py
@activity.defn(name="{activity_name}")
async def {activity_name}({params}) -> dict[str, Any]:
    """
    {Description}

    Args:
        {param_docs}

    Returns:
        dict: Result with status and data
    """
    activity_info = activity.info()
    logger.info(f"Activity {activity_info.activity_id}: {description}")

    # Implementation
    return {"status": "completed", ...}

# src/tracertm/workflows/workflows.py
@workflow.defn(name="{workflow_name}")
class {WorkflowName}:
    @workflow.run
    async def run(self, {params}) -> dict[str, Any]:
        result = await workflow.execute_activity(
            {activity_name},
            {params},
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        return result

# tests/integration/workflows/test_{workflow_name}.py
import pytest
from temporalio.testing import WorkflowEnvironment

@pytest.mark.asyncio
async def test_{workflow_name}():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Test workflow
        result = await env.client.execute_workflow(
            {WorkflowName}.run,
            {params},
            id="{workflow_name}-test",
            task_queue="test-queue",
        )
        assert result["status"] == "completed"
```

**Success Criteria:**
- ✅ Activity registered and callable
- ✅ Workflow executes activity successfully
- ✅ Unit tests passing (mocked activity)
- ✅ Integration tests passing (time-skipping env)
- ✅ Replay test passing (if existing workflow)

**Quick Win:** Automates Gap 5.4 pattern - saves 15-20 min per workflow

---

### 2.3 /neo4j-migration

**Description:** Create Neo4j schema migration with rollback

**Workflow Steps:**
1. **Schema Design (3 min)**
   - Analyze requested schema change (node, relationship, constraint)
   - Design Cypher statements (CREATE, ALTER, DROP)
   - Plan rollback strategy

2. **Migration File (2 min)**
   - Create migration in `migrations/neo4j/V{version}__{description}.cypher`
   - Add forward migration (up)
   - Add rollback migration (down) in comments

3. **Validation (3 min)**
   - Run migration in dev Neo4j instance
   - Validate schema changes (SHOW CONSTRAINTS, SHOW INDEXES)
   - Test rollback
   - Seed test data to validate

4. **Documentation (2 min)**
   - Update `docs/guides/NEO4J_SCHEMA.md`
   - Document new labels/relationships
   - Add example queries

**Template Files Created:**
```cypher
// migrations/neo4j/V001__{description}.cypher
// Forward migration
CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
FOR (n:{Label})
REQUIRE n.{property} IS UNIQUE;

CREATE INDEX {index_name} IF NOT EXISTS
FOR (n:{Label})
ON (n.{property});

// Rollback (run manually if needed):
// DROP CONSTRAINT {constraint_name} IF EXISTS;
// DROP INDEX {index_name} IF EXISTS;
```

**Success Criteria:**
- ✅ Migration runs without errors
- ✅ Constraints/indexes created
- ✅ Rollback tested successfully
- ✅ Sample queries validated
- ✅ Documentation updated

**Quick Win:** Saves 10-15 min per migration, ensures rollback plan exists

---

### 2.4 /add-websocket-event ⚡

**Description:** Add NATS event type + publisher + subscriber + tests

**Workflow Steps:**
1. **Event Definition (2 min)**
   - Define event type in `event_types.go` or `events.py`
   - Add event schema (timestamp, user_id, metadata)
   - Document event purpose

2. **Publisher (3 min)**
   - Add publish method to `event_publisher.go`
   - Wire to appropriate service (auth, graph, sync)
   - Add token masking if sensitive data

3. **Subscriber (3 min)**
   - Create NATS consumer in `nats.go` or `nats_service.py`
   - Add message handler
   - Wire to WebSocket broadcast or service logic

4. **Testing (4 min)**
   - Unit test: Publisher creates correct event
   - Integration test: Pub/sub round-trip
   - E2E test: WebSocket receives event

**Template Files Created:**
```go
// backend/internal/auth/event_publisher.go
func (p *EventPublisher) Publish{EventName}(ctx context.Context, data {EventData}) error {
    event := Event{
        Type:      "{event_type}",
        Timestamp: time.Now(),
        UserID:    data.UserID,
        Metadata:  data.Metadata,
    }
    return p.publish(ctx, "events.{domain}.{event_type}", event)
}

// backend/internal/nats/nats.go
func (n *NATSClient) Subscribe{EventName}(handler func(Event)) error {
    _, err := n.js.Subscribe("events.{domain}.{event_type}", func(msg *nats.Msg) {
        var event Event
        json.Unmarshal(msg.Data, &event)
        handler(event)
        msg.Ack()
    }, nats.Durable("{event_type}-consumer"))
    return err
}

// tests/backend/internal/nats/event_test.go
func TestPublish{EventName}(t *testing.T) {
    // Test publisher
}
```

**Success Criteria:**
- ✅ Event published successfully
- ✅ Subscriber receives event
- ✅ WebSocket client receives event (if wired)
- ✅ Tests passing (unit + integration)
- ✅ Token masking validated (if sensitive)

**Quick Win:** Automates Phase 5.2 OAuth event pattern - saves 15 min per event type

---

### 2.5 /performance-audit

**Description:** Profile application, identify bottlenecks, generate report

**Workflow Steps:**
1. **Baseline Metrics (3 min)**
   - Run Lighthouse on key pages (dashboard, graph)
   - Run k6 load test (100 VU, 1 min duration)
   - Capture database slow query log (queries >100ms)
   - Profile Go backend (pprof CPU/memory)

2. **Analysis (5 min)**
   - Identify top 5 bottlenecks (LCP, API latency, DB queries)
   - Classify: Frontend, backend, database, network
   - Calculate impact: Seconds saved if optimized

3. **Recommendations (5 min)**
   - Propose optimizations with effort estimates
   - Prioritize by ROI (high impact, low effort first)
   - Create tasks for top 3 optimizations

4. **Report Generation (2 min)**
   - Generate markdown report in `docs/reports/PERFORMANCE_AUDIT_{date}.md`
   - Include metrics, bottlenecks, recommendations
   - Create GitHub issues for optimizations

**Template Report:**
```markdown
# Performance Audit - {Date}

## Baseline Metrics
- **LCP:** {value}s (target: <2.5s)
- **FID:** {value}ms (target: <100ms)
- **API p95:** {value}ms (target: <500ms)
- **DB slow queries:** {count} queries >100ms

## Top 5 Bottlenecks
1. **{Bottleneck}**: {impact}s delay, {category}
   - Recommendation: {solution}
   - Effort: {low/medium/high}
   - ROI: {high/medium/low}

## Action Items
- [ ] #{issue_number}: {optimization_task}

## Load Test Results
- Requests: {total}
- Success rate: {percent}%
- p95 latency: {value}ms
```

**Success Criteria:**
- ✅ Baseline metrics captured
- ✅ Bottlenecks identified and prioritized
- ✅ Report generated
- ✅ GitHub issues created for top optimizations

**Quick Win:** Saves 30-40 min manual profiling, provides actionable report

---

### 2.6 /add-api-endpoint

**Description:** Create REST API endpoint with handler, tests, OpenAPI docs

**Workflow Steps:**
1. **API Design (3 min)**
   - Define endpoint: method, path, params, response
   - Design request/response schemas
   - Plan error responses

2. **Implementation (5 min)**
   - Create handler in `backend/internal/handlers/**`
   - Wire to router in `routes.go`
   - Add validation, error handling

3. **Testing (5 min)**
   - Unit test: Handler logic
   - Integration test: HTTP request/response
   - MSW mock for frontend tests

4. **Documentation (2 min)**
   - Update OpenAPI spec (`openapi.yaml`)
   - Generate TypeScript client types
   - Update API documentation

**Template Files Created:**
```go
// backend/internal/handlers/{domain}_handler.go
func (h *{Domain}Handler) Handle{Action}(c *fiber.Ctx) error {
    var req {Action}Request
    if err := c.BodyParser(&req); err != nil {
        return fiber.NewError(fiber.StatusBadRequest, "Invalid request")
    }

    result, err := h.service.{Action}(c.Context(), req)
    if err != nil {
        return err
    }

    return c.JSON(result)
}

// tests/backend/internal/handlers/{domain}_handler_test.go
func TestHandle{Action}(t *testing.T) {
    // Test handler
}

// frontend/apps/web/src/__tests__/mocks/handlers.ts
export const {domain}Handlers = [
  http.{method}('/api/v1/{path}', () => {
    return HttpResponse.json({ /* mock response */ })
  }),
]
```

**Success Criteria:**
- ✅ Endpoint accessible via HTTP
- ✅ Request validation working
- ✅ Error responses correct (4xx, 5xx)
- ✅ Tests passing (unit + integration)
- ✅ OpenAPI docs updated
- ✅ MSW mock created

**Quick Win:** Automates Gap 5.6 API endpoint pattern - saves 20 min per endpoint

---

### 2.7 /add-e2e-test

**Description:** Create Playwright E2E test for critical user flow

**Workflow Steps:**
1. **Flow Analysis (2 min)**
   - Analyze user flow (e.g., "login → create project → view graph")
   - Identify key assertions (page navigation, element visibility, data)
   - Plan test data setup

2. **Test Implementation (6 min)**
   - Create test file in `frontend/apps/web/e2e/{flow}.spec.ts`
   - Set up test data (API calls, fixtures)
   - Implement test steps with assertions
   - Add accessibility checks (`toPassAxe()`)

3. **Visual Regression (2 min)**
   - Add screenshot assertions for key states
   - Configure viewport sizes (desktop, tablet, mobile)
   - Set pixel tolerance (2%)

4. **CI Integration (2 min)**
   - Add test to CI workflow (if new critical path)
   - Document test in `docs/checklists/E2E_TEST_COVERAGE.md`

**Template Files Created:**
```typescript
// frontend/apps/web/e2e/{flow}.spec.ts
import { test, expect } from '@playwright/test';

test.describe('{Flow} E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Setup test data
  });

  test('should complete {flow} successfully', async ({ page }) => {
    // Step 1: Navigate
    await page.goto('/');

    // Step 2: Interact
    await page.click('button[data-testid="{action}"]');
    await expect(page.locator('h1')).toContainText('{expected}');

    // Step 3: Verify accessibility
    await expect(page).toPassAxe();

    // Step 4: Visual regression
    await expect(page).toHaveScreenshot('{flow}-final.png', {
      maxDiffPixelRatio: 0.02,
    });
  });
});
```

**Success Criteria:**
- ✅ E2E test passing
- ✅ Accessibility checks passing
- ✅ Visual regression baseline captured
- ✅ Test documented in coverage checklist

**Quick Win:** Automates Gap 5.5 E2E test pattern - saves 15-20 min per flow

---

### 2.8 /fix-msw-setup ⚡

**Description:** Diagnose and fix MSW (Mock Service Worker) setup issues

**Workflow Steps:**
1. **Diagnosis (2 min)**
   - Check MSW server initialization in `setup.ts`
   - Verify handler imports and registration
   - Test MSW lifecycle (start, reset, close)
   - Check for ESM/CommonJS compatibility issues

2. **Fix Application (3 min)**
   - Move router mocks to `setup.ts` if in test files
   - Add try-catch for graceful fallback
   - Ensure lazy initialization pattern
   - Fix lifecycle order: beforeAll → afterEach → afterAll

3. **Validation (2 min)**
   - Run affected tests
   - Verify MSW handlers intercepting requests
   - Check no errors in test output

4. **Documentation (1 min)**
   - Update `docs/guides/MSW_SETUP_GUIDE.md` if new pattern
   - Add comments explaining fix

**Template Fix:**
```typescript
// frontend/apps/web/src/__tests__/setup.ts
import { server } from './mocks/server';

// Router mocks MUST be here (hoisting requirement)
vi.mock('@tanstack/react-router', () => ({
  // Mock router
}));

// MSW lifecycle with error handling
beforeAll(() => {
  try {
    server.listen({ onUnhandledRequest: 'warn' });
  } catch (error) {
    console.warn('MSW server failed to start:', error);
    // Graceful fallback - tests run without HTTP mocking
  }
});

afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**Success Criteria:**
- ✅ MSW server starting without errors
- ✅ Handlers intercepting requests
- ✅ Tests passing that require MSW
- ✅ No hoisting errors

**Quick Win:** Critical for Session 6 MSW blocker - saves 30+ min debugging

---

### 2.9 /add-cypher-query

**Description:** Create optimized Neo4j Cypher query with profiling

**Workflow Steps:**
1. **Requirement Analysis (2 min)**
   - Understand query goal (e.g., "find all test cases linked to requirement")
   - Identify nodes, relationships, filters
   - Plan return data

2. **Query Development (5 min)**
   - Write Cypher query with best practices
   - Add parameters for reusability
   - Test in cypher-shell or Neo4j Browser

3. **Optimization (3 min)**
   - Run EXPLAIN to see query plan
   - Add indexes if missing (CREATE INDEX)
   - Rewrite for early filtering, low cardinality
   - Run PROFILE to validate improvement

4. **Integration (3 min)**
   - Add query to service (Go or Python)
   - Add integration test
   - Document query purpose and performance

**Template Files Created:**
```cypher
// Query with optimization comments
MATCH (r:Requirement {id: $requirementId})
MATCH (r)-[:TRACED_TO]->(tc:TestCase)
WHERE tc.status = 'active'  // Early filtering
WITH tc
MATCH (tc)-[:EXECUTED_IN]->(tr:TestRun)
WHERE tr.date >= $startDate
RETURN tc.id, tc.name, collect(tr) as runs
ORDER BY tc.name
LIMIT 100  // Prevent unbounded results
```

```go
// backend/internal/neo4j/trace_queries.go
func (r *TraceRepository) GetLinkedTestCases(ctx context.Context, requirementID string) ([]*TestCase, error) {
    query := `
        MATCH (r:Requirement {id: $requirementId})
        MATCH (r)-[:TRACED_TO]->(tc:TestCase)
        WHERE tc.status = 'active'
        RETURN tc
    `

    result, err := r.session.Run(ctx, query, map[string]any{
        "requirementId": requirementID,
    })
    // ...
}
```

**Success Criteria:**
- ✅ Query returns correct results
- ✅ PROFILE shows low db hits (<1000 for typical case)
- ✅ Indexes exist for queried properties
- ✅ Query parameterized (no SQL injection equivalent)
- ✅ Integration test passing

**Quick Win:** Saves 15-20 min per query with optimization built-in

---

### 2.10 /add-oauth-handler

**Description:** Add OAuth provider with state tokens, callback, session

**Workflow Steps:**
1. **Provider Configuration (3 min)**
   - Add provider config to `.env` (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
   - Register provider in `oauth_providers.go`
   - Document provider-specific scopes

2. **Authorization Flow (4 min)**
   - Add `/auth/{provider}` endpoint (generates state token, redirects)
   - Implement state token generation (32 bytes crypto-random)
   - Store state in Redis with 10 min TTL

3. **Callback Handler (5 min)**
   - Add `/auth/{provider}/callback` endpoint
   - Validate state token (timing-safe comparison)
   - Exchange code for access token (HTTP POST to provider)
   - Create user + session (PostgreSQL + Neo4j)

4. **Testing (4 min)**
   - Mock OAuth provider (httptest)
   - Test authorization flow (redirect, state generation)
   - Test callback (token exchange, session creation)
   - Test error cases (invalid state, expired code)

**Template Files Created:**
```go
// backend/internal/auth/oauth_handler.go
func (h *OAuthHandler) Handle{Provider}Login(c *fiber.Ctx) error {
    state, err := h.stateManager.GenerateState(c.Context())
    if err != nil {
        return err
    }

    redirectURL := fmt.Sprintf(
        "https://{provider}.com/oauth/authorize?client_id=%s&redirect_uri=%s&state=%s&scope=%s",
        h.config.{Provider}ClientID,
        h.config.RedirectURI,
        state,
        "{scopes}",
    )

    return c.Redirect(redirectURL)
}

func (h *OAuthHandler) Handle{Provider}Callback(c *fiber.Ctx) error {
    code := c.Query("code")
    state := c.Query("state")

    // Validate state
    if !h.stateManager.ValidateState(c.Context(), state) {
        return fiber.NewError(fiber.StatusBadRequest, "Invalid state")
    }

    // Exchange code for token
    token, err := h.exchangeCodeForToken(c.Context(), code)
    // ...

    // Create session
    session, err := h.sessionService.CreateSession(c.Context(), user, token)
    // ...

    return c.JSON(session)
}
```

**Success Criteria:**
- ✅ Authorization flow redirects correctly
- ✅ State token validated (timing-safe)
- ✅ Token exchange successful
- ✅ Session created (PostgreSQL + Neo4j)
- ✅ Tests passing (unit + integration)

**Quick Win:** Automates Phase 4.1 OAuth pattern - saves 30-40 min per provider

---

### 2.11 /add-temporal-test

**Description:** Create comprehensive Temporal workflow test (unit + integration + replay)

**Workflow Steps:**
1. **Unit Test (3 min)**
   - Create test file in `tests/unit/workflows/`
   - Mock activities with pytest fixtures
   - Test workflow logic in isolation

2. **Integration Test (4 min)**
   - Create test in `tests/integration/workflows/`
   - Use `WorkflowEnvironment.start_time_skipping()`
   - Test full workflow execution with real activities
   - Validate time-skipping (sleep, schedule)

3. **Replay Test (3 min)**
   - Export workflow event history
   - Create replay test
   - Validate backward compatibility

4. **Error Scenarios (3 min)**
   - Test activity failures (retry, timeout)
   - Test workflow cancellation
   - Test compensation logic (saga pattern)

**Template Files Created:**
```python
# tests/unit/workflows/test_{workflow}_unit.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_activity():
    return AsyncMock(return_value={"status": "success"})

@pytest.mark.asyncio
async def test_{workflow}_unit(mock_activity):
    # Test workflow with mocked activity
    pass

# tests/integration/workflows/test_{workflow}_integration.py
from temporalio.testing import WorkflowEnvironment

@pytest.mark.asyncio
async def test_{workflow}_integration():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Register activities
        worker = Worker(
            env.client,
            task_queue="test-queue",
            workflows=[{Workflow}],
            activities=[{activities}],
        )

        async with worker:
            result = await env.client.execute_workflow(
                {Workflow}.run,
                {params},
                id="{workflow}-test",
                task_queue="test-queue",
            )

            assert result["status"] == "completed"

# tests/integration/workflows/test_{workflow}_replay.py
@pytest.mark.asyncio
async def test_{workflow}_replay():
    # Load event history
    history = load_history("{workflow}-history.json")

    # Replay workflow
    await Replayer(workflows=[{Workflow}]).replay_workflow(history)
```

**Success Criteria:**
- ✅ Unit tests passing (mocked activities)
- ✅ Integration tests passing (time-skipping)
- ✅ Replay tests passing (backward compatibility)
- ✅ Error scenarios tested (retry, cancel, compensation)

**Quick Win:** Comprehensive test coverage for Gap 5.4 Temporal workflows

---

### 2.12 /add-performance-test

**Description:** Create k6 load test for API endpoint or user flow

**Workflow Steps:**
1. **Test Design (3 min)**
   - Define load profile (VUs, duration, ramp-up)
   - Identify endpoints/flows to test
   - Set performance targets (p95 < 500ms)

2. **Script Creation (5 min)**
   - Create k6 script in `load-tests/{test-name}.js`
   - Add test data (realistic payloads)
   - Add checks (status 200, response time)

3. **Execution (2 min)**
   - Run test locally: `k6 run {script}`
   - Analyze results (p95, error rate, throughput)
   - Identify bottlenecks

4. **CI Integration (3 min)**
   - Add to CI workflow (nightly or on-demand)
   - Set thresholds (fail if p95 > 500ms)
   - Store results in `load-tests/results/`

**Template Files Created:**
```javascript
// load-tests/api-{endpoint}.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp-up
    { duration: '3m', target: 100 }, // Steady
    { duration: '1m', target: 0 },   // Ramp-down
  ],
  thresholds: {
    'http_req_duration{p(95)}': ['<500'], // 95% < 500ms
    'http_req_failed': ['<0.01'],         // <1% errors
  },
};

export default function () {
  const payload = JSON.stringify({
    // Request body
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.API_TOKEN}`,
    },
  };

  const res = http.post('http://localhost:8080/api/v1/{endpoint}', payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

**Success Criteria:**
- ✅ Test runs successfully
- ✅ p95 latency meets target
- ✅ Error rate < 1%
- ✅ Results stored for comparison

**Quick Win:** Provides baseline for performance regression detection

---

## 3. Project Hooks (4 Quality Gates)

### 3.1 Graph Performance Gate

**Trigger:** On commit/push to files in `frontend/apps/web/src/components/graph/**` or `lib/gpu*.ts`

**Checks:**
1. **FPS Threshold:** Run Playwright perf test, ensure FPS ≥ 30 for 10k nodes
2. **Layout Time:** GPU layout <100ms for 10k nodes, <5s for 100k nodes
3. **Memory Usage:** <500MB heap for 10k nodes, no memory leaks (3 runs stable)

**Implementation:**
```bash
#!/bin/bash
# .git/hooks/graph-performance-gate.sh

echo "Running graph performance gate..."

# Run performance test
bun --cwd frontend/apps/web test:perf -- sigma-performance.perf.spec.ts

# Extract metrics from test output
FPS=$(grep "FPS:" test-results/perf.txt | awk '{print $2}')
LAYOUT_TIME=$(grep "Layout time:" test-results/perf.txt | awk '{print $3}')
MEMORY=$(grep "Memory usage:" test-results/perf.txt | awk '{print $3}')

# Check thresholds
if (( $(echo "$FPS < 30" | bc -l) )); then
  echo "❌ Graph performance gate FAILED: FPS $FPS < 30"
  exit 1
fi

if (( $(echo "$LAYOUT_TIME > 100" | bc -l) )); then
  echo "❌ Graph performance gate FAILED: Layout time $LAYOUT_TIME ms > 100ms"
  exit 1
fi

if (( $(echo "$MEMORY > 500" | bc -l) )); then
  echo "⚠️  Warning: Memory usage $MEMORY MB > 500MB"
fi

echo "✅ Graph performance gate PASSED"
```

**Failure Handling:**
- Block commit if FPS < 30 or layout time > 100ms
- Warn if memory > 500MB (soft limit)
- Provide actionable message: "Consider GPU optimization or LOD tuning"

**Quick Win:** Prevents performance regressions on critical graph features

---

### 3.2 Neo4j Cypher Complexity Gate

**Trigger:** On commit/push to files with `.cypher` or `*neo4j*.go` or `*neo4j*.py`

**Checks:**
1. **EXPLAIN Analysis:** No CartesianProduct, NodeByLabelScan on large labels
2. **Query Length:** <100 lines per query (encourage decomposition)
3. **Index Coverage:** All queried Label+property combinations have indexes
4. **Variable-Length Bound:** All `[:*]` patterns have upper bound

**Implementation:**
```bash
#!/bin/bash
# .git/hooks/cypher-complexity-gate.sh

echo "Running Cypher complexity gate..."

# Find all Cypher queries in changed files
CHANGED_FILES=$(git diff --cached --name-only | grep -E '\.(go|py|cypher)$')

for file in $CHANGED_FILES; do
  # Extract Cypher queries (basic regex, can be improved)
  QUERIES=$(grep -Eo 'MATCH.*RETURN' "$file" || true)

  while read -r query; do
    # Check for CartesianProduct anti-pattern
    if echo "$query" | grep -qE 'MATCH.*MATCH.*WHERE'; then
      echo "⚠️  Warning: Potential CartesianProduct in $file"
      echo "  Query: $query"
    fi

    # Check for unbounded variable-length
    if echo "$query" | grep -qE '\[\*\]'; then
      echo "❌ Cypher gate FAILED: Unbounded variable-length pattern in $file"
      echo "  Query: $query"
      echo "  Fix: Add upper bound, e.g., [:*1..5]"
      exit 1
    fi

    # Check query length (line count)
    LINE_COUNT=$(echo "$query" | wc -l | tr -d ' ')
    if (( LINE_COUNT > 100 )); then
      echo "⚠️  Warning: Long query ($LINE_COUNT lines) in $file"
    fi
  done <<< "$QUERIES"
done

echo "✅ Cypher complexity gate PASSED"
```

**Failure Handling:**
- Block commit if unbounded variable-length pattern found
- Warn if CartesianProduct or long query detected
- Provide fix suggestion: "Add upper bound [:*1..5] or create intermediate WITH"

**Quick Win:** Prevents slow Cypher queries from entering codebase

---

### 3.3 WebSocket Event Schema Gate

**Trigger:** On commit/push to files in `event_publisher.go`, `events.py`, `websocket/**`

**Checks:**
1. **Schema Validation:** All events have `type`, `timestamp`, `user_id`
2. **Token Masking:** No full tokens in event payloads (check for `token:`, `secret:`)
3. **Event Documentation:** Event type listed in `docs/reference/WEBSOCKET_EVENTS.md`

**Implementation:**
```bash
#!/bin/bash
# .git/hooks/websocket-event-gate.sh

echo "Running WebSocket event schema gate..."

CHANGED_FILES=$(git diff --cached --name-only | grep -E '(event_publisher|events\.py|websocket)')

for file in $CHANGED_FILES; do
  # Check for token leakage
  if grep -qE '(token|secret|password).*:' "$file"; then
    echo "❌ WebSocket event gate FAILED: Potential sensitive data in $file"
    echo "  Found: $(grep -E '(token|secret|password).*:' "$file")"
    echo "  Fix: Mask tokens (first 4 + last 4 chars only)"
    exit 1
  fi

  # Check for required event fields
  EVENT_TYPES=$(grep -oE 'Type:.*"[^"]*"' "$file" | cut -d'"' -f2)
  for event_type in $EVENT_TYPES; do
    if ! grep -q "$event_type" docs/reference/WEBSOCKET_EVENTS.md; then
      echo "⚠️  Warning: Event type '$event_type' not documented"
      echo "  Add to docs/reference/WEBSOCKET_EVENTS.md"
    fi
  done
done

echo "✅ WebSocket event schema gate PASSED"
```

**Failure Handling:**
- Block commit if unmasked tokens found
- Warn if event type not documented
- Provide fix suggestion: "Mask using first4+last4 pattern"

**Quick Win:** Prevents sensitive data leakage in WebSocket events (Phase 5.2)

---

### 3.4 Temporal Workflow Versioning Gate

**Trigger:** On commit/push to files in `workflows/**`

**Checks:**
1. **Backward Compatibility:** Modified workflows use `workflow.get_version()` for breaking changes
2. **Replay Test:** Workflow passes replay test with previous event history
3. **Activity Signature:** Activity signature changes are additive (new params optional)

**Implementation:**
```bash
#!/bin/bash
# .git/hooks/temporal-versioning-gate.sh

echo "Running Temporal workflow versioning gate..."

CHANGED_WORKFLOWS=$(git diff --cached --name-only | grep 'workflows/.*\.py')

for file in $CHANGED_WORKFLOWS; do
  # Check if workflow.defn exists in file (modified workflow)
  if git show HEAD:"$file" 2>/dev/null | grep -q '@workflow.defn'; then
    # Workflow exists in HEAD, check for versioning
    if ! grep -q 'workflow.get_version' "$file"; then
      echo "⚠️  Warning: Modified workflow without versioning in $file"
      echo "  Consider using workflow.get_version() for backward compatibility"
    fi

    # Run replay test (if exists)
    REPLAY_TEST="tests/integration/workflows/test_$(basename "$file" .py)_replay.py"
    if [ -f "$REPLAY_TEST" ]; then
      echo "Running replay test: $REPLAY_TEST"
      pytest "$REPLAY_TEST" || {
        echo "❌ Temporal versioning gate FAILED: Replay test failed"
        exit 1
      }
    fi
  fi
done

echo "✅ Temporal workflow versioning gate PASSED"
```

**Failure Handling:**
- Block commit if replay test fails
- Warn if versioning missing on modified workflow
- Provide fix suggestion: "Add workflow.get_version() before breaking change"

**Quick Win:** Prevents workflow versioning issues (Gap 5.4)

---

## 4. Integration Plan

### 4.1 Integration with Existing BMAD Framework

**Current BMAD Agents (4):**
1. BMad Master (Team Lead)
2. PM (Product Manager)
3. Analyst (Business Analyst)
4. Architect (Solution Architect)

**Current BMAD Skills (5+):**
- /commit, /review-pr, /plan, /research, etc.

**Integration Strategy:**

#### Phase 1: Domain Agents (Week 1-2)
- Install 10 domain agents as `.claude/commands/trace-{agent-name}`
- Auto-invoke configuration in `config.yaml` (trigger patterns)
- Test each agent with sample tasks from existing memory (Gap 5.1-5.8)

#### Phase 2: Project Skills (Week 3-4)
- Install 12 project skills in `.claude/commands/workflows/`
- Create skill documentation in `docs/reference/TRACE_SKILLS.md`
- Train agents to delegate to skills for common patterns

#### Phase 3: Project Hooks (Week 5)
- Install 4 hooks in `.git/hooks/` with execute permissions
- Configure thresholds in `.github/workflows/quality-gates.yml`
- Test hooks with sample commits (should block/warn correctly)

#### Phase 4: Integration Testing (Week 6)
- Full workflow: User request → Agent delegates to skill → Hook validates
- Example: "Add graph clustering" → graph-viz-expert → /add-graph-feature → graph-performance-gate
- Measure time savings vs manual implementation

### 4.2 Deployment Timeline

| Week | Phase | Deliverables | Validation |
|------|-------|--------------|------------|
| 1-2 | Domain Agents | 10 agents installed, auto-invoke working | Each agent completes sample task |
| 3-4 | Project Skills | 12 skills installed, documentation complete | Each skill runs end-to-end |
| 5 | Project Hooks | 4 hooks active, thresholds tuned | Hooks block/warn correctly |
| 6 | Integration | Full workflow tested, time savings measured | 50%+ time reduction on common tasks |

### 4.3 Maintenance Plan

**Agent Updates:**
- Review agent performance quarterly
- Update system prompts based on new patterns in memory
- Add new agents as domains emerge (e.g., ML/AI agent if features added)

**Skill Updates:**
- Version skills (v1, v2) for breaking changes
- Deprecate outdated skills with 1-month notice
- Document skill changelog in `docs/reference/TRACE_SKILLS_CHANGELOG.md`

**Hook Updates:**
- Tune thresholds based on real performance data
- Add new hooks as quality issues emerge
- Document hook changes in commit messages

---

## 5. Quick Wins (8 Components)

### Immediate Value (Can Deploy Today)

1. **Graph Visualization Expert** ⚡
   - Value: Automates Gap 5.1, 5.7 patterns
   - Time Savings: 30-40 min per graph feature
   - Deployment: 15 min (install agent, test with GPU layout task)

2. **API Testing Specialist** ⚡
   - Value: Fixes MSW setup issues (Session 6 blocker)
   - Time Savings: 30+ min debugging MSW issues
   - Deployment: 10 min (install agent, test with Gap 5.3)

3. **Accessibility Testing Expert** ⚡
   - Value: Automates Gap 5.5 E2E accessibility tests
   - Time Savings: 20 min per test
   - Deployment: 10 min (install agent, test with sample flow)

4. **Performance Optimization Specialist** ⚡
   - Value: Identifies bottlenecks proactively
   - Time Savings: 40 min per audit
   - Deployment: 20 min (install agent, run baseline audit)

5. **/add-graph-feature** ⚡
   - Value: End-to-end graph feature workflow
   - Time Savings: 20-30 min per feature
   - Deployment: 5 min (install skill, test with "add node clustering")

6. **/add-websocket-event** ⚡
   - Value: Automates Phase 5.2 OAuth event pattern
   - Time Savings: 15 min per event type
   - Deployment: 5 min (install skill, test with sample event)

7. **/fix-msw-setup** ⚡
   - Value: Critical for Session 6 MSW blocker
   - Time Savings: 30+ min debugging
   - Deployment: 5 min (install skill, test with current setup)

8. **Graph Performance Gate** ⚡
   - Value: Prevents performance regressions
   - Time Savings: Avoids 1-2 hour rollback + fix cycles
   - Deployment: 10 min (install hook, test with sample commit)

**Total Quick Win Time Savings:** 3-4 hours saved per week

---

## 6. Research Sources

This specification is informed by:

**Domain Research:**
- [Sigma.js Documentation](https://www.sigmajs.org/docs/) - WebGL graph rendering patterns
- [Temporal Python SDK Testing Guide](https://docs.temporal.io/develop/python/testing-suite) - Time-skipping test environment
- [Neo4j Cypher Manual: Query Tuning](https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/query-tuning/) - Optimization patterns
- [NATS JetStream Documentation](https://docs.nats.io/jetstream) - Event streaming best practices
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility criteria

**Performance Patterns:**
- [Big Data Visualization using Sigma.js](https://www.rapidops.com/blog/big-data-visualization-using-sigma-js/) - Batch updates, LOD switching
- [Neo4j Performance Improvements](https://neo4j.com/blog/developer/cypher-performance-neo4j-5/) - Block format, cardinality optimization
- [Temporal Workflow Best Practices](https://learn.temporal.io/tutorials/python/background-check/durable-execution/) - Idempotent activities, versioning

**Project Context:**
- Session 6 memory (MSW GraphQL ESM/CommonJS blocker resolution)
- Phase 5 execution memory (multi-wave parallelization, GPU compute, OAuth events)
- patterns.md (coverage regression, agent coordination anti-patterns)

---

## 7. Next Steps

1. **Review & Approve Specification**
   - Team lead reviews 26 components
   - Prioritize quick wins (8 components)
   - Approve integration plan

2. **Pilot Deployment (Week 1)**
   - Install 3 quick win agents: Graph Viz, API Testing, Performance
   - Install 3 quick win skills: /add-graph-feature, /fix-msw-setup, /add-websocket-event
   - Install 1 hook: Graph Performance Gate
   - Measure time savings on real tasks

3. **Full Rollout (Week 2-6)**
   - Follow integration plan timeline
   - Document lessons learned
   - Tune thresholds based on real data

4. **Continuous Improvement**
   - Review agent performance quarterly
   - Add new components as patterns emerge
   - Update documentation with new learnings

---

**Status:** ✅ COMPLETE - Ready for Team Lead Review
**Next Action:** Pilot deployment of 8 quick win components
