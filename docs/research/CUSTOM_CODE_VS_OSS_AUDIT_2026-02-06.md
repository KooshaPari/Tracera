# Custom Code vs Off-the-Shelf Audit (OSS First)

**Date:** 2026-02-06  
**Status:** Draft  
**Audience:** Engineer agents implementing hardening, capability extensions, and platform primitives

## Scope

This audit inventories the repo's major custom implementations and compares them to existing OSS libraries, tools, and reference repos that solve the same classes of problems.

This is intended to reduce bespoke maintenance, increase correctness and operability, and align implementation strategy with widely used, well tested approaches.

Out of scope for this document:

- Frontend runtime freeze debugging and transient client errors.

## Methodology

1. Inventory: computed approximate LoC by top level module for Go (`backend/internal/*`), Python (`src/tracertm/*`), and shared frontend packages (`frontend/packages/*`).
2. Evidence: read package READMEs where present and inspected representative implementation files for commodity subsystems.
3. Comparison: mapped each commodity subsystem to OSS alternatives and to common implementation patterns used in production systems.
4. Governance constraints applied as requirements: strict fail loud behavior, explicit modes, OSS and local first, no silent fallbacks.

## Inventory Snapshot (Approx LoC)

### Go `backend/internal/*` (top by LoC)

| Package | Approx LoC | Notes |
|---|---:|---|
| `services` | 30014 | Domain services. Mostly expected to remain custom. |
| `handlers` | 23919 | API layer. Mostly expected to remain custom. |
| `equivalence` | 16371 | Domain engine. Expected to remain custom. |
| `codeindex` | 10287 | Commodity parsing and indexing plus domain linking. Split candidate. |
| `graph` | 7964 | Neo4j integration plus algorithms and caching. Split candidate. |
| `agents` | 7141 | Custom coordinator and task queue. Strong off-the-shelf overlap. |
| `db` | 7129 | Data access and migrations. Commodity heavy. |
| `middleware` | 7124 | Cross cutting concerns. Commodity heavy. |
| `cache` | 6193 | Redis caching abstraction. Commodity heavy. |
| `search` | 5697 | Search indexing + query plumbing. Mixed. |
| `websocket` | 5603 | Real time hub, presence, backpressure. Commodity heavy but feature rich. |
| `docindex` | 4813 | Markdown parsing + chunking + linking. Mixed. |
| `embeddings` | 4685 | Provider clients + batching + backoff. Commodity heavy. |
| `events` | 4165 | Event store + replay. Mixed. |
| `nats` | 3871 | JetStream wrapper + publisher. Commodity heavy. |
| `temporal` | 1545 | Temporal SDK wrapper + workflows. Commodity heavy. |
| `ratelimit` | 1306 | Sliding window + throttler (Redis + Lua). Commodity heavy. |
| `resilience` | 1213 | Retry + circuit breaker wrapper. Commodity heavy. |

### Python `src/tracertm/*` (top by LoC)

| Module | Approx LoC | Notes |
|---|---:|---|
| `api` | 26577 | FastAPI app and handlers. Mostly expected to remain custom. |
| `services` | 25608 | Domain services. Mostly expected to remain custom. |
| `cli` | 21863 | CLI. Mostly expected to remain custom. |
| `mcp` | 16946 | MCP adapters and tooling. Mixed. |
| `repositories` | 8862 | Data access. Commodity heavy. |
| `storage` | 4791 | Storage and persistence helpers. Commodity heavy. |
| `workflows` | 2069 | Temporal workflows and worker. Commodity heavy. |
| `infrastructure` | 725 | NATS client, event bus, feature flags. Commodity heavy. |

### Frontend shared packages `frontend/packages/*`

| Package | Approx LoC | Notes |
|---|---:|---|
| `types` | 4517 | Mostly generated or type definitions. |
| `ui` | 3525 | UI components. Mostly expected to remain custom. |
| `env-manager` | 1004 | Commodity. |
| `api-client` | 657 | Commodity. |
| `state` | 586 | Wraps upstream state library. Likely keep thin. |

## Full Module Inventory (Top Level)

This section enumerates all top level packages in the main custom code surfaces. It is an inventory, not a recommendation.

### Go `backend/internal/*`

