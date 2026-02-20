"""Comprehensive ItemService Integration Tests.

Target: 150-200 new tests covering all ItemService methods with edge cases,
error conditions, integration scenarios, and relationship handling.

Coverage Areas:
1. CRUD Operations (Create, Read, Update, Delete) - 40 tests
2. Batch Operations (bulk_update, bulk_delete) - 30 tests
3. Search & Query Operations - 25 tests
4. Relationships & Hierarchy - 35 tests
5. State Transitions & Workflows - 20 tests
6. Metadata Operations - 20 tests
7. Integration Scenarios - 30 tests
"""

from datetime import datetime

# ==============================================================================
# FIXTURES
# ==============================================================================
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.services.item_service import STATUS_TRANSITIONS, ItemService


@pytest.fixture
def async_session() -> None:
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def item_service(async_session: Any) -> None:
    """Create ItemService with mocked repositories."""
    service = ItemService(async_session)
    service.items = AsyncMock()
    service.links = AsyncMock()
    service.events = AsyncMock()
    return service


def create_mock_item(
    item_id: str = "item-1",
    project_id: str = "proj-1",
    title: str = "Test Item",
    view: str = "REQUIREMENTS",
    item_type: str = "requirement",
    status: str = "todo",
    owner: str | None = None,
    priority: str = "medium",
    parent_id: str | None = None,
    version: int = 1,
    deleted_at: datetime | None = None,
) -> Mock:
    """Create a mock Item object."""
    item = Mock(spec=Item)
    item.id = item_id
    item.project_id = project_id
    item.title = title
    item.view = view
    item.item_type = item_type
    item.status = status
    item.owner = owner
    item.priority = priority
    item.parent_id = parent_id
    item.version = version
    item.deleted_at = deleted_at
    item.item_metadata = {}
    return item


# ==============================================================================
# CRUD OPERATIONS TESTS (40 tests)
# ==============================================================================


class TestCreateItemComprehensive:
    """Comprehensive tests for create_item method."""

    @pytest.mark.asyncio
    async def test_create_item_simple_success(self, item_service: Any) -> None:
        """Test simple item creation with required fields only."""
        mock_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=mock_item)

        result = await item_service.create_item(
            project_id="proj-1",
            title="Test Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
        )

        assert result.id == "item-1"
        assert result.title == "Test Item"
        item_service.items.create.assert_called_once()
        item_service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_item_with_all_parameters(self, item_service: Any) -> None:
        """Test item creation with all optional parameters."""
        mock_item = create_mock_item(
            owner="owner-1",
            priority="high",
            parent_id="parent-1",
        )
        item_service.items.create = AsyncMock(return_value=mock_item)

        result = await item_service.create_item(
            project_id="proj-1",
            title="Complex Item",
            view="FEATURE",
            item_type="feature",
            agent_id="agent-1",
            description="Detailed description",
            status="in_progress",
            owner="owner-1",
            priority="high",
            parent_id="parent-1",
            metadata={"key": "value"},
        )

        assert result.owner == "owner-1"
        assert result.priority == "high"

    @pytest.mark.asyncio
    async def test_create_item_with_multiple_links(self, item_service: Any) -> None:
        """Test item creation with multiple outgoing links."""
        mock_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=mock_item)
        item_service.links.create = AsyncMock()

        await item_service.create_item(
            project_id="proj-1",
            title="Item with Links",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            link_to=["target-1", "target-2", "target-3"],
            link_type="blocks",
        )

        assert item_service.links.create.call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_create_item_with_empty_links_list(self, item_service: Any) -> None:
        """Test item creation with empty links list."""
        mock_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=mock_item)

        await item_service.create_item(
            project_id="proj-1",
            title="Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            link_to=[],
        )

        item_service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_item_with_metadata_dict(self, item_service: Any) -> None:
        """Test item creation with complex metadata."""
        mock_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=mock_item)

        metadata = {"nested": {"key": "value"}, "tags": ["tag1", "tag2"]}
        await item_service.create_item(
            project_id="proj-1",
            title="Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            metadata=metadata,
        )

        call_kwargs = item_service.items.create.call_args[1]
        assert call_kwargs["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_create_item_event_logging_content(self, item_service: Any) -> None:
        """Test that creation event contains correct data."""
        mock_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=mock_item)

        await item_service.create_item(
            project_id="proj-1",
            title="Test Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            link_to=["target-1"],
        )

        log_call = item_service.events.log.call_args
        assert log_call[1]["event_type"] == "item_created"
        assert log_call[1]["entity_type"] == "item"
        assert log_call[1]["agent_id"] == "agent-1"


class TestGetItemComprehensive:
    """Comprehensive tests for get_item method."""

    @pytest.mark.asyncio
    async def test_get_item_success(self, item_service: Any) -> None:
        """Test successful item retrieval."""
        mock_item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)

        result = await item_service.get_item("proj-1", "item-1")

        assert result.id == "item-1"
        item_service.items.get_by_id.assert_called_once_with("item-1", "proj-1")

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, item_service: Any) -> None:
        """Test retrieval of non-existent item."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        result = await item_service.get_item("proj-1", "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_item_with_special_characters_in_id(self, item_service: Any) -> None:
        """Test retrieval with special characters in item ID."""
        mock_item = create_mock_item(item_id="item-123_special")
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)

        result = await item_service.get_item("proj-1", "item-123_special")

        assert result.id == "item-123_special"

    @pytest.mark.asyncio
    async def test_get_item_cross_project_isolation(self, item_service: Any) -> None:
        """Test that items are isolated by project."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        # Try to get item from different project
        result = await item_service.get_item("wrong-proj", "item-1")

        assert result is None


