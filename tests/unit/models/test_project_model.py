"""Unit tests for Project model - focused on actual model structure."""

import pytest

from tracertm.models import Project

pytestmark = pytest.mark.unit


class TestProjectModelCreation:
    """Test Project model creation with actual fields."""

    def test_project_creation_with_name_only(self) -> None:
        """Project creates successfully with just name field."""
        project = Project(name="Test Project")
        assert project.name == "Test Project"

    def test_project_creation_with_all_fields(self) -> None:
        """Project creates successfully with all fields."""
        metadata = {"env": "test", "version": "1.0"}
        project = Project(name="Full Project", description="A complete project", project_metadata=metadata)
        assert project.name == "Full Project"
        assert project.description == "A complete project"
        assert project.project_metadata == metadata

    def test_project_creation_with_explicit_id(self) -> None:
        """Project can be created with explicit ID."""
        project_id = "test-id-123"
        project = Project(name="Test", id=project_id)
        assert project.id == project_id

    def test_project_description_optional(self) -> None:
        """Project description can be provided."""
        project = Project(name="Test", description="Project description")
        assert project.description == "Project description"

    def test_project_metadata_can_be_set(self) -> None:
        """Project metadata can be set during creation."""
        metadata = {"key": "value"}
        project = Project(name="Test", project_metadata=metadata)
        assert project.project_metadata == metadata

    def test_project_has_timestamp_attributes(self) -> None:
        """Project has timestamp attributes from TimestampMixin."""
        project = Project(name="Test")
        assert hasattr(project, "created_at")
        assert hasattr(project, "updated_at")


class TestProjectModelMetadataAlias:
    """Test Project model metadata aliasing."""

    def test_metadata_alias_getter(self) -> None:
        """Project supports metadata alias for project_metadata."""
        project = Project(name="Test", project_metadata={"key": "value"})
        assert project.metadata == project.project_metadata

    def test_metadata_alias_setter(self) -> None:
        """Project metadata can be set via alias."""
        project = Project(name="Test")
        project.metadata = {"key": "new_value"}
        assert project.project_metadata == {"key": "new_value"}


class TestProjectModelValidation:
    """Test Project model validation."""

    def test_project_name_is_stored(self) -> None:
        """Project name field is properly stored."""
        project = Project(name="Test Project")
        assert project.name == "Test Project"

    def test_project_name_type(self) -> None:
        """Project name is string type."""
        project = Project(name="Test")
        assert isinstance(project.name, str)


class TestProjectModelComparison:
    """Test Project model comparison."""

    def test_projects_with_different_ids(self) -> None:
        """Projects with different IDs are different."""
        p1 = Project(name="Project", id="id-1")
        p2 = Project(name="Project", id="id-2")
        # They should have different IDs
        assert p1.id != p2.id

    def test_project_name_independence(self) -> None:
        """Projects can have same name but different IDs."""
        p1 = Project(name="Shared Name", id="id-1")
        p2 = Project(name="Shared Name", id="id-2")
        # Different instances with different IDs
        assert p1.id != p2.id
        assert p1.name == p2.name


class TestProjectModelRepresentation:
    """Test Project model string representation."""

    def test_project_repr(self) -> None:
        """Project has useful repr."""
        project = Project(name="Test Project")
        repr_str = repr(project)
        assert "Project" in repr_str
        assert "Test Project" in repr_str


class TestProjectModelIndexing:
    """Test Project model getitem support."""

    def test_project_getitem_access(self) -> None:
        """Project supports dictionary-style access."""
        project = Project(name="Test")
        assert project["name"] == "Test"

    def test_project_getitem_for_metadata(self) -> None:
        """Project getitem works with project_metadata."""
        metadata = {"custom": "value"}
        project = Project(name="Test", project_metadata=metadata)
        assert project["project_metadata"] == metadata
