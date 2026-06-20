# Phase 5.3-5.5 Implementation Plan

**Date:** 2026-02-05
**Status:** ARCHITECTURE & PLANNING
**Target:** Close 3 major gaps (15 tests total)

---

## Executive Summary

This plan addresses 3 critical gaps in the Phase 5 testing initiative:

1. **Gap 5.3:** 8 skipped integration tests (frontend)
2. **Gap 5.4:** 1 skipped temporal snapshot test (backend)
3. **Gap 5.5:** 6 skipped accessibility tests (E2E)

**Total Impact:** 15 tests → ~300-400 LOC changes across frontend, backend, and E2E

---

## Gap 5.3: Frontend Integration Tests (8 Tests)

### Problem Analysis

**Skipped Tests (file: `frontend/apps/web/src/__tests__/integration/app-integration.test.tsx`):**

1. **Line 370:** `maintain recent projects list` - ProjectStore integration
2. **Line 715:** `show loading state` - DashboardView async rendering
3. **Line 730:** `render reports templates` - ReportsView templates
4. **Line 744:** `allow format selection` - Report format selection UI
5. **Line 761:** `generate report on button click` - Export/report generation
6. **Line 852:** `perform search on input` - SearchView integration
7. **Line 876:** `show no results message` - Search empty state
8. **Line 1006:** `handle offline-to-online sync` - SyncStore reconnection

**Root Causes:**

| Issue | Impact | Scope |
|-------|--------|-------|
| **MSW Handlers Missing** | ReportsView, SearchView endpoints undefined | `handlers.ts` |
| **Store Contamination** | Tests fail due to leftover state | Global teardown missing |
| **Incomplete Test Data** | ReportsView needs projects + items | `mocks/data.ts` |
| **Async Timing** | waitFor() not catching all states | Test utilities |

### Architecture

```
Test Flow:
  1. Test Setup (beforeEach)
     ├─ Clear stores (projectStore, itemsStore, syncStore)
     ├─ Initialize MSW server
     └─ Set auth token

  2. Test Execution
     ├─ Render component with providers
     ├─ Mock API calls
     └─ Verify UI state

  3. Cleanup (afterEach)
     ├─ Reset MSW handlers
     ├─ Clear localStorage
     └─ Cleanup React Query cache
```

### Implementation Plan

**Phase 1: MSW Handler Extensions** (Files: `handlers.ts`)
- Add `/api/v1/reports/templates` endpoint
- Add `/api/v1/search` endpoint with query params
- Add `/api/v1/reports/export` endpoint
- Handler ordering: specific routes before wildcards

**Phase 2: Test Data Fixtures** (Files: `data.ts`)
- Extend mockProjects with 3+ projects
- Add mockReports (Coverage, Status, Export templates)
- Add search results data (mockSearchResults)
- Add test items for each project

**Phase 3: Global Cleanup** (Files: `setup.ts`)
- Add MSW server teardown
- Add store.getState() reset for all zustand stores
- Add localStorage cleanup
- Add React Query cache clear

**Phase 4: Test Utilities** (New file: `helpers/async-test-helpers.ts`)
```typescript
// Utilities for async test scenarios
export async function waitForLoadingState(screen, ms = 100)
export async function waitForNoLoadingState(screen)
export async function waitForElement(screen, text, timeout = 1000)
export async function clearAllStores()
```

**Phase 5: Re-enable Tests** (File: `app-integration.test.tsx`)
- Replace `it.skip()` with `it()`
- Update tests with proper async/await
- Add data assertions (not just presence)

### Dependencies

```
MSW Handlers → Test Data → Global Cleanup → Test Utilities → Re-enable Tests
```

### Acceptance Criteria

- ✓ All 8 tests passing consistently (5x run without flakes)
- ✓ No cross-test contamination (isolated state)
- ✓ Each test verifies both rendering AND data flow
- ✓ Coverage maintained at 85%+

---

## Gap 5.4: Temporal Snapshot Workflow (1 Test)

### Problem Analysis

**Skipped Test (file: `backend/tests/integration/test_minio_snapshots.py:218`):**
- `test_scheduled_snapshot_workflow`
- Reason: "Requires Temporal test environment"

**Current State:**
- MinIO integration exists (✓ `test_snapshot_upload_download` passing)
- Temporal client registered in main service
- No snapshot workflow defined
- No snapshot activities defined

