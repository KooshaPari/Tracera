# Frozen source coverage and internal archaeology

**Collection:** 2026-10-12, repository reading only; no checkout/build/runtime or complete git-history archaeology performed.
**Tracera default-branch anchor:** `9a4360e812eeee81ee7c0367b12a967cf7764440`.
**PhenoRegistry default-branch anchor:** `d756f068cc08903e250a4e5d63508639b69f3ba7`.
**Source class:** repo text from GitHub connector. Branch/PR drafts after these anchors are authored proposal artifacts, not independent evidence.

| ID | Source at frozen revision | Authority / inspected statement | Limitation |
| --- | --- | --- | --- |
| S01 | `docs/WP-07-product-graph-design.md` | Product identity above SWE-E; product/capability/obligation/target design | Draft design, not implementation verification |
| S02 | `docs/WP-00-reconciliation.md` | Historical requirement R01–R36 accounting and gaps at 2026-09-16 | Stale by design; cannot override current code |
| S03 | `crates/tracera-server/src/product/mod.rs` | Modules exposed: identity/baseline/observation/traversal/queries/ingest/assessment/detectors | API declarations not proof of mounted runtime behavior |
| S04 | `crates/tracera-server/src/product/identity.rs` | `ProductId`, `BaselineRevision`, `AcceptedIntent`, intent kinds | Type declarations alone do not prove persistence/consumer parity |
| S05 | `docs/specs/011-swe-e-graph-schema.md` | Historic SWE-E node/edge evidence schema | Different scope from product-first authority |
| S06 | `docs/specs/014-design-tokens-wcag.md` | Accessibility/token expectations | No spatial viewer-specific audit yet |
| S07 | `docs/ARCHITECTURE.md`, `README.md` | Current documents still foreground trace/observability | Document identity conflicts with newer user intent |
| S08 | `frontend/apps/web/src/lib/spatialIndex.ts`, `spatialQuadtree.ts`, `edgeSpatialIndex.ts` | Existing 2D/viewport spatial indexing | Name does NOT establish an implemented 3D scene compiler |
| S09 | PhenoRegistry `docs/intent/Tracera.md` and `docs/boundary/Tracera.md` | 2026-09-20 narrower CVP and boundary | Older dated view; separate long-horizon correction needed |
| S10 | PhenoRegistry `docs/governance/atlas/products/Tracera/DOSSIER.md` and `STATE.md` | Already recognizes persistent model and dissatisfaction as intended | Program dossier; not execution proof |
| S11 | PhenoRegistry `docs/SSOT.md` | Defines curated bindings and `render-per-repo.py` generation | Listed script NOT found at `scripts/render-per-repo.py` in inspected default branch |

## Source status and omissions

- **Current conversation user prompt:** preserved verbatim in [intent](00-INTENT-GENESIS.md), but no independent original transcript hash or materialized source ledger has been produced.
- **External literature:** comparator names and links in [SOTA](02-SOTA-ALTERNATIVES.md) are *discovery seeds*, not a comprehensive or version-pinned scientific review.
- **Implementation:** only selected Rust code, docs and frontend files were inspected. No exhaustive symbols, historical branches, network traces, actual UI builds, CI execution or consumer acceptance.
- **Source authority:** user intent is an authoritative goal, not evidence that the feature exists. Tests, ADRs, screenshots, metrics and green PR labels are insufficient without actual execution/consumer evidence.
- **Potential contradiction:** old trace-ledger wording is not deleted; reconcile as bounded historical CVP vs current long-horizon intent, with an explicitly sourced revision.

## Research and recovery to perform

Harvest raw user intent and hashes; audit full Tracera product graph data path; inspect frontend graph architecture and contracts; record available visualizer/compositor libraries and versions; inspect competitor primary sources and reproduce task scenarios; verify real product fixtures; confirm PhenoRegistry binding generator/owner; inventory current deployment and installed artifact. Mark each line VERIFIED only with a source pin and exact tested artifact.
