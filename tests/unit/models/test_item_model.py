"""Unit tests for Item model - based on actual field structure."""

import pytest
from uuid import uuid4
from tracertm.models import Item

pytestmark = pytest.mark.unit


@pytest.fixture
def project_id():
    """Create a test project ID."""
    return str(uuid4())


class TestItemModelCreation:
    """Test Item model creation with actual fields."""

    def test_item_creation_with_required_fields(self, project_id):
        """Item creates with minimum required fields: project_id, title, view, item_type."""
        item = Item(
            project_id=project_id,
            title="Test Item",
            view="Feature",
            item_type="requirement"
        )
        assert item.project_id == project_id
        assert item.title == "Test Item"
        assert item.view == "Feature"
        assert item.item_type == "requirement"

    def test_item_creation_with_all_fields(self, project_id):
        """Item creates with all fields."""
        metadata = {"custom": "value"}
        item = Item(
            project_id=project_id,
            title="Full Item",
            description="Item description",
            view="Component",
            item_type="code",
            status="in_progress",
            priority="high",
            owner="user@example.com",
            item_metadata=metadata
        )
        assert item.project_id == project_id
        assert item.title == "Full Item"
        assert item.description == "Item description"
        assert item.view == "Component"
        assert item.item_type == "code"
        assert item.status == "in_progress"
        assert item.priority == "high"
        assert item.owner == "user@example.com"
        assert item.item_metadata == metadata

    def test_item_creation_with_explicit_id(self, project_id):
        """Item can be created with explicit ID."""
        item_id = str(uuid4())
        item = Item(
            id=item_id,
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement"
        )
        assert item.id == item_id

    def test_item_description_optional(self, project_id):
        """Item description is optional."""
        item = Item(
            project_id=project_id,
            title="No Description",
            view="Feature",
            item_type="requirement"
        )
        assert item.description is None

    def test_item_has_timestamp_attributes(self, project_id):
        """Item has timestamp attributes."""
        item = Item(
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement"
        )
        assert hasattr(item, 'created_at')
        assert hasattr(item, 'updated_at')


class TestItemModelFields:
    """Test Item model field properties."""

    def test_item_title_storage(self, project_id):
        """Item title is properly stored."""
        item = Item(
            project_id=project_id,
            title="Important Task",
            view="Feature",
            item_type="requirement"
        )
        assert item.title == "Important Task"

    def test_item_status_storage(self, project_id):
        """Item status can be set and stored."""
        item = Item(
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement",
            status="done"
        )
        assert item.status == "done"

    def test_item_priority_storage(self, project_id):
        """Item priority can be set and stored."""
        item = Item(
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement",
            priority="low"
        )
        assert item.priority == "low"

    def test_item_owner_storage(self, project_id):
        """Item owner can be set and stored."""
        item = Item(
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement",
            owner="user@example.com"
        )
        assert item.owner == "user@example.com"

    def test_item_metadata_storage(self, project_id):
        """Item metadata can be stored."""
        metadata = {"priority_score": 100, "tags": ["urgent"]}
        item = Item(
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement",
            item_metadata=metadata
        )
        assert item.item_metadata == metadata

    def test_item_parent_reference(self, project_id):
        """Item can have parent_id reference."""
        parent_id = str(uuid4())
        item = Item(
            project_id=project_id,
            title="Child Item",
            view="Feature",
            item_type="requirement",
            parent_id=parent_id
        )
        assert item.parent_id == parent_id


class TestItemModelValidation:
    """Test Item model field validation."""

    def test_item_multiple_statuses(self, project_id):
        """Item supports different status values."""
        statuses = ["todo", "in_progress", "done", "blocked"]
        for status in statuses:
            item = Item(
                project_id=project_id,
                title="Test",
                view="Feature",
                item_type="requirement",
                status=status
            )
            assert item.status == status

    def test_item_multiple_priorities(self, project_id):
        """Item supports different priority values."""
        priorities = ["low", "medium", "high", "critical"]
        for priority in priorities:
            item = Item(
                project_id=project_id,
                title="Test",
                view="Feature",
                item_type="requirement",
                priority=priority
            )
            assert item.priority == priority

    def test_item_multiple_item_types(self, project_id):
        """Item supports different item_type values."""
        types = ["requirement", "feature", "bug", "task", "epic"]
        for item_type in types:
            item = Item(
                project_id=project_id,
                title="Test",
                view="Feature",
                item_type=item_type
            )
            assert item.item_type == item_type

    def test_item_multiple_views(self, project_id):
        """Item supports different view values."""
        views = ["Feature", "Component", "API", "Test", "Documentation"]
        for view in views:
            item = Item(
                project_id=project_id,
                title="Test",
                view=view,
                item_type="requirement"
            )
            assert item.view == view


class TestItemModelComparison:
    """Test Item model comparison."""

    def test_items_with_different_ids(self, project_id):
        """Items with different IDs are different."""
        item1 = Item(
            id="item-1",
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement"
        )
        item2 = Item(
            id="item-2",
            project_id=project_id,
            title="Test",
            view="Feature",
            item_type="requirement"
        )
        assert item1.id != item2.id

    def test_items_same_project_different_instances(self, project_id):
        """Different item instances with same project."""
        item1 = Item(
            id="id-1",
            project_id=project_id,
            title="Item 1",
            view="Feature",
            item_type="requirement"
        )
        item2 = Item(
            id="id-2",
            project_id=project_id,
            title="Item 2",
            view="Feature",
            item_type="requirement"
        )
        assert item1.project_id == item2.project_id
        assert item1.id != item2.id


class TestItemModelRepresentation:
    """Test Item model string representation."""

    def test_item_has_repr(self, project_id):
        """Item has string representation."""
        item = Item(
            project_id=project_id,
            title="Test Item",
            view="Feature",
            item_type="requirement"
        )
        repr_str = repr(item)
        assert "Item" in repr_str or "item" in repr_str.lower()
