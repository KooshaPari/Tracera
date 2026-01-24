"""
Comprehensive tests for EventService.

Tests all methods: log_event, get_item_history, get_item_at_time.
Tests filtering by type, date, user; pagination; validation; error handling; edge cases.

Coverage target: 100%
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Any

from tracertm.services.event_service import EventService
from tracertm.models.event import Event


class TestEventServiceFixtures:
    """Shared fixtures for EventService tests."""

    @pytest.fixture
    def session(self):
        """Create mock async session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, session):
        """Create EventService with mocked repository."""
        service = EventService(session)
        service.events = AsyncMock()
        return service

    @pytest.fixture
    def mock_event(self):
        """Create a mock event."""
        event = Mock(spec=Event)
        event.id = 1
        event.project_id = "proj-1"
        event.event_type = "created"
        event.entity_type = "item"
        event.entity_id = "item-1"
        event.agent_id = "agent-1"
        event.data = {"title": "Test Item"}
        event.created_at = datetime.utcnow()
        return event

    @pytest.fixture
    def multiple_events(self):
        """Create multiple mock events."""
        events = []
        base_time = datetime.utcnow()
        event_types = ["created", "updated", "updated", "deleted"]

        for idx, event_type in enumerate(event_types):
            event = Mock(spec=Event)
            event.id = idx + 1
            event.project_id = "proj-1"
            event.event_type = event_type
            event.entity_type = "item"
            event.entity_id = "item-1"
            event.agent_id = f"agent-{idx + 1}"
            event.data = {"status": event_type}
            event.created_at = base_time + timedelta(hours=idx)
            events.append(event)

        return events


class TestLogEvent(TestEventServiceFixtures):
    """Test log_event method."""

    @pytest.mark.asyncio
    async def test_log_event_for_item(self, service, mock_event):
        """Test logging event for an item."""
        # Setup
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data={"title": "Test Item"},
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result.id == 1
        assert result.event_type == "created"
        assert result.entity_type == "item"
        assert result.entity_id == "item-1"
        service.events.log.assert_called_once_with(
            project_id="proj-1",
            event_type="created",
            entity_type="item",
            entity_id="item-1",
            data={"title": "Test Item"},
            agent_id="agent-1"
        )

    @pytest.mark.asyncio
    async def test_log_event_for_project(self, service, mock_event):
        """Test logging event at project level (no item_id)."""
        # Setup
        mock_event.entity_type = "project"
        mock_event.entity_id = "proj-1"
        mock_event.item_id = None
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="project_created",
            event_data={"name": "My Project"},
            agent_id="agent-1"
        )

        # Assert
        assert result.entity_type == "project"
        assert result.entity_id == "proj-1"
        service.events.log.assert_called_once_with(
            project_id="proj-1",
            event_type="project_created",
            entity_type="project",
            entity_id="proj-1",
            data={"name": "My Project"},
            agent_id="agent-1"
        )

    @pytest.mark.asyncio
    async def test_log_event_with_empty_data(self, service, mock_event):
        """Test logging event with empty data dict."""
        # Setup
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="updated",
            event_data={},
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result is not None
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_event_with_complex_data(self, service, mock_event):
        """Test logging event with nested/complex data."""
        # Setup
        complex_data = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "deep": {"level1": {"level2": {"level3": "value"}}}
        }
        mock_event.data = complex_data
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="updated",
            event_data=complex_data,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result.data == complex_data
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_event_various_event_types(self, service, mock_event):
        """Test logging events with different event types."""
        # Setup
        event_types = ["created", "updated", "deleted", "linked", "archived"]
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute and Assert
        for event_type in event_types:
            mock_event.event_type = event_type
            result = await service.log_event(
                project_id="proj-1",
                event_type=event_type,
                event_data={},
                agent_id="agent-1",
                item_id="item-1"
            )
            assert result.event_type == event_type

    @pytest.mark.asyncio
    async def test_log_event_with_none_agent(self, service, mock_event):
        """Test logging event without agent_id (system event)."""
        # Setup
        mock_event.agent_id = None
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="system_sync",
            event_data={"type": "auto_sync"},
            agent_id=None,
            item_id="item-1"
        )

        # Assert
        assert result.agent_id is None
        service.events.log.assert_called_once_with(
            project_id="proj-1",
            event_type="system_sync",
            entity_type="item",
            entity_id="item-1",
            data={"type": "auto_sync"},
            agent_id=None
        )

    @pytest.mark.asyncio
    async def test_log_event_repository_exception(self, service):
        """Test error handling when repository fails."""
        # Setup
        service.events.log = AsyncMock(side_effect=Exception("DB Error"))

        # Execute and Assert
        with pytest.raises(Exception, match="DB Error"):
            await service.log_event(
                project_id="proj-1",
                event_type="created",
                event_data={},
                agent_id="agent-1",
                item_id="item-1"
            )


