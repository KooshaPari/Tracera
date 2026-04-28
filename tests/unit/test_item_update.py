from typing import Any

"""Tests for item update and optimistic locking."""

import uuid
from unittest.mock import AsyncMock

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.services.item_service import ItemService


@pytest.fixture
def mock_session() -> None:
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def item_service(mock_session: Any) -> None:
    """Create an ItemService instance with mock session."""
    return ItemService(mock_session)


@pytest.mark.asyncio
class TestItemUpdate:
    """Test suite for item update and concurrency."""

    async def test_update_item_success(self, item_service: Any, _mock_session: Any) -> None:
        """Test successful item update."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        existing_item = Item(id=item_id, title="Original Title", status="todo", version=1)

        updated_item = Item(id=item_id, title="New Title", status="in_progress", version=2)

        # Mock repository behavior
        item_service.items.get_by_id = AsyncMock(return_value=existing_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        # Correctly mock event logging - it shouldn't return anything specific but must be awaitable
        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Execute
        result = await item_service.update_item(
            item_id=item_id,
            agent_id=agent_id,
            title="New Title",
            status="in_progress",
        )

        # Verify
        assert result.title == "New Title"
        assert result.status == "in_progress"
        assert result.version == COUNT_TWO

        item_service.items.update.assert_called_once()
        kwargs = item_service.items.update.call_args.kwargs
        assert kwargs["item_id"] == item_id
        assert kwargs["expected_version"] == 1
        assert kwargs["title"] == "New Title"

        # Verify event logging
        item_service.events.log.assert_called_once()

    async def test_update_item_concurrency_retry(self, item_service: Any, _mock_session: Any) -> None:
        """Test optimistic locking retry mechanism."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        existing_item = Item(id=item_id, version=1)
        updated_item = Item(id=item_id, version=2)

        # Mock get_by_id to return item
        item_service.items.get_by_id = AsyncMock(return_value=existing_item)

        # Mock event log to avoid 'int' + 'coroutine' error if implementation calls next_id logic
        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Mock update to fail first, then succeed
        item_service.items.update = AsyncMock(side_effect=[ConcurrencyError("Version mismatch"), updated_item])

        # Execute
        result = await item_service.update_item(item_id=item_id, agent_id=agent_id, status="done")

        # Verify
        assert result.version == COUNT_TWO
        assert item_service.items.update.call_count == COUNT_TWO  # Failed once, succeeded second time

    async def test_update_item_concurrency_fail(self, item_service: Any, _mock_session: Any) -> None:
        """Test optimistic locking max retries exceeded."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        existing_item = Item(id=item_id, version=1)

        item_service.items.get_by_id = AsyncMock(return_value=existing_item)
        item_service.items.update = AsyncMock(side_effect=ConcurrencyError("Version mismatch"))

        # Execute & Verify
        with pytest.raises(ConcurrencyError):
            await item_service.update_item(item_id=item_id, agent_id=agent_id, status="done")

        # Should have tried 3 times (default max_retries)
        assert item_service.items.update.call_count == COUNT_THREE

    async def test_update_item_not_found(self, item_service: Any, _mock_session: Any) -> None:
        """Test updating non-existent item."""
        item_id = str(uuid.uuid4())
        item_service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match=r"Item .* not found"):
            await item_service.update_item(item_id=item_id, agent_id="agent", status="done")
