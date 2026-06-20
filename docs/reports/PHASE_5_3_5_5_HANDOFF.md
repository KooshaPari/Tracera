# Phase 5.3-5.5 Architecture & Planning - HANDOFF DOCUMENT

**Date:** 2026-02-05
**Architect:** integration-tests-architect
**Status:** ✅ ARCHITECTURE PHASE COMPLETE
**Next Phase:** IMPLEMENTATION (Ready for agent execution)

---

## Executive Summary

Complete architecture and planning for **Phase 5.3-5.5** (15 tests across 3 gaps) has been delivered. All documentation, code sketches, and task assignments are ready for immediate implementation.

**Key Metrics:**
- **Total Tests:** 15 (8 + 1 + 6)
- **Files to Modify:** 12 (4 create, 8 modify)
- **New Code:** ~600 LOC
- **Parallel Agents:** 3
- **Estimated Time:** 40-60 minutes wall-clock

---

## Phase 5.3: Frontend Integration Tests (8 Tests)

### Assignment
**Task:** #6 (in_progress)
**Owner:** integration-tests-implementer
**Tasks:** #9 (agent task assignment)

### Problem Statement
8 integration tests are skipped in `app-integration.test.tsx`:
- Lines 370, 715, 730, 744, 761, 852, 876, 1006

**Root Causes:**
1. Missing MSW handlers (reports, search, export endpoints)
2. Store contamination (no cleanup between tests)
3. Incomplete test fixtures
4. Async timing issues

### Solution Architecture
```
MSW Handlers (3 endpoints)
├─ GET /api/v1/reports/templates
├─ GET /api/v1/search?q=...
└─ POST /api/v1/reports/export

Test Fixtures (extended data)
├─ mockReports array
└─ Extended mockItems (5+ items)

Global Cleanup (afterEach)
├─ Reset all zustand stores
├─ Clear localStorage
└─ Reset vi.mocks()

Test Helpers (reusable utilities)
├─ clearAllStores()
├─ waitFor* functions
└─ Assert helpers

Re-enable Tests
└─ Replace 8 it.skip → it()
```

### Implementation Steps
1. **Task 5.3.1:** Extend `handlers.ts` (add 3 endpoints) - 40 LOC
2. **Task 5.3.2:** Extend `data.ts` (add mockReports) - 50 LOC
3. **Task 5.3.3:** Add to `setup.ts` (afterEach cleanup) - 50 LOC
4. **Task 5.3.4:** Create `async-test-helpers.ts` (NEW) - 150 LOC
5. **Task 5.3.5:** Update `app-integration.test.tsx` (replace it.skip) - refactor

### Files Involved
```
frontend/apps/web/src/__tests__/
├── mocks/
│   ├── handlers.ts           [+3 endpoints]
│   └── data.ts               [+mockReports]
├── setup.ts                  [+afterEach]
├── helpers/
│   └── async-test-helpers.ts [NEW]
└── integration/
    └── app-integration.test.tsx [8 it.skip→it]
```

### Success Criteria
- ✓ 8/8 tests passing
- ✓ No flakes (5x run validation)
- ✓ Coverage maintained ≥85%
- ✓ All stores isolated between tests

### Validation Command
```bash
npm test -- app-integration.test.tsx --reporter=verbose
# Expected: PASS 8, FAIL 0
```

---

## Phase 5.4: Temporal Snapshot Workflow (1 Test)

### Assignment
**Task:** #7 (in_progress)
**Owner:** general-purpose (agent)
**Tasks:** #10 (agent task assignment)

### Problem Statement
1 snapshot workflow test is skipped in `test_minio_snapshots.py:218`:
- Reason: "Requires Temporal test environment"

**Root Causes:**
1. No snapshot activities defined (activities.go missing)
2. No snapshot workflow defined (workflows.go missing)
3. No Temporal test environment setup
4. No service integration

