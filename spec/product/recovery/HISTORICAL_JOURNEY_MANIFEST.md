# Historical Journey Manifest

**Date:** 2026-09-30  
**Recovery branch:** `spec/mature-product-contract-v1`  
**Primary pre-performance anchor:** `0e8b0bdd9e4d17245e0456fc107a86439361ffdd`

## Purpose

Recover user-visible product behavior without confusing later source accumulation with the product that was actually present before the Jan-30 performance campaign.

This manifest separates:

1. **PRE-PIVOT SPINE** — behavior/source that is committed at `0e8b0bdd`;
2. **D529 BREADTH** — substantial additional intent first committed in `d5296270`;
3. **CURRENT CANDIDATE** — today's source wiring;
4. **RUNTIME VERIFICATION** — still required before declaring a journey recovered.

Source parity is not runtime parity.

## Classification

- **SOURCE_PARITY_STRONG** — recognizable current source and entry path preserve the historical behavior shape.
- **TOPOLOGY_CHANGED** — the capability still has a source path but navigation/composition changed.
- **ENTRYPOINT_NOT_FOUND** — implementation source survives but no production entry path was found.
- **D529_ONLY** — capability is not in the `0e8b0bdd` committed baseline and first enters Git in d529.
- **RUNTIME_UNKNOWN** — no current browser/runtime witness has closed the journey.
- **REGRESSED** — a concrete current contradiction exists against accepted/historical behavior.
- **RUNTIME_VERIFIED** — independent current execution has demonstrated the journey.

## Pre-pivot product spine

### HJ-PRE-001 — open a project

**Historical path**

```text
/projects/
  → ProjectsListView
  → /projects/:projectId
  → ProjectDetailView
```

Historical evidence:
- `routes/projects.index.tsx`
- `routes/projects.$projectId.tsx`
- `views/ProjectDetailView.tsx`

**Current path**

```text
/projects
  → ProjectsListView
  → /projects/:projectId
  → ProjectDetailView
```

Current source preserves project list and project detail routes, now with auth guards and lazy loading.

**State:** SOURCE_PARITY_STRONG / RUNTIME_UNKNOWN.

---

### HJ-PRE-002 — browse project items

**Historical path**

The project detail Quick Actions linked directly to:

```text
/items?project=:projectId
```

Historical `ItemsTableView` consumed the project query filter and rendered the project's item table.

**Current topology**

- `/items` still renders `ItemsTableView`, but derives a project ID from the first project returned by `useProjects()`.
- project-specific browsing is also distributed across `/projects/:projectId/views/:viewType`.
- current `ProjectDetailView` uses project-scoped view cards rather than the old direct “View Items” Quick Action.

This is not enough evidence to call the journey regressed, because the project-scoped view model may intentionally supersede the old generic item table. It is also not enough to call it preserved.

**State:** TOPOLOGY_CHANGED / PARITY_INCONCLUSIVE / RUNTIME_UNKNOWN.

**Required runtime question:** From a selected project, can a user reach a complete item inventory for that same project without silently falling onto another project's data?

---

### HJ-PRE-003 — open the unified graph for a selected project

**Historical path**

```text
ProjectDetailView
  → /graph?project=:projectId
  → graph.index.tsx
  → GraphView
  → useItems(projectId)
  + useLinks(projectId)
  → UnifiedGraphView
```

The historical route explicitly described an “Interactive graph of project relationships and dependencies.”

**Current path**

```text
ProjectDetailView
  → /projects/:projectId/views/graph
  → dynamic project view router
  → pages/projects/views/GraphView
  → UnifiedGraphView
```

The old `/graph` URL is retained as a compatibility redirect to project selection.

During this recovery pass that compatibility route was found with an empty redirect effect even though its comments, copy, and Playwright test required a redirect. It was repaired in commit `71cff4f2`.

**State:** SOURCE_PARITY_STRONG / URL_TOPOLOGY_CHANGED / RUNTIME_UNKNOWN.

