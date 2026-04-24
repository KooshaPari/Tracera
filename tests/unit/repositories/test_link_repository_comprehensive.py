"""Comprehensive unit tests for LinkRepository to achieve 85%+ coverage.

This file covers all missing functionality identified in coverage analysis:
- create() link creation
- get_by_id() retrieval
- get_by_project() project filtering
- get_by_source() source item queries
- get_by_target() target item queries
- get_by_item() item queries (source or target)
- delete() link deletion
- delete_by_item() bulk deletion
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# Use link_test_setup fixture to auto-create graphs when projects are created
pytestmark = pytest.mark.usefixtures("link_test_setup")


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_basic(db_session: AsyncSession) -> None:
    """Test creating link with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Source Item", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Target Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )

    assert link.id is not None
    assert link.project_id == project.id
    assert link.source_item_id == item1.id
    assert link.target_item_id == item2.id
    assert link.link_type == "depends_on"
    assert link.metadata == {}  # Default empty dict


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_with_metadata(db_session: AsyncSession) -> None:
    """Test creating link with metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Source", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Target", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
        metadata={"strength": "strong", "verified": True},
    )

    assert link.metadata == {"strength": "strong", "verified": True}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link_with_none_metadata(db_session: AsyncSession) -> None:
    """Test creating link with None metadata uses empty dict."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Source", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Target", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
        metadata=None,
    )

    assert link.metadata == {}


# ============================================================================
# GET_BY_ID
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing_link(db_session: AsyncSession) -> None:
    """Test get_by_id returns link when it exists."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Source", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Target", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    created = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    await db_session.commit()

    found = await link_repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.source_item_id == item1.id
    assert found.target_item_id == item2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent_link(db_session: AsyncSession) -> None:
    """Test get_by_id returns None when link doesn't exist."""
    link_repo = LinkRepository(db_session)

    found = await link_repo.get_by_id("nonexistent-id")
    assert found is None


