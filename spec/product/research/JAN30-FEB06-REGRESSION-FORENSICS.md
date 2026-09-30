# Tracera Jan 30 → Feb 6 2026 Regression Forensics

**Status:** evidence-backed preliminary forensic ledger  
**Purpose:** identify the last-known-good zone, first regressions, blast-radius escalation, and what current recovery has or has not restored.

## Executive finding

The evidence does **not** support a simplistic conclusion that one 10K/100K-node optimization commit permanently destroyed Tracera.

It supports a multi-stage failure:

1. **Pre-optimization usable candidate** — `0e8b0bdd`, Jan 29 21:33 PST / Jan 30 05:33 UTC.
2. **Performance migration destabilization** — `27262fa4`, Jan 29 23:24 PST, rewrote all major graph views for progressive loading.
3. **Immediate functional regression** — `4a897659`, nine minutes later, explicitly fixes a project graph where edges no longer rendered.
4. **Optimization expansion** — viewport culling, table virtualization, then later Sigma/WebGL work.
5. **Build/tooling/model churn** — by Feb 1–2 production TypeScript/build fixes, graph-schema migrations, module-integration type fixes, and mass lint auto-fixing were occurring.
6. **High-blast-radius agent rewrite phase** — `33545b1b` changed 106,921 lines across at least 300 files; `7016ae18` changed 819,047 lines across at least 300 files while claiming to resolve 70 TS errors.
7. **Explicitly broken test/build state** — Feb 5 records say 210/210 MSW-dependent tests failed and a primary blocker remained 40+ TS compilation errors.
8. **WebGL/Sigma expansion continued during instability** — `6df15aca` added 17,294 changed lines across 48 files and accepted skipped WebGL tests under jsdom.

The likely durable failure mechanism is therefore:

```text
performance request
→ broad graph rendering migration
→ immediate graph regression
→ expanding optimization/model/schema scope
→ build/tooling remediation campaigns
→ enormous automated rewrites
→ test infrastructure degradation / skipped or blocked suites
→ loss of continuously testable product baseline
→ later agent thrash and partial recovery
```

The performance request appears to be the **trigger point**, but the evidence currently points more strongly to **unbounded follow-on churn and lack of a preserved runnable baseline** as the reason the product stayed broken.

---

## Candidate anchors

### Anchor A — pre-optimization baseline
**SHA:** `0e8b0bdd9e4d17245e0456fc107a86439361ffdd`  
**Time:** 2026-01-29 21:33 PST / 2026-01-30 05:33 UTC  
**Commit:** "Complete cross-perspective search implementation with advanced features"

Why important:
- immediate parent of the all-graph progressive-loading migration;
- sophisticated product/UI already exists;
- commit claims 29 frontend search tests passing and substantial backend search capability;
- graph container still owns the original view/perspective navigation directly.

**Confidence:** HIGH as the last *pre-performance-migration* anchor.  
**Not yet proven:** full historical build can still be reproduced from this SHA.

### Anchor B — first optimization migration
**SHA:** `27262fa4e780efc8900f6842d101054310eea793`  
**Time:** 2026-01-29 23:24 PST  
**Blast radius:** 2,703 line changes across 6 central frontend graph files.

Changes:
- every major graph view moved to progressive edge loading;
- initial graph reduced to 500 edges vs ~116k;
- GraphViewContainer changed;
- UnifiedGraphView changed heavily;
- graph hooks changed;
- new ProjectMappingGraphView added.

Important inconsistency:
the commit message claims a backend API change adding `exclude_types`, but the actual commit file list contains **only frontend files**.

That is an early evidence mismatch between agent report and ledger reality.

### Anchor C — immediate regression repair
**SHA:** `4a897659d864d98a0194fbf95a286ccc0b27781d`  
**Time:** 2026-01-29 23:33 PST

The commit explicitly states:
- API produced snake_case fields;
- project graph expected camelCase;
- the mapping was missing;
- **edges did not render**.

This establishes that the performance migration introduced/activated a real visible product regression within minutes.

### Anchor D — performance expansion
**SHA:** `370e2c0a3028bb4204afb91bff66b2c313c985f4`  
**Time:** 2026-01-29 23:42 PST

Adds viewport frustum culling as "Phase 1 of the game engine approach":
- AABB culling;
- new React hook;
- node-position extraction;
- viewport bounds;
- planned Canvas rendering next.

The commit calls itself "drop-in" and "no breaking changes" but says it is only ready for integration; it does not prove integration correctness.

### Anchor E — Jan 30 production-claim zone
**SHA:** `d52962705eeedbb59c97ef7975b5cb3bcef25e3c`  
**Time:** 2026-01-29 23:49 PST

