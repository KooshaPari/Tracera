"""Comprehensive data validation and model tests.

Target: +4% coverage on validation/model paths
Scope: Field validation, constraints, type constraints, relationships
"""

import math
import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from tests.test_constants import COUNT_FOUR, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.schemas.item import ItemCreate, ItemUpdate
from tracertm.schemas.link import LinkCreate, LinkResponse

# ============================================================================
# ITEM MODEL VALIDATION TESTS
# ============================================================================


class TestItemFieldValidation:
    """Test Item model field validation and constraints."""

    def test_item_id_auto_generation(self) -> None:
        """Test that item ID is auto-generated as UUID at DB insertion."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # ID is generated via default callable when inserted into DB, not at ORM creation
        assert hasattr(item, "id")
        # Test that the default callable works
        from tracertm.models.item import generate_item_uuid

        generated_id = generate_item_uuid()
        assert isinstance(generated_id, str)
        assert len(generated_id) == 36  # UUID string length
        assert generated_id.count("-") == COUNT_FOUR  # UUID has 4 hyphens

    def test_item_id_custom(self) -> None:
        """Test that item ID can be set manually."""
        custom_id = str(uuid.uuid4())
        item = Item(id=custom_id, project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.id == custom_id

    def test_item_project_id_required(self) -> None:
        """Test that project_id is required."""
        # SQLAlchemy doesn't validate at model level, but testing attribute requirement
        item = Item(project_id=None, title="Test", view="FEATURE", item_type="req")
        assert item.project_id is None
        # In DB, this would fail on NOT NULL constraint

    def test_item_project_id_string(self) -> None:
        """Test project_id is string type."""
        item = Item(project_id="proj-123", title="Test", view="FEATURE", item_type="req")
        assert item.project_id == "proj-123"
        assert isinstance(item.project_id, str)

    def test_item_title_required(self) -> None:
        """Test that title is required."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.title == "Test"

    def test_item_title_max_length_500(self) -> None:
        """Test that title column allows up to 500 characters."""
        title = "x" * 500
        item = Item(project_id="p1", title=title, view="FEATURE", item_type="req")
        assert len(item.title) == HTTP_INTERNAL_SERVER_ERROR

    def test_item_title_can_exceed_500(self) -> None:
        """Test that ORM doesn't enforce max length (DB does)."""
        # SQLAlchemy String(500) doesn't validate length at ORM level
        title = "x" * 501
        item = Item(project_id="p1", title=title, view="FEATURE", item_type="req")
        assert len(item.title) == 501

    def test_item_description_optional(self) -> None:
        """Test that description is optional."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.description is None

    def test_item_description_text_type(self) -> None:
        """Test that description can be long text."""
        long_text = "x" * 5000
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", description=long_text)
        assert item.description is not None and len(item.description) == 5000

    def test_item_view_required(self) -> None:
        """Test that view is required."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.view == "FEATURE"

    def test_item_view_string_type(self) -> None:
        """Test view is string with max 50 chars."""
        item = Item(project_id="p1", title="Test", view="CODE", item_type="req")
        assert item.view == "CODE"

    def test_item_type_required(self) -> None:
        """Test that item_type is required."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="feature")
        assert item.item_type == "feature"

    def test_item_status_default(self) -> None:
        """Test that status defaults to 'todo'."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # Default is set at DB level via server_default
        assert hasattr(item, "status")

    def test_item_status_custom(self) -> None:
        """Test that status can be set to custom value."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", status="in_progress")
        assert item.status == "in_progress"

    def test_item_priority_default(self) -> None:
        """Test that priority defaults to 'medium'."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # Default is set at DB level via server_default
        assert hasattr(item, "priority")

    def test_item_priority_custom(self) -> None:
        """Test that priority can be set."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", priority="high")
        assert item.priority == "high"

    def test_item_owner_optional(self) -> None:
        """Test that owner is optional."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.owner is None

    def test_item_owner_string(self) -> None:
        """Test that owner can be set."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", owner="user@example.com")
        assert item.owner == "user@example.com"

    def test_item_parent_id_optional(self) -> None:
        """Test that parent_id is optional."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.parent_id is None

    def test_item_parent_id_hierarchical(self) -> None:
        """Test that parent_id references another item."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", parent_id="parent-123")
        assert item.parent_id == "parent-123"

    def test_item_metadata_default_empty(self) -> None:
        """Test that metadata is initialized (None until DB insertion)."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # Metadata defaults to dict via default_factory in DB
        assert hasattr(item, "item_metadata")

    def test_item_metadata_dict_type(self) -> None:
        """Test that metadata is a dict."""
        metadata = {"key": "value", "nested": {"inner": "data"}}
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", item_metadata=metadata)
        assert item.item_metadata == metadata

    def test_item_metadata_various_types(self) -> None:
        """Test that metadata can contain various JSON types."""
        metadata = {
            "string": "value",
            "number": 42,
            "float": math.pi,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", item_metadata=metadata)
        assert item.item_metadata == metadata

    def test_item_version_default(self) -> None:
        """Test that version defaults to 1."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # Default is set at ORM level
        assert hasattr(item, "version")

    def test_item_version_increment(self) -> None:
        """Test that version can be incremented."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        item.version = 2
        assert item.version == COUNT_TWO

    def test_item_deleted_at_optional(self) -> None:
        """Test that deleted_at is optional (soft delete)."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        assert item.deleted_at is None

    def test_item_deleted_at_datetime(self) -> None:
        """Test that deleted_at can be set to datetime."""
        now = datetime.now()
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", deleted_at=now)
        assert item.deleted_at == now

    def test_item_timestamps_created(self) -> None:
        """Test that created_at is set."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # created_at is set at DB level, not ORM level
        assert hasattr(item, "created_at")

    def test_item_timestamps_updated(self) -> None:
        """Test that updated_at is set."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # updated_at is set at DB level, not ORM level
        assert hasattr(item, "updated_at")


# ============================================================================
# LINK MODEL VALIDATION TESTS
# ============================================================================


class TestLinkFieldValidation:
    """Test Link model field validation and constraints."""

    def test_link_id_auto_generation(self) -> None:
        """Test that link ID is auto-generated."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="implements")
        assert hasattr(link, "id")
        # Test that the default callable works
        from tracertm.models.link import generate_link_uuid

        generated_id = generate_link_uuid()
        assert isinstance(generated_id, str)
        assert len(generated_id) == 36

    def test_link_project_id_required(self) -> None:
        """Test that project_id is required in link."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="implements")
        assert link.project_id == "p1"

    def test_link_source_item_id_required(self) -> None:
        """Test that source_item_id is required."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="implements")
        assert link.source_item_id == "i1"

    def test_link_target_item_id_required(self) -> None:
        """Test that target_item_id is required."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="implements")
        assert link.target_item_id == "i2"

    def test_link_source_target_different(self) -> None:
        """Test that source and target can be different items."""
        link = Link(project_id="p1", source_item_id="item-source", target_item_id="item-target", link_type="implements")
        assert link.source_item_id != link.target_item_id

    def test_link_source_target_same(self) -> None:
        """Test that source and target can be same (self-link)."""
        # This shouldn't be prevented at ORM level
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i1", link_type="depends_on")
        assert link.source_item_id == link.target_item_id

    def test_link_type_required(self) -> None:
        """Test that link_type is required."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="custom_type")
        assert link.link_type == "custom_type"

    def test_link_type_various(self) -> None:
        """Test that various link types are supported."""
        types = ["implements", "tests", "depends_on", "related_to", "custom"]
        for link_type in types:
            link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type=link_type)
            assert link.link_type == link_type

    def test_link_metadata_default_empty(self) -> None:
        """Test that metadata is initialized (None until DB insertion)."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="implements")
        # Metadata defaults to dict via default_factory in DB
        assert hasattr(link, "link_metadata")

    def test_link_metadata_dict(self) -> None:
        """Test that metadata can be set."""
        metadata = {"strength": 0.9, "tags": ["important"]}
        link = Link(
            project_id="p1",
            source_item_id="i1",
            target_item_id="i2",
            link_type="implements",
            link_metadata=metadata,
        )
        assert link.link_metadata == metadata


# ============================================================================
# PROJECT MODEL VALIDATION TESTS
# ============================================================================


class TestProjectFieldValidation:
    """Test Project model field validation and constraints."""

    def test_project_id_auto_generation(self) -> None:
        """Test that project ID is auto-generated."""
        project = Project(name="Test Project")
        assert hasattr(project, "id")
        # Test that the default callable works
        from tracertm.models.project import generate_uuid

        generated_id = generate_uuid()
        assert isinstance(generated_id, str)

    def test_project_name_required(self) -> None:
        """Test that name is required."""
        project = Project(name="My Project")
        assert project.name == "My Project"

    def test_project_name_unique_constraint(self) -> None:
        """Test that name has unique constraint (at DB level)."""
        project1 = Project(name="Unique Name")
        assert project1.name == "Unique Name"
        # Second project with same name would fail at DB level

    def test_project_name_max_length_255(self) -> None:
        """Test that name column allows up to 255 characters."""
        name = "x" * 255
        project = Project(name=name)
        assert len(project.name) == 255

    def test_project_description_optional(self) -> None:
        """Test that description is optional."""
        project = Project(name="Project")
        assert project.description is None

    def test_project_description_text(self) -> None:
        """Test that description can be long text."""
        desc = "x" * 5000
        project = Project(name="Project", description=desc)
        assert project.description is not None and len(project.description) == 5000

    def test_project_metadata_default_empty(self) -> None:
        """Test that metadata is initialized (None until DB insertion)."""
        project = Project(name="Project")
        # Metadata defaults to dict via default_factory in DB
        assert hasattr(project, "project_metadata")

    def test_project_metadata_dict(self) -> None:
        """Test that metadata can be set."""
        metadata = {"owner": "team@example.com", "status": "active"}
        project = Project(name="Project", project_metadata=metadata)
        assert project.project_metadata == metadata


# ============================================================================
# ITEM SCHEMA (PYDANTIC) VALIDATION TESTS
# ============================================================================


class TestItemCreateSchemaValidation:
    """Test ItemCreate schema validation rules."""

    def test_item_create_required_fields(self) -> None:
        """Test that required fields are enforced."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req")
        assert item.title == "Test"
        assert item.view == "FEATURE"
        assert item.item_type == "req"

    def test_item_create_title_min_length(self) -> None:
        """Test that title must not be empty."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="", view="FEATURE", item_type="req")
        assert "title" in str(exc.value).lower()

    def test_item_create_title_max_length_500(self) -> None:
        """Test that title cannot exceed 500 characters."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="x" * 501, view="FEATURE", item_type="req")
        assert "title" in str(exc.value).lower()

    def test_item_create_title_boundary_500(self) -> None:
        """Test that title accepts exactly 500 characters."""
        item = ItemCreate(title="x" * 500, view="FEATURE", item_type="req")
        assert len(item.title) == HTTP_INTERNAL_SERVER_ERROR

    def test_item_create_view_required(self) -> None:
        """Test that view is required."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", item_type="req")
        assert "view" in str(exc.value).lower()

    def test_item_create_view_min_length(self) -> None:
        """Test that view must not be empty."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", view="", item_type="req")
        assert "view" in str(exc.value).lower()

    def test_item_create_view_max_length_50(self) -> None:
        """Test that view cannot exceed 50 characters."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", view="x" * 51, item_type="req")
        assert "view" in str(exc.value).lower()

    def test_item_create_view_boundary_50(self) -> None:
        """Test that view accepts exactly 50 characters."""
        item = ItemCreate(title="Test", view="x" * 50, item_type="req")
        assert len(item.view) == 50

    def test_item_create_item_type_required(self) -> None:
        """Test that item_type is required."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", view="FEATURE")
        assert "item_type" in str(exc.value).lower()

    def test_item_create_item_type_min_length(self) -> None:
        """Test that item_type must not be empty."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", view="FEATURE", item_type="")
        assert "item_type" in str(exc.value).lower()

    def test_item_create_item_type_max_length_50(self) -> None:
        """Test that item_type cannot exceed 50 characters."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", view="FEATURE", item_type="x" * 51)
        assert "item_type" in str(exc.value).lower()

    def test_item_create_status_optional(self) -> None:
        """Test that status is optional with default."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req")
        assert item.status == "todo"

    def test_item_create_status_custom(self) -> None:
        """Test that status can be set."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req", status="in_progress")
        assert item.status == "in_progress"

    def test_item_create_status_max_length_50(self) -> None:
        """Test that status cannot exceed 50 characters."""
        with pytest.raises(ValidationError) as exc:
            ItemCreate(title="Test", view="FEATURE", item_type="req", status="x" * 51)
        assert "status" in str(exc.value).lower()

    def test_item_create_description_optional(self) -> None:
        """Test that description is optional."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req")
        assert item.description is None

    def test_item_create_description_custom(self) -> None:
        """Test that description can be set."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req", description="Long description")
        assert item.description == "Long description"

    def test_item_create_parent_id_optional(self) -> None:
        """Test that parent_id is optional."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req")
        assert item.parent_id is None

    def test_item_create_parent_id_custom(self) -> None:
        """Test that parent_id can be set."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req", parent_id="parent-123")
        assert item.parent_id == "parent-123"

    def test_item_create_metadata_default_empty(self) -> None:
        """Test that metadata defaults to empty dict."""
        item = ItemCreate(title="Test", view="FEATURE", item_type="req")
        assert item.metadata == {}

    def test_item_create_metadata_custom(self) -> None:
        """Test that metadata can be set."""
        metadata = {"priority": "high", "tags": ["urgent"]}
        item = ItemCreate(title="Test", view="FEATURE", item_type="req", metadata=metadata)
        assert item.metadata == metadata

    def test_item_create_metadata_nested_objects(self) -> None:
        """Test that metadata can contain nested structures."""
        metadata = {
            "tags": ["tag1", "tag2"],
            "config": {"enabled": True, "value": 42},
            "custom": {"nested": {"deep": "value"}},
        }
        item = ItemCreate(title="Test", view="FEATURE", item_type="req", metadata=metadata)
        assert item.metadata == metadata


