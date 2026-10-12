# [Instinct] Tracera gap inventory

Read-only source audit, 2026-10-12. Audited requested Windows checkout `C:\Users\koosh\tracera`, commit `497a0c364`, via direct SSH to the authorized desk host. The supplied `~/ts/ssh.sh` was absent. Existing `.probe_build/` and `sandbox/` untracked work preserved. Docs authored on isolated worktree/branch. No application source, data, configuration, secrets, screenshots, recordings, merges or rewritten history. Placement: small local analysis of a git archive; remote docs-only publication.

## Evidence boundary and coverage

The requested checkout is 26 commits behind `origin/main` (`9a4360e81` at audit). These findings are pinned to the requested checkout; A read-only HEAD..origin/main changed-file comparison found only CI/config, locks, package manifests, tracera-edge and tracera-mcp changes; audited frontend route/component/hook, API gateway, Rust server router/handlers and baseline files are unchanged on main. Deployment identity still must be reconciled before treating source findings as live defects. The production API returned Cloudflare Access HTTP 302; Windows localhost:18000 had no listener. No existing browser debugging session was accessible on 9222/9223. No application was started and no auth state was altered. All view rows are `NOT_CLICKED`; this does **not** complete the requested live click-through acceptance. CIVIS and the live summary stub response remain explicitly operator-reported. Empty source envelopes are flagged only when unconditional/fabricated; legitimate project emptiness is not inferred from an unauthenticated request.

API coverage enumerates static production frontend endpoint references, including definitions that may be unused; it is not a network trace of invoked routes. Route presence is path-level only: HTTP methods, response schemas, authorization and persistence remain unverified unless a finding cites a specific source implementation. Absence is specifically in the audited Rust router, not proof of absence from an alternate deployed gateway. `SOURCE_ROUTE_PRESENT` means mounted, not accepted.

Absent Rust registrations are coverage status UNRESOLVED_OWNER and omitted from confirmed gap entries: the alternate serving gateway may own them. Explicit stub findings are source capabilities under the audited Rust serving profile, not independently observed production failures.

Static API references: 284; classifications: {'SOURCE_ROUTE_ABSENT': 234, 'SOURCE_501_STUB': 46, 'SOURCE_ROUTE_PRESENT': 4}. View matrix: 59 rows (44 sidebar, 15 additional direct project routes); live clicked: 0. Gap inventory: 75 non-overlapping entries. See sibling CSV files for complete denominators and evidence.

## Pluggable expected-state baseline

Baseline v1 is the union of `docs/sessions/20260726-frontend-convergence/02_PARITY_MATRIX.md`, `docs/sessions/20260722-rich-dashboard-recovery/07_FRONTEND_CONVERGENCE_MATRIX.md`, `docs/04-guides/mcp-cli-api-matrix.md`, `docs/FEATURE_INVENTORY.md`, `docs/governance/policy/endpoint_traceability_map.md`, `docs/traceability.md`, and `docs/ops/TRACEABILITY.json`. The last file is empty at this revision. These are expected-state oracles, not current success evidence. A view named X must render artifact X with complete project-scoped data.

A future operator hand-built CSV replaces the expected-state baseline, not observed evidence. Record its file path, SHA-256, timestamp, owner and accepted revision here; key rows by frontend route plus artifact (API rows by method plus normalized path). Preserve prior observations and stable gap IDs. Reconcile additions, removals, renamed views and conflicting expectations explicitly, then rerun read-only authenticated click-through and route contract checks. Export observed behavior, pagination/completeness reconciliation, evidence timestamps and linked gap IDs into the view matrix. Do not silently drop old obligations or turn source-only rows into clicked passes. No replacement CSV was searched for or assumed present.

## Issues

### [Instinct] GAP-001 GET /api/v1/projects/{id}/specifications/summary

- Area: Specifications
- Severity: critical
- Expected: adrs {total,accepted,averageCompliance}; contracts {total,active,verified}; features {total,scenarios,passRate}; healthScore; healthDetails
- Actual: Operator-reported live response {items:[],data:[],results:[],total:0,count:0,stub:true}; existing ADR items reported. Independently: frontend expects structured metrics; route absent in audited Rust checkout. Live response NOT revalidated.
- Evidence: Operator Instinct task 2026-10-12; frontend/apps/web/src/hooks/use-specifications/summary-hooks.ts; frontend/apps/web/src/components/specifications/dashboard/SpecificationDashboard.tsx; production read attempt 2026-10-12 returned Access 302
- Suggested fix: Implement project-scoped summary aggregations on serving backend and verify totals against every loaded artifact, including ADRs

