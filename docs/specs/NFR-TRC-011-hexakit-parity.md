# NFR-TRC-011: HexaKit Canonical Ports Mirror

**Status:** Scaffolded (W35, Phase 0)  
**Owner:** Platform / Pillar-A Spine  
**Related:** FR-TRC-018, FR-TRC-019, NFR-TRC-010  
**Document Version:** 1.0 (2026-06-16)

---

## Executive Summary

NFR-TRC-011 ensures that **all of Tracera's port interfaces are documented and tested as canonical mirrors of the HexaKit pattern**, enabling cross-repo parity validation and predictable implementations in Rust, TypeScript, and other languages. This requirement makes Tracera's platform contracts portable, machine-readable, and compatible with heterogeneous service ecosystems.

---

## Problem Statement

Today, service boundaries in Tracera are defined by informal contracts:
- Services write to Neo4j directly (violates NFR-TRC-010)
- Scorer strategies are baked into callsites (blocks Pillar C embedding/VLM strategies)
- Model serialization adapters are ad-hoc (complicates cross-service ML integration)

**Without canonical, HexaKit-mirrored port definitions:**
- Rust HexaKit ports cannot be validated for parity with Python
- New implementations (Go, Java, TypeScript) have no compliance target
- Port changes ripple across multiple languages without systematic tracking

---

## Definition: HexaKit Canonical Port Pattern

A **canonical port** follows these structural rules:

### 1. **Abstract Interface (Protocol or ABC)**
   - Defined as a Python `Protocol` with `@runtime_checkable`, or an ABC
   - Enables duck typing (any compliant implementation is accepted)
   - No dependencies on concrete adapters

### 2. **Dependency-Free Contract**
   - Port definition uses **stdlib only** (typing, dataclasses, enum, abc)
   - Can be mirrored 1:1 to Rust, Go, TypeScript without vendoring external libs
   - Concrete implementations (adapters) may have dependencies, but the port itself does not

### 3. **Typed Methods with Clear Intent**
   - All methods have **full type annotations** (parameters and return types)
   - Method names are **domain-specific**, not generic (e.g., `score`, not `run`)
   - Docstrings explain the **contract**, not just the implementation

### 4. **Strategy Pattern (for pluggability)**
   - Ports enable the **Strategy pattern**: multiple implementations, same interface
   - Callers depend on the port, not the implementation
   - Example: `ScorerPort` → `JaccardScorer`, `EmbeddingScorer`, `VLMScorer` (swappable)

### 5. **Stable, Documented Location**
   - Each port lives in a canonical, unchanging module path (e.g., `tracertm.ports`)
   - Exported in `__init__.py` for discoverable APIs
   - Version stable: breaking changes → new port version (e.g., `GraphPortV2`)

---

## Scope: Tracera Canonical Ports (Phase 0)

### In Scope (Scaffolded W35)

| Port | Location | Pattern | Purpose |
|------|----------|---------|---------|
| **GraphPort** | `tracertm.ports.graph_contract` | Protocol | Single graph writer contract (FR-TRC-018, NFR-TRC-010) |
| **ScorerPort** | `tracertm.ports.scorer` | Protocol | Pluggable requirement↔artifact scorer (FR-TRC-019) |
| **ModelAdapter** | `tracertm.ml.registry` | Protocol | Pluggable model serialization (Pillar A/C shared) |

### Implementations Provided (Phase 0)

| Implementation | Port | Dependency | Status |
|---|---|---|---|
| `JaccardScorer` | `ScorerPort` | stdlib | Reference (W35) |
| `PickleAdapter` | `ModelAdapter` | stdlib | Reference (W35) |
| `SklearnJoblibAdapter` | `ModelAdapter` | scikit-learn | Optional (W35) |
| `PyTorchAdapter` | `ModelAdapter` | torch | Optional (W35) |
| `OnnxAdapter` | `ModelAdapter` | (bytes) | Optional (W35) |

### Out of Scope (Phase 1+)

- **EmbeddingScorer** (SentenceTransformer, SigLIP) → Pillar A Phase 1
- **VLMScorer** → Pillar C Phase 2 (FR-TRC-020)
- **Neo4j Adapter** for GraphPort → Pillar A Phase 1 (migration of existing writer)
- **StoragePort** (CRUD abstraction) → Pillar B Phase 1
- **EventBusPort** (async pub/sub) → Pillar D Phase 1

