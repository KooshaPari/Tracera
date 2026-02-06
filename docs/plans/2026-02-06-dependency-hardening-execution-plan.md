# Dependency Hardening and Capability Extensions Execution Plan (WBS and DAG)

**Date:** 2026-02-06  
**Status:** Draft  
**Primary Spec:** `docs/plans/2026-02-06-dependency-hardening-spec.md`  
**Goal:** Make dependency usage end to end correct and fail loud, then extend capabilities where it improves correctness, operability, and measurable performance.

## Deliverables

- Default dev stack starts a Temporal worker and proves workflow execution.
- Preflight and health checks validate end to end capability (not just "port open") for enabled features.
- NATS eventing is standardized on JetStream acks for critical events, with clear dedup semantics where required.
- NATS extensions are possible via explicit modes (JetStream KV and Object Store), with smoke coverage when enabled.
- Redis usage is explicit: required by default; any disabling is explicit and visible; backend selection is explicit and covered by a compatibility harness.
- Neo4j schema setup is required when enabled (indexes/constraints), with guardrails for pathological traversals; APOC and GDS are disabled by default and tests do not assume them.
- Postgres perf tooling used by gates is actually active when those gates run.
- Postgres extensions are expanded only via explicit modes (pooling and `pg_cron`), with loud preload enforcement and smoke coverage when enabled.
- CI gates match governance: required suites are gating, coverage floors are enforced, E2E projects run when required, and perf/load thresholds are not warning-only in required workflows.
- Observability can be extended via an explicit OpenTelemetry Collector mode in dev.
- Lint governance is respected: no new suppressions; existing targeted suppressions are removed via refactors.

## Related Work and Non Goals

- Frontend performance work (including the `/home` freeze) is tracked separately in `docs/plans/2026-02-01-comprehensive-performance-optimization-plan.md`.

## Change Surface (Expected Files)

This plan is designed to be implementable by subagents working in parallel. Most tasks are constrained to 1 to 3 related files.

High probability touchpoints:

- `config/process-compose.yaml`
- `config/nats-server.conf`
- `config/otel-collector.yaml` (new, if collector mode is implemented)
- `scripts/shell/postgres-if-not-running.sh`
- `scripts/shell/temporal-if-not-running.sh`
- `scripts/shell/nats-if-not-running.sh`
- `scripts/shell/readiness-*.sh` (new or updated)
- `src/tracertm/workflows/workflows.py`
- `src/tracertm/workflows/worker.py`
- `src/tracertm/services/temporal_service.py`
- `src/tracertm/api/handlers/health.py`
- `src/tracertm/preflight.py`
- `backend/internal/preflight/preflight.go`
- `backend/internal/nats/nats.go`
- `backend/internal/graph/neo4j_client.go`
- `backend/internal/graph/neo4j_init.go`
- `backend/internal/infrastructure/infrastructure.go`
- `scripts/sql/db-performance-audit.sql`
- `backend/docker-compose.test.yml` and `backend/tests/e2e/docker-compose.yml` (Neo4j plugin policy alignment)
- `.github/workflows/*.yml` (CI gate hardening)
- `frontend/**/vitest.config.ts` and `frontend/apps/web/package.json` (coverage and E2E project enforcement)

