# Frontend Test Collection Repair Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Restore deterministic collection and execution for all 230 frontend test files without deleting tests, weakening assertions, or masking failures with broad exclusions.

**Architecture:** Repair collection in three narrow layers: static module/name correctness, bounded browser-environment contracts, then current-production WebSocket harnesses. Each layer gets a focused red/green command before the 230-file collection gate and 16-shard assertion repair resume.

**Tech Stack:** TypeScript, React 19, Vitest 4, Testing Library/user-event, jsdom, TanStack Router, Sigma/WebGL.

---

### Task 1: Freeze the collection-failure inventory

**Files:**
- Create: `docs/superpowers/plans/2026-08-29-frontend-test-collection-repair.md`
- Reference: `frontend/apps/web/vitest.config.ts`

**Step 1: Reproduce the failure set**

Run the 12-file focused command recorded below. Expected: 12 failed files: two zero-suite files, six invalid imports/runner references, one undefined runtime suite name, one missing WebGL global, and two WebSocket files that replace jsdom's `window` and break clipboard teardown.

```bash
cd frontend/apps/web
npm test -- --maxWorkers=1 --reporter=dot \
  src/context/AuthTokenContext.test.tsx \
  'src/routes/projects.$projectId.views.test.tsx' \
  src/__tests__/accessibility/form-validation-accessibility.test.tsx \
  src/__tests__/e2e/hybrid-graph.e2e.test.tsx \
  src/__tests__/api/mcp-client.test.ts \
  src/__tests__/api/websocket.comprehensive.test.ts \
  src/__tests__/api/websocket.test.ts \
  src/__tests__/stores/syncStore.test.ts \
  src/__tests__/stores/uiStore.test.ts \
  src/__tests__/visual/visual-regression.test.ts \
  src/__tests__/workers/WorkerPool.test.ts \
  src/hooks/__tests__/useViewportGraph.test.ts
```

**Step 2: Commit the inventory and plan**

```bash
git add docs/superpowers/plans/2026-08-29-frontend-test-collection-repair.md
git commit -m "docs(tracera): plan frontend collection repair"
```

### Task 2: Repair static collection contracts

**Files:**
- Modify: `frontend/apps/web/src/__tests__/api/mcp-client.test.ts:7-14`
- Modify: `frontend/apps/web/src/__tests__/accessibility/form-validation-accessibility.test.tsx:11-12`
- Modify: `frontend/apps/web/src/__tests__/stores/syncStore.test.ts:9`
- Modify: `frontend/apps/web/src/__tests__/stores/uiStore.test.ts:8`
- Modify: `frontend/apps/web/src/__tests__/workers/WorkerPool.test.ts:7`
- Modify: `frontend/apps/web/src/hooks/__tests__/useViewportGraph.test.ts:10`
- Move: `frontend/apps/web/src/context/AuthTokenContext.test.tsx` to `frontend/apps/web/src/context/AuthTokenContext.deprecated.tsx`
- Modify: `frontend/apps/web/vitest.config.ts`
- Test: `frontend/apps/web/src/__tests__/config/vitest-execution-profile.test.ts`

**Step 1: Add a failing configuration contract**

Assert that the production route module `src/routes/projects.$projectId.views.test.tsx` is the only route-source collision excluded from test discovery, with a comment explaining that TanStack's filename encodes the public `/views/test` route. Assert no wildcard test exclusion was added.

**Step 2: Run the focused config test and observe failure**

```bash
cd frontend/apps/web
npm test -- src/__tests__/config/vitest-execution-profile.test.ts
```

**Step 3: Apply minimal static repairs**

- Change `describe(MCPClient, ...)` to the stable string `describe('MCPClient', ...)`; retain the type-only import.
- Remove the nonexistent `../a11y/jest-axe` side-effect import because `../a11y/setup` already installs the Vitest-compatible matcher.
- Correct camel-case paths to `sync-store`, `ui-store`, and `worker-pool`.
- Replace `bun:test` with `vitest`.
- Reclassify the one-line deprecated AuthToken marker outside `.test.*`; preserve its content and history.
- Add only the exact production-route filename to Vitest `exclude`; do not exclude a real test or use a wildcard.

**Step 4: Run focused collection tests**

```bash
cd frontend/apps/web
npm test -- --maxWorkers=1 --reporter=dot \
  src/__tests__/config/vitest-execution-profile.test.ts \
  src/__tests__/accessibility/form-validation-accessibility.test.tsx \
  src/__tests__/api/mcp-client.test.ts \
  src/__tests__/stores/syncStore.test.ts \
  src/__tests__/stores/uiStore.test.ts \
  src/__tests__/workers/WorkerPool.test.ts \
  src/hooks/__tests__/useViewportGraph.test.ts
```

Expected: all files collect. Any current-contract assertion failures are recorded for Stage D, not suppressed.

