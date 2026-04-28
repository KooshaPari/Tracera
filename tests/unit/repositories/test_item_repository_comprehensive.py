"""Comprehensive unit tests for ItemRepository to achieve 85%+ coverage.

This file covers all missing functionality identified in coverage analysis:
- Parent validation in create()
- Project scoping in get_by_id()
- Include deleted flags in list methods
- Update with optimistic locking
- Delete operations (soft delete cascade, hard delete)
- Restore operations
- get_by_project() with status filtering and pagination
- get_by_view() with status filtering and pagination
- query() with dynamic filtering
- Tree operations (get_children, get_ancestors, get_descendants)
- count_by_status()
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.link import Link
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS - Parent Validation
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_parent_validation_success(db_session: AsyncSession) -> None:
    """Test creating item with valid parent."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(project_id=str(project.id), title="Parent Item", view="EPIC", item_type="epic")
    await db_session.commit()

    # Create child with parent
    child = await item_repo.create(
        project_id=str(project.id),
        title="Child Item",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )

    assert child.parent_id == parent.id
    assert child.project_id == project.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_invalid_parent_raises_error(db_session: AsyncSession) -> None:
    """Test creating item with non-existent parent raises ValueError."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=f"Test Project {uuid4()}")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError, match=r"Parent item .* not found"):
        await item_repo.create(
            project_id=str(project.id),
            title="Orphan Item",
            view="STORY",
            item_type="story",
            parent_id="nonexistent-parent-id",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_parent_different_project_raises_error(db_session: AsyncSession) -> None:
    """Test creating item with parent from different project raises ValueError."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent in project1
    parent = await item_repo.create(project_id=project1.id, title="Parent", view="EPIC", item_type="epic")
    await db_session.commit()

    # Try to create child in project2 with parent from project1
    with pytest.raises(ValueError, match="not in same project"):
        await item_repo.create(
            project_id=str(project2.id),
            title="Child",
            view="STORY",
            item_type="story",
            parent_id=str(parent.id),
        )


# ============================================================================
# GET_BY_ID - Project Scoping
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_with_project_scope_success(db_session: AsyncSession) -> None:
    """Test get_by_id with project_id filter returns item when in correct project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=project1.id, title="Test Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Query with correct project
    found = await item_repo.get_by_id(item.id, project_id=project1.id)
    assert found is not None
    assert found.id == item.id

    # Query with wrong project
    not_found = await item_repo.get_by_id(item.id, project_id=str(project2.id))
    assert not_found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_without_project_scope(db_session: AsyncSession) -> None:
    """Test get_by_id without project_id filter returns item regardless of project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Test Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Query without project scope
    found = await item_repo.get_by_id(item.id)
    assert found is not None
    assert found.id == item.id


# ============================================================================
# LIST_BY_VIEW - Include Deleted Flag
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_view_excludes_deleted_by_default(db_session: AsyncSession) -> None:
    """Test list_by_view excludes deleted items by default."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=str(project.id), title="Active Item", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(
        project_id=str(project.id),
        title="Deleted Item",
        view="FEATURE",
        item_type="feature",
    )
    await db_session.commit()

    # Delete item2
    await item_repo.delete(str(item2.id), soft=True)
    await db_session.commit()

    # List without deleted (default)
    items = await item_repo.list_by_view(project.id, "FEATURE", include_deleted=False)
    assert len(items) == 1
    assert items[0].id == item1.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_view_includes_deleted_when_requested(db_session: AsyncSession) -> None:
    """Test list_by_view includes deleted items when include_deleted=True."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=str(project.id), title="Active Item", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(
        project_id=str(project.id),
        title="Deleted Item",
        view="FEATURE",
        item_type="feature",
    )
    await db_session.commit()

    # Delete item2
    await item_repo.delete(str(item2.id), soft=True)
    await db_session.commit()

    # List with deleted
    items = await item_repo.list_by_view(project.id, "FEATURE", include_deleted=True)
    assert len(items) == COUNT_TWO
    item_ids = {item.id for item in items}
    assert item1.id in item_ids
    assert item2.id in item_ids


