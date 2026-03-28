# TracerTM — Architecture Decision Records

**Project**: TracerTM (Requirements Traceability Matrix)
**Document Version**: 1.0
**Last Updated**: 2026-03-27
**Status**: Active

This document collects all architecture decisions made for TracerTM. Each ADR has a status
(`Proposed`, `Accepted`, `Deprecated`, `Superseded`) and traces to one or more PRD features.

Individual extended ADR documents live in `docs/adr/`.

---

## ADR Index

| ID      | Title                                    | Status   | PRD Feature  |
|---------|------------------------------------------|----------|--------------|
| ADR-001 | Polyglot Backend Architecture            | Accepted | All          |
| ADR-002 | Echo v4 as Go HTTP Framework             | Accepted | F1, F3, F9   |
| ADR-003 | PostgreSQL + Neo4j + Redis Persistence   | Accepted | F1–F12       |
| ADR-004 | NATS JetStream for Messaging             | Accepted | F8, F10      |
| ADR-005 | TanStack Router + React 19 Frontend      | Accepted | F3, F6, F8   |
| ADR-006 | Geist Design System                      | Accepted | F3, F6, F8   |
| ADR-007 | FastMCP 2.14 for MCP Protocol            | Accepted | F2, F7       |
| ADR-008 | WebSocket for Real-Time Collaboration    | Accepted | F8           |
| ADR-009 | JWT + OAuth2/OIDC Authentication         | Accepted | F9           |
| ADR-010 | SLSA Provenance and Attestation          | Accepted | F12          |
| ADR-011 | Caddy as Unified Gateway                 | Accepted | All          |
| ADR-012 | Prometheus + Loki + Jaeger Observability | Accepted | F13          |
| ADR-013 | Process Compose for Local Orchestration  | Accepted | Dev          |
| ADR-014 | Layered Transformation Migration         | Accepted | All          |
| ADR-015 | Tach for Architecture Boundary Enforcement | Accepted | Dev        |

---

## ADR-001: Polyglot Backend Architecture

**Status**: Accepted
**Date**: 2026-01-28
**PRD Traces**: All features

### Context

TracerTM requires high throughput for core API workloads, graph traversal performance, and
specialized data analysis pipelines. No single language excels at all three.

### Decision

Use a polyglot backend:
- **Go** (`backend/`): Core API server, business logic, RBAC, webhook ingestion.
  Primary runtime: Echo v4 over HTTP/2.
- **Python** (`src/`): Data analysis pipelines, CLI/TUI tooling, MCP server (FastMCP),
  background enrichment jobs.

Both services share the same PostgreSQL and Neo4j instances and communicate via NATS
JetStream for async work.

### Rationale

- Go provides sub-millisecond latency for synchronous API calls.
- Python provides mature data science libraries (pandas, networkx) for graph analytics.
- NATS decouples services without shared memory.

### Consequences

- Two separate build pipelines (go build, uv/pip).
- Two Dockerfiles; process-compose manages both in local dev.
- Shared schema owned by Go migrations (Atlas); Python reads via SQLAlchemy.

---

## ADR-002: Echo v4 as Go HTTP Framework

**Status**: Accepted
**Date**: 2026-01-28
**PRD Traces**: Feature 1, Feature 3, Feature 9

### Context

Go HTTP framework choice affects routing ergonomics, middleware composability, and
WebSocket integration.

### Decision

Use `github.com/labstack/echo/v4`. Gorilla Mux retained for legacy route groups during
transition.

### Rationale

- Echo provides built-in middleware (CORS, JWT, rate-limit, request ID).
- WebSocket upgrade via gorilla/websocket integrates cleanly into Echo handlers.
- Group-scoped middleware simplifies RBAC enforcement per route prefix.

### Consequences

- Gorilla Mux routes to be migrated to Echo groups incrementally.
- All new handlers must use Echo context (`echo.Context`).

---

## ADR-003: PostgreSQL + Neo4j + Redis Persistence

**Status**: Accepted
**Date**: 2026-01-28
**PRD Traces**: Features 1–12

### Context

TracerTM manages three distinct data shapes: relational (requirements, users, projects),
graph (dependency DAGs, impact paths), and ephemeral (session caches, WebSocket state).

