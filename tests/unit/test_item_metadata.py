from typing import Any

"""Tests for item metadata operations."""

import uuid
from unittest.mock import AsyncMock

import pytest

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
class TestItemMetadata:
    """Test suite for item metadata operations."""

    async def test_add_metadata_merge(self, item_service: Any, _mock_session: Any) -> None:
        """Test adding metadata with merge."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        existing_item = Item(id=item_id, item_metadata={"existing": "value"}, version=1)
        updated_item = Item(id=item_id, item_metadata={"existing": "value", "new": "data"}, version=2)

        item_service.items.get_by_id = AsyncMock(return_value=existing_item)
        item_service.items.update = AsyncMock(return_value=updated_item)
        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Execute
        result = await item_service.update_metadata(item_id, agent_id, {"new": "data"}, merge=True)

        # Verify
        assert result.item_metadata["new"] == "data"
        item_service.items.update.assert_called_once()
        call_args = item_service.items.update.call_args.kwargs
        assert call_args["item_metadata"] == {"existing": "value", "new": "data"}

    async def test_replace_metadata(self, item_service: Any, _mock_session: Any) -> None:
        """Test replacing metadata (no merge)."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        existing_item = Item(id=item_id, item_metadata={"existing": "value"}, version=1)
        updated_item = Item(id=item_id, item_metadata={"replaced": "true"}, version=2)

        item_service.items.get_by_id = AsyncMock(return_value=existing_item)
        item_service.items.update = AsyncMock(return_value=updated_item)
        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Execute
        result = await item_service.update_metadata(item_id, agent_id, {"replaced": "true"}, merge=False)

        # Verify
        assert result.item_metadata["replaced"] == "true"
        item_service.items.update.assert_called_once()
        call_args = item_service.items.update.call_args.kwargs
        assert call_args["item_metadata"] == {"replaced": "true"}
