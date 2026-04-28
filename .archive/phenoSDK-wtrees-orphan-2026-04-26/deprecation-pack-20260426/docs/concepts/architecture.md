# Architecture Fundamentals

Pheno-SDK encourages composition over inheritance, late binding, and environment-aware runtime configuration. This document captures the core architectural decisions that apply across all kits.

## Overview

Pheno-SDK follows a layered architecture that promotes:
- **Separation of Concerns**: Clear boundaries between different system responsibilities
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Composition over Inheritance**: Favor object composition for code reuse
- **Environment Awareness**: Runtime configuration based on deployment context

## Architecture Layers

### 1. Domain Layer
**Purpose**: Pure business logic and domain rules
**Components**: Aggregates, value objects, domain services
**Kits**: [domain-kit](../kits/domain-kit.md)
**Dependencies**: None (pure business logic)

### 2. Application Layer
**Purpose**: Application services, workflows, and orchestration
**Components**: Command handlers, workflows, orchestrators, application services
**Kits**: [adapter-kit](../kits/adapter-kit.md), [workflow-kit](../kits/workflow-kit.md), [orchestrator-kit](../kits/orchestrator-kit.md)
**Dependencies**: Domain layer only

### 3. Infrastructure Layer
**Purpose**: External system integration and persistence
**Components**: Database adapters, message queues, external APIs, storage
**Kits**: [db-kit](../kits/db-kit.md), [storage-kit](../kits/storage-kit.md), [stream-kit](../kits/stream-kit.md)
**Dependencies**: Application and domain layers

### 4. Interface Layer
**Purpose**: User interfaces and external communication
**Components**: HTTP APIs, CLIs, TUIs, event gateways
**Kits**: [api-gateway-kit](../kits/api-gateway-kit.md), [cli-builder-kit](../kits/cli-builder-kit.md), [tui-kit](../kits/tui-kit.md)
**Dependencies**: All other layers

**Key Principle**: Each layer depends only on the layer below it. Cross-layer concerns (logging, metrics, configuration) are provided through injected contracts rather than module-level singletons.

## Dependency Injection & Composition

- **Container (`adapter_kit.di.Container`)** – Minimal service locator with scoped lifetimes; used to wire services.
- **Registry (`adapter_kit.PluginRegistry`)** – Named implementations for runtime selection (e.g. choose a storage provider per tenant).
- **Factories** – Constructor wrappers to defer heavy initialization until necessary (e.g. database client factories in adapter-kit).

Prefer injecting interfaces (protocols/ABCs) instead of concrete implementations. Each kit publishes typed contracts to help with this.

## Configuration Flow

```
Environment → config-kit loaders → AppConfig → dependency injection → kit constructors
```

Configuration is never read directly from the environment inside business logic. Instead, configuration objects are assembled once and injected.

## Observability Surfaces

Observability is layered similarly:

- Logging via `observability_kit.logging.StructuredLogger`
- Metrics via `observability_kit.metrics.MetricsCollector`
- Tracing via `observability_kit.tracing.DistributedTracer`

Middleware and decorators in each kit accept these dependencies; they are not fetched from global state. See [Observability Kit](../kits/observability-kit.md).

## Tenancy & Context Propagation

db-kit, storage-kit, and vector-kit share a tenant context abstraction. Use `TenantContext` to propagate tenant identifiers, auth tokens, and correlation IDs across async calls. Stream-kit and event-kit observe the same context through middleware hooks.

## Error Handling Strategy

- Rich domain errors use value-object style error types (see `domain_kit.errors`).
- Infrastructure-level errors wrap underlying exceptions with additional context (e.g., `DatabaseError` with table and operation data).
- Use workflow compensation handlers to keep side effects consistent across partial failures.

## Threading & Async

All I/O heavy kits are async-first. To integrate with sync code:

- Use the provided synchronous facades (e.g., `sync_adapter` modules).
- Run blocking operations through `anyio.to_thread` helpers.
- Avoid running event loops manually; kits expose `start()`/`shutdown()` hooks for lifecycle management.

## Modular Releases

Each kit is released independently but shares the same version scheme. Shared utilities live in `lib/` and are vendored where necessary. `build-analyzer-kit` validates compatibility across kits before release.

## Extension Points

- **Plugins** – Many kits expose `register_*` methods to add providers, encoders, or middleware at runtime.
- **Callbacks** – Workflow and orchestrator kits emit lifecycle hooks for auditing.
- **Adapters** – Storage, database, vector, and event kits rely on adapter interfaces for provider-specific behavior.

## Documentation Workflow

When you introduce new architectural constructs:

1. Update this file with the clarified pattern.
2. Reference the relevant kit manual.
3. Add examples or diagrams in the appropriate concept or guide.

The goal is to keep architectural doctrine consistent with the implementation and tests.