---

## Acceptance Criteria

### AC-1: All Canonical Ports Are Importable
```python
from tracertm.ports import GraphPort, ScorerPort  # ✓
from tracertm.ml.registry import ModelAdapter     # ✓
```
- Each port is exported in its module's `__init__.py`
- No hidden or nested ports

### AC-2: All Ports Use Protocol with @runtime_checkable
```python
@runtime_checkable
class ScorerPort(Protocol):
    ...
```
- Enables duck typing (any matching impl is accepted)
- Allows `isinstance()` checks at runtime

### AC-3: All Methods Have Type Annotations
```python
def score(self, requirement_text: str, artifact_text: str) -> ScoreResult:
    ...
```
- Parameters and return types fully specified
- Enables static type checkers (mypy, Pyright)

### AC-4: All Ports Are Dependency-Free (in Definition)
```python
# tracertm/ports/graph_contract.py
from typing import Protocol, Sequence, Mapping  # stdlib ✓
from dataclasses import dataclass  # stdlib ✓
# NO: from neo4j import Driver  # ✗ would violate contract
```
- Port definitions use **only stdlib**
- External deps belong in adapters, not the port itself

### AC-5: All Ports Have Docstrings with Purpose and FR/NFR
```python
@runtime_checkable
class GraphPort(Protocol):
    """The sole writer/reader contract for graph truth (FR-TRC-018).
    
    Every pillar writes the graph *only* through an implementation of this port
    (NFR-TRC-010). ...
    """
```
- States the requirement it satisfies (FR/NFR)
- Explains why the port exists (problem it solves)

### AC-6: Concrete Implementations Satisfy Protocol
```python
scorer = JaccardScorer()
assert isinstance(scorer, ScorerPort)  # ✓ duck-typed satisfaction
```
- All provided implementations must pass `isinstance()` checks
- New implementations must also satisfy the protocol

### AC-7: Test Coverage ≥ 10 Tests per Port
- GraphPort: 5+ tests (import, protocol check, method discovery, validation)
- ScorerPort: 3+ tests (import, strategy pattern, implementation satisfaction)
- ModelAdapter: 2+ tests (import, adapter satisfaction)
- **Total:** 25+ tests in `tests/unit/ports/test_hexakit_parity.py`

---

## Current Status: Port Compliance Matrix (W35)

| Port | Importable | Protocol | Typed | Dep-Free | Docstring | Tests | Status |
|------|:----------:|:--------:|:----:|:--------:|:---------:|:-----:|--------|
| GraphPort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **COMPLIANT** |
| ScorerPort | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **COMPLIANT** |
| ModelAdapter | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **COMPLIANT** |

---

## HexaKit Mirror Validation

### Rust HexaKit Parity (Future)

When HexaKit Rust ports are implemented, they **must** mirror Python:

```rust
// hexakit-ports/src/ports/graph_contract.rs (Phase 1)
pub trait GraphPort {
    fn upsert_node(&mut self, node: &GraphNode) -> Result<(), GraphError>;
    fn upsert_edge(&mut self, edge: &GraphEdge) -> Result<(), GraphError>;
    // ... (all methods from Python port)
}
```

**Parity Rules:**
1. Method names must be identical (snake_case in Rust, unchanged)
2. Parameter types must map cleanly (e.g., `Sequence[T]` → `&[T]`, `Mapping[K, V]` → `HashMap<K, V>`)
3. Return types must be semantically equivalent (Python `None` → Rust `()`, Python exceptions → Rust `Result`)
4. Docstrings must reference the same FR/NFR

### Validation Script (Phase 1)

```python
# ci/validate_hexakit_parity.py (future)
def check_rust_port_parity(rust_module: str, python_port: Type[Protocol]) -> bool:
    """Verify Rust impl has all methods from Python port."""
    python_methods = set(p for p in dir(python_port) if not p.startswith("_"))
    # Parse Rust module, extract trait methods
    # Compare: method names, parameter count, return type shape
```

---

## Testing Strategy

