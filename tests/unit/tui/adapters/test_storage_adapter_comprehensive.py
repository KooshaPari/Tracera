"""
Comprehensive tests for StorageAdapter.

Tests project operations, item operations, link operations, search,
sync operations, conflict operations, statistics, and reactive callbacks.
Coverage target: 80%+ (596 lines total)
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

from tracertm.models import Item, Link, Project
from tracertm.storage.conflict_resolver import Conflict
from tracertm.storage.sync_engine import SyncState, SyncStatus
from tracertm.tui.adapters.storage_adapter import StorageAdapter


class TestStorageAdapterInitialization:
    """Test StorageAdapter initialization."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_init_with_defaults(self, mock_storage):
        """Test StorageAdapter initializes with default parameters."""
        adapter = StorageAdapter()

        assert adapter.storage is not None
        assert adapter.sync_engine is None
        assert len(adapter._sync_status_callbacks) == 0
        assert len(adapter._conflict_callbacks) == 0
        assert len(adapter._item_change_callbacks) == 0

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_init_with_base_dir(self, mock_storage):
        """Test StorageAdapter initializes with custom base directory."""
        base_dir = Path("/tmp/test")
        adapter = StorageAdapter(base_dir=base_dir)

        mock_storage.assert_called_once_with(base_dir)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_init_with_sync_engine(self, mock_storage):
        """Test StorageAdapter initializes with sync engine."""
        mock_sync_engine = MagicMock()
        adapter = StorageAdapter(sync_engine=mock_sync_engine)

        assert adapter.sync_engine is mock_sync_engine


class TestStorageAdapterProjectOperations:
    """Test project operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_project_success(self, mock_storage_class):
        """Test get_project returns project."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_project_storage = MagicMock()
        mock_project = Project(id=str(uuid4()), name="Test Project")
        mock_project_storage.get_project.return_value = mock_project
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        result = adapter.get_project("Test Project")

        assert result == mock_project
        mock_storage.get_project_storage.assert_called_once_with("Test Project")

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_project_not_found(self, mock_storage_class):
        """Test get_project returns None when project not found."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_project_storage = MagicMock()
        mock_project_storage.get_project.return_value = None
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        result = adapter.get_project("Nonexistent")

        assert result is None

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_create_project_success(self, mock_storage_class):
        """Test create_project creates or updates project."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_project_storage = MagicMock()
        mock_project = Project(
            id=str(uuid4()),
            name="New Project",
            description="Test description",
            project_metadata={"key": "value"}
        )
        mock_project_storage.create_or_update_project.return_value = mock_project
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        result = adapter.create_project(
            "New Project",
            description="Test description",
            metadata={"key": "value"}
        )

        assert result == mock_project
        mock_project_storage.create_or_update_project.assert_called_once_with(
            "New Project", "Test description", {"key": "value"}
        )


class TestStorageAdapterItemOperations:
    """Test item operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_list_items_success(self, mock_storage_class):
        """Test list_items returns items with filters."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        mock_item1 = Item(id=str(uuid4()), title="Item 1", item_type="epic")
        mock_item2 = Item(id=str(uuid4()), title="Item 2", item_type="epic")

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_item_storage.list_items.return_value = [mock_item1, mock_item2]
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        results = adapter.list_items(project, item_type="epic", status="todo")

        assert len(results) == 2
        assert results[0] == mock_item1
        mock_item_storage.list_items.assert_called_once_with(
            item_type="epic", status="todo", parent_id=None
        )

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_item_success(self, mock_storage_class):
        """Test get_item returns item by ID."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        item_id = str(uuid4())
        mock_item = Item(id=item_id, title="Test Item", item_type="story")

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_item_storage.get_item.return_value = mock_item
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        result = adapter.get_item(project, item_id)

        assert result == mock_item
        mock_item_storage.get_item.assert_called_once_with(item_id)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_create_item_success(self, mock_storage_class):
        """Test create_item creates new item and notifies listeners."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        item_id = str(uuid4())
        mock_item = Item(
            id=item_id,
            title="New Item",
            item_type="task",
            status="todo",
            priority="high"
        )

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_item_storage.create_item.return_value = mock_item
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        adapter.on_item_change(callback)

        result = adapter.create_item(
            project,
            title="New Item",
            item_type="task",
            status="todo",
            priority="high"
        )

        assert result == mock_item
        callback.assert_called_once_with(item_id)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_update_item_success(self, mock_storage_class):
        """Test update_item updates item and notifies listeners."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        item_id = str(uuid4())
        mock_item = Item(id=item_id, title="Updated Item", status="done")

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_item_storage.update_item.return_value = mock_item
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        adapter.on_item_change(callback)

        result = adapter.update_item(
            project,
            item_id,
            title="Updated Item",
            status="done"
        )

        assert result == mock_item
        callback.assert_called_once_with(item_id)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_delete_item_success(self, mock_storage_class):
        """Test delete_item soft deletes item and notifies listeners."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        item_id = str(uuid4())

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        adapter.on_item_change(callback)

        adapter.delete_item(project, item_id)

        mock_item_storage.delete_item.assert_called_once_with(item_id)
        callback.assert_called_once_with(item_id)


