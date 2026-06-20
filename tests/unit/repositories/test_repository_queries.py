"""Unit tests for repository query methods."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

# Use link_test_setup fixture for link-related tests
pytestmark = pytest.mark.usefixtures("link_test_setup")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_query_with_filters(db_session: AsyncSession) -> None:
    """Test querying items with dynamic filters."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Query Filters Test Project")

    item_repo = ItemRepository(db_session)

    # Create items with different attributes
    await item_repo.create(
        project_id=project.id,
        title="Feature 1",
        view="FEATURE",
        item_type="feature",
        status="todo",
        priority="high",
    )
    await item_repo.create(
        project_id=project.id,
        title="Feature 2",
        view="FEATURE",
        item_type="feature",
        status="done",
        priority="low",
    )
    await item_repo.create(
        project_id=project.id,
        title="Bug 1",
        view="BUG",
        item_type="bug",
        status="todo",
        priority="high",
    )

    # Query by status
    todo_items = await item_repo.query(project.id, {"status": "todo"})
    assert len(todo_items) == COUNT_TWO
    assert all(item.status == "todo" for item in todo_items)

    # Query by view
    feature_items = await item_repo.query(project.id, {"view": "FEATURE"})
    assert len(feature_items) == COUNT_TWO
    assert all(item.view == "FEATURE" for item in feature_items)

    # Query by multiple filters
    high_todo = await item_repo.query(project.id, {"status": "todo", "priority": "high"})
    assert len(high_todo) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_get_by_view_with_pagination(db_session: AsyncSession) -> None:
    """Test getting items by view with limit and offset."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Pagination Test Project")

    item_repo = ItemRepository(db_session)

    # Create 15 items
    for i in range(15):
        await item_repo.create(
            project_id=project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
        )

    # Get first page (5 items)
    page1 = await item_repo.get_by_view(project.id, "FEATURE", limit=5, offset=0)
    assert len(page1) == COUNT_FIVE

    # Get second page
    page2 = await item_repo.get_by_view(project.id, "FEATURE", limit=5, offset=5)
    assert len(page2) == COUNT_FIVE

    # Ensure no overlap
    page1_ids = {item.id for item in page1}
    page2_ids = {item.id for item in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_count_by_status(db_session: AsyncSession) -> None:
    """Test counting items grouped by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Count Status Test Project")

    item_repo = ItemRepository(db_session)

    # Create items with different statuses
    for _ in range(3):
        await item_repo.create(
            project_id=project.id,
            title="Todo Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

    for _ in range(5):
        await item_repo.create(
            project_id=project.id,
            title="In Progress Item",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
        )

    for _ in range(2):
        await item_repo.create(
            project_id=project.id,
            title="Done Item",
            view="FEATURE",
            item_type="feature",
            status="done",
        )

    # Count by status
    counts = await item_repo.count_by_status(project.id)
    assert counts["todo"] == COUNT_THREE
    assert counts["in_progress"] == COUNT_FIVE
    assert counts["done"] == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_get_children(db_session: AsyncSession) -> None:
    """Test getting direct children of an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Children Test Project")

    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(
        project_id=project.id,
        title="Parent",
        view="FEATURE",
        item_type="epic",
    )

    # Create children
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

    # Get children
    children = await item_repo.get_children(parent.id)
    assert len(children) == COUNT_TWO
    child_ids = {c.id for c in children}
    assert child1.id in child_ids
    assert child2.id in child_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_get_descendants_recursive(db_session: AsyncSession) -> None:
    """Test getting all descendants recursively."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Descendants Test Project")

    item_repo = ItemRepository(db_session)

    # Create hierarchy: grandparent -> parent -> child
    grandparent = await item_repo.create(
        project_id=project.id,
        title="Grandparent",
        view="FEATURE",
        item_type="epic",
    )

    parent = await item_repo.create(
        project_id=project.id,
        title="Parent",
        view="FEATURE",
        item_type="feature",
        parent_id=grandparent.id,
    )

    child = await item_repo.create(
        project_id=project.id,
        title="Child",
        view="FEATURE",
        item_type="task",
        parent_id=parent.id,
    )

    # Get all descendants of grandparent
    descendants = await item_repo.get_descendants(grandparent.id)
    assert len(descendants) == COUNT_TWO

    descendant_ids = {d.id for d in descendants}
    assert parent.id in descendant_ids
    assert child.id in descendant_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_get_ancestors_recursive(db_session: AsyncSession) -> None:
    """Test getting all ancestors recursively."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Ancestors Test Project")

    item_repo = ItemRepository(db_session)

    # Create hierarchy: grandparent -> parent -> child
    grandparent = await item_repo.create(
        project_id=project.id,
        title="Grandparent",
        view="FEATURE",
        item_type="epic",
    )

    parent = await item_repo.create(
        project_id=project.id,
        title="Parent",
        view="FEATURE",
        item_type="feature",
        parent_id=grandparent.id,
    )

    child = await item_repo.create(
        project_id=project.id,
        title="Child",
        view="FEATURE",
        item_type="task",
        parent_id=parent.id,
    )

    # Get all ancestors of child
    ancestors = await item_repo.get_ancestors(child.id)
    assert len(ancestors) == COUNT_TWO

    ancestor_ids = {a.id for a in ancestors}
    assert parent.id in ancestor_ids
    assert grandparent.id in ancestor_ids

    # Root (grandparent) should be first
    assert ancestors[0].id == grandparent.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_link_get_by_source_and_target(db_session: AsyncSession) -> None:
    """Test getting links by source and target separately."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Link Source Target Test Project")

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

    link_repo = LinkRepository(db_session)

    # Create links: item1 -> item2, item1 -> item3
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
        link_type="depends",
    )

    # Get by source
    source_links = await link_repo.get_by_source(item1.id)
    assert len(source_links) == COUNT_TWO
    assert all(link.source_item_id == item1.id for link in source_links)

    # Get by target
    target_links = await link_repo.get_by_target(item2.id)
    assert len(target_links) == 1
    assert target_links[0].target_item_id == item2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_event_get_by_entity(db_session: AsyncSession) -> None:
    """Test getting events for a specific entity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Event Entity Test Project")

    event_repo = EventRepository(db_session)

    # Log events for entity
    entity_id = "test-entity-123"
    await event_repo.log(
        project_id=project.id,
        event_type="created",
        entity_type="item",
        entity_id=entity_id,
        data={"title": "Test"},
    )
    await event_repo.log(
        project_id=project.id,
        event_type="updated",
        entity_type="item",
        entity_id=entity_id,
        data={"title": "Updated"},
    )

    # Log event for different entity
    await event_repo.log(
        project_id=project.id,
        event_type="created",
        entity_type="item",
        entity_id="other-entity",
        data={"title": "Other"},
    )

    # Get events for specific entity
    events = await event_repo.get_by_entity(entity_id)
    assert len(events) == COUNT_TWO
    assert all(e.entity_id == entity_id for e in events)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_event_replay_entity_state(db_session: AsyncSession) -> None:
    """Test replaying events to reconstruct entity state."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Event Replay Test Project")

    event_repo = EventRepository(db_session)
    entity_id = "replay-entity"

    # Log creation event
    await event_repo.log(
        project_id=project.id,
        event_type="created",
        entity_type="item",
        entity_id=entity_id,
        data={"title": "Original", "status": "todo"},
    )

    # Log update event
    await event_repo.log(
        project_id=project.id,
        event_type="updated",
        entity_type="item",
        entity_id=entity_id,
        data={"status": "in_progress"},
    )

    # Replay to get final state
    state = await event_repo.get_entity_at_time(entity_id, datetime.now(UTC))
    assert state is not None
    assert state["title"] == "Original"
    assert state["status"] == "in_progress"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_event_replay_shows_deletion(db_session: AsyncSession) -> None:
    """Test that event replay returns None for deleted entities."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Event Deletion Test Project")

    event_repo = EventRepository(db_session)
    entity_id = "deleted-entity"

    # Log creation
    await event_repo.log(
        project_id=project.id,
        event_type="created",
        entity_type="item",
        entity_id=entity_id,
        data={"title": "Test"},
    )

    # Log deletion
    await event_repo.log(
        project_id=project.id,
        event_type="deleted",
        entity_type="item",
        entity_id=entity_id,
        data={},
    )

    # Replay should return None since entity was deleted
    state = await event_repo.get_entity_at_time(entity_id, datetime.now(UTC))
    assert state is None
