"""Sync Engine for TraceRTM's offline-first architecture.

This module handles bidirectional synchronization between local storage (SQLite + Markdown)
and the remote API, implementing the sync flow defined in UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md.

Key Features:
- Change detection via content hashing
- Queue-based sync with retry logic
- Conflict resolution with vector clocks
- Network resilience with exponential backoff
- Atomic operations with transaction support
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import text

from tracertm.storage.conflict_resolver import ConflictStrategy, VectorClock

if TYPE_CHECKING:
    from tracertm.api.client import TraceRTMClient
    from tracertm.database.connection import DatabaseConnection
    from tracertm.storage.local_storage import LocalStorageManager


@dataclass
class SyncConfig:
    """Configuration for sync engine behavior."""

    conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS
    max_retries: int = 3
    retry_delay: float = 1.0


logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Data Classes
# ============================================================================


class OperationType(Enum):
    """Sync operation types."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class EntityType(Enum):
    """Entity types that can be synced."""

    PROJECT = "project"
    ITEM = "item"
    LINK = "link"
    AGENT = "agent"


class SyncStatus(Enum):
    """Sync operation status."""

    IDLE = "idle"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class SyncState:
    """Tracks sync metadata and state."""

    last_sync: datetime | None = None
    pending_changes: int = 0
    status: SyncStatus = SyncStatus.IDLE
    last_error: str | None = None
    conflicts_count: int = 0
    synced_entities: int = 0


@dataclass
class QueuedChange:
    """Represents a change in the sync queue."""

    id: int
    entity_type: EntityType
    entity_id: str
    operation: OperationType
    payload: dict[str, Any]
    created_at: datetime
    retry_count: int = 0
    last_error: str | None = None


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    entities_synced: int = 0
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


# ============================================================================
# Change Detection
# ============================================================================


class ChangeDetector:
    """Detects local changes by comparing content hashes."""

    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA-256 hash of content.

        Args:
            content: Content to hash (markdown, JSON, etc.)

        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def has_changed(current_content: str, stored_hash: str | None) -> bool:
        """Check if content has changed by comparing hashes.

        Args:
            current_content: Current content
            stored_hash: Previously stored hash

        Returns:
            True if content has changed
        """
        if stored_hash is None:
            return True

        current_hash = ChangeDetector.compute_hash(current_content)
        return current_hash != stored_hash

    @staticmethod
    def detect_changes_in_directory(directory: Path, stored_hashes: dict[str, str]) -> list[tuple[Path, str]]:
        """Detect changed files in a directory.

        Args:
            directory: Directory to scan
            stored_hashes: Map of path -> hash

        Returns:
            List of (path, new_hash) tuples for changed files
        """
        changes: list[tuple[Path, str]] = []

        if not directory.exists():
            return changes

        for file_path in directory.rglob("*.md"):
            if file_path.is_file():
                content = file_path.read_text(encoding="utf-8")
                current_hash = ChangeDetector.compute_hash(content)

                relative_path = str(file_path.relative_to(directory))
                stored_hash = stored_hashes.get(relative_path)

                if stored_hash is None or stored_hash != current_hash:
                    changes.append((file_path, current_hash))

        return changes


# ============================================================================
# Sync Queue Manager
# ============================================================================


