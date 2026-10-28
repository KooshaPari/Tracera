# ADR-VIZ-001: Semantic-to-Spatial Product Projections

| Field | Value |
| --- | --- |
| Status | Proposed — review required |
| Date | 2026-10-12 |
| Scope | Tracera product model and presentation adapters |
| Related spec | [TRACERA-SPEC-015](../specs/015-spatial-product-twin.md) |
| Ecosystem boundary | [PhenoRegistry ADR-ECO-024](https://github.com/KooshaPari/PhenoRegistry/blob/main/docs/adrs/ADR-ECO-024-spatial-product-twin-boundary.md) |

## Context

Tracera's long-lived product graph must connect product intent, capabilities, obligations, implementations, verification and observations. Graph-city and network renderings can be useful but often obscure functional decomposition, cross-domain hardware/software relationships and causes of failure. A skeuomorphic 3D assembly can make software tangible, yet risks presenting metaphorical geometry as fact and overwhelming users with dense edges.

The proposed spatial view must preserve the existing product-first model (WP-07), SWE-E evidence links, project scope and the existing 2D/table surfaces. This ADR evaluates a presentation architecture, **not** a new source of product truth.

## Proposed decision

1. Keep the canonical versioned product/relationship/evidence model authoritative. Implement a **read-only, scoped semantic projection** over it.
2. Compile that projection to a separate spatial scene representation with stable glyph-to-entity/edge mapping, deterministic versioned layout rules, ports, bounds, LOD and truth/provenance metadata.
3. Treat **physical, measured, semantic and illustrative** geometry as different truth classes. Their transforms and scale assumptions may not be conflated.
4. Support multiple coordinated views: assembly/cutaway, factory/flow, environment/topology, imported physical geometry, 2D graph, matrix and accessible list. Shared navigation/selection addresses canonical IDs, not mesh IDs.
5. Preserve confidence, status, missing evidence, aggregate membership, authorization/redaction and completeness when producing geometry. A healthy-looking metaphor must never imply validated functionality.
6. Make scene interactions non-authoritative. A prospective edit becomes an explicit proposal validated through product governance and optionally executed by AgilePlus/external agents; no implicit write-on-drag.
7. Prioritize a browser-based inspectable prototype. Renderer and interchange stack remain open decisions pending constraints and benchmark evidence; XR is optional.

## Alternatives considered

| Alternative | Advantage | Why not default |
| --- | --- | --- |
| Replace canonical graph with a 3D scene graph | Single apparent representation | Loses typed semantics, evidence identity and multi-view fidelity |
| Single universal software-city layout | Strong persistent spatial metaphor | Files/buildings poorly model capability, behavior and physical products |
| One fixed skeuomorphic machine for every question | Consistency and visual polish | Misleads for flow, topology and high-degree relationships |
| Pure 2D graph/matrix only | Cheap, explicit, accessible | Cannot test tangible decomposition and cross-domain digital twin comprehension |
| Separate CAD/digital-twin product | Mature physical modeling possibilities | Fragments Tracera identity and creates duplicate product authority |
| General-purpose XR first | Immersive manipulation | Device constraints and a11y cost before validating comprehension |

## Consequences

**Benefits:** task-oriented explorable product model; reversible decomposition; cross-domain geometry; same selected entity across functional, architectural, runtime and verification lenses.

**Costs:** layout compiler, scene cache, asset provenance, permissions, rendering budgets, interaction mapping, accessibility parity, versioning and empirical UX testing. Geometry may wrongly convey scale, causality or certainty; classification and source inspection are required mitigations.

**Constraints:** schema contract must remain renderer-agnostic; avoid inventing dependencies merely for visual storytelling; no persistent scene position becomes a domain fact unless separately modeled and sourced.

## Verification before acceptance

- Run identity/parity and permission fixtures against the same selected product nodes/edges in 2D, 3D and list.
- Round-trip one workflow from user-visible capability to source, runtime trace, failure and test evidence.
- Prove repeatable home layout for pinned scope + compiler version; diagnose layout conflicts.
- Demonstrate unknown/unobserved states, omissions, edge bundling and dense-graph fallback.
- Conduct measured comprehension tasks against current graph views; reject visualization if it degrades task correctness, navigation or accessibility.
- Verify proposed edits cannot mutate graph/deployments without approved authority.

## Residual risks and follow-up

Whether skeuomorphic visuals improve specific tasks is **unproven**; CAD licensing/import, federated scope, source-of-truth drift, security/redaction and very large graph rendering remain open. Proceed with staged prototypes in the linked specification; acceptance of this ADR requires real test and user evidence. This record proposes no framework mandate or implementation claim.