| Package | Approx LoC | README Header (if present) |
|---|---:|---|
| `services` | 30014 |  |
| `handlers` | 23919 |  |
| `equivalence` | 16371 | # Equivalence Engine |
| `codeindex` | 10287 | # Code Indexing Service |
| `graph` | 7964 | # TraceRTM Graph Query System |
| `agents` | 7141 | # TraceRTM Agent Coordination System |
| `db` | 7129 |  |
| `middleware` | 7124 |  |
| `cache` | 6193 |  |
| `search` | 5697 | # TraceRTM Search Engine |
| `websocket` | 5603 | # WebSocket Real-Time System |
| `repository` | 4893 |  |
| `docindex` | 4813 | # Documentation Indexing Service (docindex) |
| `embeddings` | 4685 | # TraceRTM Embeddings Package |
| `events` | 4165 | # TraceRTM Event Sourcing & Real-Time System |
| `nats` | 3871 |  |
| `journey` | 3859 | # Journey Derivation Service |
| `database` | 3667 |  |
| `auth` | 3334 |  |
| `progress` | 3314 | # Progress Tracking Package |
| `cliproxy` | 2281 | # CLIProxy Service |
| `server` | 2167 |  |
| `storybook` | 1993 | # Storybook Component Indexer Service |
| `metrics` | 1960 | # TraceRTM Service Metrics |
| `figma` | 1882 | # Figma API Integration Service |
| `clients` | 1833 |  |
| `traceability` | 1727 |  |
| `config` | 1722 |  |
| `models` | 1559 |  |
| `temporal` | 1545 |  |
| `ratelimit` | 1306 | # Rate Limiting Package |
| `grpc` | 1265 |  |
| `infrastructure` | 1238 |  |
| `validation` | 1216 |  |
| `resilience` | 1213 | # Resilience Package |
| `adapters` | 1094 |  |
| `plugin` | 943 |  |
| `tracing` | 896 |  |
| `autoupdate` | 851 |  |
| `storage` | 825 |  |
| `health` | 716 |  |
| `oauth` | 660 |  |
| `testutil` | 636 | # Test Utilities |
| `sessions` | 571 |  |
| `env` | 567 |  |
| `preflight` | 511 |  |
| `vault` | 364 |  |
| `profiling` | 336 |  |
| `pagination` | 310 |  |
| `features` | 299 |  |
| `integration` | 281 |  |
| `realtime` | 270 |  |
| `sentry` | 260 |  |
| `uuidutil` | 222 |  |
| `tx` | 209 |  |
| `docservice` | 206 |  |
| `workflows` | 0 |  |

### Python `src/tracertm/*`

| Module | Approx LoC |
|---|---:|
| `api` | 26497 |
| `services` | 25532 |
| `cli` | 21699 |
| `mcp` | 16857 |
| `repositories` | 8767 |
| `models` | 6465 |
| `schemas` | 5660 |
| `storage` | 4695 |
| `tui` | 2379 |
| `agent` | 2200 |
| `workflows` | 2064 |
| `clients` | 1834 |
| `proto` | 858 |
| `infrastructure` | 696 |
| `config` | 659 |
| `database` | 456 |
| `observability` | 379 |
| `utils` | 316 |
| `vault` | 248 |
| `core` | 228 |
| `grpc` | 187 |
| `validation` | 70 |
| `generated` | 0 |
| `migrations` | 0 |
| `tests` | 0 |
| `v1` | 0 |

### Frontend `frontend/packages/*`

| Package | Approx LoC |
|---|---:|
| `types` | 4517 |
| `ui` | 3525 |
| `env-manager` | 1004 |
| `api-client` | 657 |
| `state` | 586 |
| `config` | 5 |

## Decision Rubric (Keep Custom vs Adopt OSS)

Use this rubric per subsystem:

| Question | If Yes | If No |
|---|---|---|
| Is the behavior a commodity (cache, rate limit, retries, OAuth, queues, parsing) with mature OSS? | Prefer OSS or keep a thin wrapper. | Custom is acceptable. |
| Is there domain specific logic that is hard to buy (equivalence, traceability, canonical linking)? | Keep custom, but isolate from commodity plumbing. | Prefer OSS. |
| Is correctness and operability a core requirement (fail loud, deterministic semantics)? | Prefer OSS with strong contracts or keep custom with hard tests. | Avoid adding new complexity. |
| Does adopting OSS add a new always on service dependency? | Only do this with an explicit mode and loud startup checks. | Lower risk. |

## Commodity Subsystems: Mapping to OSS Alternatives

This table lists high overlap areas where off-the-shelf tools can replace or constrain custom implementations.

