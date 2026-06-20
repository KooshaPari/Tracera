"""Integration tests for Repository layer.

These tests use real AsyncSession with SQLite to test actual database operations,
transactions, complex queries, and data integrity.

Target Coverage: 80%+ for all repository modules
- item_repository.py: 14.62% -> 80%+
- link_repository.py: 41.18% -> 80%+
- project_repository.py: 25.58% -> 80%+
- agent_repository.py: 27.08% -> 80%+
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

# ============================================================================
# PROJECT REPOSITORY INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_project_repository_create_and_query(db_session: AsyncSession) -> None:
    """GIVEN: A ProjectRepository instance.

    WHEN: Creating a new project
    THEN: The project is persisted and can be queried by ID.
    """
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name="Integration Test Project",
        description="Test description",
        metadata={"env": "test"},
    )

    assert project.id is not None
    assert project.name == "Integration Test Project"
    assert project.description == "Test description"
    assert project.project_metadata == {"env": "test"}

    await db_session.commit()

    # Query back
    found = await repo.get_by_id(str(project.id))
    assert found is not None
    assert found.id == project.id
    assert found.name == "Integration Test Project"


@pytest.mark.asyncio
async def test_project_repository_get_by_name(db_session: AsyncSession) -> None:
    """GIVEN: A project exists in the database.

    WHEN: Querying by name
    THEN: The project is found correctly.
    """
    repo = ProjectRepository(db_session)

    project = await repo.create(name="Unique Project Name")
    await db_session.commit()

    found = await repo.get_by_name("Unique Project Name")
    assert found is not None
    assert found.id == project.id

    not_found = await repo.get_by_name("Non-Existent Project")
    assert not_found is None


@pytest.mark.asyncio
async def test_project_repository_get_all(db_session: AsyncSession) -> None:
    """GIVEN: Multiple projects in database.

    WHEN: Calling get_all
    THEN: All projects are returned.
    """
    repo = ProjectRepository(db_session)

    await repo.create(name="Project A")
    await repo.create(name="Project B")
    await repo.create(name="Project C")
    await db_session.commit()

    all_projects = await repo.get_all()
    assert len(all_projects) >= COUNT_THREE
    project_names = {p.name for p in all_projects}
    assert "Project A" in project_names
    assert "Project B" in project_names
    assert "Project C" in project_names


@pytest.mark.asyncio
async def test_project_repository_update(db_session: AsyncSession) -> None:
    """GIVEN: An existing project.

    WHEN: Updating project fields
    THEN: Changes are persisted correctly.
    """
    repo = ProjectRepository(db_session)

    project = await repo.create(name="Original Name", description="Original description", metadata={"version": "1.0"})
    await db_session.commit()

    # Update name
    updated = await repo.update(str(project.id), name="Updated Name")
    assert updated.name == "Updated Name"
    assert updated.description == "Original description"

    # Update description
    updated = await repo.update(str(project.id), description="Updated description")
    assert updated.description == "Updated description"

    # Update metadata
    updated = await repo.update(str(project.id), metadata={"version": "2.0", "env": "prod"})
    assert updated.project_metadata == {"version": "2.0", "env": "prod"}

    await db_session.commit()


@pytest.mark.asyncio
async def test_project_repository_update_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: A non-existent project ID.

    WHEN: Attempting to update
    THEN: None is returned.
    """
    repo = ProjectRepository(db_session)

    result = await repo.update("nonexistent-id", name="New Name")
    assert result is None


@pytest.mark.asyncio
async def test_project_repository_update_all_fields(db_session: AsyncSession) -> None:
    """GIVEN: An existing project.

    WHEN: Updating all fields at once
    THEN: All changes are persisted.
    """
    repo = ProjectRepository(db_session)

    project = await repo.create(name="Test Project")
    await db_session.commit()

    updated = await repo.update(
        project.id,
        name="Updated Name",
        description="Updated Description",
        metadata={"key": "value"},
    )

    assert updated.name == "Updated Name"
    assert updated.description == "Updated Description"
    assert updated.project_metadata == {"key": "value"}

    await db_session.commit()


# ============================================================================
# ITEM REPOSITORY INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_item_repository_create_basic(db_session: AsyncSession) -> None:
    """GIVEN: A project exists.

    WHEN: Creating an item
    THEN: Item is created with all fields set correctly.
    """
    # Create project first
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    # Create item
    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=str(project.id),
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        description="Test description",
        status="todo",
        priority="high",
        owner="test_user",
        metadata={"key": "value"},
    )

    assert item.id is not None
    assert item.project_id == project.id
    assert item.title == "Test Item"
    assert item.view == "FEATURE"
    assert item.item_type == "feature"
    assert item.description == "Test description"
    assert item.status == "todo"
    assert item.priority == "high"
    assert item.owner == "test_user"
    assert item.item_metadata == {"key": "value"}
    assert item.version == 1

    await db_session.commit()