### Decision

Three-tier persistence:
- **PostgreSQL 17** (`pgx/v5`): Source of truth for all domain entities. Migrations via
  Atlas HCL (`backend/atlas.hcl`).
- **Neo4j 5.0** (`neo4j-go-driver/v5`): Graph store for requirement dependency DAGs,
  impact analysis traversals, and critical path queries.
- **Redis 7** (`go-redis`): Session cache, WebSocket presence, distributed rate-limit
  counters.

### Rationale

- Relational integrity (foreign keys, transactions) required for audit logs and RBAC.
- Cypher queries over Neo4j outperform recursive CTEs for deep graph traversal (>5 hops).
- Redis provides sub-millisecond latency for presence and rate-limit checks.

### Consequences

- Three infrastructure dependencies for local dev (managed by process-compose).
- Neo4j and PostgreSQL must be kept in sync; dual-write on requirement create/update.
- Schema migrations are Go-owned; Python services must not perform DDL.

---

## ADR-004: NATS JetStream for Messaging

**Status**: Accepted
**Date**: 2026-02-01
**PRD Traces**: Feature 8, Feature 10

### Context

Async workloads (webhook ingestion, CI/CD result ingestion, coverage aggregation) must be
decoupled from synchronous API handlers. A message bus is required.

### Decision

Use **NATS JetStream** (`nats.go v1.48`). Subjects follow the convention
`tracertm.<service>.<entity>.<action>` (e.g., `tracertm.backend.requirement.created`).

### Rationale

- NATS is lightweight (<10 MB binary) and embeds well for local dev.
- JetStream persistence guarantees at-least-once delivery across restarts.
- Python consumers use `nats-py` for background workers.

### Consequences

- NATS becomes a required infrastructure dependency (non-optional).
- All async consumers must implement idempotent handlers (duplicate message safe).
- Dead-letter subject: `tracertm.dlq.*` for failed messages.

---

## ADR-005: TanStack Router + React 19 Frontend

**Status**: Accepted
**Date**: 2026-01-30
**PRD Traces**: Feature 3, Feature 6, Feature 8

### Context

Frontend requirements include complex nested routing (project → requirement → lens), type-safe
data fetching, and real-time collaborative views.

### Decision

- **React 19** with concurrent features and server components where applicable.
- **TanStack Router v1** for type-safe file-based routing.
- **TanStack Query v5** for server-state management.
- **Zustand** for ephemeral client state (WebSocket presence, optimistic updates).
- **Vite 8** build toolchain.

### Rationale

- TanStack Router provides full type inference for route parameters and search params.
- React 19 concurrent rendering improves perceived performance for large RTM matrices.
- Zustand is minimal and avoids Redux boilerplate for local UI state.

### Consequences

- All routes must be declared under `frontend/apps/` following TanStack Router file
  conventions.
- Server-state (requirements, coverage) fetched via TanStack Query; never stored in Zustand.

---

## ADR-006: Geist Design System

**Status**: Accepted
**Date**: 2026-02-05
**PRD Traces**: Feature 3, Feature 6, Feature 8

### Context

TracerTM requires a cohesive, dark-mode-first design language. Custom component libraries
are out of scope.

### Decision

Use **Geist** (`geist v1.7`) as the base design system. Supplement with Radix UI primitives
for accessible components not covered by Geist.

### Rationale

- Geist provides a professional, monochrome-first aesthetic aligned with developer tooling.
- Radix UI offers headless, accessible primitives (dialogs, tooltips, popovers).
- No custom CSS component library to maintain.

### Consequences

- All new UI components must use Geist tokens and Radix primitives.
- Plain HTML forms are prohibited; every input must use a component from Geist or Radix.

---

## ADR-007: FastMCP 2.14 for MCP Protocol

**Status**: Accepted
**Date**: 2026-02-10
**PRD Traces**: Feature 2 (Multi-Lens), Feature 7 (Spec Verification)

### Context

AI agents (Claude, Gemini, Codex) must consume TracerTM data programmatically. The MCP
(Model Context Protocol) provides a standard interface for tool-calling.

### Decision

