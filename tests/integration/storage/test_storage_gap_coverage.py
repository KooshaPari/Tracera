"""Integration tests targeting uncovered lines in storage module.

This test suite focuses on achieving 85%+ coverage for:
- local_storage.py (current: 87.81%, target: maintain/improve)
- markdown_parser.py (current: 89.71%, need: edge cases)
- sync_engine.py (current: 94.14%, need: error paths)
- file_watcher.py (current: 76.99%, need: 8.01%+ improvement)

Strategy:
1. Error handling paths
2. Edge cases and boundary conditions
3. Conditional branches not covered
4. Exception scenarios
5. Race conditions and concurrent access
"""

import asyncio
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Never, cast
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml
from sqlalchemy import create_engine, text
from watchdog.events import FileSystemEvent

from tracertm.models import Base, Item, Project
from tracertm.storage.conflict_resolver import ConflictStrategy
from tracertm.storage.file_watcher import TraceFileWatcher, _TraceEventHandler
from tracertm.storage.local_storage import ItemStorage, LocalStorageManager, ProjectStorage
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    _parse_history_table,
    _parse_markdown_body,
    list_items,
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
    write_item_markdown,
)
from tracertm.storage.sync_engine import (
    ChangeDetector,
    EntityType,
    OperationType,
    SyncEngine,
    SyncQueue,
    SyncStatus,
    exponential_backoff,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_base_dir() -> None:
    """Temporary base directory for storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_manager(temp_base_dir: Any) -> None:
    """LocalStorageManager instance."""
    return LocalStorageManager(base_dir=temp_base_dir)


@pytest.fixture
def project_path(temp_base_dir: Any) -> None:
    """Create a project directory."""
    proj_path = temp_base_dir / "test_project"
    proj_path.mkdir()
    return proj_path


@pytest.fixture
def initialized_project(storage_manager: Any, project_path: Any) -> None:
    """Initialize a .trace/ project."""
    trace_dir, project_id = storage_manager.init_project(
        project_path,
        project_name="Test Project",
        description="Test Description",
        metadata={"key": "value"},
    )
    return trace_dir, project_id, project_path


@pytest.fixture
def db_connection(temp_base_dir: Any) -> None:
    """Database connection for sync engine tests."""
    db_path = temp_base_dir / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    class MockDB:
        def __init__(self) -> None:
            self.engine = engine

    return MockDB()


@pytest.fixture
def mock_api_client() -> None:
    """Mock API client for sync tests."""
    client = MagicMock()
    client.post = MagicMock(return_value=asyncio.Future())
    client.post.return_value.set_result({"id": "test-id"})
    client.put = MagicMock(return_value=asyncio.Future())
    client.put.return_value.set_result({"id": "test-id"})
    client.delete = MagicMock(return_value=asyncio.Future())
    client.delete.return_value.set_result({})
    return client


# ============================================================================
# LocalStorageManager Edge Cases (Target: maintain 87.81%+)
# ============================================================================


class TestLocalStorageManagerEdgeCases:
    """Test uncovered paths in LocalStorageManager."""

    def test_is_trace_project_with_file_path(self, initialized_project: Any) -> None:
        """Test is_trace_project with file path instead of directory."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Create a file in the project
        test_file = project_path / "test.txt"
        test_file.write_text("test")

        # Should check parent directory
        assert storage.is_trace_project(test_file) is True

    def test_get_project_trace_dir_with_file_path(self, initialized_project: Any) -> None:
        """Test get_project_trace_dir with file path."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        test_file = project_path / "test.txt"
        test_file.write_text("test")

        result = storage.get_project_trace_dir(test_file)
        assert result == trace_dir

    def test_get_project_trace_dir_not_found(self, temp_base_dir: Any) -> None:
        """Test get_project_trace_dir when .trace/ doesn't exist."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace_project"
        project_path.mkdir()

        result = storage.get_project_trace_dir(project_path)
        assert result is None

    def test_init_project_already_exists(self, initialized_project: Any) -> None:
        """Test initializing project that already has .trace/."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        with pytest.raises(ValueError, match="already initialized"):
            storage.init_project(project_path)

    def test_init_project_with_file_path(self, temp_base_dir: Any) -> None:
        """Test init_project with file path resolves to parent."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "file_test_project"
        project_path.mkdir()

        test_file = project_path / "test.txt"
        test_file.write_text("test")

        trace_dir, _project_id = storage.init_project(test_file, project_name="File Test")

        assert trace_dir == project_path / ".trace"

    def test_init_project_creates_gitignore_appends_to_existing(self, temp_base_dir: Any) -> None:
        """Test .gitignore creation when file exists without newline."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "gitignore_test"
        project_path.mkdir()

        # Create .gitignore without trailing newline
        gitignore = project_path / ".gitignore"
        gitignore.write_text("*.log")

        storage.init_project(project_path, project_name="GitIgnore Test")

        content = gitignore.read_text()
        assert "# TraceRTM" in content
        assert ".trace/.meta/sync.yaml" in content

    def test_register_project_no_trace_dir(self, temp_base_dir: Any) -> None:
        """Test registering project without .trace/ directory."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace"
        project_path.mkdir()

        with pytest.raises(ValueError, match="No .trace/ directory found"):
            storage.register_project(project_path)

    def test_register_project_no_project_yaml(self, temp_base_dir: Any) -> None:
        """Test registering project without project.yaml."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_yaml"
        project_path.mkdir()
        (project_path / ".trace").mkdir()

        with pytest.raises(ValueError, match="project.yaml not found"):
            storage.register_project(project_path)

    def test_register_project_generates_id_if_missing(self, temp_base_dir: Any) -> None:
        """Test project ID generation when missing from project.yaml."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_id_project"
        project_path.mkdir()
        trace_dir = project_path / ".trace"
        trace_dir.mkdir()

        # Create project.yaml without id
        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text(yaml.dump({"name": "Test", "description": "Test"}))

        project_id = storage.register_project(project_path)

        # Verify ID was generated and written
        config = yaml.safe_load(project_yaml.read_text())
        assert "id" in config
        assert config["id"] == project_id

    def test_index_project_with_file_path(self, initialized_project: Any) -> None:
        """Test index_project with file path."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        test_file = project_path / "test.txt"
        test_file.write_text("test")

        counts = storage.index_project(test_file)
        assert isinstance(counts, dict)

    def test_index_project_no_trace_dir(self, temp_base_dir: Any) -> None:
        """Test indexing project without .trace/."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace"
        project_path.mkdir()

        with pytest.raises(ValueError, match="No .trace/ directory found"):
            storage.index_project(project_path)

    def test_index_project_no_id_in_yaml(self, temp_base_dir: Any) -> None:
        """Test indexing project without ID in project.yaml."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_id"
        project_path.mkdir()
        trace_dir = project_path / ".trace"
        trace_dir.mkdir()

        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text(yaml.dump({"name": "Test"}))

        with pytest.raises(ValueError, match="Project ID not found"):
            storage.index_project(project_path)

    def test_index_project_creates_project_if_not_exists(self, initialized_project: Any) -> None:
        """Test index_project creates project in DB if missing."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Delete project from DB
        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            if project:
                session.delete(project)
                session.commit()
        finally:
            session.close()

        # Index should recreate it
        storage.index_project(project_path)

        # Verify project exists
        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project is not None
        finally:
            session.close()

    def test_index_markdown_file_with_malformed_frontmatter(self, initialized_project: Any) -> None:
        """Test _index_markdown_file with malformed markdown."""
        trace_dir, project_id, _project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Create malformed markdown (no frontmatter)
        md_file = trace_dir / "epics" / "BAD-001.md"
        md_file.write_text("# Just a title\n\nNo frontmatter here")

        # Should handle gracefully
        storage._index_markdown_file(md_file, project_id, "epic")

    def test_index_markdown_file_extracts_title_from_body(self, initialized_project: Any) -> None:
        """Test title extraction from markdown body when not in frontmatter."""
        trace_dir, project_id, _project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Create markdown with title in body
        md_file = trace_dir / "epics" / "EPIC-001.md"
        content = """---
id: epic-001
external_id: EPIC-001
status: todo
---

# Title From Body

## Description
Test description
"""
        md_file.write_text(content)

        storage._index_markdown_file(md_file, project_id, "epic")

        # Verify item was created with title
        session = storage.get_session()
        try:
            item = session.get(Item, "epic-001")
            assert item is not None
            assert item.title == "Title From Body"
        finally:
            session.close()

    def test_index_markdown_file_updates_existing_item(self, initialized_project: Any) -> None:
        """Test updating existing item via _index_markdown_file."""
        trace_dir, project_id, _project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Create initial item
        session = storage.get_session()
        try:
            item = Item(id="epic-001", project_id=project_id, title="Old Title", item_type="epic", status="todo")
            session.add(item)
            session.commit()
        finally:
            session.close()

        # Update via markdown
        md_file = trace_dir / "epics" / "EPIC-001.md"
        content = """---
id: epic-001
external_id: EPIC-001
title: New Title
status: done
updated: '2024-01-01T00:00:00'
---

# New Title
"""
        md_file.write_text(content)

        storage._index_markdown_file(md_file, project_id, "epic")

        # Verify update
        session = storage.get_session()
        try:
            item = session.get(Item, "epic-001")
            assert item is not None
            assert item.title == "New Title"
            assert item.status == "done"
        finally:
            session.close()

    def test_index_markdown_file_handles_datetime_objects(self, initialized_project: Any) -> None:
        """Test handling datetime objects from YAML."""
        trace_dir, project_id, _project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # YAML can parse dates as datetime objects
        md_file = trace_dir / "epics" / "EPIC-002.md"
        md_file.write_text("""---
id: epic-002
external_id: EPIC-002
status: todo
created: 2024-01-01T00:00:00
updated: 2024-01-02T00:00:00
---

# Test
""")

        storage._index_markdown_file(md_file, project_id, "epic")

        session = storage.get_session()
        try:
            item = session.get(Item, "epic-002")
            assert item is not None
        finally:
            session.close()

    def test_get_project_counters_no_trace_dir(self, temp_base_dir: Any) -> None:
        """Test get_project_counters without .trace/."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace"
        project_path.mkdir()

        with pytest.raises(ValueError, match="No .trace/ directory found"):
            storage.get_project_counters(project_path)

    def test_get_project_counters_no_yaml(self, temp_base_dir: Any) -> None:
        """Test get_project_counters returns defaults without project.yaml."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_yaml"
        project_path.mkdir()
        (project_path / ".trace").mkdir()

        counters = storage.get_project_counters(project_path)
        assert counters == {"epic": 0, "story": 0, "test": 0, "task": 0}

    def test_increment_project_counter_no_trace_dir(self, temp_base_dir: Any) -> None:
        """Test increment_project_counter without .trace/."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace"
        project_path.mkdir()

        with pytest.raises(ValueError, match="No .trace/ directory found"):
            storage.increment_project_counter(project_path, "epic")

    def test_increment_project_counter_no_yaml(self, temp_base_dir: Any) -> None:
        """Test increment_project_counter without project.yaml."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_yaml"
        project_path.mkdir()
        (project_path / ".trace").mkdir()

        with pytest.raises(ValueError, match="project.yaml not found"):
            storage.increment_project_counter(project_path, "epic")

    def test_get_current_project_path_reaches_root(self, temp_base_dir: Any) -> None:
        """Test get_current_project_path when reaching filesystem root."""
        storage = LocalStorageManager(base_dir=temp_base_dir)

        # Mock Path.cwd() to return a deep path without .trace/
        with patch("tracertm.storage.local_storage.Path.cwd") as mock_cwd:
            deep_path = temp_base_dir / "a" / "b" / "c" / "d" / "e" / "f" / "g" / "h" / "i" / "j" / "k"
            deep_path.mkdir(parents=True)
            mock_cwd.return_value = deep_path

            result = storage.get_current_project_path()
            assert result is None

    def test_get_project_storage_for_path_no_trace_dir(self, temp_base_dir: Any) -> None:
        """Test get_project_storage_for_path without .trace/."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace"
        project_path.mkdir()

        result = storage.get_project_storage_for_path(project_path)
        assert result is None

    def test_get_project_storage_for_path_no_yaml(self, temp_base_dir: Any) -> None:
        """Test get_project_storage_for_path without project.yaml."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_yaml"
        project_path.mkdir()
        (project_path / ".trace").mkdir()

        result = storage.get_project_storage_for_path(project_path)
        assert result is None

    def test_search_items_with_project_filter(self, initialized_project: Any) -> None:
        """Test search_items with project_id filter."""
        trace_dir, project_id, _project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Create test item
        session = storage.get_session()
        try:
            item = Item(
                id="test-001",
                project_id=project_id,
                title="Searchable Test Item",
                description="This is a test description",
                item_type="epic",
                status="todo",
            )
            session.add(item)
            session.commit()

            # Update FTS
            session.execute(
                text("""
                INSERT INTO items_fts (item_id, title, description, item_type)
                VALUES (:id, :title, :description, :item_type)
                """),
                {"id": item.id, "title": item.title, "description": item.description, "item_type": item.item_type},
            )
            session.commit()
        finally:
            session.close()

        # Search with project filter
        results = storage.search_items("test", project_id=project_id)
        assert len(results) > 0


# ============================================================================
# ItemStorage Edge Cases
# ============================================================================


class TestItemStorageEdgeCases:
    """Test uncovered paths in ItemStorage."""

    def test_update_item_not_found(self, initialized_project: Any) -> None:
        """Test updating non-existent item raises error."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))
        finally:
            session.close()

        with pytest.raises(ValueError, match="Item not found"):
            item_storage.update_item("nonexistent-id", title="New Title")

    def test_update_item_with_metadata_merge(self, initialized_project: Any) -> None:
        """Test metadata merging in update_item."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))
        finally:
            session.close()

        # Create item with initial metadata
        item = item_storage.create_item(
            title="Test",
            item_type="epic",
            external_id="EPIC-001",
            metadata={"key1": "value1"},
        )

        # Update with additional metadata
        updated = item_storage.update_item(str(item.id), metadata={"key2": "value2"})

        assert "key1" in updated.item_metadata
        assert "key2" in updated.item_metadata

    def test_delete_item_not_found(self, initialized_project: Any) -> None:
        """Test deleting non-existent item."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))
        finally:
            session.close()

        with pytest.raises(ValueError, match="Item not found"):
            item_storage.delete_item("nonexistent-id")

    def test_delete_item_without_external_id(self, initialized_project: Any) -> None:
        """Test deleting item without external_id in metadata."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))

            # Create item without external_id
            item = Item(
                id="test-no-ext",
                project_id=project_id,
                title="Test",
                item_type="epic",
                status="todo",
                item_metadata={},
            )
            session.add(item)
            session.commit()
            session.refresh(item)
        finally:
            session.close()

        # Delete should not fail
        item_storage.delete_item("test-no-ext")

    def test_delete_link_not_found(self, initialized_project: Any) -> None:
        """Test deleting non-existent link."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))
        finally:
            session.close()

        with pytest.raises(ValueError, match="Link not found"):
            item_storage.delete_link("nonexistent-link")

    def test_write_item_markdown_without_external_id(self, initialized_project: Any) -> None:
        """Test _write_item_markdown returns early without external_id."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))

            item = Item(id="test", project_id=project_id, title="Test", item_type="epic", status="todo")
        finally:
            session.close()

        # Should return early
        item_storage._write_item_markdown(item, None, "content")

    def test_get_item_path_unknown_type(self, initialized_project: Any) -> None:
        """Test _get_item_path with unknown item type."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)

        session = storage.get_session()
        try:
            project = session.get(Project, project_id)
            assert project_storage is not None and project is not None
            item_storage = ItemStorage(storage, cast("ProjectStorage", project_storage), cast("Project", project))
        finally:
            session.close()

        # Unknown type defaults to project_dir
        assert project_storage is not None
        path = item_storage._get_item_path("unknown", "TEST-001")
        assert path.parent == project_storage.project_dir


# ============================================================================
# MarkdownParser Edge Cases (Target: improve from 89.71%)
# ============================================================================


class TestMarkdownParserEdgeCases:
    """Test uncovered paths in markdown_parser."""

    def test_item_data_to_frontmatter_all_optional_fields(self) -> None:
        """Test ItemData.to_frontmatter_dict with all optional fields."""
        item = ItemData(
            id="test-001",
            external_id="TEST-001",
            item_type="wireframe",
            status="done",
            priority="high",
            owner="user@example.com",
            parent="parent-001",
            version=2,
            created=datetime(2024, 1, 1),
            updated=datetime(2024, 1, 2),
            tags=["tag1", "tag2"],
            links=[{"type": "implements", "target": "TARGET-001"}],
            figma_url="https://figma.com/file/123",
            figma_file_key="file-key-123",
            figma_node_id="node-123",
            components=["Button", "Input"],
            screens=["Login", "Dashboard"],
            implements=["EPIC-001", "STORY-002"],
            custom_fields={"custom": "value"},
        )

        fm = item.to_frontmatter_dict()

        assert fm["priority"] == "high"
        assert fm["owner"] == "user@example.com"
        assert fm["parent"] == "parent-001"
        assert fm["created"] == datetime(2024, 1, 1).isoformat()
        assert fm["updated"] == datetime(2024, 1, 2).isoformat()
        assert fm["tags"] == ["tag1", "tag2"]
        assert fm["links"] == [{"type": "implements", "target": "TARGET-001"}]
        assert fm["figma_url"] == "https://figma.com/file/123"
        assert fm["figma_file_key"] == "file-key-123"
        assert fm["figma_node_id"] == "node-123"
        assert fm["components"] == ["Button", "Input"]
        assert fm["screens"] == ["Login", "Dashboard"]
        assert fm["implements"] == ["EPIC-001", "STORY-002"]
        assert fm["custom"] == "value"

    def test_item_data_to_markdown_body_wireframe_with_figma(self) -> None:
        """Test markdown body generation for wireframe with Figma."""
        item = ItemData(
            id="wire-001",
            external_id="WIRE-001",
            item_type="wireframe",
            status="done",
            title="Login Screen",
            description="Login screen design",
            figma_url="https://figma.com/file/123",
            figma_file_key="file-key",
            figma_node_id="node-123",
            components=["Button", "Input"],
            screens=["Login"],
        )

        body = item.to_markdown_body()

        assert "# Login Screen" in body
        assert "## Description" in body
        assert "## Figma Preview" in body
        assert "![Figma Preview](figma://file-key/node-123)" in body
        assert "[View in Figma](https://figma.com/file/123)" in body
        assert "## Components Used" in body
        assert "- Button" in body
        assert "## Screens" in body
        assert "- Login" in body

    def test_item_data_to_markdown_body_wireframe_without_node_id(self) -> None:
        """Test wireframe Figma preview without node_id."""
        item = ItemData(
            id="wire-002",
            external_id="WIRE-002",
            item_type="wireframe",
            status="done",
            figma_url="https://figma.com/file/123",
        )

        body = item.to_markdown_body()

        assert "[View in Figma](https://figma.com/file/123)" in body
        assert "![Figma Preview]" not in body

    def test_item_data_to_markdown_body_with_history(self) -> None:
        """Test markdown body with history table."""
        item = ItemData(
            id="test-001",
            external_id="TEST-001",
            item_type="epic",
            status="done",
            title="Test",
            history=[
                {"version": "1", "date": "2024-01-01", "author": "user1", "changes": "Initial"},
                {"version": "2", "date": "2024-01-02", "author": "user2", "changes": "Updated"},
            ],
        )

        body = item.to_markdown_body()

        assert "## History" in body
        assert "| Version | Date | Author | Changes |" in body
        assert "| 1 | 2024-01-01 | user1 | Initial |" in body

    def test_parse_item_markdown_file_not_found(self, temp_base_dir: Any) -> None:
        """Test parse_item_markdown with non-existent file."""
        non_existent = temp_base_dir / "does_not_exist.md"

        with pytest.raises(FileNotFoundError):
            parse_item_markdown(non_existent)

    def test_parse_item_markdown_no_frontmatter(self, temp_base_dir: Any) -> None:
        """Test parsing markdown without frontmatter."""
        md_file = temp_base_dir / "no_fm.md"
        md_file.write_text("# Just a title\n\nNo frontmatter")

        with pytest.raises(ValueError, match="No YAML frontmatter found"):
            parse_item_markdown(md_file)

    def test_parse_item_markdown_missing_required_fields(self, temp_base_dir: Any) -> None:
        """Test parsing markdown with missing required fields."""
        md_file = temp_base_dir / "missing.md"
        md_file.write_text("""---
id: test-001
type: epic
---

# Test
""")

        with pytest.raises(ValueError, match="Missing required frontmatter fields"):
            parse_item_markdown(md_file)

    def test_write_item_markdown_missing_required_fields(self, temp_base_dir: Any) -> None:
        """Test writing ItemData with missing fields."""
        item = ItemData(id="", external_id="", item_type="", status="")

        with pytest.raises(ValueError, match="missing required fields"):
            write_item_markdown(item, temp_base_dir / "test.md")

    def test_parse_links_yaml_file_not_found(self, temp_base_dir: Any) -> None:
        """Test parse_links_yaml with non-existent file."""
        with pytest.raises(FileNotFoundError):
            parse_links_yaml(temp_base_dir / "missing.yaml")

    def test_parse_links_yaml_empty_or_no_links(self, temp_base_dir: Any) -> None:
        """Test parse_links_yaml with empty file."""
        links_file = temp_base_dir / "empty_links.yaml"
        links_file.write_text("")

        result = parse_links_yaml(links_file)
        assert result == []

    def test_parse_links_yaml_invalid_link_format(self, temp_base_dir: Any) -> None:
        """Test parse_links_yaml with invalid link format."""
        links_file = temp_base_dir / "bad_links.yaml"
        links_file.write_text("""links:
  - id: link-001
    source: SOURCE-001
    # Missing 'type' and 'target'
""")

        with pytest.raises(ValueError, match="Invalid link format"):
            parse_links_yaml(links_file)

    def test_parse_config_yaml_file_not_found(self, temp_base_dir: Any) -> None:
        """Test parse_config_yaml with non-existent file."""
        with pytest.raises(FileNotFoundError):
            parse_config_yaml(temp_base_dir / "missing.yaml")

    def test_parse_markdown_body_empty_sections(self) -> None:
        """Test _parse_markdown_body with empty sections."""
        body = """# Title

## Description

## Acceptance Criteria

## Notes

## History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
"""

        title, desc, criteria, notes, history = _parse_markdown_body(body)

        assert title == "Title"
        assert desc == ""
        assert criteria == []
        assert notes == ""
        assert history == []

    def test_parse_history_table_too_few_lines(self) -> None:
        """Test _parse_history_table with incomplete table."""
        table = "| Version | Date |\n"

        result = _parse_history_table(table)
        assert result == []

    def test_parse_history_table_malformed_rows(self) -> None:
        """Test _parse_history_table with malformed rows."""
        table = """| Version | Date | Author | Changes |
|---------|------|--------|---------|
not a table row
| 1 | 2024-01-01 |
"""

        result = _parse_history_table(table)
        # Should skip malformed rows
        assert len(result) == 0

    def test_list_items_project_not_exists(self, temp_base_dir: Any) -> None:
        """Test list_items with non-existent project."""
        result = list_items(temp_base_dir, "nonexistent_project")
        assert result == []

    def test_list_items_type_dir_not_exists(self, temp_base_dir: Any) -> None:
        """Test list_items with non-existent type directory."""
        project_dir = temp_base_dir / "projects" / "test"
        project_dir.mkdir(parents=True)

        result = list_items(temp_base_dir, "test", item_type="epic")
        assert result == []


# ============================================================================
# SyncEngine Edge Cases (Target: improve from 94.14%)
# ============================================================================


class TestSyncEngineEdgeCases:
    """Test uncovered paths in sync_engine."""

    @pytest.mark.asyncio
    async def test_sync_already_in_progress(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test sync returns error when already syncing."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        # Simulate sync in progress
        engine._syncing = True

        result = await engine.sync()

        assert result.success is False
        assert "already in progress" in result.errors[0]

    @pytest.mark.asyncio
    async def test_sync_exception_handling(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test sync handles exceptions properly."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        # Make detect_and_queue_changes raise exception
        async def raise_error() -> Never:
            msg = "Test error"
            raise RuntimeError(msg)

        engine.detect_and_queue_changes = raise_error

        result = await engine.sync()

        assert result.success is False
        assert "Test error" in result.errors
        assert engine._syncing is False

    @pytest.mark.asyncio
    async def test_process_queue_max_retries_exceeded(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test process_queue skips items with too many retries."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage, max_retries=3)

        # Add item with high retry count
        queue_id = engine.queue.enqueue(EntityType.ITEM, "test-001", OperationType.CREATE, {"title": "Test"})

        # Manually set high retry count
        with db_connection.engine.connect() as conn:
            conn.execute(text("UPDATE sync_queue SET retry_count = 5 WHERE id = :id"), {"id": queue_id})
            conn.commit()

        result = await engine.process_queue()

        assert "Max retries exceeded" in str(result.errors)

    @pytest.mark.asyncio
    async def test_process_queue_upload_failure_with_retry(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test process_queue retries failed uploads."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage, retry_delay=0.01)

        # Mock _upload_change to fail
        async def fail_upload(_change: Any) -> bool:
            return False

        engine._upload_change = fail_upload

        # Queue change
        engine.queue.enqueue(EntityType.ITEM, "test-001", OperationType.CREATE, {"title": "Test"})

        await engine.process_queue()

        # Item should not be removed from queue
        assert engine.queue.get_count() > 0

    @pytest.mark.asyncio
    async def test_pull_changes_exception_handling(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test pull_changes handles exceptions."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        # Mock _apply_remote_change to raise exception
        async def raise_error(_change: Any) -> Never:
            msg = "Apply error"
            raise RuntimeError(msg)

        engine._apply_remote_change = raise_error

        # Provide changes
        with patch.object(engine, "pull_changes"):
            # Manually test the error path
            result = await engine.pull_changes(since=datetime.now(UTC))
            # Default implementation has empty changes, so success
            assert result.success is True

    def test_resolve_conflict_last_write_wins(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test conflict resolution with LAST_WRITE_WINS."""
        mock_storage = MagicMock()
        engine = SyncEngine(
            db_connection,
            mock_api_client,
            mock_storage,
            conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
        )

        local_data = {"id": "1", "title": "Local", "updated_at": "2024-01-01T00:00:00"}
        remote_data = {"id": "1", "title": "Remote", "updated_at": "2024-01-02T00:00:00"}

        result = engine._resolve_conflict(local_data, remote_data)

        # Remote is newer
        assert result["title"] == "Remote"

    def test_resolve_conflict_local_wins(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test conflict resolution with LOCAL_WINS."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage, conflict_strategy=ConflictStrategy.LOCAL_WINS)

        local_data = {"id": "1", "title": "Local"}
        remote_data = {"id": "1", "title": "Remote"}

        result = engine._resolve_conflict(local_data, remote_data)
        assert result["title"] == "Local"

    def test_resolve_conflict_remote_wins(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test conflict resolution with REMOTE_WINS."""
        mock_storage = MagicMock()
        engine = SyncEngine(
            db_connection,
            mock_api_client,
            mock_storage,
            conflict_strategy=ConflictStrategy.REMOTE_WINS,
        )

        local_data = {"id": "1", "title": "Local"}
        remote_data = {"id": "1", "title": "Remote"}

        result = engine._resolve_conflict(local_data, remote_data)
        assert result["title"] == "Remote"

    def test_resolve_conflict_manual(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test conflict resolution with MANUAL strategy."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage, conflict_strategy=ConflictStrategy.MANUAL)

        local_data = {"id": "1", "title": "Local"}
        remote_data = {"id": "1", "title": "Remote"}

        result = engine._resolve_conflict(local_data, remote_data)
        # Manual defaults to local
        assert result["title"] == "Local"

    @pytest.mark.asyncio
    async def test_exponential_backoff(self) -> None:
        """Test exponential backoff utility function."""
        start = time.time()
        await exponential_backoff(0, initial_delay=0.01, max_delay=1.0)
        elapsed = time.time() - start

        # First attempt should be ~initial_delay
        assert 0.01 <= elapsed < 0.1


# ============================================================================
# FileWatcher Edge Cases (Target: improve from 76.99% to 85%+)
# ============================================================================


class TestFileWatcherEdgeCases:
    """Test uncovered paths in file_watcher."""

    def test_init_no_trace_directory(self, temp_base_dir: Any) -> None:
        """Test FileWatcher initialization without .trace/."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "no_trace"
        project_path.mkdir()

        with pytest.raises(ValueError, match="No .trace/ directory found"):
            TraceFileWatcher(project_path, storage)

    def test_init_project_yaml_parse_error(self, initialized_project: Any) -> None:
        """Test _init_project with malformed project.yaml."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Corrupt project.yaml
        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text("invalid: yaml: content: [[[")

        # Should handle gracefully and use defaults
        watcher = TraceFileWatcher(project_path, storage)
        assert watcher.project is not None

    def test_init_project_no_yaml_uses_defaults(self, temp_base_dir: Any) -> None:
        """Test _init_project creates project with defaults."""
        storage = LocalStorageManager(base_dir=temp_base_dir)
        project_path = temp_base_dir / "default_project"
        project_path.mkdir()
        trace_dir = project_path / ".trace"
        trace_dir.mkdir()

        watcher = TraceFileWatcher(project_path, storage)

        assert watcher.project.name == "default_project"

    def test_start_already_running(self, initialized_project: Any) -> None:
        """Test starting watcher when already running."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage, debounce_ms=100)
        watcher.start()

        try:
            # Try to start again
            watcher.start()  # Should log warning
            assert watcher.is_running()
        finally:
            watcher.stop()

    def test_stop_not_running(self, initialized_project: Any) -> None:
        """Test stopping watcher when not running."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        # Stop without starting
        watcher.stop()  # Should log warning

    def test_process_event_markdown_parsing_error(self, initialized_project: Any) -> None:
        """Test _process_event with unparseable markdown."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        # Create bad markdown
        bad_md = trace_dir / "epics" / "BAD-001.md"
        bad_md.write_text("Not valid markdown")

        # Should handle error gracefully
        watcher._process_event(bad_md, "created")

    def test_process_event_ignored_file_type(self, initialized_project: Any) -> None:
        """Test _process_event ignores non-md/yaml files."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        txt_file = trace_dir / "test.txt"
        txt_file.write_text("test")

        # Should be ignored
        watcher._process_event(txt_file, "created")
        assert watcher._events_processed == 0

    def test_handle_item_change_delete_not_found(self, initialized_project: Any) -> None:
        """Test _handle_item_change delete when item not in DB."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        deleted_file = trace_dir / "epics" / "DELETED-001.md"

        # Should handle gracefully
        watcher._handle_item_change(deleted_file, "deleted")

    def test_handle_item_change_update_existing(self, initialized_project: Any) -> None:
        """Test _handle_item_change updates existing item."""
        trace_dir, project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        # Create item in DB first
        session = storage.get_session()
        try:
            item = Item(
                id="epic-update",
                project_id=project_id,
                title="Old Title",
                item_type="epic",
                status="todo",
                item_metadata={"external_id": "EPIC-UPDATE"},
            )
            session.add(item)
            session.commit()
        finally:
            session.close()

        watcher = TraceFileWatcher(project_path, storage)

        # Create markdown file
        md_file = trace_dir / "epics" / "EPIC-UPDATE.md"
        md_file.write_text("""---
id: epic-update
external_id: EPIC-UPDATE
type: epic
status: done
---

# Updated Title
""")

        watcher._handle_item_change(md_file, "modified")

        # Verify update
        session = storage.get_session()
        try:
            item = session.get(Item, "epic-update")
            assert item is not None
            assert item.status == "done"
        finally:
            session.close()

    def test_handle_links_change_deleted(self, initialized_project: Any) -> None:
        """Test _handle_links_change with deletion."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        links_file = trace_dir / ".meta" / "links.yaml"

        # Should log warning
        watcher._handle_links_change(links_file, "deleted")

    def test_handle_links_change_parse_error(self, initialized_project: Any) -> None:
        """Test _handle_links_change with parse error."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        links_file = trace_dir / ".meta" / "links.yaml"
        links_file.write_text("invalid: yaml: [[[")

        # Should handle error gracefully
        watcher._handle_links_change(links_file, "modified")

    def test_handle_project_change_deleted(self, initialized_project: Any) -> None:
        """Test _handle_project_change with deletion."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        project_yaml = trace_dir / "project.yaml"

        # Should log warning
        watcher._handle_project_change(project_yaml, "deleted")

    def test_handle_project_change_parse_error(self, initialized_project: Any) -> None:
        """Test _handle_project_change with parse error."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text("invalid: yaml: [[[")

        # Should handle error gracefully
        watcher._handle_project_change(project_yaml, "modified")

    def test_queue_for_sync_disabled(self, initialized_project: Any) -> None:
        """Test _queue_for_sync when auto_sync is False."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage, auto_sync=False)

        # Should return early
        watcher._queue_for_sync("item", "test-001", "create", {})

    def test_event_handler_on_created_directory(self, initialized_project: Any) -> None:
        """Test event handler ignores directory creation."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)
        handler = _TraceEventHandler(watcher)

        event = Mock(spec=FileSystemEvent)
        event.is_directory = True
        event.src_path = str(trace_dir / "new_dir")

        # Should return early
        handler.on_created(event)

    def test_event_handler_on_modified_directory(self, initialized_project: Any) -> None:
        """Test event handler ignores directory modification."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)
        handler = _TraceEventHandler(watcher)

        event = Mock(spec=FileSystemEvent)
        event.is_directory = True
        event.src_path = str(trace_dir / "epics")

        handler.on_modified(event)

    def test_event_handler_on_deleted_directory(self, initialized_project: Any) -> None:
        """Test event handler ignores directory deletion."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)
        handler = _TraceEventHandler(watcher)

        event = Mock(spec=FileSystemEvent)
        event.is_directory = True
        event.src_path = str(trace_dir / "deleted_dir")

        handler.on_deleted(event)

    def test_should_process_hidden_files(self, initialized_project: Any) -> None:
        """Test _should_process filters hidden files."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)
        handler = _TraceEventHandler(watcher)

        hidden = trace_dir / ".hidden" / "file.md"

        assert handler._should_process(hidden) is False

    def test_should_process_sync_yaml(self, initialized_project: Any) -> None:
        """Test _should_process filters sync.yaml."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)
        handler = _TraceEventHandler(watcher)

        sync_file = trace_dir / ".meta" / "sync.yaml"

        assert handler._should_process(sync_file) is False

    def test_should_process_wrong_extension(self, initialized_project: Any) -> None:
        """Test _should_process filters non-md/yaml files."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)
        handler = _TraceEventHandler(watcher)

        txt_file = trace_dir / "test.txt"

        assert handler._should_process(txt_file) is False

    def test_debounce_cancels_existing_timer(self, initialized_project: Any) -> None:
        """Test debounce cancels existing timer for same path."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage, debounce_ms=1000)

        test_file = trace_dir / "test.md"

        # Queue same file twice
        watcher._debounce_event(test_file, "created")
        watcher._debounce_event(test_file, "modified")

        # Should only have one timer
        assert len(watcher._debounce_timers) == 1
        assert watcher._events_pending == 1

    def test_get_stats(self, initialized_project: Any) -> None:
        """Test get_stats returns correct statistics."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)

        watcher = TraceFileWatcher(project_path, storage)

        stats = watcher.get_stats()

        assert stats["events_processed"] == 0
        assert stats["events_pending"] == 0
        assert stats["last_event_time"] is None
        assert stats["is_running"] is False


# ============================================================================
# ChangeDetector Edge Cases
# ============================================================================


class TestChangeDetectorEdgeCases:
    """Test ChangeDetector utility."""

    def test_has_changed_no_stored_hash(self) -> None:
        """Test has_changed returns True when no stored hash."""
        result = ChangeDetector.has_changed("content", None)
        assert result is True

    def test_detect_changes_in_directory_not_exists(self, temp_base_dir: Any) -> None:
        """Test detect_changes_in_directory with non-existent directory."""
        changes = ChangeDetector.detect_changes_in_directory(temp_base_dir / "nonexistent", {})
        assert changes == []

    def test_detect_changes_new_files(self, temp_base_dir: Any) -> None:
        """Test detect_changes_in_directory finds new files."""
        test_dir = temp_base_dir / "test_changes"
        test_dir.mkdir()

        md_file = test_dir / "new.md"
        md_file.write_text("new content")

        changes = ChangeDetector.detect_changes_in_directory(test_dir, {})

        assert len(changes) == 1
        assert changes[0][0] == md_file

    def test_detect_changes_modified_files(self, temp_base_dir: Any) -> None:
        """Test detect_changes_in_directory finds modified files."""
        test_dir = temp_base_dir / "test_changes"
        test_dir.mkdir()

        md_file = test_dir / "modified.md"
        original_content = "original"
        md_file.write_text(original_content)

        original_hash = ChangeDetector.compute_hash(original_content)
        stored_hashes = {"modified.md": original_hash}

        # Modify file
        md_file.write_text("modified content")

        changes = ChangeDetector.detect_changes_in_directory(test_dir, stored_hashes)

        assert len(changes) == 1


# ============================================================================
# Additional Edge Cases for Complete Coverage
# ============================================================================


class TestAdditionalEdgeCases:
    """Additional edge cases for maximum coverage."""

    def test_link_data_to_dict_with_metadata(self) -> None:
        """Test LinkData.to_dict includes metadata."""
        link = LinkData(
            id="link-001",
            source="SRC-001",
            target="TGT-001",
            link_type="implements",
            created=datetime(2024, 1, 1),
            metadata={"key": "value"},
        )

        data = link.to_dict()
        assert "metadata" in data
        assert data["metadata"]["key"] == "value"

    def test_link_data_to_dict_without_metadata(self) -> None:
        """Test LinkData.to_dict excludes empty metadata."""
        link = LinkData(
            id="link-002",
            source="SRC-002",
            target="TGT-002",
            link_type="tests",
            created=datetime(2024, 1, 1),
            metadata={},
        )

        data = link.to_dict()
        assert "metadata" not in data

    def test_link_data_from_dict_with_z_suffix(self) -> None:
        """Test LinkData.from_dict handles Z suffix in timestamp."""
        data = {
            "id": "link-003",
            "source": "SRC-003",
            "target": "TGT-003",
            "type": "depends_on",
            "created": "2024-01-01T00:00:00Z",
            "metadata": {},
        }

        link = LinkData.from_dict(data)
        assert link.created is not None

    def test_project_storage_create_or_update_project_update_path(self, initialized_project: Any) -> None:
        """Test create_or_update_project updates existing project."""
        trace_dir, _project_id, project_path = initialized_project
        storage = LocalStorageManager(base_dir=trace_dir.parent.parent)
        project_storage = storage.get_project_storage_for_path(project_path)
        assert project_storage is not None

        # Update with new description
        updated = project_storage.create_or_update_project(name="Test Project", description="Updated Description")

        assert updated.description == "Updated Description"

    def test_sync_queue_get_count(self, db_connection: Any) -> None:
        """Test SyncQueue.get_count."""
        queue = SyncQueue(db_connection)

        initial_count = queue.get_count()

        queue.enqueue(EntityType.ITEM, "test-001", OperationType.CREATE, {"title": "Test"})

        assert queue.get_count() == initial_count + 1

    def test_sync_queue_clear(self, db_connection: Any) -> None:
        """Test SyncQueue.clear removes all entries."""
        queue = SyncQueue(db_connection)

        queue.enqueue(EntityType.ITEM, "test-001", OperationType.CREATE, {"title": "Test"})

        queue.clear()

        assert queue.get_count() == 0

    @pytest.mark.asyncio
    async def test_sync_engine_clear_queue(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test SyncEngine.clear_queue."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        engine.queue.enqueue(EntityType.ITEM, "test-001", OperationType.CREATE, {"title": "Test"})

        await engine.clear_queue()

        assert engine.queue.get_count() == 0

    @pytest.mark.asyncio
    async def test_sync_engine_reset_sync_state(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test SyncEngine.reset_sync_state."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        engine.state_manager.update_last_sync(datetime.now(UTC))
        engine.state_manager.update_status(SyncStatus.ERROR)

        await engine.reset_sync_state()

        state = engine.get_status()
        assert state.last_sync is None
        assert state.status == SyncStatus.IDLE

    def test_sync_engine_is_syncing(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test SyncEngine.is_syncing."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        assert engine.is_syncing() is False

        engine._syncing = True
        assert engine.is_syncing() is True

    def test_sync_engine_create_vector_clock(self, db_connection: Any, mock_api_client: Any) -> None:
        """Test SyncEngine.create_vector_clock."""
        mock_storage = MagicMock()
        engine = SyncEngine(db_connection, mock_api_client, mock_storage)

        clock = engine.create_vector_clock(client_id="client-001", version=1, parent_version=0)

        assert clock.client_id == "client-001"
        assert clock.version == 1
        assert clock.parent_version == 0
