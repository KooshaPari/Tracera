# Jan 29 – Feb 6, 2026 Working-MVP Regression Forensic

**Status:** ACTIVE RECOVERY INVESTIGATION  
**Owner recollection:** Jan 30–31 is a high-confidence last-known-working window; Feb 6 is an outer bound. The product was a usable MVP before a request to make large HTML graph rendering (~10K nodes) reasonable. Subsequent graph-performance work and DG/problem/user-model expansion coincided with loss of a reliably buildable/testable product.

This document treats that recollection as a forensic hypothesis, not yet a proven single-cause narrative.

## Why this window matters

The current recovery program must not merely make today's branch compile. It must determine whether a more coherent/useful product existed in history and whether later recovery work restored all of it.

A green current build that is functionally below the Jan/Feb product is a regression, not recovery.

## Evidence already recovered

### Previously misclassified E2E evidence — corrected

`frontend/apps/web/e2e/TEST_SUMMARY.txt` says it was “Created: January 29, 2026” and describes 5 files / 81 Playwright tests.

Git ancestry shows those files were **not present in the `0e8b0bdd` pre-performance tree**. Path history places their first committed appearance in **`d5296270`**, the mega-transaction.

The suite is therefore evidence of product intent captured during d529, not proof of a committed pre-pivot browser oracle. Its own documentation further says unimplemented optional features can degrade without failing tests.

**Correct classification:** D529 INTENT EVIDENCE / PRE-PIVOT RUNTIME PROOF = UNKNOWN.

### Performance pivot 1 — bounded/drop-in optimization

Commit `370e2c0a3028bb4204afb91bff66b2c313c985f4`:
**FEAT: Add viewport frustum culling for graph performance optimization (Phase 1)**

It describes:
- ReactFlow viewport-aware edge culling;
- AABB filtering;
- feature-flagged hook;
- claimed 40–60% edge reduction;
- claimed 2–3x FPS improvement;
- explicit statement: **"drop-in enhancement - no breaking changes"**;
- "Next: Canvas-based rendering (Phase 2) researched and documented."

This appears architecturally bounded and is not by itself proof of the break.

### Performance pivot 2 — cross-cutting graph/API migration

Commit `27262fa4e780efc8900f6842d101054310eea793`:
**FEAT: Migrate all graph components to use progressive edge loading**

It changes:
- backend API filtering/pagination;
- `useLinks`;
- `GraphViewContainer`;
- `UnifiedGraphView`;
- project GraphView;
- generic GraphView;
- ProjectMappingGraphView.

It changes initial graph semantics from full edge load to 500-edge progressive loading and targets 100K+ edges.

This is no longer a local rendering optimization; it changes data retrieval + every graph projection and is a prime regression-boundary candidate.

### Concrete graph regression evidence

Commit `4a897659d864d98a0194fbf95a286ccc0b27781d`:
**FIX: Map snake_case API response to camelCase for link rendering**

The commit states project graph edges did not render because the API returned `source_id/target_id/link_type` while graph components expected `sourceId/targetId/type`.

This proves at least one later graph path reached a state where basic edge rendering was broken by contract drift.

### Phase-5 architectural expansion

Commit `6df15aca9fc1f34125a9a166319eeb248aed3163` records Feb 5/6 Phase-5 execution and:
- Sigma/WebGL graph work;
- LOD rendering;
- visual regression;
- performance metrics;
- planned GPU/WebGPU shaders;
- planned spatial indexing;
- parallel-agent execution across multiple unrelated gaps.

Current repository remnants additionally include:
- `SigmaGraphView`;
- enhanced Sigma renderers;
- ReactFlow/Sigma hybrid switching;
- virtualization;
- viewport culling;
- R-tree indexing;
- Web Worker layout;
- GPU force layout;
- 10K-node benchmarks;
- 100K+ edge/node performance targets.

The optimization request therefore expanded into a multi-renderer/game-engine-like graph subsystem rather than remaining a narrow ReactFlow optimization.

### Phase-5 test-system break

Commit `daaa4eb9b63057b05635c69694630b5fb2a9c1e9`:
**fix: disable MSW temporarily due to graphql ESM/CommonJS import failure**

It explicitly records:
- **210/210 tests failing**;
- MSW 2.12.7 / GraphQL / Vitest+jsdom incompatibility;
- MSW lifecycle disabled;
- HTTP-mocking-dependent gaps blocked;
- adjusted Phase-5 target only 34/80 tests executable.

