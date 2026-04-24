"""Comprehensive Database and Repository Layer Integration Tests.

These tests validate:
- Complex database queries and transactions
- Repository CRUD operations with real database
- Data integrity and constraints
- Concurrency and locking behavior
- Cascading operations and cleanup
- Complex filter and search operations

Target Coverage: 90%+ for repository layer
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = pytest.mark.integration


# ============================================================================
# PROJECT REPOSITORY - ADVANCED TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_project_create_with_metadata(db_session: AsyncSession) -> None:
    """Test project creation with complex metadata."""
    repo = ProjectRepository(db_session)

    metadata = {
        "team": "backend",
        "environment": "production",
        "version": "2.0.1",
        "features": ["traceability", "analytics"],
        "nested": {"key": "value", "list": [1, 2, 3]},
    }

    project = await repo.create(
        name="Complex Metadata Project",
        description="Project with complex metadata",
        metadata=metadata,
    )
    await db_session.commit()

    # Verify metadata persisted
    found = await repo.get_by_id(project.id)
    assert found is not None
    assert found.project_metadata == metadata


@pytest.mark.asyncio
async def test_project_update_partial(db_session: AsyncSession) -> None:
    """Test partial project updates."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name="Original Name", description="Original Description", metadata={"version": 1})
    await db_session.commit()

    # Update only name
    updated = await repo.update(project.id, name="New Name")
    assert updated is not None
    assert updated.name == "New Name"
    assert updated.description == "Original Description"
    assert updated.project_metadata == {"version": 1}


@pytest.mark.asyncio
async def test_project_update_metadata_merge(db_session: AsyncSession) -> None:
    """Test that metadata updates replace, not merge."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name="Project", metadata={"version": 1, "env": "dev"})
    await db_session.commit()

    # Update metadata - should replace entirely
    updated = await repo.update(project.id, metadata={"version": 2})
    assert updated is not None
    assert updated.project_metadata == {"version": 2}


@pytest.mark.asyncio
async def test_project_nonexistent_update(db_session: AsyncSession) -> None:
    """Test updating non-existent project returns None."""
    repo = ProjectRepository(db_session)

    result = await repo.update("nonexistent-id", name="New Name")
    assert result is None


@pytest.mark.asyncio
async def test_get_all_projects_empty(db_session: AsyncSession) -> None:
    """Test get_all on empty database."""
    repo = ProjectRepository(db_session)

    projects = await repo.get_all()
    assert isinstance(projects, list)


@pytest.mark.asyncio
async def test_project_isolation(db_session: AsyncSession) -> None:
    """Test that projects are properly isolated."""
    repo = ProjectRepository(db_session)

    proj1 = await repo.create(name="Project 1")
    proj2 = await repo.create(name="Project 2")
    await db_session.commit()

    assert proj1.id != proj2.id

    found1 = await repo.get_by_id(proj1.id)
    found2 = await repo.get_by_id(proj2.id)

    assert found1 is not None and found2 is not None
    assert found1.name == "Project 1"
    assert found2.name == "Project 2"


# ============================================================================
# ITEM REPOSITORY - ADVANCED TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_item_create_with_metadata(db_session: AsyncSession) -> None:
    """Test item creation with complex metadata."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")
    await db_session.commit()

    metadata = {
        "assigned_to": "developer@example.com",
        "labels": ["urgent", "backend"],
        "custom_fields": {"story_points": 5, "epic": "auth"},
    }

    item = await repo_item.create(
        project_id=project.id,
        title="Complex Item",
        view="FEATURE",
        item_type="feature",
        metadata=metadata,
        priority="high",
        owner="dev@example.com",
    )
    await db_session.commit()

    found = await repo_item.get_by_id(item.id)
    assert found is not None
    assert found.item_metadata == metadata


