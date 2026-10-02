# Jan 30 – Feb 6 Regression Forensics — Preliminary Dossier

**Owner recollection:** product was a usable MVP before the large-graph optimization push; Jan 30/31 was remembered as working, Feb 6 as an outer bound after which the product was no longer reliably buildable/usable. The 10K-node HTML graph optimization request is the suspected inflection point, followed by DG/problem/user-model expansion and later agent thrash.

## Evidence-backed chronology

### Candidate pre-optimization anchor
`0e8b0bdd` — 2026-01-29 21:33 PST
**FEAT: Complete cross-perspective search implementation with advanced features**

This is currently the strongest *candidate* last-known-good anchor immediately before the large-graph migration. It is not yet certified buildable/usable.

### Performance migration begins
`27262fa4` — 2026-01-29 23:24 PST
**FEAT: Migrate all graph components to use progressive edge loading**

Commit claims:
- all graph visualization components migrated;
- initial edge load reduced to 500;
- backend filtering/pagination changes;
- 116k-edge target;
- 98% initial-render/memory improvement.

This is not a small optimization. It crosses backend API, hooks, graph container, and every graph-view consumer.

### Immediate regression evidence
`4a897659` — 2026-01-29 23:33 PST
**FIX: Map snake_case API response to camelCase for link rendering**

The commit explicitly states the preceding migration caused a project graph view to render no edges because API response shape and graph component expectations diverged.

This is the first direct regression witness currently identified.

### Additional rendering architecture added
`370e2c0a` — 2026-01-29 23:42 PST
**FEAT: Add viewport frustum culling for graph performance optimization (Phase 1)**

Adds viewport/AABB culling and a ReactFlow-aware hook. Commit calls it drop-in/non-breaking, but this claim requires independent validation.

### Adjacent virtualization expansion
`d5296270` — 2026-01-29 23:49 PST
**FEAT: Implement virtual scrolling in ItemsTableView**

Optimization effort expands beyond graph rendering into general frontend virtualization.

### Build repair appears shortly after
`b7367a4e` — 2026-02-01 16:54 PST
**fix: TypeScript compilation and production build issues**

This is an important candidate witness that the post-optimization tree was not continuously build-clean. Exact failures and causality still need inspection.

### Large-scale lint/type refactor wave
2026-02-02 contains dozens of lint/type-safety/refactor/fix commits, including:
- strict oxlint activation;
- complexity enforcement;
- frontend formatter/linter replacement;
- broad type-safety changes;
- module-integration type-error repair.

This creates a second regression-risk wave layered on top of the graph-performance changes.

### WebGL/Sigma/LOD phase
`6df15aca` — 2026-02-05 19:19 PST
**feat: complete Gap 5.1-5.2 (WebGL + OAuth events) implementation**

By this point the graph-performance work had advanced to Sigma/WebGL/LOD visual-regression coverage. This is materially beyond the original HTML/ReactFlow optimization and must be treated as a separate rendering-generation candidate.

## Scale of the initial optimization change

Comparing candidate anchor `0e8b0bdd` → viewport-culling point `370e2c0a` spans 8 commits.

Selected graph/frontend churn:
- GraphViewContainer: +507 / -467
- UnifiedGraphView: +1153 / -145
- API client: +100 / -33
- useLinks: +60 / -6
- project GraphView: +121 / -16
- generic GraphView: +146 / -19
- new viewport culling hook: +150
- new viewport culling library: +182
- new ProjectMappingGraphView: +71

This was effectively a graph rendering/data-loading architecture migration, not a narrow optimization.

## Current forensic hypothesis

The likely failure was not one single bad commit. The evidence currently supports a cascade:

1. usable product / cross-perspective feature state;
2. broad progressive-loading migration;
3. immediate graph rendering regression;
4. viewport-culling/virtualization additions before full usability was re-proven;
5. infrastructure/build changes;
6. broad lint/type refactors;
7. further WebGL/Sigma/LOD rendering generation;
8. later product-model expansion and agent changes;
9. loss of a continuously tested canonical build;
10. later recovery operating from a mixed/regressed tree.

This hypothesis is provisional.

## Required next forensic work

### A. Certify last-known-good
Test candidate snapshots, not recollection alone:
- `0e8b0bdd`;
- parent/predecessors immediately before it;
- selected Jan 30/31 snapshots.

For each capture:
- install/build;
- frontend boot;
- backend boot;
- project open;
- graph render;
- create/edit/link flows;
- cross-perspective search;
- representative persisted data.

### B. Bisect first build failure
Find first commit where canonical install/build fails.

### C. Bisect first product-journey regression
Build-green does not imply usable. Independently bisect:
- graph visible;
- edges visible;
- interactions;
- navigation;
- editing;
- persistence;
- reload.

### D. Rendering-generation map
Separate:
1. pre-performance ReactFlow;
2. progressive loading;
3. viewport culling;
4. Sigma/WebGL/LOD;
5. current/recovered rendering.

For each, inventory capabilities gained/lost.

### E. Product-model history
Locate DG/problem/user-model changes after the rendering transition and determine whether they:
- changed storage/API contracts;
- invalidated frontend assumptions;
- introduced migrations;
- replaced working flows;
- were later partially reverted/recovered.

### F. Current comparison
Compare the certified best historical snapshot against:
- current main;
- current recovery branch.

Classify every historically useful capability:
`PRESERVED | REGRESSED | LOST | REPLACED | SUPERSEDED | UNKNOWN`.

## Recovery rule

Do **not** reset the repository to the old snapshot.

The old snapshot is an oracle/reference asset. Recover superior historical behavior/capabilities into the mature current architecture while preserving later valid work and Git history.
