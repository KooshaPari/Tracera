# Bounded implementation mapping and gap register

**Anchor:** Tracera `main` commit `9a4360e812eeee81ee7c0367b12a967cf7764440`, inspected 2026-10-12. This is a **text-only spot-check**, not a build, route mount, test result, deployment or exhaustive audit.

| Concern | Observed source | Assessment | Next proof |
| --- | --- | --- | --- |
| Stable product identity | `crates/tracera-server/src/product/identity.rs` | Types `ProductId`, `BaselineRevision`, accepted intents present | Database round trip + API read on real product |
| Product domain modules | `crates/tracera-server/src/product/mod.rs` | Declared baseline, observations, traversal, detectors, queries, assessment | Verify mounted route, data path and fixture |
| Product-first graph | `docs/WP-07-product-graph-design.md` | Draft design in docs | Match source migrations + end-to-end UI witness |
| Trace/evidence graph | `docs/specs/011-swe-e-graph-schema.md` | Typed SWE-E proposal/historical contract | Actual schema and provenance parity |
| Frontend spatial indexing | `frontend/apps/web/src/lib/spatialIndex.ts`, `spatialQuadtree.ts`, `edgeSpatialIndex.ts` | 2D/viewport indexing logic exists | Inspect consumer integration and performance |
| 3D semantic compiler | No qualified source identified in bounded sampling | **NOT VERIFIED; do not infer absence** | Code search, dependency audit, runtime inspect |
| 3D viewer / CAD importer | No qualified mounted feature identified in bounded sampling | **NOT VERIFIED** | Bundle/UI/e2e inspect |
| Geometry-truth provenance | This proposal only | **NOT IMPLEMENTED BY THIS DOC** | Read/compile round-trip fixture |
| Cross-view identity parity | Draft acceptance only | **UNTESTED** | UI + API + accessible list fixture |
| Authorization / safe edits | Existing auth/governance principles; new gesture contract proposed | **UNTESTED** | Negative authorization tests |

## Planned components (do NOT confuse with existing paths)

- `SemanticProjectionPort` read-only domain interface or equivalent existing query port.
- Projection normalizer validating type, time/baseline, source, permission, completeness and budgets.
- Deterministic scene IR with versioned layout and semantic glyph mappings.
- Browser renderer adapter; a11y tree and 2D matrix backed by identical projection signature.
- Scene selection/navigation state with deep links and breadcrumbs.
- Optional physical asset importer; separate permission and source inspection gate.

## Contradictions to reconcile

Root `README.md`, `ARCHITECTURE.md` and `docs/ARCHITECTURE.md` contain trace-ledger-first descriptions, whereas `docs/WP-07-product-graph-design.md` and newer product code/owner intent describe a product-first layer. Mark each as historical/current implementation/product intent; do not assign all of them equal authority. Registry CVP is historical and bounded, not automatic proof of today's endpoints.

## No implementation conclusions

A source symbol, migration, compiled file, green CI, screenshot, endpoint listing, PR description or documentation score alone does not establish that a real product was imported, traversed, diagnosed and persisted. Exact tested binary/source/consumer/environment and independent oracle receipts must be furnished.
