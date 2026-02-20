# Phase 1: Fix 67 Failing Tests - Detailed Action Plan
## TraceRTM Python Test Coverage - Systematic Failure Resolution

**Target**: Fix all 67 failing tests to achieve 100% pass rate
**Status**: 35+ tests fixed, 32 remaining
**Priority**: CRITICAL - Blocking Phase 4 completion

---

## FAILING TESTS SUMMARY (32 Remaining)

### Category 1: Database Initialization (20+ failures)
These all stem from missing database setup in test fixtures

**Pattern**: All integration tests expecting database tables that aren't created

**Affected Test Files**:
- `tests/integration/test_epic3_query_command.py` (6 failures)
- `tests/integration/test_epic3_yaml_export.py` (3 failures)
- `tests/integration/test_epic4_cycle_detection.py` (2-3 failures)
- `tests/integration/test_epic4_auto_linking.py` (1 failure)
- `tests/integration/test_epic4_query_by_relationship.py` (1 failure)
- `tests/integration/test_epic6_multi_project.py` (3 failures)
- `tests/integration/test_epic7_progress_tracking.py` (6 failures)
- `tests/integration/test_epic7_search_filters.py` (3 failures)

**Root Cause**: Integration test fixtures don't run database migrations

**Solution**: Add database initialization to conftest.py

```python
# File: tests/conftest.py (or tests/integration/conftest.py)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.tracertm.database.base import Base
from src.tracertm.database.migrations import run_migrations

@pytest.fixture(scope="function")
def db_session():
    """Database session with all tables created"""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(engine)

    # Run migrations if needed
    # run_migrations(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    engine.dispose()

@pytest.fixture(scope="function")
def initialized_db():
    """Database with sample data for integration tests"""
    # Same as db_session but with sample projects/items created
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create sample project
    from src.tracertm.models import Project
    project = Project(id="test-project", name="Test Project")
    session.add(project)
    session.commit()

    yield session
    session.close()
    engine.dispose()
```

**Implementation Steps**:
1. Check if `tests/conftest.py` exists, if not create it
2. Add database initialization fixtures
3. Update failing tests to use `db_session` fixture
4. Run tests: `pytest tests/integration/ -k "query or yaml or cycle" -x`

---

### Category 2: Query/Export Commands (9 failures)

**Tests Failing**:
```
test_epic3_query_command.py::test_query_by_status_filter - Exit code 2
test_epic3_query_command.py::test_query_by_multiple_filters - Exit code 2
test_epic3_query_command.py::test_query_with_flags - Exit code 2
test_epic3_query_command.py::test_query_json_output - Exit code 2
test_epic3_query_command.py::test_query_no_results - Exit code 2
test_epic3_query_command.py::test_query_limit - Exit code 2
test_epic3_yaml_export.py::test_export_yaml_format - Exit code 1
test_epic3_yaml_export.py::test_export_yaml_to_file - Exit code 1
test_epic3_yaml_export.py::test_export_yaml_includes_all_data - KeyError: 'items'
```

**Root Cause**: Commands not implemented or wrong signature

**Investigation Steps**:
1. Check if `src/tracertm/cli/commands/query.py` exists
2. Check if `src/tracertm/cli/commands/export.py` exists
3. Verify command signatures match test expectations
4. Check if commands are registered in CLI app

**Solution Pattern**:

```python
# File: src/tracertm/cli/commands/query.py

@app.command()
def query(
    project: str = typer.Option(..., help="Project ID"),
    status: Optional[str] = typer.Option(None, help="Filter by status"),
    # ... other options
):
    """Query items with filters"""
    # Implementation
```

**Test Pattern Expecting**:
```python
result = runner.invoke(app, ["query", "--project", "test", "--status", "open"])
assert result.exit_code == 0
```

---

### Category 3: Database Connection Mock Path (2 failures)

**Tests Failing**:
```
tests/cli/test_performance.py::test_command_registration_lazy
tests/e2e/test_cli_journeys.py::TestNewUserJourney::test_new_user_onboarding
```