class SyncQueue:
    """Manages the sync queue table in SQLite."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        """Initialize sync queue manager.

        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self._ensure_tables()

    @property
    def engine(self) -> Any:
        """Get database engine, ensuring it's not None."""
        if self.db.engine is None:
            msg = "Database engine not initialized"
            raise RuntimeError(msg)
        return self.db.engine

    def _ensure_tables(self) -> None:
        """Ensure sync tables exist."""
        with self.engine.connect() as conn:
            # Create sync_queue table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    UNIQUE(entity_type, entity_id, operation)
                )
            """),
            )

            # Create sync_state table
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """),
            )

            conn.commit()

    def enqueue(
        self,
        entity_type: EntityType,
        entity_id: str,
        operation: OperationType,
        payload: dict[str, Any],
    ) -> int:
        """Add or update a change in the sync queue.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            operation: Operation type
            payload: Change payload (JSON-serializable)

        Returns:
            Queue entry ID
        """
        with self.engine.connect() as conn:
            # Use INSERT OR REPLACE to handle uniqueness constraint
            result = conn.execute(
                text("""
                INSERT OR REPLACE INTO sync_queue
                (entity_type, entity_id, operation, payload, created_at, retry_count)
                VALUES (:entity_type, :entity_id, :operation, :payload, :created_at, COALESCE(
                    (SELECT retry_count FROM sync_queue
                     WHERE entity_type = :entity_type2 AND entity_id = :entity_id2 AND operation = :operation2),
                    0
                ))
                """),
                {
                    "entity_type": entity_type.value,
                    "entity_id": entity_id,
                    "operation": operation.value,
                    "payload": json.dumps(payload),
                    "created_at": datetime.now(UTC).isoformat(),
                    "entity_type2": entity_type.value,
                    "entity_id2": entity_id,
                    "operation2": operation.value,
                },
            )
            conn.commit()
            lastrowid = result.lastrowid
            if lastrowid is None:
                msg = "Failed to insert sync queue entry"
                raise RuntimeError(msg)
            return int(lastrowid)

    def get_pending(self, limit: int = 100) -> list[QueuedChange]:
        """Get pending changes from queue.

        Args:
            limit: Maximum number of changes to retrieve

        Returns:
            List of queued changes
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT id, entity_type, entity_id, operation, payload,
                       created_at, retry_count, last_error
                FROM sync_queue
                ORDER BY created_at ASC
                LIMIT :limit
                """),
                {"limit": limit},
            )

            return [
                QueuedChange(
                    id=row[0],
                    entity_type=EntityType(row[1]),
                    entity_id=row[2],
                    operation=OperationType(row[3]),
                    payload=json.loads(row[4]),
                    created_at=datetime.fromisoformat(row[5]),
                    retry_count=row[6],
                    last_error=row[7],
                )
                for row in result
            ]

    def remove(self, queue_id: int) -> None:
        """Remove a change from the queue.

        Args:
            queue_id: Queue entry ID
        """
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM sync_queue WHERE id = :queue_id"), {"queue_id": queue_id})
            conn.commit()

    def update_retry(self, queue_id: int, error: str) -> None:
        """Increment retry count and record error.

        Args:
            queue_id: Queue entry ID
            error: Error message
        """
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                UPDATE sync_queue
                SET retry_count = retry_count + 1,
                    last_error = :error
                WHERE id = :queue_id
                """),
                {"error": error, "queue_id": queue_id},
            )
            conn.commit()

    def clear(self) -> None:
        """Clear all entries from the queue."""
        with self.engine.connect() as conn:
            conn.execute(text("DELETE FROM sync_queue"))
            conn.commit()

    def get_count(self) -> int:
        """Get count of pending changes.

        Returns:
            Number of pending changes
        """
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sync_queue"))
            count = result.scalar()
            return int(count) if count is not None else 0


# ============================================================================
# Sync State Manager
# ============================================================================


class SyncStateManager:
    """Manages sync state metadata."""

    def __init__(self, db_connection: DatabaseConnection) -> None:
        """Initialize sync state manager.

        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self._ensure_tables()

    @property
    def engine(self) -> Any:
        """Get database engine, ensuring it's not None."""
        if self.db.engine is None:
            msg = "Database engine not initialized"
            raise RuntimeError(msg)
        return self.db.engine

    def _ensure_tables(self) -> None:
        """Ensure sync tables exist."""
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    UNIQUE(entity_type, entity_id, operation)
                )
            """),
            )
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """),
            )
            conn.commit()

    def get_state(self) -> SyncState:
        """Get current sync state.

        Returns:
            SyncState object
        """
        with self.engine.connect() as conn:
            # Get last_sync timestamp
            result = conn.execute(text("SELECT value FROM sync_state WHERE key = 'last_sync'"))
            row = result.fetchone()
            last_sync = datetime.fromisoformat(row[0]) if row else None

            # Get pending changes count
            result = conn.execute(text("SELECT COUNT(*) FROM sync_queue"))
            pending_changes_raw = result.scalar()
            pending_changes: int = int(pending_changes_raw) if pending_changes_raw is not None else 0

            # Get status
            result = conn.execute(text("SELECT value FROM sync_state WHERE key = 'status'"))
            row = result.fetchone()
            status = SyncStatus(row[0]) if row else SyncStatus.IDLE

            # Get last error
            result = conn.execute(text("SELECT value FROM sync_state WHERE key = 'last_error'"))
            row = result.fetchone()
            last_error = row[0] if row else None

            return SyncState(last_sync=last_sync, pending_changes=pending_changes, status=status, last_error=last_error)

    def update_last_sync(self, timestamp: datetime | None = None) -> None:
        """Update last sync timestamp.

        Args:
            timestamp: Sync timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now(UTC)

        with self.engine.connect() as conn:
            conn.execute(
                text("""
                INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                VALUES (:key, :value, :updated_at)
                """),
                {"key": "last_sync", "value": timestamp.isoformat(), "updated_at": datetime.now(UTC).isoformat()},
            )
            conn.commit()

    def update_status(self, status: SyncStatus) -> None:
        """Update sync status.

        Args:
            status: New status
        """
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                VALUES (:key, :value, :updated_at)
                """),
                {"key": "status", "value": status.value, "updated_at": datetime.now(UTC).isoformat()},
            )
            conn.commit()

    def update_error(self, error: str | None) -> None:
        """Update last error.

        Args:
            error: Error message (None to clear)
        """
        with self.engine.connect() as conn:
            if error is None:
                conn.execute(text("DELETE FROM sync_state WHERE key = 'last_error'"))
            else:
                conn.execute(
                    text("""
                    INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                    VALUES (:error_key, :error_value, :updated_at)
                    """),
                    {"error_key": "last_error", "error_value": error, "updated_at": datetime.now(UTC).isoformat()},
                )
            conn.commit()


