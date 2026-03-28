# ADR — TracerTM

**Project**: TracerTM (Requirements Traceability Matrix)
**Version**: 1.0
**Last Updated**: 2026-03-27

---

## ADR-001: Polyglot Backend Architecture (Python + Go)

**Status**: Accepted

**Context**:
TracerTM requires two distinct execution profiles under one system: a Python-native ML/analysis layer
(FR-RTM-010 through FR-RTM-013) with access to rich AI/ML libraries, and a high-throughput API
gateway layer capable of handling real-time WebSocket connections and hundreds of concurrent
requirement linkage queries.

**Decision**:
Run two backend services in parallel:
- `backend/` (Go, Echo v4): primary REST/WebSocket API gateway, authentication, real-time
  collaboration, and traceability graph queries via Neo4j.
- `src/` (Python 3.13, FastAPI + uvicorn): analysis engine, LLM-backed requirement inference,
  compliance report generation, CLI tooling.

Both services share a PostgreSQL database schema (managed by Alembic migrations). The Go service
handles hot paths; the Python service handles compute-intensive or ML-dependent tasks.

**Consequences**:
- (+) Go service sustains <2s matrix load for 1000+ requirements (FR-RTM-003).
- (+) Python service uses native Pydantic + SQLAlchemy for domain modelling without FFI overhead.
- (-) Two build pipelines, two Docker images, two language runtime environments to maintain.
- (-) Shared schema requires coordination; Alembic migrations must be applied before Go binary start.

---

## ADR-002: Neo4j for Graph-Based Dependency Analysis

**Status**: Accepted

**Context**:
Requirement dependency chains (FR-DEP-001 through FR-DEP-006) require traversal of directed graphs
where nodes are requirements and edges represent blocking/optional/related relationships. Relational
databases require recursive CTEs that become expensive beyond ~500 dependencies; pure in-memory
graphs do not persist or scale across services.

**Decision**:
Use Neo4j (community edition) as a dedicated graph store, accessed via the official
`neo4j-go-driver/v5` from the Go service. Requirement nodes and linkage edges are written to Neo4j
in parallel with the authoritative PostgreSQL record. Dependency path queries (impact analysis,
circular detection) execute as Cypher traversals.

**Consequences**:
- (+) Cypher `MATCH p=(a)-[*1..10]->(b)` traversals are O(edges traversed), not O(rows scanned).
- (+) Circular dependency detection (FR-RTM-002) is a single Cypher query.
- (-) Dual-write to PostgreSQL + Neo4j introduces eventual consistency window; the Go service
  compensates with a write barrier before returning the API response.
- (-) Neo4j community edition is single-instance; HA requires Enterprise license.

---

## ADR-003: PostgreSQL as Authoritative Relational Store with Alembic Migrations

**Status**: Accepted

**Context**:
Requirements, users, projects, linkages, and audit events must survive restarts, support point-in-time
recovery, and be queryable by multiple services. ACID semantics are required for requirement status
transitions (FR-RTM-006) and compliance audit trails (FR-COMP-001 through FR-COMP-004).

**Decision**:
PostgreSQL (v16+) is the single authoritative store. Schema is managed by Alembic (Python migration
tool); migration scripts live in `alembic/versions/`. The Go service connects via `pgx/v5` with a
connection pool; the Python service connects via `asyncpg` through SQLAlchemy async.

Raw SQL queries for read-heavy paths use `queries.sql` (PGXC naming convention). PostgreSQL-native
features used: generated columns, `tstzrange` for time-bounded audits, `jsonb` for requirement
metadata blobs, `pg_notify` for CDC-style event fanout.

**Consequences**:
- (+) Single migration tool (Alembic) controls schema evolution; no schema drift between services.
- (+) `jsonb` allows forward-compatible requirement metadata without schema churn.
- (-) Alembic is Python-native; Go migrations must be applied via `make migrate` before service
  start, adding a deployment sequencing constraint.

---

## ADR-004: Redis for Caching, Session State, and Rate Limiting

**Status**: Accepted

**Context**:
Real-time collaboration (FR-COLLAB-001 through FR-COLLAB-004) and live dashboard views
(FR-OBS-001) need fast shared state that does not require round-trips to PostgreSQL. API
rate-limiting must be enforced across Go service replicas without a central coordinator.

**Decision**:
Redis (accessed via `go-redis` from Go, `aioredis` from Python) serves three roles:
1. Session token store: JWT refresh tokens cached with TTL equal to token expiry.
2. Dashboard/matrix cache: rendered matrix rows cached for up to 60 s; invalidated on requirement
   write-through.
3. Rate-limit counters: sliding-window counters per `(user_id, endpoint)` stored as Redis HLLs for
   sub-millisecond increments.

`alicebob/miniredis/v2` is used in Go tests to replace Redis without network I/O.

