# Historical Capability Survival Scan

**Date:** 2026-09-30  
**Branch:** `spec/mature-product-contract-v1`  
**Purpose:** convert Jan 30–Feb 6 archaeology into a recovery ledger without confusing source presence with product recovery.

## Status vocabulary

This scan deliberately does **not** use a recovered/not-recovered boolean.

- **SOURCE_PRESENT** — current branch contains an implementation surface with the historical capability's recognizable intent.
- **ROUTE_PRESENT** — a current route/entry surface exists.
- **TEST_PRESENT** — tests exist for the surface.
- **RUNTIME_VERIFIED** — the historical journey has been exercised successfully on the current candidate.
- **CHANGED_INTENTIONALLY** — behavior differs from history and the change has accepted product intent behind it.
- **REGRESSED** — a historical behavior is demonstrably worse or broken.
- **MISSING** — no current implementation corresponding to the historical behavior was found.
- **UNKNOWN** — available evidence cannot establish the state.

File presence is evidence of implementation footprint only. It is **not** evidence that a journey works.

## Historical anchors carried forward

| Anchor | SHA | Current interpretation |
|---|---|---|
| Pre-performance candidate | `0e8b0bdd` | Strong last-pre-migration reference; reproducible build still UNKNOWN. |
| Progressive-loading migration | `27262fa4` | High-confidence initial destabilization trigger. |
| Documented broken-edge repair | `4a897659` | First explicit visible regression evidence, but not a direct child of `27262fa4`. |
| Scope-collapse mega-transaction | `d5296270` | Primary forensic pivot; ~1.86M changed lines spanning multiple product domains plus generated state. |
| First explicit production-build repair | `b7367a4e` | Proves build breakage existed by Feb 1. |
| Mass lint rewrite | `33545b1b` | High-blast-radius regression amplifier. |
| Massive TS remediation | `7016ae18` | High-blast-radius regression amplifier. |
| Explicit test-infrastructure collapse | `daaa4eb9` | Strong stability-loss evidence: 210/210 MSW-dependent tests failing and 40+ TS errors reported. |

### Important correction to the immediate-regression narrative

`4a897659` occurred roughly nine minutes after `27262fa4`, but it is **six commits ahead**, not its direct child.

The ancestry between them is:

```text
27262fa4  progressive edge loading
  ↓
fdd50f92  backend coverage analysis doc
  ↓
24c56e7c  test coverage summary doc
  ↓
308e4a88  API client typing + Layout refactor
  ↓
eb3d4255  coverage-analysis index
  ↓
13339737  START_HERE navigation doc
  ↓
4a897659  repair missing snake_case → camelCase edge mapping
```

Therefore the evidence supports:

> a visible graph regression existed within minutes of the performance migration while additional API/layout and documentation churn was also occurring.

It does **not** yet prove that `27262fa4` alone was the sole first-bad transaction.

## Current source-survival matrix

| Historical capability / intent | Current evidence | Source state | Route state | Test state | Runtime state |
|---|---|---:|---:|---:|---:|
| Traceability graph | `GraphViewConfig.ts`, `UnifiedGraphView.tsx` | SOURCE_PRESENT | UNKNOWN | TEST_PRESENT in broader graph suites | UNKNOWN |
| Page-flow graph | `GraphViewConfig.ts`, graph components | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Component-library graph | `GraphViewConfig.ts`, graph components | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Product perspective | `GraphViewConfig.ts` | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Business perspective | `GraphViewConfig.ts` | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Technical perspective | `GraphViewConfig.ts` | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| UI perspective | `GraphViewConfig.ts` | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Security perspective | `GraphViewConfig.ts` | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Performance perspective | `GraphViewConfig.ts` | SOURCE_PRESENT | UNKNOWN | UNKNOWN | UNKNOWN |
| Page decomposition | `PageDecompositionView.tsx` (~873 lines) | SOURCE_PRESENT | UNKNOWN | `PageDecompositionView.test.tsx` | UNKNOWN |
| Journey exploration / derived journeys | `JourneyExplorer.tsx` (~871 lines), journeys API | SOURCE_PRESENT | ROUTE_PRESENT | unit + integration + E2E journey-overlay tests | UNKNOWN |
| Problem model | problem migrations, server handlers/stores, form, hook, `ProblemView.tsx` | SOURCE_PRESENT | ROUTE_PRESENT | contract E2E YAMLs present | UNKNOWN |
| Process model | process form/hooks, `ProcessView.tsx` | SOURCE_PRESENT | ROUTE_PRESENT | UNKNOWN | UNKNOWN |
| Items table virtualization | wrapper + `items-table/ItemsTableViewImpl.tsx` | SOURCE_PRESENT | UNKNOWN | virtual + comprehensive + a11y tests | UNKNOWN |
| Auth/account surface | Rust auth, Python authz, frontend auth stores/routes/providers | SOURCE_PRESENT | ROUTE_PRESENT | multiple auth E2E and unit suites | UNKNOWN |
| Specification UI | ADR, BDD, contracts, analytics, dashboard, item-spec components | SOURCE_PRESENT | UNKNOWN | coverage incomplete/UNKNOWN | UNKNOWN |