@pytest.mark.asyncio
async def test_item_repository_create_with_parent(db_session: AsyncSession) -> None:
    """GIVEN: A parent item exists.

    WHEN: Creating a child item with parent_id
    THEN: Parent-child relationship is established.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(project_id=str(project.id), title="Parent Item", view="EPIC", item_type="epic")
    await db_session.commit()

    # Create child
    child = await item_repo.create(
        project_id=str(project.id),
        title="Child Item",
        view="STORY",
        item_type="story",
        parent_id=str(parent.id),
    )
    await db_session.commit()

    assert child.parent_id == parent.id


@pytest.mark.asyncio
async def test_item_repository_create_invalid_parent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent parent ID.

    WHEN: Creating item with invalid parent_id
    THEN: ValueError is raised.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError, match="Parent item .* not found"):
        await item_repo.create(
            project_id=str(project.id),
            title="Orphan Item",
            view="STORY",
            item_type="story",
            parent_id="nonexistent-parent",
        )


@pytest.mark.asyncio
async def test_item_repository_create_parent_different_project(db_session: AsyncSession) -> None:
    """GIVEN: Parent item in different project.

    WHEN: Creating child with parent from different project
    THEN: ValueError is raised.
    """
    proj_repo = ProjectRepository(db_session)
    project1 = await proj_repo.create(name="Project 1")
    project2 = await proj_repo.create(name="Project 2")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create parent in project1
    parent = await item_repo.create(project_id=str(project1.id), title="Parent", view="EPIC", item_type="epic")
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


@pytest.mark.asyncio
async def test_item_repository_get_by_id(db_session: AsyncSession) -> None:
    """GIVEN: Items exist in database.

    WHEN: Querying by ID
    THEN: Correct item is returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Test Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    found = await item_repo.get_by_id(str(item.id))
    assert found is not None
    assert found.id == item.id
    assert found.title == "Test Item"

    not_found = await item_repo.get_by_id("nonexistent-id")
    assert not_found is None


@pytest.mark.asyncio
async def test_item_repository_get_by_id_with_project_scope(db_session: AsyncSession) -> None:
    """GIVEN: Items in different projects.

    WHEN: Querying by ID with project_id filter
    THEN: Only item in correct project is returned.
    """
    proj_repo = ProjectRepository(db_session)
    project1 = await proj_repo.create(name="Project 1")
    project2 = await proj_repo.create(name="Project 2")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project1.id), title="Item 1", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Query with correct project
    found = await item_repo.get_by_id(str(item1.id), project_id=str(project1.id))
    assert found is not None

    # Query with wrong project
    not_found = await item_repo.get_by_id(str(item1.id), project_id=str(project2.id))
    assert not_found is None


@pytest.mark.asyncio
async def test_item_repository_get_by_id_excludes_deleted(db_session: AsyncSession) -> None:
    """GIVEN: A soft-deleted item.

    WHEN: Querying by ID
    THEN: Deleted item is not returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=str(project.id),
        title="To Be Deleted",
        view="FEATURE",
        item_type="feature",
    )
    await db_session.commit()

    # Soft delete
    await item_repo.delete(str(item.id), soft=True)
    await db_session.commit()

    # Should not be found
    found = await item_repo.get_by_id(str(item.id))
    assert found is None


@pytest.mark.asyncio
async def test_item_repository_list_by_view(db_session: AsyncSession) -> None:
    """GIVEN: Multiple items in different views.

    WHEN: Listing items by view
    THEN: Only items in specified view are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create items in different views
    await item_repo.create(project_id=str(project.id), title="Feature 1", view="FEATURE", item_type="feature")
    await item_repo.create(project_id=str(project.id), title="Feature 2", view="FEATURE", item_type="feature")
    await item_repo.create(project_id=str(project.id), title="Story 1", view="STORY", item_type="story")
    await db_session.commit()

    features = await item_repo.list_by_view(str(project.id), "FEATURE")
    assert len(features) == COUNT_TWO
    assert all(item.view == "FEATURE" for item in features)

    stories = await item_repo.list_by_view(str(project.id), "STORY")
    assert len(stories) == 1
    assert stories[0].view == "STORY"