class TestStorageAdapterLinkOperations:
    """Test link operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_list_links_success(self, mock_storage_class):
        """Test list_links returns links with filters."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        mock_link1 = Link(id=str(uuid4()), source_item_id=str(uuid4()), target_item_id=str(uuid4()))
        mock_link2 = Link(id=str(uuid4()), source_item_id=str(uuid4()), target_item_id=str(uuid4()))

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_item_storage.list_links.return_value = [mock_link1, mock_link2]
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        results = adapter.list_links(project, link_type="implements")

        assert len(results) == 2
        mock_item_storage.list_links.assert_called_once_with(
            source_id=None, target_id=None, link_type="implements"
        )

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_create_link_success(self, mock_storage_class):
        """Test create_link creates traceability link."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        source_id = str(uuid4())
        target_id = str(uuid4())
        mock_link = Link(
            id=str(uuid4()),
            source_item_id=source_id,
            target_item_id=target_id,
            link_type="tests"
        )

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_item_storage.create_link.return_value = mock_link
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        result = adapter.create_link(
            project,
            source_id,
            target_id,
            "tests",
            metadata={"coverage": "100%"}
        )

        assert result == mock_link
        mock_item_storage.create_link.assert_called_once()

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_delete_link_success(self, mock_storage_class):
        """Test delete_link deletes link."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")
        link_id = str(uuid4())

        mock_project_storage = MagicMock()
        mock_item_storage = MagicMock()
        mock_project_storage.get_item_storage.return_value = mock_item_storage
        mock_storage.get_project_storage.return_value = mock_project_storage

        adapter = StorageAdapter()
        adapter.delete_link(project, link_id)

        mock_item_storage.delete_link.assert_called_once_with(link_id)


class TestStorageAdapterSearchOperations:
    """Test search operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_search_items_success(self, mock_storage_class):
        """Test search_items performs full-text search."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_item1 = Item(id=str(uuid4()), title="Authentication Feature")
        mock_item2 = Item(id=str(uuid4()), title="Auth Tests")
        mock_storage.search_items.return_value = [mock_item1, mock_item2]

        adapter = StorageAdapter()
        results = adapter.search_items("auth", project_id="proj-123")

        assert len(results) == 2
        mock_storage.search_items.assert_called_once_with("auth", "proj-123")


