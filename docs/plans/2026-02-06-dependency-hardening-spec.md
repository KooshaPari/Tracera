# Dependency Hardening and Capability Extensions Spec (Fail Loud): Temporal, NATS, Redis, Neo4j, Postgres

**Date:** 2026-02-06  
**Status:** Draft  
**Audience:** Engineer agents and subagents implementing dependency hardening and capability extensions  
**Scope:** Local dev (`config/process-compose.yaml`), CI gates, and production runtime behavior (where applicable)

## Problem Statement

TraceRTM uses Postgres, Redis, Neo4j, NATS (JetStream), and Temporal in real ways, but parts of the system still validate only connectivity and then proceed with partial functionality. This violates the repo governance stance: required dependencies must be required, and failures must be clear and loud.

This spec also consolidates high leverage dependency extensions and optimizations so "better usage" means improved correctness, operability, and measurable performance rather than chasing transient runtime errors.

## Goals

- Make dependency usage end to end correct and fail loud for all enabled features.
- Make "optional" behavior explicit via named modes only, never via silent fallback.
- Extend dependency usage where it reduces bespoke code or improves reliability and performance.
- Make CI enforcement match governance for required suites, coverage thresholds, and performance budgets.

## Non Negotiable Principles

- Required dependencies are required.
- Fail loud, not silently.
- "Graceful" means retries with visible progress and actionable errors, not optional fallbacks.
- Do not use linter suppression to hide issues (`//nolint:*`, linter ignores, or config disables). Fix properly.
- Prefer native services and local OSS/free options in dev; do not introduce paid hosted services to satisfy requirements.

## Definitions

- Required dependency: a service or configuration that must be available for correctness in a given runtime mode. If unavailable, the process must refuse to start (or the specific feature must refuse to execute) with an explicit error listing failing items.
- Explicitly disabled feature: functionality intentionally turned off via a named configuration mode. Disabled behavior must be visible and must not be inferred from missing config.
- End to end health: validates the actual contract, not just "port open". Example: Temporal PingWorkflow completion, not just TCP connect.
- Required gate: a CI workflow or job that must fail the change on any failure. A required gate must not use `continue-on-error: true` or `|| true` for the checks it claims to enforce.
- Informational workflow: a workflow that is explicitly labeled informational and is not claimed as validation or enforcement.

## Dependency Contract (Baseline Required Behavior)

This table defines the minimum contract each dependency must satisfy when enabled.

| Dependency | Required When | Minimum End To End Health Definition | Startup Gate | Runtime Failure Behavior |
|---|---|---|---|---|
| Postgres | Always | Can connect and run `SELECT 1`. Schema migrations required for active service. | Preflight and process start | Startup fails if unreachable; endpoints using DB return explicit error if DB becomes unavailable. |
| Postgres perf tooling (`pg_stat_statements`) | Dev and CI when perf gates are enabled | `SHOW shared_preload_libraries` contains `pg_stat_statements` and a query against `pg_stat_statements` succeeds. | Preflight and dev stack configuration | Perf gates fail loudly if enabled but inactive; no skip paths. |
| Redis | Always for rate limiting, feature flags, and correctness critical caches | Can connect and `PING` succeeds. For required cache modes, basic `GET/SET/DEL` succeed. | Preflight and process start | Startup fails when required and unavailable; no silent "cache disabled" fallback unless explicitly configured. |
| Neo4j | Always for graph operations | Driver connectivity verified and required indexes/constraints exist for query patterns used by the app. | Preflight and process start | Startup fails if unreachable or schema requirements are not met. |
| NATS (JetStream) | When eventing provider is enabled | Can connect, JetStream context is usable, and required stream(s) exist with expected retention and storage policy. | Preflight and process start | Startup fails when required and unavailable; critical publishes fail on missing publish ack. |
| Temporal server | When workflows are enabled | Can connect to namespace, and workflow start API is usable. | Preflight and process start | Startup fails when required and unavailable. |
| Temporal worker (pollers) | When workflows are enabled | A small PingWorkflow can be started and completes within a short timeout on the configured task queue. | Dev stack gate and preflight | Startup fails in dev and CI if workflows enabled but no worker can execute tasks. |
| Agent task queue backend | When agent task distribution is enabled | Can enqueue a task, claim a task, and transition it to a terminal state under the configured backend mode. | Preflight and process start | Startup fails when enabled but backend is misconfigured; task APIs fail loudly rather than dropping tasks or relying on in-memory-only state. |