# ============================================================================
# LIST_ALL - Include Deleted Flag
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_excludes_deleted_by_default(db_session: AsyncSession) -> None:
    """Test list_all excludes deleted items by default."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=str(project.id), title="Active Item", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Deleted Item", view="STORY", item_type="story")
    await db_session.commit()

    # Delete item2
    await item_repo.delete(str(item2.id), soft=True)
    await db_session.commit()

    # List without deleted (default)
    items = await item_repo.list_all(project.id, include_deleted=False)
    assert len(items) == 1
    assert items[0].id == item1.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_includes_deleted_when_requested(db_session: AsyncSession) -> None:
    """Test list_all includes deleted items when include_deleted=True."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=str(project.id), title="Active Item", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Deleted Item", view="STORY", item_type="story")
    await db_session.commit()

    # Delete item2
    await item_repo.delete(str(item2.id), soft=True)
    await db_session.commit()

    # List with deleted
    items = await item_repo.list_all(project.id, include_deleted=True)
    assert len(items) == COUNT_TWO
    item_ids = {item.id for item in items}
    assert item1.id in item_ids
    assert item2.id in item_ids


# ============================================================================
# UPDATE - Optimistic Locking & Error Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_with_missing_item_raises_error(db_session: AsyncSession) -> None:
    """Test update raises ValueError when item doesn't exist."""
    project_repo = ProjectRepository(db_session)
    _project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError, match=r"Item .* not found"):
        await item_repo.update(item_id="nonexistent-id", expected_version=1, title="Updated")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_with_stale_version_raises_concurrency_error(db_session: AsyncSession) -> None:
    """Test update raises ConcurrencyError when version is stale."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Test Item", view="FEATURE", item_type="feature")
    original_version = item.version
    await db_session.commit()

    # First update succeeds
    updated = await item_repo.update(item_id=item.id, expected_version=original_version, status="in_progress")
    assert updated.version == original_version + 1
    await db_session.commit()

    # Second update with stale version fails
    with pytest.raises(ConcurrencyError, match="was modified by another agent"):
        await item_repo.update(
            item_id=item.id,
            expected_version=original_version,  # Stale version (before first update)
            status="done",
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_version_increments(db_session: AsyncSession) -> None:
    """Test update increments version number."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Test Item", view="FEATURE", item_type="feature")
    original_version = item.version
    await db_session.commit()

    # Update should increment version
    updated = await item_repo.update(item_id=item.id, expected_version=original_version, title="Updated Title")
    assert updated.version == original_version + 1


# ============================================================================
# DELETE - Soft Delete Cascade
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_soft_delete_cascades_to_children(db_session: AsyncSession) -> None:
    """Test soft delete cascades to all children."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(project_id=str(project.id), title="Parent", view="EPIC", item_type="epic")
    await db_session.commit()

    # Create children
    child1 = await item_repo.create(
        project_id=str(project.id),
        title="Child 1",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    child2 = await item_repo.create(
        project_id=str(project.id),
        title="Child 2",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    await db_session.commit()

    # Soft delete parent
    deleted = await item_repo.delete(str(parent.id), soft=True)
    assert deleted is True
    await db_session.commit()

    # Check parent is deleted
    found_parent = await item_repo.get_by_id(parent.id)
    assert found_parent is None

    # Check children are also deleted
    found_child1 = await item_repo.get_by_id(child1.id)
    assert found_child1 is None

    found_child2 = await item_repo.get_by_id(child2.id)
    assert found_child2 is None

    # Verify children have deleted_at set (by querying with include_deleted)
    all_items = await item_repo.list_all(project.id, include_deleted=True)
    deleted_items = [item for item in all_items if item.deleted_at is not None]
    assert len(deleted_items) == COUNT_THREE  # parent + 2 children


@pytest.mark.unit
@pytest.mark.asyncio
async def test_soft_delete_nonexistent_item_returns_false(db_session: AsyncSession) -> None:
    """Test soft delete returns False when item doesn't exist."""
    project_repo = ProjectRepository(db_session)
    _project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    deleted = await item_repo.delete("nonexistent-id", soft=True)
    assert deleted is False


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.usefixtures("link_test_setup")
async def test_hard_delete_removes_links(db_session: AsyncSession) -> None:
    """Test hard delete removes associated links."""
    from tracertm.repositories.link_repository import LinkRepository

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Create link using repository (which handles graph_id)
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="depends_on",
    )
    await db_session.commit()

    # Hard delete item1
    deleted = await item_repo.delete(str(item1.id), soft=False)
    assert deleted is True
    await db_session.commit()

    # Verify link is removed
    from sqlalchemy import select

    result = await db_session.execute(select(Link).where(Link.id == link.id))
    found_link = result.scalar_one_or_none()
    assert found_link is None

    # Verify item is removed
    found_item = await item_repo.get_by_id(item1.id)
    assert found_item is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hard_delete_nonexistent_item_returns_false(db_session: AsyncSession) -> None:
    """Test hard delete returns False when item doesn't exist."""
    project_repo = ProjectRepository(db_session)
    _project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    deleted = await item_repo.delete("nonexistent-id", soft=False)
    assert deleted is False


