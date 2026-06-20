---
audience: [developers, agents]
status: active
---

# Implementation Strategy

## Recovery First

Work in `Tracera-recovered/` until the recovered checkout is clean. The existing `Tracera/`
directory stays untouched until replacement is safe.

First recovery patch:

- remove lowercase root duplicates that collide on macOS
- keep `AGENTS.md` and `CLAUDE.md` as canonical root governance files
- keep any unique lowercase content by moving it into appropriate docs only if needed

## Infrastructure Modernization

Promtail is not a modernization candidate. Replace it with Alloy.

Recommended local observability shape:

- Alloy collects file logs and OTLP traces.
- Loki remains acceptable as the local log backend.
- Alloy is the default local collector and exports traces to Tempo/shared tracing storage.
- Remove the remaining Jaeger wrapper scripts once no live callers remain; do not preserve
  default-path teaching text in compatibility surfaces.
- The prod-like Docker Compose stack should own a Tempo service rather than depending on Jaeger,
  and backend envs should use `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT`.
- Prometheus and Grafana remain useful for local developer dashboards.
- On macOS, `alloy` may be the formal-methods Alloy CLI. The local wrapper now verifies Grafana
  Alloy by checking `run --help` and also accepts `$HOME/.local/bin/grafana-alloy`.

Recommended data-plane split:

- PostgreSQL: source-of-truth records, versions, locks that need transactions, audit indexes.
- NATS JetStream: event streams, real-time graph updates, session/checkpoint events, watchers,
  object-transfer notifications, SSE notification fan-out, and short-history KV where stream
  semantics are useful.
- Dragonfly: default Redis-compatible cache/rate-limit/session runtime for local and
  production-like runs.
- Redis: explicit fallback only for compatibility testing or concrete command incompatibility.

Local runtime switch:

- default: `REDIS_COMPAT_PROVIDER=dragonfly`
- Redis fallback: `REDIS_COMPAT_PROVIDER=redis`

Dragonfly-backed Redis-compatible responsibilities that remain valid:

- cache/read-through/invalidation
- rate limiting and adaptive throttling
- session and OAuth CSRF state
- bootstrap health checks and exporter wiring

Responsibilities to move:

- notification pub/sub -> NATS JetStream (implemented for Go SSE notifications)
- feature flags and operational config -> PostgreSQL

Implemented notification shape:

- `NotificationService` persists notification state in PostgreSQL.
- A NATS-backed notification event bus publishes user-scoped subjects under
  `tracertm.notifications.<user_id>`.
- Each backend instance subscribes to the notification subject tree and fans events out only to
  local SSE subscribers.
- Redis is no longer part of the Go notification fan-out path.

## Product Consolidation

Do not delete the high-scale graph renderer. It is aligned with the product.

Do consolidate:

- duplicate graph view entrypoints
- overlapping traceability services
- history, event sourcing, temporal, and graph snapshot boundaries
- root/status markdown sprawl

## QA/Test Router Extraction

The QA and test management surface was moved out of `src/tracertm/api/main.py`
into dedicated routers:

- `src/tracertm/api/routers/test_cases.py`
- `src/tracertm/api/routers/test_suites.py`
- `src/tracertm/api/routers/test_runs.py`
- `src/tracertm/api/routers/test_run_results.py`
- `src/tracertm/api/routers/coverage.py`
- `src/tracertm/api/routers/qa_metrics.py`

`main.py` now only wires those routers in and no longer owns the duplicated
handlers for `/api/v1/test-cases`, `/api/v1/test-suites`, `/api/v1/test-runs`,
`/api/v1/coverage`, or `/api/v1/qa/metrics`.

## Problem Management Extraction

The problem-management cluster was moved out of `src/tracertm/api/main.py`
into `src/tracertm/api/routers/problems.py`:

- `/api/v1/problems`
- `/api/v1/problems/{problem_id}`
- `/api/v1/problems/{problem_id}/activities`
- `/api/v1/problems/{problem_id}/close`
- `/api/v1/problems/{problem_id}/permanent-fix`
- `/api/v1/problems/{problem_id}/rca`
- `/api/v1/problems/{problem_id}/status`
- `/api/v1/problems/{problem_id}/workaround`
- `/api/v1/projects/{project_id}/problems/stats`

The router keeps the existing auth, rate-limit, repository, and response
shapes intact. `main.py` now only registers the router.

## Documentation and Journeys

Tracera should ship with fun, inspectable demo journeys:

- an onboarding journey from empty repo to first trace graph
- a requirements-to-code-to-test-to-release journey
- a graph scale journey proving 10k/50k behavior
- an agent session/versioning journey with checkpoints and rollback
- an AgilePlus-to-Tracera planning journey once AgilePlus is stable

## Auth Router Split

The public auth lane was separated into `src/tracertm/api/routers/auth_public.py`
for the remaining signup/login routes. The authenticated `me` and `logout`
paths continue to live in the existing `auth.py` router, and the device-flow
routes remain unchanged there as well.
