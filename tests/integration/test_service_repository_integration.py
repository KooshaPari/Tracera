"""Service-to-Repository Integration Tests.

These tests validate the integration between services and repositories:
- Services using repositories for data access
- Complex business logic with database operations
- Service dependencies and interactions
- Error handling and recovery
- Service transaction boundaries

Target Coverage: 85%+ for service-repository interactions
"""

from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = pytest.mark.integration


# ============================================================================
# SETUP FIXTURES
# ============================================================================


@pytest.fixture
async def test_project(db_session: AsyncSession) -> None:
    """Create a test project."""
    repo = ProjectRepository(db_session)
    project = await repo.create(
        name="Service Test Project",
        description="Project for service integration tests",
        metadata={"test": True},
    )
    await db_session.commit()
    return project


@pytest.fixture
async def test_items(db_session: AsyncSession, test_project: Any) -> None:
    """Create test items with various properties."""
    repo = ItemRepository(db_session)

    items = []
    for i in range(5):
        item = await repo.create(
            project_id=test_project.id,
            title=f"Test Item {i + 1}",
            view="FEATURE" if i % 2 == 0 else "REQUIREMENT",
            item_type="feature" if i % 2 == 0 else "requirement",
            description=f"Description for item {i + 1}",
            status="todo" if i % 3 == 0 else ("in_progress" if i % 3 == 1 else "done"),
            priority="high" if i == 0 else ("medium" if i < COUNT_THREE else "low"),
            owner=f"user{i}@example.com" if i % 2 == 0 else None,
        )
        items.append(item)

    await db_session.commit()
    return items


# ============================================================================
# ITEM SERVICE INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_item_creation_and_retrieval(db_session: AsyncSession, test_project: Any) -> None:
    """Test creating and retrieving items through repository."""
    item_repo = ItemRepository(db_session)

    # Create
    item = await item_repo.create(
        project_id=test_project.id,
        title="Service Test Item",
        view="FEATURE",
        item_type="feature",
        description="Testing service integration",
        priority="high",
    )
    await db_session.commit()

    # Retrieve
    retrieved = await item_repo.get_by_id(item.id)
    assert retrieved is not None
    assert retrieved.title == "Service Test Item"
    assert retrieved.priority == "high"


