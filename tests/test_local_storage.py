from typing import Any

"""Tests for LocalStorageManager."""

import tempfile
from pathlib import Path

import pytest
import yaml

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.storage import LocalStorageManager


@pytest.fixture
def temp_storage_dir() -> None:
    """Create a temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_manager(temp_storage_dir: Any) -> None:
    """Create a LocalStorageManager instance."""
    return LocalStorageManager(base_dir=temp_storage_dir)


@pytest.fixture
def project_storage(storage_manager: Any) -> None:
    """Create a ProjectStorage instance."""
    ps = storage_manager.get_project_storage("test-project")
    ps.create_or_update_project(
        name="test-project",
        description="Test project for unit tests",
        metadata={"test": True},
    )
    return ps


@pytest.fixture
def item_storage(project_storage: Any) -> None:
    """Create an ItemStorage instance."""
    project = project_storage.get_project()
    return project_storage.get_item_storage(project)


class TestLocalStorageManager:
    """Tests for LocalStorageManager."""

    def test_init_creates_directories(self, temp_storage_dir: Any) -> None:
        """Test that initialization creates required directories."""
        LocalStorageManager(base_dir=temp_storage_dir)

        assert (temp_storage_dir / "tracertm.db").exists()
        assert (temp_storage_dir / "projects").exists()

    def test_database_schema_created(self, storage_manager: Any) -> None:
        """Test that database schema is created properly."""
        from sqlalchemy import text

        session = storage_manager.get_session()
        try:
            # Check that tables exist by querying them
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = {row[0] for row in result.fetchall()}

            assert "projects" in tables
            assert "items" in tables
            assert "links" in tables
            assert "sync_queue" in tables
            assert "sync_state" in tables
            assert "items_fts" in tables
        finally:
            session.close()

    def test_sync_queue_operations(self, storage_manager: Any) -> None:
        """Test sync queue operations."""
        # Queue a change
        storage_manager.queue_sync(
            entity_type="item",
            entity_id="test-123",
            operation="create",
            payload={"title": "Test Item"},
        )

        # Get queue
        queue = storage_manager.get_sync_queue()
        assert len(queue) == 1
        assert queue[0]["entity_type"] == "item"
        assert queue[0]["entity_id"] == "test-123"
        assert queue[0]["operation"] == "create"
        assert queue[0]["payload"]["title"] == "Test Item"

        # Clear queue entry
        storage_manager.clear_sync_queue_entry(queue[0]["id"])

        # Verify cleared
        queue = storage_manager.get_sync_queue()
        assert len(queue) == 0

    def test_sync_state_operations(self, storage_manager: Any) -> None:
        """Test sync state operations."""
        # Set state
        storage_manager.update_sync_state("last_sync", "2024-01-15T10:30:00Z")

        # Get state
        value = storage_manager.get_sync_state("last_sync")
        assert value == "2024-01-15T10:30:00Z"

        # Update state
        storage_manager.update_sync_state("last_sync", "2024-01-16T12:00:00Z")
        value = storage_manager.get_sync_state("last_sync")
        assert value == "2024-01-16T12:00:00Z"

        # Non-existent key
        value = storage_manager.get_sync_state("non_existent")
        assert value is None


class TestProjectStorage:
    """Tests for ProjectStorage."""

    def test_create_project(self, storage_manager: Any, temp_storage_dir: Any) -> None:
        """Test project creation."""
        ps = storage_manager.get_project_storage("my-project")
        project = ps.create_or_update_project(
            name="my-project",
            description="A test project",
            metadata={"version": "1.0"},
        )

        assert project.name == "my-project"
        assert project.description == "A test project"
        assert project.project_metadata["version"] == "1.0"

        # Check directories created
        project_dir = temp_storage_dir / "projects" / "my-project"
        assert project_dir.exists()
        assert (project_dir / "epics").exists()
        assert (project_dir / "stories").exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / "tasks").exists()
        assert (project_dir / ".meta").exists()

        # Check README.md created
        readme_path = project_dir / "README.md"
        assert readme_path.exists()
        readme_content = readme_path.read_text()
        assert "my-project" in readme_content
        assert "A test project" in readme_content

        # Check links.yaml created
        links_path = project_dir / ".meta" / "links.yaml"
        assert links_path.exists()

    def test_update_project(self, project_storage: Any) -> None:
        """Test project update."""
        project = project_storage.get_project()
        original_id = project.id

        # Update project
        updated_project = project_storage.create_or_update_project(
            name="test-project",
            description="Updated description",
            metadata={"test": True, "updated": True},
        )

        assert updated_project.id == original_id
        assert updated_project.description == "Updated description"
        assert updated_project.project_metadata["updated"] is True

    def test_get_project(self, project_storage: Any) -> None:
        """Test getting a project."""
        project = project_storage.get_project()
        assert project is not None
        assert project.name == "test-project"


class TestItemStorage:
    """Tests for ItemStorage."""

    def test_create_item(self, item_storage: Any, temp_storage_dir: Any) -> None:
        """Test item creation."""
        item = item_storage.create_item(
            title="User Authentication",
            item_type="epic",
            external_id="EPIC-001",
            description="Implement user authentication system",
            status="in_progress",
            priority="high",
            owner="@dev-team",
            metadata={"tags": ["security", "auth"]},
        )

        assert item.title == "User Authentication"
        assert item.item_type == "epic"
        assert item.status == "in_progress"
        assert item.priority == "high"
        assert item.owner == "@dev-team"
        assert item.item_metadata["external_id"] == "EPIC-001"
        assert "content_hash" in item.item_metadata

        # Check markdown file created
        epic_path = temp_storage_dir / "projects" / "test-project" / "epics" / "EPIC-001.md"
        assert epic_path.exists()

        # Parse markdown content
        content = epic_path.read_text()
        assert "---" in content
        assert "# User Authentication" in content

        # Parse frontmatter
        parts = content.split("---")
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["external_id"] == "EPIC-001"
        assert frontmatter["type"] == "epic"
        assert frontmatter["status"] == "in_progress"
        assert frontmatter["priority"] == "high"
        assert frontmatter["tags"] == ["security", "auth"]

    def test_update_item(self, item_storage: Any) -> None:
        """Test item update."""
        # Create item
        item = item_storage.create_item(
            title="Original Title",
            item_type="story",
            external_id="STORY-001",
            status="todo",
        )

        original_id = item.id

        # Update item
        updated_item = item_storage.update_item(
            item_id=item.id,
            title="Updated Title",
            status="in_progress",
            metadata={"updated": True},
        )

        assert updated_item.id == original_id
        assert updated_item.title == "Updated Title"
        assert updated_item.status == "in_progress"
        assert updated_item.item_metadata["updated"] is True

        # Verify new content hash
        assert "content_hash" in updated_item.item_metadata

    def test_delete_item(self, item_storage: Any) -> None:
        """Test item deletion."""
        # Create item
        item = item_storage.create_item(
            title="To be deleted",
            item_type="task",
            external_id="TASK-001",
        )

        item_id = item.id

        # Delete item
        item_storage.delete_item(item_id)

        # Verify soft delete
        deleted_item = item_storage.get_item(item_id)
        assert deleted_item is not None
        assert deleted_item.deleted_at is not None

    def test_list_items(self, item_storage: Any) -> None:
        """Test listing items."""
        # Create multiple items
        item_storage.create_item(
            title="Epic 1",
            item_type="epic",
            external_id="EPIC-001",
            status="in_progress",
        )
        item_storage.create_item(
            title="Epic 2",
            item_type="epic",
            external_id="EPIC-002",
            status="todo",
        )
        item_storage.create_item(
            title="Story 1",
            item_type="story",
            external_id="STORY-001",
            status="in_progress",
        )

        # List all items
        all_items = item_storage.list_items()
        assert len(all_items) == COUNT_THREE

        # List epics only
        epics = item_storage.list_items(item_type="epic")
        assert len(epics) == COUNT_TWO
        assert all(item.item_type == "epic" for item in epics)

        # List in_progress items
        in_progress = item_storage.list_items(status="in_progress")
        assert len(in_progress) == COUNT_TWO
        assert all(item.status == "in_progress" for item in in_progress)

    def test_create_link(self, item_storage: Any, temp_storage_dir: Any) -> None:
        """Test creating traceability links."""
        # Create items
        epic = item_storage.create_item(
            title="Epic 1",
            item_type="epic",
            external_id="EPIC-001",
        )
        story = item_storage.create_item(
            title="Story 1",
            item_type="story",
            external_id="STORY-001",
        )

        # Create link
        link = item_storage.create_link(
            source_id=epic.id,
            target_id=story.id,
            link_type="implements",
            metadata={"note": "Epic contains this story"},
        )

        assert link.source_item_id == epic.id
        assert link.target_item_id == story.id
        assert link.link_type == "implements"
        assert link.link_metadata["note"] == "Epic contains this story"

        # Check links.yaml updated
        links_path = temp_storage_dir / "projects" / "test-project" / ".meta" / "links.yaml"
        links_content = yaml.safe_load(links_path.read_text())

        assert len(links_content["links"]) == 1
        assert links_content["links"][0]["source"] == "EPIC-001"
        assert links_content["links"][0]["target"] == "STORY-001"
        assert links_content["links"][0]["type"] == "implements"

    def test_delete_link(self, item_storage: Any) -> None:
        """Test deleting links."""
        # Create items
        epic = item_storage.create_item(
            title="Epic 1",
            item_type="epic",
            external_id="EPIC-001",
        )
        story = item_storage.create_item(
            title="Story 1",
            item_type="story",
            external_id="STORY-001",
        )

        # Create link
        link = item_storage.create_link(
            source_id=epic.id,
            target_id=story.id,
            link_type="implements",
        )

        link_id = link.id

        # Delete link
        item_storage.delete_link(link_id)

        # Verify deleted
        links = item_storage.list_links()
        assert len(links) == 0

    def test_list_links(self, item_storage: Any) -> None:
        """Test listing links."""
        # Create items
        epic = item_storage.create_item(
            title="Epic 1",
            item_type="epic",
            external_id="EPIC-001",
        )
        story1 = item_storage.create_item(
            title="Story 1",
            item_type="story",
            external_id="STORY-001",
        )
        story2 = item_storage.create_item(
            title="Story 2",
            item_type="story",
            external_id="STORY-002",
        )

        # Create links
        item_storage.create_link(
            source_id=epic.id,
            target_id=story1.id,
            link_type="implements",
        )
        item_storage.create_link(
            source_id=epic.id,
            target_id=story2.id,
            link_type="implements",
        )
        item_storage.create_link(
            source_id=story2.id,
            target_id=story1.id,
            link_type="depends_on",
        )

        # List all links
        all_links = item_storage.list_links()
        assert len(all_links) == COUNT_THREE

        # List by source
        epic_links = item_storage.list_links(source_id=epic.id)
        assert len(epic_links) == COUNT_TWO

        # List by link type
        implements_links = item_storage.list_links(link_type="implements")
        assert len(implements_links) == COUNT_TWO


class TestFullTextSearch:
    """Tests for full-text search."""

    def test_search_items(self, storage_manager: Any, item_storage: Any) -> None:
        """Test full-text search."""
        # Create items with searchable content
        item_storage.create_item(
            title="User Authentication System",
            item_type="epic",
            external_id="EPIC-001",
            description="Implement OAuth2 and JWT authentication",
        )
        item_storage.create_item(
            title="Login Page",
            item_type="story",
            external_id="STORY-001",
            description="Create login form with email and password",
        )
        item_storage.create_item(
            title="Password Reset",
            item_type="story",
            external_id="STORY-002",
            description="Implement password reset flow",
        )

        # Search for "authentication"
        results = storage_manager.search_items("authentication")
        assert len(results) >= 1
        assert any("Authentication" in item.title for item in results)

        # Search for "password"
        results = storage_manager.search_items("password")
        assert len(results) >= COUNT_TWO


class TestMarkdownGeneration:
    """Tests for markdown file generation."""

    def test_markdown_with_links(self, item_storage: Any, temp_storage_dir: Any) -> None:
        """Test markdown generation with traceability links."""
        # Create epic and story
        epic = item_storage.create_item(
            title="User Management",
            item_type="epic",
            external_id="EPIC-001",
            description="Complete user management system",
            status="in_progress",
            priority="high",
            metadata={"tags": ["users", "admin"]},
        )
        story = item_storage.create_item(
            title="User Registration",
            item_type="story",
            external_id="STORY-001",
        )

        # Create link
        item_storage.create_link(
            source_id=epic.id,
            target_id=story.id,
            link_type="implements",
        )

        # Re-generate markdown (happens automatically on link creation)
        epic_path = temp_storage_dir / "projects" / "test-project" / "epics" / "EPIC-001.md"
        content = epic_path.read_text()

        # Parse frontmatter
        parts = content.split("---")
        frontmatter = yaml.safe_load(parts[1])

        # Verify links in frontmatter
        assert "links" in frontmatter
        assert len(frontmatter["links"]) == 1
        assert frontmatter["links"][0]["type"] == "implements"
        assert frontmatter["links"][0]["target"] == "STORY-001"

        # Verify tags
        assert frontmatter["tags"] == ["users", "admin"]

        # Verify content
        assert "# User Management" in content
        assert "Complete user management system" in content
