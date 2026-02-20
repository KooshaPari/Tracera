from typing import Any

"""Tests for project-local .trace/ storage functionality."""

import tempfile
from pathlib import Path

import pytest
import yaml

from tests.test_constants import COUNT_TWO
from tracertm.storage.local_storage import LocalStorageManager


class TestProjectLocalStorage:
    """Test project-local .trace/ directory management."""

    @pytest.fixture
    def temp_dir(self) -> None:
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def storage(self, temp_dir: Any) -> None:
        """Create a LocalStorageManager with temporary base directory."""
        return LocalStorageManager(base_dir=temp_dir / ".tracertm")

    def test_is_trace_project_exists(self, temp_dir: Any, storage: Any) -> None:
        """Test is_trace_project returns True when .trace/ exists."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()
        trace_dir = project_dir / ".trace"
        trace_dir.mkdir()

        assert storage.is_trace_project(project_dir) is True

    def test_is_trace_project_not_exists(self, temp_dir: Any, storage: Any) -> None:
        """Test is_trace_project returns False when .trace/ doesn't exist."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()

        assert storage.is_trace_project(project_dir) is False

    def test_get_project_trace_dir_exists(self, temp_dir: Any, storage: Any) -> None:
        """Test get_project_trace_dir returns path when .trace/ exists."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()
        trace_dir = project_dir / ".trace"
        trace_dir.mkdir()

        result = storage.get_project_trace_dir(project_dir)
        assert result.resolve() == trace_dir.resolve()

    def test_get_project_trace_dir_not_exists(self, temp_dir: Any, storage: Any) -> None:
        """Test get_project_trace_dir returns None when .trace/ doesn't exist."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()

        result = storage.get_project_trace_dir(project_dir)
        assert result is None

    def test_init_project_creates_structure(self, temp_dir: Any, storage: Any) -> None:
        """Test init_project creates complete .trace/ structure."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()

        trace_dir, project_id = storage.init_project(project_dir, project_name="My Project", description="Test project")

        # Check directory structure
        assert trace_dir.exists()
        assert (trace_dir / "project.yaml").exists()
        assert (trace_dir / "epics").is_dir()
        assert (trace_dir / "stories").is_dir()
        assert (trace_dir / "tests").is_dir()
        assert (trace_dir / "tasks").is_dir()
        assert (trace_dir / "docs").is_dir()
        assert (trace_dir / "changes").is_dir()
        assert (trace_dir / ".meta").is_dir()
        assert (trace_dir / ".meta" / "links.yaml").exists()
        assert (trace_dir / ".meta" / "agents.yaml").exists()

        # Check project.yaml content
        project_yaml = yaml.safe_load((trace_dir / "project.yaml").read_text())
        assert project_yaml["id"] == project_id
        assert project_yaml["name"] == "My Project"
        assert project_yaml["description"] == "Test project"
        assert "counters" in project_yaml
        assert project_yaml["counters"]["epic"] == 0
        assert project_yaml["counters"]["story"] == 0

        # Check .gitignore created
        gitignore = project_dir / ".gitignore"
        assert gitignore.exists()
        assert ".trace/.meta/sync.yaml" in gitignore.read_text()

    def test_init_project_already_exists(self, temp_dir: Any, storage: Any) -> None:
        """Test init_project raises error when .trace/ already exists."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()
        (project_dir / ".trace").mkdir()

        with pytest.raises(ValueError, match="already initialized"):
            storage.init_project(project_dir)

    def test_register_project(self, temp_dir: Any, storage: Any) -> None:
        """Test register_project registers an existing .trace/ directory."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()

        # Create .trace/ manually
        trace_dir = project_dir / ".trace"
        trace_dir.mkdir()

        project_yaml = trace_dir / "project.yaml"
        project_data = {
            "id": "test-project-id",
            "name": "Test Project",
            "description": "A test project",
            "counters": {"epic": 0, "story": 0, "test": 0, "task": 0},
        }
        project_yaml.write_text(yaml.dump(project_data))

        # Register project
        project_id = storage.register_project(project_dir)

        assert project_id == "test-project-id"

        # Verify in database
        from sqlalchemy import text

        session = storage.get_session()
        try:
            result = session.execute(
                text("SELECT * FROM project_registry WHERE id = :id"),
                {"id": project_id},
            )
            row = result.fetchone()
            assert row is not None
            assert row[0] == "test-project-id"  # id column
            assert row[1] == "Test Project"  # name column
        finally:
            session.close()

    def test_get_project_counters(self, temp_dir: Any, storage: Any) -> None:
        """Test get_project_counters reads counters from project.yaml."""
        project_dir = temp_dir / "my-project"
        storage.init_project(project_dir)

        counters = storage.get_project_counters(project_dir)
        assert counters == {"epic": 0, "story": 0, "test": 0, "task": 0}

    def test_increment_project_counter(self, temp_dir: Any, storage: Any) -> None:
        """Test increment_project_counter updates counters in project.yaml."""
        project_dir = temp_dir / "my-project"
        storage.init_project(project_dir)

        # Increment epic counter
        counter_value, external_id = storage.increment_project_counter(project_dir, "epic")

        assert counter_value == 1
        assert external_id == "EPIC-001"

        # Verify in file
        counters = storage.get_project_counters(project_dir)
        assert counters["epic"] == 1

        # Increment again
        counter_value2, external_id2 = storage.increment_project_counter(project_dir, "epic")

        assert counter_value2 == COUNT_TWO
        assert external_id2 == "EPIC-002"

    def test_get_current_project_path(self, temp_dir: Any, storage: Any, monkeypatch: Any) -> None:
        """Test get_current_project_path finds .trace/ in parent directories."""
        project_dir = temp_dir / "my-project"
        storage.init_project(project_dir)

        # Change to subdirectory
        subdir = project_dir / "src" / "app"
        subdir.mkdir(parents=True)

        monkeypatch.chdir(subdir)

        result = storage.get_current_project_path()
        assert result.resolve() == project_dir.resolve()

    def test_get_current_project_path_not_found(self, temp_dir: Any, storage: Any, monkeypatch: Any) -> None:
        """Test get_current_project_path returns None when no .trace/ found."""
        project_dir = temp_dir / "my-project"
        project_dir.mkdir()

        monkeypatch.chdir(project_dir)

        result = storage.get_current_project_path()
        assert result is None

    def test_index_project(self, temp_dir: Any, storage: Any) -> None:
        """Test index_project indexes all markdown files into SQLite."""
        project_dir = temp_dir / "my-project"
        trace_dir, _project_id = storage.init_project(project_dir)

        # Create a test epic markdown file
        epic_md = trace_dir / "epics" / "EPIC-001.md"
        epic_content = """---
