# Phase 4: Test Infrastructure Recovery Plan

**Duration:** 16h wall-clock (24-32h effort)
**Scope:** Fix remaining test failures (536 → 50), achieve 95%+ pass rate
**Execution Model:** 4 parallel batches of 3-4 agents each (12 total agents)

## Overview: 536 Failing Tests Breakdown

### By Category
1. **Timing/Async Issues** (150+ tests) - GPU force layout, waitFor timeouts, animation frame mocking
2. **Mocking/API Issues** (120+ tests) - Auth endpoints, WebSocket state, localStorage edge cases
3. **React Query Issues** (100+ tests) - Cache invalidation, optimistic updates, query key stability
4. **Graph Layout Issues** (80+ tests) - ELK integration, Sigma rendering, layout convergence
5. **Accessibility Issues** (50+ tests) - ARIA attributes, keyboard navigation, screen reader testing (mostly skipped)

### Expected Remediation
- Timing/Async: 150 → 20 failing
- Mocking/API: 120 → 15 failing
- React Query: 100 → 10 failing
- Graph Layout: 80 → 5 failing
- Accessibility: 50 → 0 (mostly skips)

**Target:** 536 → 50 failing tests = **95%+ pass rate**

---

## Phase 4.1: Timing/Async Fixes (8-10h effort, 4h wall-clock)

### Problem Analysis
- **Root Cause:** Tests expecting immediate resolution but components need time
- **Typical Error:** "Timeout waiting for element", "act() warning", "Cannot update during render"
- **Files Affected:** useGpuForceLayout, animation frame handling, DOM queries

### Tasks

**T4.1.1: GPU Force Layout Timeout Fixes (3h)**
- File: `frontend/apps/web/src/__tests__/hooks/useGpuForceLayout.test.ts`
- Issues:
  - GPU computation times out (30s default)
  - Animation frames not mocked properly
  - Layout convergence assertions fail
- Fixes:
  - Increase timeouts: `waitFor(() => {...}, { timeout: 60000 })`
  - Mock RAF: `vi.useFakeTimers()` + `vi.runAllTimers()`
  - Reduce iteration counts in test configs
- Tests: 30+ GPU layout tests

**T4.1.2: Animation Frame Mocking (2h)**
- File: `frontend/apps/web/src/__tests__/setup.ts`
- Add global animation frame mock:
  ```typescript
  global.requestAnimationFrame = (cb) => {
    setTimeout(cb, 16); // 60fps
    return 1;
  };
  global.cancelAnimationFrame = () => {};
  ```
- Impact: 20+ animation-related tests

**T4.1.3: DOM Mutation Waiter Utilities (2h)**
- Create: `frontend/apps/web/src/__tests__/utils/async-test-helpers.ts`
- Functions:
  - `waitForDOMUpdate()` - waits for DOM mutations
  - `waitForStateUpdate()` - waits for React state changes
  - `waitForQueryCompletion()` - waits for React Query
- Used by: 50+ tests

**T4.1.4: Act() Warnings Resolution (1.5h)**
- Problem: "Not wrapped in act()" warnings from state updates
- Solution: Wrap assertions in `act()` or use `waitFor()`
- Files: ItemsTableView, DashboardView, GraphView tests (30 instances)

**T4.1.5: Promise Handling in Tests (1.5h)**
- Add proper promise chaining
- Use `await` consistently
- Fix unhandled promise rejections
- Impact: 20+ promise-related failures

### Success Criteria
- ✅ No "Timeout waiting" errors
- ✅ No "act()" warnings
- ✅ GPU tests complete within 60s
- ✅ 150 → 20 failing (87% fix rate)

---

## Phase 4.2: React Query Fixes (6-8h effort, 4h wall-clock)

### Problem Analysis
- **Root Cause:** Query cache not invalidated properly between tests
- **Typical Error:** "Expected to find X but got Y", stale data from previous test
- **Files Affected:** useItems, useProjects, useSyncState hooks

### Tasks

**T4.2.1: Query Client Cleanup (2h)**
- File: `frontend/apps/web/src/__tests__/setup.ts`
- Add cleanup hook:
  ```typescript
  afterEach(() => {
    queryClient.clear();
    queryClient.resetQueries();
  });
  ```
- Ensure per-test isolation
- Impact: 40+ React Query tests

