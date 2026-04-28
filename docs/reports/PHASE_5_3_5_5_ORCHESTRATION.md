# Phase 5.3-5.5 Implementation Orchestration

**Date:** 2026-02-05
**Status:** Task Delegation Complete - Awaiting Agent Execution
**Coordinator:** integration-tests-implementer
**Plan Reference:** `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md`

---

## Executive Summary

Delegated 3 parallel implementation streams for closing Phase 5 gaps 5.3-5.5 (15 tests total):

| Gap | Tests | Status | Task IDs | Est. Time |
|-----|-------|--------|----------|-----------|
| **5.3** - Frontend Integration | 8 | Assigned | #6, #9 | 60-90 min |
| **5.4** - Temporal Snapshots | 1 | Assigned | #7, #10 | 45-60 min |
| **5.5** - E2E Accessibility | 6 | Assigned | #8, #11 | 30-45 min |
| **TOTAL** | **15** | **Parallel** | **6 tasks** | **45-90 min** |

---

## Task Assignment & Routing

### Broadcast Message Sent
✅ All teammates notified via broadcast at 2026-02-05 (team-lead, visual-regression-architect, integration-tests-architect, api-performance-architect, visual-regression-implementer)

### Task Delegation Strategy
**3 agent assignments created:**
- **Task #9:** general-purpose agent → Gap 5.3 (Frontend Integration)
- **Task #10:** general-purpose agent → Gap 5.4 (Temporal Snapshot)
- **Task #11:** general-purpose agent → Gap 5.5 (E2E Accessibility)

**Key:** Agents self-assign from available tasks and report progress via messaging.

---

## Gap 5.3: Frontend Integration Tests (8 tests)

**Files Modified:**
```
frontend/apps/web/src/__tests__/
├── mocks/handlers.ts              (add 3 endpoints)
├── mocks/data.ts                  (extend fixtures)
├── setup.ts                        (add cleanup)
├── helpers/async-test-helpers.ts  (NEW file)
└── integration/app-integration.test.tsx (re-enable 8 tests)
```

**Key Changes:**
1. **handlers.ts:** Add `/api/v1/reports/templates`, `/api/v1/search`, `/api/v1/reports/export`
2. **data.ts:** Add mockProjects (≥5), mockReports (4 templates), mockSearchResults
3. **setup.ts:** Add store resets, localStorage clear, React Query cache clear, MSW teardown
4. **async-test-helpers.ts:** Utilities for waitForLoadingState, waitForElement, clearAllStores
5. **app-integration.test.tsx:** Replace `it.skip()` with `it()` for 8 tests

**Acceptance Criteria:**
- ✅ 8/8 tests passing
- ✅ 5x consecutive runs without flakes
- ✅ Coverage ≥85%
- ✅ No cross-test contamination

**Code Sketches:** Lines 423-509 in implementation plan

---

## Gap 5.4: Temporal Snapshot Workflow (1 test)

**Files Created/Modified:**
```
backend/
├── internal/temporal/
│   ├── activities.go              (NEW file)
│   └── workflows.go               (NEW file)
├── internal/services/service.go   (wire integration)
└── tests/integration/
    └── test_minio_snapshots.py    (add temporal_worker fixture)
```

**Key Changes:**
1. **activities.go:** Create SnapshotActivities with QuerySnapshot, CreateSnapshot, UploadSnapshot
2. **workflows.go:** Create SnapshotWorkflow with activity chaining and retry policies
3. **test_minio_snapshots.py:** Add Temporal test server setup and temporal_worker fixture
4. **test_minio_snapshots.py:** Implement test_scheduled_snapshot_workflow
5. **service.go:** Register activities and workflows, set up periodic trigger

**Acceptance Criteria:**
- ✅ 1/1 test passing
- ✅ Workflow executes without errors
- ✅ MinIO object created (>0 bytes)
- ✅ Session metadata updated with S3 key

**Code Sketches:** Lines 511-621 in implementation plan

---

## Gap 5.5: E2E Accessibility Tests (6 tests)

**Files Modified:**
```
frontend/apps/web/e2e/
├── fixtures/testData.ts           (add tableTestItems)
├── fixtures/api-mocks.ts          (add GET /api/v1/items handler)
└── table-accessibility.a11y.spec.ts (re-enable 6 tests)
```