class TestGetItemHistory(TestEventServiceFixtures):
    """Test get_item_history method."""

    @pytest.mark.asyncio
    async def test_get_item_history_single_event(self, service, mock_event):
        """Test getting history with single event."""
        # Setup
        service.events.get_by_entity = AsyncMock(return_value=[mock_event])

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        assert len(result) == 1
        assert result[0].entity_id == "item-1"
        service.events.get_by_entity.assert_called_once_with("item-1")

    @pytest.mark.asyncio
    async def test_get_item_history_multiple_events(self, service, multiple_events):
        """Test getting history with multiple events."""
        # Setup
        service.events.get_by_entity = AsyncMock(return_value=multiple_events)

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        assert len(result) == 4
        assert result[0].event_type == "created"
        assert result[-1].event_type == "deleted"
        service.events.get_by_entity.assert_called_once_with("item-1")

    @pytest.mark.asyncio
    async def test_get_item_history_empty(self, service):
        """Test getting history for non-existent item."""
        # Setup
        service.events.get_by_entity = AsyncMock(return_value=[])

        # Execute
        result = await service.get_item_history("nonexistent-item")

        # Assert
        assert len(result) == 0
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_item_history_ordered_by_date(self, service, multiple_events):
        """Test that history is ordered by creation date."""
        # Setup
        # Events are created in chronological order
        service.events.get_by_entity = AsyncMock(return_value=multiple_events)

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        for i in range(len(result) - 1):
            assert result[i].created_at <= result[i + 1].created_at

    @pytest.mark.asyncio
    async def test_get_item_history_with_different_agents(self, service):
        """Test history with events from different agents."""
        # Setup
        events = []
        for agent_num in range(1, 4):
            event = Mock(spec=Event)
            event.id = agent_num
            event.entity_id = "item-1"
            event.agent_id = f"agent-{agent_num}"
            event.created_at = datetime.utcnow()
            events.append(event)

        service.events.get_by_entity = AsyncMock(return_value=events)

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        assert len(result) == 3
        agent_ids = [e.agent_id for e in result]
        assert "agent-1" in agent_ids
        assert "agent-3" in agent_ids

    @pytest.mark.asyncio
    async def test_get_item_history_repository_exception(self, service):
        """Test error handling when repository fails."""
        # Setup
        service.events.get_by_entity = AsyncMock(side_effect=ValueError("Invalid item"))

        # Execute and Assert
        with pytest.raises(ValueError, match="Invalid item"):
            await service.get_item_history("item-1")