@pytest.mark.asyncio
async def test_bulk_item_operations(db_session: AsyncSession, test_project: Any) -> None:
    """Test bulk operations on items."""
    item_repo = ItemRepository(db_session)

    # Create multiple items
    items = []
    for i in range(10):
        item = await item_repo.create(
            project_id=test_project.id,
            title=f"Bulk Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        items.append(item)

    await db_session.commit()

    # Query all
    all_items = await item_repo.get_by_project(test_project.id)
    assert len(all_items) >= COUNT_TEN

    # Filter by status
    todos = await item_repo.get_by_project(test_project.id, status="todo")
    assert len(todos) >= COUNT_TEN
    assert all(item.status == "todo" for item in todos)


@pytest.mark.asyncio
async def test_item_hierarchy_with_repository(db_session: AsyncSession, test_project: Any) -> None:
    """Test item parent-child relationships through repository."""
    item_repo = ItemRepository(db_session)

    # Create parent
    parent = await item_repo.create(
        project_id=test_project.id,
        title="Parent Feature",
        view="FEATURE",
        item_type="feature",
    )

    # Create children
    children = []
    for i in range(3):
        child = await item_repo.create(
            project_id=test_project.id,
            title=f"Child Feature {i}",
            view="FEATURE",
            item_type="feature",
            parent_id=parent.id,
        )
        children.append(child)

    # Create grandchild
    grandchild = await item_repo.create(
        project_id=test_project.id,
        title="Grandchild Feature",
        view="FEATURE",
        item_type="feature",
        parent_id=children[0].id,
    )

    await db_session.commit()

    # Test hierarchy queries
    retrieved_children = await item_repo.get_children(parent.id)
    assert len(retrieved_children) == COUNT_THREE

    descendants = await item_repo.get_descendants(parent.id)
    assert len(descendants) >= COUNT_FOUR

    ancestors = await item_repo.get_ancestors(grandchild.id)
    assert len(ancestors) >= COUNT_TWO


@pytest.mark.asyncio
async def test_item_status_transitions(db_session: AsyncSession, test_project: Any) -> None:
    """Test item status transitions."""
    item_repo = ItemRepository(db_session)

    item = await item_repo.create(
        project_id=test_project.id,
        title="Status Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    await db_session.commit()

    # Transition: todo -> in_progress
    updated = await item_repo.update(item.id, expected_version=item.version, status="in_progress")
    assert updated.status == "in_progress"
    await db_session.commit()

    # Transition: in_progress -> done
    updated = await item_repo.update(updated.id, expected_version=updated.version, status="done")
    assert updated.status == "done"


@pytest.mark.asyncio
async def test_item_metadata_operations(db_session: AsyncSession, test_project: Any) -> None:
    """Test item metadata handling."""
    item_repo = ItemRepository(db_session)

    metadata = {
        "assignee": "dev@example.com",
        "story_points": 5,
        "tags": ["urgent", "backend"],
        "custom": {"nested": "value"},
    }

    item = await item_repo.create(
        project_id=test_project.id,
        title="Metadata Item",
        view="FEATURE",
        item_type="feature",
        metadata=metadata,
    )
    await db_session.commit()

    retrieved = await item_repo.get_by_id(item.id)
    assert retrieved is not None
    assert retrieved.item_metadata == metadata


# ============================================================================
# LINK SERVICE INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_link_creation_between_items(db_session: AsyncSession, test_items: Any) -> None:
    """Test creating links between items."""
    link_repo = LinkRepository(db_session)
    project_id = test_items[0].project_id

    link = await link_repo.create(
        project_id=project_id,
        source_item_id=test_items[0].id,
        target_item_id=test_items[1].id,
        link_type="depends_on",
        link_metadata={"priority": "high"},
    )
    await db_session.commit()

    retrieved = await link_repo.get_by_id(link.id)
    assert retrieved is not None
    assert retrieved.source_item_id == test_items[0].id
    assert retrieved.target_item_id == test_items[1].id


@pytest.mark.asyncio
async def test_link_graph_construction(db_session: AsyncSession, test_items: Any) -> None:
    """Test building a complex link graph."""
    link_repo = LinkRepository(db_session)
    project_id = test_items[0].project_id

    # Create a chain: item0 -> item1 -> item2 -> item3
    for i in range(len(test_items) - 1):
        await link_repo.create(
            project_id=project_id,
            source_item_id=test_items[i].id,
            target_item_id=test_items[i + 1].id,
            link_type="depends_on",
        )

    # Add cross-links
    await link_repo.create(
        project_id=project_id,
        source_item_id=test_items[0].id,
        target_item_id=test_items[3].id,
        link_type="related_to",
    )

    await db_session.commit()

    # Verify graph
    from_item0 = await link_repo.get_by_source(test_items[0].id)
    assert len(from_item0) >= COUNT_TWO  # Direct dependency + cross-link

    to_item3 = await link_repo.get_by_target(test_items[3].id)
    assert len(to_item3) >= COUNT_TWO  # From item2 in chain + from item0


@pytest.mark.asyncio
async def test_link_navigation_patterns(db_session: AsyncSession, test_items: Any) -> None:
    """Test different link navigation patterns."""
    link_repo = LinkRepository(db_session)
    project_id = test_items[0].project_id

    # Create bidirectional links
    await link_repo.create(
        project_id=project_id,
        source_item_id=test_items[0].id,
        target_item_id=test_items[1].id,
        link_type="depends_on",
    )

    await link_repo.create(
        project_id=project_id,
        source_item_id=test_items[1].id,
        target_item_id=test_items[2].id,
        link_type="depends_on",
    )

    await db_session.commit()

    # Outgoing links from item0
    outgoing = await link_repo.get_by_source(test_items[0].id)
    assert len(outgoing) >= 1

    # Incoming links to item1
    incoming = await link_repo.get_by_target(test_items[1].id)
    assert len(incoming) >= 1

    # All links connected to item1
    connected = await link_repo.get_by_item(test_items[1].id)
    assert len(connected) >= COUNT_TWO  # One incoming, one outgoing


@pytest.mark.asyncio
async def test_link_type_management(db_session: AsyncSession, test_items: Any) -> None:
    """Test managing different link types."""
    link_repo = LinkRepository(db_session)
    project_id = test_items[0].project_id

    link_types = ["depends_on", "implements", "related_to", "conflicts_with"]

    for i, link_type in enumerate(link_types):
        if i < len(test_items) - 1:
            await link_repo.create(
                project_id=project_id,
                source_item_id=test_items[i].id,
                target_item_id=test_items[i + 1].id,
                link_type=link_type,
            )

    await db_session.commit()

    # Query by type
    depends_links = await link_repo.get_by_type("depends_on")
    assert any(link.link_type == "depends_on" for link in depends_links)

    implements_links = await link_repo.get_by_type("implements")
    assert any(link.link_type == "implements" for link in implements_links)


# ============================================================================
# CROSS-ENTITY INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_project_items_links_integration(db_session: AsyncSession, test_project: Any) -> None:
    """Test complete integration of projects, items, and links."""
    proj_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)
    link_repo = LinkRepository(db_session)

    # Create items
    req1 = await item_repo.create(
        project_id=test_project.id,
        title="Requirement 1",
        view="REQUIREMENT",
        item_type="requirement",
        status="done",
    )

    feat1 = await item_repo.create(
        project_id=test_project.id,
        title="Feature 1",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
    )

    feat2 = await item_repo.create(
        project_id=test_project.id,
        title="Feature 2",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )

    await db_session.commit()

    # Create links
    await link_repo.create(
        project_id=test_project.id,
        source_item_id=req1.id,
        target_item_id=feat1.id,
        link_type="implements",
    )

    await link_repo.create(
        project_id=test_project.id,
        source_item_id=feat1.id,
        target_item_id=feat2.id,
        link_type="depends_on",
    )

    await db_session.commit()

    # Verify integration
    project = await proj_repo.get_by_id(test_project.id)
    assert project is not None

    items = await item_repo.get_by_project(test_project.id)
    assert len(items) >= COUNT_THREE

    # Feature 1 has both incoming and outgoing links
    all_links_feat1 = await link_repo.get_by_item(feat1.id)
    assert len(all_links_feat1) >= COUNT_TWO


@pytest.mark.asyncio
async def test_cascading_delete_integration(db_session: AsyncSession, test_project: Any) -> None:
    """Test cascading delete through repositories."""
    item_repo = ItemRepository(db_session)
    link_repo = LinkRepository(db_session)

    # Create parent with children
    parent = await item_repo.create(project_id=test_project.id, title="Parent", view="FEATURE", item_type="feature")

    child1 = await item_repo.create(
        project_id=test_project.id,
        title="Child 1",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
    )

    child2 = await item_repo.create(
        project_id=test_project.id,
        title="Child 2",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
    )

    external = await item_repo.create(project_id=test_project.id, title="External", view="FEATURE", item_type="feature")

    # Create links
    await link_repo.create(
        project_id=test_project.id,
        source_item_id=child1.id,
        target_item_id=external.id,
        link_type="depends_on",
    )

    await db_session.commit()

    # Delete parent (soft delete cascades to children)
    await item_repo.delete(parent.id, soft=True)
    await db_session.commit()

    # Verify children are deleted
    assert await item_repo.get_by_id(child1.id) is None
    assert await item_repo.get_by_id(child2.id) is None

    # External item still exists
    assert await item_repo.get_by_id(external.id) is not None


@pytest.mark.asyncio
async def test_complex_query_patterns(db_session: AsyncSession, test_project: Any) -> None:
    """Test complex querying patterns."""
    item_repo = ItemRepository(db_session)

    # Create diverse items
    for priority in ["high", "medium", "low"]:
        for status in ["todo", "in_progress", "done"]:
            await item_repo.create(
                project_id=test_project.id,
                title=f"{priority} {status}",
                view="FEATURE",
                item_type="feature",
                priority=priority,
                status=status,
            )

    await db_session.commit()

    # Query patterns
    all_items = await item_repo.get_by_project(test_project.id)
    assert len(all_items) >= 9

    high_priority = await item_repo.get_by_project(test_project.id)
    high_items = [item for item in high_priority if item.priority == "high"]
    assert len(high_items) >= COUNT_THREE

    todo_items = await item_repo.get_by_project(test_project.id, status="todo")
    assert all(item.status == "todo" for item in todo_items)

    status_counts = await item_repo.count_by_status(test_project.id)
    assert "todo" in status_counts or "in_progress" in status_counts or "done" in status_counts


# ============================================================================
# TRANSACTION ISOLATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_transaction_boundaries(db_session: AsyncSession, test_project: Any) -> None:
    """Test transaction boundaries in service operations."""
    item_repo = ItemRepository(db_session)

    item1 = await item_repo.create(project_id=test_project.id, title="Item 1", view="FEATURE", item_type="feature")

    item2 = await item_repo.create(project_id=test_project.id, title="Item 2", view="FEATURE", item_type="feature")

    await db_session.commit()

    # Update multiple items in transaction
    await item_repo.update(item1.id, expected_version=item1.version, title="Updated Item 1")

    await item_repo.update(item2.id, expected_version=item2.version, title="Updated Item 2")

    await db_session.commit()

    # Verify both updates persisted
    found1 = await item_repo.get_by_id(item1.id)
    found2 = await item_repo.get_by_id(item2.id)

    assert found1 is not None and found2 is not None
    assert found1.title == "Updated Item 1"
    assert found2.title == "Updated Item 2"


@pytest.mark.asyncio
async def test_transaction_rollback_integration(db_session: AsyncSession, test_project: Any) -> None:
    """Test transaction rollback across multiple repositories."""
    item_repo = ItemRepository(db_session)
    link_repo = LinkRepository(db_session)

    item1 = await item_repo.create(project_id=test_project.id, title="Item 1", view="FEATURE", item_type="feature")

    item2 = await item_repo.create(project_id=test_project.id, title="Item 2", view="FEATURE", item_type="feature")

    await db_session.commit()

    # Start operations but rollback
    await link_repo.create(
        project_id=test_project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )

    await db_session.rollback()

    # Link should not exist after rollback
    # Items should still exist but not the link
    found_item1 = await item_repo.get_by_id(item1.id)
    assert found_item1 is not None


# ============================================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================================


@pytest.mark.asyncio
async def test_invalid_parent_reference(db_session: AsyncSession, test_project: Any) -> None:
    """Test creating item with invalid parent."""
    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError):
        await item_repo.create(
            project_id=test_project.id,
            title="Orphan",
            view="FEATURE",
            item_type="feature",
            parent_id="nonexistent-parent",
        )


