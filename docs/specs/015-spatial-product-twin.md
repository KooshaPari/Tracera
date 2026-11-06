# 015 — Spatial Product Twin and Semantic Physicalization

| Field | Value |
| --- | --- |
| Spec ID | TRACERA-SPEC-015 |
| Status | Draft / design proposal; not implemented by this document |
| Date | 2026-10-12 |
| Applies to | Product graph, projection APIs, front-end exploration, evidence links |
| Decision | [ADR-VIZ-001](../governance/ADR-VIZ-001-spatial-product-projections.md) |
| Ecosystem | [PhenoRegistry spatial boundary contract](https://github.com/KooshaPari/PhenoRegistry/blob/main/docs/specs/spatial-product-twin-ecosystem-contract.md) |

**Documentation dossier:** [source/intent/SOTA/ontology/implementation/evidence/gates](../product-spatial-twin/README.md). All requirement-level acceptance below remains proposed and unverified.

## 1. Intent and non-goals

Build a traversable, searchable, inspectable **spatial product twin**: a product-first, skeuomorphic and optionally literal 3D representation of software, hardware, services, infrastructure, workflows and hybrids. Users should be able to understand a product as an explorable engineered object, follow functional/structural/runtime/evidence relationships and navigate back to canonical sources.

This is **a projection of Tracera's product model**, not a new authoritative graph, replacement for 2D views, generic repository-file city, mandatory XR interface, CAD editor, or agent execution system. No 3D geometry is evidence of a physical object unless explicitly classified and sourced as physical geometry.

Related documents: [WP-07 product-first graph design](../WP-07-product-graph-design.md), [SWE-E schema](011-swe-e-graph-schema.md), [design/accessibility](014-design-tokens-wcag.md), [graph ingestion ADR](../governance/ADR-GOV-002-graph-ingestion-architecture.md).

## 2. Normative invariants

- **Identity:** every interactive scene element resolves to a canonical product-scoped entity or an explicitly derived aggregate. Never mint a second product identity for visualization.
- **Scope:** pin each projection to product, model revision/baseline, configuration/variant, environment/deployment (when applicable), and effective/observation time. Never silently mix incompatible snapshots.
- **Typed truth:** preserve edge direction, relation kind, confidence, provenance, time validity, and lifecycle/verification state. Visual adjacency or a cable is not a new semantic edge.
- **Evidence:** distinguish intended, implemented, deployed, observed, verified, failed, disputed, inferred and unknown. Unobserved is **Unknown**, not healthy or broken.
- **Authority:** scene compilation is read-only. A gesture cannot write canonical graph state or deploy a change; edits become separately authorized, reviewable proposals through existing governance/execution channels.
- **Projection parity:** the 2D graph, table/query, accessibility list and 3D scene navigate to the same canonical references.
- **No invented physicality:** geometry has a declared truth class: physical (sourced dimensions/CAD), measured/anchored, semantic (structured metaphor), or illustrative (presentation only).
- **No forced single metaphor:** assemblies, flow factories, environments, and literal digital twins may all be views over the same scope.

## 3. View and navigation contract

**Supported representation families**

| Family | Primary question | Example |
| --- | --- | --- |
| Assembly / exploded engineering cutaway | What parts exist and how do they interface? | Service modules, removable chassis, connectors |
| Factory / flow system | How does input become output? | Runtime requests, workflow stages, queues |
| Building / environment | What shares a boundary, deployment or location? | Distributed topology, subsystems, tenants |
| Literal physical twin | What corresponds to actual measured geometry? | CAD mechanism, electronics + controlling firmware |
| 2D graph / dependency matrix / table | Which precise relationships exist? | Dense edges, verification/coverage, search results |

**Navigation operations:** enter/exit scope, semantic zoom, reveal/close enclosure, explode/reassemble, X-ray, follow typed relation, isolate neighborhood, search and jump, breadcrumb/backtrack, compare revisions side-by-side, replay evidence when recorded, focus related requirement/test/source, return to stable home layout. These are semantic commands; presentational animations must not reinterpret the underlying relationship.

**Stable spatial memory:** maintain deterministic home coordinates within a given projection signature, with transient task layouts (dependency, runtime, verification) that are reversible. Stable identity does not require invariant coordinates across dissimilar metaphor layouts. Provide visible transitions, orientation landmarks, and deep links.

**Adaptive density:** load scoped subgraphs only; bundle and label edges, aggregate components, collapse containers, and route particularly dense questions to a 2D matrix or list. Never make a claim of fully displaying a million-node graph when only a slice is rendered.

## 4. Proposed contracts (not existing endpoints)

The following are conceptual contracts to refine against the actual Rust domain and current API. They **do not** assert that any route or schema exists yet.

### Projection request

~~~json
{
  "product_ref": "product:illustrative-demo",
  "baseline_ref": "revision:illustrative-v1",
  "configuration_ref": null,
  "environment_ref": null,
  "effective_at": null,
  "observed_at": null,
  "view": "assembly",
  "focus_entity_ref": "component:illustrative-api",
  "relation_kinds": ["contains", "depends_on", "implements", "verifies"],
  "max_depth": 2,
  "node_budget": 500,
  "edge_budget": 1500
}
~~~

All illustrative references above are examples, not real persisted IDs. A projection response MUST provide:

| Field | Semantics |
| --- | --- |
| projection_id / projection_version | Immutable fingerprint of query inputs + compiler rules/version |
| snapshot | Resolved baseline, configuration, environment, valid/observation time |
| entities | Canonical refs and types, stable selectable IDs, source and permission hints |
| relations | Canonical edge refs, type, direction, provenance and confidence |
| aggregates | Member-ref list or paged membership query, never a silent synthetic fact |
| glyphs | Representation type, truth class, transform, bounds, ports, LOD, style token |
| evidence | Observed/verified/unknown assertions with source refs and timestamps |
| completeness | Authorized-scope omitted entities/edges, pagination state, and a non-disclosing restricted-content flag; never return exact forbidden-entity/edge cardinalities |
| diagnostics | Layout conflicts, ambiguous mappings, missing geometry, invalid source refs |

**Identity map:** selection of a glyph resolves to one canonical entity ref, or an explicit aggregate. A port may resolve to an interface entity; a conduit resolves to a canonical relation or identified bundle of relations. Generated meshes are ephemeral and never canonical entities.

**Geometry semantics:** use standard units/frames for physical geometry; no implied real size for semantic/illustrative geometry. Geometry provenance and license must accompany imported CAD/asset data. Annotate metaphor boundaries; physical and metaphorical parts must be distinguishable without relying on color.

**Security:** scoped requests inherit graph authorization, redact hidden members, avoid revealing secret labels in aggregate counts, and do not leak topology via spatial caches. Cache keys include principal/scope and relevant permissions.

## 5. Requirements and acceptance evidence

| ID | Requirement | Demonstrable acceptance |
| --- | --- | --- |
| ST-001 | Load a scoped product and identify visible completeness | API/render fixture shows scope signature and omitted counts |
| ST-002 | Preserve entity/edge identity across views | Selecting the same node in 3D, 2D and table yields identical refs |
| ST-003 | Preserve typed/directed relations and provenance | Trace a selected relation to source, time and confidence |
| ST-004 | Classify geometry truth | Physical/measured/semantic/illustrative visibly discriminated |
| ST-005 | Deterministic stable home layout | Same scope+compiler version yields same coordinates on replay |
| ST-006 | Inspect product recursively | Open/explode/close and breadcrumb round-trip preserves context |
| ST-007 | Runtime/verification lenses | Distinguish trace observation from requirement and test outcome |
| ST-008 | Explicit unknown and missing evidence | Unverified capability never appears as verified/healthy |
| ST-009 | Time/configuration comparison | Compare two pinned baselines without silent mixing |
| ST-010 | Density controls | Budgets, edge bundles, aggregates and matrix fallback remain inspectable |
| ST-011 | Search, deep-link, keyboard and screen-reader fallback | Every demo inspection task completes without 3D pointer input |
| ST-012 | No unapproved product mutation | Scene gestures are read-only or generate separately approved proposals |
| ST-013 | Authorization and partial projections | Hidden nodes cannot be inferred through layout, labels or counters |
| ST-014 | Cross-domain reuse | One software-only and one real physical/hybrid fixture share semantic API |

Quality targets are **measurement hypotheses**, not guarantees: interaction should remain responsive at a bounded active working set; define budget/LOD, FPS, latency and memory baselines on representative devices **after** profiling. Accuracy, accessibility and task success outrank scene size or maximum frame rate.

## 6. Initial slice and evaluation

1. **P0—Semantic projection**: fix selected canonical entity/edge semantics, snapshot and reference mapping with golden fixtures. Include failure/unknown cases; no 3D yet.
2. **P1—Assembly viewer**: a single software product with containment, interfaces, ports, stable layout, enter/explode, search, source links and 2D fallback.
3. **P2—Behavior and verification**: one real capability journey tied to requirement, test, runtime trace and issue, with honest states and temporal context.
4. **P3—Scale and alternatives**: varying graph densities, bundling, adjacency matrix, keyboard/a11y tests, user comprehension experiment vs current 2D UI.
5. **P4—Hybrid**: CAD-import adapter for one physically sourced assembly and associated software; semantic vs physical geometry checks.

Require artifact-level test evidence, schema fixtures, task-level UX measures and a documented decision before graduating a prototype. Use AgilePlus for scoped specs/work packages and gated execution. Tracera remains the persistent product authority.

## 7. Outstanding decisions

- Which existing Tracera product reference and snapshot APIs can be reused without migration?
- Which interface and relationship kinds should have first-class geometric ports?
- Which geometry DSL / scene interchange is necessary? Candidates include procedural meshes, glTF and OpenUSD; no engine is selected by this spec.
- How should uncertainty, redaction, authorization changes and incomplete ingest be represented spatially?
- How do stable coordinate anchors compose across product boundaries, federated views and explicit layout changes?
- What measured comprehension improvement, if any, justifies skeuomorphic complexity against 2D/matrix alternatives?

**Current status:** design only. No CAD importer, new endpoint, 3D engine, benchmark result, UX evaluation or implementation claim is established by this commit.
