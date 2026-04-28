"""Comprehensive Integration Tests for Storage Module.

Tests the entire storage stack with real file system and databases:
- LocalStorageManager
- SyncEngine
- MarkdownParser
- ConflictResolver

Target: 80%+ coverage for:
- local_storage.py (566 lines, 7.63% → 80%+)
- sync_engine.py (279 lines, 28.53% → 80%+)
- markdown_parser.py (263 lines, 16.62% → 80%+)
- conflict_resolver.py (266 lines, 26.22% → 80%+)

Uses real file system (tempfile.TemporaryDirectory) and real SQLite databases.
"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO

# Import ALL models to ensure they're registered with Base.metadata
from tracertm.models import Base, Item, Link
from tracertm.storage.conflict_resolver import (
    Conflict,
    ConflictBackup,
    ConflictResolver,
    ConflictStatus,
    ConflictStrategy,
    EntityVersion,
    VectorClock,
    compare_versions,
    format_conflict_summary,
)
from tracertm.storage.local_storage import (
    LocalStorageManager,
)
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    get_config_path,
    get_item_path,
    get_links_path,
    list_items,
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
    write_config_yaml,
    write_item_markdown,
    write_links_yaml,
)
from tracertm.storage.sync_engine import (
    ChangeDetector,
    OperationType,
    SyncEngine,
    SyncQueue,
    SyncStateManager,
    SyncStatus,
    exponential_backoff,
)
from tracertm.storage.sync_engine import (
    EntityType as SyncEntityType,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_storage_dir() -> None:
    """Create temporary directory for storage tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_project_dir() -> None:
    """Create temporary directory for project tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_manager(temp_storage_dir: Any) -> None:
    """Create LocalStorageManager with temporary directory."""
    return LocalStorageManager(base_dir=temp_storage_dir)
    # Cleanup is handled by temp_storage_dir fixture


@pytest.fixture
def test_engine(temp_storage_dir: Any) -> None:
    """Create test SQLite engine."""
    db_path = temp_storage_dir / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine: Any) -> None:
    """Create test database session."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def conflict_resolver(test_session: Any, temp_storage_dir: Any) -> None:
    """Create ConflictResolver instance."""
    backup_dir = temp_storage_dir / "conflicts"
    return ConflictResolver(
        session=test_session,
        backup_dir=backup_dir,
        default_strategy=ConflictStrategy.LAST_WRITE_WINS,
    )


# ============================================================================
# LocalStorageManager Integration Tests
# ============================================================================


