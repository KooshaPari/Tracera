# Dependency Hardening Execution Plan (WBS and DAG)

**Date:** 2026-02-06  
**Status:** Draft  
**Primary Spec:** `docs/plans/2026-02-06-dependency-hardening-spec.md`  
**Goal:** Make dependency usage end to end correct and fail loud (no silent degradation) for Temporal, NATS JetStream, Redis, Neo4j, and Postgres.

## Deliverables

- Default dev stack starts a Temporal worker and proves workflow execution.
- Preflight and health checks validate end to end capability (not just "port open") for enabled features.
- NATS eventing is standardized on JetStream acks for critical events, with clear dedup semantics where required.
- Redis usage is explicit: required by default; any disabling is explicit and visible.
- Neo4j schema setup is required when enabled (indexes/constraints), with guardrails for pathological traversals.
- Postgres perf tooling used by gates is actually active when those gates run.
- Lint governance is respected: no new suppressions; existing targeted suppressions are removed via refactors.

## Change Surface (Expected Files)

This plan is designed to be implementable by subagents working in parallel. Most tasks are constrained to 1 to 3 related files.

High probability touchpoints:

- `config/process-compose.yaml`
- `config/nats-server.conf`
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

## Phased WBS (Work Breakdown Structure)

| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| 1 | P1-01 | Encode a dependency contract in code and configuration defaults (strict by default). |  |
| 1 | P1-02 | Align env var usage across process-compose, Go, and Python for Temporal/NATS/Redis/Neo4j/Postgres. | P1-01 |
| 1 | P1-03 | Standardize preflight failure formatting and retry semantics (aggregated failures, visible waiting). | P1-01 |
| 2 | P2-01 | Add a minimal PingWorkflow (Temporal) for end to end readiness. | P1-02 |
| 2 | P2-02 | Register PingWorkflow in the Python worker. | P2-01 |
| 2 | P2-03 | Add `temporal-worker` process to `config/process-compose.yaml`. | P1-02 |
| 2 | P2-04 | Add a readiness probe that proves worker execution (PingWorkflow completes). | P2-02, P2-03 |
| 2 | P2-05 | Update health and preflight to report Temporal server and worker separately and fail loud when workflows enabled but worker absent. | P2-04, P1-03 |
| 2 | P2-06 | Add tests that fail if workflows can be started but cannot execute. | P2-05 |
| 3 | P3-01 | Expand `config/nats-server.conf` (JetStream store dir and limits) and ensure local directories exist. | P1-02 |
| 3 | P3-02 | Standardize Go event publishing: JetStream ack, timeouts, and (when required) Msg-Id dedup. | P3-01 |
| 3 | P3-03 | Standardize Go consumer defaults: durable naming, ack policy, max deliver, and backoff. | P3-02 |
| 3 | P3-04 | Add a preflight check that verifies JetStream stream existence and basic publish ack behavior when NATS is enabled. | P3-02, P1-03 |
| 3 | P3-05 | Add NATS integration tests: ack required, redelivery behavior, and dedup where configured. | P3-03 |
| 3 | P4-01 | Define Redis cache and feature flag boundaries in Go: required by default; disable only by explicit mode. | P1-01 |
| 3 | P4-02 | Make Upstash (if supported) an explicit backend mode, never an implicit fallback. | P4-01 |
| 3 | P4-03 | Add tests to prevent regression into silent Redis degradation. | P4-02 |
| 4 | P5-01 | Make `pg_stat_statements` actually active in dev (process-compose Postgres start flags) and add a dev-time check. | P1-02 |
| 4 | P5-02 | Convert perf tooling into a loud gate: remove "skip because extension not enabled" behavior in perf gates. | P5-01 |
| 4 | P5-03 | Wire perf checks into CI (or a dedicated strict validation target). | P5-02 |
| 4 | P6-01 | Make Neo4j index creation and schema verification required (no warn and continue). | P1-01 |
| 4 | P6-02 | Add query guardrails: timeouts and bounded traversals at the API boundary. | P6-01 |
| 4 | P6-03 | Add tests for Neo4j schema requirements and guardrails. | P6-02 |
| 4 | P7-01 | Refactor `backend/internal/infrastructure/infrastructure.go` to remove `//nolint:funlen` (split into focused init functions). | P1-01 |
| 4 | P7-02 | Remove test suppressions tied to the infrastructure init refactor (no new suppressions). | P7-01 |
| 5 | P8-01 | Add an end to end smoke validation entrypoint for dev and CI (preflight plus minimal actions). | P2-06, P3-05, P5-03, P6-03 |
| 5 | P8-02 | Update verification docs and checklists for the new strict behavior (explicit modes, required dependencies). | P8-01 |

