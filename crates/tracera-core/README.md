# `tracera-core`

**Status**: scaffold (2026-06-10) — Phase 0 of decouple plan  
**Source plan**: `plans/2026-06-09-tracera-decouple-plan-v1.md`  
**Authority**: User directive 2026-06-10: "decouple the frontend 'product' from the backend live service and the headless logic/backend that agileplus and others may want to consume/build off of"

The canonical home for the TraceLink entity model, FR/NFR enums, matrix/coverage/gap logic, impact scoring, and graph/code/doc/equivalence/embedding core logic.

## Consumers

- `tracera-live` (Go backend) — consumes via FFI / cbindgen
- `tracera-mcp` (Python service) — consumes via PyO3
- `@kooshapari/tracera-product` (TypeScript frontend) — consumes via generated TS types
- `AgilePlus` (Rust workspace) — consumes as `tracera-core = { git = "...", version = "0.1" }`

## Phase Plan

| Phase | Goal | Status |
|---|---|---|
| 0 | Scaffold + interface freeze | ✓ 2026-06-10 |
| 1 | Port `trace_link.py` (Python) → Rust types | pending |
| 2 | Port `internal/traceability/types.go` → Rust types | pending |
| 3 | Port matrix/coverage/gap logic | pending |
| 4 | Generate cbindgen headers for Go FFI | pending |
| 5 | Generate PyO3 module for Python | pending |
| 6 | Generate TS types via ts-rs or specta | pending |
| 7 | Migrate `tracera-live` to FFI consumer | pending |
| 8 | Migrate `tracera-mcp` to PyO3 consumer | pending |
| 9 | Wire `AgilePlus` as Rust consumer | pending |

## SOTA wraps (per agent-wave1 SOTA research)

- **Kuzu** (MIT) — embedded graph DB for PKG store
- **StrictDoc** (Apache-2.0) — repo-native requirements spine
- **OpenFastTrace** (MIT) — code↔spec coverage
- **Graphiti** (Apache-2.0) — temporal knowledge graph for agent memory
- **Promptfoo + OpenTelemetry GenAI** — autograder + cross-vendor event schema

## Source references (to port)

- Python: `Tracera/src/tracertm/models/trace_link.py` (modified 2026-06-08)
- Go: `Tracera/backend/internal/traceability/types.go` (1,224 LOC)
- Python: `Tracera/src/tracertm/services/spec_analytics_service.py`
- Go: `Tracera/backend/internal/services/matrix_service.go`
- TypeScript: `Tracera/frontend/packages/types/src/`

See: `plans/2026-06-09-tracera-decouple-plan-v1.md` for the full Wave A / Wave B plan.
