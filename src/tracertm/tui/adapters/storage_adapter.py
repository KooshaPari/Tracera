"""Storage adapter for TUI integration.

Provides a reactive interface between LocalStorageManager and Textual TUI components.
"""

import contextlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tracertm.models import Item, Link, Project
from tracertm.storage.conflict_resolver import Conflict
from tracertm.storage.local_storage import LocalStorageManager
from tracertm.storage.sync_engine import SyncEngine, SyncState, SyncStatus

logger = logging.getLogger(__name__)


@dataclass
class ItemCreateConfig:
    """Configuration for creating items."""

    external_id: str | None = None
    description: str | None = None
    status: str = "todo"
    priority: str = "medium"
    owner: str | None = None
    parent_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ItemUpdateConfig:
    """Configuration for updating items."""

    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    owner: str | None = None
    metadata: dict[str, Any] | None = None


class StorageAdapter:
    """Adapter layer between LocalStorageManager and TUI.

    Provides:
    - Reactive data access with callbacks
    - Sync status monitoring
    - Conflict notifications
    - Combined SQLite + Markdown item listings
    """

    def __init__(
        self,
        base_dir: Path | None = None,
        sync_engine: SyncEngine | None = None,
    ) -> None:
        """Initialize storage adapter.

        Args:
            base_dir: Base directory for local storage
            sync_engine: Optional sync engine for sync operations
        """
        self.storage = LocalStorageManager(base_dir)
        self.sync_engine = sync_engine

        # Callbacks for reactive updates
        self._sync_status_callbacks: list[Callable[[SyncState], None]] = []
        self._conflict_callbacks: list[Callable[[Conflict], None]] = []
        self._item_change_callbacks: list[Callable[[str], None]] = []

    # ========================================================================
    # Project Operations
    # ========================================================================

    def get_project(self, project_name: str) -> Project | None:
        """Get project by name.

        Args:
            project_name: Project name

        Returns:
            Project or None
        """
        project_storage = self.storage.get_project_storage(project_name)
        return project_storage.get_project()

    def create_project(
        self,
        name: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Project:
        """Create or update project.

        Args:
            name: Project name
            description: Project description
            metadata: Additional metadata

        Returns:
            Project instance
        """
        project_storage = self.storage.get_project_storage(name)
        return project_storage.create_or_update_project(name, description, metadata)

    # ========================================================================
    # Item Operations
    # ========================================================================

    def list_items(
        self,
        project: Project,
        item_type: str | None = None,
        status: str | None = None,
        parent_id: str | None = None,
    ) -> list[Item]:
        """List items with optional filters.

        Combines items from both SQLite and Markdown sources.

        Args:
            project: Project instance
            item_type: Filter by item type
            status: Filter by status
            parent_id: Filter by parent ID

        Returns:
            List of items
        """
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)

        # Get items from SQLite
        # tracked: https://github.com/KooshaPari/trace/issues/219
        # This would scan the markdown directories and parse frontmatter
        # For now, return SQLite items only
        return item_storage.list_items(
            item_type=item_type,
            status=status,
            parent_id=parent_id,
        )

    def get_item(self, project: Project, item_id: str) -> Item | None:
        """Get item by ID.

        Args:
            project: Project instance
            item_id: Item ID

        Returns:
            Item or None
        """
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)
        return item_storage.get_item(item_id)

    def create_item(
        self,
        project: Project,
        title: str,
        item_type: str,
        config: ItemCreateConfig | None = None,
    ) -> Item:
        """Create a new item.

        Args:
            project: Project instance
            title: Item title
            item_type: Type (epic, story, test, task)
            config: Item creation configuration

        Returns:
            Created item
        """
        cfg = config or ItemCreateConfig()
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)

        item = item_storage.create_item(
            title=title,
            item_type=item_type,
            external_id=cfg.external_id,
            description=cfg.description,
            status=cfg.status,
            priority=cfg.priority,
            owner=cfg.owner,
            parent_id=cfg.parent_id,
            metadata=cfg.metadata,
        )

        # Notify listeners
        self._notify_item_change(str(item.id))

        return item

    def update_item(
        self,
        project: Project,
        item_id: str,
        config: ItemUpdateConfig | None = None,
    ) -> Item:
        """Update an existing item.

        Args:
            project: Project instance
            item_id: Item ID
            config: Item update configuration

        Returns:
            Updated item
        """
        cfg = config or ItemUpdateConfig()
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)

        item = item_storage.update_item(
            item_id=item_id,
            title=cfg.title,
            description=cfg.description,
            status=cfg.status,
            priority=cfg.priority,
            owner=cfg.owner,
            metadata=cfg.metadata,
        )

        # Notify listeners
        self._notify_item_change(str(item.id))

        return item

    def delete_item(self, project: Project, item_id: str) -> None:
        """Delete an item (soft delete).

        Args:
            project: Project instance
            item_id: Item ID
        """
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)
        item_storage.delete_item(item_id)

        # Notify listeners
        self._notify_item_change(item_id)

    # ========================================================================
    # Link Operations
    # ========================================================================

    def list_links(
        self,
        project: Project,
        source_id: str | None = None,
        target_id: str | None = None,
        link_type: str | None = None,
    ) -> list[Link]:
        """List links with optional filters.

        Args:
            project: Project instance
            source_id: Filter by source item ID
            target_id: Filter by target item ID
            link_type: Filter by link type

        Returns:
            List of links
        """
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)

        return item_storage.list_links(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
        )

    def create_link(
        self,
        project: Project,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> Link:
        """Create a traceability link.

        Args:
            project: Project instance
            source_id: Source item ID
            target_id: Target item ID
            link_type: Link type (implements, tests, depends_on, etc.)
            metadata: Additional metadata

        Returns:
            Created link
        """
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)

        return item_storage.create_link(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            metadata=metadata,
        )

    def delete_link(self, project: Project, link_id: str) -> None:
        """Delete a link.

        Args:
            project: Project instance
            link_id: Link ID
        """
        project_storage = self.storage.get_project_storage(project.name)
        item_storage = project_storage.get_item_storage(project)
        item_storage.delete_link(link_id)

    # ========================================================================
    # Search Operations
    # ========================================================================

    def search_items(self, query: str, project_id: str | None = None) -> list[Item]:
        """Full-text search across items.

        Args:
            query: Search query
            project_id: Optional project ID filter

        Returns:
            List of matching items
        """
        return self.storage.search_items(query, project_id)

    # ========================================================================
    # Sync Operations
    # ========================================================================

    def get_sync_status(self) -> SyncState:
        """Get current sync status.

        Returns:
            SyncState object
        """
        if not self.sync_engine:
            # Return default state if no sync engine
            return SyncState(
                last_sync=None,
                pending_changes=len(self.storage.get_sync_queue()),
                status=SyncStatus.IDLE,
            )

        return self.sync_engine.get_status()

    async def trigger_sync(self, force: bool = False) -> dict[str, Any]:
        """Trigger a sync operation.

        Args:
            force: Force sync even if recently synced

        Returns:
            Sync result as dict
        """
        if not self.sync_engine:
            return {
                "success": False,
                "error": "Sync engine not configured",
            }

        # Notify listeners of sync starting
        state = SyncState(status=SyncStatus.SYNCING, pending_changes=0)
        self._notify_sync_status(state)

        try:
            result = await self.sync_engine.sync(_force=force)

            # Notify listeners of sync completion
            final_state = self.get_sync_status()
            self._notify_sync_status(final_state)

            return {
                "success": result.success,
                "entities_synced": result.entities_synced,
                "conflicts": len(result.conflicts),
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
            }

        except (ConnectionError, OSError, RuntimeError, TimeoutError, ValueError) as sync_error:
            # Notify listeners of error
            error_state = SyncState(
                status=SyncStatus.ERROR,
                last_error=str(sync_error),
                pending_changes=0,
            )
            self._notify_sync_status(error_state)

            return {
                "success": False,
                "error": str(sync_error),
            }

    def get_pending_changes_count(self) -> int:
        """Get count of pending sync changes.

        Returns:
            Number of pending changes
        """
        return len(self.storage.get_sync_queue())

    # ========================================================================
    # Conflict Operations
    # ========================================================================

    def get_unresolved_conflicts(self) -> list[Conflict]:
        """Get all unresolved conflicts.

        Returns:
            List of conflicts
        """
        if not self.sync_engine:
            return []

        # Access conflict resolver through sync engine's storage manager
        session = self.storage.get_session()
        try:
            from tracertm.storage.conflict_resolver import ConflictResolver

            resolver = ConflictResolver(session)
            return resolver.list_unresolved()
        finally:
            session.close()

    def get_conflict_count(self) -> int:
        """Get count of unresolved conflicts.

        Returns:
            Number of unresolved conflicts
        """
        return len(self.get_unresolved_conflicts())

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_project_stats(self, project: Project) -> dict[str, Any]:
        """Get statistics for a project.

        Args:
            project: Project instance

        Returns:
            Dict with statistics
        """
        session = self.storage.get_session()
        try:
            # Count items by type
            items_by_type: dict[str, int] = {}
            for item_type in ["epic", "story", "test", "task"]:
                count = (
                    session
                    .query(Item)
                    .filter(
                        Item.project_id == project.id,
                        Item.item_type == item_type,
                        Item.deleted_at.is_(None),
                    )
                    .count()
                )
                items_by_type[item_type] = count

            # Count items by status
            items_by_status: dict[str, int] = {}
            for status in ["todo", "in_progress", "done", "blocked"]:
                count = (
                    session
                    .query(Item)
                    .filter(
                        Item.project_id == project.id,
                        Item.status == status,
                        Item.deleted_at.is_(None),
                    )
                    .count()
                )
                items_by_status[status] = count

            # Count links
            total_links = session.query(Link).filter(Link.project_id == project.id).count()

            return {
                "total_items": sum(items_by_type.values()),
                "items_by_type": items_by_type,
                "items_by_status": items_by_status,
                "total_links": total_links,
            }
        finally:
            session.close()

    # ========================================================================
    # Reactive Callbacks
    # ========================================================================

    def on_sync_status_change(self, callback: Callable[[SyncState], None]) -> Callable[[], None]:
        """Register callback for sync status changes.

        Args:
            callback: Callback function that receives SyncState

        Returns:
            Unregister function
        """
        self._sync_status_callbacks.append(callback)

        def unregister() -> None:
            self._sync_status_callbacks.remove(callback)

        return unregister

    def on_conflict_detected(self, callback: Callable[[Conflict], None]) -> Callable[[], None]:
        """Register callback for conflict detection.

        Args:
            callback: Callback function that receives Conflict

        Returns:
            Unregister function
        """
        self._conflict_callbacks.append(callback)

        def unregister() -> None:
            self._conflict_callbacks.remove(callback)

        return unregister

    def on_item_change(self, callback: Callable[[str], None]) -> Callable[[], None]:
        """Register callback for item changes.

        Args:
            callback: Callback function that receives item ID

        Returns:
            Unregister function
        """
        self._item_change_callbacks.append(callback)

        def unregister() -> None:
            self._item_change_callbacks.remove(callback)

        return unregister

    def _notify_sync_status(self, state: SyncState) -> None:
        """Notify all sync status listeners."""
        for callback in self._sync_status_callbacks:
            try:
                callback(state)
            except RuntimeError as error:
                # App may be shutting down; continue notifying remaining listeners.
                logger.debug("Ignoring sync status callback runtime error: %s", error)

    def _notify_conflict(self, conflict: Conflict) -> None:
        """Notify all conflict listeners."""
        for callback in self._conflict_callbacks:
            with contextlib.suppress(RuntimeError):
                callback(conflict)

    def _notify_item_change(self, item_id: str) -> None:
        """Notify all item change listeners."""
        for callback in self._item_change_callbacks:
            with contextlib.suppress(RuntimeError):
                callback(item_id)