## Current graph-mode footprint

The current `GraphViewConfig.ts` still exposes the old core modes/perspectives and has expanded beyond them.

Current IDs:

```text
traceability
flow-chart
dependency-graph
hierarchy
impact-map
journey-map
mind-map
gallery
page-flow
components
perspective-product
perspective-business
perspective-technical
perspective-ui
perspective-security
perspective-performance
```

This is evidence that old graph intent was not simply deleted. It does **not** establish that the modes are wired to correct data, render complete graphs, preserve interactions, or satisfy the Jan-30 journeys.

## Product/model surfaces that survived the d529 scope-collapse pivot

The following d529-era initiatives have recognizable current source descendants:

### R-GRAPH-RENDER
Evidence:
- `UnifiedGraphView.tsx` remains a large central renderer (~1,111 lines).
- current graph configuration exposes multiple render/view modes.
- page decomposition and journey graph surfaces remain.

Classification: **SOURCE_PRESENT / RUNTIME UNKNOWN**

### R-GRAPH-MODEL
Evidence:
- current graph-mode configuration includes dependency, hierarchy, impact, journey and perspective projections.
- current recovery work separately adds historical product-baseline/entity persistence.

Classification: **SOURCE_PRESENT / SEMANTIC PARITY UNKNOWN**

### R-PROBLEM-PROCESS
Evidence:
- problem persistence exists in SQLite/Postgres server stores;
- problem route, form, hooks and view exist;
- process route, form, hooks and view exist.

Classification: **SOURCE_PRESENT / ROUTE_PRESENT / RUNTIME UNKNOWN**

### R-USER-ACCOUNT
Evidence:
- backend auth modules;
- frontend auth routes/stores/providers;
- multiple auth E2E suites.

Classification: **SOURCE_PRESENT / ROUTE_PRESENT / TEST_PRESENT / RUNTIME UNKNOWN**

### R-SPEC
Evidence:
- extensive current specification component hierarchy including ADR, BDD, contracts, analytics and item-specific specification views.

Classification: **SOURCE_PRESENT / JOURNEY UNKNOWN**

### R-JOURNEY
Evidence:
- journey API modules;
- `JourneyExplorer.tsx`;
- project journey route;
- unit, integration and E2E journey tests.

Classification: **SOURCE_PRESENT / ROUTE_PRESENT / TEST_PRESENT / RUNTIME UNKNOWN**

### R-EXECUTION
Not yet assessed deeply in this scan.

Classification: **UNKNOWN**

### R-INTEGRATIONS
Not yet assessed deeply in this scan.

Classification: **UNKNOWN**

### R-GENERATED-NOISE
Historical d529 contamination included generated state, Hypothesis constants, local/test databases, snapshots, session artifacts, backups and large generated documentation volumes.

Classification: **HISTORICAL GENERATED-NOISE; current hygiene not yet graded**

## Recovery gates created by this scan

### HG-01 — historical source survival
For each Jan-30 user-visible capability, identify a current implementation surface or mark it MISSING.

**State:** partially closed. Major graph, problem/process, journey, auth and specification surfaces are source-present.

### HG-02 — current route reachability
For each source-present capability, prove there is an actual route/entry path where one is required.

**State:** open.

### HG-03 — behavior parity
Exercise each historical journey against the current candidate and classify:

```text
PRESERVED
IMPROVED
CHANGED_INTENTIONALLY
REGRESSED
MISSING
UNKNOWN
```

**State:** open. Source inspection cannot close this gate.

### HG-04 — historical anchor reproducibility
Build/run selected historical anchors in isolated worktrees without modifying their commits.

