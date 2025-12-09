# Coverage Improvement Plan: 85%+ Target

**Goal**: Improve test coverage for 4 critical areas from current levels to **85%+**

**Current Status**:
- Repositories: **40.16%** → Target: **85%+** (Gap: 44.84%)
- CLI Commands: **58.23%** → Target: **85%+** (Gap: 26.77%)
- TUI Module: **24.03%** → Target: **85%+** (Gap: 60.97%)
- Database: **39.08%** → Target: **85%+** (Gap: 45.92%)

---

## 📋 Executive Summary

This plan provides a structured approach to improve test coverage across four critical areas. Each area is broken down into phases with specific test files, methods to test, and estimated effort.

**Total Estimated Effort**: ~40-50 hours
- Phase 1 (Repositories): 12-15 hours
- Phase 2 (Database): 6-8 hours
- Phase 3 (CLI Commands): 15-20 hours
- Phase 4 (TUI Module): 7-10 hours

---

## 🎯 Phase 1: Repositories (40.16% → 85%+)

### Current Coverage Analysis

| File | Current | Target | Missing Lines | Priority |
|------|---------|--------|---------------|----------|
| `item_repository.py` | 32.12% | 85%+ | 38-42, 67, 79-84, 92-98, 108-129, 133-157, 161-172, 188, 204-216, 231->230, 240-246, 251-274, 278-299, 311-325 | 🔴 Critical |
| `project_repository.py` | 32.56% | 85%+ | 24-33, 44-45, 49-50, 60-73 | 🔴 Critical |
| `agent_repository.py` | 43.75% | 85%+ | 26-37, 41-42, 62-68, 72-78, 82-83 | 🟡 High |
| `event_repository.py` | 42.00% | 85%+ | 55-61, 69-75, 83-89, 98-118 | 🟡 High |
| `link_repository.py` | 50.00% | 85%+ | 26-37, 41-42, 53-56, 60-63, 67-72, 76-77, 81-86 | 🟡 High |

### Missing Functionality to Test

#### `item_repository.py` (129 statements, 82 missing)
**Untested Methods**:
- `create()` - Parent validation (lines 38-42)
- `get_by_id()` - Project scoping (line 67)
- `list_by_view()` - Include deleted flag (lines 79-84)
- `list_all()` - Include deleted flag (lines 92-98)
- `update()` - Optimistic locking, version checks (lines 108-129)
- `delete()` - Soft delete cascade, hard delete (lines 133-157)
- `restore()` - Restore soft-deleted items (lines 159-172)
- `get_by_project()` - Status filtering, pagination (lines 174-193)
- `get_by_view()` - Status filtering, pagination (lines 195-216)
- `query()` - Dynamic filtering (lines 218-236)
- `get_children()` - Child retrieval (lines 238-246)
- `get_ancestors()` - Recursive CTE queries (lines 248-274)
- `get_descendants()` - Recursive CTE queries (lines 276-299)
- `search()` - Full-text search (lines 301-325)

**Test File**: `tests/unit/repositories/test_item_repository_comprehensive.py`