### [Instinct] GAP-002 CIVIS project

- Area: Project data
- Severity: high
- Expected: Complete imported CIVIS artifact corpus with explicit import provenance and reconciliation counts
- Actual: Operator reports CIVIS has 0 items loaded; no authenticated live project/item inventory available to independently verify count or expected denominator
- Evidence: Operator Instinct task 2026-10-12; live project API Access 302; runtime UNKNOWN
- Suggested fix: Reconcile authoritative CIVIS source inventory with project import receipts, pagination totals and rendered artifacts; distinguish intentionally empty corpus from failed/missing import

### [Instinct] GAP-003 /projects/{id}/views/dependency (Dependency Graph)

- Area: named-artifact
- Severity: high
- Expected: Render dependency nodes and relationship edges
- Actual: Route only renders generic item table; no artifact-specific renderer is invoked
- Evidence: frontend/apps/web/src/routes/projects.$projectId.views.dependency.tsx:7
- Suggested fix: Bind a project-scoped Dependency Graph renderer to complete artifact data and preserve item detail navigation

### [Instinct] GAP-004 /projects/{id}/views/journey (Journey Map)

- Area: named-artifact
- Severity: high
- Expected: Render ordered journey stages and transitions
- Actual: Route only renders generic item table; no artifact-specific renderer is invoked
- Evidence: frontend/apps/web/src/routes/projects.$projectId.views.journey.tsx:7
- Suggested fix: Bind a project-scoped Journey Map renderer to complete artifact data and preserve item detail navigation

### [Instinct] GAP-005 /projects/{id}/views/dataflow (Data Flow)

- Area: named-artifact
- Severity: high
- Expected: Render sources, sinks and directed data-flow edges
- Actual: Route only renders generic item table; no artifact-specific renderer is invoked
- Evidence: frontend/apps/web/src/routes/projects.$projectId.views.dataflow.tsx:7
- Suggested fix: Bind a project-scoped Data Flow renderer to complete artifact data and preserve item detail navigation

### [Instinct] GAP-006 /projects/{id}/views/database (Database Schema)

- Area: named-artifact
- Severity: high
- Expected: Render tables, columns, keys and relationships
- Actual: Route only renders generic item table; no artifact-specific renderer is invoked
- Evidence: frontend/apps/web/src/routes/projects.$projectId.views.database.tsx:16
- Suggested fix: Bind a project-scoped Database Schema renderer to complete artifact data and preserve item detail navigation

### [Instinct] GAP-007 /projects/{id}/views/wireframe

- Area: named-artifact
- Severity: high
- Expected: Render project wireframe/UI design artifacts
- Actual: Route renders ProjectMappingGraphView; graph selects mapping or first graph and defaults to components, without wireframe filtering
- Evidence: frontend/apps/web/src/routes/projects.$projectId.views.wireframe.tsx:31; frontend/apps/web/src/views/ProjectMappingGraphView.tsx:39; frontend/apps/web/src/views/ProjectMappingGraphView.tsx:62
- Suggested fix: Use project wireframe data and wireframe renderer rather than general mapping projection

### [Instinct] GAP-008 Sidebar Timeline -> /projects/{id}/views/monitoring

- Area: named-artifact
- Severity: high
- Expected: Render project timeline events in temporal order
- Actual: Timeline and Monitoring Dashboard share monitoring route; renderer produces item-status cards/table, not timeline
- Evidence: frontend/apps/web/src/components/layout/sidebar-nav.ts:289; frontend/apps/web/src/components/layout/sidebar-nav.ts:343; frontend/apps/web/src/pages/projects/views/MonitoringView.tsx:40
- Suggested fix: Provide dedicated temporal route and event timeline with complete event data

### [Instinct] GAP-009 Sidebar Reports -> /projects/{id}/views/performance

- Area: named-artifact
- Severity: high
- Expected: Render generated/project reports
- Actual: Reports and Performance Metrics share performance route, which renders ItemsTableView(view=performance)
- Evidence: frontend/apps/web/src/components/layout/sidebar-nav.ts:295; frontend/apps/web/src/components/layout/sidebar-nav.ts:325; frontend/apps/web/src/routes/projects.$projectId.views.performance.tsx:7
- Suggested fix: Bind Reports to a dedicated report artifact list/detail/export renderer

