"""Comprehensive unit tests for AgentRepository to achieve 85%+ coverage.

This file covers all missing functionality identified in coverage analysis:
- create() agent creation
- get_by_id() retrieval
- get_by_project() with status filtering
- update_status() status updates
- update_activity() activity timestamp updates
- delete() agent deletion
"""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.project_repository import ProjectRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_agent_basic(db_session: AsyncSession) -> None:
    """Test creating agent with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")

    assert agent.id is not None
    assert agent.project_id == project.id
    assert agent.name == "Test Agent"
    assert agent.agent_type == "test"
    assert agent.status == "active"  # Default status
    assert agent.agent_metadata == {}  # Default empty dict


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_agent_with_metadata(db_session: AsyncSession) -> None:
    """Test creating agent with metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(
        project_id=str(project.id),
        name="Test Agent",
        agent_type="test",
        metadata={"key": "value", "version": "1.0"},
    )

    assert agent.agent_metadata == {"key": "value", "version": "1.0"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_agent_with_none_metadata(db_session: AsyncSession) -> None:
    """Test creating agent with None metadata uses empty dict."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test", metadata=None)

    assert agent.agent_metadata == {}


# ============================================================================
# GET_BY_ID
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing_agent(db_session: AsyncSession) -> None:
    """Test get_by_id returns agent when it exists."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    created = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")
    await db_session.commit()

    found = await agent_repo.get_by_id(str(created.id))
    assert found is not None
    assert found.id == created.id
    assert found.name == created.name


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent_agent(db_session: AsyncSession) -> None:
    """Test get_by_id returns None when agent doesn't exist."""
    agent_repo = AgentRepository(db_session)

    found = await agent_repo.get_by_id("nonexistent-id")
    assert found is None


# ============================================================================
# GET_BY_PROJECT - Status Filtering
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_all_agents(db_session: AsyncSession) -> None:
    """Test get_by_project returns all agents when no status filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)

    agent1 = await agent_repo.create(project_id=str(project.id), name="Agent 1", agent_type="test")
    agent2 = await agent_repo.create(project_id=str(project.id), name="Agent 2", agent_type="test")
    await db_session.commit()

    # Update agent2 status
    await agent_repo.update_status(str(agent2.id), "inactive")
    await db_session.commit()

    # Get all agents
    all_agents = await agent_repo.get_by_project(str(project.id))
    assert len(all_agents) == COUNT_TWO
    agent_ids = {agent.id for agent in all_agents}
    assert agent1.id in agent_ids
    assert agent2.id in agent_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_with_status_filter(db_session: AsyncSession) -> None:
    """Test get_by_project filters by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)

    agent1 = await agent_repo.create(project_id=str(project.id), name="Active Agent", agent_type="test")
    agent2 = await agent_repo.create(project_id=str(project.id), name="Inactive Agent", agent_type="test")
    await db_session.commit()

    # Update agent2 status
    await agent_repo.update_status(str(agent2.id), "inactive")
    await db_session.commit()

    # Get only active agents
    active_agents = await agent_repo.get_by_project(str(project.id), status="active")
    assert len(active_agents) == 1
    assert active_agents[0].id == agent1.id

    # Get only inactive agents
    inactive_agents = await agent_repo.get_by_project(str(project.id), status="inactive")
    assert len(inactive_agents) == 1
    assert inactive_agents[0].id == agent2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_empty_when_no_agents(db_session: AsyncSession) -> None:
    """Test get_by_project returns empty list when no agents exist."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)

    agents = await agent_repo.get_by_project(str(project.id))
    assert len(agents) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_filters_by_project(db_session: AsyncSession) -> None:
    """Test get_by_project only returns agents for specified project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)

    agent1 = await agent_repo.create(project_id=str(project1.id), name="Agent 1", agent_type="test")
    agent2 = await agent_repo.create(project_id=str(project2.id), name="Agent 2", agent_type="test")
    await db_session.commit()

    # Get agents for project1
    project1_agents = await agent_repo.get_by_project(str(project1.id))
    assert len(project1_agents) == 1
    assert project1_agents[0].id == agent1.id

    # Get agents for project2
    project2_agents = await agent_repo.get_by_project(str(project2.id))
    assert len(project2_agents) == 1
    assert project2_agents[0].id == agent2.id


