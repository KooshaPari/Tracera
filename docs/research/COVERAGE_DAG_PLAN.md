# Coverage Improvement DAG Plan - All Phases

## DAG Structure

```
Phase 1: API Layer ✅ COMPLETE
  └─> Phase 2: Hooks (Parallel)
      ├─> Phase 3: Views/Components (Parallel)
      │   └─> Phase 4: Utils/Helpers (Parallel)
      │       └─> Phase 5: Final Polish
```

## Phase 2: Hooks Coverage (Parallel Tasks)

### Task 2.1: Data Hooks

- `src/hooks/useItems.ts` - Items management hook
- `src/hooks/useProjects.ts` - Projects management hook
- `src/hooks/useLinks.ts` - Links management hook
- `src/hooks/useAgents.ts` - Agents management hook

### Task 2.2: UI Hooks

- `src/hooks/useSearch.ts` - Search functionality
- `src/hooks/useFilters.ts` - Filtering logic
- `src/hooks/usePagination.ts` - Pagination logic
- `src/hooks/useSorting.ts` - Sorting logic

### Task 2.3: State Hooks

- `src/hooks/useAuth.ts` - Authentication state
- `src/hooks/useWebSocket.ts` - WebSocket connections
- `src/hooks/useNotifications.ts` - Notifications

## Phase 3: Views/Components (Parallel Tasks)

### Task 3.1: Core Views

- `src/views/ItemsTableView.tsx` - Error states, edge cases
- `src/views/ProjectsListView.tsx` - Error states, edge cases
- `src/views/ProjectDetailView.tsx` - Error states, edge cases
- `src/views/ItemDetailView.tsx` - Error states, edge cases

### Task 3.2: Advanced Views

- `src/views/GraphView.tsx` - Error states, edge cases
- `src/views/ItemsKanbanView.tsx` - Error states, edge cases
- `src/views/ItemsTreeView.tsx` - Error states, edge cases
- `src/views/TraceabilityMatrixView.tsx` - Error states, edge cases

### Task 3.3: UI Components

- `src/components/ui/*.tsx` - Error states, edge cases
- `src/components/layout/*.tsx` - Error states, edge cases

## Phase 4: Utils/Helpers (Parallel Tasks)

### Task 4.1: Core Utils

- `src/lib/openapi-utils.ts` - OpenAPI utilities
- `src/lib/enterprise-optimizations.ts` - Optimization utilities
- `src/utils/*.ts` - All utility functions

### Task 4.2: API Helpers

- `src/api/reports.ts` - Reports API
- `src/api/settings.ts` - Settings API
- `src/api/matrix.ts` - Matrix API

## Phase 5: Final Polish

### Task 5.1: Coverage Verification

- Run full coverage report
- Identify remaining gaps
- Fix any failing tests

### Task 5.2: Threshold Validation

- Verify 95% coverage across all metrics
- Fix any threshold violations
- Update documentation

## Execution Strategy

1. **Parallel Execution**: Run Phase 2 tasks in parallel (3 subagents)
2. **Streaming Progress**: Each subagent outputs JSON progress updates
3. **Dependency Management**: Phase 3 starts after Phase 2 completes
4. **Background Tasks**: Use background processes with progress tracking

## Progress Tracking Format

```json
{
  "phase": "2",
  "task": "2.1",
  "status": "in_progress|complete|error",
  "files_processed": 4,
  "files_total": 4,
  "tests_created": 45,
  "coverage_before": 60,
  "coverage_after": 85,
  "errors": []
}
```