@pytest.mark.asyncio
async def test_item_repository_list_by_view_include_deleted(db_session: AsyncSession) -> None:
    """GIVEN: Deleted and active items in a view.

    WHEN: Listing with include_deleted=True
    THEN: Deleted items are included.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=str(project.id), title="Active", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Deleted", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Delete item2
    await item_repo.delete(str(item2.id), soft=True)
    await db_session.commit()

    # Without deleted
    active_only = await item_repo.list_by_view(str(project.id), "FEATURE", include_deleted=False)
    assert len(active_only) == 1
    assert active_only[0].id == item1.id

    # With deleted
    all_items = await item_repo.list_by_view(str(project.id), "FEATURE", include_deleted=True)
    assert len(all_items) == COUNT_TWO


@pytest.mark.asyncio
async def test_item_repository_list_all(db_session: AsyncSession) -> None:
    """GIVEN: Items in various views and states.

    WHEN: Listing all items in project
    THEN: All non-deleted items are returned in order.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create multiple items
    for i in range(5):
        await item_repo.create(project_id=str(project.id), title=f"Item {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    all_items = await item_repo.list_all(str(project.id))
    assert len(all_items) == COUNT_FIVE

    # Should be ordered by created_at desc
    # (most recent first due to order_by in list_all)


@pytest.mark.asyncio
async def test_item_repository_update_basic(db_session: AsyncSession) -> None:
    """GIVEN: An existing item.

    WHEN: Updating fields with correct version
    THEN: Item is updated and version increments.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=str(project.id),
        title="Original Title",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await db_session.commit()

    assert item.version == 1

    updated = await item_repo.update(str(item.id), expected_version=1, title="Updated Title", status="in_progress")

    assert updated.title == "Updated Title"
    assert updated.status == "in_progress"
    assert updated.version == COUNT_TWO

    await db_session.commit()


@pytest.mark.asyncio
async def test_item_repository_update_concurrency_error(db_session: AsyncSession) -> None:
    """GIVEN: An item with version 2.

    WHEN: Updating with expected_version=1
    THEN: ConcurrencyError is raised.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Test", view="FEATURE", item_type="feature")
    await db_session.commit()

    # First update
    await item_repo.update(str(item.id), expected_version=1, status="in_progress")
    await db_session.commit()

    # Second update with stale version
    with pytest.raises(ConcurrencyError, match="was modified by another agent"):
        await item_repo.update(str(item.id), expected_version=1, title="Conflict")


@pytest.mark.asyncio
async def test_item_repository_update_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent item ID.

    WHEN: Attempting to update
    THEN: ValueError is raised.
    """
    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError, match="Item .* not found"):
        await item_repo.update("nonexistent-id", expected_version=1, title="Won't Work")


@pytest.mark.asyncio
async def test_item_repository_soft_delete(db_session: AsyncSession) -> None:
    """GIVEN: An active item.

    WHEN: Soft deleting the item
    THEN: deleted_at is set and item is not found in queries.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="To Delete", view="FEATURE", item_type="feature")
    await db_session.commit()

    result = await item_repo.delete(str(item.id), soft=True)
    assert result is True
    await db_session.commit()

    # Should not be found
    found = await item_repo.get_by_id(str(item.id))
    assert found is None


@pytest.mark.asyncio
async def test_item_repository_soft_delete_cascade_children(db_session: AsyncSession) -> None:
    """GIVEN: Parent item with children.

    WHEN: Soft deleting parent
    THEN: Children are also soft-deleted.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    parent = await item_repo.create(project_id=str(project.id), title="Parent", view="EPIC", item_type="epic")
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

    # Delete parent
    await item_repo.delete(str(parent.id), soft=True)
    await db_session.commit()

    # Children should also be deleted
    assert await item_repo.get_by_id(str(child1.id)) is None
    assert await item_repo.get_by_id(str(child2.id)) is None


@pytest.mark.asyncio
async def test_item_repository_hard_delete(db_session: AsyncSession) -> None:
    """GIVEN: An active item.

    WHEN: Hard deleting the item
    THEN: Item is permanently removed from database.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="To Delete", view="FEATURE", item_type="feature")
    item_id = item.id
    await db_session.commit()

    result = await item_repo.delete(str(item_id), soft=False)
    assert result is True
    await db_session.commit()

    # Should not exist at all
    found = await item_repo.get_by_id(str(item_id))
    assert found is None


@pytest.mark.asyncio
async def test_item_repository_delete_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent item ID.

    WHEN: Attempting to delete
    THEN: False is returned.
    """
    item_repo = ItemRepository(db_session)

    result = await item_repo.delete("nonexistent-id", soft=True)
    assert result is False


@pytest.mark.asyncio
async def test_item_repository_restore(db_session: AsyncSession) -> None:
    """GIVEN: A soft-deleted item.

    WHEN: Restoring the item
    THEN: Item is accessible again.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="To Restore", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Delete
    await item_repo.delete(str(item.id), soft=True)
    await db_session.commit()

    # Restore
    restored = await item_repo.restore(str(item.id))
    assert restored is not None
    assert restored.id == item.id
    assert restored.deleted_at is None
    await db_session.commit()

    # Should be findable again
    found = await item_repo.get_by_id(str(item.id))
    assert found is not None


@pytest.mark.asyncio
async def test_item_repository_restore_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent item ID.

    WHEN: Attempting to restore
    THEN: None is returned.
    """
    item_repo = ItemRepository(db_session)

    result = await item_repo.restore("nonexistent-id")
    assert result is None


@pytest.mark.asyncio
async def test_item_repository_restore_non_deleted(db_session: AsyncSession) -> None:
    """GIVEN: An active (non-deleted) item.

    WHEN: Attempting to restore
    THEN: None is returned (item is not deleted).
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Active Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    result = await item_repo.restore(str(item.id))
    assert result is None  # Not deleted, so restore returns None