| Subsystem | Current Custom Implementation | OSS Alternatives (libs and repos) | Recommendation | Migration Strategy (No Silent Fallbacks) |
|---|---|---|---|---|
| Config and env validation | Go: `backend/internal/config/*`, `backend/internal/env/*`; Python: `pydantic-settings` based configs; Frontend: `frontend/packages/env-manager/*` | Go: `github.com/caarlos0/env/v11`; `github.com/knadh/koanf`; `github.com/spf13/viper` | Keep strict typed config, but consider using a single env parsing library to reduce bespoke parsing edge cases. | Keep fail loud defaults; generate a config report endpoint in dev mode and ensure required vars are enforced in preflight. |
| Retry and backoff | `backend/internal/resilience/retry.go` | `github.com/cenkalti/backoff/v4`; `github.com/avast/retry-go` | Prefer direct use of a single backoff lib everywhere to avoid divergent behavior. | Keep `resilience` as a thin policy wrapper that delegates to one library; add table driven tests for retry classification. |
| Circuit breaker | `backend/internal/resilience/circuit_breaker.go` (wraps `github.com/sony/gobreaker`) | `github.com/sony/gobreaker` | Keep wrapper if it adds metrics and naming; otherwise remove and use upstream directly. | Standardize breaker configuration per dependency; expose state in `/health` and metrics. |
| Sliding window rate limit | `backend/internal/ratelimit/sliding_window.go` (Redis ZSET + Lua) | `github.com/go-redis/redis_rate/v9`; `github.com/ulule/limiter/v3` | Prefer OSS unless sliding window semantics are required for product reasons. | Replace the limiter implementation behind an interface; keep strict behavior when Redis is required and explicit mode for fail open. |
| Adaptive throttling | `backend/internal/ratelimit/throttle.go` | NATS JetStream queue consumers; Temporal task queues; `golang.org/x/sync/semaphore` (local only) | Keep custom if priority queueing and breaker integration are required. | Add contract tests for concurrency limits and priority order; surface queue depth metrics and fail loud when limits exceeded. |
| Redis cache abstraction | `backend/internal/cache/*.go` (JSON encode, tag invalidation, metrics) | `github.com/eko/gocache`; `github.com/go-redis/cache` (if adopting its semantics); `github.com/dgraph-io/ristretto` (local cache) | Keep custom only if tag invalidation and existing key taxonomy are required; otherwise migrate to gocache. | Introduce a `Cache` interface with explicit miss sentinel; make cache mode explicit and required by default. |
| Feature flags | `backend/internal/features/flags.go`; `src/tracertm/infrastructure/feature_flags.py` | OpenFeature SDKs (`github.com/open-feature/go-sdk`; `openfeature` Python SDK); `github.com/thomaspoignant/go-feature-flag` | Keep custom for now but adopt an OpenFeature shaped interface to avoid lock in. | Define a stable interface and harden preflight for the backing store; do not add a hosted flag service by default. |
| OAuth flows and token handling | `backend/internal/cliproxy/*` | `golang.org/x/oauth2`; `github.com/oauth2-proxy/oauth2-proxy` (separate service) | Use `x/oauth2` for correctness and token refresh semantics; keep proxy routing custom. | Replace manual OAuth logic with `x/oauth2` while keeping fail loud config checks; keep provider selection explicit. |
| Agent coordination and task queue | `backend/internal/agents/*` | Temporal task queues; Postgres queue libs such as River (`github.com/riverqueue/river`); Redis queue libs such as Asynq (`github.com/hibiken/asynq`); NATS JetStream work queue patterns | Strong candidate to migrate off custom queue semantics to Temporal or a Postgres-backed queue library. | Treat the coordinator API as a compatibility layer; move retries and timeouts into the chosen backend contract; keep backend selection explicit with hard preflight. |
| Event bus abstraction | `backend/internal/nats/*`; `src/tracertm/infrastructure/event_bus.py` | `nats-io/nats.go` JetStream; `github.com/ThreeDotsLabs/watermill` (messaging patterns) | Keep wrapper but standardize everything correctness critical on JetStream acks and durable consumers. | Enforce publish acks and Msg-Id where needed; create shared subscription defaults; add integration tests for redelivery and dedup. |
| Event sourcing store | `backend/internal/events/*` (Postgres store + replay) | `github.com/looplab/eventhorizon` (CQRS/ES toolkit); EventStoreDB (external service) | Keep custom if domain events and schema are tightly coupled; otherwise consider adopting a framework for projections and replay. | If staying custom: enforce idempotent replay and projection rebuild; wire to JetStream or Temporal for background consumers. |
| WebSocket hub, presence, backpressure | `backend/internal/websocket/*` | `github.com/nhooyr/websocket`; `github.com/gorilla/websocket`; `github.com/centrifugal/centrifugo` (server); `github.com/centrifugal/centrifuge` (library) | Keep custom if feature set is required; consider Centrifugo if you need proven fanout and scaling. | If adopting a server: add explicit mode, hard preflight, and an adapter layer; do not silently swap transport behavior. |
| Code parsing and indexing | `backend/internal/codeindex/parsers/*` (regex foundation) | Tree-sitter bindings (`github.com/smacker/go-tree-sitter`); SCIP toolchain (`github.com/sourcegraph/scip`; `github.com/sourcegraph/scip-go`; `github.com/sourcegraph/scip-typescript`) | Split commodity parsing and symbol extraction from domain linking. Prefer tree-sitter or SCIP for parsing. | Replace per language parsers incrementally behind a `Parser` interface; keep canonical linker and confidence scoring custom. |
| Code search | `backend/internal/codeindex/*` custom repository and query path | `github.com/sourcegraph/zoekt`; `github.com/livegrep/livegrep` | Add only if repo scale makes custom search insufficient. | Add as explicit mode; create a compatibility layer for existing API queries; keep Postgres authoritative where required. |
| Markdown parsing and doc chunking | `backend/internal/docindex/*` (goldmark + custom chunking + concept extraction) | Keep goldmark; optional splitters (`github.com/tmc/langchaingo/textsplitter`) | Keep custom linking but consider adopting a standard splitter implementation and tokenizer for deterministic chunk sizes. | Standardize chunk strategy in one place and add golden tests for chunk boundaries and extracted references. |
| Graph algorithms | `backend/internal/graph/graph.go`, `advanced_queries.go` | `gonum.org/v1/gonum/graph`; Neo4j Cypher; Neo4j GDS plugin (explicit) | Prefer Neo4j for persistence queries; prefer gonum for in memory algorithms. Avoid duplicating semantics. | Create clear boundary: what runs in Neo4j vs in memory; enforce query timeouts and max depth; require indexes and constraints at startup. |
| S3 integration | `backend/internal/storage/s3.go` | AWS SDK v2; MinIO Go SDK | Pick one client stack and delete the other to reduce drift. | Standardize on AWS SDK v2 for AWS; keep MinIO for S3 compatible endpoints only if needed; make endpoint selection explicit. |
| Figma API integration | `backend/internal/figma/*` | Go Figma clients (`github.com/torie/figma`; `github.com/alridev/figma`) | Keep custom if we require tight control over retry, rate limiting, and mapping logic. Consider using a client lib only if it is complete and maintained. | If adopting: isolate the HTTP client behind an interface; keep mapping and sync logic custom; enforce fail loud health checks. |
| Storybook component indexing | `backend/internal/storybook/*` | Storybook `stories.json` is the source; TS tooling exists but Go libs are uncommon | Keep custom. The "commodity" piece is only fetching and parsing JSON, not the indexing semantics. | Tighten schema validation, caching, and incremental reindex strategy; keep fail loud Storybook connectivity in preflight when enabled. |
| Embeddings providers | `backend/internal/embeddings/*` (VoyageAI, OpenRouter, reranking, batching) | Unofficial clients (`github.com/conneroisu/go-voyageai`; OpenRouter clients like `github.com/revrost/go-openrouter`); provider REST APIs | Keep custom provider selection and cost tracking, but consider adopting a well scoped client to reduce HTTP boilerplate. | Keep provider mode explicit; if adopting a client, wrap it to preserve strict retries, timeouts, and failure surfaces. |
| Observability plumbing | `backend/internal/metrics/*`, `backend/internal/tracing/*`, Python `tracertm/observability/*` | OpenTelemetry Collector (`open-telemetry/opentelemetry-collector-contrib`); `prometheus/client_golang` | Keep custom metrics naming and business metrics; add collector mode to simplify exporters and pipelines. | Add collector as explicit mode, fail loud when enabled but unreachable; add a smoke test exporting spans and metrics. |

