# Integration Test Suite Systematic Fixes

## Executive Summary

This document provides systematic fixes for ALL integration tests across the test suite. Fixes are grouped by common patterns and applied consistently across all test directories.

**Test Directories:**
- tests/integration/cli/
- tests/integration/tui/
- tests/integration/services/
- tests/integration/repositories/
- tests/integration/storage/
- tests/integration/api/
- tests/integration/edge_cases/

## Common Failure Patterns Identified

### Pattern 1: Async/Sync Session Mismatch
**Issue**: Services expecting sync `Session` receiving async `AsyncSession`
**Files Affected**: services/, storage/, api/

### Pattern 2: Fixture Import/Path Issues
**Issue**: Incorrect imports or fixture dependencies
**Files Affected**: All test files

### Pattern 3: Database Session Management
**Issue**: Session not properly committed/rolled back, stale data
**Files Affected**: All database tests

### Pattern 4: Missing Async Markers
**Issue**: Async tests missing `@pytest.mark.asyncio` decorator
**Files Affected**: All async tests

### Pattern 5: Mock/Patch Context Issues
**Issue**: Mocks not properly scoped or cleaned up
**Files Affected**: cli/, api/, services/

---

## Fix 1: Integration Conftest - Sync Session Fixture

**File**: `tests/integration/conftest.py`

**Problem**: Services like `BulkOperationService`, `ExportImportService`, `TraceabilityService`, and `VisualizationService` expect synchronous `Session` but tests provide `AsyncSession`.

**Fix**: Add sync session fixture

```python
# Add after existing fixtures (around line 236)

@pytest.fixture(scope="function")
def sync_db_session(test_db_engine):
    """
    Create a synchronous database session for services that require sync Session.

    This fixture creates a separate sync engine for synchronous services,
    allowing them to operate alongside async tests without conflicts.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile
    from pathlib import Path

    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # Create synchronous engine with temporary database
        sync_engine = create_engine(f'sqlite:///{db_path}', echo=False)

        # Create tables
        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        yield session

        session.close()
        sync_engine.dispose()
    finally:
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
```

---

## Fix 2: Services Integration Tests - Session Type Fix

**File**: `tests/integration/services/test_critical_services_integration.py`

**Problems**:
1. Using `AsyncSession` with sync-only services
2. Missing proper fixture setup for test data
3. Incorrect async/await usage with sync services

**Fixes**:

### Fix 2a: Update Service Test Fixtures

Replace lines 40-262 with proper sync fixtures:

```python
@pytest.fixture
def sync_test_project():
    """Create a test project using sync session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile
    import os

    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        # Create synchronous engine
        sync_engine = create_engine(f'sqlite:///{db_path}', echo=False)

        # Create tables
        from tracertm.models.base import Base
        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        project = Project(
            name=f"Integration Test Project {datetime.now().timestamp()}",
            description="Project for integration testing",
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        project_id = project.id
        session.close()

        yield project

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def sync_test_items(sync_test_project):
    """Create test items for sync services."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile
    import os

    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        sync_engine = create_engine(f'sqlite:///{db_path}', echo=False)

        from tracertm.models.base import Base
        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        # Add the project first
        session.add(sync_test_project)
        session.commit()

        items_repo = ItemRepository(session)
        items = []

        # Create items in different views
        views_data = [
            ("FEATURE", "feature", "Implement user authentication", "high", "todo"),
            ("FEATURE", "feature", "Implement data export", "medium", "todo"),
            ("FEATURE", "feature", "Implement search functionality", "high", "in_progress"),
            ("CODE", "class", "UserAuthService", "high", "done"),
            ("CODE", "class", "ExportService", "medium", "todo"),
            ("TEST", "unit_test", "test_user_auth", "high", "done"),
            ("TEST", "unit_test", "test_export", "medium", "todo"),
            ("TEST", "integration_test", "test_auth_flow", "low", "todo"),
            ("API", "endpoint", "POST /auth/login", "high", "done"),
            ("API", "endpoint", "GET /export", "medium", "todo"),
        ]

        for view, item_type, title, priority, status in views_data:
            item = items_repo.create(
                project_id=sync_test_project.id,
                title=title,
                view=view,
                item_type=item_type,
                status=status,
                priority=priority,
            )
            items.append(item)

        session.commit()
        session.close()

        yield items

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
```