class TestStorageAdapterSyncOperations:
    """Test sync operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_sync_status_with_engine(self, mock_storage_class):
        """Test get_sync_status returns status from sync engine."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_sync_engine = MagicMock()
        expected_state = SyncState(
            status=SyncStatus.SUCCESS,
            last_sync=datetime.now(),
            pending_changes=0
        )
        mock_sync_engine.get_status.return_value = expected_state

        adapter = StorageAdapter(sync_engine=mock_sync_engine)
        result = adapter.get_sync_status()

        assert result == expected_state
        mock_sync_engine.get_status.assert_called_once()

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_sync_status_without_engine(self, mock_storage_class):
        """Test get_sync_status returns default state without sync engine."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage
        mock_storage.get_sync_queue.return_value = ["item1", "item2"]

        adapter = StorageAdapter()
        result = adapter.get_sync_status()

        assert result.status == SyncStatus.IDLE
        assert result.pending_changes == 2
        assert result.last_sync is None

    @pytest.mark.asyncio
    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    async def test_trigger_sync_success(self, mock_storage_class):
        """Test trigger_sync executes sync and notifies listeners."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_sync_engine = MagicMock()
        mock_result = MagicMock(
            success=True,
            entities_synced=10,
            conflicts=[],
            errors=[],
            duration_seconds=2.5
        )
        mock_sync_engine.sync = AsyncMock(return_value=mock_result)
        mock_sync_engine.get_status.return_value = SyncState(
            status=SyncStatus.SUCCESS,
            pending_changes=0
        )

        adapter = StorageAdapter(sync_engine=mock_sync_engine)
        callback = MagicMock()
        adapter.on_sync_status_change(callback)

        result = await adapter.trigger_sync(force=True)

        assert result["success"] is True
        assert result["entities_synced"] == 10
        assert callback.call_count >= 2  # Starting and completion notifications

    @pytest.mark.asyncio
    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    async def test_trigger_sync_without_engine(self, mock_storage_class):
        """Test trigger_sync fails gracefully without sync engine."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        result = await adapter.trigger_sync()

        assert result["success"] is False
        assert "not configured" in result["error"]

    @pytest.mark.asyncio
    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    async def test_trigger_sync_error(self, mock_storage_class):
        """Test trigger_sync handles errors and notifies listeners."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_sync_engine = MagicMock()
        mock_sync_engine.sync = AsyncMock(side_effect=Exception("Network error"))

        adapter = StorageAdapter(sync_engine=mock_sync_engine)
        callback = MagicMock()
        adapter.on_sync_status_change(callback)

        result = await adapter.trigger_sync()

        assert result["success"] is False
        assert "Network error" in result["error"]
        assert callback.call_count >= 2  # Starting and error notifications

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_pending_changes_count(self, mock_storage_class):
        """Test get_pending_changes_count returns queue length."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage
        mock_storage.get_sync_queue.return_value = ["item1", "item2", "item3"]

        adapter = StorageAdapter()
        result = adapter.get_pending_changes_count()

        assert result == 3


class TestStorageAdapterConflictOperations:
    """Test conflict operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    @patch("tracertm.storage.conflict_resolver.ConflictResolver")
    def test_get_unresolved_conflicts_success(self, mock_resolver_class, mock_storage_class):
        """Test get_unresolved_conflicts returns conflicts."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_session = MagicMock()
        mock_storage.get_session.return_value = mock_session

        mock_conflict1 = MagicMock()
        mock_conflict2 = MagicMock()
        mock_resolver = MagicMock()
        mock_resolver.list_unresolved.return_value = [mock_conflict1, mock_conflict2]
        mock_resolver_class.return_value = mock_resolver

        mock_sync_engine = MagicMock()
        adapter = StorageAdapter(sync_engine=mock_sync_engine)
        results = adapter.get_unresolved_conflicts()

        assert len(results) == 2
        mock_session.close.assert_called_once()

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_unresolved_conflicts_without_engine(self, mock_storage_class):
        """Test get_unresolved_conflicts returns empty list without engine."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        results = adapter.get_unresolved_conflicts()

        assert results == []

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    @patch("tracertm.storage.conflict_resolver.ConflictResolver")
    def test_get_conflict_count(self, mock_resolver_class, mock_storage_class):
        """Test get_conflict_count returns count of conflicts."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        mock_session = MagicMock()
        mock_storage.get_session.return_value = mock_session

        mock_resolver = MagicMock()
        mock_resolver.list_unresolved.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_resolver_class.return_value = mock_resolver

        mock_sync_engine = MagicMock()
        adapter = StorageAdapter(sync_engine=mock_sync_engine)
        count = adapter.get_conflict_count()

        assert count == 3


class TestStorageAdapterStatistics:
    """Test statistics operations."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_get_project_stats(self, mock_storage_class):
        """Test get_project_stats returns comprehensive statistics."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        project = Project(id=str(uuid4()), name="Test Project")

        mock_session = MagicMock()
        mock_storage.get_session.return_value = mock_session

        # Mock query results for counts
        mock_query = MagicMock()
        # Item counts by type: epic=5, story=10, test=8, task=15, links=20
        count_values = [5, 10, 8, 15, 3, 7, 12, 8, 20]
        mock_query.filter.return_value.count.side_effect = count_values
        mock_session.query.return_value = mock_query

        adapter = StorageAdapter()
        stats = adapter.get_project_stats(project)

        assert stats["total_items"] == 38  # 5+10+8+15
        assert stats["items_by_type"]["epic"] == 5
        assert stats["items_by_type"]["story"] == 10
        assert stats["items_by_type"]["test"] == 8
        assert stats["items_by_type"]["task"] == 15
        assert stats["total_links"] == 20
        assert "items_by_status" in stats
        mock_session.close.assert_called_once()


class TestStorageAdapterReactiveCallbacks:
    """Test reactive callback system."""

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_on_sync_status_change_register(self, mock_storage_class):
        """Test on_sync_status_change registers callback."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        unregister = adapter.on_sync_status_change(callback)

        assert len(adapter._sync_status_callbacks) == 1
        assert callback in adapter._sync_status_callbacks
        assert callable(unregister)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_on_sync_status_change_unregister(self, mock_storage_class):
        """Test unregister function removes callback."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        unregister = adapter.on_sync_status_change(callback)

        unregister()

        assert len(adapter._sync_status_callbacks) == 0

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_on_conflict_detected_register(self, mock_storage_class):
        """Test on_conflict_detected registers callback."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        unregister = adapter.on_conflict_detected(callback)

        assert len(adapter._conflict_callbacks) == 1
        assert callback in adapter._conflict_callbacks

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_on_item_change_register(self, mock_storage_class):
        """Test on_item_change registers callback."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        unregister = adapter.on_item_change(callback)

        assert len(adapter._item_change_callbacks) == 1

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_notify_sync_status(self, mock_storage_class):
        """Test _notify_sync_status calls all registered callbacks."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback1 = MagicMock()
        callback2 = MagicMock()
        adapter.on_sync_status_change(callback1)
        adapter.on_sync_status_change(callback2)

        state = SyncState(status=SyncStatus.SUCCESS, pending_changes=0)
        adapter._notify_sync_status(state)

        callback1.assert_called_once_with(state)
        callback2.assert_called_once_with(state)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_notify_sync_status_handles_errors(self, mock_storage_class):
        """Test _notify_sync_status handles callback errors gracefully."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        failing_callback = MagicMock(side_effect=Exception("Callback error"))
        working_callback = MagicMock()
        adapter.on_sync_status_change(failing_callback)
        adapter.on_sync_status_change(working_callback)

        state = SyncState(status=SyncStatus.SUCCESS, pending_changes=0)
        adapter._notify_sync_status(state)

        # Both should be called despite first one failing
        failing_callback.assert_called_once()
        working_callback.assert_called_once()

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_notify_conflict(self, mock_storage_class):
        """Test _notify_conflict calls all registered callbacks."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        adapter.on_conflict_detected(callback)

        conflict = MagicMock()
        adapter._notify_conflict(conflict)

        callback.assert_called_once_with(conflict)

    @patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager")
    def test_notify_item_change(self, mock_storage_class):
        """Test _notify_item_change calls all registered callbacks."""
        mock_storage = MagicMock()
        mock_storage_class.return_value = mock_storage

        adapter = StorageAdapter()
        callback = MagicMock()
        adapter.on_item_change(callback)

        item_id = str(uuid4())
        adapter._notify_item_change(item_id)

        callback.assert_called_once_with(item_id)
