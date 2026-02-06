# Phase 5.3-5.5 Code Implementation Guide

**Status:** DETAILED IMPLEMENTATION INSTRUCTIONS
**Audience:** Implementation agents (parallel execution)
**Date:** 2026-02-05

---

## Gap 5.3: Frontend Integration Tests (8 Tests)

### Agent 1: Frontend Integration Tests

**Objective:** Close 8 skipped integration tests
**Time:** ~20 minutes
**Parallel with:** Agents 2 & 3

---

### Task 5.3.1: Extend MSW Handlers

**File:** `frontend/apps/web/src/__tests__/mocks/handlers.ts`

**Current State:**
```typescript
export const handlers = [
  http.get(`${API_BASE}/api/v1/projects`, ...),
  http.get(`${API_BASE}/api/v1/items`, ...),
  http.get(`${API_BASE}/api/v1/links`, ...),
];
```

**Changes Required:**

1. **Add Reports Endpoint** (used by line 730: render reports templates)
   - Endpoint: `GET /api/v1/reports/templates`
   - Response: Array of templates with formats
   - Used by: ReportsView component

2. **Add Search Endpoint** (used by line 852: perform search on input)
   - Endpoint: `GET /api/v1/search?q=<query>`
   - Response: Filtered items based on query
   - Used by: SearchView component

3. **Add Export Endpoint** (used by line 761: generate report on button click)
   - Endpoint: `POST /api/v1/reports/export`
   - Request body: { format: 'PDF' | 'CSV', type: 'coverage' | 'status' | 'export' }
   - Response: { downloadUrl, filename }

**Implementation:**

```typescript
import { HttpResponse, http } from 'msw'
import { mockItems, mockLinks, mockProjects, mockReports } from './data'

const API_BASE = 'http://localhost:4000'

export const handlers = [
  // Existing handlers
  http.get(`${API_BASE}/api/v1/projects`, () =>
    HttpResponse.json({
      projects: mockProjects,
      total: mockProjects.length,
    }),
  ),

  http.get(`${API_BASE}/api/v1/items`, () =>
    HttpResponse.json({
      items: mockItems,
      total: mockItems.length,
    }),
  ),

  http.get(`${API_BASE}/api/v1/links`, () =>
    HttpResponse.json({
      links: mockLinks,
      total: mockLinks.length,
    }),
  ),

  // NEW: Reports Templates Endpoint
  http.get(`${API_BASE}/api/v1/reports/templates`, () =>
    HttpResponse.json({
      templates: mockReports,
    }),
  ),

  // NEW: Search Endpoint
  http.get(`${API_BASE}/api/v1/search`, ({ request }) => {
    const url = new URL(request.url)
    const q = url.searchParams.get('q') ?? ''

    // Simple substring search on title and description
    const results = mockItems.filter(item =>
      item.title.toLowerCase().includes(q.toLowerCase()) ||
      (item.description?.toLowerCase().includes(q.toLowerCase()) ?? false),
    )

    return HttpResponse.json({
      results,
      total: results.length,
      query: q,
    })
  }),

  // NEW: Export/Report Generation Endpoint
  http.post(`${API_BASE}/api/v1/reports/export`, async ({ request }) => {
    const body = (await request.json()) as {
      format: 'PDF' | 'CSV' | 'JSON'
      type?: string
    }

    const filename = `report-${Date.now()}.${body.format.toLowerCase()}`

    return HttpResponse.json({
      downloadUrl: `blob:http://localhost:4000/${Math.random().toString(36).slice(2)}`,
      filename,
      status: 'success',
    })
  }),
]
```

**Key Points:**
- Handlers must be in same order (specific → general)
- Use `url.searchParams.get()` for query params
- Return proper response objects with `total` count
- Test data must match component expectations

---

### Task 5.3.2: Extend Test Data

**File:** `frontend/apps/web/src/__tests__/mocks/data.ts`

**Current State:**
- 2 projects (proj-1, proj-2)
- 2 items (item-1, item-2)
- 1 link (link-1)

**Changes Required:**

1. **Add mockReports** - Array of report templates
2. **Extend mockItems** - Add more items for search tests
3. **Keep mockProjects** - Reuse existing (proj-1, proj-2)
4. **Keep mockLinks** - Reuse existing (link-1)

**Implementation:**

```typescript
import type {
  Item,
  ItemStatus,
  Link,
  Priority,
  Project,
  ViewType,
} from '@tracertm/types'

// Helper timestamps
const now = new Date().toISOString()
const yesterday = new Date(Date.now() - 86_400_000).toISOString()
const lastWeek = new Date(Date.now() - 604_800_000).toISOString()

// Existing projects (keep as-is)
export const mockProjects: Project[] = [
  {
    createdAt: lastWeek,
    description: 'Core traceability management system',
    id: 'proj-1',
    name: 'TraceRTM Core',
    updatedAt: yesterday,
  },
  {
    createdAt: yesterday,
    description: 'Web interface for traceability management',
    id: 'proj-2',
    name: 'Web Dashboard',
    updatedAt: now,
  },
]

