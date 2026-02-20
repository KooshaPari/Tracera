"""Unit tests for ItemService - based on actual implementation.

Functional Requirements Coverage:
    - FR-APP-001: Create Traceability Item
    - FR-APP-002: Retrieve Traceability Item
    - FR-APP-003: Update Traceability Item
    - FR-APP-004: Delete Traceability Item
    - FR-APP-005: List Traceability Items

Epics:
    - EPIC-003: Application & Tracking
"""

from typing import Any

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_THREE
from tracertm.models.item import Item
from tracertm.services.item_service import ItemService

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> None:
    """Create a mock async session."""
    return AsyncMock()


@pytest.fixture
def mock_item_repository() -> None:
    """Create a mock item repository."""
    return AsyncMock()


@pytest.fixture
def mock_link_repository() -> None:
    """Create a mock link repository."""
    return AsyncMock()


@pytest.fixture
def mock_event_repository() -> None:
    """Create a mock event repository."""
    return AsyncMock()


@pytest.fixture
def item_service(
    mock_session: Any, mock_item_repository: Any, mock_link_repository: Any, mock_event_repository: Any
) -> None:
    """Create ItemService with mocked dependencies."""
    service = ItemService(mock_session)
    service.items = mock_item_repository
    service.links = mock_link_repository
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


class TestItemServiceInitialization:
    """Test ItemService initialization."""

    def test_item_service_creates_with_session(self, mock_session: Any) -> None:
        """ItemService initializes with async session."""
        service = ItemService(mock_session)
        assert service.session == mock_session
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None

    def test_item_service_has_repositories(self, mock_session: Any) -> None:
        """ItemService creates repository instances."""
        service = ItemService(mock_session)
        assert hasattr(service, "items")
        assert hasattr(service, "links")
        assert hasattr(service, "events")


class TestItemServiceCreateItem:
    """Test ItemService.create_item method."""

    @pytest.mark.asyncio
    async def test_create_item_with_required_fields(self, item_service: Any, test_data: Any) -> None:
        """create_item creates item with required fields."""
        created_item = Item(
            id=str(uuid4()),
            project_id=test_data["project_id"],
            title="Test Item",
            view="Feature",
            item_type="requirement",
        )
        item_service.items.create = AsyncMock(return_value=created_item)
        item_service.events.log = AsyncMock()

        result = await item_service.create_item(
            project_id=test_data["project_id"],
            title="Test Item",
            view="Feature",
            item_type="requirement",
            agent_id=test_data["agent_id"],
        )

        assert result is not None
        assert result.title == "Test Item"
        item_service.items.create.assert_called_once()
        item_service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_item_with_optional_fields(self, item_service: Any, test_data: Any) -> None:
        """create_item creates item with optional fields."""
        created_item = Item(
            id=str(uuid4()),
            project_id=test_data["project_id"],
            title="Full Item",
            description="Description",
            view="Component",
            item_type="code",
            status="in_progress",
            priority="high",
            owner="user@example.com",
        )
        item_service.items.create = AsyncMock(return_value=created_item)
        item_service.events.log = AsyncMock()

        result = await item_service.create_item(
            project_id=test_data["project_id"],
            title="Full Item",
            description="Description",
            view="Component",
            item_type="code",
            status="in_progress",
            priority="high",
            owner="user@example.com",
            agent_id=test_data["agent_id"],
        )

        assert result is not None
        assert result.description == "Description"
        assert result.status == "in_progress"

    @pytest.mark.asyncio
    async def test_create_item_with_links(self, item_service: Any, test_data: Any) -> None:
        """create_item creates item and links it to other items."""
        target_id = str(uuid4())
        created_item = Item(
            id=str(uuid4()),
            project_id=test_data["project_id"],
            title="Test Item",
            view="Feature",
            item_type="requirement",
        )
        item_service.items.create = AsyncMock(return_value=created_item)
        item_service.links.create = AsyncMock()
        item_service.events.log = AsyncMock()

        result = await item_service.create_item(
            project_id=test_data["project_id"],
            title="Test Item",
            view="Feature",
            item_type="requirement",
            agent_id=test_data["agent_id"],
            link_to=[target_id],
        )

        assert result is not None
        item_service.links.create.assert_called_once()