## Configuration Modes (Explicit, No Silent Fallbacks)

The system must have explicit modes for any behavior that could otherwise become "optional by accident".

Minimum required explicit modes:

- Workflows mode: enabled by default and requires both Temporal server and a running worker in dev and CI.
- Cache mode: required by default; if allowed to be off, it must be explicit and visible (example: `CACHE_MODE=disabled`).
- Eventing mode: if eventing is `nats`, publishing for critical events uses JetStream publish acks and dedup where required.
- Redis backend mode: selection is explicit (example: `REDIS_BACKEND=redis|valkey|keydb`), never inferred from missing config.
- Neo4j plugins mode: APOC and GDS are disabled by default and may be enabled only by explicit mode plus allowlists.
- Agent task backend mode: selection is explicit (example: `AGENT_TASK_BACKEND=coordinator|temporal|postgres-queue|jetstream`), never inferred from missing config.

This spec does not mandate exact env var names. It requires strict defaults, explicit disabled modes, and no implicit fallback based on missing env vars.

## Preflight Requirements

Preflight is not "nice to have". It is the primary failure surface for required dependencies.

Preflight output requirements:

- Aggregated failure list with stable names: `preflight failed: postgres; redis; temporal-worker`.
- Actionable messages per item (missing env var, unreachable host, mismatched namespace, missing stream).
- Retries are allowed only when visible: `Waiting for temporal-host (2/6)`.
- No warning-only behavior for required items.

Preflight semantic requirements:

- Temporal checks prove execution (PingWorkflow completion) when workflows are enabled.
- NATS checks verify JetStream capability and required stream existence.
- Postgres perf extension checks fail loudly when perf gates depend on them.

## Runtime Health Requirements

Health endpoints must reflect correctness, not just "process alive".

- If a required dependency is unhealthy, overall health must be unhealthy.
- If a feature is explicitly disabled, health reports it as disabled.
- Temporal health differentiates Temporal server reachability from worker execution capability.

## Reliability Guarantees (Eventing and Workflows)

- NATS critical events publish via JetStream and require publish acks.
- NATS duplicate-sensitive events publish with a dedup key (Msg-Id) and define a dedup window intentionally.
- NATS subscriptions define durable consumer semantics and explicit ack and redelivery policy.
- Temporal workflow start implies the workflow can execute in the current environment; if not, it fails fast with an explicit error.

## Reliability Guarantees (Agents and Task Distribution)

This section defines the minimum reliability semantics when agent task distribution is enabled. It is intentionally strict because "agents" are the surface where silent degradation is most likely (in-memory queue, best-effort status transitions, polling loops).

Required semantics by default:

- Durability: a successfully enqueued task must survive process restart and must remain discoverable for execution.
- Single-claim: a task is claimed by at most one worker at a time, across all API instances.
- Leases and rescue: if a worker crashes mid-task, tasks are rescued and become claimable again after a lease timeout.
- Retries and backoff: retry policy is explicit per task type; terminal failure states are durable; dead-letter behavior is explicit when retries exhaust.
- Idempotency: duplicate execution must be treated as possible; handlers must have idempotency keys or safe repeated effects.
- Observability: queue depth, claim latency, attempt counts, and rescue counts are emitted as metrics and surfaced in health output.

Explicitly forbidden behaviors:

- In-memory-only queue semantics in any enabled production mode.
- Silent "task dropped" behavior on enqueue, claim, or completion.
- Best-effort background loops that mask persistence failures via logging only.

## Capability Extensions (Program Abilities)

All extensions below must follow the same governance as baseline hardening: explicit modes, strict defaults, and loud failures when required.