## Redis-Compatible Servers (License and Fit)

This section is included because Redis is a correctness critical dependency in this repo (rate limiting, feature flags, caches). Server selection must be explicit and enforceable.

| Option | License posture | Fit For This Repo | Notes |
|---|---|---|---|
| Valkey | OSS permissive | Strong default | Redis OSS line continuation with open governance; best match for "OSS first" posture. |
| Redis | Mixed (AGPL option plus source available options depending on distro) | Strong if policy allows | Treat as a legal policy decision, not a technical one. |
| KeyDB | OSS permissive | Conditional | Consider only if you specifically need its replication or throughput model and can validate semantics. |
| Garnet | OSS permissive | Conditional | Promising, but requires explicit compatibility validation for the exact Redis command set the app uses. |
| Dragonfly | BSL 1.1 source available (not OSS) | Generally avoid for core infra | License restricts production use for competing in-memory data store services and forbids offering Dragonfly "as a Service" to third parties; current Change Date is 2029-03-01 and Change License is Apache-2.0. Only consider under an explicit opt-in mode with a compatibility harness and an org-wide license decision. |
| Kvrocks | OSS permissive | Unlikely | RocksDB backed, optimized for large keyspaces and persistence; less aligned with in memory cache and latency goals. |

## Methodology Alignment Gaps (Where We Diverge From Common Patterns)

