# ADR 0002: Unified Plugin Registry API

- Status: Proposed
- Date: 2025-10-12
- Decision Makers: Pheno-SDK Core Team
- Tags: plugins, registry, extensibility, API stability

## Context
Multiple kits use a form of registry (adapter-kit registries, build-analyzer parser registry, etc.). These implementations are similar but not consistent, which increases cognitive load and hinders reuse.

## Decision
Create a tiny, reusable Plugin Registry API (in a new mini-kit or within adapter-kit as a public, standalone module) with the following stable surface:

- register(name: str, obj: T, *, replace: bool = False) -> None
- get(name: str) -> T
- try_get(name: str) -> T | None
- list(prefix: str | None = None) -> dict[str, T]
- entrypoint integration (optional): load from Python entry points group
- optional typing support for categories: Registry[T]

Guidelines:
- Namespaced keys: "capability:provider" (e.g., "vector:qdrant").
- Immutable snapshots for read paths; thread-safe writes.
- Versioned capabilities: optional metadata {version, description, tags}.
- Clear error semantics (KeyError vs None).

## Alternatives Considered
- Keep per-kit registries (status quo): leads to divergence, duplicated code.
- Depend on entrypoints-only: lacks programmatic registration flexibility.

## Consequences
Pros:
- Consistency across kits; simpler docs and examples.
- Easy discovery/listing; better testing of plugin availability.
- Enables external adapters to register cleanly.

Cons:
- Small migration needed for existing registries.

## API Sketch
```python
from typing import Generic, TypeVar
T = TypeVar("T")

class Registry(Generic[T]):
    def __init__(self, name: str):
        self._name = name
        self._items: dict[str, T] = {}
    def register(self, key: str, item: T, *, replace: bool = False) -> None: ...
    def get(self, key: str) -> T: ...   # KeyError if missing
    def try_get(self, key: str) -> T | None: ...
    def list(self, prefix: str | None = None) -> dict[str, T]: ...
```

## Migration Plan
- Provide a drop-in Registry type and helper functions.
- Update adapter-kit registry exports to re-export the standard type.
- Refactor kits gradually; keep shims to avoid breaking imports.

## Open Questions
- Hosting: separate mini-kit (plugin-registry) vs adapter-kit.submodule?
- Do we include metadata and discovery filters now or iterate later?