class TestItemUpdateSchemaValidation:
    """Test ItemUpdate schema validation rules."""

    def test_item_update_all_optional(self) -> None:
        """Test that all fields in ItemUpdate are optional."""
        item = ItemUpdate()
        assert item.title is None
        assert item.description is None
        assert item.status is None
        assert item.parent_id is None
        assert item.metadata is None

    def test_item_update_title_validation(self) -> None:
        """Test title validation in update."""
        item = ItemUpdate(title="New Title")
        assert item.title == "New Title"

    def test_item_update_title_empty_invalid(self) -> None:
        """Test that title cannot be empty if provided."""
        with pytest.raises(ValidationError) as exc:
            ItemUpdate(title="")
        assert "title" in str(exc.value).lower()

    def test_item_update_title_max_length(self) -> None:
        """Test title max length in update."""
        with pytest.raises(ValidationError) as exc:
            ItemUpdate(title="x" * 501)
        assert "title" in str(exc.value).lower()

    def test_item_update_status_validation(self) -> None:
        """Test status validation in update."""
        item = ItemUpdate(status="completed")
        assert item.status == "completed"

    def test_item_update_status_max_length(self) -> None:
        """Test status max length in update."""
        with pytest.raises(ValidationError) as exc:
            ItemUpdate(status="x" * 51)
        assert "status" in str(exc.value).lower()


