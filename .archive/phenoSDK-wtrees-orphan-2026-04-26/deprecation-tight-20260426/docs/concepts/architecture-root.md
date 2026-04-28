# Pheno-SDK Architecture Overview

The authoritative architecture guide now lives in [`docs/concepts/architecture.md`](docs/concepts/architecture.md). This file provides a quick synopsis and links to complementary resources.

## Monorepo Structure

**All code is now consolidated under `src/pheno/`** following a clean hexagonal architecture:

```
src/pheno/
├── core/              # Core utilities, registry, pathing
├── domain/            # Domain models and business logic
├── ports/             # Port protocols (interfaces)
├── adapters/          # Adapter implementations
├── [feature modules]  # Feature-specific modules (ai, web, data, etc.)
```

See [CONSOLIDATION_COMPLETE.md](CONSOLIDATION_COMPLETE.md) for details on the recent consolidation.

## Core Tenets
- **Composition over frameworks:** Kits expose typed contracts so teams can assemble only what they need.
- **Hexagonal architecture:** Domain → Ports → Adapters → Application. Clear boundaries and dependencies.
- **Single namespace:** All code under `pheno.*` for consistency and discoverability.
- **Async-first:** All I/O heavy kits are async, with sync facades where required. Use `anyio` helpers when bridging contexts.
- **Observability by default:** Logging, metrics, and tracing are injected dependencies rather than globals.

## Reference Materials
- Architecture fundamentals: [`docs/concepts/architecture.md`](docs/concepts/architecture.md)
- Patterns & best practices: [`docs/concepts/patterns.md`](docs/concepts/patterns.md)
- Testing & QA strategy: [`docs/concepts/testing-quality.md`](docs/concepts/testing-quality.md)
- Kit manuals: [`docs/kits/`](docs/kits)


## Packaging policy and Python baseline

- Baseline: Python 3.13 across all kits (requires-python = ">=3.13").
- Packaging: PEP 621 pyproject.toml is the canonical source of metadata.
- Legacy: setup.py files remain temporarily as legacy shims for local workflows and will be removed in a future release.
- CI: Workflows run on Python 3.13 only. Older versions are no longer tested.

Rationale: one consistent interpreter target simplifies testing, reduces dependency skew, and enables modern typing and tooling. The deprecation and removal of setup.py avoids dual sources of truth for packaging metadata.

## When Updating Architecture
1. Document the change in `docs/concepts/architecture.md` and reference affected kits.
2. Update kit manuals detailing new APIs or patterns.
3. Provide migration guidance in the relevant kit's *Change Log* section if behaviour changes.

For deep architectural details, cross-cutting diagrams, and example flows, see the documentation hub.
