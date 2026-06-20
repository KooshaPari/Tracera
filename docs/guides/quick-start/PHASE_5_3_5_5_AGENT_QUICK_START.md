# Phase 5.3-5.5 Agent Quick Start

**Format:** Quick reference for parallel agent execution
**Date:** 2026-02-05
**Est. Time:** 45-90 min (parallel execution)

---

## Agent Assignment

Choose ONE of the following tasks:

### Task #9: Gap 5.3 - Frontend Integration Tests (8 tests)
**File:** `Task #6` (tracking) + `Task #9` (your assignment)
**Est. Duration:** 60-90 minutes
**Parallelization:** Independent (no dependencies on other gaps)

### Task #10: Gap 5.4 - Temporal Snapshot Workflow (1 test)
**File:** `Task #7` (tracking) + `Task #10` (your assignment)
**Est. Duration:** 45-60 minutes
**Parallelization:** Independent (no dependencies on other gaps)

### Task #11: Gap 5.5 - E2E Accessibility Tests (6 tests)
**File:** `Task #8` (tracking) + `Task #11` (your assignment)
**Est. Duration:** 30-45 minutes
**Parallelization:** Independent (no dependencies on other gaps)

---

## Quick Reference: Each Gap at a Glance

### Gap 5.3: Frontend Integration Tests

```
Step 1: handlers.ts       → Add 3 endpoints (templates, search, export)
Step 2: data.ts           → Add fixtures (projects, reports, items)
Step 3: setup.ts          → Add cleanup (stores, localStorage, React Query)
Step 4: async-test-helpers.ts → Create waitFor utilities
Step 5: app-integration.test.tsx → Replace it.skip() with it() (8 tests)
```

**Files to Edit:**
- `frontend/apps/web/src/__tests__/mocks/handlers.ts`
- `frontend/apps/web/src/__tests__/mocks/data.ts`
- `frontend/apps/web/src/__tests__/setup.ts`
- `frontend/apps/web/src/__tests__/integration/app-integration.test.tsx`
- `frontend/apps/web/src/__tests__/helpers/async-test-helpers.ts` (NEW)

**Validation:**
```bash
# Run with timeout to catch async issues
bun test -- app-integration.test.tsx --reporter=verbose --bail

# Run 5x to detect flakes
for i in {1..5}; do bun test -- app-integration.test.tsx; done

# Check coverage
bun test -- app-integration.test.tsx --coverage
```

**Success:** 8/8 tests passing, 5x runs without flakes, ≥85% coverage

---

### Gap 5.4: Temporal Snapshot Workflow

```
Step 1: activities.go       → QuerySnapshot, CreateSnapshot, UploadSnapshot
Step 2: workflows.go        → SnapshotWorkflow with activities + retry policies
Step 3: test_minio_snapshots.py → Add temporal_worker fixture + test setup
Step 4: service.go          → Register activities & workflows
Step 5: test_scheduled_snapshot_workflow → Run test & verify
```

**Files to Edit/Create:**
- `backend/internal/temporal/activities.go` (NEW)
- `backend/internal/temporal/workflows.go` (NEW)
- `backend/tests/integration/test_minio_snapshots.py`
- `backend/internal/services/service.go`

**Validation:**
```bash
# Run with Temporal test server
make test-backend TEST_TEMPORAL=1 -k test_scheduled_snapshot_workflow

# Verify MinIO integration
docker logs tracertm-minio | grep "snapshot"

# Check workflow logs
tctl workflow show -w <workflow-id>
```

**Success:** 1/1 test passing, MinIO object created, session metadata updated

---

### Gap 5.5: E2E Accessibility Tests

```
Step 1: testData.ts           → Add tableTestItems (7+ items)
Step 2: api-mocks.ts          → Add GET /api/v1/items handler
Step 3: table-accessibility.a11y.spec.ts → Replace test.skip() with test() (6 tests)
Step 4: Validate WCAG 2.1 AA  → Run axe-core compliance check
```

**Files to Edit:**
- `frontend/apps/web/e2e/fixtures/testData.ts`
- `frontend/apps/web/e2e/fixtures/api-mocks.ts`
- `frontend/apps/web/e2e/table-accessibility.a11y.spec.ts`

