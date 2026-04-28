# WP-2.2 Failure Analysis & Root Cause Report

**Test File:** `tests/integration/services/test_services_medium_full_coverage.py`
**Total Failures:** 31
**Failure Categories:** 2 (Async/Sync Mismatch, Data Serialization)

---

## Failure Category 1: Async/Sync Fixture Mismatch

### Symptom
```
AttributeError: 'coroutine' object has no attribute 'id'
TypeError: cannot unpack non-iterable coroutine object
AttributeError: 'async_generator' object has no attribute 'execute'
```

### Root Cause Analysis

The test file defines both sync and async fixtures, but async services are being tested with sync fixtures. When a sync test method calls an async fixture, it receives a coroutine object instead of the actual data.

**Example from ItemService tests:**
```python
# This fixture is async but test method is not
@pytest.fixture
async def async_project():  # <-- Returns coroutine
    project = Project(id="test-project", name="Test Project")
    await session.add(project)
    await session.commit()
    return project

def test_create_item_basic(async_project):  # <-- Sync test
    project_id = async_project.id  # <-- async_project is still a coroutine!
    # Error: 'coroutine' object has no attribute 'id'
```

### Affected Tests

**ItemService (12 failures):**
1. test_create_item_basic
2. test_create_item_with_metadata
3. test_create_item_with_links
4. test_create_item_with_parent
5. test_create_item_event_logging
6. test_create_item_all_statuses
7. test_get_item_by_id
8. test_get_item_not_found
9. test_get_item_wrong_project
10. test_update_item_status
11. test_update_item_multiple_fields
12. test_delete_item

**ChaosModeService (10 failures):**
1. test_detect_zombies
2. test_analyze_impact
3. test_create_temporal_snapshot
4. test_mass_update_items
5. test_get_project_health
6. test_explode_file_markdown
7. test_track_scope_crash
8. test_cleanup_zombies
9. test_create_snapshot_wrapper
10. (Plus one async-related failure)

**ImpactAnalysisService (4 failures):**
1. test_analyze_impact_single_item
2. test_analyze_impact_with_depth_limit
3. test_analyze_reverse_impact
4. test_analyze_impact_no_dependencies

**AdvancedTraceabilityService (3 failures):**
1. test_find_all_paths_direct
2. test_find_all_paths_no_path
3. test_find_all_paths_max_depth

**CycleDetectionService (1 failure):**
1. test_detect_cycles_async

**ChaosModeService Cross-Integration (1 failure):**
1. test_chaos_mode_with_impact_analysis

**Total: 31 failures from this category**

---

## Failure Category 2: Data Serialization

### Symptom
```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) datatype mismatch
[SQL: INSERT INTO events (id, project_id, event_type, entity_type, entity_id, agent_id, data) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id, created_at, updated_at]
[parameters: ('event-1', 'test-project', 'item_created', 'item', 'item-1', 'test-agent', 'null')]
```

### Root Cause

The Event model's `data` field expects JSON but is receiving the string `'null'` instead of a proper JSON object or NULL value.

**Affected Test:**
- ProjectBackupService::test_backup_project_with_history (1 failure)

### Example Code Problem

```python
# Test creates event with improper data
Event(
    project_id="test-project",
    event_type="item_created",
    entity_type="item",
    entity_id="item-1",
    agent_id="test-agent",
    data='null',  # <-- Should be None, {}, or proper JSON
)
```

---

## Fix Strategy

### Phase 1: Fix Async/Sync Fixtures (Priority 1)

**Step 1: Create Async Database Setup**

Replace the current fixture logic with proper async fixtures:

```python
@pytest.fixture
async def async_db():
    """Create an async test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_db):
    """Create an async database session."""
    async_sessionmaker_instance = async_sessionmaker(
        async_db,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_sessionmaker_instance() as session:
        yield session
```

**Step 2: Convert Tests to Async**

```python
# Change test method from sync to async
@pytest.mark.asyncio
async def test_create_item_basic(async_session):
    """Test basic item creation."""
    project = Project(id="proj-1", name="Test Project")
    async_session.add(project)
    await async_session.commit()

    service = ItemService(async_session)
    item = await service.create_item(
        project_id="proj-1",
        title="New Item",
        view="FEATURE",
        item_type="feature",
        agent_id="agent-1",
    )

    assert item.id is not None
    assert item.title == "New Item"
```

