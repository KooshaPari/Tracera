# Phase 5.3-5.5 Quick Reference

**Dates:** 2026-02-05
**Status:** READY FOR IMPLEMENTATION
**Total Tests:** 15 (8 + 1 + 6)
**Estimated Time:** 40-60 min with 3 parallel agents

---

## At-a-Glance Summary

| Gap | Issue | Fix | File Count | Lines |
|-----|-------|-----|-----------|-------|
| **5.3** | 8 skipped integration tests | MSW handlers + fixtures + cleanup | 4 files | ~200 |
| **5.4** | 1 skipped temporal workflow | Add activities + workflows + tests | 3 files | ~300 |
| **5.5** | 6 skipped accessibility tests | Table test data + fixtures | 2 files | ~100 |
| **TOTAL** | 15 skipped tests | Close all gaps | 9 files | ~600 |

---

## Gap 5.3: Frontend Integration Tests

### Files to Modify

```
frontend/apps/web/src/__tests__/
├── mocks/
│   ├── handlers.ts          [+reports, +search endpoints]
│   └── data.ts              [+mockReports, +mockSearchResults]
├── setup.ts                 [+global MSW/store cleanup]
├── helpers/
│   └── async-test-helpers.ts [NEW - clearAllStores() + helpers]
└── integration/
    └── app-integration.test.tsx [replace 8 it.skip() with it()]
```

### Quick Checklist

- [ ] Add `/api/v1/reports/templates` to handlers.ts
- [ ] Add `/api/v1/search` to handlers.ts
- [ ] Add `/api/v1/reports/export` to handlers.ts
- [ ] Extend mockData with 3+ projects + reports data
- [ ] Create clearAllStores() helper
- [ ] Add MSW teardown in setup.ts
- [ ] Replace 8 `it.skip()` → `it()`
- [ ] Run: `npm test -- app-integration.test.tsx`
- [ ] Verify: All 8 tests pass, 0 flakes (run 5x)

### Key Functions

```typescript
// helpers/async-test-helpers.ts
export async function clearAllStores() { /* reset all zustand */ }
export function clearMSW() { /* localStorage + mocks */ }
export async function waitForLoadingState() { /* wait for skeleton */ }
export async function waitForNoLoadingState() { /* wait for data */ }
```

### Test Data Needs

```typescript
mockReports = [
  { id: 'coverage', name: 'Coverage Report', formats: ['PDF', 'CSV'] },
  { id: 'status', name: 'Status Report', formats: ['PDF', 'HTML'] },
  { id: 'export', name: 'Items Export', formats: ['CSV', 'JSON'] },
]

mockSearchResults = mockItems.filter(...)
```

---

## Gap 5.4: Temporal Snapshot Workflow

### Files to Create/Modify

```
backend/internal/temporal/
├── activities.go            [NEW - SnapshotActivities]
├── workflows.go             [NEW - SnapshotWorkflow]
└── diff_service.go          [existing, no changes]

backend/tests/integration/
└── test_minio_snapshots.py  [uncomment test + add fixture]

backend/internal/services/
└── service.go               [register workflow + activities]
```

### Quick Checklist

- [ ] Create activities.go with 3 activities:
  - QuerySnapshot(sessionID) → SnapshotPayload
  - CreateSnapshot(payload) → []byte (tarball)
  - UploadSnapshot(sessionID, data) → string (S3 key)
- [ ] Create workflows.go with SnapshotWorkflow
  - Chain: QuerySnapshot → CreateSnapshot → UploadSnapshot
  - Add retry policies (2-3 retries per activity)
- [ ] Add Temporal test setup (test server + worker)
- [ ] Register activities/workflows in service.go
- [ ] Run: `make test-backend TEST_TEMPORAL=1 -k snapshot`
- [ ] Verify: 1 test passes, MinIO objects created

### Activity Signatures

```go
func (a *SnapshotActivities) QuerySnapshot(ctx context.Context, sessionID string) (*SnapshotPayload, error)
func (a *SnapshotActivities) CreateSnapshot(ctx context.Context, payload *SnapshotPayload) ([]byte, error)
func (a *SnapshotActivities) UploadSnapshot(ctx context.Context, sessionID string, data []byte) (string, error)
```

### Temporal Pattern

```go
// In workflow
var result SnapshotPayload
err := workflow.ExecuteActivity(ctx, activities.QuerySnapshot, sessionID).Get(ctx, &result)
// Handle err
// Chain next activity with result...
```

---

## Gap 5.5: E2E Accessibility Tests

### Files to Modify