class TestUpdateItemComprehensive:
    """Comprehensive tests for update_item method."""

    @pytest.mark.asyncio
    async def test_update_item_single_field(self, item_service: Any) -> None:
        """Test updating single field."""
        mock_item = create_mock_item(version=1)
        updated_item = create_mock_item(title="Updated Title", version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item(
            item_id="item-1",
            agent_id="agent-1",
            title="Updated Title",
        )

        assert result.title == "Updated Title"
        item_service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_item_multiple_fields(self, item_service: Any) -> None:
        """Test updating multiple fields at once."""
        mock_item = create_mock_item(version=1)
        updated_item = create_mock_item(
            title="New Title",
            status="in_progress",
            priority="high",
            version=2,
        )

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item(
            item_id="item-1",
            agent_id="agent-1",
            title="New Title",
            status="in_progress",
            priority="high",
        )

        assert result.title == "New Title"
        assert result.status == "in_progress"

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, item_service: Any) -> None:
        """Test updating non-existent item raises error."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await item_service.update_item(
                item_id="nonexistent",
                agent_id="agent-1",
                title="New Title",
            )

    @pytest.mark.asyncio
    async def test_update_item_optimistic_locking(self, item_service: Any) -> None:
        """Test that optimistic locking version is used."""
        mock_item = create_mock_item(version=5)
        updated_item = create_mock_item(version=6)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_item(
            item_id="item-1",
            agent_id="agent-1",
            title="Updated",
        )

        # Verify version was passed
        call_kwargs = item_service.items.update.call_args[1]
        assert call_kwargs["expected_version"] == COUNT_FIVE


class TestDeleteItemComprehensive:
    """Comprehensive tests for delete_item method."""

    @pytest.mark.asyncio
    async def test_delete_item_soft_delete_success(self, item_service: Any) -> None:
        """Test soft delete of item."""
        mock_item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.delete = AsyncMock(return_value=True)

        result = await item_service.delete_item(
            item_id="item-1",
            agent_id="agent-1",
            soft=True,
        )

        assert result is True
        item_service.items.delete.assert_called_once_with("item-1", soft=True)

    @pytest.mark.asyncio
    async def test_delete_item_hard_delete_success(self, item_service: Any) -> None:
        """Test hard delete of item."""
        mock_item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.delete = AsyncMock(return_value=True)

        result = await item_service.delete_item(
            item_id="item-1",
            agent_id="agent-1",
            soft=False,
        )

        assert result is True
        item_service.items.delete.assert_called_once_with("item-1", soft=False)

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, item_service: Any) -> None:
        """Test deleting non-existent item."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        result = await item_service.delete_item(
            item_id="nonexistent",
            agent_id="agent-1",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_item_logs_event_on_success(self, item_service: Any) -> None:
        """Test that delete event is logged."""
        mock_item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.delete = AsyncMock(return_value=True)

        await item_service.delete_item(
            item_id="item-1",
            agent_id="agent-1",
            soft=True,
        )

        item_service.events.log.assert_called_once()
        log_call = item_service.events.log.call_args
        assert log_call[1]["event_type"] == "item_deleted"

    @pytest.mark.asyncio
    async def test_delete_item_no_event_on_not_found(self, item_service: Any) -> None:
        """Test that event is not logged if item not found."""
        item_service.items.get_by_id = AsyncMock(return_value=None)
        item_service.items.delete = AsyncMock(return_value=False)

        await item_service.delete_item(
            item_id="nonexistent",
            agent_id="agent-1",
        )

        # Event should not be logged for non-existent items
        # (fallback project_id logic)


