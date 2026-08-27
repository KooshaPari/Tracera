# Tracera Architecture

## Overview

Tracera is a trace-link matrix system for Agentic and LLM observability. It captures structured trace-links across runs, distills short-term and long-term memory, and serves an Electrobun desktop viewer over OKF-bundled session history.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Tracera System                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Web UI    │  │   Desktop   │  │   CLI       │            │
│  │  (React)    │  │ (Electrobun)│  │  (Rust)     │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API Server (Rust)                      │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │  Auth   │  │  Store  │  │  Queue  │  │Ingestion│   │   │
│  │  │  Layer  │  │  Trait  │  │  System │  │ Adapters│   │   │
│  │  └─────────┘  └────┬────┘  └─────────┘  └─────────┘   │   │
│  └─────────────────────┼───────────────────────────────────┘   │
│                        │                                        │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Data Layer                             │   │
│  │  ┌─────────────┐              ┌─────────────┐           │   │
│  │  │  PostgreSQL │              │   SQLite    │           │   │
│  │  │  (Server)   │              │  (On-Device)│           │   │
│  │  └─────────────┘              └─────────────┘           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. API Server (`crates/tracera-server`)

The central component providing RESTful API endpoints for trace management, evidence tracking, and governance.

**Key Modules:**

- **`main.rs`**: Server entry point with Axum-based HTTP routing
- **`store.rs`**: Store trait defining database operations
- **`pg_store.rs`**: PostgreSQL implementation of the Store trait
- **`sqlite_store.rs`**: SQLite implementation of the Store trait
- **`auth.rs`**: Bearer token authentication middleware
- **`ingest.rs`**: GitHub and Jira issue ingestion adapters
- **`queue/`**: Asynchronous task queue system (feature-gated)

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz`, `/health` | GET | Liveness probes |
| `/readyz`, `/ready` | GET | Readiness probes |
| `/metrics` | GET | Prometheus metrics |
| `/api/v1/coverage-matrix` | POST | Generate coverage matrix from trace links |
| `/api/v1/impact` | POST | Calculate impact analysis (blast radius) |
| `/api/v1/confidence` | POST | Compute trace-link confidence scores |
| `/api/v1/blast-radius` | POST | Determine affected artifacts |
| `/api/v1/governance/spec-check` | POST | Validate governance compliance |
| `/api/v1/trace/{id}/links` | GET | List persisted trace links |
| `/evidence` | GET/POST | Evidence management |
| `/ingest/github` | POST | GitHub issue ingestion |
| `/ingest/jira` | POST | Jira issue ingestion |
| `/sdlc-pm/sprints` | GET/POST | Sprint management |
| `/problems` | GET/POST | Problem management (ITIL) |
| `/api/v1/projects` | GET | Project listing |
| `/org-intel/teams` | GET | Team intelligence |
| `/org-intel/metrics` | GET | Organization metrics |

### 2. Store Trait (`store.rs`)

The Store trait provides a database-agnostic interface for persistence operations:

```rust
#[async_trait]
pub trait Store: Send + Sync {
    // Evidence operations
    async fn list_evidence(&self) -> Result<Vec<EvidenceItem>, StoreError>;
    async fn create_evidence(...) -> Result<EvidenceItem, StoreError>;
    async fn count_evidence(&self) -> Result<i64, StoreError>;

    // Sprint operations
    async fn list_sprints(&self) -> Result<Vec<Sprint>, StoreError>;
    async fn create_sprint(...) -> Result<Sprint, StoreError>;

    // Story operations
    async fn list_stories(&self) -> Result<Vec<Story>, StoreError>;

    // Problem operations
    async fn list_problems(...) -> Result<Vec<Problem>, StoreError>;
    async fn create_problem(...) -> Result<Problem, StoreError>;
    async fn count_problems_filtered(...) -> Result<i64, StoreError>;

    // Trace link operations
    async fn list_trace_links_for_artifact(...) -> Result<Vec<TraceLink>, StoreError>;
    async fn create_trace_link(...) -> Result<(), StoreError>;

    // Project operations
    async fn list_projects(...) -> Result<Vec<Project>, StoreError>;
    async fn get_project(...) -> Result<Option<Project>, StoreError>;
    async fn count_projects(&self) -> Result<i64, StoreError>;

