"""
Comprehensive tests for AgentCoordinationService.

Tests all methods including:
- register_agent
- detect_conflicts
- resolve_conflict
- get_agent_activity

Coverage target: 90%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from tracertm.services.agent_coordination_service import (
    AgentCoordinationService,
    AgentConflict,
    ConflictResolution,
)
from tracertm.models.agent import Agent


class TestRegisterAgent:
    """Test register_agent method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return AgentCoordinationService(mock_session)

    @pytest.mark.asyncio
    async def test_register_agent_success(self, service):
        """Test successful agent registration."""
        # Setup mocks
        mock_agent = Mock(spec=Agent)
        mock_agent.id = "agent-1"
        mock_agent.name = "TestAgent"
        mock_agent.agent_type = "worker"

        service.agents.create = AsyncMock(return_value=mock_agent)
        service.events.log = AsyncMock()

        # Execute
        result = await service.register_agent(
            project_id="proj-1",
            name="TestAgent",
            agent_type="worker",
            metadata={"version": "1.0"},
        )

        # Verify
        assert result.id == "agent-1"
        assert result.name == "TestAgent"
        service.agents.create.assert_called_once_with(
            project_id="proj-1",
            name="TestAgent",
            agent_type="worker",
            metadata={"version": "1.0"},
        )
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_agent_without_metadata(self, service):
        """Test agent registration without metadata."""
        mock_agent = Mock(spec=Agent)
        mock_agent.id = "agent-2"
        mock_agent.name = "SimpleAgent"

        service.agents.create = AsyncMock(return_value=mock_agent)
        service.events.log = AsyncMock()

        result = await service.register_agent(
            project_id="proj-1",
            name="SimpleAgent",
            agent_type="monitor",
        )

        assert result.id == "agent-2"
        service.agents.create.assert_called_once_with(
            project_id="proj-1",
            name="SimpleAgent",
            agent_type="monitor",
            metadata=None,
        )

    @pytest.mark.asyncio
    async def test_register_agent_logs_event(self, service):
        """Test that registration logs an event."""
        mock_agent = Mock(spec=Agent)
        mock_agent.id = "agent-3"
        mock_agent.name = "EventAgent"
        mock_agent.agent_type = "processor"

        service.agents.create = AsyncMock(return_value=mock_agent)
        service.events.log = AsyncMock()

        await service.register_agent(
            project_id="proj-1",
            name="EventAgent",
            agent_type="processor",
        )

        # Verify event was logged with correct parameters
        call_args = service.events.log.call_args[1]
        assert call_args["project_id"] == "proj-1"
        assert call_args["event_type"] == "agent_registered"
        assert call_args["entity_type"] == "agent"
        assert call_args["entity_id"] == "agent-3"
        assert call_args["agent_id"] == "agent-3"