---

### HJ-PRE-004 — switch graph representation without changing the product being inspected

At `0e8b0bdd`, `GraphViewContainer` exposes exactly three primary modes:

1. **Traceability Graph** — full node graph with all connections.
2. **Page Flow** — UI page interactions and navigation.
3. **Component Library** — UI component tree and hierarchy.

The same historical graph also exposes six perspective projections:

- Product
- Business
- Technical
- UI/UX
- Security
- Performance

`UnifiedGraphView` routes:
- `page-flow` → `PageInteractionFlow`;
- `components` → `ComponentLibraryView`;
- traceability + six perspectives → `FlowGraphViewInner`, with perspective filtering.

The current graph configuration still contains:

```text
traceability
page-flow
components
perspective-product
perspective-business
perspective-technical
perspective-ui
perspective-security
perspective-performance
```

and has added other graph projections.

This establishes strong source survival of the committed pre-pivot graph contract. It does not establish:
- complete link loading;
- stable mode switching;
- correct filtering;
- preserved selection/navigation;
- acceptable performance;
- usable 10K-node behavior.

**State:** SOURCE_PARITY_STRONG / RUNTIME_UNKNOWN.

**Critical recovery oracle:** changing graph mode or perspective must not silently change, truncate, or corrupt the underlying product truth being inspected.

---

### HJ-PRE-005 — inspect traceability as a matrix

**Historical path**

```text
ProjectDetailView
  → /matrix?project=:projectId
  → TraceabilityMatrixView
```

Both `/matrix/` and `/matrix/traceability/` rendered `TraceabilityMatrixView`.

**Current path**

The project-scoped dynamic view router maps `matrix` to `TraceabilityMatrixView`, and `ProjectDetailView` exposes a Matrix view card.

**State:** SOURCE_PARITY_STRONG / URL_TOPOLOGY_CHANGED / RUNTIME_UNKNOWN.

---

### HJ-PRE-006 — open an item detail from product navigation

**Historical path**

```text
/items/:itemId
  → ItemDetailView
```

**Current path**

The legacy item route resolves the item's project/view identity and redirects into:

```text
/projects/:projectId/views/:viewType/:itemId
```

The project view parent yields to its child outlet for detail routes.

The existing backward-compatibility E2E suite directly tests this redirect behavior.

**State:** SOURCE_PARITY_STRONG / URL_TOPOLOGY_CHANGED / RUNTIME_UNKNOWN.

---

### HJ-PRE-007 — inspect and manage typed relationships

**Historical path**

```text
/links/
  → LinksView
```

The route described:

> Manage 60+ link types and relationships between project items

This is central to the original “graphify a product” thesis because links are not decoration; they encode product relationships.

**Current source**

- `frontend/apps/web/src/views/LinksView.tsx` still exists and has live link/item hooks plus delete behavior.
- item detail contains a Relationships/Links tab.
- current repository code search finds no production import of `LinksView`.
- the current route directory has no top-level links route.

Therefore the specialized global relationship-management surface survives in source but has no current production entrypoint identified.

This may be intentional consolidation into item-level relationship management, or it may be a stranded historical surface.

**State:** ENTRYPOINT_NOT_FOUND / TOPOLOGY_CHANGED / RUNTIME_UNKNOWN.

**Required product decision:** determine whether global relationship management remains part of the mature product contract. Do not delete the source merely because the old route disappeared.

---

### HJ-PRE-008 — inspect typed project projections

The pre-pivot project router already exposes typed views including:

```text
feature
code
test
api
database
wireframe
architecture
infrastructure
dataflow
security
performance
monitoring
domain
journey
configuration
dependency
```

The historical `journey` route at this point is a generic `ItemsTableView`, not the later specialized `JourneyExplorer`.

Most of these view identities remain in the current project-view router, with additional current views.

**State:** SOURCE_PARITY_SUBSTANTIAL / INDIVIDUAL_VIEW_RUNTIME_UNKNOWN.

