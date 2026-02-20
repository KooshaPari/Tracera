# CRITICAL BLOCKER: MSW GraphQL ESM/CommonJS Import Failure

**Date:** 2026-02-06
**Status:** 🔴 BLOCKING ALL TEST EXECUTION
**Impact:** 210/210 test files failing (0% pass rate)
**Phase 5 Status:** Wave 2-3 BLOCKED - cannot execute without working tests

---

## The Problem

**Error:**
```
SyntaxError: The requested module 'graphql' does not provide an export named 'parse'
❯ src/__tests__/mocks/handlers.ts:1
```

**Root Cause:**
- MSW 2.12.7 has internal dependency on `graphql` package
- graphql@16.12.0 has ESM/CommonJS compatibility issues in vitest+jsdom environment
- MSW server initialization fails on import, cascading to all 210 test files
- Commit cdd1f8a09 attempted to disable MSW but re-enabled in later commits

**Impact:**
- ✅ Wave 1 (Gaps 5.1-5.2): COMPLETE (18 tests) - no HTTP mocking required
- ❌ Wave 2 (Gaps 5.3-5.5): BLOCKED - requires MSW handlers for integration tests
- ❌ Wave 3 (Gaps 5.6-5.8): BLOCKED - requires MSW handlers for API endpoint tests
- ❌ ALL 210 TEST FILES FAILING - test infrastructure completely broken

---

## Evidence

### Test Run Output (2026-02-06 20:18-20:20)
```
Test Files  210 failed (210)
Tests  no tests
Duration  81.54s

SyntaxError: The requested module 'graphql' does not provide an export named 'parse'
```

### Git History
```
cdd1f8a09 - fix: disable MSW in setup.ts to unblock test execution
267e49f7a - Phase 5 Checkpoint 3 - MSW fixes validated (❌ NOT VALIDATED)
a00404607 - enable app-integration tests with MSW server initialization
```

**Key Finding:** MSW was disabled in cdd1f8a09 but re-enabled in subsequent commits without fixing the graphql issue.

---

## Why This Blocks Phase 5

### Wave 2 (Gaps 5.3-5.5) Requirements
- **Gap 5.3:** Frontend integration tests - **REQUIRES MSW** for API mocking
  - 8 tests target: search endpoints, export, app initialization
  - Cannot execute without MSW handlers
- **Gap 5.4:** Temporal workflow - May work (backend-focused)
- **Gap 5.5:** E2E accessibility - **REQUIRES MSW** for API handlers
  - 6 tests target: table data, WCAG validation
  - Cannot execute without test data from mocked APIs

### Wave 3 (Gaps 5.6-5.8) Requirements
- **Gap 5.6:** API endpoint tests - **REQUIRES MSW** (15 tests)
  - All CRUD operations depend on MSW handlers
- **Gap 5.7:** GPU compute shaders - May work (no HTTP mocking)
- **Gap 5.8:** Spatial indexing - May work (no HTTP mocking)

**Wave 2 Blocked:** 14/15 tests require MSW
**Wave 3 Blocked:** 15/30 tests require MSW
**Total Blocked:** 29/45 remaining tests (64%)

---

## Possible Solutions

### Solution 1: Downgrade graphql (RECOMMENDED)
```json
// package.json
"graphql": "^16.8.1"  // Known stable with MSW 2.x
```
- **Pros:** Proven fix, minimal changes
- **Cons:** Slightly older version
- **Risk:** Low
- **Time:** 2-3 minutes (install + test)

### Solution 2: Configure Vitest ESM Resolution
```ts
// vitest.config.ts
export default defineConfig({
  resolve: {
    alias: {
      'graphql': 'graphql/index.mjs'
    }
  }
})
```
- **Pros:** No dependency changes
- **Cons:** May not fully resolve issue
- **Risk:** Medium
- **Time:** 5-10 minutes (config + test + troubleshoot)