### [Instinct] GAP-010 User Story detail

- Area: item-detail
- Severity: high
- Expected: Render complete stored item and type-specific fields
- Actual: Type branch returns Coming Soon card; item content and generic fallback are bypassed
- Evidence: frontend/apps/web/src/views/details/ItemDetailRouter.tsx:60
- Suggested fix: Implement type-specific detail or render full generic data until available

### [Instinct] GAP-011 Task detail

- Area: item-detail
- Severity: high
- Expected: Render complete stored item and type-specific fields
- Actual: Type branch returns Coming Soon card; item content and generic fallback are bypassed
- Evidence: frontend/apps/web/src/views/details/ItemDetailRouter.tsx:83
- Suggested fix: Implement type-specific detail or render full generic data until available

### [Instinct] GAP-012 Defect detail

- Area: item-detail
- Severity: high
- Expected: Render complete stored item and type-specific fields
- Actual: Type branch returns Coming Soon card; item content and generic fallback are bypassed
- Evidence: frontend/apps/web/src/views/details/ItemDetailRouter.tsx:105
- Suggested fix: Implement type-specific detail or render full generic data until available

### [Instinct] GAP-013 TestSuite New/Create modal

- Area: nonfunctional-control
- Severity: high
- Expected: Create and persist submitted artifact then refresh data
- Actual: Submit invokes handleCreateSuccess which only closes modal; no create mutation
- Evidence: frontend/apps/web/src/pages/projects/views/TestSuiteView.tsx:46; frontend/apps/web/src/pages/projects/views/TestSuiteView.tsx:265
- Suggested fix: Wire controlled form to create hook, show validation/server errors, invalidate artifact queries

### [Instinct] GAP-014 TestRun New/Create modal

- Area: nonfunctional-control
- Severity: high
- Expected: Create and persist submitted artifact then refresh data
- Actual: Submit invokes handleCreateSuccess which only closes modal; no create mutation
- Evidence: frontend/apps/web/src/pages/projects/views/TestRunView.tsx:58; frontend/apps/web/src/pages/projects/views/TestRunView.tsx:284
- Suggested fix: Wire controlled form to create hook, show validation/server errors, invalidate artifact queries

### [Instinct] GAP-015 ItemsTableView Refresh

- Area: nonfunctional-control
- Severity: medium
- Expected: Refetch current project/view data and report outcome
- Actual: Refresh only starts a timer and loading overlay; it never refetches/invalidates data
- Evidence: frontend/apps/web/src/views/items-table/ItemsTableViewImpl.tsx:154
- Suggested fix: Invoke query refetch or invalidate current item query; tie loading and outcome to request

### [Instinct] GAP-016 ItemsTableView project artifact lists

- Area: error-state
- Severity: high
- Expected: Distinguish request failure from genuine empty data
- Actual: Hook error is ignored; destructures only data/isLoading and defaults missing data to empty items
- Evidence: frontend/apps/web/src/views/items-table/ItemsTableViewImpl.tsx:78
- Suggested fix: Render actionable error state and retry separately from empty artifact state

### [Instinct] GAP-017 Wireframe/mapping graph node navigation

- Area: nonfunctional-control
- Severity: medium
- Expected: Open selected graph artifact detail
- Actual: handleNavigateToItem is an empty callback
- Evidence: frontend/apps/web/src/views/ProjectMappingGraphView.tsx:53
- Suggested fix: Navigate selected node to project-scoped item detail

### [Instinct] GAP-018 /projects/{id}/views/api

- Area: api-documentation
- Severity: medium
- Expected: Render project endpoint contracts with current schema/status
- Actual: Page includes hard-coded Tracera platform API groups/status/examples regardless of selected project alongside project items
- Evidence: frontend/apps/web/src/pages/projects/views/ApiView.tsx:33; frontend/apps/web/src/pages/projects/views/ApiView.tsx:171
- Suggested fix: Build endpoint documentation from project API specs and current contract; clearly separate platform reference

### [Instinct] GAP-019 docs/ops/TRACEABILITY.json