## D529 breadth — do not backdate into the known-good baseline

The following recognizable product surfaces first enter committed Git in `d5296270`:

- `PageDecompositionView`;
- `JourneyExplorer`;
- `ProblemView`;
- `ProcessView`;
- the five multi-dimensional Playwright specs and their `TEST_SUMMARY.txt`;
- major graph-model/schema and adjacent product expansions documented in the d529 recovery packages.

These are not evidence of what `0e8b0bdd` already contained.

They are still high-value historical intent.

### D529-J-001 — page decomposition

Current source:
- large `PageDecompositionView.tsx`;
- dedicated test;
- no production import found.

**State:** D529_ONLY / SOURCE_PRESENT / ENTRYPOINT_NOT_FOUND / RUNTIME_UNKNOWN.

### D529-J-002 — specialized journey explorer

Current source:
- large `JourneyExplorer.tsx`;
- unit/integration tests;
- no production import found;
- current journey route uses generic `ItemsTableView view="journey"`.

**State:** D529_ONLY / SOURCE_PRESENT / SPECIALIZED_ENTRYPOINT_NOT_FOUND / RUNTIME_UNKNOWN.

### D529-J-003 — problem model

Current source includes persistence, server handlers/stores, form, hooks, view, route and contract E2E definitions.

**State:** D529_ONLY / SOURCE_PRESENT / ROUTE_PRESENT / RUNTIME_UNKNOWN.

### D529-J-004 — process model

Current source includes form/hooks/view and a project route.

**State:** D529_ONLY / SOURCE_PRESENT / ROUTE_PRESENT / RUNTIME_UNKNOWN.

### D529-J-005 — multi-dimensional graph intent suite

The d529 suite describes:
- five display modes;
- dimension filters;
- equivalence management;
- journey overlays;
- component-library interactions.

Its own summary explicitly allows graceful degradation for missing/unimplemented optional features and says “Implement Features” as a next step.

**State:** D529_ONLY / INTENT_EVIDENCE / ORACLE_STRENGTH_WEAK.

It must not be used to prove the pre-pivot product worked.

## Current recovery execution order

### Gate J-1 — preserve the old spine

First close runtime evidence for:
1. project open;
2. project-scoped item browsing;
3. project-scoped graph open;
4. graph primary-mode switching;
5. graph six-perspective switching;
6. matrix open;
7. item detail;
8. relationship inspection.

### Gate J-2 — prove data integrity across projections

For the same candidate/project:
- item identity must remain stable;
- link identity/count must be explainable;
- a projection may hide data by declared semantics but may not silently fail to load it;
- mode changes must not create false absence;
- bounded/progressive loading must expose incompleteness rather than masquerading as full product truth.

### Gate J-3 — disposition d529 breadth

Each d529-only journey/surface receives one explicit disposition:

```text
PRESERVE
RECOVER
ADAPT
SUPERSEDE
RETIRE
GENERATED-NOISE
```

No d529 feature becomes “recovered” from file presence alone.

### Gate J-4 — build a strict browser oracle

The recovery browser suite must fail when a required behavior is missing.

Forbidden false-green patterns for required behavior include:
- swallowing failed selectors/actions with `.catch()`;
- logging and continuing when required UI is absent;
- treating unimplemented required features as optional;
- asserting only that a page shell loaded.

## Working conclusion

The source record supports a narrower and more defensible historical statement than “everything in the Jan/Feb frontend was the known-good MVP.”

The committed pre-pivot product spine was already substantial:

```text
project
  → items
  → item detail
  → typed relationships
  → unified graph
      → traceability
      → page flow
      → component library
      → six perspectives
  → traceability matrix
  → typed project views
```

The post-pivot tree then added a large amount of breadth in one poorly isolated transaction.

Recovery should therefore:

> restore and independently verify the pre-pivot spine first, while recovering d529 breadth as separately classified mature-product intent.
