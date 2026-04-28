from typing import Any

"""Unit tests for EventService - based on actual implementation."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.event import Event
from tracertm.services.event_service import EventService

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> None:
    """Create a mock async session."""
    return AsyncMock()


@pytest.fixture
def mock_event_repository() -> None:
    """Create a mock event repository."""
    return AsyncMock()


@pytest.fixture
def event_service(mock_session: Any, mock_event_repository: Any) -> None:
    """Create EventService with mocked dependencies."""
    service = EventService(mock_session)
    service.events = mock_event_repository
    return service


@pytest.fixture
def test_data() -> None:
    """Provide test data."""
    return {
        "project_id": str(uuid4()),
        "item_id": str(uuid4()),
        "agent_id": str(uuid4()),
    }


class TestEventServiceInitialization:
    """Test EventService initialization."""

    def test_event_service_creates_with_session(self, mock_session: Any) -> None:
        """EventService initializes with async session."""
        service = EventService(mock_session)
        assert service.session == mock_session
        assert service.events is not None

    def test_event_service_has_event_repository(self, mock_session: Any) -> None:
        """EventService creates EventRepository instance."""
        service = EventService(mock_session)
        assert hasattr(service, "events")


class TestEventServiceLogEvent:
    """Test EventService.log_event method."""

    @pytest.mark.asyncio
    async def test_log_event_with_item_id(self, event_service: Any, test_data: Any) -> None:
        """log_event creates event with item_id."""
        mock_event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="item",
            entity_id=test_data["item_id"],
            agent_id=test_data["agent_id"],
            data={"title": "New Item"},
        )
        event_service.events.log = AsyncMock(return_value=mock_event)

        event_data = {"title": "New Item"}
        result = await event_service.log_event(
            project_id=test_data["project_id"],
            event_type="item_created",
            event_data=event_data,
            agent_id=test_data["agent_id"],
            item_id=test_data["item_id"],
        )

        assert result is not None
        event_service.events.log.assert_called_once()
        call_kwargs = event_service.events.log.call_args[1]
        assert call_kwargs["project_id"] == test_data["project_id"]
        assert call_kwargs["event_type"] == "item_created"
        assert call_kwargs["entity_type"] == "item"

    @pytest.mark.asyncio
    async def test_log_event_without_item_id(self, event_service: Any, test_data: Any) -> None:
        """log_event creates project event when no item_id."""
        mock_event = Event(
            project_id=test_data["project_id"],
            event_type="project_created",
            entity_type="project",
            entity_id=test_data["project_id"],
            agent_id=test_data["agent_id"],
            data={},
        )
        event_service.events.log = AsyncMock(return_value=mock_event)

        result = await event_service.log_event(
            project_id=test_data["project_id"],
            event_type="project_created",
            event_data={},
            agent_id=test_data["agent_id"],
            item_id=None,
        )

        assert result is not None
        call_kwargs = event_service.events.log.call_args[1]
        assert call_kwargs["entity_type"] == "project"
        assert call_kwargs["entity_id"] == test_data["project_id"]


class TestEventServiceGetItemHistory:
    """Test EventService.get_item_history method."""

    @pytest.mark.asyncio
    async def test_get_item_history_returns_events(self, event_service: Any, test_data: Any) -> None:
        """get_item_history returns list of events."""
        mock_events = [
            Event(
                project_id=test_data["project_id"],
                event_type="item_created",
                entity_type="item",
                entity_id=test_data["item_id"],
                agent_id=test_data["agent_id"],
                data={"title": "Item"},
            ),
            Event(
                project_id=test_data["project_id"],
                event_type="item_updated",
                entity_type="item",
                entity_id=test_data["item_id"],
                agent_id=test_data["agent_id"],
                data={"status": "done"},
            ),
        ]
        event_service.events.get_by_entity = AsyncMock(return_value=mock_events)

        result = await event_service.get_item_history(test_data["item_id"])

        assert isinstance(result, list)
        assert len(result) == COUNT_TWO
        event_service.events.get_by_entity.assert_called_once_with(test_data["item_id"])

    @pytest.mark.asyncio
    async def test_get_item_history_empty_list(self, event_service: Any, test_data: Any) -> None:
        """get_item_history returns empty list when no events."""
        event_service.events.get_by_entity = AsyncMock(return_value=[])

        result = await event_service.get_item_history(test_data["item_id"])

        assert isinstance(result, list)
        assert len(result) == 0


class TestEventServiceGetItemAtTime:
    """Test EventService.get_item_at_time method."""

    @pytest.mark.asyncio
    async def test_get_item_at_time_returns_state(self, event_service: Any, test_data: Any) -> None:
        """get_item_at_time returns item state at specific time."""
        item_state = {"id": test_data["item_id"], "title": "Item at that time", "status": "in_progress"}
        event_service.events.get_entity_at_time = AsyncMock(return_value=item_state)

        target_time = datetime.now()
        result = await event_service.get_item_at_time(test_data["item_id"], target_time)

        assert result == item_state
        event_service.events.get_entity_at_time.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_item_at_time_returns_none(self, event_service: Any, test_data: Any) -> None:
        """get_item_at_time returns None when no history."""
        event_service.events.get_entity_at_time = AsyncMock(return_value=None)

        target_time = datetime.now()
        result = await event_service.get_item_at_time(test_data["item_id"], target_time)

        assert result is None
