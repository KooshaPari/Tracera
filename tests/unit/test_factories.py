"""Unit tests for testing_factories.py.

Tests: Factory helper functions for test data generation.
Coverage Target: 100% (64/64 lines)
"""

import pytest

from tracertm.models import Item, Link, Project
from tracertm.testing_factories import (
    create_item,
    create_link,
    create_project,
)


@pytest.mark.unit
class TestCreateItemHelper:
    """Test create_item helper function."""

    def test_create_item_with_defaults(self) -> None:
        """Test create_item creates Item with default values."""
        # Act
        item = create_item()

        # Assert
        assert item is not None
        assert isinstance(item, Item)
        assert item.title == "Test Item"
        assert item.view == "FEATURE"
        assert item.item_type == "feature"
        assert item.status == "todo"
        assert item.priority == "medium"
        assert item.id is not None
        assert item.project_id is not None

    def test_create_item_with_custom_title(self) -> None:
        """Test create_item creates Item with custom title."""
        # Arrange
        custom_title = "Custom Test Item"

        # Act
        item = create_item(title=custom_title)

        # Assert
        assert item.title == custom_title
        assert item.view == "FEATURE"
        assert item.item_type == "feature"

    def test_create_item_with_custom_view(self) -> None:
        """Test create_item creates Item with custom view."""
        # Arrange
        custom_view = "CODE"

        # Act
        item = create_item(view=custom_view)

        # Assert
        assert item.title == "Test Item"
        assert item.view == custom_view
        assert item.item_type == "feature"

    def test_create_item_with_custom_type(self) -> None:
        """Test create_item creates Item with custom item_type."""
        # Arrange
        custom_type = "file"

        # Act
        item = create_item(item_type=custom_type)

        # Assert
        assert item.title == "Test Item"
        assert item.view == "FEATURE"
        assert item.item_type == custom_type

    def test_create_item_with_custom_project_id(self) -> None:
        """Test create_item creates Item with custom project_id."""
        # Arrange
        custom_project_id = "custom-project-123"

        # Act
        item = create_item(project_id=custom_project_id)

        # Assert
        assert item.project_id == custom_project_id

    def test_create_item_with_custom_status(self) -> None:
        """Test create_item creates Item with custom status."""
        # Arrange
        custom_status = "in_progress"

        # Act
        item = create_item(status=custom_status)

        # Assert
        assert item.status == custom_status

    def test_create_item_with_custom_priority(self) -> None:
        """Test create_item creates Item with custom priority."""
        # Arrange
        custom_priority = "high"

        # Act
        item = create_item(priority=custom_priority)

        # Assert
        assert item.priority == custom_priority

    def test_create_item_with_all_custom_values(self) -> None:
        """Test create_item creates Item with all custom values."""
        # Arrange
        custom_title = "Integration Test"
        custom_view = "TEST"
        custom_type = "test_case"
        custom_project_id = "proj-456"
        custom_status = "done"
        custom_priority = "low"

        # Act
        item = create_item(
            title=custom_title,
            view=custom_view,
            item_type=custom_type,
            project_id=custom_project_id,
            status=custom_status,
            priority=custom_priority,
        )

        # Assert
        assert item.title == custom_title
        assert item.view == custom_view
        assert item.item_type == custom_type
        assert item.project_id == custom_project_id
        assert item.status == custom_status
        assert item.priority == custom_priority

    def test_create_item_generates_unique_ids(self) -> None:
        """Test that create_item generates unique IDs for different items."""
        # Act
        item1 = create_item(title="Item 1")
        item2 = create_item(title="Item 2")

        # Assert
        assert item1.id != item2.id

    def test_create_item_auto_generates_project_id_when_none(self) -> None:
        """Test that create_item auto-generates project_id when not provided."""
        # Act
        item = create_item()

        # Assert
        assert item.project_id is not None
        assert len(str(item.project_id)) > 0

    def test_create_item_has_all_required_fields(self) -> None:
        """Test that created item has all required fields."""
        # Act
        item = create_item()

        # Assert
        assert hasattr(item, "id")
        assert hasattr(item, "project_id")
        assert hasattr(item, "title")
        assert hasattr(item, "view")
        assert hasattr(item, "item_type")
        assert hasattr(item, "status")
        assert hasattr(item, "priority")


