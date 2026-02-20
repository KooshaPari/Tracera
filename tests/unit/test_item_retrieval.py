from typing import Any

"""Tests for item retrieval logic."""

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
class TestItemRetrieval:
    """Test suite for item retrieval operations."""

    async def test_get_item_found(self, item_service: Any, _mock_session: Any) -> None:
        """Test retrieving an existing item."""
        # Setup
        project_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())

        expected_item = Item(
            id=item_id,
            project_id=project_id,
            title="Test Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )

        # Mock repository behavior
        item_service.items.get_by_id = AsyncMock(return_value=expected_item)

        # Execute
        result = await item_service.get_item(project_id, item_id)

        # Verify
        assert result is not None
        assert result.id == item_id
        assert result.project_id == project_id
        item_service.items.get_by_id.assert_called_once_with(item_id, project_id)

    async def test_list_items_by_view(self, item_service: Any, _mock_session: Any) -> None:
        """Test listing items filtered by view."""
        # Setup
        project_id = str(uuid.uuid4())
        view = "FEATURE"

        expected_items = [
            Item(id=str(uuid.uuid4()), title="Item 1", view=view),
            Item(id=str(uuid.uuid4()), title="Item 2", view=view),
        ]

        # Mock repository behavior
        item_service.items.get_by_view = AsyncMock(return_value=expected_items)

        # Execute
        result = await item_service.list_items(project_id, view=view)

        # Verify
        assert len(result) == COUNT_TWO
        assert all(i.view == view for i in result)
        # Updated assertion to match new signature
        item_service.items.get_by_view.assert_called_once()
        call_args = item_service.items.get_by_view.call_args
        assert call_args[0] == (project_id, view, None)  # project_id, view, status

    async def test_list_items_by_status(self, item_service: Any, _mock_session: Any) -> None:
        """Test listing items filtered by status."""
        # Setup
        project_id = str(uuid.uuid4())
        status = "todo"

        expected_items = [
            Item(id=str(uuid.uuid4()), title="Item 1", status=status),
            Item(id=str(uuid.uuid4()), title="Item 2", status=status),
        ]

        # Mock repository behavior
        item_service.items.get_by_project = AsyncMock(return_value=expected_items)

        # Execute
        result = await item_service.list_items(project_id, status=status)

        # Verify
        assert len(result) == COUNT_TWO
        assert all(i.status == status for i in result)
        item_service.items.get_by_project.assert_called_once()
        # Verify status was passed
        _, kwargs = item_service.items.get_by_project.call_args
        assert kwargs.get("status") == status

    async def test_list_items_with_view_and_status(self, item_service: Any, _mock_session: Any) -> None:
        """Test listing items filtered by both view and status."""
        # Setup
        project_id = str(uuid.uuid4())
        view = "FEATURE"
        status = "todo"

        expected_items = [Item(id=str(uuid.uuid4()), title="Item 1", view=view, status=status)]

        # Mock repository behavior
        item_service.items.get_by_view = AsyncMock(return_value=expected_items)

        # Execute
        result = await item_service.list_items(project_id, view=view, status=status)

        # Verify
        assert len(result) == 1
        item_service.items.get_by_view.assert_called_once()
        call_args = item_service.items.get_by_view.call_args
        assert call_args[0] == (project_id, view, status)

    async def test_get_item_with_links(self, item_service: Any, _mock_session: Any) -> None:
        """Test retrieving item with its links."""
        # Setup
        project_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())

        mock_item = Item(id=item_id, project_id=project_id, title="Item")
        mock_links = [{"id": "link1", "source": item_id, "target": "other"}]

        # Mock repository behavior
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.links.get_by_item = AsyncMock(return_value=mock_links)

        # Execute
        result = await item_service.get_item_with_links(item_id)

        # Verify
        assert result is not None
        assert result["item"] == mock_item
        assert result["links"] == mock_links
        item_service.items.get_by_id.assert_called_once_with(item_id)
        item_service.links.get_by_item.assert_called_once_with(item_id)

    async def test_get_item_not_found(self, item_service: Any, _mock_session: Any) -> None:
        """Test retrieving non-existent item."""
        # Setup
        project_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())

        # Mock repository behavior
        item_service.items.get_by_id = AsyncMock(return_value=None)

        # Execute
        result = await item_service.get_item(project_id, item_id)

        # Verify
        assert result is None