@pytest.mark.asyncio
async def test_item_soft_delete(db_session: AsyncSession) -> None:
    """Test soft delete functionality."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")
    item = await repo_item.create(project_id=project.id, title="Item to Delete", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Soft delete
    success = await repo_item.delete(item.id, soft=True)
    assert success is True
    await db_session.commit()

    # Should not be found in normal queries
    found = await repo_item.get_by_id(item.id)
    assert found is None


@pytest.mark.asyncio
async def test_item_restore(db_session: AsyncSession) -> None:
    """Test restoring soft-deleted items."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")
    item = await repo_item.create(project_id=project.id, title="Item to Restore", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Soft delete
    await repo_item.delete(item.id, soft=True)
    await db_session.commit()

    # Restore
    restored = await repo_item.restore(item.id)
    assert restored is not None
    assert restored.id == item.id
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_item_cascade_soft_delete(db_session: AsyncSession) -> None:
    """Test that soft deleting parent cascades to children."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    parent = await repo_item.create(project_id=project.id, title="Parent Item", view="FEATURE", item_type="feature")

    child = await repo_item.create(
        project_id=project.id,
        title="Child Item",
        view="FEATURE",
        item_type="feature",
        parent_id=parent.id,
    )
    await db_session.commit()

    # Delete parent
    await repo_item.delete(parent.id, soft=True)
    await db_session.commit()

    # Child should also be soft deleted
    found_child = await repo_item.get_by_id(child.id)
    assert found_child is None


@pytest.mark.asyncio
async def test_item_list_by_view(db_session: AsyncSession) -> None:
    """Test querying items by view."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    await repo_item.create(project_id=project.id, title="Feature 1", view="FEATURE", item_type="feature")

    await repo_item.create(
        project_id=project.id,
        title="Requirement 1",
        view="REQUIREMENT",
        item_type="requirement",
    )
    await db_session.commit()

    features = await repo_item.list_by_view(project.id, "FEATURE")
    assert len(features) >= 1
    assert all(item.view == "FEATURE" for item in features)


@pytest.mark.asyncio
async def test_item_count_by_status(db_session: AsyncSession) -> None:
    """Test counting items by status."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    await repo_item.create(project_id=project.id, title="Todo 1", view="FEATURE", item_type="feature", status="todo")
    await repo_item.create(project_id=project.id, title="Todo 2", view="FEATURE", item_type="feature", status="todo")
    await repo_item.create(project_id=project.id, title="Done 1", view="FEATURE", item_type="feature", status="done")
    await db_session.commit()

    counts = await repo_item.count_by_status(project.id)
    assert counts.get("todo", 0) >= COUNT_TWO
    assert counts.get("done", 0) >= 1


@pytest.mark.asyncio
async def test_item_get_by_project_with_status_filter(db_session: AsyncSession) -> None:
    """Test querying items by project and status."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    await repo_item.create(
        project_id=project.id,
        title="In Progress 1",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
    )
    await repo_item.create(project_id=project.id, title="Done 1", view="FEATURE", item_type="feature", status="done")
    await db_session.commit()

    in_progress = await repo_item.get_by_project(project.id, status="in_progress")
    assert len(in_progress) >= 1
    assert all(item.status == "in_progress" for item in in_progress)


@pytest.mark.asyncio
async def test_item_query_with_filters(db_session: AsyncSession) -> None:
    """Test dynamic query filtering."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    await repo_item.create(
        project_id=project.id,
        title="High Priority Item",
        view="FEATURE",
        item_type="feature",
        priority="high",
    )
    await repo_item.create(
        project_id=project.id,
        title="Medium Priority Item",
        view="FEATURE",
        item_type="feature",
        priority="medium",
    )
    await db_session.commit()

    # Query by priority
    results = await repo_item.query(project.id, filters={"priority": "high"})
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_item_hierarchy_operations(db_session: AsyncSession) -> None:
    """Test parent-child relationship operations."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    root = await repo_item.create(project_id=project.id, title="Root Item", view="FEATURE", item_type="feature")

    child1 = await repo_item.create(
        project_id=project.id,
        title="Child 1",
        view="FEATURE",
        item_type="feature",
        parent_id=root.id,
    )

    await repo_item.create(
        project_id=project.id,
        title="Child 2",
        view="FEATURE",
        item_type="feature",
        parent_id=root.id,
    )

    grandchild = await repo_item.create(
        project_id=project.id,
        title="Grandchild",
        view="FEATURE",
        item_type="feature",
        parent_id=child1.id,
    )
    await db_session.commit()

    # Get children
    children = await repo_item.get_children(root.id)
    assert len(children) >= COUNT_TWO

    # Get descendants
    descendants = await repo_item.get_descendants(root.id)
    assert len(descendants) >= COUNT_THREE

    # Get ancestors
    ancestors = await repo_item.get_ancestors(grandchild.id)
    assert len(ancestors) >= COUNT_TWO


@pytest.mark.asyncio
async def test_item_optimistic_locking(db_session: AsyncSession) -> None:
    """Test optimistic locking prevents concurrent modifications."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    item = await repo_item.create(project_id=project.id, title="Original Title", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Simulate concurrent modification with wrong version
    with pytest.raises(ConcurrencyError):
        await repo_item.update(
            item.id,
            expected_version=999,  # Wrong version
            title="Updated Title",
        )


# ============================================================================
# LINK REPOSITORY - ADVANCED TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_link_create_with_metadata(db_session: AsyncSession) -> None:
    """Test link creation with metadata."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    item1 = await repo_item.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")

    item2 = await repo_item.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    metadata = {"reason": "implements_requirement", "impact": "high", "priority": 1}

    link = await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="implements",
        link_metadata=metadata,
    )
    await db_session.commit()

    found = await repo_link.get_by_id(link.id)
    assert found is not None
    assert found.link_metadata == metadata