This is a concrete loss of testability during the suspected window.

### Later recovery/stabilization evidence

Commit `57915f011c43fae51970c49497ce2bf2cd000e19`:
**Fix Phase 2 baseline test failures: Restore from 97.4% to 100% (1303/1303 passing)**

This proves later stabilization occurred, but test-count recovery is not sufficient evidence that the Jan 29–31 usable product shape was restored.

Later history also contains explicit frontend restoration commits, including:
- `d7126f11d3571ae477468094a533691ba40f668c` — **restore rich Tracera frontend (1,398 files, full historical UI)**.

That strongly supports the broader historical fact that frontend/product content was lost or absent and later recovered from history.

## Working hypothesis

The likely failure was not "performance optimization is inherently bad."

A more precise hypothesis is:

1. Jan 29–31 had a coherent ReactFlow/browser product according to owner recollection and source history; committed pre-pivot E2E coverage has **not** been established.
2. Initial viewport culling was a bounded optimization.
3. Optimization scope expanded from rendering into graph data semantics and every graph projection.
4. The rendering architecture expanded again into hybrid ReactFlow/Sigma/WebGL/LOD/workers/GPU/spatial indexing.
5. Simultaneous unrelated model/backend/auth/test work increased integration surface and agent concurrency.
6. Frontend test infrastructure broke during that campaign and was partially disabled.
7. Contract drift produced user-visible graph regressions such as missing edges.
8. Later agents optimized/stabilized pieces and eventually restored large historical frontend sets, but "tests green" and "files restored" do not prove restoration of the original usable product journey.

## Forensic questions to close

### A. Identify exact last-known-good commit

Search Jan 29–31 ancestry for the strongest commit that can demonstrate:
- frontend production build;
- graph page renders;
- nodes + edges visible;
- project navigation works;
- traceability interactions work;
- a strict historical oracle can be recovered independently of the d529 81-test intent suite;
- backend/frontend contract aligns.

Do not choose by date alone.

### B. Identify first product-breaking commit

Bisect conceptually across:
- viewport culling;
- progressive loading;
- hybrid renderer;
- Sigma/WebGL;
- LOD;
- workers;
- API contract changes;
- DG/problem/user model changes.

"First CI red" and "first user-visible regression" may be different commits.

### C. Reconstruct the Jan-31 product contract

Inventory from that commit:
- routes/pages;
- graph interactions;
- CRUD;
- filters;
- matrix/trace views;
- auth/user behavior;
- DG/problem model;
- project model;
- APIs;
- build/start commands;
- E2E journeys.

### D. Compare three states

```text
LAST-KNOWN-GOOD (Jan 29–31)
        vs
FIRST-BROKEN / Feb-6 boundary
        vs
CURRENT recovery branch
```

For every user-visible capability classify:
- PRESERVED;
- IMPROVED;
- REGRESSED;
- LOST;
- REPLACED;
- UNKNOWN.

### E. Performance architecture adjudication

Do not assume current hybrid stack is desirable merely because it exists.

For each optimization:
- Was the original bottleneck measured?
- Does it improve the target workload?
- Does it preserve semantics?
- What complexity/reliability cost did it add?
- Can modern ReactFlow/Sigma/other current libraries now solve it more simply?
- Is 10K simultaneous visible nodes actually a required UX, or should hierarchy/LOD/progressive disclosure reduce visible cardinality?

### F. Recovery gate

Current Tracera is not "historically recovered" until:
1. the last-known-good product can be reconstructed;
2. its user journeys are represented in the mature contract;
3. current branch is proven no worse on those journeys unless explicitly superseded;
4. lost useful code/features are either restored or consciously retired with rationale.

## Immediate evidence tasks

1. enumerate commits in Jan 29–Feb 6 ancestry, not keyword search only;
2. preserve the finding that d529 first committed the 81-test suite, and reconstruct pre-pivot journeys from source/UI history plus stronger evidence;
3. map graph-performance commits in topological order;
4. map DG/problem/user-model commits in same interval;
5. inspect build/package/lockfile changes in the interval;
6. inspect first commits reporting broken builds/tests;
7. inspect later recovery commits for which historical trees they restored;
8. compare historical GraphView/API/types to current equivalents;
9. add recovered Jan-31 journeys to the mature requirement/source register;
10. make this forensic window a blocking recovery gate, not optional archaeology.