**Root Causes:**

| Component | Status | Issue |
|-----------|--------|-------|
| **workflows.go** | ✗ Missing | No snapshot creation workflow |
| **activities.go** | ✗ Missing | No MinIO activities |
| **Temporal tests** | ✗ Missing | No test setup/fixtures |
| **MinIO client** | ✓ Ready | Already integrated |

### Architecture

```
Temporal Workflow Design:

SnapshotWorkflow (periodic trigger every 1h or on-demand)
├─ QuerySnapshot Activity
│  ├─ Query project state from Neo4j
│  ├─ Query items from PostgreSQL
│  └─ Return snapshot payload
├─ CreateSnapshot Activity
│  ├─ Serialize to tarball
│  ├─ Compress with gzip
│  └─ Return tarball bytes
└─ UploadSnapshot Activity
   ├─ Upload to MinIO
   ├─ Update session metadata
   └─ Return S3 key

Activity Retry Policies:
- QuerySnapshot: 2 retries, 5s backoff
- CreateSnapshot: 1 retry, 10s backoff
- UploadSnapshot: 3 retries, 2s exponential

Data Flow:
  Project State → Serialization → Compression → Upload → Metadata Store
```

### Implementation Plan

**Phase 1: Activities** (New file: `backend/internal/temporal/activities.go`)

```go
type SnapshotActivities struct {
    db         *sql.DB
    neo4j      neo4j.Driver
    minio      *minio.Client
    logger     *zap.Logger
}

// Activity 1: Query snapshot state
QuerySnapshot(ctx context.Context, sessionID string) (*SnapshotPayload, error)

// Activity 2: Create tarball
CreateSnapshot(ctx context.Context, payload *SnapshotPayload) ([]byte, error)

// Activity 3: Upload to MinIO
UploadSnapshot(ctx context.Context, sessionID string, data []byte) (string, error)
```

**Phase 2: Workflows** (New file: `backend/internal/temporal/workflows.go`)

```go
func SnapshotWorkflow(ctx workflow.Context, req SnapshotRequest) (SnapshotResult, error)
    // Execute activities with retry policies
    // Chain: QuerySnapshot → CreateSnapshot → UploadSnapshot
    // Update session metadata with S3 key
```

**Phase 3: Test Setup** (Extend `test_minio_snapshots.py`)

```python
# Fixture: Temporal test server
@pytest.fixture
def temporal_worker():
    # Setup test server
    # Register workflows + activities
    # Start worker thread
    # Yield for test
    # Cleanup

# Test: Snapshot workflow execution
async def test_scheduled_snapshot_workflow(temporal_worker, minio_clean):
    # Start workflow
    # Wait for completion
    # Verify MinIO upload
    # Verify metadata
```

**Phase 4: Integration** (Update: `internal/services/service.go`)
- Register snapshot activities
- Register snapshot workflow
- Set up periodic trigger (scheduler or cron)

### Dependencies

```
Activities.go → Workflows.go → Test Setup → Service Integration
```

### Acceptance Criteria

- ✓ Test passing with Temporal test environment
- ✓ Snapshot tarball created correctly (>0 bytes)
- ✓ MinIO upload verified (object exists)
- ✓ Session metadata updated with S3 key
- ✓ Retry policies working (simulate failures)

---

## Gap 5.5: E2E Accessibility Tests (6 Tests)

### Problem Analysis

**Skipped Tests (file: `frontend/apps/web/e2e/table-accessibility.a11y.spec.ts`):**

Lines with `test.skip()`:
- **Line 60:** Arrow key up/down navigation (needs 3+ rows)
- **Line 82:** Home key navigation (needs cells)
- **Line 101:** End key navigation (needs cells)
- **Line 118:** Ctrl+Home navigation (needs 2+ rows)
- **Line 139:** Ctrl+End navigation (needs 2+ rows)
- **Line 157:** PageUp navigation (needs 7+ rows)

**Root Cause:** No table test data (needs 7+ data rows minimum)

**Current Dependencies:**
- ✓ Playwright + Axe configured
- ✓ Table component has ARIA roles
- ✓ Keyboard event handlers implemented
- ✗ Test fixture data only (no real data rows)

### Architecture