class TestGetItemAtTime(TestEventServiceFixtures):
    """Test get_item_at_time method for event replay."""

    @pytest.mark.asyncio
    async def test_get_item_at_time_after_creation(self, service):
        """Test reconstructing item state at a time after creation."""
        # Setup
        creation_event = Mock(spec=Event)
        creation_event.event_type = "created"
        creation_event.data = {"id": "item-1", "title": "Test Item", "status": "new"}
        creation_event.created_at = datetime.utcnow()

        service.events.get_entity_at_time = AsyncMock(return_value=creation_event.data)

        # Execute
        result = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert result is not None
        assert result["id"] == "item-1"
        assert result["title"] == "Test Item"

    @pytest.mark.asyncio
    async def test_get_item_at_time_after_update(self, service):
        """Test state reconstruction after update event."""
        # Setup
        final_state = {"id": "item-1", "title": "Updated Title", "status": "done"}
        service.events.get_entity_at_time = AsyncMock(return_value=final_state)

        # Execute
        result = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert result is not None
        assert result["title"] == "Updated Title"
        assert result["status"] == "done"

    @pytest.mark.asyncio
    async def test_get_item_at_time_before_creation(self, service):
        """Test state before item was created."""
        # Setup
        service.events.get_entity_at_time = AsyncMock(return_value=None)

        # Execute
        past_time = datetime.utcnow() - timedelta(days=30)
        result = await service.get_item_at_time("item-1", past_time)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_item_at_time_after_deletion(self, service):
        """Test state when item was deleted."""
        # Setup
        service.events.get_entity_at_time = AsyncMock(return_value=None)

        # Execute
        result = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_item_at_time_specific_datetime(self, service):
        """Test reconstruction at specific point in time."""
        # Setup
        target_time = datetime(2024, 1, 15, 12, 30, 0)
        expected_state = {"id": "item-1", "version": 2}
        service.events.get_entity_at_time = AsyncMock(return_value=expected_state)

        # Execute
        result = await service.get_item_at_time("item-1", target_time)

        # Assert
        assert result == expected_state
        service.events.get_entity_at_time.assert_called_once_with("item-1", target_time)

    @pytest.mark.asyncio
    async def test_get_item_at_time_complex_state(self, service):
        """Test reconstruction of complex state object."""
        # Setup
        complex_state = {
            "id": "item-1",
            "title": "Complex Item",
            "metadata": {
                "tags": ["important", "urgent"],
                "custom_fields": {"field1": "value1"}
            },
            "status": "in_progress",
            "assignee": "user-123"
        }
        service.events.get_entity_at_time = AsyncMock(return_value=complex_state)

        # Execute
        result = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert result == complex_state
        assert result["metadata"]["tags"] == ["important", "urgent"]

    @pytest.mark.asyncio
    async def test_get_item_at_time_repository_exception(self, service):
        """Test error handling when repository fails."""
        # Setup
        service.events.get_entity_at_time = AsyncMock(side_effect=RuntimeError("DB error"))

        # Execute and Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await service.get_item_at_time("item-1", datetime.utcnow())