@pytest.mark.asyncio
async def test_link_get_by_source_and_target(db_session: AsyncSession) -> None:
    """Test getting links by both source and target."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    item1 = await repo_item.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")

    item2 = await repo_item.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")

    item3 = await repo_item.create(project_id=project.id, title="Item 3", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Create multiple links
    await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )

    await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item3.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Get links from item1
    links = await repo_link.get_by_source(item1.id)
    assert len(links) >= COUNT_TWO


@pytest.mark.asyncio
async def test_link_get_all_by_item(db_session: AsyncSession) -> None:
    """Test getting all links connected to an item."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    item1 = await repo_item.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await repo_item.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    item3 = await repo_item.create(project_id=project.id, title="Item 3", view="FEATURE", item_type="feature")
    await db_session.commit()

    # item2 is source, item1 is target (item2 -> item1)
    await repo_link.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item1.id,
        link_type="depends_on",
    )

    # item1 is source, item3 is target (item1 -> item3)
    await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item3.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Get all links for item1 (both incoming and outgoing)
    all_links = await repo_link.get_by_item(item1.id)
    assert len(all_links) >= COUNT_TWO


@pytest.mark.asyncio
async def test_link_delete_by_item(db_session: AsyncSession) -> None:
    """Test cascade delete of links when item is deleted."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    item1 = await repo_item.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await repo_item.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    link = await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Delete all links for item
    deleted_count = await repo_link.delete_by_item(item1.id)
    assert deleted_count >= 1
    await db_session.commit()

    # Verify link is gone
    found = await repo_link.get_by_id(link.id)
    assert found is None


@pytest.mark.asyncio
async def test_link_get_by_type(db_session: AsyncSession) -> None:
    """Test getting links by type."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    item1 = await repo_item.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await repo_item.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Get links by type
    dep_links = await repo_link.get_by_type("depends_on")
    assert len(dep_links) >= 1
    assert all(link.link_type == "depends_on" for link in dep_links)


# ============================================================================
# CROSS-REPOSITORY INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_item_project_relationship(db_session: AsyncSession) -> None:
    """Test item and project relationship integrity."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)

    proj1 = await repo_proj.create(name="Project 1")
    proj2 = await repo_proj.create(name="Project 2")
    await db_session.commit()

    # Create items in different projects
    item1 = await repo_item.create(project_id=proj1.id, title="Item in Project 1", view="FEATURE", item_type="feature")
    item2 = await repo_item.create(project_id=proj2.id, title="Item in Project 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    # Verify items are in their respective projects
    proj1_items = await repo_item.get_by_project(proj1.id)
    proj2_items = await repo_item.get_by_project(proj2.id)

    assert any(item.id == item1.id for item in proj1_items)
    assert any(item.id == item2.id for item in proj2_items)


@pytest.mark.asyncio
async def test_complex_link_graph(db_session: AsyncSession) -> None:
    """Test complex multi-level link graph."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    project = await repo_proj.create(name="Test Project")

    # Create items in diamond pattern: A -> B, A -> C, B -> D, C -> D
    items = {}
    for letter in ["A", "B", "C", "D"]:
        items[letter] = await repo_item.create(
            project_id=project.id,
            title=f"Item {letter}",
            view="FEATURE",
            item_type="feature",
        )
    await db_session.commit()

    # Create diamond links
    await repo_link.create(
        project_id=project.id,
        source_item_id=items["A"].id,
        target_item_id=items["B"].id,
        link_type="depends_on",
    )
    await repo_link.create(
        project_id=project.id,
        source_item_id=items["A"].id,
        target_item_id=items["C"].id,
        link_type="depends_on",
    )
    await repo_link.create(
        project_id=project.id,
        source_item_id=items["B"].id,
        target_item_id=items["D"].id,
        link_type="depends_on",
    )
    await repo_link.create(
        project_id=project.id,
        source_item_id=items["C"].id,
        target_item_id=items["D"].id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Verify graph structure
    a_deps = await repo_link.get_by_source(items["A"].id)
    d_incoming = await repo_link.get_by_target(items["D"].id)

    assert len(a_deps) >= COUNT_TWO
    assert len(d_incoming) >= COUNT_TWO


# ============================================================================
# TRANSACTION AND ISOLATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession) -> None:
    """Test that rollback reverts changes."""
    repo_proj = ProjectRepository(db_session)

    project = await repo_proj.create(name="Test Project")
    await db_session.commit()

    original_id = project.id

    # Start a change
    await repo_proj.update(project.id, name="Updated Name")

    # Rollback
    await db_session.rollback()

    # Re-fetch and verify rollback
    found = await repo_proj.get_by_id(original_id)
    assert found is not None
    assert found.name == "Test Project"  # Should have original name


@pytest.mark.asyncio
async def test_multiple_concurrent_repositories(db_session: AsyncSession) -> None:
    """Test multiple repositories working on same session."""
    repo_proj = ProjectRepository(db_session)
    repo_item = ItemRepository(db_session)
    repo_link = LinkRepository(db_session)

    # All operations in single session
    project = await repo_proj.create(name="Concurrent Test")
    item1 = await repo_item.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await repo_item.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    link = await repo_link.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Verify all persisted correctly
    assert (await repo_proj.get_by_id(project.id)) is not None
    assert (await repo_item.get_by_id(item1.id)) is not None
    assert (await repo_link.get_by_id(link.id)) is not None
