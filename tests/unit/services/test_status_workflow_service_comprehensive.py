"""
Comprehensive tests for StatusWorkflowService.

Tests all methods: validate_transition, update_item_status, get_status_history.

Coverage target: 85%+
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from tracertm.services.status_workflow_service import (
    StatusWorkflowService,
    VALID_STATUSES,
    STATUS_TRANSITIONS,
    STATUS_PROGRESS,
)
from tracertm.models.item import Item
from tracertm.models.event import Event


class TestValidateTransition:
    """Test validate_transition method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = Mock(spec=Session)
        return StatusWorkflowService(session)

    def test_valid_todo_to_in_progress(self, service):
        """Test valid transition from todo to in_progress."""
        assert service.validate_transition("todo", "in_progress") is True

    def test_valid_todo_to_blocked(self, service):
        """Test valid transition from todo to blocked."""
        assert service.validate_transition("todo", "blocked") is True

    def test_valid_in_progress_to_done(self, service):
        """Test valid transition from in_progress to done."""
        assert service.validate_transition("in_progress", "done") is True

    def test_valid_in_progress_to_blocked(self, service):
        """Test valid transition from in_progress to blocked."""
        assert service.validate_transition("in_progress", "blocked") is True

    def test_valid_in_progress_to_todo(self, service):
        """Test valid transition from in_progress to todo."""
        assert service.validate_transition("in_progress", "todo") is True

    def test_valid_blocked_to_todo(self, service):
        """Test valid transition from blocked to todo."""
        assert service.validate_transition("blocked", "todo") is True

    def test_valid_blocked_to_in_progress(self, service):
        """Test valid transition from blocked to in_progress."""
        assert service.validate_transition("blocked", "in_progress") is True

    def test_valid_done_to_todo(self, service):
        """Test valid transition from done to todo (reopening)."""
        assert service.validate_transition("done", "todo") is True

    def test_invalid_todo_to_done(self, service):
        """Test invalid transition from todo directly to done."""
        assert service.validate_transition("todo", "done") is False

    def test_invalid_archived_transition(self, service):
        """Test that archived is terminal state."""
        assert service.validate_transition("archived", "todo") is False
        assert service.validate_transition("archived", "in_progress") is False

    def test_invalid_new_status(self, service):
        """Test invalid new status value."""
        assert service.validate_transition("todo", "invalid_status") is False

    def test_invalid_current_status(self, service):
        """Test invalid current status value."""
        assert service.validate_transition("unknown_status", "todo") is False


class TestUpdateItemStatus:
    """Test update_item_status method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return StatusWorkflowService(mock_session)

    def test_update_status_success(self, service, mock_session):
        """Test successful status update."""
        item = Mock()
        item.id = "item-1"
        item.project_id = "proj-1"
        item.title = "Test Item"
        item.status = "todo"

        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.update_item_status("item-1", "in_progress")

        assert result["item_id"] == "item-1"
        assert result["old_status"] == "todo"
        assert result["new_status"] == "in_progress"
        assert result["progress"] == 50  # in_progress = 50%
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_status_with_agent(self, service, mock_session):
        """Test status update with agent ID."""
        item = Mock()
        item.id = "item-1"
        item.project_id = "proj-1"
        item.title = "Test Item"
        item.status = "in_progress"

        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.update_item_status("item-1", "done", agent_id="agent-1")

        assert result["new_status"] == "done"
        assert result["progress"] == 100

    def test_update_status_item_not_found(self, service, mock_session):
        """Test error when item not found."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Item not found"):
            service.update_item_status("nonexistent", "in_progress")

    def test_update_status_invalid_transition(self, service, mock_session):
        """Test error on invalid transition."""
        item = Mock()
        item.id = "item-1"
        item.status = "todo"

        mock_session.query.return_value.filter.return_value.first.return_value = item

        with pytest.raises(ValueError, match="Invalid status transition"):
            service.update_item_status("item-1", "done")  # Can't go from todo to done

    def test_update_status_none_to_in_progress(self, service, mock_session):
        """Test status update when current status is None (defaults to todo)."""
        item = Mock()
        item.id = "item-1"
        item.project_id = "proj-1"
        item.title = "New Item"
        item.status = None  # None status

        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.update_item_status("item-1", "in_progress")

        # None defaults to "todo", so transition to in_progress is valid
        assert result["old_status"] is None
        assert result["new_status"] == "in_progress"

    def test_update_status_to_blocked(self, service, mock_session):
        """Test update to blocked status."""
        item = Mock()
        item.id = "item-1"
        item.project_id = "proj-1"
        item.title = "Blocked Item"
        item.status = "in_progress"

        mock_session.query.return_value.filter.return_value.first.return_value = item

        result = service.update_item_status("item-1", "blocked")

        assert result["new_status"] == "blocked"
        assert result["progress"] == 0  # blocked = 0%


class TestGetStatusHistory:
    """Test get_status_history method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return StatusWorkflowService(mock_session)

    def test_get_history_empty(self, service, mock_session):
        """Test getting history with no events."""
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = service.get_status_history("item-1")

        assert result == []

    def test_get_history_with_events(self, service, mock_session):
        """Test getting history with events."""
        now = datetime.utcnow()
        event1 = Mock()
        event1.created_at = now
        event1.data = {"old_status": "todo", "new_status": "in_progress"}
        event1.agent_id = "agent-1"

        event2 = Mock()
        event2.created_at = now
        event2.data = {"old_status": "in_progress", "new_status": "done"}
        event2.agent_id = None

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1,
            event2,
        ]

        result = service.get_status_history("item-1")

        assert len(result) == 2
        assert result[0]["old_status"] == "todo"
        assert result[0]["new_status"] == "in_progress"
        assert result[0]["agent_id"] == "agent-1"
        assert result[1]["old_status"] == "in_progress"
        assert result[1]["new_status"] == "done"

    def test_get_history_no_created_at(self, service, mock_session):
        """Test history with None created_at."""
        event = Mock()
        event.created_at = None
        event.data = {"old_status": "todo", "new_status": "blocked"}
        event.agent_id = None

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [event]

        result = service.get_status_history("item-1")

        assert len(result) == 1
        assert result[0]["timestamp"] is None


class TestStatusConstants:
    """Test status constants."""

    def test_valid_statuses(self):
        """Test valid statuses list."""
        assert "todo" in VALID_STATUSES
        assert "in_progress" in VALID_STATUSES
        assert "blocked" in VALID_STATUSES
        assert "done" in VALID_STATUSES
        assert "archived" in VALID_STATUSES

    def test_status_transitions_defined(self):
        """Test all valid statuses have transition rules."""
        for status in VALID_STATUSES:
            assert status in STATUS_TRANSITIONS

    def test_status_progress_values(self):
        """Test status progress values."""
        assert STATUS_PROGRESS["todo"] == 0
        assert STATUS_PROGRESS["in_progress"] == 50
        assert STATUS_PROGRESS["blocked"] == 0
        assert STATUS_PROGRESS["done"] == 100
        assert STATUS_PROGRESS["archived"] == 100
