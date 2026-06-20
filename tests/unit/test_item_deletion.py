from typing import Any

"""Tests for item deletion and recovery."""

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
class TestItemDeletion:
    """Test suite for item deletion operations."""

    async def test_soft_delete_item(self, item_service: Any, _mock_session: Any) -> None:
        """Test soft deletion of an item."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        mock_item = Item(id=item_id, project_id="proj1", title="Item")

        # Mock behavior
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.delete = AsyncMock(return_value=True)
        item_service.links.delete_by_item = AsyncMock()

        # Mock event log
        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Execute
        result = await item_service.delete_item(item_id, agent_id, soft=True)

        # Verify
        assert result is True
        item_service.items.delete.assert_called_once_with(item_id, soft=True)
        # item_service.links.delete_by_item.assert_called_once_with(item_id) # Service now trusts repo for links

    async def test_hard_delete_item(self, item_service: Any, _mock_session: Any) -> None:
        """Test permanent deletion of an item."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        mock_item = Item(id=item_id, project_id="proj1", title="Item")

        # Mock behavior
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.delete = AsyncMock(return_value=True)

        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Execute
        result = await item_service.delete_item(item_id, agent_id, soft=False)

        # Verify
        assert result is True
        item_service.items.delete.assert_called_once_with(item_id, soft=False)

    async def test_delete_non_existent_item(self, item_service: Any, _mock_session: Any) -> None:
        """Test deletion of non-existent item."""
        item_id = str(uuid.uuid4())
        item_service.items.get_by_id = AsyncMock(return_value=None)

        result = await item_service.delete_item(item_id, "agent", soft=True)
        assert result is False

    async def test_undelete_item(self, item_service: Any, _mock_session: Any) -> None:
        """Test recovery of deleted item."""
        # Setup
        item_id = str(uuid.uuid4())
        agent_id = "test-agent"

        restored_item = Item(id=item_id, project_id="proj1", deleted_at=None)

        item_service.items.restore = AsyncMock(return_value=restored_item)

        item_service.events = AsyncMock()
        item_service.events.log = AsyncMock()

        # Execute
        result = await item_service.undelete_item(item_id, agent_id)

        # Verify
        assert result is not None
        assert result.deleted_at is None
        item_service.items.restore.assert_called_once_with(item_id)