### Solution Architecture
```
Activities (3 functions)
├─ QuerySnapshot(sessionID) → SnapshotPayload
│  └─ Query Neo4j + PostgreSQL
├─ CreateSnapshot(payload) → []byte
│  └─ Serialize JSON + gzip compression
└─ UploadSnapshot(sessionID, data) → s3Key
   └─ Upload to MinIO

Workflow (chain activities)
├─ Execute QuerySnapshot
├─ Execute CreateSnapshot (uses payload from #1)
├─ Execute UploadSnapshot (uses tarball from #2)
└─ Return SnapshotResult

Test Environment
├─ Temporal test server
├─ Worker with workflow + activities
└─ Pytest fixture

Service Integration
└─ Register workflow + activities
```

### Implementation Steps
1. **Task 5.4.1:** Create `activities.go` (3 activities) - 200 LOC
2. **Task 5.4.2:** Create `workflows.go` (workflow + retry) - 100 LOC
3. **Task 5.4.3:** Add to `test_minio_snapshots.py` (fixture + uncomment) - 30 LOC
4. **Task 5.4.4:** Update `service.go` (register) - 30 LOC

### Files Involved
```
backend/
├── internal/temporal/
│   ├── activities.go         [NEW - 200 LOC]
│   └── workflows.go          [NEW - 100 LOC]
├── tests/integration/
│   └── test_minio_snapshots.py [+fixture, uncomment]
└── internal/services/
    └── service.go             [+registration]
```

### Success Criteria
- ✓ 1/1 test passing
- ✓ Snapshot tarball created (>0 bytes)
- ✓ MinIO upload verified
- ✓ Session metadata updated with S3 key
- ✓ Retry policies working

### Validation Command
```bash
make test-backend TEST_TEMPORAL=1 -k snapshot
# Expected: PASS 1, MinIO objects created
```

---

## Phase 5.5: E2E Accessibility Tests (6 Tests)

### Assignment
**Task:** #8 (in_progress)
**Owner:** general-purpose (agent)
**Tasks:** #11 (agent task assignment)

### Problem Statement
6 accessibility tests are skipped in `table-accessibility.a11y.spec.ts`:
- Lines 60, 82, 101, 118, 139, 157

**Root Cause:**
Tests skip due to insufficient table rows (need 7+ data rows)

### Solution Architecture
```
Table Test Data (10 items)
├─ 7 minimum required (for PageUp test)
├─ 10 recommended (better coverage)
└─ Mix of types/status/priority

API Handler Update
├─ Return all 10 items
├─ Support limit/offset pagination
└─ Return total count

Playwright Fixture (beforeEach)
├─ Route /api/v1/items requests
├─ Navigate to /items
├─ Wait for row at index 7 (ensures 8+ rows)
└─ Add 100ms stability delay

Re-enable Tests
├─ Remove conditional test.skip()
├─ Tests now run (rows exist)
└─ 6 tests verify keyboard navigation

WCAG Validation (optional)
├─ Use AxeBuilder for accessibility audit
├─ Verify WCAG 2.1 AA compliance
└─ Check ARIA structure
```

### Implementation Steps
1. **Task 5.5.1:** Extend `testData.ts` (10 items) - 100 LOC
2. **Task 5.5.2:** Update `api-mocks.ts` (items handler) - 20 LOC
3. **Task 5.5.3:** Update `table-accessibility.a11y.spec.ts` (beforeEach) - fixture
4. **Task 5.5.4:** Remove test.skip() from 6 tests - refactor
5. **Task 5.5.5:** Add WCAG validation tests (optional) - 50 LOC

### Files Involved
```
frontend/apps/web/e2e/
├── fixtures/
│   ├── testData.ts              [+10 tableTestItems]
│   └── api-mocks.ts             [update items endpoint]
└── table-accessibility.a11y.spec.ts [beforeEach wait + remove 6 skip]
```

### Success Criteria
- ✓ 6/6 tests passing
- ✓ All 10 data rows loaded
- ✓ Keyboard navigation verified
- ✓ WCAG 2.1 AA compliant (0 violations)
- ✓ Focus management working

### Validation Command
```bash
npx playwright test table-accessibility.a11y.spec.ts
# Expected: PASS 6, WCAG 2.1 AA compliance verified
```

---

## Implementation Timeline

### Phase 1: Parallel (10-15 minutes)

**Agent 1 (Gap 5.3):** MSW handlers + test data
- Task 5.3.1: handlers.ts (3 endpoints)
- Task 5.3.2: data.ts (mockReports)

