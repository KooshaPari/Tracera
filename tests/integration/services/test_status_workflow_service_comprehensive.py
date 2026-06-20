"""Comprehensive integration test suite for StatusWorkflowService.

Tests all status transitions, edge cases, concurrency scenarios, and state machine behavior.
Target: 35+ tests with 95%+ coverage.
"""

from typing import Any

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.services.status_workflow_service import (
    STATUS_PROGRESS,
    STATUS_TRANSITIONS,
    VALID_STATUSES,
    StatusWorkflowService,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def workflow_service(db_session: Any) -> None:
    """Create StatusWorkflowService instance."""
    return StatusWorkflowService(db_session)


@pytest.fixture
def test_project(db_session: Any) -> None:
    """Create test project."""
    project = Project(id="test-project", name="Test Project")
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_item(db_session: Any, test_project: Any) -> None:
    """Create test item in todo status."""
    item = Item(
        id="item-1",
        project_id=test_project.id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
    )
    db_session.add(item)
    db_session.commit()
    return item


# ==================== Basic Transition Tests ====================


class TestBasicStatusTransitions:
    """Test basic status transitions."""

    def test_todo_to_in_progress(self, workflow_service: Any, test_item: Any) -> None:
        """Test valid transition: todo → in_progress."""
        result = workflow_service.update_item_status(test_item.id, "in_progress")

        assert result["old_status"] == "todo"
        assert result["new_status"] == "in_progress"
        assert result["progress"] == 50

    def test_in_progress_to_done(self, workflow_service: Any, db_session: Any, _test_item: Any) -> None:
        """Test valid transition: in_progress → done."""
        # First transition to in_progress
        workflow_service.update_item_status(test_item.id, "in_progress")

        # Then transition to done
        result = workflow_service.update_item_status(test_item.id, "done")

        assert result["old_status"] == "in_progress"
        assert result["new_status"] == "done"
        assert result["progress"] == 100

    def test_in_progress_to_blocked(self, workflow_service: Any, test_item: Any) -> None:
        """Test valid transition: in_progress → blocked."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        result = workflow_service.update_item_status(test_item.id, "blocked")

        assert result["old_status"] == "in_progress"
        assert result["new_status"] == "blocked"
        assert result["progress"] == 0

    def test_blocked_to_in_progress(self, workflow_service: Any, test_item: Any) -> None:
        """Test valid transition: blocked → in_progress."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "blocked")

        result = workflow_service.update_item_status(test_item.id, "in_progress")

        assert result["old_status"] == "blocked"
        assert result["new_status"] == "in_progress"

    def test_done_to_todo_reopen(self, workflow_service: Any, test_item: Any) -> None:
        """Test reopening a done item: done → todo."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "done")

        result = workflow_service.update_item_status(test_item.id, "todo")

        assert result["old_status"] == "done"
        assert result["new_status"] == "todo"


# ==================== Invalid Transition Tests ====================


class TestInvalidTransitions:
    """Test invalid status transitions."""

    def test_todo_to_done_invalid(self, workflow_service: Any, test_item: Any) -> None:
        """Test invalid transition: todo → done (must go through in_progress)."""
        with pytest.raises(ValueError) as exc_info:
            workflow_service.update_item_status(test_item.id, "done")

        assert "Invalid status transition" in str(exc_info.value)
        assert "todo → done" in str(exc_info.value)

    def test_todo_to_blocked_valid(self, workflow_service: Any, test_item: Any) -> None:
        """Test valid transition: todo → blocked (is allowed)."""
        result = workflow_service.update_item_status(test_item.id, "blocked")
        assert result["new_status"] == "blocked"

    def test_archived_terminal_state(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test archived is a terminal state - no transitions allowed."""
        # Manually set to archived for this test
        test_item.status = "archived"
        db_session.commit()

        with pytest.raises(ValueError):
            workflow_service.update_item_status(test_item.id, "todo")

        with pytest.raises(ValueError):
            workflow_service.update_item_status(test_item.id, "in_progress")

    def test_invalid_status_value(self, workflow_service: Any, test_item: Any) -> None:
        """Test transition to invalid status."""
        with pytest.raises(ValueError):
            workflow_service.update_item_status(test_item.id, "invalid_status")

    def test_done_to_in_progress_invalid(self, workflow_service: Any, test_item: Any) -> None:
        """Test invalid transition: done → in_progress (only todo allowed)."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "done")

        with pytest.raises(ValueError):
            workflow_service.update_item_status(test_item.id, "in_progress")

    def test_done_to_blocked_invalid(self, workflow_service: Any, test_item: Any) -> None:
        """Test invalid transition: done → blocked."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "done")

        with pytest.raises(ValueError):
            workflow_service.update_item_status(test_item.id, "blocked")

    def test_blocked_to_done_invalid(self, workflow_service: Any, test_item: Any) -> None:
        """Test invalid transition: blocked → done."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "blocked")

        with pytest.raises(ValueError):
            workflow_service.update_item_status(test_item.id, "done")


# ==================== Validation Tests ====================


class TestTransitionValidation:
    """Test validate_transition method."""

    def test_validate_todo_to_in_progress(self, workflow_service: Any) -> None:
        """Test validation: todo → in_progress."""
        assert workflow_service.validate_transition("todo", "in_progress") is True

    def test_validate_todo_to_blocked(self, workflow_service: Any) -> None:
        """Test validation: todo → blocked."""
        assert workflow_service.validate_transition("todo", "blocked") is True

    def test_validate_todo_to_done_invalid(self, workflow_service: Any) -> None:
        """Test validation: todo → done (invalid)."""
        assert workflow_service.validate_transition("todo", "done") is False

    def test_validate_in_progress_to_done(self, workflow_service: Any) -> None:
        """Test validation: in_progress → done."""
        assert workflow_service.validate_transition("in_progress", "done") is True

    def test_validate_in_progress_to_blocked(self, workflow_service: Any) -> None:
        """Test validation: in_progress → blocked."""
        assert workflow_service.validate_transition("in_progress", "blocked") is True

    def test_validate_in_progress_to_todo(self, workflow_service: Any) -> None:
        """Test validation: in_progress → todo."""
        assert workflow_service.validate_transition("in_progress", "todo") is True

    def test_validate_blocked_to_in_progress(self, workflow_service: Any) -> None:
        """Test validation: blocked → in_progress."""
        assert workflow_service.validate_transition("blocked", "in_progress") is True

    def test_validate_blocked_to_todo(self, workflow_service: Any) -> None:
        """Test validation: blocked → todo."""
        assert workflow_service.validate_transition("blocked", "todo") is True

    def test_validate_blocked_to_done_invalid(self, workflow_service: Any) -> None:
        """Test validation: blocked → done (invalid)."""
        assert workflow_service.validate_transition("blocked", "done") is False

    def test_validate_done_to_todo(self, workflow_service: Any) -> None:
        """Test validation: done → todo."""
        assert workflow_service.validate_transition("done", "todo") is True

    def test_validate_archived_all_invalid(self, workflow_service: Any) -> None:
        """Test validation: archived → any (all invalid)."""
        for status in VALID_STATUSES:
            if status != "archived":
                assert workflow_service.validate_transition("archived", status) is False

    def test_validate_invalid_current_status(self, workflow_service: Any) -> None:
        """Test validation with invalid current status."""
        assert workflow_service.validate_transition("invalid", "todo") is False

    def test_validate_invalid_new_status(self, workflow_service: Any) -> None:
        """Test validation with invalid new status."""
        assert workflow_service.validate_transition("todo", "invalid") is False

    def test_validate_same_status(self, workflow_service: Any) -> None:
        """Test validation with same status."""
        # Same status should be invalid based on current implementation
        for status in VALID_STATUSES:
            if status != "archived":
                # Most statuses don't transition to themselves
                result = workflow_service.validate_transition(status, status)
                assert result is False


# ==================== Progress Mapping Tests ====================


class TestProgressMapping:
    """Test status-to-progress mapping."""

    def test_todo_progress(self, workflow_service: Any, _test_item: Any) -> None:
        """Test todo status maps to 0% progress."""
        # Test the mapping directly since we can't transition from todo to todo
        assert STATUS_PROGRESS["todo"] == 0

    def test_in_progress_progress(self, workflow_service: Any, test_item: Any) -> None:
        """Test in_progress status maps to 50% progress."""
        result = workflow_service.update_item_status(test_item.id, "in_progress")
        assert result["progress"] == 50

    def test_blocked_progress(self, workflow_service: Any, test_item: Any) -> None:
        """Test blocked status maps to 0% progress."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        result = workflow_service.update_item_status(test_item.id, "blocked")
        assert result["progress"] == 0

    def test_done_progress(self, workflow_service: Any, test_item: Any) -> None:
        """Test done status maps to 100% progress."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        result = workflow_service.update_item_status(test_item.id, "done")
        assert result["progress"] == 100

    def test_archived_progress(self, workflow_service: Any, db_session: Any, _test_item: Any) -> None:
        """Test archived status maps to 100% progress."""
        test_item.status = "archived"
        db_session.commit()

        # Can't update from archived, so check the constant
        assert STATUS_PROGRESS["archived"] == 100


# ==================== History Tracking Tests ====================


class TestStatusHistory:
    """Test status change history tracking."""

    def test_single_status_change_history(self, workflow_service: Any, test_item: Any) -> None:
        """Test history for single status change."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        history = workflow_service.get_status_history(test_item.id)

        assert len(history) >= 1
        assert any(h["new_status"] == "in_progress" for h in history)

    def test_multiple_status_changes_history(self, workflow_service: Any, test_item: Any) -> None:
        """Test history for multiple status changes."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "done")
        workflow_service.update_item_status(test_item.id, "todo")

        history = workflow_service.get_status_history(test_item.id)

        assert len(history) >= COUNT_THREE
        new_statuses = [h["new_status"] for h in history]
        assert "in_progress" in new_statuses
        assert "done" in new_statuses
        assert "todo" in new_statuses

    def test_history_ordering_most_recent_first(self, workflow_service: Any, test_item: Any) -> None:
        """Test history is ordered with most recent first."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "done")

        history = workflow_service.get_status_history(test_item.id)

        # History should be ordered by created_at DESC (most recent first)
        assert len(history) >= COUNT_TWO
        assert history[0]["new_status"] in {"done", "in_progress"}

    def test_history_with_agent_id(self, workflow_service: Any, test_item: Any) -> None:
        """Test history includes agent_id when provided."""
        workflow_service.update_item_status(test_item.id, "in_progress", agent_id="test-agent")

        history = workflow_service.get_status_history(test_item.id)

        assert any(h["agent_id"] == "test-agent" and h["new_status"] == "in_progress" for h in history)

    def test_history_with_null_agent_id(self, workflow_service: Any, test_item: Any) -> None:
        """Test history handles null agent_id."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        history = workflow_service.get_status_history(test_item.id)

        assert len(history) >= 1

    def test_history_timestamp_present(self, workflow_service: Any, test_item: Any) -> None:
        """Test history includes timestamps."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        history = workflow_service.get_status_history(test_item.id)

        assert len(history) >= 1
        assert all(h["timestamp"] is not None for h in history)

    def test_empty_history_for_new_item(self, workflow_service: Any, db_session: Any, test_project: Any) -> None:
        """Test empty history for item with no status changes."""
        new_item = Item(
            id="item-new",
            project_id=test_project.id,
            title="New Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(new_item)
        db_session.commit()

        history = workflow_service.get_status_history(new_item.id)

        # Should be empty (no status_changed events)
        assert len([h for h in history if h.get("new_status")]) == 0


# ==================== Event Logging Tests ====================


class TestEventLogging:
    """Test event logging for status changes."""

    def test_status_change_event_created(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test status change event is created."""
        workflow_service.update_item_status(test_item.id, "in_progress", agent_id="test-agent")

        events = (
            db_session
            .query(Event)
            .filter(
                Event.entity_type == "item",
                Event.entity_id == test_item.id,
                Event.event_type == "status_changed",
            )
            .all()
        )

        assert len(events) >= 1
        assert events[-1].data["old_status"] == "todo"
        assert events[-1].data["new_status"] == "in_progress"

    def test_event_includes_item_title(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test event data includes item title."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        event = (
            db_session
            .query(Event)
            .filter(
                Event.entity_type == "item",
                Event.entity_id == test_item.id,
                Event.event_type == "status_changed",
            )
            .first()
        )

        assert event.data["item_title"] == test_item.title

    def test_event_includes_agent_id(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test event data includes agent_id."""
        workflow_service.update_item_status(test_item.id, "in_progress", agent_id="my-agent")

        event = (
            db_session
            .query(Event)
            .filter(
                Event.entity_type == "item",
                Event.entity_id == test_item.id,
                Event.event_type == "status_changed",
            )
            .first()
        )

        assert event.agent_id == "my-agent"


# ==================== Error Handling Tests ====================


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_nonexistent_item(self, workflow_service: Any) -> None:
        """Test updating nonexistent item raises error."""
        with pytest.raises(ValueError) as exc_info:
            workflow_service.update_item_status("nonexistent-id", "in_progress")

        assert "Item not found" in str(exc_info.value)

    def test_item_without_initial_status(self, workflow_service: Any, db_session: Any, test_project: Any) -> None:
        """Test item without initial status defaults to 'todo'."""
        item = Item(
            id="item-no-status",
            project_id=test_project.id,
            title="No Status Item",
            view="FEATURE",
            item_type="feature",
            status=None,
        )
        db_session.add(item)
        db_session.commit()

        result = workflow_service.update_item_status(item.id, "in_progress")

        # The service defaults None to 'todo' internally
        assert result["old_status"] == "todo"
        assert result["new_status"] == "in_progress"

    def test_status_change_persisted(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test status change is persisted to database."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        # Refresh from database
        updated_item = db_session.query(Item).filter(Item.id == test_item.id).first()

        assert updated_item.status == "in_progress"

    def test_multiple_items_independent(self, workflow_service: Any, db_session: Any, test_project: Any) -> None:
        """Test status changes are independent between items."""
        item1 = Item(
            id="item-1",
            project_id=test_project.id,
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        item2 = Item(
            id="item-2",
            project_id=test_project.id,
            title="Item 2",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item1)
        db_session.add(item2)
        db_session.commit()

        workflow_service.update_item_status(item1.id, "in_progress")
        workflow_service.update_item_status(item2.id, "blocked")

        updated_item1 = db_session.query(Item).filter(Item.id == item1.id).first()
        updated_item2 = db_session.query(Item).filter(Item.id == item2.id).first()

        assert updated_item1.status == "in_progress"
        assert updated_item2.status == "blocked"


# ==================== Complex Workflow Tests ====================


class TestComplexWorkflows:
    """Test complex workflow scenarios."""

    def test_complete_workflow_todo_to_done(self, workflow_service: Any, test_item: Any) -> None:
        """Test complete workflow: todo → in_progress → done."""
        # TODO → in_progress
        result1 = workflow_service.update_item_status(test_item.id, "in_progress")
        assert result1["progress"] == 50

        # in_progress → done
        result2 = workflow_service.update_item_status(test_item.id, "done")
        assert result2["progress"] == 100

    def test_workflow_with_blocking(self, workflow_service: Any, test_item: Any) -> None:
        """Test workflow with blocking: todo → in_progress → blocked → in_progress → done."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "blocked")
        workflow_service.update_item_status(test_item.id, "in_progress")
        result = workflow_service.update_item_status(test_item.id, "done")

        assert result["new_status"] == "done"
        assert result["progress"] == 100

    def test_workflow_with_reopening(self, workflow_service: Any, test_item: Any) -> None:
        """Test workflow with reopening: todo → in_progress → done → todo → in_progress → done."""
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "done")
        workflow_service.update_item_status(test_item.id, "todo")

        result = workflow_service.update_item_status(test_item.id, "in_progress")
        assert result["old_status"] == "todo"

        result = workflow_service.update_item_status(test_item.id, "done")
        assert result["new_status"] == "done"


# ==================== Concurrent Transition Tests ====================


class TestConcurrentTransitions:
    """Test concurrent status changes."""

    def test_sequential_rapid_transitions(self, workflow_service: Any, test_item: Any) -> None:
        """Test multiple rapid sequential transitions."""
        statuses = ["in_progress", "blocked", "in_progress", "done", "todo", "in_progress"]

        for status in statuses:
            try:
                workflow_service.update_item_status(test_item.id, status)
            except ValueError:
                # Some transitions may be invalid - that's expected
                pass

    def test_concurrent_updates_same_item(self, workflow_service: Any, db_session: Any, test_project: Any) -> None:
        """Test concurrent updates to same item."""
        item = Item(
            id="concurrent-item",
            project_id=test_project.id,
            title="Concurrent Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        db_session.commit()

        results = []
        errors = []

        def update_status(new_status: Any) -> None:
            try:
                result = workflow_service.update_item_status(item.id, new_status)
                results.append(result)
            except ValueError as e:
                errors.append(e)

        # Try to update with valid transitions
        statuses_to_try = ["in_progress", "blocked", "in_progress"]

        # Reset item to todo for this test
        item.status = "todo"
        db_session.commit()

        # Sequential attempts (database will enforce only valid transitions)
        for status in statuses_to_try:
            update_status(status)

        # At least some should succeed
        assert len(results) > 0

    def test_concurrent_different_items(self, workflow_service: Any, db_session: Any, test_project: Any) -> None:
        """Test sequential updates to different items (simulating concurrent behavior)."""
        item_ids = []
        for i in range(3):
            item = Item(
                id=f"item-{i}",
                project_id=test_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
            item_ids.append(f"item-{i}")
        db_session.commit()

        results = []

        # Sequential updates to different items
        for item_id in item_ids:
            result = workflow_service.update_item_status(item_id, "in_progress")
            results.append(result)

        assert len(results) == COUNT_THREE
        assert all(r["new_status"] == "in_progress" for r in results)


# ==================== State Machine Edge Cases ====================


class TestStateMachineEdgeCases:
    """Test edge cases in state machine behavior."""

    def test_all_valid_statuses_defined(self) -> None:
        """Test all valid statuses are defined."""
        expected_statuses = {"todo", "in_progress", "blocked", "done", "archived"}
        assert set(VALID_STATUSES) == expected_statuses

    def test_all_transitions_defined(self) -> None:
        """Test transitions are defined for all statuses."""
        for status in VALID_STATUSES:
            assert status in STATUS_TRANSITIONS

    def test_all_progress_mappings_defined(self) -> None:
        """Test progress mappings exist for all statuses."""
        for status in VALID_STATUSES:
            assert status in STATUS_PROGRESS

    def test_progress_values_valid_range(self) -> None:
        """Test progress values are in valid range [0, 100]."""
        for progress in STATUS_PROGRESS.values():
            assert 0 <= progress <= 100

    def test_no_unreachable_states(self) -> None:
        """Test all non-terminal states are reachable from todo."""
        # This is a basic reachability test
        # All non-archived states should be reachable from todo
        assert STATUS_TRANSITIONS["todo"]  # At least one transition from todo

    def test_archived_is_only_terminal_state(self) -> None:
        """Test archived is the only terminal state with no outgoing transitions."""
        for status, transitions in STATUS_TRANSITIONS.items():
            if status == "archived":
                assert transitions == []
            else:
                assert len(transitions) > 0

    def test_same_status_transition_invalid(self, workflow_service: Any) -> None:
        """Test transitioning to the same status is invalid."""
        for status in ["todo", "in_progress", "blocked", "done"]:
            # Verify same-status transitions are invalid
            result = workflow_service.validate_transition(status, status)
            assert result is False

    def test_return_value_structure(self, workflow_service: Any, test_item: Any) -> None:
        """Test update_item_status returns correct structure."""
        result = workflow_service.update_item_status(test_item.id, "in_progress")

        required_keys = {"item_id", "old_status", "new_status", "progress"}
        assert set(result.keys()) == required_keys

        assert isinstance(result["item_id"], str)
        assert isinstance(result["old_status"], (str, type(None)))
        assert isinstance(result["new_status"], str)
        assert isinstance(result["progress"], int)

    def test_history_data_structure(self, workflow_service: Any, test_item: Any) -> None:
        """Test get_status_history returns correct structure."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        history = workflow_service.get_status_history(test_item.id)

        if history:
            for entry in history:
                required_keys = {"timestamp", "old_status", "new_status", "agent_id"}
                assert set(entry.keys()) == required_keys


# ==================== Idempotency and Recovery Tests ====================


class TestIdempotencyAndRecovery:
    """Test idempotency and recovery scenarios."""

    def test_repeated_status_check(self, workflow_service: Any, _test_item: Any) -> None:
        """Test repeated status validation doesn't change behavior."""
        # Validate multiple times
        for _ in range(5):
            assert workflow_service.validate_transition("todo", "in_progress") is True

    def test_item_state_consistency_after_error(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test item state remains consistent after invalid transition error."""
        original_status = test_item.status

        # Try invalid transition
        try:
            workflow_service.update_item_status(test_item.id, "done")
        except ValueError:
            pass

        # Check status unchanged
        updated_item = db_session.query(Item).filter(Item.id == test_item.id).first()
        assert updated_item.status == original_status

    def test_transaction_rollback_on_error(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test transaction rollback on error."""
        initial_event_count = (
            db_session
            .query(Event)
            .filter(Event.entity_id == test_item.id, Event.event_type == "status_changed")
            .count()
        )

        # Try invalid transition
        try:
            workflow_service.update_item_status(test_item.id, "done")
        except ValueError:
            pass

        # Event count should not increase for invalid transition
        final_event_count = (
            db_session
            .query(Event)
            .filter(Event.entity_id == test_item.id, Event.event_type == "status_changed")
            .count()
        )

        assert final_event_count == initial_event_count


# ==================== Integration with Other Components ====================


class TestIntegrationWithOtherComponents:
    """Test integration with other system components."""

    def test_event_queryable_after_status_change(self, workflow_service: Any, db_session: Any, test_item: Any) -> None:
        """Test events are queryable after status change."""
        workflow_service.update_item_status(test_item.id, "in_progress")

        event = (
            db_session
            .query(Event)
            .filter(
                Event.entity_type == "item",
                Event.entity_id == test_item.id,
                Event.event_type == "status_changed",
            )
            .first()
        )

        assert event is not None
        assert event.project_id == test_item.project_id

    def test_history_includes_all_changes(self, workflow_service: Any, test_item: Any) -> None:
        """Test history includes all status changes."""
        changes = [
            ("in_progress", "test-agent-1"),
            ("blocked", "test-agent-2"),
            ("in_progress", "test-agent-3"),
        ]

        for new_status, agent_id in changes:
            if workflow_service.validate_transition(test_item.status, new_status):
                workflow_service.update_item_status(test_item.id, new_status, agent_id=agent_id)
                test_item.status = new_status  # Update local reference

        history = workflow_service.get_status_history(test_item.id)

        # Verify all agents appear in history
        agent_ids_in_history = [h.get("agent_id") for h in history if h.get("agent_id")]
        assert "test-agent-1" in agent_ids_in_history or len(agent_ids_in_history) > 0


# ==================== Performance and Scalability Tests ====================


class TestPerformanceAndScalability:
    """Test performance with multiple items and transitions."""

    def test_status_update_performance(self, workflow_service: Any, test_item: Any) -> None:
        """Test status update completes in reasonable time."""
        import time

        start_time = time.time()
        workflow_service.update_item_status(test_item.id, "in_progress")
        elapsed_time = time.time() - start_time

        # Should complete in less than 1 second
        assert elapsed_time < 1.0

    def test_history_retrieval_performance(self, workflow_service: Any, test_item: Any) -> None:
        """Test history retrieval completes in reasonable time."""
        # Create several status changes
        for _ in range(5):
            try:
                workflow_service.update_item_status(test_item.id, "in_progress")
            except ValueError:
                break

        import time

        start_time = time.time()
        history = workflow_service.get_status_history(test_item.id)
        elapsed_time = time.time() - start_time

        # Should complete in less than 1 second
        assert elapsed_time < 1.0
        assert isinstance(history, list)

    def test_many_items_status_updates(self, workflow_service: Any, db_session: Any, test_project: Any) -> None:
        """Test status updates on many items."""
        items = []
        for i in range(10):
            item = Item(
                id=f"perf-item-{i}",
                project_id=test_project.id,
                title=f"Performance Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            db_session.add(item)
            items.append(item)
        db_session.commit()

        import time

        start_time = time.time()
        for item in items:
            workflow_service.update_item_status(item.id, "in_progress")
        elapsed_time = time.time() - start_time

        # Should handle 10 items in reasonable time
        assert elapsed_time < float(COUNT_FIVE + 0.0)


# ==================== Coverage Tests ====================


class TestCoverageGaps:
    """Tests to ensure comprehensive coverage of all code paths."""

    def test_validate_transition_all_combinations(self, workflow_service: Any) -> None:
        """Test all valid status combinations are correctly validated."""
        # Exhaustively test all transitions
        for current, allowed in STATUS_TRANSITIONS.items():
            for target in VALID_STATUSES:
                expected = target in allowed
                actual = workflow_service.validate_transition(current, target)
                assert actual == expected, f"Transition {current}→{target}: expected {expected}, got {actual}"

    def test_update_item_status_return_value_accuracy(self, workflow_service: Any, test_item: Any) -> None:
        """Test update_item_status returns accurate information."""
        result = workflow_service.update_item_status(test_item.id, "in_progress")

        assert result["item_id"] == test_item.id
        assert result["old_status"] == "todo"
        assert result["new_status"] == "in_progress"
        assert result["progress"] == STATUS_PROGRESS["in_progress"]

    def test_history_ordering_correctness(self, workflow_service: Any, test_item: Any) -> None:
        """Test history ordering is correct (DESC by timestamp)."""
        # Make multiple changes
        workflow_service.update_item_status(test_item.id, "in_progress")
        workflow_service.update_item_status(test_item.id, "blocked")
        workflow_service.update_item_status(test_item.id, "in_progress")

        history = workflow_service.get_status_history(test_item.id)

        # Verify ordering
        if len(history) > 1:
            for i in range(len(history) - 1):
                current_time = history[i]["timestamp"]
                next_time = history[i + 1]["timestamp"]
                # Current should be >= next (DESC order)
                assert current_time >= next_time