Virtualizes ItemsTable and claims:
- production build successful;
- TypeScript compliance;
- performance tests/E2E.

This is consistent with the owner's memory that a usable product may still have existed around Jan 30. The claim is useful evidence but weaker than a reproduced build.

### Anchor F — first explicit production-build repair
**SHA:** `b7367a4e8e0830c1879d5b3e6f2674dbbf14f5aa`  
**Time:** 2026-02-01 17:29 PST

Title:
> fix: TypeScript compilation and production build issues

It changes:
- tsconfig behavior;
- Vite syntax;
- graph component export;
- build config options.

This proves that by this point the frontend production build had accumulated blocking issues.

### Anchor G — mass lint rewrite
**SHA:** `33545b1b8a2a5c53293f97588e3a4ef6b413e615`  
**Time:** 2026-02-02 17:25 PST

Commit report:
- 15,666 violations across 988 files;
- 2,551 auto-fixed;
- 13,115 left.

GitHub stats:
- **106,921 changed lines**;
- **53,750 additions / 53,171 deletions**;
- API returns the maximum 300 changed files.

This is a major semantic-regression risk even if many edits are formatting/lint.

### Anchor H — graph model/schema expansion
**SHA:** `1178cba59716473f0d758496ac7b72818a6f758d`  
**Time:** 2026-02-02 18:29 PST

Refactors already-existing migrations:
- `008_add_graph_views_and_kinds.py`;
- `009_add_graphs_and_graph_nodes.py`.

Those migrations include:
- graph views/kinds;
- graph tables;
- graph_nodes;
- link graph IDs;
- backfills from old views.

This confirms significant graph/product-model schema evolution was occurring during the instability window.

The original introduction of these migrations still needs its own ancestry trace.

### Anchor I — module-integration breakage
**SHA:** `dbd6d283fb41c2306976e60902010226281ef9dc`  
**Time:** 2026-02-02 19:31 PST

Title:
> fix: resolve type errors in main.py from module integration

This explicitly documents integration-generated type breakage across the Python API.

### Anchor J — enormous "70 TS errors" repair
**SHA:** `7016ae1887563adcc2b9bbb7e203c735a4989081`  
**Time:** 2026-02-05 17:30 PST

Commit claims:
- resolved 70 TS errors;
- Dashboard tests fixed;
- quality checks passing.

GitHub stats:
- **819,047 changed lines**;
- **450,478 additions / 368,569 deletions**;
- at least 300 files.

This is far too broad to treat as a normal targeted TypeScript repair. It is a major forensic boundary.

### Anchor K — WebGL/Sigma expansion
**SHA:** `6df15aca9fc1f34125a9a166319eeb248aed3163`  
**Time:** 2026-02-05 19:19 PST

Changes:
- Sigma/WebGL tests;
- visual regression suite;
- OAuth event publisher;
- extensive Phase 5 orchestration/docs.

Stats:
- 17,294 changed lines;
- 48 files.

The enhanced Sigma tests report 13 tests skipped because WebGL is unavailable under jsdom.

### Anchor L — test infrastructure collapse
**SHA:** `daaa4eb9b63057b05635c69694630b5fb2a9c1e9`  
**Time:** 2026-02-05 20:23 PST

Commit says:
- **210/210 tests failing** from MSW/graphql import problem;
- MSW lifecycle disabled;
- HTTP-mocking-dependent test groups blocked;
- primary blocker remained **40+ TypeScript compilation errors**.

This is the strongest explicit proof that by the end of Feb 5 the repo was not maintaining a clean, continuously runnable product baseline.

### Anchor M — Feb 6/7 repeated compile remediation
Subsequent commits continue fixing:
- health/framework/Temporal issues;
- frontend TS compilation errors;
- test TS errors;
- test infrastructure.

A Feb 7 commit eventually claims "100/100 Quality - All Tests Passing", but this must be independently reproduced before treating it as a true recovered product baseline.

---

## Current vs pre-optimization UI shape

### GraphViewContainer
At `0e8b0bdd`:
- 508 lines;
- owns graph-mode sidebar;
- owns six perspective views;
- computes perspective counts;
- renders badges/counts;
- owns mode/perspective selection.

Current main:
- 129 lines;
- delegates to GraphViewSidebar, GraphViewTopBar and useGraphViewState;
- sidebar now represents **project views**;
- top bar represents graph/diagram/perspective modes.

This is not simple loss. It is architectural decomposition plus UX topology change.

### Current GraphViewConfig
Current main still has the old conceptual views:
- traceability;
- page flow;
- components;
- product/business/technical/UI/security/performance perspectives.