**Test Cases Needed**:
```python
# Phase 1.1: CRUD Operations
- test_create_item_with_parent_validation()
- test_create_item_with_invalid_parent()
- test_create_item_with_parent_different_project()
- test_get_by_id_with_project_scope()
- test_get_by_id_without_project_scope()
- test_list_by_view_include_deleted()
- test_list_by_view_exclude_deleted()
- test_list_all_include_deleted()
- test_list_all_exclude_deleted()

# Phase 1.2: Update & Optimistic Locking
- test_update_with_correct_version()
- test_update_with_stale_version_raises_error()
- test_update_with_missing_item()
- test_update_multiple_fields()
- test_version_increments_on_update()

# Phase 1.3: Delete Operations
- test_soft_delete_item()
- test_soft_delete_cascades_to_children()
- test_hard_delete_item()
- test_hard_delete_removes_links()
- test_delete_nonexistent_item()
- test_restore_soft_deleted_item()
- test_restore_nonexistent_item()

# Phase 1.4: Query & Filtering
- test_get_by_project_with_status_filter()
- test_get_by_project_with_pagination()
- test_get_by_view_with_status_filter()
- test_get_by_view_with_pagination()
- test_query_with_single_filter()
- test_query_with_multiple_filters()
- test_query_with_limit()

# Phase 1.5: Tree Operations
- test_get_children_returns_direct_children()
- test_get_children_excludes_deleted()
- test_get_ancestors_returns_all_parents()
- test_get_ancestors_handles_deep_hierarchy()
- test_get_descendants_returns_all_children()
- test_get_descendants_handles_deep_hierarchy()

# Phase 1.6: Search
- test_search_by_title()
- test_search_by_description()
- test_search_with_multiple_terms()
- test_search_case_insensitive()
```

#### `project_repository.py` (35 statements, 21 missing)
**Untested Methods**:
- `create()` - Metadata handling (lines 24-33)
- `get_by_id()` - Basic retrieval (lines 44-45)
- `update()` - Update operations (lines 49-50)
- `list_all()` - Listing with filters (lines 60-73)

**Test File**: `tests/unit/repositories/test_project_repository_comprehensive.py`

**Test Cases Needed**:
```python
- test_create_project_with_metadata()
- test_create_project_without_metadata()
- test_get_by_id_existing_project()
- test_get_by_id_nonexistent_project()
- test_update_project_fields()
- test_list_all_projects()
- test_list_all_with_filters()
```

#### `agent_repository.py` (42 statements, 23 missing)
**Untested Methods**:
- `create()` - Agent creation (lines 26-37)
- `get_by_id()` - Retrieval (lines 41-42)
- `get_active_agents()` - Active agent filtering (lines 62-68)
- `update_status()` - Status updates (lines 72-78)
- `release_lock()` - Lock management (lines 82-83)

**Test File**: `tests/unit/repositories/test_agent_repository_comprehensive.py`

#### `event_repository.py` (40 statements, 19 missing)
**Untested Methods**:
- `create()` - Event creation (lines 55-61)
- `get_by_entity()` - Entity event retrieval (lines 69-75)
- `get_by_project()` - Project event filtering (lines 83-89)
- `get_recent()` - Recent events query (lines 98-118)

**Test File**: `tests/unit/repositories/test_event_repository_comprehensive.py`

#### `link_repository.py` (34 statements, 17 missing)
**Untested Methods**:
- `create()` - Link creation (lines 26-37)
- `get_by_id()` - Retrieval (lines 41-42)
- `get_by_source()` - Source item links (lines 53-56)
- `get_by_target()` - Target item links (lines 60-63)
- `delete()` - Link deletion (lines 67-72)
- `get_by_project()` - Project link filtering (lines 76-77, 81-86)

**Test File**: `tests/unit/repositories/test_link_repository_comprehensive.py`

### Implementation Plan

**Step 1**: Create comprehensive test files for each repository
- Use existing `tests/integration/repositories/test_repositories_integration.py` as reference
- Create unit tests with mocked sessions for faster execution
- Add integration tests for complex queries

**Step 2**: Test Coverage Areas
1. **CRUD Operations** (Create, Read, Update, Delete)
2. **Query Methods** (Filtering, pagination, sorting)
3. **Error Handling** (Validation, not found, concurrency)
4. **Edge Cases** (Empty results, boundary conditions)
5. **Optimistic Locking** (Version conflicts, concurrent updates)
6. **Soft Delete** (Cascade, restore operations)
7. **Tree Operations** (Ancestors, descendants, children)

**Step 3**: Run Coverage & Verify
```bash
pytest tests/unit/repositories/ --cov=src/tracertm/repositories --cov-report=term-missing
```

**Estimated Effort**: 12-15 hours