class TestDetectConflicts:
    """Test detect_conflicts method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return AgentCoordinationService(mock_session)

    @pytest.mark.asyncio
    async def test_detect_no_conflicts(self, service):
        """Test when no conflicts exist."""
        # Setup agents with different activity times
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.name = "Agent1"
        agent1.last_activity_at = (datetime.utcnow() - timedelta(minutes=10)).isoformat()

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.name = "Agent2"
        agent2.last_activity_at = (datetime.utcnow() - timedelta(minutes=20)).isoformat()

        service.agents.get_by_project = AsyncMock(return_value=[agent1, agent2])

        # Execute
        conflicts = await service.detect_conflicts("proj-1")

        # Verify
        assert len(conflicts) == 0

    @pytest.mark.asyncio
    async def test_detect_concurrent_conflicts(self, service):
        """Test detection of concurrent activity conflicts."""
        now = datetime.utcnow()

        # Setup agents with concurrent activity
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.name = "Agent1"
        agent1.last_activity_at = now.isoformat()

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.name = "Agent2"
        agent2.last_activity_at = (now + timedelta(seconds=30)).isoformat()

        service.agents.get_by_project = AsyncMock(return_value=[agent1, agent2])

        # Execute
        conflicts = await service.detect_conflicts("proj-1")

        # Verify
        assert len(conflicts) == 1
        assert conflicts[0].agent1_id == "agent-1"
        assert conflicts[0].agent2_id == "agent-2"
        assert conflicts[0].conflict_type == "concurrent_activity"
        assert "concurrent activity" in conflicts[0].description.lower()

    @pytest.mark.asyncio
    async def test_detect_conflicts_no_activity(self, service):
        """Test with agents having no activity."""
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.name = "Agent1"
        agent1.last_activity_at = None

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.name = "Agent2"
        agent2.last_activity_at = None

        service.agents.get_by_project = AsyncMock(return_value=[agent1, agent2])

        conflicts = await service.detect_conflicts("proj-1")

        assert len(conflicts) == 0

    @pytest.mark.asyncio
    async def test_detect_conflicts_single_agent(self, service):
        """Test with single agent (no conflicts possible)."""
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.name = "Agent1"
        agent1.last_activity_at = datetime.utcnow().isoformat()

        service.agents.get_by_project = AsyncMock(return_value=[agent1])

        conflicts = await service.detect_conflicts("proj-1")

        assert len(conflicts) == 0

    @pytest.mark.asyncio
    async def test_detect_conflicts_multiple_pairs(self, service):
        """Test with multiple agents creating multiple conflicts."""
        now = datetime.utcnow()

        # All agents active within 1 minute window
        agents = []
        for i in range(4):
            agent = Mock(spec=Agent)
            agent.id = f"agent-{i}"
            agent.name = f"Agent{i}"
            agent.last_activity_at = (now + timedelta(seconds=i * 10)).isoformat()
            agents.append(agent)

        service.agents.get_by_project = AsyncMock(return_value=agents)

        conflicts = await service.detect_conflicts("proj-1")

        # Should detect multiple conflicts (n choose 2 pairs)
        assert len(conflicts) > 0


class TestResolveConflict:
    """Test resolve_conflict method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return AgentCoordinationService(mock_session)

    @pytest.mark.asyncio
    async def test_resolve_last_write_wins_agent1(self, service):
        """Test last_write_wins strategy with agent1 winning."""
        now = datetime.utcnow()

        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.last_activity_at = (now + timedelta(minutes=5)).isoformat()

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.last_activity_at = now.isoformat()

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_activity",
            entity_id="item-1",
            description="Test conflict",
        )

        service.agents.get_by_id = AsyncMock(side_effect=lambda id: agent1 if id == "agent-1" else agent2)
        service.events.log = AsyncMock()

        # Execute
        resolution = await service.resolve_conflict("proj-1", conflict, "last_write_wins")

        # Verify
        assert resolution.resolved is True
        assert resolution.winner_agent_id == "agent-1"
        assert resolution.loser_agent_id == "agent-2"
        assert resolution.resolution_strategy == "last_write_wins"

    @pytest.mark.asyncio
    async def test_resolve_last_write_wins_agent2(self, service):
        """Test last_write_wins strategy with agent2 winning."""
        now = datetime.utcnow()

        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.last_activity_at = now.isoformat()

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.last_activity_at = (now + timedelta(minutes=5)).isoformat()

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_activity",
            entity_id="item-1",
            description="Test conflict",
        )

        service.agents.get_by_id = AsyncMock(side_effect=lambda id: agent1 if id == "agent-1" else agent2)
        service.events.log = AsyncMock()

        resolution = await service.resolve_conflict("proj-1", conflict, "last_write_wins")

        assert resolution.winner_agent_id == "agent-2"
        assert resolution.loser_agent_id == "agent-1"

    @pytest.mark.asyncio
    async def test_resolve_priority_based(self, service):
        """Test priority_based strategy."""
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.last_activity_at = datetime.utcnow().isoformat()

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.last_activity_at = datetime.utcnow().isoformat()

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_activity",
            entity_id="item-1",
            description="Test conflict",
        )

        service.agents.get_by_id = AsyncMock(side_effect=lambda id: agent1 if id == "agent-1" else agent2)
        service.events.log = AsyncMock()

        resolution = await service.resolve_conflict("proj-1", conflict, "priority_based")

        assert resolution.resolved is True
        assert resolution.winner_agent_id == "agent-1"
        assert resolution.resolution_strategy == "priority_based"

    @pytest.mark.asyncio
    async def test_resolve_agent_not_found(self, service):
        """Test error when agent not found."""
        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_activity",
            entity_id="item-1",
            description="Test conflict",
        )

        service.agents.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="One or both agents not found"):
            await service.resolve_conflict("proj-1", conflict, "last_write_wins")

    @pytest.mark.asyncio
    async def test_resolve_unknown_strategy(self, service):
        """Test error with unknown strategy."""
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_activity",
            entity_id="item-1",
            description="Test conflict",
        )

        service.agents.get_by_id = AsyncMock(side_effect=lambda id: agent1 if id == "agent-1" else agent2)

        with pytest.raises(ValueError, match="Unknown resolution strategy"):
            await service.resolve_conflict("proj-1", conflict, "invalid_strategy")

    @pytest.mark.asyncio
    async def test_resolve_logs_event(self, service):
        """Test that resolution logs an event."""
        agent1 = Mock(spec=Agent)
        agent1.id = "agent-1"
        agent1.last_activity_at = datetime.utcnow().isoformat()

        agent2 = Mock(spec=Agent)
        agent2.id = "agent-2"
        agent2.last_activity_at = datetime.utcnow().isoformat()

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_activity",
            entity_id="item-1",
            description="Test conflict",
        )

        service.agents.get_by_id = AsyncMock(side_effect=lambda id: agent1 if id == "agent-1" else agent2)
        service.events.log = AsyncMock()

        await service.resolve_conflict("proj-1", conflict, "last_write_wins")

        # Verify event logged
        call_args = service.events.log.call_args[1]
        assert call_args["event_type"] == "conflict_resolved"
        assert call_args["entity_type"] == "conflict"


