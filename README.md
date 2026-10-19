<h1 align="center">Tracera</h1>

<p align="center">
  <a href="assets/brand/icon.svg"><img src="assets/brand/icon.svg" alt="Tracera" width="160" height="160"></a>
</p>
<p align="center"><em>Hexagonal trace-link matrix for agentic + LLM observability — Rust core, React web UI, Electrobun/Tauri desktop.</em></p>
<p align="center"><sub>Tracera palette (navy + teal + indigo) · <a href="assets/brand/favicon.svg">favicon</a> · <a href="docs/assets/identity/">visual identity demo</a></sub></p>

<p align="center">
  <a href="https://github.com/KooshaPari/Tracera/releases"><img src="https://img.shields.io/github/v/release/KooshaPari/Tracera?sort=semver" alt="Release"></a>
  <a href="https://github.com/KooshaPari/Tracera/releases"><img src="https://img.shields.io/github/downloads/KooshaPari/Tracera/total" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
  <a href="Cargo.toml"><img src="https://img.shields.io/badge/rust-1.82%2B-orange" alt="Rust 1.82+"></a>
  <a href="frontend/package.json"><img src="https://img.shields.io/badge/frontend-bun%20%2B%20React%2019-black" alt="Frontend"></a>
</p>

---

## What Tracera is

Tracera is the Phenotype-org **trace + observability + audit ledger** for
agentic and LLM workflows. It captures structured trace-links across runs,
distills short-term and long-term memory, and serves a web UI plus an
Electrobun/Tauri desktop viewer over that session history.

The problem it solves: agent and LLM pipelines generate artifacts (runs,
decisions, deploys, traces, LLM calls) whose provenance is normally scattered
across logs, CI systems, and chat transcripts. Tracera gives those artifacts a
single, queryable trace-link matrix so you can answer:

- **What is this artifact connected to?** Forward/reverse trace traversal across a SWEE graph.
- **What is the blast radius of a change?** Impact and blast-radius analysis over trace links.
- **Is coverage complete?** Coverage-matrix generation from persisted trace links.
- **Who or what produced this?** Evidence records, agent-of-record, and signed webhook ingest.

The supported runtime is the **Rust workspace**. Older Python/FastAPI
(`tracertm`) code is retained only as historical migration material; see
[`docs/FEATURE_INVENTORY.md`](docs/FEATURE_INVENTORY.md) for the migration-safety oracle.

## Key capabilities

- **Trace-link matrix** — forward/reverse trace traversal, impact analysis,
  blast-radius scoring, and coverage-matrix generation (`crates/tracera-server`).
- **Dual-store persistence** — SQLite for on-device/local, PostgreSQL (sqlx) for
  hosted, behind a single `Store` trait (`ADR-DATA-001`).
- **SWEE graph** — graph read/write/navigate/propose surface with Neo4j sync.
- **Agent memory** — short-term capture plus long-term distillation (`memory/`).
- **Events + analytics** — ClickHouse-backed ingest for `agent_runs`,
  `decisions`, `deploys`, `traces`, and `llm_calls` (`crates/tracera-events`).
- **MCP servers** — Model Context Protocol stdio servers exposing the SWEE
  graph tools to agents (`crates/tracera-mcp`, `crates/tracertm-mcp`).
- **Auth + audit** — WorkOS AuthKit hosted login, HMAC-signed webhooks,
  directory sync, and audit-log ingest (`crates/tracera-workos`).
- **Edge + GraphQL** — Cloudflare Worker edge API and a GraphQL gateway
  mirroring the REST surface with graph subscriptions.
- **Polyglot clients** — Rust CLI, Go CLI, and Python SDK for driving the stack.
- **Desktop + web viewers** — React 19 + TanStack Router SPA, Electrobun
  desktop shell, and a Tauri shell.

## Quickstart

Prerequisites: Rust ≥ 1.82 (per `rust-toolchain.toml`), and — for the full
stack — Docker/podman plus `task` (see [`Taskfile.yml`](Taskfile.yml)).

### 1. Build and run the server directly (fastest path)

```bash
cargo build --release -p tracera-server
export TRACERA_BIND_ADDR=127.0.0.1:8080
export TRACERA_DB_PATH=/tmp/tracera-quickstart.db
./target/release/tracera-server
```

Verify the probes:

```bash
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/ready
curl -i http://127.0.0.1:8080/evidence
```