---

## 🎯 Phase 2: Database (39.08% → 85%+)

### Current Coverage Analysis

| File | Current | Target | Missing Lines | Priority |
|------|---------|--------|---------------|----------|
| `database/connection.py` | 39.08% | 85%+ | 101-104, 113-116, 128-166, 181-184, 188-191, 210-214, 227-234 | 🔴 Critical |
| `core/database.py` | 31.71% | 85%+ | 19-32, 38-45, 51-60, 65-67, 72-74 | 🟡 High |

### Missing Functionality to Test

#### `database/connection.py` (71 statements, 39 missing)
**Untested Methods**:
- `create_tables()` - Schema creation (lines 101-104)
- `drop_tables()` - Schema deletion (lines 113-116)
- `health_check()` - Health monitoring (lines 128-166)
  - PostgreSQL version check
  - SQLite version check
  - Table counting
  - Pool status
  - Error handling
- `get_session()` - Session factory (lines 181-184)
- `close()` - Connection cleanup (lines 188-191)
- `get_engine()` - Global engine management (lines 210-214)
- `get_session()` - Session generator (lines 227-234)

**Test File**: `tests/unit/database/test_connection_comprehensive.py`

**Test Cases Needed**:
```python
# Phase 2.1: Connection Management
- test_connect_with_postgresql_url()
- test_connect_with_sqlite_url()
- test_connect_with_invalid_url_raises_error()
- test_connect_creates_engine()
- test_connect_creates_session_factory()
- test_connect_tests_connection()
- test_connect_handles_connection_failure()

# Phase 2.2: Schema Operations
- test_create_tables_creates_all_tables()
- test_create_tables_raises_if_not_connected()
- test_drop_tables_drops_all_tables()
- test_drop_tables_raises_if_not_connected()

# Phase 2.3: Health Checks
- test_health_check_postgresql_returns_status()
- test_health_check_postgresql_returns_version()
- test_health_check_postgresql_returns_table_count()
- test_health_check_postgresql_returns_pool_info()
- test_health_check_sqlite_returns_status()
- test_health_check_sqlite_returns_version()
- test_health_check_sqlite_returns_table_count()
- test_health_check_handles_errors()
- test_health_check_raises_if_not_connected()

# Phase 2.4: Session Management
- test_get_session_returns_session()
- test_get_session_raises_if_not_connected()
- test_get_session_generator_yields_session()
- test_get_session_generator_closes_on_exit()

# Phase 2.5: Connection Cleanup
- test_close_disposes_engine()
- test_close_resets_engine()
- test_close_resets_session_factory()

# Phase 2.6: Global Functions
- test_get_engine_creates_connection()
- test_get_engine_reuses_connection()
- test_get_session_generator_creates_session()
```

#### `core/database.py` (37 statements, 24 missing)
**Untested Methods**:
- Database initialization (lines 19-32)
- Connection pooling (lines 38-45)
- Async session management (lines 51-60)
- Error handling (lines 65-67, 72-74)

**Test File**: `tests/unit/core/test_database_comprehensive.py`

### Implementation Plan

**Step 1**: Create test files with database fixtures
- Use SQLite for fast unit tests
- Use PostgreSQL for integration tests
- Mock connection failures for error handling

**Step 2**: Test Coverage Areas
1. **Connection Management** (Connect, disconnect, pooling)
2. **Schema Operations** (Create, drop tables)
3. **Health Monitoring** (Status checks, version info)
4. **Session Management** (Session creation, cleanup)
5. **Error Handling** (Connection failures, invalid URLs)
6. **Pool Management** (Pool size, overflow, pre-ping)

**Step 3**: Run Coverage & Verify
```bash
pytest tests/unit/database/ tests/unit/core/test_database*.py --cov=src/tracertm/database --cov=src/tracertm/core/database --cov-report=term-missing
```

**Estimated Effort**: 6-8 hours

---