@pytest.mark.unit
class TestCreateLinkHelper:
    """Test create_link helper function."""

    def test_create_link_with_defaults(self) -> None:
        """Test create_link creates Link with default values."""
        # Act
        link = create_link()

        # Assert
        assert link is not None
        assert isinstance(link, Link)
        assert link.source_item_id == "source"
        assert link.target_item_id == "target"
        assert link.link_type == "depends_on"
        assert link.id is not None
        assert link.project_id is not None

    def test_create_link_with_custom_source(self) -> None:
        """Test create_link creates Link with custom source_item_id."""
        # Arrange
        custom_source = "custom-source-123"

        # Act
        link = create_link(source_item_id=custom_source)

        # Assert
        assert link.source_item_id == custom_source
        assert link.target_item_id == "target"
        assert link.link_type == "depends_on"

    def test_create_link_with_custom_target(self) -> None:
        """Test create_link creates Link with custom target_item_id."""
        # Arrange
        custom_target = "custom-target-456"

        # Act
        link = create_link(target_item_id=custom_target)

        # Assert
        assert link.source_item_id == "source"
        assert link.target_item_id == custom_target
        assert link.link_type == "depends_on"

    def test_create_link_with_custom_type(self) -> None:
        """Test create_link creates Link with custom link_type."""
        # Arrange
        custom_type = "implements"

        # Act
        link = create_link(link_type=custom_type)

        # Assert
        assert link.source_item_id == "source"
        assert link.target_item_id == "target"
        assert link.link_type == custom_type

    def test_create_link_with_custom_project_id(self) -> None:
        """Test create_link creates Link with custom project_id."""
        # Arrange
        custom_project_id = "custom-project-789"

        # Act
        link = create_link(project_id=custom_project_id)

        # Assert
        assert link.project_id == custom_project_id

    def test_create_link_with_all_custom_values(self) -> None:
        """Test create_link creates Link with all custom values."""
        # Arrange
        custom_source = "feature-001"
        custom_target = "test-001"
        custom_type = "tests"
        custom_project_id = "proj-789"

        # Act
        link = create_link(
            source_item_id=custom_source,
            target_item_id=custom_target,
            link_type=custom_type,
            project_id=custom_project_id,
        )

        # Assert
        assert link.source_item_id == custom_source
        assert link.target_item_id == custom_target
        assert link.link_type == custom_type
        assert link.project_id == custom_project_id

    def test_create_link_generates_unique_ids(self) -> None:
        """Test that create_link generates unique IDs for different links."""
        # Act
        link1 = create_link(link_type="depends_on")
        link2 = create_link(link_type="implements")

        # Assert
        assert link1.id != link2.id

    def test_create_link_auto_generates_project_id_when_none(self) -> None:
        """Test that create_link auto-generates project_id when not provided."""
        # Act
        link = create_link()

        # Assert
        assert link.project_id is not None
        assert len(str(link.project_id)) > 0

    def test_create_link_has_all_required_fields(self) -> None:
        """Test that created link has all required fields."""
        # Act
        link = create_link()

        # Assert
        assert hasattr(link, "id")
        assert hasattr(link, "project_id")
        assert hasattr(link, "source_item_id")
        assert hasattr(link, "target_item_id")
        assert hasattr(link, "link_type")


@pytest.mark.unit
class TestCreateProjectHelper:
    """Test create_project helper function."""

    def test_create_project_with_defaults(self) -> None:
        """Test create_project creates Project with default values."""
        # Act
        project = create_project()

        # Assert
        assert project is not None
        assert isinstance(project, Project)
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.id is not None

    def test_create_project_with_custom_name(self) -> None:
        """Test create_project creates Project with custom name."""
        # Arrange
        custom_name = "My Custom Project"

        # Act
        project = create_project(name=custom_name)

        # Assert
        assert project.name == custom_name
        assert project.description == "A test project"

    def test_create_project_with_custom_description(self) -> None:
        """Test create_project creates Project with custom description."""
        # Arrange
        custom_description = "A custom project description"

        # Act
        project = create_project(description=custom_description)

        # Assert
        assert project.name == "Test Project"
        assert project.description == custom_description

    def test_create_project_with_all_custom_values(self) -> None:
        """Test create_project creates Project with all custom values."""
        # Arrange
        custom_name = "Integration Test Project"
        custom_description = "Project for integration testing"

        # Act
        project = create_project(
            name=custom_name,
            description=custom_description,
        )

        # Assert
        assert project.name == custom_name
        assert project.description == custom_description

    def test_create_project_generates_unique_ids(self) -> None:
        """Test that create_project generates unique IDs for different projects."""
        # Act
        project1 = create_project(name="Project 1")
        project2 = create_project(name="Project 2")

        # Assert
        assert project1.id != project2.id

    def test_create_project_has_all_required_fields(self) -> None:
        """Test that created project has all required fields."""
        # Act
        project = create_project()

        # Assert
        assert hasattr(project, "id")
        assert hasattr(project, "name")
        assert hasattr(project, "description")


