# Tracera Architecture

> Canonical architecture for Tracera — the Phenotype-org trace + observability +
> audit ledger for agentic and LLM workflows. Companion: `docs/CONTRIBUTING.md`.
> The repo-root `ARCHITECTURE.md` is the long-form design narrative; this
> document is the operator-facing component map kept aligned to the current
> `Cargo.toml` / `frontend/package.json` state.

## 1. System Overview

Tracera is a **hexagonal trace-link matrix** for agentic + LLM observability:
it captures structured trace-links across runs, distills short-term and
long-term memory, and serves an Electrobun/Tauri desktop viewer plus a web UI
over the session history.

The supported runtime is the **Rust workspace**. Older Python/FastAPI code is
retained as historical migration material only.

Three language surfaces plus a container platform:

| Surface | Location | Role |
|---------|----------|------|
| Rust (Cargo workspace) | `crates/*`, `src/` | Server, MCP, edge worker, events, atlas, CLI |
| TypeScript (bun + Turborepo) | `frontend/` | Web app, desktop shell, shared packages |
| Go/Python (auxiliary) | `sidecar/go/`, `alembic/`, `migrations/` | Sidecar, legacy migration, schema tooling |
| Local platform | `docker-compose.dev.yml`, `Taskfile.yml` | 27-service dev stack (DBs, graph, streams, observability) |

## 2. Component Inventory

### 2.1 Rust workspace (`Cargo.toml`)

`resolver = "2"`, edition 2021, `rust-version = "1.82"`, license
`MIT OR Apache-2.0`. Distribution via **cargo-dist 0.28.0** (GitHub CI,
shell + powershell + msi installers; targets: x86_64-pc-windows-msvc,
x86_64-unknown-linux-gnu, aarch64-apple-darwin, x86_64-apple-darwin).

Workspace members:

| Member | Responsibility |
|--------|----------------|
| `tracera-server` | Core HTTP server (axum 0.8): traceability, impact, coverage, evidence, ingest, memory, SWEE graph, dual store (SQLite + Postgres via sqlx 0.9), auth, Redis cache, R2 object store. |
| `tracera-mcp` | MCP server over stdio exposing SWEE graph read/write/navigate/propose tools backed by the server's `Store` trait. |
| `tracertm-mcp` | Native Rust MCP stdio server, replacing the legacy `python -m tracertm.mcp`. |
| `tracera-edge` | Cloudflare Worker edge API (deployed to `tracera-edge.pheno.studio`). |
| `tracera-cli` | Manages the bundled/local Tracera Compose stack across docker, podman, apple-container, and WSL2 runtimes. |
| `tracera-events` | ClickHouse-backed ingest/analytics for agent_runs, decisions, deploys, traces, llm_calls. |
| `tracera-workos` | WorkOS integration: AuthKit hosted login, webhook handling (HMAC), directory sync, audit-log ingest. |
| `tracera-atlas` | Atlas ALM: WorkItem delegation, SDLC observability, agent-of-record, CI bridge. |
| `mock-agcord` | Mock AgCord server returning AgCord-compatible JSON for `/ingest/agileplus`. |

Additional `crates/` trees present but **not** in the workspace member list:
`tracera-graphql` (GraphQL gateway mirroring REST + graph subscriptions),
`tracera-ml` (embeddings, Qdrant + pgvector, RAG), `tracera-neo4j` (SWEE graph
sync/queries), `tracera-go-cli`, `tracera-py-sdk`.

`tracera-server` module map: `handlers/`, `ingest/`, `memory/`, `pg_store/`,
`sqlite_store/`, `traceability/`, `queue/`, plus `swee.rs`, `graph.rs`,
`store.rs`, `datastore.rs`, `db.rs`, `auth.rs`, `cache.rs`, `neo4j.rs`,
`r2.rs`, `events.rs`, `health.rs`, `middleware.rs`, `observability.rs`,
`router.rs`, `validation.rs`. The `phenodag-queue` cargo feature is opt-in
until its HTTP/service wiring is complete (see ADR-DEP-001).

### 2.2 Frontend monorepo (`frontend/`)

**bun workspaces + Turborepo** (`frontend/package.json` name
`tracertm-frontend`):

| Workspace | Purpose |
|-----------|---------|
| `apps/web` | React 19 + TanStack Router SPA (Vite; OpenAPI types generated from `public/specs/openapi.json` via `openapi-typescript`). |
| `apps/desktop` | Electrobun desktop viewer (`tracera-desktop`). |
| `apps/tauri-desktop` | Tauri desktop shell (Rust `Cargo.toml` + `src-tauri/` + `tauri.conf.json`). |
| `apps/os-service` | Rust crate for OS-level service integration. |
| `packages/api-client`, `packages/config`, `packages/env-manager`, `packages/state`, `packages/tokens`, `packages/types`, `packages/ui` | Shared client, config, state, design tokens, and UI library. |

Tooling: **oxlint** (+ oxlint-tsgolint) and **oxfmt** for lint/format,
stylelint for CSS, Vitest for unit tests, Playwright for e2e/visual tests,
Storybook + Chromatic (and Percy) for visual review, bun as package manager and
runtime, Turborepo for task orchestration.

