# Jan 30–Feb 6 2026 Regression Forensics — Recovery Anchor

**Status:** active forensic dossier  
**Owner recollection:** Jan 30–31 was last known usable/working period; Feb 6 is an outer bound after which the product was no longer reliably buildable/usable. The suspected initiating request was scaling the HTML graph toward ~10K nodes, followed by broader DG/problem-model and user-model expansion.

## Evidence already recovered

### Jan 29 23:24 PST — 27262fa4

`FEAT: Migrate all graph components to use progressive edge loading`

This is a direct match for the remembered performance transition. It changed all major graph views, the link hook, graph container, and backend filtering. The commit claims an initial-load change from the full graph to 500 edges and targets 100k+ edges.

This is not merely an optimization internal to the renderer: it changes **data-loading semantics and graph completeness at first render**.

### Jan 29 23:33 PST — 4a897659

Nine minutes later:

`FIX: Map snake_case API response to camelCase for link rendering`

The commit explicitly states that edges were not rendering in one project graph view after the migration because the API response shape did not match graph-component expectations.

This is the first concrete regression witness in the suspected window.

### Jan 29 23:42 PST — 370e2c0a

`FEAT: Add viewport frustum culling for graph performance optimization (Phase 1)`

Introduces viewport-aware edge culling and advertises a game-engine approach. It is described as drop-in/not breaking, but that claim must be independently verified against the working predecessor.

### Jan 29 23:49 PST — d5296270

`FEAT: Implement virtual scrolling in ItemsTableView`

Broadens the optimization campaign beyond the graph renderer.

### Jan 31–Feb 2

The history then pivots heavily into process orchestration, Docker/infrastructure, linting hardening, complexity refactors, naming-explosion remediation, migration refactors, and repeated TypeScript/module fixes.

Notable evidence:
- Feb 1: `fix: TypeScript compilation and production build issues`.
- Feb 2: repeated module/type-safety refactors.
- Feb 2: `fix: resolve type errors in main.py from module integration`.

This is consistent with a repository entering a broad stabilization/refactor campaign rather than remaining a stable product line.

### Feb 5

There is an extremely dense test/CI remediation burst:
- route validation;
- TypeScript diagnostics;
- 70 TypeScript compilation errors;
- Dashboard failures;
- vitest setup fixes;
- memory-intensive tests skipped;
- MSW repeatedly enabled/disabled/re-enabled;
- GraphQL ESM/CommonJS blocker;
- WebGL/OAuth work;
- multiple temporary/checkpoint commits.

This is strong evidence that by Feb 5 the tree was not simply a stable Jan product plus one renderer optimization.

## Current working hypothesis

The failure was likely **not one single bad commit**.

A more plausible chain is:

1. usable product state;
2. graph-scale request;
3. progressive loading changes data completeness semantics across every graph view;
4. immediate graph rendering regression proves integration was already brittle;
5. additional culling/virtualization/performance work;
6. broad infrastructure/lint/type/module refactors;
7. DG/user/product-model expansion (still to pinpoint);
8. test harness instability and large-scale remediation;
9. prolonged lack of a reliable owner-testable build;
10. later agent work accumulates over an already unstable base;
11. subsequent recovery restores pieces but may not reconstruct the last coherent product.

## Recovery methodology

Do **not** pick Jan 30 or Feb 6 by date alone.

Identify four anchors:

- **LKG-A:** last commit with evidence of a complete owner-usable build before the performance campaign.
- **PERF-START:** first semantic performance change (currently 27262fa4 is a strong candidate).
- **FIRST-BAD:** first commit where the previously usable journey demonstrably breaks (4a897659 proves a preceding edge-rendering failure, but the precise first-bad parent/commit still needs bisect-style reconstruction).
- **STABILITY-LOSS:** point where build/test/product coherence becomes continuously unreliable.

For each anchor reconstruct:
- build/install commands;
- frontend route tree;
- graph components/renderers;
- data loading semantics;
- item/link/domain models;
- DG/problem model;
- user/auth model;
- API contracts;
- tests actually runnable;
- screenshots/docs/demos if present;
- owner-critical journeys.

Then compare each anchor to:
1. current main;
2. mature recovery branch;
3. any later recovery commits.

Classify every meaningful capability:
- PRESERVED;
- IMPROVED;
- REGRESSED;
- LOST;
- REPLACED;
- UNKNOWN.

## Critical rule

Do not revert the performance campaign wholesale. Some optimizations may be valuable and correct.

Recover the **usable product semantics** first, then re-admit optimizations individually behind evidence:
- functional equivalence;
- graph completeness semantics;
- visual correctness;
- interaction correctness;
- performance benchmark;
- buildability;
- rollback/fallback.

## Immediate next forensic work

1. identify parent/predecessor of 27262fa4 and reconstruct that frontend;
2. enumerate all commits in the 2-hour performance burst;
3. locate DG/problem-model and user-model commits through Feb 6;
4. compare route/API/model surfaces before and after;
5. locate historical build artifacts/workflows and actual successful CI evidence;
6. find screenshots, demos, E2E tests, Storybook, deployment records;
7. produce capability delta matrix against current branch;
8. turn lost/regressed capabilities into explicit recovery requirements rather than ad-hoc cherry-picks.
