from typing import Any

"""Tests for item hierarchy operations."""

import uuid
from unittest.mock import AsyncMock

import pytest

from tests.test_constants import COUNT_TWO
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
class TestItemHierarchy:
    """Test suite for item hierarchy operations."""

    async def test_get_children(self, item_service: Any, _mock_session: Any) -> None:
        """Test retrieving item children."""
        parent_id = str(uuid.uuid4())

        expected_children = [
            Item(id=str(uuid.uuid4()), parent_id=parent_id, title="Child 1"),
            Item(id=str(uuid.uuid4()), parent_id=parent_id, title="Child 2"),
        ]

        item_service.items.get_children = AsyncMock(return_value=expected_children)

        result = await item_service.get_children(parent_id)

        assert len(result) == COUNT_TWO
        assert all(c.parent_id == parent_id for c in result)
        item_service.items.get_children.assert_called_once_with(parent_id)

    async def test_get_ancestors(self, item_service: Any, _mock_session: Any) -> None:
        """Test retrieving item ancestors."""
        item_id = str(uuid.uuid4())

        expected_ancestors = [
            Item(id=str(uuid.uuid4()), title="Grandparent"),
            Item(id=str(uuid.uuid4()), title="Parent"),
        ]

        item_service.items.get_ancestors = AsyncMock(return_value=expected_ancestors)

        result = await item_service.get_ancestors(item_id)

        assert len(result) == COUNT_TWO
        item_service.items.get_ancestors.assert_called_once_with(item_id)

    async def test_get_descendants(self, item_service: Any, _mock_session: Any) -> None:
        """Test retrieving all descendants."""
        item_id = str(uuid.uuid4())

        expected_descendants = [
            Item(id=str(uuid.uuid4()), title="Child"),
            Item(id=str(uuid.uuid4()), title="Grandchild"),
        ]

        item_service.items.get_descendants = AsyncMock(return_value=expected_descendants)

        result = await item_service.get_descendants(item_id)

        assert len(result) == COUNT_TWO
        item_service.items.get_descendants.assert_called_once_with(item_id)

    async def test_create_child_item_validation(self, item_service: Any, mock_session: Any) -> None:
        """Test validation when creating a child item."""
        # This tests the logic in create_item service method if we add specific parent validation logic there
        # Currently simple pass-through to repo, but good to have a placeholder or test repo constraints
