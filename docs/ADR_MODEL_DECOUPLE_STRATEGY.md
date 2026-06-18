# ADR: Tracera Model Decoupling — thin-service on traceability-core

## Status
DRAFT — Pending phenotype-pm-core availability and decision on re-export approach.

## Context
Tracera currently defines its own domain models (Artifact, TraceLink, Requirement, etc.) in `src/tracertm/models/`. These models are now canonical in the shared **traceability-core** (merged into phenotype-pm-core per PR #2). To implement the "two graphs, one product" spine:
- **AgilePlus** authors and publishes the traceability specification
- **Tracera** provides the runtime service (FastAPI + Neo4j)
- Both consume the **single canonical traceability-core**

This ADR evaluates the model re-export strategy.

## Decision: Generated Python Mirror (vs. PyO3)

**Option A: PyO3 Bindings** (Rust → Python)
- Pros: Type-safe, compile-time checks, single-source-of-truth
- Cons: Requires Rust expertise, slow build, platform-specific wheels

**Option B: Generated Python Mirror** (codegen Rust → Python)
- Pros: Pure Python, fast development, simple deployment
- Cons: Requires codegen tool, sync discipline

**CHOSEN: Option B (Generated Python Mirror)**
- Rationale: Tracera is Python-first; codegen overhead is small; reduces deployment complexity
- Implementation: serde-json-schema or similar to generate Python dataclass mirrors from Rust models
- Sync: Include `cargo generate-python-models` in CI pre-test, fail CI if models drift

## Implementation Plan

### Phase 1: Stub (this PR)
- [ ] Create `src/tracertm/core_types.py` — placeholder for generated mirror
- [ ] Document codegen hook (comment with command to regenerate)
- [ ] Update imports in models/artifact.py, models/trace_link.py to from-import canonical types
- [ ] Verify existing tests pass with stub (tests should target endpoints, not internal models)

### Phase 2: Codegen & Wire (next PR)
- [ ] Implement codegen tool (or use existing serializer)
- [ ] Generate Python from Rust traceability-core
- [ ] Wire codegen into CI (pre-test check)
- [ ] Run all tests with generated types

### Phase 3: Remove Duplicates
- [ ] Delete old model definitions
- [ ] Keep only re-exports + service logic

## Test Strategy
- All endpoint tests (coverage-matrix, impact, spec-check) should PASS unchanged
- Proof: identical results using canonical core types (measured via comparison test)

## Open Questions
- phenotype-pm-core location/clone URL?
- Codegen tool already in place, or build custom?

## Related ADRs
- [[ADR_SUPERSET_MERGE_STRATEGY]]
- [[ADR_TWO_GRAPHS_ONE_PRODUCT]]