class TestLocalStorageManagerIntegration:
    """Integration tests for LocalStorageManager with real filesystem."""

    def test_init_creates_directory_structure(self, temp_storage_dir: Any) -> None:
        """Given: New storage directory.

        When: LocalStorageManager initialized
        Then: All required directories and database created.
        """
        manager = LocalStorageManager(base_dir=temp_storage_dir)

        # Verify directories exist
        assert temp_storage_dir.exists()
        assert (temp_storage_dir / "projects").exists()
        assert (temp_storage_dir / "tracertm.db").exists()

        # Verify database initialized
        session = manager.get_session()
        try:
            # Check tables exist
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = {row[0] for row in result}
            assert "projects" in tables
            assert "items" in tables
            assert "links" in tables
            assert "project_registry" in tables
            assert "sync_queue" in tables
        finally:
            session.close()

    def test_init_project_creates_trace_directory(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Empty project directory.

        When: init_project called
        Then: .trace/ directory created with all subdirectories.
        """
        trace_dir, project_id = storage_manager.init_project(
            temp_project_dir,
            project_name="TestProject",
            description="Test project",
        )

        # Verify .trace/ directory structure
        assert trace_dir.exists()
        assert trace_dir.name == ".trace"
        assert (trace_dir / "epics").exists()
        assert (trace_dir / "stories").exists()
        assert (trace_dir / "tests").exists()
        assert (trace_dir / "tasks").exists()
        assert (trace_dir / "docs").exists()
        assert (trace_dir / "changes").exists()
        assert (trace_dir / ".meta").exists()

        # Verify project.yaml exists and is valid
        project_yaml = trace_dir / "project.yaml"
        assert project_yaml.exists()

        config = yaml.safe_load(project_yaml.read_text())
        assert config["id"] == project_id
        assert config["name"] == "TestProject"
        assert config["description"] == "Test project"
        assert "counters" in config
        assert config["counters"]["epic"] == 0

    def test_init_project_creates_gitignore(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Project without .gitignore.

        When: init_project called
        Then: .gitignore created with .trace exclusions.
        """
        storage_manager.init_project(temp_project_dir, project_name="Test")

        gitignore = temp_project_dir / ".gitignore"
        assert gitignore.exists()

        content = gitignore.read_text()
        assert ".trace/.meta/sync.yaml" in content

    def test_init_project_appends_to_existing_gitignore(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Project with existing .gitignore.

        When: init_project called
        Then: .gitignore appended, not overwritten.
        """
        # Create existing .gitignore
        gitignore = temp_project_dir / ".gitignore"
        gitignore.write_text("node_modules/\n")

        storage_manager.init_project(temp_project_dir, project_name="Test")

        content = gitignore.read_text()
        assert "node_modules/" in content
        assert ".trace/.meta/sync.yaml" in content

    def test_init_project_raises_if_already_initialized(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Project already initialized.

        When: init_project called again
        Then: ValueError raised.
        """
        storage_manager.init_project(temp_project_dir, project_name="Test")

        with pytest.raises(ValueError, match="already initialized"):
            storage_manager.init_project(temp_project_dir, project_name="Test")

    def test_register_project_adds_to_database(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Initialized .trace/ directory.

        When: register_project called
        Then: Project registered in global database.
        """
        _trace_dir, project_id = storage_manager.init_project(temp_project_dir, project_name="RegisterTest")

        registered_id = storage_manager.register_project(temp_project_dir)
        assert registered_id == project_id

        # Verify in database
        session = storage_manager.get_session()
        try:
            result = session.execute(
                text("SELECT id, name, path FROM project_registry WHERE id = :id"),
                {"id": project_id},
            )
            row = result.fetchone()
            assert row is not None
            assert row[1] == "RegisterTest"
            assert str(temp_project_dir.resolve()) in row[2]
        finally:
            session.close()

    def test_register_project_generates_id_if_missing(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: project.yaml without id.

        When: register_project called
        Then: ID generated and written to project.yaml.
        """
        trace_dir = temp_project_dir / ".trace"
        trace_dir.mkdir(parents=True)

        # Create project.yaml without id
        project_yaml = trace_dir / "project.yaml"
        project_yaml.write_text(yaml.dump({"name": "NoID", "counters": {"epic": 0}}))

        project_id = storage_manager.register_project(temp_project_dir)
        assert project_id is not None

        # Verify ID added to file
        config = yaml.safe_load(project_yaml.read_text())
        assert config["id"] == project_id

    def test_register_project_raises_without_trace_dir(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Directory without .trace/.

        When: register_project called
        Then: ValueError raised.
        """
        with pytest.raises(ValueError, match="No .trace/ directory"):
            storage_manager.register_project(temp_project_dir)

    def test_is_trace_project_detects_trace_directory(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Directory with .trace/.

        When: is_trace_project called
        Then: Returns True.
        """
        storage_manager.init_project(temp_project_dir, project_name="Test")
        assert storage_manager.is_trace_project(temp_project_dir) is True

    def test_is_trace_project_returns_false_without_trace(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Directory without .trace/.

        When: is_trace_project called
        Then: Returns False.
        """
        assert storage_manager.is_trace_project(temp_project_dir) is False

    def test_get_project_trace_dir_returns_path(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Initialized project.

        When: get_project_trace_dir called
        Then: Returns .trace/ path.
        """
        trace_dir, _ = storage_manager.init_project(temp_project_dir, project_name="Test")
        result = storage_manager.get_project_trace_dir(temp_project_dir)
        # Resolve symlinks for comparison (macOS has /var -> /private/var)
        assert result.resolve() == trace_dir.resolve()

    def test_get_project_trace_dir_returns_none_without_trace(
        self, temp_project_dir: Any, storage_manager: Any
    ) -> None:
        """Given: Directory without .trace/.

        When: get_project_trace_dir called
        Then: Returns None.
        """
        result = storage_manager.get_project_trace_dir(temp_project_dir)
        assert result is None

    def test_increment_project_counter_updates_yaml(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Initialized project.

        When: increment_project_counter called
        Then: Counter incremented in project.yaml and ID returned.
        """
        storage_manager.init_project(temp_project_dir, project_name="Test")

        counter, external_id = storage_manager.increment_project_counter(temp_project_dir, "epic")

        assert counter == 1
        assert external_id == "EPIC-001"

        # Verify file updated
        trace_dir = temp_project_dir / ".trace"
        config = yaml.safe_load((trace_dir / "project.yaml").read_text())
        assert config["counters"]["epic"] == 1

    def test_increment_project_counter_sequential_increments(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Project with existing counter.

        When: increment_project_counter called multiple times
        Then: Counter increments sequentially.
        """
        storage_manager.init_project(temp_project_dir, project_name="Test")

        _, id1 = storage_manager.increment_project_counter(temp_project_dir, "story")
        _, id2 = storage_manager.increment_project_counter(temp_project_dir, "story")
        _, id3 = storage_manager.increment_project_counter(temp_project_dir, "story")

        assert id1 == "STORY-001"
        assert id2 == "STORY-002"
        assert id3 == "STORY-003"

    def test_get_project_counters_returns_all_counters(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Project with counters.

        When: get_project_counters called
        Then: All counter values returned.
        """
        storage_manager.init_project(temp_project_dir, project_name="Test")
        storage_manager.increment_project_counter(temp_project_dir, "epic")
        storage_manager.increment_project_counter(temp_project_dir, "story")
        storage_manager.increment_project_counter(temp_project_dir, "story")

        counters = storage_manager.get_project_counters(temp_project_dir)

        assert counters["epic"] == 1
        assert counters["story"] == COUNT_TWO
        assert counters["test"] == 0

    def test_index_project_parses_markdown_files(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: .trace/ with markdown items.

        When: index_project called
        Then: Items indexed into SQLite database.
        """
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir, project_name="IndexTest")

        # Create sample markdown file
        epics_dir = trace_dir / "epics"
        epic_file = epics_dir / "EPIC-001.md"
        epic_content = """---
id: epic-uuid-001
external_id: EPIC-001
type: epic
status: todo
priority: high
created: 2024-01-01T00:00:00
updated: 2024-01-02T00:00:00
---

# User Authentication

## Description

Implement user authentication system.
"""
        epic_file.write_text(epic_content)

        # Index project
        counts = storage_manager.index_project(temp_project_dir)

        assert counts["epics"] == 1

        # Verify item in database
        session = storage_manager.get_session()
        try:
            item = session.get(Item, "epic-uuid-001")
            assert item is not None
            assert item.title == "User Authentication"
            assert item.description == "Implement user authentication system."
            assert item.status == "todo"
            assert item.priority == "high"
        finally:
            session.close()

    def test_index_project_updates_fts_index(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Markdown items with searchable content.

        When: index_project called
        Then: FTS index populated for search.
        """
        trace_dir, project_id = storage_manager.init_project(temp_project_dir, project_name="SearchTest")

        # Create item with searchable content
        stories_dir = trace_dir / "stories"
        story_file = stories_dir / "STORY-001.md"
        story_content = """---
id: story-uuid-001
external_id: STORY-001
type: story
status: todo
---

# Login API Endpoint

## Description

RESTful API endpoint for user authentication.
"""
        story_file.write_text(story_content)

        storage_manager.index_project(temp_project_dir)

        # Test FTS search
        results = storage_manager.search_items("authentication", project_id=project_id)
        assert len(results) == 1
        assert results[0].title == "Login API Endpoint"

    def test_search_items_returns_matching_items(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: Multiple indexed items.

        When: search_items called with query
        Then: Matching items returned.
        """
        trace_dir, project_id = storage_manager.init_project(temp_project_dir, project_name="Test")

        # Create multiple items
        stories_dir = trace_dir / "stories"
        for i, title in enumerate(["Login Feature", "Profile API", "Authentication Service"], 1):
            story_file = stories_dir / f"STORY-{i:03d}.md"
            content = f"""---
id: story-{i}
external_id: STORY-{i:03d}
type: story
status: todo
---

# {title}

## Description

Test item {i}
"""
            story_file.write_text(content)

        storage_manager.index_project(temp_project_dir)

        # Search for "Authentication"
        results = storage_manager.search_items("Authentication", project_id=project_id)
        assert len(results) == 1
        assert results[0].title == "Authentication Service"

    def test_queue_sync_adds_to_sync_queue(self, storage_manager: Any) -> None:
        """Given: Storage manager initialized.

        When: queue_sync called
        Then: Change added to sync queue.
        """
        storage_manager.queue_sync(
            entity_type="item",
            entity_id="test-item-1",
            operation="create",
            payload={"title": "Test Item", "status": "todo"},
        )

        # Verify in queue
        queued = storage_manager.get_sync_queue(limit=10)
        assert len(queued) == 1
        assert queued[0]["entity_type"] == "item"
        assert queued[0]["entity_id"] == "test-item-1"
        assert queued[0]["operation"] == "create"

    def test_get_sync_queue_respects_limit(self, storage_manager: Any) -> None:
        """Given: Multiple queued items.

        When: get_sync_queue called with limit
        Then: Only limited items returned.
        """
        for i in range(10):
            storage_manager.queue_sync(
                entity_type="item",
                entity_id=f"item-{i}",
                operation="update",
                payload={},
            )

        queued = storage_manager.get_sync_queue(limit=5)
        assert len(queued) == COUNT_FIVE

    def test_clear_sync_queue_entry_removes_item(self, storage_manager: Any) -> None:
        """Given: Item in sync queue.

        When: clear_sync_queue_entry called
        Then: Item removed from queue.
        """
        storage_manager.queue_sync(entity_type="item", entity_id="test-1", operation="create", payload={})

        queued = storage_manager.get_sync_queue(limit=10)
        queue_id = queued[0]["id"]

        storage_manager.clear_sync_queue_entry(queue_id)

        # Verify removed
        queued = storage_manager.get_sync_queue(limit=10)
        assert len(queued) == 0

    def test_update_and_get_sync_state(self, storage_manager: Any) -> None:
        """Given: Storage manager.

        When: update_sync_state and get_sync_state called
        Then: State persisted and retrieved.
        """
        storage_manager.update_sync_state("last_sync_time", "2024-01-01T00:00:00Z")
        storage_manager.update_sync_state("sync_count", "42")

        last_sync = storage_manager.get_sync_state("last_sync_time")
        sync_count = storage_manager.get_sync_state("sync_count")

        assert last_sync == "2024-01-01T00:00:00Z"
        assert sync_count == "42"

    def test_get_sync_state_returns_none_for_missing_key(self, storage_manager: Any) -> None:
        """Given: No sync state.

        When: get_sync_state called with unknown key
        Then: None returned.
        """
        result = storage_manager.get_sync_state("nonexistent")
        assert result is None


# ============================================================================
# ProjectStorage Integration Tests
# ============================================================================


class TestProjectStorageIntegration:
    """Integration tests for ProjectStorage with real filesystem."""

    def test_create_project_in_global_projects_dir(self, storage_manager: Any) -> None:
        """Given: ProjectStorage (global projects dir).

        When: create_or_update_project called
        Then: Project created in database and filesystem.
        """
        project_storage = storage_manager.get_project_storage("GlobalProject")
        project = project_storage.create_or_update_project(name="GlobalProject", description="Test global projects dir")

        assert project.name == "GlobalProject"
        assert project.description == "Test global projects dir"

        # Verify README generated
        readme = project_storage.project_dir / "README.md"
        assert readme.exists()
        assert "GlobalProject" in readme.read_text()

    def test_create_project_in_project_local_mode(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Given: ProjectStorage in project-local mode.

        When: create_or_update_project called
        Then: Project uses .trace/ directory.
        """
        trace_dir, _project_id = storage_manager.init_project(temp_project_dir, project_name="LocalProject")

        project_storage = storage_manager.get_project_storage_for_path(temp_project_dir)
        assert project_storage is not None
        # Resolve symlinks for comparison (macOS has /var -> /private/var)
        assert project_storage.project_dir.resolve() == trace_dir.resolve()

    def test_update_existing_project(self, storage_manager: Any) -> None:
        """Given: Existing project.

        When: create_or_update_project called again
        Then: Project updated, not duplicated.
        """
        project_storage = storage_manager.get_project_storage("UpdateTest")
        project1 = project_storage.create_or_update_project(name="UpdateTest", description="Original")

        project2 = project_storage.create_or_update_project(name="UpdateTest", description="Updated")

        assert project1.id == project2.id
        assert project2.description == "Updated"

    def test_get_project_returns_project(self, storage_manager: Any) -> None:
        """Given: Created project.

        When: get_project called
        Then: Project returned.
        """
        project_storage = storage_manager.get_project_storage("GetTest")
        created = project_storage.create_or_update_project(name="GetTest", description="Test")

        retrieved = project_storage.get_project()
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_project_returns_none_for_nonexistent(self, storage_manager: Any) -> None:
        """Given: No project created.

        When: get_project called
        Then: None returned.
        """
        project_storage = storage_manager.get_project_storage("NonExistent")
        result = project_storage.get_project()
        assert result is None


# ============================================================================
# ItemStorage Integration Tests
# ============================================================================


class TestItemStorageIntegration:
    """Integration tests for ItemStorage with real filesystem and database."""

    @pytest.fixture
    def item_storage(self, temp_project_dir: Any, storage_manager: Any) -> None:
        """Create ItemStorage for testing."""
        _trace_dir, _project_id = storage_manager.init_project(temp_project_dir, project_name="ItemTest")
        project_storage = storage_manager.get_project_storage_for_path(temp_project_dir)
        project = project_storage.create_or_update_project(name="ItemTest", description="Test")
        return project_storage.get_item_storage(project)

    def test_create_item_writes_to_database_and_filesystem(self, item_storage: Any, temp_project_dir: Any) -> None:
        """Given: ItemStorage initialized.

        When: create_item called
        Then: Item saved to both SQLite and markdown file.
        """
        item = item_storage.create_item(
            title="Test Epic",
            item_type="epic",
            external_id="EPIC-001",
            description="Test epic description",
            status="todo",
            priority="high",
        )

        # Verify in database
        retrieved = item_storage.get_item(item.id)
        assert retrieved is not None
        assert retrieved.title == "Test Epic"

        # Verify markdown file exists
        trace_dir = temp_project_dir / ".trace"
        epic_file = trace_dir / "epics" / "EPIC-001.md"
        assert epic_file.exists()

        # Verify file content
        content = epic_file.read_text()
        assert "Test Epic" in content
        assert "Test epic description" in content

    def test_create_item_updates_fts_index(self, item_storage: Any) -> None:
        """Given: ItemStorage.

        When: create_item called
        Then: Item searchable via FTS.
        """
        item_storage.create_item(
            title="Searchable Item",
            item_type="story",
            external_id="STORY-001",
            description="Unique search term xyzabc",
        )

        # Search should find it
        session = item_storage.manager.get_session()
        try:
            result = session.execute(
                text("SELECT item_id FROM items_fts WHERE items_fts MATCH :query"),
                {"query": "xyzabc"},
            )
            rows = result.fetchall()
            assert len(rows) > 0
        finally:
            session.close()

    def test_update_item_modifies_database_and_filesystem(self, item_storage: Any, temp_project_dir: Any) -> None:
        """Given: Existing item.

        When: update_item called
        Then: Both database and markdown file updated.
        """
        item = item_storage.create_item(
            title="Original Title",
            item_type="epic",
            external_id="EPIC-001",
        )

        updated = item_storage.update_item(item_id=item.id, title="Updated Title", description="New description")

        assert updated.title == "Updated Title"
        assert updated.description == "New description"

        # Verify markdown file updated
        trace_dir = temp_project_dir / ".trace"
        epic_file = trace_dir / "epics" / "EPIC-001.md"
        content = epic_file.read_text()
        assert "Updated Title" in content
        assert "New description" in content

    def test_update_item_increments_version(self, item_storage: Any) -> None:
        """Given: Item with version 1.

        When: update_item called
        Then: Version incremented automatically.
        """
        item = item_storage.create_item(title="Version Test", item_type="story", external_id="STORY-001")

        original_version = item.version

        item_storage.update_item(item_id=item.id, title="Updated")

        updated = item_storage.get_item(item.id)
        # Version is auto-incremented on update (optimistic locking)
        assert updated.version > original_version

    def test_delete_item_soft_deletes_in_database(self, item_storage: Any) -> None:
        """Given: Existing item.

        When: delete_item called
        Then: Item soft-deleted (deleted_at set).
        """
        item = item_storage.create_item(title="Delete Test", item_type="task", external_id="TASK-001")

        item_storage.delete_item(item.id)

        # Verify soft delete
        session = item_storage.manager.get_session()
        try:
            deleted_item = session.get(Item, item.id)
            assert deleted_item.deleted_at is not None
        finally:
            session.close()

    def test_delete_item_removes_markdown_file(self, item_storage: Any, temp_project_dir: Any) -> None:
        """Given: Item with markdown file.

        When: delete_item called
        Then: Markdown file deleted.
        """
        item_storage.create_item(title="Delete File Test", item_type="test", external_id="TEST-001")

        trace_dir = temp_project_dir / ".trace"
        test_file = trace_dir / "tests" / "TEST-001.md"
        assert test_file.exists()

        item = item_storage.list_items(item_type="test")[0]
        item_storage.delete_item(item.id)

        assert not test_file.exists()

    def test_list_items_filters_by_type(self, item_storage: Any) -> None:
        """Given: Items of different types.

        When: list_items called with type filter
        Then: Only matching items returned.
        """
        item_storage.create_item(title="Epic 1", item_type="epic", external_id="EPIC-001")
        item_storage.create_item(title="Story 1", item_type="story", external_id="STORY-001")
        item_storage.create_item(title="Epic 2", item_type="epic", external_id="EPIC-002")

        epics = item_storage.list_items(item_type="epic")
        stories = item_storage.list_items(item_type="story")

        assert len(epics) == COUNT_TWO
        assert len(stories) == 1

    def test_list_items_filters_by_status(self, item_storage: Any) -> None:
        """Given: Items with different statuses.

        When: list_items called with status filter
        Then: Only matching items returned.
        """
        item_storage.create_item(title="Todo 1", item_type="story", external_id="STORY-001", status="todo")
        item_storage.create_item(title="In Progress", item_type="story", external_id="STORY-002", status="in_progress")
        item_storage.create_item(title="Todo 2", item_type="story", external_id="STORY-003", status="todo")

        todo_items = item_storage.list_items(status="todo")
        in_progress_items = item_storage.list_items(status="in_progress")

        assert len(todo_items) == COUNT_TWO
        assert len(in_progress_items) == 1

    def test_list_items_excludes_deleted(self, item_storage: Any) -> None:
        """Given: Mix of active and deleted items.

        When: list_items called
        Then: Deleted items excluded.
        """
        item1 = item_storage.create_item(title="Active", item_type="story", external_id="STORY-001")
        item2 = item_storage.create_item(title="Deleted", item_type="story", external_id="STORY-002")

        item_storage.delete_item(item2.id)

        items = item_storage.list_items(item_type="story")
        assert len(items) == 1
        assert items[0].id == item1.id

    def test_create_link_creates_in_database_and_yaml(self, item_storage: Any, temp_project_dir: Any) -> None:
        """Given: Two items.

        When: create_link called
        Then: Link created in database and links.yaml.
        """
        item1 = item_storage.create_item(title="Epic", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Story", item_type="story", external_id="STORY-001")

        link = item_storage.create_link(
            source_id=item1.id,
            target_id=item2.id,
            link_type="implements",
            metadata={"note": "test"},
        )

        # Verify in database
        session = item_storage.manager.get_session()
        try:
            retrieved = session.get(Link, link.id)
            assert retrieved is not None
            assert retrieved.link_type == "implements"
        finally:
            session.close()

        # Verify in links.yaml
        trace_dir = temp_project_dir / ".trace"
        links_file = trace_dir / ".meta" / "links.yaml"
        assert links_file.exists()

        links_data = yaml.safe_load(links_file.read_text())
        assert len(links_data["links"]) == 1
        assert links_data["links"][0]["type"] == "implements"

    def test_delete_link_removes_from_database_and_yaml(self, item_storage: Any, temp_project_dir: Any) -> None:
        """Given: Existing link.

        When: delete_link called
        Then: Link removed from database and links.yaml.
        """
        item1 = item_storage.create_item(title="Item 1", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Item 2", item_type="story", external_id="STORY-001")

        link = item_storage.create_link(source_id=item1.id, target_id=item2.id, link_type="depends_on")

        item_storage.delete_link(link.id)

        # Verify removed from database
        session = item_storage.manager.get_session()
        try:
            retrieved = session.get(Link, link.id)
            assert retrieved is None
        finally:
            session.close()

        # Verify removed from links.yaml
        trace_dir = temp_project_dir / ".trace"
        links_file = trace_dir / ".meta" / "links.yaml"
        links_data = yaml.safe_load(links_file.read_text())
        assert len(links_data["links"]) == 0

    def test_list_links_filters_by_source(self, item_storage: Any) -> None:
        """Given: Multiple links.

        When: list_links called with source_id
        Then: Only links from that source returned.
        """
        item1 = item_storage.create_item(title="Source", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Target 1", item_type="story", external_id="STORY-001")
        item3 = item_storage.create_item(title="Target 2", item_type="story", external_id="STORY-002")

        item_storage.create_link(item1.id, item2.id, "implements")
        item_storage.create_link(item1.id, item3.id, "implements")
        item_storage.create_link(item2.id, item3.id, "depends_on")

        links = item_storage.list_links(source_id=item1.id)
        assert len(links) == COUNT_TWO

    def test_list_links_filters_by_target(self, item_storage: Any) -> None:
        """Given: Multiple links.

        When: list_links called with target_id
        Then: Only links to that target returned.
        """
        item1 = item_storage.create_item(title="Source 1", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Source 2", item_type="epic", external_id="EPIC-002")
        item3 = item_storage.create_item(title="Target", item_type="story", external_id="STORY-001")

        item_storage.create_link(item1.id, item3.id, "implements")
        item_storage.create_link(item2.id, item3.id, "implements")

        links = item_storage.list_links(target_id=item3.id)
        assert len(links) == COUNT_TWO

    def test_list_links_filters_by_type(self, item_storage: Any) -> None:
        """Given: Links of different types.

        When: list_links called with link_type
        Then: Only matching links returned.
        """
        item1 = item_storage.create_item(title="Item 1", item_type="epic", external_id="EPIC-001")
        item2 = item_storage.create_item(title="Item 2", item_type="story", external_id="STORY-001")
        item3 = item_storage.create_item(title="Item 3", item_type="test", external_id="TEST-001")

        item_storage.create_link(item1.id, item2.id, "implements")
        item_storage.create_link(item2.id, item3.id, "tests")

        implements_links = item_storage.list_links(link_type="implements")
        test_links = item_storage.list_links(link_type="tests")

        assert len(implements_links) == 1
        assert len(test_links) == 1


# ============================================================================
# MarkdownParser Integration Tests
# ============================================================================


class TestMarkdownParserIntegration:
    """Integration tests for markdown parsing with real files."""

    def test_write_and_parse_item_roundtrip(self, temp_storage_dir: Any) -> None:
        """Given: ItemData object.

        When: write_item_markdown then parse_item_markdown
        Then: Data preserved perfectly.
        """
        original = ItemData(
            id="item-123",
            external_id="EPIC-001",
            item_type="epic",
            status="in_progress",
            priority="high",
            owner="alice",
            title="Authentication System",
            description="Implement secure user authentication",
            tags=["security", "auth"],
            acceptance_criteria=["- [ ] Login works", "- [ ] Logout works"],
            notes="Important security considerations",
        )

        # Write to file
        file_path = temp_storage_dir / "EPIC-001.md"
        write_item_markdown(original, file_path)

        # Parse back
        parsed = parse_item_markdown(file_path)

        # Verify all fields preserved
        assert parsed.id == original.id
        assert parsed.external_id == original.external_id
        assert parsed.title == original.title
        assert parsed.description == original.description
        assert parsed.status == original.status
        assert parsed.priority == original.priority
        assert parsed.owner == original.owner
        assert parsed.tags == original.tags

    def test_parse_item_with_links_in_frontmatter(self, temp_storage_dir: Any) -> None:
        """Given: Markdown with links in frontmatter.

        When: parse_item_markdown called
        Then: Links parsed correctly.
        """
        content = """---
id: story-1
external_id: STORY-001
type: story
status: todo
links:
  - type: implements
    target: EPIC-001
  - type: depends_on
    target: STORY-002
---

# Login Feature
"""
        file_path = temp_storage_dir / "STORY-001.md"
        file_path.write_text(content)

        parsed = parse_item_markdown(file_path)

        assert len(parsed.links) == COUNT_TWO
        assert parsed.links[0]["type"] == "implements"
        assert parsed.links[1]["target"] == "STORY-002"

    def test_parse_item_raises_on_missing_file(self, temp_storage_dir: Any) -> None:
        """Given: Non-existent file path.

        When: parse_item_markdown called
        Then: FileNotFoundError raised.
        """
        with pytest.raises(FileNotFoundError):
            parse_item_markdown(temp_storage_dir / "nonexistent.md")

    def test_parse_item_raises_on_invalid_frontmatter(self, temp_storage_dir: Any) -> None:
        """Given: Markdown without frontmatter.

        When: parse_item_markdown called
        Then: ValueError raised.
        """
        file_path = temp_storage_dir / "invalid.md"
        file_path.write_text("# Just a title\n\nNo frontmatter here")

        with pytest.raises(ValueError, match="No YAML frontmatter"):
            parse_item_markdown(file_path)

    def test_parse_item_raises_on_missing_required_fields(self, temp_storage_dir: Any) -> None:
        """Given: Frontmatter missing required fields.

        When: parse_item_markdown called
        Then: ValueError raised.
        """
        content = """---
id: item-1
type: story
---

# Missing external_id and status
"""
        file_path = temp_storage_dir / "incomplete.md"
        file_path.write_text(content)

        with pytest.raises(ValueError, match="Missing required frontmatter fields"):
            parse_item_markdown(file_path)

    def test_write_and_parse_links_roundtrip(self, temp_storage_dir: Any) -> None:
        """Given: List of LinkData.

        When: write_links_yaml then parse_links_yaml
        Then: Links preserved.
        """
        original_links = [
            LinkData(
                id="link-1",
                source="EPIC-001",
                target="STORY-001",
                link_type="implements",
                created=datetime(2024, 1, 1, tzinfo=UTC),
            ),
            LinkData(
                id="link-2",
                source="STORY-001",
                target="TEST-001",
                link_type="tests",
                created=datetime(2024, 1, 2, tzinfo=UTC),
                metadata={"coverage": "90%"},
            ),
        ]

        # Write to file
        file_path = temp_storage_dir / "links.yaml"
        write_links_yaml(original_links, file_path)

        # Parse back
        parsed_links = parse_links_yaml(file_path)

        assert len(parsed_links) == COUNT_TWO
        assert parsed_links[0].id == "link-1"
        assert parsed_links[0].source == "EPIC-001"
        assert parsed_links[1].metadata["coverage"] == "90%"

    def test_parse_links_returns_empty_for_missing_file(self, temp_storage_dir: Any) -> None:
        """Given: Non-existent links.yaml.

        When: parse_links_yaml called
        Then: FileNotFoundError raised.
        """
        with pytest.raises(FileNotFoundError):
            parse_links_yaml(temp_storage_dir / "nonexistent.yaml")

    def test_parse_links_handles_empty_file(self, temp_storage_dir: Any) -> None:
        """Given: links.yaml with no links.

        When: parse_links_yaml called
        Then: Empty list returned.
        """
        file_path = temp_storage_dir / "links.yaml"
        file_path.write_text("links: []\n")

        links = parse_links_yaml(file_path)
        assert len(links) == 0

    def test_write_and_parse_config_roundtrip(self, temp_storage_dir: Any) -> None:
        """Given: Configuration dict.

        When: write_config_yaml then parse_config_yaml
        Then: Config preserved.
        """
        config = {
            "project_name": "TestProject",
            "version": "1.0.0",
            "settings": {"auto_sync": True, "max_retries": 3},
        }

        file_path = temp_storage_dir / "config.yaml"
        write_config_yaml(config, file_path)

        parsed = parse_config_yaml(file_path)

        assert parsed["project_name"] == "TestProject"
        assert parsed["settings"]["auto_sync"] is True

    def test_list_items_finds_all_markdown_files(self, temp_storage_dir: Any) -> None:
        """Given: Project with multiple item files.

        When: list_items called
        Then: All markdown files found.
        """
        project_dir = temp_storage_dir / "projects" / "TestProject"

        # Create items in different directories - use correct directory names
        # epics, stories, tests (plural)
        for item_type, dir_name in [("epic", "epics"), ("story", "stories"), ("test", "tests")]:
            type_dir = project_dir / dir_name
            type_dir.mkdir(parents=True)
            (type_dir / f"{item_type.upper()}-001.md").write_text("# Test")

        items = list_items(temp_storage_dir, "TestProject")
        assert len(items) == COUNT_THREE

    def test_list_items_filters_by_type(self, temp_storage_dir: Any) -> None:
        """Given: Items of multiple types.

        When: list_items called with type filter
        Then: Only matching files returned.
        """
        project_dir = temp_storage_dir / "projects" / "TestProject"

        epics_dir = project_dir / "epics"
        epics_dir.mkdir(parents=True)
        (epics_dir / "EPIC-001.md").write_text("# Epic")
        (epics_dir / "EPIC-002.md").write_text("# Epic 2")

        stories_dir = project_dir / "stories"
        stories_dir.mkdir(parents=True)
        (stories_dir / "STORY-001.md").write_text("# Story")

        epics = list_items(temp_storage_dir, "TestProject", item_type="epic")
        assert len(epics) == COUNT_TWO

    def test_get_item_path_constructs_correct_path(self, temp_storage_dir: Any) -> None:
        """Given: Item parameters.

        When: get_item_path called
        Then: Correct path constructed.
        """
        path = get_item_path(temp_storage_dir, "MyProject", "epic", "EPIC-001")

        expected = temp_storage_dir / "projects" / "MyProject" / "epics" / "EPIC-001.md"
        assert path == expected

    def test_get_links_path_constructs_correct_path(self, temp_storage_dir: Any) -> None:
        """Given: Project name.

        When: get_links_path called
        Then: Correct path to links.yaml.
        """
        path = get_links_path(temp_storage_dir, "MyProject")

        expected = temp_storage_dir / "projects" / "MyProject" / ".meta" / "links.yaml"
        assert path == expected

    def test_get_config_path_constructs_correct_path(self, temp_storage_dir: Any) -> None:
        """Given: Project name.

        When: get_config_path called
        Then: Correct path to config.yaml.
        """
        path = get_config_path(temp_storage_dir, "MyProject")

        expected = temp_storage_dir / "projects" / "MyProject" / ".meta" / "config.yaml"
        assert path == expected


# ============================================================================
# SyncEngine Integration Tests
# ============================================================================


class TestSyncEngineIntegration:
    """Integration tests for SyncEngine with real database."""

    @pytest.fixture
    def sync_db(self, temp_storage_dir: Any) -> None:
        """Create sync database."""
        db_path = temp_storage_dir / "sync.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def sync_queue(self, sync_db: Any) -> None:
        """Create SyncQueue instance."""
        mock_db = Mock()
        mock_db.engine = sync_db
        return SyncQueue(mock_db)

    @pytest.fixture
    def sync_state_manager(self, sync_db: Any) -> None:
        """Create SyncStateManager instance."""
        mock_db = Mock()
        mock_db.engine = sync_db
        return SyncStateManager(mock_db)

    @pytest_asyncio.fixture
    async def sync_engine(self, sync_db: Any, storage_manager: Any) -> None:
        """Create SyncEngine instance."""
        mock_db = Mock()
        mock_db.engine = sync_db
        mock_api = AsyncMock()
        return SyncEngine(
            db_connection=mock_db,
            api_client=mock_api,
            storage_manager=storage_manager,
        )

    def test_sync_queue_enqueue_creates_entry(self, sync_queue: Any) -> None:
        """Given: Empty sync queue.

        When: enqueue called
        Then: Entry added to queue.
        """
        queue_id = sync_queue.enqueue(
            entity_type=SyncEntityType.ITEM,
            entity_id="item-123",
            operation=OperationType.CREATE,
            payload={"title": "Test Item"},
        )

        assert queue_id is not None

        pending = sync_queue.get_pending(limit=10)
        assert len(pending) == 1
        assert pending[0].entity_id == "item-123"

    def test_sync_queue_enqueue_replaces_duplicate(self, sync_queue: Any) -> None:
        """Given: Existing queue entry.

        When: enqueue called with same entity/operation
        Then: Entry replaced, not duplicated.
        """
        sync_queue.enqueue(SyncEntityType.ITEM, "item-1", OperationType.UPDATE, {"version": 1})
        sync_queue.enqueue(SyncEntityType.ITEM, "item-1", OperationType.UPDATE, {"version": 2})

        pending = sync_queue.get_pending(limit=10)
        assert len(pending) == 1
        assert pending[0].payload["version"] == COUNT_TWO

    def test_sync_queue_get_pending_orders_by_created_at(self, sync_queue: Any) -> None:
        """Given: Multiple queue entries.

        When: get_pending called
        Then: Entries ordered by creation time (oldest first).
        """
        import time

        sync_queue.enqueue(SyncEntityType.ITEM, "item-1", OperationType.CREATE, {})
        time.sleep(0.01)
        sync_queue.enqueue(SyncEntityType.ITEM, "item-2", OperationType.CREATE, {})
        time.sleep(0.01)
        sync_queue.enqueue(SyncEntityType.ITEM, "item-3", OperationType.CREATE, {})

        pending = sync_queue.get_pending(limit=10)
        assert pending[0].entity_id == "item-1"
        assert pending[1].entity_id == "item-2"
        assert pending[2].entity_id == "item-3"

    def test_sync_queue_remove_deletes_entry(self, sync_queue: Any) -> None:
        """Given: Queue entry.

        When: remove called
        Then: Entry deleted from queue.
        """
        queue_id = sync_queue.enqueue(SyncEntityType.ITEM, "item-1", OperationType.CREATE, {})

        sync_queue.remove(queue_id)

        pending = sync_queue.get_pending(limit=10)
        assert len(pending) == 0

    def test_sync_queue_clear_removes_all(self, sync_queue: Any) -> None:
        """Given: Multiple queue entries.

        When: clear called
        Then: All entries removed.
        """
        for i in range(5):
            sync_queue.enqueue(SyncEntityType.ITEM, f"item-{i}", OperationType.CREATE, {})

        sync_queue.clear()

        pending = sync_queue.get_pending(limit=10)
        assert len(pending) == 0

    def test_sync_queue_get_count_returns_correct_count(self, sync_queue: Any) -> None:
        """Given: Queue with entries.

        When: get_count called
        Then: Correct count returned.
        """
        for i in range(7):
            sync_queue.enqueue(SyncEntityType.ITEM, f"item-{i}", OperationType.CREATE, {})

        count = sync_queue.get_count()
        assert count == 7

    def test_sync_state_manager_get_state_returns_defaults(self, sync_state_manager: Any) -> None:
        """Given: No sync state.

        When: get_state called
        Then: Default state returned.
        """
        state = sync_state_manager.get_state()

        assert state.last_sync is None
        assert state.pending_changes == 0
        assert state.status == SyncStatus.IDLE

    def test_sync_state_manager_update_last_sync_persists(self, sync_state_manager: Any) -> None:
        """Given: State manager.

        When: update_last_sync called
        Then: Timestamp persisted.
        """
        timestamp = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        sync_state_manager.update_last_sync(timestamp)

        state = sync_state_manager.get_state()
        assert state.last_sync == timestamp

    def test_sync_state_manager_update_status_persists(self, sync_state_manager: Any) -> None:
        """Given: State manager.

        When: update_status called
        Then: Status persisted.
        """
        sync_state_manager.update_status(SyncStatus.SYNCING)

        state = sync_state_manager.get_state()
        assert state.status == SyncStatus.SYNCING

    def test_sync_state_manager_update_error_persists(self, sync_state_manager: Any) -> None:
        """Given: State manager.

        When: update_error called
        Then: Error persisted.
        """
        sync_state_manager.update_error("Test error message")

        state = sync_state_manager.get_state()
        assert state.last_error == "Test error message"

    def test_sync_state_manager_update_error_clears_on_none(self, sync_state_manager: Any) -> None:
        """Given: Error state.

        When: update_error called with None
        Then: Error cleared.
        """
        sync_state_manager.update_error("Error")
        sync_state_manager.update_error(None)

        state = sync_state_manager.get_state()
        assert state.last_error is None

    def test_change_detector_compute_hash_is_deterministic(self) -> None:
        """Given: Same content.

        When: compute_hash called multiple times
        Then: Same hash returned.
        """
        content = "Test content for hashing"

        hash1 = ChangeDetector.compute_hash(content)
        hash2 = ChangeDetector.compute_hash(content)

        assert hash1 == hash2

    def test_change_detector_has_changed_detects_change(self) -> None:
        """Given: Different content.

        When: has_changed called
        Then: Returns True.
        """
        original = "Original content"
        modified = "Modified content"

        original_hash = ChangeDetector.compute_hash(original)
        changed = ChangeDetector.has_changed(modified, original_hash)

        assert changed is True

    def test_change_detector_has_changed_detects_no_change(self) -> None:
        """Given: Identical content.

        When: has_changed called
        Then: Returns False.
        """
        content = "Same content"

        content_hash = ChangeDetector.compute_hash(content)
        changed = ChangeDetector.has_changed(content, content_hash)

        assert changed is False

    def test_change_detector_detect_changes_in_directory(self, temp_storage_dir: Any) -> None:
        """Given: Directory with markdown files.

        When: detect_changes_in_directory called
        Then: Changed files detected.
        """
        md_dir = temp_storage_dir / "items"
        md_dir.mkdir()

        file1 = md_dir / "item1.md"
        file2 = md_dir / "item2.md"

        file1.write_text("Original content 1")
        file2.write_text("Original content 2")

        # Create hash map
        stored_hashes = {
            "item1.md": ChangeDetector.compute_hash("Original content 1"),
            "item2.md": ChangeDetector.compute_hash("Different content"),
        }

        # Modify file2
        file2.write_text("Modified content 2")

        changes = ChangeDetector.detect_changes_in_directory(md_dir, stored_hashes)

        # Only item2.md should be detected as changed
        assert len(changes) == 1
        assert changes[0][0].name == "item2.md"

    @pytest.mark.asyncio
    async def test_exponential_backoff_increases_delay(self) -> None:
        """Given: Retry attempts.

        When: exponential_backoff called
        Then: Delay increases exponentially.
        """
        import time

        start = time.time()
        await exponential_backoff(0, initial_delay=0.01)
        delay0 = time.time() - start

        start = time.time()
        await exponential_backoff(1, initial_delay=0.01)
        delay1 = time.time() - start

        start = time.time()
        await exponential_backoff(2, initial_delay=0.01)
        delay2 = time.time() - start

        # Each delay should be roughly double the previous
        assert delay1 > delay0
        assert delay2 > delay1


# ============================================================================
# ConflictResolver Integration Tests
# ============================================================================


class TestConflictResolverIntegration:
    """Integration tests for ConflictResolver with real database and filesystem."""

    def test_detect_conflict_identifies_concurrent_changes(self, conflict_resolver: Any) -> None:
        """Given: Two concurrent versions of same entity.

        When: detect_conflict called
        Then: Conflict detected.
        """
        now = datetime.now(UTC)

        local_clock = VectorClock(client_id="client-1", version=5, timestamp=now, parent_version=4)
        remote_clock = VectorClock(client_id="client-2", version=5, timestamp=now, parent_version=4)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local Title"},
            vector_clock=local_clock,
            content_hash="hash-local",
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote Title"},
            vector_clock=remote_clock,
            content_hash="hash-remote",
        )

        conflict = conflict_resolver.detect_conflict(local, remote)

        assert conflict is not None
        assert conflict.entity_id == "item-1"
        assert conflict.status == ConflictStatus.UNRESOLVED

    def test_detect_conflict_returns_none_for_ordered_changes(self, conflict_resolver: Any) -> None:
        """Given: One version clearly before another.

        When: detect_conflict called
        Then: No conflict detected.
        """
        now = datetime.now(UTC)

        local_clock = VectorClock(client_id="client-1", version=4, timestamp=now - timedelta(hours=1))
        remote_clock = VectorClock(client_id="client-1", version=5, timestamp=now)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Old Title"},
            vector_clock=local_clock,
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "New Title"},
            vector_clock=remote_clock,
        )

        conflict = conflict_resolver.detect_conflict(local, remote)
        assert conflict is None

    def test_detect_conflict_returns_none_for_same_content(self, conflict_resolver: Any) -> None:
        """Given: Concurrent versions with same content.

        When: detect_conflict called
        Then: No conflict (same hash).
        """
        now = datetime.now(UTC)

        local_clock = VectorClock(client_id="client-1", version=5, timestamp=now)
        remote_clock = VectorClock(client_id="client-2", version=5, timestamp=now)

        same_hash = "same-content-hash"

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Same Title"},
            vector_clock=local_clock,
            content_hash=same_hash,
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Same Title"},
            vector_clock=remote_clock,
            content_hash=same_hash,
        )

        conflict = conflict_resolver.detect_conflict(local, remote)
        assert conflict is None

    def test_resolve_last_write_wins_chooses_newer(self, conflict_resolver: Any) -> None:
        """Given: Conflict with different timestamps.

        When: resolve called with LAST_WRITE_WINS
        Then: Newer version wins.
        """
        now = datetime.now(UTC)
        older = now - timedelta(hours=1)

        local_clock = VectorClock(client_id="client-1", version=5, timestamp=older)
        remote_clock = VectorClock(client_id="client-2", version=5, timestamp=now)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Old"},
            vector_clock=local_clock,
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "New"},
            vector_clock=remote_clock,
        )

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        resolved = conflict_resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)

        assert resolved.version == remote
        assert resolved.version.data["title"] == "New"

    def test_resolve_local_wins_always_chooses_local(self, conflict_resolver: Any) -> None:
        """Given: Conflict.

        When: resolve called with LOCAL_WINS
        Then: Local version always wins.
        """
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 5, now - timedelta(hours=1)),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 5, now),
        )

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        resolved = conflict_resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)

        assert resolved.version == local

    def test_resolve_remote_wins_always_chooses_remote(self, conflict_resolver: Any) -> None:
        """Given: Conflict.

        When: resolve called with REMOTE_WINS
        Then: Remote version always wins.
        """
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 5, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 5, now - timedelta(hours=1)),
        )

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        resolved = conflict_resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)

        assert resolved.version == remote

    def test_resolve_creates_backup(self, conflict_resolver: Any, _temp_storage_dir: Any) -> None:
        """Given: Conflict.

        When: resolve called
        Then: Backup created before resolution.
        """
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 5, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 5, now),
        )

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        conflict_resolver.resolve(conflict)

        # Verify backup created
        assert conflict.backup_path is not None
        assert conflict.backup_path.exists()
        assert (conflict.backup_path / "local.json").exists()
        assert (conflict.backup_path / "remote.json").exists()

    def test_resolve_manual_creates_merged_version(self, conflict_resolver: Any) -> None:
        """Given: Conflict.

        When: resolve_manual called with merged data
        Then: New version created with merged content.
        """
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local", "status": "in_progress"},
            vector_clock=VectorClock("client-1", 5, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote", "priority": "high"},
            vector_clock=VectorClock("client-2", 5, now),
        )

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        merged_data = {
            "title": "Merged Title",
            "status": "in_progress",
            "priority": "high",
        }

        resolved = conflict_resolver.resolve_manual(conflict, merged_data, merged_by="alice")

        assert resolved.version.data == merged_data
        assert resolved.version.vector_clock.version == 6  # max(5,5) + 1
        assert conflict.metadata["merged_by"] == "alice"

    def test_create_backup_writes_all_files(self, conflict_resolver: Any, temp_storage_dir: Any) -> None:
        """Given: Conflict.

        When: create_backup called
        Then: All backup files written.
        """
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 5, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 5, now),
        )

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        backup_path = conflict_resolver.create_backup(conflict)

        assert (backup_path / "local.json").exists()
        assert (backup_path / "remote.json").exists()
        assert (backup_path / "conflict.json").exists()

        # Verify content
        with Path(backup_path / "local.json").open(encoding="utf-8") as f:
            local_data = json.load(f)
            assert local_data["data"]["title"] == "Local"

    def test_list_unresolved_returns_unresolved_conflicts(self, conflict_resolver: Any) -> None:
        """Given: Mix of resolved and unresolved conflicts.

        When: list_unresolved called
        Then: Only unresolved conflicts returned.
        """
        now = datetime.now(UTC)

        # Create unresolved conflict
        local1 = EntityVersion("item-1", "item", {"title": "L1"}, VectorClock("c1", 1, now))
        remote1 = EntityVersion("item-1", "item", {"title": "R1"}, VectorClock("c2", 1, now))
        conflict_resolver.detect_conflict(local1, remote1)

        # Create and resolve another conflict
        local2 = EntityVersion("item-2", "item", {"title": "L2"}, VectorClock("c1", 1, now))
        remote2 = EntityVersion("item-2", "item", {"title": "R2"}, VectorClock("c2", 1, now))
        conflict2 = conflict_resolver.detect_conflict(local2, remote2)
        conflict_resolver.resolve(conflict2)

        unresolved = conflict_resolver.list_unresolved()

        assert len(unresolved) == 1
        assert unresolved[0].entity_id == "item-1"

    def test_get_conflict_retrieves_by_id(self, conflict_resolver: Any) -> None:
        """Given: Stored conflict.

        When: get_conflict called with ID
        Then: Conflict retrieved.
        """
        now = datetime.now(UTC)

        local = EntityVersion("item-1", "item", {"title": "Local"}, VectorClock("c1", 1, now))
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, VectorClock("c2", 1, now))

        created = conflict_resolver.detect_conflict(local, remote)
        conflict_id = created.id

        retrieved = conflict_resolver.get_conflict(conflict_id)

        assert retrieved is not None
        assert retrieved.id == conflict_id
        assert retrieved.entity_id == "item-1"

    def test_get_conflict_returns_none_for_unknown_id(self, conflict_resolver: Any) -> None:
        """Given: No conflicts.

        When: get_conflict called with unknown ID
        Then: None returned.
        """
        result = conflict_resolver.get_conflict("nonexistent-conflict-id")
        assert result is None

    def test_get_conflict_stats_returns_statistics(self, conflict_resolver: Any) -> None:
        """Given: Multiple conflicts.

        When: get_conflict_stats called
        Then: Correct statistics returned.
        """
        now = datetime.now(UTC)

        # Create multiple conflicts
        for i in range(3):
            local = EntityVersion(f"item-{i}", "item", {"title": f"L{i}"}, VectorClock("c1", 1, now))
            remote = EntityVersion(f"item-{i}", "item", {"title": f"R{i}"}, VectorClock("c2", 1, now))
            conflict = conflict_resolver.detect_conflict(local, remote)

            # Resolve first conflict
            if i == 0:
                conflict_resolver.resolve(conflict)

        stats = conflict_resolver.get_conflict_stats()

        assert stats["total"] == COUNT_THREE
        assert ConflictStatus.UNRESOLVED.value in stats["by_status"]
        assert "item" in stats["by_entity_type"]

    def test_vector_clock_happens_before_same_client(self) -> None:
        """Given: Two clocks from same client.

        When: happens_before called
        Then: Version comparison used.
        """
        now = datetime.now(UTC)

        clock1 = VectorClock("client-1", 4, now)
        clock2 = VectorClock("client-1", 5, now)

        assert clock1.happens_before(clock2) is True
        assert clock2.happens_before(clock1) is False

    def test_vector_clock_happens_before_different_clients(self) -> None:
        """Given: Two clocks from different clients.

        When: happens_before called
        Then: Timestamp comparison used.
        """
        now = datetime.now(UTC)
        earlier = now - timedelta(hours=1)

        clock1 = VectorClock("client-1", 5, earlier)
        clock2 = VectorClock("client-2", 5, now)

        assert clock1.happens_before(clock2) is True

    def test_vector_clock_is_concurrent_detects_conflict(self) -> None:
        """Given: Two concurrent clocks.

        When: is_concurrent called
        Then: Returns True.
        """
        now = datetime.now(UTC)

        clock1 = VectorClock("client-1", 5, now)
        clock2 = VectorClock("client-2", 5, now)

        assert clock1.is_concurrent(clock2) is True

    def test_compare_versions_identifies_differences(self) -> None:
        """Given: Two versions with different fields.

        When: compare_versions called
        Then: Differences identified.
        """
        now = datetime.now(UTC)

        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Title", "status": "todo", "local_only": "value"},
            VectorClock("c1", 1, now),
        )

        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Different", "status": "todo", "remote_only": "value"},
            VectorClock("c2", 1, now),
        )

        diff = compare_versions(local, remote)

        assert "title" in diff["modified"]
        assert "remote_only" in diff["added"]
        assert "local_only" in diff["removed"]

    def test_format_conflict_summary_creates_readable_output(self) -> None:
        """Given: Conflict.

        When: format_conflict_summary called
        Then: Human-readable summary generated.
        """
        now = datetime.now(UTC)

        local = EntityVersion("item-1", "item", {"title": "Local"}, VectorClock("c1", 5, now))
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, VectorClock("c2", 6, now))

        conflict = Conflict(
            id="conflict-1",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        summary = format_conflict_summary(conflict)

        assert "item-1" in summary
        assert "v5" in summary
        assert "v6" in summary
        assert "item" in summary


# ============================================================================
# ConflictBackup Integration Tests
# ============================================================================


class TestConflictBackupIntegration:
    """Integration tests for ConflictBackup with real filesystem."""

    @pytest.fixture
    def backup_manager(self, temp_storage_dir: Any) -> None:
        """Create ConflictBackup instance."""
        return ConflictBackup(temp_storage_dir / "backups")

    def test_list_backups_finds_all_backups(self, backup_manager: Any, temp_storage_dir: Any) -> None:
        """Given: Multiple backup directories.

        When: list_backups called
        Then: All backups listed.
        """
        backup_dir = temp_storage_dir / "backups"

        # Create sample backups
        for i in range(3):
            item_backup = backup_dir / "item" / f"item-{i}_20240101_120000"
            item_backup.mkdir(parents=True)

            conflict_meta = {
                "conflict_id": f"conflict-{i}",
                "entity_id": f"item-{i}",
                "detected_at": "2024-01-01T12:00:00Z",
            }

            (item_backup / "conflict.json").write_text(json.dumps(conflict_meta))

        backups = backup_manager.list_backups()
        assert len(backups) == COUNT_THREE

    def test_list_backups_filters_by_entity_type(self, backup_manager: Any, temp_storage_dir: Any) -> None:
        """Given: Backups of different entity types.

        When: list_backups called with entity_type filter
        Then: Only matching backups returned.
        """
        backup_dir = temp_storage_dir / "backups"

        # Create item backup
        item_backup = backup_dir / "item" / "item-1_20240101_120000"
        item_backup.mkdir(parents=True)
        (item_backup / "conflict.json").write_text(
            json.dumps({"conflict_id": "c1", "entity_id": "item-1", "detected_at": "2024-01-01T12:00:00Z"}),
        )

        # Create link backup
        link_backup = backup_dir / "link" / "link-1_20240101_120000"
        link_backup.mkdir(parents=True)
        (link_backup / "conflict.json").write_text(
            json.dumps({"conflict_id": "c2", "entity_id": "link-1", "detected_at": "2024-01-01T12:00:00Z"}),
        )

        backups = backup_manager.list_backups(entity_type="item")
        assert len(backups) == 1
        assert backups[0]["entity_id"] == "item-1"

    def test_load_backup_restores_versions(self, backup_manager: Any, temp_storage_dir: Any) -> None:
        """Given: Backup directory with version files.

        When: load_backup called
        Then: Versions restored.
        """
        now = datetime.now(UTC)
        backup_dir = temp_storage_dir / "backups" / "item" / "test_backup"
        backup_dir.mkdir(parents=True)

        local = EntityVersion("item-1", "item", {"title": "Local"}, VectorClock("c1", 1, now))
        remote = EntityVersion("item-1", "item", {"title": "Remote"}, VectorClock("c2", 1, now))

        # Write backup files
        (backup_dir / "local.json").write_text(json.dumps(local.to_dict()))
        (backup_dir / "remote.json").write_text(json.dumps(remote.to_dict()))

        loaded = backup_manager.load_backup(backup_dir)

        assert loaded is not None
        local_loaded, remote_loaded = loaded
        assert local_loaded.data["title"] == "Local"
        assert remote_loaded.data["title"] == "Remote"

    def test_load_backup_returns_none_for_incomplete_backup(self, backup_manager: Any, temp_storage_dir: Any) -> None:
        """Given: Backup directory with missing files.

        When: load_backup called
        Then: None returned.
        """
        backup_dir = temp_storage_dir / "incomplete"
        backup_dir.mkdir()

        # Only create local.json, not remote.json
        (backup_dir / "local.json").write_text("{}")

        result = backup_manager.load_backup(backup_dir)
        assert result is None

    def test_delete_backup_removes_directory(self, backup_manager: Any, temp_storage_dir: Any) -> None:
        """Given: Backup directory.

        When: delete_backup called
        Then: Directory removed.
        """
        backup_dir = temp_storage_dir / "backups" / "item" / "test_backup"
        backup_dir.mkdir(parents=True)
        (backup_dir / "test.txt").write_text("test")

        assert backup_dir.exists()

        result = backup_manager.delete_backup(backup_dir)

        assert result is True
        assert not backup_dir.exists()

    def test_delete_backup_returns_false_for_nonexistent(self, backup_manager: Any, temp_storage_dir: Any) -> None:
        """Given: Non-existent backup directory.

        When: delete_backup called
        Then: False returned.
        """
        nonexistent = temp_storage_dir / "nonexistent"

        result = backup_manager.delete_backup(nonexistent)
        assert result is False
