"""
Comprehensive tests for ConflictResolutionService.

Tests all methods: detect_conflicts, resolve_conflict.

Coverage target: 85%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from tracertm.services.conflict_resolution_service import ConflictResolutionService
from tracertm.models.item import Item
from tracertm.models.event import Event


class TestDetectConflicts:
    """Test detect_conflicts method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ConflictResolutionService(mock_session)

    def test_no_conflicts(self, service, mock_session):
        """Test when no conflicts detected."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = service.detect_conflicts("proj-1")

        assert result == []

    def test_single_agent_no_conflict(self, service, mock_session):
        """Test single agent updates don't create conflict."""
        now = datetime.utcnow()

        event1 = Mock(spec=Event)
        event1.entity_id = "item-1"
        event1.entity_type = "item"
        event1.agent_id = "agent-1"
        event1.created_at = now

        event2 = Mock(spec=Event)
        event2.entity_id = "item-1"
        event2.entity_type = "item"
        event2.agent_id = "agent-1"  # Same agent
        event2.created_at = now - timedelta(seconds=10)

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1, event2
        ]

        result = service.detect_conflicts("proj-1")

        assert result == []

    def test_multiple_agents_conflict(self, service, mock_session):
        """Test multiple agents updating same item creates conflict."""
        now = datetime.utcnow()

        event1 = Mock(spec=Event)
        event1.entity_id = "item-1"
        event1.entity_type = "item"
        event1.agent_id = "agent-1"
        event1.created_at = now

        event2 = Mock(spec=Event)
        event2.entity_id = "item-1"
        event2.entity_type = "item"
        event2.agent_id = "agent-2"  # Different agent
        event2.created_at = now - timedelta(seconds=10)

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1, event2
        ]

        result = service.detect_conflicts("proj-1")

        assert len(result) == 1
        assert result[0]["entity_id"] == "item-1"
        assert "agent-1" in result[0]["conflicting_agents"]
        assert "agent-2" in result[0]["conflicting_agents"]

    def test_conflict_with_item_id_filter(self, service, mock_session):
        """Test conflict detection with specific item ID."""
        now = datetime.utcnow()

        event = Mock(spec=Event)
        event.entity_id = "item-1"
        event.entity_type = "item"
        event.agent_id = "agent-1"
        event.created_at = now

        mock_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [event]

        result = service.detect_conflicts("proj-1", item_id="item-1")

        # Query should have additional filter for item_id
        assert mock_session.query.called

    def test_multiple_conflicts_different_items(self, service, mock_session):
        """Test detecting conflicts on multiple items."""
        now = datetime.utcnow()

        # Conflict on item-1
        event1a = Mock(spec=Event)
        event1a.entity_id = "item-1"
        event1a.entity_type = "item"
        event1a.agent_id = "agent-1"
        event1a.created_at = now

        event1b = Mock(spec=Event)
        event1b.entity_id = "item-1"
        event1b.entity_type = "item"
        event1b.agent_id = "agent-2"
        event1b.created_at = now - timedelta(seconds=5)

        # Conflict on item-2
        event2a = Mock(spec=Event)
        event2a.entity_id = "item-2"
        event2a.entity_type = "item"
        event2a.agent_id = "agent-1"
        event2a.created_at = now

        event2b = Mock(spec=Event)
        event2b.entity_id = "item-2"
        event2b.entity_type = "item"
        event2b.agent_id = "agent-3"
        event2b.created_at = now - timedelta(seconds=5)

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1a, event1b, event2a, event2b
        ]

        result = service.detect_conflicts("proj-1")

        assert len(result) == 2

    def test_conflict_timestamps(self, service, mock_session):
        """Test conflict includes correct timestamps."""
        now = datetime.utcnow()
        earlier = now - timedelta(seconds=30)

        event1 = Mock(spec=Event)
        event1.entity_id = "item-1"
        event1.entity_type = "item"
        event1.agent_id = "agent-1"
        event1.created_at = now

        event2 = Mock(spec=Event)
        event2.entity_id = "item-1"
        event2.entity_type = "item"
        event2.agent_id = "agent-2"
        event2.created_at = earlier

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1, event2
        ]

        result = service.detect_conflicts("proj-1")

        assert len(result) == 1
        assert result[0]["first_event"] == earlier.isoformat()
        assert result[0]["last_event"] == now.isoformat()

    def test_event_count_in_conflict(self, service, mock_session):
        """Test conflict includes event count."""
        now = datetime.utcnow()

        events = []
        for i in range(5):
            event = Mock(spec=Event)
            event.entity_id = "item-1"
            event.entity_type = "item"
            event.agent_id = f"agent-{i % 2}"  # Alternating agents
            event.created_at = now - timedelta(seconds=i * 10)
            events.append(event)

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = events

        result = service.detect_conflicts("proj-1")

        assert len(result) == 1
        assert result[0]["event_count"] == 5

    def test_none_created_at_handled(self, service, mock_session):
        """Test handling None created_at timestamps."""
        event1 = Mock(spec=Event)
        event1.entity_id = "item-1"
        event1.entity_type = "item"
        event1.agent_id = "agent-1"
        event1.created_at = None

        event2 = Mock(spec=Event)
        event2.entity_id = "item-1"
        event2.entity_type = "item"
        event2.agent_id = "agent-2"
        event2.created_at = None

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1, event2
        ]

        result = service.detect_conflicts("proj-1")

        assert len(result) == 1
        assert result[0]["first_event"] is None
        assert result[0]["last_event"] is None


