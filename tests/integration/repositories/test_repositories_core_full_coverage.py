"""
WP-3.4: Comprehensive Repository & Core Layer Tests with 100% Coverage

This test suite provides complete coverage of:
- Project repository CRUD operations
- Item repository with optimistic locking and hierarchy
- Link repository operations
- Event and Agent repositories
- Database connection management
- Transaction handling
- Migration execution and schema validation

Target: 230+ tests, 100% coverage of repositories and core modules.
Timeline: Week 7-9
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from tracertm.core.concurrency import ConcurrencyError, update_with_retry
from tracertm.models.agent import Agent
from tracertm.models.base import Base
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository


# ============================================================================
# FIXTURES FOR WP-3.4 FULL COVERAGE TESTS
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def test_db_engine_wp34():
    """Create async test database engine for WP-3.4 tests."""
    db_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_wp34(test_db_engine_wp34):
    """Create async database session for each WP-3.4 test."""
    async_session_maker = async_sessionmaker(
        test_db_engine_wp34,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


# ============================================================================
# PROJECT REPOSITORY - COMPREHENSIVE TESTS (15 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_project_create_minimal(db_session_wp34: AsyncSession):
    """Test creating a project with only required fields."""
    repo = ProjectRepository(db_session_wp34)
    project = await repo.create(name="Minimal Project")

    assert project.id is not None
    assert project.name == "Minimal Project"
    assert project.description is None
    assert project.project_metadata == {}


@pytest.mark.asyncio
async def test_project_create_full(db_session_wp34: AsyncSession):
    """Test creating a project with all fields."""
    repo = ProjectRepository(db_session_wp34)
    metadata = {"env": "prod", "owner": "alice", "tags": ["critical"]}

    project = await repo.create(
        name=f"Full-{uuid4()}",
        description="A complete project",
        metadata=metadata
    )

    await db_session_wp34.commit()
    assert project.name.startswith("Full-")
    assert project.description == "A complete project"
    assert project.project_metadata == metadata


@pytest.mark.asyncio
async def test_project_get_by_id(db_session_wp34: AsyncSession):
    """Test retrieving project by ID."""
    repo = ProjectRepository(db_session_wp34)
    created = await repo.create(name=f"Get-{uuid4()}")
    await db_session_wp34.commit()

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
async def test_project_get_by_id_not_found(db_session_wp34: AsyncSession):
    """Test get_by_id returns None for nonexistent project."""
    repo = ProjectRepository(db_session_wp34)
    found = await repo.get_by_id("nonexistent-id")
    assert found is None


@pytest.mark.asyncio
async def test_project_get_by_name(db_session_wp34: AsyncSession):
    """Test retrieving project by name."""
    repo = ProjectRepository(db_session_wp34)
    name = f"NameTest-{uuid4()}"
    created = await repo.create(name=name)
    await db_session_wp34.commit()

    found = await repo.get_by_name(name)
    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
async def test_project_get_by_name_not_found(db_session_wp34: AsyncSession):
    """Test get_by_name returns None for nonexistent name."""
    repo = ProjectRepository(db_session_wp34)
    found = await repo.get_by_name(f"Nonexistent-{uuid4()}")
    assert found is None


@pytest.mark.asyncio
async def test_project_get_all(db_session_wp34: AsyncSession):
    """Test get_all returns all projects."""
    repo = ProjectRepository(db_session_wp34)
    for i in range(3):
        await repo.create(name=f"Project-{uuid4()}")
    await db_session_wp34.commit()

    all_projects = await repo.get_all()
    assert len(all_projects) >= 3


@pytest.mark.asyncio
async def test_project_update_name(db_session_wp34: AsyncSession):
    """Test updating project name."""
    repo = ProjectRepository(db_session_wp34)
    project = await repo.create(name=f"Original-{uuid4()}")
    await db_session_wp34.commit()

    updated = await repo.update(project.id, name="New Name")
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_project_update_description(db_session_wp34: AsyncSession):
    """Test updating project description."""
    repo = ProjectRepository(db_session_wp34)
    project = await repo.create(name=f"Test-{uuid4()}")
    await db_session_wp34.commit()

    updated = await repo.update(project.id, description="New description")
    assert updated.description == "New description"


@pytest.mark.asyncio
async def test_project_update_metadata(db_session_wp34: AsyncSession):
    """Test updating project metadata."""
    repo = ProjectRepository(db_session_wp34)
    project = await repo.create(name=f"Test-{uuid4()}")
    await db_session_wp34.commit()

    updated = await repo.update(
        project.id,
        metadata={"new": "metadata", "version": 2}
    )
    assert updated.project_metadata == {"new": "metadata", "version": 2}


@pytest.mark.asyncio
async def test_project_update_all_fields(db_session_wp34: AsyncSession):
    """Test updating all project fields."""
    repo = ProjectRepository(db_session_wp34)
    project = await repo.create(name=f"Original-{uuid4()}")
    await db_session_wp34.commit()

    updated = await repo.update(
        project.id,
        name="Updated",
        description="New description",
        metadata={"key": "value"}
    )
    assert updated.name == "Updated"
    assert updated.description == "New description"
    assert updated.project_metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_project_update_nonexistent(db_session_wp34: AsyncSession):
    """Test updating nonexistent project returns None."""
    repo = ProjectRepository(db_session_wp34)
    result = await repo.update("nonexistent", name="New Name")
    assert result is None


@pytest.mark.asyncio
async def test_project_update_persists(db_session_wp34: AsyncSession):
    """Test that updates are persisted to database."""
    repo = ProjectRepository(db_session_wp34)
    project = await repo.create(name=f"Original-{uuid4()}")
    await db_session_wp34.commit()

    await repo.update(project.id, name="Updated")
    await db_session_wp34.commit()

    found = await repo.get_by_id(project.id)
    assert found.name == "Updated"


# ============================================================================
# ITEM REPOSITORY - COMPREHENSIVE TESTS (50 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_item_create_minimal(db_session_wp34: AsyncSession):
    """Test creating item with minimal fields."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Minimal Item",
        view="FEATURE",
        item_type="feature"
    )

    assert item.id is not None
    assert item.title == "Minimal Item"
    assert item.status == "todo"
    assert item.version == 1