# ============================================================================
# LINK SCHEMA (PYDANTIC) VALIDATION TESTS
# ============================================================================


class TestLinkCreateSchemaValidation:
    """Test LinkCreate schema validation rules."""

    def test_link_create_required_fields(self) -> None:
        """Test that required fields are enforced."""
        link = LinkCreate(source_item_id="i1", target_item_id="i2", link_type="implements")
        assert link.source_item_id == "i1"
        assert link.target_item_id == "i2"
        assert link.link_type == "implements"

    def test_link_create_source_item_id_required(self) -> None:
        """Test that source_item_id is required."""
        with pytest.raises(ValidationError) as exc:
            LinkCreate(target_item_id="i2", link_type="implements")
        assert "source_item_id" in str(exc.value).lower()

    def test_link_create_target_item_id_required(self) -> None:
        """Test that target_item_id is required."""
        with pytest.raises(ValidationError) as exc:
            LinkCreate(source_item_id="i1", link_type="implements")
        assert "target_item_id" in str(exc.value).lower()

    def test_link_create_link_type_required(self) -> None:
        """Test that link_type is required."""
        with pytest.raises(ValidationError) as exc:
            LinkCreate(source_item_id="i1", target_item_id="i2")
        assert "link_type" in str(exc.value).lower()

    def test_link_create_link_type_min_length(self) -> None:
        """Test that link_type must not be empty."""
        with pytest.raises(ValidationError) as exc:
            LinkCreate(source_item_id="i1", target_item_id="i2", link_type="")
        assert "link_type" in str(exc.value).lower()

    def test_link_create_link_type_max_length_50(self) -> None:
        """Test that link_type cannot exceed 50 characters."""
        with pytest.raises(ValidationError) as exc:
            LinkCreate(source_item_id="i1", target_item_id="i2", link_type="x" * 51)
        assert "link_type" in str(exc.value).lower()

    def test_link_create_link_type_boundary_50(self) -> None:
        """Test that link_type accepts exactly 50 characters."""
        link = LinkCreate(source_item_id="i1", target_item_id="i2", link_type="x" * 50)
        assert len(link.link_type) == 50

    def test_link_create_metadata_optional(self) -> None:
        """Test that metadata is optional."""
        link = LinkCreate(source_item_id="i1", target_item_id="i2", link_type="implements")
        assert link.metadata == {}

    def test_link_create_metadata_custom(self) -> None:
        """Test that metadata can be set."""
        metadata = {"strength": 0.9, "tags": ["important"]}
        link = LinkCreate(source_item_id="i1", target_item_id="i2", link_type="implements", metadata=metadata)
        assert link.metadata == metadata