## 🎯 Phase 3: CLI Commands (58.23% → 85%+)

### Current Coverage Analysis

**Critical Files (0-20% coverage)**:
- `cli/commands/test.py` - **0.00%** (223 statements)
- `cli/commands/test/app.py` - **0.00%** (218 statements)
- `cli/commands/history.py` - **6.12%** (204 statements, 186 missing)
- `cli/commands/state.py` - **15.48%** (66 statements, 53 missing)
- `cli/commands/progress.py` - **9.95%** (185 statements, 163 missing)
- `cli/commands/watch.py` - **18.99%** (71 statements, 56 missing)

**Medium Priority (30-60% coverage)**:
- `cli/commands/export.py` - **30.41%** (110 statements, 70 missing)
- `cli/commands/item.py` - **40.39%** (845 statements, 466 missing) - Largest file
- `cli/commands/agents.py` - **54.57%** (248 statements, 110 missing)
- `cli/commands/tui.py` - **54.76%** (76 statements, 34 missing)
- `cli/commands/chaos.py` - **59.71%** (158 statements, 59 missing)
- `cli/commands/migrate.py` - **58.37%** (167 statements, 67 missing)
- `cli/commands/search.py` - **50.00%** (98 statements, 50 missing)
- `cli/commands/ingest.py` - **62.21%** (132 statements, 45 missing)

**Near Target (70-85% coverage)**:
- `cli/commands/init.py` - **74.77%** (255 statements, 50 missing)
- `cli/commands/query.py` - **76.88%** (122 statements, 23 missing)
- `cli/commands/sync.py` - **84.69%** (295 statements, 46 missing)

### Missing Functionality to Test

#### `cli/commands/test.py` (0% coverage - 223 statements)
**Untested Functionality**:
- Test discovery across languages
- Test execution orchestration
- Test result aggregation
- Coverage reporting
- Traceability matrix generation
- Domain/functional grouping

**Test File**: `tests/unit/cli/commands/test_test_command.py`

**Test Cases Needed**:
```python
# Phase 3.1: Test Discovery
- test_discover_python_tests()
- test_discover_go_tests()
- test_discover_typescript_tests()
- test_discover_with_domain_filter()
- test_discover_with_epic_filter()
- test_discover_with_marker_filter()

# Phase 3.2: Test Execution
- test_run_all_tests()
- test_run_python_tests_only()
- test_run_go_tests_only()
- test_run_e2e_tests_only()
- test_run_with_domain_filter()
- test_handle_test_failures()

# Phase 3.3: Result Aggregation
- test_aggregate_results_from_multiple_languages()
- test_format_results_table()
- test_generate_summary_statistics()

# Phase 3.4: Coverage Reporting
- test_generate_coverage_report()
- test_merge_coverage_across_languages()

# Phase 3.5: Traceability Matrix
- test_generate_traceability_matrix()
- test_matrix_includes_test_metadata()
```

#### `cli/commands/history.py` (6.12% coverage - 204 statements, 186 missing)
**Untested Functionality**:
- Show item history
- Temporal queries (--at flag)
- Event filtering
- History formatting
- Date parsing (ISO and date-only formats)

**Test File**: `tests/unit/cli/commands/test_history_command.py`

**Test Cases Needed**:
```python
# Phase 3.6: History Display
- test_show_history_for_item()
- test_show_history_with_limit()
- test_show_history_nonexistent_item()
- test_show_history_no_events()

# Phase 3.7: Temporal Queries
- test_history_at_specific_date()
- test_history_at_specific_datetime()
- test_history_at_invalid_date_format()
- test_history_at_date_before_item_creation()
- test_history_at_date_after_item_deletion()

# Phase 3.8: Event Filtering
- test_history_filters_by_event_type()
- test_history_filters_by_agent()
- test_history_shows_creation_event()
- test_history_shows_update_events()
- test_history_shows_deletion_event()

# Phase 3.9: Date Parsing
- test_parse_iso_datetime()
- test_parse_date_only()
- test_parse_invalid_date_raises_error()
- test_parse_date_with_timezone()
```