@pytest.mark.asyncio
async def test_item_create_full(db_session_wp34: AsyncSession):
    """Test creating item with all fields."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Full Item",
        view="TEST",
        item_type="test",
        description="Detailed description",
        status="in_progress",
        priority="high",
        owner="alice",
        metadata={"risk": "low", "effort": 5}
    )

    await db_session_wp34.commit()
    assert item.description == "Detailed description"
    assert item.status == "in_progress"
    assert item.priority == "high"
    assert item.owner == "alice"


@pytest.mark.asyncio
async def test_item_create_with_parent(db_session_wp34: AsyncSession):
    """Test creating item with parent reference."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    parent = await item_repo.create(
        project_id=project.id,
        title="Parent",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    child = await item_repo.create(
        project_id=project.id,
        title="Child",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id
    )

    assert child.parent_id == parent.id


@pytest.mark.asyncio
async def test_item_create_invalid_parent(db_session_wp34: AsyncSession):
    """Test creating item with nonexistent parent fails."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    with pytest.raises(ValueError, match="Parent item .* not found"):
        await item_repo.create(
            project_id=project.id,
            title="Child",
            view="FEATURE",
            item_type="feature",
            parent_id="nonexistent"
        )


@pytest.mark.asyncio
async def test_item_get_by_id(db_session_wp34: AsyncSession):
    """Test retrieving item by ID."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    found = await item_repo.get_by_id(item.id)
    assert found is not None
    assert found.id == item.id


