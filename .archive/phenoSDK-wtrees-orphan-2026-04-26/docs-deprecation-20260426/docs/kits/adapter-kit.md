# Adapter Kit Manual

Dependency injection, factory registries, and repository abstractions for clean architecture layering in Pheno-SDK applications.

## Overview

The Adapter Kit provides the foundational building blocks for implementing clean architecture patterns in Pheno-SDK applications. It offers dependency injection, factory registries, and repository abstractions that enable loose coupling and high testability.

## Features

- **Dependency Injection**: Constructor and provider-based DI with scoped lifetimes
- **Factory Registries**: Named registries for runtime adapter selection
- **Repository Pattern**: Async CRUD contracts with in-memory test implementations
- **Type Safety**: Full type hints and generic support throughout
- **Testing Support**: Mock-friendly design with easy test doubles
- **Legacy Integration**: Global container helper for existing codebases

## Installation

```bash
pip install adapter-kit
```

## Getting Started

### Installation
```
pip install adapter-kit
```

### Minimal Example
```python
from adapter_kit import Container, Repository, inject

class EmailService:
    async def send(self, to: str, subject: str, body: str) -> None:
        ...

container = Container()
container.register(EmailService, EmailService, singleton=True)

@inject
async def welcome_user(email_service: EmailService, user_email: str) -> None:
    await email_service.send(user_email, "Welcome", "Thanks for joining")
```

## How It Works
- `adapter_kit.di.Container` stores registrations and resolves dependencies using constructor inspection.
- `adapter_kit.PluginRegistry` keeps named implementations (e.g., `"vector:qdrant"`, `"tools:search"`).
- `adapter_kit.repository.Repository` defines the CRUD interface; extend it for your aggregates.
- `adapter_kit.inject.inject` pulls dependencies from the container within functions or coroutines.

## Usage Recipes
- Register a database connection as a singleton and repositories as scoped services.
- Use registries to choose implementations per tenant or environment.
- Combine container scopes with FastAPI dependency overrides by injecting inside dependency functions.
- Wrap expensive resources in callable factories via `register_factory` (see module docs) to defer initialization.

## Interoperability
- Domain aggregates from [domain-kit](domain-kit.md) receive repositories injected via adapter-kit.
- db-kit and storage-kit adapters are typically registered in the container and reused elsewhere.
- Observability components (loggers, tracers, metrics) are provided to middleware using the same container.

## Operations & Observability
- Emit resolver traces by hooking into `container.on_resolve` callback (configure in your bootstrap code).
- Monitor container usage by incrementing counters when resolving high-churn dependencies.
- Document container wiring in `docs/architecture.md` to keep diagrams current.

## Testing & QA
- Use `InMemoryRepository` to test domain logic without touching the database.
- Swap implementations via the container in tests; register fakes or stubs inside fixtures.
- Validate container configuration with `container.validate()` (raises when dependencies are missing).

## Troubleshooting
- **ResolutionError**: indicates the container cannot find a registration—ensure module import order is correct.
- **Circular dependency**: break the cycle using factory callables or split responsibilities.
- **Async resolution**: when dependencies require async initialization, wrap them in factories returning awaitables.

## Primary API Surface
- `Container.register(interface, implementation, singleton=False)`
- `Container.register_instance(interface, instance)`
- `Container.resolve(interface)`
- `PluginRegistry[name_type](name).register(key, implementation)` / `PluginRegistry[name_type](name).get(key)`
- `Repository` abstract methods: `get_by_id`, `list`, `save`, `delete`, `count`
- `InMemoryRepository` ready-to-use test double
- Decorators: `@inject`, `provide(interface)`


## Unified Plugin Registry (ADR-0002) — Preferred
A minimal, threadsafe, namespaced registry is available at `adapter_kit.PluginRegistry`. This replaces and removes the older `adapter_kit.registry.ClassRegistry` and `InstanceRegistry`. Use namespaced keys like `capability:provider`.

Example:

```
from adapter_kit import PluginRegistry

vector_stores = PluginRegistry[object]("vector")
vector_stores.register("qdrant:client", QdrantClient, metadata={"version": "1.0"})
store_cls = vector_stores.get("qdrant:client")
```

Migration note:
- Replace ClassRegistry with PluginRegistry[type]("<namespace>") and register as `<ns>:<name>`.
- Replace InstanceRegistry with PluginRegistry[YourType]("<ns>") and store instances (or factories) as values.
- Legacy registries have been removed in this repository; use PluginRegistry exclusively.

Notes:
- Keys support namespaces like `"vector:qdrant"` or using the registry name as the prefix.
- Optional entry point loading via `load_entry_points(group="pheno.plugins")`.
- Use `metadata()`/`set_metadata()` to annotate entries with version/tags.

## Additional Resources
- Examples: `adapter-kit/examples/`
- Tests: `adapter-kit/tests/`
- Related concepts: [Architecture fundamentals](../concepts/architecture.md), [Patterns](../concepts/patterns.md)