id: "epic-001-uuid"
external_id: "EPIC-001"
type: epic
status: todo
priority: high
owner: "@alice"
created: 2024-01-15T10:30:00
updated: 2024-01-15T10:30:00
version: 1
---

# User Authentication

## Description

Implement user authentication system with OAuth2 support.
"""
        epic_md.write_text(epic_content)

        # Create a test story markdown file
        story_md = trace_dir / "stories" / "STORY-001.md"
        story_content = """---
id: "story-001-uuid"
external_id: "STORY-001"
type: story
status: in_progress
priority: medium
owner: "@bob"
parent: "epic-001-uuid"
created: 2024-01-16T09:00:00
updated: 2024-01-16T09:00:00
version: 1
---

# Login Page

## Description

Create login page with email and password fields.
"""
        story_md.write_text(story_content)

        # Index the project
        counts = storage.index_project(project_dir)

        assert counts["epics"] == 1
        assert counts["stories"] == 1
        assert counts["tests"] == 0
        assert counts["tasks"] == 0

        # Verify items in database
        session = storage.get_session()
        from tracertm.models import Item

        epic = session.get(Item, "epic-001-uuid")
        assert epic is not None
        assert epic.title == "User Authentication"
        assert epic.item_type == "epic"
        assert epic.status == "todo"
        assert epic.priority == "high"

        story = session.get(Item, "story-001-uuid")
        assert story is not None
        assert story.title == "Login Page"
        assert story.item_type == "story"
        assert story.status == "in_progress"
        assert story.parent_id == "epic-001-uuid"

        session.close()

    def test_get_project_storage_for_path(self, temp_dir: Any, storage: Any) -> None:
        """Test get_project_storage_for_path returns ProjectStorage for .trace/ directory."""
        project_dir = temp_dir / "my-project"
        storage.init_project(project_dir, project_name="My Project")

        project_storage = storage.get_project_storage_for_path(project_dir)

        assert project_storage is not None
        assert project_storage.project_name == "My Project"
        assert project_storage.is_project_local is True
        assert project_storage.epics_dir.exists()

    def test_project_storage_local_mode(self, temp_dir: Any, storage: Any) -> None:
        """Test ProjectStorage works in project-local mode."""
        project_dir = temp_dir / "my-project"
        trace_dir, _project_id = storage.init_project(project_dir, project_name="My Project")

        project_storage = storage.get_project_storage_for_path(project_dir)

        assert project_storage.project_dir.resolve() == trace_dir.resolve()
        assert project_storage.is_project_local is True
        assert project_storage.docs_dir.exists()
        assert project_storage.changes_dir.exists()

    def test_project_storage_global_projects_dir(self, temp_dir: Any, _storage: Any) -> None:
        """Test ProjectStorage works with global projects dir (~/.tracertm/projects/)."""
        project_storage = storage.get_project_storage("global-project")

        assert project_storage.is_project_local is False
        assert str(storage.projects_dir) in str(project_storage.project_dir)