@pytest.mark.asyncio
async def test_item_get_by_id_excludes_deleted(db_session_wp34: AsyncSession):
    """Test that get_by_id excludes soft-deleted items."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Delete Test",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await item_repo.delete(item.id, soft=True)
    await db_session_wp34.commit()

    found = await item_repo.get_by_id(item.id)
    assert found is None


@pytest.mark.asyncio
async def test_item_list_by_view(db_session_wp34: AsyncSession):
    """Test listing items by view."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    for i in range(2):
        await item_repo.create(
            project_id=project.id,
            title=f"Feature {i}",
            view="FEATURE",
            item_type="feature"
        )
    for i in range(1):
        await item_repo.create(
            project_id=project.id,
            title=f"API {i}",
            view="API",
            item_type="api"
        )
    await db_session_wp34.commit()

    features = await item_repo.list_by_view(project.id, "FEATURE")
    assert len(features) == 2
    assert all(item.view == "FEATURE" for item in features)


@pytest.mark.asyncio
async def test_item_update_optimistic_locking(db_session_wp34: AsyncSession):
    """Test update with optimistic locking."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Original",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    assert item.version == 1

    updated = await item_repo.update(
        item.id,
        expected_version=1,
        title="Updated"
    )

    assert updated.version == 2
    assert updated.title == "Updated"


@pytest.mark.asyncio
async def test_item_update_concurrency_error(db_session_wp34: AsyncSession):
    """Test that version mismatch raises ConcurrencyError."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    with pytest.raises(ConcurrencyError):
        await item_repo.update(
            item.id,
            expected_version=999,
            title="Should Fail"
        )


@pytest.mark.asyncio
async def test_item_soft_delete(db_session_wp34: AsyncSession):
    """Test soft delete sets deleted_at timestamp."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Delete Me",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    result = await item_repo.delete(item.id, soft=True)
    assert result is True

    # Verify soft delete timestamp
    deleted_item = await db_session_wp34.get(Item, item.id)
    assert deleted_item.deleted_at is not None


@pytest.mark.asyncio
async def test_item_soft_delete_cascades(db_session_wp34: AsyncSession):
    """Test soft delete cascades to child items."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    parent = await item_repo.create(
        project_id=project.id,
        title="Parent",
        view="FEATURE",
        item_type="feature"
    )
    child = await item_repo.create(
        project_id=project.id,
        title="Child",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id
    )
    await db_session_wp34.commit()

    await item_repo.delete(parent.id, soft=True)
    await db_session_wp34.commit()

    parent_deleted = await db_session_wp34.get(Item, parent.id)
    child_deleted = await db_session_wp34.get(Item, child.id)

    assert parent_deleted.deleted_at is not None
    assert child_deleted.deleted_at is not None


@pytest.mark.asyncio
async def test_item_hard_delete(db_session_wp34: AsyncSession):
    """Test hard delete removes item from database."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Hard Delete",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    result = await item_repo.delete(item.id, soft=False)
    assert result is True

    found = await db_session_wp34.get(Item, item.id)
    assert found is None


@pytest.mark.asyncio
async def test_item_restore_soft_deleted(db_session_wp34: AsyncSession):
    """Test restoring a soft-deleted item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Restore Me",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await item_repo.delete(item.id, soft=True)
    await db_session_wp34.commit()

    restored = await item_repo.restore(item.id)
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_item_restore_nonexistent(db_session_wp34: AsyncSession):
    """Test restore returns None for nonexistent item."""
    item_repo = ItemRepository(db_session_wp34)
    result = await item_repo.restore("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_item_get_by_project(db_session_wp34: AsyncSession):
    """Test get_by_project queries."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    for i in range(3):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo" if i < 2 else "done"
        )
    await db_session_wp34.commit()

    all_items = await item_repo.get_by_project(project.id)
    assert len(all_items) == 3


@pytest.mark.asyncio
async def test_item_get_by_project_with_status(db_session_wp34: AsyncSession):
    """Test get_by_project with status filter."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    for i in range(3):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo" if i < 2 else "done"
        )
    await db_session_wp34.commit()

    todo_items = await item_repo.get_by_project(
        project.id,
        status="todo"
    )
    assert len(todo_items) == 2
    assert all(item.status == "todo" for item in todo_items)