**Key Changes:**
1. **testData.ts:** Add tableTestItems array (7+ items with varied types/status/priority)
2. **api-mocks.ts:** Add handler for `/api/v1/items?projectId=...` returning tableTestItems
3. **table-accessibility.a11y.spec.ts:** Replace `test.skip()` with `test()` for 6 tests
4. **Validation:** Verify WCAG 2.1 AA compliance with axe-core
5. **Keyboard Nav:** Test Arrow, Home, End, Ctrl+Home, Ctrl+End, PageUp navigation

**Acceptance Criteria:**
- ✅ 6/6 tests passing
- ✅ 7+ data rows consistently rendered
- ✅ WCAG 2.1 AA compliant (0 violations)
- ✅ Keyboard navigation verified
- ✅ Screen reader roles correct

**Code Sketches:** Lines 623-651 in implementation plan

---

## Execution Timeline

### Phase 1: Initial Setup (T+5 min)
- Agents claim tasks #9, #10, #11
- Begin Gap 5.3 Step 1 (MSW handlers)
- Begin Gap 5.4 Step 1 (activities.go)
- Begin Gap 5.5 Step 1 (test data)

### Phase 2: Parallel Execution (T+5-50 min)
- **Gap 5.3:** Steps 1-4 complete (MSW, data, setup, helpers)
- **Gap 5.4:** Steps 1-2 complete (activities, workflows)
- **Gap 5.5:** Steps 1-2 complete (data, handlers)

### Phase 3: Integration & Testing (T+50-80 min)
- **Gap 5.3:** Step 5 - Re-enable tests + 5x verification
- **Gap 5.4:** Steps 3-4 - Temporal setup + service integration
- **Gap 5.5:** Steps 3-4 - Fixture setup + test re-enable

### Phase 4: Validation & Commit (T+80-90 min)
- All agents run final test suites
- Verify success criteria met
- Create comprehensive commits with test output

---

## Success Metrics

**Overall Pass Rate:** 15/15 tests passing (100%)
- Gap 5.3: 8/8 integration tests
- Gap 5.4: 1/1 temporal snapshot test
- Gap 5.5: 6/6 E2E accessibility tests

**Quality Standards:**
- No flakes: All tests pass 5x in succession
- Coverage: ≥85% maintained across all changes
- Compliance: WCAG 2.1 AA (Gap 5.5)
- Documentation: Comprehensive commit messages with test logs

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| MSW handler ordering | Medium | High | Test handlers independently; use specific route matching |
| Store contamination | High | High | Comprehensive afterEach cleanup in setup.ts |
| Temporal test env unavailable | Low | Critical | Use Temporal test server package; mock if needed |
| Async race conditions | High | Medium | Explicit waits for all async operations |
| WCAG compliance failures | Low | Low | Pre-run axe checks; address violations before commit |
| Flaky tests | Medium | High | 5x verification runs; add retries where appropriate |

---

## Deliverables

**Code Changes:**
- 5 new/modified frontend files (Gap 5.3)
- 3 new/modified backend files (Gap 5.4)
- 3 modified E2E files (Gap 5.5)

**Commits:**
- Gap 5.3: "feat(integration-tests): close gap 5.3 - 8 integration tests + MSW handlers"
- Gap 5.4: "feat(temporal): close gap 5.4 - snapshot workflow + activities"
- Gap 5.5: "feat(e2e-a11y): close gap 5.5 - table accessibility tests + WCAG validation"

**Documentation:**
- Test execution logs (all 15 tests passing)
- Coverage reports (≥85%)
- WCAG compliance audit report
- Temporal workflow logs

---

## Team Lead Checkpoint

**Before Implementation:**
- [ ] Review architectural plan at `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md`
- [ ] Approve task delegation strategy
- [ ] Confirm 3 agents available for parallel execution

**During Execution:**
- Monitor task progress via TaskList
- Watch for cross-gap dependencies (none expected)
- Address blockers immediately

**After Execution:**
- Verify all 15 tests passing
- Review commits before merge
- Celebrate Phase 5 completion!

---

**Next Step:** Agents claim tasks and begin implementation.
**Estimated Completion:** 2026-02-05 (45-90 min from task assignment)