### 2.3 Local platform (`docker-compose.dev.yml`)

The dev stack defines ~27 services including postgres17, redis7, dragonfly,
nats-jetstream, minio, rabbitmq (management + streams), meilisearch,
clickhouse, qdrant, opensearch, neo4j5, temporal, kafka/zookeeper, vault,
jaeger, loki, prometheus, grafana, keycloak, mailhog, traefik, mongodb7,
elasticsearch, and `atlassian-statuspage-mock`.

## 3. Data / Control Flow

```text
 agent runs / CI / dev tools
      |
      +--> tracera-ingest (ClickHouse)         [tracera-events]
      +--> /ingest/agileplus (AgCord JSON)     [mock-agcord for tests]
      |
      v
 tracera-server (axum, :8080)
      |-- traceability: /api/v1/trace/{forward,reverse}/{artifact_id}
      |-- impact:       /api/v1/impact, /api/v1/blast-radius
      |-- coverage:     /api/v1/coverage-matrix
      |-- evidence:     /evidence (+ health)
      |-- SWEE graph:   graph.rs + neo4j sync + dual store
      |-- memory:       memory/ (short-term + long-term distillation)
      |-- auth:         AuthKit via tracera-workos (+ signed webhooks)
      |
      +--> stores: sqlite (local) | postgres (sqlx) | neo4j (graph) | qdrant/pgvector (RAG)
      +--> cache/objects: redis | R2 (r2.rs)
      |
      v
 consumers: frontend/apps/web + desktop, tracera-mcp / tracertm-mcp (stdio),
            tracera-graphql (REST mirror), Cloudflare edge worker
```

Operational probes: `GET /health`, `/ready`, `/healthz`, `/readyz`. The
authoritative route inventory and mount status live in
`docs/governance/policy/endpoint_traceability_map.md`; `docs/API_REFERENCE.md`
is the audit-facing target contract, not a claim that every route is mounted.

Deployment surfaces (canonical URIs):
- API `https://tracera.pheno.studio/api/*`
- MCP `https://mcp.tracera.pheno.studio`
- Edge `https://tracera-edge.pheno.studio`
- Web app `https://app.tracera.pheno.studio`
- Landing `https://phenotype.space` (separate repo)

## 4. Key Dependencies

- **PhenoInfra** shared infrakit crates (git `rev dd040ed1`):
  `phenotype-crypto`, `phenotype-telemetry`, `phenotype-git-core`,
  `phenotype-health`, `phenotype-observability`.
- axum 0.8 / tower-http, sqlx 0.9 (postgres + sqlite + migrations),
  metrics-exporter-prometheus, tracing.
- ClickHouse (analytics), Neo4j (SWEE graph), Qdrant/pgvector (RAG),
  Redis/Dragonfly (cache), NATS/Temporal/Kafka (events/queue).
- WorkOS (AuthKit + directory sync + audit logs); Cloudflare Workers (edge).
- Frontend: bun, Turborepo, Vite, React 19 + TanStack Router, openapi-typescript,
  Vitest/Playwright, Storybook/Chromatic, oxlint/oxfmt; Electrobun desktop;
  Tauri shell.

## 5. Build / Run Topology

`task` is the canonical entrypoint (Sep-2026 rule; `make` is a one-line
forwarder). See `Taskfile.yml` and `Makefile`.

```bash
# Rust workspace
cargo build --workspace
cargo test --workspace
cargo check --workspace
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings

# Local platform + runtime (Makefile targets)
task stack          # docker compose -f docker-compose.dev.yml up -d
task stack-seed     # seed fixtures
task run-server     # cargo run -p tracera-server   (:8080)
task mcp-server     # cargo run -p tracera-mcp --bin mcp-server
task tunnel         # hybrid Tailnet-first, Cloudflare fallback
task prod           # stack + run-server + tunnel

# Frontend
cd frontend && bun install
cd frontend && bun run dev            # apps/web
cd frontend && bun run build          # turbo build --filter=@tracertm/web
cd frontend && bun run check          # lint + format:check + typecheck
```

Note: `Taskfile.yml` documents that on some hosts the verified container
runtime is rootful `podman-compose` inside WSL (`FedoraLinux-44`); the host
Docker Desktop socket and podman-machine may be broken. Prefer `task stack`
over raw `docker compose` when the socket is unreliable.

## 6. Governance & Quality

- ADRs live in `docs/governance/` (hexagonal architecture, dual-store
  strategy, phenodag absorption, graph ingestion, signed commits branch
  protection, OpenTelemetry adoption, SWEE graph schema, test coverage policy,
  mutation testing).
- CI: `.github/workflows/` (33 workflows) covering rust/go/python/typescript
  lint + test, coverage, mutants, codeql, dependency audit, trunk-check, e2e,
  frontend-contract-checks, sidecar-bootstrap-checks, deploy (cloudflare /
  render / vercel / full-stack), and release (dist, crates, desktop signing).
- Audit outputs land in `audit/`; per-service SLOs in `docs/SLO.md`.