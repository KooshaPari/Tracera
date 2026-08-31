# ADR-ARCH-001: Hexagonal (Ports and Adapters) Architecture for tracera-server

**Status:** Accepted  
**Date:** 2026-08-30  
**Deciders:** Tracera Architecture Team  

## Context

The `tracera-server` has grown from a simple API server into a complex orchestration layer handling trace ingestion, evidence management, governance checks, and asynchronous queuing. Currently, core domain logic (e.g., trace-link confidence calculations, impact analysis) is interleaved with infrastructure concerns:

1. **Persistence Coupling**: Business rules are scattered across `pg_store.rs` and `sqlite_store.rs`, making it difficult to test logic without a database.
2. **Ingestion Tangles**: GitHub and Jira ingestion logic (`ingest.rs`) is tightly bound to HTTP request handling and external API clients.
3. **Testing Friction**: Integration tests require a running PostgreSQL instance or complex SQLite setup, slowing down the development loop.
4. **Extensibility Barriers**: Adding new data sources (e.g., GitLab, Linear) or new persistence backends (e.g., S3, DynamoDB) requires modifying core modules.

We need a clear separation between the **domain** (what the system does) and the **infrastructure** (how it's done).

## Decision

We will adopt **Hexagonal Architecture (Ports and Adapters)** for the `tracera-server` crate.

### 1. Ports (Interfaces)

Ports will be defined as traits in the `domain` and `ports` modules, representing the system's boundaries.

*   **Driving Ports (Primary):**
    *   `TraceIngestionPort`: Interface for receiving trace data (REST, CLI, gRPC).
    *   `GovernancePort`: Interface for spec-checks and compliance validation.
*   **Driven Ports (Secondary):**
    *   `TraceStorePort`: Interface for persisting/retrieving `TraceLink`, `Evidence`, and `Project` entities.
    *   `QueuePort`: Interface for dispatching asynchronous jobs.
    *   `ExternalIssuePort`: Interface for fetching/enriching data from external systems (GitHub, Jira).

### 2. Adapters (Implementations)

Adapters will provide concrete implementations of these ports, isolated from the core domain.

*   **Driving Adapters:**
    *   `AxumHttpAdapter`: Translates HTTP requests into domain use-cases.
    *   `CLIAdapter`: Handles local CLI interactions.
*   **Driven Adapters:**
    *   `PostgresTraceStoreAdapter`: Implements `TraceStorePort` using `sqlx`.
    *   `SqliteTraceStoreAdapter`: Implements `TraceStorePort` for local/desktop mode.
    *   `GitHubAdapter`: Implements `ExternalIssuePort` for GitHub issues.
    *   `PgQueueAdapter`: Implements `QueuePort` using the `phenodag-queue`.

### 3. Proposed Directory Structure

The `crates/tracera-server/src` directory will be restructured to reflect these boundaries:

```text
crates/tracera-server/src/
├── main.rs                     # Composition root / Bootstrap
├── domain/                     # Core business logic & entities (Pure Rust)
│   ├── mod.rs
│   ├── trace.rs                # TraceLink, Artifact entities
│   ├── evidence.rs             # EvidenceItem entity
│   ├── impact.rs               # Impact analysis logic
│   └── confidence.rs           # Confidence scoring logic
├── ports/                      # Interface definitions
│   ├── mod.rs
│   ├── store.rs                # TraceStorePort trait
│   ├── ingest.rs               # TraceIngestionPort trait
│   └── queue.rs                # QueuePort trait
├── adapters/                   # Infrastructure implementations
│   ├── mod.rs
│   ├── http/                   # Driving adapters (Axum handlers)
│   │   ├── mod.rs
│   │   ├── health.rs
│   │   └── routes.rs
│   ├── persistence/            # Driven adapters (Store implementations)
│   │   ├── mod.rs
│   │   ├── pg_store.rs
│   │   └── sqlite_store.rs
│   ├── queue/                  # Driven adapters (Queue implementations)
│   │   └── mod.rs
│   └── external/               # Driven adapters (GitHub, Jira)
│       ├── mod.rs
│       └── github.rs
└── config.rs                   # Application configuration
```

## Consequences

### Positive
*   **Isolatable Business Logic**: Core logic in `domain/` and `ports/` can be unit-tested with simple mocks/fakes, no database required.
*   **Pluggable Infrastructure**: We can swap `PostgresTraceStoreAdapter` for an `InMemoryStoreAdapter` (for tests) or a `S3StoreAdapter` (for archival) without touching business logic.
*   **Clear Boundaries**: New developers can easily identify what is "logic" vs "plumbing".
*   **Parallel Development**: Multiple developers can work on different adapters (e.g., a new GitLab adapter) without merge conflicts in core domain files.

### Negative
*   **Initial Refactoring Effort**: Moving existing logic into the new modules will require a significant one-time refactor.
*   **Increased Indirection**: More traits and modules mean more mental overhead when navigating the codebase (mitigated by the `Composition Root` in `main.rs`).

### Migration Path
1.  Create `domain` and `ports` modules.
2.  Extract `Store` trait from `store.rs` into `ports/store.rs`.
3.  Move `main.rs` routing logic into `adapters/http/`.
4.  Move `pg_store.rs` and `sqlite_store.rs` into `adapters/persistence/`.

---
*This ADR updates the "Architecture Principles" section in the project's `ARCHITECTURE.md`.*
