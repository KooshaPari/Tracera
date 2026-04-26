# Microservice Scaffold Templates

Production-ready microservice templates following hexagonal/clean architecture.

## Templates

| Language | Template | Description |
|----------|----------|-------------|
| Go | `go/` | Go microservice with hexagonal architecture |
| Rust | `rust/` | Rust microservice with clean architecture |
| TypeScript | `typescript/` | Node.js/TS microservice with plugin support |
| Python | `python/` | Python microservice with hexagonal patterns |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (gRPC/HTTP)                  │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                          │
│              (Commands, Queries, Handlers)                   │
├─────────────────────────────────────────────────────────────┤
│                       Domain Layer                           │
│           (Entities, Value Objects, Domain Services)         │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
│        (Persistence, Messaging, External Services)          │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

- **Ports & Adapters**: Domain isolated from infrastructure
- **CQRS**: Command Query Responsibility Segregation
- **Event-Driven**: Async messaging via NATS/Kafka
- **Observability**: Structured logging, metrics, tracing
- **Resilience**: Circuit breaker, retry, timeout patterns

## Quick Start

```bash
# Clone template
cp -r microservice-scaffold/go my-service
cd my-service

# Update configuration
# 1. Replace 'microservice' with your service name
# 2. Update go.mod with your module path
# 3. Configure docker-compose.yml
# 4. Set up Makefile targets

# Run locally
make run

# Run tests
make test

# Build Docker image
make docker-build
```

## Observability Stack

| Component | Tool |
|-----------|------|
| Logging | Structured JSON (zerolog, tracing, pino) |
| Metrics | Prometheus |
| Tracing | OpenTelemetry |
| Visualization | Grafana |

## Resilience Patterns

| Pattern | Implementation |
|---------|----------------|
| Circuit Breaker | Resilience4j, Polly |
| Retry | Exponential backoff |
| Timeout | Context deadlines |
| Bulkhead | Connection pools |
| Rate Limiting | Token bucket |

## See Also

- [Hexagonal Architecture](../hexagonal-go/)
- [Clean Architecture](../clean-rust/)
- [xDD Methodologies](../docs/reference/xDD/XDD_METHODOLOGIES.md)
- [Library Decomposition](../docs/guides/LIBRARY_DECOMPOSITION.md)