### Solution 3: Disable MSW Temporarily
```ts
// frontend/apps/web/src/__tests__/setup.ts (lines 331-349)
// Comment out beforeAll, afterAll, afterEach MSW lifecycle
```
- **Pros:** Immediate unblock for non-HTTP tests
- **Cons:** Wave 2-3 still blocked (29 tests unusable)
- **Risk:** Low for partial execution
- **Time:** 1 minute
- **Impact:** Only Gap 5.4, 5.7, 5.8 can execute (16/45 tests, 36%)

### Solution 4: Replace MSW with fetch-mock
- **Pros:** No GraphQL dependency
- **Cons:** Major refactor, 100+ handler rewrites
- **Risk:** Very High
- **Time:** 4-6 hours
- **Recommendation:** ❌ NOT VIABLE for Phase 5 timeline

---

## Recommended Action Plan

### Immediate (5 minutes)
1. **Downgrade graphql** to 16.8.1 (Solution 1)
2. **Run install:** `bun install`
3. **Verify fix:** `bun run test --run | head -100`
4. **Expected:** Tests execute, MSW handlers work

### If Solution 1 Fails (15 minutes)
1. **Try Solution 2:** Configure vitest ESM alias
2. **Test again**
3. **If still failing:** Apply Solution 3 (disable MSW)
   - Document which tests can execute
   - Adjust Phase 5 targets: 16/80 tests (Gap 5.4, 5.7, 5.8 only)

### Fallback (Wave 2-3 Pivot)
If MSW cannot be fixed in 20 minutes:
1. **Execute Gap 5.4, 5.7, 5.8 only** (16 tests, no MSW required)
2. **Skip Gap 5.3, 5.5, 5.6** (29 tests, MSW required)
3. **Adjust Phase 5 target:** 18 (Wave 1) + 16 (Wave 2-3 subset) = 34/80 tests (43%)
4. **Document MSW blocker** for future remediation (Phase 6)

---

## Impact Timeline

**If Fixed in Next 20 Minutes:**
- ✅ Wave 2-3 can execute as planned
- ✅ Target: 18 + 15 + 30 = 63+ tests (originally 65+)
- ✅ Phase 5 completion: T+90 (on schedule)

**If Not Fixed:**
- ❌ Wave 2-3 reduced to Gap 5.4, 5.7, 5.8 only
- ❌ Target: 18 + 16 = 34 tests (47% reduction)
- ❌ Phase 5 completion: 34/80 tests (42.5% vs 81% target)
- 📋 MSW fix deferred to Phase 6 (backend focus)

---

## Current State

**Test Suite:** 0% passing (210/210 FAIL)
**Blocker:** graphql ESM import in MSW initialization
**Phase 5 Progress:** 18/80 tests (22.5%) - Wave 1 only
**Time Remaining:** ~40-50 minutes to T+90 target
**Action Required:** IMMEDIATE - fix MSW or pivot to non-MSW tests

---

## Files Involved

**Test Infrastructure:**
- `frontend/apps/web/src/__tests__/setup.ts` (lines 331-349) - MSW lifecycle
- `frontend/apps/web/src/__tests__/mocks/handlers.ts` - HTTP handlers
- `frontend/apps/web/package.json` - graphql dependency

**Phase 5 Blocked Tests:**
- `src/__tests__/integration/app-integration.test.tsx` (Gap 5.3, 8 tests)
- `src/__tests__/views/ItemsTableView.a11y.test.tsx` (Gap 5.5, 6 tests)
- `src/__tests__/api/endpoints.test.ts` (Gap 5.6, 15 tests)
- **Total Blocked:** 29/45 remaining tests

---

**Status:** 🔴 CRITICAL - IMMEDIATE ACTION REQUIRED
**Recommendation:** Apply Solution 1 (downgrade graphql) immediately
**Fallback:** Solution 3 (disable MSW, execute subset) if Solution 1 fails

---

*This blocker must be resolved or pivoted around within 20 minutes to preserve Phase 5 timeline.*
