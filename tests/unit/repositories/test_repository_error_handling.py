"""Unit tests for repository error handling and edge cases."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_update_version_conflict(db_session: AsyncSession) -> None:
    """Test optimistic locking raises error on version conflict."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
    )

    # Update with correct version
    await item_repo.update(item.id, expected_version=1, title="Updated")

    # Try to update with stale version (should fail)
    with pytest.raises(ConcurrencyError) as exc_info:
        await item_repo.update(item.id, expected_version=1, title="Conflict")

    assert "was modified by another agent" in str(exc_info.value)
    assert "expected version 1" in str(exc_info.value)
    assert "current version 2" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_update_nonexistent(db_session: AsyncSession) -> None:
    """Test updating non-existent item raises error."""
    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError, match=r"not found") as exc_info:
        await item_repo.update("nonexistent-id", expected_version=1, title="Test")

    assert "not found" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_create_with_invalid_parent(db_session: AsyncSession) -> None:
    """Test creating item with non-existent parent raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project")

    item_repo = ItemRepository(db_session)

    with pytest.raises(ValueError, match=r"not found") as exc_info:
        await item_repo.create(
            project_id=project.id,
            title="Test Item",
            view="FEATURE",
            item_type="feature",
            parent_id="nonexistent-parent",
        )

    assert "not found" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_create_with_parent_from_different_project(db_session: AsyncSession) -> None:
    """Test creating item with parent from different project raises error."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name="Project 1")
    project2 = await project_repo.create(name="Project 2")

    item_repo = ItemRepository(db_session)
    parent = await item_repo.create(
        project_id=project1.id,
        title="Parent Item",
        view="FEATURE",
        item_type="feature",
    )

    with pytest.raises(ValueError, match=r"not in same project") as exc_info:
        await item_repo.create(
            project_id=project2.id,
            title="Child Item",
            view="FEATURE",
            item_type="feature",
            parent_id=parent.id,
        )

    assert "not in same project" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_update_status_nonexistent(db_session: AsyncSession) -> None:
    """Test updating status of non-existent agent raises error."""
    agent_repo = AgentRepository(db_session)

    with pytest.raises(ValueError, match=r"not found") as exc_info:
        await agent_repo.update_status("nonexistent-id", "inactive")

    assert "not found" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_update_activity_nonexistent(db_session: AsyncSession) -> None:
    """Test updating activity of non-existent agent raises error."""
    agent_repo = AgentRepository(db_session)

    with pytest.raises(ValueError, match=r"not found") as exc_info:
        await agent_repo.update_activity("nonexistent-id")

    assert "not found" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_item_get_by_id_with_project_scope(db_session: AsyncSession) -> None:
    """Test getting item by ID scoped to project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name="Project 1")
    project2 = await project_repo.create(name="Project 2")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project1.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
    )

    # Should find in correct project
    found = await item_repo.get_by_id(item.id, project_id=project1.id)
    assert found is not None
    assert found.id == item.id

    # Should not find in different project
    not_found = await item_repo.get_by_id(item.id, project_id=project2.id)
    assert not_found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_item_returns_false(db_session: AsyncSession) -> None:
    """Test deleting non-existent item returns False."""
    item_repo = ItemRepository(db_session)
    result = await item_repo.delete("nonexistent-id", soft=True)
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_link_returns_false(db_session: AsyncSession) -> None:
    """Test deleting non-existent link returns False."""
    link_repo = LinkRepository(db_session)
    result = await link_repo.delete("nonexistent-id")
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_agent_returns_false(db_session: AsyncSession) -> None:
    """Test deleting non-existent agent returns False."""
    agent_repo = AgentRepository(db_session)
    result = await agent_repo.delete("nonexistent-id")
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_project_update_nonexistent_returns_none(db_session: AsyncSession) -> None:
    """Test updating non-existent project returns None."""
    project_repo = ProjectRepository(db_session)
    result = await project_repo.update("nonexistent-id", name="New Name")
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restore_nonexistent_item_returns_none(db_session: AsyncSession) -> None:
    """Test restoring non-existent item returns None."""
    item_repo = ItemRepository(db_session)
    result = await item_repo.restore("nonexistent-id")
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_restore_non_deleted_item_returns_none(db_session: AsyncSession) -> None:
    """Test restoring non-deleted item returns None."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project")

    item_repo = ItemRepository(db_session)
    item = await item_repo.create(
        project_id=project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
    )

    # Item is not deleted, so restore should return None
    result = await item_repo.restore(item.id)
    assert result is None
