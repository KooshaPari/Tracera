# Comprehensive Test Plan: TraceRTM

**Project:** Requirements Traceability Management System (TraceRTM)
**Date:** 2026-01-24
**Version:** 1.0
**Scope:** Full-stack testing pyramid covering backend (Python/FastAPI), frontend (React), and end-to-end workflows

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Pyramid Architecture](#test-pyramid-architecture)
3. [Backend Testing Strategy](#backend-testing-strategy)
4. [Frontend Testing Strategy](#frontend-testing-strategy)
5. [Integration & E2E Testing](#integration--e2e-testing)
6. [Performance & Load Testing](#performance--load-testing)
7. [Security Testing](#security-testing)
8. [Accessibility Testing](#accessibility-testing)
9. [Testing Gaps & Remediation](#testing-gaps--remediation)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Metrics & Success Criteria](#metrics--success-criteria)

---

## Executive Summary

### Current State
- **Backend:** 590 test files (8,189 test functions) - Comprehensive unit/integration coverage
- **Frontend:** 113+ test files - Good component coverage, needs hook/store integration tests
- **E2E:** 18+ Playwright specs - Covers major workflows, gaps in performance/security scenarios

### Target State
- **Backend:** Add 50+ integration tests for service chains, API endpoint coverage, concurrency scenarios
- **Frontend:** Add 40+ tests for complex hook interactions, store integration, performance regression
- **E2E:** Add 25+ tests for performance baselines, security validation, accessibility compliance
- **Cross-Layer:** Add holistic tests for full user journeys and system behavior

### Testing Pyramid

```
                    🔺
                   / \
                  /   \
                 /  E2E \ (10-15%)
                /________\
               /          \
              /            \
             / Integration  \ (15-25%)
            /________________\
           /                  \
          /                    \
         /     Unit Tests       \ (60-75%)
        /______________________ \
```

---

## Test Pyramid Architecture

### Layer 1: Unit Tests (Base - 60-75%)
**Focus:** Individual functions, classes, and isolated components
**Speed:** < 100ms per test
**Dependencies:** Mocked
**Coverage Target:** 80-85%

**Backend Unit Tests:**
- Service functions isolated
- Model validation
- Utility functions
- Calculation logic
- Error handling

**Frontend Unit Tests:**
- Component rendering (isolated)
- Hook logic (isolated)
- Store actions
- Utility functions
- Validators

### Layer 2: Integration Tests (Middle - 15-25%)
**Focus:** Multiple units working together
**Speed:** 100ms - 5s per test
**Dependencies:** Real dependencies where practical, mocked external services
**Coverage Target:** 70-80%

**Backend Integration Tests:**
- Service + Repository chains
- API endpoint + Database
- Complex workflows (import/export)
- Event sourcing scenarios
- Concurrent operations

**Frontend Integration Tests:**
- Component + Hook + Store interactions
- Multiple components working together
- Hook chains with stores
- API client + Store synchronization
- Real query behavior

### Layer 3: End-to-End Tests (Apex - 10-15%)
**Focus:** Full user workflows across the entire system
**Speed:** 5s - 60s per test
**Dependencies:** Real backend & database (test environment)
**Coverage Target:** 60-70% (critical paths)

**E2E Tests:**
- User authentication flows
- Create → Read → Update → Delete workflows
- Multi-step operations
- Cross-feature interactions
- Error recovery flows
- Performance baselines

### Layer 4: Holistic Tests (Cross-cutting)
**Focus:** System-wide behavior, performance, security, accessibility
**Speed:** Variable (60s - 10min)
**Coverage Target:** 40-50% of critical paths

**Holistic Tests:**
- Load testing (concurrent users)
- Stress testing (edge capacities)
- Performance regression detection
- Security vulnerability scanning
- WCAG 2.1 AA compliance
- Multi-user synchronization

---

## Backend Testing Strategy

### Current Coverage (590 files, 8,189 tests)

**Existing Test Categories:**
- Unit tests: ~350 files (core services, models, utilities)
- Integration tests: ~150 files (API endpoints, database)
- CLI tests: ~40 files (command execution)
- Concurrent tests: ~30 files (agent coordination)
- Performance tests: ~20 files (benchmarking)
- Property-based tests: ~10 files (Hypothesis)

### Testing Framework Setup

**Stack:**
- pytest 9.0+
- pytest-asyncio 1.3+ (async support)
- pytest-cov (coverage tracking)
- pytest-mock (mocking)
- pytest-xdist (parallel execution)
- pytest-benchmark (performance)
- Hypothesis (property-based testing)
- Faker (test data)
- Factory Boy (test factories)

**Configuration:**
```bash
# Run unit tests only
pytest tests/unit/ -v -k "not slow" --durations=10

# Run with coverage
pytest --cov=src/tracertm --cov-report=html --cov-report=term-missing

# Run in parallel
pytest -n auto tests/

# Run by marker
pytest -m "integration" tests/
pytest -m "asyncio" tests/
pytest -m "performance" tests/
```

### Detailed Backend Test Plan

#### 1. Unit Tests (Expand: +15 test files)

**Domain Models (5 files):**
```python
# tests/unit/models/test_item_model.py
- Item creation with all fields
- Item validation (required fields, constraints)
- Item status transitions
- Item view types (Feature, Code, API, Test, DB, etc.)
- Custom metadata serialization
- UUID generation and uniqueness
- Timestamp management
- Item deletion cascades

# tests/unit/models/test_link_model.py
- Link creation and validation
- Link type constraints (depends_on, blocked_by, validates, etc.)
- Self-reference prevention
- Link bidirectional properties
- Link deletion handling

# tests/unit/models/test_project_model.py
- Project creation and validation
- Multi-view initialization
- Project status lifecycle
- Owner/member management
- Project settings and metadata

# tests/unit/models/test_agent_model.py
- Agent registration and status
- Agent event logging
- Agent lock mechanisms
- Agent metrics storage

# tests/unit/models/test_event_model.py
- Event creation and immutability
- Event sourcing chains
- Event serialization/deserialization
- Event ordering
```

**Service Logic (10 files):**
```python
# tests/unit/services/test_cycle_detection_service.py
- Detect simple cycles (A→B→A)
- Detect complex cycles (A→B→C→A)
- Detect self-references
- Handle disconnected graphs
- Performance with large graphs (1000+ nodes)

# tests/unit/services/test_impact_analysis_service.py
- Direct impact analysis
- Transitive impact (multi-level)
- Exclude analysis (what's NOT impacted)
- Bidirectional impact
- Circular impact handling

# tests/unit/services/test_shortest_path_service.py
- Find path between two items
- No path scenarios
- Multiple path scenarios
- Path cost calculation
- Optimized path finding

# tests/unit/services/test_critical_path_service.py
- Identify critical path
- Handle missing dependencies
- Duration calculations
- Slack time computation
- Timeline analysis

# tests/unit/services/test_bulk_operation_service.py
- Bulk create items (100+)
- Bulk update items
- Bulk create links
- Bulk delete with cascades
- Transaction rollback on error

# tests/unit/services/test_import_service.py
- CSV import validation
- JSON import validation
- Data mapping
- Conflict detection
- Partial import handling

# tests/unit/services/test_export_service.py
- Export to CSV format
- Export to JSON format
- Filter export by view
- Preserve relationships in export
- Large dataset export

# tests/unit/services/test_cache_service.py
- Cache hit/miss behavior
- Cache invalidation
- TTL expiration
- Cache size management
- Concurrent cache access

# tests/unit/services/test_conflict_resolution_service.py
- Last-write-wins resolution
- Three-way merge scenarios
- Custom conflict strategies
- Conflict metadata

# tests/unit/services/test_concurrent_operations_service.py
- Concurrent item creation
- Concurrent link updates
- Lock acquisition/release
- Deadlock prevention
- Lock timeout handling
```

**Utilities & Helpers (5 files):**
```python
# tests/unit/utils/test_validators.py
- Item ID validation
- Project name validation
- Link type validation
- View type validation
- Custom constraint validation

# tests/unit/utils/test_formatters.py
- Date formatting
- Duration formatting
- Link type display
- Status display
- Custom format strings

# tests/unit/utils/test_graph_helpers.py
- Graph construction from items/links
- Graph serialization
- Graph validation
- Node/edge counting
- Subgraph extraction

# tests/unit/utils/test_pagination.py
- Page calculation
- Offset computation
- Limit handling
- Sort specification
- Cursor-based pagination

# tests/unit/utils/test_filters.py
- Filter parsing
- Filter combination (AND/OR)
- Date range filtering
- Enum filtering
- Complex filter chains
```

#### 2. Integration Tests (Expand: +30 test files)

**API Endpoint Integration (12 files):**
```python
# tests/integration/api/test_items_endpoint_chain.py
- Create item → Read item → List items
- Create item → Update item → Delete item
- Create item → Create link → Get item with links
- List items with filters (status, view, type)
- Search items
- Batch item operations

# tests/integration/api/test_links_endpoint_chain.py
- Create link → Verify in source item
- Create link → Verify in target item
- Delete link → Verify removal
- List links with filters
- Link validation (source/target existence)
- Circular link prevention

# tests/integration/api/test_projects_endpoint_chain.py
- Create project → List projects
- Update project → Verify changes
- Delete project → Cascade delete items/links
- Get project with statistics
- Project export
- Project import

# tests/integration/api/test_analysis_endpoint_chain.py
- Impact analysis endpoint + underlying service
- Cycle detection endpoint + result verification
- Shortest path endpoint accuracy
- Critical path calculation
- Traceability matrix generation

# tests/integration/api/test_search_endpoint_chain.py
- Advanced search across items
- Search result ranking
- Filter + search combination
- Search performance baseline
- Search result consistency

# tests/integration/api/test_import_export_endpoint_chain.py
- Export project → Import as new project
- Verify data integrity post-import
- Partial import scenarios
- Conflict resolution during import
- Large dataset import/export

# tests/integration/api/test_auth_endpoint_chain.py
- Login → Token generation
- Token refresh → New token
- Expired token → Refresh
- Logout → Token invalidation
- Multiple concurrent logins

# tests/integration/api/test_webhook_endpoint_chain.py
- Register webhook → Trigger event → Receive webhook
- Webhook retry on failure
- Webhook timeout handling
- Webhook payload validation
- Webhook filtering

# tests/integration/api/test_sync_endpoint_chain.py
- Create item → Sync to client
- Update item → Sync change
- Delete item → Sync removal
- Concurrent syncs → Consistency
- Sync conflict resolution

# tests/integration/api/test_performance_endpoint.py
- Get project performance metrics
- Performance trend analysis
- Agent performance comparison
- Query performance regression detection

# tests/integration/api/test_agent_coordination_endpoint_chain.py
- Register agent → Get tasks
- Complete task → Update agent status
- Agent health check
- Agent load distribution

# tests/integration/api/test_health_endpoint.py
- Health check response
- Database connectivity check
- Service dependencies check
- Performance metrics in health
```

**Database & ORM Integration (8 files):**
```python
# tests/integration/database/test_item_repository_chain.py
- Create → Query by ID → Verify fields
- Update → Query → Verify changes
- Delete → Query → Verify absence
- Create multiple → Query all → Paginate
- Complex filters → Correct results

# tests/integration/database/test_link_repository_chain.py
- Create link → Query → Verify both directions
- Update link type → Query → Verify change
- Delete link → Orphan handling
- Query links by source → Verify all results
- Query links by target → Verify all results

# tests/integration/database/test_transaction_handling.py
- Multiple queries in transaction
- Rollback on error
- Concurrent transactions
- Transaction isolation levels
- Deadlock detection

# tests/integration/database/test_cascade_operations.py
- Delete project → Delete all items
- Delete item → Delete all links
- Delete agent → Clean agent events
- Verify no orphaned records
- Cascade performance with large datasets

# tests/integration/database/test_migration_chain.py
- Run migration forward
- Verify schema changes
- Run migration backward
- Verify schema restoration
- Data preservation across migrations

# tests/integration/database/test_connection_pool.py
- Connection acquisition
- Connection release
- Pool exhaustion handling
- Connection timeout
- Concurrent connection requests

# tests/integration/database/test_async_session_chain.py
- Session creation → Query → Close
- Nested sessions (if applicable)
- Session isolation
- Async iteration over results
- Session exception handling

# tests/integration/database/test_indexes_and_query_optimization.py
- Verify index usage
- Query plan analysis
- Index performance improvement validation
- Missing index detection
```

**Service Chain Integration (10 files):**
```python
# tests/integration/services/test_analysis_service_chain.py
- Cycle detection → Impact analysis chain
- Critical path → Resource allocation chain
- Impact analysis → Link suggestion chain
- Traceability matrix → Gap analysis chain
- Service error handling and recovery

# tests/integration/services/test_import_export_chain.py
- Import CSV → Export same data → Compare
- Import JSON → Verify relationships preserved
- Partial import → Partial export consistency
- Conflict resolution during import
- Large dataset (10k+ items) import/export

# tests/integration/services/test_event_sourcing_chain.py
- Create event → Query event log
- Multiple events → Reconstruct state
- Event filtering and ordering
- Event snapshot functionality
- Event log compaction

# tests/integration/services/test_auto_linking_chain.py
- Suggest links based on title similarity
- Suggest links based on relationships
- Accept suggestion → Create link
- Reject suggestion → Remove from suggestions
- Batch link creation from suggestions

# tests/integration/services/test_webhook_processing_chain.py
- Item created → Webhook fired
- Link changed → Webhook fired
- Webhook → External system → Webhook response
- Webhook failure → Retry logic
- Webhook filtering by event type

# tests/integration/services/test_agent_coordination_chain.py
- Register agent → Get assignment
- Process task → Update status → Get next task
- Multiple agents → Load balance
- Agent failure → Task reassignment
- Agent metrics collection and analysis

# tests/integration/services/test_concurrent_bulk_operation.py
- Bulk create + concurrent update same item
- Bulk delete + concurrent read same item
- Multiple bulk operations on different items
- Bulk operation + normal operation mix
- Bulk operation failure handling

# tests/integration/services/test_cache_invalidation_chain.py
- Cache item → Modify item → Cache invalidated
- Cache analysis result → Dependent modification → Cache cascading
- Cache warm-up strategy
- Cache memory usage management
- Concurrent cache invalidation

# tests/integration/services/test_github_import_chain.py
- GitHub repo access
- Extract requirements from code/issues
- Create items and links from GitHub data
- Update local on new GitHub changes
- Bidirectional sync (if supported)

# tests/integration/services/test_file_watcher_chain.py
- Watch file system
- Detect changes
- Parse changes into items/links
- Sync with database
- Conflict resolution with manual edits
```

#### 3. Concurrency & Agent Tests (Expand: +5 test files)

```python
# tests/integration/concurrency/test_race_conditions.py
- Concurrent item creation with same title
- Concurrent link creation (same source/target)
- Concurrent status updates
- Concurrent metadata changes
- Race condition detection

# tests/integration/concurrency/test_deadlock_prevention.py
- Multiple items locked → No deadlock
- Circular lock dependency → Timeout handling
- Lock ordering enforcement
- Lock release on exception
- Lock monitoring/debugging

# tests/integration/concurrency/test_agent_load_balancing.py
- Distribute 1000 tasks to 5 agents
- Verify even distribution
- Agent failure → Task reassignment
- Agent performance monitoring
- Load rebalancing

# tests/integration/concurrency/test_concurrent_api_requests.py
- 100 concurrent item read requests
- 50 concurrent item create requests
- Mixed read/write concurrent requests
- Request timeout handling
- Connection pool exhaustion

# tests/integration/concurrency/test_chaos_mode_resilience.py
- Random service failures → Recovery
- Database connection drops → Reconnection
- Partial response failures → Retry
- Cascade failure handling
- Graceful degradation
```

#### 4. Error Handling & Edge Cases (Expand: +5 test files)

```python
# tests/integration/error_handling/test_validation_errors.py
- Invalid item data → Clear error message
- Missing required fields → Validation error
- Constraint violation → Helpful error
- Type mismatch → Type error
- Custom validation errors

# tests/integration/error_handling/test_not_found_errors.py
- Query non-existent item → 404
- Delete already deleted item → 404
- Update non-existent link → 404
- Reference non-existent project → Error
- Clear error messages with resource type

# tests/integration/error_handling/test_authorization_errors.py
- Access item without permission → 403
- Modify project without permission → 403
- Delete project without ownership → 403
- Clear error indicating missing permission
- Permission checking in all endpoints

# tests/integration/error_handling/test_database_errors.py
- Database connection lost → Error recovery
- Transaction rollback on error
- Partial write on multi-table operation
- Connection pool exhaustion
- Database timeout handling

# tests/integration/error_handling/test_service_errors.py
- Service throws exception → HTTP error
- Service timeout → Timeout response
- Service resource exhaustion → 503
- Cascading service errors
- Error context preservation
```

### Backend Test Execution Plan

**Phase 1 (Weeks 1-2): Unit Test Enhancement**
- Add 15 new unit test files
- Target 85% coverage for services
- Add property-based tests for validation logic
- Run on every commit

**Phase 2 (Weeks 3-5): Integration Test Expansion**
- Add 30 new integration test files
- Test API endpoint chains
- Test database transactions
- Test service interactions
- Run on every merge to main

**Phase 3 (Week 6): Concurrency & Resilience**
- Add 5 concurrency test files
- Chaos mode testing
- Load balancing verification
- Run weekly

**Metrics to Track:**
```bash
# Code coverage by module
pytest --cov=src/tracertm --cov-report=term-missing

# Test execution time
pytest --durations=20 tests/

# Parallel test execution
pytest -n auto --durations=20 tests/

# Specific test markers
pytest -m "unit" --co -q | wc -l
pytest -m "integration" --co -q | wc -l
pytest -m "asyncio" tests/
```

---

## Frontend Testing Strategy

### Current Coverage (113+ files)

**Existing Test Categories:**
- Unit tests: ~60 files (components, hooks, stores, utilities)
- Integration tests: ~30 files (component chains, hook+store)
- E2E tests: 18+ Playwright specs

### Testing Framework Stack

**Tools:**
- Vitest 4.0+ (unit/integration)
- Playwright 1.57+ (E2E)
- Testing Library (component testing)
- MSW 2.12+ (API mocking)
- Vitest UI (test debugging)

**Configuration:**
```bash
# Run all tests
bun run test

# Run only unit tests
bun run test -- --grep "^(?!.*e2e)"

# Run specific test file
bun run test -- src/__tests__/hooks/useItems.test.ts

# Watch mode
bun run test -- --watch

# With coverage
bun run test -- --coverage

# E2E tests
bun run test:e2e
```

### Detailed Frontend Test Plan

#### 1. Component Unit Tests (Expand: +10 test files)

**Layout Components (2 files):**
```typescript
// src/__tests__/components/layout/test_Header.test.tsx
- Render with auth state (logged in/out)
- Navigation menu display
- User profile menu
- Search input functionality
- Mobile responsive header
- Icon button states (notifications, settings)

// src/__tests__/components/layout/test_Sidebar.test.tsx
- Navigation menu rendering
- Active route highlighting
- Collapsed/expanded states
- Responsive behavior
- Menu item click navigation
- Nested menu expansion
```

**Form Components (3 files):**
```typescript
// src/__tests__/components/forms/test_CreateItemForm.test.tsx
- Form field rendering
- Field validation feedback
- Required field indicators
- Submit button state (disabled/enabled)
- Cancel button functionality
- Error display on submit failure
- Success message display
- Form reset after submit

// src/__tests__/components/forms/test_CreateProjectForm.test.tsx
- All form fields render
- Multi-view selection
- Form submission
- Project creation success
- Duplicate project name handling
- Navigation after creation

// src/__tests__/components/forms/test_CreateLinkForm.test.tsx
- Source/target item selection
- Link type selection
- Form validation
- Prevent self-links
- Submit and cancel
- Auto-complete source/target
```

**Modal & Dialog Components (2 files):**
```typescript
// src/__tests__/components/ui/test_Dialog.test.tsx
- Modal opens on trigger
- Modal closes on dismiss
- Close button functionality
- Escape key dismissal
- Click outside dismissal
- Modal focus management
- Accessibility (aria-label, role)

// src/__tests__/components/ui/test_ConfirmDialog.test.tsx
- Confirmation title/message display
- Action button (confirm/cancel)
- Callback execution on confirm
- Modal closes on action
- Keyboard shortcuts (Enter = confirm, Esc = cancel)
```

**Data Display Components (3 files):**
```typescript
// src/__tests__/components/test_ItemsTable.test.tsx
- Render table with items
- Column headers display
- Item rows with data
- Sort functionality
- Filter functionality
- Pagination controls
- Row selection (checkbox)
- Bulk action buttons
- Item context menu

// src/__tests__/components/test_ItemsTree.test.tsx
- Tree structure rendering
- Parent-child relationships
- Expand/collapse nodes
- Drag-and-drop reordering
- Tree navigation
- Tree node selection

// src/__tests__/components/test_TraceabilityMatrix.test.tsx
- Matrix structure rendering
- Row headers (source items)
- Column headers (target items)
- Link markers in cells
- Link type legends
- Matrix zoom/scroll
- Matrix filtering
```

#### 2. Hook Unit & Integration Tests (Expand: +20 test files)

**Data Management Hooks (6 files):**
```typescript
// src/__tests__/hooks/test_useItems.comprehensive.test.tsx
- Fetch items on mount
- Items data structure
- Loading state transitions
- Error handling and display
- Refetch items on demand
- Update single item
- Delete single item
- Create new item
- Filter items by criteria
- Sort items by field
- Paginate items
- Cache behavior
- Optimistic update

// src/__tests__/hooks/test_useProjects.integration.test.tsx
- Fetch projects list
- Fetch single project
- Create project
- Update project
- Delete project with cascade
- Project loading states
- Error handling
- Multiple project queries
- Project data structure

// src/__tests__/hooks/test_useLinks.integration.test.tsx
- Fetch links for item
- Create link
- Update link type
- Delete link
- Verify link endpoints exist
- Link validation
- Bidirectional link verification

// src/__tests__/hooks/test_useSearch.test.tsx
- Search by keywords
- Search with filters
- Debounced search
- Search result structure
- Empty search results
- Search error handling
- Search result caching
- Advanced search options

// src/__tests__/hooks/test_useGraph.integration.test.tsx
- Initialize graph with items/links
- Update graph on item change
- Update graph on link change
- Graph layout calculation
- Node positioning
- Edge rendering
- Graph performance with large datasets

// src/__tests__/hooks/test_useAuth.test.tsx
- Login flow
- Token storage
- Token refresh
- Logout flow
- Auth state persistence
- Protected route access
- Auth error handling
```

**UI Interaction Hooks (5 files):**
```typescript
// src/__tests__/hooks/test_useMediaQuery.test.tsx
- Match media query on mount
- Update on window resize
- Mobile breakpoint detection
- Tablet breakpoint detection
- Desktop breakpoint detection

// src/__tests__/hooks/test_useLocalStorage.test.tsx
- Store value in localStorage
- Retrieve value on mount
- Update localStorage on change
- Handle missing value
- Serialize/deserialize complex types
- Clear storage on unmount (optional)

// src/__tests__/hooks/test_useDebounce.test.tsx
- Debounce value changes
- Delay before update
- Cancel pending debounce
- Multiple debounce instances
- Edge case: rapid fire changes

// src/__tests__/hooks/test_useOnClickOutside.test.tsx
- Detect outside clicks
- Ignore inside container clicks
- Cleanup on unmount
- Multiple containers

// src/__tests__/hooks/test_useKeyPress.test.tsx
- Detect key press
- Detect key release
- Modifier key combinations (Ctrl+S, Cmd+Z)
- Multiple key listeners
- Cleanup on unmount
```

**Performance & Advanced Hooks (3 files):**
```typescript
// src/__tests__/hooks/test_usePerformance.test.tsx
- Measure component render time
- Track function execution time
- Monitor memory usage
- Identify performance regressions
- Performance metrics export

// src/__tests__/hooks/test_useNodeExpansion.test.tsx
- Expand node in graph
- Collapse node in graph
- Multiple node expansion
- Expansion persistence
- Performance with many nodes

// src/__tests__/hooks/test_useWebSocket.test.tsx
- WebSocket connection
- Message receiving
- Message sending
- Reconnection on disconnect
- Close connection
- Error handling
```

**Query Hooks (3 files):**
```typescript
// src/__tests__/hooks/test_useItemsQuery.test.tsx
- useQuery with items endpoint
- Loading state
- Error state
- Success state with data
- Refetch functionality
- Stale time handling
- Background refetch

// src/__tests__/hooks/test_useProjectsQuery.test.tsx
- useQuery for projects list
- useQuery for single project
- Query invalidation
- Query dependencies
- Parallel queries

// src/__tests__/hooks/test_useMutation.test.tsx
- Create item mutation
- Update item mutation
- Delete item mutation
- Mutation loading state
- Mutation error handling
- Optimistic update with mutation
- Rollback on failure
```

#### 3. Store Unit & Integration Tests (Expand: +8 test files)

**Zustand Store Tests (6 files):**
```typescript
// src/__tests__/stores/test_itemsStore.detailed.test.ts
- Initial state
- setItems action
- addItem action
- updateItem action
- deleteItem action
- getItem selector
- filterItems selector
- sortItems selector
- Store persistence across actions
- Store reset/cleanup
- Concurrent store updates

// src/__tests__/stores/test_projectStore.integration.test.ts
- setProjects action
- setActiveProject action
- addProject action
- updateProject action
- deleteProject action
- getActiveProject selector
- Project list selector
- Clear on logout

// src/__tests__/stores/test_authStore.test.ts
- setAuth action (login)
- clearAuth action (logout)
- setToken action
- isAuthenticated selector
- getCurrentUser selector
- Persist on refresh
- Clear sensitive data on logout

// src/__tests__/stores/test_uiStore.test.ts
- Toggle sidebar
- Set active view
- Set theme (light/dark)
- Show/hide modals
- Toast notifications
- Multiple UI state changes
- UI preferences persistence

// src/__tests__/stores/test_syncStore.test.ts
- Track pending sync
- Mark as synced
- Sync conflict detection
- Sync queue management
- Sync error handling
- Auto-retry sync
- Clear sync state

// src/__tests__/stores/test_websocketStore.test.ts
- setConnected action
- setError action
- addMessage action
- Connection state
- Message queue
- Error state handling
- Auto-reconnection
```

**Cross-Store Integration (2 files):**
```typescript
// src/__tests__/stores/test_store_integration.test.ts
- itemsStore + projectStore interaction
- authStore + itemsStore interaction (auth-protected items)
- uiStore + multiple stores
- Store action chaining
- Derived state across stores

// src/__tests__/stores/test_store_with_hooks.integration.test.ts
- Hook using store
- Store updates → Hook updates
- Hook action → Store update
- Hook selector changes
- Multiple hooks sharing store
```

#### 4. View/Page Integration Tests (Expand: +8 test files)

**Major Views (5 files):**
```typescript
// src/__tests__/views/test_DashboardView.integration.test.tsx
- Dashboard render
- Project summary cards
- Recent items list
- Quick stats
- Navigation to details
- Responsive layout
- Loading states
- Error states

// src/__tests__/views/test_GraphView.integration.test.tsx
- Graph renders with items
- Graph updates on item change
- Layout switching (ELK, force, circular)
- Node selection
- Edge interaction
- Zoom/pan controls
- Legend display
- Export functionality

// src/__tests__/views/test_ProjectsListView.integration.test.tsx
- List projects
- Filter projects
- Sort projects
- Create project button
- Navigate to project detail
- Delete project
- Search projects

// src/__tests__/views/test_ItemsTableView.integration.test.tsx
- Display items table
- Sort by column
- Filter by status/view/type
- Pagination
- Bulk select items
- Bulk delete items
- Create new item
- Edit item from table
- Item context menu

// src/__tests__/views/test_ImportExportView.integration.test.tsx
- Import form display
- File selection
- Progress tracking
- Conflict resolution UI
- Import completion
- Export format selection
- Download exported file
```

**Advanced Views (3 files):**
```typescript
// src/__tests__/views/test_TraceabilityMatrixView.integration.test.tsx
- Matrix rendering
- Row/column labels
- Link indicators in cells
- Filter matrix
- Export matrix

// src/__tests__/views/test_ImpactAnalysisView.integration.test.tsx
- Display impacted items
- Highlight impact chain
- Filter by impact type
- Show statistics
- Navigate to impacted item

// src/__tests__/views/test_AdvancedSearchView.integration.test.tsx
- Search form with filters
- Execute search
- Display results
- Result details on click
- Save search
- Search history
```

#### 5. API Client & Mock Tests (Expand: +5 test files)

```typescript
// src/__tests__/api/test_client.integration.test.ts
- API client initialization
- Request headers (auth, content-type)
- Response parsing
- Error response handling
- Retry logic
- Timeout handling
- Base URL configuration

// src/__tests__/api/test_endpoints.test.ts
- All endpoints defined
- Endpoint URL structure
- Request/response typing
- Endpoint parameters
- Query string building

// src/__tests__/api/test_msw_handlers.test.ts
- MSW handlers coverage
- Mock response correctness
- Error response mocking
- Latency simulation
- Handler matching logic

// src/__tests__/api/test_trpc_integration.test.ts
- tRPC router setup
- tRPC procedures (query, mutation)
- tRPC error handling
- tRPC type safety
- tRPC caching

// src/__tests__/api/test_tansack_query_integration.test.ts
- useQuery with error
- useQuery with refetch
- useMutation flow
- Query invalidation
- Optimistic updates
```

### Frontend Test Execution Plan

**Phase 1 (Weeks 1-2): Hook & Store Expansion**
- Add 28 new hook/store test files
- Focus on complex interactions
- Run on every commit

**Phase 2 (Weeks 3-4): View & Page Integration**
- Add 13 new view/page test files
- Test multi-component workflows
- Run on every commit

**Phase 3 (Week 5): API & Mock Testing**
- Add 5 API integration tests
- Verify MSW mock coverage
- Run on every commit

**Phase 4 (Week 6): E2E Enhancement**
- Add 20+ new E2E tests
- Focus on critical workflows
- Run on every merge to main

---

## Integration & E2E Testing

### Current E2E Coverage (18+ specs)

**Existing Specs:**
- auth.spec.ts - Login/logout workflows
- projects.spec.ts - Project CRUD
- items.spec.ts - Item management
- links.spec.ts - Link management
- graph.spec.ts - Graph visualization
- search.spec.ts - Search functionality
- import-export.spec.ts - Data import/export
- bulk-operations.spec.ts - Bulk item operations
- settings.spec.ts - Settings management
- (others): dashboard, performance, accessibility, security, sync, navigation, agents, edge cases

### Comprehensive E2E Test Plan

#### 1. Critical User Journeys (New: +8 specs)

```typescript
// e2e/critical-flows/complete-project-setup.spec.ts
Test: Create project → Add items → Create links → Analyze impact → Export
- Create new project
- Add 10+ items with different types
- Create links between items
- Run impact analysis
- Verify results
- Export project data
- Verify exported data

// e2e/critical-flows/requirements-traceability.spec.ts
Test: Feature requirement → Code → Test → Database mapping
- Create feature requirement
- Link to code files/classes
- Link to test cases
- Link to database schema
- Run traceability matrix
- Verify all traces complete
- Export traceability report

// e2e/critical-flows/change-impact-workflow.spec.ts
Test: Modify requirement → Identify impact → Update downstream
- Modify existing requirement
- Run impact analysis
- Identify impacted code
- Identify impacted tests
- Update impacted items
- Verify changes propagated

// e2e/critical-flows/multi-user-collaboration.spec.ts
Test: Multiple users working simultaneously
- User A creates item
- User B sees item (via sync)
- User A updates item
- User B sees update
- User B creates link
- User A sees link
- Conflict resolution if same item edited

// e2e/critical-flows/bulk-import-workflow.spec.ts
Test: Import 1000+ items from CSV
- Upload CSV file
- Map columns to fields
- Detect duplicates
- Resolve conflicts
- Complete import
- Verify all items imported
- Performance baseline

// e2e/critical-flows/search-and-filter.spec.ts
Test: Find items using various search/filter methods
- Search by keyword
- Filter by status/view/type
- Combine filters
- Advanced search with operators
- Save search
- Load saved search
- Performance with 1000+ items

// e2e/critical-flows/analytics-reporting.spec.ts
Test: Generate reports and analytics
- Open analytics view
- Generate completion report
- Generate impact report
- Export report as PDF
- Schedule periodic reports
- View report history

// e2e/critical-flows/agent-coordination.spec.ts
Test: Agent-native task assignment and execution
- Create task for agent
- Agent receives task
- Agent processes task
- Agent reports completion
- Verify task results
- Load balance across agents
```

#### 2. Feature Coverage E2E Tests (Expand: +12 specs)

```typescript
// e2e/features/comprehensive-graph-operations.spec.ts
- Open graph view
- Switch layouts (hierarchical, force, circular)
- ELKjs layout calculations verify
- Zoom in/out controls
- Pan graph
- Select node and show details
- Highlight impact path
- Filter nodes by type
- Mini-map navigation
- Export graph visualization
- Performance: 500+ node graph interaction

// e2e/features/advanced-filtering-and-sorting.spec.ts
- Open items list
- Apply single filter
- Combine multiple filters
- Clear filters
- Persistent filter state
- Sort by different columns
- Reverse sort order
- Keyboard shortcuts for filtering
- Filter persistence on navigation
- Filter export

// e2e/features/real-time-synchronization.spec.ts
- Open in two browser tabs
- Create item in tab A
- Verify appears in tab B (within 2s)
- Update item in tab B
- Verify update in tab A
- Delete item in one tab
- Verify deletion in other tab
- Handle conflict (same item updated)
- Network disconnection recovery

// e2e/features/view-switching.spec.ts
- Switch between all 10+ views
- Table → Tree → Kanban transitions
- Verify data consistency across views
- Filter in one view → Applies to others
- Selection persistence across views
- Loading times for view switches

// e2e/features/mobile-responsive.spec.ts
- Mobile viewport (iPhone 12)
- Tablet viewport (iPad)
- Desktop viewport (1920x1080)
- Navigation menu (hamburger mobile)
- Form inputs on mobile
- Touch interactions (tap, swipe)
- Table scrolling on mobile
- Graph panning on mobile
- Text readability on small screens

// e2e/features/keyboard-navigation.spec.ts
- Tab through form fields
- Enter to submit
- Escape to cancel
- Arrow keys for tree navigation
- Ctrl+F for search
- Ctrl+S for save
- Ctrl+Z for undo
- Shift+Click for multi-select
- Focus indicators visible

// e2e/features/dark-mode-toggle.spec.ts
- Switch to dark mode
- Verify colors change
- Verify readability
- Persist preference
- Switch back to light
- Graph colors in dark mode
- Print friendly colors

// e2e/features/permission-based-access.spec.ts
- Admin can edit project
- Member can edit items
- Viewer can only read
- Attempt unauthorized action → Error
- Permission changes → UI updates
- Share project with permissions
- Revoke permissions

// e2e/features/notification-system.spec.ts
- Create item → Toast notification
- Long operation → Progress notification
- Error → Error notification
- Dismiss notification
- Notification persistence (if desired)
- Notification sounds/alerts

// e2e/features/undo-redo-functionality.spec.ts
- Create item → Undo → Item gone
- Undo → Redo → Item back
- Multiple undo steps
- Redo after new action clears stack
- Undo with bulk operations
- Undo in different views

// e2e/features/custom-fields.spec.ts
- Add custom field to item type
- Custom field appears in form
- Custom field data persists
- Custom field searchable
- Custom field in export

// e2e/features/tagging-and-labeling.spec.ts
- Add tag to item
- Filter by tag
- Tag auto-complete
- Edit tags
- Remove tags
- Tag color coding
```

#### 3. Performance & Load Testing (New: +8 specs)

```typescript
// e2e/performance/load-testing.spec.ts
Test: System under load (concurrent users)
- Simulate 10 concurrent users
- Each user: login → view dashboard → create items
- Measure response times
- Measure page load times
- Verify no errors under load
- Check memory usage
- Generate load test report

// e2e/performance/large-dataset-handling.spec.ts
Test: Large project with 10,000+ items
- Create/load project with 10k items
- List view loads within 3s
- Table scrolling smooth (60 FPS)
- Graph view interactive with 500 nodes
- Search 10k items within 500ms
- Filter 10k items within 1s
- Export 10k items within 30s

// e2e/performance/graph-rendering-scaling.spec.ts
Test: Graph performance with increasing nodes
- 100 nodes → Should render instantly
- 500 nodes → Should render within 2s
- 1000 nodes → Should render within 5s
- 5000 nodes → Should render within 10s
- Interaction remains smooth (no jank)
- Mini-map renders in <1s
- ELKjs layout within <5s

// e2e/performance/import-performance.spec.ts
Test: Import speed with varying dataset sizes
- Import 100 items → <1s
- Import 1000 items → <5s
- Import 10k items → <30s
- Memory usage stays reasonable
- No memory leaks after import
- Can open project after large import

// e2e/performance/search-performance.spec.ts
Test: Search speed across dataset sizes
- Search 100 items → <100ms
- Search 1000 items → <200ms
- Search 10k items → <500ms
- Advanced search (multiple filters) → <1s
- Search result highlighting fast
- Typo tolerance (fuzzy search) performance

// e2e/performance/memory-usage.spec.ts
Test: Memory usage doesn't grow unbounded
- Open project
- Perform 100 CRUD operations
- Verify memory doesn't grow >50MB
- Switch views 20 times
- Verify memory stabilized
- Long session (1 hour) stability

// e2e/performance/caching-validation.spec.ts
Test: Client-side caching works correctly
- Load items → Network request
- Reload items → No network request (cached)
- Modify item → Cache invalidated
- Reload after modification → Network request
- Background refetch → User sees fresh data
- Stale-while-revalidate pattern

// e2e/performance/lazy-loading-verification.spec.ts
Test: Lazy loading improves performance
- Initial page load with list
- Verify only first 20 items loaded
- Scroll down
- Next 20 items load on-demand
- No jank during lazy load
- All items eventually available
```

#### 4. Accessibility Testing (Expand: +6 specs)

```typescript
// e2e/accessibility/wcag-2.1-compliance.spec.ts
Test: WCAG 2.1 AA compliance
- Headings hierarchy correct (H1 → H2 → H3)
- All images have alt text
- All buttons have accessible labels
- Focus indicators visible
- Color not only way to convey info
- Sufficient color contrast (WCAG AA minimum)
- Verify with axe accessibility checker

// e2e/accessibility/keyboard-only-navigation.spec.ts
Test: Full navigation with keyboard only (no mouse)
- Tab through all interactive elements
- Shift+Tab to go backwards
- Enter to activate buttons
- Space to toggle checkboxes
- Arrow keys in lists
- Escape to close dialogs
- All features accessible via keyboard

// e2e/accessibility/screen-reader-testing.spec.ts
Test: Compatibility with screen readers (NVDA/JAWS)
- Page structure announced correctly
- Form labels announced with inputs
- Buttons have accessible names
- Links have meaningful text
- ARIA labels where needed
- Dynamic content updates announced
- Lists announced as lists with count

// e2e/accessibility/zoom-and-text-scaling.spec.ts
Test: Usability at 200% zoom
- Page content readable at 200% zoom
- No horizontal scrolling at 200%
- Form inputs accessible at zoom
- Buttons clickable at zoom
- Text size override respected (browser setting)
- Responsive at larger text sizes

// e2e/accessibility/motion-sensitivity.spec.ts
Test: Respects motion preferences
- Animations disabled if prefers-reduced-motion
- Transitions still smooth (not instant)
- Auto-play videos paused if prefers-no-motion
- Scrolling behavior normal

// e2e/accessibility/dark-mode-contrast.spec.ts
Test: Contrast maintained in dark mode
- Text/background contrast >= 4.5:1 (AA)
- Form inputs visible in dark mode
- Focus indicators visible in dark
- Graphs readable in dark mode
```

#### 5. Security Testing (Expand: +6 specs)

```typescript
// e2e/security/authentication-security.spec.ts
Test: Authentication security
- Password field masked
- Token not exposed in URL
- Token cleared on logout
- Expired token triggers re-login
- CSRF token validation
- No session fixation vulnerability

// e2e/security/authorization-enforcement.spec.ts
Test: Authorization enforcement
- User cannot access others' projects
- User cannot edit without permission
- User cannot delete without permission
- Admin can override permissions
- Role-based access control verified
- Permission changes take effect immediately

// e2e/security/xss-prevention.spec.ts
Test: XSS prevention
- HTML in item title rendered as text
- Script tags not executed
- Event handlers not executed
- SVG injection prevented
- JSON injection prevented
- User input sanitized

// e2e/security/csrf-protection.spec.ts
Test: CSRF protection
- Forms include CSRF token
- Requests include CSRF header
- Invalid CSRF token rejected
- Token refresh works

// e2e/security/sql-injection-prevention.spec.ts
Test: SQL injection prevention
- Quote injection in search
- OR statements in search
- Parameterized queries used
- No raw SQL in logs

// e2e/security/rate-limiting.spec.ts
Test: Rate limiting prevents abuse
- 100 requests in 10s → Throttled
- 429 response returned
- Rate limit header shows reset time
- Different endpoints have separate limits
- Rate limit doesn't affect legitimate users
```

#### 6. Cross-Browser Testing (Expand: +3 specs)

```typescript
// e2e/cross-browser/chromium-webkit-firefox.spec.ts
Test: Functionality across browsers
- Run all critical flows in:
  - Chromium (Chrome)
  - Firefox
  - WebKit (Safari)
- Verify identical behavior
- Performance similar across browsers
- No console errors in any browser

// e2e/cross-browser/mobile-browsers.spec.ts
Test: Mobile browser compatibility
- iPhone Safari (iOS)
- Android Chrome
- Samsung Internet
- All critical flows work
- Touch interactions work
- Viewport adjustments correct

// e2e/cross-browser/older-browser-support.spec.ts
Test: Fallback behavior for older browsers
- Graceful degradation (if supporting older browsers)
- Essential features work
- Enhanced features disabled if not supported
- Clear messaging for unsupported features
```

#### 7. Edge Cases & Error Scenarios (Expand: +5 specs)

```typescript
// e2e/edge-cases/network-resilience.spec.ts
Test: Handle network issues gracefully
- Network offline → Show offline message
- Network slow (5G) → Show loading
- Network disconnects → Auto-retry
- Network reconnects → Sync data
- Mixed online/offline → Queue operations

// e2e/edge-cases/boundary-conditions.spec.ts
Test: Handle boundary conditions
- Create item with empty title → Error
- Create 10k items in one project
- Create very long item description (10k chars)
- Create circular link dependencies → Cycle detection
- Delete item with 1000 links → Verify cascade
- Filter with 1000 items in result

// e2e/edge-cases/concurrent-operations.spec.ts
Test: Handle concurrent operations
- Open same item in two tabs
- Edit in both simultaneously
- Conflict resolution shown
- Merge or overwrite option
- Verify final state correct
- No data loss

// e2e/edge-cases/storage-limits.spec.ts
Test: Handle storage limits
- LocalStorage quota exceeded → Fallback to memory
- SessionStorage issues → Graceful handling
- Database backup space → Warning to user
- Cache eviction → LRU strategy

// e2e/edge-cases/error-recovery.spec.ts
Test: Recover from errors gracefully
- Create item → Network error → Retry visible
- Import → Server error → Resume option
- Graph render → Out of memory → Fallback view
- Search → Timeout → Partial results
- Export → Disk full → Clear message
```

### E2E Test Execution Plan

**Phase 1 (Weeks 1-2): Critical Journey Tests**
- Add 8 critical flow specs
- Run on every commit

**Phase 2 (Weeks 3-4): Feature Coverage**
- Add 12 feature specs
- Run on every commit

**Phase 3 (Week 5): Performance Baseline**
- Add 8 performance specs
- Establish baselines
- Run on every merge to main

**Phase 4 (Week 6): Security & Accessibility**
- Add 12 security/accessibility specs
- Run weekly

**Phase 5 (Week 7): Edge Cases & Cross-browser**
- Add 8 edge case specs
- Cross-browser tests
- Run on release candidates

---

## Performance & Load Testing

### Performance Testing Strategy

#### 1. Client-Side Performance (Frontend)

**Web Vitals Monitoring:**
```typescript
// e2e/performance/web-vitals.spec.ts
- Largest Contentful Paint (LCP) < 2.5s
- First Input Delay (FID) < 100ms
- Cumulative Layout Shift (CLS) < 0.1
- Time to First Byte (TTFB) < 600ms
- First Contentful Paint (FCP) < 1.8s
```

**Bundle Size Analysis:**
```bash
# Measure bundle sizes
bun run build

# Analyze bundle composition
bun run analyze-bundle

# Target sizes:
# - Main JS: < 150KB (gzipped)
# - CSS: < 50KB (gzipped)
# - Total: < 250KB (gzipped)
```

**Rendering Performance:**
```typescript
// e2e/performance/rendering-performance.spec.ts
- Initial page load: < 2s
- View switches: < 500ms
- List item render: < 50ms per item
- Graph initial render: < 3s (500 nodes)
- Scroll smoothness: 60 FPS
- Zoom/pan smoothness: 60 FPS
```

#### 2. Server-Side Performance (Backend)

**Request Latency Baselines:**
```python
# tests/performance/test_api_latency.py
GET /api/v1/items - p99 < 200ms
GET /api/v1/items?limit=100 - p99 < 500ms
POST /api/v1/items - p99 < 300ms
GET /api/v1/analysis/impact/{id} - p99 < 1000ms (complexity dependent)
POST /api/v1/projects/{id}/import - p99 < 30s (10k items)
```

**Database Query Performance:**
```python
# tests/integration/database/test_query_performance.py
- Simple item fetch: < 10ms
- Item with links fetch: < 50ms
- List with filters: < 100ms (1000 items)
- Cycle detection: < 1000ms (500 nodes)
- Impact analysis: < 2000ms (500 nodes)
```

**Memory & Resource Usage:**
```python
# tests/performance/test_memory_usage.py
- API process baseline: < 100MB
- Per-request memory overhead: < 10MB
- Cache memory growth: < 500MB max
- Database connection pool: < 50MB
- Event log size management (archival)
```

### Load Testing Strategy

#### 1. Load Test Scenarios

**Scenario 1: Normal Load (Baseline)**
```python
# tests/performance/load_tests/test_normal_load.py
- 50 concurrent users
- 5 requests/second total
- 30 minute duration
- Success rate: > 99%
- p95 latency: < 500ms
- p99 latency: < 2s
```

**Scenario 2: Peak Load**
```python
# tests/performance/load_tests/test_peak_load.py
- 200 concurrent users
- 20 requests/second total
- 15 minute duration
- Success rate: > 95%
- p95 latency: < 1s
- p99 latency: < 5s
- Monitor for 503 errors
```

**Scenario 3: Stress Test**
```python
# tests/performance/load_tests/test_stress_load.py
- 500 concurrent users
- Increase by 50 users every 30s
- Until system breaks
- Record breaking point
- Monitor recovery
```

**Scenario 4: Spike Test**
```python
# tests/performance/load_tests/test_spike_load.py
- 50 users baseline
- Spike to 500 users in 10s
- Hold for 5 minutes
- Drop back to 50
- Verify recovery
```

#### 2. Load Test Tools

**Tool Options:**
- **Locust** (Python-based, great for API testing)
- **K6** (Go-based, excellent performance)
- **Apache JMeter** (Java, widely used)
- **Artillery.io** (Node-based, easy scripting)

**Recommended: K6 for backend + Playwright for frontend load**

#### 3. Load Test Scripts

```python
# Backend load test (using K6)
# tests/performance/load_tests/k6_basic_flow.js

import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 50,
  duration: '30m',
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<2000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  // 1. Login
  const loginRes = http.post('http://localhost:8000/api/auth/login', {
    email: 'user@example.com',
    password: 'password',
  });
  check(loginRes, { 'login succeeded': (r) => r.status === 200 });

  const token = loginRes.json('token');

  // 2. List items
  const itemsRes = http.get('http://localhost:8000/api/v1/items', {
    headers: { Authorization: `Bearer ${token}` },
  });
  check(itemsRes, { 'items listed': (r) => r.status === 200 });

  // 3. Create item
  const createRes = http.post(
    'http://localhost:8000/api/v1/items',
    {
      title: `Item ${__VU}-${__ITER}`,
      description: 'Load test item',
    },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  check(createRes, { 'item created': (r) => r.status === 201 });

  // 4. Get analysis
  const analysisRes = http.get(
    `http://localhost:8000/api/v1/analysis/impact/${createRes.json('id')}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  check(analysisRes, { 'analysis retrieved': (r) => r.status === 200 });
}
```

### Stress Testing Strategy

**Database Connection Stress:**
```python
# tests/performance/stress_tests/test_db_connection_stress.py
- Create 100 concurrent connections
- Verify pool handles it
- Create 1000 queries simultaneously
- Verify queuing/handling
- Monitor connection timeouts
- Verify graceful degradation
```

**Memory Stress:**
```python
# tests/performance/stress_tests/test_memory_stress.py
- Create 10k items in memory
- Create 100k links in memory
- Verify cache eviction works
- Verify no memory leaks
- Measure peak memory usage
```

**Concurrent Modification Stress:**
```python
# tests/performance/stress_tests/test_concurrent_modification.py
- 100 concurrent item modifications
- 100 concurrent link creations
- 100 concurrent deletes
- Verify ACID properties
- Detect deadlocks
- Measure conflict resolution
```

---

## Security Testing

### Security Test Plan

#### 1. Authentication & Authorization (Expand: +5 tests)

**Backend Tests:**
```python
# tests/security/test_authentication.py
- Valid credentials → Token
- Invalid credentials → 401
- Expired token → 401 or refresh needed
- Invalid token → 401
- Token refresh → New token
- Logout → Token invalidation
- Password hashing (bcrypt)
- Token signing verification

# tests/security/test_authorization.py
- User can access own data
- User cannot access others' data
- Role-based access control
  - Admin: full access
  - Editor: create/edit/delete own
  - Viewer: read-only
  - Guest: limited read-only
- Permission changes take effect
- Cascading permissions (project → items)
```

**Frontend Tests:**
```typescript
// src/__tests__/security/test_auth_token_handling.test.ts
- Token stored securely (httpOnly cookie or secure localStorage)
- Token not exposed in URL
- Token cleared on logout
- Token refreshed automatically
- Expired token triggers re-login
- XSS cannot access token
```

#### 2. Input Validation & Sanitization (Expand: +5 tests)

**Backend Tests:**
```python
# tests/security/test_input_validation.py
- Item title: max 255 chars
- Item description: max 10k chars
- Project name: alphanumeric + spaces
- Email format validation
- URL format validation
- Date format validation
- Enum validation (status, view, type)
- Custom validation rules

# tests/security/test_xss_prevention.py
- HTML in title rendered as text (not executed)
- Script tags in description escaped
- Event handlers stripped (onload, onclick, etc.)
- SVG injection prevented
- DOM-based XSS prevented
- User content sanitization
```

**Frontend Tests:**
```typescript
// src/__tests__/security/test_input_sanitization.test.ts
- Form input validation
- Required field validation
- Format validation (email, URL)
- Range validation (numbers)
- Length validation (strings)
- Enum validation
- Custom rule validation
- Validation error messages shown
```

#### 3. SQL Injection Prevention

```python
# tests/security/test_sql_injection_prevention.py
- Quote injection in search: ' OR '1'='1'
- OR statements in filter: status='done' OR 1=1
- Comment injection: '; --
- Union injection: UNION SELECT
- Parameterized queries verified
- ORM prevents raw SQL injection
```

#### 4. CSRF Protection

```python
# tests/security/test_csrf_protection.py
- CSRF token generated on form page
- CSRF token included in POST requests
- Invalid CSRF token → 403
- Missing CSRF token → 403 or 400
- Token refresh works
- Double-submit cookie pattern (if used)
```

#### 5. API Security (Expand: +5 tests)

```python
# tests/security/test_api_security.py
- API requires authentication (except public endpoints)
- API returns minimal error info (no stack traces)
- API rate limiting implemented
- API CORS configured correctly
- API headers security:
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - Content-Security-Policy
  - Strict-Transport-Security (HTTPS)
- API versioning (v1 backward compatibility)
```

#### 6. Data Protection

```python
# tests/security/test_data_protection.py
- Passwords hashed (never stored plain)
- Sensitive fields encrypted at rest (if applicable)
- Secure cookie flags (httpOnly, Secure, SameSite)
- No sensitive data in logs
- PII redaction in error messages
- Data deletion (GDPR compliance)
```

#### 7. Dependency Security

```bash
# Run vulnerability scans
# Backend
pip audit
poetry check

# Frontend
npm audit
bun audit

# Docker images
docker scan backend:latest

# Track CVEs with dependabot/snyk
```

---

## Accessibility Testing

### WCAG 2.1 AA Compliance

#### 1. Structure & Semantics

```typescript
// src/__tests__/a11y/test_semantics.test.tsx
- Proper heading hierarchy (H1 > H2 > H3)
- No skipped heading levels
- Lists use <ul>, <ol>, <li>
- Tables have <thead>, <tbody>, proper <th>
- Form labels properly associated with inputs
- Buttons have accessible names
- Links have meaningful text (not "click here")
```

#### 2. Color & Contrast

```typescript
// src/__tests__/a11y/test_color_contrast.test.tsx
- Text contrast >= 4.5:1 (normal text)
- Text contrast >= 3:1 (large text)
- Color not only way to convey info
- Dark mode contrast verified
- Graph colors accessible
- Links distinguishable from text
```

#### 3. Keyboard Navigation

```typescript
// src/__tests__/a11y/test_keyboard_navigation.test.tsx
- All interactive elements focusable (Tab key)
- Tab order logical
- Focus indicator visible
- No keyboard traps
- Escape closes modals/menus
- Enter activates buttons
- Space activates checkboxes/toggles
- Arrow keys in lists/trees/comboboxes
```

#### 4. Screen Reader Support

```typescript
// src/__tests__/a11y/test_screen_reader.test.tsx
- Page title descriptive
- Heading structure announced correctly
- Form labels announced with inputs
- Button purposes announced
- ARIA labels for icon buttons
- Dynamic content updates announced (aria-live)
- Inaccessible to screen readers: aria-hidden on decorative elements
- Status updates announced (role="status", aria-live)
```

#### 5. Zoom & Text Scaling

```typescript
// src/__tests__/a11y/test_zoom_scaling.test.tsx
- Page functional at 200% zoom
- No horizontal scrolling at 200% zoom
- Text size overrides work (browser text size setting)
- Responsive layout adjusts for larger text
- Form inputs remain accessible with text zoom
- Images have alt text for context
```

#### 6. Motion & Animation

```typescript
// src/__tests__/a11y/test_motion.test.tsx
- Animations respect prefers-reduced-motion
- Flashing/strobing: no more than 3 times/second
- Auto-play videos paused
- Scroll behavior not essential to function
- Parallax effects have text alternative
```

#### 7. Automation Testing (Axe)

```bash
# Install axe accessibility scanner
npm install --save-dev @axe-core/react axe-core

# Test component accessibility
import { axe } from 'jest-axe';

test('button accessible', async () => {
  const { container } = render(<Button>Click me</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Testing Gaps & Remediation

### Gap Analysis Matrix

| Layer | Current | Gap | Priority | Effort | Target |
|-------|---------|-----|----------|--------|--------|
| **Unit Tests** | 350 files | +15 files | High | 2 weeks | 365 files |
| **Integration Tests** | 150 files | +30 files | High | 3 weeks | 180 files |
| **E2E Tests** | 18 specs | +35 specs | High | 4 weeks | 53 specs |
| **Performance Tests** | 20 files | +30 tests | High | 2 weeks | 50 tests |
| **Security Tests** | Limited | +20 tests | High | 2 weeks | 20+ tests |
| **A11y Tests** | Limited | +15 tests | Medium | 1.5 weeks | 15+ tests |
| **Load Tests** | None | +10 tests | Medium | 2 weeks | 10+ tests |

### Remediation Roadmap

**Phase 1 (Weeks 1-2): Foundation**
- Add missing unit tests (+15 files)
- Document test infrastructure
- Set up performance baseline
- **Deliverable:** 365 unit tests, baseline metrics

**Phase 2 (Weeks 3-5): Integration**
- Add integration test suite (+30 files)
- Add service chain tests
- Add database concurrency tests
- **Deliverable:** 180 integration tests, 100% API endpoint coverage

**Phase 3 (Weeks 6-10): E2E & Performance**
- Add E2E critical journey tests (+8 specs)
- Add feature coverage tests (+12 specs)
- Add performance tests (+8 specs)
- Add load test scenarios (+5 tests)
- **Deliverable:** 53 E2E specs, performance baselines

**Phase 4 (Weeks 11-13): Security & A11y**
- Add security tests (+20 tests)
- Add accessibility tests (+15 tests)
- Run security audit
- Run accessibility audit
- **Deliverable:** Security and accessibility compliance report

**Phase 5 (Week 14+): Continuous Improvement**
- Monitor test metrics
- Fix flaky tests
- Optimize slow tests
- Update test data/mocks
- **Ongoing:** Maintain 85%+ coverage, <3s test suite, 100% E2E critical paths

---

## Implementation Roadmap

### Timeline Overview

```
Week 1-2: Unit Tests (+15)
   └─ models, services, utilities
   └─ Parallel: Backend + Frontend
   └─ Goal: 365 total unit tests

Week 3-5: Integration Tests (+30)
   └─ API endpoint chains
   └─ Database transactions
   └─ Service interactions
   └─ Goal: 180 integration tests

Week 6: E2E Critical Flows (+8)
   └─ Complete user journeys
   └─ Multi-step workflows
   └─ Goal: 26 E2E specs

Week 7-8: Feature Coverage E2E (+12)
   └─ Feature-specific tests
   └─ View switching
   └─ Real-time sync
   └─ Goal: 38 E2E specs

Week 9: Performance Baseline (+8)
   └─ Load testing setup
   └─ Performance benchmarks
   └─ Establish baselines
   └─ Goal: 8 performance specs

Week 10: Performance Advanced (+8)
   └─ Stress testing
   └─ Memory profiling
   └─ Query optimization
   └─ Goal: 50+ performance tests

Week 11: Security Tests (+20)
   └─ Auth/authz tests
   └─ Input validation
   └─ SQL injection prevention
   └─ Goal: 20 security tests

Week 12: Accessibility Tests (+15)
   └─ WCAG 2.1 AA compliance
   └─ Screen reader testing
   └─ Keyboard navigation
   └─ Goal: 15+ a11y tests

Week 13: Cross-Browser & Edge Cases (+8)
   └─ Chromium/Firefox/WebKit
   └─ Mobile browsers
   └─ Edge case scenarios
   └─ Goal: 8 edge case specs

Week 14: Documentation & Optimization
   └─ Test documentation
   └─ Flaky test fixes
   └─ Performance optimization
   └─ Goal: 100% documented test suite
```

### Resource Allocation

**Backend Testing (Python)**
- 1 Senior Test Engineer (full-time)
- Support: 1 Backend Engineer (part-time)
- Tools: pytest, pytest-asyncio, K6, Locust

**Frontend Testing (TypeScript/React)**
- 1 Senior Test Engineer (full-time)
- Support: 1 Frontend Engineer (part-time)
- Tools: Vitest, Playwright, Testing Library, MSW

**Performance & Security**
- 1 Specialist (full-time, weeks 9-13)
- Tools: K6, Artillery, OWASP ZAP, Axe

**Total Effort:** ~3.5 FTE for 14 weeks (~490 person-hours)

---

## Metrics & Success Criteria

### Code Coverage Targets

| Layer | Current | Target | Method |
|-------|---------|--------|--------|
| Backend Services | ~75% | 85% | pytest-cov |
| Backend APIs | ~70% | 80% | pytest-cov |
| Frontend Components | ~65% | 75% | vitest --coverage |
| Frontend Hooks | ~50% | 75% | vitest --coverage |
| Frontend Stores | ~70% | 85% | vitest --coverage |
| **Overall** | **~65%** | **80%** | Combined coverage |

### Test Execution Performance

| Metric | Target | Tool |
|--------|--------|------|
| Unit tests (backend) | < 10 min total | pytest-xdist |
| Unit tests (frontend) | < 5 min total | vitest |
| Integration tests | < 20 min total | pytest-xdist |
| E2E tests | < 15 min per spec | Playwright |
| Full suite | < 1 hour | CI/CD pipeline |
| Parallel execution | 8 workers | pytest -n auto, vitest --threads |

### Test Quality Metrics

| Metric | Target | Definition |
|--------|--------|------------|
| Flaky Test Rate | < 0.5% | Tests that intermittently fail |
| Test Maintenance | < 2% effort | % of dev time fixing tests |
| Test ROI | High | Bugs caught by tests / time spent |
| Mutation Score | > 80% | % of mutations killed by tests |
| Coverage Growth | 2% monthly | Coverage increase per month |

### Critical Path Coverage

| User Journey | E2E Coverage | Acceptance Criteria |
|--------------|--------------|---------------------|
| Create Project → Add Items → Analyze | 100% | Full journey automated |
| Requirements → Code → Test Tracing | 100% | All trace links tested |
| Multi-user Collaboration | 100% | Concurrent edits tested |
| Bulk Import Workflow | 100% | 10k item import tested |
| Search & Filter | 100% | All filter combinations tested |
| Mobile Responsiveness | 100% | Mobile, tablet, desktop tested |
| Performance SLAs | 100% | Load test baselines met |

### Automated Test Execution

**CI/CD Pipeline:**
```yaml
# GitHub Actions workflow
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backend unit tests
        run: pytest tests/unit/ -v --cov=src/tracertm
      - name: Frontend unit tests
        run: bun run test

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backend integration tests
        run: pytest tests/integration/ -v -m "not slow"

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: E2E tests (critical only on PR)
        run: bun run test:e2e -- --tag @critical

  performance:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Performance baselines
        run: pytest tests/performance/ -v

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Dependency audit
        run: |
          pip audit
          npm audit
      - name: SAST scan
        uses: github/super-linter@v4
```

### Success Criteria (Exit Criteria)

**Phase 1 Complete When:**
- [ ] 365 unit tests passing
- [ ] 80% code coverage for services
- [ ] Unit test suite runs in < 10 minutes
- [ ] No flaky tests

**Phase 2 Complete When:**
- [ ] 180 integration tests passing
- [ ] 100% API endpoint coverage
- [ ] Database concurrency tests passing
- [ ] Integration test suite runs in < 20 minutes

**Phase 3 Complete When:**
- [ ] 53 E2E specs passing
- [ ] All critical user journeys covered
- [ ] Performance baselines established
- [ ] Load test scenarios documented

**Phase 4 Complete When:**
- [ ] 20 security tests passing
- [ ] 15 accessibility tests passing
- [ ] WCAG 2.1 AA compliance verified
- [ ] Security audit clean

**Project Complete When:**
- [ ] 80%+ code coverage across all layers
- [ ] All critical paths covered by E2E tests
- [ ] Performance SLAs met (5s page load, 100ms API responses)
- [ ] Zero high-severity security issues
- [ ] WCAG 2.1 AA accessibility compliance
- [ ] <3s test execution for unit tests
- [ ] Full test suite runs in CI/CD < 1 hour

---

## Appendix: Test Execution Commands

### Backend Test Commands

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific marker
pytest -m "unit" tests/
pytest -m "integration" tests/
pytest -m "asyncio" tests/
pytest -m "performance" tests/

# With coverage
pytest --cov=src/tracertm --cov-report=html --cov-report=term-missing

# Parallel execution
pytest -n auto tests/

# Failing tests first
pytest --ff tests/

# Watch mode (with pytest-watch)
ptw tests/

# Specific test file
pytest tests/unit/services/test_cycle_detection_service.py -v

# Specific test function
pytest tests/unit/services/test_cycle_detection_service.py::test_detect_simple_cycles -v

# Slowest 10 tests
pytest --durations=10 tests/

# Stop on first failure
pytest -x tests/

# Database tests only
pytest tests/integration/database/ -v

# Performance benchmarks
pytest tests/performance/ -v --benchmark-only
```

### Frontend Test Commands

```bash
# All tests
bun run test

# Watch mode
bun run test -- --watch

# Specific file
bun run test -- src/__tests__/hooks/useItems.test.ts

# Specific pattern
bun run test -- --grep "useItems"

# Coverage
bun run test -- --coverage

# UI test viewer
bun run test -- --ui

# E2E tests
bun run test:e2e

# E2E with specific spec
bun run test:e2e -- auth.spec.ts

# E2E with tag
bun run test:e2e -- --grep @critical

# E2E headed mode (see browser)
bun run test:e2e -- --headed

# E2E debug mode
bun run test:e2e -- --debug
```

### Performance Testing Commands

```bash
# K6 load test
k6 run tests/performance/load_tests/k6_basic_flow.js

# K6 with specific scenario
k6 run --vus 100 --duration 5m tests/performance/load_tests/k6_basic_flow.js

# Python performance tests
pytest tests/performance/ -v --benchmark-only

# Generate HTML report
pytest tests/performance/ -v --benchmark-only --benchmark-html=report.html

# Memory profiling
python -m memory_profiler tests/performance/test_memory_usage.py

# Flame graphs (if using py-spy)
py-spy record -o profile.svg -- pytest tests/performance/test_memory_usage.py
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-24
**Next Review:** Weekly during implementation phases