`/health`, `/ready`, `/healthz`, and `/readyz` are public. All other routes
require `Authorization: Bearer <TRACERA_AUTH_TOKEN>`. Do not expose port 8080
directly — terminate auth at the ingress (see [Deployment](#deployment)).

### 2. Full local platform (dev compose, ~27 services)

```bash
task stack          # docker compose -f docker-compose.dev.yml up -d
task stack-seed     # seed fixtures
task run-server     # cargo run -p tracera-server   (:8080)
task mcp-server     # cargo run -p tracera-mcp --bin mcp-server (:8081)
task prod           # stack + run-server + tunnel ("go live locally")
```

`task` is the canonical entrypoint; `make` is a one-line forwarder. Host note:
on some machines the verified container runtime is rootful `podman-compose`
inside WSL (`FedoraLinux-44`) because the host Docker socket is unreliable —
prefer `task stack` over raw `docker compose` there.

### 3. Frontend

```bash
cd frontend && bun install
cd frontend && bun run dev        # apps/web dev server
cd frontend && bun run build      # turbo build --filter=@tracertm/web
```

See [`docs/quickstart.md`](docs/quickstart.md) for the full bootstrap and
[`docs/01-getting-started/`](docs/01-getting-started/README.md) for a CLI walkthrough.

## Architecture

Tracera is a **hexagonal trace-link matrix**: domain logic is isolated from
adapters (HTTP, stores, queues, caches) so persistence and transports can be
swapped without touching trace semantics.

```
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

The authoritative route inventory and mount status live in
[`docs/governance/policy/endpoint_traceability_map.md`](docs/governance/policy/endpoint_traceability_map.md).
[`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) is the audit-facing **target**
contract, not a claim that every route is mounted.
The full design narrative is in [`ARCHITECTURE.md`](ARCHITECTURE.md) (long-form)
and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (operator-facing component map).

## Component map

### Rust workspace (`Cargo.toml`)

`resolver = "2"`, edition 2021, MSRV 1.82. Distribution via **cargo-dist
0.28.0** (shell + powershell + msi installers).

| Crate                   | Binary           | Responsibility                                                                                                            |
| ----------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `crates/tracera-server` | `tracera-server` | Core axum HTTP server: traceability, impact, coverage, evidence, ingest, memory, SWEE graph, dual store, auth, cache, R2. |
| `crates/tracera-mcp`    | `mcp-server`     | MCP stdio server exposing SWEE graph read/write/navigate/propose tools over the server `Store` trait.                     |
| `crates/tracertm-mcp`   | `tracertm-mcp`   | Native Rust MCP stdio server, replacing the legacy `python -m tracertm.mcp`.                                              |
| `crates/tracera-edge`   | (cdylib)         | Cloudflare Worker edge API for Tracera.                                                                                   |
| `crates/tracera-cli`    | `tracera`        | Manages the bundled/local Compose stack across docker, podman, apple-container, and WSL2 runtimes.                        |
| `crates/tracera-events` | `events-ingest`  | ClickHouse-backed ingest/analytics for agent runs, decisions, deploys, traces, LLM calls.                                 |
| `crates/tracera-workos` | `workos-mock`    | WorkOS AuthKit login, HMAC webhooks, directory sync, audit-log ingest.                                                    |
| `crates/tracera-atlas`  | `atlas-server`   | Atlas ALM: WorkItem delegation, SDLC observability, agent-of-record, CI bridge.                                           |
| `crates/mock-agcord`    | (test)           | Mock AgCord server returning AgCord-compatible JSON for `/ingest/agileplus`.                                              |

Additional `crates/` trees present but **not** workspace members (built
separately): `tracera-graphql` (GraphQL gateway + subscriptions),
`tracera-ml` (embeddings, Qdrant + pgvector, RAG), `tracera-neo4j` (SWEE graph
sync/queries), `tracera-go-cli`, `tracera-py-sdk`.

`tracera-server` module map: `handlers/`, `ingest/`, `memory/`, `pg_store/`,
`sqlite_store/`, `traceability/`, `queue/`, plus `swee.rs`, `graph.rs`,
`store.rs`, `datastore.rs`, `db.rs`, `auth.rs`, `cache.rs`, `neo4j.rs`,
`r2.rs`, `events.rs`, `health.rs`, `middleware.rs`, `observability.rs`,
`router.rs`, `validation.rs`. The `phenodag-queue` cargo feature is opt-in until
its HTTP/service wiring completes (`ADR-DEP-001`).

### Frontend monorepo (`frontend/`, bun workspaces + Turborepo)

| Workspace                                                        | Purpose                                                                                          |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `apps/web`                                                       | React 19 + TanStack Router SPA (Vite; OpenAPI types generated from `public/specs/openapi.json`). |
| `apps/desktop`                                                   | Electrobun desktop viewer.                                                                       |
| `apps/tauri-desktop`                                             | Tauri desktop shell.                                                                             |
| `apps/os-service`                                                | OS-level service integration crate.                                                              |
| `packages/{api-client,config,env-manager,state,tokens,types,ui}` | Shared client, config, state, design tokens, and UI library.                                     |

Tooling: oxlint/oxfmt, stylelint, Vitest, Playwright, Storybook + Chromatic,
bun, Turborepo.

### Other surfaces

- `sidecar/go/` — Go sidecar (`tracera-sidecar`).
- `src/tracertm/` — historical Python service (migration material).
- `desktop/` — Electrobun desktop entrypoint.
- `docker-compose.dev.yml` + `Taskfile.yml` — the ~27-service local platform.
- `.github/workflows/` — 33 CI workflows (rust/go/python/typescript lint+test,
  coverage, mutants, CodeQL, dependency audit, trunk-check, e2e, deploys, releases).

## Documentation map

| Guide                                 | Location                                                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Quickstart                            | [`docs/quickstart.md`](docs/quickstart.md)                                                                   |
| Getting started + CLI tutorial        | [`docs/01-getting-started/README.md`](docs/01-getting-started/README.md)                                     |
| Architecture (long-form)              | [`ARCHITECTURE.md`](ARCHITECTURE.md)                                                                         |
| Architecture (component map)          | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)                                                               |
| API reference (target contract)       | [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)                                                             |
| Endpoint traceability (FR→route→test) | [`docs/governance/policy/endpoint_traceability_map.md`](docs/governance/policy/endpoint_traceability_map.md) |
| Guided + deployment guides            | [`docs/04-guides/`](docs/04-guides/DEVELOPER_GUIDE.md)                                                       |
| Governance / ADRs                     | [`docs/governance/README.md`](docs/governance/README.md)                                                     |
| Feature inventory (migration oracle)  | [`docs/FEATURE_INVENTORY.md`](docs/FEATURE_INVENTORY.md)                                                     |
| WBS + work packages                   | [`docs/WBS.md`](docs/WBS.md), [`docs/WP-00-reconciliation.md`](docs/WP-00-reconciliation.md)                 |
| Specifications                        | [`docs/specs/`](docs/specs)                                                                                  |
| Security                              | [`SECURITY.md`](SECURITY.md), [`docs/security/`](docs/security/SECURITY.md)                                  |
| Self-hosted deployment                | [`deploy/selfhost/README.md`](deploy/selfhost/README.md)                                                     |
| Changelog                             | [`CHANGELOG.md`](CHANGELOG.md)                                                                               |