**Consequences**:
- (+) Cache hit on RTM matrix load reduces P95 latency from ~1.8 s to ~120 ms for 1000-row matrices.
- (+) Rate-limiting is consistent across replicas with no external coordinator.
- (-) Session state in Redis is non-durable; a Redis restart invalidates all active sessions.
  Mitigation: Go service falls back to PostgreSQL session lookup on Redis miss.

---

## ADR-005: NATS for Asynchronous Event Fanout

**Status**: Accepted

**Context**:
Multiple subsystems need to react to requirement changes without tight coupling: the observability
pipeline (Prometheus counters), the compliance audit logger, and the WebSocket broadcast relay.
Synchronous HTTP calls between services would introduce latency spikes and coupling.

**Decision**:
NATS.io (accessed via `nats.go`) is used as a lightweight pub/sub bus. The Go service publishes
`requirement.changed`, `linkage.created`, and `project.status` events on named subjects. Consumers
include: the Python analytics service (via `nats.py` client), the WebSocket relay (in-process Go),
and the audit writer (in-process Go).

NATS JetStream is not required for current durability needs; at-most-once delivery is acceptable
because downstream consumers are idempotent or reconstruct state from PostgreSQL on startup.

**Consequences**:
- (+) Decouples Python analytics startup from Go API hot path.
- (+) WebSocket broadcast latency is <50 ms after requirement write (FR-COLLAB-002).
- (-) At-most-once delivery means events may be dropped during NATS restart. Acceptable because
  affected consumers (Prometheus counters, audit writer) reconcile from PostgreSQL on startup.

---

## ADR-006: gRPC + Protobuf for Cross-Service Contract Enforcement

**Status**: Accepted

**Context**:
The Go and Python services share data models (requirement schema, linkage records, audit events).
REST JSON payloads offer no compile-time contract guarantees. Schema drift between Go structs and
Python Pydantic models caused silent bugs during early development.

**Decision**:
Define all shared data contracts as Protobuf v3 schemas in `proto/`. Use `buf` (buf.build toolchain,
`buf.yaml` + `buf.gen.yaml`) to generate Go stubs (`grpc/v2`) and Python stubs (`grpcio`). The Go
service exposes a gRPC server on an internal port; the Python service calls it for requirement reads
to avoid direct DB contention on analytics paths.

The external-facing public API remains REST/JSON (Echo v4 for Go, FastAPI for Python) because client
tooling (browsers, CLI) cannot speak gRPC directly.

**Consequences**:
- (+) Protobuf schema is the single source of truth for cross-service types; `buf lint` enforces
  backward compatibility.
- (+) gRPC streaming enables streaming requirement exports without buffering full result sets.
- (-) buf codegen adds a build step; Go and Python stub files must be regenerated after schema
  changes and committed (`proto/gen/`).

---

## ADR-007: S3-Compatible Object Storage (MinIO / AWS S3) for Artifact and Evidence Storage

**Status**: Accepted

**Context**:
Compliance audit artifacts (FR-COMP-003), evidence bundles (test reports, Playwright screenshots),
and requirement export archives may be large binary blobs. Storing binaries in PostgreSQL degrades
query performance; serving them from application memory limits scalability.

**Decision**:
Use an S3-compatible backend for blob storage. In development, MinIO (`minio-go/v7`) runs as a
native process. In production, AWS S3 (`aws-sdk-go-v2/service/s3`) is targeted. The Go service
abstracts both via the `S3Manager` interface in `pkg/storage/`. Upload/download presigned URLs are
returned to clients; blobs never transit the application tier.

**Consequences**:
- (+) Artifact uploads are non-blocking; the Go handler returns a presigned URL immediately.
- (+) MinIO is fully compatible with AWS S3 API; switching requires only an endpoint + credential
  environment variable change.
- (-) Local dev requires MinIO process running (added to `docker-compose.yml` and process-compose).

---

## ADR-008: Prometheus + Loki + Jaeger Observability Stack

**Status**: Accepted

**Context**:
FR-OBS-001 through FR-OBS-004 require real-time metrics dashboards, structured log aggregation, and
distributed trace correlation across Go and Python services. A homogeneous vendor-agnostic
observability stack is preferred over a paid SaaS.

**Decision**:
- **Metrics**: Prometheus scrapes `/metrics` from both services (Go uses `prometheus/client_golang`;
  Python uses `prometheus-fastapi-instrumentator`). Grafana provides dashboards.
- **Logs**: Structured logs (Go: `slog` JSON; Python: `structlog` JSON) are shipped to Loki via
  Promtail. Log queries use LogQL.
- **Traces**: Both services emit OpenTelemetry spans. Jaeger collects and stores traces. Trace IDs
  are propagated in HTTP headers (`traceparent`) and NATS message metadata.

