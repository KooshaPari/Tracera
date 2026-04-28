"""Comprehensive test suite for TraceRTM Storage Module - Part 2.

This file continues comprehensive testing for:
- local_storage.py - LocalStorageManager, ProjectStorage, ItemStorage
- file_watcher.py - File system monitoring and auto-indexing

Coverage includes:
- Project initialization and registration
- Item CRUD operations
- Link management
- Full-text search
- Sync queue operations
- File watching and debouncing
- Error recovery scenarios
"""

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
import yaml
from sqlalchemy import text

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.models import Item, Project
from tracertm.storage.file_watcher import TraceFileWatcher, _TraceEventHandler
from tracertm.storage.local_storage import (
    LocalStorageManager,
)

# ============================================================================
# LocalStorageManager Tests
# ============================================================================


class TestLocalStorageManager:
    """Test local storage manager initialization and core functionality."""

    def test_initialization_default_dir(self) -> None:
        """Test initialization with default directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LocalStorageManager(base_dir=Path(tmpdir))

            assert manager.base_dir.exists()
            assert manager.db_path.exists()
            assert manager.projects_dir.exists()

    def test_initialization_creates_schema(self) -> None:
        """Test initialization creates database schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LocalStorageManager(base_dir=Path(tmpdir))

            # Check that tables exist
            with manager.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]

            assert "project_registry" in tables
            assert "sync_queue" in tables
            assert "sync_state" in tables
            assert "items_fts" in tables

    def test_get_session(self) -> None:
        """Test getting database session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LocalStorageManager(base_dir=Path(tmpdir))

            session = manager.get_session()

            assert session is not None
            session.close()

    def test_is_trace_project_true(self) -> None:
        """Test is_trace_project returns True for .trace/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            trace_dir = tmpdir / ".trace"
            trace_dir.mkdir()

            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            assert manager.is_trace_project(tmpdir) is True

    def test_is_trace_project_false(self) -> None:
        """Test is_trace_project returns False without .trace/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            assert manager.is_trace_project(tmpdir) is False

    def test_is_trace_project_with_file_path(self) -> None:
        """Test is_trace_project works with file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            trace_dir = tmpdir / ".trace"
            trace_dir.mkdir()
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")

            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            assert manager.is_trace_project(test_file) is True

    def test_get_project_trace_dir_exists(self) -> None:
        """Test getting .trace/ directory when it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            trace_dir = tmpdir / ".trace"
            trace_dir.mkdir()

            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            result = manager.get_project_trace_dir(tmpdir)

            assert result == trace_dir

    def test_get_project_trace_dir_not_exists(self) -> None:
        """Test getting .trace/ directory when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            result = manager.get_project_trace_dir(tmpdir)

            assert result is None

    def test_init_project_creates_structure(self) -> None:
        """Test init_project creates complete directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            trace_dir, _project_id = manager.init_project(
                tmpdir,
                project_name="Test Project",
                description="Test description",
            )

            assert trace_dir.exists()
            assert (trace_dir / "epics").exists()
            assert (trace_dir / "stories").exists()
            assert (trace_dir / "tests").exists()
            assert (trace_dir / "tasks").exists()
            assert (trace_dir / "docs").exists()
            assert (trace_dir / "changes").exists()
            assert (trace_dir / ".meta").exists()
            assert (trace_dir / "project.yaml").exists()
            assert (trace_dir / ".meta" / "links.yaml").exists()
            assert (trace_dir / ".meta" / "agents.yaml").exists()

    def test_init_project_creates_project_yaml(self) -> None:
        """Test init_project creates valid project.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            trace_dir, _project_id = manager.init_project(
                tmpdir,
                project_name="Test Project",
                description="Test description",
            )

            project_yaml_path = trace_dir / "project.yaml"
            config = yaml.safe_load(project_yaml_path.read_text())

            assert config["name"] == "Test Project"
            assert config["description"] == "Test description"
            assert "counters" in config
            assert config["counters"]["epic"] == 0

    def test_init_project_raises_if_exists(self) -> None:
        """Test init_project raises error if .trace/ already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            # Create first time
            manager.init_project(tmpdir)

            # Try to create again
            with pytest.raises(ValueError, match="already initialized"):
                manager.init_project(tmpdir)

    def test_init_project_adds_gitignore(self) -> None:
        """Test init_project adds .gitignore entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            manager.init_project(tmpdir)

            gitignore_path = tmpdir / ".gitignore"
            assert gitignore_path.exists()
            content = gitignore_path.read_text()
            assert ".trace/.meta/sync.yaml" in content

    def test_register_project_existing(self) -> None:
        """Test registering existing .trace/ project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            # Initialize project
            _trace_dir, original_id = manager.init_project(tmpdir)

            # Register it (simulating loading existing project)
            project_id = manager.register_project(tmpdir)

            assert project_id == original_id

    def test_register_project_no_trace_dir(self) -> None:
        """Test register_project raises error without .trace/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            with pytest.raises(ValueError, match="No .trace/"):
                manager.register_project(tmpdir)

    def test_register_project_generates_id_if_missing(self) -> None:
        """Test register_project generates ID if missing from project.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            trace_dir = tmpdir / ".trace"
            trace_dir.mkdir()

            # Create project.yaml without ID
            project_yaml = trace_dir / "project.yaml"
            project_yaml.write_text("name: Test Project\n")

            manager = LocalStorageManager(base_dir=tmpdir / "storage")
            project_id = manager.register_project(tmpdir)

            # Should have generated and saved ID
            assert project_id is not None
            config = yaml.safe_load(project_yaml.read_text())
            assert config["id"] == project_id

    def test_get_project_counters(self) -> None:
        """Test getting project counters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            _trace_dir, _project_id = manager.init_project(tmpdir)

            counters = manager.get_project_counters(tmpdir)

            assert counters["epic"] == 0
            assert counters["story"] == 0
            assert counters["test"] == 0
            assert counters["task"] == 0

    def test_increment_project_counter(self) -> None:
        """Test incrementing project counter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            manager.init_project(tmpdir)

            counter, external_id = manager.increment_project_counter(tmpdir, "epic")

            assert counter == 1
            assert external_id == "EPIC-001"

            # Increment again
            counter, external_id = manager.increment_project_counter(tmpdir, "epic")

            assert counter == COUNT_TWO
            assert external_id == "EPIC-002"

    def test_get_current_project_path_from_cwd(self) -> None:
        """Test getting current project path from working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            _trace_dir, _project_id = manager.init_project(tmpdir)

            # Change to project directory
            import os

            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)
                result = manager.get_current_project_path()
                assert result == tmpdir
            finally:
                os.chdir(original_cwd)

    def test_get_current_project_path_not_found(self) -> None:
        """Test get_current_project_path returns None when not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            import os

            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)
                result = manager.get_current_project_path()
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_search_items_fts(self) -> None:
        """Test full-text search for items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            # Create project and item
            session = manager.get_session()
            try:
                project = Project(name="Test Project")
                session.add(project)
                session.commit()
                session.refresh(project)

                item = Item(
                    project_id=project.id,
                    title="Authentication Feature",
                    description="Implement user authentication",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                )
                session.add(item)
                session.commit()
                session.refresh(item)

                # Add to FTS index
                session.execute(
                    text(
                        "INSERT INTO items_fts (item_id, title, description, item_type) VALUES (:item_id, :title, :description, :item_type)",
                    ),
                    {
                        "item_id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "item_type": item.item_type,
                    },
                )
                session.commit()

                # Search
                results = manager.search_items("authentication", project_id=str(project.id))

                assert len(results) > 0
                assert any("authentication" in r.title.lower() for r in results)
            finally:
                session.close()

    def test_queue_sync_operation(self) -> None:
        """Test queuing sync operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            manager.queue_sync("item", "item-123", "create", {"title": "Test Item"})

            # Verify queued
            queue = manager.get_sync_queue(limit=10)
            assert len(queue) == 1
            assert queue[0]["entity_id"] == "item-123"

    def test_get_sync_queue(self) -> None:
        """Test getting sync queue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            # Queue multiple items
            for i in range(5):
                manager.queue_sync("item", f"item-{i}", "create", {"index": i})

            queue = manager.get_sync_queue(limit=3)

            assert len(queue) == COUNT_THREE

    def test_clear_sync_queue_entry(self) -> None:
        """Test clearing specific queue entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            manager.queue_sync("item", "item-123", "create", {})
            queue = manager.get_sync_queue()
            queue_id = queue[0]["id"]

            manager.clear_sync_queue_entry(queue_id)

            queue = manager.get_sync_queue()
            assert len(queue) == 0

    def test_update_sync_state(self) -> None:
        """Test updating sync state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            manager.update_sync_state("last_sync_time", "2024-01-01T12:00:00")

            value = manager.get_sync_state("last_sync_time")

            assert value == "2024-01-01T12:00:00"

    def test_get_sync_state_nonexistent(self) -> None:
        """Test getting nonexistent sync state returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            value = manager.get_sync_state("nonexistent_key")

            assert value is None


class TestProjectStorage:
    """Test project storage operations."""

    @pytest.fixture
    def project_storage(self) -> None:
        """Create project storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")
            storage = manager.get_project_storage("test-project")
            yield storage

    def test_initialization(self, project_storage: Any) -> None:
        """Test project storage initializes correctly."""
        assert project_storage.project_name == "test-project"
        assert project_storage.project_dir.exists()
        assert project_storage.epics_dir.exists()
        assert project_storage.stories_dir.exists()

    def test_create_project(self, project_storage: Any) -> None:
        """Test creating a project."""
        project = project_storage.create_or_update_project(name="Test Project", description="Test description")

        assert project.name == "Test Project"
        assert project.description == "Test description"

    def test_update_project(self, project_storage: Any) -> None:
        """Test updating existing project."""
        # Create
        project1 = project_storage.create_or_update_project(name="Test Project", description="Original")

        # Update
        project2 = project_storage.create_or_update_project(name="Test Project", description="Updated")

        assert project1.id == project2.id
        assert project2.description == "Updated"

    def test_get_project(self, project_storage: Any) -> None:
        """Test getting project."""
        project_storage.create_or_update_project(name="Test Project")

        project = project_storage.get_project()

        assert project is not None
        assert project.name == "Test Project"

    def test_get_project_nonexistent(self, project_storage: Any) -> None:
        """Test getting nonexistent project returns None."""
        project = project_storage.get_project()

        assert project is None


