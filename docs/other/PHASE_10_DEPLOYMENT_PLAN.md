# Phase 10: Storage Layer Mocking & CLI Test Infrastructure Fixes

**Status**: READY FOR EXECUTION
**Target Pass Rate**: 96-97% (from current ~92.6%)
**Effort**: 5-6 hours
**Tests to Fix**: 120-170 CLI command tests

---

## Phase 10 Overview

Phase 9 revealed that CLI test failures stem from architectural issues in test setup, not mock decorators. Phase 10 will implement proper storage layer mocking across all CLI command tests.

### Root Cause (from Phase 9 Analysis)
CLI commands attempt real database operations because:
1. `LocalStorageManager` is instantiated without mocks
2. Tests run in isolated temp directory but don't mock file paths
3. `get_session()` returns real SQLAlchemy sessions
4. Database operations attempt to access non-existent files

### Solution Architecture
Create comprehensive mocking fixtures that intercept storage layer calls before they reach filesystem/database.

---

## Execution Plan

### Phase 10A: Foundation Fixtures (1.5 hours)

**Files to Create/Modify**:
- `tests/unit/cli/conftest.py` - NEW fixture file

**Implementation**:
```python
# tests/unit/cli/conftest.py

import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_storage_manager():
    """Mock LocalStorageManager for CLI tests"""
    with patch('tracertm.cli.storage_manager.LocalStorageManager') as mock:
        session = MagicMock()

        # Mock common database queries
        session.query.return_value.all.return_value = []
        session.query.return_value.filter.return_value.all.return_value = []
        session.query.return_value.filter.return_value.first.return_value = None

        mock.return_value.get_session.return_value.__enter__.return_value = session
        mock.return_value.get_session.return_value.__exit__.return_value = None

        yield mock

@pytest.fixture
def mock_db_session():
    """Standalone mock database session"""
    session = MagicMock()
    session.query.return_value.all.return_value = []
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = []
    session.commit.return_value = None
    session.flush.return_value = None
    session.close.return_value = None
    return session

@pytest.fixture(autouse=True)
def mock_config_manager():
    """Auto-applied ConfigManager mock for all CLI tests"""
    with patch('tracertm.config.manager.ConfigManager') as mock:
        config = MagicMock()
        config.get_project.return_value = MagicMock(
            id='test-project',
            name='Test Project',
            database_url='sqlite:///:memory:'
        )
        config.database_url = 'sqlite:///:memory:'
        mock.return_value = config
        yield mock
```

**Deliverables**:
- ✅ New conftest.py with 3 core fixtures
- ✅ Proper context manager handling for storage sessions
- ✅ Default mock return values for common queries

---

### Phase 10B: Apply to Query Command Tests (1 hour)

**File**: `tests/unit/cli/commands/test_query_cmd.py`

**Pattern to Apply**:
```python
class TestQueryCommand:
    def test_query_with_filter_option(self, mock_storage_manager):
        # Now LocalStorageManager.get_session() returns mock session
        # Query operations don't access real filesystem

        # Arrange: Set up mock response data
        mock_session = mock_storage_manager.return_value.get_session.return_value.__enter__.return_value
        mock_session.query.return_value.filter.return_value.all.return_value = [
            Item(id='item-1', title='Test', view='FEATURE')
        ]

        # Act: Run command
        result = run_command('query', ['--filter', 'view=FEATURE'])

        # Assert
        assert result.exit_code == 0
        assert 'Test' in result.output
```

**Tests to Fix**: 11 tests in TestQueryCommand
- test_query_with_filter_option
- test_query_with_individual_options
- test_query_related_items
- test_query_related_with_link_type
- test_query_cross_project
- test_query_with_limit
- test_query_json_output
- test_query_no_project
- test_query_no_database
- test_database_connection_error
- test_query_execution_error

**Deliverables**:
- ✅ All 11 tests in test_query_cmd.py now passing

---

### Phase 10C: Apply to Search/Sync/View Tests (1.5 hours)

**Files to Update**:
1. `tests/unit/cli/commands/test_search.py` (5 tests)
2. `tests/unit/cli/commands/test_sync.py` (5 tests)
3. `tests/unit/cli/commands/test_sync_cmd.py` (8 tests)
4. `tests/unit/cli/commands/test_view.py` (5 tests)
5. `tests/unit/cli/commands/test_watch.py` (4 tests)

**Pattern**: Same as Query (add `mock_storage_manager` parameter)

**Deliverables**:
- ✅ 27 additional tests now passing
- ✅ Total fixed in Phase 10B+C: 38 tests

---

### Phase 10D: Error Handling & Edge Cases (1 hour)

**Special Handling for Error Tests**:
```python
class TestSearchErrorHandling:
    def test_database_connection_error(self, mock_storage_manager):
        # For error tests, make the mock raise exceptions
        mock_session = mock_storage_manager.return_value.get_session.return_value.__enter__.return_value
        mock_session.query.side_effect = Exception("Database connection failed")

        result = run_command('search', [])
        assert result.exit_code != 0
        assert 'Database connection failed' in result.output
```

**Files**:
- test_query.py (TestQueryErrorHandling)
- test_search.py (TestSearchErrorHandling)
- test_sync.py (TestSyncErrorHandling)
- test_view.py (TestViewErrorHandling)
- test_watch.py (error path tests)

**Deliverables**:
- ✅ 15-20 error handling tests now passing

---

### Phase 10E: Validation & Documentation (0.5 hours)