```
frontend/apps/web/e2e/
├── fixtures/
│   ├── testData.ts          [+tableTestItems (7+ rows)]
│   └── api-mocks.ts         [extend items endpoint]
└── table-accessibility.a11y.spec.ts [replace 6 test.skip() with test()]
```

### Quick Checklist

- [ ] Add 7+ test items to testData.ts (tableTestItems)
- [ ] Items must have: id, title, status, priority, type
- [ ] Extend api-mocks.ts to return all 7+ items
- [ ] Add beforeEach waitFor to ensure rows render
- [ ] Replace 6 `test.skip()` → `test()`
- [ ] Run: `npx playwright test table-accessibility.a11y.spec.ts`
- [ ] Verify: All 6 tests pass, keyboard navigation works
- [ ] Bonus: Add axe scan (WCAG 2.1 AA check)

### Test Item Template

```typescript
{
  id: 'tbl-item-N',
  title: 'Item Title',
  description: 'Item description',
  type: 'requirement' | 'feature' | 'test' | 'bug' | 'doc',
  status: 'todo' | 'in_progress' | 'done',
  priority: 'high' | 'medium' | 'low',
  projectId: 'test-proj-1',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
}
```

### Keyboard Tests

```
Test 1: Arrow Up/Down (rows.length >= 3)
Test 2: Home key (cells.length > 0)
Test 3: End key (cells.length > 0)
Test 4: Ctrl+Home (rows.length >= 2)
Test 5: Ctrl+End (rows.length >= 2)
Test 6: PageUp (rows.length >= 7)
```

---

## Implementation Order

### Phase 1 (Parallel - 10-15 min)

```bash
# Agent 1: Gap 5.3 handlers & data
cd frontend/apps/web/src/__tests__
# Edit: mocks/handlers.ts, mocks/data.ts

# Agent 2: Gap 5.4 activities
cd backend/internal/temporal
# Create: activities.go

# Agent 3: Gap 5.5 test data
cd frontend/apps/web/e2e/fixtures
# Edit: testData.ts
```

### Phase 2 (Parallel - 10-15 min)

```bash
# Agent 1: Gap 5.3 cleanup & helpers
# Edit: setup.ts, create helpers/async-test-helpers.ts

# Agent 2: Gap 5.4 workflows
# Create: workflows.go

# Agent 3: Gap 5.5 API mocks & fixtures
# Edit: api-mocks.ts, table-accessibility.a11y.spec.ts (beforeEach)
```

### Phase 3 (Parallel - 5-10 min)

```bash
# Agent 1: Gap 5.3 re-enable tests
# Edit: app-integration.test.tsx (8 it.skip → it)

# Agent 2: Gap 5.4 test setup & integration
# Add test fixture, register in service.go

# Agent 3: Gap 5.5 re-enable tests
# Edit: table-accessibility.a11y.spec.ts (6 test.skip → test)
```

### Phase 4: Testing & Validation (10 min)

```bash
# Run all tests
npm test -- app-integration.test.tsx        # Gap 5.3
make test-backend TEST_TEMPORAL=1           # Gap 5.4
npx playwright test table-accessibility.a11y.spec.ts  # Gap 5.5

# Verify results
# - 8 + 1 + 6 = 15 tests passing ✓
# - No flakes (run 5x) ✓
# - Coverage maintained ✓
```

---

## Parallel Agent Tasks

### Agent 1: Frontend Integration Tests (Gap 5.3)

**Responsibility:** Handlers, fixtures, cleanup, re-enable
**Files:** 4 (handlers.ts, data.ts, setup.ts, async-test-helpers.ts, app-integration.test.tsx)
**Complexity:** Medium
**Time:** ~20 min

**Subtasks:**
1. Extend handlers.ts (reports + search endpoints)
2. Extend data.ts (mockReports + search results)
3. Add cleanup to setup.ts
4. Create async-test-helpers.ts
5. Replace 8 it.skip → it

**Validation:**
```bash
npm test -- app-integration.test.tsx --reporter=verbose
# Expected: 8 passing, 0 failing, 0 flakes
```

---

### Agent 2: Temporal Snapshot Workflow (Gap 5.4)

**Responsibility:** Activities, workflows, test setup, service integration
**Files:** 3 (activities.go, workflows.go, test_minio_snapshots.py, service.go)
**Complexity:** High (Temporal + Go + Python)
**Time:** ~30 min

**Subtasks:**
1. Create activities.go (QuerySnapshot, CreateSnapshot, UploadSnapshot)
2. Create workflows.go (SnapshotWorkflow with retries)
3. Add Temporal test fixture to test_minio_snapshots.py
4. Register workflow + activities in service.go
5. Run & validate