```
Test Data Strategy:

ItemsTable Component
├─ Header Row (ARIA roles correct)
├─ Data Rows (7+ required)
│  ├─ Row 1-7: Different item types
│  ├─ All have: id, title, status, priority
│  └─ Grid cells with role="gridcell"
└─ Footer (pagination, etc.)

Data Fixture (testData.ts):
  testItems: Item[]
    - item-1: requirement, high
    - item-2: feature, medium
    - item-3: test case, low
    - item-4: bug, high
    - item-5: documentation, low
    - item-6: feature, medium
    - item-7: requirement, high

Navigation Tests:
  Arrow keys (Up/Down/Left/Right)
  Home/End (row start/end)
  Ctrl+Home/End (table start/end)
  PageUp/Down (5-row jumps)
```

### Implementation Plan

**Phase 1: Test Data Extension** (File: `e2e/fixtures/testData.ts`)

```typescript
export const tableTestItems = [
  // Need 7+ items for pagination tests
  { id: 'tbl-item-1', title: 'First Item', ... },
  { id: 'tbl-item-2', title: 'Second Item', ... },
  // ... through tbl-item-7
]

export const tableTestData = {
  headers: ['Node ID', 'Title', 'Status', 'Priority'],
  rows: tableTestItems,
}
```

**Phase 2: API Handler Extension** (File: `e2e/fixtures/api-mocks.ts`)

```typescript
// Return table test data with proper structure
route('GET /api/v1/items', ({ request }) => {
  const params = new URL(request.url).searchParams
  const limit = params.get('limit') ?? '10'
  return HttpResponse.json({
    items: tableTestItems.slice(0, parseInt(limit)),
    total: tableTestItems.length,
  })
})
```

**Phase 3: Test Fixture Setup** (Update: `table-accessibility.a11y.spec.ts`)

```typescript
test.beforeEach(async ({ page }) => {
  // Seed test data before navigation
  await page.route('/api/v1/items*', route => {
    route.continue()
  })

  await page.goto('/items')
  await page.waitForLoadState('networkidle')

  // Wait for table rows to render
  await page.locator('[role="row"]').nth(7).waitFor()
})
```

**Phase 4: Re-enable Tests** (File: `table-accessibility.a11y.spec.ts`)
- Replace `test.skip()` with `test()`
- Keep conditional checks for row counts
- Add Axe accessibility checks (separate suite)

**Phase 5: Accessibility Validation** (New test suite)

```typescript
test('table should pass WCAG 2.1 AA with axe', async ({ page }) => {
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2aa'])
    .analyze()

  expect(results.violations).toHaveLength(0)
})
```

### Dependencies

```
Test Data → API Handlers → Fixture Setup → Test Re-enable → A11y Validation
```

### Acceptance Criteria

- ✓ All 6 keyboard navigation tests passing
- ✓ 7+ data rows consistently rendered
- ✓ WCAG 2.1 AA compliance verified (no violations)
- ✓ Screen reader roles correct (table, row, columnheader, gridcell)
- ✓ Focus visible on all navigable elements

---

## Phased Implementation Schedule

### Dependency Graph (DAG)

```
Task 5.3a: MSW Handlers
    ↓
Task 5.3b: Test Data
    ↓
Task 5.3c: Global Cleanup
    ↓
Task 5.3d: Test Helpers
    ↓
Task 5.3e: Re-enable Tests (Gate: all above ✓)

Task 5.4a: Activities.go
    ↓
Task 5.4b: Workflows.go
    ↓
Task 5.4c: Test Setup
    ↓
Task 5.4d: Service Integration
    ↓
Task 5.4e: Run Test (Gate: all above ✓)

Task 5.5a: Table Test Data
    ↓
Task 5.5b: API Handler Extension
    ↓
Task 5.5c: Fixture Setup
    ↓
Task 5.5d: Re-enable Tests
    ↓
Task 5.5e: Accessibility Validation
```

### Implementation Order (Parallel where possible)

| Phase | Tasks | Duration | Priority |
|-------|-------|----------|----------|
| **1** | 5.3a, 5.3b, 5.4a, 5.5a | ~10-15 min | HIGH |
| **2** | 5.3c, 5.3d, 5.4b, 5.5b | ~10-15 min | HIGH |
| **3** | 5.3e, 5.4c, 5.5c | ~5-10 min | HIGH |
| **4** | 5.4d, 5.5d, 5.5e | ~5-10 min | HIGH |
| **5** | Testing & Validation | ~10 min | MEDIUM |