| Area | Extension Target | Mode | Acceptance Definition |
|---|---|---|---|
| Temporal | Schedules as the single source of truth for recurring workflows | Always on when workflows enabled | Schedules are created and described via API; no competing cron glue runs in parallel. |
| Temporal | Visibility and operational querying via Search Attributes | Enabled by explicit mode | Workflows set and query Search Attributes; failure to register required attributes fails loudly in that mode. |
| Temporal | Worker versioning strategy | Always on for deploys | Rollouts do not strand in-flight workflows; versioning is encoded in worker config and validated. |
| NATS JetStream | Durable consumer defaults everywhere for correctness-critical streams | Always on when eventing enabled | Consumers are durable, ack policy is explicit, and redelivery behavior is tested. |
| NATS JetStream | Evaluate JetStream KV for small coordination state | Enabled by explicit mode | KV use replaces bespoke state only when it removes complexity and is observable. |
| NATS JetStream | Evaluate JetStream Object Store for blob-style artifacts | Enabled by explicit mode | Object store is used only where it replaces another moving part and has clear retention limits. |
| Redis | Redis-compatible server selection with compatibility harness | Always on | A harness enumerates required commands and passes against the chosen server. |
| Agents | Durable task queue semantics with leases and rescue | Always on when agent task distribution enabled | Tasks survive restart; tasks are claimable by one worker; crashed tasks are rescued; retries and DLQ behavior are explicit. |
| Agents | Backend convergence to a single durable queue mode | Enabled by explicit mode | Selected mode is explicit; misconfiguration fails loud; parity tests prove behavior matches the contract. |
| Agents | Task routing and backpressure | Always on when agent task distribution enabled | Per-project limits exist; queue growth is observable; overload fails fast with explicit errors instead of uncontrolled memory growth. |
| Postgres | Connection pooling strategy | Enabled by explicit mode | When enabled, app connects via pooler and p99 latency and error rates improve measurably. |
| Postgres | In-database scheduling via `pg_cron` | Enabled by explicit mode | When enabled, preload requirements are enforced and job execution is observable. |
| Neo4j | Constraints and indexes as required startup contract | Always on when Neo4j required | Startup fails if required constraints/indexes are missing. |
| Neo4j | APOC policy | Disabled by default | Tests do not assume APOC in default dev; enabling APOC requires an allowlist and a hard preflight check. |
| Observability | OpenTelemetry Collector for dev pipeline | Enabled by explicit mode | Apps export OTLP to the collector; failures in collector mode are loud and actionable. |

## CI and Quality Gate Contract

| Area | Requirement | Acceptance Definition |
|---|---|---|
| Pass rate | Required suites fail CI on any failure | No `continue-on-error: true` and no `|| true` in required suites. |
| Coverage | Minimum coverage thresholds are enforced everywhere | Go >= 85, Python >= 90, JS/TS >= 85 as a repo-wide floor, and CI runs coverage where thresholds are defined. |
| E2E projects | Declared Playwright projects are executed when the gate is required | If accessibility and performance projects exist, they run and fail CI on failure. |
| Perf and load | Threshold violations fail when the gate is required | Lighthouse and k6 thresholds are enforced as gates, not warnings, in required workflows. |
| Single gate | One aggregator job is the only required PR check | The aggregator depends on all required suites; informational workflows are separate and clearly labeled. |

## Acceptance Criteria (System Level)

Dependency hardening is complete when all items below are true:

- Default local dev stack starts a Temporal worker and PingWorkflow completes without manual steps.
- Workflows enabled and worker absent yields an explicit failure; the system does not claim Temporal is healthy.
- NATS is healthy only when JetStream is usable and required streams exist; critical publishes fail without publish ack.
- Neo4j schema setup failures are fatal when Neo4j is required.
- Postgres perf tooling used by scripts and tests is active when those gates run.
- No new linter suppressions are introduced to pass gates; targeted suppressions are removed via refactor.
- When agent task distribution is enabled, tasks are durable and claim semantics are correct across restarts.
- Agent task backend selection is explicit; selecting a mode that is misconfigured fails at startup with an aggregated error list.

Capability extensions are complete when all enabled extension modes meet their acceptance definitions and are covered by tests or smoke checks where applicable.

CI hardening is complete when required workflows enforce pass rate, coverage, and performance budgets without "report-only" escapes.

## Out of Scope

- Debugging transient frontend runtime errors or the `/home` freeze. Track performance work separately in `docs/plans/2026-02-01-comprehensive-performance-optimization-plan.md`.
- Major redesign of the data model, message schema versioning, or full operationalization of multi account NATS.
- Introducing paid external services to satisfy dependencies (local OSS and native services are preferred).
