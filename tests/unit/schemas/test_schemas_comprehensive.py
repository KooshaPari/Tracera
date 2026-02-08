"""Comprehensive unit tests for Pydantic schema models.

Tests all schemas in tracertm.schemas:
- ItemCreate
- ItemUpdate
- ItemResponse
- LinkCreate
- LinkResponse
- EventCreate
- EventResponse
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from tests.test_constants import HTTP_INTERNAL_SERVER_ERROR
from tracertm.schemas.event import EventCreate, EventResponse
from tracertm.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from tracertm.schemas.link import LinkCreate, LinkResponse


class TestItemCreateSchema:
    """Test ItemCreate schema validation."""

    def test_create_item_minimal(self) -> None:
        """Test creating item with minimal required fields."""
        item = ItemCreate(
            title="Test Item",
            view="FEATURE",
            item_type="requirement",
        )
        assert item.title == "Test Item"
        assert item.view == "FEATURE"
        assert item.item_type == "requirement"
        assert item.status == "todo"  # Default value
        assert item.metadata == {}  # Default empty dict

    def test_create_item_full(self) -> None:
        """Test creating item with all fields."""
        item = ItemCreate(
            title="Test Item",
            description="Test description",
            view="FEATURE",
            item_type="requirement",
            status="in_progress",
            parent_id="parent-123",
            metadata={"key": "value"},
        )
        assert item.title == "Test Item"
        assert item.description == "Test description"
        assert item.status == "in_progress"
        assert item.parent_id == "parent-123"
        assert item.metadata == {"key": "value"}

    def test_create_item_title_required(self) -> None:
        """Test that title is required."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(view="FEATURE", item_type="requirement")
        assert "title" in str(exc_info.value)

    def test_create_item_title_not_empty(self) -> None:
        """Test that title cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="", view="FEATURE", item_type="requirement")
        assert "title" in str(exc_info.value)

    def test_create_item_title_max_length(self) -> None:
        """Test that title has max length of 500."""
        long_title = "x" * 501
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title=long_title, view="FEATURE", item_type="requirement")
        assert "title" in str(exc_info.value)

    def test_create_item_title_at_max_length(self) -> None:
        """Test that title accepts exactly 500 characters."""
        title = "x" * 500
        item = ItemCreate(title=title, view="FEATURE", item_type="requirement")
        assert len(item.title) == HTTP_INTERNAL_SERVER_ERROR

    def test_create_item_view_required(self) -> None:
        """Test that view is required."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="Test", item_type="requirement")
        assert "view" in str(exc_info.value)

    def test_create_item_view_not_empty(self) -> None:
        """Test that view cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="Test", view="", item_type="requirement")
        assert "view" in str(exc_info.value)

    def test_create_item_view_max_length(self) -> None:
        """Test that view has max length of 50."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="Test", view="x" * 51, item_type="requirement")
        assert "view" in str(exc_info.value)

    def test_create_item_type_required(self) -> None:
        """Test that item_type is required."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="Test", view="FEATURE")
        assert "item_type" in str(exc_info.value)

    def test_create_item_type_not_empty(self) -> None:
        """Test that item_type cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="Test", view="FEATURE", item_type="")
        assert "item_type" in str(exc_info.value)

    def test_create_item_type_max_length(self) -> None:
        """Test that item_type has max length of 50."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(title="Test", view="FEATURE", item_type="x" * 51)
        assert "item_type" in str(exc_info.value)

    def test_create_item_status_max_length(self) -> None:
        """Test that status has max length of 50."""
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(
                title="Test",
                view="FEATURE",
                item_type="requirement",
                status="x" * 51,
            )
        assert "status" in str(exc_info.value)

    def test_create_item_description_optional(self) -> None:
        """Test that description is optional."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="requirement")
        assert item.description is None

    def test_create_item_parent_id_optional(self) -> None:
        """Test that parent_id is optional."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="requirement")
        assert item.parent_id is None

    def test_create_item_metadata_default_empty(self) -> None:
        """Test that metadata defaults to empty dict."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="requirement")
        assert item.metadata == {}

    def test_create_item_metadata_nested(self) -> None:
        """Test that metadata can contain nested structures."""
        metadata = {
            "tags": ["tag1", "tag2"],
            "priority": 1,
            "config": {"enabled": True, "value": 42},
        }
        item = ItemCreate(
            title="Test",
            view="FEATURE",
            item_type="requirement",
            metadata=metadata,
        )
        assert item.metadata == metadata