- Area: baseline-documentation
- Severity: high
- Expected: Parseable populated traceability graph/manifest
- Actual: File is zero bytes and cannot be parsed as JSON
- Evidence: docs/ops/TRACEABILITY.json:1 (file size 0 bytes)
- Suggested fix: Regenerate manifest from current endpoint/FR/test inventory with provenance and validation

### [Instinct] GAP-020 July parity/convergence matrices

- Area: baseline-documentation
- Severity: medium
- Expected: Current route-by-route expected-state baseline with evidence
- Actual: Parity matrix has all gates pending; convergence matrix is historical 2026-07-26 merge plan referencing former 12-source-file shell; neither is current exhaustive view matrix
- Evidence: docs/sessions/20260726-frontend-convergence/02_PARITY_MATRIX.md:3; docs/sessions/20260722-rich-dashboard-recovery/07_FRONTEND_CONVERGENCE_MATRIX.md:3
- Suggested fix: Preserve historical matrices and attach versioned current baseline adapter supporting replacement Koosha CSV

### [Instinct] GAP-021 MCP/CLI/API matrix and endpoint governance map

- Area: baseline-documentation
- Severity: medium
- Expected: Consistent current Rust endpoint/feature/test oracle
- Actual: MCP matrix declares retired historical Python scope yet reports 17 mounted endpoints and source main.py; governance map is a 24/26 slice whose test links are mostly Not covered
- Evidence: docs/04-guides/mcp-cli-api-matrix.md:3; docs/04-guides/mcp-cli-api-matrix.md:47; docs/governance/policy/endpoint_traceability_map.md:5
- Suggested fix: Use historical expectations as provenance and generate complete current Rust endpoint/test mapping without inferring runtime state

### [Instinct] GAP-022 /projects/{id}/temporal

- Area: mock-data
- Severity: high
- Expected: Load complete project temporal artifacts from authoritative data
- Actual: Fabricates Main branch and Version 1.0 with current timestamps; milestones/sprints empty; no backend calls
- Evidence: frontend/apps/web/src/routes/projects.$projectId.temporal.tsx:51; frontend/apps/web/src/routes/projects.$projectId.temporal.tsx:167
- Suggested fix: Replace mock factories/arrays with project-scoped API queries and explicit error/empty/loading states

### [Instinct] GAP-023 /projects/{id}/equivalence

- Area: mock-data
- Severity: high
- Expected: Load complete project equivalence artifacts from authoritative data
- Actual: All links/concepts/projections/items are constant empty mock arrays; export/import/panel receive mock data; navigation callback empty
- Evidence: frontend/apps/web/src/components/EquivalenceManager.tsx:23; frontend/apps/web/src/components/EquivalenceManager.tsx:75
- Suggested fix: Replace mock factories/arrays with project-scoped API queries and explicit error/empty/loading states