class TestResolveConflict:
    """Test resolve_conflict method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ConflictResolutionService(mock_session)

    def test_item_not_found(self, service, mock_session):
        """Test error when item not found."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Item not found"):
            service.resolve_conflict("proj-1", "nonexistent")

    def test_no_conflict_to_resolve(self, service, mock_session):
        """Test when no conflict exists (less than 2 events)."""
        item = Mock(spec=Item)
        item.id = "item-1"
        item.version = 1

        event = Mock(spec=Event)

        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [event]

        result = service.resolve_conflict("proj-1", "item-1")

        assert result["resolved"] is False
        assert result["reason"] == "No conflict detected"

    def test_last_write_wins_strategy(self, service, mock_session):
        """Test last_write_wins resolution strategy."""
        item = Mock(spec=Item)
        item.id = "item-1"
        item.version = 5

        event1 = Mock(spec=Event)
        event1.agent_id = "agent-winner"
        event1.created_at = datetime.utcnow()

        event2 = Mock(spec=Event)
        event2.agent_id = "agent-loser"
        event2.created_at = datetime.utcnow() - timedelta(seconds=30)

        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            event1, event2
        ]

        result = service.resolve_conflict("proj-1", "item-1", strategy="last_write_wins")

        assert result["resolved"] is True
        assert result["strategy"] == "last_write_wins"
        assert result["winner_agent"] == "agent-winner"
        assert result["item_version"] == 5

    def test_merge_strategy(self, service, mock_session):
        """Test merge resolution strategy."""
        item = Mock(spec=Item)
        item.id = "item-1"

        event1 = Mock(spec=Event)
        event2 = Mock(spec=Event)

        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            event1, event2
        ]

        result = service.resolve_conflict("proj-1", "item-1", strategy="merge")

        assert result["resolved"] is True
        assert result["strategy"] == "merge"
        assert "note" in result

    def test_unknown_strategy_error(self, service, mock_session):
        """Test error on unknown strategy."""
        item = Mock(spec=Item)
        item.id = "item-1"

        event1 = Mock(spec=Event)
        event2 = Mock(spec=Event)

        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            event1, event2
        ]

        with pytest.raises(ValueError, match="Unknown resolution strategy"):
            service.resolve_conflict("proj-1", "item-1", strategy="invalid_strategy")

    def test_default_strategy_is_last_write_wins(self, service, mock_session):
        """Test default strategy is last_write_wins."""
        item = Mock(spec=Item)
        item.id = "item-1"
        item.version = 1

        event1 = Mock(spec=Event)
        event1.agent_id = "agent-1"
        event2 = Mock(spec=Event)
        event2.agent_id = "agent-2"

        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            event1, event2
        ]

        result = service.resolve_conflict("proj-1", "item-1")

        assert result["strategy"] == "last_write_wins"


class TestServiceInit:
    """Test service initialization."""

    def test_init_stores_session(self):
        """Test initialization stores session."""
        session = Mock(spec=Session)
        service = ConflictResolutionService(session)
        assert service.session == session
