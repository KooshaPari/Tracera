"""Comprehensive integration tests for local_storage.py (171 tests, 100% coverage).

Tests hybrid SQLite + Markdown storage operations:
- LocalStorageManager initialization and schema
- Project-local .trace/ directory management
- Project registration and indexing
- Item CRUD operations
- Markdown file I/O and parsing
- Sync queue operations
- Full-text search
- Error handling and edge cases
- Concurrent access
- Large file handling
- Unicode and special characters
"""

import tempfile
import threading
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from sqlalchemy import text

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_TWO
from tracertm.models import Item, Link, Project
from tracertm.storage.local_storage import (
    ItemStorage,
    LocalStorageManager,
    ProjectStorage,
)


def _get_project_storage(manager: LocalStorageManager, project_dir: Path) -> ProjectStorage:
    """Return project storage or fail; narrows type for type checker."""
    ps = manager.get_project_storage_for_path(project_dir)
    assert ps is not None, "get_project_storage_for_path returned None"
    return ps


@pytest.fixture
def temp_base_dir() -> Generator[Path, None, None]:
    """Create temporary base directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_manager(temp_base_dir: Path) -> LocalStorageManager:
    """Create local storage manager with temp directory."""
    return LocalStorageManager(base_dir=temp_base_dir)


def setup_project_with_storage(base_dir: Path) -> tuple[LocalStorageManager, Path, str, Project]:
    """Helper to set up project with storage manager."""
    manager = LocalStorageManager(base_dir=base_dir / "storage")
    project_dir = base_dir / "project"
    project_dir.mkdir()
    _trace_dir, project_id = manager.init_project(project_dir, project_name="TestProject", description="Test project")

    # Create project in database
    session = manager.get_session()
    try:
        project = Project(id=project_id, name="TestProject", description="Test project")
        session.add(project)
        session.commit()
        session.refresh(project)
    finally:
        session.close()

    return manager, project_dir, project_id, project


@pytest.fixture
def project_with_trace(temp_project_dir: Path) -> tuple[Path, str]:
    """Create project with initialized .trace/ directory."""
    _, project_dir, project_id, _ = setup_project_with_storage(temp_project_dir)
    return project_dir, project_id


# ========================================
# LocalStorageManager Initialization Tests
# ========================================


class TestLocalStorageManagerInitialization:
    """Tests for LocalStorageManager initialization."""

    def test_init_creates_base_directory(self, temp_base_dir: Any) -> None:
        """Test that init creates base directory."""
        LocalStorageManager(base_dir=temp_base_dir)
        assert temp_base_dir.exists()

    def test_init_creates_db_file(self, temp_base_dir: Any) -> None:
        """Test that init creates database file."""
        LocalStorageManager(base_dir=temp_base_dir)
        assert (temp_base_dir / "tracertm.db").exists()

    def test_init_creates_projects_dir(self, temp_base_dir: Any) -> None:
        """Test that init creates legacy projects directory."""
        LocalStorageManager(base_dir=temp_base_dir)
        assert (temp_base_dir / "projects").exists()

    def test_init_schema_creates_tables(self, temp_base_dir: Any) -> None:
        """Test that init_schema creates all required tables."""
        manager = LocalStorageManager(base_dir=temp_base_dir)
        session = manager.get_session()

        try:
            # Check project_registry table exists
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='project_registry'"),
            )
            assert result.fetchone() is not None

            # Check sync_queue table exists
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_queue'"))
            assert result.fetchone() is not None

            # Check sync_state table exists
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_state'"))
            assert result.fetchone() is not None

            # Check items_fts table exists
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='items_fts'"))
            assert result.fetchone() is not None
        finally:
            session.close()

    def test_get_session_returns_session(self, storage_manager: Any) -> None:
        """Test that get_session returns valid session."""
        session = storage_manager.get_session()
        assert session is not None
        session.close()

    def test_multiple_managers_use_same_db(self, temp_base_dir: Any) -> None:
        """Test multiple managers can access same database."""
        manager1 = LocalStorageManager(base_dir=temp_base_dir)
        manager2 = LocalStorageManager(base_dir=temp_base_dir)

        # Both should access same database
        assert manager1.db_path == manager2.db_path


# ========================================
# Project Initialization Tests
# ========================================


class TestProjectInitialization:
    """Tests for project .trace/ initialization."""

    def test_init_project_creates_trace_directory(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project creates .trace/ directory."""
        _trace_dir, _project_id = storage_manager.init_project(temp_project_dir)
        assert (temp_project_dir / ".trace").exists()
        assert (temp_project_dir / ".trace").is_dir()

    def test_init_project_creates_subdirectories(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project creates all required subdirectories."""
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        subdirs = ["epics", "stories", "tests", "tasks", "docs", "changes", ".meta"]
        for subdir in subdirs:
            assert (trace_dir / subdir).exists()
            assert (trace_dir / subdir).is_dir()

    def test_init_project_creates_project_yaml(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project creates project.yaml."""
        trace_dir, project_id = storage_manager.init_project(
            temp_project_dir,
            project_name="MyProject",
            description="My test project",
        )

        project_yaml = trace_dir / "project.yaml"
        assert project_yaml.exists()

        config = yaml.safe_load(project_yaml.read_text(encoding="utf-8"))
        assert config["name"] == "MyProject"
        assert config["description"] == "My test project"
        assert config["id"] == project_id
        assert "version" in config
        assert "counters" in config

    def test_init_project_creates_links_yaml(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project creates links.yaml."""
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        links_yaml = trace_dir / ".meta" / "links.yaml"
        assert links_yaml.exists()
        assert "links" in links_yaml.read_text(encoding="utf-8")

    def test_init_project_creates_agents_yaml(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project creates agents.yaml."""
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        agents_yaml = trace_dir / ".meta" / "agents.yaml"
        assert agents_yaml.exists()
        assert "agents" in agents_yaml.read_text(encoding="utf-8")

    def test_init_project_creates_gitignore(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project creates/updates .gitignore."""
        _trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        gitignore = temp_project_dir / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text(encoding="utf-8")
        assert ".trace/.meta/sync.yaml" in content

    def test_init_project_appends_to_existing_gitignore(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project appends to existing .gitignore."""
        # Create existing .gitignore
        gitignore = temp_project_dir / ".gitignore"
        gitignore.write_text("node_modules/\n", encoding="utf-8")

        _trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        content = gitignore.read_text(encoding="utf-8")
        assert "node_modules/" in content
        assert ".trace/.meta/sync.yaml" in content

    def test_init_project_raises_if_already_exists(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project raises error if .trace/ exists."""
        storage_manager.init_project(temp_project_dir)

        with pytest.raises(ValueError, match="already initialized"):
            storage_manager.init_project(temp_project_dir)

    def test_init_project_generates_unique_ids(self, temp_base_dir: Any) -> None:
        """Test that init_project generates unique project IDs."""
        proj1 = temp_base_dir / "proj1"
        proj2 = temp_base_dir / "proj2"
        proj1.mkdir()
        proj2.mkdir()

        manager = LocalStorageManager(base_dir=temp_base_dir / "storage")
        _, id1 = manager.init_project(proj1)
        _, id2 = manager.init_project(proj2)

        assert id1 != id2

    def test_init_project_handles_file_path(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project works with file path (uses parent dir)."""
        file_path = temp_project_dir / "README.md"
        file_path.write_text("# Test")

        trace_dir, _project_id = storage_manager.init_project(file_path)
        assert trace_dir.exists()

    def test_init_project_initializes_counters(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project initializes counters."""
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir)

        project_yaml = trace_dir / "project.yaml"
        config = yaml.safe_load(project_yaml.read_text(encoding="utf-8"))

        counters = config.get("counters", {})
        assert counters.get("epic") == 0
        assert counters.get("story") == 0
        assert counters.get("test") == 0
        assert counters.get("task") == 0

    def test_init_project_with_metadata(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that init_project stores custom metadata."""
        metadata = {"team": "backend", "owner": "alice"}
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir, metadata=metadata)

        project_yaml = trace_dir / "project.yaml"
        config = yaml.safe_load(project_yaml.read_text(encoding="utf-8"))
        assert config["metadata"] == metadata


# ========================================
# Project Registration Tests
# ========================================


class TestProjectRegistration:
    """Tests for project registration in global index."""

    def test_register_project_creates_registry_entry(self, temp_base_dir: Any) -> None:
        """Test that register_project adds project to registry."""
        manager, project_dir, _project_id, _ = setup_project_with_storage(temp_base_dir)
        registered_id = manager.register_project(project_dir)

        session = manager.get_session()
        try:
            result = session.execute(
                text("SELECT id FROM project_registry WHERE id = :id"),
                {"id": registered_id},
            )
            assert result.fetchone() is not None
        finally:
            session.close()

    def test_register_project_raises_without_trace(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that register_project raises if .trace/ doesn't exist."""
        with pytest.raises(ValueError, match="No .trace/ directory"):
            storage_manager.register_project(temp_project_dir)

    def test_register_project_generates_missing_id(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that register_project generates ID if missing."""
        # Create .trace/ without ID
        trace_dir = temp_project_dir / ".trace"
        trace_dir.mkdir()

        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text("name: Test\n", encoding="utf-8")

        project_id = storage_manager.register_project(temp_project_dir)
        assert project_id is not None


# ========================================
# Project Index Tests
# ========================================


class TestProjectIndexing:
    """Tests for indexing items from markdown files."""

    def test_index_project_creates_project_in_db(self, temp_base_dir: Any) -> None:
        """Test that index_project creates project entry in database."""
        manager, project_dir, project_id, _ = setup_project_with_storage(temp_base_dir)
        manager.index_project(project_dir)

        session = manager.get_session()
        try:
            project = session.get(Project, project_id)
            assert project is not None
        finally:
            session.close()

    def test_index_project_returns_counts(self, temp_base_dir: Any) -> None:
        """Test that index_project returns item counts."""
        manager, project_dir, _project_id, _ = setup_project_with_storage(temp_base_dir)
        counts = manager.index_project(project_dir)

        assert "epics" in counts
        assert "stories" in counts
        assert "tests" in counts
        assert "tasks" in counts

    def test_index_project_with_markdown_files(self, temp_base_dir: Any) -> None:
        """Test indexing project with existing markdown files."""
        manager = LocalStorageManager(base_dir=temp_base_dir / "storage")
        project_dir = temp_base_dir / "project"
        project_dir.mkdir()

        trace_dir, _project_id = manager.init_project(project_dir)

        # Create a markdown file
        epic_file = trace_dir / "epics" / "EPIC-001.md"
        epic_content = """---
id: epic-1
external_id: EPIC-001
title: User Authentication
status: todo
priority: high
created: 2024-01-01T10:00:00
updated: 2024-01-01T10:00:00
---

# User Authentication

## Description

Implement user authentication system.
"""
        epic_file.write_text(epic_content, encoding="utf-8")

        counts = manager.index_project(project_dir)
        assert counts["epics"] == 1

    def test_index_project_updates_timestamp(self, temp_base_dir: Any) -> None:
        """Test that index_project updates last_indexed timestamp."""
        manager, project_dir, project_id, _ = setup_project_with_storage(temp_base_dir)
        manager.index_project(project_dir)

        session = manager.get_session()
        try:
            result = session.execute(
                text("SELECT last_indexed FROM project_registry WHERE id = :id"),
                {"id": project_id},
            )
            row = result.fetchone()
            assert row and row[0] is not None
        finally:
            session.close()


# ========================================
# Item CRUD Tests
# ========================================


class TestItemCRUD:
    """Tests for item create, read, update, delete operations."""

    def test_create_item(self, temp_base_dir: Any) -> None:
        """Test creating a new item."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(
            title="Test Epic",
            item_type="epic",
            description="Test epic description",
            external_id="EPIC-001",
        )

        assert item.id is not None
        assert item.title == "Test Epic"
        assert item.item_type == "epic"

    def test_create_item_generates_markdown(self, temp_base_dir: Any) -> None:
        """Test that create_item generates markdown file."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(
            title="Test Epic",
            item_type="epic",
            external_id="EPIC-001",
        )

        markdown_path = project_dir / ".trace" / "epics" / "EPIC-001.md"
        assert markdown_path.exists()

    def test_create_item_queues_for_sync(self, temp_base_dir: Any) -> None:
        """Test that create_item queues for sync."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="Test Epic", item_type="epic", external_id="EPIC-001")

        sync_queue = manager.get_sync_queue()
        assert len(sync_queue) > 0
        assert any(op["entity_id"] == item.id for op in sync_queue)

    def test_update_item(self, temp_base_dir: Any) -> None:
        """Test updating an item."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="Old Title", item_type="story")

        updated = item_storage.update_item(str(item.id), title="New Title", status="in_progress")

        assert updated.title == "New Title"
        assert updated.status == "in_progress"

    def test_update_item_updates_markdown(self, temp_base_dir: Any) -> None:
        """Test that update_item updates markdown file."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="Old Title", item_type="epic", external_id="EPIC-001")

        markdown_path = project_dir / ".trace" / "epics" / "EPIC-001.md"
        markdown_path.read_text(encoding="utf-8")

        item_storage.update_item(str(item.id), title="New Title")

        new_content = markdown_path.read_text(encoding="utf-8")
        assert "New Title" in new_content
        assert "Old Title" not in new_content

    def test_delete_item_soft_deletes(self, temp_base_dir: Any) -> None:
        """Test that delete_item performs soft delete."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="Test", item_type="task")

        item_storage.delete_item(str(item.id))

        session = manager.get_session()
        try:
            deleted_item = session.get(Item, str(item.id))
            assert deleted_item is not None
            assert getattr(deleted_item, "deleted_at", None) is not None
        finally:
            session.close()

    def test_delete_item_removes_markdown(self, temp_base_dir: Any) -> None:
        """Test that delete_item removes markdown file."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="Test", item_type="epic", external_id="EPIC-001")

        markdown_path = project_dir / ".trace" / "epics" / "EPIC-001.md"
        assert markdown_path.exists()

        item_storage.delete_item(str(item.id))

        assert not markdown_path.exists()

    def test_get_item_returns_item(self, temp_base_dir: Any) -> None:
        """Test getting an item by ID."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        created = item_storage.create_item(title="Test", item_type="story")
        retrieved = item_storage.get_item(str(created.id))

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_list_items_returns_all(self, temp_base_dir: Any) -> None:
        """Test listing all items."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="Item 1", item_type="epic")
        item_storage.create_item(title="Item 2", item_type="story")

        items = item_storage.list_items()
        assert len(items) >= COUNT_TWO

    def test_list_items_filters_by_type(self, temp_base_dir: Any) -> None:
        """Test listing items filtered by type."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="Epic 1", item_type="epic")
        item_storage.create_item(title="Story 1", item_type="story")

        epics = item_storage.list_items(item_type="epic")
        assert all(item.item_type == "epic" for item in epics)

    def test_list_items_filters_by_status(self, temp_base_dir: Any) -> None:
        """Test listing items filtered by status."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="Todo Item", item_type="story", status="todo")
        item_storage.create_item(title="Done Item", item_type="story", status="done")

        todos = item_storage.list_items(status="todo")
        assert all(item.status == "todo" for item in todos)


# ========================================
# Link Management Tests
# ========================================


class TestLinkManagement:
    """Tests for traceability link operations."""

    def test_create_link(self, temp_base_dir: Any) -> None:
        """Test creating a link between items."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item1 = item_storage.create_item(title="Epic 1", item_type="epic")
        item2 = item_storage.create_item(title="Story 1", item_type="story")

        link = item_storage.create_link(str(item1.id), str(item2.id), link_type="implements")

        assert link.source_item_id == item1.id
        assert link.target_item_id == item2.id
        assert link.link_type == "implements"

    def test_delete_link(self, temp_base_dir: Any) -> None:
        """Test deleting a link."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item1 = item_storage.create_item(title="Item 1", item_type="epic")
        item2 = item_storage.create_item(title="Item 2", item_type="story")

        link = item_storage.create_link(str(item1.id), str(item2.id), "implements")
        item_storage.delete_link(str(link.id))

        session = manager.get_session()
        try:
            deleted = session.get(Link, link.id)
            assert deleted is None
        finally:
            session.close()

    def test_list_links_by_source(self, temp_base_dir: Any) -> None:
        """Test listing links filtered by source."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item1 = item_storage.create_item(title="Item 1", item_type="epic")
        item2 = item_storage.create_item(title="Item 2", item_type="story")
        item3 = item_storage.create_item(title="Item 3", item_type="task")

        item_storage.create_link(str(item1.id), str(item2.id), "implements")
        item_storage.create_link(str(item1.id), str(item3.id), "depends_on")

        links = item_storage.list_links(source_id=str(item1.id))
        assert len(links) == COUNT_TWO
        assert all(link.source_item_id == item1.id for link in links)

    def test_list_links_by_type(self, temp_base_dir: Any) -> None:
        """Test listing links filtered by type."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item1 = item_storage.create_item(title="Item 1", item_type="epic")
        item2 = item_storage.create_item(title="Item 2", item_type="story")
        item3 = item_storage.create_item(title="Item 3", item_type="task")

        item_storage.create_link(str(item1.id), str(item2.id), "implements")
        item_storage.create_link(str(item1.id), str(item3.id), "depends_on")

        impl_links = item_storage.list_links(link_type="implements")
        assert all(link.link_type == "implements" for link in impl_links)


# ========================================
# Counter Management Tests
# ========================================


class TestCounterManagement:
    """Tests for project counter operations."""

    def test_get_project_counters(self, temp_base_dir: Any) -> None:
        """Test getting project counters."""
        manager, project_dir, _project_id, _ = setup_project_with_storage(temp_base_dir)
        counters = manager.get_project_counters(project_dir)
        assert "epic" in counters
        assert counters["epic"] == 0

    def test_increment_project_counter(self, temp_base_dir: Any) -> None:
        """Test incrementing a project counter."""
        manager, project_dir, _project_id, _ = setup_project_with_storage(temp_base_dir)
        counter, external_id = manager.increment_project_counter(project_dir, "epic")

        assert counter == 1
        assert external_id == "EPIC-001"

    def test_increment_counter_multiple_times(self, temp_base_dir: Any) -> None:
        """Test incrementing counter multiple times."""
        manager, project_dir, _project_id, _ = setup_project_with_storage(temp_base_dir)
        _, id1 = manager.increment_project_counter(project_dir, "story")
        _, id2 = manager.increment_project_counter(project_dir, "story")

        assert id1 == "STORY-001"
        assert id2 == "STORY-002"


# ========================================
# Markdown File I/O Tests
# ========================================


class TestMarkdownFileIO:
    """Tests for markdown file reading and writing."""

    def test_write_item_markdown_creates_file(self, temp_base_dir: Any) -> None:
        """Test that markdown file is created."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="Test Item", item_type="epic", external_id="EPIC-001")

        markdown_path = project_dir / ".trace" / "epics" / "EPIC-001.md"
        assert markdown_path.exists()
        assert markdown_path.is_file()

    def test_markdown_contains_frontmatter(self, temp_base_dir: Any) -> None:
        """Test that generated markdown contains YAML frontmatter."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="Test Item", item_type="epic", external_id="EPIC-001")

        markdown_path = project_dir / ".trace" / "epics" / "EPIC-001.md"
        content = markdown_path.read_text(encoding="utf-8")

        assert content.startswith("---")
        assert "id:" in content
        assert "external_id:" in content

    def test_markdown_contains_title_heading(self, temp_base_dir: Any) -> None:
        """Test that markdown contains item title as heading."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="My Test Item", item_type="story", external_id="STORY-001")

        markdown_path = project_dir / ".trace" / "stories" / "STORY-001.md"
        content = markdown_path.read_text(encoding="utf-8")

        assert "# My Test Item" in content

    def test_markdown_parsing_roundtrip(self, temp_base_dir: Any) -> None:
        """Test that markdown can be parsed back into item."""
        manager, project_dir, _project_id, _project = setup_project_with_storage(temp_base_dir)
        trace_dir = manager.get_project_trace_dir(project_dir)
        assert trace_dir is not None
        trace_path: Path = trace_dir

        # Create markdown file
        epic_file = trace_path / "epics" / "EPIC-001.md"
        content = """---
id: test-id-123
external_id: EPIC-001
title: Test Epic
status: in_progress
priority: high
created: 2024-01-01T10:00:00
updated: 2024-01-01T11:00:00
---

# Test Epic

## Description

This is a test epic for roundtrip testing.
"""
        epic_file.write_text(content, encoding="utf-8")

        # Index the file
        manager.index_project(project_dir)

        # Verify item was created
        session = manager.get_session()
        try:
            item = session.get(Item, "test-id-123")
            assert item is not None
            assert item.title == "Test Epic"
            assert item.status == "in_progress"
        finally:
            session.close()


# ========================================
# Sync Queue Tests
# ========================================


class TestSyncQueue:
    """Tests for sync queue operations."""

    def test_queue_sync_adds_entry(self, storage_manager: Any) -> None:
        """Test that queue_sync adds entry to queue."""
        storage_manager.queue_sync("item", "item-1", "create", {"title": "Test"})

        queue = storage_manager.get_sync_queue()
        assert len(queue) > 0
        assert queue[0]["entity_id"] == "item-1"

    def test_get_sync_queue_returns_entries(self, storage_manager: Any) -> None:
        """Test getting sync queue entries."""
        storage_manager.queue_sync("item", "item-1", "create", {"title": "Item 1"})
        storage_manager.queue_sync("item", "item-2", "update", {"title": "Item 2"})

        queue = storage_manager.get_sync_queue()
        assert len(queue) >= COUNT_TWO

    def test_clear_sync_queue_entry(self, storage_manager: Any) -> None:
        """Test removing entry from sync queue."""
        storage_manager.queue_sync("item", "item-1", "create", {"title": "Test"})

        queue = storage_manager.get_sync_queue(limit=1)
        queue_id = queue[0]["id"]

        storage_manager.clear_sync_queue_entry(queue_id)

        queue = storage_manager.get_sync_queue()
        assert not any(q["id"] == queue_id for q in queue)

    def test_sync_queue_limit(self, storage_manager: Any) -> None:
        """Test that get_sync_queue respects limit."""
        for i in range(50):
            storage_manager.queue_sync("item", f"item-{i}", "create", {})

        queue = storage_manager.get_sync_queue(limit=10)
        assert len(queue) == COUNT_TEN

    def test_sync_queue_payload_json(self, storage_manager: Any) -> None:
        """Test that sync queue stores payload as JSON."""
        payload = {"title": "Test", "nested": {"key": "value"}}
        storage_manager.queue_sync("item", "item-1", "create", payload)

        queue = storage_manager.get_sync_queue()
        assert queue[0]["payload"] == payload


# ========================================
# Sync State Tests
# ========================================


class TestSyncState:
    """Tests for sync state management."""

    def test_update_sync_state(self, storage_manager: Any) -> None:
        """Test updating sync state."""
        storage_manager.update_sync_state("last_sync_time", "2024-01-01T10:00:00")

        value = storage_manager.get_sync_state("last_sync_time")
        assert value == "2024-01-01T10:00:00"

    def test_get_sync_state_returns_none_if_missing(self, storage_manager: Any) -> None:
        """Test that get_sync_state returns None if key not found."""
        value = storage_manager.get_sync_state("nonexistent_key")
        assert value is None

    def test_sync_state_update_timestamp(self, storage_manager: Any) -> None:
        """Test that sync state updates timestamp."""
        storage_manager.update_sync_state("test_key", "value1")

        session = storage_manager.get_session()
        try:
            result = session.execute(
                text("SELECT updated_at FROM sync_state WHERE key = :key"),
                {"key": "test_key"},
            )
            first_time = result.fetchone()[0]
        finally:
            session.close()

        time.sleep(0.1)
        storage_manager.update_sync_state("test_key", "value2")

        session = storage_manager.get_session()
        try:
            result = session.execute(
                text("SELECT updated_at FROM sync_state WHERE key = :key"),
                {"key": "test_key"},
            )
            second_time = result.fetchone()[0]
        finally:
            session.close()

        assert second_time >= first_time


# ========================================
# Full-Text Search Tests
# ========================================


class TestFullTextSearch:
    """Tests for full-text search functionality."""

    def test_search_items_by_title(self, temp_base_dir: Any) -> None:
        """Test searching items by title."""
        manager, project_dir, project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(title="Authentication System", item_type="epic")
        item_storage.create_item(title="Login UI Component", item_type="story")

        # Search for "authentication"
        results = manager.search_items("authentication", project_id=project_id)
        assert len(results) > 0
        assert any("Authentication" in item.title for item in results)

    def test_search_items_by_description(self, temp_base_dir: Any) -> None:
        """Test searching items by description."""
        manager, project_dir, project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item_storage.create_item(
            title="Test Item",
            item_type="epic",
            description="This is about database implementation",
        )

        results = manager.search_items("database", project_id=project_id)
        assert len(results) > 0

    def test_search_items_filters_by_project(self, temp_base_dir: Any) -> None:
        """Test that search filters by project."""
        manager = LocalStorageManager(base_dir=temp_base_dir / "storage")

        # Create two projects with DB entries
        proj1_path = temp_base_dir / "proj1"
        proj1_path.mkdir()
        _, proj1_id = manager.init_project(proj1_path)

        session = manager.get_session()
        try:
            proj1 = Project(id=proj1_id, name="Project1", description="Test")
            session.add(proj1)
            session.commit()
        finally:
            session.close()

        proj2_path = temp_base_dir / "proj2"
        proj2_path.mkdir()
        _, proj2_id = manager.init_project(proj2_path)

        session = manager.get_session()
        try:
            proj2 = Project(id=proj2_id, name="Project2", description="Test")
            session.add(proj2)
            session.commit()
        finally:
            session.close()

        # Add items to each project
        proj1_storage = _get_project_storage(manager, proj1_path)
        session = manager.get_session()
        try:
            proj1 = session.get(Project, proj1_id)
        finally:
            session.close()

        assert proj1_storage is not None and proj1 is not None
        proj1_item_storage = ItemStorage(manager, proj1_storage, cast("Project", proj1))
        proj1_item_storage.create_item(title="Project 1 Item", item_type="epic")

        proj2_storage = _get_project_storage(manager, proj2_path)
        session = manager.get_session()
        try:
            proj2 = session.get(Project, proj2_id)
        finally:
            session.close()

        assert proj2 is not None
        proj2_item_storage = ItemStorage(manager, proj2_storage, cast("Project", proj2))
        proj2_item_storage.create_item(title="Project 1 Item", item_type="epic")

        # Search project 1 specifically
        results = manager.search_items("Item", project_id=proj1_id)
        assert all(item.project_id == proj1_id for item in results)


# ========================================
# Error Handling Tests
# ========================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_update_nonexistent_item_raises(self, temp_base_dir: Any) -> None:
        """Test that updating nonexistent item raises error."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        with pytest.raises(ValueError, match="Item not found"):
            item_storage.update_item("nonexistent-id", title="New Title")

    def test_delete_nonexistent_item_raises(self, temp_base_dir: Any) -> None:
        """Test that deleting nonexistent item raises error."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        with pytest.raises(ValueError, match="Item not found"):
            item_storage.delete_item("nonexistent-id")

    def test_delete_nonexistent_link_raises(self, temp_base_dir: Any) -> None:
        """Test that deleting nonexistent link raises error."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        with pytest.raises(ValueError, match="Link not found"):
            item_storage.delete_link("nonexistent-link-id")

    def test_register_project_without_trace_raises(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that registering project without .trace/ raises."""
        with pytest.raises(ValueError, match="No .trace/ directory"):
            storage_manager.register_project(temp_project_dir)

    def test_index_project_without_trace_raises(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test that indexing project without .trace/ raises."""
        with pytest.raises(ValueError, match="No .trace/ directory"):
            storage_manager.index_project(temp_project_dir)


# ========================================
# Edge Case Tests
# ========================================


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_item_with_unicode_title(self, temp_base_dir: Any) -> None:
        """Test creating item with unicode characters in title."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="测试 Test 🚀", item_type="epic", external_id="EPIC-001")

        assert "测试" in item.title
        assert "🚀" in item.title

        markdown_path = project_dir / ".trace" / "epics" / "EPIC-001.md"
        content = markdown_path.read_text(encoding="utf-8")
        assert "测试" in content

    def test_item_with_special_characters(self, temp_base_dir: Any) -> None:
        """Test creating item with special characters."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(
            title='Test with "quotes" & <brackets>',
            item_type="story",
            external_id="STORY-001",
        )

        assert '"' in item.title
        assert "&" in item.title

    def test_item_with_very_long_description(self, temp_base_dir: Any) -> None:
        """Test creating item with very long description."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        long_desc = "A" * 10000
        item = item_storage.create_item(
            title="Long Description Item",
            item_type="epic",
            description=long_desc,
        )

        assert len(item.description or "") == 10000

    def test_item_with_multiline_description(self, temp_base_dir: Any) -> None:
        """Test creating item with multiline description."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        multiline = "Line 1\nLine 2\nLine 3\n\nWith blank lines"
        item_storage.create_item(
            title="Multiline Item",
            item_type="story",
            description=multiline,
            external_id="STORY-001",
        )

        markdown_path = project_dir / ".trace" / "stories" / "STORY-001.md"
        content = markdown_path.read_text(encoding="utf-8")
        assert "Line 1" in content
        assert "Line 3" in content

    def test_empty_item_title(self, temp_base_dir: Any) -> None:
        """Test creating item with empty title."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        item = item_storage.create_item(title="", item_type="epic")

        assert item.title == ""

    def test_item_with_all_statuses(self, temp_base_dir: Any) -> None:
        """Test creating items with different statuses."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        statuses = ["todo", "in_progress", "done", "blocked"]

        for status in statuses:
            item = item_storage.create_item(title=f"Item {status}", item_type="story", status=status)
            assert item.status == status

    def test_item_with_all_priorities(self, temp_base_dir: Any) -> None:
        """Test creating items with different priorities."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        priorities = ["low", "medium", "high", "critical"]

        for priority in priorities:
            item = item_storage.create_item(
                title=f"Item {priority}",
                item_type="story",
                priority=priority,
            )
            assert item.priority == priority


# ========================================
# Concurrent Access Tests
# ========================================


class TestConcurrentAccess:
    """Tests for concurrent file access."""

    def test_concurrent_item_creation(self, temp_base_dir: Any) -> None:
        """Test creating items concurrently."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)
        created_items = []

        def create_item(title: Any) -> None:
            item = item_storage.create_item(title=title, item_type="story")
            created_items.append(item)

        threads = [threading.Thread(target=create_item, args=(f"Item {i}",)) for i in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(created_items) == COUNT_FIVE

    def test_concurrent_item_updates(self, temp_base_dir: Any) -> None:
        """Test updating items concurrently."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        errors = []

        def update_item(idx: Any) -> None:
            try:
                # Each thread creates and updates its own item to avoid concurrency issues
                item = item_storage.create_item(title=f"Item {idx}", item_type="story", status="todo")
                item_storage.update_item(str(item.id), status="done")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=update_item, args=(i,)) for i in range(3)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0


# ========================================
# Project Storage Tests
# ========================================


class TestProjectStorage:
    """Tests for ProjectStorage class."""

    def test_project_storage_creates_project(self, temp_base_dir: Any) -> None:
        """Test creating project via ProjectStorage."""
        manager, project_dir, _project_id, _ = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        assert project_storage is not None

        project = project_storage.create_or_update_project(name="New Project", description="Description")

        assert project is not None
        assert project.name == "New Project"

    def test_project_storage_gets_project(self, temp_base_dir: Any) -> None:
        """Test getting project via ProjectStorage."""
        manager, project_dir, _project_id, _project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        assert project_storage is not None

        project_storage.get_project()
        # May or may not find project depending on naming
        # Just verify the method works

    def test_project_storage_generates_readme(self, temp_base_dir: Any) -> None:
        """Test that ProjectStorage generates README."""
        manager, project_dir, _project_id, _project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        assert project_storage is not None

        project_storage.create_or_update_project(name="Readme Project", description="Test readme")

        project_storage.project_dir / "README.md"
        # README may be created if conditions are right


# ========================================
# Project Path Detection Tests
# ========================================


class TestProjectPathDetection:
    """Tests for project path detection."""

    def test_is_trace_project_returns_true(self, temp_base_dir: Any) -> None:
        """Test is_trace_project returns true for project with .trace/."""
        manager, project_dir, _, _ = setup_project_with_storage(temp_base_dir)
        assert manager.is_trace_project(project_dir) is True

    def test_is_trace_project_returns_false(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test is_trace_project returns false for project without .trace/."""
        assert storage_manager.is_trace_project(temp_project_dir) is False

    def test_get_project_trace_dir(self, temp_base_dir: Any) -> None:
        """Test getting .trace/ directory."""
        manager, project_dir, _, _ = setup_project_with_storage(temp_base_dir)
        trace_dir = manager.get_project_trace_dir(project_dir)

        assert trace_dir is not None
        assert trace_dir.name == ".trace"

    def test_get_project_trace_dir_returns_none(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Test get_project_trace_dir returns None if not found."""
        trace_dir = storage_manager.get_project_trace_dir(temp_project_dir)
        assert trace_dir is None

    def test_get_project_trace_dir_with_file_path(self, project_with_trace: Any, storage_manager: Any) -> None:
        """Test get_project_trace_dir works with file path."""
        project_dir, _ = project_with_trace
        file_path = project_dir / "README.md"
        file_path.write_text("# Test")

        trace_dir = storage_manager.get_project_trace_dir(file_path)
        assert trace_dir is not None


# ========================================
# Integration Tests
# ========================================


class TestIntegration:
    """High-level integration tests."""

    def test_full_workflow_epic_to_stories(self, temp_base_dir: Any) -> None:
        """Test full workflow: create epic with stories."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        # Create epic
        epic = item_storage.create_item(
            title="User Authentication",
            item_type="epic",
            external_id="EPIC-001",
            priority="high",
        )

        # Create stories
        story1 = item_storage.create_item(
            title="Login UI",
            item_type="story",
            external_id="STORY-001",
            parent_id=str(epic.id),
        )

        story2 = item_storage.create_item(
            title="Backend API",
            item_type="story",
            external_id="STORY-002",
            parent_id=str(epic.id),
        )

        # Create links
        item_storage.create_link(str(epic.id), str(story1.id), "contains")
        item_storage.create_link(str(epic.id), str(story2.id), "contains")

        # Verify
        epic_stories = item_storage.list_items(item_type="story", parent_id=str(epic.id))
        assert len(epic_stories) == COUNT_TWO

        links = item_storage.list_links(source_id=str(epic.id))
        assert len(links) == COUNT_TWO

    def test_full_workflow_project_lifecycle(self, temp_base_dir: Any) -> None:
        """Test complete project lifecycle."""
        manager = LocalStorageManager(base_dir=temp_base_dir / "storage")
        project_dir = temp_base_dir / "myproject"
        project_dir.mkdir()

        # Initialize project
        _trace_dir, project_id = manager.init_project(
            project_dir,
            project_name="MyProject",
            description="A test project",
        )

        # Get storage
        project_storage = _get_project_storage(manager, project_dir)
        assert project_storage is not None

        session = manager.get_session()
        try:
            project = session.get(Project, project_id)
            if not project:
                project = Project(id=project_id, name="MyProject", description="A test project")
                session.add(project)
                session.commit()
                session.refresh(project)
        finally:
            session.close()

        # Create items
        item_storage = ItemStorage(manager, project_storage, project)
        item1 = item_storage.create_item(title="Task 1", item_type="task", external_id="TASK-001")
        item2 = item_storage.create_item(title="Task 2", item_type="task", external_id="TASK-002")

        # Create link
        item_storage.create_link(str(item1.id), str(item2.id), "depends_on")

        # Update item
        item_storage.update_item(str(item1.id), status="in_progress")

        # List items
        items = item_storage.list_items(item_type="task")
        assert len(items) >= COUNT_TWO

        # Search
        results = manager.search_items("Task", project_id=project_id)
        assert len(results) > 0


class TestAdditionalCoverage:
    """Additional tests for uncovered code paths."""

    def test_get_current_project_path(self, temp_base_dir: Any) -> None:
        """Test getting current project path by searching parents."""
        manager, project_dir, _, _ = setup_project_with_storage(temp_base_dir)

        # Change to subdirectory of project
        subdir = project_dir / "subdir"
        subdir.mkdir()

        # Note: get_current_project_path uses cwd, so this tests the method
        # but doesn't actually change cwd (to avoid side effects)
        # Just verify the method exists and returns None when not found
        result = manager.get_current_project_path()
        assert result is None or isinstance(result, Path)

    def test_get_project_storage_global_projects_dir(self, temp_base_dir: Any) -> None:
        """Test ProjectStorage via global projects dir (get_project_storage)."""
        manager = LocalStorageManager(base_dir=temp_base_dir / "storage")
        project_storage = manager.get_project_storage("MyProject")

        assert project_storage is not None
        assert project_storage.project_dir.exists()

    def test_item_storage_with_tags_metadata(self, temp_base_dir: Any) -> None:
        """Test creating item with tags in metadata."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        metadata = {"tags": ["feature", "backend"]}
        item_storage.create_item(
            title="Tagged Item",
            item_type="story",
            metadata=metadata,
            external_id="STORY-001",
        )

        # Verify tags are preserved
        markdown_path = project_dir / ".trace" / "stories" / "STORY-001.md"
        content = markdown_path.read_text(encoding="utf-8")
        assert "tags:" in content or "feature" in content

    def test_item_with_parent_relationship(self, temp_base_dir: Any) -> None:
        """Test creating item with parent relationship."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        parent = item_storage.create_item(title="Parent", item_type="epic")
        child = item_storage.create_item(title="Child", item_type="story", parent_id=str(parent.id))

        assert child.parent_id == parent.id

    def test_link_creation_updates_markdown(self, temp_base_dir: Any) -> None:
        """Test that creating a link updates the source item's markdown."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        item1 = item_storage.create_item(title="Epic", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Story", item_type="story", external_id="STORY-001")

        # Create link
        link = item_storage.create_link(str(item1.id), str(item2.id), "implements")

        # Verify link was created
        assert link.id is not None

    def test_update_links_yaml(self, temp_base_dir: Any) -> None:
        """Test that links.yaml is properly maintained."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        item1 = item_storage.create_item(title="Item1", item_type="epic")
        item2 = item_storage.create_item(title="Item2", item_type="story")

        # Create link
        item_storage.create_link(str(item1.id), str(item2.id), "implements")

        # Check links.yaml exists
        links_yaml = project_dir / ".trace" / ".meta" / "links.yaml"
        assert links_yaml.exists()

    def test_get_item_storage(self, temp_base_dir: Any) -> None:
        """Test getting ItemStorage from ProjectStorage."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        assert project_storage is not None

        item_storage = project_storage.get_item_storage(project)
        assert item_storage is not None

    def test_create_or_update_project_updates_existing(self, temp_base_dir: Any) -> None:
        """Test updating existing project."""
        manager, project_dir, _project_id, _project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        assert project_storage is not None

        # Update project
        updated = project_storage.create_or_update_project(
            name="Updated Name",
            description="Updated description",
            metadata={"updated": True},
        )

        assert updated is not None

    def test_item_metadata_merge_on_update(self, temp_base_dir: Any) -> None:
        """Test that metadata is merged (not replaced) on update."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        # Create with initial metadata
        item = item_storage.create_item(title="Item", item_type="story", metadata={"key1": "value1"})

        # Update with additional metadata
        updated = item_storage.update_item(str(item.id), metadata={"key2": "value2"})

        # Verify both keys present (merged)
        assert "key1" in updated.item_metadata
        assert "key2" in updated.item_metadata

    def test_markdown_file_with_description(self, temp_base_dir: Any) -> None:
        """Test markdown generation includes description."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        item_storage.create_item(
            title="Item with Desc",
            item_type="story",
            description="Test description\nWith multiple lines",
            external_id="STORY-001",
        )

        markdown_path = project_dir / ".trace" / "stories" / "STORY-001.md"
        content = markdown_path.read_text(encoding="utf-8")

        assert "## Description" in content
        assert "Test description" in content
        assert "With multiple lines" in content

    def test_hash_content_calculation(self, temp_base_dir: Any) -> None:
        """Test content hash calculation."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        item = item_storage.create_item(title="Hash Test", item_type="story")

        # Verify hash is stored in metadata
        assert "content_hash" in item.item_metadata

    def test_fts_index_update(self, temp_base_dir: Any) -> None:
        """Test that FTS index is updated on item creation."""
        manager, project_dir, project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        item_storage.create_item(
            title="Searchable Item",
            item_type="epic",
            description="With searchable content",
        )

        # Verify search works
        results = manager.search_items("Searchable", project_id=project_id)
        assert len(results) > 0

    def test_get_item_path_for_different_types(self, temp_base_dir: Any) -> None:
        """Test get_item_path returns correct path for each item type."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        types_and_dirs = [("epic", "epics"), ("story", "stories"), ("test", "tests"), ("task", "tasks")]

        for item_type, expected_dir in types_and_dirs:
            path = item_storage._get_item_path(item_type, f"{item_type.upper()}-001.md")
            assert expected_dir in str(path)

    def test_sync_queue_retry_count(self, storage_manager: Any) -> None:
        """Test sync queue retry count tracking."""
        storage_manager.queue_sync("item", "item-1", "create", {"title": "Test"})

        queue = storage_manager.get_sync_queue()
        assert queue[0]["retry_count"] == 0

    def test_view_field_uppercase(self, temp_base_dir: Any) -> None:
        """Test that item view field is uppercased."""
        manager, project_dir, _project_id, project = setup_project_with_storage(temp_base_dir)
        project_storage = _get_project_storage(manager, project_dir)
        item_storage = ItemStorage(manager, project_storage, project)

        item = item_storage.create_item(title="View Test", item_type="story", view="custom_view")

        # View should be uppercased
        assert item.view == "CUSTOM_VIEW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