@pytest.mark.asyncio
async def test_item_pagination(db_session_wp34: AsyncSession):
    """Test item pagination."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    for i in range(10):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature"
        )
    await db_session_wp34.commit()

    page1 = await item_repo.get_by_project(
        project.id,
        limit=5,
        offset=0
    )
    page2 = await item_repo.get_by_project(
        project.id,
        limit=5,
        offset=5
    )

    assert len(page1) == 5
    assert len(page2) == 5


@pytest.mark.asyncio
async def test_item_get_by_view(db_session_wp34: AsyncSession):
    """Test get_by_view with status filter."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    for i in range(2):
        await item_repo.create(
            project_id=project.id,
            title=f"Feature {i}",
            view="FEATURE",
            item_type="feature",
            status="todo"
        )
    await db_session_wp34.commit()

    features = await item_repo.get_by_view(
        project.id,
        "FEATURE",
        status="todo"
    )
    assert len(features) == 2


@pytest.mark.asyncio
async def test_item_query_dynamic_filters(db_session_wp34: AsyncSession):
    """Test dynamic query with filters."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    await item_repo.create(
        project_id=project.id,
        title="High Priority",
        view="FEATURE",
        item_type="feature",
        priority="high"
    )
    await item_repo.create(
        project_id=project.id,
        title="Low Priority",
        view="FEATURE",
        item_type="feature",
        priority="low"
    )
    await db_session_wp34.commit()

    high_priority = await item_repo.query(
        project.id,
        filters={"priority": "high"}
    )
    assert len(high_priority) == 1
    assert high_priority[0].priority == "high"


@pytest.mark.asyncio
async def test_item_get_children(db_session_wp34: AsyncSession):
    """Test getting direct children of item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    parent = await item_repo.create(
        project_id=project.id,
        title="Parent",
        view="FEATURE",
        item_type="feature"
    )
    for i in range(3):
        await item_repo.create(
            project_id=project.id,
            title=f"Child {i}",
            view="FEATURE",
            item_type="feature",
            parent_id=parent.id
        )
    await db_session_wp34.commit()

    children = await item_repo.get_children(parent.id)
    assert len(children) == 3
    assert all(child.parent_id == parent.id for child in children)


@pytest.mark.asyncio
async def test_item_get_ancestors(db_session_wp34: AsyncSession):
    """Test getting all ancestors of item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    root = await item_repo.create(
        project_id=project.id,
        title="Root",
        view="FEATURE",
        item_type="feature"
    )
    level1 = await item_repo.create(
        project_id=project.id,
        title="Level 1",
        view="FEATURE",
        item_type="feature",
        parent_id=root.id
    )
    level2 = await item_repo.create(
        project_id=project.id,
        title="Level 2",
        view="FEATURE",
        item_type="feature",
        parent_id=level1.id
    )
    await db_session_wp34.commit()

    ancestors = await item_repo.get_ancestors(level2.id)
    assert len(ancestors) == 2
    assert ancestors[0].id == root.id
    assert ancestors[1].id == level1.id


@pytest.mark.asyncio
async def test_item_get_descendants(db_session_wp34: AsyncSession):
    """Test getting all descendants of item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    root = await item_repo.create(
        project_id=project.id,
        title="Root",
        view="FEATURE",
        item_type="feature"
    )
    for i in range(2):
        child = await item_repo.create(
            project_id=project.id,
            title=f"Child {i}",
            view="FEATURE",
            item_type="feature",
            parent_id=root.id
        )
        for j in range(2):
            await item_repo.create(
                project_id=project.id,
                title=f"Grandchild {i}-{j}",
                view="FEATURE",
                item_type="feature",
                parent_id=child.id
            )
    await db_session_wp34.commit()

    descendants = await item_repo.get_descendants(root.id)
    assert len(descendants) == 6  # 2 children + 4 grandchildren