    // Team operations
    async fn list_teams(&self) -> Result<Vec<TeamRow>, StoreError>;
}
```

### 3. Database Backends

#### PostgreSQL (Server Tier)
- **Use Case**: Production deployments, multi-user environments
- **Location**: `crates/tracera-server/src/pg_store.rs`
- **Migrations**: `crates/tracera-server/migrations/`
- **Connection**: Uses `sqlx` with connection pooling

#### SQLite (On-Device Tier)
- **Use Case**: Local development, single-user desktop apps
- **Location**: `crates/tracera-server/src/sqlite_store.rs`
- **Migrations**: `crates/tracera-server/migrations-sqlite/`
- **Connection**: File-based or in-memory databases

### 4. Frontend Applications

#### Web Application (`frontend/apps/web`)
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query / TanStack Query
- **Testing**: Playwright (E2E), Vitest (Unit)

#### Desktop Application (`frontend/apps/desktop`)
- **Framework**: Electrobun (Rust + Web)
- **Purpose**: Native desktop viewer for trace sessions
- **Bundling**: Custom bundle process via `bundle.ts`

#### Shared UI Package (`frontend/packages/ui`)
- **Components**: Reusable UI primitives (Button, Card, Dialog, etc.)
- **Testing**: Comprehensive test suite with Vitest

### 5. CLI Tool (`crates/tracera-cli`)

Command-line interface for Tracera operations:

- **`main.rs`**: CLI entry point with clap-based argument parsing
- **`commands.rs`**: Command implementations
- **`bundle.rs`**: Frontend bundling utilities
- **`compose.rs`**: Composition helpers
- **`runtime.rs`**: Runtime configuration

### 6. Queue System (`crates/tracera-server/src/queue/`)

Feature-gated asynchronous task queue for background processing:

- **`mod.rs`**: Queue module definitions
- **`init.rs`**: Queue initialization
- **`claim.rs`**: Task claiming logic
- **`dedup.rs`**: Deduplication mechanisms
- **`export.rs`**: Data export operations
- **`heartbeat.rs`**: Worker heartbeat monitoring
- **`lifecycle.rs`**: Task lifecycle management
- **`scanner.rs`**: Queue scanning utilities
- **`status.rs`**: Task status tracking

### 7. Edge Computing (`crates/tracera-edge`)

Lightweight edge deployment component for distributed trace collection.

### 8. MCP Integration (`crates/tracertm-mcp`)

Model Context Protocol integration for AI agent observability.

## Data Model

### Core Entities

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Evidence     │────▶│   TraceLink     │◀────│    Artifact     │
│                 │     │                 │     │                 │
│ - id            │     │ - id            │     │ - artifact_id   │
│ - artifact_id   │     │ - source_id     │     │ - kind          │
│ - kind          │     │ - target_id     │     │ - metadata      │
│ - url           │     │ - relationship  │     └─────────────────┘
│ - metadata      │     │ - confidence    │
│ - created_at    │     │ - source        │
└─────────────────┘     │ - created_at    │
                        │ - updated_at    │
                        └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Sprint      │     │     Story       │     │    Problem      │
│                 │     │                 │     │                 │
│ - id            │     │ - id            │     │ - id            │
│ - name          │     │ - sprint_id     │     │ - project_id    │
│ - goal          │     │ - title         │     │ - title         │
│ - start_date    │     │ - status        │     │ - status        │
│ - end_date      │     └─────────────────┘     │ - impact_level  │
└─────────────────┘                             │ - urgency       │
                                                │ - priority      │
                                                └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│      Team       │     │     Project     │
│                 │     │                 │
│ - id            │     │ - id            │
│ - name          │     │ - name          │
│ - description   │     │ - description   │
│ - members       │     │ - metadata      │
└─────────────────┘     │ - problem_count │
                        └─────────────────┘
```

### Trace Link Relationships

- `implements`: Source implements target
- `verified_by`: Source is verified by target
- `depends_on`: Source depends on target
- `conflicts_with`: Source conflicts with target
- `satisfies`: Source satisfies target requirement
- `verifies`: Source verifies target

## Security Architecture

### Authentication