It also adds:
- flow chart;
- dependency graph;
- hierarchy;
- impact map;
- journey map;
- mind map;
- gallery.

Thus some old feature intent survives and has expanded.

### UnifiedGraphView
Pre-optimization: ~173 lines.  
Current main: ~1,111 lines.

This is a major concentration of responsibility and should be audited carefully for:
- recovered old journeys;
- renderer selection;
- duplicated state;
- unreachable branches;
- regressions hidden by increased capability.

---

## Preliminary causal assessment

### Performance migration itself
**Confidence: HIGH trigger, MEDIUM root cause.**

Evidence:
- first graph optimization touches all graph views at once;
- immediate broken-edge regression;
- subsequent culling/Canvas/WebGL direction.

Counter-evidence:
- same-day repair exists;
- later commits still claim production builds/tests;
- therefore one commit did not necessarily permanently destroy the product.

### Graph/model expansion
**Confidence: MEDIUM-HIGH contributor.**

Evidence:
- migrations 008/009 add new graph/view/node semantics and backfills;
- module-integration fixes follow;
- owner's recollection includes model expansion after the performance request.

Need:
- identify original commits creating migrations 008/009;
- trace user/problem-model changes under their actual historical names.

### Tooling/lint mass rewrite
**Confidence: VERY HIGH regression amplifier.**

Evidence:
- 106k-line mass rewrite on Feb 2;
- 819k-line mass rewrite on Feb 5;
- thousands of automated fixes;
- repeated follow-up compile/type fixes.

This is precisely the sort of agent operation that can destroy known-good local behavior while leaving a superficially "cleaner" codebase.

### Loss of executable oracle
**Confidence: VERY HIGH durable-failure mechanism.**

Evidence:
- build repair commits repeatedly recur;
- tests become blocked/skipped/disabled;
- MSW was disabled with 210/210 failures;
- benchmark tests later excluded for memory exhaustion;
- owner reports no usable build for months.

Without a permanently enforced known-good smoke journey, agents could continue changing the tree after the product had ceased being usable.

---

## Recovery interpretation

Do **not** simply revert to `0e8b0bdd`.

It is a forensic reference, not the desired current product.

Recovery should construct a behavioral manifest from several historical anchors:

1. `0e8b0bdd` — pre-performance product behavior.
2. `4a897659` / `d5296270` — immediately post-optimization state after first repair.
3. pre-Feb-2 model state.
4. useful later capabilities that were correctly added.
5. current recovered implementation.

For every user-visible capability:
```text
historical behavior
→ current implementation
→ status:
   PRESERVED
   IMPROVED
   CHANGED_INTENTIONALLY
   REGRESSED
   MISSING
   UNKNOWN
```

---

## Required next forensic work

### F-01 — prove historical runnable anchors
Attempt builds/checks at:
- `0e8b0bdd`;
- `4a897659`;
- `d5296270`;
- `b7367a4e`;
- one pre-mass-lint commit;
- `64fc1983` Feb 7 claimed-quality point.

Do not modify those commits. Use detached/worktree builds and record environment failures separately from source failures.

### F-02 — original graph-schema introduction
Trace creation of migrations 008/009 and predecessor schema.

### F-03 — product journey reconstruction
At each anchor capture:
- startup/build;
- login/project selection where applicable;
- project graph;
- global graph;
- page flow;
- component view;
- all perspectives;
- search;
- graph interactions;
- create/edit/link flows.

### F-04 — graph-renderer lineage
Trace:
```text
original renderer
→ progressive loading
→ viewport culling
→ Sigma/WebGL
→ current renderer selection
```

### F-05 — model lineage
Recover historical names/changes for:
- graph/view model;
- problem/domain model the owner remembers;
- user/account model;
- item/link model;
- project model.

### F-06 — mass-rewrite damage scan
For `33545b1b` and `7016ae18`:
- classify files as formatting-only vs semantic;
- inspect high-value graph/API/model diffs;
- identify removed logic later repaired or never recovered.

### F-07 — current recovery completeness
Build a bidirectional trace:
```text
historical capability
↔ current file/route/test
↔ runnable evidence
```

Unknowns stay UNKNOWN; do not invent recovery percentages.

---

## Current conclusion

The best current working hypothesis is:

> Tracera's "core hand" did not fail because graph performance work was intrinsically the wrong idea. The request triggered a whole-product optimization/rearchitecture campaign without preserving the already-usable product as a continuously runnable oracle. An immediate graph regression appeared on Jan 30, then graph/model changes, infrastructure work, mass lint rewrites, and WebGL/test-framework changes compounded the blast radius. By Feb 5 the repository explicitly had blocked test infrastructure and dozens of TypeScript build errors. From there agent changes could no longer reliably distinguish improvement from regression.

