# Tracera — SPEC

> **Status:** Implemented (v0.2.0)
> **Last audited:** 2026-06-21 against branch `chore/tier-0-hygiene-batch`.
> **Substrate tier:** `app` (multi-stack monorepo).
> **Substrate role:** Agent-native requirements traceability + project management.

---

## 1. What (1 paragraph)

**Tracera** is an agent-native, multi-view Requirements Traceability Matrix
(RTM) and project management system. It binds requirements to code, tests,
deployments, and project artifacts in real time across multiple architectural
lenses (code, API, database, deployment, test). The system is built for
human-agent collaboration and operates at a **critical** quality tier — every
mutation is auditable, every link is signed, every trace is exportable.

## 2. Why (1 paragraph)

Development teams lack unified requirement traceability. Requirements live in
documents, code in Git, tests are scattered across pytest/Jest/go-test, and
deployments are opaque. Tracera unifies these so that:

- A change in code can be traced back to its requirement (impact analysis).
- A requirement can be verified by the tests that exercise it (coverage).
- A deployment can be cross-referenced with the requirements it ships
  (audit / SLSA / compliance).
- AI agents can navigate, query, and update the requirement graph through
  the same API a human would use (MCP substrate).

## 3. How (architecture, ASCII diagram)

```
                  ┌──────────────────────────────┐
                  │       Frontend (TS/Bun)      │
                  │  web / docs / storybook /    │
                  │  desktop / desktop-electrobun│
                  └──────────────┬───────────────┘
                                 │ HTTPS / WS
                                 ▼
                  ┌──────────────────────────────┐
                  │    Backend (Go 1.25)         │
                  │    backend/cmd/tracertm      │
                  │  chi router, agents,         │
                  │  adapters, codeindex, etc.   │
                  └──┬──────────┬──────────┬─────┘
                     │          │          │
       ┌─────────────┘          │          └─────────────┐
       ▼                        ▼                        ▼
  ┌─────────┐            ┌──────────┐            ┌──────────┐
  │Postgres │            │  Neo4j   │            │   NATS   │
  │ (data)  │            │ (graph)  │            │ (events) │
  └─────────┘            └──────────┘            └──────────┘
       ▲                        ▲
       │                        │
       │      ┌─────────────────┴──────────────┐
       │      │  Rust core: crates/tracera-core │
       │      │  traceability-engine / hashing  │
       │      │  (used by both Go + Python)     │
       │      └────────────────────────────────┘
       │
  ┌─────────┐            ┌──────────┐
  │  Redis  │            │  Python  │
  │ (cache) │            │ bindings │
  └─────────┘            └──────────┘
```

## 4. Public Surfaces

### 4.1 Rust core (`crates/tracera-core`)

- `tracera_core` — traceability engine, impact analysis, deterministic
  content hashing. MSRV 1.82, edition 2021, no_std-friendly.
- Library only; no binary entry point. Used by both the Go service (via
  the `traceability-core` upstream substrate) and the Python bindings.

### 4.2 Go backend (`backend/cmd/tracertm`)

- `GET /healthz` — liveness probe (200 `{"status":"ok"}`).
- `GET /readyz` — readiness probe (200 `{"status":"ready"}`).
- `/api/v1/requirements` — CRUD + query.
- `/api/v1/trace` — code-to-requirement trace.
- `/api/v1/coverage` — test coverage per requirement.
- `/api/v1/deployments` — deployment history.
- `/ws` — WebSocket for real-time collaboration.
- `cmd/tracertm` — main entry point.

### 4.3 Python bindings (`pyproject.toml`)

- Package name: `tracertm` — Python 3.12 / 3.13+, hatchling build backend.
- Re-exports the Rust core's API surface for Python.
- Used by pytest, integration tests, and data-science workflows.

### 4.4 Frontend (`frontend/`)

- bun@1.1.38 + Turborepo monorepo.
- Apps: `web` (main), `docs`, `storybook`, `desktop`, `desktop-electrobun`.
- Packages: `ui`, `api-client`, `types`, `state`, `config`, `env-manager`.

## 5. Conventions

- **Branch naming:** `chore/<req-id>-<slug>-<date>` /
  `feat/<req-id>-<slug>-<date>`.