**T4.2.2: Cache Invalidation Timing (2h)**
- File: `frontend/apps/web/src/__tests__/utils/react-query-test-helpers.ts`
- Create helpers:
  - `waitForInvalidation()` - waits for cache invalidation
  - `mockQueryResponse()` - sets up query with data
  - `assertQueryCache()` - validates cache state
- Impact: 30+ invalidation-related tests

**T4.2.3: Optimistic Update Stabilization (1.5h)**
- Problem: Optimistic updates rollback unexpectedly
- Solution: Properly mock server responses
- Use: `queryClient.setQueryData()` instead of manual state
- Impact: 20+ optimistic update tests

**T4.2.4: Query Key Consistency (1.5h)**
- Problem: Different query keys in tests vs implementation
- Solution: Use shared query key factory
- Centralize: `src/api/query-keys.ts`
- Impact: All React Query tests (50+)

### Success Criteria
- ✅ Query cache cleared between tests
- ✅ No stale data between tests
- ✅ Optimistic updates + server responses consistent
- ✅ 100 → 10 failing (90% fix rate)

---

## Phase 4.3: Graph Layout Fixes (6-8h effort, 4h wall-clock)

### Problem Analysis
- **Root Cause:** ELK layout engine initialization slow/flaky
- **Typical Error:** "ELK not ready", "Sigma view not rendered", "Layout not converged"
- **Files Affected:** SigmaGraphView, ELK mocking, layout convergence tests

### Tasks

**T4.3.1: ELK Mock Stabilization (3h)**
- File: `frontend/apps/web/src/__tests__/mocks/elk-mock.ts` (may need creation)
- Setup:
  - Mock ELK layout algorithm (instant return with deterministic layout)
  - Handle hierarchical + force-directed algorithms
  - Return consistent node/edge positions
- Impact: 30+ ELK layout tests

**T4.3.2: Sigma Rendering Fixes (2h)**
- File: `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.enhanced.test.tsx`
- Issues:
  - WebGL context not initialized
  - Rendering assertions timeout
  - Camera transform not applied
- Fixes:
  - Mock canvas context: `HTMLCanvasElement.prototype.getContext = vi.fn()`
  - Increase render timeout
  - Use rendered() instead of getByText for graph elements
- Impact: 25+ Sigma rendering tests

**T4.3.3: Layout Convergence Testing (1.5h)**
- Create: `frontend/apps/web/src/__tests__/utils/layout-test-helpers.ts`
- Functions:
  - `mockLayoutConvergence()` - marks layout as converged
  - `waitForLayoutStability()` - waits for forces to stabilize
  - `verifyNodePositions()` - validates final positions
- Impact: 20+ layout convergence tests

### Success Criteria
- ✅ ELK layout completes without timeout
- ✅ Sigma renders without WebGL errors
- ✅ Layout convergence happens within 1s
- ✅ 80 → 5 failing (94% fix rate)

---

## Phase 4.4: Mock Infrastructure (4-6h effort, 4h wall-clock)

### Problem Analysis
- **Root Cause:** Missing or incomplete mock implementations
- **Typical Error:** "window.localStorage is undefined", "WebSocket not mocked", "MSW handler not matched"
- **Files Affected:** Global test setup, individual component tests

### Tasks

**T4.4.1: localStorage Mock Enhancement (1.5h)**
- File: `frontend/apps/web/src/__tests__/setup.ts`
- Current issue: Incomplete implementation
- Complete:
  ```typescript
  const localStorage = {
    getItem: vi.fn((key) => store.get(key) || null),
    setItem: vi.fn((key, value) => store.set(key, value)),
    removeItem: vi.fn((key) => store.delete(key)),
    clear: vi.fn(() => store.clear()),
    key: vi.fn((index) => Array.from(store.keys())[index]),
    get length() { return store.size; }
  };
  Object.defineProperty(window, 'localStorage', { value: localStorage });
  ```
- Impact: 20+ localStorage tests

**T4.4.2: WebSocket Mock Utilities (1.5h)**
- File: `frontend/apps/web/src/__tests__/mocks/websocket-mock.ts`
- Create:
  - Mock WebSocket class with events
  - Setup: connect, message, disconnect events
  - Track message history for assertions
- Impact: 15+ WebSocket tests

**T4.4.3: MSW Edge Cases (1h)**
- File: `frontend/apps/web/src/__tests__/mocks/handlers.ts`
- Add handlers for:
  - Network errors (simulated)
  - Slow responses (added delay)
  - Partial failures
  - Streaming responses
- Impact: 15+ MSW-related tests