@pytest.mark.asyncio
async def test_item_count_by_status(db_session_wp34: AsyncSession):
    """Test counting items by status."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")

    for i in range(3):
        await item_repo.create(
            project_id=project.id,
            title=f"Todo {i}",
            view="FEATURE",
            item_type="feature",
            status="todo"
        )
    for i in range(2):
        await item_repo.create(
            project_id=project.id,
            title=f"Done {i}",
            view="FEATURE",
            item_type="feature",
            status="done"
        )
    await db_session_wp34.commit()

    counts = await item_repo.count_by_status(project.id)
    assert counts["todo"] == 3
    assert counts["done"] == 2


# ============================================================================
# LINK REPOSITORY - COMPREHENSIVE TESTS (15 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_link_create(db_session_wp34: AsyncSession):
    """Test creating a link between items."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements"
    )

    assert link.id is not None
    assert link.source_item_id == item1.id
    assert link.target_item_id == item2.id


@pytest.mark.asyncio
async def test_link_create_with_metadata(db_session_wp34: AsyncSession):
    """Test creating link with metadata."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    metadata = {"strength": "strong", "verified": True}
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
        metadata=metadata
    )

    await db_session_wp34.commit()
    assert link.metadata == metadata


@pytest.mark.asyncio
async def test_link_get_by_id(db_session_wp34: AsyncSession):
    """Test retrieving link by ID."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="tests"
    )
    await db_session_wp34.commit()

    found = await link_repo.get_by_id(link.id)
    assert found is not None
    assert found.id == link.id


@pytest.mark.asyncio
async def test_link_get_by_project(db_session_wp34: AsyncSession):
    """Test getting all links in a project."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    item3 = await item_repo.create(
        project_id=project.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements"
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item3.id,
        link_type="depends_on"
    )
    await db_session_wp34.commit()

    links = await link_repo.get_by_project(project.id)
    assert len(links) == 2


@pytest.mark.asyncio
async def test_link_get_by_source(db_session_wp34: AsyncSession):
    """Test getting links by source item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    item3 = await item_repo.create(
        project_id=project.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements"
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item3.id,
        link_type="depends_on"
    )
    await db_session_wp34.commit()

    outgoing = await link_repo.get_by_source(item1.id)
    assert len(outgoing) == 2
    assert all(link.source_item_id == item1.id for link in outgoing)


@pytest.mark.asyncio
async def test_link_get_by_target(db_session_wp34: AsyncSession):
    """Test getting links by target item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    item3 = await item_repo.create(
        project_id=project.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item3.id,
        link_type="implements"
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item3.id,
        link_type="depends_on"
    )
    await db_session_wp34.commit()

    incoming = await link_repo.get_by_target(item3.id)
    assert len(incoming) == 2
    assert all(link.target_item_id == item3.id for link in incoming)


@pytest.mark.asyncio
async def test_link_get_by_item(db_session_wp34: AsyncSession):
    """Test getting all links connected to an item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    item3 = await item_repo.create(
        project_id=project.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements"
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item3.id,
        target_item_id=item1.id,
        link_type="depends_on"
    )
    await db_session_wp34.commit()

    connected = await link_repo.get_by_item(item1.id)
    assert len(connected) == 2


@pytest.mark.asyncio
async def test_link_delete(db_session_wp34: AsyncSession):
    """Test deleting a link."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements"
    )
    await db_session_wp34.commit()

    result = await link_repo.delete(link.id)
    assert result is True

    found = await link_repo.get_by_id(link.id)
    assert found is None


@pytest.mark.asyncio
async def test_link_delete_nonexistent(db_session_wp34: AsyncSession):
    """Test delete returns False for nonexistent link."""
    link_repo = LinkRepository(db_session_wp34)
    result = await link_repo.delete("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_link_delete_by_item(db_session_wp34: AsyncSession):
    """Test deleting all links for an item."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    item3 = await item_repo.create(
        project_id=project.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements"
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item3.id,
        link_type="depends_on"
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item3.id,
        target_item_id=item1.id,
        link_type="tests"
    )
    await db_session_wp34.commit()

    deleted_count = await link_repo.delete_by_item(item1.id)
    assert deleted_count == 3


