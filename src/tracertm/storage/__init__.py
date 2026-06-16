<<<<<<< HEAD
"""Tracera storage package."""
=======
"""Storage module for TracerTM."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class LocalStorageManager:
    """Simple local file storage manager for items and links."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.items_dir = base_path / "items"
        self.links_dir = base_path / "links"
        self.items_dir.mkdir(parents=True, exist_ok=True)
        self.links_dir.mkdir(parents=True, exist_ok=True)

    def save_item(self, item_id: str, data: dict[str, Any]) -> None:
        """Save an item to disk."""
        filepath = self.items_dir / f"{item_id}.json"
        with Path(filepath).open("w") as f:
            json.dump(data, f, default=str)

    def load_item(self, item_id: str) -> dict[str, Any] | None:
        """Load an item from disk."""
        filepath = self.items_dir / f"{item_id}.json"
        if filepath.exists():
            with Path(filepath).open() as f:
                return json.load(f)
        return None

    def delete_item(self, item_id: str) -> bool:
        """Delete an item from disk."""
        filepath = self.items_dir / f"{item_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def list_items(self) -> list[str]:
        """List all item IDs."""
        return [f.stem for f in self.items_dir.glob("*.json")]

    def save_link(self, link_id: str, data: dict[str, Any]) -> None:
        """Save a link to disk."""
        filepath = self.links_dir / f"{link_id}.json"
        with Path(filepath).open("w") as f:
            json.dump(data, f, default=str)

    def load_link(self, link_id: str) -> dict[str, Any] | None:
        """Load a link from disk."""
        filepath = self.links_dir / f"{link_id}.json"
        if filepath.exists():
            with Path(filepath).open() as f:
                return json.load(f)
        return None

    def delete_link(self, link_id: str) -> bool:
        """Delete a link from disk."""
        filepath = self.links_dir / f"{link_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def list_links(self) -> list[str]:
        """List all link IDs."""
        return [f.stem for f in self.links_dir.glob("*.json")]


class ChangeDetector:
    """Detect changes in storage for syncing."""

    def __init__(self, storage: LocalStorageManager):
        self.storage = storage
        self._last_sync = datetime.now()

    def detect_changes(self) -> list[dict[str, Any]]:
        """Detect items changed since last sync."""
        # Simple implementation - returns empty list
        return []

    def mark_synced(self, item_id: str) -> None:
        """Mark an item as synced."""


class SyncQueue:
    """Queue for sync operations."""


class SyncEngine:
    """Sync engine for storage."""


class SyncState:
    """Sync state enum."""

    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"


class SyncStatus:
    """Sync status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ConflictStrategy:
    """Conflict resolution strategy enum."""

    LATEST = "latest"
    MANUAL = "manual"
    LOCAL = "local"
    REMOTE = "remote"


class ConflictStatus:
    """Conflict status enum."""

    NONE = "none"
    DETECTED = "detected"
    RESOLVED = "resolved"


class EntityType:
    """Entity type enum."""

    ITEM = "item"
    LINK = "link"


class Conflict:
    """Conflict representation."""

    def __init__(self, entity_type: str, entity_id: str, local_version: Any, remote_version: Any):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.local_version = local_version
        self.remote_version = remote_version


class ConflictBackup:
    """Backup for conflict resolution."""


class ConflictResolver:
    """Resolve conflicts between local and remote."""


class VectorClock:
    """Vector clock for causal consistency."""

    def __init__(self):
        self._clock = {}

    def increment(self, node: str) -> None:
        """Increment clock for a node."""
        self._clock[node] = self._clock.get(node, 0) + 1

    def merge(self, other: "VectorClock") -> None:
        """Merge with another clock."""
        for node, value in other._clock.items():
            self._clock[node] = max(self._clock.get(node, 0), value)


class EntityVersion:
    """Entity version with vector clock."""

    def __init__(self, version: int, clock: VectorClock):
        self.version = version
        self.clock = clock


class OperationType:
    """Operation type enum for sync."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class QueuedChange:
    """Queued change for sync."""


class SyncResult:
    """Result of a sync operation."""

    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message


class SyncStateManager:
    """Manage sync state."""


class ResolvedEntity:
    """Resolved entity after conflict resolution."""
>>>>>>> c5656f5a9e2b6956447a252295042e6f2cdd1ffe

from tracertm.storage.artifact_writer import ArtifactWriter, InMemoryArtifactWriter
from tracertm.storage.trace_link_writer import TraceLinkWriter, InMemoryTraceLinkWriter

__all__ = [
    "ArtifactWriter",
    "InMemoryArtifactWriter",
    "TraceLinkWriter",
    "InMemoryTraceLinkWriter",
]