## DAG (Dependencies as an Explicit List)

- P1-02 depends on P1-01
- P1-03 depends on P1-01
- P2-01 depends on P1-02
- P2-02 depends on P2-01
- P2-03 depends on P1-02
- P2-04 depends on P2-02 and P2-03
- P2-05 depends on P2-04 and P1-03
- P2-06 depends on P2-05
- P3-01 depends on P1-02
- P3-02 depends on P3-01
- P3-03 depends on P3-02
- P3-04 depends on P3-02 and P1-03
- P3-05 depends on P3-03
- P4-01 depends on P1-01
- P4-02 depends on P4-01
- P4-03 depends on P4-02
- P5-01 depends on P1-02
- P5-02 depends on P5-01
- P5-03 depends on P5-02
- P6-01 depends on P1-01
- P6-02 depends on P6-01
- P6-03 depends on P6-02
- P7-01 depends on P1-01
- P7-02 depends on P7-01
- P8-01 depends on P2-06 and P3-05 and P5-03 and P6-03
- P8-02 depends on P8-01

## Parallelization Plan (Subagent Packets)

Subagent packets are designed so each packet can be implemented independently with minimal overlap. Keep each packet constrained to 1 to 3 related files unless explicitly noted.

Packet A (Temporal workflow execution readiness):

- Tasks: P2-01, P2-02
- Files: `src/tracertm/workflows/workflows.py`, `src/tracertm/workflows/worker.py`

Packet B (Temporal worker orchestration and readiness probe):

- Tasks: P2-03, P2-04
- Files: `config/process-compose.yaml`, `scripts/shell/readiness-temporal-worker.sh` (new), `scripts/shell/temporal-worker-if-not-running.sh` (new, if needed)

Packet C (Temporal health and preflight semantics):

- Tasks: P2-05, P2-06
- Files: `src/tracertm/services/temporal_service.py`, `src/tracertm/api/handlers/health.py`, `src/tracertm/preflight.py`

Packet D (NATS server config):

- Tasks: P3-01
- Files: `config/nats-server.conf`, optional: `scripts/shell/nats-if-not-running.sh` if store dir requires enforcement

Packet E (NATS Go publish and consumer semantics):

- Tasks: P3-02, P3-03
- Files: `backend/internal/nats/nats.go`

Packet F (NATS preflight and tests):

- Tasks: P3-04, P3-05
- Files: `backend/internal/preflight/preflight.go`, plus the smallest possible Go test files for NATS integration

Packet G (Redis policy enforcement in Go):

- Tasks: P4-01, P4-02, P4-03
- Files: `backend/internal/infrastructure/infrastructure.go` and/or `backend/internal/cache/*` depending on where policy belongs, plus the smallest targeted tests

Packet H (Postgres perf tooling activation):

- Tasks: P5-01, P5-02, P5-03
- Files: `scripts/shell/postgres-if-not-running.sh`, `backend/internal/database/*` (only where gates exist), and CI wiring (`Makefile` or workflow files) as needed

Packet I (Neo4j strict schema and guardrails):

- Tasks: P6-01, P6-02, P6-03
- Files: `backend/internal/graph/neo4j_client.go`, `backend/internal/graph/neo4j_init.go`, plus targeted tests

Packet J (Infrastructure refactor for lint governance):

- Tasks: P7-01, P7-02
- Files: `backend/internal/infrastructure/infrastructure.go`, `backend/internal/infrastructure/infrastructure_test.go`

Packet K (End to end smoke and docs updates):

- Tasks: P8-01, P8-02
- Files: a dedicated smoke script under `scripts/` (new) and the minimum doc/checklist updates under `docs/checklists/` or `docs/guides/`

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

## Recommended PR Slices (Agent Executable)

To reduce risk and maximize parallelism, land changes in small, reviewable slices:

1. Temporal PingWorkflow plus worker registration (Packet A).
2. Temporal worker process-compose wiring plus readiness probe (Packet B).
3. Temporal health and preflight semantics plus tests (Packet C).
4. NATS config plus Go publish/consume standardization plus tests (Packets D, E, F).
5. Postgres perf activation plus gates (Packet H).
6. Neo4j strict schema and guardrails (Packet I).
7. Infrastructure refactor for lint governance (Packet J).
8. End to end smoke plus checklist updates (Packet K).