**Error**: `AttributeError: <module 'tracertm.cli.commands.db'> does not have attribute 'DatabaseConnection'`

**Root Cause**: Mock patch path is wrong

**Current (Wrong)**:
```python
@patch('tracertm.cli.commands.db.DatabaseConnection')
```

**Need to Find**:
1. Where is `DatabaseConnection` class actually defined?
   - Check: `src/tracertm/database/connection.py`
   - Check: `src/tracertm/database/manager.py`
   - Check: `src/tracertm/db.py`

2. Once found, update patch to:
```python
@patch('src.tracertm.database.connection.DatabaseConnection')
# OR
@patch('src.tracertm.database.manager.DatabaseManager')
```

**Implementation Steps**:
1. Search for DatabaseConnection class definition:
   ```bash
   grep -r "class DatabaseConnection" src/
   ```

2. Update patch decorators in failing tests to match actual location

3. Run tests: `pytest tests/cli/test_performance.py tests/e2e/test_cli_journeys.py -x`

---

### Category 4: Rate Limit Timeout (1 failure)

**Test Failing**:
```
tests/unit/api/test_sync_client.py::TestApiClient::test_rate_limit_error
```

**Error**: Test took 181.93 seconds (3+ minutes!)

**Root Cause**: Real `time.sleep()` calls in retry logic instead of mocked

**Current Test Pattern**:
```python
async def test_rate_limit_error():
    # Test expects rate limit handling
    # But sleep() is NOT mocked, so it actually waits 60 seconds * 3 retries!
```

**Solution**:
```python
@pytest.mark.asyncio
async def test_rate_limit_error():
    """Test rate limit error handling"""
    api_client = ApiClient(...)

    # Mock the response to always return 429 (rate limited)
    with patch.object(api_client, '_request') as mock_request:
        mock_request.side_effect = RateLimitError("Rate limited")

        # Mock time.sleep to avoid actual delays
        with patch('time.sleep') as mock_sleep:
            with pytest.raises(ApiError):
                await api_client._retry_request("GET", "/api/test")

            # Verify sleep was called with correct backoff times
            assert mock_sleep.call_count == 3  # 3 retries
```

**Implementation Steps**:
1. Open `tests/unit/api/test_sync_client.py`
2. Find `test_rate_limit_error` function
3. Add `@patch('time.sleep')` decorator
4. Update test to accept `mock_sleep` parameter
5. Run test: `pytest tests/unit/api/test_sync_client.py::TestApiClient::test_rate_limit_error -x`

---

### Category 5: Cycle Detection & Multi-Project (8 failures)

**Tests Failing**:
```
test_epic4_cycle_detection.py::test_cycle_prevention_on_link_creation
test_epic4_cycle_detection.py::test_cycle_detection_command
test_epic4_cycle_detection.py::test_cycle_detection_service
test_epic6_multi_project.py::test_separate_state_per_project
test_epic6_multi_project.py::test_cross_project_queries
test_epic6_multi_project.py::test_multi_project_dashboard
+ 2 more
```

**Root Causes**:
1. Missing database tables (same as Category 1)
2. Commands not fully implemented
3. Query logic issues

**Solution**:
- Add database fixtures (same as Category 1)
- Verify command implementations
- Test with populated database

---

### Category 6: Progress Tracking & Search (9 failures)

**Tests Failing**:
```
test_epic7_progress_tracking.py (6 failures)
test_epic7_search_filters.py (3 failures)
```

**Root Causes**:
1. Database initialization (20% of issues)
2. Commands not implemented or incomplete (80% of issues)

**Solution**:
- Add database fixtures
- Verify service implementations
- Add sample data for testing

---

## IMPLEMENTATION WORKFLOW

### Step 1: Database Fixture Setup (30-45 minutes)

**Task**: Create robust database fixtures

```bash
# 1. Check existing conftest
cat tests/conftest.py
cat tests/integration/conftest.py

# 2. Create/update conftest.py with database fixtures
# See fixture code above

# 3. Test database fixture
pytest tests/integration/test_epic2_bulk_operations.py -x  # This one should pass
```