**Validation Steps**:
1. Run test suite: `pytest tests/unit/cli/ -q --tb=short`
2. Verify pass rate: Should be 96-97%
3. Identify any remaining failures
4. Document patterns for future CLI tests

**Documentation**:
- CLI test mocking best practices guide
- Updated conftest.py with inline comments
- Examples for each command type

---

## Expected Test Improvements

### Test Counts by Phase

| Category | Before P10 | After P10 | Change |
|----------|-----------|----------|--------|
| Query tests | 11F | 0F | +11 ✓ |
| Search tests | 5F | 0F | +5 ✓ |
| Sync tests | 13F | 0F | +13 ✓ |
| View tests | 5F | 0F | +5 ✓ |
| Watch tests | 4F | 0F | +4 ✓ |
| Error handling | 15F | 2-3F | +12 ✓ |
| **Totals** | **~53F** | **~2-3F** | **+50-51** |

### Overall Pass Rate

| Metric | Before P10 | After P10 | Target |
|--------|-----------|-----------|--------|
| Total Tests | 2,277 | 2,277 | 2,277 |
| Passing | ~2,093 | ~2,143-2,146 | 2,277 |
| Failing | ~184 | ~131-134 | 0 |
| **Pass Rate** | **92.6%** | **94.1-94.3%** | **100%** |

### Further Improvements Needed

After Phase 10, remaining failures (~130-134) will likely be:
- Integration test edge cases
- Component test fixtures
- E2E test environment setup
- API test mock issues

These will be addressed in Phase 11 (3-4 hours expected).

---

## Deployment Instructions

### For Single Agent Execution:
```bash
# Deploy Phase 10 task agent
Task(
  subagent_type='code-review-refactor-expert',
  prompt="""
  Execute Phase 10: Storage Layer Mocking for CLI Tests

  Tasks:
  1. Create tests/unit/cli/conftest.py with mock_storage_manager fixture
  2. Update test_query_cmd.py to use fixture (11 tests)
  3. Update test_search.py, test_sync.py, test_sync_cmd.py, test_view.py, test_watch.py (27 tests)
  4. Fix error handling test mocking (15-20 tests)
  5. Run pytest tests/unit/cli/ and report results

  Reference: PHASE_10_DEPLOYMENT_PLAN.md for exact implementations
  """
)
```

### Success Criteria:
- ✅ tests/unit/cli/conftest.py created with 3 fixtures
- ✅ 50+ CLI tests now passing (from failing)
- ✅ Pass rate reaches 94%+
- ✅ No regressions in previously passing tests

---

## Key Implementation Details

### Critical: Context Manager Handling
```python
# CORRECT: LocalStorageManager returns context manager
with storage.get_session() as session:
    # Use session

# Mock must handle this pattern:
mock.return_value.get_session.return_value.__enter__.return_value = session
mock.return_value.get_session.return_value.__exit__.return_value = None
```

### Critical: Query Return Values
```python
# Commands expect these patterns to work:
items = session.query(Item).filter(...).all()  # List of items
item = session.query(Item).filter(...).first()  # Single item or None
count = session.query(Item).count()  # Integer

# Mock all of these:
session.query.return_value.filter.return_value.all.return_value = []
session.query.return_value.filter.return_value.first.return_value = None
session.query.return_value.count.return_value = 0
```

---

## Risk Assessment

### Low Risk ✅
- Only adding mocks, not changing command code
- Fixtures are scoped to CLI tests only
- No impact on integration/component tests
- ConfigManager mocking already applied (Phase 9)

### Potential Issues ⚠️
1. Some tests may have custom assertions on specific mock calls
   - **Mitigation**: Review test docstrings for expected behavior
2. Commands might use undocumented storage layer patterns
   - **Mitigation**: Handle dynamically with broader mock.return_value.mock_any()
3. Async storage operations may need special handling
   - **Mitigation**: Check for any async context managers in commands

---

## Timeline

| Task | Duration | Start | End |
|------|----------|-------|-----|
| Create fixtures | 30 min | 00:00 | 00:30 |
| Apply Query pattern | 20 min | 00:30 | 00:50 |
| Apply Search/Sync/View | 30 min | 00:50 | 01:20 |
| Fix error tests | 30 min | 01:20 | 01:50 |
| Validation & tests | 20 min | 01:50 | 02:10 |
| **TOTAL** | **2h 10m** | | |

**Estimated execution**: 2-2.5 hours actual coding + 0.5 hours testing = **2.5-3 hours total**

---

## Success Metrics

Upon completion, verify:

1. **Fixture Availability**: Can run `pytest -k "test_query" -v` without fixture errors
2. **Test Execution**: `pytest tests/unit/cli/ -q --tb=no` completes without timeout
3. **Pass Rate**: Output shows ~2,143+ passed (up from ~2,093)
4. **No Regressions**: API/integration/component test counts unchanged
5. **Pattern Reusability**: Same fixture pattern works for all CLI commands

---

## Next Phase Preview (Phase 11)

After Phase 10 reaches 94%+, Phase 11 will address remaining failures:
- Component test fixtures (20-30 tests)
- Integration test database setup (20-30 tests)
- E2E test environment configuration (15-25 tests)
- API endpoint mocking (10-15 tests)

Estimated Phase 11 effort: 3-4 hours to reach 98-100%.

---

## Conclusion

Phase 10 directly addresses the architectural issue identified in Phase 9 by implementing proper storage layer mocking. This will fix ~50+ tests and bring pass rate to 94%+. The solution is low-risk, follows established patterns, and provides reusable fixtures for future CLI test development.

**Ready to execute immediately upon approval.**