Implement a Python MCP server using **FastMCP 2.14** (`src/` service). Tools exposed:
- `get_requirement(id)`: fetch requirement with all links.
- `get_coverage_matrix(project_id)`: return RTM coverage summary.
- `run_spec_verification(project_id)`: trigger and return spec verification report.
- `link_requirement_to_code(req_id, file_path, start_line, end_line)`: create code link.

### Rationale

- FastMCP abstracts the MCP wire protocol; tool functions are plain Python.
- Python chosen for MCP layer because LLM ecosystem libraries are Python-native.
- Decoupled from Go API — MCP server calls Go REST API internally.

### Consequences

- MCP server is a separate Python process, not embedded in Go.
- MCP tools must be kept in sync with Go API contract changes.
- Tool function signatures must be fully type-annotated (pydantic models).

---

## ADR-008: WebSocket for Real-Time Collaboration

**Status**: Accepted
**Date**: 2026-02-01
**PRD Traces**: Feature 8

### Context

Multiple users editing requirements simultaneously requires real-time propagation of changes
without polling.

### Decision

Use **WebSocket** via `gorilla/websocket` on the Go backend. Hub pattern: per-project
connection pool. Events published to NATS; hub fans out to connected clients.

### Rationale

- WebSocket provides bidirectional full-duplex channel, eliminating polling.
- NATS fan-out decouples write path (API handler) from broadcast path (WebSocket hub).
- Conflict resolution: last-write-wins for field-level updates; explicit UI prompt for
  structural changes (new links, status transitions).

### Consequences

- WebSocket connections must authenticate via JWT on upgrade handshake.
- Connection state tracked in Redis (presence map).
- Graceful reconnect with exponential backoff required on frontend.

---

## ADR-009: JWT + OAuth2/OIDC Authentication

**Status**: Accepted
**Date**: 2026-01-28
**PRD Traces**: Feature 9

### Context

TracerTM must support both direct user login and federated identity (GitHub, Google).
API clients (agents, CI/CD systems) require token-based auth.

### Decision

- **JWT** (`golang-jwt/jwt/v5`): Access tokens (15-min TTL) and refresh tokens (7-day TTL).
- **OAuth2/OIDC**: GitHub and Google as identity providers. Tokens exchanged for internal
  JWTs.
- **Vault** (`hashicorp/vault/api`): JWT signing keys stored in Vault; rotated quarterly.

### Rationale

- JWTs are stateless, suitable for horizontal scaling.
- Vault centralizes secret management and key rotation.
- OIDC providers reduce password management burden.

### Consequences

- Vault is a required runtime dependency (fails loudly if unavailable).
- All API endpoints must validate JWT on every request (no session cookies for API clients).
- Refresh token rotation must be atomic (database transaction).

---

## ADR-010: SLSA Provenance and Attestation

**Status**: Accepted
**Date**: 2026-02-15
**PRD Traces**: Feature 12

### Context

Compliance teams require verifiable build provenance for audit trails.

### Decision

All CI/CD builds generate **SLSA Level 3 attestations** via `sigstore/cosign`. Attestations
are attached to container images and stored in OCI registry alongside images. SBOM generated
via `syft` on each release.

### Rationale

- SLSA Level 3 satisfies SOC2 and ISO 27001 build integrity requirements.
- Cosign is OSS and integrates with GitHub Actions without paid services.

### Consequences

- Release pipeline must include `cosign sign` and `cosign attest` steps.
- Container registry must support OCI artifact referrers.
- Attestation verification is a gate in production deployment workflow.

---

## ADR-011: Caddy as Unified Gateway

**Status**: Accepted
**Date**: 2026-01-30
**PRD Traces**: All

### Context

Local development requires routing `localhost:4000` to multiple backend services (Go API,
Python API, Vite HMR, VitePress docs). Production requires TLS termination and routing.

### Decision

Use **Caddy 2** as the reverse proxy and unified gateway in both dev and production.
Config: `Taskfile.gateway.yml` and `Makefile.gateway`.

### Rationale

- Caddy provides automatic HTTPS (ACME) in production.
- Caddy's Caddyfile is simpler than Nginx for multi-upstream routing.
- Single gateway means all services share one port (4000) in dev.

### Consequences

- All service URLs in frontend are relative paths (`/api/`, `/python-api/`).
- Caddy config must be updated when new services are added.