#### `cli/commands/item.py` (40.39% coverage - 845 statements, 466 missing)
**Largest CLI file - needs comprehensive testing**

**Untested Functionality**:
- Item creation with all options
- Item updates
- Item deletion
- Item listing with filters
- Item search
- Item linking
- Bulk operations
- Export/import

**Test File**: `tests/unit/cli/commands/test_item_command_comprehensive.py`

**Test Cases Needed** (Sample - full list would be 50+ tests):
```python
# Phase 3.10: Item CRUD
- test_create_item_basic()
- test_create_item_with_all_options()
- test_create_item_with_parent()
- test_create_item_invalid_project()
- test_update_item()
- test_delete_item_soft()
- test_delete_item_hard()

# Phase 3.11: Item Listing
- test_list_items_by_view()
- test_list_items_with_status_filter()
- test_list_items_with_pagination()
- test_list_items_with_search()

# Phase 3.12: Item Operations
- test_link_items()
- test_unlink_items()
- test_bulk_update()
- test_bulk_delete()
```

#### `cli/commands/state.py` (15.48% coverage - 66 statements, 53 missing)
**Untested Functionality**:
- State display
- State transitions
- State validation

**Test File**: `tests/unit/cli/commands/test_state_command.py`

#### `cli/commands/progress.py` (9.95% coverage - 185 statements, 163 missing)
**Untested Functionality**:
- Progress tracking
- Progress reporting
- Progress calculations

**Test File**: `tests/unit/cli/commands/test_progress_command.py`

#### `cli/commands/watch.py` (18.99% coverage - 71 statements, 56 missing)
**Untested Functionality**:
- File watching
- Change detection
- Auto-sync

**Test File**: `tests/unit/cli/commands/test_watch_command.py`

### Implementation Plan

**Step 1**: Prioritize by Impact
1. **Critical**: `test.py`, `history.py`, `state.py`, `progress.py`, `watch.py` (0-20%)
2. **High**: `item.py` (largest file, 40%)
3. **Medium**: `export.py`, `agents.py`, `search.py`, `ingest.py` (30-60%)
4. **Low**: `init.py`, `query.py`, `sync.py` (70-85%)

**Step 2**: Create Test Files
- Use `typer.testing.CliRunner` for CLI testing
- Mock storage/database dependencies
- Test both success and error paths
- Test argument parsing and validation

**Step 3**: Test Coverage Areas
1. **Command Execution** (Success paths, error handling)
2. **Argument Parsing** (Required args, optional args, flags)
3. **Output Formatting** (Tables, trees, progress bars)
4. **Error Handling** (Validation errors, not found errors)
5. **Integration** (Storage operations, database queries)

**Step 4**: Run Coverage & Verify
```bash
pytest tests/unit/cli/commands/ --cov=src/tracertm/cli/commands --cov-report=term-missing
```

**Estimated Effort**: 15-20 hours

---

## 🎯 Phase 4: TUI Module (24.03% → 85%+)

### Current Coverage Analysis