class TestGetAgentActivity:
    """Test get_agent_activity method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return AgentCoordinationService(mock_session)

    @pytest.mark.asyncio
    async def test_get_activity_success(self, service):
        """Test retrieving agent activity."""
        # Setup mock events
        events = []
        for i in range(5):
            event = Mock()
            event.event_type = f"event_{i}"
            event.entity_type = "item"
            event.entity_id = f"item-{i}"
            event.created_at = datetime.utcnow().isoformat()
            event.data = {"action": f"action_{i}"}
            events.append(event)

        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute
        activity = await service.get_agent_activity("agent-1")

        # Verify
        assert len(activity) == 5
        assert activity[0]["event_type"] == "event_0"
        assert activity[0]["entity_type"] == "item"
        assert "timestamp" in activity[0]
        assert "data" in activity[0]

    @pytest.mark.asyncio
    async def test_get_activity_with_limit(self, service):
        """Test activity retrieval with limit."""
        # Create 150 events
        events = []
        for i in range(150):
            event = Mock()
            event.event_type = f"event_{i}"
            event.entity_type = "item"
            event.entity_id = f"item-{i}"
            event.created_at = datetime.utcnow().isoformat()
            event.data = {}
            events.append(event)

        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute with limit
        activity = await service.get_agent_activity("agent-1", limit=50)

        # Verify only first 50 returned
        assert len(activity) == 50

    @pytest.mark.asyncio
    async def test_get_activity_no_events(self, service):
        """Test with no activity."""
        service.events.get_by_agent = AsyncMock(return_value=[])

        activity = await service.get_agent_activity("agent-1")

        assert len(activity) == 0

    @pytest.mark.asyncio
    async def test_get_activity_default_limit(self, service):
        """Test default limit of 100."""
        events = [Mock() for _ in range(120)]
        for i, event in enumerate(events):
            event.event_type = f"event_{i}"
            event.entity_type = "item"
            event.entity_id = f"item-{i}"
            event.created_at = datetime.utcnow().isoformat()
            event.data = {}

        service.events.get_by_agent = AsyncMock(return_value=events)

        activity = await service.get_agent_activity("agent-1")

        # Default limit is 100
        assert len(activity) == 100