## Phased WBS (Work Breakdown Structure)

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| 1 | P1-01 | Encode a dependency contract in code and configuration defaults (strict by default). |  |
| 1 | P1-02 | Align env var usage across process-compose, Go, and Python for Temporal/NATS/Redis/Neo4j/Postgres. | P1-01 |
| 1 | P1-03 | Standardize preflight failure formatting and retry semantics (aggregated failures, visible waiting). | P1-01 |
| 1 | P1-04 | Inventory CI gates and classify required vs informational workflows (single quality gate contract). |  |
| 1 | P1-05 | Make required CI gates fail loud and add a single aggregator job (`quality-gate`). | P1-04 |
| 1 | P1-06 | Enforce coverage floors, E2E project execution, and perf/load thresholds in required CI gates. | P1-05 |
| 2 | P2-01 | Add a minimal PingWorkflow (Temporal) for end to end readiness. | P1-02 |
| 2 | P2-02 | Register PingWorkflow in the Python worker. | P2-01 |
| 2 | P2-03 | Add `temporal-worker` process to `config/process-compose.yaml`. | P1-02 |
| 2 | P2-04 | Add a readiness probe that proves worker execution (PingWorkflow completes). | P2-02, P2-03 |
| 2 | P2-05 | Update health and preflight to report Temporal server and worker separately and fail loud when workflows enabled but worker absent. | P2-04, P1-03 |
| 2 | P2-06 | Add tests that fail if workflows can be started but cannot execute. | P2-05 |
| 2 | P2-07 | Temporal schedules hardening (idempotent upsert, ownership policy, operational listing). | P2-05 |
| 2 | P2-08 | Temporal Search Attributes mode (registration, set/query conventions, health visibility). | P2-05 |
| 2 | P2-09 | Temporal worker versioning policy and validation. | P2-05 |
| 3 | P3-01 | Expand `config/nats-server.conf` (JetStream store dir and limits) and ensure local directories exist. | P1-02 |
| 3 | P3-02 | Standardize Go event publishing: JetStream ack, timeouts, and (when required) Msg-Id dedup. | P3-01 |
| 3 | P3-03 | Standardize Go consumer defaults: durable naming, ack policy, max deliver, and backoff. | P3-02 |
| 3 | P3-04 | Add a preflight check that verifies JetStream stream existence and basic publish ack behavior when NATS is enabled. | P3-02, P1-03 |
| 3 | P3-05 | Add NATS integration tests: ack required, redelivery behavior, and dedup where configured. | P3-03 |
| 3 | P3-06 | NATS JetStream observability: consumer lag and stream health surfaced via metrics and health output. | P3-03 |
| 3 | P3-07 | JetStream KV mode: wrapper plus first concrete use-case. | P1-01, P3-01 |
| 3 | P3-08 | JetStream Object Store mode: wrapper plus first concrete use-case. | P1-01, P3-01 |
| 3 | P4-01 | Define Redis cache and feature flag boundaries in Go: required by default; disable only by explicit mode. | P1-01 |
| 3 | P4-02 | Make Upstash (if supported) an explicit backend mode, never an implicit fallback. | P4-01 |
| 3 | P4-03 | Add tests to prevent regression into silent Redis degradation. | P4-02 |
| 3 | P4-04 | Inventory Redis command surface and any Lua usage to define a compatibility contract. |  |
| 3 | P4-05 | Build and run a Redis compatibility harness against Redis OSS and Valkey (KeyDB optional). | P4-04 |
| 3 | P4-06 | Optional: add Valkey backend to dev stack and wire explicit `REDIS_BACKEND` selection. | P4-05, P1-02 |
| 4 | P5-01 | Make `pg_stat_statements` actually active in dev (process-compose Postgres start flags) and add a dev-time check. | P1-02 |
| 4 | P5-02 | Convert perf tooling into a loud gate: remove "skip because extension not enabled" behavior in perf gates. | P5-01 |
| 4 | P5-03 | Wire perf checks into CI (or a dedicated strict validation target). | P5-02 |
| 4 | P5-04 | PgBouncer mode: explicit enablement, process-compose wiring, and smoke coverage when enabled. | P1-02 |
| 4 | P5-05 | `pg_cron` mode: explicit enablement, preload enforcement, and smoke coverage when enabled. | P1-02 |
| 4 | P6-01 | Make Neo4j index creation and schema verification required (no warn and continue). | P1-01 |
| 4 | P6-02 | Add query guardrails: timeouts and bounded traversals at the API boundary. | P6-01 |
| 4 | P6-03 | Add tests for Neo4j schema requirements and guardrails. | P6-02 |
| 4 | P6-04 | Align test stacks with the default dev Neo4j plugin policy (APOC and GDS disabled by default). | P1-01 |
| 4 | P7-01 | Refactor `backend/internal/infrastructure/infrastructure.go` to remove `//nolint:funlen` (split into focused init functions). | P1-01 |
| 4 | P7-02 | Remove test suppressions tied to the infrastructure init refactor (no new suppressions). | P7-01 |
| 5 | P8-01 | Add an end to end smoke validation entrypoint for dev and CI (preflight plus minimal actions). | P2-06, P3-05, P5-03, P6-03 |
| 5 | P8-02 | Update verification docs and checklists for the new strict behavior (explicit modes, required dependencies). | P8-01 |
| 5 | P8-03 | Extend smoke validation to cover enabled extension modes (Search Attributes, KV/Object, PgBouncer, `pg_cron`, collector mode) when explicitly enabled. | P8-01, P2-08, P3-07, P3-08, P5-04, P5-05 |
| 6 | P10-01 | OpenTelemetry Collector mode in dev stack (process-compose + config) with loud failures in that mode. | P1-02 |
| 6 | P10-02 | Collector mode smoke validation (OTLP export proves end to end trace flow). | P10-01, P8-01 |