- **Commit messages:** Conventional Commits (`feat:`, `fix:`, `chore:`,
  `docs:`, `refactor:`, `test:`, `build:`, `ci:`).
- **PR labels:** `governance`, `L<n>-#<n>` for DAG-level tracking.
- **Worklog schema:** v2.1 (ADR-025 / ADR-030) — 11 columns including the
  `device:` field (`macbook` / `heavy-runner` / `subagent` / `ci`).
- **Architectural boundaries:** enforced by `tach.toml` (when present) and
  the hexagonal L4 Port/Adapter policy (ADR-038).
- **License:** dual MIT + Apache-2.0.

## 6. Persistence

- **PostgreSQL** — primary data store (`backend/internal/database`).
- **Neo4j** — graph layer for requirement → code → test relations.
- **Redis** — cache + pub/sub for ingestion workers.
- **NATS** — message bus for async pipelines (`backend/cmd/nats-*`).

## 7. Quality Gates (CI)

| Gate | Tool | Threshold |
|---|---|---|
| Rust lint | `cargo clippy --all-targets --all-features -- -D warnings` | zero warnings |
| Rust test | `cargo test` | 100% pass |
| Rust format | `cargo fmt --all -- --check` | no diff |
| Rust license/ban | `cargo deny check` | pass |
| Rust coverage | `cargo llvm-cov` | ≥ 80% (per ADR-040, lib gate) |
| Go test | `go test ./...` | 100% pass |
| Go lint | `golangci-lint run` | zero issues |
| Python lint | `uv run ruff check .` | zero issues |
| Python format | `uv run ruff format . --check` | no diff |
| Python type | `uv run mypy .` | zero errors |
| Python test | `uv run pytest` | 100% pass |
| TS lint | `bun run lint` | zero issues |
| TS type | `bun run typecheck` | zero errors |
| TS test | `bun run test` | 100% pass |
| Secret scan | `trufflehog` (pre-push) | zero findings |
| Commit lint | `conventional-pre-commit` (commit-msg) | pass |

## 8. Phenotype Integration

- **OTLP wire:** exports spans / metrics / logs via `pheno-otel` substrate
  (ADR-037). Sinks to Grafana Alloy → Tempo / Loki / Prometheus.
- **Worklog substrate:** `pheno-worklog-schema` v2.1 (with `device:` field,
  ADR-025 / ADR-030).
- **Agent substrate:** MCP server (50+ tools), `phenotype-skills` plugin
  runtime, `phenotype-observability` for telemetry.
- **Edge deploy:** `nanovms` (per ADR-031 family).
- **71-pillar audit:** tracked in `findings/71-pillar-2026-06-17-*.md` (per
  ADR-024).

## 9. Status

- **Implemented:** all tier-0 surfaces above; observability SLOs in
  `docs/specs/SPEC.md` (Tracera Observability SLO Contract).
- **Test matrix:** unit + integration + e2e + property (proptest in Rust,
  hypothesis in Python).
- **Coverage gate:** 80% (per ADR-040, lib/SDK tier).
- **Pattern conformance:** yes, follows `Port` trait + `Adapter` impl
  (ADR-038) for substrate interop.
- **Observability:** wired via `pheno-otel` (ADR-037) → Alloy → Tempo /
  Loki / Prometheus.

## 10. References

- `README.md` — Project overview.
- `AGENTS.md` — Agent guide (this batch: v22-SD1, 2026-06-21).
- `llms.txt` — Agent-readable project summary.
- `CHANGELOG.md` — Version history.
- `PRD.md` / `docs/PRD.md` — Product Requirements Document.
- `FUNCTIONAL_REQUIREMENTS.md` — Functional requirements index.
- `docs/specs/SPEC.md` — Observability SLO Contract.
- `docs/boundary/Tracera.md` — Boundary snapshot (L7-001).
- `docs/intent/Tracera.md` — Intent snapshot (L7-001).
- ADR-023 — Agent-effort governance (substrate placement + Rule 3.1).
- ADR-024 — 71-pillar audit framework.
- ADR-025 / ADR-030 — pheno-worklog-schema v2.1 (WORKLOG.md `device:` field).
- ADR-037 — pheno-otel OTLP wire.
- ADR-038 — Hexagonal L4 Port/Adapter policy.
- ADR-040 — Test coverage gates per tier (80% lib/SDK).