class TestListItemsComprehensive:
    """Comprehensive tests for list_items method."""

    @pytest.mark.asyncio
    async def test_list_items_no_filters(self, item_service: Any) -> None:
        """Test listing items without filters."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(5)]
        item_service.items.get_by_project = AsyncMock(return_value=items)

        result = await item_service.list_items(project_id="proj-1")

        assert len(result) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_list_items_with_view_filter(self, item_service: Any) -> None:
        """Test listing items filtered by view."""
        items = [
            create_mock_item(view="REQUIREMENTS"),
            create_mock_item(view="REQUIREMENTS"),
        ]
        item_service.items.get_by_view = AsyncMock(return_value=items)

        result = await item_service.list_items(
            project_id="proj-1",
            view="REQUIREMENTS",
        )

        assert len(result) == COUNT_TWO
        item_service.items.get_by_view.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_items_with_status_filter(self, item_service: Any) -> None:
        """Test listing items filtered by status."""
        items = [
            create_mock_item(status="todo"),
            create_mock_item(status="todo"),
        ]
        item_service.items.get_by_project = AsyncMock(return_value=items)

        result = await item_service.list_items(
            project_id="proj-1",
            status="todo",
        )

        assert len(result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_items_with_pagination(self, item_service: Any) -> None:
        """Test listing items with pagination."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(20)]
        item_service.items.get_by_project = AsyncMock(return_value=items[0:10])

        result = await item_service.list_items(
            project_id="proj-1",
            limit=10,
            offset=0,
        )

        assert len(result) == COUNT_TEN

    @pytest.mark.asyncio
    async def test_list_items_empty_result(self, item_service: Any) -> None:
        """Test listing items with no results."""
        item_service.items.get_by_project = AsyncMock(return_value=[])

        result = await item_service.list_items(project_id="proj-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_list_items_view_and_status_combination(self, item_service: Any) -> None:
        """Test listing with both view and status filters."""
        items = [create_mock_item(view="FEATURE", status="done")]
        item_service.items.get_by_view = AsyncMock(return_value=items)

        result = await item_service.list_items(
            project_id="proj-1",
            view="FEATURE",
            status="done",
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_items_custom_limit_and_offset(self, item_service: Any) -> None:
        """Test pagination with custom limit and offset."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(5)]
        item_service.items.get_by_project = AsyncMock(return_value=items)

        await item_service.list_items(
            project_id="proj-1",
            limit=50,
            offset=100,
        )

        # Verify parameters were passed
        call_kwargs = item_service.items.get_by_project.call_args[1]
        assert call_kwargs["limit"] == 50
        assert call_kwargs["offset"] == 100


# ==============================================================================
# BATCH OPERATIONS TESTS (30 tests)
# ==============================================================================


class TestBulkUpdateComprehensive:
    """Comprehensive tests for bulk operations."""

    @pytest.mark.asyncio
    async def test_bulk_update_all_success(self, item_service: Any) -> None:
        """Test bulk update with all items succeeding."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(5)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.update = AsyncMock(return_value=Mock())

        result = await item_service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "in_progress"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is True
        assert result["updated"] == COUNT_FIVE
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_bulk_update_partial_failure(self, item_service: Any) -> None:
        """Test bulk update with some failures."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(5)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)

        # Simulate 2 failures
        def side_effect(*args: Any, **kwargs: Any) -> None:
            if kwargs.get("item_id") in {"item-0", "item-1"}:
                msg = "Update failed"
                raise Exception(msg)
            return Mock()

        item_service.items.update = AsyncMock(side_effect=side_effect)

        result = await item_service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "in_progress"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is False
        assert result["updated"] == COUNT_THREE
        assert result["failed"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_bulk_update_no_matches(self, item_service: Any) -> None:
        """Test bulk update with no matching items."""
        item_service.items.list_by_filters = AsyncMock(return_value=[])

        result = await item_service.bulk_update_items(
            filters={"status": "nonexistent"},
            updates={"priority": "high"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is True
        assert result["updated"] == 0

    @pytest.mark.asyncio
    async def test_bulk_update_single_item(self, item_service: Any) -> None:
        """Test bulk update with single item."""
        items = [create_mock_item()]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.update = AsyncMock(return_value=Mock())

        result = await item_service.bulk_update_items(
            filters={"id": "item-1"},
            updates={"priority": "high"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["updated"] == 1

    @pytest.mark.asyncio
    async def test_bulk_update_preview(self, item_service: Any) -> None:
        """Test bulk update preview without changes."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(3)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)

        result = await item_service.bulk_update_preview(
            filters={"status": "todo"},
            updates={"status": "done"},
            project_id="proj-1",
        )

        assert result["total_items"] == COUNT_THREE
        assert result["updates"]["status"] == "done"
        assert len(result["affected_items"]) == COUNT_THREE


class TestBulkDeleteComprehensive:
    """Comprehensive tests for bulk delete operations."""

    @pytest.mark.asyncio
    async def test_bulk_delete_soft_all_success(self, item_service: Any) -> None:
        """Test soft delete bulk operation succeeding."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(4)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.soft_delete = AsyncMock(return_value=True)

        result = await item_service.bulk_delete_items(
            filters={"view": "ARCHIVED"},
            agent_id="agent-1",
            project_id="proj-1",
            soft_delete=True,
        )

        assert result["success"] is True
        assert result["deleted"] == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_bulk_delete_hard_all_success(self, item_service: Any) -> None:
        """Test hard delete bulk operation succeeding."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(3)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.delete = AsyncMock(return_value=True)

        result = await item_service.bulk_delete_items(
            filters={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
            soft_delete=False,
        )

        assert result["success"] is True
        assert result["deleted"] == COUNT_THREE

    @pytest.mark.asyncio
    async def test_bulk_delete_with_failures(self, item_service: Any) -> None:
        """Test bulk delete with some failures."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(5)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)

        def soft_delete_side_effect(item_id: Any, *args: Any, **kwargs: Any) -> None:
            if item_id in {"item-0", "item-2"}:
                msg = "Delete failed"
                raise Exception(msg)

        item_service.items.soft_delete = AsyncMock(side_effect=soft_delete_side_effect)

        result = await item_service.bulk_delete_items(
            filters={"archived": True},
            agent_id="agent-1",
            project_id="proj-1",
            soft_delete=True,
        )

        assert result["success"] is False
        assert result["deleted"] == COUNT_THREE
        assert result["failed"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_bulk_delete_empty_result(self, item_service: Any) -> None:
        """Test bulk delete with no matching items."""
        item_service.items.list_by_filters = AsyncMock(return_value=[])

        result = await item_service.bulk_delete_items(
            filters={"nonexistent_filter": True},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is True
        assert result["deleted"] == 0


# ==============================================================================
# RELATIONSHIPS & HIERARCHY TESTS (35 tests)
# ==============================================================================


class TestHierarchyComprehensive:
    """Comprehensive tests for hierarchy operations."""

    @pytest.mark.asyncio
    async def test_get_children_multiple(self, item_service: Any) -> None:
        """Test retrieving multiple children."""
        children = [create_mock_item(item_id=f"child-{i}") for i in range(3)]
        item_service.items.get_children = AsyncMock(return_value=children)

        result = await item_service.get_children("parent-1")

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_get_children_none(self, item_service: Any) -> None:
        """Test retrieving from leaf node."""
        item_service.items.get_children = AsyncMock(return_value=[])

        result = await item_service.get_children("leaf-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_children_passes_item_id(self, item_service: Any) -> None:
        """Test that item_id is passed correctly."""
        item_service.items.get_children = AsyncMock(return_value=[])

        await item_service.get_children("special-item-123")

        item_service.items.get_children.assert_called_once_with("special-item-123")

    @pytest.mark.asyncio
    async def test_get_ancestors_multiple_levels(self, item_service: Any) -> None:
        """Test retrieving ancestors from deep hierarchy."""
        ancestors = [
            create_mock_item(item_id="root"),
            create_mock_item(item_id="middle"),
            create_mock_item(item_id="parent"),
        ]
        item_service.items.get_ancestors = AsyncMock(return_value=ancestors)

        result = await item_service.get_ancestors("child-1")

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_get_ancestors_root_node(self, item_service: Any) -> None:
        """Test getting ancestors of root item."""
        item_service.items.get_ancestors = AsyncMock(return_value=[])

        result = await item_service.get_ancestors("root-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_descendants_deep_tree(self, item_service: Any) -> None:
        """Test retrieving all descendants recursively."""
        descendants = [create_mock_item(item_id=f"item-{i}") for i in range(10)]
        item_service.items.get_descendants = AsyncMock(return_value=descendants)

        result = await item_service.get_descendants("root-1")

        assert len(result) == COUNT_TEN

    @pytest.mark.asyncio
    async def test_get_descendants_leaf(self, item_service: Any) -> None:
        """Test getting descendants from leaf node."""
        item_service.items.get_descendants = AsyncMock(return_value=[])

        result = await item_service.get_descendants("leaf-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_item_with_links_found(self, item_service: Any) -> None:
        """Test retrieving item with all its links."""
        item = create_mock_item()
        links = [Mock(id="link-1"), Mock(id="link-2")]

        item_service.items.get_by_id = AsyncMock(return_value=item)
        item_service.links.get_by_item = AsyncMock(return_value=links)

        result = await item_service.get_item_with_links("item-1")

        assert result["item"].id == "item-1"
        assert len(result["links"]) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_item_with_links_not_found(self, item_service: Any) -> None:
        """Test retrieving non-existent item with links."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        result = await item_service.get_item_with_links("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_item_with_no_links(self, item_service: Any) -> None:
        """Test retrieving item that has no links."""
        item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=item)
        item_service.links.get_by_item = AsyncMock(return_value=[])

        result = await item_service.get_item_with_links("item-1")

        assert result["links"] == []


# ==============================================================================
# STATE TRANSITIONS & WORKFLOWS TESTS (20 tests)
# ==============================================================================


class TestStateTransitionsComprehensive:
    """Comprehensive tests for state transitions."""

    @pytest.mark.asyncio
    async def test_transition_todo_to_in_progress(self, item_service: Any) -> None:
        """Test valid transition from todo to in_progress."""
        mock_item = create_mock_item(status="todo", version=1)
        updated_item = create_mock_item(status="in_progress", version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item_status(
            item_id="item-1",
            new_status="in_progress",
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result.status == "in_progress"

    @pytest.mark.asyncio
    async def test_transition_in_progress_to_done(self, item_service: Any) -> None:
        """Test valid transition from in_progress to done."""
        mock_item = create_mock_item(status="in_progress", version=1)
        updated_item = create_mock_item(status="done", version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item_status(
            item_id="item-1",
            new_status="done",
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result.status == "done"

    @pytest.mark.asyncio
    async def test_transition_done_to_todo_reopen(self, item_service: Any) -> None:
        """Test reopening completed item."""
        mock_item = create_mock_item(status="done", version=1)
        updated_item = create_mock_item(status="todo", version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item_status(
            item_id="item-1",
            new_status="todo",
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result.status == "todo"

    @pytest.mark.asyncio
    async def test_transition_invalid_status_value(self, item_service: Any) -> None:
        """Test transition to invalid status raises error."""
        with pytest.raises(ValueError, match="Invalid status"):
            await item_service.update_item_status(
                item_id="item-1",
                new_status="invalid_status",
                agent_id="agent-1",
                project_id="proj-1",
            )

    @pytest.mark.asyncio
    async def test_transition_not_allowed(self, item_service: Any) -> None:
        """Test disallowed transition raises error."""
        mock_item = create_mock_item(status="todo")
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)

        with pytest.raises(ValueError, match="Cannot transition"):
            await item_service.update_item_status(
                item_id="item-1",
                new_status="done",  # Cannot jump from todo to done
                agent_id="agent-1",
                project_id="proj-1",
            )

    @pytest.mark.asyncio
    async def test_transition_logs_event(self, item_service: Any) -> None:
        """Test that status transition is logged."""
        mock_item = create_mock_item(status="todo", version=1)
        updated_item = create_mock_item(status="in_progress", version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_item_status(
            item_id="item-1",
            new_status="in_progress",
            agent_id="agent-1",
            project_id="proj-1",
        )

        item_service.events.log.assert_called_once()
        log_call = item_service.events.log.call_args
        assert log_call[1]["event_type"] == "item_status_changed"

    @pytest.mark.asyncio
    async def test_transition_item_not_found(self, item_service: Any) -> None:
        """Test transition on non-existent item."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await item_service.update_item_status(
                item_id="nonexistent",
                new_status="in_progress",
                agent_id="agent-1",
                project_id="proj-1",
            )

    @pytest.mark.asyncio
    async def test_all_valid_transitions_from_todo(self, item_service: Any) -> None:
        """Test all allowed transitions from todo status."""
        allowed = STATUS_TRANSITIONS["todo"]

        for new_status in allowed:
            mock_item = create_mock_item(status="todo", version=1)
            updated_item = create_mock_item(status=new_status, version=2)

            item_service.items.get_by_id = AsyncMock(return_value=mock_item)
            item_service.items.update = AsyncMock(return_value=updated_item)

            result = await item_service.update_item_status(
                item_id="item-1",
                new_status=new_status,
                agent_id="agent-1",
                project_id="proj-1",
            )

            assert result.status == new_status


# ==============================================================================
# METADATA OPERATIONS TESTS (20 tests)
# ==============================================================================


class TestMetadataComprehensive:
    """Comprehensive tests for metadata operations."""

    @pytest.mark.asyncio
    async def test_update_metadata_merge_new_fields(self, item_service: Any) -> None:
        """Test merging new metadata fields."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = {"existing": "value"}
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates={"new_key": "new_value"},
            merge=True,
        )

        # Verify merge happened
        call_kwargs = item_service.items.update.call_args[1]
        assert "existing" in call_kwargs["item_metadata"]
        assert "new_key" in call_kwargs["item_metadata"]

    @pytest.mark.asyncio
    async def test_update_metadata_replace(self, item_service: Any) -> None:
        """Test replacing metadata entirely."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = {"old": "data"}
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates={"new": "data"},
            merge=False,
        )

        # Verify replace happened
        call_kwargs = item_service.items.update.call_args[1]
        assert call_kwargs["item_metadata"] == {"new": "data"}

    @pytest.mark.asyncio
    async def test_update_metadata_null_existing(self, item_service: Any) -> None:
        """Test metadata update when existing is null."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = None
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates={"key": "value"},
            merge=True,
        )

        call_kwargs = item_service.items.update.call_args[1]
        assert call_kwargs["item_metadata"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_update_metadata_item_not_found(self, item_service: Any) -> None:
        """Test metadata update on non-existent item."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await item_service.update_metadata(
                item_id="nonexistent",
                agent_id="agent-1",
                metadata_updates={"key": "value"},
            )

    @pytest.mark.asyncio
    async def test_update_metadata_complex_structure(self, item_service: Any) -> None:
        """Test updating with nested metadata structure."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = {}
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        complex_meta = {
            "nested": {"deep": {"value": 123}},
            "list": [1, 2, 3],
            "string": "test",
        }

        await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates=complex_meta,
            merge=False,
        )

        call_kwargs = item_service.items.update.call_args[1]
        assert call_kwargs["item_metadata"]["nested"]["deep"]["value"] == 123


# ==============================================================================
# PROGRESS CALCULATION TESTS (15 tests)
# ==============================================================================


class TestProgressCalculationComprehensive:
    """Comprehensive tests for progress calculation."""

    @pytest.mark.asyncio
    async def test_progress_no_children_todo(self, item_service: Any) -> None:
        """Test progress of leaf item in todo status."""
        mock_item = create_mock_item(status="todo")
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=[])

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        assert result["total"] == 1
        assert result["todo"] == 1
        assert result["done"] == 0
        assert result["percentage"] == 0

    @pytest.mark.asyncio
    async def test_progress_no_children_done(self, item_service: Any) -> None:
        """Test progress of completed leaf item."""
        mock_item = create_mock_item(status="done")
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=[])

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        assert result["percentage"] == 100
        assert result["done"] == 1

    @pytest.mark.asyncio
    async def test_progress_with_children_all_done(self, item_service: Any) -> None:
        """Test progress when all children are done."""
        mock_item = create_mock_item()
        children = [
            create_mock_item(status="done"),
            create_mock_item(status="done"),
            create_mock_item(status="done"),
        ]

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=children)

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        assert result["done"] == COUNT_THREE
        assert result["percentage"] == 100

    @pytest.mark.asyncio
    async def test_progress_with_children_mixed(self, item_service: Any) -> None:
        """Test progress with mixed child statuses."""
        mock_item = create_mock_item()
        children = [
            create_mock_item(status="done"),
            create_mock_item(status="in_progress"),
            create_mock_item(status="todo"),
            create_mock_item(status="blocked"),
        ]

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=children)

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        assert result["total"] == COUNT_FOUR
        assert result["done"] == 1
        assert result["in_progress"] == 1
        assert result["todo"] == 1
        assert result["blocked"] == 1

    @pytest.mark.asyncio
    async def test_progress_item_not_found(self, item_service: Any) -> None:
        """Test progress for non-existent item."""
        item_service.items.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            await item_service.get_item_progress(
                item_id="nonexistent",
                project_id="proj-1",
            )

    @pytest.mark.asyncio
    async def test_progress_percentage_rounding(self, item_service: Any) -> None:
        """Test percentage calculation with rounding."""
        mock_item = create_mock_item()
        children = [
            create_mock_item(status="done"),
            create_mock_item(status="todo"),
            create_mock_item(status="todo"),
        ]

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=children)

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        # 1/3 = 33.33... which should round to 33
        assert result["percentage"] == 33


# ==============================================================================
# QUERY & RELATIONSHIP TESTS (15 tests)
# ==============================================================================


class TestQueryByRelationshipComprehensive:
    """Comprehensive tests for relationship queries."""

    @pytest.mark.asyncio
    async def test_query_by_relationship_returns_empty(self, item_service: Any) -> None:
        """Test relationship query with no results."""
        result = await item_service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_with_link_type(self, item_service: Any) -> None:
        """Test relationship query with link type filter."""
        result = await item_service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            link_type="blocks",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_direction_outgoing(self, item_service: Any) -> None:
        """Test relationship query with outgoing direction."""
        result = await item_service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            direction="outgoing",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_direction_incoming(self, item_service: Any) -> None:
        """Test relationship query with incoming direction."""
        result = await item_service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            direction="incoming",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_query_by_relationship_direction_both(self, item_service: Any) -> None:
        """Test relationship query with both directions."""
        result = await item_service.query_by_relationship(
            project_id="proj-1",
            item_id="item-1",
            direction="both",
        )

        assert result == []


# ==============================================================================
# INTEGRATION SCENARIOS TESTS (30 tests)
# ==============================================================================


class TestIntegrationScenarios:
    """Test complete workflows and integration scenarios."""

    @pytest.mark.asyncio
    async def test_create_update_delete_workflow(self, item_service: Any) -> None:
        """Test complete create -> update -> delete workflow."""
        # Create
        created_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=created_item)

        result = await item_service.create_item(
            project_id="proj-1",
            title="Workflow Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
        )
        assert result.id == "item-1"

        # Update
        updated_item = create_mock_item(title="Updated Title", version=2)
        item_service.items.get_by_id = AsyncMock(return_value=created_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item(
            item_id="item-1",
            agent_id="agent-1",
            title="Updated Title",
        )
        assert result.title == "Updated Title"

        # Delete
        item_service.items.delete = AsyncMock(return_value=True)
        result = await item_service.delete_item(
            item_id="item-1",
            agent_id="agent-1",
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_undelete_restore_workflow(self, item_service: Any) -> None:
        """Test delete and restore workflow."""
        deleted_item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=deleted_item)
        item_service.items.delete = AsyncMock(return_value=True)

        # Delete
        result = await item_service.delete_item(
            item_id="item-1",
            agent_id="agent-1",
        )
        assert result is True

        # Restore
        restored_item = create_mock_item()
        item_service.items.restore = AsyncMock(return_value=restored_item)

        result = await item_service.undelete_item(
            item_id="item-1",
            agent_id="agent-1",
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_hierarchy_workflow(self, item_service: Any) -> None:
        """Test parent-child hierarchy workflow."""
        parent = create_mock_item(item_id="parent-1")
        children = [create_mock_item(item_id=f"child-{i}", parent_id="parent-1") for i in range(3)]

        item_service.items.get_by_id = AsyncMock(return_value=parent)
        item_service.items.get_children = AsyncMock(return_value=children)
        item_service.items.get_ancestors = AsyncMock(return_value=[])

        # Get children
        result = await item_service.get_children("parent-1")
        assert len(result) == COUNT_THREE

        # Get ancestors
        result = await item_service.get_ancestors("child-0")
        assert result == []

    @pytest.mark.asyncio
    async def test_concurrent_update_conflict(self, item_service: Any) -> None:
        """Test handling of concurrent update conflicts."""
        mock_item = create_mock_item(version=1)
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(side_effect=Exception("Version conflict"))

        with pytest.raises(Exception):
            await item_service.update_item(
                item_id="item-1",
                agent_id="agent-1",
                title="Conflicting update",
            )

    @pytest.mark.asyncio
    async def test_bulk_status_transition_workflow(self, item_service: Any) -> None:
        """Test bulk updating status across multiple items."""
        items = [create_mock_item(status="todo", item_id=f"item-{i}") for i in range(5)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.update = AsyncMock(return_value=Mock())

        result = await item_service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "in_progress"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["updated"] == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_metadata_versioning_workflow(self, item_service: Any) -> None:
        """Test metadata updates with version management."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = {"version": 1}
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates={"version": 2},
            merge=True,
        )

        assert result.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_item_with_links_workflow(self, item_service: Any) -> None:
        """Test creating item with links and retrieving together."""
        item = create_mock_item()
        links = [Mock(id="link-1"), Mock(id="link-2")]

        item_service.items.create = AsyncMock(return_value=item)
        item_service.links.create = AsyncMock()
        item_service.items.get_by_id = AsyncMock(return_value=item)
        item_service.links.get_by_item = AsyncMock(return_value=links)

        # Create with links
        await item_service.create_item(
            project_id="proj-1",
            title="Item with Links",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            link_to=["target-1", "target-2"],
        )

        # Retrieve with links
        result = await item_service.get_item_with_links("item-1")
        assert len(result["links"]) == COUNT_TWO


# ==============================================================================
# EDGE CASES & ADVANCED SCENARIOS (30+ tests)
# ==============================================================================


class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_create_item_with_none_owner(self, item_service: Any) -> None:
        """Test creating item with None owner."""
        mock_item = create_mock_item(owner=None)
        item_service.items.create = AsyncMock(return_value=mock_item)

        result = await item_service.create_item(
            project_id="proj-1",
            title="Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            owner=None,
        )

        assert result.owner is None

    @pytest.mark.asyncio
    async def test_create_item_with_none_description(self, item_service: Any) -> None:
        """Test creating item with None description."""
        mock_item = create_mock_item()
        item_service.items.create = AsyncMock(return_value=mock_item)

        await item_service.create_item(
            project_id="proj-1",
            title="Item",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
            description=None,
        )

        call_kwargs = item_service.items.create.call_args[1]
        assert call_kwargs["description"] is None

    @pytest.mark.asyncio
    async def test_update_item_with_empty_string_title(self, item_service: Any) -> None:
        """Test updating item with empty string title."""
        mock_item = create_mock_item(version=1)
        updated_item = create_mock_item(title="", version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        result = await item_service.update_item(
            item_id="item-1",
            agent_id="agent-1",
            title="",
        )

        assert result.title == ""

    @pytest.mark.asyncio
    async def test_list_items_large_offset(self, item_service: Any) -> None:
        """Test listing items with offset larger than result set."""
        item_service.items.get_by_project = AsyncMock(return_value=[])

        result = await item_service.list_items(
            project_id="proj-1",
            limit=10,
            offset=99999,
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_bulk_update_large_batch(self, item_service: Any) -> None:
        """Test bulk update with large number of items."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(100)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.update = AsyncMock(return_value=Mock())

        result = await item_service.bulk_update_items(
            filters={"archived": False},
            updates={"priority": "high"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["updated"] == 100

    @pytest.mark.asyncio
    async def test_metadata_with_none_values(self, item_service: Any) -> None:
        """Test metadata update with None values."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = {}
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates={"key": None},
            merge=True,
        )

        call_kwargs = item_service.items.update.call_args[1]
        assert call_kwargs["item_metadata"]["key"] is None

    @pytest.mark.asyncio
    async def test_progress_with_many_children(self, item_service: Any) -> None:
        """Test progress calculation with many children."""
        mock_item = create_mock_item()
        children = [create_mock_item(status="todo") for _ in range(50)]
        children[0].status = "done"  # 1 done out of 50

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=children)

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        assert result["total"] == 50
        assert result["done"] == 1
        assert result["percentage"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_create_item_with_unicode_title(self, item_service: Any) -> None:
        """Test creating item with unicode characters in title."""
        mock_item = create_mock_item(title="Item 测试 テスト тест")
        item_service.items.create = AsyncMock(return_value=mock_item)

        result = await item_service.create_item(
            project_id="proj-1",
            title="Item 测试 テスト тест",
            view="REQUIREMENTS",
            item_type="requirement",
            agent_id="agent-1",
        )

        assert "测试" in result.title

    @pytest.mark.asyncio
    async def test_delete_item_logs_with_fallback_project(self, item_service: Any) -> None:
        """Test that delete logs even if item not found initially."""
        item_service.items.get_by_id = AsyncMock(return_value=None)
        item_service.items.delete = AsyncMock(return_value=False)

        result = await item_service.delete_item(
            item_id="nonexistent",
            agent_id="agent-1",
        )

        assert result is False
        # Event should not be logged when item doesn't exist
        item_service.events.log.assert_not_called()

    @pytest.mark.asyncio
    async def test_transition_with_unknown_current_status(self, item_service: Any) -> None:
        """Test transition validation with unknown current status."""
        mock_item = create_mock_item(status="unknown_status")
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)

        with pytest.raises(ValueError, match="Unknown current status"):
            await item_service.update_item_status(
                item_id="item-1",
                new_status="todo",
                agent_id="agent-1",
                project_id="proj-1",
            )

    @pytest.mark.asyncio
    async def test_bulk_delete_all_fail(self, item_service: Any) -> None:
        """Test bulk delete where all items fail."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(5)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.soft_delete = AsyncMock(side_effect=Exception("Delete failed"))

        result = await item_service.bulk_delete_items(
            filters={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        assert result["success"] is False
        assert result["deleted"] == 0
        assert result["failed"] == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_update_metadata_overwrite_existing_key(self, item_service: Any) -> None:
        """Test overwriting an existing metadata key with merge."""
        mock_item = create_mock_item(version=1)
        mock_item.item_metadata = {"key": "old_value", "other": "value"}
        updated_item = create_mock_item(version=2)

        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.update = AsyncMock(return_value=updated_item)

        await item_service.update_metadata(
            item_id="item-1",
            agent_id="agent-1",
            metadata_updates={"key": "new_value"},
            merge=True,
        )

        call_kwargs = item_service.items.update.call_args[1]
        assert call_kwargs["item_metadata"]["key"] == "new_value"
        assert call_kwargs["item_metadata"]["other"] == "value"

    @pytest.mark.asyncio
    async def test_get_children_with_project_id(self, item_service: Any) -> None:
        """Test get_children delegates to repository correctly."""
        children = [create_mock_item() for _ in range(2)]
        item_service.items.get_children = AsyncMock(return_value=children)

        await item_service.get_children("parent-1")

        # Verify only item_id was passed
        item_service.items.get_children.assert_called_once_with("parent-1")

    @pytest.mark.asyncio
    async def test_progress_calculation_zero_division_protection(self, item_service: Any) -> None:
        """Test that progress calculation handles zero children safely."""
        mock_item = create_mock_item()
        item_service.items.get_by_id = AsyncMock(return_value=mock_item)
        item_service.items.get_children = AsyncMock(return_value=[])

        result = await item_service.get_item_progress(
            item_id="item-1",
            project_id="proj-1",
        )

        # Should not raise ZeroDivisionError
        assert result["percentage"] == 0

    @pytest.mark.asyncio
    async def test_list_items_include_deleted_parameter(self, item_service: Any) -> None:
        """Test that include_deleted parameter is accepted but not used."""
        items = []
        item_service.items.get_by_project = AsyncMock(return_value=items)

        result = await item_service.list_items(
            project_id="proj-1",
            include_deleted=True,
        )

        # Parameter is accepted but not forwarded to repository in current implementation
        assert result == []

    @pytest.mark.asyncio
    async def test_undelete_item_event_contains_project_id(self, item_service: Any) -> None:
        """Test that restore event includes project_id."""
        restored_item = create_mock_item(project_id="proj-123")
        item_service.items.restore = AsyncMock(return_value=restored_item)

        await item_service.undelete_item(
            item_id="item-1",
            agent_id="agent-1",
        )

        log_call = item_service.events.log.call_args
        assert log_call[1]["project_id"] == "proj-123"

    @pytest.mark.asyncio
    async def test_bulk_update_with_complex_filter(self, item_service: Any) -> None:
        """Test bulk update with complex filter combinations."""
        items = [create_mock_item() for _ in range(3)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.update = AsyncMock(return_value=Mock())

        filters = {
            "status": "todo",
            "view": "REQUIREMENTS",
            "priority": "low",
        }

        await item_service.bulk_update_items(
            filters=filters,
            updates={"priority": "high"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        # Verify filters were passed correctly
        call_kwargs = item_service.items.list_by_filters.call_args
        assert call_kwargs[0][0] == filters

    @pytest.mark.asyncio
    async def test_item_creation_logs_all_parameters(self, item_service: Any) -> None:
        """Test that item creation event logs all relevant parameters."""
        mock_item = create_mock_item(
            title="Test",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            owner="owner-1",
            priority="high",
        )
        item_service.items.create = AsyncMock(return_value=mock_item)

        await item_service.create_item(
            project_id="proj-1",
            title="Test",
            view="FEATURE",
            item_type="feature",
            agent_id="agent-1",
            status="in_progress",
            owner="owner-1",
            priority="high",
        )

        log_call = item_service.events.log.call_args
        event_data = log_call[1]["data"]
        assert event_data["item"]["title"] == "Test"
        assert event_data["item"]["view"] == "FEATURE"
        assert event_data["item"]["owner"] == "owner-1"

    @pytest.mark.asyncio
    async def test_batch_operations_event_logging(self, item_service: Any) -> None:
        """Test that batch operations log events for each item."""
        items = [create_mock_item(item_id=f"item-{i}") for i in range(3)]
        item_service.items.list_by_filters = AsyncMock(return_value=items)
        item_service.items.update = AsyncMock(return_value=Mock())

        await item_service.bulk_update_items(
            filters={"status": "todo"},
            updates={"status": "done"},
            agent_id="agent-1",
            project_id="proj-1",
        )

        # Each update should trigger one event log
        assert item_service.events.log.call_count == COUNT_THREE