@pytest.mark.asyncio
async def test_item_repository_get_by_project(db_session: AsyncSession) -> None:
    """GIVEN: Items in different projects.

    WHEN: Querying by project_id
    THEN: Only items from that project are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project1 = await proj_repo.create(name="Project 1")
    project2 = await proj_repo.create(name="Project 2")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    for i in range(3):
        await item_repo.create(project_id=str(project1.id), title=f"P1 Item {i}", view="FEATURE", item_type="feature")
    for i in range(2):
        await item_repo.create(project_id=str(project2.id), title=f"P2 Item {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    p1_items = await item_repo.get_by_project(str(project1.id))
    assert len(p1_items) == COUNT_THREE

    p2_items = await item_repo.get_by_project(str(project2.id))
    assert len(p2_items) == COUNT_TWO


@pytest.mark.asyncio
async def test_item_repository_get_by_project_with_status(db_session: AsyncSession) -> None:
    """GIVEN: Items with different statuses.

    WHEN: Querying by project and status
    THEN: Only items with matching status are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    await item_repo.create(
        project_id=str(project.id),
        title="Todo 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Todo 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Done 1",
        view="FEATURE",
        item_type="feature",
        status="done",
    )
    await db_session.commit()

    todo_items = await item_repo.get_by_project(str(project.id), status="todo")
    assert len(todo_items) == COUNT_TWO
    assert all(item.status == "todo" for item in todo_items)

    done_items = await item_repo.get_by_project(str(project.id), status="done")
    assert len(done_items) == 1


@pytest.mark.asyncio
async def test_item_repository_get_by_project_pagination(db_session: AsyncSession) -> None:
    """GIVEN: Many items in project.

    WHEN: Using limit and offset
    THEN: Correct page of results is returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    for i in range(15):
        await item_repo.create(project_id=str(project.id), title=f"Item {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    # First page
    page1 = await item_repo.get_by_project(str(project.id), limit=5, offset=0)
    assert len(page1) == COUNT_FIVE

    # Second page
    page2 = await item_repo.get_by_project(str(project.id), limit=5, offset=5)
    assert len(page2) == COUNT_FIVE

    # Third page
    page3 = await item_repo.get_by_project(str(project.id), limit=5, offset=10)
    assert len(page3) == COUNT_FIVE


@pytest.mark.asyncio
async def test_item_repository_get_by_view_with_status(db_session: AsyncSession) -> None:
    """GIVEN: Items in same view with different statuses.

    WHEN: Querying by view and status
    THEN: Only matching items are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    await item_repo.create(
        project_id=str(project.id),
        title="Feature Todo",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Feature Done",
        view="FEATURE",
        item_type="feature",
        status="done",
    )
    await db_session.commit()

    result = await item_repo.get_by_view(str(project.id), "FEATURE", status="todo")
    assert len(result) == 1
    assert result[0].title == "Feature Todo"


@pytest.mark.asyncio
async def test_item_repository_get_by_view_pagination(db_session: AsyncSession) -> None:
    """GIVEN: Many items in view.

    WHEN: Using limit and offset
    THEN: Pagination works correctly.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    for i in range(10):
        await item_repo.create(project_id=str(project.id), title=f"Feature {i}", view="FEATURE", item_type="feature")
    await db_session.commit()

    page1 = await item_repo.get_by_view(str(project.id), "FEATURE", limit=3, offset=0)
    assert len(page1) == COUNT_THREE

    page2 = await item_repo.get_by_view(str(project.id), "FEATURE", limit=3, offset=3)
    assert len(page2) == COUNT_THREE


@pytest.mark.asyncio
async def test_item_repository_query_dynamic_filters(db_session: AsyncSession) -> None:
    """GIVEN: Items with various attributes.

    WHEN: Using dynamic filters via query method
    THEN: Only matching items are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    await item_repo.create(
        project_id=str(project.id),
        title="High Priority Feature",
        view="FEATURE",
        item_type="feature",
        priority="high",
        owner="alice",
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Low Priority Feature",
        view="FEATURE",
        item_type="feature",
        priority="low",
        owner="bob",
    )
    await db_session.commit()

    # Filter by priority
    high_priority = await item_repo.query(str(project.id), filters={"priority": "high"})
    assert len(high_priority) == 1
    assert high_priority[0].priority == "high"

    # Filter by owner
    alice_items = await item_repo.query(str(project.id), filters={"owner": "alice"})
    assert len(alice_items) == 1
    assert alice_items[0].owner == "alice"

    # Multiple filters
    specific = await item_repo.query(str(project.id), filters={"priority": "high", "owner": "alice"})
    assert len(specific) == 1


