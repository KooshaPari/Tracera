"""Tests for missing AgentCoordinationService methods."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.agent_coordination_service import (
    AgentConflict,
    AgentCoordinationService,
    ConflictResolution,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_conflicts_with_agents(db_session: AsyncSession):
    """Test detecting conflicts with active agents."""
    service = AgentCoordinationService(db_session)

    now = datetime.utcnow()
    mock_agent1 = MagicMock()
    mock_agent1.id = "agent1"
    mock_agent1.name = "Agent 1"
    mock_agent1.last_activity_at = now.isoformat()

    mock_agent2 = MagicMock()
    mock_agent2.id = "agent2"
    mock_agent2.name = "Agent 2"
    mock_agent2.last_activity_at = (now - timedelta(seconds=30)).isoformat()

    with patch.object(service.agents, 'get_by_project', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [mock_agent1, mock_agent2]

        result = await service.detect_conflicts(project_id="proj1")

        assert isinstance(result, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_conflicts_no_recent_activity(db_session: AsyncSession):
    """Test detecting conflicts when no recent activity."""
    service = AgentCoordinationService(db_session)

    old_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    mock_agent1 = MagicMock()
    mock_agent1.id = "agent1"
    mock_agent1.last_activity_at = old_time

    mock_agent2 = MagicMock()
    mock_agent2.id = "agent2"
    mock_agent2.last_activity_at = old_time

    with patch.object(service.agents, 'get_by_project', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [mock_agent1, mock_agent2]

        result = await service.detect_conflicts(project_id="proj1")

        assert isinstance(result, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_conflict_last_write_wins(db_session: AsyncSession):
    """Test resolving conflict with last_write_wins strategy."""
    service = AgentCoordinationService(db_session)

    now = datetime.utcnow()
    mock_agent1 = MagicMock()
    mock_agent1.id = "agent1"
    mock_agent1.last_activity_at = now.isoformat()

    mock_agent2 = MagicMock()
    mock_agent2.id = "agent2"
    mock_agent2.last_activity_at = (now - timedelta(seconds=30)).isoformat()

    conflict = AgentConflict(
        agent1_id="agent1",
        agent2_id="agent2",
        conflict_type="write_conflict",
        entity_id="item1",
        description="Test conflict",
    )

    with patch.object(service.agents, 'get_by_id', new_callable=AsyncMock) as mock_get:
        with patch.object(service.events, 'log', new_callable=AsyncMock):
            async def get_agent(agent_id):
                return mock_agent1 if agent_id == "agent1" else mock_agent2

            mock_get.side_effect = get_agent

            result = await service.resolve_conflict(
                project_id="proj1",
                conflict=conflict,
                strategy="last_write_wins",
            )

            assert isinstance(result, ConflictResolution)
            assert result.resolved is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_resolve_conflict_priority_based(db_session: AsyncSession):
    """Test resolving conflict with priority_based strategy."""
    service = AgentCoordinationService(db_session)

    mock_agent1 = MagicMock()
    mock_agent1.id = "agent1"
    mock_agent1.last_activity_at = "2024-01-01T00:00:00"

    mock_agent2 = MagicMock()
    mock_agent2.id = "agent2"
    mock_agent2.last_activity_at = "2024-01-01T00:00:00"

    conflict = AgentConflict(
        agent1_id="agent1",
        agent2_id="agent2",
        conflict_type="write_conflict",
        entity_id="item1",
        description="Test conflict",
    )

    with patch.object(service.agents, 'get_by_id', new_callable=AsyncMock) as mock_get:
        with patch.object(service.events, 'log', new_callable=AsyncMock):
            async def get_agent(agent_id):
                return mock_agent1 if agent_id == "agent1" else mock_agent2

            mock_get.side_effect = get_agent

            result = await service.resolve_conflict(
                project_id="proj1",
                conflict=conflict,
                strategy="priority_based",
            )

            assert result.resolution_strategy == "priority_based"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agent_activity(db_session: AsyncSession):
    """Test getting agent activity."""
    service = AgentCoordinationService(db_session)

    mock_events = [
        MagicMock(
            event_type="write",
            entity_type="item",
            entity_id=f"item{i}",
            created_at="2024-01-01T00:00:00",
            data={"action": "update"},
        )
        for i in range(5)
    ]

    with patch.object(service.events, 'get_by_agent', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_events

        result = await service.get_agent_activity(agent_id="agent1", limit=10)

        assert isinstance(result, list)
        assert len(result) == 5
