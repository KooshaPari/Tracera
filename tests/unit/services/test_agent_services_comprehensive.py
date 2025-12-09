"""
Comprehensive tests for agent services: AgentPerformanceService, AgentMonitoringService,
AgentCoordinationService, and AgentMetricsService.

Full coverage of all methods with real test scenarios.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from tracertm.services.agent_performance_service import AgentPerformanceService
from tracertm.services.agent_monitoring_service import AgentMonitoringService
from tracertm.services.agent_coordination_service import (
    AgentCoordinationService,
    ConflictResolution,
    AgentConflict,
)
from tracertm.services.agent_metrics_service import AgentMetricsService


class TestAgentPerformanceService:
    """Test AgentPerformanceService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = AsyncMock()
        service = AgentPerformanceService(session)
        service.agents = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_agent_stats_basic(self, service):
        """Test getting basic agent statistics."""
        # Setup agent - need to set name as a direct attribute, not a Mock
        agent = Mock()
        agent.id = "agent-1"
        agent.name = "Test Agent"
        service.agents.get_by_id = AsyncMock(return_value=agent)

        # Setup events
        events = []
        for i in range(10):
            event = Mock()
            event.created_at = datetime.utcnow() - timedelta(hours=1)
            event.event_type = "item_created"
            events.append(event)
        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute
        stats = await service.get_agent_stats("agent-1", time_window_hours=24)

        # Assert
        assert stats["agent_id"] == "agent-1"
        assert stats["agent_name"] == "Test Agent"
        assert stats["total_events"] == 10
        assert stats["events_per_hour"] > 0

    @pytest.mark.asyncio
    async def test_get_agent_stats_agent_not_found(self, service):
        """Test error when agent not found."""
        service.agents.get_by_id = AsyncMock(return_value=None)

        stats = await service.get_agent_stats("nonexistent")

        assert "error" in stats
        assert stats["error"] == "Agent not found"

    @pytest.mark.asyncio
    async def test_get_agent_stats_event_types(self, service):
        """Test event type breakdown."""
        agent = Mock(id="agent-1", name="Test Agent")
        service.agents.get_by_id = AsyncMock(return_value=agent)

        # Mixed event types
        events = []
        for i in range(5):
            event = Mock()
            event.created_at = datetime.utcnow() - timedelta(minutes=30)
            event.event_type = "item_created"
            events.append(event)
        for i in range(3):
            event = Mock()
            event.created_at = datetime.utcnow() - timedelta(minutes=30)
            event.event_type = "item_updated"
            events.append(event)
        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute
        stats = await service.get_agent_stats("agent-1")

        # Assert
        assert stats["event_types"]["item_created"] == 5
        assert stats["event_types"]["item_updated"] == 3

    @pytest.mark.asyncio
    async def test_get_team_performance(self, service):
        """Test getting team performance metrics."""
        # Setup agents
        agents = [
            Mock(id="agent-1", name="Agent 1"),
            Mock(id="agent-2", name="Agent 2"),
        ]
        service.agents.get_by_project = AsyncMock(return_value=agents)

        # Mock get_agent_stats
        async def mock_get_stats(agent_id, time_window_hours=24):
            return {
                "agent_id": agent_id,
                "total_events": 10,
                "events_per_hour": 1.0,
            }

        service.get_agent_stats = mock_get_stats

        # Execute
        team_stats = await service.get_team_performance("proj-1")

        # Assert
        assert team_stats["project_id"] == "proj-1"
        assert team_stats["total_agents"] == 2
        assert len(team_stats["agents"]) == 2
        assert team_stats["total_events"] == 20

    @pytest.mark.asyncio
    async def test_get_agent_efficiency(self, service):
        """Test agent efficiency score calculation."""
        agent = Mock(id="agent-1", name="Test Agent")
        service.agents.get_by_id = AsyncMock(return_value=agent)

        events = [Mock(created_at=datetime.utcnow(), event_type=f"type-{i % 3}")
                 for i in range(10)]
        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute
        efficiency = await service.get_agent_efficiency("agent-1")

        # Assert
        assert "efficiency_score" in efficiency
        assert "rating" in efficiency
        assert 0 <= efficiency["efficiency_score"] <= 100

    def test_get_efficiency_rating(self, service):
        """Test efficiency rating categorization."""
        assert service._get_efficiency_rating(95) == "Excellent"
        assert service._get_efficiency_rating(80) == "Good"
        assert service._get_efficiency_rating(60) == "Fair"
        assert service._get_efficiency_rating(30) == "Poor"

    @pytest.mark.asyncio
    async def test_get_agent_workload(self, service):
        """Test getting agent workload metrics."""
        agent = Mock(id="agent-1", name="Test Agent")
        service.agents.get_by_id = AsyncMock(return_value=agent)

        # High workload events
        events = [Mock(created_at=datetime.utcnow() - timedelta(minutes=i))
                 for i in range(50)]
        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute
        workload = await service.get_agent_workload("agent-1")

        # Assert
        assert workload["agent_id"] == "agent-1"
        assert workload["workload"] in ["Heavy", "Moderate", "Light", "Idle"]

    @pytest.mark.asyncio
    async def test_recommend_agent_assignment(self, service):
        """Test agent recommendation for task assignment."""
        # Setup team with varying workloads
        agents = [
            Mock(id="agent-1", name="Busy Agent"),
            Mock(id="agent-2", name="Available Agent"),
        ]
        service.agents.get_by_project = AsyncMock(return_value=agents)

        # Mock team stats
        async def mock_team_perf(project_id):
            return {
                "agents": [
                    {"agent_id": "agent-1", "agent_name": "Busy Agent", "events_per_hour": 10.0},
                    {"agent_id": "agent-2", "agent_name": "Available Agent", "events_per_hour": 2.0},
                ]
            }

        service.get_team_performance = mock_team_perf

        # Execute
        recommendation = await service.recommend_agent_assignment("proj-1")

        # Assert
        assert recommendation["recommended_agent_id"] == "agent-2"
        assert recommendation["agent_name"] == "Available Agent"

    @pytest.mark.asyncio
    async def test_recommend_agent_no_agents(self, service):
        """Test recommendation when no agents available."""
        service.agents.get_by_project = AsyncMock(return_value=[])

        async def mock_team_perf(project_id):
            return {"agents": []}

        service.get_team_performance = mock_team_perf

        recommendation = await service.recommend_agent_assignment("proj-1")

        assert "error" in recommendation