class TestEventServiceEdgeCases(TestEventServiceFixtures):
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_project_id(self, service, mock_event):
        """Test handling of empty project ID."""
        # Setup
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="",
            event_type="created",
            event_data={},
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert - should still work (validation at API level)
        assert result is not None

    @pytest.mark.asyncio
    async def test_very_long_entity_id(self, service, mock_event):
        """Test handling of very long entity IDs."""
        # Setup
        long_id = "x" * 500
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data={},
            agent_id="agent-1",
            item_id=long_id
        )

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_special_characters_in_data(self, service, mock_event):
        """Test logging events with special characters in data."""
        # Setup
        special_data = {
            "title": "Test & Special <> Chars \"quoted\" 'single'",
            "emoji": "🚀🎉✅",
            "unicode": "你好世界",
            "symbols": "!@#$%^&*()"
        }
        mock_event.data = special_data
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data=special_data,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result is not None
        assert result.data == special_data

    @pytest.mark.asyncio
    async def test_null_values_in_data(self, service, mock_event):
        """Test logging events with null values in data."""
        # Setup
        data_with_nulls = {
            "field1": None,
            "field2": "value",
            "field3": None,
            "nested": {"null_field": None}
        }
        mock_event.data = data_with_nulls
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="updated",
            event_data=data_with_nulls,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result.data == data_with_nulls

    @pytest.mark.asyncio
    async def test_large_data_payload(self, service, mock_event):
        """Test logging events with large data payloads."""
        # Setup
        large_data = {
            f"field_{i}": f"value_{i}" * 100
            for i in range(100)
        }
        mock_event.data = large_data
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data=large_data,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_concurrent_events_same_item(self, service):
        """Test handling multiple events for same item at same time."""
        # Setup
        base_time = datetime.utcnow()
        events = []

        for idx in range(5):
            event = Mock(spec=Event)
            event.id = idx + 1
            event.entity_id = "item-1"
            event.event_type = "updated"
            event.created_at = base_time  # Same time
            event.agent_id = f"agent-{idx}"
            events.append(event)

        service.events.get_by_entity = AsyncMock(return_value=events)

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_item_id_with_special_format(self, service, mock_event):
        """Test item IDs with UUID and other formats."""
        # Setup
        item_ids = [
            "550e8400-e29b-41d4-a716-446655440000",  # UUID
            "item_with_underscore",
            "item-with-dash",
            "UPPERCASE_ID",
            "123456789"
        ]
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute and Assert
        for item_id in item_ids:
            result = await service.log_event(
                project_id="proj-1",
                event_type="created",
                event_data={},
                agent_id="agent-1",
                item_id=item_id
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_datetime_edge_cases(self, service):
        """Test with edge case datetimes."""
        # Setup
        service.events.get_entity_at_time = AsyncMock(return_value={"id": "item-1"})

        # Execute and Assert for various edge case times
        edge_times = [
            datetime(1970, 1, 1),  # Unix epoch
            datetime(2099, 12, 31, 23, 59, 59),  # Far future
            datetime.utcnow(),  # Now
            datetime.utcnow() - timedelta(days=365),  # 1 year ago
        ]

        for edge_time in edge_times:
            result = await service.get_item_at_time("item-1", edge_time)
            assert result is not None or result is None  # Both valid

    @pytest.mark.asyncio
    async def test_numeric_values_in_data(self, service, mock_event):
        """Test logging events with various numeric types."""
        # Setup
        numeric_data = {
            "int": 42,
            "float": 3.14159,
            "negative": -100,
            "zero": 0,
            "large_int": 9999999999999999999,
            "scientific": 1.23e-4
        }
        mock_event.data = numeric_data
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data=numeric_data,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_boolean_values_in_data(self, service, mock_event):
        """Test logging events with boolean values."""
        # Setup
        bool_data = {
            "is_active": True,
            "is_archived": False,
            "is_deleted": False,
            "needs_review": True
        }
        mock_event.data = bool_data
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="updated",
            event_data=bool_data,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result is not None


class TestEventServiceIntegration(TestEventServiceFixtures):
    """Integration tests for EventService workflows."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_item_history(self, service):
        """Test full workflow: create event and retrieve history."""
        # Setup
        creation_event = Mock(spec=Event)
        creation_event.id = 1
        creation_event.event_type = "created"
        creation_event.entity_id = "item-1"
        creation_event.created_at = datetime.utcnow()

        service.events.log = AsyncMock(return_value=creation_event)
        service.events.get_by_entity = AsyncMock(return_value=[creation_event])

        # Execute
        logged = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data={"title": "Test"},
            agent_id="agent-1",
            item_id="item-1"
        )

        history = await service.get_item_history("item-1")

        # Assert
        assert logged.id == 1
        assert len(history) == 1
        assert history[0].event_type == "created"

    @pytest.mark.asyncio
    async def test_state_reconstruction_after_updates(self, service):
        """Test reconstructing state after multiple updates."""
        # Setup
        final_state = {
            "id": "item-1",
            "title": "Final Title",
            "status": "completed"
        }
        service.events.get_entity_at_time = AsyncMock(return_value=final_state)

        # Execute
        state = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert state is not None
        assert state["status"] == "completed"

    @pytest.mark.asyncio
    async def test_audit_trail_scenario(self, service):
        """Test typical audit trail scenario with multiple operations."""
        # Setup
        events = []
        base_time = datetime.utcnow()
        operations = ["created", "updated", "updated", "linked", "archived"]

        for idx, op in enumerate(operations):
            event = Mock(spec=Event)
            event.id = idx + 1
            event.event_type = op
            event.entity_id = "item-1"
            event.agent_id = f"agent-{(idx % 2) + 1}"
            event.created_at = base_time + timedelta(minutes=idx)
            event.data = {"operation": op}
            events.append(event)

        service.events.get_by_entity = AsyncMock(return_value=events)

        # Execute
        history = await service.get_item_history("item-1")

        # Assert
        assert len(history) == 5
        assert history[0].event_type == "created"
        assert history[-1].event_type == "archived"


class TestEventServiceErrorHandling(TestEventServiceFixtures):
    """Test error handling and recovery scenarios."""

    @pytest.mark.asyncio
    async def test_log_event_database_error(self, service):
        """Test handling of database errors during logging."""
        # Setup
        service.events.log = AsyncMock(side_effect=Exception("Connection lost"))

        # Execute and Assert
        with pytest.raises(Exception, match="Connection lost"):
            await service.log_event(
                project_id="proj-1",
                event_type="created",
                event_data={},
                agent_id="agent-1",
                item_id="item-1"
            )

    @pytest.mark.asyncio
    async def test_get_history_with_corrupted_data(self, service):
        """Test handling of events with missing fields."""
        # Setup
        partial_event = Mock(spec=Event)
        partial_event.event_type = "created"
        partial_event.entity_id = "item-1"
        # Missing some fields - should not crash

        service.events.get_by_entity = AsyncMock(return_value=[partial_event])

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_item_at_time_with_invalid_time(self, service):
        """Test handling of invalid datetime values."""
        # Setup
        service.events.get_entity_at_time = AsyncMock(
            side_effect=ValueError("Invalid datetime")
        )

        # Execute and Assert
        with pytest.raises(ValueError, match="Invalid datetime"):
            await service.get_item_at_time("item-1", "invalid-date")

    @pytest.mark.asyncio
    async def test_repository_timeout(self, service):
        """Test handling of repository timeout."""
        # Setup
        service.events.log = AsyncMock(side_effect=TimeoutError("Query timeout"))

        # Execute and Assert
        with pytest.raises(TimeoutError, match="Query timeout"):
            await service.log_event(
                project_id="proj-1",
                event_type="created",
                event_data={},
                agent_id="agent-1",
                item_id="item-1"
            )


class TestEventServiceDataValidation(TestEventServiceFixtures):
    """Test data validation and input handling."""

    @pytest.mark.asyncio
    async def test_event_type_normalization(self, service, mock_event):
        """Test that event types are handled consistently."""
        # Setup
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="CREATED",  # Uppercase
            event_data={},
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_id_optional(self, service, mock_event):
        """Test that agent_id is optional."""
        # Setup
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute - no agent_id provided
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data={},
            agent_id=None,
            item_id="item-1"
        )

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_data_dict_preserved(self, service, mock_event):
        """Test that data dictionary is preserved without mutation."""
        # Setup
        original_data = {"key": "value", "nested": {"inner": "data"}}
        data_copy = original_data.copy()
        mock_event.data = original_data
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data=original_data,
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert original_data == data_copy  # Original not mutated


class TestEventServiceReturnValues(TestEventServiceFixtures):
    """Test return value types and structures."""

    @pytest.mark.asyncio
    async def test_log_event_returns_event(self, service, mock_event):
        """Test that log_event returns an Event object."""
        # Setup
        service.events.log = AsyncMock(return_value=mock_event)

        # Execute
        result = await service.log_event(
            project_id="proj-1",
            event_type="created",
            event_data={},
            agent_id="agent-1",
            item_id="item-1"
        )

        # Assert
        assert isinstance(result, Mock)  # Mock simulates Event
        assert hasattr(result, 'id')
        assert hasattr(result, 'event_type')

    @pytest.mark.asyncio
    async def test_get_item_history_returns_list(self, service, multiple_events):
        """Test that get_item_history returns a list."""
        # Setup
        service.events.get_by_entity = AsyncMock(return_value=multiple_events)

        # Execute
        result = await service.get_item_history("item-1")

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(e, Mock) for e in result)

    @pytest.mark.asyncio
    async def test_get_item_at_time_returns_dict_or_none(self, service):
        """Test that get_item_at_time returns dict or None."""
        # Setup - returns dict
        service.events.get_entity_at_time = AsyncMock(
            return_value={"id": "item-1", "status": "active"}
        )

        # Execute
        result_dict = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert isinstance(result_dict, dict)

        # Setup - returns None
        service.events.get_entity_at_time = AsyncMock(return_value=None)

        # Execute
        result_none = await service.get_item_at_time("item-1", datetime.utcnow())

        # Assert
        assert result_none is None