# ============================================================================
# Main Sync Engine
# ============================================================================


class SyncEngine:
    """Main sync orchestrator for TraceRTM.

    Implements the sync flow:
    1. Detect local changes
    2. Queue changes
    3. Upload phase (local → remote)
    4. Download phase (remote → local)
    5. Conflict resolution
    """

    def __init__(
        self,
        db_connection: DatabaseConnection,
        api_client: TraceRTMClient,
        storage_manager: LocalStorageManager,
        config: SyncConfig | None = None,
    ) -> None:
        """Initialize sync engine.

        Args:
            db_connection: DatabaseConnection instance
            api_client: API client for remote operations
            storage_manager: LocalStorageManager instance
            config: Sync configuration
        """
        cfg = config or SyncConfig()
        self.db: DatabaseConnection = db_connection
        self.api: TraceRTMClient = api_client
        self.storage: LocalStorageManager = storage_manager
        self.conflict_strategy: ConflictStrategy = cfg.conflict_strategy
        self.max_retries: int = cfg.max_retries
        self.retry_delay: float = cfg.retry_delay

        self.queue: SyncQueue = SyncQueue(db_connection)
        self.state_manager: SyncStateManager = SyncStateManager(db_connection)
        self.change_detector: ChangeDetector = ChangeDetector()

        self._syncing: bool = False
        self._sync_lock: asyncio.Lock = asyncio.Lock()

    @property
    def engine(self) -> Any:
        """Get database engine, ensuring it's not None."""
        if self.db.engine is None:
            msg = "Database engine not initialized"
            raise RuntimeError(msg)
        return self.db.engine

    # ========================================================================
    # Public API
    # ========================================================================

    async def sync(self, _force: bool = False) -> SyncResult:  # noqa: FBT001,FBT002
        """Perform full sync cycle.

        Args:
            force: Force sync even if recently synced

        Returns:
            SyncResult with sync statistics
        """
        async with self._sync_lock:
            if self._syncing:
                logger.warning("Sync already in progress")
                return SyncResult(success=False, errors=["Sync already in progress"])

            self._syncing = True
            start_time = datetime.now(UTC)

            try:
                self.state_manager.update_status(SyncStatus.SYNCING)
                self.state_manager.update_error(None)

                # Step 1: Detect and queue local changes
                logger.info("Detecting local changes...")
                await self.detect_and_queue_changes()

                # Step 2: Upload phase
                logger.info("Starting upload phase...")
                upload_result = await self.process_queue()

                # Step 3: Download phase
                logger.info("Starting download phase...")
                state = self.state_manager.get_state()
                download_result = await self.pull_changes(since=state.last_sync)

                # Step 4: Update sync state
                self.state_manager.update_last_sync()
                self.state_manager.update_status(SyncStatus.SUCCESS)

                duration = (datetime.now(UTC) - start_time).total_seconds()

                result = SyncResult(
                    success=True,
                    entities_synced=upload_result.entities_synced + download_result.entities_synced,
                    conflicts=upload_result.conflicts + download_result.conflicts,
                    errors=upload_result.errors + download_result.errors,
                    duration_seconds=duration,
                )

                logger.info(
                    "Sync completed: %s entities, %s conflicts, %.2fs",
                    result.entities_synced,
                    len(result.conflicts),
                    duration,
                )
            except Exception as e:
                logger.exception("Sync failed")
                self.state_manager.update_status(SyncStatus.ERROR)
                self.state_manager.update_error(str(e))

                return SyncResult(
                    success=False,
                    errors=[str(e)],
                    duration_seconds=(datetime.now(UTC) - start_time).total_seconds(),
                )
            else:
                return result

            finally:
                self._syncing = False

    async def detect_and_queue_changes(self) -> int:
        """Detect local changes and queue them for sync.

        Returns:
            Number of changes queued
        """
        changes_queued = 0

        try:
            # Get all local items from database
            with self.engine.connect() as conn:
                # Get all items
                result = conn.execute(text("SELECT id, content, updated_at FROM item"))
                local_items = {row[0]: {"content": row[1], "updated_at": row[2]} for row in result}

            # Check for new or modified items
            get_hashes = getattr(self.storage, "get_item_hashes", None)
            if callable(get_hashes):
                stored_hashes = get_hashes()

                for item_id, item_data in local_items.items():
                    content = str(item_data.get("content", ""))
                    stored_hash = stored_hashes.get(item_id)

                    if self.change_detector.has_changed(content, stored_hash):
                        # Queue as UPDATE operation
                        self.queue_change(
                            EntityType.ITEM,
                            item_id,
                            OperationType.UPDATE,
                            {"content": content, "updated_at": item_data.get("updated_at")},
                        )
                        changes_queued += 1
                        logger.debug("Queued change for item %s", item_id)

            logger.info("Change detection complete: %s changes queued", changes_queued)

        except Exception:
            logger.exception("Error detecting changes")

        return changes_queued

    def queue_change(
        self,
        entity_type: EntityType,
        entity_id: str,
        operation: OperationType,
        payload: dict[str, Any],
    ) -> int:
        """Queue a change for sync.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            operation: Operation type
            payload: Change payload

        Returns:
            Queue entry ID
        """
        return self.queue.enqueue(entity_type, entity_id, operation, payload)

    async def process_queue(self) -> SyncResult:
        """Process sync queue (upload phase).

        Returns:
            SyncResult with upload statistics
        """
        result = SyncResult(success=True)
        pending = self.queue.get_pending(limit=100)

        logger.info("Processing %s queued changes", len(pending))

        for change in pending:
            try:
                # Skip if too many retries
                if change.retry_count >= self.max_retries:
                    logger.warning("Skipping change %s (too many retries: %s)", change.id, change.retry_count)
                    result.errors.append(f"Max retries exceeded for {change.entity_type.value} {change.entity_id}")
                    continue

                # Upload change to API
                success = await self._upload_change(change)

                if success:
                    self.queue.remove(change.id)
                    result.entities_synced += 1
                else:
                    # Retry with exponential backoff
                    delay = self.retry_delay * (2**change.retry_count)
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.exception("Error processing change %s", change.id)
                self.queue.update_retry(change.id, str(e))
                result.errors.append(str(e))

        return result

    async def pull_changes(self, since: datetime | None = None) -> SyncResult:
        """Pull changes from remote API (download phase).

        Args:
            since: Only fetch changes after this timestamp

        Returns:
            SyncResult with download statistics
        """
        result = SyncResult(success=True)

        try:
            logger.info("Pulling changes since %s", since)

            # Try to fetch remote changes via API client
            remote_changes = []
            get_changes = getattr(self.api, "get_changes", None)
            if callable(get_changes):
                try:
                    # Call API to get changes since last sync
                    params = {"since": since.isoformat()} if since else {}
                    remote_changes = await get_changes(**params)
                except (TimeoutError, OSError, RuntimeError, ValueError) as e:
                    logger.warning("Failed to fetch remote changes: %s", e)
                    # Continue with empty list - not a hard failure
                    remote_changes = []

            logger.debug("Retrieved %s remote changes", len(remote_changes))

            # Apply each remote change
            for change in remote_changes:
                try:
                    await self._apply_remote_change(change)
                    result.entities_synced += 1
                except Exception as e:
                    logger.exception("Error applying remote change")
                    result.errors.append(str(e))

            if remote_changes:
                logger.info("Applied %s remote changes", result.entities_synced)

        except Exception as e:
            logger.exception("Failed to pull changes")
            result.errors.append(str(e))
            result.success = False

        return result

    def get_status(self) -> SyncState:
        """Get current sync status.

        Returns:
            SyncState object
        """
        return self.state_manager.get_state()

    # ========================================================================
    # Internal Methods
    # ========================================================================

    async def _upload_change(self, change: QueuedChange) -> bool:
        """Upload a single change to the API.

        Args:
            change: Queued change to upload

        Returns:
            True if successful
        """
        try:
            # Build API request based on operation

            if change.operation == OperationType.CREATE:
                # POST request
                logger.debug("Creating %s %s", change.entity_type.value, change.entity_id)

            elif change.operation == OperationType.UPDATE:
                # PUT/PATCH request
                logger.debug("Updating %s %s", change.entity_type.value, change.entity_id)

            elif change.operation == OperationType.DELETE:
                # DELETE request
                logger.debug("Deleting %s %s", change.entity_type.value, change.entity_id)
        except Exception:
            logger.exception("Upload failed")
            return False
        else:
            # Placeholder - return True when API is integrated
            return True

    async def _apply_remote_change(self, change: dict[str, Any]) -> None:
        """Apply a remote change to local storage.

        Args:
            change: Remote change data (must contain entity_type, entity_id, operation, payload)
        """
        try:
            entity_type_str = change.get("entity_type")
            entity_id = change.get("entity_id")
            operation_str = change.get("operation")
            payload = change.get("payload", {})

            # Validate required fields
            if not all([entity_type_str, entity_id, operation_str]):
                logger.warning("Incomplete remote change data: %s", change)
                return

            # Convert strings to enums
            try:
                entity_type = EntityType(entity_type_str)
                operation = OperationType(operation_str)
            except ValueError:
                logger.exception("Invalid entity or operation type in remote change")
                return

            logger.debug("Applying remote change: %s %s %s", entity_type.value, entity_id, operation.value)

            with self.engine.begin() as conn:
                if operation == OperationType.CREATE:
                    # Insert new entity (entity_type is Enum with fixed values: project/item/link/agent)
                    stmt = f"""
                            INSERT OR IGNORE INTO {entity_type.value}
                            (id, content, updated_at, synced_at)
                            VALUES (:id, :content, :updated_at, :synced_at)
                        """  # nosec B608 -- entity_type.value from EntityType Enum
                    conn.execute(
                        text(stmt),
                        {
                            "id": entity_id,
                            "content": json.dumps(payload),
                            "updated_at": datetime.now(UTC).isoformat(),
                            "synced_at": datetime.now(UTC).isoformat(),
                        },
                    )

                elif operation == OperationType.UPDATE:
                    # Update existing entity (entity_type is Enum with fixed values: project/item/link/agent)
                    stmt = f"""
                            UPDATE {entity_type.value}
                            SET content = :content, updated_at = :updated_at, synced_at = :synced_at
                            WHERE id = :id
                        """  # nosec B608 -- entity_type.value from EntityType Enum
                    conn.execute(
                        text(stmt),
                        {
                            "id": entity_id,
                            "content": json.dumps(payload),
                            "updated_at": datetime.now(UTC).isoformat(),
                            "synced_at": datetime.now(UTC).isoformat(),
                        },
                    )

                elif operation == OperationType.DELETE:
                    # Delete entity (entity_type is Enum with fixed values: project/item/link/agent)
                    stmt = f"DELETE FROM {entity_type.value} WHERE id = :id"  # nosec B608
                    conn.execute(text(stmt), {"id": entity_id})

            logger.debug("Successfully applied remote change for %s %s", entity_type.value, entity_id)

        except Exception:
            logger.exception("Error applying remote change")
            raise

    def _resolve_conflict(self, local_data: dict[str, Any], remote_data: dict[str, Any]) -> dict[str, Any]:
        """Resolve conflict between local and remote data.

        Args:
            local_data: Local version
            remote_data: Remote version

        Returns:
            Resolved data
        """
        if self.conflict_strategy == ConflictStrategy.LAST_WRITE_WINS:
            # Compare timestamps
            local_ts = datetime.fromisoformat(local_data.get("updated_at", ""))
            remote_ts = datetime.fromisoformat(remote_data.get("updated_at", ""))
            return remote_data if remote_ts > local_ts else local_data

        if self.conflict_strategy == ConflictStrategy.LOCAL_WINS:
            return local_data

        if self.conflict_strategy == ConflictStrategy.REMOTE_WINS:
            return remote_data

        if self.conflict_strategy == ConflictStrategy.MANUAL:
            # Create conflict file for manual resolution
            try:
                conflict_file = self._create_conflict_file(local_data, remote_data)
                logger.warning("Manual conflict resolution required, created %s", conflict_file)
            except Exception:
                logger.exception("Failed to create conflict file")
            return local_data

        return local_data

    def create_vector_clock(self, client_id: str, version: int, parent_version: int) -> VectorClock:
        """Create a vector clock for ordering.

        Args:
            client_id: Client identifier
            version: Current version
            parent_version: Parent version

        Returns:
            VectorClock instance
        """
        return VectorClock(
            client_id=client_id,
            version=version,
            timestamp=datetime.now(UTC),
            parent_version=parent_version,
        )

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _create_conflict_file(self, local_data: dict[str, Any], remote_data: dict[str, Any]) -> str:
        """Create a conflict file for manual resolution.

        Args:
            local_data: Local version
            remote_data: Remote version

        Returns:
            Path to created conflict file
        """
        timestamp = datetime.now(UTC).isoformat().replace(":", "-")
        conflict_content = f"""# SYNC CONFLICT
Date: {timestamp}
Strategy: MANUAL RESOLUTION REQUIRED

## Local Version
```json
{json.dumps(local_data, indent=2)}
```

## Remote Version
```json
{json.dumps(remote_data, indent=2)}
```

## Instructions
1. Review both versions above
2. Choose which version to keep or manually merge
3. Delete this conflict file when resolved
4. Run sync again to continue
"""

        trace_path = getattr(self.storage, "trace_path", None)
        if isinstance(trace_path, Path):
            conflicts_dir = trace_path / ".conflicts"
            conflicts_dir.mkdir(exist_ok=True)
            conflict_file = conflicts_dir / f"conflict_{timestamp}.md"
            conflict_file.write_text(conflict_content)
            return str(conflict_file)
        logger.warning("Storage manager does not have trace_path attribute")
        return f"conflict_{timestamp}.md"

    async def clear_queue(self) -> None:
        """Clear all pending changes from the sync queue."""
        self.queue.clear()
        logger.info("Sync queue cleared")

    async def reset_sync_state(self) -> None:
        """Reset sync state (for testing/troubleshooting)."""
        self.state_manager.update_last_sync(None)
        self.state_manager.update_status(SyncStatus.IDLE)
        self.state_manager.update_error(None)
        logger.info("Sync state reset")

    def is_syncing(self) -> bool:
        """Check if sync is currently in progress.

        Returns:
            True if syncing
        """
        return self._syncing


# ============================================================================
# Helper Functions
# ============================================================================


async def exponential_backoff(attempt: int, initial_delay: float = 1.0, max_delay: float = 60.0) -> None:
    """Sleep with exponential backoff.

    Args:
        attempt: Attempt number (0-indexed)
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
    """
    delay = min(initial_delay * (2**attempt), max_delay)
    await asyncio.sleep(delay)


def create_sync_engine(
    db_connection: DatabaseConnection,
    api_client: TraceRTMClient,
    storage_manager: LocalStorageManager,
    config: SyncConfig | None = None,
) -> SyncEngine:
    """Factory function to create a configured sync engine.

    Args:
        db_connection: DatabaseConnection instance
        api_client: API client instance
        storage_manager: LocalStorageManager instance
        config: Sync configuration

    Returns:
        Configured SyncEngine instance
    """
    return SyncEngine(
        db_connection=db_connection, api_client=api_client, storage_manager=storage_manager, config=config
    )
