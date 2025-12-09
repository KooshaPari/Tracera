"""
Comprehensive tests for EventSourcingService.

Tests all methods: get_audit_trail, replay_events, _apply_event,
get_event_history, get_changes_between.

Coverage target: 85%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import asdict

from tracertm.services.event_sourcing_service import (
    EventSourcingService,
    AuditTrailEntry,
    ReplayResult,
)
from tracertm.models.event import Event


class TestAuditTrailEntry:
    """Test AuditTrailEntry dataclass."""

    def test_audit_trail_entry_fields(self):
        """Test AuditTrailEntry has correct fields."""
        entry = AuditTrailEntry(
            timestamp="2024-01-01T12:00:00",
            event_type="item_created",
            entity_type="item",
            entity_id="item-1",
            agent_id="agent-1",
            data={"title": "Test"},
        )
        assert entry.timestamp == "2024-01-01T12:00:00"
        assert entry.event_type == "item_created"
        assert entry.entity_id == "item-1"
        assert entry.agent_id == "agent-1"

    def test_audit_trail_entry_no_agent(self):
        """Test AuditTrailEntry with no agent."""
        entry = AuditTrailEntry(
            timestamp="2024-01-01T12:00:00",
            event_type="item_updated",
            entity_type="item",
            entity_id="item-1",
            agent_id=None,
            data={},
        )
        assert entry.agent_id is None


class TestReplayResult:
    """Test ReplayResult dataclass."""

    def test_replay_result_fields(self):
        """Test ReplayResult has correct fields."""
        result = ReplayResult(
            total_events=10,
            replayed_events=9,
            failed_events=1,
            final_state={"id": "item-1", "status": "done"},
        )
        assert result.total_events == 10
        assert result.replayed_events == 9
        assert result.failed_events == 1
        assert result.final_state["status"] == "done"


class TestGetAuditTrail:
    """Test get_audit_trail method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = EventSourcingService(session)
        service.events = AsyncMock()
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_audit_trail_for_project(self, service):
        """Test getting audit trail for entire project."""
        now = datetime.utcnow()
        event = Mock()
        event.created_at = now
        event.event_type = "item_created"
        event.entity_type = "item"
        event.entity_id = "item-1"
        event.agent_id = "agent-1"
        event.data = {"title": "New Item"}

        service.events.get_by_project = AsyncMock(return_value=[event])

        result = await service.get_audit_trail("proj-1")

        assert len(result) == 1
        assert result[0].event_type == "item_created"
        assert result[0].entity_id == "item-1"

    @pytest.mark.asyncio
    async def test_get_audit_trail_for_entity(self, service):
        """Test getting audit trail for specific entity."""
        now = datetime.utcnow()
        event = Mock()
        event.created_at = now
        event.event_type = "item_updated"
        event.entity_type = "item"
        event.entity_id = "item-1"
        event.agent_id = None
        event.data = {"status": "done"}

        service.events.get_by_entity = AsyncMock(return_value=[event])

        result = await service.get_audit_trail("proj-1", entity_id="item-1")

        assert len(result) == 1
        service.events.get_by_entity.assert_called_once_with("item-1")

    @pytest.mark.asyncio
    async def test_get_audit_trail_with_limit(self, service):
        """Test audit trail respects limit."""
        events = []
        for i in range(10):
            event = Mock()
            event.created_at = datetime.utcnow()
            event.event_type = "item_updated"
            event.entity_type = "item"
            event.entity_id = f"item-{i}"
            event.agent_id = None
            event.data = {}
            events.append(event)

        service.events.get_by_project = AsyncMock(return_value=events[:5])

        result = await service.get_audit_trail("proj-1", limit=5)

        service.events.get_by_project.assert_called_with("proj-1", limit=5)

    @pytest.mark.asyncio
    async def test_get_audit_trail_empty(self, service):
        """Test empty audit trail."""
        service.events.get_by_project = AsyncMock(return_value=[])

        result = await service.get_audit_trail("proj-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_audit_trail_handles_string_timestamp(self, service):
        """Test handling timestamps without isoformat method."""
        event = Mock(spec=["event_type", "entity_type", "entity_id", "agent_id", "data", "created_at"])
        event.created_at = "2024-01-01T12:00:00"  # String, not datetime
        event.event_type = "item_created"
        event.entity_type = "item"
        event.entity_id = "item-1"
        event.agent_id = None
        event.data = {}

        service.events.get_by_project = AsyncMock(return_value=[event])

        result = await service.get_audit_trail("proj-1")

        assert len(result) == 1
        # String timestamp should be converted via str()
        assert result[0].timestamp == "2024-01-01T12:00:00"


class TestReplayEvents:
    """Test replay_events method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = EventSourcingService(session)
        service.events = AsyncMock()
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_replay_empty_events(self, service):
        """Test replay with no events."""
        service.events.get_by_entity = AsyncMock(return_value=[])

        result = await service.replay_events("proj-1", "item-1")

        assert result.total_events == 0
        assert result.replayed_events == 0
        assert result.failed_events == 0
        assert result.final_state == {}

    @pytest.mark.asyncio
    async def test_replay_item_created(self, service):
        """Test replay with item_created event."""
        event = Mock()
        event.id = "event-1"
        event.created_at = datetime.utcnow().isoformat()
        event.event_type = "item_created"
        event.entity_id = "item-1"
        event.data = {"title": "New Item"}

        service.events.get_by_entity = AsyncMock(return_value=[event])

        result = await service.replay_events("proj-1", "item-1")

        assert result.total_events == 1
        assert result.replayed_events == 1
        assert result.final_state["id"] == "item-1"
        assert result.final_state["title"] == "New Item"
        assert result.final_state["status"] == "created"

    @pytest.mark.asyncio
    async def test_replay_item_updated(self, service):
        """Test replay with item_updated event."""
        event = Mock()
        event.id = "event-1"
        event.created_at = datetime.utcnow().isoformat()
        event.event_type = "item_updated"
        event.entity_id = "item-1"
        event.data = {"status": "done", "priority": "high"}

        service.events.get_by_entity = AsyncMock(return_value=[event])

        result = await service.replay_events("proj-1", "item-1")

        assert result.final_state["status"] == "done"
        assert result.final_state["priority"] == "high"
        assert result.final_state["version"] == 2

    @pytest.mark.asyncio
    async def test_replay_item_deleted(self, service):
        """Test replay with item_deleted event."""
        event = Mock()
        event.id = "event-1"
        event.created_at = datetime.utcnow().isoformat()
        event.event_type = "item_deleted"
        event.entity_id = "item-1"
        event.data = {"deleted_at": "2024-01-01T12:00:00"}

        service.events.get_by_entity = AsyncMock(return_value=[event])

        result = await service.replay_events("proj-1", "item-1")

        assert result.final_state["deleted"] is True
        assert result.final_state["deleted_at"] == "2024-01-01T12:00:00"

    @pytest.mark.asyncio
    async def test_replay_link_created(self, service):
        """Test replay with link_created event."""
        event = Mock()
        event.id = "event-1"
        event.created_at = datetime.utcnow().isoformat()
        event.event_type = "link_created"
        event.entity_id = "item-1"
        event.data = {"target_item_id": "item-2", "link_type": "depends_on"}

        service.events.get_by_entity = AsyncMock(return_value=[event])

        result = await service.replay_events("proj-1", "item-1")

        assert "links" in result.final_state
        assert len(result.final_state["links"]) == 1
        assert result.final_state["links"][0]["target_id"] == "item-2"

    @pytest.mark.asyncio
    async def test_replay_multiple_events(self, service):
        """Test replay with multiple events."""
        event1 = Mock()
        event1.id = "event-1"
        event1.created_at = datetime.utcnow().isoformat()
        event1.event_type = "item_created"
        event1.entity_id = "item-1"
        event1.data = {"title": "Item"}

        event2 = Mock()
        event2.id = "event-2"
        event2.created_at = (datetime.utcnow() + timedelta(minutes=1)).isoformat()
        event2.event_type = "item_updated"
        event2.entity_id = "item-1"
        event2.data = {"status": "in_progress"}

        service.events.get_by_entity = AsyncMock(return_value=[event1, event2])

        result = await service.replay_events("proj-1", "item-1")

        assert result.total_events == 2
        assert result.replayed_events == 2
        assert result.final_state["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_replay_with_timestamp_filter(self, service):
        """Test replay with timestamp filter."""
        now = datetime.utcnow()
        past_event = Mock()
        past_event.id = "event-1"
        past_event.created_at = (now - timedelta(hours=2)).isoformat()
        past_event.event_type = "item_created"
        past_event.entity_id = "item-1"
        past_event.data = {"title": "Item"}

        future_event = Mock()
        future_event.id = "event-2"
        future_event.created_at = (now + timedelta(hours=2)).isoformat()
        future_event.event_type = "item_updated"
        future_event.entity_id = "item-1"
        future_event.data = {"status": "done"}

        service.events.get_by_entity = AsyncMock(return_value=[past_event, future_event])

        result = await service.replay_events(
            "proj-1", "item-1", up_to_timestamp=now.isoformat()
        )

        # Only past_event should be replayed
        assert result.total_events == 1
        assert result.replayed_events == 1


class TestGetEventHistory:
    """Test get_event_history method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = EventSourcingService(session)
        service.events = AsyncMock()
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_all_events(self, service):
        """Test getting all events for entity."""
        event1 = Mock(event_type="item_created")
        event2 = Mock(event_type="item_updated")

        service.events.get_by_entity = AsyncMock(return_value=[event1, event2])

        result = await service.get_event_history("item-1")

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_filter_by_event_type(self, service):
        """Test filtering by event type."""
        event1 = Mock(event_type="item_created")
        event2 = Mock(event_type="item_updated")
        event3 = Mock(event_type="item_updated")

        service.events.get_by_entity = AsyncMock(return_value=[event1, event2, event3])

        result = await service.get_event_history("item-1", event_type="item_updated")

        assert len(result) == 2
        assert all(e.event_type == "item_updated" for e in result)

    @pytest.mark.asyncio
    async def test_empty_history(self, service):
        """Test empty event history."""
        service.events.get_by_entity = AsyncMock(return_value=[])

        result = await service.get_event_history("item-1")

        assert result == []


class TestGetChangesBetween:
    """Test get_changes_between method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        service = EventSourcingService(session)
        service.events = AsyncMock()
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_changes_in_range(self, service):
        """Test getting changes within time range."""
        now = datetime.utcnow()
        event = Mock()
        event.created_at = now.isoformat()
        event.event_type = "item_updated"
        event.entity_type = "item"
        event.entity_id = "item-1"
        event.agent_id = "agent-1"
        event.data = {"status": "done"}

        service.events.get_by_entity = AsyncMock(return_value=[event])

        start = (now - timedelta(hours=1)).isoformat()
        end = (now + timedelta(hours=1)).isoformat()

        result = await service.get_changes_between("item-1", start, end)

        assert len(result) == 1
        assert result[0].event_type == "item_updated"

    @pytest.mark.asyncio
    async def test_get_changes_excludes_outside_range(self, service):
        """Test changes outside range are excluded."""
        now = datetime.utcnow()
        old_event = Mock()
        old_event.created_at = (now - timedelta(days=10)).isoformat()
        old_event.event_type = "item_created"
        old_event.entity_type = "item"
        old_event.entity_id = "item-1"
        old_event.agent_id = None
        old_event.data = {}

        service.events.get_by_entity = AsyncMock(return_value=[old_event])

        start = (now - timedelta(hours=1)).isoformat()
        end = now.isoformat()

        result = await service.get_changes_between("item-1", start, end)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_changes_empty(self, service):
        """Test no changes in range."""
        service.events.get_by_entity = AsyncMock(return_value=[])

        now = datetime.utcnow()
        result = await service.get_changes_between(
            "item-1",
            (now - timedelta(hours=1)).isoformat(),
            now.isoformat(),
        )

        assert result == []


class TestApplyEvent:
    """Test _apply_event method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return EventSourcingService(session)

    @pytest.mark.asyncio
    async def test_apply_unknown_event_type(self, service):
        """Test applying unknown event type doesn't change state."""
        event = Mock()
        event.event_type = "unknown_type"
        event.entity_id = "item-1"
        event.data = {"foo": "bar"}

        initial_state = {"existing": "data"}
        result = await service._apply_event(initial_state.copy(), event)

        assert result == {"existing": "data"}

    @pytest.mark.asyncio
    async def test_apply_multiple_links(self, service):
        """Test applying multiple link_created events."""
        event1 = Mock()
        event1.event_type = "link_created"
        event1.data = {"target_item_id": "item-2", "link_type": "depends_on"}

        event2 = Mock()
        event2.event_type = "link_created"
        event2.data = {"target_item_id": "item-3", "link_type": "relates_to"}

        state = {}
        state = await service._apply_event(state, event1)
        state = await service._apply_event(state, event2)

        assert len(state["links"]) == 2


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_repositories(self):
        """Test initialization creates repositories."""
        session = AsyncMock()
        service = EventSourcingService(session)

        assert service.session == session
        assert service.events is not None
        assert service.items is not None
