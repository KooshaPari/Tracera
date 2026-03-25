# TracerTM: Architecture Decision Records

## ADR-001: Polyglot Backend (Go + Python)

- **Status:** Accepted
- **Context:** Need high-performance API serving AND data analysis/ML capabilities.
- **Decision:** Go for the core API server (backend/cmd/tracertm), Python for specialized services (analysis, CLI/TUI, background processing).
- **Rationale:** Go provides low-latency HTTP/gRPC serving; Python provides rich ML/data ecosystem.
- **Alternatives:** Monolingual Go (poor ML support), monolingual Python (poor API performance).

## ADR-002: Neo4j for Graph Storage

- **Status:** Accepted
- **Context:** Traceability data is inherently a graph (requirements -> code -> tests -> deployments).
- **Decision:** Use Neo4j for graph queries and visualization; PostgreSQL for relational data.
- **Rationale:** Cypher queries for impact analysis and dependency traversal are orders of magnitude simpler than recursive SQL.
- **Alternatives:** PostgreSQL-only with recursive CTEs (complex, slow for deep traversals).

## ADR-003: NATS for Event Streaming

- **Status:** Accepted
- **Context:** Real-time updates across multiple frontend clients and backend services.
- **Decision:** NATS JetStream for event bus; WebSocket bridge for frontend delivery.
- **Rationale:** NATS provides lightweight pub/sub with persistence, lower operational overhead than Kafka.
- **Alternatives:** Kafka (heavier), Redis Pub/Sub (no persistence), SSE (no bidirectional).

## ADR-004: React SPA with TanStack Router

- **Status:** Accepted
- **Context:** Complex multi-view UI with interactive graph visualizations.
- **Decision:** React + TypeScript, TanStack Router, Zustand for state.
- **Rationale:** TanStack Router provides type-safe routing; Zustand is minimal and performant.
- **Alternatives:** Next.js (SSR unnecessary for internal tool), Vue (team Go/TS-focused).

## ADR-005: Caddy as Unified Gateway

- **Status:** Accepted
- **Context:** Need to serve frontend, API, and docs from a single origin.
- **Decision:** Caddy reverse proxy on port 4000, routing to Go backend, Python services, and static frontend.
- **Rationale:** Automatic HTTPS, simple config, low resource usage.

## ADR-006: Embedding-Based Code Search

- **Status:** Accepted
- **Context:** Semantic search for finding related requirements and code across the project.
- **Decision:** Generate embeddings for code and requirements, store in PostgreSQL pgvector.
- **Rationale:** Enables "find similar" queries that go beyond keyword matching.

## ADR-007: Process Compose for Dev Orchestration

- **Status:** Accepted
- **Context:** Multiple services (Go, Python, frontend, DBs, caches) need coordinated local dev.
- **Decision:** process-compose with TUI dashboard; hot reload per service.
- **Rationale:** Lighter than Docker Compose for native dev; provides live log aggregation.