**Total Wall Clock:** ~40-60 minutes with 3 parallel agents

---

## Code Sketches

### 5.3: MSW Handler Extension

```typescript
// handlers.ts additions
import { HttpResponse, http } from 'msw'

export const handlers = [
  // ... existing handlers ...

  // Gap 5.3: Reports endpoint
  http.get(`${API_BASE}/api/v1/reports/templates`, () =>
    HttpResponse.json({
      templates: [
        { id: 'coverage', name: 'Coverage Report', formats: ['PDF', 'CSV'] },
        { id: 'status', name: 'Status Report', formats: ['PDF', 'HTML'] },
        { id: 'export', name: 'Items Export', formats: ['CSV', 'JSON'] },
      ],
    })
  ),

  // Gap 5.3: Search endpoint
  http.get(`${API_BASE}/api/v1/search`, ({ request }) => {
    const url = new URL(request.url)
    const q = url.searchParams.get('q') ?? ''

    const filtered = mockItems.filter(item =>
      item.title.toLowerCase().includes(q.toLowerCase()) ||
      item.description?.toLowerCase().includes(q.toLowerCase())
    )

    return HttpResponse.json({
      results: filtered,
      total: filtered.length,
    })
  }),

  // Gap 5.3: Export endpoint
  http.post(`${API_BASE}/api/v1/reports/export`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      downloadUrl: `blob:http://localhost:4000/abc123`,
      filename: `export-${Date.now()}.${body.format}`,
    })
  }),
]
```

### 5.3: Global Cleanup Helper

```typescript
// helpers/async-test-helpers.ts
import { useAuthStore } from '../../stores/auth-store'
import { useItemsStore } from '../../stores/items-store'
import { useProjectStore } from '../../stores/project-store'
import { useSyncStore } from '../../stores/sync-store'

export async function clearAllStores() {
  // Reset all zustand stores
  useAuthStore.setState({
    user: null,
    isAuthenticated: false,
    token: null,
  })

  useItemsStore.setState({
    items: new Map(),
    pendingDeletes: new Set(),
  })

  useProjectStore.setState({
    currentProject: null,
    currentProjectId: null,
    recentProjects: [],
  })

  useSyncStore.setState({
    isOnline: true,
    pendingMutations: [],
    failedMutations: [],
  })
}

export function clearMSW() {
  localStorage.clear()
  vi.clearAllMocks()
}
```

### 5.4: Temporal Activities

```go
// internal/temporal/activities.go
package temporal

import (
  "context"
  "encoding/json"
  "time"

  "go.temporal.io/sdk/activity"
  "go.uber.org/zap"
)

type SnapshotPayload struct {
  SessionID string                 `json:"session_id"`
  Projects  []map[string]interface{} `json:"projects"`
  Items     []map[string]interface{} `json:"items"`
  Timestamp time.Time              `json:"timestamp"`
}

type SnapshotActivities struct {
  // Inject dependencies
}

// Activity: Query project/item state
func (a *SnapshotActivities) QuerySnapshot(
  ctx context.Context,
  sessionID string,
) (*SnapshotPayload, error) {
  // Query PostgreSQL + Neo4j
  // Return serializable payload
  return &SnapshotPayload{
    SessionID: sessionID,
    Timestamp: time.Now(),
  }, nil
}

// Activity: Create tarball
func (a *SnapshotActivities) CreateSnapshot(
  ctx context.Context,
  payload *SnapshotPayload,
) ([]byte, error) {
  // Serialize to JSON
  // Compress with gzip
  return []byte("tarball_bytes"), nil
}

// Activity: Upload to MinIO
func (a *SnapshotActivities) UploadSnapshot(
  ctx context.Context,
  sessionID string,
  data []byte,
) (string, error) {
  // Upload to MinIO
  // Return S3 key
  return "s3://bucket/snapshots/" + sessionID, nil
}
```

### 5.4: Temporal Workflow

```go
// internal/temporal/workflows.go
package temporal

import (
  "go.temporal.io/sdk/workflow"
  "time"
)

