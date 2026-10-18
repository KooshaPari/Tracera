# Tracera spatial product twin — repo-local AgilePlus work specification

**Work ID:** TRACERA-SPATIAL-001  
**State:** PROPOSED / NOT registered in AgilePlus SQLite or accepted.  
**Date:** 2026-10-13  
**Source:** [TRACERA-SPEC-015](../../specs/015-spatial-product-twin.md) and [intent/Genesis](../../product-spatial-twin/00-INTENT-GENESIS.md) in documentation PR #1104.  
**Engineering pilot:** PR #1122. **Ecosystem decision:** PhenoRegistry PR #626.  
**Scope owner:** Tracera product model. **Execution governance:** AgilePlus. **Registry:** PhenoRegistry only records boundaries.

## User outcome

Import or open a **real** software product with stable product and baseline identity. Traverse its nested capabilities/components and typed edges from an accessible frontend or CLI/API, inspect source and evidence, see unknown/failed/stale verification correctly, replay a pinned revision after restart, and optionally physicalize the same facts into an inspectable semantic assembly. Later prove hardware/firmware/CAD provenance in the same ontology.

No mock-only demonstration, fake source/geometry, unapproved live mutation, or declaration of universal 3D superiority.

## Acceptance / consumer contract

1. Product and capability IDs remain distinct throughout the API/store/graph; every scoped query prevents cross-product leakage.
2. Every observation explicitly pins product, capability (when capability-level), baseline, source and recorded time; no product ID inferred as capability ID.
3. Missing, stale, inconclusive or unknown evidence never displays as satisfied.
4. Relation edges preserve type, direction, source and revision/configuration/effective-time semantics.
5. SQLite/Postgres persist and query the same full model with clean restart and migrations.
6. A real product graph is consumed through a supported API, not a static JSON screenshot.
7. Scene IR is deterministic, source-anchored, budgeted, permission-aware, read-only and renderer-agnostic.
8. Keyboard/list and existing 2D graph remain effective; 3D selection retains identical canonical IDs.
9. Partial scope, permission-denied and paginated content is marked incomplete, not incorrectly green or complete.
10. Real hardware fixture uses CAD source with units, frame, license, and clearly distinct metaphor geometry.
11. Negative tests cover duplicate/missing refs, conflicting baselines, malicious payloads, stale evidence, redaction, cycles and oversized input.
12. Browser/native test fixtures, production verification and independent negative oracles must pass before accepting ADR-VIZ-001.

## Work boundaries

- Tracera: product graph, data adapters, typed projection API and views.
- AgilePlus: repo-local specification and work-state transitions, not persistent product authority.
- PhenoRegistry: source-backed intent/boundary SSOT and dated provenance.
- Design/CAD/telemetry sources: retain their own asset/measurement authority.

### Excluded from first executable slice

Full GPU/photorealistic renderer, arbitrary CAD synthesis, physical simulation, VR, global all-node instantiation, external agent execution and fleet-wide content mutation.

**Status honesty:** PR #1122 adds experimental Rust contracts, API and CSS-depth pilot. The complete witness above is NOT proven or accepted yet; do not mark tasks done based on commits alone.