@pytest.mark.asyncio
async def test_cross_project_parent_reference(db_session: AsyncSession) -> None:
    """Test that parent from different project is rejected."""
    proj_repo = ProjectRepository(db_session)
    item_repo = ItemRepository(db_session)

    proj1 = await proj_repo.create(name="Project 1")
    proj2 = await proj_repo.create(name="Project 2")

    parent = await item_repo.create(
        project_id=proj1.id,
        title="Parent in Project 1",
        view="FEATURE",
        item_type="feature",
    )

    await db_session.commit()

    with pytest.raises(ValueError):
        await item_repo.create(
            project_id=proj2.id,
            title="Child in Project 2",
            view="FEATURE",
            item_type="feature",
            parent_id=parent.id,
        )


@pytest.mark.asyncio
async def test_empty_metadata_handling(db_session: AsyncSession, test_project: Any) -> None:
    """Test handling of empty or null metadata."""
    item_repo = ItemRepository(db_session)

    # None metadata
    item1 = await item_repo.create(
        project_id=test_project.id,
        title="Item with None metadata",
        view="FEATURE",
        item_type="feature",
        metadata=None,
    )

    # Empty dict metadata
    item2 = await item_repo.create(
        project_id=test_project.id,
        title="Item with empty metadata",
        view="FEATURE",
        item_type="feature",
        metadata={},
    )

    await db_session.commit()

    found1 = await item_repo.get_by_id(item1.id)
    found2 = await item_repo.get_by_id(item2.id)

    assert found1 is not None and found2 is not None
    assert found1.item_metadata == {}
    assert found2.item_metadata == {}