class TestItemStorage:
    """Test item storage operations."""

    @pytest.fixture
    def item_storage(self) -> None:
        """Create item storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")
            project_storage = manager.get_project_storage("test-project")
            project = project_storage.create_or_update_project(name="Test Project")
            storage = project_storage.get_item_storage(project)
            yield storage

    def test_create_item(self, item_storage: Any) -> None:
        """Test creating an item."""
        item = item_storage.create_item(
            title="Test Item",
            item_type="epic",
            external_id="EPIC-001",
            description="Test description",
            status="todo",
            priority="high",
        )

        assert item.title == "Test Item"
        assert item.item_type == "epic"
        assert item.status == "todo"
        assert item.priority == "high"

    def test_create_item_generates_markdown(self, item_storage: Any) -> None:
        """Test creating item generates markdown file."""
        item_storage.create_item(
            title="Test Epic",
            item_type="epic",
            external_id="EPIC-001",
            description="Test description",
        )

        md_path = item_storage.project_storage.epics_dir / "EPIC-001.md"
        assert md_path.exists()
        content = md_path.read_text()
        assert "Test Epic" in content

    def test_update_item(self, item_storage: Any) -> None:
        """Test updating an item."""
        item = item_storage.create_item(title="Original Title", item_type="epic", external_id="EPIC-001")

        updated = item_storage.update_item(item_id=item.id, title="Updated Title", status="in_progress")

        assert updated.title == "Updated Title"
        assert updated.status == "in_progress"

    def test_update_item_nonexistent(self, item_storage: Any) -> None:
        """Test updating nonexistent item raises error."""
        with pytest.raises(ValueError, match="not found"):
            item_storage.update_item(item_id="nonexistent-id", title="New Title")

    def test_delete_item(self, item_storage: Any) -> None:
        """Test deleting an item (soft delete)."""
        item = item_storage.create_item(title="Test Item", item_type="epic", external_id="EPIC-001")

        item_storage.delete_item(item.id)

        # Check soft deleted
        deleted_item = item_storage.get_item(item.id)
        assert deleted_item.deleted_at is not None

    def test_delete_item_removes_markdown(self, item_storage: Any) -> None:
        """Test deleting item removes markdown file."""
        item = item_storage.create_item(title="Test Item", item_type="epic", external_id="EPIC-001")

        md_path = item_storage.project_storage.epics_dir / "EPIC-001.md"
        assert md_path.exists()

        item_storage.delete_item(item.id)

        assert not md_path.exists()

    def test_get_item(self, item_storage: Any) -> None:
        """Test getting item by ID."""
        item = item_storage.create_item(title="Test Item", item_type="epic", external_id="EPIC-001")

        retrieved = item_storage.get_item(item.id)

        assert retrieved is not None
        assert retrieved.id == item.id

    def test_get_item_nonexistent(self, item_storage: Any) -> None:
        """Test getting nonexistent item returns None."""
        result = item_storage.get_item("nonexistent-id")

        assert result is None

    def test_list_items(self, item_storage: Any) -> None:
        """Test listing items."""
        for i in range(3):
            item_storage.create_item(title=f"Item {i}", item_type="epic", external_id=f"EPIC-{i:03d}")

        items = item_storage.list_items()

        assert len(items) == COUNT_THREE

    def test_list_items_with_type_filter(self, item_storage: Any) -> None:
        """Test listing items with type filter."""
        item_storage.create_item(title="Epic", item_type="epic", external_id="EPIC-001")
        item_storage.create_item(title="Story", item_type="story", external_id="STORY-001")

        epics = item_storage.list_items(item_type="epic")

        assert len(epics) == 1
        assert epics[0].item_type == "epic"

    def test_list_items_with_status_filter(self, item_storage: Any) -> None:
        """Test listing items with status filter."""
        item_storage.create_item(title="Item 1", item_type="epic", external_id="EPIC-001", status="todo")
        item_storage.create_item(title="Item 2", item_type="epic", external_id="EPIC-002", status="done")

        todo_items = item_storage.list_items(status="todo")

        assert len(todo_items) == 1
        assert todo_items[0].status == "todo"

    def test_create_link(self, item_storage: Any) -> None:
        """Test creating a traceability link."""
        item1 = item_storage.create_item(title="Source", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Target", item_type="story", external_id="STORY-001")

        link = item_storage.create_link(source_id=item1.id, target_id=item2.id, link_type="implements")

        assert link.source_item_id == item1.id
        assert link.target_item_id == item2.id
        assert link.link_type == "implements"

    def test_delete_link(self, item_storage: Any) -> None:
        """Test deleting a link."""
        item1 = item_storage.create_item(title="Source", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Target", item_type="story", external_id="STORY-001")
        link = item_storage.create_link(item1.id, item2.id, "implements")

        item_storage.delete_link(link.id)

        # Verify deleted
        links = item_storage.list_links(source_id=item1.id)
        assert len(links) == 0

    def test_list_links(self, item_storage: Any) -> None:
        """Test listing links."""
        item1 = item_storage.create_item(title="Source", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Target 1", item_type="story", external_id="STORY-001")
        item3 = item_storage.create_item(title="Target 2", item_type="story", external_id="STORY-002")

        item_storage.create_link(item1.id, item2.id, "implements")
        item_storage.create_link(item1.id, item3.id, "implements")

        links = item_storage.list_links(source_id=item1.id)

        assert len(links) == COUNT_TWO

    def test_list_links_with_type_filter(self, item_storage: Any) -> None:
        """Test listing links with type filter."""
        item1 = item_storage.create_item(title="Source", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Target 1", item_type="story", external_id="STORY-001")
        item3 = item_storage.create_item(title="Target 2", item_type="test", external_id="TEST-001")

        item_storage.create_link(item1.id, item2.id, "implements")
        item_storage.create_link(item1.id, item3.id, "tested_by")

        implements_links = item_storage.list_links(link_type="implements")

        assert len(implements_links) == 1
        assert implements_links[0].link_type == "implements"


# ============================================================================
# FileWatcher Tests
# ============================================================================


class TestFileWatcher:
    """Test file watcher functionality."""

    @pytest.fixture
    def watcher_setup(self) -> None:
        """Setup file watcher environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create .trace/ structure
            trace_dir = tmpdir / ".trace"
            trace_dir.mkdir()
            (trace_dir / "epics").mkdir()
            (trace_dir / ".meta").mkdir()

            # Create project.yaml
            project_yaml = trace_dir / "project.yaml"
            project_yaml.write_text(yaml.dump({"id": "test-project-id", "name": "Test Project", "description": "Test"}))

            storage = LocalStorageManager(base_dir=tmpdir / "storage")

            yield tmpdir, storage

    def test_initialization(self, watcher_setup: Any) -> None:
        """Test file watcher initializes correctly."""
        project_path, storage = watcher_setup

        watcher = TraceFileWatcher(project_path=project_path, storage=storage, debounce_ms=500, auto_sync=False)

        assert watcher.project_path == project_path.resolve()
        assert watcher.trace_path == project_path / ".trace"
        assert watcher.debounce_delay == 0.5
        assert watcher.auto_sync is False

    def test_initialization_no_trace_dir(self) -> None:
        """Test initialization raises error without .trace/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            storage = LocalStorageManager(base_dir=tmpdir / "storage")

            with pytest.raises(ValueError, match="No .trace/"):
                TraceFileWatcher(tmpdir, storage)

    def test_start_creates_observer(self, watcher_setup: Any) -> None:
        """Test start creates and starts observer."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage)

        watcher.start()

        assert watcher._observer is not None
        assert watcher.is_running()

        watcher.stop()

    def test_stop_cleans_up(self, watcher_setup: Any) -> None:
        """Test stop cleans up observer."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage)

        watcher.start()
        watcher.stop()

        assert watcher._observer is None
        assert not watcher.is_running()

    def test_is_running(self, watcher_setup: Any) -> None:
        """Test is_running returns correct state."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage)

        assert watcher.is_running() is False

        watcher.start()
        assert watcher.is_running() is True

        watcher.stop()
        assert watcher.is_running() is False

    def test_get_stats(self, watcher_setup: Any) -> None:
        """Test getting watcher statistics."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage)

        stats = watcher.get_stats()

        assert "events_processed" in stats
        assert "events_pending" in stats
        assert "changes_by_type" in stats
        assert "is_running" in stats

    def test_debounce_event(self, watcher_setup: Any) -> None:
        """Test event debouncing."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage, debounce_ms=100)

        test_file = project_path / ".trace" / "epics" / "test.md"

        watcher._debounce_event(test_file, "modified")

        # Check pending count increased
        assert watcher._events_pending > 0

    def test_handle_item_change_create(self, watcher_setup: Any) -> None:
        """Test handling item creation."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage)

        # Create markdown file
        epic_file = project_path / ".trace" / "epics" / "EPIC-001.md"
        epic_file.write_text("""---