// Existing items + new ones for search
export const mockItems: Item[] = [
  {
    createdAt: lastWeek,
    description: 'Implement secure user authentication system',
    id: 'item-1',
    priority: 'high' as Priority,
    projectId: 'proj-1',
    status: 'done' as ItemStatus,
    title: 'User Authentication',
    type: 'requirement',
    updatedAt: yesterday,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
  {
    createdAt: lastWeek,
    description: 'Create comprehensive project dashboard with metrics',
    id: 'item-2',
    parentId: 'item-1',
    priority: 'high' as Priority,
    projectId: 'proj-1',
    status: 'in_progress' as ItemStatus,
    title: 'Project Dashboard',
    type: 'feature',
    updatedAt: now,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
  // NEW: Additional items for search tests
  {
    createdAt: lastWeek,
    description: 'Database schema design and migration',
    id: 'item-3',
    priority: 'high' as Priority,
    projectId: 'proj-1',
    status: 'done' as ItemStatus,
    title: 'Database Schema',
    type: 'requirement',
    updatedAt: yesterday,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
  {
    createdAt: yesterday,
    description: 'API endpoint documentation and examples',
    id: 'item-4',
    priority: 'medium' as Priority,
    projectId: 'proj-2',
    status: 'in_progress' as ItemStatus,
    title: 'API Documentation',
    type: 'feature',
    updatedAt: now,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
  {
    createdAt: yesterday,
    description: 'Unit test coverage for core modules',
    id: 'item-5',
    priority: 'medium' as Priority,
    projectId: 'proj-1',
    status: 'todo' as ItemStatus,
    title: 'Unit Tests',
    type: 'test',
    updatedAt: now,
    version: 1,
    view: 'FEATURE' as ViewType,
  },
]

// Existing link
export const mockLinks: Link[] = [
  {
    createdAt: lastWeek,
    id: 'link-1',
    projectId: 'proj-1',
    sourceId: 'item-1',
    targetId: 'item-2',
    type: 'implements',
  },
]

// NEW: Mock Reports for reports endpoint
export const mockReports = [
  {
    id: 'coverage',
    name: 'Coverage Report',
    description: 'Traceability coverage analysis',
    formats: ['PDF', 'CSV', 'JSON'],
    icon: 'chart-bar',
  },
  {
    id: 'status',
    name: 'Status Report',
    description: 'Project status and progress',
    formats: ['PDF', 'HTML'],
    icon: 'activity',
  },
  {
    id: 'export',
    name: 'Items Export',
    description: 'Export all items and links',
    formats: ['CSV', 'JSON', 'Excel'],
    icon: 'download',
  },
]

// Combine all data
export const mockData = {
  items: mockItems,
  links: mockLinks,
  projects: mockProjects,
  reports: mockReports,
}
```

**Key Points:**
- Timestamps must be in ISO format
- Item types: 'requirement' | 'feature' | 'test' | 'bug' | 'documentation'
- Include variety for search tests (item-3 through item-5 with different titles)
- mockReports should have id, name, formats array

---

### Task 5.3.3: Add Global Cleanup

**File:** `frontend/apps/web/src/__tests__/setup.ts`

**Current State:** Mocks are defined but no cleanup between tests

**Changes Required:**

1. **Add afterEach hook** to cleanup stores + MSW
2. **Add store reset functions** for all zustand stores
3. **Clear localStorage** between tests
4. **Reset MSW server** between tests

**Location:** Add after MSW setup (around line 100-120)

**Implementation:**

```typescript
// At the END of setup.ts file (after other mocks), add:

import { afterEach } from 'vitest'
import { getServer } from './mocks/server'

// Zustand store imports (for cleanup)
import { useAuthStore } from '../stores/auth-store'
import { useItemsStore } from '../stores/items-store'
import { useProjectStore } from '../stores/project-store'
import { useSyncStore } from '../stores/sync-store'

// Global cleanup after each test
afterEach(() => {
  // Reset MSW handlers to defaults
  getServer().resetHandlers()

  // Clear all zustand stores
  useAuthStore.setState({
    user: null,
    isAuthenticated: false,
    token: null,
    // ... reset all auth state fields
  })

  useItemsStore.setState({
    items: new Map(),
    pendingDeletes: new Set(),
    // ... reset all items state fields
  })

  useProjectStore.setState({
    currentProject: null,
    currentProjectId: null,
    recentProjects: [],
    // ... reset all project state fields
  })

  useSyncStore.setState({
    isOnline: true,
    pendingMutations: [],
    failedMutations: [],
    // ... reset all sync state fields
  })

  // Clear localStorage
  localStorage.clear()

  // Clear all mocks
  vi.clearAllMocks()
})
```

**Key Points:**
- Use `getServer().resetHandlers()` to reset MSW (not create new server)
- Call `getState()` on each store to get current state, then reset
- Must be in afterEach (not in specific test file)
- Also clear vi.mocks() to prevent cross-contamination

---

### Task 5.3.4: Create Async Test Helpers

**File:** `frontend/apps/web/src/__tests__/helpers/async-test-helpers.ts` (NEW)

**Purpose:** Reusable async utilities for integration tests

**Implementation:**

```typescript
/**
 * Async test helpers for integration tests
 * Provides utilities for waiting on async state changes
 */

import { render, screen, waitFor } from '@testing-library/react'
import { useAuthStore } from '../../stores/auth-store'
import { useItemsStore } from '../../stores/items-store'
import { useProjectStore } from '../../stores/project-store'
import { useSyncStore } from '../../stores/sync-store'

// ============================================================================
// Store Cleanup
// ============================================================================

/**
 * Clear all zustand stores to initial state
 * Use in beforeEach or afterEach
 */
export async function clearAllStores(): Promise<void> {
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

/**
 * Clear localStorage and vi mocks
 */
export function clearMSW(): void {
  localStorage.clear()
  vi.clearAllMocks()
}

// ============================================================================
// Async Wait Utilities
// ============================================================================

/**
 * Wait for loading state (skeleton loaders visible)
 * @param ms - milliseconds to wait
 */
export async function waitForLoadingState(ms: number = 500): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Wait for loading state to disappear
 * @param timeout - waitFor timeout in ms
 */
export async function waitForNoLoadingState(timeout: number = 3000): Promise<void> {
  await waitFor(
    () => {
      const skeletons = document.querySelectorAll('[data-testid*="skeleton"]')
      if (skeletons.length > 0) {
        throw new Error('Loading skeleton still visible')
      }
    },
    { timeout },
  )
}

/**
 * Wait for specific element to appear
 * @param text - Text content to find
 * @param timeout - waitFor timeout in ms
 */
export async function waitForElement(
  text: string,
  timeout: number = 3000,
): Promise<HTMLElement> {
  let element: HTMLElement | null = null

  await waitFor(
    () => {
      element = screen.getByText(new RegExp(text, 'i'))
      if (!element) {
        throw new Error(`Element with text "${text}" not found`)
      }
    },
    { timeout },
  )

  return element!
}

/**
 * Wait for elements to be removed
 * @param testId - data-testid to wait for removal
 * @param timeout - waitFor timeout in ms
 */
export async function waitForElementToDisappear(
  testId: string,
  timeout: number = 3000,
): Promise<void> {
  await waitFor(
    () => {
      const element = document.querySelector(`[data-testid="${testId}"]`)
      if (element) {
        throw new Error(`Element with testId "${testId}" still visible`)
      }
    },
    { timeout },
  )
}

// ============================================================================
// Store State Assertions
// ============================================================================

/**
 * Verify current project is set
 */
export function assertCurrentProject(
  projectId: string,
  projectName: string,
): void {
  const state = useProjectStore.getState()
  expect(state.currentProjectId).toBe(projectId)
  expect(state.currentProject?.name).toBe(projectName)
}

/**
 * Verify items are loaded
 */
export function assertItemsLoaded(count: number): void {
  const state = useItemsStore.getState()
  expect(state.items.size).toBe(count)
}

/**
 * Verify sync status
 */
export function assertSyncOnline(isOnline: boolean): void {
  const state = useSyncStore.getState()
  expect(state.isOnline).toBe(isOnline)
}
```

**Key Points:**
- Export individual helpers for reuse
- Use waitFor() for async operations
- Provide store assertion helpers
- Document each function with JSDoc

---

### Task 5.3.5: Re-enable Integration Tests

**File:** `frontend/apps/web/src/__tests__/integration/app-integration.test.tsx`

**Changes:**

1. **Line 370:** Replace `it.skip('should maintain recent projects list',`
   ```diff
   - it.skip('should maintain recent projects list', () => {
   + it('should maintain recent projects list', () => {
   ```

2. **Line 715:** Replace `it.skip('should show loading state',`
   ```diff
   - it.skip('should show loading state', () => {
   + it('should show loading state', async () => {
   ```
   Also update test to use waitFor:
   ```typescript
   it('should show loading state', async () => {
     vi.spyOn(api.projects, 'list').mockImplementation(
       async () => new Promise(() => {}), // Never resolves
     )

     renderWithProviders(<DashboardView />)

     // Wait for skeletons to appear
     await waitFor(() => {
       const skeletons = screen.getAllByTestId(/skeleton/i)
       expect(skeletons.length).toBeGreaterThan(0)
     })
   })
   ```

3. **Line 730:** Replace `it.skip('should render reports templates',`
   ```diff
   - it.skip('should render reports templates', async () => {
   + it('should render reports templates', async () => {
   ```
   Add proper test data setup at top of function

4. **Line 744:** Replace `it.skip('should allow format selection',`
   ```diff
   - it.skip('should allow format selection', async () => {
   + it('should allow format selection', async () => {
   ```

5. **Line 761:** Replace `it.skip('should generate report on button click',`
   ```diff
   - it.skip('should generate report on button click', async () => {
   + it('should generate report on button click', async () => {
   ```

6. **Line 852:** Replace `it.skip('should perform search on input',`
   ```diff
   - it.skip('should perform search on input', () => {
   + it('should perform search on input', async () => {
   ```
   Update to use async/await properly

7. **Line 876:** Replace `it.skip('should show no results message',`
   ```diff
   - it.skip('should show no results message', async () => {
   + it('should show no results message', async () => {
   ```

8. **Line 1006:** Replace `it.skip('should handle offline-to-online sync',`
   ```diff
   - it.skip('should handle offline-to-online sync', async () => {
   + it('should handle offline-to-online sync', async () => {
   ```

**Summary:** 8 replacements of `it.skip` → `it` and `it.skip` → `it async`

---

## Gap 5.4: Temporal Snapshot Workflow (1 Test)

### Agent 2: Temporal Snapshot Workflow

**Objective:** Implement snapshot creation workflow with Temporal
**Time:** ~30 minutes
**Parallel with:** Agents 1 & 3
**Dependencies:** None (can start immediately)
**Blocks:** Nothing (independent)

---

### Task 5.4.1: Create Snapshot Activities

**File:** `backend/internal/temporal/activities.go` (NEW)

**Purpose:** Define three activities for snapshot workflow

**Implementation:**

```go
package temporal

import (
  "bytes"
  "compress/gzip"
  "context"
  "database/sql"
  "encoding/json"
  "fmt"
  "time"

  "github.com/neo4j/neo4j-go-driver/v5/neo4j"
  "go.temporal.io/sdk/activity"
  "go.uber.org/zap"
  "minio/minio-go/v7"
)

// SnapshotPayload represents the snapshot data
type SnapshotPayload struct {
  SessionID string        `json:"session_id"`
  Projects  []interface{} `json:"projects"`
  Items     []interface{} `json:"items"`
  Timestamp time.Time     `json:"timestamp"`
  Size      int64         `json:"size"`
}

// SnapshotResult is the workflow result
type SnapshotResult struct {
  S3Key    string        `json:"s3_key"`
  Size     int64         `json:"size"`
  Duration time.Duration `json:"duration"`
}

// SnapshotActivities contains activity implementations
type SnapshotActivities struct {
  db     *sql.DB
  neo4j  neo4j.Driver
  minio  *minio.Client
  logger *zap.Logger
}

// NewSnapshotActivities creates new snapshot activities
func NewSnapshotActivities(
  db *sql.DB,
  neo4j neo4j.Driver,
  minio *minio.Client,
  logger *zap.Logger,
) *SnapshotActivities {
  return &SnapshotActivities{
    db:    db,
    neo4j: neo4j,
    minio: minio,
    logger: logger,
  }
}

// QuerySnapshot activity: Load project state from Neo4j + PostgreSQL
func (a *SnapshotActivities) QuerySnapshot(
  ctx context.Context,
  sessionID string,
) (*SnapshotPayload, error) {
  // Log activity execution
  logger := activity.GetLogger(ctx)
  logger.Info("QuerySnapshot activity started", "sessionID", sessionID)

  payload := &SnapshotPayload{
    SessionID: sessionID,
    Projects:  []interface{}{},
    Items:     []interface{}{},
    Timestamp: time.Now(),
  }

  // Query projects from PostgreSQL
  rows, err := a.db.QueryContext(ctx, `
    SELECT id, name, description, metadata, created_at, updated_at
    FROM projects
    WHERE deleted_at IS NULL
  `)
  if err != nil {
    logger.Error("Failed to query projects", "error", err)
    return nil, fmt.Errorf("query projects: %w", err)
  }
  defer rows.Close()

  var projects []interface{}
  for rows.Next() {
    var id, name, description, metadata string
    var createdAt, updatedAt time.Time
    if err := rows.Scan(&id, &name, &description, &metadata, &createdAt, &updatedAt); err != nil {
      logger.Error("Failed to scan project", "error", err)
      return nil, fmt.Errorf("scan project: %w", err)
    }
    projects = append(projects, map[string]interface{}{
      "id":          id,
      "name":        name,
      "description": description,
      "created_at":  createdAt,
      "updated_at":  updatedAt,
    })
  }
  payload.Projects = projects

  // Query items from PostgreSQL
  itemRows, err := a.db.QueryContext(ctx, `
    SELECT id, project_id, type, title, description, status, priority, created_at, updated_at
    FROM items
    WHERE deleted_at IS NULL
  `)
  if err != nil {
    logger.Error("Failed to query items", "error", err)
    return nil, fmt.Errorf("query items: %w", err)
  }
  defer itemRows.Close()

  var items []interface{}
  for itemRows.Next() {
    var id, projectID, itemType, title, description, status, priority string
    var createdAt, updatedAt time.Time
    if err := itemRows.Scan(&id, &projectID, &itemType, &title, &description, &status, &priority, &createdAt, &updatedAt); err != nil {
      logger.Error("Failed to scan item", "error", err)
      return nil, fmt.Errorf("scan item: %w", err)
    }
    items = append(items, map[string]interface{}{
      "id":          id,
      "project_id":  projectID,
      "type":        itemType,
      "title":       title,
      "description": description,
      "status":      status,
      "priority":    priority,
      "created_at":  createdAt,
      "updated_at":  updatedAt,
    })
  }
  payload.Items = items

  logger.Info("QuerySnapshot completed", "projects", len(projects), "items", len(items))
  return payload, nil
}

// CreateSnapshot activity: Serialize and compress snapshot
func (a *SnapshotActivities) CreateSnapshot(
  ctx context.Context,
  payload *SnapshotPayload,
) ([]byte, error) {
  logger := activity.GetLogger(ctx)
  logger.Info("CreateSnapshot activity started", "sessionID", payload.SessionID)

  // Serialize payload to JSON
  jsonData, err := json.MarshalIndent(payload, "", "  ")
  if err != nil {
    logger.Error("Failed to marshal payload", "error", err)
    return nil, fmt.Errorf("marshal payload: %w", err)
  }

  // Compress with gzip
  var compressed bytes.Buffer
  gz := gzip.NewWriter(&compressed)
  if _, err := gz.Write(jsonData); err != nil {
    logger.Error("Failed to compress data", "error", err)
    return nil, fmt.Errorf("compress data: %w", err)
  }
  if err := gz.Close(); err != nil {
    logger.Error("Failed to close gzip writer", "error", err)
    return nil, fmt.Errorf("close gzip: %w", err)
  }

  tarballBytes := compressed.Bytes()
  logger.Info("CreateSnapshot completed", "originalSize", len(jsonData), "compressedSize", len(tarballBytes))

  return tarballBytes, nil
}

// UploadSnapshot activity: Upload compressed snapshot to MinIO
func (a *SnapshotActivities) UploadSnapshot(
  ctx context.Context,
  sessionID string,
  data []byte,
) (string, error) {
  logger := activity.GetLogger(ctx)
  logger.Info("UploadSnapshot activity started", "sessionID", sessionID, "size", len(data))

  bucket := "tracertm"
  s3Key := fmt.Sprintf("snapshots/%s/snapshot-%d.tar.gz", sessionID, time.Now().Unix())

  // Upload to MinIO
  info, err := a.minio.PutObject(
    ctx,
    bucket,
    s3Key,
    bytes.NewReader(data),
    int64(len(data)),
    minio.PutObjectOptions{
      ContentType: "application/gzip",
    },
  )
  if err != nil {
    logger.Error("Failed to upload to MinIO", "error", err)
    return "", fmt.Errorf("upload to minio: %w", err)
  }

  logger.Info("UploadSnapshot completed", "s3Key", s3Key, "etag", info.ETag)
  return s3Key, nil
}
```

**Key Points:**
- Use activity.GetLogger(ctx) for logging
- Return errors properly (will trigger retries)
- Query data must be serializable to JSON
- Gzip compression reduces size significantly
- MinIO path: `snapshots/{sessionId}/snapshot-{timestamp}.tar.gz`

---

### Task 5.4.2: Create Snapshot Workflow

**File:** `backend/internal/temporal/workflows.go` (NEW)

**Purpose:** Define workflow that chains activities together

**Implementation:**

```go
package temporal

import (
  "fmt"
  "time"

  "go.temporal.io/sdk/workflow"
  "go.uber.org/zap"
)

// SnapshotWorkflow executes the snapshot creation workflow
func SnapshotWorkflow(
  ctx workflow.Context,
  sessionID string,
) (*SnapshotResult, error) {
  // Create logger for workflow
  logger := workflow.GetLogger(ctx)
  logger.Info("SnapshotWorkflow started", "sessionID", sessionID)

  startTime := time.Now()

  // Configure activity options with retry policy
  ao := workflow.ActivityOptions{
    ScheduleToCloseTimeout: time.Minute * 5,
    RetryPolicy: &workflow.RetryPolicy{
      BackoffCoefficient: 2.0,
      InitialInterval:    time.Second * 2,
      MaximumInterval:    time.Second * 10,
      MaximumAttempts:    3,
    },
  }
  ctx = workflow.WithActivityOptions(ctx, ao)

  activities := &SnapshotActivities{}

  // Step 1: Query snapshot state
  logger.Info("Executing QuerySnapshot activity")
  var payload *SnapshotPayload
  if err := workflow.ExecuteActivity(
    ctx,
    activities.QuerySnapshot,
    sessionID,
  ).Get(ctx, &payload); err != nil {
    logger.Error("QuerySnapshot activity failed", "error", err)
    return nil, fmt.Errorf("query snapshot: %w", err)
  }
  logger.Info("QuerySnapshot completed", "projects", len(payload.Projects), "items", len(payload.Items))

  // Step 2: Create compressed snapshot
  logger.Info("Executing CreateSnapshot activity")
  var tarballData []byte
  if err := workflow.ExecuteActivity(
    ctx,
    activities.CreateSnapshot,
    payload,
  ).Get(ctx, &tarballData); err != nil {
    logger.Error("CreateSnapshot activity failed", "error", err)
    return nil, fmt.Errorf("create snapshot: %w", err)
  }
  logger.Info("CreateSnapshot completed", "size", len(tarballData))

  // Step 3: Upload to MinIO
  logger.Info("Executing UploadSnapshot activity")
  var s3Key string
  if err := workflow.ExecuteActivity(
    ctx,
    activities.UploadSnapshot,
    sessionID,
    tarballData,
  ).Get(ctx, &s3Key); err != nil {
    logger.Error("UploadSnapshot activity failed", "error", err)
    return nil, fmt.Errorf("upload snapshot: %w", err)
  }
  logger.Info("UploadSnapshot completed", "s3Key", s3Key)

  duration := time.Since(startTime)
  logger.Info("SnapshotWorkflow completed successfully", "duration", duration.String())

  return &SnapshotResult{
    S3Key:    s3Key,
    Size:     int64(len(tarballData)),
    Duration: duration,
  }, nil
}
```

**Key Points:**
- Use workflow.GetLogger() for logging
- Configure retry policy (2-3 retries, exponential backoff)
- Chain activities: Query → Create → Upload
- Return SnapshotResult with S3 key and metadata
- Use fmt.Errorf for error wrapping

---

### Task 5.4.3: Add Temporal Test Setup

**File:** `backend/tests/integration/test_minio_snapshots.py`

**Location:** Add before the skipped test (around line 215)

**Add Pytest Fixture:**

```python
import pytest
from temporalio.client import Client
from temporalio.worker import Worker


@pytest.fixture
async def temporal_worker():
    """
    Setup Temporal test environment with worker and workflow registration.

    Yields:
        Worker instance for the test duration
    """
    # Connect to Temporal test server
    client = await Client.connect("localhost:7233")

    # Create worker with task queue
    worker = Worker(
        client,
        task_queue="test-queue",
        workflows=[/* workflow classes */],
        activities=[/* activity instances */],
    )

    # Start worker in background
    async with worker:
        yield worker
```

**Update Skipped Test:**

```python
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_scheduled_snapshot_workflow(
    db_session,
    neo4j_driver,
    minio_clean,
    temporal_worker,  # Add this parameter
):
    """
    Test scheduled snapshot workflow creates snapshots periodically.

    Verifies:
    - Workflow executes successfully
    - Snapshots created and uploaded to MinIO
    - Session metadata updated with S3 key
    """
    from temporalio.client import Client

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Start workflow
    handle = await client.start_workflow(
        "SnapshotWorkflow",
        session_id,
        id=f"snapshot-{session_id}",
        task_queue="test-queue",
    )

    # Wait for completion with timeout
    result = await asyncio.wait_for(
        handle.result(),
        timeout=30.0,
    )

    # Verify result
    assert result.s3_key is not None
    assert result.size > 0

    # Verify MinIO upload
    bucket = "tracertm"
    obj_info = verify_s3_object(minio_clean, bucket, result.s3_key)
    assert obj_info is not None
    assert obj_info["size"] == result.size

    # Verify session metadata updated
    query_result = db_session.execute(
        sqlalchemy.text("""
            SELECT sandbox_snapshot_s3_key
            FROM sessions
            WHERE session_id = :session_id
        """),
        {"session_id": session_id},
    )
    row = query_result.first()
    assert row.sandbox_snapshot_s3_key == result.s3_key

    # Cleanup
    cleanup_s3_objects(minio_clean, bucket, f"snapshots/{session_id}/")
    await cleanup_test_session(db_session, neo4j_driver, session_id)
```

**Key Points:**
- Use `@pytest.fixture` for temporal_worker
- Connect to Temporal test server on localhost:7233
- Start workflow and wait for result with timeout
- Verify MinIO upload AND metadata update
- Clean up test data after verification

---

### Task 5.4.4: Register Workflow + Activities in Service

**File:** `backend/internal/services/service.go`

**Location:** In service initialization (setup method)

**Add Registration:**

```go
func (s *Service) setupTemporalWorkflows(ctx context.Context) error {
  // Get Temporal client (already exists in service)
  client := s.temporalClient

  // Create snapshot activities
  snapshotActivities := temporal.NewSnapshotActivities(
    s.db,
    s.neo4j,
    s.minio,
    s.logger,
  )

  // Register snapshot workflow
  worker := worker.New(
    client,
    "snapshot-queue",
    worker.Options{
      Workflows: []interface{}{
        temporal.SnapshotWorkflow,
      },
      Activities: snapshotActivities,
    },
  )

  // Start worker (non-blocking)
  go func() {
    if err := worker.Run(worker.InterruptCh()); err != nil {
      s.logger.Error("Snapshot worker error", zap.Error(err))
    }
  }()

  s.logger.Info("Temporal snapshot workflow registered")
  return nil
}
```

**Call During Service Init:**

```go
func (s *Service) Initialize(ctx context.Context) error {
  // ... existing init code ...

  // Setup Temporal workflows
  if err := s.setupTemporalWorkflows(ctx); err != nil {
    return fmt.Errorf("setup temporal workflows: %w", err)
  }

  return nil
}
```

**Key Points:**
- Register both workflow AND activities
- Use goroutine to run worker (non-blocking)
- Proper error logging
- Activities instance should be created once per worker

---

## Gap 5.5: E2E Accessibility Tests (6 Tests)

### Agent 3: E2E Accessibility Tests

**Objective:** Add table test data and re-enable 6 accessibility tests
**Time:** ~20 minutes
**Parallel with:** Agents 1 & 2

---

### Task 5.5.1: Extend Table Test Data

**File:** `frontend/apps/web/e2e/fixtures/testData.ts`

**Location:** Add after existing testItems definition

**Implementation:**

```typescript
/**
 * Table Test Items - For Accessibility Tests
 * Requires minimum 7 rows for PageUp test
 */
export const tableTestItems: Item[] = [
  {
    id: 'tbl-item-1',
    projectId: 'test-proj-1',
    type: 'requirement',
    title: 'System Requirements Definition',
    description: 'Define all system requirements and constraints',
    status: 'done',
    priority: 'high',
    createdAt: lastWeek,
    updatedAt: yesterday,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-2',
    projectId: 'test-proj-1',
    type: 'feature',
    title: 'User Authentication Module',
    description: 'Implement secure user authentication with OAuth',
    status: 'in_progress',
    priority: 'high',
    createdAt: lastWeek,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-3',
    projectId: 'test-proj-1',
    type: 'test',
    title: 'Authentication Unit Tests',
    description: 'Write comprehensive tests for auth module',
    status: 'in_progress',
    priority: 'high',
    createdAt: yesterday,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-4',
    projectId: 'test-proj-1',
    type: 'feature',
    title: 'Database Schema Migration',
    description: 'Create initial database schema with migrations',
    status: 'done',
    priority: 'medium',
    createdAt: lastWeek,
    updatedAt: yesterday,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-5',
    projectId: 'test-proj-2',
    type: 'bug',
    title: 'Fix Login Form Validation',
    description: 'Resolve email validation issues on login form',
    status: 'done',
    priority: 'high',
    createdAt: yesterday,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-6',
    projectId: 'test-proj-2',
    type: 'documentation',
    title: 'API Documentation',
    description: 'Write OpenAPI documentation for REST endpoints',
    status: 'todo',
    priority: 'medium',
    createdAt: now,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-7',
    projectId: 'test-proj-2',
    type: 'feature',
    title: 'Dashboard Performance Optimization',
    description: 'Optimize dashboard rendering for large datasets',
    status: 'todo',
    priority: 'low',
    createdAt: now,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-8',
    projectId: 'test-proj-1',
    type: 'requirement',
    title: 'WCAG 2.1 AA Compliance',
    description: 'Ensure all UI components are WCAG 2.1 AA accessible',
    status: 'in_progress',
    priority: 'high',
    createdAt: now,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-9',
    projectId: 'test-proj-1',
    type: 'test',
    title: 'Accessibility Automated Tests',
    description: 'Set up automated accessibility testing with axe-core',
    status: 'in_progress',
    priority: 'medium',
    createdAt: now,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
  {
    id: 'tbl-item-10',
    projectId: 'test-proj-2',
    type: 'feature',
    title: 'Dark Mode Support',
    description: 'Implement dark mode theme for UI',
    status: 'todo',
    priority: 'low',
    createdAt: now,
    updatedAt: now,
    version: 1,
    view: 'feature',
  },
]

// Export for use in E2E tests
export const tableTestData = {
  headers: [
    'Node Identifier',
    'Title',
    'Type',
    'Status',
    'Priority',
  ],
  items: tableTestItems,
  total: tableTestItems.length,
}
```

**Key Points:**
- Minimum 7 items needed for PageUp test
- 10 items recommended (covers all pagination tests)
- Mix of types: requirement, feature, test, bug, documentation
- Mix of statuses: done, in_progress, todo
- Mix of priorities: high, medium, low
- All must have required Item type fields

---

### Task 5.5.2: Update API Mock Handler

**File:** `frontend/apps/web/e2e/fixtures/api-mocks.ts`

**Location:** Find existing items handler or add new one

**Update/Add Handler:**

```typescript
import { HttpResponse, http } from 'msw'
import { tableTestItems, tableTestData } from './testData'

const API_BASE = 'http://localhost:4000'

export const a11yHandlers = [
  // Items endpoint - return table test data
  http.get(`${API_BASE}/api/v1/items`, ({ request }) => {
    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') ?? '10')
    const offset = parseInt(url.searchParams.get('offset') ?? '0')

    const paginatedItems = tableTestItems.slice(offset, offset + limit)

    return HttpResponse.json({
      items: paginatedItems,
      total: tableTestItems.length,
      offset,
      limit,
    })
  }),

  // Projects endpoint - return test projects
  http.get(`${API_BASE}/api/v1/projects`, () =>
    HttpResponse.json({
      projects: [
        {
          id: 'test-proj-1',
          name: 'TraceRTM Core',
          description: 'Core project for accessibility tests',
        },
        {
          id: 'test-proj-2',
          name: 'Web Dashboard',
          description: 'Dashboard project for accessibility tests',
        },
      ],
    })
  ),
]
```

**Key Points:**
- Support limit/offset pagination
- Return total count for pagination tests
- Include at least 2 projects
- Match API response format exactly

---

### Task 5.5.3: Update Playwright Test Fixture

**File:** `frontend/apps/web/e2e/table-accessibility.a11y.spec.ts`

**Location:** Update beforeEach hook (around line 13)

**Current Code:**
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/items')
  await page.waitForLoadState('networkidle')
})
```

**Updated Code:**
```typescript
test.beforeEach(async ({ page }) => {
  // Ensure test data is loaded before navigation
  await page.route('/api/v1/items*', route => {
    route.continue()
  })

  // Navigate to items page
  await page.goto('/items')

  // Wait for network to be idle
  await page.waitForLoadState('networkidle')

  // CRITICAL: Wait for table rows to render (minimum 7 for some tests)
  await page.locator('[role="row"]').nth(7).waitFor({
    timeout: 5000,
  })

  // Wait additional 100ms to ensure all rows are stable
  await page.waitForTimeout(100)
})
```

**Key Points:**
- Wait for row at index 7 (ensures 8+ rows rendered)
- Use timeout of 5 seconds
- Add small delay to ensure rendering is stable
- This fixes the `test.skip()` conditions

---

### Task 5.5.4: Re-enable Accessibility Tests

**File:** `frontend/apps/web/e2e/table-accessibility.a11y.spec.ts`

**Changes:**

1. **Line 60** - Arrow key up/down test:
   ```diff
   - test('should support arrow key navigation up/down', async ({ page }) => {
     const rows = await page.locator('[role="row"]').all();
   - if (rows.length < 3) {
   -   test.skip(); // Need at least header + 2 data rows
   - }
   ```
   Keep test as-is (beforeEach now ensures rows exist)

2. **Line 82** - Home key test:
   ```diff
   - test('should support Home key to jump to first column', async ({ page }) => {
     const cells = await page.locator('[role="gridcell"]').all();
   - if (cells.length === 0) {
   -   test.skip();
   - }
   ```

3. **Line 101** - End key test:
   ```diff
   - test('should support End key to jump to last column', async ({ page }) => {
     const cells = await page.locator('[role="gridcell"]').all();
   - if (cells.length === 0) {
   -   test.skip();
   - }
   ```

4. **Line 118** - Ctrl+Home test:
   ```diff
   - test('should support Ctrl+Home to jump to first cell', async ({ page }) => {
     const cells = await page.locator('[role="gridcell"]').all();
   - if (cells.length === 0) {
   -   test.skip();
   - }
   ```

5. **Line 139** - Ctrl+End test:
   ```diff
   - test('should support Ctrl+End to jump to last cell', async ({ page }) => {
     const rows = await page.locator('[role="row"]').all();
   - if (rows.length < 2) {
   -   test.skip();
   - }
   ```

6. **Line 157** - PageUp test:
   ```diff
   - test('should support PageUp to jump up 5 rows', async ({ page }) => {
     const rows = await page.locator('[role="row"]').all();
   - if (rows.length < 7) {
   -   test.skip(); // Need at least 7 rows
   - }
   ```

**Summary:** Remove all `if (condition) test.skip()` blocks (6 total)

---

### Task 5.5.5: Add WCAG Accessibility Validation (Optional)

**File:** `frontend/apps/web/e2e/table-accessibility.a11y.spec.ts`

**Add New Test Suite:**

```typescript
test.describe('Table Accessibility - WCAG 2.1 AA Compliance', () => {
  test('should pass axe accessibility checks', async ({ page }) => {
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2aa', 'wcag21aa'])
      .disableRules(['color-contrast']) // Can disable specific rules if needed
      .analyze()

    // Log violations for debugging
    if (results.violations.length > 0) {
      console.error('Accessibility violations found:')
      results.violations.forEach(violation => {
        console.error(
          `  - ${violation.id}: ${violation.description}`,
          violation.nodes.map(n => n.target),
        )
      })
    }

    // Assert no violations
    expect(results.violations).toHaveLength(0)
  })

  test('table should have correct ARIA structure', async ({ page }) => {
    // Check for table roles
    const table = page.locator('[role="table"]').first()
    await expect(table).toBeVisible()

    // Check for row roles
    const rows = await page.locator('[role="row"]').all()
    expect(rows.length).toBeGreaterThanOrEqual(8) // Header + 7 data rows

    // Check for gridcell roles
    const cells = await page.locator('[role="gridcell"]').all()
    expect(cells.length).toBeGreaterThan(0)

    // Check for column header roles
    const headers = await page.locator('[role="columnheader"]').all()
    expect(headers.length).toBeGreaterThan(0)
  })
})
```

**Key Points:**
- Uses AxeBuilder for automated accessibility testing
- Tests for WCAG 2.1 AA compliance
- Logs violations for debugging
- Tests ARIA structure separately
- Optional but recommended for complete coverage

---

## Summary of All Changes

### Gap 5.3: 5 Files Modified/Created
- `handlers.ts` - Add 3 endpoints
- `data.ts` - Add mockReports + extended items
- `setup.ts` - Add afterEach cleanup
- `helpers/async-test-helpers.ts` - NEW file
- `app-integration.test.tsx` - Replace 8 it.skip

### Gap 5.4: 4 Files Modified/Created
- `activities.go` - NEW file (3 activities)
- `workflows.go` - NEW file (workflow)
- `test_minio_snapshots.py` - Add fixture + uncomment test
- `service.go` - Add workflow registration

### Gap 5.5: 3 Files Modified/Created
- `testData.ts` - Add tableTestItems
- `api-mocks.ts` - Update items handler
- `table-accessibility.a11y.spec.ts` - Remove 6 skip() calls + optional axe tests

**Total:** 12 files, ~600 lines of code

---

## Testing Commands

```bash
# Gap 5.3
cd frontend/apps/web
npm test -- src/__tests__/integration/app-integration.test.tsx

# Gap 5.4
cd backend
make test-backend TEST_TEMPORAL=1 -k snapshot

# Gap 5.5
cd frontend/apps/web
npx playwright test e2e/table-accessibility.a11y.spec.ts

# All three gaps
npm test -- src/__tests__/integration/app-integration.test.tsx && \
  make test-backend TEST_TEMPORAL=1 -k snapshot && \
  npx playwright test e2e/table-accessibility.a11y.spec.ts
```

Success = 8 + 1 + 6 = **15/15 tests passing**