These are not errors; they are places where our implementation strategy increases maintenance.

1. Two stacks implement overlapping infrastructure concerns (Go and Python both integrate NATS, workflows, and health). This is normal in polyglot systems, but it requires explicit ownership boundaries to avoid incompatible semantics.
2. Some commodity subsystems are fully custom while mature OSS exists (rate limiting, task queues, parsing). This is the biggest source of avoidable ongoing work.
3. Parsing and indexing: regex based parsing is an acceptable bootstrap but diverges quickly across languages; tree-sitter or SCIP style indexing reduces correctness risk.
4. Real time: custom websockets can work, but scalability and correctness often become transport semantics and backpressure edge cases. A proven server can be a faster path when scale demands it.

## Recommended Work Items (Tie Back to Plans)

These items are intended to be merged into the dependency hardening and capability extension execution plan.

| Priority | Work Item | Why | Related Plan |
|---|---|---|---|
| P0 | Standardize event publishing and consuming on JetStream acks and durable consumers | Reliability and operability with minimal new dependencies | `docs/plans/2026-02-06-dependency-hardening-execution-plan.md` |
| P0 | Make workflow execution end to end required in dev and CI when workflows are enabled | Prevent "started but never executed" workflows | `docs/plans/2026-02-06-dependency-hardening-spec.md` |
| P1 | Replace custom sliding window limiter with `redis_rate` or `limiter` unless sliding window semantics are required | Reduce custom Lua maintenance and edge cases | New task in execution plan Phase 4 |
| P1 | Decide agent coordination runtime: Temporal task queues or keep custom | Avoid duplicating queue semantics in multiple places | New task in execution plan Phase 2 |
| P1 | Split `codeindex` into commodity parsing and custom linking; adopt tree-sitter or SCIP | Improves correctness and reduces parser drift | New task in execution plan Phase 7 |
| P2 | Evaluate whether WebSocket hub should remain embedded or move to Centrifugo mode | Scaling and backpressure reliability | New task in execution plan Phase 7 |

## Appendix: Useful OSS Packages and Tools (Shortlist)

This is a curated shortlist to evaluate in this repo. Categories are based on likely ROI and alignment with governance.

| Category | Go | Python | Frontend |
|---|---|---|---|
| Needed | `golang.org/x/oauth2`; `github.com/go-redis/redis_rate/v9`; a durable queue backend choice (Temporal or River); tree-sitter binding | Temporal test patterns (`temporalio` test server usage); OpenTelemetry Collector mode wiring | CI coverage provider compatible with Bun; deterministic module resolution hygiene |
| Useful | `github.com/ulule/limiter/v3`; `github.com/eko/gocache`; `gonum.org/v1/gonum/graph`; `github.com/nhooyr/websocket`; `github.com/hibiken/asynq` (only if Redis-backed queue is chosen) | OpenFeature SDK; `aiocache` or explicit cache interfaces where needed | OpenAPI client generator if api-client is hand maintained |
| Interesting | `github.com/sourcegraph/scip-go`; `github.com/sourcegraph/zoekt`; `github.com/livegrep/livegrep`; `github.com/ThreeDotsLabs/watermill` | Hatchet server as alternative orchestrator if Temporal is not used as the universal queue | A11y and perf enforcement tooling (LHCI, axe CI) |