Sentry (`getsentry/sentry-go`) is used for error capture and alerting on unhandled panics.

**Consequences**:
- (+) Full OSS stack; zero per-request cost at any volume.
- (+) Trace IDs link Jaeger spans to Loki log lines for end-to-end debugging.
- (-) Prometheus + Loki + Jaeger + Grafana = four additional runtime processes in dev. Managed via
  `docker-compose.yml` and `process-compose` profiles.

---

## ADR-009: React + TypeScript Frontend with Bun as Package Manager

**Status**: Accepted

**Context**:
TracerTM requires a rich UI with a live RTM matrix (FR-RTM-003), dependency graph visualization
(FR-DEP-004), real-time collaboration cursors (FR-COLLAB-001), and compliance dashboards
(FR-COMP-004). The frontend must support >1000 matrix rows without jank.

**Decision**:
- React 19 (concurrent mode) for component architecture.
- TypeScript (strict mode) for type safety.
- Bun as the package manager and bundler (`bun.lock` is the lockfile); `bunfig.toml` for config.
- Radix UI primitives + Tailwind CSS for accessible, composable components.
- React Query for server state; Zustand for local UI state.
- Virtualized row rendering (`@tanstack/react-virtual`) for the RTM matrix to handle 1000+ rows
  at <16 ms frame budget.

**Consequences**:
- (+) Virtual rendering eliminates DOM node count issues for large matrices.
- (+) Bun install is 5-10x faster than npm; cold CI installs drop from ~40 s to ~6 s.
- (-) Bun's module resolution differs from Node.js in edge cases; a small number of CJS-only
  packages require `--bun` shim or replacement.

---

## ADR-010: HashiCorp Vault for Secrets Management

**Status**: Accepted

**Context**:
TracerTM handles provider API keys, database credentials, and JWT signing secrets. Hardcoding
credentials in environment files is unacceptable for production; a secrets management system
with audit logging is required (FR-COMP-001).

**Decision**:
HashiCorp Vault (`hashicorp/vault/api v1.22.0`) is used as the secrets backend. The Go service
fetches secrets at startup via the AppRole auth method; secrets are renewed before lease expiry.
In development, a dev-mode Vault instance (started via `process-compose`) is pre-seeded by the
`scripts/seed-vault.sh` script. The Python service reads secrets via the `hvac` client.

**Consequences**:
- (+) Credential rotation does not require application redeployment; Vault leases handle expiry.
- (+) Vault audit log provides a tamper-evident record of all secret accesses (FR-COMP-001).
- (-) Vault adds a critical runtime dependency; Go service hard-fails at startup if Vault is
  unreachable (consistent with the project's explicit-failure stance in CLAUDE.md).

---

## ADR-011: Gorilla Mux + Echo v4 Dual Routing Strategy

**Status**: Accepted

**Context**:
The Go backend was initially developed with `gorilla/mux v1.8.1`. As middleware needs (JWT
validation, rate-limiting, CORS) grew, Echo v4's built-in middleware ecosystem reduced boilerplate.
A full migration was deferred due to endpoint volume (~80 handlers).

**Decision**:
Maintain both routers during a transition period:
- Echo v4 (`labstack/echo/v4 v4.15.0`) handles all new endpoints and is the primary router.
- Gorilla Mux (`gorilla/mux v1.8.1`) handles legacy endpoints not yet migrated.
Echo's `Any` handler mounts the Mux router as a fallback catch-all.

Target: complete migration to Echo v4 before v1.0 GA; remove Gorilla Mux dependency.

**Consequences**:
- (+) New features are developed exclusively on Echo with full middleware support.
- (-) Two routers in the same process create potential middleware ordering ambiguity. Mitigated by
  explicit middleware registration order and integration tests covering all legacy routes.

---

## ADR-012: Typer CLI for Agent-Native Automation

**Status**: Accepted

**Context**:
FR-CLI-001 through FR-CLI-006 specify a rich CLI for requirement import/export, spec verification,
and batch operations. The CLI must be scriptable by AI agents and support JSON output for
machine-readable pipelines.

**Decision**:
Use Typer (`typer>=0.21.1`) with Rich (`rich>=14.3.1`) for the Python CLI layer. All commands
support `--output json | table | csv` via a shared output formatter. The CLI connects to the Go
backend REST API rather than the database directly, ensuring consistent validation and authorization.

`pydantic-settings` manages CLI config from environment variables, `.env` files, and explicit flags
in priority order.

**Consequences**:
- (+) Typer generates `--help` documentation automatically; agent tooling can introspect commands.
- (+) `--output json` enables pipe-safe agent pipelines: `tracertm list --output json | jq ...`.
- (-) CLI depends on the Go backend being reachable; offline / local-only mode is not supported.
  Hard failure with actionable error message is emitted when the backend is unreachable.