**Validation:**
```bash
# Run accessibility suite
npx playwright test table-accessibility.a11y.spec.ts

# Generate accessibility report
npx playwright test table-accessibility.a11y.spec.ts --reporter=html

# Manual axe check
npx axe http://localhost:5173/items
```

**Success:** 6/6 tests passing, WCAG 2.1 AA compliant (0 violations)

---

## Code Sketches

**Full code sketches available in:**
`/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md` (lines 420-651)

Quick copy-paste templates:

### Gap 5.3 - MSW Handlers Template
```typescript
// handlers.ts additions
http.get(`${API_BASE}/api/v1/reports/templates`, () =>
  HttpResponse.json({
    templates: [
      { id: 'coverage', name: 'Coverage Report', formats: ['PDF', 'CSV'] },
      { id: 'status', name: 'Status Report', formats: ['PDF', 'HTML'] },
    ],
  })
),

http.get(`${API_BASE}/api/v1/search`, ({ request }) => {
  const url = new URL(request.url)
  const q = url.searchParams.get('q') ?? ''
  const filtered = mockItems.filter(item =>
    item.title.toLowerCase().includes(q.toLowerCase())
  )
  return HttpResponse.json({
    results: filtered,
    total: filtered.length,
  })
}),
```

### Gap 5.4 - Activities Template
```go
type SnapshotActivities struct {
    db         *sql.DB
    neo4j      neo4j.Driver
    minio      *minio.Client
    logger     *zap.Logger
}

func (a *SnapshotActivities) QuerySnapshot(
  ctx context.Context,
  sessionID string,
) (*SnapshotPayload, error) {
  // Query PostgreSQL + Neo4j
  return &SnapshotPayload{
    SessionID: sessionID,
    Timestamp: time.Now(),
  }, nil
}
```

### Gap 5.5 - Table Test Data Template
```typescript
export const tableTestItems: Item[] = [
  {
    id: 'tbl-item-1',
    title: 'System Requirements',
    type: 'requirement',
    status: 'done',
    priority: 'high',
    projectId: 'test-proj-1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  // ... items 2-7 with varying types/status/priority
]
```

---

## Execution Checklist

### Before Starting
- [ ] Read assigned task description
- [ ] Understand success criteria
- [ ] Review code sketches in implementation plan
- [ ] Verify dev environment is running (`make dev`)

### During Implementation
- [ ] Follow step-by-step instructions
- [ ] Copy code sketches and adapt as needed
- [ ] Run validation commands after each step
- [ ] Address failures immediately (don't skip)

### After Implementation
- [ ] Run full test suite for your gap
- [ ] Verify success criteria met
- [ ] Run tests 5x in succession (no flakes)
- [ ] Check coverage maintained ≥85%
- [ ] Create comprehensive commit message

### Commit Message Format
```
feat(gap-5.X): close gap 5.X - X tests + description

- Test 1: detail
- Test 2: detail
- Implementation: changes
- Coverage: X%

Tests: X/X passing (5x runs)
```

---

## Support Resources

**Master Plan:** `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md` (742 lines)
- Full architecture
- Code sketches
- Risk mitigation
- Testing strategy

**Orchestration Guide:** `/PHASE_5_3_5_5_ORCHESTRATION.md`
- Team coordination
- Task routing
- Timeline
- Success metrics

**This Quick Start:** `/docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md`

---

## Success Metrics

| Metric | Target | Your Task |
|--------|--------|-----------|
| **Tests Passing** | 8/8 or 1/1 or 6/6 | ✅ All pass |
| **Flakes** | 0 (5x runs) | ✅ 5 consecutive passes |
| **Coverage** | ≥85% | ✅ Check before commit |
| **Commit Quality** | Detailed message | ✅ Include test logs |

---

## Next Steps

1. **Claim Task:** Update TaskUpdate to set owner = your name
2. **Begin Step 1:** Follow checklist for your assigned gap
3. **Report Progress:** Send message when each step completes
4. **Submit Results:** Commit to branch with comprehensive logs

**Questions?** Ask in team channel or check master plan.

Good luck! You've got this! 🚀