class TestItemUpdateSchema:
    """Test ItemUpdate schema validation."""

    def test_update_item_all_optional(self) -> None:
        """Test that all fields are optional in update."""
        update = ItemUpdate()
        assert update.title is None
        assert update.description is None
        assert update.status is None
        assert update.parent_id is None
        assert update.metadata is None

    def test_update_item_title_only(self) -> None:
        """Test updating only title."""
        update = ItemUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.description is None

    def test_update_item_title_not_empty(self) -> None:
        """Test that title cannot be empty string when provided."""
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(title="")
        assert "title" in str(exc_info.value)

    def test_update_item_title_max_length(self) -> None:
        """Test that title has max length of 500."""
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(title="x" * 501)
        assert "title" in str(exc_info.value)

    def test_update_item_status_only(self) -> None:
        """Test updating only status."""
        update = ItemUpdate(status="done")
        assert update.status == "done"

    def test_update_item_status_max_length(self) -> None:
        """Test that status has max length of 50."""
        with pytest.raises(ValidationError) as exc_info:
            ItemUpdate(status="x" * 51)
        assert "status" in str(exc_info.value)

    def test_update_item_multiple_fields(self) -> None:
        """Test updating multiple fields."""
        update = ItemUpdate(
            title="New Title",
            description="New description",
            status="in_progress",
        )
        assert update.title == "New Title"
        assert update.description == "New description"
        assert update.status == "in_progress"

    def test_update_item_metadata(self) -> None:
        """Test updating metadata."""
        metadata = {"key": "new_value"}
        update = ItemUpdate(metadata=metadata)
        assert update.metadata == metadata

    def test_update_item_clear_description(self) -> None:
        """Test clearing description by setting to None."""
        update = ItemUpdate(description=None)
        assert update.description is None

    def test_update_item_clear_parent_id(self) -> None:
        """Test clearing parent_id by setting to None."""
        update = ItemUpdate(parent_id=None)
        assert update.parent_id is None


class TestItemResponseSchema:
    """Test ItemResponse schema validation."""

    def test_response_from_dict(self) -> None:
        """Test creating response from dictionary."""
        data = {
            "id": "item-123",
            "project_id": "proj-456",
            "title": "Test Item",
            "description": "Test description",
            "view": "FEATURE",
            "item_type": "requirement",
            "status": "todo",
            "parent_id": None,
            "metadata": {},
            "version": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "deleted_at": None,
        }
        response = ItemResponse(**data)
        assert response.id == "item-123"
        assert response.project_id == "proj-456"
        assert response.title == "Test Item"

    def test_response_all_fields_required(self) -> None:
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as exc_info:
            ItemResponse(id="item-123")
        error_str = str(exc_info.value)
        assert "project_id" in error_str or "title" in error_str

    def test_response_from_attributes_config(self) -> None:
        """Test that from_attributes config is set."""
        assert ItemResponse.model_config.get("from_attributes") is True