id: test-item-id
external_id: EPIC-001
type: epic
status: todo
---

# Test Epic
""")

        # Process event
        watcher._handle_item_change(epic_file, "created")

        # Verify item was created in database
        session = storage.get_session()
        try:
            from tracertm.models import Item

            item = session.get(Item, "test-item-id")
            assert item is not None
            assert item.title == "Test Epic"
        finally:
            session.close()

    def test_handle_item_change_delete(self, watcher_setup: Any) -> None:
        """Test handling item deletion."""
        project_path, storage = watcher_setup
        watcher = TraceFileWatcher(project_path, storage)

        # Create item first
        epic_file = project_path / ".trace" / "epics" / "EPIC-001.md"
        epic_file.write_text("""---
id: test-item-id
external_id: EPIC-001
type: epic
status: todo
---

# Test Epic
""")
        watcher._handle_item_change(epic_file, "created")

        # Delete file and handle
        epic_file.unlink()
        watcher._handle_item_change(epic_file, "deleted")

        # Verify item was soft deleted
        session = storage.get_session()
        try:
            from tracertm.models import Item

            item = session.get(Item, "test-item-id")
            assert item is not None
            assert item.deleted_at is not None
        finally:
            session.close()


class TestTraceEventHandler:
    """Test watchdog event handler."""

    @pytest.fixture
    def handler_setup(self) -> None:
        """Setup event handler environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create .trace/ structure
            trace_dir = tmpdir / ".trace"
            trace_dir.mkdir()
            (trace_dir / "epics").mkdir()

            # Create project.yaml
            project_yaml = trace_dir / "project.yaml"
            project_yaml.write_text(yaml.dump({"id": "test-project-id", "name": "Test Project"}))

            storage = LocalStorageManager(base_dir=tmpdir / "storage")
            watcher = TraceFileWatcher(tmpdir, storage)
            handler = _TraceEventHandler(watcher)

            yield handler, watcher, tmpdir

    def test_on_created_processes_md_file(self, handler_setup: Any) -> None:
        """Test on_created processes .md files."""
        handler, watcher, tmpdir = handler_setup

        test_file = tmpdir / ".trace" / "epics" / "test.md"
        test_file.write_text("# Test")

        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)

        handler.on_created(event)

        # Check event was debounced
        assert watcher._events_pending > 0

    def test_on_created_ignores_directory(self, handler_setup: Any) -> None:
        """Test on_created ignores directories."""
        handler, watcher, tmpdir = handler_setup

        event = Mock()
        event.is_directory = True
        event.src_path = str(tmpdir / ".trace" / "epics")

        initial_pending = watcher._events_pending
        handler.on_created(event)

        assert watcher._events_pending == initial_pending

    def test_on_modified_processes_yaml_file(self, handler_setup: Any) -> None:
        """Test on_modified processes .yaml files."""
        handler, watcher, tmpdir = handler_setup

        test_file = tmpdir / ".trace" / ".meta" / "links.yaml"
        test_file.write_text("links: []")

        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)

        handler.on_modified(event)

        assert watcher._events_pending > 0

    def test_should_process_md_files(self, handler_setup: Any) -> None:
        """Test _should_process returns True for .md files."""
        handler, _watcher, tmpdir = handler_setup

        test_file = tmpdir / ".trace" / "epics" / "test.md"

        assert handler._should_process(test_file) is True

    def test_should_process_yaml_files(self, handler_setup: Any) -> None:
        """Test _should_process returns True for .yaml files."""
        handler, _watcher, tmpdir = handler_setup

        test_file = tmpdir / ".trace" / ".meta" / "links.yaml"

        assert handler._should_process(test_file) is True

    def test_should_process_ignores_other_extensions(self, handler_setup: Any) -> None:
        """Test _should_process returns False for other extensions."""
        handler, _watcher, tmpdir = handler_setup

        test_file = tmpdir / ".trace" / "test.txt"

        assert handler._should_process(test_file) is False

    def test_should_process_ignores_sync_yaml(self, handler_setup: Any) -> None:
        """Test _should_process ignores sync.yaml."""
        handler, _watcher, tmpdir = handler_setup

        test_file = tmpdir / ".trace" / ".meta" / "sync.yaml"

        assert handler._should_process(test_file) is False