**State:** open.

### HG-05 — d529 recovery-package disposition
For each d529 recovery package, assign and evidence one of:

```text
PRESERVE
RECOVER
ADAPT
SUPERSEDE
RETIRE
GENERATED-NOISE
```

**State:** open.

### HG-06 — no source-footprint false green
A current capability may not be reported as recovered merely because its files, tests or routes exist.

**State:** policy established; enforcement still open.

## Immediate next work

1. Prove route reachability for graph/page-decomposition/problem/process/journey/specification surfaces.
2. Create a historical-journey manifest from the Jan-29 E2E suite and pre-pivot UI.
3. Bind each journey to current route/component/API/test evidence.
4. Reproduce selected historical builds where tool/environment archaeology permits.
5. Independently execute the current journeys; only then promote UNKNOWN to a stronger status.
6. Trace R-EXECUTION and R-INTEGRATIONS from d529 into current code.
7. Continue mass-rewrite semantic-damage sampling for `33545b1b` and `7016ae18`.

## Bottom line

The current tree contains a surprising amount of recognizable Jan/Feb product intent. That materially weakens any theory that recovery should simply revert to the old tree.

The unresolved question is harder and more important:

> Are these surviving implementation surfaces coherently wired into a usable product, or are they a large source footprint around broken or unreachable journeys?

Until runtime/journey evidence answers that question, the correct state is **SOURCE_PRESENT, RECOVERY UNKNOWN**.


## Route reachability update

Source-level route tracing closes part of **HG-02** without implying runtime success.

### Confirmed production entry paths

- **Graph:** `projects.$projectId.views.$viewType.tsx` maps `graph` to a lazy import of `@/pages/projects/views/GraphView`; that view imports and renders `UnifiedGraphView`.  
  **Classification:** SOURCE_PRESENT / ROUTE_PRESENT / RUNTIME UNKNOWN.
- **Problem:** `projects.$projectId.views.problem.tsx` renders `ProblemView`, and the dynamic project-view router maps `problem` to that route component.  
  **Classification:** SOURCE_PRESENT / ROUTE_PRESENT / RUNTIME UNKNOWN.
- **Process:** `projects.$projectId.views.process.tsx` renders `ProcessView`, and the dynamic project-view router maps `process` to that route component.  
  **Classification:** SOURCE_PRESENT / ROUTE_PRESENT / RUNTIME UNKNOWN.
- **Journey:** `projects.$projectId.views.journey.tsx` is a live route, but it renders `ItemsTableView projectId={projectId} view="journey"`.  
  **Classification:** JOURNEY ROUTE_PRESENT / CURRENT TOPOLOGY DIFFERS / RUNTIME UNKNOWN.

### Specialized historical UI with no production entry found

#### PageDecompositionView

Repository code search currently finds:
- `PageDecompositionView.tsx`;
- `PageDecompositionView.test.tsx`;

but no production import or route reference.

**Classification:** SOURCE_PRESENT / TEST_PRESENT / ENTRYPOINT_NOT_FOUND / RUNTIME UNKNOWN.

This is not proof that the capability is impossible to reach through some indirect mechanism. It is, however, evidence that the specialized component is not wired through an ordinary production import path visible to repository code search.

#### JourneyExplorer

Repository code search currently finds:
- `JourneyExplorer.tsx`;
- unit tests;
- integration tests;

but no production route/component import. The current journey route instead uses the generic `ItemsTableView` journey projection.

**Classification:** SOURCE_PRESENT / TEST_PRESENT / SPECIALIZED_ENTRYPOINT_NOT_FOUND / JOURNEY_ROUTE_PRESENT_VIA_DIFFERENT_UI / RUNTIME UNKNOWN.

This creates a concrete recovery question rather than a presumed regression:

> Was `JourneyExplorer` intentionally superseded by the generic journey projection, or did a richer historical journey UI become stranded during later refactors?

That question must be answered from historical intent and runtime comparison before assigning PRESERVED, CHANGED_INTENTIONALLY, or REGRESSED.

### HG-02 status

**HG-02 is now PARTIALLY CLOSED.**

Confirmed source-level production entry paths exist for graph, problem, process, and a journey projection. Page decomposition and the specialized JourneyExplorer do not currently have a production entrypoint identified.

No state in this section is equivalent to RUNTIME_VERIFIED.