### Unit Tests (W35)
- **File:** `tests/unit/ports/test_hexakit_parity.py`
- **Coverage:** 25+ tests
  - Port importability (3)
  - Protocol compliance (3)
  - Method discovery (3)
  - Implementation satisfaction (5)
  - Dependency-free validation (3)
  - Strategy pattern (2)
  - Docstring validation (2)
  - HexaKit structural parity (2+)

### Integration Tests (Phase 1)
- Verify Neo4j adapter implements GraphPort
- Verify embedding scorer implements ScorerPort
- End-to-end: service → port → adapter → storage

### Cross-Repo Validation (Phase 1+)
- HexaKit Rust ports mirror Python 1:1
- CI job: `ci/validate_hexakit_parity.sh` (compares method names, params, returns)

---

## Rollout Plan

### Phase 0 (W35) — Scaffold
- [x] Define canonical port pattern (this document)
- [x] Document existing 3 ports (GraphPort, ScorerPort, ModelAdapter)
- [x] Verify all 3 are compliant (AC-1 through AC-7)
- [x] Write 25+ unit tests (`test_hexakit_parity.py`)
- [ ] Merge to `integration/consolidate`

### Phase 1 (W36+) — Migrate & Extend
- [ ] Implement Neo4j GraphPort adapter (graduate from internal writer)
- [ ] Implement EmbeddingScorer (SentenceTransformer)
- [ ] Add HexaKit Rust mirror validation to CI
- [ ] Document Rust port mirror template

### Phase 2 (W40+) — Ecosystem
- [ ] Introduce TypeScript/Go ports (via HexaKit)
- [ ] Add VLMScorer (Pillar C, FR-TRC-020)
- [ ] Define StoragePort (multi-backend CRUD)
- [ ] Add cross-repo parity CI gate

---

## Design Rationale

### Why HexaKit Pattern?
- **Hexagonal Architecture** (Alistair Cockburn) separates domain from infrastructure
- **HexaKit** (Tracera's port library) makes ports a first-class, language-agnostic abstraction
- **Rust/Python parity** ensures semantic compatibility across polyglot services

### Why Protocols (Not ABCs)?
- `Protocol` + `@runtime_checkable` enables **structural subtyping** (duck typing)
- No inheritance chain required (cleaner for adapters)
- Compatible with PEP 544 static typing (mypy, Pyright)

### Why Dependency-Free Definitions?
- Ports must be **mirrored** to Rust, Go, TypeScript without vendoring
- External deps (Neo4j driver, torch, sklearn) belong in adapters, not the contract
- Keeps port definitions lean (< 100 LOC typical)

### Why Docstrings with FR/NFR?
- **Traceability:** every port traces back to a requirement
- **Governance:** port changes are visible to stakeholders (FR owners)
- **Cross-repo:** HexaKit maintainers can verify parity by reading docstrings

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| **Port definition changes break existing code** | Versioning: `GraphPortV1` vs `GraphPortV2` in same module; phased migration |
| **Rust ports drift from Python (no automated sync)** | CI job to parse both and report discrepancies; manual review gate |
| **Adapters accumulate; hard to discover which one to use** | Registry in module docstring + selection comments in code |
| **Team invents new ports without consensus** | Port ADR process (Port Proposal → Pillar Owner → Steering) |

---

## Success Metrics (Phase 0→1)

1. **All 3 initial ports compliant** (AC-1 through AC-7) → W35 ✓
2. **25+ tests passing** → W35 ✓
3. **Zero external deps in port definitions** → W35 ✓
4. **Rust HexaKit mirror defined** (method parity) → W36
5. **Neo4j adapter graduated** (implements GraphPort) → W36
6. **CI validates Rust↔Python parity** → W37

---

## References

- **Platform Blueprint:** `docs/TRACERA_PLATFORM_RND.md` (PR #493)
- **Requirements:** `docs/requirements/tracera-frnfr.md` (FR-TRC-018, FR-TRC-019, NFR-TRC-010)
- **Hexagonal Architecture:** Cockburn, A. (2005) "Ports and Adapters" pattern
- **HexaKit Specification:** `docs/HEXAKIT_PORTS.md` (TBD, Phase 1)

---

## Document History

| Date | Author | Change |
|------|--------|--------|
| 2026-06-16 | Platform / L1 | Initial scaffold (W35, Phase 0) |