## DAG (Dependencies as an Explicit List)

- P1-02 depends on P1-01
- P1-03 depends on P1-01
- P1-05 depends on P1-04
- P1-06 depends on P1-05
- P2-01 depends on P1-02
- P2-02 depends on P2-01
- P2-03 depends on P1-02
- P2-04 depends on P2-02 and P2-03
- P2-05 depends on P2-04 and P1-03
- P2-06 depends on P2-05
- P2-07 depends on P2-05
- P2-08 depends on P2-05
- P2-09 depends on P2-05
- P3-01 depends on P1-02
- P3-02 depends on P3-01
- P3-03 depends on P3-02
- P3-04 depends on P3-02 and P1-03
- P3-05 depends on P3-03
- P3-06 depends on P3-03
- P3-07 depends on P1-01 and P3-01
- P3-08 depends on P1-01 and P3-01
- P4-01 depends on P1-01
- P4-02 depends on P4-01
- P4-03 depends on P4-02
- P4-05 depends on P4-04
- P4-06 depends on P4-05 and P1-02
- P5-01 depends on P1-02
- P5-02 depends on P5-01
- P5-03 depends on P5-02
- P5-04 depends on P1-02
- P5-05 depends on P1-02
- P6-01 depends on P1-01
- P6-02 depends on P6-01
- P6-03 depends on P6-02
- P6-04 depends on P1-01
- P7-01 depends on P1-01
- P7-02 depends on P7-01
- P8-01 depends on P2-06 and P3-05 and P5-03 and P6-03
- P8-02 depends on P8-01
- P8-03 depends on P8-01 and P2-08 and P3-07 and P3-08 and P5-04 and P5-05
- P10-01 depends on P1-02
- P10-02 depends on P10-01 and P8-01

## Parallelization Plan (Subagent Packets)

Subagent packets are designed so each packet can be implemented independently with minimal overlap. Keep each packet constrained to 1 to 3 related files unless explicitly noted.

| Packet | Tasks | Files |
|---|---|---|
| A | P2-01, P2-02 | `src/tracertm/workflows/workflows.py`; `src/tracertm/workflows/worker.py` |
| B | P2-03, P2-04 | `config/process-compose.yaml`; `scripts/shell/readiness-temporal-worker.sh` (new); `scripts/shell/temporal-worker-if-not-running.sh` (new, if needed) |
| C | P2-05, P2-06 | `src/tracertm/services/temporal_service.py`; `src/tracertm/api/handlers/health.py`; `src/tracertm/preflight.py` |
| D | P3-01 | `config/nats-server.conf`; `scripts/shell/nats-if-not-running.sh` (optional) |
| E | P3-02, P3-03 | `backend/internal/nats/nats.go` |
| F | P3-04, P3-05 | `backend/internal/preflight/preflight.go`; minimal Go tests for NATS integration |
| G | P4-01, P4-02, P4-03 | `backend/internal/infrastructure/infrastructure.go` and/or `backend/internal/cache/*`; minimal Go tests |
| H | P5-01, P5-02, P5-03 | `scripts/shell/postgres-if-not-running.sh`; `backend/internal/database/*`; minimal CI wiring |
| I | P6-01, P6-02, P6-03 | `backend/internal/graph/neo4j_client.go`; `backend/internal/graph/neo4j_init.go`; minimal Go tests |
| J | P7-01, P7-02 | `backend/internal/infrastructure/infrastructure.go`; `backend/internal/infrastructure/infrastructure_test.go` |
| K | P8-01, P8-02, P8-03 | new smoke script under `scripts/`; minimal docs under `docs/checklists/` or `docs/guides/` |
| L | P1-04, P1-05, P1-06 | `.github/workflows/*.yml`; `frontend/**/vitest.config.ts`; `frontend/apps/web/package.json` |
| M | P4-04, P4-05, P4-06 | compatibility harness under `scripts/` or `backend/`; `config/process-compose.yaml` |
| N | P6-04 | `backend/docker-compose.test.yml`; `backend/tests/e2e/docker-compose.yml` |
| O | P2-07, P2-08, P2-09 | `src/tracertm/services/temporal_service.py`; `src/tracertm/workflows/*`; `src/tracertm/api/handlers/health.py` |
| P | P3-06, P3-07, P3-08 | `backend/internal/nats/*`; optional shared health/metrics surfaces |
| Q | P5-04, P5-05 | `config/process-compose.yaml`; `scripts/shell/postgres-if-not-running.sh` |
| R | P10-01, P10-02 | `config/process-compose.yaml`; `config/otel-collector.yaml` (new); tracing env wiring |

