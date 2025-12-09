"""
Comprehensive tests for ItemService.

Coverage target: 100%
Tests all methods: create_item, get_item, list_items, update_item, delete_item,
update_item_status, get_item_progress, bulk operations, metadata updates, hierarchy methods.

Covers:
- Success and failure scenarios
- Edge cases and validation
- Integration with repositories
- Error handling and logging
- Optimistic locking
- Status transitions
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, call
from typing import Any

from tracertm.services.item_service import ItemService, STATUS_TRANSITIONS, VALID_STATUSES
from tracertm.models.item import Item


class TestItemServiceInit:
    """Test ItemService initialization."""

    @pytest.mark.asyncio
    async def test_init_creates_repositories(self):
        """Test that initialization creates all required repositories."""
        session = AsyncMock()

        with patch("tracertm.services.item_service.ItemRepository") as mock_item_repo, \
             patch("tracertm.services.item_service.LinkRepository") as mock_link_repo, \
             patch("tracertm.services.item_service.EventRepository") as mock_event_repo:

            service = ItemService(session)

            assert service.session == session
            mock_item_repo.assert_called_once_with(session)
            mock_link_repo.assert_called_once_with(session)
            mock_event_repo.assert_called_once_with(session)

    @pytest.mark.asyncio
    async def test_init_stores_session_reference(self):
        """Test that session is stored for later use."""
        session = AsyncMock()
        service = ItemService(session)
        assert service.session is session


class TestCreateItem:
    """Test create_item method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_item_minimal(self, service):
        """Test item creation with minimal required parameters."""
        created_item = Mock(
            id="item-1",
            title="Test Item",
            view="REQ",
            item_type="feature",
            status="todo",
            owner=None,
            priority="medium",
        )
        service.items.create = AsyncMock(return_value=created_item)
        service.events.log = AsyncMock()

        result = await service.create_item(
            project_id="proj-1",
            title="Test Item",
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
        )

        assert result.id == "item-1"
        assert result.title == "Test Item"
        service.items.create.assert_called_once()
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_item_with_single_link(self, service):
        """Test item creation with a single link."""
        created_item = Mock(
            id="item-1",
            title="Test",
            view="REQ",
            item_type="feature",
            status="todo",
            owner=None,
            priority="medium",
        )
        service.items.create = AsyncMock(return_value=created_item)
        service.links.create = AsyncMock()
        service.events.log = AsyncMock()

        result = await service.create_item(
            project_id="proj-1",
            title="Test",
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
            link_to=["item-2"],
            link_type="depends_on",
        )

        assert result.id == "item-1"
        service.links.create.assert_called_once_with(
            project_id="proj-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )

    @pytest.mark.asyncio
    async def test_create_item_with_multiple_links(self, service):
        """Test item creation with multiple links."""
        created_item = Mock(
            id="item-1",
            title="Test",
            view="REQ",
            item_type="feature",
            status="todo",
            owner=None,
            priority="medium",
        )
        service.items.create = AsyncMock(return_value=created_item)
        service.links.create = AsyncMock()
        service.events.log = AsyncMock()

        await service.create_item(
            project_id="proj-1",
            title="Test",
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
            link_to=["item-2", "item-3", "item-4"],
            link_type="relates_to",
        )

        assert service.links.create.call_count == 3

    @pytest.mark.asyncio
    async def test_create_item_with_empty_link_list(self, service):
        """Test that empty link list doesn't create links."""
        created_item = Mock(id="item-1", title="Test", view="REQ", item_type="feature", status="todo", owner=None, priority="medium")
        service.items.create = AsyncMock(return_value=created_item)
        service.links.create = AsyncMock()
        service.events.log = AsyncMock()

        await service.create_item(
            project_id="proj-1",
            title="Test",
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
            link_to=[],
        )

        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_item_with_all_optional_parameters(self, service):
        """Test item creation with all optional parameters."""
        created_item = Mock(
            id="item-1",
            title="Full Item",
            view="DEV",
            item_type="story",
            status="in_progress",
            owner="developer-1",
            priority="high",
        )
        service.items.create = AsyncMock(return_value=created_item)
        service.events.log = AsyncMock()

        result = await service.create_item(
            project_id="proj-1",
            title="Full Item",
            view="DEV",
            item_type="story",
            agent_id="agent-1",
            description="Detailed description",
            status="in_progress",
            parent_id="parent-1",
            metadata={"custom": "data", "tags": ["tag1", "tag2"]},
            owner="developer-1",
            priority="high",
        )

        assert result.owner == "developer-1"
        assert result.priority == "high"

    @pytest.mark.asyncio
    async def test_create_item_logs_event_with_correct_data(self, service):
        """Test that event logging includes correct data."""
        created_item = Mock(
            id="item-1",
            title="Test",
            view="REQ",
            item_type="feature",
            status="todo",
            owner="owner-1",
            priority="low",
        )
        service.items.create = AsyncMock(return_value=created_item)
        service.events.log = AsyncMock()

        await service.create_item(
            project_id="proj-1",
            title="Test",
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
            link_to=["item-2"],
        )

        service.events.log.assert_called_once()
        call_args = service.events.log.call_args[1]
        assert call_args["event_type"] == "item_created"
        assert call_args["entity_type"] == "item"
        assert call_args["entity_id"] == "item-1"
        assert call_args["agent_id"] == "agent-1"


class TestGetItem:
    """Test get_item method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_item_found(self, service):
        """Test getting an existing item."""
        item = Mock(id="item-1", title="Test")
        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.get_item("proj-1", "item-1")

        assert result.id == "item-1"
        service.items.get_by_id.assert_called_once_with("item-1", "proj-1")

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, service):
        """Test getting a non-existent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.get_item("proj-1", "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_item_with_special_characters(self, service):
        """Test getting item with special characters in ID."""
        item = Mock(id="item-with-uuid-123-456-789")
        service.items.get_by_id = AsyncMock(return_value=item)

        result = await service.get_item("proj-1", "item-with-uuid-123-456-789")

        assert result is not None


class TestListItems:
    """Test list_items method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_list_items_all_defaults(self, service):
        """Test listing all items with default parameters."""
        items = [Mock(id="1"), Mock(id="2")]
        service.items.get_by_project = AsyncMock(return_value=items)

        result = await service.list_items("proj-1")

        assert len(result) == 2
        service.items.get_by_project.assert_called_once_with(
            "proj-1", status=None, limit=100, offset=0
        )

    @pytest.mark.asyncio
    async def test_list_items_by_view(self, service):
        """Test listing items filtered by view."""
        items = [Mock(id="1", view="REQ")]
        service.items.get_by_view = AsyncMock(return_value=items)

        result = await service.list_items("proj-1", view="REQ")

        assert len(result) == 1
        service.items.get_by_view.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_items_by_status(self, service):
        """Test listing items filtered by status."""
        items = [Mock(id="1", status="done")]
        service.items.get_by_project = AsyncMock(return_value=items)

        result = await service.list_items("proj-1", status="done")

        assert len(result) == 1
        service.items.get_by_project.assert_called_once_with(
            "proj-1", status="done", limit=100, offset=0
        )

    @pytest.mark.asyncio
    async def test_list_items_with_custom_pagination(self, service):
        """Test listing items with custom limit and offset."""
        items = [Mock(id="1")]
        service.items.get_by_project = AsyncMock(return_value=items)

        await service.list_items("proj-1", limit=50, offset=10)

        service.items.get_by_project.assert_called_once_with(
            "proj-1", status=None, limit=50, offset=10
        )

    @pytest.mark.asyncio
    async def test_list_items_empty_result(self, service):
        """Test listing items returns empty list when none found."""
        service.items.get_by_project = AsyncMock(return_value=[])

        result = await service.list_items("proj-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_list_items_with_view_and_status(self, service):
        """Test listing items with both view and status filters."""
        items = [Mock(id="1", view="REQ", status="done")]
        service.items.get_by_view = AsyncMock(return_value=items)

        await service.list_items("proj-1", view="REQ", status="done")

        service.items.get_by_view.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_items_include_deleted(self, service):
        """Test listing items includes deleted flag."""
        items = [Mock(id="1")]
        service.items.get_by_project = AsyncMock(return_value=items)

        await service.list_items("proj-1", include_deleted=True)

        service.items.get_by_project.assert_called_once()


class TestUpdateItem:
    """Test update_item method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_update_item_success(self, service):
        """Test successful item update."""
        item = Mock(id="item-1", version=1, project_id="proj-1")
        updated_item = Mock(id="item-1", version=2, project_id="proj-1", title="Updated")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            result = await service.update_item("item-1", "agent-1", title="Updated")

            assert result.title == "Updated"
            service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, service):
        """Test update fails when item not found."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            with pytest.raises(ValueError, match="Item .* not found"):
                await service.update_item("nonexistent", "agent-1", title="New")

    @pytest.mark.asyncio
    async def test_update_item_multiple_fields(self, service):
        """Test updating multiple fields at once."""
        item = Mock(id="item-1", version=1, project_id="proj-1")
        updated_item = Mock(id="item-1", version=2, project_id="proj-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            await service.update_item(
                "item-1",
                "agent-1",
                title="New Title",
                description="New Desc",
                priority="high",
            )

            call_kwargs = service.items.update.call_args[1]
            assert call_kwargs["title"] == "New Title"
            assert call_kwargs["description"] == "New Desc"
            assert call_kwargs["priority"] == "high"

    @pytest.mark.asyncio
    async def test_update_item_uses_optimistic_locking(self, service):
        """Test that update uses optimistic locking with version."""
        item = Mock(id="item-1", version=5, project_id="proj-1")
        updated_item = Mock(id="item-1", version=6, project_id="proj-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            await service.update_item("item-1", "agent-1", title="Updated")

            service.items.update.assert_called_once()
            call_kwargs = service.items.update.call_args[1]
            assert call_kwargs["expected_version"] == 5


class TestGetItemWithLinks:
    """Test get_item_with_links method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_item_with_links_found(self, service):
        """Test getting item with its links."""
        item = Mock(id="item-1")
        links = [Mock(id="link-1"), Mock(id="link-2")]

        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_item = AsyncMock(return_value=links)

        result = await service.get_item_with_links("item-1")

        assert result["item"] == item
        assert len(result["links"]) == 2

    @pytest.mark.asyncio
    async def test_get_item_with_links_not_found(self, service):
        """Test getting non-existent item with links."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.get_item_with_links("nonexistent")

        assert result is None
        service.links.get_by_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_item_with_no_links(self, service):
        """Test getting item that has no links."""
        item = Mock(id="item-1")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.links.get_by_item = AsyncMock(return_value=[])

        result = await service.get_item_with_links("item-1")

        assert result["item"] == item
        assert result["links"] == []


class TestHierarchyMethods:
    """Test hierarchy methods: get_children, get_ancestors, get_descendants."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_children_multiple(self, service):
        """Test getting multiple children of an item."""
        children = [Mock(id="child-1"), Mock(id="child-2"), Mock(id="child-3")]
        service.items.get_children = AsyncMock(return_value=children)

        result = await service.get_children("parent-1")

        assert len(result) == 3
        service.items.get_children.assert_called_once_with("parent-1")

    @pytest.mark.asyncio
    async def test_get_children_none(self, service):
        """Test getting children when item has none."""
        service.items.get_children = AsyncMock(return_value=[])

        result = await service.get_children("item-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_ancestors_multiple_levels(self, service):
        """Test getting ancestors with multiple levels."""
        ancestors = [
            Mock(id="parent"),
            Mock(id="grandparent"),
            Mock(id="great-grandparent"),
        ]
        service.items.get_ancestors = AsyncMock(return_value=ancestors)

        result = await service.get_ancestors("item-1")

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_ancestors_root_item(self, service):
        """Test getting ancestors of a root item (no ancestors)."""
        service.items.get_ancestors = AsyncMock(return_value=[])

        result = await service.get_ancestors("root-item")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_descendants_deep_tree(self, service):
        """Test getting all descendants in a deep tree."""
        descendants = [
            Mock(id="child"),
            Mock(id="grandchild-1"),
            Mock(id="grandchild-2"),
            Mock(id="great-grandchild"),
        ]
        service.items.get_descendants = AsyncMock(return_value=descendants)

        result = await service.get_descendants("parent-1")

        assert len(result) == 4

    @pytest.mark.asyncio
    async def test_get_descendants_leaf_item(self, service):
        """Test getting descendants of a leaf item (no descendants)."""
        service.items.get_descendants = AsyncMock(return_value=[])

        result = await service.get_descendants("leaf-item")

        assert result == []


class TestDeleteItem:
    """Test delete_item method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_delete_item_soft_success(self, service):
        """Test successful soft delete of an item."""
        item = Mock(id="item-1", project_id="proj-1")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.delete = AsyncMock(return_value=True)
        service.events.log = AsyncMock()

        result = await service.delete_item("item-1", "agent-1", soft=True)

        assert result is True
        service.items.delete.assert_called_once_with("item-1", soft=True)
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_item_hard_success(self, service):
        """Test successful hard delete of an item."""
        item = Mock(id="item-1", project_id="proj-1")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.delete = AsyncMock(return_value=True)
        service.events.log = AsyncMock()

        result = await service.delete_item("item-1", "agent-1", soft=False)

        assert result is True
        service.items.delete.assert_called_once_with("item-1", soft=False)

    @pytest.mark.asyncio
    async def test_delete_item_soft_not_found(self, service):
        """Test soft delete of non-existent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        result = await service.delete_item("nonexistent", "agent-1", soft=True)

        assert result is False
        service.items.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_hard_not_found(self, service):
        """Test hard delete of non-existent item (may still attempt)."""
        service.items.get_by_id = AsyncMock(return_value=None)
        service.items.delete = AsyncMock(return_value=False)

        result = await service.delete_item("nonexistent", "agent-1", soft=False)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_item_logs_correct_data(self, service):
        """Test that delete logs correct event data."""
        item = Mock(id="item-1", project_id="proj-1")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.delete = AsyncMock(return_value=True)
        service.events.log = AsyncMock()

        await service.delete_item("item-1", "agent-1", soft=True)

        call_args = service.events.log.call_args[1]
        assert call_args["event_type"] == "item_deleted"
        assert call_args["data"]["soft"] is True

    @pytest.mark.asyncio
    async def test_delete_item_failure_no_event_logged(self, service):
        """Test that failed delete doesn't log event."""
        item = Mock(id="item-1", project_id="proj-1")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.delete = AsyncMock(return_value=False)
        service.events.log = AsyncMock()

        result = await service.delete_item("item-1", "agent-1", soft=True)

        assert result is False
        service.events.log.assert_not_called()


class TestUndeleteItem:
    """Test undelete_item method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_undelete_item_success(self, service):
        """Test successful item restore."""
        item = Mock(id="item-1", project_id="proj-1")
        service.items.restore = AsyncMock(return_value=item)
        service.events.log = AsyncMock()

        result = await service.undelete_item("item-1", "agent-1")

        assert result.id == "item-1"
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_undelete_item_not_found(self, service):
        """Test restoring non-existent item."""
        service.items.restore = AsyncMock(return_value=None)

        result = await service.undelete_item("nonexistent", "agent-1")

        assert result is None
        service.events.log.assert_not_called()

    @pytest.mark.asyncio
    async def test_undelete_item_logs_correct_event(self, service):
        """Test that undelete logs correct event type."""
        item = Mock(id="item-1", project_id="proj-1")
        service.items.restore = AsyncMock(return_value=item)
        service.events.log = AsyncMock()

        await service.undelete_item("item-1", "agent-1")

        call_args = service.events.log.call_args[1]
        assert call_args["event_type"] == "item_restored"


class TestUpdateMetadata:
    """Test update_metadata method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_update_metadata_merge(self, service):
        """Test updating metadata with merge."""
        item = Mock(id="item-1", version=1, item_metadata={"existing": "value"}, project_id="proj-1")
        updated_item = Mock(id="item-1", version=2, project_id="proj-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            await service.update_metadata("item-1", "agent-1", {"new": "data"}, merge=True)

            call_kwargs = service.items.update.call_args[1]
            assert "existing" in call_kwargs["item_metadata"]
            assert "new" in call_kwargs["item_metadata"]

    @pytest.mark.asyncio
    async def test_update_metadata_replace(self, service):
        """Test updating metadata with replace."""
        item = Mock(id="item-1", version=1, item_metadata={"old": "data"}, project_id="proj-1")
        updated_item = Mock(id="item-1", version=2, project_id="proj-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            await service.update_metadata("item-1", "agent-1", {"new": "data"}, merge=False)

            call_kwargs = service.items.update.call_args[1]
            assert call_kwargs["item_metadata"] == {"new": "data"}

    @pytest.mark.asyncio
    async def test_update_metadata_not_found(self, service):
        """Test updating metadata of non-existent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            with pytest.raises(ValueError, match="Item .* not found"):
                await service.update_metadata("nonexistent", "agent-1", {"data": "value"})

    @pytest.mark.asyncio
    async def test_update_metadata_null_existing(self, service):
        """Test updating metadata when current metadata is None."""
        item = Mock(id="item-1", version=1, item_metadata=None, project_id="proj-1")
        updated_item = Mock(id="item-1", version=2, project_id="proj-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            await service.update_metadata("item-1", "agent-1", {"new": "data"}, merge=True)

            call_kwargs = service.items.update.call_args[1]
            assert call_kwargs["item_metadata"] == {"new": "data"}


class TestUpdateItemStatus:
    """Test update_item_status method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_update_status_valid_transition_todo_to_in_progress(self, service):
        """Test valid transition from todo to in_progress."""
        item = Mock(id="item-1", version=1, status="todo")
        updated_item = Mock(id="item-1", version=2, status="in_progress")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            result = await service.update_item_status("item-1", "in_progress", "agent-1", "proj-1")

            assert result.status == "in_progress"

    @pytest.mark.asyncio
    async def test_update_status_valid_transition_in_progress_to_done(self, service):
        """Test valid transition from in_progress to done."""
        item = Mock(id="item-1", version=1, status="in_progress")
        updated_item = Mock(id="item-1", version=2, status="done")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            result = await service.update_item_status("item-1", "done", "agent-1", "proj-1")

            assert result.status == "done"

    @pytest.mark.asyncio
    async def test_update_status_valid_transition_done_to_todo(self, service):
        """Test valid transition from done back to todo (reopening)."""
        item = Mock(id="item-1", version=1, status="done")
        updated_item = Mock(id="item-1", version=2, status="todo")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            result = await service.update_item_status("item-1", "todo", "agent-1", "proj-1")

            assert result.status == "todo"

    @pytest.mark.asyncio
    async def test_update_status_invalid_new_status(self, service):
        """Test invalid new status."""
        with pytest.raises(ValueError, match="Invalid status"):
            await service.update_item_status("item-1", "invalid_status", "agent-1", "proj-1")

    @pytest.mark.asyncio
    async def test_update_status_invalid_transition(self, service):
        """Test invalid status transition."""
        item = Mock(id="item-1", version=1, status="done")

        service.items.get_by_id = AsyncMock(return_value=item)

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            with pytest.raises(ValueError, match="Cannot transition"):
                await service.update_item_status("item-1", "in_progress", "agent-1", "proj-1")

    @pytest.mark.asyncio
    async def test_update_status_item_not_found(self, service):
        """Test status update of non-existent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            with pytest.raises(ValueError, match="not found"):
                await service.update_item_status("nonexistent", "in_progress", "agent-1", "proj-1")

    @pytest.mark.asyncio
    async def test_update_status_logs_event(self, service):
        """Test that status update logs event with old and new status."""
        item = Mock(id="item-1", version=1, status="todo")
        updated_item = Mock(id="item-1", version=2, status="in_progress")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            await service.update_item_status("item-1", "in_progress", "agent-1", "proj-1")

            call_args = service.events.log.call_args[1]
            assert call_args["event_type"] == "item_status_changed"
            assert call_args["data"]["old_status"] == "todo"
            assert call_args["data"]["new_status"] == "in_progress"


class TestGetItemProgress:
    """Test get_item_progress method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_progress_no_children_done(self, service):
        """Test progress for item with no children, status done."""
        item = Mock(id="item-1", status="done")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.get_children = AsyncMock(return_value=[])

        result = await service.get_item_progress("item-1", "proj-1")

        assert result["total"] == 1
        assert result["done"] == 1
        assert result["percentage"] == 100

    @pytest.mark.asyncio
    async def test_progress_no_children_todo(self, service):
        """Test progress for item with no children, status todo."""
        item = Mock(id="item-1", status="todo")
        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.get_children = AsyncMock(return_value=[])

        result = await service.get_item_progress("item-1", "proj-1")

        assert result["total"] == 1
        assert result["todo"] == 1
        assert result["percentage"] == 0

    @pytest.mark.asyncio
    async def test_progress_with_children_all_done(self, service):
        """Test progress when all children are done."""
        item = Mock(id="item-1", status="in_progress")
        children = [
            Mock(status="done"),
            Mock(status="done"),
            Mock(status="done"),
        ]

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.get_children = AsyncMock(return_value=children)

        result = await service.get_item_progress("item-1", "proj-1")

        assert result["total"] == 3
        assert result["done"] == 3
        assert result["percentage"] == 100

    @pytest.mark.asyncio
    async def test_progress_with_children_mixed_statuses(self, service):
        """Test progress with mixed status children."""
        item = Mock(id="item-1", status="in_progress")
        children = [
            Mock(status="done"),
            Mock(status="done"),
            Mock(status="in_progress"),
            Mock(status="blocked"),
            Mock(status="todo"),
        ]

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.get_children = AsyncMock(return_value=children)

        result = await service.get_item_progress("item-1", "proj-1")

        assert result["total"] == 5
        assert result["done"] == 2
        assert result["in_progress"] == 1
        assert result["blocked"] == 1
        assert result["todo"] == 1
        assert result["percentage"] == 40

    @pytest.mark.asyncio
    async def test_progress_item_not_found(self, service):
        """Test progress for non-existent item."""
        service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await service.get_item_progress("nonexistent", "proj-1")

    @pytest.mark.asyncio
    async def test_progress_percentage_calculation(self, service):
        """Test percentage calculation precision."""
        item = Mock(id="item-1", status="in_progress")
        children = [Mock(status="done") for _ in range(3)] + [Mock(status="todo") for _ in range(7)]

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.get_children = AsyncMock(return_value=children)

        result = await service.get_item_progress("item-1", "proj-1")

        assert result["percentage"] == 30  # 3/10 = 30%


class TestBulkUpdatePreview:
    """Test bulk_update_preview method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_bulk_update_preview(self, service):
        """Test bulk update preview returns correct structure."""
        items = [
            Mock(id="1", title="Item 1", status="todo", priority="low"),
            Mock(id="2", title="Item 2", status="todo", priority="medium"),
        ]
        service.items.list_by_filters = AsyncMock(return_value=items)

        result = await service.bulk_update_preview(
            filters={"status": "todo"},
            updates={"status": "in_progress", "priority": "high"},
            project_id="proj-1",
        )

        assert result["total_items"] == 2
        assert len(result["affected_items"]) == 2
        assert result["updates"] == {"status": "in_progress", "priority": "high"}

    @pytest.mark.asyncio
    async def test_bulk_update_preview_no_matches(self, service):
        """Test preview with no matching items."""
        service.items.list_by_filters = AsyncMock(return_value=[])

        result = await service.bulk_update_preview(
            filters={"status": "nonexistent"},
            updates={"priority": "high"},
            project_id="proj-1",
        )

        assert result["total_items"] == 0
        assert result["affected_items"] == []


class TestBulkUpdateItems:
    """Test bulk_update_items method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_bulk_update_empty(self, service):
        """Test bulk update with no matching items."""
        service.items.list_by_filters = AsyncMock(return_value=[])

        result = await service.bulk_update_items(
            filters={"status": "nonexistent"},
            updates={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is True
        assert result["updated"] == 0
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_bulk_update_success(self, service):
        """Test successful bulk update."""
        items = [Mock(id="1", version=1), Mock(id="2", version=1), Mock(id="3", version=1)]
        service.items.list_by_filters = AsyncMock(return_value=items)
        service.items.update = AsyncMock()
        service.events.log = AsyncMock()

        result = await service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is True
        assert result["updated"] == 3
        assert result["failed"] == 0
        assert service.events.log.call_count == 3

    @pytest.mark.asyncio
    async def test_bulk_update_partial_failure(self, service):
        """Test bulk update with some failures."""
        items = [Mock(id="1", version=1), Mock(id="2", version=1), Mock(id="3", version=1)]
        service.items.list_by_filters = AsyncMock(return_value=items)

        # First and third succeed, second fails
        service.items.update = AsyncMock(
            side_effect=[Mock(), Exception("Conflict error"), Mock()]
        )
        service.events.log = AsyncMock()

        result = await service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is False
        assert result["updated"] == 2
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_bulk_update_all_failures(self, service):
        """Test bulk update where all updates fail."""
        items = [Mock(id="1", version=1), Mock(id="2", version=1)]
        service.items.list_by_filters = AsyncMock(return_value=items)
        service.items.update = AsyncMock(side_effect=Exception("Database error"))
        service.events.log = AsyncMock()

        result = await service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is False
        assert result["updated"] == 0
        assert result["failed"] == 2


class TestBulkDeleteItems:
    """Test bulk_delete_items method."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_bulk_delete_empty(self, service):
        """Test bulk delete with no matching items."""
        service.items.list_by_filters = AsyncMock(return_value=[])

        result = await service.bulk_delete_items(
            filters={"status": "cancelled"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is True
        assert result["deleted"] == 0

    @pytest.mark.asyncio
    async def test_bulk_delete_soft(self, service):
        """Test bulk soft delete."""
        items = [Mock(id="1"), Mock(id="2")]
        service.items.list_by_filters = AsyncMock(return_value=items)
        service.items.soft_delete = AsyncMock()
        service.events.log = AsyncMock()

        result = await service.bulk_delete_items(
            filters={"status": "cancelled"},
            agent_id="agent-1",
            project_id="proj-1",
            soft_delete=True,
        )

        assert result["success"] is True
        assert result["deleted"] == 2
        assert service.items.soft_delete.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_delete_hard(self, service):
        """Test bulk hard delete."""
        items = [Mock(id="1"), Mock(id="2"), Mock(id="3")]
        service.items.list_by_filters = AsyncMock(return_value=items)
        service.items.delete = AsyncMock()
        service.events.log = AsyncMock()

        result = await service.bulk_delete_items(
            filters={"status": "cancelled"},
            agent_id="agent-1",
            project_id="proj-1",
            soft_delete=False,
        )

        assert result["success"] is True
        assert result["deleted"] == 3
        service.items.delete.assert_called()

    @pytest.mark.asyncio
    async def test_bulk_delete_with_failures(self, service):
        """Test bulk delete with some failures."""
        items = [Mock(id="1"), Mock(id="2")]
        service.items.list_by_filters = AsyncMock(return_value=items)
        service.items.soft_delete = AsyncMock(
            side_effect=[None, Exception("Delete failed")]
        )
        service.events.log = AsyncMock()

        result = await service.bulk_delete_items(
            filters={"status": "cancelled"},
            agent_id="agent-1",
            project_id="proj-1",
            soft_delete=True,
        )

        assert result["success"] is False
        assert result["deleted"] == 1
        assert result["failed"] == 1


class TestQueryByRelationship:
    """Test query_by_relationship method (stub)."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        return service

    @pytest.mark.asyncio
    async def test_query_by_relationship_returns_empty(self, service):
        """Test that stub returns empty list."""
        result = await service.query_by_relationship("proj-1", "item-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_with_link_type(self, service):
        """Test query with link type filter."""
        result = await service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            link_type="depends_on",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_outgoing(self, service):
        """Test query with outgoing direction."""
        result = await service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            direction="outgoing",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_incoming(self, service):
        """Test query with incoming direction."""
        result = await service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            direction="incoming",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_both(self, service):
        """Test query with both directions."""
        result = await service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            direction="both",
        )

        assert result == []


class TestStatusTransitionsConstants:
    """Test STATUS_TRANSITIONS and VALID_STATUSES constants."""

    def test_valid_statuses_contains_all_states(self):
        """Test that all valid statuses are defined."""
        assert "todo" in VALID_STATUSES
        assert "in_progress" in VALID_STATUSES
        assert "blocked" in VALID_STATUSES
        assert "done" in VALID_STATUSES
        assert len(VALID_STATUSES) == 4

    def test_status_transitions_defined_for_all_statuses(self):
        """Test that transitions are defined for all valid statuses."""
        for status in VALID_STATUSES:
            assert status in STATUS_TRANSITIONS

    def test_transitions_are_valid_statuses(self):
        """Test that all transition targets are valid statuses."""
        for status, transitions in STATUS_TRANSITIONS.items():
            for target in transitions:
                assert target in VALID_STATUSES

    def test_todo_transitions(self):
        """Test todo status transitions."""
        assert "in_progress" in STATUS_TRANSITIONS["todo"]
        assert "blocked" in STATUS_TRANSITIONS["todo"]

    def test_in_progress_transitions(self):
        """Test in_progress status transitions."""
        assert "done" in STATUS_TRANSITIONS["in_progress"]
        assert "blocked" in STATUS_TRANSITIONS["in_progress"]
        assert "todo" in STATUS_TRANSITIONS["in_progress"]

    def test_blocked_transitions(self):
        """Test blocked status transitions."""
        assert "todo" in STATUS_TRANSITIONS["blocked"]
        assert "in_progress" in STATUS_TRANSITIONS["blocked"]

    def test_done_transitions(self):
        """Test done status transitions (allow reopening)."""
        assert "todo" in STATUS_TRANSITIONS["done"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repositories."""
        session = AsyncMock()
        service = ItemService(session)
        service.items = AsyncMock()
        service.links = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_item_with_empty_metadata(self, service):
        """Test creating item with empty metadata dict."""
        created_item = Mock(id="item-1", title="Test", view="REQ", item_type="feature", status="todo", owner=None, priority="medium")
        service.items.create = AsyncMock(return_value=created_item)
        service.events.log = AsyncMock()

        await service.create_item(
            project_id="proj-1",
            title="Test",
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
            metadata={},
        )

        service.items.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_items_zero_limit(self, service):
        """Test listing items with limit of 0."""
        service.items.get_by_project = AsyncMock(return_value=[])

        await service.list_items("proj-1", limit=0)

        service.items.get_by_project.assert_called_once_with(
            "proj-1", status=None, limit=0, offset=0
        )

    @pytest.mark.asyncio
    async def test_update_metadata_with_nested_dict(self, service):
        """Test updating metadata with nested dictionary."""
        item = Mock(id="item-1", version=1, item_metadata={}, project_id="proj-1")
        updated_item = Mock(id="item-1", version=2, project_id="proj-1")

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        with patch("tracertm.services.item_service.update_with_retry") as mock_retry:
            async def execute_callback(callback):
                return await callback()
            mock_retry.side_effect = execute_callback

            nested_metadata = {
                "level1": {
                    "level2": {
                        "level3": "value"
                    }
                }
            }

            await service.update_metadata("item-1", "agent-1", nested_metadata)

            service.items.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_update_single_item(self, service):
        """Test bulk update with only one item."""
        items = [Mock(id="1", version=1)]
        service.items.list_by_filters = AsyncMock(return_value=items)
        service.items.update = AsyncMock()
        service.events.log = AsyncMock()

        result = await service.bulk_update_items(
            filters={"id": "1"},
            updates={"priority": "high"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["updated"] == 1

    @pytest.mark.asyncio
    async def test_create_item_with_very_long_title(self, service):
        """Test creating item with very long title."""
        long_title = "A" * 500
        created_item = Mock(id="item-1", title=long_title, view="REQ", item_type="feature", status="todo", owner=None, priority="medium")
        service.items.create = AsyncMock(return_value=created_item)
        service.events.log = AsyncMock()

        result = await service.create_item(
            project_id="proj-1",
            title=long_title,
            view="REQ",
            item_type="feature",
            agent_id="agent-1",
        )

        assert len(result.title) == 500

    @pytest.mark.asyncio
    async def test_progress_with_single_child(self, service):
        """Test progress calculation with single child."""
        item = Mock(id="item-1", status="in_progress")
        children = [Mock(status="done")]

        service.items.get_by_id = AsyncMock(return_value=item)
        service.items.get_children = AsyncMock(return_value=children)

        result = await service.get_item_progress("item-1", "proj-1")

        assert result["total"] == 1
        assert result["done"] == 1
        assert result["percentage"] == 100
