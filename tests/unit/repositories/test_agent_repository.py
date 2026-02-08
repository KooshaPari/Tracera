"""Unit tests for AgentRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO
from tracertm.repositories.agent_repository import AgentRepository
from tracertm.repositories.project_repository import ProjectRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_agent(db_session: AsyncSession) -> None:
    """Test creating an agent."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(
        project_id=project.id,
        name="Agent-1",
        agent_type="cli",
        metadata={"version": "1.0"},
    )

    assert agent.id is not None
    assert agent.name == "Agent-1"
    assert agent.agent_type == "cli"
    assert agent.status == "active"
    assert agent.agent_metadata["version"] == "1.0"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession) -> None:
    """Test retrieving an agent by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    agent_repo = AgentRepository(db_session)
    created = await agent_repo.create(
        project_id=project.id,
        name="Agent-1",
        agent_type="cli",
    )

    retrieved = await agent_repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project(db_session: AsyncSession) -> None:
    """Test getting agents by project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name="Project 1", description="Test")
    project2 = await project_repo.create(name="Project 2", description="Test")

    agent_repo = AgentRepository(db_session)

    # Create agents in project 1
    await agent_repo.create(project_id=project1.id, name="Agent-1", agent_type="cli")
    await agent_repo.create(project_id=project1.id, name="Agent-2", agent_type="api")

    # Create agent in project 2
    await agent_repo.create(project_id=project2.id, name="Agent-3", agent_type="cli")

    agents = await agent_repo.get_by_project(project1.id)
    assert len(agents) == COUNT_TWO
    assert all(a.project_id == project1.id for a in agents)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_status(db_session: AsyncSession) -> None:
    """Test updating agent status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(
        project_id=project.id,
        name="Agent-1",
        agent_type="cli",
    )

    updated = await agent_repo.update_status(agent.id, "inactive")
    assert updated.status == "inactive"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_activity(db_session: AsyncSession) -> None:
    """Test updating agent last activity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(
        project_id=project.id,
        name="Agent-1",
        agent_type="cli",
    )

    assert agent.last_activity_at is None

    updated = await agent_repo.update_activity(agent.id)
    assert updated.last_activity_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_active_agents(db_session: AsyncSession) -> None:
    """Test getting only active agents."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    agent_repo = AgentRepository(db_session)

    # Create active agents
    await agent_repo.create(project_id=project.id, name="Agent-1", agent_type="cli")
    await agent_repo.create(project_id=project.id, name="Agent-2", agent_type="api")

    # Create inactive agent
    agent3 = await agent_repo.create(project_id=project.id, name="Agent-3", agent_type="cli")
    await agent_repo.update_status(agent3.id, "inactive")

    active_agents = await agent_repo.get_by_project(project.id, status="active")
    assert len(active_agents) == COUNT_TWO
    assert all(a.status == "active" for a in active_agents)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_agent(db_session: AsyncSession) -> None:
    """Test deleting an agent."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    agent_repo = AgentRepository(db_session)
    agent = await agent_repo.create(
        project_id=project.id,
        name="Agent-1",
        agent_type="cli",
    )

    await agent_repo.delete(agent.id)

    deleted = await agent_repo.get_by_id(agent.id)
    assert deleted is None
