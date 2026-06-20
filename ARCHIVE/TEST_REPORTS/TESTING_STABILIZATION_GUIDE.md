# Testing Stabilization & Documentation Guide

## Executive Summary

This guide provides comprehensive documentation for testing patterns, fixture usage, mock strategies, and test reliability best practices for the TraceRTM project. It covers the full test suite architecture and provides patterns for achieving 99%+ test pass rate with zero flaky tests.

---

## Table of Contents

1. [Test Architecture Overview](#test-architecture-overview)
2. [Fixture Hierarchy & Best Practices](#fixture-hierarchy--best-practices)
3. [Async/Await Patterns](#asyncawait-patterns)
4. [Mock Patterns & Strategies](#mock-patterns--strategies)
5. [Test Isolation & Independence](#test-isolation--independence)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Flaky Test Detection & Fixing](#flaky-test-detection--fixing)
8. [Test Coverage Map by Module](#test-coverage-map-by-module)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Quick Reference](#quick-reference)

---

## Test Architecture Overview

### Project Structure

```
tests/
├── __init__.py
├── conftest.py                 # Root fixtures (db_session, test_db_engine, etc)
├── fixtures.py                 # Reusable fixture definitions
├── unit/                        # Unit tests (5000+ tests)
│   ├── algorithms/            # Algorithm tests
│   ├── api/                   # API endpoint tests
│   ├── services/              # Service logic tests
│   ├── models/                # Model tests
│   └── ...
├── integration/                # Integration tests (100+ tests)
│   ├── conftest.py           # Integration-specific fixtures
│   ├── repositories/          # Repository tests
│   ├── services/              # Service integration tests
│   └── ...
├── e2e/                        # End-to-end tests (20+ tests)
├── cli/                        # CLI command tests
├── component/                  # Component tests
├── performance/                # Performance benchmarks
└── seeds/                      # Test data factories

```

### Test Categories

| Category | Count | Duration | Purpose |
|----------|-------|----------|---------|
| Unit | ~5000 | 2-3 min | Fast, isolated tests |
| Integration | ~100 | 1-2 min | Multi-component interaction |
| E2E | ~20 | 2-5 min | Full workflow validation |
| Performance | ~10 | 1-2 min | Benchmark and optimization |
| CLI | ~50 | 30-60 sec | Command validation |
| Component | ~100 | 1-2 min | Component isolation |

**Total: 5,000+ tests, ~10 minutes full run**

---

## Fixture Hierarchy & Best Practices

### Session Scope Fixtures (One per test run)

These fixtures are expensive to create and are shared across all tests:

```python
@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    """
    Provides the database engine for all tests.

    COST: ~2 seconds to create
    SHARED: Across all tests

    Best Practice: Keep at session scope, never modify directly
    """
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
```

**Use Cases:**
- Database engine creation (heavy I/O)
- Connection pool initialization
- Test environment setup

### Function Scope Fixtures (One per test)

These fixtures provide clean, isolated state for each test:

```python
@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine):
    """
    Provides a fresh database session for each test.

    COST: ~50ms per test
    ISOLATION: Complete - each test gets clean slate
    AUTO-CLEANUP: Transaction rolled back after test

    Best Practice: Use for all database operations in tests
    """
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()
```

**Use Cases:**
- Each test needs fresh database state
- Test isolation is critical
- No shared data between tests

### Fixture Composition Pattern

**DON'T** - Share data between tests:
```python
# WRONG: Fixture holds state
@pytest_asyncio.fixture(scope="session")
async def shared_item():
    item = await create_item()
    yield item
    # Item persists across tests!
```

**DO** - Create fresh data in function scope:
```python
# CORRECT: Each test gets fresh data
@pytest_asyncio.fixture(scope="function")
async def fresh_item(db_session):
    item = Item(name="test")
    db_session.add(item)
    await db_session.commit()
    yield item
    # Automatically rolled back
```

### Fixture Dependency Chain

```
test_db_engine (session)
    ↓
db_session (function) ← depends on engine
    ↓
repositories (function) ← depends on session
    ↓
service (function) ← depends on repositories
    ↓
individual test
```

This chain ensures:
- Engine created once
- Each test gets fresh session
- Each test gets fresh repositories
- Each test gets fresh service instances

---

## Async/Await Patterns

### Correct Async Test Structure

```python
@pytest.mark.asyncio
async def test_async_operation(db_session):
    """
    Proper async test pattern.

    Key points:
    - Use @pytest.mark.asyncio decorator
    - Make test function async
    - Await all async calls
    - Use async fixtures
    """
    # Arrange
    item = Item(name="test")
    db_session.add(item)
    await db_session.commit()

    # Act
    result = await item_service.update(item.id, name="updated")

    # Assert
    assert result.name == "updated"

    # Cleanup is automatic (session rollback)
```

### Async Context Manager Pattern

```python
@pytest.mark.asyncio
async def test_with_async_context_manager():
    """
    Pattern for testing async context managers.
    """
    async with some_service.context_manager() as ctx:
        result = await ctx.operation()
        assert result is not None
        # Context is cleaned up automatically
```

### Mixing Sync and Async (SQLAlchemy)

```python
@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine):
    """
    For SQLAlchemy, use:
    - async_sessionmaker for session creation
    - AsyncSession for session type
    - await for all operations
    """
    async_maker = async_sessionmaker(test_db_engine)

    async with async_maker() as session:
        yield session
        # Let pytest-asyncio handle cleanup
```

### Common Async Pitfalls

**WRONG - Missing await:**
```python
# DON'T DO THIS
result = item_service.get_item(item_id)  # Returns coroutine!
assert result.name == "test"  # Fails because result is coroutine
```

**CORRECT:**
```python
result = await item_service.get_item(item_id)
assert result.name == "test"
```

**WRONG - Not using async fixture:**
```python
@pytest.fixture  # Should be @pytest_asyncio.fixture
def db_session(test_db_engine):
    # Can't create async session in sync fixture
    pass
```

**CORRECT:**
```python
@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine):
    # Proper async fixture
    pass
```

---

## Mock Patterns & Strategies

### Repository Mock Pattern

```python
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_service_with_mock_repository():
    """
    Pattern for mocking repository operations.
    """
    # Create mock repository
    mock_repo = AsyncMock()
    mock_repo.get.return_value = Item(id=1, name="test")

    # Create service with mocked repo
    service = SomeService(item_repo=mock_repo)

    # Test the service
    result = await service.get_item(1)

    # Verify mock was called correctly
    mock_repo.get.assert_called_once_with(1)
    assert result.name == "test"
```

### Database Mock Pattern

```python
@pytest.mark.asyncio
async def test_with_mock_session():
    """
    Pattern for mocking database sessions.
    """
    # Create mock session
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock query behavior
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Item(id=1, name="item1"),
        Item(id=2, name="item2"),
    ]

    # Set up mock to return results
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Use in test
    items = await item_repo.list_items(mock_session)

    # Verify
    mock_session.execute.assert_called_once()
```

### Service Mock Pattern with Dependencies

```python
@pytest.mark.asyncio
async def test_service_chain():
    """
    Pattern for testing service chains with mocked dependencies.
    """
    # Mock lower-level services
    mock_item_repo = AsyncMock()
    mock_link_repo = AsyncMock()

    # Set up return values
    mock_item_repo.get.return_value = Item(id=1)
    mock_link_repo.find_by_source.return_value = []

    # Create service with mocked dependencies
    service = ImpactAnalysisService(
        item_repo=mock_item_repo,
        link_repo=mock_link_repo
    )

    # Test
    result = await service.analyze_impact(1)

    # Verify call chain
    mock_item_repo.get.assert_called_once()
    mock_link_repo.find_by_source.assert_called_once()
```

### Mock Verification Patterns

```python
@pytest.mark.asyncio
async def test_mock_verification():
    """
    Common mock verification patterns.
    """
    mock_repo = AsyncMock()
    mock_repo.create.return_value = Item(id=1)

    service = ItemService(item_repo=mock_repo)
    await service.create_item({"name": "test"})

    # Verify called exactly once
    mock_repo.create.assert_called_once()

    # Verify called with specific args
    mock_repo.create.assert_called_once_with({"name": "test"})

    # Verify called multiple times
    for i in range(3):
        await service.create_item({"name": f"test{i}"})
    assert mock_repo.create.call_count == 4

    # Verify not called
    mock_repo.delete.assert_not_called()

    # Verify call args
    calls = mock_repo.create.call_args_list
    assert len(calls) == 4
```

---

## Test Isolation & Independence

### Rule 1: No Shared State

**WRONG:**
```python
# DON'T use class variables for test data
class TestItems:
    shared_item = None  # Shared across all tests

    def test_item_1(self):
        # This modifies shared state
        self.shared_item = Item(name="test1")

    def test_item_2(self):
        # This gets polluted state from test_item_1
        assert self.shared_item.name == "test2"  # Actually "test1"!
```

**CORRECT:**
```python
# Use fixtures for each test
class TestItems:
    @pytest.fixture
    async def item(self, db_session):
        item = Item(name="test")
        db_session.add(item)
        await db_session.commit()
        return item

    @pytest.mark.asyncio
    async def test_item_1(self, item):
        # Fresh item for this test
        assert item.name == "test"

    @pytest.mark.asyncio
    async def test_item_2(self, item):
        # Different fresh item for this test
        assert item.name == "test"
```

### Rule 2: Database Transaction Isolation

**Pattern for clean test state:**
```python
@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine):
    """Each test gets isolated transaction."""
    async_maker = async_sessionmaker(test_db_engine)

    async with async_maker() as session:
        # Start transaction
        async with session.begin():
            yield session
            # Transaction rolled back automatically
```

### Rule 3: Mock Isolation

**WRONG - Mocks leak between tests:**
```python
mock_repo = AsyncMock()

def test_1():
    mock_repo.get.return_value = Item(id=1)
    # mock_repo.call_count is now 0

def test_2():
    # mock_repo.call_count from test_1 still there!
    assert mock_repo.call_count == 0  # Actually might be 1!
```

**CORRECT - Fresh mocks per test:**
```python
@pytest_asyncio.fixture
async def mock_repo():
    """Fresh mock for each test."""
    return AsyncMock()

async def test_1(mock_repo):
    mock_repo.get.return_value = Item(id=1)
    # Fresh mock

async def test_2(mock_repo):
    # Different fresh mock
    assert mock_repo.call_count == 0
```

### Rule 4: Test Ordering Independence

Tests must pass regardless of order:

```python
# WRONG - Depends on test order
class TestSequence:
    def test_1_create_item(self):
        create_item("item1")

    def test_2_list_items(self):
        items = list_items()
        assert len(items) == 1  # Only works if test_1 ran first!

# CORRECT - Each test is independent
class TestSequence:
    @pytest_asyncio.fixture
    async def item(self, db_session):
        return await create_item("item1")

    async def test_1_create_item(self, item):
        assert item.name == "item1"

    async def test_2_list_items(self, db_session):
        # Create own data
        await create_item("item1")
        items = await list_items()
        assert len(items) == 1
```

---

## Performance Benchmarks

### Test Execution Times

| Category | Count | Time | Per-Test Avg |
|----------|-------|------|--------------|
| Unit | 5000 | 2-3 min | 25-35ms |
| Integration | 100 | 1-2 min | 500-1200ms |
| E2E | 20 | 2-5 min | 6-15s |
| Performance | 10 | 1-2 min | 6-12s |

### Optimization Targets

**Slow Tests (>1s):**
- Integration tests with real databases
- E2E tests with full workflows
- Performance benchmarks

**Fast Tests (<50ms):**
- Unit tests with mocks
- Fixture-less tests
- Pure function tests

### Profiling a Test

```bash
# Run with timing
python -m pytest tests/unit/test_module.py -v --durations=10

# Profile a specific test
python -m cProfile -m pytest tests/unit/test_module.py::test_name

# Get detailed async timing
python -m pytest tests/ --asyncio-mode=strict -v --asyncio-mode=strict
```

---

## Flaky Test Detection & Fixing

### What Makes Tests Flaky

1. **Race Conditions** - Async operations without proper synchronization
2. **Timing Dependencies** - Tests that depend on execution speed
3. **Random Data** - Tests using random values without seeding
4. **Mock Pollution** - Mock state leaking between tests
5. **Database State** - Tests accessing shared database state
6. **Time-Based Tests** - Tests that check timestamps without mocking time

### Detection Strategy

**Run tests multiple times:**
```bash
# Run tests 10 times, stop on first failure
for i in {1..10}; do
    echo "Run $i"
    python -m pytest tests/unit -x -q
done

# Run tests in random order to detect dependencies
python -m pytest tests/unit -p no:cacheprovider --random-order

# Run tests with different concurrency levels
python -m pytest tests/unit -n 4  # 4 workers
python -m pytest tests/unit -n 8  # 8 workers
```

### Fixing Race Conditions

**WRONG - Race condition with async:**
```python
@pytest.mark.asyncio
async def test_concurrent_updates():
    item = Item(id=1, count=0)
    db_session.add(item)

    # Race condition! Both run concurrently
    task1 = asyncio.create_task(increment_item(1))
    task2 = asyncio.create_task(increment_item(1))

    # Who finishes first? Flaky!
    await asyncio.gather(task1, task2)

    assert item.count == 2  # Might be 1!
```

**CORRECT - Proper synchronization:**
```python
@pytest.mark.asyncio
async def test_concurrent_updates():
    item = Item(id=1, count=0)
    db_session.add(item)
    await db_session.commit()

    # Refresh before test
    await db_session.refresh(item)

    # Run tasks with proper awaiting
    task1 = increment_item(1)
    task2 = increment_item(1)

    await asyncio.gather(task1, task2)

    # Refresh to see final state
    await db_session.refresh(item)
    assert item.count == 2  # Consistent
```

### Fixing Timing Dependencies

**WRONG - Timing dependent:**
```python
@pytest.mark.asyncio
async def test_delayed_operation():
    service.schedule_operation()

    # Hope it completes within 1 second? Flaky!
    await asyncio.sleep(1)

    result = await service.get_result()
    assert result is not None
```

**CORRECT - Wait for completion:**
```python
@pytest.mark.asyncio
async def test_delayed_operation():
    # Use event instead of sleep
    completion_event = asyncio.Event()
    service.on_complete = lambda: completion_event.set()

    service.schedule_operation()

    # Wait for actual completion (with timeout)
    try:
        await asyncio.wait_for(completion_event.wait(), timeout=5)
    except asyncio.TimeoutError:
        pytest.fail("Operation did not complete in time")

    result = await service.get_result()
    assert result is not None
```

### Fixing Mock Pollution

**WRONG - Mock state leaks:**
```python
mock_service = AsyncMock()

def test_1():
    mock_service.get.return_value = "value1"
    call_count_1 = mock_service.get.call_count  # 0

def test_2():
    # Previous mock state still here!
    call_count_2 = mock_service.get.call_count  # 0, but might be > 0 if test_1 called it
```

**CORRECT - Fresh mocks:**
```python
@pytest_asyncio.fixture
async def mock_service():
    """Fresh mock for each test."""
    return AsyncMock()

async def test_1(mock_service):
    mock_service.get.return_value = "value1"
    call_count_1 = mock_service.get.call_count  # 0

async def test_2(mock_service):
    # Different mock instance
    call_count_2 = mock_service.get.call_count  # Always 0
```

---

## Test Coverage Map by Module

### Module: src/tracertm/services/

| Service | Unit Tests | Integration Tests | Coverage |
|---------|-----------|------------------|----------|
| cycle_detection_service.py | 63 | 5 | 70.61% |
| item_service.py | 120+ | 15 | 85%+ |
| link_service.py | 100+ | 10 | 80%+ |
| sync_engine.py | 150+ | 20 | 90%+ |
| storage_service.py | 80+ | 10 | 75%+ |

### Module: src/tracertm/repositories/

| Repository | Unit Tests | Integration Tests | Coverage |
|-----------|-----------|------------------|----------|
| item_repository.py | 100+ | 20 | 85%+ |
| link_repository.py | 80+ | 15 | 80%+ |
| project_repository.py | 60+ | 10 | 75%+ |
| agent_repository.py | 70+ | 10 | 78%+ |

### Module: src/tracertm/api/

| Endpoint | Unit Tests | Integration Tests | Coverage |
|----------|-----------|------------------|----------|
| items_endpoint.py | 150+ | 30 | 90%+ |
| links_endpoint.py | 120+ | 25 | 88%+ |
| analysis_endpoint.py | 100+ | 20 | 85%+ |
| search_endpoint.py | 80+ | 15 | 82%+ |

---

## Troubleshooting Guide

### Issue: "RuntimeError: Event loop is closed"

**Cause:** Async fixture scope mismatch

**Solution:**
```python
# WRONG
@pytest.fixture(scope="session")
async def async_fixture():  # Async fixture with session scope
    pass

# CORRECT
@pytest_asyncio.fixture(scope="session")  # Use pytest_asyncio
async def async_fixture():
    pass
```

### Issue: "asyncio.TimeoutError" in tests

**Cause:** Test takes longer than expected

**Solutions:**
1. Mock external I/O instead of making real calls
2. Increase timeout: `await asyncio.wait_for(..., timeout=10)`
3. Use events instead of sleep: `await event.wait()`

### Issue: "Database is locked" SQLite error

**Cause:** Multiple async engines or scope issues

**Solution:**
```python
@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    # Use SINGLE engine for all tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False}  # IMPORTANT!
    )
    yield engine
```

### Issue: "Test passed locally but fails in CI"

**Common causes:**
1. Timing assumptions - use events instead of sleep
2. Environment variables - check CI env config
3. Import order - use conftest.py properly
4. Parallel execution - ensure test isolation

**Solution:** Run tests with same settings locally
```bash
python -m pytest tests/ -n 4 -p no:cacheprovider --random-order
```

### Issue: "Mock not called as expected"

**Cause:** Incorrect mock setup

**Solutions:**
```python
# Check if mock is being used
mock_obj.assert_called()  # Was called at least once
mock_obj.assert_called_once()  # Called exactly once
mock_obj.assert_called_with(arg1, arg2)  # Called with specific args
mock_obj.assert_not_called()  # Never called

# Check call arguments
call_args = mock_obj.call_args  # Last call arguments
all_calls = mock_obj.call_args_list  # All calls

# Debug: print what was called
print(f"Called with: {mock_obj.call_args_list}")
```

---

## Quick Reference

### Running Tests

```bash
# All tests
python -m pytest tests/

# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Specific file
python -m pytest tests/unit/api/test_api_comprehensive.py

# Specific test
python -m pytest tests/unit/api/test_api_comprehensive.py::TestClass::test_method

# With pattern matching
python -m pytest tests/ -k "test_create"

# Verbose output
python -m pytest tests/ -v

# Show print statements
python -m pytest tests/ -s

# Stop on first failure
python -m pytest tests/ -x

# Show slowest tests
python -m pytest tests/ --durations=10
```

### Common Decorators

```python
# Mark test as async
@pytest.mark.asyncio
async def test_something():
    pass

# Skip test
@pytest.mark.skip(reason="Not ready yet")
def test_skip():
    pass

# Mark as expected to fail
@pytest.mark.xfail
def test_fails():
    pass

# Run with multiple parameters
@pytest.mark.parametrize("input,expected", [
    ("a", 1),
    ("b", 2),
])
def test_multiple(input, expected):
    pass
```

### Fixture Usage

```python
# Use fixture in test
def test_with_fixture(db_session):
    # Use db_session
    pass

# Combine multiple fixtures
def test_multiple_fixtures(db_session, mock_service):
    # Use both
    pass

# Create fixture that depends on other fixtures
@pytest.fixture
def complex_fixture(db_session, mock_service):
    # Build complex object using both
    return ComplexObject(db_session, mock_service)
```

---

## Best Practices Checklist

- [ ] All tests use fixtures for shared resources
- [ ] No global state or class variables
- [ ] All async tests use @pytest.mark.asyncio
- [ ] All async fixtures use @pytest_asyncio.fixture
- [ ] Database operations use db_session fixture
- [ ] Mocks are created fresh for each test
- [ ] Tests are independent and order-agnostic
- [ ] No hardcoded timeouts (use events instead)
- [ ] Clear test naming (test_<action>_<condition>_<result>)
- [ ] Each test tests one behavior
- [ ] Proper assertion messages for debugging
- [ ] Error cases tested explicitly

---

## Conclusion

Following these patterns and practices ensures:
- **Reliable Tests**: No flaky failures
- **Fast Tests**: 25-35ms average per unit test
- **Maintainable Tests**: Clear structure and patterns
- **Scalable Suite**: Easily add new tests
- **CI/CD Ready**: Consistent results across environments

For questions or issues, refer to the specific section above or check the test examples in the codebase.

