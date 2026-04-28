# INTG-A1 – Pheno Analytics Code Adapters

**Status:** ✅ Complete (Design Approved)
**Date:** 2025-10-14
**Owner:** SDK Architecture Guild
**Related Tasks:** `INTG-A1`, `INTG-A2`, `INTG-A5`
**Consumers:** Morph (`morph_core` analyzers), Router (routing cost heuristics)

---

## 1. Summary

Introduce a new `pheno.analytics` namespace providing async-friendly complexity and dependency analysis built on top of radon and grimp. The abstractions expose consistent dataclasses, integrate with SDK logging/telemetry, and align with Morph/Router performance expectations.

---

## 2. Package Layout

```
src/pheno/analytics/
├── __init__.py
├── code/
│   ├── __init__.py
│   ├── complexity.py        # radon integration
│   ├── dependencies.py      # grimp integration
│   └── models.py            # shared DTOs
└── ast/
    └── __init__.py          # placeholder for INTG-A2 tree-sitter adapters
```

`setup.cfg` / `pyproject.toml` will declare optional extras `analytics-code` pulling `radon>=6.0,<7.0`, `grimp>=3.3,<4.0`.

---

## 3. API Design

```python
# src/pheno/analytics/code/models.py
@dataclass(frozen=True)
class ComplexityReport:
    module: str
    filepath: Path
    average_cc: float
    scores: dict[str, float]  # by function/class

@dataclass(frozen=True)
class DependencyEdge:
    importer: str
    imported: str
    line_no: int | None

@dataclass(frozen=True)
class DependencyGraph:
    module: str
    edges: list[DependencyEdge]
    cycles: list[list[str]]
```

```python
# src/pheno/analytics/code/complexity.py
async def analyze_complexity(
    path: Path,
    *,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    thresholds: Mapping[str, float] | None = None,
    cache: CacheProtocol | None = None,
) -> list[ComplexityReport]:
    """Run radon CC analysis over Python modules."""
```

```python
# src/pheno/analytics/code/dependencies.py
async def analyze_dependencies(
    path: Path,
    *,
    package: str | None = None,
    include_internal: bool = True,
    cache: CacheProtocol | None = None,
) -> DependencyGraph:
    """Build a dependency graph using grimp."""
```

All public APIs will emit telemetry via `pheno.logging` and `pheno.observability` hooks, making use of structured log fields (`analysis.type`, `analysis.duration_ms`, `analysis.path`).

---

## 4. Asynchronous Strategy

Radon and grimp are synchronous. Wrappers will:

1. Offload heavy work to thread pool using `asyncio.to_thread`.
2. Respect SDK cache protocol (INTG-A5) to avoid repeated scans.
3. Expose cancellation tolerant behaviour with timeouts and early exit when thresholds are satisfied.

---

## 5. Testing Strategy

- Unit tests verifying dataclass construction and telemetry fields.
- Contract tests:
  - `tests/analytics/test_complexity_contract.py`
  - `tests/analytics/test_dependencies_contract.py`
- Fixtures referencing Morph/Router sample modules to validate expected outputs.
- Performance regression test ensuring <2s analysis for Morph core baseline on standard hardware.

---

## 6. Telemetry & Configuration

- Accept optional `TelemetryContext` to propagate trace/span IDs.
- Use `pheno.config` to read defaults (`PHENO_ANALYTICS_MAX_WORKERS`, thresholds).
- Provide feature flag `pheno.analytics.radon.enabled` for safe rollouts.

---

## 7. Deliverables & Follow-ups

- [x] API spec (this document).
- [ ] Implementation & tests (future sprint).
- [ ] Documentation update in `docs/guides/integration/morph-migration.md` (INTG-A6).
- [ ] ADR covering namespace introduction (tracked under `docs/adr/TBD`).

Approved by SDK Architecture Guild on 2025-10-14.
