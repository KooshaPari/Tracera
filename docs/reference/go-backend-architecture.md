# Go Backend Architecture

## Scope
- Service: `go-backend` (root `main.go`, `internal/*`, `cmd/*`)

## High-level stack
- Language/runtime: Go (module `github.com/kooshapari/tracertm-backend`)
- HTTP framework: Echo
- gRPC: `internal/grpc`
- Storage: Postgres (pgx), Redis, Neo4j
- Messaging: NATS
- Observability: OpenTelemetry + Sentry
- Migrations: `internal/db` + `internal/database`

## Dependency map (major subsystems)
```mermaid
flowchart TB
  Main[main.go] --> Server[internal/server]
  Server --> Handlers[internal/handlers]
  Server --> Middleware[internal/middleware]
  Server --> Services[internal/services]
  Services --> Repository[internal/repository]
  Services --> Cache[internal/cache]
  Services --> Search[internal/search]
  Services --> Graph[internal/graph]
  Services --> Equivalence[internal/equivalence]
  Services --> Embeddings[internal/embeddings]
  Services --> DocIndex[internal/docindex]
  Services --> CodeIndex[internal/codeindex]
  Repository --> DB[internal/database]
  Cache --> Redis[(Redis)]
  Repository --> Postgres[(Postgres)]
  Graph --> Neo4j[(Neo4j)]
  Services --> NATS[(NATS)]
```

## Runtime flow (simplified)
1) `main.go` loads config and preflight checks.
2) Infrastructure initialized (Postgres, Redis, NATS, Neo4j).
3) Services wired (business logic, indexers, search).
4) Echo HTTP + gRPC servers start.
5) Middleware adds auth, metrics, tracing, rate limits.

## Key entrypoints
- Main: `main.go`
- Server wiring: `internal/server/server.go`
- HTTP handlers: `internal/handlers/*`
- Services: `internal/services/*`
- Repositories: `internal/repository/*`
- DB/infra: `internal/database/*`, `internal/infrastructure/*`

## Quality gates
- Linting: golangci-lint + custom rules (mnd, gocognit, funlen, gosec)
- Tests: `go test ./...`