**Step 3: Update Conftest**

Add async marker configuration to `conftest.py`:

```python
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async (deselect with '-m \"not asyncio\"')",
    )
```

---

### Phase 2: Fix Data Serialization (Priority 2)

**Step 1: Fix Event Data Serialization**

Update test fixtures to use proper JSON:

```python
# Before (wrong)
Event(
    data='null'
)

# After (correct)
Event(
    data=None  # or {} or {"key": "value"}
)
```

**Step 2: Update Event Model if Needed**

Check the Event model's data field:

```python
# In tracertm/models/event.py
class Event(Base):
    data = Column(JSON, nullable=True)  # Ensure JSON type, nullable=True
```

---

## Implementation Plan

### Timeline: 4-6 Hours

**Hour 1-2: Async Fixture Setup**
- Create async database fixtures
- Add pytest-asyncio configuration
- Update conftest.py

**Hour 2-3: Convert ItemService Tests**
- Mark all ItemService tests with `@pytest.mark.asyncio`
- Convert test methods to async
- Test and verify

**Hour 3-4: Convert ChaosModeService Tests**
- Mark all ChaosModeService tests with `@pytest.mark.asyncio`
- Convert test methods to async
- Test and verify

**Hour 4-5: Convert Remaining Async Services**
- ImpactAnalysisService
- AdvancedTraceabilityService
- CycleDetectionServiceAsync

**Hour 5-6: Fix Data Serialization**
- Update Event test fixtures
- Fix ProjectBackupService test
- Final verification

---

## Expected Outcomes

After fixes:

| Service | Before | After |
|---------|--------|-------|
| ItemService | 0/12 (0%) | 12/12 (100%) |
| ChaosModeService | 0/10 (0%) | 10/10 (100%) |
| ImpactAnalysisService | 0/4 (0%) | 4/4 (100%) |
| AdvancedTraceabilityService | 0/3 (0%) | 3/3 (100%) |
| ProjectBackupService | 8/9 (88%) | 9/9 (100%) |
| CycleDetectionService | 6/7 (85%) | 7/7 (100%) |
| **Total** | **30/61 (49%)** | **61/61 (100%)** |

---

## Verification Checklist

After implementing fixes, verify:

- [ ] All async fixtures return awaited values, not coroutines
- [ ] All async tests use `@pytest.mark.asyncio` decorator
- [ ] All async test methods are declared with `async def`
- [ ] All service calls are properly awaited
- [ ] Event data is properly serialized as JSON
- [ ] Database session creation is properly awaited
- [ ] Session commit/flush operations are properly awaited
- [ ] All tests pass: `pytest tests/integration/services/test_services_medium_full_coverage.py -v`

---

## Quick Fix Commands

```bash
# Run only passing tests to verify they still work
pytest tests/integration/services/test_services_medium_full_coverage.py::TestBulkOperationService -v

# Run only failing tests to verify fixes
pytest tests/integration/services/test_services_medium_full_coverage.py::TestItemServiceCreate -v

# Run all tests with verbose output
pytest tests/integration/services/test_services_medium_full_coverage.py -v --tb=short

# Run with asyncio verbose mode
pytest tests/integration/services/test_services_medium_full_coverage.py -v --asyncio-mode=strict
```

---

## Prevention for Future Tests

1. **Use Service-Appropriate Fixtures**
   - Async services → Async fixtures
   - Sync services → Sync fixtures

2. **Fixture Return Type Validation**
   - Never return coroutines from sync fixtures
   - Always await async operations in async fixtures

3. **Test Method Signatures**
   - Mark async tests with `@pytest.mark.asyncio`
   - Use `async def` for async tests

4. **Data Serialization**
   - Validate JSON types match model expectations
   - Use type hints for fixture return values

---

## References

- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy AsyncSession Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

---

*Analysis Date: 2025-12-09*
*Prepared by: Claude Haiku 4.5*