## Task Specs (Granular Implementation Notes)

Each task below includes concrete file targets, required behavior, and validation. Agents should implement without human handoffs.

### Phase 1: Contract and Preflight

#### P1-01: Encode a Dependency Contract (Strict Defaults)

Scope:

- Ensure strict defaults are encoded in code paths that decide whether a dependency is required.
- Ensure no feature becomes "optional by accident" due to missing env vars.

Files (likely):

- `backend/internal/config/*` and `backend/internal/preflight/preflight.go`
- `src/tracertm/preflight.py`

Implementation requirements:

1. Define explicit mode switches for any behavior currently inferred from "missing config".
2. Defaults must be strict and fail loud.
3. Any disabled mode must be explicit and visible (logged once at startup and reported via health output).

Validation:

- Run the service with required env vars missing and confirm startup fails with an aggregated error listing each missing item.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P1-02: Align Env Var Usage Across Orchestration, Go, and Python

Primary intent:

- Ensure `config/process-compose.yaml` passes the same required env vars that preflight and services expect.

Files:

- `config/process-compose.yaml`
- `.env.example` (only if an env var is missing or ambiguous)

Acceptance:

- Running dev stack does not rely on implicit defaults that contradict preflight requirements (example: Temporal namespace must be set where required).

Estimates:

- Tool calls: 4 to 8
- Wall clock: 5 to 10 minutes

#### P1-03: Standardize Preflight Failure Formatting and Retry Semantics

Intent:

- Make failures explicit and itemized, and retries visible, in both Go and Python preflight.

Files:

- `backend/internal/preflight/preflight.go`
- `src/tracertm/preflight.py`

Acceptance:

- Preflight failures are formatted as a stable list of named items.
- Required failures always fail the process; optional checks never hide required ones.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P1-04: Inventory CI Gates and Classify Required vs Informational

Intent:

- Produce an enforcement matrix for workflows, suites, and thresholds.
- Classify each workflow and job as required or informational.

Files:

- `.github/workflows/*.yml`
- Optional output doc: `docs/research/ci-gate-enforcement-matrix.md` (new)

Requirements:

1. Every workflow that claims validation or enforcement is required and gating, or is clearly labeled informational.
2. Required suites are enumerated as the dependency hardening and extensions "quality gate" set.
3. The matrix includes coverage thresholds and E2E project coverage per app where configured.

Acceptance:

- A single matrix exists under `docs/research/` and is referenced by this plan.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P1-05: Make Required CI Gates Fail Loud and Add a Single Aggregator Job

Files:

- `.github/workflows/*.yml`

Requirements:

1. Remove `continue-on-error: true` and `|| true` from required suites.
2. Add a `quality-gate` aggregator job that depends on required suites and is the only required PR check.
3. Informational workflows are separate and do not masquerade as validation.

Acceptance:

- Any failing required suite fails the overall required check.
- The aggregator job fails if any required dependency fails.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P1-06: Enforce Coverage Floors, E2E Projects, and Perf and Load Thresholds in CI

Files:

- `.github/workflows/*.yml`
- `frontend/**/vitest.config.ts`
- `frontend/apps/web/package.json`

Requirements:

1. JS and TS unit tests run with coverage where thresholds are defined.
2. Repo-wide JS and TS coverage floor is >= 85, including Storybook.
3. Playwright runs declared projects for accessibility and performance when the workflow is required.
4. Performance and load thresholds fail required workflows when violated.

Acceptance:

- CI fails on any threshold violation or project failure in required workflows.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

### Phase 2: Temporal End to End Execution

#### P2-01: Add PingWorkflow for Readiness

Files:

- `src/tracertm/workflows/workflows.py`

Requirements:

1. Add a minimal workflow that returns a small payload and completes quickly.
2. Workflow must run on the standard task queue used by the worker.

Acceptance:

- PingWorkflow can be started and returns within a short timeout when the worker is running.

Estimates:

- Tool calls: 3 to 6
- Wall clock: 5 to 10 minutes

#### P2-02: Register PingWorkflow in Worker

Files:

- `src/tracertm/workflows/worker.py`

Acceptance:

- Worker registers PingWorkflow and can execute it.

Estimates:

- Tool calls: 2 to 4
- Wall clock: 3 to 6 minutes

#### P2-03: Add Temporal Worker Process to Process Compose

Files:

- `config/process-compose.yaml`
- `scripts/shell/temporal-worker-if-not-running.sh` (new, if necessary)

Requirements:

1. Default dev stack must start the worker process.
2. Worker must share the same env config as the Python API for `TEMPORAL_HOST`, `TEMPORAL_NAMESPACE`, and `TEMPORAL_TASK_QUEUE`.

Acceptance:

- `process-compose` shows the worker running in the default stack.

Estimates:

- Tool calls: 4 to 8
- Wall clock: 5 to 10 minutes

#### P2-04: Readiness Probe That Proves Worker Execution

Files:

- `scripts/shell/readiness-temporal-worker.sh` (new)
- `config/process-compose.yaml`

Requirements:

1. The readiness probe must fail if Temporal is reachable but no worker can execute tasks.
2. The readiness probe must succeed only when PingWorkflow completes on the configured task queue.
3. Failure output must be actionable (host, namespace, task queue, and next steps).

Acceptance:

- With worker stopped, readiness probe fails.
- With worker running, readiness probe succeeds.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P2-05: Health and Preflight Must Report Worker Readiness

Files:

- `src/tracertm/services/temporal_service.py`
- `src/tracertm/api/handlers/health.py`
- `src/tracertm/preflight.py`

Requirements:

1. Temporal health must separately report "server reachable" and "worker can execute".
2. When workflows are enabled, lack of worker execution must be considered unhealthy.

Acceptance:

- Health output does not claim Temporal is healthy if workflows cannot execute.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P2-06: Tests That Prevent "Workflows Started but Never Execute"

Files:

- Smallest possible Python test file(s) under `tests/` to validate readiness semantics

Requirements:

1. Add a test that fails if PingWorkflow cannot complete.
2. The test must be deterministic and fast (short timeouts).

Acceptance:

- The test fails when worker is absent and passes when worker is present.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P2-07: Temporal Schedules Hardening

Files:

- `src/tracertm/services/temporal_service.py`
- Any schedule definition files already used by the repo under `src/tracertm/`

Requirements:

1. Schedule create operations are idempotent (upsert semantics), not "create and hope".
2. Schedule IDs are stable and namespaced per environment to avoid cross-env collisions.
3. Enabling and disabling schedules is explicit and visible in health output.

Acceptance:

- Enabling schedules results in exactly one schedule per intended ID and it is describable.
- Disabling schedules removes or pauses them intentionally, with an explicit health banner.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P2-08: Temporal Search Attributes Mode (Visibility)

Files:

- `src/tracertm/services/temporal_service.py`
- `src/tracertm/api/handlers/health.py` (or the smallest health surface that reports workflow capability)

Requirements:

1. Search Attributes usage is behind an explicit mode switch.
2. When the mode is enabled, required attributes are present and workflows set them consistently.
3. When the mode is enabled but prerequisites are missing, the system fails loudly and points at the missing items.

Acceptance:

- In Search Attributes mode, at least one workflow is queryable by attribute and the health output reports visibility readiness.
- With the mode enabled but attributes missing, preflight fails with an itemized error.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P2-09: Temporal Worker Versioning Policy

Files:

- `src/tracertm/workflows/worker.py`
- `src/tracertm/services/temporal_service.py` (only if client-side validation is needed)

Requirements:

1. Worker version identity is explicit and visible (not implicit via git state).
2. Rollout policy is encoded so deploys do not strand in-flight workflows.
3. Failures around versioning are loud and actionable.

Acceptance:

- Worker reports an explicit version identity and the system can run workflows across a version rollout without silent execution gaps.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

### Phase 3: NATS JetStream Reliability

#### P3-01: Expand NATS JetStream Server Config

Files:

- `config/nats-server.conf`

Requirements:

1. Set JetStream `store_dir` to a repo-local directory suitable for dev.
2. Define explicit disk and memory limits to avoid unbounded growth.

Acceptance:

- NATS starts with JetStream enabled and uses the configured store dir.

Estimates:

- Tool calls: 3 to 6
- Wall clock: 5 to 10 minutes

#### P3-02: Standardize Publishing on JetStream Acks and Dedup (Go)

Files:

- `backend/internal/nats/nats.go`

Requirements:

1. Critical publishes must require a publish ack and time out loudly when not received.
2. Where duplicates are harmful, set Msg-Id for server-side deduplication.
3. Core NATS best effort publish may remain only for explicitly labeled ephemeral signals.

Acceptance:

- A critical publish path errors when ack is not received.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P3-03: Standardize Consumer Defaults (Go)

Files:

