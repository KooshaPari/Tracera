---
audience: [developers, agents]
status: active
---

# Research

## Repository Recovery

- Local `Tracera/` is docs-only and has no `.git`, no live backend, and no frontend source.
- GitHub repo `KooshaPari/Tracera` contains the full implementation.
- Remote `origin/main` includes `backend/`, `src/tracertm/`, `frontend/`, `config/`,
  `process-compose.yml`, `config/process-compose.yaml`, `pyproject.toml`, `backend/go.mod`,
  and `frontend/package.json`.
- A recovered checkout was created at `Tracera-recovered/` so recovery work can proceed without
  replacing the tainted local snapshot.

## Rust Evidence

- No live `.rs`, `Cargo.toml`, or `Cargo.lock` exists outside archive/vendor paths on current
  `origin/main`.
- Rust is present in archived Tauri desktop example material under
  `ARCHIVE/EXAMPLES/desktop/src-tauri/`.
- Rust is also mentioned through vendored syntax-highlighting assets in archived dependency
  snapshots.
- Interpretation: the user's memory of Rust incorporation is credible historically, but the live
  remote has lost or archived that surface.

## Frontend Graph Performance

- The frontend has specialized graph rendering components:
  - `frontend/apps/web/src/components/graph/SigmaGraphView.tsx`
  - `frontend/apps/web/src/components/graph/VirtualizedGraphView.tsx`
  - `frontend/apps/web/src/components/graph/StreamingGraphView.tsx`
  - `frontend/apps/web/src/components/graph/ClusteredGraphView.tsx`
  - `frontend/apps/web/src/components/graph/HybridGraphView.tsx`
- It has performance infrastructure:
  - graph workers
  - GPU force layout
  - LOD utilities
  - Sigma/WebGL rendering
  - rbush/d3-quadtree type dependencies
- E2E tests explicitly target:
  - 10k nodes at 60 FPS
  - 50k nodes in performance mode
  - LOD transitions
  - memory behavior

## Traceability and Versioning Surface

- Traceability/versioning concerns are spread across services such as traceability matrix,
  event sourcing, history, temporal workflows, graph snapshots, advanced traceability, and MCP tools.
- Related models cover events, graph changes, graph snapshots, requirements, specifications,
  workflow runs, test runs, and coverage.
- `.trace/` has hundreds of artifacts and phase/status records.
- Interpretation: the architecture is a platform, not a narrow app. Completion requires
  consolidation and strong routing boundaries, not more parallel abstractions.

## Infrastructure Modernization Sources

- Grafana Promtail is end-of-life as of March 2, 2026:
  https://grafana.com/docs/loki/latest/send-data/promtail/
- Grafana documents migration from Promtail to Alloy:
  https://grafana.com/docs/alloy/latest/tasks/migrate/from-promtail/
- Grafana Alloy is an OpenTelemetry Collector distribution that can collect metrics, logs,
  traces, and profiles:
  https://grafana.com/docs/alloy/latest/introduction/
- The local trace datasource is already Tempo-backed; the remaining drift lives in the default
  process graph and live docs/scripts.
- The Alloy OTLP exporter node can be renamed from `jaeger` to `tempo` without changing the
  endpoint, which reduces legacy coupling in the active collector config.
- The prod-like Docker Compose stack can run Tempo directly using the shared collector contract
  (`PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=tempo:4317`) and a local Tempo config file.
- NATS JetStream provides streams, key/value, object store, watch, history, and atomic updates:
  https://docs.nats.io/nats-concepts/jetstream
  https://docs.nats.io/nats-concepts/jetstream/key-value-store
- Dragonfly is documented as Redis and Memcached API compatible with a multi-threaded
  architecture:
  https://www.dragonflydb.io/docs

## Jaeger Wrapper Removal Audit

- `scripts/shell/jaeger-if-not-running.sh` and `scripts/shell/readiness-jaeger.sh` were the only
  live shell wrappers carrying Jaeger-specific default-path text.
- `config/process-compose.yaml` does not reference either wrapper and already routes observability
  through Alloy plus Tempo/shared tracing storage.
- `scripts/shell/verify-apm-integration.sh` and `scripts/shell/alloy-if-not-running.sh` are already
  aligned to the shared collector model.
- The remaining `jaeger` mentions found by repo search are in historical report docs, not active
  boot or readiness scripts.