**Files to Create/Modify**:
- `tests/conftest.py` - Add database fixtures
- `tests/integration/conftest.py` - Add integration-specific fixtures

---

### Step 2: Find and Fix Mock Paths (15-20 minutes)

```bash
# Find DatabaseConnection class
grep -r "class DatabaseConnection" src/

# Find all patch decorators using it
grep -r "@patch.*DatabaseConnection" tests/

# Update patch paths in failing tests
# Pattern: Change @patch('tracertm.cli.commands.db.DatabaseConnection')
#          To: @patch('path.to.actual.DatabaseConnection')
```

**Files to Modify**:
- `tests/cli/test_performance.py`
- `tests/e2e/test_cli_journeys.py`

---

### Step 3: Fix Rate Limit Test (10-15 minutes)

**File**: `tests/unit/api/test_sync_client.py`

**Changes**:
1. Add `@patch('time.sleep')` to `test_rate_limit_error`
2. Accept `mock_sleep` parameter in test function
3. Update test to mock API responses properly
4. Verify sleep is mocked (not real)

---

### Step 4: Verify Command Implementations (30-60 minutes)

**For each failing command test**:
1. Check if command module exists
   ```bash
   ls -la src/tracertm/cli/commands/{query,export,cycle_detection,progress}.py
   ```

2. Check if command is registered in app
   ```bash
   grep -A5 "def query" src/tracertm/cli/commands/query.py
   ```

3. Check command signature matches test expectations

4. If missing, either:
   - Create stub implementation
   - Mark test as skip with reason
   - Update test to match actual implementation

---

### Step 5: Systematic Testing (1 hour)

**Test groups in priority order**:

```bash
# 1. Database fixture tests (should all pass after fixture setup)
pytest tests/integration/test_epic2_bulk_operations.py -x

# 2. Query and export tests
pytest tests/integration/test_epic3_* -x

# 3. Cycle detection
pytest tests/integration/test_epic4_cycle_detection.py -x

# 4. Mock path fixes
pytest tests/cli/test_performance.py tests/e2e/test_cli_journeys.py -x

# 5. Rate limit test
pytest tests/unit/api/test_sync_client.py::TestApiClient::test_rate_limit_error -x

# 6. Multi-project and progress
pytest tests/integration/test_epic6_multi_project.py tests/integration/test_epic7_* -x

# 7. Final validation - all tests
pytest tests/ -q --tb=no
```

---

## VERIFICATION CHECKLIST

After completing all fixes, verify:

- [ ] All 67 previously failing tests now pass
- [ ] No regressions in previously passing tests
- [ ] Database fixtures properly initialized
- [ ] Mock paths correct and patching works
- [ ] Rate limit test completes in <5 seconds
- [ ] All CLI commands registered and callable
- [ ] Integration tests have proper data setup
- [ ] Full test suite passes: `pytest tests/ -q`

---

## ROLLBACK STRATEGY

If a fix breaks other tests:
1. Revert the change
2. Run affected tests to confirm they pass again
3. Try alternative approach
4. Document the issue for Phase 4 review

---

## DELIVERABLES

After Phase 1 completion:
- ✅ All 67 tests fixed
- ✅ 0 failures, 100% pass rate
- ✅ Database fixtures documented
- ✅ All commands verified working
- ✅ Ready for Phase 4: fine-tuning

---

## ESTIMATED TIMELINE

- Database fixtures: 30-45 min
- Mock path fixes: 15-20 min
- Rate limit test: 10-15 min
- Command verification: 30-60 min
- Testing & validation: 1 hour
- **Total: 2-3 hours**

---

## SUCCESS METRICS

**Target**:
```
Before Phase 1:  1,651 tests, 67 failures (95.4% pass)
After Phase 1:   2,333 tests, 0 failures (100% pass)
After Phase 4:   2,400+ tests, 0 failures, 80%+ coverage
```

**Final Status When Complete**:
```
pytest tests/ -q
===================== 2,333 passed in 180s =====================
```

---

**Action**: Implement fixes in order above
**Timeline**: 2-3 hours
**Target Completion**: Phase 1 done, ready for Phase 4