@pytest.mark.asyncio
async def test_item_repository_get_children(db_session: AsyncSession) -> None:
    """GIVEN: Parent item with multiple children.

    WHEN: Getting children
    THEN: All direct children are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    parent = await item_repo.create(project_id=str(project.id), title="Parent", view="EPIC", item_type="epic")
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
    # Grandchild - should not be in children
    await item_repo.create(
        project_id=str(project.id),
        title="Grandchild",
        view="TASK",
        item_type="task",
        parent_id=str(child1.id),
    )
    await db_session.commit()

    children = await item_repo.get_children(str(parent.id))
    assert len(children) == COUNT_TWO
    child_ids = {c.id for c in children}
    assert child1.id in child_ids
    assert child2.id in child_ids


@pytest.mark.asyncio
async def test_item_repository_get_ancestors(db_session: AsyncSession) -> None:
    """GIVEN: Multi-level item hierarchy.

    WHEN: Getting ancestors of deep item
    THEN: All ancestors up to root are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create hierarchy: root -> parent -> child -> grandchild
    root = await item_repo.create(project_id=str(project.id), title="Root", view="EPIC", item_type="epic")
    parent = await item_repo.create(
        project_id=str(project.id),
        title="Parent",
        view="STORY",
        item_type="story",
        parent_id=str(root.id),
    )
    child = await item_repo.create(
        project_id=str(project.id),
        title="Child",
        view="TASK",
        item_type="task",
        parent_id=str(parent.id),
    )
    grandchild = await item_repo.create(
        project_id=str(project.id),
        title="Grandchild",
        view="SUBTASK",
        item_type="subtask",
        parent_id=str(child.id),
    )
    await db_session.commit()

    # Get ancestors of grandchild
    ancestors = await item_repo.get_ancestors(str(grandchild.id))
    assert len(ancestors) == COUNT_THREE

    # Should be ordered root first
    ancestor_titles = [a.title for a in ancestors]
    assert "Root" in ancestor_titles
    assert "Parent" in ancestor_titles
    assert "Child" in ancestor_titles


@pytest.mark.asyncio
async def test_item_repository_get_descendants(db_session: AsyncSession) -> None:
    """GIVEN: Multi-level item hierarchy.

    WHEN: Getting descendants of root
    THEN: All descendants are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create hierarchy
    root = await item_repo.create(project_id=str(project.id), title="Root", view="EPIC", item_type="epic")
    child1 = await item_repo.create(
        project_id=str(project.id),
        title="Child 1",
        view="STORY",
        item_type="story",
        parent_id=str(root.id),
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Child 2",
        view="STORY",
        item_type="story",
        parent_id=str(root.id),
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Grandchild",
        view="TASK",
        item_type="task",
        parent_id=str(child1.id),
    )
    await db_session.commit()

    descendants = await item_repo.get_descendants(str(root.id))
    assert len(descendants) == COUNT_THREE

    descendant_titles = {d.title for d in descendants}
    assert "Child 1" in descendant_titles
    assert "Child 2" in descendant_titles
    assert "Grandchild" in descendant_titles


@pytest.mark.asyncio
async def test_item_repository_count_by_status(db_session: AsyncSession) -> None:
    """GIVEN: Items with various statuses.

    WHEN: Counting by status
    THEN: Correct counts are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
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
            title=f"In Progress {i}",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
        )
    await item_repo.create(project_id=str(project.id), title="Done", view="FEATURE", item_type="feature", status="done")
    await db_session.commit()

    counts = await item_repo.count_by_status(str(project.id))
    assert counts["todo"] == COUNT_THREE
    assert counts["in_progress"] == COUNT_TWO
    assert counts["done"] == 1


# ============================================================================
# LINK REPOSITORY INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_link_repository_create(db_session: AsyncSession) -> None:
    """GIVEN: Two items exist.

    WHEN: Creating a link between them
    THEN: Link is persisted with all fields.
    """
    # Setup
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project.id), title="Source Item", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Target Item", view="API", item_type="api")
    await db_session.commit()

    # Create link
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="implements",
        link_metadata={"confidence": 0.95},
    )

    assert link.id is not None
    assert link.project_id == project.id
    assert link.source_item_id == item1.id
    assert link.target_item_id == item2.id
    assert link.link_type == "implements"
    assert link.link_metadata == {"confidence": 0.95}

    await db_session.commit()