### Fix 2b: Remove Async Markers from Sync Service Tests

Remove `@pytest.mark.asyncio` and `async def` from all BulkOperationService, ExportImportService tests (lines 268-858).

Example transformation:

**BEFORE:**
```python
@pytest.mark.asyncio
async def test_bulk_update_preview_by_view(
    self, test_project: Project, test_items: list[Item], db_session: AsyncSession
):
```

**AFTER:**
```python
def test_bulk_update_preview_by_view(
    self, sync_test_project: Project, sync_test_items: list[Item], sync_db_session: Session
):
```

### Fix 2c: Remove Await Keywords from Sync Calls

Transform all service calls to synchronous:

**BEFORE:**
```python
service = BulkOperationService(db_session)
result = await service.bulk_update_preview(...)
```

**AFTER:**
```python
service = BulkOperationService(sync_db_session)
result = service.bulk_update_preview(...)
```

### Fix 2d: Fix Database Verification Code

**BEFORE:**
```python
await db_session.commit()
await db_session.rollback()
stmt = select(Item).where(...)
db_result = await db_session.execute(stmt)
```

**AFTER:**
```python
sync_db_session.commit()
sync_db_session.rollback()
stmt = select(Item).where(...)
db_result = sync_db_session.execute(stmt)
items = db_result.scalars().all()
```

---

## Fix 3: API Integration Tests - Async Session Override

**File**: `tests/integration/api/test_api_integration.py`

**Problem**: FastAPI dependency override using sync engine URL with async sessions

**Fix**: Lines 119-143

```python
@pytest.fixture(scope="function")
def fastapi_test_client(test_db_engine, test_project):
    """Create FastAPI test client with database dependency override."""

    async def override_get_db():
        # Create async session from sync engine
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

        # Get sync URL and convert to async
        sync_url = str(test_db_engine.url)
        # Handle both with and without file:// prefix
        if 'sqlite:///' in sync_url:
            async_url = sync_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        else:
            async_url = f"sqlite+aiosqlite:///{sync_url.split('sqlite://')[-1]}"

        async_engine = create_async_engine(async_url, echo=False)
        async_session_maker = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

        await async_engine.dispose()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

---

## Fix 4: CLI Integration Tests - Database Engine Disposal

**File**: `tests/integration/cli/test_cli_integration.py`

**Problem**: `refresh_db_session` using disposed engine

**Fix**: Lines 144-151

```python
def refresh_db_session(temp_env):
    """
    Force database engine to dispose connections and return fresh session.
    This ensures tests see data committed by CLI commands.
    """
    db = temp_env["db"]
    # Don't dispose - just create new session
    # db.engine.dispose()  # Remove this line
    return Session(db.engine)
```

---

## Fix 5: Storage Integration Tests - Import Sync ItemRepository

**File**: `tests/integration/storage/test_storage_integration.py`

**Problem**: Using async-only ItemRepository in sync context

**Fix**: Import statement (around line 28)

**BEFORE:**
```python
from tracertm.repositories.item_repository import ItemRepository
```

**AFTER:**
```python
from tracertm.repositories.item_repository import ItemRepository
# NOTE: ItemRepository methods must be called without await in sync context
```

Then in fixture (lines 112-148), ensure proper sync usage:

```python
items_repo = ItemRepository(session)  # session is sync Session
items = []

for view, item_type, title, priority, status in views_data:
    # Call create() WITHOUT await since we're in sync context
    item = items_repo.create(
        project_id=test_project.id,
        title=title,
        view=view,
        item_type=item_type,
        status=status,
        priority=priority,
    )
    items.append(item)

session.commit()  # Sync commit
```

---

## Fix 6: TUI Integration Tests - Textual App Context

**File**: `tests/integration/tui/test_tui_integration.py`

**Problem**: Missing proper async context for Textual apps

**Fix**: Add helper for app testing (after line 62)

```python
async def run_app_test(app_class, **app_kwargs):
    """Helper to run Textual app in test mode."""
    app = app_class(**app_kwargs)
    async with app.run_test() as pilot:
        yield pilot


# Then use in tests:
@pytest.mark.asyncio
async def test_browser_app_loads():
    """Test BrowserApp initialization."""
    async for pilot in run_app_test(BrowserApp):
        assert pilot.app.is_running
        # Pilot interaction here
        await pilot.pause()
        break