- `backend/internal/nats/nats.go`

Requirements:

1. Durable names must be stable.
2. Ack policy and redelivery behavior must be explicit for each subscription site.

Acceptance:

- Consumer config is intentional, not implicit defaults.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P3-04: Add NATS JetStream Preflight Check (Go)

Files:

- `backend/internal/preflight/preflight.go`

Requirements:

1. When NATS is enabled, preflight must verify JetStream is usable and required streams exist.
2. Failure output must include stream name(s) and the connected server URL.

Acceptance:

- NATS preflight fails loudly if JetStream stream is missing.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P3-05: NATS Integration Tests

Files:

- New minimal Go test file(s) colocated with NATS package or integration tests directory

Requirements:

1. Tests must cover publish ack requirement and at least one redelivery scenario.
2. Tests must be reliable in CI.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P3-06: NATS JetStream Observability (Consumer Lag and Stream Health)

Files:

- `backend/internal/nats/nats.go` and any existing metrics surfaces
- Optional: shared health output surfaces

Requirements:

1. Consumer lag, ack pending, and redelivery indicators are observable.
2. Stream storage growth is observable and bounded by configured limits.
3. When NATS is enabled, health output includes explicit JetStream status and key stream names.

Acceptance:

- A developer can tell whether consumers are keeping up without inspecting the NATS server directly.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P3-07: JetStream KV Mode (Wrapper Plus First Use Case)

Files:

- Smallest possible new wrapper under `backend/internal/nats/` or a dedicated package
- `config/process-compose.yaml` only if enabling requires new env/config wiring

Requirements:

1. KV use is behind an explicit mode switch and never inferred from missing Redis.
2. KV errors are loud and actionable when KV mode is enabled.
3. First use-case replaces bespoke coordination state only when it reduces moving parts.

Acceptance:

- With KV mode enabled, a basic KV put and get operation succeeds and is covered by a smoke check.
- With KV mode disabled, no KV behavior is executed and no silent fallback occurs.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P3-08: JetStream Object Store Mode (Wrapper Plus First Use Case)

Files:

- Smallest possible new wrapper under `backend/internal/nats/` or a dedicated package
- `config/process-compose.yaml` only if enabling requires new env/config wiring

Requirements:

1. Object Store use is behind an explicit mode switch.
2. Storage limits and retention are explicit and verified.
3. First use-case is selected only when it eliminates an existing subsystem or a bespoke blob pipeline.

Acceptance:

- With Object Store mode enabled, a basic put and get operation succeeds and is covered by a smoke check.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

### Phase 3: Redis Correctness Boundaries (Go)

#### P4-01: Define Cache and Redis Required Policy (Go)

Files:

- `backend/internal/infrastructure/infrastructure.go` and/or `backend/internal/cache/*`

Requirements:

1. Required by default for correctness critical paths.
2. If caching is allowed to be disabled, it must be explicit and visible.
3. No implicit fallback to alternate backends based on missing env vars.

Acceptance:

- Startup fails when Redis is required and unavailable.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P4-02: Upstash Is an Explicit Mode Only

Files:

- Smallest config and init surfaces that currently consider Upstash or alternate Redis backends

Acceptance:

- Selecting Upstash without required config fails loudly; missing native Redis does not silently switch to Upstash.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P4-03: Redis Policy Regression Tests

Files:

- Smallest targeted Go test file(s) validating policy

Acceptance:

- Tests fail if code reintroduces silent degradation or fallback.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P4-04: Inventory Redis Command Surface and Lua Usage

Intent:

- Define the Redis compatibility contract based on what the repo actually uses.

Files:

- Redis callsites under `backend/` and `src/`
- Optional output doc: `docs/research/redis-compatibility-contract.md` (new)

Requirements:

1. Enumerate commands and features used, including Lua scripts if present.
2. Record required behaviors that affect alternative servers, including streams, pubsub, transactions, and key expiry semantics.
3. Produce a compatibility contract that a harness can execute.

Acceptance:

- A compatibility contract exists under `docs/research/` and is referenced by the harness task.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P4-05: Redis Compatibility Harness (Redis OSS and Valkey)

Files:

- A small harness under `scripts/` or as a focused Go test target

Requirements:

1. Harness covers the compatibility contract from P4-04 and fails loudly on any incompatibility.
2. Harness can run locally as a single command.
3. Harness can run in CI when Redis server selection is being evaluated or enforced.

Acceptance:

- Harness passes against Redis OSS and Valkey for the repo's required command surface.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P4-06: Optional Valkey Backend in Dev Stack With Explicit Backend Selection