# ============================================================================
# Integration Tests
# ============================================================================


class TestStorageIntegration:
    """Integration tests for storage module components working together."""

    def test_full_workflow_create_project_and_items(self) -> None:
        """Test complete workflow: create project, add items, link them."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            # Initialize project
            trace_dir, _project_id = manager.init_project(tmpdir, project_name="Integration Test Project")

            # Register and get storage
            project_storage = manager.get_project_storage_for_path(tmpdir)
            assert project_storage is not None
            project = project_storage.get_project()
            assert project is not None
            item_storage = project_storage.get_item_storage(project)

            # Create items
            epic = item_storage.create_item(
                title="Test Epic",
                item_type="epic",
                external_id="EPIC-001",
                description="Epic description",
            )

            story = item_storage.create_item(
                title="Test Story",
                item_type="story",
                external_id="STORY-001",
                parent_id=str(epic.id),
            )

            # Create link
            link = item_storage.create_link(str(epic.id), str(story.id), "implements")

            # Verify everything exists
            assert epic.id is not None
            assert story.id is not None
            assert link.id is not None
            assert (trace_dir / "epics" / "EPIC-001.md").exists()
            assert (trace_dir / "stories" / "STORY-001.md").exists()

    def test_index_project_from_markdown_files(self) -> None:
        """Test indexing project from existing markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            manager = LocalStorageManager(base_dir=tmpdir / "storage")

            # Initialize project
            trace_dir, _project_id = manager.init_project(tmpdir)

            # Create markdown files manually
            epic_file = trace_dir / "epics" / "EPIC-001.md"
            epic_file.write_text("""---
id: epic-001-id
external_id: EPIC-001
type: epic
status: todo
priority: high
---

# Test Epic

## Description

This is a test epic.
""")

            # Index project
            counts = manager.index_project(tmpdir)

            assert counts["epics"] == 1

            # Verify indexed
            session = manager.get_session()
            try:
                from tracertm.models import Item

                item = session.get(Item, "epic-001-id")
                assert item is not None
                assert item.title == "Test Epic"
            finally:
                session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