**Agent 2 (Gap 5.4):** Temporal activities + workflows
- Task 5.4.1: activities.go (3 activities)
- Task 5.4.2: workflows.go (workflow)

**Agent 3 (Gap 5.5):** Table test data
- Task 5.5.1: testData.ts (10 items)
- Task 5.5.2: api-mocks.ts (handler)

✓ **Sync Checkpoint:** All 3 agents report completion

---

### Phase 2: Parallel (10-15 minutes)

**Agent 1 (Gap 5.3):** Cleanup + helpers
- Task 5.3.3: setup.ts (afterEach)
- Task 5.3.4: async-test-helpers.ts (NEW)

**Agent 2 (Gap 5.4):** Test setup + integration
- Task 5.4.3: test_minio_snapshots.py (fixture)
- Task 5.4.4: service.go (registration)

**Agent 3 (Gap 5.5):** Fixture + re-enable
- Task 5.5.3: beforeEach update
- Task 5.5.4: Remove 6 test.skip()

✓ **Sync Checkpoint:** All 3 agents report completion

---

### Phase 3: Parallel (5-10 minutes)

**Agent 1 (Gap 5.3):** Re-enable tests
- Task 5.3.5: app-integration.test.tsx (replace 8 it.skip)

**Agent 2 (Gap 5.4):** Verification
- Verify workflow/activities registered

**Agent 3 (Gap 5.5):** WCAG validation
- Task 5.5.5: Add axe-core tests (optional)

✓ **Sync Checkpoint:** All 3 agents report completion

---

### Phase 4: Sequential Testing (10 minutes)

```bash
# Gap 5.3: 8 tests
npm test -- app-integration.test.tsx
# Expected: PASS 8/8

# Gap 5.4: 1 test
make test-backend TEST_TEMPORAL=1 -k snapshot
# Expected: PASS 1/1

# Gap 5.5: 6 tests
npx playwright test table-accessibility.a11y.spec.ts
# Expected: PASS 6/6
```

✓ **Final Success:** 15/15 tests passing

---

## Total Scope Summary

### Code Changes
```
Files to Create:  4
├─ backend/internal/temporal/activities.go
├─ backend/internal/temporal/workflows.go
├─ frontend/apps/web/src/__tests__/helpers/async-test-helpers.ts
└─ (extends) frontend/apps/web/e2e/fixtures/testData.ts

Files to Modify:  8
├─ frontend/apps/web/src/__tests__/mocks/handlers.ts
├─ frontend/apps/web/src/__tests__/mocks/data.ts
├─ frontend/apps/web/src/__tests__/setup.ts
├─ frontend/apps/web/src/__tests__/integration/app-integration.test.tsx
├─ backend/tests/integration/test_minio_snapshots.py
├─ backend/internal/services/service.go
├─ frontend/apps/web/e2e/fixtures/api-mocks.ts
└─ frontend/apps/web/e2e/table-accessibility.a11y.spec.ts

Total New Code: ~600 LOC
```

### Execution Model
```
3 Parallel Agents
├─ Agent 1: Gap 5.3 (integration-tests-implementer) - 20 min
├─ Agent 2: Gap 5.4 (general-purpose) - 30 min
└─ Agent 3: Gap 5.5 (general-purpose) - 20 min

4 Phases (3 parallel + 1 sequential)
├─ Phase 1: 10-15 min (parallel)
├─ Phase 2: 10-15 min (parallel)
├─ Phase 3: 5-10 min (parallel)
└─ Phase 4: 10 min (sequential)

Total Wall-Clock: 40-60 minutes
```

---

## Documentation Structure

All documents are located in `/docs/`:

```
docs/
├── reports/
│   ├── PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md      (800 lines)
│   └── PHASE_5_3_5_5_ARCHITECTURE_COMPLETE.md    (200 lines)
├── reference/
│   └── PHASE_5_3_5_5_QUICK_REFERENCE.md          (400 lines)
└── guides/
    └── PHASE_5_3_5_5_CODE_IMPLEMENTATION.md      (900 lines)
```

