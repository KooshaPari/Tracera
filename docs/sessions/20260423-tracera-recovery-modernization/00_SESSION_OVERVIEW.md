---
audience: [developers, agents, pms]
status: active
---

# Tracera Recovery and Modernization

## Goals

- Recover the full Tracera implementation after the local `Tracera/` directory was found to be
  a docs-only, down-converted snapshot.
- Establish the live architecture facts before implementation waves.
- Modernize local infrastructure choices without erasing useful product capabilities.
- Stabilize Tracera enough to support complete demo journeys and long-form operator guides.
- Coordinate with AgilePlus completion work after the Tracera recovery baseline is reliable.

## Current Evidence

- Remote source of truth: `https://github.com/KooshaPari/Tracera.git`
- Verified remote `origin/main`: `fefa970ff06ea4d2e0b557d6fd9906054cf80faa`
- Non-destructive recovered checkout: `Tracera-recovered/`
- Current local `Tracera/` remains preserved as the tainted docs-only snapshot.

## Key Findings

- Tracera is active as a Go plus Python backend, React/TypeScript frontend, and a 25-process
  local process-compose stack.
- Live Rust source is not present on current `origin/main`; Rust survives only in archived Tauri
  desktop example material and vendored syntax assets.
- The frontend contains dedicated high-scale graph rendering machinery, including Sigma/WebGL,
  virtualization, LOD, workers, clustering, and performance tests for 10k and 50k node scenarios.
- Traceability, versioning, audit, event, workflow, snapshot, and governance concerns are heavily
  modeled. The system is powerful but currently over-split.
- Promtail is no longer a valid long-term choice and should be replaced with Grafana Alloy.
- Redis should be narrowed to cases where an in-memory Redis-compatible store is truly needed.
  NATS JetStream and PostgreSQL can absorb several current coordination and state duties.

## Implemented This Session

- Replaced the local Promtail process with Grafana Alloy in `config/process-compose.yaml`.
- Added `deploy/monitoring/alloy-local.alloy` and `scripts/shell/alloy-if-not-running.sh`.
- Switched local OTLP app endpoints to Alloy on `127.0.0.1:4319`, with Alloy forwarding to
  Jaeger on `127.0.0.1:4317`.
- Renamed the Alloy trace exporter node from `jaeger` to `tempo` to match the shared
  collector semantics without changing the endpoint.
- Extracted the FastAPI router registration block into
  `src/tracertm/api/router_registry.py` and kept `main.py` as the app wiring surface.
- Migrated `docker-compose.prod.yml` from Jaeger to a self-contained Tempo service and switched
  the Go backend k8s env contract to `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT`.
- Removed the default `trace-backend` process-compose service and renamed the Grafana datasource
  to `deploy/monitoring/grafana/provisioning/datasources/tempo.yml`.
- Made Dragonfly the default Redis-compatible runtime, with `REDIS_COMPAT_PROVIDER=redis` kept
  only for explicit fallback testing.
- Moved Go notification fan-out from Redis pub/sub to NATS JetStream-backed notification events.
- Updated SSE notification docs to describe NATS-backed scaling instead of Redis pub/sub.
- Removed the remaining Jaeger wrapper surfaces from `scripts/shell/` after confirming there were
  no live callers in `config/process-compose.yaml` or other active shell scripts.

## Current Validation

- `process-compose -f config/process-compose.yaml --dry-run --no-server -t=false`
- `bash -n scripts/shell/redis-if-not-running.sh scripts/shell/alloy-if-not-running.sh scripts/shell/check-loki-installation.sh`
- `bash -n scripts/shell/verify-apm-integration.sh`
- semantic process-compose assertions for Alloy, backend dependencies, Tempo datasource wiring,
  and Dragonfly defaulting
- `go test ./internal/nats ./internal/services`

## Active Decisions

- Do not restore Tracera from the shelf root git history; use the real remote repository.
- Keep `Tracera-recovered/` separate until the recovered checkout is clean and validated.
- Treat root case-collision files (`agents.md`, `claude.md`) as recovery hygiene; canonical files
  are `AGENTS.md` and `CLAUDE.md`.
- Stabilize the platform by reducing duplicate infrastructure duties before deep feature work.
- Preserve the rich graph and journey/demo ambitions, but force them through runnable demo projects
  and repeatable validation.
