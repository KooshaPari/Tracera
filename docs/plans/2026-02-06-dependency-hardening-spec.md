# Dependency Hardening Spec (Fail Loud): Temporal, NATS, Redis, Neo4j, Postgres

**Date:** 2026-02-06  
**Status:** Draft  
**Audience:** Engineer agents and subagents implementing reliability and correctness hardening  
**Scope:** Local dev (`config/process-compose.yaml`), CI gates, and production runtime behavior (where applicable)

## Problem Statement

TraceRTM uses Postgres, Redis, Neo4j, NATS (JetStream), and Temporal in real ways, but several paths currently validate only connectivity and then proceed with partial functionality. This violates the repo governance stance: required dependencies must be required, and failures must be clear and loud.

Key gaps this spec targets:

- Temporal workflows can be started from the Python API, but the default dev stack does not start a Temporal worker, so workflows may never execute.
- Health and preflight checks validate host reachability, not end to end capability (example: Temporal host reachable but no pollers; NATS reachable but JetStream durability not verified).
- Some initialization paths log warnings and continue even when the resulting system behavior is incorrect (example: Neo4j index creation).
- Postgres performance tooling (notably `pg_stat_statements`) is installed via migration but often not active unless `shared_preload_libraries` is configured.

## Non Negotiable Principles

- Required dependencies are required.
- Fail loud, not silently.
- "Graceful" means retries with visible progress and actionable errors, not optional fallbacks.
- Do not use linter suppression to hide issues (`//nolint:*`, linter ignores, or config disables). Fix properly.

## Definitions

- Required dependency: a service or configuration that must be available for correctness in a given runtime mode. If unavailable, the process must refuse to start (or the specific feature must refuse to execute) with an explicit error listing the failing items.
- Explicitly disabled feature: functionality that is intentionally turned off via a named configuration mode. Disabled behavior must be visible (startup banner and health output) and must not be inferred from missing config.
- End to end health: a check that validates the actual contract, not just "port open". Example: Temporal PingWorkflow completion, not just TCP connect.

## Dependency Contract (Required Behavior)

This table defines the minimum contract each dependency must satisfy when enabled.

| Dependency | Required When | Minimum End To End Health Definition | Startup Gate | Runtime Failure Behavior |
|---|---|---|---|---|
| Postgres | Always | Can connect and run `SELECT 1`. Schema migrations required for active service. | Preflight and process start | Startup fails if unreachable; endpoints using DB return explicit error if DB becomes unavailable. |
| Postgres perf tooling (`pg_stat_statements`) | Dev and CI (when perf gates enabled) | `SHOW shared_preload_libraries` contains `pg_stat_statements` and query against `pg_stat_statements` succeeds. | Preflight (dev and CI), plus dev stack configuration | Startup fails in dev and CI if enabled but inactive; no "skip" behavior in gates. |
| Redis | Always for rate limiting, feature flags, and correctness critical caches | Can connect and `PING` succeeds. For required cache modes, basic `GET/SET/DEL` succeed. | Preflight and process start | Startup fails when required and unavailable; no silent "cache disabled" fallback unless explicitly configured. |
| Neo4j | Always for graph operations | Driver connectivity verified and required indexes/constraints exist for query patterns used by the app. | Preflight and process start | Startup fails if unreachable or schema requirements are not met. |
| NATS | When realtime/eventing provider is enabled | Can connect and JetStream context is usable. Required streams exist with expected retention and storage policy. | Preflight and process start | Startup fails when required and unavailable; publish operations must fail with explicit errors (no best effort publish for critical events). |
| Temporal server | When workflows are enabled | Can connect to namespace, and workflow start API is usable. | Preflight and process start | Startup fails when required and unavailable. |
| Temporal worker (pollers) | When workflows are enabled | A small PingWorkflow can be started and completes within a short timeout on the configured task queue. | Dev stack gate; preflight where applicable | Startup fails (dev and CI) if workflows enabled but no worker can execute tasks. |

## Configuration Modes (Explicit, No Silent Fallbacks)

The system must have explicit modes for any behavior that could otherwise become "optional by accident".

Minimum required explicit modes:

- Workflows mode: workflows are enabled by default, and must require both Temporal server and a running worker in dev and CI.
- Cache mode: caching is required by default; if caching is allowed to be off, it must be an explicit `CACHE_MODE=disabled` style setting, and the app must clearly report that caching is disabled.
- Eventing mode: if realtime/eventing is `nats`, publishing for critical events must use JetStream publish acks and deduplication policy where applicable.

This spec does not mandate the exact env var names, but it requires:

- Defaults are strict.
- Any "disabled" mode is explicit and visible.
- Missing configuration is not treated as "disable" unless the user explicitly selected that mode.

## Preflight Requirements

Preflight is not "nice to have". It is the primary failure surface for required dependencies.

Preflight output requirements:

- Aggregated failure list with stable names: `preflight failed: postgres; redis; temporal-worker`.
- Actionable messages per item (how to fix, which env var is missing, which host is unreachable).
- Retrying is allowed only when visible: `Waiting for temporal-host (2/6)`.
- No warning-only behavior for required items.

Preflight semantic requirements:

- Temporal must be checked end to end (PingWorkflow completion) in dev and CI when workflows are enabled.
- NATS checks must verify JetStream capability and required stream existence, not just TCP connectivity.
- Postgres perf extension checks must be explicit and must fail loud when perf gates depend on it.

## Runtime Health Requirements

Health endpoints must reflect correctness, not just "process alive".

- If a required dependency is unhealthy, overall health must be unhealthy.
- If a feature is explicitly disabled, health must report it as disabled (not "unhealthy" or "missing").
- Temporal health must differentiate:
  - Temporal server reachable.
  - Temporal worker can execute tasks on the configured task queue.

## Reliability Guarantees (Eventing and Workflows)

NATS:

- All critical domain events must be published via JetStream with publish acks.
- For events where duplicates are harmful, publishing must set an idempotency key (Msg-Id) for server side deduplication.
- Subscriptions must define durable consumer semantics and explicit ack policies.

Temporal:

- Starting a workflow must imply it can execute in the current environment. If the system cannot guarantee this (no pollers), starting workflows must fail fast with an explicit error.

## Acceptance Criteria (System Level)

This hardening effort is complete when all items below are true:

- Default local dev stack starts a Temporal worker and a PingWorkflow completes successfully without manual steps.
- If the Temporal worker is not running while workflows are enabled, the system fails loud (preflight and/or service readiness) and does not silently claim Temporal is healthy.
- NATS is considered healthy only when JetStream is usable and required streams/consumers are present; critical publishes fail if publish ack is not received.
- Neo4j index/constraint setup failures are fatal when required for query performance or correctness.
- Postgres perf tooling used by scripts/tests is actually active when those checks run (no "installed but inert" state in dev and CI).
- Repository governance is respected: no linter suppressions are introduced to "fix" quality gates, and existing suppressions targeted by this plan are removed via refactor.

## Out of Scope

- Major redesign of the data model, message schema versioning, or full operationalization of multi account NATS.
- Introducing paid external services to satisfy dependencies (local OSS and native services are preferred).