Files:

- `config/process-compose.yaml`
- The smallest config surface that selects Redis backend and builds `REDIS_URL`

Requirements:

1. Backend selection is explicit and visible, never inferred from missing config.
2. If Valkey mode is selected and Valkey is unavailable, startup fails loudly.
3. Default mode remains strict and uses the default Redis-compatible backend without hidden fallbacks.

Acceptance:

- Dev stack can run with `REDIS_BACKEND=valkey` and preflight reports the selected backend.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

### Phase 4: Postgres Perf Tooling Becomes Real

#### P5-01: Make `pg_stat_statements` Active in Dev Stack

Files:

- `scripts/shell/postgres-if-not-running.sh`

Requirements:

1. When Postgres is launched via process-compose, it must preload `pg_stat_statements`.
2. If Postgres is already running without the required preload, the dev stack must fail loudly with an actionable message rather than silently proceeding.

Acceptance:

- `pg_stat_statements` queries work in dev without manual config edits.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P5-02: Perf Gates Must Fail Loud (No Skips)

Files:

- `backend/internal/database/performance_test.go`
- `scripts/sql/db-performance-audit.sql` (if needed)

Acceptance:

- Perf gate tests produce an explicit failure message when prerequisites are not met.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P5-03: CI Wiring for Perf Gate

Files:

- `Makefile` and CI workflow files (only the minimal changes required)

Acceptance:

- CI job fails loudly when perf prerequisites are missing or perf gate fails.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

#### P5-04: PgBouncer Mode (Explicit Enablement and Smoke Coverage)

Files:

- `config/process-compose.yaml`
- The smallest connection wiring surfaces for Postgres in Go and Python

Requirements:

1. PgBouncer is enabled only by explicit mode and is visible in startup and health output.
2. When PgBouncer mode is enabled, connection strings and pooling configuration are validated.
3. Failures in PgBouncer mode are loud and itemized, not "fallback to direct Postgres".

Acceptance:

- With PgBouncer mode enabled, app connects via PgBouncer and a smoke check proves connectivity.
- With PgBouncer mode enabled and PgBouncer missing, startup fails loudly.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P5-05: `pg_cron` Mode (Explicit Enablement and Preload Enforcement)

Files:

- `scripts/shell/postgres-if-not-running.sh`
- `config/process-compose.yaml` (only if needed to wire config)

Requirements:

1. `pg_cron` is enabled only by explicit mode and is visible in startup and health output.
2. When `pg_cron` mode is enabled, preload requirements are enforced and validated.
3. Failures in `pg_cron` mode are loud and actionable.

Acceptance:

- With `pg_cron` mode enabled, a minimal cron job can be created and observed.
- With `pg_cron` mode enabled but preload missing, startup fails loudly.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

### Phase 4: Neo4j Strict Schema and Guardrails

#### P6-01: Make Schema Setup Required (No Warn and Continue)

Files:

- `backend/internal/graph/neo4j_client.go`
- `backend/internal/graph/neo4j_init.go`

Requirements:

1. Index creation failures are fatal when Neo4j is required.
2. Verification checks ensure expected indexes/constraints exist.

Acceptance:

- Startup fails if schema requirements are not met.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P6-02: Query Guardrails (Timeouts and Bounded Traversals)

Files:

- The smallest possible API boundary layer or graph query wrapper where max depth and timeouts can be enforced

Acceptance:

- Pathological queries are rejected or time out with a clear error message.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P6-03: Neo4j Schema and Guardrails Tests

Files:

- Minimal Go test files for schema verification and guardrails

Acceptance:

- Tests fail if indexes are not created or if guardrails are removed.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P6-04: Align Test Stacks With Default Dev Neo4j Plugin Policy

Files:

- `backend/docker-compose.test.yml`
- `backend/tests/e2e/docker-compose.yml`

Requirements:

1. Default dev does not require APOC or GDS and tests must not implicitly assume these plugins exist in dev.
2. If any tests require APOC or GDS, that dependency is explicit and the required procedures are allowlisted narrowly.
3. When plugin mode is enabled, preflight validates plugin availability loudly and refuses to run without it.

Acceptance:

- Running the default dev stack does not require Neo4j plugins.
- Tests that require plugins declare that requirement explicitly and fail loudly if plugins are missing.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

### Phase 4: Lint Governance Refactor

#### P7-01: Refactor Infrastructure Init (Remove `//nolint:funlen`)

Files:

- `backend/internal/infrastructure/infrastructure.go`

Requirements:

1. Replace `InitializeInfrastructure` monolith with small, named init steps.
2. No functionality loss; all existing services still initialize correctly.

Acceptance:

- Lint passes without `//nolint:funlen` suppression.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P7-02: Remove Related Test Suppressions

Files:

- `backend/internal/infrastructure/infrastructure_test.go`

Acceptance:

- Tests remain meaningful and no new suppressions are added.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

### Phase 5: End to End Validation and Handoff

#### P8-01: End to End Smoke Validation Entry Point

Files:

- New script under `scripts/` (name chosen to match repo conventions)

Requirements:

1. Runs preflight.
2. Runs Temporal PingWorkflow.
3. Runs a minimal NATS publish and confirms ack.
4. Runs minimal Neo4j connectivity and schema check.
5. Runs Postgres `pg_stat_statements` verification when perf gates enabled.

Acceptance:

- One command yields a loud pass or a named failure list with actionable messages.

Estimates:

- Tool calls: 10 to 20
- Wall clock: 20 to 40 minutes

#### P8-02: Update Verification Docs and Checklists

Files:

- `docs/checklists/` (choose existing checklist to extend, or add a new checklist under `docs/checklists/`)

Acceptance:

- Docs reflect explicit modes and strict failure semantics.

Estimates:

- Tool calls: 4 to 8
- Wall clock: 5 to 10 minutes

#### P8-03: Extend Smoke Validation for Enabled Extension Modes

Files:

- The smoke script introduced by P8-01

Requirements:

1. Smoke checks are conditional on explicit mode enablement, never on inferred defaults.
2. When enabled, each mode has a minimal end to end proof, including Temporal Search Attributes, JetStream KV, JetStream Object Store, PgBouncer, `pg_cron`, and collector mode.
3. Failures list each failing mode item explicitly and include next steps.

Acceptance:

- Enabling any extension mode without its prerequisites yields a loud smoke failure naming the missing prerequisite.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

### Phase 6: Observability Extensions

#### P10-01: OpenTelemetry Collector Mode in Dev Stack

Files:

- `config/process-compose.yaml`
- `config/otel-collector.yaml` (new)

Requirements:

1. Collector mode is enabled only by explicit configuration and is visible in startup and health output.
2. When enabled, app OTLP export goes to the collector and the collector exports onward to the chosen backend.
3. Failures in collector mode are loud and actionable, not a silent "no traces" state.

Acceptance:

- With collector mode enabled, a developer can confirm end to end trace flow without manual wiring changes.

Estimates:

- Tool calls: 8 to 16
- Wall clock: 15 to 30 minutes

#### P10-02: Collector Mode Smoke Validation

Files:

- The smoke script introduced by P8-01

Requirements:

1. Smoke check proves that OTLP export succeeds in collector mode.
2. Smoke check failure output names the failing component and the configuration mode in use.

Acceptance:

- In collector mode, the smoke script fails loudly if traces cannot be exported.

Estimates:

- Tool calls: 6 to 12
- Wall clock: 10 to 20 minutes

## Recommended PR Slices (Agent Executable)

To reduce risk and maximize parallelism, land changes in small, reviewable slices:

1. CI enforcement inventory and required-vs-informational classification (P1-04, Packet L partial).
2. Temporal PingWorkflow plus worker registration (Packet A).
3. Temporal worker process-compose wiring plus readiness probe (Packet B).
4. Temporal health and preflight semantics plus tests (Packet C).
5. NATS config plus Go publish and consume standardization plus tests (Packets D, E, F).
6. Redis policy enforcement plus regression tests (Packet G).
7. Postgres perf activation plus gates (Packet H).
8. Neo4j strict schema, guardrails, and tests (Packet I).
9. Infrastructure refactor for lint governance (Packet J).
10. End to end smoke plus checklist updates, including extension mode smoke checks (Packet K).
11. CI gate hardening implementation and single `quality-gate` aggregator job (P1-05, P1-06, Packet L remainder).
12. Redis compatibility harness and optional Valkey dev backend mode (Packet M).
13. Neo4j plugin policy alignment for tests (Packet N).
14. Temporal capability extensions: schedules, Search Attributes mode, worker versioning policy (Packet O).
15. NATS capability extensions: observability, JetStream KV mode, JetStream Object Store mode (Packet P).
16. Postgres capability extensions: PgBouncer mode and `pg_cron` mode (Packet Q).
17. Observability extension: OpenTelemetry Collector mode and smoke validation (Packet R).