@pytest.mark.unit
class TestFactoryIntegration:
    """Test factory integration and edge cases."""

    def test_multiple_items_have_unique_ids(self) -> None:
        """Test that factory creates items with unique IDs."""
        # Act
        item1 = create_item(title="Item 1")
        item2 = create_item(title="Item 2")
        item3 = create_item(title="Item 3")

        # Assert
        assert item1.id != item2.id
        assert item2.id != item3.id
        assert item1.id != item3.id

    def test_multiple_links_have_unique_ids(self) -> None:
        """Test that factory creates links with unique IDs."""
        # Act
        link1 = create_link(link_type="depends_on")
        link2 = create_link(link_type="implements")
        link3 = create_link(link_type="tests")

        # Assert
        assert link1.id != link2.id
        assert link2.id != link3.id
        assert link1.id != link3.id

    def test_multiple_projects_have_unique_ids(self) -> None:
        """Test that factory creates projects with unique IDs."""
        # Act
        project1 = create_project(name="Project 1")
        project2 = create_project(name="Project 2")
        project3 = create_project(name="Project 3")

        # Assert
        assert project1.id != project2.id
        assert project2.id != project3.id
        assert project1.id != project3.id

    def test_factory_preserves_model_structure(self) -> None:
        """Test that factories preserve model structure and required fields."""
        # Act
        item = create_item()
        link = create_link()
        project = create_project()

        # Assert - Item has all required attributes
        assert hasattr(item, "id")
        assert hasattr(item, "project_id")
        assert hasattr(item, "title")
        assert hasattr(item, "view")
        assert hasattr(item, "item_type")
        assert hasattr(item, "status")
        assert hasattr(item, "priority")

        # Assert - Link has all required attributes
        assert hasattr(link, "id")
        assert hasattr(link, "project_id")
        assert hasattr(link, "source_item_id")
        assert hasattr(link, "target_item_id")
        assert hasattr(link, "link_type")

        # Assert - Project has all required attributes
        assert hasattr(project, "id")
        assert hasattr(project, "name")
        assert hasattr(project, "description")

    def test_factory_creates_valid_string_ids(self) -> None:
        """Test that factories create valid string IDs."""
        # Act
        item = create_item()
        link = create_link()
        project = create_project()

        # Assert
        assert isinstance(item.id, str)
        assert len(item.id) > 0
        assert isinstance(link.id, str)
        assert len(link.id) > 0
        assert isinstance(project.id, str)
        assert len(project.id) > 0

    def test_item_and_link_can_share_project_id(self) -> None:
        """Test that items and links can be created with same project_id."""
        # Arrange
        shared_project_id = "shared-project-123"

        # Act
        item = create_item(project_id=shared_project_id)
        link = create_link(project_id=shared_project_id)

        # Assert
        assert item.project_id == shared_project_id
        assert link.project_id == shared_project_id
        assert item.project_id == link.project_id

    def test_link_can_reference_items(self) -> None:
        """Test that link can reference item IDs."""
        # Act
        item1 = create_item(title="Source Item")
        item2 = create_item(title="Target Item")
        link = create_link(
            source_item_id=str(item1.id),
            target_item_id=str(item2.id),
        )

        # Assert
        assert link.source_item_id == str(item1.id)
        assert link.target_item_id == str(item2.id)

    def test_empty_string_values_are_accepted(self) -> None:
        """Test that empty string values are accepted where appropriate."""
        # Act
        item = create_item(title="")
        project = create_project(name="", description="")

        # Assert
        assert item.title == ""
        assert project.name == ""
        assert project.description == ""

    def test_factory_handles_special_characters(self) -> None:
        """Test that factories handle special characters in strings."""
        # Arrange
        special_title = "Test Item @#$%^&*() 123"
        special_name = "Project with 日本語 and émojis 🎉"
        special_desc = "Description with\nnewlines\tand\ttabs"

        # Act
        item = create_item(title=special_title)
        project = create_project(name=special_name, description=special_desc)

        # Assert
        assert item.title == special_title
        assert project.name == special_name
        assert project.description == special_desc