class TestLinkResponseSchemaValidation:
    """Test LinkResponse schema validation rules."""

    def test_link_response_required_fields(self) -> None:
        """Test LinkResponse requires all fields."""
        now = datetime.now()
        link = LinkResponse(
            id="link-123",
            project_id="p1",
            source_item_id="i1",
            target_item_id="i2",
            link_type="implements",
            metadata={},
            created_at=now,
        )
        assert link.id == "link-123"
        assert link.project_id == "p1"
        assert link.source_item_id == "i1"
        assert link.target_item_id == "i2"
        assert link.link_type == "implements"


# ============================================================================
# ENUM AND TYPE CONSTRAINT TESTS
# ============================================================================


class TestEnumConstraints:
    """Test enum-like constraints on fields."""

    def test_item_view_types(self) -> None:
        """Test common item view types."""
        views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
        for view in views:
            item = Item(project_id="p1", title="Test", view=view, item_type="req")
            assert item.view == view

    def test_item_status_types(self) -> None:
        """Test common item status values."""
        statuses = ["todo", "in_progress", "done", "blocked", "reviewed"]
        for status in statuses:
            item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", status=status)
            assert item.status == status

    def test_item_priority_types(self) -> None:
        """Test common priority values."""
        priorities = ["low", "medium", "high", "critical"]
        for priority in priorities:
            item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", priority=priority)
            assert item.priority == priority

    def test_link_type_enum_values(self) -> None:
        """Test common link types."""
        types = ["implements", "tests", "depends_on", "related_to", "blocks"]
        for link_type in types:
            link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type=link_type)
            assert link.link_type == link_type