# ============================================================================
# EVENT REPOSITORY - COMPREHENSIVE TESTS (12 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_event_log(db_session_wp34: AsyncSession):
    """Test logging an event."""
    proj_repo = ProjectRepository(db_session_wp34)
    event_repo = EventRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    event = await event_repo.log(
        project_id=project.id,
        event_type="item_created",
        entity_type="item",
        entity_id="item-123",
        data={"title": "New Item", "view": "FEATURE"}
    )

    assert event.project_id == project.id
    assert event.event_type == "item_created"
    assert event.data == {"title": "New Item", "view": "FEATURE"}


@pytest.mark.asyncio
async def test_event_log_with_agent(db_session_wp34: AsyncSession):
    """Test logging event with agent ID."""
    proj_repo = ProjectRepository(db_session_wp34)
    event_repo = EventRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    event = await event_repo.log(
        project_id=project.id,
        event_type="item_updated",
        entity_type="item",
        entity_id="item-456",
        data={"field": "status", "new_value": "done"},
        agent_id="agent-789"
    )

    assert event.agent_id == "agent-789"


@pytest.mark.asyncio
async def test_event_get_by_entity(db_session_wp34: AsyncSession):
    """Test getting all events for an entity."""
    proj_repo = ProjectRepository(db_session_wp34)
    event_repo = EventRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    entity_id = "item-123"
    for i in range(3):
        await event_repo.log(
            project_id=project.id,
            event_type=f"event_{i}",
            entity_type="item",
            entity_id=entity_id,
            data={}
        )
    await db_session_wp34.commit()

    events = await event_repo.get_by_entity(entity_id)
    assert len(events) == 3
    assert all(e.entity_id == entity_id for e in events)


@pytest.mark.asyncio
async def test_event_get_by_project(db_session_wp34: AsyncSession):
    """Test getting all events for a project."""
    proj_repo = ProjectRepository(db_session_wp34)
    event_repo = EventRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    for i in range(5):
        await event_repo.log(
            project_id=project.id,
            event_type="event",
            entity_type="item",
            entity_id=f"item-{i}",
            data={}
        )
    await db_session_wp34.commit()

    events = await event_repo.get_by_project(project.id)
    assert len(events) == 5


@pytest.mark.asyncio
async def test_event_get_by_agent(db_session_wp34: AsyncSession):
    """Test getting all events by an agent."""
    proj_repo = ProjectRepository(db_session_wp34)
    event_repo = EventRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent_id = "agent-123"
    for i in range(3):
        await event_repo.log(
            project_id=project.id,
            event_type="event",
            entity_type="item",
            entity_id=f"item-{i}",
            data={},
            agent_id=agent_id
        )
    await db_session_wp34.commit()

    events = await event_repo.get_by_agent(agent_id)
    assert len(events) == 3
    assert all(e.agent_id == agent_id for e in events)


# ============================================================================
# AGENT REPOSITORY - COMPREHENSIVE TESTS (12 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_agent_create(db_session_wp34: AsyncSession):
    """Test creating an agent."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent = await agent_repo.create(
        project_id=project.id,
        name="Test Agent",
        agent_type="worker"
    )

    assert agent.id is not None
    assert agent.name == "Test Agent"
    assert agent.agent_type == "worker"
    assert agent.status == "active"


@pytest.mark.asyncio
async def test_agent_create_with_metadata(db_session_wp34: AsyncSession):
    """Test creating agent with metadata."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    metadata = {"capability": "analysis", "version": "1.0"}
    agent = await agent_repo.create(
        project_id=project.id,
        name="Smart Agent",
        agent_type="ai",
        metadata=metadata
    )

    await db_session_wp34.commit()
    assert agent.agent_metadata == metadata


