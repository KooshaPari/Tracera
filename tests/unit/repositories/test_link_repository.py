"""Unit tests for LinkRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository



@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_link(db_session: AsyncSession):
    """Test creating a link between items."""
    # Setup: Create project and items
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=project.id,
        title="Source Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    target = await item_repo.create(
        project_id=project.id,
        title="Target Item",
        view="CODE",
        item_type="file",
        status="todo",
    )

    # Test: Create link
    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target.id,
        link_type="implements",
    )

    assert link.id is not None
    assert link.source_item_id == source.id
    assert link.target_item_id == target.id
    assert link.link_type == "implements"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession):
    """Test retrieving a link by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=project.id, title="Source", view="FEATURE", item_type="feature", status="todo"
    )
    target = await item_repo.create(
        project_id=project.id, title="Target", view="CODE", item_type="file", status="todo"
    )

    link_repo = LinkRepository(db_session)
    created = await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target.id,
        link_type="implements",
    )

    retrieved = await link_repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_links_for_item(db_session: AsyncSession):
    """Test getting all links for an item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    feature = await item_repo.create(
        project_id=project.id, title="Feature", view="FEATURE", item_type="feature", status="todo"
    )
    code1 = await item_repo.create(
        project_id=project.id, title="Code 1", view="CODE", item_type="file", status="todo"
    )
    code2 = await item_repo.create(
        project_id=project.id, title="Code 2", view="CODE", item_type="file", status="todo"
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=project.id,
        source_item_id=feature.id,
        target_item_id=code1.id,
        link_type="implements",
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=feature.id,
        target_item_id=code2.id,
        link_type="implements",
    )

    links = await link_repo.get_by_item(feature.id)
    assert len(links) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_link(db_session: AsyncSession):
    """Test deleting a link."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=project.id, title="Source", view="FEATURE", item_type="feature", status="todo"
    )
    target = await item_repo.create(
        project_id=project.id, title="Target", view="CODE", item_type="file", status="todo"
    )

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target.id,
        link_type="implements",
    )

    await link_repo.delete(link.id)

    deleted = await link_repo.get_by_id(link.id)
    assert deleted is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_source(db_session: AsyncSession):
    """Test getting links by source item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=project.id, title="Source", view="FEATURE", item_type="feature", status="todo"
    )
    target1 = await item_repo.create(
        project_id=project.id, title="Target 1", view="CODE", item_type="file", status="todo"
    )
    target2 = await item_repo.create(
        project_id=project.id, title="Target 2", view="CODE", item_type="file", status="todo"
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target1.id,
        link_type="implements",
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target2.id,
        link_type="implements",
    )

    links = await link_repo.get_by_source(source.id)
    assert len(links) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_target(db_session: AsyncSession):
    """Test getting links by target item."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source1 = await item_repo.create(
        project_id=project.id, title="Source 1", view="FEATURE", item_type="feature", status="todo"
    )
    source2 = await item_repo.create(
        project_id=project.id, title="Source 2", view="FEATURE", item_type="feature", status="todo"
    )
    target = await item_repo.create(
        project_id=project.id, title="Target", view="CODE", item_type="file", status="todo"
    )

    link_repo = LinkRepository(db_session)
    await link_repo.create(
        project_id=project.id,
        source_item_id=source1.id,
        target_item_id=target.id,
        link_type="implements",
    )
    await link_repo.create(
        project_id=project.id,
        source_item_id=source2.id,
        target_item_id=target.id,
        link_type="implements",
    )

    links = await link_repo.get_by_target(target.id)
    assert len(links) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_link_with_metadata(db_session: AsyncSession):
    """Test creating link with metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    item_repo = ItemRepository(db_session)
    source = await item_repo.create(
        project_id=project.id, title="Source", view="FEATURE", item_type="feature", status="todo"
    )
    target = await item_repo.create(
        project_id=project.id, title="Target", view="CODE", item_type="file", status="todo"
    )

    link_repo = LinkRepository(db_session)
    link = await link_repo.create(
        project_id=project.id,
        source_item_id=source.id,
        target_item_id=target.id,
        link_type="implements",
        metadata={"priority": "high", "verified": True},
    )

    assert link.metadata["priority"] == "high"
    assert link.metadata["verified"] is True