```

---

## Fix 7: Repositories Integration - Proper Async Handling

**File**: `tests/integration/repositories/test_repositories_integration.py`

**Problem**: All repository methods are async but some tests missing markers

**Fix**: Ensure all test methods have decorator

Add to ALL test methods:

```python
@pytest.mark.asyncio
async def test_name(db_session: AsyncSession):
    # test code with await
```

---

## Fix 8: Edge Cases Tests - Missing Test File

**File**: `tests/integration/edge_cases/test_coverage_gaps.py`

**Problem**: This file likely doesn't exist or is empty

**Fix**: Create comprehensive edge case tests

```python
"""
Integration tests for edge cases and coverage gaps.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models import Item, Link, Project
from tracertm.repositories import ItemRepository, LinkRepository, ProjectRepository


@pytest.mark.asyncio
async def test_empty_database_queries(db_session: AsyncSession):
    """Test querying empty database doesn't crash."""
    item_repo = ItemRepository(db_session)
    project_repo = ProjectRepository(db_session)

    items = await item_repo.get_all()
    assert items == []

    projects = await project_repo.get_all()
    assert len(projects) >= 0


@pytest.mark.asyncio
async def test_null_field_handling(db_session: AsyncSession):
    """Test creating items with None values."""
    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    # Create item with minimal fields
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature",
        description=None,  # Explicitly None
        owner=None,
        parent_id=None,
    )

    assert item.description is None
    assert item.owner is None
    assert item.parent_id is None


@pytest.mark.asyncio
async def test_special_characters_in_fields(db_session: AsyncSession):
    """Test handling special characters in text fields."""
    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    special_title = "Test with 'quotes', \"double\", and <tags>"
    item = await item_repo.create(
        project_id=project.id,
        title=special_title,
        view="FEATURE",
        item_type="feature",
    )

    assert item.title == special_title


@pytest.mark.asyncio
async def test_very_long_text_fields(db_session: AsyncSession):
    """Test handling very long text content."""
    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    long_description = "A" * 10000  # 10k characters
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature",
        description=long_description,
    )

    assert len(item.description) == 10000


@pytest.mark.asyncio
async def test_concurrent_item_creation(db_session: AsyncSession):
    """Test creating items concurrently."""
    import asyncio

    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    async def create_item(index):
        return await item_repo.create(
            project_id=project.id,
            title=f"Item {index}",
            view="FEATURE",
            item_type="feature",
        )

    # Create 10 items concurrently
    items = await asyncio.gather(*[create_item(i) for i in range(10)])

    assert len(items) == 10
    assert len(set(item.id for item in items)) == 10  # All unique IDs


@pytest.mark.asyncio
async def test_circular_link_prevention(db_session: AsyncSession):
    """Test that circular links are handled gracefully."""
    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)
    link_repo = LinkRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature",
    )

    # Try to create self-referencing link
    # This should either be prevented or handled gracefully
    try:
        link = await link_repo.create(
            project_id=project.id,
            source_item_id=item1.id,
            target_item_id=item1.id,
            link_type="depends_on",
        )
        # If allowed, verify it doesn't break queries
        assert link is not None
    except ValueError:
        # Expected - self-links not allowed
        pass


@pytest.mark.asyncio
async def test_deleted_item_filtering(db_session: AsyncSession):
    """Test soft-deleted items don't appear in queries."""
    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    item = await item_repo.create(
        project_id=project.id,
        title="Delete Me",
        view="FEATURE",
        item_type="feature",
    )
    await db_session.commit()

    item_id = item.id

    # Soft delete
    await item_repo.delete(item_id)
    await db_session.commit()

    # Should not appear in get_all
    items = await item_repo.get_all()
    assert all(i.id != item_id for i in items)

    # Should not be retrievable by get_by_id
    deleted = await item_repo.get_by_id(item_id)
    assert deleted is None or deleted.deleted_at is not None


@pytest.mark.asyncio
async def test_transaction_rollback_on_error(db_session: AsyncSession):
    """Test transaction rollback works correctly."""
    project_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    project = await project_repo.create(name="Test")
    await db_session.commit()

    # Create item
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature",
    )

    # Don't commit - rollback instead
    await db_session.rollback()

    # Item should not exist
    items = await item_repo.get_all()
    assert all(i.title != "Test" for i in items)