# ============================================================================
# UPDATE_STATUS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_status_success(db_session: AsyncSession) -> None:
    """Test update_status updates agent status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")
    assert agent.status == "active"
    await db_session.commit()

    # Update status
    updated = await agent_repo.update_status(str(agent.id), "inactive")
    assert updated.status == "inactive"
    await db_session.commit()

    # Verify persisted
    found = await agent_repo.get_by_id(str(agent.id))
    assert found is not None and found.status == "inactive"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_status_nonexistent_agent_raises_error(db_session: AsyncSession) -> None:
    """Test update_status raises ValueError when agent doesn't exist."""
    agent_repo = AgentRepository(db_session)

    with pytest.raises(ValueError, match=r"Agent .* not found"):
        await agent_repo.update_status("nonexistent-id", "inactive")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_status_multiple_updates(db_session: AsyncSession) -> None:
    """Test update_status can be called multiple times."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")
    await db_session.commit()

    # Update to inactive
    updated = await agent_repo.update_status(str(agent.id), "inactive")
    assert updated.status == "inactive"
    await db_session.commit()

    # Update back to active
    updated = await agent_repo.update_status(str(agent.id), "active")
    assert updated.status == "active"
    await db_session.commit()

    # Update to paused
    updated = await agent_repo.update_status(str(agent.id), "paused")
    assert updated.status == "paused"


# ============================================================================
# UPDATE_ACTIVITY
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_activity_success(db_session: AsyncSession) -> None:
    """Test update_activity updates last_activity_at timestamp."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")
    assert agent.last_activity_at is None
    await db_session.commit()

    # Update activity
    updated = await agent_repo.update_activity(str(agent.id))
    assert updated.last_activity_at is not None
    assert isinstance(updated.last_activity_at, str)
    await db_session.commit()

    # Verify persisted
    found = await agent_repo.get_by_id(str(agent.id))
    assert found is not None
    assert found.last_activity_at is not None
    assert found.last_activity_at == updated.last_activity_at


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_activity_nonexistent_agent_raises_error(db_session: AsyncSession) -> None:
    """Test update_activity raises ValueError when agent doesn't exist."""
    agent_repo = AgentRepository(db_session)

    with pytest.raises(ValueError, match=r"Agent .* not found"):
        await agent_repo.update_activity("nonexistent-id")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_activity_updates_timestamp(db_session: AsyncSession) -> None:
    """Test update_activity updates timestamp on each call."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")
    await db_session.commit()

    # First update
    updated1 = await agent_repo.update_activity(str(agent.id))
    first_timestamp = updated1.last_activity_at
    await db_session.commit()

    # Wait a bit
    await asyncio.sleep(0.1)

    # Second update
    updated2 = await agent_repo.update_activity(str(agent.id))
    second_timestamp = updated2.last_activity_at
    await db_session.commit()

    # Timestamps should be different
    assert first_timestamp != second_timestamp


# ============================================================================
# DELETE
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_agent_success(db_session: AsyncSession) -> None:
    """Test delete removes agent."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(project_id=str(project.id), name="Test Agent", agent_type="test")
    await db_session.commit()

    # Delete agent
    deleted = await agent_repo.delete(str(agent.id))
    assert deleted is True
    await db_session.commit()

    # Verify deleted
    found = await agent_repo.get_by_id(str(agent.id))
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_agent_returns_false(db_session: AsyncSession) -> None:
    """Test delete returns False when agent doesn't exist."""
    agent_repo = AgentRepository(db_session)

    deleted = await agent_repo.delete("nonexistent-id")
    assert deleted is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_multiple_agents(db_session: AsyncSession) -> None:
    """Test delete can remove multiple agents."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    agent_repo = AgentRepository(db_session)

    agent1 = await agent_repo.create(project_id=str(project.id), name="Agent 1", agent_type="test")
    agent2 = await agent_repo.create(project_id=str(project.id), name="Agent 2", agent_type="test")
    await db_session.commit()

    # Delete both
    deleted1 = await agent_repo.delete(str(agent1.id))
    deleted2 = await agent_repo.delete(str(agent2.id))
    assert deleted1 is True
    assert deleted2 is True
    await db_session.commit()

    # Verify both deleted
    assert await agent_repo.get_by_id(str(agent1.id)) is None
    assert await agent_repo.get_by_id(str(agent2.id)) is None