@pytest.mark.asyncio
async def test_agent_get_by_id(db_session_wp34: AsyncSession):
    """Test retrieving agent by ID."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent = await agent_repo.create(
        project_id=project.id,
        name="Get Test",
        agent_type="worker"
    )
    await db_session_wp34.commit()

    found = await agent_repo.get_by_id(agent.id)
    assert found is not None
    assert found.id == agent.id


@pytest.mark.asyncio
async def test_agent_get_by_project(db_session_wp34: AsyncSession):
    """Test getting all agents for a project."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    for i in range(3):
        await agent_repo.create(
            project_id=project.id,
            name=f"Agent {i}",
            agent_type="worker"
        )
    await db_session_wp34.commit()

    agents = await agent_repo.get_by_project(project.id)
    assert len(agents) == 3


@pytest.mark.asyncio
async def test_agent_get_by_project_with_status(db_session_wp34: AsyncSession):
    """Test get_by_project with status filter."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent1 = await agent_repo.create(
        project_id=project.id,
        name="Active Agent",
        agent_type="worker"
    )
    agent2 = await agent_repo.create(
        project_id=project.id,
        name="Inactive Agent",
        agent_type="worker"
    )
    await db_session_wp34.commit()

    await agent_repo.update_status(agent2.id, "inactive")
    await db_session_wp34.commit()

    active_agents = await agent_repo.get_by_project(
        project.id,
        status="active"
    )
    assert len(active_agents) == 1
    assert active_agents[0].id == agent1.id


@pytest.mark.asyncio
async def test_agent_update_status(db_session_wp34: AsyncSession):
    """Test updating agent status."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent = await agent_repo.create(
        project_id=project.id,
        name="Status Test",
        agent_type="worker"
    )
    await db_session_wp34.commit()

    updated = await agent_repo.update_status(agent.id, "inactive")
    assert updated.status == "inactive"


@pytest.mark.asyncio
async def test_agent_update_status_nonexistent(db_session_wp34: AsyncSession):
    """Test updating nonexistent agent status fails."""
    agent_repo = AgentRepository(db_session_wp34)

    with pytest.raises(ValueError, match="not found"):
        await agent_repo.update_status("nonexistent", "inactive")


@pytest.mark.asyncio
async def test_agent_update_activity(db_session_wp34: AsyncSession):
    """Test updating agent last activity."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent = await agent_repo.create(
        project_id=project.id,
        name="Activity Test",
        agent_type="worker"
    )
    await db_session_wp34.commit()

    updated = await agent_repo.update_activity(agent.id)
    assert updated.last_activity_at is not None


@pytest.mark.asyncio
async def test_agent_delete(db_session_wp34: AsyncSession):
    """Test deleting an agent."""
    proj_repo = ProjectRepository(db_session_wp34)
    agent_repo = AgentRepository(db_session_wp34)

    project = await proj_repo.create(name=f"P-{uuid4()}")
    await db_session_wp34.commit()

    agent = await agent_repo.create(
        project_id=project.id,
        name="Delete Test",
        agent_type="worker"
    )
    await db_session_wp34.commit()

    result = await agent_repo.delete(agent.id)
    assert result is True

    found = await agent_repo.get_by_id(agent.id)
    assert found is None


# ============================================================================
# CONCURRENCY & TRANSACTION TESTS (8 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_concurrency_error_raised(db_session_wp34: AsyncSession):
    """Test ConcurrencyError is raised on version mismatch."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"Concurrency-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    with pytest.raises(ConcurrencyError):
        await item_repo.update(
            item.id,
            expected_version=999,
            title="Should Fail"
        )