class TestAgentMonitoringService:
    """Test AgentMonitoringService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.query.return_value.filter.return_value.all.return_value = []
        return AgentMonitoringService(session)

    def test_check_agent_health_healthy(self, service):
        """Test checking health of healthy agent."""
        agent = Mock(spec=["id", "name", "status", "last_activity_at"])
        agent.id = "agent-1"
        agent.name = "Test Agent"
        agent.status = "active"
        agent.last_activity_at = datetime.utcnow().isoformat()

        # For agent_id query path
        service.session.query.return_value.filter.return_value.first.return_value = agent

        # Execute
        health = service.check_agent_health("proj-1", "agent-1")

        # Assert
        assert len(health) == 1
        assert health[0]["agent_id"] == "agent-1"
        assert health[0]["health"] == "healthy"
        assert health[0]["health_status"] == "ok"

    def test_check_agent_health_idle(self, service):
        """Test idle agent detection."""
        agent = Mock(spec=["id", "name", "status", "last_activity_at"])
        agent.id = "agent-1"
        agent.name = "Idle Agent"
        agent.status = "active"
        # Last activity 12 hours ago
        agent.last_activity_at = (datetime.utcnow() - timedelta(hours=12)).isoformat()

        service.session.query.return_value.filter.return_value.first.return_value = agent

        # Execute
        health = service.check_agent_health("proj-1", "agent-1")

        # Assert
        assert health[0]["health"] == "idle"
        assert health[0]["health_status"] == "warning"

    def test_check_agent_health_stale(self, service):
        """Test stale agent detection."""
        agent = Mock(spec=["id", "name", "status", "last_activity_at"])
        agent.id = "agent-1"
        agent.name = "Stale Agent"
        agent.status = "active"
        # Last activity 48 hours ago
        agent.last_activity_at = (datetime.utcnow() - timedelta(hours=48)).isoformat()

        service.session.query.return_value.filter.return_value.first.return_value = agent

        # Execute
        health = service.check_agent_health("proj-1", "agent-1", stale_threshold_hours=24)

        # Assert
        assert health[0]["health"] == "stale"
        assert health[0]["health_status"] == "error"

    def test_check_agent_health_no_activity(self, service):
        """Test agent with no activity."""
        agent = Mock(spec=["id", "name", "status", "last_activity_at"])
        agent.id = "agent-1"
        agent.name = "New Agent"
        agent.status = "active"
        agent.last_activity_at = None

        service.session.query.return_value.filter.return_value.first.return_value = agent

        # Execute
        health = service.check_agent_health("proj-1", "agent-1")

        # Assert
        assert health[0]["health"] == "no_activity"
        assert health[0]["health_status"] == "warning"

    def test_get_alerts_stale_agents(self, service):
        """Test getting stale agent alerts."""
        agent = Mock()
        agent.id = "agent-1"
        agent.name = "Stale Agent"
        agent.last_activity_at = (datetime.utcnow() - timedelta(hours=48)).isoformat()
        agent.status = "active"

        service.session.query.return_value.filter.return_value.all.return_value = [agent]

        # Execute
        alerts = service.get_alerts("proj-1", alert_types=["stale"])

        # Assert
        assert len(alerts) > 0
        assert alerts[0]["type"] == "stale_agent"
        assert alerts[0]["severity"] == "warning"

    def test_get_alerts_high_conflict_rate(self, service):
        """Test high conflict rate alerts."""
        # AgentMetricsService is imported inside the function, so we need to patch the import location
        mock_instance = Mock()
        mock_instance.calculate_metrics.return_value = {
            "metrics": [
                {"agent_id": "agent-1", "agent_name": "Agent 1", "conflict_rate": 15.0}
            ]
        }

        with patch("tracertm.services.agent_metrics_service.AgentMetricsService", return_value=mock_instance):
            service.session.query.return_value.filter.return_value.all.return_value = []

            # Execute
            alerts = service.get_alerts("proj-1", alert_types=["high_conflict_rate"])

            # Assert
            assert len(alerts) > 0
            assert alerts[0]["type"] == "high_conflict_rate"


class TestAgentCoordinationService:
    """Test AgentCoordinationService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = AsyncMock()
        service = AgentCoordinationService(session)
        service.agents = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_register_agent(self, service):
        """Test registering a new agent."""
        agent = Mock(id="agent-1", name="Test Agent")
        service.agents.create = AsyncMock(return_value=agent)
        service.events.log = AsyncMock()

        # Execute
        result = await service.register_agent(
            project_id="proj-1",
            name="Test Agent",
            agent_type="developer",
            metadata={"skill": "python"},
        )

        # Assert
        assert result.id == "agent-1"
        service.agents.create.assert_called_once()
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_conflicts_concurrent_activity(self, service):
        """Test detecting conflicts from concurrent activity."""
        # Setup agents with concurrent activity
        now = datetime.utcnow()
        agent1 = Mock(
            id="agent-1",
            name="Agent 1",
            last_activity_at=(now - timedelta(seconds=30)).isoformat(),
        )
        agent2 = Mock(
            id="agent-2",
            name="Agent 2",
            last_activity_at=now.isoformat(),
        )

        service.agents.get_by_project = AsyncMock(return_value=[agent1, agent2])

        # Execute
        conflicts = await service.detect_conflicts("proj-1")

        # Assert
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == "concurrent_activity"

    @pytest.mark.asyncio
    async def test_detect_conflicts_no_conflicts(self, service):
        """Test when no conflicts exist."""
        agent1 = Mock(
            id="agent-1",
            name="Agent 1",
            last_activity_at=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
        )
        agent2 = Mock(
            id="agent-2",
            name="Agent 2",
            last_activity_at=datetime.utcnow().isoformat(),
        )

        service.agents.get_by_project = AsyncMock(return_value=[agent1, agent2])

        # Execute
        conflicts = await service.detect_conflicts("proj-1")

        # Assert
        assert len(conflicts) == 0

    @pytest.mark.asyncio
    async def test_resolve_conflict_last_write_wins(self, service):
        """Test conflict resolution with last_write_wins strategy."""
        # Setup agents
        now = datetime.utcnow()
        agent1 = Mock(
            id="agent-1",
            last_activity_at=(now - timedelta(minutes=5)).isoformat(),
        )
        agent2 = Mock(
            id="agent-2",
            last_activity_at=now.isoformat(),
        )

        service.agents.get_by_id = AsyncMock(side_effect=[agent1, agent2])
        service.events.log = AsyncMock()

        # Create conflict
        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="concurrent_write",
            entity_id="item-1",
            description="Both agents modified item-1",
        )

        # Execute
        resolution = await service.resolve_conflict(
            "proj-1",
            conflict,
            strategy="last_write_wins",
        )

        # Assert
        assert resolution.resolved is True
        assert resolution.winner_agent_id == "agent-2"  # Most recent
        assert resolution.loser_agent_id == "agent-1"
        assert resolution.resolution_strategy == "last_write_wins"

    @pytest.mark.asyncio
    async def test_resolve_conflict_priority_based(self, service):
        """Test conflict resolution with priority_based strategy."""
        agent1 = Mock(id="agent-1", last_activity_at=datetime.utcnow().isoformat())
        agent2 = Mock(id="agent-2", last_activity_at=datetime.utcnow().isoformat())

        service.agents.get_by_id = AsyncMock(side_effect=[agent1, agent2])
        service.events.log = AsyncMock()

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="resource_conflict",
            entity_id="item-1",
            description="Resource conflict",
        )

        # Execute
        resolution = await service.resolve_conflict(
            "proj-1",
            conflict,
            strategy="priority_based",
        )

        # Assert
        assert resolution.resolved is True
        assert resolution.resolution_strategy == "priority_based"

    @pytest.mark.asyncio
    async def test_resolve_conflict_invalid_strategy(self, service):
        """Test error on invalid resolution strategy."""
        agent1 = Mock(id="agent-1", last_activity_at=datetime.utcnow().isoformat())
        agent2 = Mock(id="agent-2", last_activity_at=datetime.utcnow().isoformat())

        service.agents.get_by_id = AsyncMock(side_effect=[agent1, agent2])

        conflict = AgentConflict(
            agent1_id="agent-1",
            agent2_id="agent-2",
            conflict_type="conflict",
            entity_id="item-1",
            description="Test",
        )

        # Execute & Assert
        with pytest.raises(ValueError, match="Unknown resolution strategy"):
            await service.resolve_conflict("proj-1", conflict, strategy="invalid")

    @pytest.mark.asyncio
    async def test_get_agent_activity(self, service):
        """Test getting agent activity history."""
        events = [
            Mock(
                event_type="item_created",
                entity_type="item",
                entity_id="item-1",
                created_at=datetime.utcnow(),
                data={"action": "create"},
            )
            for _ in range(5)
        ]
        service.events.get_by_agent = AsyncMock(return_value=events)

        # Execute
        activity = await service.get_agent_activity("agent-1", limit=100)

        # Assert
        assert len(activity) == 5
        assert activity[0]["event_type"] == "item_created"