# ============================================================================
# GET_BY_PROJECT
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_returns_all_links(db_session: AsyncSession) -> None:
    """Test get_by_project returns all links in project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    item3 = await item_repo.create(project_id=project.id, title="Item 3", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    link1 = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    link2 = await link_repo.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item3.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Get all links in project
    links = await link_repo.get_by_project(project.id)
    assert len(links) == COUNT_TWO
    link_ids = {link.id for link in links}
    assert link1.id in link_ids
    assert link2.id in link_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_filters_by_project(db_session: AsyncSession) -> None:
    """Test get_by_project only returns links for specified project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1_p1 = await item_repo.create(project_id=project1.id, title="Item 1", view="FEATURE", item_type="feature")
    item2_p1 = await item_repo.create(project_id=project1.id, title="Item 2", view="FEATURE", item_type="feature")
    item1_p2 = await item_repo.create(project_id=project2.id, title="Item 1", view="FEATURE", item_type="feature")
    item2_p2 = await item_repo.create(project_id=project2.id, title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    link1 = await link_repo.create(
        project_id=project1.id,
        source_item_id=item1_p1.id,
        target_item_id=item2_p1.id,
        link_type="depends_on",
    )
    link2 = await link_repo.create(
        project_id=project2.id,
        source_item_id=item1_p2.id,
        target_item_id=item2_p2.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Get links for project1
    project1_links = await link_repo.get_by_project(project1.id)
    assert len(project1_links) == 1
    assert project1_links[0].id == link1.id

    # Get links for project2
    project2_links = await link_repo.get_by_project(project2.id)
    assert len(project2_links) == 1
    assert project2_links[0].id == link2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_empty_when_no_links(db_session: AsyncSession) -> None:
    """Test get_by_project returns empty list when no links exist."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    links = await link_repo.get_by_project(project.id)
    assert len(links) == 0


# ============================================================================
# GET_BY_SOURCE
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source_returns_outgoing_links(db_session: AsyncSession) -> None:
    """Test get_by_source returns all links from source item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(project_id=project.id, title="Source", view="FEATURE", item_type="feature")
    target1 = await item_repo.create(project_id=project.id, title="Target 1", view="FEATURE", item_type="feature")
    target2 = await item_repo.create(project_id=project.id, title="Target 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    link1 = await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target1.id,
        link_type="depends_on",
    )
    link2 = await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target2.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Get links from source
    links = await link_repo.get_by_source(source.id)
    assert len(links) == COUNT_TWO
    link_ids = {link.id for link in links}
    assert link1.id in link_ids
    assert link2.id in link_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source_excludes_incoming_links(db_session: AsyncSession) -> None:
    """Test get_by_source excludes links where item is target."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    # Link from item1 to item2
    outgoing = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    # Link from item2 to item1 (item1 is target, not source)
    incoming = await link_repo.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item1.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Get links from item1 (should only return outgoing)
    links = await link_repo.get_by_source(item1.id)
    assert len(links) == 1
    assert links[0].id == outgoing.id
    assert incoming.id not in {link.id for link in links}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source_empty_when_no_outgoing_links(db_session: AsyncSession) -> None:
    """Test get_by_source returns empty list when item has no outgoing links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=project.id, title="Isolated Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    links = await link_repo.get_by_source(item.id)
    assert len(links) == 0


# ============================================================================
# GET_BY_TARGET
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target_returns_incoming_links(db_session: AsyncSession) -> None:
    """Test get_by_target returns all links to target item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    source1 = await item_repo.create(project_id=project.id, title="Source 1", view="FEATURE", item_type="feature")
    source2 = await item_repo.create(project_id=project.id, title="Source 2", view="FEATURE", item_type="feature")
    target = await item_repo.create(project_id=project.id, title="Target", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    link1 = await link_repo.create(
        project_id=project.id,
        source_item_id=source1.id,
        target_item_id=target.id,
        link_type="depends_on",
    )
    link2 = await link_repo.create(
        project_id=project.id,
        source_item_id=source2.id,
        target_item_id=target.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Get links to target
    links = await link_repo.get_by_target(target.id)
    assert len(links) == COUNT_TWO
    link_ids = {link.id for link in links}
    assert link1.id in link_ids
    assert link2.id in link_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target_excludes_outgoing_links(db_session: AsyncSession) -> None:
    """Test get_by_target excludes links where item is source."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    # Link from item1 to item2 (item2 is target)
    incoming = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    # Link from item2 to item1 (item2 is source, not target)
    outgoing = await link_repo.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item1.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Get links to item2 (should only return incoming)
    links = await link_repo.get_by_target(item2.id)
    assert len(links) == 1
    assert links[0].id == incoming.id
    assert outgoing.id not in {link.id for link in links}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target_empty_when_no_incoming_links(db_session: AsyncSession) -> None:
    """Test get_by_target returns empty list when item has no incoming links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=project.id, title="Isolated Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    links = await link_repo.get_by_target(item.id)
    assert len(links) == 0


# ============================================================================
# GET_BY_ITEM
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_item_returns_all_links(db_session: AsyncSession) -> None:
    """Test get_by_item returns all links connected to item (source or target)."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    item3 = await item_repo.create(project_id=project.id, title="Item 3", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    # Link from item1 to item2 (item1 is source)
    link1 = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    # Link from item3 to item1 (item1 is target)
    link2 = await link_repo.create(
        project_id=project.id,
        source_item_id=item3.id,
        target_item_id=item1.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Get all links connected to item1
    links = await link_repo.get_by_item(item1.id)
    assert len(links) == COUNT_TWO
    link_ids = {link.id for link in links}
    assert link1.id in link_ids
    assert link2.id in link_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_item_empty_when_no_links(db_session: AsyncSession) -> None:
    """Test get_by_item returns empty list when item has no links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=project.id, title="Isolated Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    links = await link_repo.get_by_item(item.id)
    assert len(links) == 0


# ============================================================================
# DELETE
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_link_success(db_session: AsyncSession) -> None:
    """Test delete removes link."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Source", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Target", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Delete link
    deleted = await link_repo.delete(link.id)
    assert deleted is True
    await db_session.commit()

    # Verify deleted
    found = await link_repo.get_by_id(link.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_link_returns_false(db_session: AsyncSession) -> None:
    """Test delete returns False when link doesn't exist."""
    link_repo = LinkRepository(db_session)

    deleted = await link_repo.delete("nonexistent-id")
    assert deleted is False


# ============================================================================
# DELETE_BY_ITEM
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_by_item_removes_all_links(db_session: AsyncSession) -> None:
    """Test delete_by_item removes all links connected to item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    item3 = await item_repo.create(project_id=project.id, title="Item 3", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    # Create links involving item1
    link1 = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    link2 = await link_repo.create(
        project_id=project.id,
        source_item_id=item3.id,
        target_item_id=item1.id,
        link_type="blocks",
    )
    # Link not involving item1
    link3 = await link_repo.create(
        project_id=project.id,
        source_item_id=item2.id,
        target_item_id=item3.id,
        link_type="depends_on",
    )
    await db_session.commit()

    # Delete all links involving item1
    deleted_count = await link_repo.delete_by_item(item1.id)
    assert deleted_count == COUNT_TWO
    await db_session.commit()

    # Verify links involving item1 are deleted
    assert await link_repo.get_by_id(link1.id) is None
    assert await link_repo.get_by_id(link2.id) is None

    # Verify link not involving item1 still exists
    assert await link_repo.get_by_id(link3.id) is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_by_item_returns_zero_when_no_links(db_session: AsyncSession) -> None:
    """Test delete_by_item returns 0 when item has no links."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(project_id=project.id, title="Isolated Item", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    deleted_count = await link_repo.delete_by_item(item.id)
    assert deleted_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_by_item_handles_both_source_and_target(db_session: AsyncSession) -> None:
    """Test delete_by_item removes links where item is source or target."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    item_repo = ItemRepository(db_session)
    item1 = await item_repo.create(project_id=project.id, title="Item 1", view="FEATURE", item_type="feature")
    item2 = await item_repo.create(project_id=project.id, title="Item 2", view="FEATURE", item_type="feature")
    item3 = await item_repo.create(project_id=project.id, title="Item 3", view="FEATURE", item_type="feature")
    await db_session.commit()

    link_repo = LinkRepository(db_session)

    # Link where item1 is source
    link_as_source = await link_repo.create(
        project_id=project.id,
        source_item_id=item1.id,
        target_item_id=item2.id,
        link_type="depends_on",
    )
    # Link where item1 is target
    link_as_target = await link_repo.create(
        project_id=project.id,
        source_item_id=item3.id,
        target_item_id=item1.id,
        link_type="blocks",
    )
    await db_session.commit()

    # Delete all links involving item1
    deleted_count = await link_repo.delete_by_item(item1.id)
    assert deleted_count == COUNT_TWO
    await db_session.commit()

    # Verify both links are deleted
    assert await link_repo.get_by_id(link_as_source.id) is None
    assert await link_repo.get_by_id(link_as_target.id) is None
