"""Unit tests for ItemRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_item(db_session: AsyncSession) -> None:
    """Test creating an item."""
    # Create project first
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id=project.id,
        title="Test Feature",
        view="FEATURE",
        item_type="feature",
        description="Test description",
        status="todo",
    )

    assert item.id is not None
    assert item.title == "Test Feature"
    assert item.view == "FEATURE"
    assert item.item_type == "feature"
    assert item.status == "todo"
    assert item.version == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession) -> None:
    """Test retrieving an item by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    repo = ItemRepository(db_session)
    created = await repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    retrieved = await repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == created.title


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving non-existent item returns None."""
    repo = ItemRepository(db_session)
    item = await repo.get_by_id("non-existent-id")
    assert item is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_item(db_session: AsyncSession) -> None:
    """Test updating an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id=project.id,
        title="Original Title",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    updated = await repo.update(
        item_id=item.id,
        expected_version=item.version,
        title="Updated Title",
        status="in_progress",
    )

    assert updated.title == "Updated Title"
    assert updated.status == "in_progress"
    assert updated.version == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_optimistic_locking(db_session: AsyncSession) -> None:
    """Test optimistic locking prevents concurrent updates."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    original_version = item.version

    # First update succeeds
    updated = await repo.update(
        item_id=item.id,
        expected_version=original_version,
        status="in_progress",
    )

    assert updated.version == original_version + 1

    # Second update with stale version fails
    with pytest.raises(ConcurrencyError):
        await repo.update(
            item_id=item.id,
            expected_version=original_version,  # Stale version
            status="done",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_item(db_session: AsyncSession) -> None:
    """Test soft deleting an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    await repo.delete(item.id)

    # Item should not be retrievable after deletion
    deleted = await repo.get_by_id(item.id)
    assert deleted is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project(db_session: AsyncSession) -> None:
    """Test listing items by project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name="Project 1", description="Test")
    project2 = await project_repo.create(name="Project 2", description="Test")

    repo = ItemRepository(db_session)

    # Create items in project 1
    await repo.create(
        project_id=project1.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await repo.create(
        project_id=project1.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    # Create item in project 2
    await repo.create(
        project_id=project2.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    # List items in project 1 using get_by_view
    items = await repo.get_by_view(project1.id, "FEATURE")
    assert len(items) == COUNT_TWO
    assert all(item.project_id == project1.id for item in items)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status(db_session: AsyncSession) -> None:
    """Test counting items by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)

    # Create items with different statuses
    for i in range(3):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

    for i in range(2):
        await item_repo.create(
            project_id=project.id,
            title=f"Done Item {i}",
            view="FEATURE",
            item_type="feature",
            status="done",
        )

    counts = await item_repo.count_by_status(project.id)

    assert counts.get("todo") == COUNT_THREE
    assert counts.get("done") == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_items(db_session: AsyncSession) -> None:
    """Test querying items with filters."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)

    # Create items
    for i in range(5):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo" if i < COUNT_THREE else "done",
        )

    # Query with filter
    items = await item_repo.query(
        project_id=project.id,
        filters={"status": "todo"},
    )

    assert len(items) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_multiple_fields(db_session: AsyncSession) -> None:
    """Test updating multiple fields at once."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Original",
        view="FEATURE",
        item_type="feature",
        status="todo",
        description="Original description",
    )

    updated = await item_repo.update(
        item_id=item.id,
        expected_version=item.version,
        title="Updated",
        status="in_progress",
        description="Updated description",
    )

    assert updated.title == "Updated"
    assert updated.status == "in_progress"
    assert updated.description == "Updated description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_view_empty(db_session: AsyncSession) -> None:
    """Test getting items by view when none exist."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)

    items = await item_repo.get_by_view(project.id, "NONEXISTENT")
    assert len(items) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_hard_delete(db_session: AsyncSession) -> None:
    """Test hard delete of item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    # Hard delete
    deleted = await item_repo.delete(item.id, soft=False)
    assert deleted is True

    # Item should not exist
    retrieved = await item_repo.get_by_id(item.id)
    assert retrieved is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_view_with_status_filter(db_session: AsyncSession) -> None:
    """Test getting items by view with status filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)

    # Create items with different statuses
    await item_repo.create(
        project_id=project.id,
        title="Todo Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    await item_repo.create(
        project_id=project.id,
        title="Done Item",
        view="FEATURE",
        item_type="feature",
        status="done",
    )

    # Get only todo items
    items = await item_repo.get_by_view(project.id, "FEATURE", status="todo")
    assert len(items) == 1
    assert items[0].status == "todo"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_with_version_mismatch(db_session: AsyncSession) -> None:
    """Test update fails with version mismatch."""
    from tracertm.core.concurrency import ConcurrencyError

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    # Try to update with wrong version
    with pytest.raises(ConcurrencyError):
        await item_repo.update(
            item_id=item.id,
            expected_version=999,  # Wrong version
            status="done",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_view_with_limit_and_offset(db_session: AsyncSession) -> None:
    """Test pagination with limit and offset."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)

    # Create 5 items
    for i in range(5):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

    # Get first 2
    items = await item_repo.get_by_view(project.id, "FEATURE", limit=2, offset=0)
    assert len(items) == COUNT_TWO

    # Get next 2
    items = await item_repo.get_by_view(project.id, "FEATURE", limit=2, offset=2)
    assert len(items) == COUNT_TWO