- **Bearer Token Auth**: API endpoints protected via `TRACERA_AUTH_TOKEN`
- **Middleware**: `auth::require_bearer` validates tokens on protected routes
- **Health Endpoints**: Exempt from authentication for orchestrator probes

### Network Security

- **Bind Address Validation**: Non-loopback binds require explicit deployment mode
- **Deployment Modes**:
  - `authenticated-proxy`: Behind authenticated reverse proxy
  - `loopback-published`: Loopback-only with external proxy
  - `private-network`: Trusted internal network

### Request Protection

- **CSRF Protection**: Origin/Referer validation for state-mutating requests
- **Rate Limiting**: Per-IP request rate limiting (configurable via `TRACERA_RATE_LIMIT_RPS`)
- **Body Size Limits**: 10 MB maximum request body
- **Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Cache-Control: no-store`

## Observability

### Metrics

- **Prometheus Exporter**: `/metrics` endpoint for Prometheus scraping
- **Custom Metrics**: Request latency, error rates, queue depths

### Tracing

- **OpenTelemetry Integration**: Distributed tracing support
- **Structured Logging**: `tracing` crate with environment-based filtering

### Health Checks

- **Liveness** (`/healthz`): Server process is running
- **Readiness** (`/readyz`): Server can accept traffic (database connected)

## Deployment Architecture

### Docker

```dockerfile
# Multi-stage build
FROM rust:latest AS builder
# ... build stage ...

FROM debian:bookworm-slim
# ... runtime stage ...
```

### Self-Hosted

- **Docker Compose**: `docker-compose.yml` for full stack
- **Local Development**: `docker-compose.local.yml` for dev environment

### Cloud Platforms

- **Vercel**: Frontend deployment via `vercel.json`
- **Cloudflare Workers**: Edge deployment via `wrangler.toml`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | Required |
| `TRACERA_AUTH_TOKEN` | Bearer token for API auth | None |
| `TRACERA_BIND_ADDR` | Server bind address | `127.0.0.1:8080` |
| `TRACERA_PUBLIC_BIND_MODE` | Network deployment mode | `private-network` |
| `TRACERA_FRONTEND_DIST` | Frontend dist path | `frontend/dist` |
| `TRACERA_RATE_LIMIT_RPS` | Rate limit (requests/second) | `100` |
| `GITHUB_TOKEN` | GitHub API token | Optional |
| `GITHUB_REPO` | GitHub repository (owner/repo) | Optional |
| `JIRA_URL` | Jira server URL | Optional |
| `JIRA_EMAIL` | Jira user email | Optional |
| `JIRA_API_TOKEN` | Jira API token | Optional |
| `JIRA_PROJECT_KEY` | Jira project key | Optional |

### Cargo Features

- `phenodag-queue`: Enable async task queue system

## Development Workflow

### Building

```bash
# Build entire workspace
cargo build --workspace

# Build specific crate
cargo build -p tracera-server

# Build with features
cargo build -p tracera-server --features phenodag-queue
```

### Testing

```bash
# Run all tests
cargo test --workspace

# Run specific crate tests
cargo test -p tracera-server

# Run with PostgreSQL (requires TRACERA_TEST_DATABASE_URL)
cargo test -p tracera-server -- --ignored
```

### Frontend Development

```bash
cd frontend
bun install
bun run dev
```

## Architecture Principles

1. **Hexagonal Architecture**: Core domain logic isolated from infrastructure concerns
2. **Store Trait Abstraction**: Database-agnostic persistence layer
3. **Fail-Loud Policy**: Explicit errors on configuration or connection failures
4. **Defense-in-Depth**: Multiple security layers (auth, CSRF, rate limiting, headers)
5. **Observability-First**: Built-in health checks, metrics, and tracing
6. **Progressive Enhancement**: SQLite for local dev, PostgreSQL for production
7. **Feature Gating**: Optional components (queue system) behind Cargo features

## Future Considerations

- **Distributed Tracing**: OpenTelemetry span propagation across services
- **Event Sourcing**: Audit trail for all state changes
- **Multi-Tenancy**: Workspace isolation for enterprise deployments
- **Real-Time Updates**: WebSocket support for live trace updates
- **Plugin System**: Extensible ingestion adapters beyond GitHub/Jira