@pytest.mark.asyncio
async def test_link_repository_get_by_id(db_session: AsyncSession) -> None:
    """GIVEN: A link exists.

    WHEN: Querying by ID
    THEN: Correct link is returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Item 2", view="API", item_type="api")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="tests",
    )
    await db_session.commit()

    found = await link_repo.get_by_id(str(link.id))
    assert found is not None
    assert found.id == link.id
    assert found.link_type == "tests"

    not_found = await link_repo.get_by_id("nonexistent-id")
    assert not_found is None


@pytest.mark.asyncio
async def test_link_repository_get_by_project(db_session: AsyncSession) -> None:
    """GIVEN: Links in different projects.

    WHEN: Querying by project_id
    THEN: Only links from that project are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project1 = await proj_repo.create(name="Project 1")
    project2 = await proj_repo.create(name="Project 2")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    p1_item1 = await item_repo.create(
        project_id=str(project1.id),
        title="P1 Item 1",
        view="FEATURE",
        item_type="feature",
    )
    p1_item2 = await item_repo.create(project_id=str(project1.id), title="P1 Item 2", view="API", item_type="api")
    p2_item1 = await item_repo.create(
        project_id=str(project2.id),
        title="P2 Item 1",
        view="FEATURE",
        item_type="feature",
    )
    p2_item2 = await item_repo.create(project_id=str(project2.id), title="P2 Item 2", view="API", item_type="api")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project1.id),
        source_item_id=str(p1_item1.id),
        target_item_id=str(p1_item2.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project2.id),
        source_item_id=str(p2_item1.id),
        target_item_id=str(p2_item2.id),
        link_type="tests",
    )
    await db_session.commit()

    p1_links = await link_repo.get_by_project(str(project1.id))
    assert len(p1_links) == 1
    assert p1_links[0].project_id == project1.id

    p2_links = await link_repo.get_by_project(str(project2.id))
    assert len(p2_links) == 1
    assert p2_links[0].project_id == project2.id


@pytest.mark.asyncio
async def test_link_repository_get_by_source(db_session: AsyncSession) -> None:
    """GIVEN: Multiple links from same source.

    WHEN: Querying by source_item_id
    THEN: All outgoing links are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(project_id=str(project.id), title="Source", view="FEATURE", item_type="feature")
    target1 = await item_repo.create(project_id=str(project.id), title="Target 1", view="API", item_type="api")
    target2 = await item_repo.create(project_id=str(project.id), title="Target 2", view="TEST", item_type="test")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target1.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source.id),
        target_item_id=str(target2.id),
        link_type="depends_on",
    )
    await db_session.commit()

    links = await link_repo.get_by_source(str(source.id))
    assert len(links) == COUNT_TWO
    assert all(link.source_item_id == source.id for link in links)


@pytest.mark.asyncio
async def test_link_repository_get_by_target(db_session: AsyncSession) -> None:
    """GIVEN: Multiple links to same target.

    WHEN: Querying by target_item_id
    THEN: All incoming links are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    source1 = await item_repo.create(project_id=str(project.id), title="Source 1", view="FEATURE", item_type="feature")
    source2 = await item_repo.create(project_id=str(project.id), title="Source 2", view="STORY", item_type="story")
    target = await item_repo.create(project_id=str(project.id), title="Target", view="API", item_type="api")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source1.id),
        target_item_id=str(target.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(source2.id),
        target_item_id=str(target.id),
        link_type="implements",
    )
    await db_session.commit()

    links = await link_repo.get_by_target(str(target.id))
    assert len(links) == COUNT_TWO
    assert all(link.target_item_id == target.id for link in links)


@pytest.mark.asyncio
async def test_link_repository_get_by_item(db_session: AsyncSession) -> None:
    """GIVEN: Links where item is both source and target.

    WHEN: Querying by item_id
    THEN: All connected links are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Item 2", view="API", item_type="api")
    item3 = await item_repo.create(project_id=str(project.id), title="Item 3", view="TEST", item_type="test")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    # item2 as source
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item2.id),
        target_item_id=str(item3.id),
        link_type="tests",
    )
    # item2 as target
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="implements",
    )
    await db_session.commit()

    links = await link_repo.get_by_item(str(item2.id))
    assert len(links) == COUNT_TWO


@pytest.mark.asyncio
async def test_link_repository_delete(db_session: AsyncSession) -> None:
    """GIVEN: A link exists.

    WHEN: Deleting the link
    THEN: Link is removed from database.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Item 2", view="API", item_type="api")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="implements",
    )
    await db_session.commit()

    result = await link_repo.delete(str(link.id))
    assert result is True
    await db_session.commit()

    # Should not exist
    found = await link_repo.get_by_id(str(link.id))
    assert found is None


@pytest.mark.asyncio
async def test_link_repository_delete_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent link ID.

    WHEN: Attempting to delete
    THEN: False is returned.
    """
    link_repo = LinkRepository(db_session)

    result = await link_repo.delete("nonexistent-id")
    assert result is False


@pytest.mark.asyncio
async def test_link_repository_delete_by_item(db_session: AsyncSession) -> None:
    """GIVEN: Multiple links connected to an item.

    WHEN: Deleting by item_id
    THEN: All connected links are removed.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Item 2", view="API", item_type="api")
    item3 = await item_repo.create(project_id=str(project.id), title="Item 3", view="TEST", item_type="test")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item2.id),
        target_item_id=str(item3.id),
        link_type="tests",
    )
    await db_session.commit()

    # Delete all links for item2
    deleted_count = await link_repo.delete_by_item(str(item2.id))
    assert deleted_count == COUNT_TWO
    await db_session.commit()

    # Verify all links for item2 are gone
    remaining = await link_repo.get_by_item(str(item2.id))
    assert len(remaining) == 0