class TestItemServiceGetItem:
    """Test ItemService.get_item method."""

    @pytest.mark.asyncio
    async def test_get_item_returns_item(self, item_service: Any, test_data: Any) -> None:
        """get_item returns an item."""
        mock_item = Item(
            id=test_data["item_id"],
            project_id=test_data["project_id"],
            title="Test Item",
            view="Feature",
            item_type="requirement",
        )
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)

        result = await item_service.get_item(test_data["project_id"], test_data["item_id"])

        assert result is not None
        assert result.id == test_data["item_id"]
        item_service.items.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_item_returns_none(self, item_service: Any, test_data: Any) -> None:
        """get_item returns None when item not found."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        result = await item_service.get_item(test_data["project_id"], test_data["item_id"])

        assert result is None


class TestItemServiceListItems:
    """Test ItemService.list_items method."""

    @pytest.mark.asyncio
    async def test_list_items_without_filters(self, item_service: Any, test_data: Any) -> None:
        """list_items returns items without filters."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title=f"Item {i}",
                view="Feature",
                item_type="requirement",
            )
            for i in range(3)
        ]
        item_service.items.get_by_project = AsyncMock(return_value=mock_items)

        result = await item_service.list_items(test_data["project_id"])

        assert isinstance(result, list)
        assert len(result) == COUNT_THREE
        item_service.items.get_by_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_items_with_view_filter(self, item_service: Any, test_data: Any) -> None:
        """list_items returns items filtered by view."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Component Item",
                view="Component",
                item_type="code",
            ),
        ]
        item_service.items.get_by_view = AsyncMock(return_value=mock_items)

        result = await item_service.list_items(test_data["project_id"], view="Component")

        assert isinstance(result, list)
        item_service.items.get_by_view.assert_called_once()


class TestItemServiceUpdateItem:
    """Test ItemService.update_item method."""

    @pytest.mark.asyncio
    async def test_update_item_basic(self, item_service: Any, test_data: Any) -> None:
        """update_item updates item fields."""
        mock_item = Item(
            id=test_data["item_id"],
            project_id=test_data["project_id"],
            title="Original",
            view="Feature",
            item_type="requirement",
        )
        updated_item = Item(
            id=test_data["item_id"],
            project_id=test_data["project_id"],
            title="Updated",
            view="Feature",
            item_type="requirement",
        )
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)
        item_service.events.log = AsyncMock()

        result = await item_service.update_item(test_data["item_id"], test_data["agent_id"], title="Updated")

        assert result is not None
        item_service.items.update.assert_called_once()
        item_service.events.log.assert_called_once()


class TestItemServiceItemHierarchy:
    """Test ItemService hierarchy methods."""

    @pytest.mark.asyncio
    async def test_get_children(self, item_service: Any, test_data: Any) -> None:
        """get_children returns direct children."""
        child_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Child",
                view="Feature",
                item_type="requirement",
                parent_id=test_data["item_id"],
            ),
        ]
        item_service.items.get_children = AsyncMock(return_value=child_items)

        result = await item_service.get_children(test_data["item_id"])

        assert isinstance(result, list)
        assert len(result) == 1
        item_service.items.get_children.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_ancestors(self, item_service: Any, test_data: Any) -> None:
        """get_ancestors returns path to root."""
        ancestor_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Ancestor",
                view="Feature",
                item_type="requirement",
            ),
        ]
        item_service.items.get_ancestors = AsyncMock(return_value=ancestor_items)

        result = await item_service.get_ancestors(test_data["item_id"])

        assert isinstance(result, list)
        item_service.items.get_ancestors.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_descendants(self, item_service: Any, test_data: Any) -> None:
        """get_descendants returns all descendants."""
        descendant_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Descendant",
                view="Feature",
                item_type="requirement",
            ),
        ]
        item_service.items.get_descendants = AsyncMock(return_value=descendant_items)

        result = await item_service.get_descendants(test_data["item_id"])

        assert isinstance(result, list)
        item_service.items.get_descendants.assert_called_once()


class TestItemServiceStatusTransitions:
    """Test ItemService status transition validation."""

    @pytest.mark.asyncio
    async def test_valid_status_transition(self, item_service: Any, test_data: Any) -> None:
        """update_item_status validates valid transitions."""
        mock_item = Item(
            id=test_data["item_id"],
            project_id=test_data["project_id"],
            title="Test",
            view="Feature",
            item_type="requirement",
            status="todo",
        )
        updated_item = Item(
            id=test_data["item_id"],
            project_id=test_data["project_id"],
            title="Test",
            view="Feature",
            item_type="requirement",
            status="in_progress",
        )
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)
        item_service.events.log = AsyncMock()

        result = await item_service.update_item_status(
            test_data["item_id"],
            "in_progress",
            test_data["agent_id"],
            test_data["project_id"],
        )

        assert result is not None
        item_service.items.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_status_raises_error(self, item_service: Any, test_data: Any) -> None:
        """update_item_status raises error for invalid status."""
        with pytest.raises(ValueError, match="Invalid status") as exc_info:
            await item_service.update_item_status(
                test_data["item_id"],
                "invalid_status",
                test_data["agent_id"],
                test_data["project_id"],
            )
        assert "Invalid status" in str(exc_info.value)