### [Instinct] GAP-024 /api/v1/auth/login

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/data.ts:167; crates/tracera-server/src/router.rs:227
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-025 /api/v1/auth/logout

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/auth-api.ts:123; frontend/apps/web/src/stores/auth-store.ts:373; crates/tracera-server/src/router.rs:228
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-026 /api/v1/auth/refresh

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/auth-api.ts:133; crates/tracera-server/src/router.rs:229
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-027 /api/v1/components/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/component-library-mutations-library.ts:237; frontend/apps/web/src/api/component-library-mutations-library.ts:276; frontend/apps/web/src/api/component-library.queries.ts:92; crates/tracera-server/src/router.rs:308
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-028 /api/v1/components/{id}/usage

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/component-library.queries.ts:116; crates/tracera-server/src/router.rs:309
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-029 /api/v1/equivalences/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/equivalence.ts:84; crates/tracera-server/src/router.rs:236
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-030 /api/v1/graph/ancestors/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:203; crates/tracera-server/src/router.rs:190
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-031 /api/v1/graph/cycles

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:260; crates/tracera-server/src/router.rs:198
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-032 /api/v1/graph/dependencies/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:291; crates/tracera-server/src/router.rs:193
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-033 /api/v1/graph/descendants/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:214; crates/tracera-server/src/router.rs:191
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-034 /api/v1/graph/full

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:245; crates/tracera-server/src/router.rs:197
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-035 /api/v1/graph/impact/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:280; crates/tracera-server/src/router.rs:192
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-036 /api/v1/graph/orphans

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:302; crates/tracera-server/src/router.rs:200
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-037 /api/v1/graph/path

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:225; crates/tracera-server/src/router.rs:195
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-038 /api/v1/graph/paths

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:235; crates/tracera-server/src/router.rs:196
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-039 /api/v1/graph/topo-sort

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:270; crates/tracera-server/src/router.rs:199
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-040 /api/v1/graph/traverse/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:316; crates/tracera-server/src/router.rs:194
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-041 /api/v1/import

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:501; crates/tracera-server/src/router.rs:225
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-042 /api/v1/items

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/api.ts:126; frontend/apps/web/scripts/lib/api.ts:22; frontend/apps/web/scripts/lib/data.ts:171; crates/tracera-server/src/router.rs:175
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-043 /api/v1/items/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/data.ts:173; frontend/apps/web/scripts/lib/data.ts:174; frontend/apps/web/src/api/endpoints.ts:117; crates/tracera-server/src/router.rs:178
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-044 /api/v1/items/{id}/pivot

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/canonical.ts:308; crates/tracera-server/src/router.rs:183
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-045 /api/v1/items/{id}/pivot-targets

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/canonical.ts:290; crates/tracera-server/src/router.rs:179
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-046 /api/v1/journeys/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/journeys-mutations.ts:123; frontend/apps/web/src/api/journeys-mutations.ts:157; frontend/apps/web/src/api/journeys-queries.ts:48; crates/tracera-server/src/router.rs:270
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-047 /api/v1/journeys/{id}/steps

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/journeys-mutations.ts:199; frontend/apps/web/src/api/journeys-queries.ts:70; crates/tracera-server/src/router.rs:271
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-048 /api/v1/journeys/{id}/steps/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/journeys-mutations.ts:237; crates/tracera-server/src/router.rs:272
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-049 /api/v1/libraries/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/component-library-mutations-library.ts:111; frontend/apps/web/src/api/component-library-mutations-library.ts:146; frontend/apps/web/src/api/component-library.queries.ts:43; crates/tracera-server/src/router.rs:304
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-050 /api/v1/libraries/{id}/components

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/component-library-mutations-library.ts:184; frontend/apps/web/src/api/component-library.queries.ts:67; crates/tracera-server/src/router.rs:305
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-051 /api/v1/libraries/{id}/tokens

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/component-library-mutations-tokens.ts:38; frontend/apps/web/src/api/component-library.queries.ts:141; crates/tracera-server/src/router.rs:306
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-052 /api/v1/links

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/api.ts:76; frontend/apps/web/scripts/lib/data.ts:176; frontend/apps/web/src/api/endpoints.ts:156; crates/tracera-server/src/router.rs:185
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-053 /api/v1/links/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/data.ts:177; frontend/apps/web/src/api/endpoints.ts:164; frontend/apps/web/src/api/endpoints.ts:180; crates/tracera-server/src/router.rs:186
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-054 /api/v1/projects

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/api.ts:136; frontend/apps/web/scripts/lib/api.ts:143; frontend/apps/web/scripts/lib/data.ts:169; crates/tracera-server/src/router.rs:158
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-055 /api/v1/projects/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:52; frontend/apps/web/src/api/endpoints.ts:69; frontend/apps/web/src/api/endpoints.ts:78; crates/tracera-server/src/router.rs:163
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-056 /api/v1/projects/{id}/codex/auth-status

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/codex.ts:62; crates/tracera-server/src/router.rs:312
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-057 /api/v1/projects/{id}/equivalences

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/equivalence.ts:63; crates/tracera-server/src/router.rs:240
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-058 /api/v1/projects/{id}/equivalences/detect

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/equivalence.ts:106; crates/tracera-server/src/router.rs:256
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-059 /api/v1/projects/{id}/export

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:455; crates/tracera-server/src/router.rs:219
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-060 /api/v1/projects/{id}/import

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:491; crates/tracera-server/src/router.rs:220
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-061 /api/v1/projects/{id}/journeys

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/journeys-mutations.ts:78; frontend/apps/web/src/api/journeys-queries.ts:23; crates/tracera-server/src/router.rs:278
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-062 /api/v1/projects/{id}/links

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/queries-links.ts:33; frontend/apps/web/src/api/queries-links.ts:50; crates/tracera-server/src/router.rs:188
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-063 /api/v1/search

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/scripts/lib/data.ts:178; frontend/apps/web/src/api/endpoints.ts:333; frontend/apps/web/src/api/endpoints.ts:341; crates/tracera-server/src/router.rs:211
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-064 /api/v1/search/batch-index

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:367; crates/tracera-server/src/router.rs:214
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-065 /api/v1/search/health

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:382; crates/tracera-server/src/router.rs:217
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-066 /api/v1/search/index/{id}

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:359; frontend/apps/web/src/api/endpoints.ts:387; crates/tracera-server/src/router.rs:213
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-067 /api/v1/search/reindex

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:374; crates/tracera-server/src/router.rs:215
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-068 /api/v1/search/stats

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:378; crates/tracera-server/src/router.rs:216
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-069 /api/v1/search/suggest