**Validation:**
```bash
make test-backend TEST_TEMPORAL=1 -k test_scheduled_snapshot_workflow
# Expected: 1 passing, MinIO objects created
```

---

### Agent 3: E2E Accessibility Tests (Gap 5.5)

**Responsibility:** Test data, fixtures, re-enable tests, accessibility validation
**Files:** 3 (testData.ts, api-mocks.ts, table-accessibility.a11y.spec.ts)
**Complexity:** Medium
**Time:** ~20 min

**Subtasks:**
1. Add tableTestItems (7+ rows) to testData.ts
2. Extend api-mocks.ts to return all items
3. Update beforeEach to wait for rows
4. Replace 6 test.skip → test
5. Run & validate with axe

**Validation:**
```bash
npx playwright test table-accessibility.a11y.spec.ts
# Expected: 6 passing, keyboard navigation works
```

---

## Common Pitfalls & Solutions

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| **MSW handler ordering** | Tests sometimes pass, sometimes fail | Put specific routes BEFORE wildcards; use exact URL matching |
| **Store contamination** | Test 1 passes alone, fails with others | Add proper afterEach cleanup with getState() reset |
| **Async timing** | waitFor() times out | Add explicit waits for all async operations (table rows, skeletons) |
| **Temporal test env missing** | "Temporal client not found" error | Use Temporal test server package; mock if unavailable |
| **Table data too small** | Accessibility tests still skip | Need minimum 7 rows; hardcode count in fixture |
| **Focus management** | Focus visible tests fail | Verify ARIA roles + focus indicators on grid cells |

---

## Commands Reference

```bash
# Gap 5.3: Run integration tests
npm test -- app-integration.test.tsx --run
npm test -- app-integration.test.tsx --watch  # TDD mode

# Gap 5.4: Run temporal + snapshot tests
make test-backend                  # All backend tests
make test-backend TEST_TEMPORAL=1  # Only Temporal tests
make test-backend -k snapshot      # Only snapshot tests

# Gap 5.5: Run accessibility tests
npx playwright test table-accessibility.a11y.spec.ts
npx playwright test table-accessibility.a11y.spec.ts --headed  # With browser

# Combined validation
npm test -- app-integration.test.tsx &&
  make test-backend TEST_TEMPORAL=1 -k snapshot &&
  npx playwright test table-accessibility.a11y.spec.ts

# Check coverage
npm test -- --coverage
```

---

## Success Criteria

### Gap 5.3: ✓ All 8 Tests Passing
- [ ] Test 370: maintain recent projects list
- [ ] Test 715: show loading state
- [ ] Test 730: render reports templates
- [ ] Test 744: allow format selection
- [ ] Test 761: generate report on button click
- [ ] Test 852: perform search on input
- [ ] Test 876: show no results message
- [ ] Test 1006: handle offline-to-online sync

### Gap 5.4: ✓ Snapshot Workflow Working
- [ ] test_scheduled_snapshot_workflow passing
- [ ] Snapshot tarball created correctly
- [ ] MinIO upload verified
- [ ] Session metadata updated with S3 key
- [ ] Retry policies working

### Gap 5.5: ✓ All 6 Accessibility Tests Passing
- [ ] Test 60: Arrow key up/down navigation
- [ ] Test 82: Home key navigation
- [ ] Test 101: End key navigation
- [ ] Test 118: Ctrl+Home navigation
- [ ] Test 139: Ctrl+End navigation
- [ ] Test 157: PageUp navigation
- [ ] WCAG 2.1 AA compliance verified

### Final: ✓ 15/15 Tests Passing
- [ ] Gap 5.3: 8/8 ✓
- [ ] Gap 5.4: 1/1 ✓
- [ ] Gap 5.5: 6/6 ✓
- [ ] No flakes (5x run each gap)
- [ ] Coverage maintained (85%+)

---

## Resources

**Full Plan:** `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md`
**MSW Docs:** https://mswjs.io/docs/api/setup-server
**Temporal Go SDK:** https://pkg.go.dev/go.temporal.io/sdk
**Playwright Axe:** https://github.com/dequelabs/axe-core-npm/tree/develop/packages/playwright

---

## Handoff Notes

- **Start:** Phase 1 (parallel agents on 3 gaps)
- **Sync:** After Phase 2 to unblock Phase 3 dependencies
- **Validate:** Run all tests in Phase 4
- **Report:** 15/15 passing = Phase 5.3-5.5 complete
- **Next:** Commit to main, merge to production

**Estimated Wall-Clock:** 40-60 minutes total
**Recommended:** Start all 3 agents in parallel, regroup after Phase 2