| File | Current | Target | Missing Lines | Priority |
|------|---------|--------|---------------|----------|
| `tui/adapters/storage_adapter.py` | 24.03% | 85%+ | 62-63, 79-80, 107-121, 134-136, 169-187, 216-232, 242-247, 272-275, 302-305, 320-322, 339, 352-360, 372-406, 418, 431-442, 451, 467-509, 527-532, 546-551, 565-570, 574-579, 583-587, 591-595 | 🔴 Critical |
| `tui/apps/browser.py` | 21.48% | 85%+ | 14-35, 78-83, 87-99, 103-105, 109-115, 119-122, 126-143, 147-155, 159-161, 165-188, 193, 197, 201-202, 206, 210-218 | 🟡 High |
| `tui/apps/dashboard.py` | 18.34% | 85%+ | 14-34, 84-88, 92-108, 112-115, 119-125, 129-132, 136-142, 146-150, 154-192, 196-211, 220-224, 229-235, 239, 244, 248, 252-261 | 🟡 High |
| `tui/apps/dashboard_v2.py` | 17.02% | 85%+ | 20-49, 131-141, 145-166, 170-174, 178-181, 185-196, 201-207, 211, 215-223, 227-236, 240-270, 274-287, 297-303, 307-313, 317-318, 322-346, 351, 355-362, 366-376, 383-407, 411-420, 425-429, 433-444 | 🟡 High |
| `tui/apps/graph.py` | 20.86% | 85%+ | 15-34, 76-82, 86-97, 101-104, 108-114, 118-121, 125-147, 155-195, 199-200, 204-205, 209-210, 214, 218-226 | 🟡 High |
| `tui/widgets/conflict_panel.py` | 20.45% | 85%+ | 15-40, 114-116, 120-136, 140, 144-152, 162-164, 173-209, 213-214, 222-223, 231-232, 240, 244-251, 258-260, 266-275 | 🟡 High |
| `tui/widgets/sync_status.py` | 26.54% | 85%+ | 16-29, 90, 98, 102, 106, 110, 114, 118, 122, 127-177, 189-204, 213, 222, 231, 240, 249, 258, 273-291, 295, 299, 303, 307-321 | 🟡 High |
| `tui/widgets/view_switcher.py` | 39.13% | 85%+ | 6-9, 16, 20, 24-30 | 🟢 Medium |
| `tui/widgets/item_list.py` | 36.36% | 85%+ | 6-9, 16-17, 21-27 | 🟢 Medium |
| `tui/widgets/graph_view.py` | 46.67% | 85%+ | 6-9, 16-20 | 🟢 Medium |
| `tui/widgets/state_display.py` | 33.33% | 85%+ | 6-11, 18-19, 23-29 | 🟢 Medium |

### Strategy for TUI Testing

**Challenge**: TUI components are harder to test because they involve:
- UI rendering (Textual framework)
- User interactions (keyboard, mouse)
- Async event handling
- State management

**Approach**: Focus on business logic, not UI rendering
- Test widget initialization
- Test data loading methods
- Test event handlers (business logic)
- Test state management
- Use Textual's testing utilities where possible

### Missing Functionality to Test

#### `tui/adapters/storage_adapter.py` (24.03% coverage)
**Untested Functionality**:
- Storage operations
- Data loading
- Error handling
- Cache management

**Test File**: `tests/unit/tui/adapters/test_storage_adapter.py`

**Test Cases Needed**:
```python
# Phase 4.1: Storage Operations
- test_load_items_from_storage()
- test_save_items_to_storage()
- test_handle_storage_errors()
- test_cache_management()
```

#### `tui/apps/browser.py` (21.48% coverage)
**Untested Functionality**:
- App initialization
- Item browsing
- Navigation
- Search functionality

**Test File**: `tests/unit/tui/apps/test_browser_app.py`

**Test Cases Needed**:
```python
# Phase 4.2: Browser App
- test_app_initialization()
- test_load_items()
- test_navigate_to_item()
- test_search_items()
- test_handle_keyboard_events()
```

#### `tui/widgets/conflict_panel.py` (20.45% coverage)
**Untested Functionality**:
- Conflict detection
- Conflict resolution UI
- Merge operations

**Test File**: `tests/unit/tui/widgets/test_conflict_panel.py`

#### `tui/widgets/sync_status.py` (26.54% coverage)
**Untested Functionality**:
- Sync status display
- Status updates
- Progress tracking

**Test File**: `tests/unit/tui/widgets/test_sync_status.py`

### Implementation Plan

**Step 1**: Create Test Infrastructure
- Use Textual's testing utilities (`textual.app.App`)
- Mock storage/database dependencies
- Focus on business logic, not rendering