# ============================================================================
# RESTORE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restore_soft_deleted_item(db_session: AsyncSession) -> None:
    """Test restoring a soft-deleted item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=str(project.id),
        title="To Be Restored",
        view="FEATURE",
        item_type="feature",
    )
    await db_session.commit()

    # Soft delete
    await item_repo.delete(str(item.id), soft=True)
    await db_session.commit()

    # Verify deleted
    found = await item_repo.get_by_id(item.id)
    assert found is None

    # Restore
    restored = await item_repo.restore(item.id)
    assert restored is not None
    assert restored.id == item.id
    assert restored.deleted_at is None
    await db_session.commit()

    # Verify restored
    found = await item_repo.get_by_id(item.id)
    assert found is not None
    assert found.id == item.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restore_nonexistent_item_returns_none(db_session: AsyncSession) -> None:
    """Test restore returns None when item doesn't exist."""
    project_repo = ProjectRepository(db_session)
    _project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    restored = await item_repo.restore("nonexistent-id")
    assert restored is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restore_active_item_returns_none(db_session: AsyncSession) -> None:
    """Test restore returns None when item is not deleted."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Active Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Try to restore active item
    restored = await item_repo.restore(item.id)
    assert restored is None  # Not deleted, so nothing to restore


# ============================================================================
# GET_BY_PROJECT - Status Filtering & Pagination
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_with_status_filter(db_session: AsyncSession) -> None:
    """Test get_by_project filters by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items with different statuses
    await item_repo.create(
        project_id=str(project.id),
        title="Todo Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Done Item",
        view="FEATURE",
        item_type="feature",
        status="done",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Another Todo",
        view="STORY",
        item_type="story",
        status="todo",
    )
    await db_session.commit()

    # Get only todo items
    todo_items = await item_repo.get_by_project(project.id, status="todo")
    assert len(todo_items) == COUNT_TWO
    assert all(item.status == "todo" for item in todo_items)

    # Get only done items
    done_items = await item_repo.get_by_project(project.id, status="done")
    assert len(done_items) == 1
    assert done_items[0].status == "done"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_with_pagination(db_session: AsyncSession) -> None:
    """Test get_by_project supports pagination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create 5 items
    for i in range(5):
        await item_repo.create(project_id=str(project.id), title=f"Item {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Get first page (limit=2)
    page1 = await item_repo.get_by_project(project.id, limit=2, offset=0)
    assert len(page1) == COUNT_TWO

    # Get second page
    page2 = await item_repo.get_by_project(project.id, limit=2, offset=2)
    assert len(page2) == COUNT_TWO

    # Get third page
    page3 = await item_repo.get_by_project(project.id, limit=2, offset=4)
    assert len(page3) == 1

    # Verify no overlap
    page1_ids = {item.id for item in page1}
    page2_ids = {item.id for item in page2}
    page3_ids = {item.id for item in page3}
    assert page1_ids.isdisjoint(page2_ids)
    assert page2_ids.isdisjoint(page3_ids)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_without_status_filter(db_session: AsyncSession) -> None:
    """Test get_by_project returns all items when no status filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items with different statuses
    await item_repo.create(
        project_id=str(project.id),
        title="Todo Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Done Item",
        view="FEATURE",
        item_type="feature",
        status="done",
    )
    await db_session.commit()

    # Get all items
    all_items = await item_repo.get_by_project(project.id)
    assert len(all_items) == COUNT_TWO
    statuses = {item.status for item in all_items}
    assert "todo" in statuses
    assert "done" in statuses