class TestLinkCreateSchema:
    """Test LinkCreate schema validation."""

    def test_create_link_minimal(self) -> None:
        """Test creating link with minimal fields."""
        link = LinkCreate(
            source_item_id="source-123",
            target_item_id="target-456",
            link_type="dependency",
        )
        assert link.source_item_id == "source-123"
        assert link.target_item_id == "target-456"
        assert link.link_type == "dependency"
        assert link.metadata == {}

    def test_create_link_with_metadata(self) -> None:
        """Test creating link with metadata."""
        metadata = {"strength": "strong", "bidirectional": True}
        link = LinkCreate(
            source_item_id="source-123",
            target_item_id="target-456",
            link_type="dependency",
            metadata=metadata,
        )
        assert link.metadata == metadata

    def test_create_link_source_required(self) -> None:
        """Test that source_item_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            LinkCreate(target_item_id="target-456", link_type="dependency")
        assert "source_item_id" in str(exc_info.value)

    def test_create_link_target_required(self) -> None:
        """Test that target_item_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            LinkCreate(source_item_id="source-123", link_type="dependency")
        assert "target_item_id" in str(exc_info.value)

    def test_create_link_type_required(self) -> None:
        """Test that link_type is required."""
        with pytest.raises(ValidationError) as exc_info:
            LinkCreate(source_item_id="source-123", target_item_id="target-456")
        assert "link_type" in str(exc_info.value)

    def test_create_link_type_not_empty(self) -> None:
        """Test that link_type cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            LinkCreate(
                source_item_id="source-123",
                target_item_id="target-456",
                link_type="",
            )
        assert "link_type" in str(exc_info.value)

    def test_create_link_type_max_length(self) -> None:
        """Test that link_type has max length of 50."""
        with pytest.raises(ValidationError) as exc_info:
            LinkCreate(
                source_item_id="source-123",
                target_item_id="target-456",
                link_type="x" * 51,
            )
        assert "link_type" in str(exc_info.value)

    def test_create_link_metadata_default_empty(self) -> None:
        """Test that metadata defaults to empty dict."""
        link = LinkCreate(
            source_item_id="source-123",
            target_item_id="target-456",
            link_type="dependency",
        )
        assert link.metadata == {}


class TestLinkResponseSchema:
    """Test LinkResponse schema validation."""

    def test_response_from_dict(self) -> None:
        """Test creating response from dictionary."""
        data = {
            "id": "link-123",
            "project_id": "proj-456",
            "source_item_id": "source-789",
            "target_item_id": "target-012",
            "link_type": "dependency",
            "metadata": {},
            "created_at": datetime.now(),
        }
        response = LinkResponse(**data)
        assert response.id == "link-123"
        assert response.source_item_id == "source-789"
        assert response.link_type == "dependency"

    def test_response_all_fields_required(self) -> None:
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as exc_info:
            LinkResponse(id="link-123")
        error_str = str(exc_info.value)
        assert "project_id" in error_str or "source_item_id" in error_str

    def test_response_from_attributes_config(self) -> None:
        """Test that from_attributes config is set."""
        assert LinkResponse.model_config.get("from_attributes") is True


class TestEventCreateSchema:
    """Test EventCreate schema validation."""

    def test_create_event_minimal(self) -> None:
        """Test creating event with minimal fields."""
        event = EventCreate(
            event_type="item_created",
            event_data={"item_id": "item-123"},
            agent_id="agent-456",
        )
        assert event.event_type == "item_created"
        assert event.event_data == {"item_id": "item-123"}
        assert event.agent_id == "agent-456"
        assert event.item_id is None

    def test_create_event_with_item_id(self) -> None:
        """Test creating event with item_id."""
        event = EventCreate(
            event_type="item_updated",
            event_data={"field": "status", "old": "todo", "new": "done"},
            agent_id="agent-456",
            item_id="item-789",
        )
        assert event.item_id == "item-789"

    def test_create_event_type_required(self) -> None:
        """Test that event_type is required."""
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(event_data={}, agent_id="agent-456")
        assert "event_type" in str(exc_info.value)

    def test_create_event_type_not_empty(self) -> None:
        """Test that event_type cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(event_type="", event_data={}, agent_id="agent-456")
        assert "event_type" in str(exc_info.value)

    def test_create_event_type_max_length(self) -> None:
        """Test that event_type has max length of 50."""
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(
                event_type="x" * 51,
                event_data={},
                agent_id="agent-456",
            )
        assert "event_type" in str(exc_info.value)

    def test_create_event_data_required(self) -> None:
        """Test that event_data is required."""
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(event_type="item_created", agent_id="agent-456")
        assert "event_data" in str(exc_info.value)

    def test_create_event_agent_id_required(self) -> None:
        """Test that agent_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(event_type="item_created", event_data={})
        assert "agent_id" in str(exc_info.value)

    def test_create_event_data_nested(self) -> None:
        """Test that event_data can contain nested structures."""
        event_data = {
            "changes": [
                {"field": "status", "old": "todo", "new": "done"},
                {"field": "priority", "old": 1, "new": 2},
            ],
            "metadata": {"user": "system", "automated": True},
        }
        event = EventCreate(
            event_type="bulk_update",
            event_data=event_data,
            agent_id="agent-456",
        )
        assert event.event_data == event_data


class TestEventResponseSchema:
    """Test EventResponse schema validation."""

    def test_response_from_dict(self) -> None:
        """Test creating response from dictionary."""
        data = {
            "id": "event-123",
            "project_id": "proj-456",
            "item_id": None,
            "event_type": "item_created",
            "event_data": {"item_id": "item-789"},
            "agent_id": "agent-012",
            "timestamp": datetime.now(),
        }
        response = EventResponse(**data)
        assert response.id == "event-123"
        assert response.event_type == "item_created"
        assert response.agent_id == "agent-012"

    def test_response_all_fields_required(self) -> None:
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as exc_info:
            EventResponse(id="event-123")
        error_str = str(exc_info.value)
        assert "project_id" in error_str or "event_type" in error_str

    def test_response_from_attributes_config(self) -> None:
        """Test that from_attributes config is set."""
        assert EventResponse.model_config.get("from_attributes") is True

    def test_response_with_item_id(self) -> None:
        """Test response with item_id set."""
        data = {
            "id": "event-123",
            "project_id": "proj-456",
            "item_id": "item-789",
            "event_type": "item_updated",
            "event_data": {},
            "agent_id": "agent-012",
            "timestamp": datetime.now(),
        }
        response = EventResponse(**data)
        assert response.item_id == "item-789"

    def test_response_without_item_id(self) -> None:
        """Test response with item_id as None."""
        data = {
            "id": "event-123",
            "project_id": "proj-456",
            "item_id": None,
            "event_type": "system_event",
            "event_data": {},
            "agent_id": "agent-012",
            "timestamp": datetime.now(),
        }
        response = EventResponse.model_validate(data)
        assert response.item_id is None
