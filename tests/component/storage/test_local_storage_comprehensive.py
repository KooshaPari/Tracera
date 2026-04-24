"""Comprehensive tests for LocalStorageManager.

Tests cover:
- Project initialization and registration
- Counter management
- Index operations
- Project discovery
- FTS (Full-Text Search) operations
- Sync queue operations
- Project storage integration
"""

import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import yaml
from sqlalchemy import text

from tests.test_constants import COUNT_FIVE
from tracertm.storage.local_storage import (
    LocalStorageManager,
    ProjectStorage,
)


@pytest.fixture
def temp_base_dir() -> None:
    """Create temporary base directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_manager(temp_base_dir: Any) -> None:
    """Create LocalStorageManager instance."""
    return LocalStorageManager(base_dir=temp_base_dir)


@pytest.fixture
def temp_project_dir() -> None:
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestLocalStorageManagerInit:
    """Test LocalStorageManager initialization."""

    def test_default_base_dir(self) -> None:
        """Test default base directory creation."""
        manager = LocalStorageManager()
        assert manager.base_dir == Path.home() / ".tracertm"
        assert manager.base_dir.exists()

    def test_custom_base_dir(self, temp_base_dir: Any) -> None:
        """Test custom base directory."""
        manager = LocalStorageManager(base_dir=temp_base_dir)
        assert manager.base_dir == temp_base_dir
        assert manager.base_dir.exists()

    def test_db_initialization(self, storage_manager: Any) -> None:
        """Test database file creation."""
        assert storage_manager.db_path.exists()
        assert storage_manager.db_path.name == "tracertm.db"

    def test_projects_dir_creation(self, storage_manager: Any) -> None:
        """Test projects directory creation (legacy)."""
        assert storage_manager.projects_dir.exists()
        assert storage_manager.projects_dir.name == "projects"

    def test_schema_tables_created(self, storage_manager: Any) -> None:
        """Test that all required tables are created."""
        session = storage_manager.get_session()
        try:
            # Check project_registry table
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='project_registry'"),
            )
            assert result.fetchone() is not None

            # Check sync_queue table
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_queue'"))
            assert result.fetchone() is not None

            # Check sync_state table
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_state'"))
            assert result.fetchone() is not None

            # Check items_fts table
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='items_fts'"))
            assert result.fetchone() is not None
        finally:
            session.close()


class TestProjectInitialization:
    """Test project initialization with .trace/ directory."""

    def test_init_project_creates_trace_dir(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test .trace/ directory creation."""
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        assert trace_dir.exists()
        assert trace_dir.name == ".trace"
        # Use resolve to handle /var vs /private/var symlinks on macOS
        assert trace_dir.parent.resolve() == temp_project_dir.resolve()

    def test_init_project_creates_subdirectories(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test subdirectory creation."""
        trace_dir, _ = storage_manager.init_project(temp_project_dir)

        expected_dirs = ["epics", "stories", "tests", "tasks", "docs", "changes", ".meta"]
        for subdir in expected_dirs:
            assert (trace_dir / subdir).exists()
            assert (trace_dir / subdir).is_dir()

    def test_init_project_creates_project_yaml(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test project.yaml creation."""
        trace_dir, project_id = storage_manager.init_project(
            temp_project_dir,
            project_name="TestProject",
            description="Test description",
        )

        project_yaml = trace_dir / "project.yaml"
        assert project_yaml.exists()

        config = yaml.safe_load(project_yaml.read_text())
        assert config["id"] == project_id
        assert config["name"] == "TestProject"
        assert config["description"] == "Test description"
        assert "counters" in config
        assert config["counters"] == {"epic": 0, "story": 0, "test": 0, "task": 0}

    def test_init_project_default_name(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test default project name from directory."""
        trace_dir, _ = storage_manager.init_project(temp_project_dir)

        project_yaml = trace_dir / "project.yaml"
        config = yaml.safe_load(project_yaml.read_text())
        assert config["name"] == temp_project_dir.name

    def test_init_project_creates_links_yaml(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test links.yaml creation."""
        trace_dir, _ = storage_manager.init_project(temp_project_dir)

        links_yaml = trace_dir / ".meta" / "links.yaml"
        assert links_yaml.exists()
        content = links_yaml.read_text()
        assert "links: []" in content

    def test_init_project_creates_agents_yaml(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test agents.yaml creation."""
        trace_dir, _ = storage_manager.init_project(temp_project_dir)

        agents_yaml = trace_dir / ".meta" / "agents.yaml"
        assert agents_yaml.exists()
        content = agents_yaml.read_text()
        assert "agents: []" in content

    def test_init_project_updates_gitignore(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test .gitignore update."""
        _trace_dir, _ = storage_manager.init_project(temp_project_dir)

        gitignore = temp_project_dir / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert ".trace/.meta/sync.yaml" in content

    def test_init_project_appends_to_existing_gitignore(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test appending to existing .gitignore."""
        # Create existing .gitignore
        gitignore = temp_project_dir / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n")

        _trace_dir, _ = storage_manager.init_project(temp_project_dir)

        content = gitignore.read_text()
        assert "*.pyc" in content
        assert ".trace/.meta/sync.yaml" in content

    def test_init_project_raises_if_already_exists(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test error when project already initialized."""
        storage_manager.init_project(temp_project_dir)

        with pytest.raises(ValueError, match="already initialized"):
            storage_manager.init_project(temp_project_dir)

    def test_init_project_registers_in_db(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test project registration in database."""
        _trace_dir, project_id = storage_manager.init_project(temp_project_dir)

        session = storage_manager.get_session()
        try:
            result = session.execute(text("SELECT * FROM project_registry WHERE id = :id"), {"id": project_id})
            row = result.fetchone()
            assert row is not None
            # Use realpath to handle /var vs /private/var symlinks on macOS
            assert Path(row.path).resolve() == temp_project_dir.resolve()
        finally:
            session.close()

    def test_init_project_with_metadata(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test project initialization with custom metadata."""
        metadata = {"team": "Engineering", "tags": ["backend", "api"]}
        trace_dir, _ = storage_manager.init_project(temp_project_dir, metadata=metadata)

        project_yaml = trace_dir / "project.yaml"
        config = yaml.safe_load(project_yaml.read_text())
        assert config["metadata"] == metadata


class TestProjectRegistration:
    """Test project registration."""

    def test_register_existing_project(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test registering existing .trace/ directory."""
        # Initialize project first
        _trace_dir, original_id = storage_manager.init_project(temp_project_dir)

        # Create new manager (simulating restart)
        new_manager = LocalStorageManager(base_dir=storage_manager.base_dir)

        # Register the existing project
        project_id = new_manager.register_project(temp_project_dir)
        assert project_id == original_id

    def test_register_project_without_trace_raises(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test error when .trace/ doesn't exist."""
        with pytest.raises(ValueError, match="No .trace/ directory found"):
            storage_manager.register_project(temp_project_dir)

    def test_register_project_without_yaml_raises(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test error when project.yaml missing."""
        trace_dir = temp_project_dir / ".trace"
        trace_dir.mkdir()

        with pytest.raises(ValueError, match="project.yaml not found"):
            storage_manager.register_project(temp_project_dir)

    def test_register_project_generates_id_if_missing(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test ID generation if missing from project.yaml."""
        trace_dir = temp_project_dir / ".trace"
        trace_dir.mkdir()

        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text(yaml.dump({"name": "Test"}))

        project_id = storage_manager.register_project(temp_project_dir)
        assert project_id is not None

        # Verify ID was written back
        config = yaml.safe_load(project_yaml.read_text())
        assert config["id"] == project_id


class TestProjectDetection:
    """Test project detection methods."""

    def test_is_trace_project_true(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test detection of .trace/ directory."""
        storage_manager.init_project(temp_project_dir)
        assert storage_manager.is_trace_project(temp_project_dir)

    def test_is_trace_project_false(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test non-trace directory."""
        assert not storage_manager.is_trace_project(temp_project_dir)

    def test_is_trace_project_with_file(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test with file path (should check parent)."""
        storage_manager.init_project(temp_project_dir)
        file_path = temp_project_dir / "test.txt"
        file_path.write_text("test")

        assert storage_manager.is_trace_project(file_path)

    def test_get_project_trace_dir_returns_path(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test getting .trace/ directory."""
        trace_dir, _ = storage_manager.init_project(temp_project_dir)

        result = storage_manager.get_project_trace_dir(temp_project_dir)
        # Use resolve to handle /var vs /private/var symlinks on macOS
        assert result.resolve() == trace_dir.resolve()

    def test_get_project_trace_dir_returns_none(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test None when .trace/ doesn't exist."""
        result = storage_manager.get_project_trace_dir(temp_project_dir)
        assert result is None

    def test_get_current_project_path(self, storage_manager: Any, temp_project_dir: Any, monkeypatch: Any) -> None:
        """Test finding current project from working directory."""
        storage_manager.init_project(temp_project_dir)

        # Change working directory
        monkeypatch.chdir(temp_project_dir)

        result = storage_manager.get_current_project_path()
        # Use resolve to handle /var vs /private/var symlinks on macOS
        assert result.resolve() == temp_project_dir.resolve()

    def test_get_current_project_path_from_subdirectory(
        self, storage_manager: Any, temp_project_dir: Any, monkeypatch: Any
    ) -> None:
        """Test finding project from subdirectory."""
        storage_manager.init_project(temp_project_dir)

        subdir = temp_project_dir / "src" / "components"
        subdir.mkdir(parents=True)

        monkeypatch.chdir(subdir)

        result = storage_manager.get_current_project_path()
        # Use resolve to handle /var vs /private/var symlinks on macOS
        assert result.resolve() == temp_project_dir.resolve()

    def test_get_current_project_path_not_found(
        self, storage_manager: Any, temp_project_dir: Any, monkeypatch: Any
    ) -> None:
        """Test None when not in a project."""
        monkeypatch.chdir(temp_project_dir)

        result = storage_manager.get_current_project_path()
        assert result is None


class TestCounterManagement:
    """Test project counter operations."""

    def test_get_project_counters(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test getting counters from project.yaml."""
        storage_manager.init_project(temp_project_dir)

        counters = storage_manager.get_project_counters(temp_project_dir)
        assert counters == {"epic": 0, "story": 0, "test": 0, "task": 0}

    def test_get_project_counters_missing_yaml(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test default counters when yaml missing."""
        trace_dir = temp_project_dir / ".trace"
        trace_dir.mkdir()

        counters = storage_manager.get_project_counters(temp_project_dir)
        assert counters == {"epic": 0, "story": 0, "test": 0, "task": 0}

    def test_increment_project_counter(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test counter increment."""
        storage_manager.init_project(temp_project_dir)

        value, external_id = storage_manager.increment_project_counter(temp_project_dir, "epic")
        assert value == 1
        assert external_id == "EPIC-001"

        # Verify persisted
        counters = storage_manager.get_project_counters(temp_project_dir)
        assert counters["epic"] == 1

    def test_increment_project_counter_multiple_times(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test multiple increments."""
        storage_manager.init_project(temp_project_dir)

        for i in range(1, 6):
            value, external_id = storage_manager.increment_project_counter(temp_project_dir, "story")
            assert value == i
            assert external_id == f"STORY-{i:03d}"

    def test_increment_different_counter_types(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test different counter types independently."""
        storage_manager.init_project(temp_project_dir)

        _, epic_id = storage_manager.increment_project_counter(temp_project_dir, "epic")
        _, story_id = storage_manager.increment_project_counter(temp_project_dir, "story")
        _, test_id = storage_manager.increment_project_counter(temp_project_dir, "test")
        _, task_id = storage_manager.increment_project_counter(temp_project_dir, "task")

        assert epic_id == "EPIC-001"
        assert story_id == "STORY-001"
        assert test_id == "TEST-001"
        assert task_id == "TASK-001"


class TestIndexingOperations:
    """Test project indexing operations."""

    def test_index_project_empty(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test indexing empty project."""
        storage_manager.init_project(temp_project_dir)

        counts = storage_manager.index_project(temp_project_dir)
        assert counts == {"epics": 0, "stories": 0, "tests": 0, "tasks": 0}

    def test_index_project_with_items(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test indexing project with markdown files."""
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        # Create sample epic file
        epic_file = trace_dir / "epics" / "EPIC-001.md"
        # Quote timestamps to prevent YAML from parsing them as datetime objects
        now = datetime.now().isoformat()
        epic_content = f"""---
id: {uuid.uuid4()}
external_id: EPIC-001
type: epic
status: todo
priority: high
version: 1
created: "{now}"
updated: "{now}"
---

# User Authentication

## Description

Implement user authentication system with OAuth2 support.
"""
        epic_file.write_text(epic_content)

        # Index the project
        counts = storage_manager.index_project(temp_project_dir)
        assert counts["epics"] == 1

    def test_index_project_updates_last_indexed(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test last_indexed timestamp update."""
        _trace_dir, project_id = storage_manager.init_project(temp_project_dir)

        storage_manager.index_project(temp_project_dir)

        session = storage_manager.get_session()
        try:
            result = session.execute(
                text("SELECT last_indexed FROM project_registry WHERE id = :id"),
                {"id": project_id},
            )
            row = result.fetchone()
            assert row is not None
            assert row.last_indexed is not None
        finally:
            session.close()


class TestFullTextSearch:
    """Test FTS operations."""

    def test_search_items_empty(self, storage_manager: Any) -> None:
        """Test search with no items."""
        results = storage_manager.search_items("test query")
        assert results == []

    def test_search_items_by_title(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test searching by title."""
        trace_dir, project_id = storage_manager.init_project(temp_project_dir)

        # Create and index item
        epic_file = trace_dir / "epics" / "EPIC-001.md"
        item_id = str(uuid.uuid4())
        epic_content = f"""---
id: {item_id}
external_id: EPIC-001
type: epic
status: todo
---

# Authentication System
"""
        epic_file.write_text(epic_content)
        storage_manager.index_project(temp_project_dir)

        # Search
        results = storage_manager.search_items("authentication", project_id=project_id)
        assert len(results) > 0
        assert any(item.id == item_id for item in results)

    def test_search_items_project_filter(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test project_id filter."""
        trace_dir, project_id = storage_manager.init_project(temp_project_dir)

        # Create item
        epic_file = trace_dir / "epics" / "EPIC-001.md"
        epic_content = f"""---
id: {uuid.uuid4()}
external_id: EPIC-001
type: epic
status: todo
---

# Test Epic
"""
        epic_file.write_text(epic_content)
        storage_manager.index_project(temp_project_dir)

        # Search with correct project_id
        results = storage_manager.search_items("test", project_id=project_id)
        assert len(results) > 0

        # Search with wrong project_id
        results = storage_manager.search_items("test", project_id="wrong-id")
        assert len(results) == 0


class TestSyncQueueOperations:
    """Test sync queue operations."""

    def test_queue_sync(self, storage_manager: Any) -> None:
        """Test queueing sync operation."""
        storage_manager.queue_sync("item", "item-123", "create", {"title": "Test Item"})

        queue = storage_manager.get_sync_queue()
        assert len(queue) == 1
        assert queue[0]["entity_type"] == "item"
        assert queue[0]["entity_id"] == "item-123"
        assert queue[0]["operation"] == "create"

    def test_get_sync_queue_limit(self, storage_manager: Any) -> None:
        """Test queue limit."""
        # Queue multiple items
        for i in range(10):
            storage_manager.queue_sync("item", f"item-{i}", "create", {"title": f"Item {i}"})

        queue = storage_manager.get_sync_queue(limit=5)
        assert len(queue) == COUNT_FIVE

    def test_clear_sync_queue_entry(self, storage_manager: Any) -> None:
        """Test removing queue entry."""
        storage_manager.queue_sync("item", "item-123", "create", {})

        queue = storage_manager.get_sync_queue()
        queue_id = queue[0]["id"]

        storage_manager.clear_sync_queue_entry(queue_id)

        queue = storage_manager.get_sync_queue()
        assert len(queue) == 0


class TestSyncStateOperations:
    """Test sync state operations."""

    def test_update_sync_state(self, storage_manager: Any) -> None:
        """Test updating sync state."""
        storage_manager.update_sync_state("last_sync_time", "2024-01-01T00:00:00Z")

        value = storage_manager.get_sync_state("last_sync_time")
        assert value == "2024-01-01T00:00:00Z"

    def test_get_sync_state_not_found(self, storage_manager: Any) -> None:
        """Test getting non-existent state."""
        value = storage_manager.get_sync_state("nonexistent")
        assert value is None

    def test_update_sync_state_overwrites(self, storage_manager: Any) -> None:
        """Test state overwrite."""
        storage_manager.update_sync_state("key", "value1")
        storage_manager.update_sync_state("key", "value2")

        value = storage_manager.get_sync_state("key")
        assert value == "value2"


class TestProjectStorageIntegration:
    """Test integration with ProjectStorage."""

    def test_get_project_storage(self, storage_manager: Any) -> None:
        """Test getting project storage (global projects dir)."""
        project_storage = storage_manager.get_project_storage("TestProject")
        assert isinstance(project_storage, ProjectStorage)
        assert project_storage.project_name == "TestProject"

    def test_get_project_storage_for_path(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test getting project storage for .trace/ path."""
        storage_manager.init_project(temp_project_dir, project_name="MyProject")

        project_storage = storage_manager.get_project_storage_for_path(temp_project_dir)
        assert project_storage is not None
        assert project_storage.project_name == "MyProject"

    def test_get_project_storage_for_path_not_found(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test None when .trace/ doesn't exist."""
        result = storage_manager.get_project_storage_for_path(temp_project_dir)
        assert result is None

    def test_get_project_storage_by_id(self, storage_manager: Any, temp_project_dir: Any) -> None:
        """Test getting storage by project ID."""
        trace_dir, project_id = storage_manager.init_project(temp_project_dir)
        storage_manager.index_project(temp_project_dir)

        project_storage = storage_manager.get_project_storage_by_id(project_id, trace_dir)
        assert project_storage is not None
