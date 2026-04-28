"""Unit tests for repository transaction handling."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

# Use link_test_setup fixture for link-related tests
pytestmark = pytest.mark.usefixtures("link_test_setup")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_soft_delete_cascades_to_children(db_session: AsyncSession) -> None:
    """Test soft delete cascades to child items."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project")

    item_repo = ItemRepository(db_session)

    # Create parent item
    parent = await item_repo.create(
        project_id=project.id,
        title="Parent Item",
        view="FEATURE",
        item_type="feature",
    )

    # Create child items
    child1 = await item_repo.create(
        project_id=project.id,
        title="Child 1",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
    )

    child2 = await item_repo.create(
        project_id=project.id,
        title="Child 2",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
    )

    # Soft delete parent
    result = await item_repo.delete(parent.id, soft=True)
    assert result is True

    # Verify parent is deleted
    await db_session.commit()
    parent_check = await item_repo.get_by_id(parent.id)
    assert parent_check is None

    # Verify children are also soft deleted
    child1_check = await item_repo.get_by_id(child1.id)
    child2_check = await item_repo.get_by_id(child2.id)
    assert child1_check is None
    assert child2_check is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_hard_delete_removes_links(db_session: AsyncSession) -> None:
    """Test hard delete removes associated links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Hard Delete Test Project")

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature",
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature",
    )

    # Create link between items
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="related",
    )

    # Hard delete item1
    result = await item_repo.delete(item1.id, soft=False)
    assert result is True

    # Verify link is also deleted
    await db_session.commit()
    link_check = await link_repo.get_by_id(link.id)
    assert link_check is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restore_soft_deleted_item(db_session: AsyncSession) -> None:
    """Test restoring a soft-deleted item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Restore Test Project")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
    )

    # Soft delete
    await item_repo.delete(item.id, soft=True)
    await db_session.commit()

    # Verify deleted
    deleted_check = await item_repo.get_by_id(item.id)
    assert deleted_check is None

    # Restore
    restored = await item_repo.restore(item.id)
    assert restored is not None
    assert restored.id == item.id
    assert restored.deleted_at is None

    # Verify restored item is queryable
    await db_session.commit()
    restored_check = await item_repo.get_by_id(item.id)
    assert restored_check is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_multiple_updates_increment_version(db_session: AsyncSession) -> None:
    """Test multiple updates correctly increment version."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Version Test Project")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
    )

    assert item.version == 1

    # First update
    updated1 = await item_repo.update(item.id, expected_version=1, title="Update 1")
    assert updated1.version == COUNT_TWO

    # Second update
    updated2 = await item_repo.update(item.id, expected_version=2, title="Update 2")
    assert updated2.version == COUNT_THREE

    # Third update
    updated3 = await item_repo.update(item.id, expected_version=3, title="Update 3")
    assert updated3.version == COUNT_FOUR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_item_by_links_count(db_session: AsyncSession) -> None:
    """Test deleting all links for an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Delete Links Test Project")

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(
        project_id=project.id,
        title="Item 1",
        view="FEATURE",
        item_type="feature",
    )
    item2 = await item_repo.create(
        project_id=project.id,
        title="Item 2",
        view="FEATURE",
        item_type="feature",
    )
    item3 = await item_repo.create(
        project_id=project.id,
        title="Item 3",
        view="FEATURE",
        item_type="feature",
    )

    # Create multiple links from item1
    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="related",
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item3.id,
        link_type="related",
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=item3.id,
        target_item_id=item1.id,
        link_type="depends",
    )

    # Delete all links for item1
    count = await link_repo.delete_by_item(item1.id)
    assert count == COUNT_THREE

    # Verify links are deleted
    await db_session.commit()
    remaining = await link_repo.get_by_item(item1.id)
    assert len(remaining) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_project_update_partial_fields(db_session: AsyncSession) -> None:
    """Test updating only specific project fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(
        name="Original Name",
        description="Original Description",
        metadata={"key": "value"},
    )

    # Update only name
    updated = await project_repo.update(project.id, name="New Name")
    assert updated is not None
    u = updated
    assert u.name == "New Name"
    assert u.description == "Original Description"
    assert u.metadata == {"key": "value"}

    # Update only description
    updated = await project_repo.update(project.id, description="New Description")
    assert updated is not None
    u = updated
    assert u.name == "New Name"
    assert u.description == "New Description"
    assert u.metadata == {"key": "value"}

    # Update only metadata
    updated = await project_repo.update(project.id, metadata={"new": "data"})
    assert updated is not None
    u = updated
    assert u.name == "New Name"
    assert u.description == "New Description"
    assert u.metadata == {"new": "data"}
