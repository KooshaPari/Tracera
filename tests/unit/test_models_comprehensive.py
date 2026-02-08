"""Comprehensive unit tests for all models.

Tests: Model creation, properties, relationships
"""

from tests.test_constants import COUNT_TWO
from tracertm.models.agent import Agent
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class TestItemModelComprehensive:
    """Comprehensive Item model tests."""

    def test_item_creation_minimal(self) -> None:
        """Test creating item with minimal fields."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="feature")
        assert item.project_id == "p1"
        assert item.title == "Test"

    def test_item_creation_full(self) -> None:
        """Test creating item with all fields."""
        item = Item(
            project_id="p1",
            title="Test",
            description="Desc",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            parent_id="parent-1",
            item_metadata={"key": "value"},
        )
        assert item.description == "Desc"
        assert item.status == "in_progress"
        assert item.item_metadata["key"] == "value"

    def test_item_with_status(self) -> None:
        """Test item with explicit status."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="feature", status="in_progress")
        assert item.status == "in_progress"

    def test_item_with_version(self) -> None:
        """Test item with explicit version."""
        item = Item(project_id="p1", title="Test", view="FEATURE", item_type="feature")
        item.version = 2
        assert item.version == COUNT_TWO

    def test_item_with_metadata(self) -> None:
        """Test item with metadata."""
        item = Item(
            project_id="p1",
            title="Test",
            view="FEATURE",
            item_type="feature",
            item_metadata={"priority": "high", "tags": ["urgent"]},
        )
        assert item.item_metadata["priority"] == "high"


class TestProjectModelComprehensive:
    """Comprehensive Project model tests."""

    def test_project_creation(self) -> None:
        """Test creating project."""
        project = Project(name="Test Project", description="Description")
        assert project.name == "Test Project"
        assert project.description == "Description"

    def test_project_metadata(self) -> None:
        """Test project metadata."""
        project = Project(name="Test", project_metadata={"owner": "user1"})
        assert project.project_metadata["owner"] == "user1"

    def test_project_metadata_update(self) -> None:
        """Test updating project metadata."""
        project = Project(name="Test")
        project.project_metadata = {"key": "value"}
        assert project.project_metadata["key"] == "value"


class TestLinkModelComprehensive:
    """Comprehensive Link model tests."""

    def test_link_creation(self) -> None:
        """Test creating link."""
        link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="depends_on")
        assert link.source_item_id == "i1"
        assert link.target_item_id == "i2"

    def test_link_types(self) -> None:
        """Test all link types."""
        types = ["depends_on", "blocks", "relates_to", "duplicates", "parent_of", "implements", "tests"]
        for link_type in types:
            link = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type=link_type)
            assert link.link_type == link_type

    def test_link_metadata(self) -> None:
        """Test link metadata."""
        link = Link(
            project_id="p1",
            source_item_id="i1",
            target_item_id="i2",
            link_type="depends_on",
            link_metadata={"priority": "high"},
        )
        assert link.link_metadata["priority"] == "high"


class TestAgentModelComprehensive:
    """Comprehensive Agent model tests."""

    def test_agent_creation(self) -> None:
        """Test creating agent."""
        agent = Agent(project_id="p1", name="agent-1", agent_type="analyzer")
        assert agent.name == "agent-1"
        assert agent.agent_type == "analyzer"

    def test_agent_types(self) -> None:
        """Test agent types."""
        types = ["analyzer", "writer", "reviewer", "coordinator"]
        for agent_type in types:
            agent = Agent(project_id="p1", name="agent", agent_type=agent_type)
            assert agent.agent_type == agent_type

    def test_agent_metadata(self) -> None:
        """Test agent metadata."""
        agent = Agent(project_id="p1", name="agent-1", agent_type="analyzer", agent_metadata={"version": "1.0"})
        assert agent.agent_metadata["version"] == "1.0"


class TestModelRelationships:
    """Test relationships between models."""

    def test_item_hierarchy(self) -> None:
        """Test item parent-child relationship."""
        parent = Item(project_id="p1", title="Parent", view="FEATURE", item_type="feature")
        child = Item(project_id="p1", title="Child", view="FEATURE", item_type="feature", parent_id=parent.id)

        assert child.parent_id == parent.id

    def test_link_chain(self) -> None:
        """Test link chain."""
        link1 = Link(project_id="p1", source_item_id="i1", target_item_id="i2", link_type="depends_on")
        link2 = Link(project_id="p1", source_item_id="i2", target_item_id="i3", link_type="depends_on")

        assert link1.target_item_id == link2.source_item_id

    def test_project_items(self) -> None:
        """Test project contains items."""
        project = Project(name="Test")
        item1 = Item(project_id=project.id, title="Item1", view="FEATURE", item_type="feature")
        item2 = Item(project_id=project.id, title="Item2", view="FEATURE", item_type="feature")

        assert item1.project_id == project.id
        assert item2.project_id == project.id