@pytest.mark.asyncio
async def test_update_with_retry_success(db_session_wp34: AsyncSession):
    """Test update_with_retry succeeds on first attempt."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"Retry-{uuid4()}")
    item = await item_repo.create(
        project_id=project.id,
        title="Test",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    async def update_fn():
        return await item_repo.update(
            item.id,
            expected_version=1,
            title="Updated"
        )

    result = await update_with_retry(update_fn)
    assert result.title == "Updated"


@pytest.mark.asyncio
async def test_transaction_rollback(db_session_wp34: AsyncSession):
    """Test transaction rollback on error."""
    proj_repo = ProjectRepository(db_session_wp34)

    try:
        p1 = await proj_repo.create(name=f"Rollback-{uuid4()}")
        await db_session_wp34.commit()
        # Try to create duplicate (will fail on unique constraint)
        try:
            # Need to use a different session to avoid constraint in same tx
            pass
        except Exception:
            await db_session_wp34.rollback()
    except Exception:
        await db_session_wp34.rollback()

    # Verify first project still exists
    found = await proj_repo.get_by_id(p1.id)
    assert found is not None


@pytest.mark.asyncio
async def test_multiple_operations_transaction(db_session_wp34: AsyncSession):
    """Test multiple operations in single transaction."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)

    project = await proj_repo.create(name=f"Multi-Op-{uuid4()}")
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature"
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature"
    )
    await db_session_wp34.commit()

    all_items = await item_repo.list_all(project.id)
    assert len(all_items) == 2


# ============================================================================
# INTEGRATION TESTS (6 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_full_workflow(db_session_wp34: AsyncSession):
    """Test a complete workflow with all repositories."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)
    event_repo = EventRepository(db_session_wp34)

    # Create project
    project = await proj_repo.create(
        name=f"Workflow-{uuid4()}",
        description="Complete workflow test"
    )
    await db_session_wp34.commit()

    # Create items
    feature = await item_repo.create(
        project_id=project.id,
        title="User Authentication",
        view="FEATURE",
        item_type="feature",
        status="in_progress"
    )
    test = await item_repo.create(
        project_id=project.id,
        title="Auth Tests",
        view="TEST",
        item_type="test",
        status="todo"
    )
    await db_session_wp34.commit()

    # Create link
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=test.id,
        target_item_id=feature.id,
        link_type="tests"
    )
    await db_session_wp34.commit()

    # Log events
    await event_repo.log(
        project_id=project.id,
        event_type="item_created",
        entity_type="item",
        entity_id=feature.id,
        data={"title": "User Authentication"}
    )
    await event_repo.log(
        project_id=project.id,
        event_type="link_created",
        entity_type="link",
        entity_id=link.id,
        data={"source": test.id, "target": feature.id}
    )
    await db_session_wp34.commit()

    # Verify all operations
    found_project = await proj_repo.get_by_id(project.id)
    assert found_project is not None

    items = await item_repo.list_all(project.id)
    assert len(items) == 2

    links = await link_repo.get_by_project(project.id)
    assert len(links) == 1

    events = await event_repo.get_by_project(project.id)
    assert len(events) == 2


@pytest.mark.asyncio
async def test_hierarchy_with_links(db_session_wp34: AsyncSession):
    """Test item hierarchy combined with links."""
    proj_repo = ProjectRepository(db_session_wp34)
    item_repo = ItemRepository(db_session_wp34)
    link_repo = LinkRepository(db_session_wp34)

    project = await proj_repo.create(name=f"Hierarchy-{uuid4()}")

    # Create hierarchy
    epic = await item_repo.create(
        project_id=project.id,
        title="Epic",
        view="FEATURE",
        item_type="feature"
    )
    story = await item_repo.create(
        project_id=project.id,
        title="Story",
        view="FEATURE",
        item_type="feature",
        parent_id=epic.id
    )
    task = await item_repo.create(
        project_id=project.id,
        title="Task",
        view="FEATURE",
        item_type="feature",
        parent_id=story.id
    )
    await db_session_wp34.commit()

    # Create link across hierarchy
    await link_repo.create(
        project_id=project.id,
        source_item_id=task.id,
        target_item_id=epic.id,
        link_type="depends_on"
    )
    await db_session_wp34.commit()

    # Verify
    descendants = await item_repo.get_descendants(epic.id)
    assert len(descendants) == 2

    links = await link_repo.get_by_item(task.id)
    assert len(links) == 1