## Development

```bash
# Rust — build, check, test, lint
cargo build --workspace
cargo check --workspace
cargo test --workspace
cargo test -p tracera-server
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings

# Makefile aliases
make build / make check / make test / make fmt / make clippy

# Frontend
cd frontend && bun install
cd frontend && bun run check        # lint + format:check + typecheck
cd frontend && bun run test         # turbo test
cd frontend && bun run test:a11y
cd frontend && bun run test:perf

# Python (migration material)
uv run pytest

# Go sidecar
cd sidecar/go && go test ./...
```

Lefthook (`lefthook.yml`) runs rustfmt/clippy on Rust, prettier on frontend
assets, ruff-format on Python, and commit-msg validation.

## Deployment

| Surface     | Canonical URI                        |
| ----------- | ------------------------------------ |
| API         | `https://tracera.pheno.studio/api/*` |
| MCP         | `https://mcp.tracera.pheno.studio`   |
| Edge worker | `https://tracera-edge.pheno.studio`  |
| Web app     | `https://app.tracera.pheno.studio`   |

Self-hosted stack: Tracera server + Caddy (TLS + security headers) + Cloudflare
Tunnel — see [`deploy/selfhost/README.md`](deploy/selfhost/README.md). The Rust
gateway refuses non-loopback binding unless `TRACERA_PUBLIC_BIND_MODE` is
`authenticated-proxy`, and requires a non-empty `TRACERA_AUTH_TOKEN`.
Also available: [`deploy/kubernetes/`](deploy/kubernetes/Chart.yaml).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).
Conventional Commits (`type(scope): subject`); every commit carries
immutable-ledger trailers (`tx-agent`, `tx-task`, `tx-validated`, `tx-scope`,
`tx-intent`). Local gates before pushing:

```bash
cargo fmt --all && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace
cd frontend && bun run check && bun run test
```

## License

MIT — see [`LICENSE`](LICENSE). The Cargo workspace metadata declares
`MIT OR Apache-2.0`.