**Step 2**: Test Coverage Areas
1. **Widget Initialization** (Setup, data loading)
2. **Business Logic** (Data processing, calculations)
3. **Event Handlers** (Key handlers, action handlers)
4. **State Management** (State updates, state queries)
5. **Error Handling** (Error states, error recovery)

**Step 3**: Run Coverage & Verify
```bash
pytest tests/unit/tui/ --cov=src/tracertm/tui --cov-report=term-missing
```

**Estimated Effort**: 7-10 hours

---

## 📊 Implementation Timeline

### Week 1: Repositories & Database
- **Days 1-2**: Repositories Phase 1 (item_repository, project_repository)
- **Days 3-4**: Repositories Phase 2 (agent_repository, event_repository, link_repository)
- **Day 5**: Database connection tests

### Week 2: CLI Commands (Critical)
- **Days 1-2**: CLI test.py and history.py (0-6% coverage)
- **Days 3-4**: CLI state.py, progress.py, watch.py (9-18% coverage)
- **Day 5**: CLI item.py (largest file, 40% coverage)

### Week 3: CLI Commands (Medium) & TUI
- **Days 1-2**: CLI export.py, agents.py, search.py, ingest.py
- **Days 3-4**: TUI adapters and apps
- **Day 5**: TUI widgets

### Week 4: Finalization & Verification
- **Days 1-2**: Run full coverage reports, identify remaining gaps
- **Days 3-4**: Fill remaining gaps to reach 85%+
- **Day 5**: Documentation and verification

---

## ✅ Success Criteria

### Coverage Targets
- ✅ Repositories: **85%+** (currently 40.16%)
- ✅ Database: **85%+** (currently 39.08%)
- ✅ CLI Commands: **85%+** (currently 58.23%)
- ✅ TUI Module: **85%+** (currently 24.03%)

### Quality Criteria
- ✅ All critical paths tested
- ✅ Error handling tested
- ✅ Edge cases covered
- ✅ Integration tests for complex flows
- ✅ Tests are maintainable and well-documented

### Verification Commands
```bash
# Check overall coverage
coverage report --show-missing | grep -E "(repositories|cli|tui|database|TOTAL)"

# Check specific modules
pytest tests/unit/repositories/ --cov=src/tracertm/repositories --cov-report=term-missing
pytest tests/unit/cli/commands/ --cov=src/tracertm/cli/commands --cov-report=term-missing
pytest tests/unit/tui/ --cov=src/tracertm/tui --cov-report=term-missing
pytest tests/unit/database/ --cov=src/tracertm/database --cov-report=term-missing

# Generate HTML report
pytest --cov=src/tracertm --cov-report=html
open htmlcov/index.html
```

---

## 📝 Notes

1. **Test Organization**: Follow existing test structure
   - Unit tests: `tests/unit/{module}/`
   - Integration tests: `tests/integration/{module}/`
   - Component tests: `tests/component/{module}/`

2. **Test Patterns**: Use existing fixtures and patterns
   - Database fixtures: `db_session`, `async_session`
   - Storage fixtures: `temp_storage`, `local_storage`
   - Mock patterns: `pytest-mock`, `unittest.mock`

3. **Coverage Measurement**: Use pytest-cov
   - `--cov=src/tracertm/{module}` for module-specific
   - `--cov-report=term-missing` for missing lines
   - `--cov-report=html` for HTML reports

4. **Priority**: Focus on critical paths first
   - Repositories (data layer) → Database (infrastructure) → CLI (user-facing) → TUI (UI)

5. **Maintainability**: Write clear, maintainable tests
   - Descriptive test names
   - Good test documentation
   - Reusable fixtures
   - Consistent patterns

---

**Last Updated**: 2025-12-06  
**Status**: Planning Phase  
**Next Step**: Begin Phase 1 (Repositories)