func SnapshotWorkflow(
  ctx workflow.Context,
  sessionID string,
) (string, error) {
  // Retry policies
  ao := workflow.ActivityOptions{
    RetryPolicy: &temporal.RetryPolicy{
      BackoffCoefficient: 2.0,
      MaximumInterval:    time.Second * 10,
      InitialInterval:    time.Second * 2,
    },
    ScheduleToCloseTimeout: time.Minute * 5,
  }
  ctx = workflow.WithActivityOptions(ctx, ao)

  // Execute activities in sequence
  var activities SnapshotActivities
  var payload *SnapshotPayload

  err := workflow.ExecuteActivity(ctx, activities.QuerySnapshot, sessionID).Get(ctx, &payload)
  if err != nil {
    return "", err
  }

  var tarball []byte
  err = workflow.ExecuteActivity(ctx, activities.CreateSnapshot, payload).Get(ctx, &tarball)
  if err != nil {
    return "", err
  }

  var s3Key string
  err = workflow.ExecuteActivity(ctx, activities.UploadSnapshot, sessionID, tarball).Get(ctx, &s3Key)
  if err != nil {
    return "", err
  }

  return s3Key, nil
}
```

### 5.5: Extended Test Data

```typescript
// e2e/fixtures/testData.ts additions
export const tableTestItems: Item[] = [
  {
    id: 'tbl-item-1',
    title: 'System Requirements',
    description: 'Define system requirements',
    type: 'requirement',
    status: 'done',
    priority: 'high',
    projectId: 'test-proj-1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'tbl-item-2',
    title: 'User Authentication',
    description: 'Implement auth module',
    type: 'feature',
    status: 'in_progress',
    priority: 'high',
    projectId: 'test-proj-1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  // ... items 3-7 with varying types/status/priority
]
```

---

## Testing Strategy

### Gap 5.3: Integration Test Validation

```bash
# Run with timeout to catch async issues
npm test -- app-integration.test.tsx --reporter=verbose --bail

# Run 5x to detect flakes
for i in {1..5}; do npm test -- app-integration.test.tsx; done

# Check coverage
npm test -- app-integration.test.tsx --coverage
```

### Gap 5.4: Temporal Test Validation

```bash
# Run with Temporal test server
make test-backend TEST_TEMPORAL=1 -k test_scheduled_snapshot_workflow

# Verify MinIO integration
docker logs tracertm-minio | grep "snapshot"

# Check workflow logs
tctl workflow show -w <workflow-id>
```

### Gap 5.5: Accessibility Test Validation

```bash
# Run accessibility suite
npx playwright test table-accessibility.a11y.spec.ts

# Generate accessibility report
npx playwright test table-accessibility.a11y.spec.ts --reporter=html

# Manual axe check
npx axe http://localhost:5173/items
```

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **MSW handler ordering issues** | Medium | High | Test handlers independently, use specific route matching |
| **Store contamination** | High | High | Implement comprehensive afterEach cleanup |
| **Temporal test environment not available** | Low | Critical | Use Temporal test server package, mock if needed |
| **Table data fixture count** | Low | Medium | Hardcode 10+ items in fixture |
| **Async race conditions** | High | Medium | Add explicit waits for all async operations |
| **WCAG compliance unexpected** | Low | Low | Pre-run axe checks before test run |

---

## Success Metrics

- **Gap 5.3:** 8/8 tests passing, 0 flakes, 85%+ coverage
- **Gap 5.4:** 1/1 test passing, snapshot integrity verified
- **Gap 5.5:** 6/6 tests passing, WCAG 2.1 AA compliance

**Overall:** 15/15 tests passing → Phase 5 completion

---

## Handoff Checklist

- [ ] Architecture approved
- [ ] Code sketches reviewed
- [ ] Dependencies understood
- [ ] Testing strategy validated
- [ ] Risk mitigation acknowledged
- [ ] Team ready for implementation

---

## Next Steps

1. **Approve Plan** - Review architecture & code sketches
2. **Assign Tasks** - Delegate to implementation agents (parallel)
3. **Execute Phase 1** - MSW handlers + test data
4. **Execute Phase 2** - Cleanup + temporal activities
5. **Execute Phase 3** - Integration + test re-enable
6. **Validate** - Run full test suite + accessibility audit
7. **Commit** - Merge to main with comprehensive test report