This hypothesis should remain falsifiable until historical builds and journeys are reproduced.


## Critical update — d5296270 is the primary forensic pivot

Further paginated GitHub commit inspection shows that `d5296270` is far larger and broader than the commit title suggests.

GitHub stats:
- **1,855,953 changed lines**;
- **1,737,255 additions**;
- **118,698 deletions**;
- commit file listing extends well beyond 1,000 files; the standard API response is capped and requires pagination.

The commit is titled:
> "Implement virtual scrolling in ItemsTableView"

but paginated file history shows that the same transaction also contains or first introduces major portions of:

### Product/domain schema
- `006_add_priority_owner_to_items.py`
- `007_add_problems_and_processes.py`
- `008_add_graph_views_and_kinds.py`
- `009_add_graphs_and_graph_nodes.py`
- graph integrity/denormalization migrations;
- execution system;
- specification tables;
- accounts;
- provider user IDs;
- GitHub/Linear integrations;
- canonical concepts;
- canonical projections;
- perspective configs;
- component libraries;
- equivalence links;
- derived journeys;
- versions/milestones;
- performance indexes.

### User/account/auth surface
- authentication implementation/docs;
- account migration;
- WorkOS/AuthKit work;
- auth routes/store;
- account/user-related database migrations.

### Problem/process surface
- problem/process migration;
- problem-management research;
- `CreateProblemForm`;
- `CreateProcessForm`;
- `useProblems`;
- `ProblemView`;
- `ProcessView`;
- project problem/process routes.

### Graph/product UI
- EnhancedGraphView;
- FlowGraphView;
- VirtualizedGraphView;
- PageDecompositionView;
- JourneyExplorer;
- equivalence UI;
- dimension filters;
- pivot navigation;
- UI-code trace;
- component library;
- graph worker/virtualization hooks;
- graph cache;
- many graph E2E/unit tests.

### Specification/traceability expansion
- ADR UI;
- BDD/Gherkin UI;
- contracts/state-machine UI;
- prioritization;
- analytics/quality;
- item specification cards;
- specification dashboards/APIs/hooks.

### Repository contamination / generated state
The commit also includes:
- Hypothesis generated constants;
- local/test databases;
- exported graph snapshots;
- backup files;
- very large volumes of generated documentation;
- session/trace artifacts.

### Forensic implication

This transaction collapses several logically independent initiatives into one commit:

```text
table virtualization
+ graph performance
+ problem/process model
+ graph schema
+ user/account/auth model
+ specifications
+ journeys
+ execution
+ canonical/equivalence model
+ integration work
+ generated/test artifacts
```

This makes `d5296270` the **primary forensic pivot**.

The owner's memory that the performance request was followed by problem/user/model expansion is not merely chronological: Git shows those changes were committed together in the same enormous transaction.

### Revised causal confidence

- `27262fa4` progressive-loading migration: **HIGH confidence initial destabilization trigger**.
- `d5296270` mega-commit: **VERY HIGH confidence scope-collapse / recoverability failure point**.
- `33545b1b` + `7016ae18`: **VERY HIGH confidence later regression amplifiers**.

The strongest current hypothesis is that the product lost a meaningful transaction boundary at `d5296270`: after that commit it became difficult to isolate whether any break came from rendering, graph schema, domain model, account/auth changes, specifications, or unrelated generated state.

## d5296270 recovery decomposition

Treat the mega-commit as a bundle of independent recovery packages:

1. **R-GRAPH-RENDER** — progressive loading, virtualization, culling, renderer work.
2. **R-GRAPH-MODEL** — graph views/kinds, graph_nodes, integrity, canonical/equivalence model.
3. **R-PROBLEM-PROCESS** — problem/process entities, routes, forms, services.
4. **R-USER-ACCOUNT** — account/user/provider identity/auth changes.
5. **R-SPEC** — specification entities, item specs, BDD/contracts/analytics.
6. **R-JOURNEY** — journeys/derived journeys and UI.
7. **R-EXECUTION** — execution/workflow system.
8. **R-INTEGRATIONS** — GitHub/Linear/webhooks/etc.
9. **R-GENERATED-NOISE** — snapshots, test DBs, generated docs, caches, backups.

Each package must be independently classified:
`PRESERVE / RECOVER / ADAPT / SUPERSEDE / RETIRE / GENERATED-NOISE`.

Do not treat the mega-commit as a single valid historical feature unit.