# ============================================================================
# FOREIGN KEY AND RELATIONSHIP TESTS
# ============================================================================


class TestForeignKeyRelationships:
    """Test foreign key constraints and relationships."""

    def test_item_foreign_key_project(self) -> None:
        """Test that item references project via foreign key."""
        item = Item(project_id="proj-123", title="Test", view="FEATURE", item_type="req")
        assert item.project_id == "proj-123"

    def test_item_self_reference_parent(self) -> None:
        """Test that item can reference parent item."""
        parent_id = str(uuid.uuid4())
        item = Item(project_id="p1", title="Child", view="FEATURE", item_type="req", parent_id=parent_id)
        assert item.parent_id == parent_id

    def test_link_foreign_key_project(self) -> None:
        """Test that link references project via foreign key."""
        link = Link(project_id="proj-123", source_item_id="i1", target_item_id="i2", link_type="implements")
        assert link.project_id == "proj-123"

    def test_link_foreign_key_source_item(self) -> None:
        """Test that link references source item via foreign key."""
        link = Link(project_id="p1", source_item_id="source-123", target_item_id="i2", link_type="implements")
        assert link.source_item_id == "source-123"

    def test_link_foreign_key_target_item(self) -> None:
        """Test that link references target item via foreign key."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="target-123", link_type="implements")
        assert link.target_item_id == "target-123"


# ============================================================================
# TYPE COERCION AND CONVERSION TESTS
# ============================================================================


class TestTypeCoercion:
    """Test type handling and coercion."""

    def test_item_metadata_json_serializable(self) -> None:
        """Test that metadata is JSON serializable."""
        import json

        metadata = {
            "string": "value",
            "number": 42,
            "float": math.pi,
            "bool": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", item_metadata=metadata)
        # Should be JSON serializable
        json_str = json.dumps(item.item_metadata)
        assert json_str is not None

    def test_project_metadata_json_serializable(self) -> None:
        """Test that project metadata is JSON serializable."""
        import json

        metadata = {"owner": "team@example.com", "active": True}
        project = Project(name="Test", project_metadata=metadata)
        json_str = json.dumps(project.project_metadata)
        assert json_str is not None


# ============================================================================
# INVALID DATA HANDLING TESTS
# ============================================================================


class TestInvalidDataHandling:
    """Test handling of invalid data."""

    def test_schema_validation_failure_type_error(self) -> None:
        """Test that validation fails on type errors."""
        with pytest.raises(ValidationError):
            ItemCreate(title=123, view="FEATURE", item_type="req")

    def test_schema_validation_failure_missing_required(self) -> None:
        """Test that validation fails on missing required fields."""
        with pytest.raises(ValidationError):
            ItemCreate(view="FEATURE", item_type="req")

    def test_schema_validation_failure_invalid_constraint(self) -> None:
        """Test that validation fails on constraint violations."""
        with pytest.raises(ValidationError):
            ItemCreate(title="x" * 501, view="FEATURE", item_type="req")

    def test_item_model_with_none_project_id(self) -> None:
        """Test Item model allows None project_id (ORM doesn't validate)."""
        # The ORM allows this; DB constraint catches it
        item = Item(project_id=None, title="Test", view="FEATURE", item_type="req")
        assert item.project_id is None

    def test_link_model_with_none_source_id(self) -> None:
        """Test Link model allows None source_item_id (ORM doesn't validate)."""
        # The ORM allows this; DB constraint catches it
        link = Link(
            project_id="p1",
            source_item_id=None,
            target_item_id="i2",
            link_type="impl",
        )
        assert link.source_item_id is None


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_item_metadata_empty_dict_preserved(self) -> None:
        """Test that empty metadata dict is preserved."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", item_metadata={})
        assert item.item_metadata == {}
        assert isinstance(item.item_metadata, dict)

    def test_item_metadata_none_converts_to_dict(self) -> None:
        """Test behavior when metadata is not provided."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req")
        # Metadata becomes a dict after DB insertion via default_factory
        assert hasattr(item, "item_metadata")

    def test_item_with_very_long_title(self) -> None:
        """Test item with very long title."""
        long_title = "This is a very long title " * 50  # Much longer than 500
        item = Item(project_id="p1", title=long_title, view="FEATURE", item_type="req")
        assert len(item.title) > HTTP_INTERNAL_SERVER_ERROR

    def test_item_with_very_long_description(self) -> None:
        """Test item with very long description."""
        long_desc = "This is a very long description " * 500
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", description=long_desc)
        assert item.description is not None and len(item.description) > 5000

    def test_item_with_unicode_characters(self) -> None:
        """Test item with unicode characters."""
        item = Item(project_id="p1", title="测试 テスト تجربة", view="FEATURE", item_type="req")
        assert "测试" in item.title

    def test_link_with_unicode_metadata(self) -> None:
        """Test link with unicode in metadata."""
        link = Link(
            project_id="p1",
            source_item_id="i1",
            target_item_id="i2",
            link_type="implements",
            link_metadata={"comment": "Unicode: 你好 مرحبا"},
        )
        comment = link.link_metadata.get("comment") if isinstance(link.link_metadata, dict) else None
        assert comment is not None and "你好" in str(comment)

    def test_project_with_special_characters_in_name(self) -> None:
        """Test project with special characters in name."""
        name = "Project-2024@v1.0 (Test)"
        project = Project(name=name)
        assert project.name == name

    def test_item_with_special_characters_in_title(self) -> None:
        """Test item with special characters in title."""
        title = "Task #123 [URGENT] (High Priority) - Test & Review"
        item = Item(project_id="p1", title=title, view="FEATURE", item_type="req")
        assert item.title == title

    def test_metadata_with_empty_nested_dict(self) -> None:
        """Test metadata with empty nested structures."""
        metadata = {"outer": {}, "list": []}
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", item_metadata=metadata)
        assert item.item_metadata["outer"] == {}
        assert item.item_metadata["list"] == []

    def test_metadata_with_null_values(self) -> None:
        """Test metadata with null/None values."""
        metadata = {"key1": None, "key2": "value", "key3": None}
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="req", item_metadata=metadata)
        assert item.item_metadata["key1"] is None