- Area: API route reference
- Severity: high
- Expected: Rust serving backend implements the frontend-referenced endpoint and declared response contract
- Actual: Explicit 501 not_implemented or project stub handler in Rust router; production runtime UNKNOWN
- Evidence: frontend/apps/web/src/api/endpoints.ts:349; crates/tracera-server/src/router.rs:212
- Suggested fix: Reconcile deployed gateway with Rust API and implement contract; verify the view actually invokes this definition

### [Instinct] GAP-070 GET /api/v1/projects

- Area: Vercel fallback
- Severity: high
- Expected: Return complete persisted data or explicit backend unavailable failure
- Actual: Fallback always fabricates HTTP 200 {total:0,projects:[]} when TRACERA_BACKEND_URL is unset or network fetch fails; activation in production UNKNOWN
- Evidence: api/[...path].ts:127; api/[...path].ts:554-582
- Suggested fix: Fail closed with explicit unavailable status rather than manufacturing empty-success data; retain only genuine persisted empty results

### [Instinct] GAP-071 GET /api/v1/items

- Area: Vercel fallback
- Severity: high
- Expected: Return complete persisted data or explicit backend unavailable failure
- Actual: Fallback always fabricates HTTP 200 {total:0,items:[]} when TRACERA_BACKEND_URL is unset or network fetch fails; activation in production UNKNOWN
- Evidence: api/[...path].ts:160; api/[...path].ts:554-582
- Suggested fix: Fail closed with explicit unavailable status rather than manufacturing empty-success data; retain only genuine persisted empty results

### [Instinct] GAP-072 GET /api/v1/items/summary

- Area: Vercel fallback
- Severity: high
- Expected: Return complete persisted data or explicit backend unavailable failure
- Actual: Fallback always fabricates HTTP 200 {total:0,items:[]} when TRACERA_BACKEND_URL is unset or network fetch fails; activation in production UNKNOWN
- Evidence: api/[...path].ts:174; api/[...path].ts:554-582
- Suggested fix: Fail closed with explicit unavailable status rather than manufacturing empty-success data; retain only genuine persisted empty results

### [Instinct] GAP-073 GET /api/v1/links

- Area: Vercel fallback
- Severity: high
- Expected: Return complete persisted data or explicit backend unavailable failure
- Actual: Fallback always fabricates HTTP 200 [] when TRACERA_BACKEND_URL is unset or network fetch fails; activation in production UNKNOWN
- Evidence: api/[...path].ts:196; api/[...path].ts:554-582
- Suggested fix: Fail closed with explicit unavailable status rather than manufacturing empty-success data; retain only genuine persisted empty results

### [Instinct] GAP-074 GET /api/v1/dashboard/summary

- Area: Vercel fallback
- Severity: high
- Expected: Return complete persisted data or explicit backend unavailable failure
- Actual: Fallback always fabricates HTTP 200 {total_artifacts:0,coverage_ratio:0,open_gaps:0} when TRACERA_BACKEND_URL is unset or network fetch fails; activation in production UNKNOWN
- Evidence: api/[...path].ts:122; api/[...path].ts:554-582
- Suggested fix: Fail closed with explicit unavailable status rather than manufacturing empty-success data; retain only genuine persisted empty results

### [Instinct] GAP-075 generateReport

- Area: Reports
- Severity: high
- Expected: Generate selected complete report artifact
- Actual: Local stub fabricates report id/timestamp with data:{} and no artifact URL
- Evidence: frontend/apps/web/src/api/reports.ts:59-74
- Suggested fix: Implement report generation and artifact delivery