# ============================================================================
# AGENT REPOSITORY INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_agent_repository_create(db_session: AsyncSession) -> None:
    """GIVEN: A project exists.

    WHEN: Creating an agent
    THEN: Agent is persisted with all fields.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(
        project_id=str(project.id),
        name="Test Agent",
        agent_type="coordinator",
        metadata={"version": "1.0"},
    )

    assert agent.id is not None
    assert agent.project_id == project.id
    assert agent.name == "Test Agent"
    assert agent.agent_type == "coordinator"
    assert agent.status == "active"
    assert agent.agent_metadata == {"version": "1.0"}

    await db_session.commit()


@pytest.mark.asyncio
async def test_agent_repository_get_by_id(db_session: AsyncSession) -> None:
    """GIVEN: An agent exists.

    WHEN: Querying by ID
    THEN: Correct agent is returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="worker")
    await db_session.commit()

    found = await agent_repo.get_by_id(str(agent.id))
    assert found is not None
    assert found.id == agent.id
    assert found.name == "Test Agent"

    not_found = await agent_repo.get_by_id("nonexistent-id")
    assert not_found is None


@pytest.mark.asyncio
async def test_agent_repository_get_by_project(db_session: AsyncSession) -> None:
    """GIVEN: Agents in different projects.

    WHEN: Querying by project_id
    THEN: Only agents from that project are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project1 = await proj_repo.create(name="Project 1")
    project2 = await proj_repo.create(name="Project 2")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    await agent_repo.create(project_id=str(project1.id), name="Agent P1-1", agent_type="worker")
    await agent_repo.create(project_id=str(project1.id), name="Agent P1-2", agent_type="coordinator")
    await agent_repo.create(project_id=str(project2.id), name="Agent P2-1", agent_type="worker")
    await db_session.commit()

    p1_agents = await agent_repo.get_by_project(str(project1.id))
    assert len(p1_agents) == COUNT_TWO

    p2_agents = await agent_repo.get_by_project(str(project2.id))
    assert len(p2_agents) == 1


@pytest.mark.asyncio
async def test_agent_repository_get_by_project_with_status(db_session: AsyncSession) -> None:
    """GIVEN: Agents with different statuses.

    WHEN: Querying by project and status
    THEN: Only matching agents are returned.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent1 = await agent_repo.create(project_id=str(project.id), name="Active Agent", agent_type="worker")
    agent2 = await agent_repo.create(project_id=str(project.id), name="Inactive Agent", agent_type="worker")
    await db_session.commit()

    # Update status of agent2
    await agent_repo.update_status(str(agent2.id), "inactive")
    await db_session.commit()

    # Query active agents
    active_agents = await agent_repo.get_by_project(str(project.id), status="active")
    assert len(active_agents) == 1
    assert active_agents[0].id == agent1.id

    # Query inactive agents
    inactive_agents = await agent_repo.get_by_project(str(project.id), status="inactive")
    assert len(inactive_agents) == 1
    assert inactive_agents[0].id == agent2.id


@pytest.mark.asyncio
async def test_agent_repository_update_status(db_session: AsyncSession) -> None:
    """GIVEN: An active agent.

    WHEN: Updating status
    THEN: Status is changed correctly.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="worker")
    await db_session.commit()

    assert agent.status == "active"

    updated = await agent_repo.update_status(str(agent.id), "paused")
    assert updated.status == "paused"
    await db_session.commit()

    # Verify persisted
    found = await agent_repo.get_by_id(str(agent.id))
    assert found is not None and found.status == "paused"


@pytest.mark.asyncio
async def test_agent_repository_update_status_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent agent ID.

    WHEN: Attempting to update status
    THEN: ValueError is raised.
    """
    agent_repo = AgentRepository(db_session)

    with pytest.raises(ValueError, match="Agent .* not found"):
        await agent_repo.update_status("nonexistent-id", "inactive")


@pytest.mark.asyncio
async def test_agent_repository_update_activity(db_session: AsyncSession) -> None:
    """GIVEN: An agent exists.

    WHEN: Updating activity timestamp
    THEN: last_activity_at is updated.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="worker")
    await db_session.commit()

    assert agent.last_activity_at is None

    updated = await agent_repo.update_activity(str(agent.id))
    assert updated.last_activity_at is not None
    await db_session.commit()


@pytest.mark.asyncio
async def test_agent_repository_update_activity_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent agent ID.

    WHEN: Attempting to update activity
    THEN: ValueError is raised.
    """
    agent_repo = AgentRepository(db_session)

    with pytest.raises(ValueError, match="Agent .* not found"):
        await agent_repo.update_activity("nonexistent-id")