# ============================================================================
# GET_BY_VIEW - Status Filtering & Pagination
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_view_with_status_filter(db_session: AsyncSession) -> None:
    """Test get_by_view filters by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items in same view with different statuses
    await item_repo.create(
        project_id=str(project.id),
        title="Todo Feature",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Done Feature",
        view="FEATURE",
        item_type="feature",
        status="done",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="In Progress Feature",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
    )
    await db_session.commit()

    # Get only todo items in FEATURE view
    todo_features = await item_repo.get_by_view(project.id, "FEATURE", status="todo")
    assert len(todo_features) == 1
    assert todo_features[0].status == "todo"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_view_with_pagination(db_session: AsyncSession) -> None:
    """Test get_by_view supports pagination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create 5 items in same view
    for i in range(5):
        await item_repo.create(project_id=str(project.id), title=f"Feature {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Get first page
    page1 = await item_repo.get_by_view(project.id, "FEATURE", limit=2, offset=0)
    assert len(page1) == COUNT_TWO

    # Get second page
    page2 = await item_repo.get_by_view(project.id, "FEATURE", limit=2, offset=2)
    assert len(page2) == COUNT_TWO

    # Verify no overlap
    page1_ids = {item.id for item in page1}
    page2_ids = {item.id for item in page2}
    assert page1_ids.isdisjoint(page2_ids)


# ============================================================================
# QUERY - Dynamic Filtering
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_with_single_filter(db_session: AsyncSession) -> None:
    """Test query with single filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items
    await item_repo.create(
        project_id=str(project.id),
        title="High Priority",
        view="FEATURE",
        item_type="feature",
        priority="high",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Low Priority",
        view="FEATURE",
        item_type="feature",
        priority="low",
    )
    await db_session.commit()

    # Query by priority
    high_priority = await item_repo.query(project_id=str(project.id), filters={"priority": "high"})
    assert len(high_priority) == 1
    assert high_priority[0].priority == "high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_with_multiple_filters(db_session: AsyncSession) -> None:
    """Test query with multiple filters."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items
    await item_repo.create(
        project_id=str(project.id),
        title="High Todo",
        view="FEATURE",
        item_type="feature",
        priority="high",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="High Done",
        view="FEATURE",
        item_type="feature",
        priority="high",
        status="done",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Low Todo",
        view="FEATURE",
        item_type="feature",
        priority="low",
        status="todo",
    )
    await db_session.commit()

    # Query with multiple filters
    results = await item_repo.query(project_id=str(project.id), filters={"priority": "high", "status": "todo"})
    assert len(results) == 1
    assert results[0].priority == "high"
    assert results[0].status == "todo"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_with_limit(db_session: AsyncSession) -> None:
    """Test query respects limit."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create 5 items
    for i in range(5):
        await item_repo.create(project_id=str(project.id), title=f"Item {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Query with limit
    results = await item_repo.query(project_id=str(project.id), filters={}, limit=3)
    assert len(results) <= COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_with_invalid_filter_attribute_ignored(db_session: AsyncSession) -> None:
    """Test query ignores filters for non-existent attributes."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    _item = await item_repo.create(project_id=str(project.id), title="Test Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Query with invalid filter (should be ignored)
    results = await item_repo.query(project_id=str(project.id), filters={"nonexistent_field": "value"})
    # Should return all items since invalid filter is ignored
    assert len(results) >= 1


# ============================================================================
# TREE OPERATIONS - Get Children
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_children_returns_direct_children(db_session: AsyncSession) -> None:
    """Test get_children returns only direct children."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(project_id=str(project.id), title="Parent", view="EPIC", item_type="epic")
    await db_session.commit()

    # Create direct children
    child1 = await item_repo.create(
        project_id=str(project.id),
        title="Child 1",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    child2 = await item_repo.create(
        project_id=str(project.id),
        title="Child 2",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    await db_session.commit()

    # Create grandchild (should not be returned)
    grandchild = await item_repo.create(
        project_id=str(project.id),
        title="Grandchild",
        view="TASK",
        item_type="task",
        parent_id=str(child1.id),
    )
    await db_session.commit()

    # Get children
    children = await item_repo.get_children(str(parent.id))
    assert len(children) == COUNT_TWO
    child_ids = {child.id for child in children}
    assert child1.id in child_ids
    assert child2.id in child_ids
    assert grandchild.id not in child_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_children_excludes_deleted(db_session: AsyncSession) -> None:
    """Test get_children excludes deleted children."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(project_id=str(project.id), title="Parent", view="EPIC", item_type="epic")
    await db_session.commit()

    # Create children
    child1 = await item_repo.create(
        project_id=str(project.id),
        title="Active Child",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    child2 = await item_repo.create(
        project_id=str(project.id),
        title="Deleted Child",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    await db_session.commit()

    # Delete child2
    await item_repo.delete(str(child2.id), soft=True)
    await db_session.commit()

    # Get children (should exclude deleted)
    children = await item_repo.get_children(str(parent.id))
    assert len(children) == 1
    assert children[0].id == child1.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_children_empty_when_no_children(db_session: AsyncSession) -> None:
    """Test get_children returns empty list when item has no children."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item = await item_repo.create(
        project_id=str(project.id),
        title="Item Without Children",
        view="FEATURE",
        item_type="feature",
    )
    await db_session.commit()

    children = await item_repo.get_children(str(item.id))
    assert len(children) == 0


# ============================================================================
# TREE OPERATIONS - Get Ancestors
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ancestors_returns_all_parents(db_session: AsyncSession) -> None:
    """Test get_ancestors returns all ancestors up to root."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create hierarchy: root -> parent -> child
    root = await item_repo.create(project_id=str(project.id), title="Root", view="EPIC", item_type="epic")
    await db_session.commit()

    parent = await item_repo.create(
        project_id=str(project.id),
        title="Parent",
        view="STORY",
        item_type="story",
        parent_id=str(root.id),
    )
    await db_session.commit()

    child = await item_repo.create(
        project_id=str(project.id),
        title="Child",
        view="TASK",
        item_type="task",
        parent_id=str(parent.id),
    )
    await db_session.commit()

    # Get ancestors of child
    ancestors = await item_repo.get_ancestors(str(child.id))
    assert len(ancestors) == COUNT_TWO
    ancestor_ids = {ancestor.id for ancestor in ancestors}
    assert root.id in ancestor_ids
    assert parent.id in ancestor_ids
    assert child.id not in ancestor_ids  # Should exclude self


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ancestors_handles_deep_hierarchy(db_session: AsyncSession) -> None:
    """Test get_ancestors handles deep hierarchies."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create deep hierarchy: level1 -> level2 -> level3 -> level4
    level1 = await item_repo.create(project_id=str(project.id), title="Level 1", view="EPIC", item_type="epic")
    await db_session.commit()

    level2 = await item_repo.create(
        project_id=str(project.id),
        title="Level 2",
        view="STORY",
        item_type="story",
        parent_id=str(level1.id),
    )
    await db_session.commit()

    level3 = await item_repo.create(
        project_id=str(project.id),
        title="Level 3",
        view="TASK",
        item_type="task",
        parent_id=str(level2.id),
    )
    await db_session.commit()

    level4 = await item_repo.create(
        project_id=str(project.id),
        title="Level 4",
        view="TASK",
        item_type="task",
        parent_id=str(level3.id),
    )
    await db_session.commit()

    # Get ancestors of level4
    ancestors = await item_repo.get_ancestors(str(level4.id))
    assert len(ancestors) == COUNT_THREE
    ancestor_ids = {ancestor.id for ancestor in ancestors}
    assert level1.id in ancestor_ids
    assert level2.id in ancestor_ids
    assert level3.id in ancestor_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ancestors_empty_for_root_item(db_session: AsyncSession) -> None:
    """Test get_ancestors returns empty list for root item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    root = await item_repo.create(project_id=str(project.id), title="Root", view="EPIC", item_type="epic")
    await db_session.commit()

    ancestors = await item_repo.get_ancestors(str(root.id))
    assert len(ancestors) == 0


# ============================================================================
# TREE OPERATIONS - Get Descendants
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_descendants_returns_all_children(db_session: AsyncSession) -> None:
    """Test get_descendants returns all descendants."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create hierarchy: parent -> child1, child2 -> grandchild
    parent = await item_repo.create(project_id=str(project.id), title="Parent", view="EPIC", item_type="epic")
    await db_session.commit()

    child1 = await item_repo.create(
        project_id=str(project.id),
        title="Child 1",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    child2 = await item_repo.create(
        project_id=str(project.id),
        title="Child 2",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    await db_session.commit()

    grandchild = await item_repo.create(
        project_id=str(project.id),
        title="Grandchild",
        view="TASK",
        item_type="task",
        parent_id=str(child1.id),
    )
    await db_session.commit()

    # Get descendants of parent
    descendants = await item_repo.get_descendants(str(parent.id))
    assert len(descendants) == COUNT_THREE
    descendant_ids = {descendant.id for descendant in descendants}
    assert child1.id in descendant_ids
    assert child2.id in descendant_ids
    assert grandchild.id in descendant_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_descendants_handles_deep_hierarchy(db_session: AsyncSession) -> None:
    """Test get_descendants handles deep hierarchies."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create deep hierarchy
    root = await item_repo.create(project_id=str(project.id), title="Root", view="EPIC", item_type="epic")
    await db_session.commit()

    level2 = await item_repo.create(
        project_id=str(project.id),
        title="Level 2",
        view="STORY",
        item_type="story",
        parent_id=str(root.id),
    )
    await db_session.commit()

    level3 = await item_repo.create(
        project_id=str(project.id),
        title="Level 3",
        view="TASK",
        item_type="task",
        parent_id=str(level2.id),
    )
    await db_session.commit()

    level4 = await item_repo.create(
        project_id=str(project.id),
        title="Level 4",
        view="TASK",
        item_type="task",
        parent_id=str(level3.id),
    )
    await db_session.commit()

    # Get descendants of root
    descendants = await item_repo.get_descendants(str(root.id))
    assert len(descendants) == COUNT_THREE
    descendant_ids = {descendant.id for descendant in descendants}
    assert level2.id in descendant_ids
    assert level3.id in descendant_ids
    assert level4.id in descendant_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_descendants_empty_for_leaf_item(db_session: AsyncSession) -> None:
    """Test get_descendants returns empty list for leaf item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    leaf = await item_repo.create(project_id=str(project.id), title="Leaf", view="TASK", item_type="task")
    await db_session.commit()

    descendants = await item_repo.get_descendants(str(leaf.id))
    assert len(descendants) == 0


# ============================================================================
# COUNT_BY_STATUS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status_counts_correctly(db_session: AsyncSession) -> None:
    """Test count_by_status returns correct counts."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items with different statuses
    for i in range(3):
        await item_repo.create(
            project_id=str(project.id),
            title=f"Todo {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

    for i in range(2):
        await item_repo.create(
            project_id=str(project.id),
            title=f"Done {i}",
            view="FEATURE",
            item_type="feature",
            status="done",
        )

    await item_repo.create(
        project_id=str(project.id),
        title="In Progress",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
    )
    await db_session.commit()

    # Count by status
    counts = await item_repo.count_by_status(str(project.id))
    assert counts.get("todo") == COUNT_THREE
    assert counts.get("done") == COUNT_TWO
    assert counts.get("in_progress") == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status_excludes_deleted(db_session: AsyncSession) -> None:
    """Test count_by_status excludes deleted items."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items
    _item1 = await item_repo.create(
        project_id=str(project.id),
        title="Todo Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    item2 = await item_repo.create(
        project_id=str(project.id),
        title="Done Item",
        view="FEATURE",
        item_type="feature",
        status="done",
    )
    await db_session.commit()

    # Delete one item
    await item_repo.delete(str(item2.id), soft=True)
    await db_session.commit()

    # Count should exclude deleted
    counts = await item_repo.count_by_status(str(project.id))
    assert counts.get("todo") == 1
    assert counts.get("done", 0) == 0  # Deleted item not counted (use .get with default)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status_empty_project_returns_empty_dict(db_session: AsyncSession) -> None:
    """Test count_by_status returns empty dict for project with no items."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    counts = await item_repo.count_by_status(str(project.id))
    assert counts == {}