---

## ADR-012: Prometheus + Loki + Jaeger Observability

**Status**: Accepted
**Date**: 2026-02-01
**PRD Traces**: Feature 13

### Context

Production requires metrics (SLA tracking), centralized logs (debugging), and distributed
tracing (latency attribution across Go and Python services).

### Decision

Three-pillar observability:
- **Prometheus**: metrics scrape from Go (`/metrics`) and Python services.
- **Loki + Promtail**: log aggregation from all process-compose services.
- **Jaeger**: distributed tracing via OpenTelemetry SDK in Go and Python.
- **Grafana**: unified dashboard consuming all three.

All configured via `docker-compose.yml` for production; native processes in dev.

### Rationale

- Full OSS stack; no SaaS dependency.
- OpenTelemetry provides vendor-neutral instrumentation.
- Grafana unifies all three data sources in one UI.

### Consequences

- Go backend must instrument all handlers with OTel spans.
- Python services must propagate trace context via `opentelemetry-sdk`.
- Grafana dashboards defined as code (JSON provisioning in `config/grafana/`).

---

## ADR-013: Process Compose for Local Orchestration

**Status**: Accepted
**Date**: 2026-01-28
**PRD Traces**: Dev experience

### Context

TracerTM has 10+ services (Go backend, Python backend, frontend, Caddy, PostgreSQL, Neo4j,
Redis, NATS, Prometheus, Grafana, Jaeger). Docker Compose imposes container overhead in dev.

### Decision

Use **process-compose** as the native local orchestrator. Config: `process-compose.yml`.
Services run as native OS processes (not containers). Accessed via TUI dashboard
(`task dev:tui`) and CLI (`process-compose process list --port 18080`).

### Rationale

- Native processes start in <1 second vs 10+ seconds for Docker containers.
- Hot reload (Air, uvicorn --reload, Vite HMR) works without volume mounts.
- process-compose CLI allows per-service restart without stopping the full stack.

### Consequences

- All service dependencies (Postgres, Neo4j, Redis, NATS) must be installed natively.
- `Brewfile.dev` provides the canonical native dependency list.
- CI uses Docker Compose; local dev uses process-compose.

---

## ADR-014: Layered Transformation Migration Strategy

**Status**: Accepted
**Date**: 2026-01-28
**PRD Traces**: All

### Context

TracerTM was initially a CRUD-only system. Upgrading to the full specification-driven,
graph-backed, MCP-native system must not break existing data or workflows.

### Decision

Use **layered transformation** (not a full rewrite):
1. Preserve existing PostgreSQL schema; add new tables via Atlas migrations.
2. Add Neo4j as a complementary store; populate from existing PostgreSQL data.
3. Introduce MCP server alongside existing REST API.
4. Migrate frontend views progressively (matrix view first, graph view second).

### Rationale

- Preserves existing data and in-flight work.
- Each layer is independently testable.
- Risk is reduced by incremental rollout.

### Consequences

- Migration scripts must be idempotent (safe to re-run).
- Neo4j sync job must handle PostgreSQL as source of truth for conflict resolution.
- Legacy CRUD API routes remain until all consumers migrate to new endpoints.

---

## ADR-015: Tach for Architecture Boundary Enforcement

**Status**: Accepted
**Date**: 2026-02-10
**PRD Traces**: Dev experience

### Context

Python codebase (`src/`) has multiple modules (API, MCP server, analysis, CLI). Without
enforcement, imports will cross layer boundaries (e.g., CLI importing database models
directly).

### Decision

Use **tach** (`tach.toml`) to declare and enforce Python module dependency boundaries.
Layering: `cli` → `application` → `domain`; `api` → `application` → `domain`.
`domain` imports nothing from `application` or `cli`.

### Rationale

- Tach runs in CI as a quality gate (`task lint`).
- Boundary violations are caught before review, not after merge.
- Mirrors hexagonal architecture from Go backend.

### Consequences

- All new Python modules must declare their layer in `tach.toml`.
- Cross-layer imports are compile-time errors in CI.
- `tach check` must pass as part of every PR.

---

*For extended decision context and alternatives considered, see individual ADR files in
`docs/adr/`.*