@pytest.mark.asyncio
async def test_agent_repository_delete(db_session: AsyncSession) -> None:
    """GIVEN: An agent exists.

    WHEN: Deleting the agent
    THEN: Agent is removed from database.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="worker")
    await db_session.commit()

    result = await agent_repo.delete(str(agent.id))
    assert result is True
    await db_session.commit()

    # Should not exist
    found = await agent_repo.get_by_id(str(agent.id))
    assert found is None


@pytest.mark.asyncio
async def test_agent_repository_delete_nonexistent(db_session: AsyncSession) -> None:
    """GIVEN: Non-existent agent ID.

    WHEN: Attempting to delete
    THEN: False is returned.
    """
    agent_repo = AgentRepository(db_session)

    result = await agent_repo.delete("nonexistent-id")
    assert result is False


# ============================================================================
# TRANSACTION AND ROLLBACK TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_transaction_rollback_item_creation(db_session: AsyncSession) -> None:
    """GIVEN: A transaction is started.

    WHEN: Creating items and rolling back
    THEN: No items are persisted.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create item
    item = await item_repo.create(
        project_id=str(project.id),
        title="Temporary Item",
        view="FEATURE",
        item_type="feature",
    )
    item_id = item.id

    # Rollback instead of commit
    await db_session.rollback()

    # Item should not exist
    found = await item_repo.get_by_id(str(item_id))
    assert found is None


@pytest.mark.asyncio
async def test_transaction_rollback_link_creation(db_session: AsyncSession) -> None:
    """GIVEN: Items exist.

    WHEN: Creating link and rolling back
    THEN: Link is not persisted.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=str(project.id), title="Item 2", view="API", item_type="api")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(item1.id),
        target_item_id=str(item2.id),
        link_type="implements",
    )
    link_id = link.id

    # Rollback
    await db_session.rollback()

    # Link should not exist
    found = await link_repo.get_by_id(str(link_id))
    assert found is None


@pytest.mark.asyncio
async def test_transaction_commit_persists_changes(db_session: AsyncSession) -> None:
    """GIVEN: Multiple repository operations.

    WHEN: Committing transaction
    THEN: All changes are persisted.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=str(project.id), title="Test Item", view="FEATURE", item_type="feature")

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="worker")

    # Commit all at once
    await db_session.commit()

    # All should exist
    assert await proj_repo.get_by_id(str(project.id)) is not None
    assert await item_repo.get_by_id(str(item.id)) is not None
    assert await agent_repo.get_by_id(str(agent.id)) is not None


# ============================================================================
# COMPLEX QUERY TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_complex_query_items_with_links(db_session: AsyncSession) -> None:
    """GIVEN: Items with various links.

    WHEN: Querying items and their links
    THEN: Complete graph can be traversed.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    feature = await item_repo.create(project_id=str(project.id), title="Feature", view="FEATURE", item_type="feature")
    api = await item_repo.create(project_id=str(project.id), title="API", view="API", item_type="api")
    test = await item_repo.create(project_id=str(project.id), title="Test", view="TEST", item_type="test")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(feature.id),
        target_item_id=str(api.id),
        link_type="implements",
    )
    await link_repo.create(
        project_id=str(project.id),
        source_item_id=str(test.id),
        target_item_id=str(api.id),
        link_type="tests",
    )
    await db_session.commit()

    # Traverse graph
    api_links = await link_repo.get_by_item(str(api.id))
    assert len(api_links) == COUNT_TWO

    # Get implementers
    implementers = await link_repo.get_by_target(str(api.id))
    implementer_types = {link.link_type for link in implementers}
    assert "implements" in implementer_types
    assert "tests" in implementer_types


@pytest.mark.asyncio
async def test_complex_hierarchy_operations(db_session: AsyncSession) -> None:
    """GIVEN: Multi-level item hierarchy.

    WHEN: Performing ancestor/descendant queries
    THEN: Hierarchy is correctly traversed.
    """
    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(name="Test Project")
    await db_session.commit()

    item_repo = ItemRepository(db_session)

    # Create 3-level hierarchy
    epic = await item_repo.create(project_id=str(project.id), title="Epic", view="EPIC", item_type="epic")
    story1 = await item_repo.create(
        project_id=str(project.id),
        title="Story 1",
        view="STORY",
        item_type="story",
        parent_id=str(epic.id),
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Story 2",
        view="STORY",
        item_type="story",
        parent_id=str(epic.id),
    )
    task1 = await item_repo.create(
        project_id=str(project.id),
        title="Task 1",
        view="TASK",
        item_type="task",
        parent_id=str(story1.id),
    )
    await item_repo.create(
        project_id=str(project.id),
        title="Task 2",
        view="TASK",
        item_type="task",
        parent_id=str(story1.id),
    )
    await db_session.commit()

    # Get children of epic
    epic_children = await item_repo.get_children(str(epic.id))
    assert len(epic_children) == COUNT_TWO

    # Get descendants of epic (should include stories and tasks)
    epic_descendants = await item_repo.get_descendants(str(epic.id))
    assert len(epic_descendants) == COUNT_FOUR  # 2 stories + 2 tasks

    # Get ancestors of task1
    task1_ancestors = await item_repo.get_ancestors(str(task1.id))
    assert len(task1_ancestors) == COUNT_TWO  # story1 + epic