**How to Use:**
1. **Overview:** Start with ARCHITECTURE_COMPLETE.md (this section)
2. **Quick Setup:** Use QUICK_REFERENCE.md for checklists
3. **Deep Dive:** Read IMPLEMENTATION_PLAN.md for full architecture
4. **Implementation:** Follow CODE_IMPLEMENTATION.md (step-by-step)

---

## Success Criteria

### Gap 5.3: ✓ 8 Tests Passing
```
✓ Line 370: maintain recent projects list
✓ Line 715: show loading state
✓ Line 730: render reports templates
✓ Line 744: allow format selection
✓ Line 761: generate report on button click
✓ Line 852: perform search on input
✓ Line 876: show no results message
✓ Line 1006: handle offline-to-online sync

Validation: 5x run with no flakes
Coverage: 85%+ maintained
```

### Gap 5.4: ✓ 1 Test Passing
```
✓ test_scheduled_snapshot_workflow passes
✓ Snapshot tarball created (verified size > 0)
✓ MinIO upload successful (object exists)
✓ Session metadata updated with S3 key
✓ Retry policies working (simulate failures)
```

### Gap 5.5: ✓ 6 Tests Passing
```
✓ Arrow key navigation (Up/Down)
✓ Home key navigation
✓ End key navigation
✓ Ctrl+Home navigation
✓ Ctrl+End navigation
✓ PageUp navigation

Additional:
✓ WCAG 2.1 AA compliance (0 violations)
✓ All keyboard events firing
✓ Focus management working
```

### Final: ✓ 15/15 Tests Passing
```
Phase 5.3: 8/8
Phase 5.4: 1/1
Phase 5.5: 6/6
─────────────
Total:    15/15 ✓
```

---

## Getting Started

### For Implementation Agents

1. **Read This Document** (5 min)
   - Get overview of all 3 gaps
   - Understand assignment & timeline

2. **Review Your Gap Section** (5 min)
   - Read detailed problem statement
   - Review solution architecture
   - Check file list

3. **Follow CODE_IMPLEMENTATION.md** (30-40 min)
   - Go to your gap section (5.3, 5.4, or 5.5)
   - Follow step-by-step instructions
   - Copy code from sketches

4. **Validate Your Work** (5 min)
   - Run tests for your gap
   - Verify all tests pass
   - Report completion

### For Team Lead

1. **Review Architecture** (10 min)
   - Read PHASE_5_3_5_5_ARCHITECTURE_COMPLETE.md
   - Check task assignments
   - Review timeline

2. **Approve & Assign** (5 min)
   - Assign agents to Task #6, #7, #8
   - Confirm parallel execution model
   - Set sync checkpoints

3. **Monitor Execution** (ongoing)
   - Check agent progress after each phase
   - Review test results in Phase 4
   - Validate 15/15 success criteria

---

## Next Steps

✅ **Completed:**
- Architecture & planning
- Root cause analysis
- Solution design
- Code sketches
- Documentation (4 files)
- Task assignment (3 agents)

→ **Ready for:**
- Agent review & approval
- Phase 1 execution (parallel)
- Phase 2 execution (parallel)
- Phase 3 execution (parallel)
- Phase 4 testing & validation
- Commit & merge to main

---

## Questions & Support

**Architecture Questions:**
→ See `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md`

**Quick Setup Issues:**
→ See `/docs/reference/PHASE_5_3_5_5_QUICK_REFERENCE.md`

**Implementation Details:**
→ See `/docs/guides/PHASE_5_3_5_5_CODE_IMPLEMENTATION.md`

**Task Status:**
→ Check Task #6, #7, #8 in task list

---

## Sign-Off

**Architecture Phase:** ✅ COMPLETE
**Documentation:** ✅ 4 FILES, 2,700+ LINES
**Code Sketches:** ✅ READY TO COPY
**Task Assignment:** ✅ 3 AGENTS ASSIGNED
**Timeline Estimate:** ✅ 40-60 MIN WALL-CLOCK

**Status:** READY FOR IMPLEMENTATION HANDOFF

---

**Prepared by:** integration-tests-architect
**Date:** 2026-02-05
**For:** Phase 5.3-5.5 Implementation Team