class TestAgentMetricsService:
    """Test AgentMetricsService."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        return AgentMetricsService(session)

    def test_calculate_metrics_single_agent(self, service):
        """Test calculating metrics for single agent."""
        # Setup agent
        agent = Mock(spec=["id", "name"])
        agent.id = "agent-1"
        agent.name = "Test Agent"

        # Setup events
        events = []
        for i in range(10):
            event = Mock(spec=["event_type", "data", "created_at", "agent_id"])
            event.event_type = "item_created" if i < 8 else "conflict_detected"
            event.data = {}
            event.created_at = datetime.utcnow()
            event.agent_id = "agent-1"
            events.append(event)

        # Create a chainable mock for the query
        query_chain = Mock()
        query_chain.filter.return_value = query_chain
        query_chain.all.return_value = events
        query_chain.first.return_value = agent

        service.session.query.return_value = query_chain

        # Execute
        metrics = service.calculate_metrics("proj-1", agent_id="agent-1")

        # Assert
        assert len(metrics["metrics"]) == 1
        assert metrics["metrics"][0]["total_operations"] == 10
        assert metrics["metrics"][0]["conflicts"] == 2
        assert metrics["metrics"][0]["success_rate"] == 80.0

    def test_calculate_metrics_all_agents(self, service):
        """Test calculating metrics for all agents."""
        # Setup agents
        agent1 = Mock(spec=["id", "name"])
        agent1.id = "agent-1"
        agent1.name = "Agent 1"

        # Setup events
        events = [Mock(spec=["event_type", "data", "created_at", "agent_id"])]
        events[0].event_type = "item_created"
        events[0].data = {}
        events[0].created_at = datetime.utcnow()
        events[0].agent_id = "agent-1"

        # Create chainable mock
        query_chain = Mock()
        query_chain.filter.return_value = query_chain
        query_chain.all.side_effect = [[agent1], events]  # First call returns agents, second returns events
        query_chain.first.return_value = agent1

        service.session.query.return_value = query_chain

        # Execute
        metrics = service.calculate_metrics("proj-1")

        # Assert - should have metrics for agents with events
        assert "metrics" in metrics

    def test_get_agent_workload(self, service):
        """Test getting agent workload."""
        # Setup items owned by agent
        items = [
            Mock(status="todo"),
            Mock(status="todo"),
            Mock(status="in_progress"),
            Mock(status="done"),
        ]

        query_mock = Mock()
        query_mock.filter.return_value.all.return_value = items
        service.session.query.return_value = query_mock

        # Execute
        workload = service.get_agent_workload("proj-1", "agent-1")

        # Assert
        assert workload["total_items"] == 4
        assert workload["by_status"]["todo"] == 2
        assert workload["by_status"]["in_progress"] == 1
        assert workload["by_status"]["done"] == 1
