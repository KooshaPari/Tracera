from typing import Any

"""Unit tests for Event model."""

from uuid import uuid4

import pytest

from tracertm.models import Event

pytestmark = pytest.mark.unit


@pytest.fixture
def test_data() -> None:
    """Provide test data."""
    return {
        "project_id": str(uuid4()),
        "entity_id": str(uuid4()),
        "agent_id": str(uuid4()),
    }


class TestEventModelCreation:
    """Test Event model creation."""

    def test_event_creation_with_required_fields(self, test_data: Any) -> None:
        """Event creates with required fields."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={"title": "New Item"},
        )
        assert event.project_id == test_data["project_id"]
        assert event.event_type == "item_created"
        assert event.entity_type == "Item"
        assert event.entity_id == test_data["entity_id"]
        assert event.data == {"title": "New Item"}

    def test_event_creation_with_agent(self, test_data: Any) -> None:
        """Event can include agent_id."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_updated",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            agent_id=test_data["agent_id"],
            data={"status": "done"},
        )
        assert event.agent_id == test_data["agent_id"]

    def test_event_agent_id_optional(self, test_data: Any) -> None:
        """Event agent_id is optional."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.agent_id is None


class TestEventModelTypes:
    """Test Event model with different event types."""

    def test_event_type_item_created(self, test_data: Any) -> None:
        """Event supports item_created type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.event_type == "item_created"

    def test_event_type_item_updated(self, test_data: Any) -> None:
        """Event supports item_updated type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_updated",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.event_type == "item_updated"

    def test_event_type_link_created(self, test_data: Any) -> None:
        """Event supports link_created type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="link_created",
            entity_type="Link",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.event_type == "link_created"

    def test_event_type_project_created(self, test_data: Any) -> None:
        """Event supports project_created type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="project_created",
            entity_type="Project",
            entity_id=test_data["project_id"],
            data={},
        )
        assert event.event_type == "project_created"


class TestEventModelEntityTypes:
    """Test Event model with different entity types."""

    def test_entity_type_item(self, test_data: Any) -> None:
        """Event supports Item entity type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.entity_type == "Item"

    def test_entity_type_link(self, test_data: Any) -> None:
        """Event supports Link entity type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="link_created",
            entity_type="Link",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.entity_type == "Link"

    def test_entity_type_project(self, test_data: Any) -> None:
        """Event supports Project entity type."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="project_updated",
            entity_type="Project",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.entity_type == "Project"


class TestEventModelData:
    """Test Event model data field."""

    def test_event_data_is_dict(self, test_data: Any) -> None:
        """Event data field is dictionary."""
        event_data = {"status": "done", "updated_by": "user@example.com"}
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_updated",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data=event_data,
        )
        assert isinstance(event.data, dict)
        assert event.data == event_data

    def test_event_data_empty_dict(self, test_data: Any) -> None:
        """Event data can be empty dict."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert event.data == {}

    def test_event_data_nested_structures(self, test_data: Any) -> None:
        """Event data can contain nested structures."""
        event_data = {
            "changes": {"status": {"from": "todo", "to": "done"}, "priority": {"from": "low", "to": "high"}},
            "metadata": ["tag1", "tag2"],
        }
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_updated",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data=event_data,
        )
        assert event.data == event_data


class TestEventModelAttributes:
    """Test Event model attributes."""

    def test_event_has_timestamp_attributes(self, test_data: Any) -> None:
        """Event has timestamp attributes."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert hasattr(event, "created_at")
        assert hasattr(event, "updated_at")

    def test_event_has_id_attribute(self, test_data: Any) -> None:
        """Event has id attribute (auto-increment)."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        assert hasattr(event, "id")


class TestEventModelRepresentation:
    """Test Event model representation."""

    def test_event_repr(self, test_data: Any) -> None:
        """Event has string representation."""
        event = Event(
            project_id=test_data["project_id"],
            event_type="item_created",
            entity_type="Item",
            entity_id=test_data["entity_id"],
            data={},
        )
        repr_str = repr(event)
        assert "Event" in repr_str or "event" in repr_str.lower()