**Step 5: Commit**

```bash
git add frontend/apps/web
git commit -m "test(frontend): repair static test collection"
```

### Task 3: Restore the visual-regression utility contract

**Files:**
- Create: `frontend/apps/web/src/components/graph/__stories__/visual-regression-automation.ts`
- Test: `frontend/apps/web/src/__tests__/visual/visual-regression.test.ts`

**Step 1: Treat the existing 36-test suite as the contract**

Run it and retain the missing-module failure.

```bash
cd frontend/apps/web
npm test -- src/__tests__/visual/visual-regression.test.ts
```

**Step 2: Implement the bounded pure utility**

Implement deterministic snapshot-name normalization, viewport/theme/interaction story factories, an in-memory regression tracker, snapshot metrics, and configuration validation. Keep the module side-effect free; it must not invoke Storybook, browsers, network, or filesystem.

**Step 3: Run the focused suite**

Expected: all visual-regression utility tests pass and terminate.

**Step 4: Commit**

```bash
git add frontend/apps/web/src/components/graph/__stories__/visual-regression-automation.ts frontend/apps/web/src/__tests__/visual/visual-regression.test.ts
git commit -m "test(frontend): restore visual regression helpers"
```

### Task 4: Bound the WebGL environment contract

**Files:**
- Modify: `frontend/apps/web/src/__tests__/setup.ts:22-45`
- Test: `frontend/apps/web/src/__tests__/e2e/hybrid-graph.e2e.test.tsx`

**Step 1: Preserve the import-time red test**

Run the hybrid graph suite. Expected: Sigma import throws because `WebGLRenderingContext` is undefined even though `WebGL2RenderingContext` exists.

**Step 2: Add the missing constructor-shaped global**

Install configurable `WebGLRenderingContext` and `WebGL2RenderingContext` test constructors with only constants needed at module import. Do not patch production graph code or claim render fidelity from the double.

**Step 3: Run focused hybrid graph tests**

```bash
cd frontend/apps/web
npm test -- src/__tests__/e2e/hybrid-graph.e2e.test.tsx
```

Expected: module collection succeeds. Record assertion-level drift separately.

**Step 4: Commit**

```bash
git add frontend/apps/web/src/__tests__/setup.ts
git commit -m "test(frontend): provide bounded WebGL globals"
```

### Task 5: Stop WebSocket suites from replacing jsdom

**Files:**
- Modify: `frontend/apps/web/src/__tests__/api/websocket.test.ts`
- Modify: `frontend/apps/web/src/__tests__/api/websocket.comprehensive.test.ts`
- Reference: `frontend/apps/web/src/api/websocket.ts`

**Step 1: Preserve the teardown and assertion failures**

Run both suites together. Expected: clipboard teardown errors plus authentication/current-contract failures.

**Step 2: Replace the narrow dependencies, not `window`**

Retain jsdom's `window`, document, navigator, and clipboard. Spy or stub only `location`, interval functions, `WebSocket`, and the authentication dependency consumed by current production code. Restore every stub in unconditional teardown and reset the singleton through its supported boundary or module isolation.

**Step 3: Run both focused suites**

```bash
cd frontend/apps/web
npm test -- --maxWorkers=1 \
  src/__tests__/api/websocket.test.ts \
  src/__tests__/api/websocket.comprehensive.test.ts
```

Expected: no clipboard/user-event unhandled errors; assertions reflect current authenticated WebSocket behavior.

**Step 4: Commit**

```bash
git add frontend/apps/web/src/__tests__/api/websocket.test.ts frontend/apps/web/src/__tests__/api/websocket.comprehensive.test.ts
git commit -m "test(frontend): isolate websocket browser harness"
```

### Task 6: Prove complete collection before assertion churn

**Files:**
- Modify only if required by a newly exposed collection error.

**Step 1: Verify discovery count**

```bash
cd frontend/apps/web
bun x vitest list --filesOnly | wc -l
```

Expected: 229 included test files after the obsolete AuthToken marker is reclassified and the production route collision is excluded. This preserves all 228 genuine tests plus the newly added config contract; the former 230 count included two non-tests.

**Step 2: Run a collection-only execution pass**

```bash
cd frontend
node scripts/verify-vitest-termination.mjs --deadline-ms 240000 --grace-ms 5000 -- \
  npm --prefix apps/web test -- --testNamePattern='^$' --maxWorkers=1
```

Expected: no failed suite, import error, zero-test file, or unhandled setup error; process exits autonomously. A nonzero no-matching-test status is acceptable only if the output proves all files imported without collection failure.

**Step 3: Resume Stage D**

Run the 16 deterministic shards, classify assertion failures by current production boundary, and repair one bounded contract family per commit. Do not push or open the PR until all shards, full `test:unit:bounded`, typecheck, build, parity, and accessibility gates are green.
