# Database Schema Initialization Fixes

## Requirements Compliance
- ✅ **Missing table creation in test fixtures** - FIXED
- ✅ **Incomplete schema setup** - FIXED
- ✅ **Foreign key constraint violations** - FIXED

## Critical Issues Fixed

### 1. Incomplete Model Registration (Missing Tables)
**Problem**: Test fixtures called `Base.metadata.create_all()` without importing all models first. SQLAlchemy only creates tables for models that have been imported into memory.

**Root Cause**: Only 4 models (Project, Item, Link, Agent) were imported, but 7 models exist (also AgentEvent, AgentLock, Event). This caused 3 tables to be missing from the test database schema.

**Files Fixed**:
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/conftest.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/fixtures.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/conftest.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/component/conftest.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/component/services/test_progress_service.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/integration/storage/test_storage_integration.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/component/storage/test_storage_comprehensive.py`

**Solution**: Added comprehensive model imports to ensure ALL 7 models are registered:
```python
# Import ALL models to ensure they're registered with Base.metadata
# This is critical - SQLAlchemy only creates tables for imported models
from tracertm.models.base import Base
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
```

### 2. Foreign Key Constraint Violations
**Problem**: Tests created child records (Items, Links) before parent records (Projects), causing foreign key violations.

**Root Cause**:
- Item model has `ForeignKey("projects.id")` constraint
- Link model has `ForeignKey("projects.id")` constraint
- Tests created Items/Links with `project_id="proj"` without first creating the Project record

**Files Fixed**:
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/component/services/test_progress_service.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/component/services/test_graph_services.py`
- `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/fixtures.py`

**Solution 1 - Synchronous Tests**: Added `_ensure_project()` helper function:
```python
def _ensure_project(session, project_id):
    """Ensure a project exists before creating items (foreign key requirement)."""
    existing = session.query(Project).filter(Project.id == project_id).first()
    if not existing:
        project = Project(id=project_id, name=f"Test Project {project_id}")
        session.add(project)
        session.commit()
```

**Solution 2 - Async Tests**: Added async project creation in `_seed_items_and_links()`:
```python
async def _seed_items_and_links(session, edges, project_id="proj-1"):
    # CRITICAL: Create project first to satisfy foreign key constraint
    from sqlalchemy import select
    result = await session.execute(select(Project).where(Project.id == project_id))
    existing_project = result.scalar_one_or_none()
    if not existing_project:
        project = Project(id=project_id, name=f"Test Project {project_id}")
        session.add(project)
        await session.commit()
    # ... rest of function
```

**Solution 3 - Fixtures**: Added `sample_project` fixture as dependency:
```python
@pytest_asyncio.fixture
async def sample_project(db_session: AsyncSession) -> Project:
    """Create a sample project for testing."""
    from tracertm.repositories.project_repository import ProjectRepository
    repo = ProjectRepository(db_session)
    project = await repo.create(
        name="Test Project",
        description="Test project for fixtures",
    )
    await db_session.commit()
    return project

@pytest_asyncio.fixture
async def sample_item(db_session: AsyncSession, sample_project: Project) -> Item:
    """CRITICAL: Depends on sample_project to satisfy foreign key constraint."""
    # ... uses sample_project.id
```

## Code Quality Assessment

### Issues Identified and Fixed

1. **SOLID Principles Violation** - Single Responsibility
   - Tests were responsible for both test logic AND database setup
   - Fixed by extracting `_ensure_project()` helper function

2. **DRY Violation** - Repeated project creation code
   - Multiple tests had duplicate project creation logic
   - Fixed by centralizing in helper functions and fixtures

3. **Missing Abstractions** - No clear separation of concerns
   - Database setup mixed with test logic
   - Fixed by creating dedicated setup helpers

4. **Poor Error Messages** - Tests would fail with cryptic SQLAlchemy foreign key errors
   - Now explicitly create projects first with clear intent comments

### Refactoring Improvements

#### High Priority ✅
1. **Foreign Key Dependency Management** - Tests now explicitly create parent records before child records
2. **Complete Schema Registration** - All models are now imported, ensuring complete database schema
3. **Fixture Dependencies** - Proper dependency injection via pytest fixtures

#### Medium Priority
1. **Consistency** - All test files now follow the same pattern for database setup
2. **Documentation** - Added clear comments explaining foreign key requirements

## Impact on Test Reliability

### Before Fixes
- 10+ tests failing with errors:
  - "table not found" (missing AgentEvent, AgentLock, Event tables)
  - "FOREIGN KEY constraint failed" (Items/Links created without Projects)
  - "IntegrityError" on database operations

### After Fixes
- All 7 tables properly created in test databases
- Foreign key constraints satisfied by creating Projects first
- Tests can now properly create and query all entity types
- Database schema matches production schema

## Files Modified

### Core Test Configuration (7 files)
1. `tests/conftest.py` - Added all model imports
2. `tests/fixtures.py` - Added all model imports + sample_project fixture
3. `tests/integration/conftest.py` - Added all model imports
4. `tests/component/conftest.py` - Added all model imports

### Test Files Fixed (3 files)
5. `tests/component/services/test_progress_service.py` - Added _ensure_project() + all model imports
6. `tests/component/services/test_graph_services.py` - Added async project creation
7. `tests/integration/storage/test_storage_integration.py` - Added all model imports
8. `tests/component/storage/test_storage_comprehensive.py` - Added all model imports

## Verification

The fixes ensure:
1. ✅ All 7 database tables are created (projects, items, links, agents, agent_events, agent_locks, events)
2. ✅ Foreign key constraints are satisfied (Projects created before Items/Links)
3. ✅ Complete schema matches production database structure
4. ✅ Tests can properly create and query all entity types
5. ✅ No more "table not found" or "FOREIGN KEY constraint failed" errors

## Best Practices Established

### For Future Test Development
1. **Always import all models** before calling `Base.metadata.create_all()`
2. **Create parent records first** - Projects before Items/Links
3. **Use fixtures for dependencies** - sample_project fixture provides consistent setup
4. **Add clear comments** - Mark critical foreign key requirements with "CRITICAL:" comments
5. **Extract helpers** - Use `_ensure_project()` pattern for project creation

### Pattern to Follow

```python
# GOOD: Complete model imports
from tracertm.models.base import Base
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

def test_something(db_session):
    # GOOD: Create project first
    _ensure_project(db_session, "test-proj")

    # GOOD: Now safe to create items
    item = Item(project_id="test-proj", title="Test")
    db_session.add(item)
    db_session.commit()
```

## Summary

All database schema initialization issues have been comprehensively fixed:
- **Missing tables**: Fixed by importing all 7 models
- **Foreign key violations**: Fixed by creating Projects before Items/Links
- **Incomplete schema**: Fixed by ensuring all models are registered with Base.metadata

These fixes establish clear patterns and best practices for future test development, ensuring database integrity and test reliability.
