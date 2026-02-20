# Agent Task Queue Backend Convergence (Fail Loud Spec and Options)

**Date:** 2026-02-06  
**Status:** Draft  
**Primary Plan:** `docs/plans/2026-02-06-dependency-hardening-execution-plan.md`  
**Primary Governance:** fail loud, explicit modes, no silent fallback

## Problem Statement

TraceRTM has a real agent coordination and task distribution surface in Go (`backend/internal/agents/*`) and exposed HTTP endpoints (`backend/internal/handlers/agent_handler.go`). The current implementation mixes durable storage (tasks persisted to `agent_tasks` in Postgres) with in-memory scheduling and best-effort persistence behaviors.

That mix is risky in practice:

- A process restart can strand tasks in the database but not in the in-memory queue.
- Task claim and assignment are not guaranteed to be persisted at the time they occur.
- Multi-instance deployment semantics are undefined, creating double-claim and split-brain risks.
- Failures in persistence paths are sometimes logged but not made fatal, violating "fail loud" governance.

## Goals

- Define a strict task distribution contract that is durable, observable, and multi-instance safe.
- Converge on an explicit backend mode with no implicit fallback.
- Reduce bespoke queue semantics where an OSS solution or an existing dependency (Temporal, JetStream, Postgres) provides a stronger contract with less custom code.

## Non Goals

- Redesigning agent business logic or adding new agent types.
- Building a paid/hosted queue product dependency.
- Adding "graceful degradation" that continues without the selected backend.

## Current State (Repo Facts)

- Tasks are represented by `agents.Task` and stored as JSONB in Postgres table `agent_tasks` via GORM (`backend/internal/agents/queue.go`).
- In-memory priority queue is the primary scheduling mechanism (`backend/internal/agents/queue.go`).
- `LoadTasksFromDB` exists but is not called from startup code paths.
- Status transitions like assign and claim are performed in memory and are not consistently persisted at the time they occur (`backend/internal/agents/coordinator.go` and `backend/internal/agents/queue.go`).
- The HTTP surface supports register, heartbeat, task polling, completion, failure, queue stats, list queued tasks, cancel, and task details (`backend/internal/handlers/agent_handler.go`).

## Contract (Required Semantics When Enabled)

When agent task distribution is enabled, the system must satisfy:

- Durability: enqueued tasks survive restart and remain claimable.
- Single-claim: at most one worker holds an active claim at a time, across all instances.
- Leases: claims expire; crashed workers do not strand tasks forever.
- Rescue: expired leases are detected and tasks become claimable again.
- Retry policy: explicit max retries and backoff; exhausted retries become terminal and are visible.
- Idempotency: duplicate execution is treated as possible; side effects are safe or keyed.
- Backpressure: explicit limits exist per project and globally; overload fails loudly and predictably.
- Observability: queue depth by status, claim latency, retries, rescues, and failures are surfaced as metrics and in health output.

## Backend Mode Options

This section lists durable queue backends that fit the existing stack and governance. The intent is not to add all of them, but to pick one explicit mode and converge.

| Mode | Core idea | Primary dependency | Pros | Cons | Fit |
|---|---|---|---|---|---|
| `coordinator` (fixed) | Keep current Go coordinator, but make it durable and correct | Postgres | Smallest conceptual change; preserves current HTTP contract; no new infra | Must implement correct claim semantics and multi-instance safety; easy to get wrong | Acceptable only after it meets the contract |
| `temporal` | Agent tasks are driven by Temporal task queues and workflow/activity semantics | Temporal | Strong durability, retries, backoff, visibility; already a required dependency | Requires a mapping layer to preserve current HTTP agent contract or a planned API change | Strong |
| `postgres-queue` | Use Postgres atomic claim primitives (`FOR UPDATE SKIP LOCKED`) or an OSS library | Postgres | Strong claim semantics; fewer moving parts; aligns with Postgres requiredness | Requires schema and careful design; library selection must be deliberate | Strong |
| `jetstream` | Use JetStream pull consumers as a work queue | NATS JetStream | Work queue semantics with acks and redelivery; replay; already in dev stack | Task payloads still need DB for state; careful dedup/idempotency needed | Conditional |
| `redis-queue` | Use an OSS Redis queue library (example: `asynq`) | Redis | Mature patterns and tooling; fast | Adds another semantics surface; Redis is required but queue correctness would now depend on it | Conditional |

## Recommended Convergence Strategy

Default recommendation is a two-step path that preserves momentum and reduces risk:

1. Fix `coordinator` mode to meet the contract in dev and CI so agent tasks are correct today.
2. Add `temporal` mode as the long-term durable backend, then run parity tests and cut over behind an explicit mode.

If Temporal is not desired for this surface, prefer `postgres-queue` over `redis-queue` to avoid expanding the set of correctness-critical dependencies beyond what already exists.

## Acceptance Criteria

- A restart does not lose tasks, and stranded tasks are detectable and recoverable.
- Claim is atomic and multi-instance safe, or coordinator mode explicitly refuses multi-instance startup.
- Selected backend mode is explicit and required; missing prerequisites fail at startup and preflight.
- Parity tests cover enqueue, claim, completion, failure with retries, cancellation, and rescue behavior.
- Health output and metrics show queue depth, claim latency, retry counts, and rescue counts.

## WBS and DAG (Agent Subsystem Only)

Phase | Task ID | Description | Depends On
---|---|---|---
1 | A1 | Decide backend mode and write contract plus parity definition | -
1 | A2 | Add backend interface and explicit selection mode | A1
2 | A3 | Make coordinator mode durable and correct (load, persist transitions, fatal on persist failure) | A2
2 | A4 | Add strict preflight and health checks for agent task distribution | A3
2 | A5 | Multi-instance semantics for coordinator mode (leader election or loud refusal) | A3
3 | A6 | Implement Temporal mode with strict preflight and health semantics | A2
3 | A7 | Parity tests and smoke checks for mode flip | A4, A6

## Migration and Rollback

- Migration is mode-based: deploy code with both modes available, keep default mode unchanged until parity checks pass.
- Rollback is mode-based: revert to the previous mode explicitly; no silent fallback is allowed.
- Any schema changes must be forward-compatible across modes during the transition window.

## Risks

- Getting claim semantics wrong in custom code creates duplicate task execution and data corruption risks.
- Mixing multiple backends without a strict mode boundary creates silent fallback behavior.
- Multi-instance operation without leader election or atomic claim will double-assign tasks under load.