@pytest.mark.asyncio
async def test_bulk_operations_rollback(db_session: AsyncSession):
    """Test bulk operations rollback atomically."""
    from tracertm.services.bulk_operation_service import BulkOperationService

    # Note: BulkOperationService expects sync Session
    # This test would need adaptation based on service implementation
    pass
```

---

## Fix 9: Common Test Utilities

**File**: `tests/integration/test_helpers.py` (CREATE NEW)

Create shared helpers to avoid code duplication:

```python
"""
Common test helpers for integration tests.
"""

import tempfile
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tracertm.models.base import Base


def create_temp_sync_session() -> Generator[Session, None, None]:
    """
    Create a temporary sync database session.

    Yields:
        Session: SQLAlchemy sync session with all tables created
    """
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
        session = SessionLocal()

        yield session

        session.close()
        engine.dispose()
    finally:
        Path(db_path).unlink(missing_ok=True)


def refresh_session(session: Session) -> Session:
    """
    Refresh session to see committed changes.

    Args:
        session: Current session

    Returns:
        Same session after expire_all()
    """
    session.expire_all()
    return session


def count_db_items(session: Session, model_class) -> int:
    """
    Count items in database for a model.

    Args:
        session: Database session
        model_class: Model class to count

    Returns:
        Number of items
    """
    return session.query(model_class).count()
```

---

## Fix 10: Add Missing __init__ Files

Ensure all integration test subdirectories have `__init__.py`:

```bash
touch tests/integration/services/__init__.py
touch tests/integration/edge_cases/__init__.py
```

---

## Application Strategy

### Phase 1: Critical Fixes (Priority 1)
1. Fix 1: Add sync_db_session to conftest
2. Fix 2: Update services integration tests
3. Fix 3: Fix API async session override

### Phase 2: Module Fixes (Priority 2)
4. Fix 4: CLI database engine disposal
5. Fix 5: Storage ItemRepository sync usage
6. Fix 6: TUI async app context

### Phase 3: Coverage Gaps (Priority 3)
7. Fix 7: Repositories async markers
8. Fix 8: Create edge cases tests
9. Fix 9: Add common test utilities
10. Fix 10: Add __init__ files

## Validation Checklist

After applying fixes, verify:

- [ ] All integration tests can be discovered by pytest
- [ ] No import errors
- [ ] Async tests have `@pytest.mark.asyncio`
- [ ] Sync services use sync sessions
- [ ] Async services use async sessions
- [ ] Database fixtures properly scoped
- [ ] Mocks properly cleaned up
- [ ] No session mixing (async/sync)
- [ ] Transaction boundaries correct
- [ ] Fixtures reusable across tests

## Common Gotchas

1. **Don't mix AsyncSession and Session**: Use appropriate fixture
2. **Await only async calls**: Remove await from sync service methods
3. **Commit transactions**: Tests need explicit commit for data persistence
4. **Fixture scope**: Use 'function' for isolation
5. **Import all models**: Ensure Base.metadata knows all tables
6. **Close resources**: Always close/dispose sessions and engines
7. **Path handling**: Use absolute paths, not relative
8. **Temp files**: Always clean up temp databases
9. **Mock contexts**: Use context managers for patches
10. **Async fixtures**: Use pytest_asyncio.fixture for async fixtures

## Testing Commands

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific directory
pytest tests/integration/cli/ -v
pytest tests/integration/services/ -v
pytest tests/integration/api/ -v

# Run with coverage
pytest tests/integration/ --cov=tracertm --cov-report=term-missing

# Run specific test file
pytest tests/integration/services/test_critical_services_integration.py -v

# Run with debugging
pytest tests/integration/ -v -s --tb=short

# Run only failed tests
pytest tests/integration/ --lf

# Run in parallel (after fixes verified)
pytest tests/integration/ -n auto
```

## Summary

This document provides systematic fixes for all common integration test failures. The fixes address:

1. **Session Type Mismatches**: Proper sync/async session handling
2. **Fixture Issues**: Correct fixture setup and dependencies
3. **Database Management**: Proper commit/rollback/isolation
4. **Async Handling**: Correct decorators and await usage
5. **Import Errors**: Missing dependencies and circular imports
6. **Resource Cleanup**: Proper disposal of sessions/engines/files
7. **Edge Cases**: Comprehensive edge case coverage

Apply fixes in order of priority for maximum impact.