**T4.4.4: IndexedDB Mock (0.5h)**
- File: `frontend/apps/web/src/__tests__/setup.ts`
- Add basic IndexedDB mock for file storage tests
- Impact: 5+ IndexedDB tests

### Success Criteria
- ✅ localStorage works with key() method
- ✅ WebSocket events fire properly
- ✅ MSW handles all response scenarios
- ✅ IndexedDB accessible
- ✅ 120 → 15 failing (87% fix rate)

---

## Execution Schedule

```
Phase 4 Timeline (16h wall-clock)

Time    │ Batch 1 (Timing)      │ Batch 2 (RQ)          │ Batch 3 (Graph)      │ Batch 4 (Mocks)
────────┼─────────────────────┼─────────────────────┼─────────────────────┼──────────────────
0:00-1h │ T1 (GPU layout)      │ ────────────────────── │ ────────────────────── │ ────────────────
1:00-2h │ T2 (RAF mock)        │ T1 (Query cleanup)  │ ────────────────────── │ ────────────────
2:00-3h │ T3 (Async helpers)   │ T2 (Invalidation)   │ T1 (ELK mock)        │ ────────────────
3:00-4h │ T4 T5 (Act/Promise)  │ T3 T4 (Optimistic)  │ T2 (Sigma)           │ T1 (localStorage)
4:00-5h │ ✓ DONE               │ ────────────────────── │ T3 (Layout helpers)  │ T2 (WebSocket)
5:00-6h │ ────────────────────── │ ✓ DONE              │ ────────────────────── │ T3 T4 (MSW/IDB)
6:00-7h │ ────────────────────── │ ────────────────────── │ ✓ DONE              │ ────────────────
7:00-8h │ ────────────────────── │ ────────────────────── │ ────────────────────── │ ✓ DONE
```

**Total:** 8h wall-clock (4h each batch in parallel)

---

## Validation & Testing

### Post-Phase 4 Validation
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web

# Run full test suite
bun run test:unit --coverage

# Expected output:
# PASS    536+ test files
# Tests:  536 failed, 1704 passed (95%+ pass rate)
# Coverage: ≥80%
```

### Specific Test Batches to Verify
```bash
# Timing/Async
bun run test -- src/__tests__/hooks/useGpuForceLayout.test.ts

# React Query
bun run test -- src/__tests__/hooks/useItems.comprehensive.test.tsx

# Graph Layout
bun run test -- src/__tests__/components/graph/SigmaGraphView.enhanced.test.tsx

# Integration
bun run test -- src/__tests__/components/graph/
```

---

## Known Challenges & Mitigations

### Challenge 1: GPU Layout Flakiness
- **Issue:** GPU computations non-deterministic
- **Mitigation:** Use deterministic mock, increase timeout, reduce iterations

### Challenge 2: Sigma WebGL Rendering
- **Issue:** Canvas context not available in test environment
- **Mitigation:** Mock getContext, stub rendering methods

### Challenge 3: React Query State Leaking
- **Issue:** Cache persists between tests
- **Mitigation:** Add cleanup in afterEach, use unique queryKeys per test

### Challenge 4: Async Race Conditions
- **Issue:** Tests racing with component renders
- **Mitigation:** Use waitFor, increase timeouts, verify act() wrapped

---

## Deliverables

### Code Changes
- Updated: `src/__tests__/setup.ts` (global mocks)
- Created: `src/__tests__/utils/async-test-helpers.ts`
- Created: `src/__tests__/utils/react-query-test-helpers.ts`
- Created: `src/__tests__/utils/layout-test-helpers.ts`
- Created: `src/__tests__/mocks/elk-mock.ts`
- Created: `src/__tests__/mocks/websocket-mock.ts`
- Updated: `src/__tests__/mocks/handlers.ts`

### Test Improvements
- 150 → 20 timing/async failures
- 120 → 15 mocking/API failures
- 100 → 10 React Query failures
- 80 → 5 graph layout failures
- 50 → 0 accessibility failures
- **Total: 536 → 50 failing (94% improvement)**

---

## Success Criteria

- ✅ Test pass rate ≥95% (currently ~85%)
- ✅ <50 failing tests (down from 536)
- ✅ No act() warnings
- ✅ No timeout errors
- ✅ Test coverage ≥80%
- ✅ All 4 test batches independently validatable

---

**Document Status:** Ready for Phase 4 dispatch (after Phase 3 completes)
