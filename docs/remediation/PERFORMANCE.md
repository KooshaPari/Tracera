# Tracera Remediation: Performance (H-Perf) Plan

## Scope

- `POST /api/v1/coverage-matrix`
- `POST /api/v1/impact`
- `GET /api/v1/impact/forward/{artifact_id}`
- `GET /api/v1/impact/reverse/{artifact_id}`

## 1) Documented load ceiling (initial hard limits)

These limits are additive and reversible guardrails while no dedicated queue/batching layer exists.

- `coverage-matrix`
  - 1,000 links: immediate in-memory build (current behavior)
  - 5,000 links: soft warning with structured warning log
  - 25,000 links: hard reject with `413` and remediation guidance unless `X-Trace-Batch-Mode: true` is provided
- `impact` and Neo4j impact traversals
  - 2,000 edges: normal response expectation
  - 10,000 edges or nodes visited: route should return `202` + job token and stream/streaming follow-up is recommended (see section 2)

Implementation path for guardrails:

- enforce request-size and payload-size checks at serializer boundary;
- return explicit `429/413` with actionable message:
  - “retry with range filters, time window, or async/export mode.”

## 2) Backpressure + streaming plan for heavy endpoints

### Coverage endpoints (`coverage-matrix`, `impact`)

1. Introduce request-size quotas and token bucket-like soft throttle keyed by `(api_key, tenant_id)` in-memory now; persist to cache later.
2. Add paged/stream output path for heavy responses:
   - `POST /api/v1/coverage-matrix`:
     - if `Accept: text/event-stream` and payload exceeds soft limit, emit streamed matrix cells in deterministic batches.
   - `POST /api/v1/impact`:
     - if traversed component count exceeds soft limit, emit partial impact windows and continue-id with `next_cursor`.
3. For overload, move to asynchronous mode:
   - response `202 Accepted`, job token, and follow-up `GET /api/v1/jobs/{token}`.

### Neo4j impact traversals (`impact/forward`, `impact/reverse`)

1. Replace unbounded Cypher paths with bounded windows by default:
   - add optional `max_hops`, `max_nodes`, `after` cursor params.
2. Add query-time guard:
   - if estimated growth exceeds bound, cut off and return `206` with `truncated=true`.
3. Add server-side queueing for concurrent heavy traversals (first-in, backpressure via HTTP `Retry-After`).

## 3) Caching strategy

- Coverage matrix cache: `cache_key = sha256( sorted links + stale_after_days )`.
  - Cache TTL: 60s for development, 5m production.
- Impact cache:
  - cache per `(artifact_id, changed_artifacts, max_depth, max_hops, stale_after_days)` tuple.
  - invalidate when trace-link writes occur (artifact/link mutation endpoints).
- Query cache layering:
  - in-memory per-process cache first.
  - Redis fallback via existing `dragonfly` role in production topology.

## 4) Profiling hooks

Add low-friction hooks before deep optimization:

- CPU profiling:
  - wrap `/api/v1/coverage-matrix` and impact endpoints with optional `tracemalloc` + `cProfile` dumps behind env flag `TRACERA_PROFILE_ROUTES=1`.
  - write to `./.profiles/<route>-<ts>.json`.
- Event-loop lag and latency:
  - log `elapsed_ms` for each request in `src/tracertm/api/observability.py`.
- Query-level profiling:
  - log Cypher execution duration and returned row count around `session.run()` in
    `src/tracertm/api/handlers/impact.py`.
- Regression checks:
  - add benchmark threshold in `tests/performance/test_matrix_build_benchmark.py` for large synthetic matrices.

## 5) Implementation sequence

1. Add request-size gating (fastest, safe).
2. Add bounded pagination and `max_hops` for Neo4j endpoints.
3. Add streaming fallback for oversized coverage requests.
4. Add async job-based deferred heavy job path.
5. Add cache and profiling gating behind feature flags.

