"""Comprehensive tests for tracertm.tui.adapters.storage_adapter module.

Tests storage adapter functionality including project operations, item management,
link management, sync operations, and reactive callbacks.
Coverage target: 80%+ of 138 statements
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Never
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models import Item, Link, Project
from tracertm.storage.sync_engine import SyncState, SyncStatus
from tracertm.tui.adapters.storage_adapter import StorageAdapter


@pytest.fixture
def mock_storage() -> None:
    """Create mock LocalStorageManager."""
    return MagicMock()


@pytest.fixture
def mock_sync_engine() -> None:
    """Create mock SyncEngine."""
    return MagicMock()


@pytest.fixture
def storage_adapter(mock_storage: Any, mock_sync_engine: Any) -> None:
    """Create StorageAdapter instance with mocked dependencies."""
    with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager") as mock_cls:
        mock_cls.return_value = mock_storage
        adapter = StorageAdapter(sync_engine=mock_sync_engine)
        adapter.storage = mock_storage
        return adapter


class TestAdapterInitialization:
    """Test StorageAdapter initialization."""

    def test_init_with_default_base_dir(self) -> None:
        """Test adapter initializes with default base directory."""
        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager") as mock_storage:
            adapter = StorageAdapter()

            mock_storage.assert_called_once_with(None)
            assert adapter.sync_engine is None
            assert adapter._sync_status_callbacks == []
            assert adapter._conflict_callbacks == []
            assert adapter._item_change_callbacks == []

    def test_init_with_custom_base_dir(self) -> None:
        """Test adapter initializes with custom base directory."""
        custom_dir = Path("/custom/path")

        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager") as mock_storage:
            StorageAdapter(base_dir=custom_dir)

            mock_storage.assert_called_once_with(custom_dir)

    def test_init_with_sync_engine(self, mock_sync_engine: Any) -> None:
        """Test adapter initializes with sync engine."""
        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager"):
            adapter = StorageAdapter(sync_engine=mock_sync_engine)

            assert adapter.sync_engine == mock_sync_engine


class TestProjectOperations:
    """Test project-related operations."""

    def test_get_project_success(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test getting project by name."""
        project_storage = MagicMock()
        mock_project = Project(name="Test Project", description="Test")
        project_storage.get_project.return_value = mock_project
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.get_project("Test Project")

        assert result == mock_project
        mock_storage.get_project_storage.assert_called_once_with("Test Project")
        project_storage.get_project.assert_called_once()

    def test_get_project_not_found(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test getting non-existent project returns None."""
        project_storage = MagicMock()
        project_storage.get_project.return_value = None
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.get_project("Nonexistent")

        assert result is None

    def test_create_project(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test creating a project."""
        project_storage = MagicMock()
        mock_project = Project(name="New Project", description="Description")
        project_storage.create_or_update_project.return_value = mock_project
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.create_project("New Project", description="Description", metadata={"key": "value"})

        assert result == mock_project
        project_storage.create_or_update_project.assert_called_once_with("New Project", "Description", {"key": "value"})


class TestItemOperations:
    """Test item-related operations."""

    def test_list_items_all(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test listing all items in a project."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_items = [Item(id="item-1", title="Item 1"), Item(id="item-2", title="Item 2")]
        item_storage.list_items.return_value = mock_items

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.list_items(project)

        assert result == mock_items
        item_storage.list_items.assert_called_once_with(item_type=None, status=None, parent_id=None)

    def test_list_items_with_filters(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test listing items with type, status, and parent filters."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_items = [Item(id="item-1", title="Filtered Item")]
        item_storage.list_items.return_value = mock_items

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.list_items(project, item_type="epic", status="in_progress", parent_id="parent-1")

        assert result == mock_items
        item_storage.list_items.assert_called_once_with(item_type="epic", status="in_progress", parent_id="parent-1")

    def test_get_item(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test getting single item by ID."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_item = Item(id="item-1", title="Test Item")
        item_storage.get_item.return_value = mock_item

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.get_item(project, "item-1")

        assert result == mock_item
        item_storage.get_item.assert_called_once_with("item-1")

    def test_create_item(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test creating a new item."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_item = Item(id="item-new", title="New Item")
        item_storage.create_item.return_value = mock_item

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        # Track callback notifications
        callback_called = []
        storage_adapter.on_item_change(callback_called.append)

        result = storage_adapter.create_item(
            project,
            title="New Item",
            item_type="story",
            external_id="STORY-001",
            description="Description",
            status="todo",
            priority="high",
        )

        assert result == mock_item
        assert "item-new" in callback_called

    def test_update_item(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test updating an existing item."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_item = Item(id="item-1", title="Updated Item")
        item_storage.update_item.return_value = mock_item

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        # Track callback notifications
        callback_called = []
        storage_adapter.on_item_change(callback_called.append)

        result = storage_adapter.update_item(project, item_id="item-1", title="Updated Item", status="done")

        assert result == mock_item
        assert "item-1" in callback_called

    def test_delete_item(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test soft-deleting an item."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        # Track callback notifications
        callback_called = []
        storage_adapter.on_item_change(callback_called.append)

        storage_adapter.delete_item(project, "item-1")

        item_storage.delete_item.assert_called_once_with("item-1")
        assert "item-1" in callback_called


class TestLinkOperations:
    """Test link-related operations."""

    def test_list_links(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test listing links with filters."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_links = [Link(id="link-1", source_item_id="item-1", target_item_id="item-2")]
        item_storage.list_links.return_value = mock_links

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.list_links(project, source_id="item-1", link_type="implements")

        assert result == mock_links
        item_storage.list_links.assert_called_once_with(source_id="item-1", target_id=None, link_type="implements")

    def test_create_link(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test creating a traceability link."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()
        mock_link = Link(id="link-1", source_item_id="item-1", target_item_id="item-2")
        item_storage.create_link.return_value = mock_link

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        result = storage_adapter.create_link(
            project,
            source_id="item-1",
            target_id="item-2",
            link_type="implements",
            metadata={"key": "value"},
        )

        assert result == mock_link

    def test_delete_link(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test deleting a link."""
        project = Project(name="Test", id="proj-1")
        item_storage = MagicMock()

        project_storage = MagicMock()
        project_storage.get_item_storage.return_value = item_storage
        mock_storage.get_project_storage.return_value = project_storage

        storage_adapter.delete_link(project, "link-1")

        item_storage.delete_link.assert_called_once_with("link-1")


class TestSearchOperations:
    """Test search functionality."""

    def test_search_items(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test full-text search across items."""
        mock_results = [Item(id="item-1", title="Matching Item")]
        mock_storage.search_items.return_value = mock_results

        result = storage_adapter.search_items("query", project_id="proj-1")

        assert result == mock_results
        mock_storage.search_items.assert_called_once_with("query", "proj-1")


class TestSyncOperations:
    """Test sync-related operations."""

    def test_get_sync_status_with_sync_engine(self, storage_adapter: Any, mock_sync_engine: Any) -> None:
        """Test getting sync status when sync engine is configured."""
        mock_state = SyncState(last_sync=datetime.now(), pending_changes=5, status=SyncStatus.IDLE)
        mock_sync_engine.get_status.return_value = mock_state

        result = storage_adapter.get_sync_status()

        assert result == mock_state
        mock_sync_engine.get_status.assert_called_once()

    def test_get_sync_status_without_sync_engine(self, mock_storage: Any) -> None:
        """Test getting sync status without sync engine returns default state."""
        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager"):
            adapter = StorageAdapter(sync_engine=None)
            adapter.storage = mock_storage
            mock_storage.get_sync_queue.return_value = [{"id": "1"}, {"id": "2"}]

            result = adapter.get_sync_status()

            assert result.last_sync is None
            assert result.pending_changes == COUNT_TWO
            assert result.status == SyncStatus.IDLE

    @pytest.mark.asyncio
    async def test_trigger_sync_success(self, storage_adapter: Any, mock_sync_engine: Any) -> None:
        """Test triggering sync operation successfully."""
        mock_result = MagicMock(success=True, entities_synced=10, conflicts=[], errors=[], duration_seconds=2.5)
        mock_sync_engine.sync = AsyncMock(return_value=mock_result)
        mock_sync_engine.get_status.return_value = SyncState(status=SyncStatus.IDLE, pending_changes=0)

        # Track callback notifications
        callback_states = []
        storage_adapter.on_sync_status_change(callback_states.append)

        result = await storage_adapter.trigger_sync()

        assert result["success"] is True
        assert result["entities_synced"] == COUNT_TEN
        assert len(callback_states) >= 1  # At least one callback

    @pytest.mark.asyncio
    async def test_trigger_sync_without_sync_engine(self, _mock_storage: Any) -> None:
        """Test triggering sync without sync engine returns error."""
        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager"):
            adapter = StorageAdapter(sync_engine=None)

            result = await adapter.trigger_sync()

            assert result["success"] is False
            assert "not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_trigger_sync_error(self, storage_adapter: Any, mock_sync_engine: Any) -> None:
        """Test sync operation handling errors."""
        mock_sync_engine.sync = AsyncMock(side_effect=Exception("Sync failed"))

        # Track callback notifications
        callback_states = []
        storage_adapter.on_sync_status_change(callback_states.append)

        result = await storage_adapter.trigger_sync()

        assert result["success"] is False
        assert "Sync failed" in result["error"]

    def test_get_pending_changes_count(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test getting count of pending sync changes."""
        mock_storage.get_sync_queue.return_value = [{"id": str(i)} for i in range(5)]

        result = storage_adapter.get_pending_changes_count()

        assert result == COUNT_FIVE


class TestConflictOperations:
    """Test conflict-related operations."""

    def test_get_unresolved_conflicts(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test getting unresolved conflicts."""
        mock_session = MagicMock()
        mock_storage.get_session.return_value = mock_session

        with patch("tracertm.storage.conflict_resolver.ConflictResolver") as mock_resolver:
            resolver_instance = MagicMock()
            mock_conflicts = [MagicMock(), MagicMock()]
            resolver_instance.list_unresolved.return_value = mock_conflicts
            mock_resolver.return_value = resolver_instance

            result = storage_adapter.get_unresolved_conflicts()

            assert result == mock_conflicts
            mock_session.close.assert_called_once()

    def test_get_conflict_count(self, storage_adapter: Any, mock_storage: Any) -> None:
        """Test getting count of unresolved conflicts."""
        mock_session = MagicMock()
        mock_storage.get_session.return_value = mock_session

        with patch("tracertm.storage.conflict_resolver.ConflictResolver") as mock_resolver:
            resolver_instance = MagicMock()
            resolver_instance.list_unresolved.return_value = [MagicMock(), MagicMock(), MagicMock()]
            mock_resolver.return_value = resolver_instance

            result = storage_adapter.get_conflict_count()

            assert result == COUNT_THREE


class TestReactiveCallbacks:
    """Test reactive callback registration and notifications."""

    def test_on_sync_status_change_registration(self, storage_adapter: Any) -> None:
        """Test registering sync status change callback."""
        callback_called = []

        def test_callback(state: Any) -> None:
            callback_called.append(state)

        unregister = storage_adapter.on_sync_status_change(test_callback)

        # Trigger notification
        test_state = SyncState(status=SyncStatus.SYNCING, pending_changes=0)
        storage_adapter._notify_sync_status(test_state)

        assert len(callback_called) == 1
        assert callback_called[0] == test_state

        # Unregister and verify no more notifications
        unregister()
        storage_adapter._notify_sync_status(test_state)
        assert len(callback_called) == 1  # Still 1

    def test_on_conflict_detected_registration(self, storage_adapter: Any) -> None:
        """Test registering conflict detection callback."""
        callback_called = []

        def test_callback(conflict: Any) -> None:
            callback_called.append(conflict)

        unregister = storage_adapter.on_conflict_detected(test_callback)

        # Trigger notification
        test_conflict = MagicMock()
        storage_adapter._notify_conflict(test_conflict)

        assert len(callback_called) == 1

        # Unregister
        unregister()
        storage_adapter._notify_conflict(test_conflict)
        assert len(callback_called) == 1

    def test_on_item_change_registration(self, storage_adapter: Any) -> None:
        """Test registering item change callback."""
        callback_called = []

        def test_callback(item_id: Any) -> None:
            callback_called.append(item_id)

        unregister = storage_adapter.on_item_change(test_callback)

        # Trigger notification
        storage_adapter._notify_item_change("item-123")

        assert len(callback_called) == 1
        assert callback_called[0] == "item-123"

        # Unregister
        unregister()
        storage_adapter._notify_item_change("item-456")
        assert len(callback_called) == 1

    def test_callback_error_handling(self, storage_adapter: Any) -> None:
        """Test callbacks that raise exceptions don't break notification."""

        def failing_callback(_state: Any) -> Never:
            msg = "Callback error"
            raise Exception(msg)

        called: list[bool] = [False]

        def working_callback(_state: Any) -> None:
            called[0] = True

        storage_adapter.on_sync_status_change(failing_callback)
        storage_adapter.on_sync_status_change(working_callback)

        # Should not raise even though first callback fails
        test_state = SyncState(status=SyncStatus.IDLE, pending_changes=0)
        storage_adapter._notify_sync_status(test_state)

        # Second callback should still execute
        assert called[0] is True
