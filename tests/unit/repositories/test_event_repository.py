"""Unit tests for EventRepository."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TWO
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.project_repository import ProjectRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_log_event(db_session: AsyncSession) -> None:
    """Test logging an event."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)
    event = await event_repo.log(
        project_id=str(project.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-123",
        agent_id="agent-1",
        data={"title": "New Item"},
    )

    assert event.id is not None
    assert event.event_type == "item_created"
    assert event.entity_type == "item"
    assert event.entity_id == "item-123"
    assert event.data["title"] == "New Item"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_entity(db_session: AsyncSession) -> None:
    """Test getting events for an entity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    # Log multiple events for same entity
    await event_repo.log(
        project_id=str(project.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-123",
        data={"action": "create"},
    )
    await event_repo.log(
        project_id=str(project.id),
        event_type="item_updated",
        entity_type="item",
        entity_id="item-123",
        data={"action": "update"},
    )

    events = await event_repo.get_by_entity("item-123")
    assert len(events) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project(db_session: AsyncSession) -> None:
    """Test getting events for a project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name="Project 1", description="Test")
    project2 = await project_repo.create(name="Project 2", description="Test")

    event_repo = EventRepository(db_session)

    # Log events in project 1
    await event_repo.log(
        project_id=str(project1.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-1",
        data={},
    )
    await event_repo.log(
        project_id=str(project1.id),
        event_type="item_updated",
        entity_type="item",
        entity_id="item-2",
        data={},
    )

    # Log event in project 2
    await event_repo.log(
        project_id=str(project2.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-3",
        data={},
    )

    events = await event_repo.get_by_project(str(project1.id), limit=10)
    assert len(events) == COUNT_TWO
    assert all(e.project_id == project1.id for e in events)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_agent(db_session: AsyncSession) -> None:
    """Test getting events by agent."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    await event_repo.log(
        project_id=str(project.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-1",
        agent_id="agent-1",
        data={},
    )
    await event_repo.log(
        project_id=str(project.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-2",
        agent_id="agent-1",
        data={},
    )
    await event_repo.log(
        project_id=str(project.id),
        event_type="item_updated",
        entity_type="item",
        entity_id="item-3",
        agent_id="agent-2",
        data={},
    )

    agent_events = await event_repo.get_by_agent("agent-1")
    assert len(agent_events) == COUNT_TWO
    assert all(e.agent_id == "agent-1" for e in agent_events)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_agent_no_events(db_session: AsyncSession) -> None:
    """Test getting events for agent with no events."""
    event_repo = EventRepository(db_session)

    agent_events = await event_repo.get_by_agent("nonexistent-agent")
    assert len(agent_events) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_log_event_with_all_fields(db_session: AsyncSession) -> None:
    """Test logging event with all optional fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)
    event = await event_repo.log(
        project_id=str(project.id),
        event_type="item_created",
        entity_type="item",
        entity_id="item-1",
        agent_id="agent-1",
        data={"title": "Test", "status": "todo", "nested": {"key": "value"}},
    )

    assert event.agent_id == "agent-1"
    assert event.data["nested"]["key"] == "value"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_entity_multiple_events(db_session: AsyncSession) -> None:
    """Test getting multiple events for same entity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    # Create multiple events for same entity
    for i in range(5):
        await event_repo.log(
            project_id=str(project.id),
            event_type=f"event_{i}",
            entity_type="item",
            entity_id="item-1",
            data={"index": i},
        )

    events = await event_repo.get_by_entity("item-1")
    assert len(events) == COUNT_FIVE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_project_with_limit(db_session: AsyncSession) -> None:
    """Test getting project events with limit."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    # Create 10 events
    for i in range(10):
        await event_repo.log(
            project_id=str(project.id),
            event_type="item_created",
            entity_type="item",
            entity_id=f"item-{i}",
            data={},
        )

    events = await event_repo.get_by_project(str(project.id), limit=5)
    assert len(events) <= COUNT_FIVE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_event_data_persistence(db_session: AsyncSession) -> None:
    """Test that event data is persisted correctly."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    complex_data = {
        "string": "value",
        "number": 42,
        "boolean": True,
        "array": [1, 2, 3],
        "nested": {"key": "value", "deep": {"level": 2}},
    }

    event = await event_repo.log(
        project_id=str(project.id),
        event_type="complex_event",
        entity_type="item",
        entity_id="item-1",
        data=complex_data,
    )

    assert event.data == complex_data
    assert event.data["nested"]["deep"]["level"] == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_entity_at_time(db_session: AsyncSession) -> None:
    """Test getting entity state at a specific timestamp."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    # Create event
    await event_repo.log(
        project_id=str(project.id),
        event_type="created",
        entity_type="item",
        entity_id="item-1",
        data={"title": "Test", "status": "todo"},
    )

    # Get state at current time
    state = await event_repo.get_entity_at_time("item-1", datetime.now(UTC))

    assert state is not None
    assert state["title"] == "Test"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_entity_at_time_nonexistent(db_session: AsyncSession) -> None:
    """Test getting state for non-existent entity."""
    event_repo = EventRepository(db_session)

    state = await event_repo.get_entity_at_time("nonexistent", datetime.now(UTC))
    assert state is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_entity_at_time_after_deletion(db_session: AsyncSession) -> None:
    """Test getting state after entity deletion."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name="Test Project", description="Test")

    event_repo = EventRepository(db_session)

    # Create and delete
    await event_repo.log(
        project_id=str(project.id),
        event_type="created",
        entity_type="item",
        entity_id="item-1",
        data={"title": "Test"},
    )

    await event_repo.log(
        project_id=str(project.id),
        event_type="deleted",
        entity_type="item",
        entity_id="item-1",
        data={},
    )

    # Get state after deletion
    state = await event_repo.get_entity_at_time("item-1", datetime.now(UTC))
    assert state is None
