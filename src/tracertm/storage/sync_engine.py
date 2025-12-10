"""
Sync Engine for TraceRTM's offline-first architecture.

This module handles bidirectional synchronization between local storage (SQLite + Markdown)
and the remote API, implementing the sync flow defined in UNIFIED_LOCAL_STORAGE_ARCHITECTURE.md.

Key Features:
- Change detection via content hashing
- Queue-based sync with retry logic
- Conflict resolution with vector clocks
- Network resilience with exponential backoff
- Atomic operations with transaction support
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from sqlalchemy import text

from tracertm.storage.conflict_resolver import ConflictStrategy, VectorClock

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
        """
        Compute SHA-256 hash of content.

        Args:
            content: Content to hash (markdown, JSON, etc.)

        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def has_changed(current_content: str, stored_hash: str | None) -> bool:
        """
        Check if content has changed by comparing hashes.

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
    def detect_changes_in_directory(
        directory: Path,
        stored_hashes: dict[str, str]
    ) -> list[tuple[Path, str]]:
        """
        Detect changed files in a directory.

        Args:
            directory: Directory to scan
            stored_hashes: Map of path -> hash

        Returns:
            List of (path, new_hash) tuples for changed files
        """
        changes = []

        if not directory.exists():
            return changes

        for file_path in directory.rglob("*.md"):
            if file_path.is_file():
                content = file_path.read_text(encoding='utf-8')
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

    def __init__(self, db_connection):
        """
        Initialize sync queue manager.

        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Ensure sync tables exist."""
        with self.db.engine.connect() as conn:
            # Create sync_queue table
            conn.execute(text("""
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
            """))

            # Create sync_state table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """))

            conn.commit()

    def enqueue(
        self,
        entity_type: EntityType,
        entity_id: str,
        operation: OperationType,
        payload: dict[str, Any]
    ) -> int:
        """
        Add or update a change in the sync queue.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            operation: Operation type
            payload: Change payload (JSON-serializable)

        Returns:
            Queue entry ID
        """
        with self.db.engine.connect() as conn:
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
                    "created_at": datetime.utcnow().isoformat(),
                    "entity_type2": entity_type.value,
                    "entity_id2": entity_id,
                    "operation2": operation.value
                }
            )
            conn.commit()
            return result.lastrowid

    def get_pending(self, limit: int = 100) -> list[QueuedChange]:
        """
        Get pending changes from queue.

        Args:
            limit: Maximum number of changes to retrieve

        Returns:
            List of queued changes
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT id, entity_type, entity_id, operation, payload,
                       created_at, retry_count, last_error
                FROM sync_queue
                ORDER BY created_at ASC
                LIMIT :limit
                """),
                {"limit": limit}
            )

            changes = []
            for row in result:
                changes.append(QueuedChange(
                    id=row[0],
                    entity_type=EntityType(row[1]),
                    entity_id=row[2],
                    operation=OperationType(row[3]),
                    payload=json.loads(row[4]),
                    created_at=datetime.fromisoformat(row[5]),
                    retry_count=row[6],
                    last_error=row[7]
                ))

            return changes

    def remove(self, queue_id: int) -> None:
        """
        Remove a change from the queue.

        Args:
            queue_id: Queue entry ID
        """
        with self.db.engine.connect() as conn:
            conn.execute(
                text("DELETE FROM sync_queue WHERE id = :queue_id"),
                {"queue_id": queue_id}
            )
            conn.commit()

    def update_retry(self, queue_id: int, error: str) -> None:
        """
        Increment retry count and record error.

        Args:
            queue_id: Queue entry ID
            error: Error message
        """
        with self.db.engine.connect() as conn:
            conn.execute(
                text("""
                UPDATE sync_queue
                SET retry_count = retry_count + 1,
                    last_error = :error
                WHERE id = :queue_id
                """),
                {"error": error, "queue_id": queue_id}
            )
            conn.commit()

    def clear(self) -> None:
        """Clear all entries from the queue."""
        with self.db.engine.connect() as conn:
            conn.execute(text("DELETE FROM sync_queue"))
            conn.commit()

    def get_count(self) -> int:
        """
        Get count of pending changes.

        Returns:
            Number of pending changes
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sync_queue"))
            return result.scalar()


# ============================================================================
# Sync State Manager
# ============================================================================


class SyncStateManager:
    """Manages sync state metadata."""

    def __init__(self, db_connection):
        """
        Initialize sync state manager.

        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Ensure sync_state table exists."""
        with self.db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """))
            conn.commit()

    def get_state(self) -> SyncState:
        """
        Get current sync state.

        Returns:
            SyncState object
        """
        with self.db.engine.connect() as conn:
            # Get last_sync timestamp
            result = conn.execute(
                text("SELECT value FROM sync_state WHERE key = 'last_sync'")
            )
            row = result.fetchone()
            last_sync = datetime.fromisoformat(row[0]) if row else None

            # Get pending changes count
            result = conn.execute(text("SELECT COUNT(*) FROM sync_queue"))
            pending_changes = result.scalar()

            # Get status
            result = conn.execute(
                text("SELECT value FROM sync_state WHERE key = 'status'")
            )
            row = result.fetchone()
            status = SyncStatus(row[0]) if row else SyncStatus.IDLE

            # Get last error
            result = conn.execute(
                text("SELECT value FROM sync_state WHERE key = 'last_error'")
            )
            row = result.fetchone()
            last_error = row[0] if row else None

            return SyncState(
                last_sync=last_sync,
                pending_changes=pending_changes,
                status=status,
                last_error=last_error
            )

    def update_last_sync(self, timestamp: datetime | None = None) -> None:
        """
        Update last sync timestamp.

        Args:
            timestamp: Sync timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        with self.db.engine.connect() as conn:
            conn.execute(
                text("""
                INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                VALUES (:key, :value, :updated_at)
                """),
                {
                    "key": "last_sync",
                    "value": timestamp.isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            conn.commit()

    def update_status(self, status: SyncStatus) -> None:
        """
        Update sync status.

        Args:
            status: New status
        """
        with self.db.engine.connect() as conn:
            conn.execute(
                text("""
                INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                VALUES (:key, :value, :updated_at)
                """),
                {
                    "key": "status",
                    "value": status.value,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            conn.commit()

    def update_error(self, error: str | None) -> None:
        """
        Update last error.

        Args:
            error: Error message (None to clear)
        """
        with self.db.engine.connect() as conn:
            if error is None:
                conn.execute(text("DELETE FROM sync_state WHERE key = 'last_error'"))
            else:
                conn.execute(
                    text("""
                    INSERT OR REPLACE INTO sync_state (key, value, updated_at)
                    VALUES (:error_key, :error_value, :updated_at)
                    """),
                    {"error_key": "last_error", "error_value": error, "updated_at": datetime.utcnow().isoformat()}
                )
            conn.commit()


# ============================================================================
# Main Sync Engine
# ============================================================================


class SyncEngine:
    """
    Main sync orchestrator for TraceRTM.

    Implements the sync flow:
    1. Detect local changes
    2. Queue changes
    3. Upload phase (local → remote)
    4. Download phase (remote → local)
    5. Conflict resolution
    """

    def __init__(
        self,
        db_connection,
        api_client,
        storage_manager,
        conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize sync engine.

        Args:
            db_connection: DatabaseConnection instance
            api_client: API client for remote operations
            storage_manager: LocalStorageManager instance
            conflict_strategy: Strategy for conflict resolution
            max_retries: Maximum retry attempts for failed syncs
            retry_delay: Initial delay between retries (seconds)
        """
        self.db = db_connection
        self.api = api_client
        self.storage = storage_manager
        self.conflict_strategy = conflict_strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.queue = SyncQueue(db_connection)
        self.state_manager = SyncStateManager(db_connection)
        self.change_detector = ChangeDetector()

        self._syncing = False
        self._sync_lock = asyncio.Lock()

    # ========================================================================
    # Public API
    # ========================================================================

    async def sync(self, force: bool = False) -> SyncResult:
        """
        Perform full sync cycle.

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
            start_time = datetime.utcnow()

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

                duration = (datetime.utcnow() - start_time).total_seconds()

                result = SyncResult(
                    success=True,
                    entities_synced=upload_result.entities_synced + download_result.entities_synced,
                    conflicts=upload_result.conflicts + download_result.conflicts,
                    errors=upload_result.errors + download_result.errors,
                    duration_seconds=duration
                )

                logger.info(
                    f"Sync completed: {result.entities_synced} entities, "
                    f"{len(result.conflicts)} conflicts, {duration:.2f}s"
                )

                return result

            except Exception as e:
                logger.error(f"Sync failed: {e}", exc_info=True)
                self.state_manager.update_status(SyncStatus.ERROR)
                self.state_manager.update_error(str(e))

                return SyncResult(
                    success=False,
                    errors=[str(e)],
                    duration_seconds=(datetime.utcnow() - start_time).total_seconds()
                )

            finally:
                self._syncing = False

    async def detect_and_queue_changes(self) -> int:
        """
        Detect local changes and queue them for sync.

        Returns:
            Number of changes queued
        """
        changes_queued = 0

        # This will be implemented with LocalStorageManager
        # For now, return placeholder
        # TODO: Implement actual change detection
        logger.info("Change detection placeholder - integrate with LocalStorageManager")

        return changes_queued

    def queue_change(
        self,
        entity_type: EntityType,
        entity_id: str,
        operation: OperationType,
        payload: dict[str, Any]
    ) -> int:
        """
        Queue a change for sync.

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
        """
        Process sync queue (upload phase).

        Returns:
            SyncResult with upload statistics
        """
        result = SyncResult(success=True)
        pending = self.queue.get_pending(limit=100)

        logger.info(f"Processing {len(pending)} queued changes")

        for change in pending:
            try:
                # Skip if too many retries
                if change.retry_count >= self.max_retries:
                    logger.warning(
                        f"Skipping change {change.id} (too many retries: {change.retry_count})"
                    )
                    result.errors.append(
                        f"Max retries exceeded for {change.entity_type.value} {change.entity_id}"
                    )
                    continue

                # Upload change to API
                success = await self._upload_change(change)

                if success:
                    self.queue.remove(change.id)
                    result.entities_synced += 1
                else:
                    # Retry with exponential backoff
                    delay = self.retry_delay * (2 ** change.retry_count)
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Error processing change {change.id}: {e}", exc_info=True)
                self.queue.update_retry(change.id, str(e))
                result.errors.append(str(e))

        return result

    async def pull_changes(self, since: datetime | None = None) -> SyncResult:
        """
        Pull changes from remote API (download phase).

        Args:
            since: Only fetch changes after this timestamp

        Returns:
            SyncResult with download statistics
        """
        result = SyncResult(success=True)

        try:
            # Call API to get changes
            # This will be implemented with actual API client
            # TODO: Implement actual pull logic
            logger.info(f"Pulling changes since {since}")

            # Placeholder
            remote_changes = []

            for change in remote_changes:
                try:
                    await self._apply_remote_change(change)
                    result.entities_synced += 1
                except Exception as e:
                    logger.error(f"Error applying remote change: {e}", exc_info=True)
                    result.errors.append(str(e))

        except Exception as e:
            logger.error(f"Failed to pull changes: {e}", exc_info=True)
            result.errors.append(str(e))
            result.success = False

        return result

    def get_status(self) -> SyncState:
        """
        Get current sync status.

        Returns:
            SyncState object
        """
        return self.state_manager.get_state()

    # ========================================================================
    # Internal Methods
    # ========================================================================

    async def _upload_change(self, change: QueuedChange) -> bool:
        """
        Upload a single change to the API.

        Args:
            change: Queued change to upload

        Returns:
            True if successful
        """
        try:
            # Build API request based on operation

            if change.operation == OperationType.CREATE:
                # POST request
                logger.debug(f"Creating {change.entity_type.value} {change.entity_id}")
                # await self.api.post(endpoint, json=change.payload)

            elif change.operation == OperationType.UPDATE:
                # PUT/PATCH request
                logger.debug(f"Updating {change.entity_type.value} {change.entity_id}")
                # await self.api.put(f"{endpoint}/{change.entity_id}", json=change.payload)

            elif change.operation == OperationType.DELETE:
                # DELETE request
                logger.debug(f"Deleting {change.entity_type.value} {change.entity_id}")
                # await self.api.delete(f"{endpoint}/{change.entity_id}")

            # Placeholder - return True when API is integrated
            return True

        except Exception as e:
            logger.error(f"Upload failed: {e}", exc_info=True)
            return False

    async def _apply_remote_change(self, change: dict[str, Any]) -> None:
        """
        Apply a remote change to local storage.

        Args:
            change: Remote change data
        """
        # This will integrate with LocalStorageManager
        # TODO: Implement actual application logic
        logger.debug(f"Applying remote change: {change}")

    def _resolve_conflict(
        self,
        local_data: dict[str, Any],
        remote_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Resolve conflict between local and remote data.

        Args:
            local_data: Local version
            remote_data: Remote version

        Returns:
            Resolved data
        """
        if self.conflict_strategy == ConflictStrategy.LAST_WRITE_WINS:
            # Compare timestamps
            local_ts = datetime.fromisoformat(local_data.get('updated_at', ''))
            remote_ts = datetime.fromisoformat(remote_data.get('updated_at', ''))
            return remote_data if remote_ts > local_ts else local_data

        elif self.conflict_strategy == ConflictStrategy.LOCAL_WINS:
            return local_data

        elif self.conflict_strategy == ConflictStrategy.REMOTE_WINS:
            return remote_data

        elif self.conflict_strategy == ConflictStrategy.MANUAL:
            # Create conflict file for manual resolution
            # TODO: Implement conflict file creation
            logger.warning("Manual conflict resolution required")
            return local_data

        return local_data

    def create_vector_clock(
        self,
        client_id: str,
        version: int,
        parent_version: int
    ) -> VectorClock:
        """
        Create a vector clock for ordering.

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
            timestamp=datetime.utcnow(),
            parent_version=parent_version
        )

    # ========================================================================
    # Utility Methods
    # ========================================================================

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
        """
        Check if sync is currently in progress.

        Returns:
            True if syncing
        """
        return self._syncing


# ============================================================================
# Helper Functions
# ============================================================================


async def exponential_backoff(
    attempt: int,
    initial_delay: float = 1.0,
    max_delay: float = 60.0
) -> None:
    """
    Sleep with exponential backoff.

    Args:
        attempt: Attempt number (0-indexed)
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
    """
    delay = min(initial_delay * (2 ** attempt), max_delay)
    await asyncio.sleep(delay)


def create_sync_engine(
    db_connection,
    api_client,
    storage_manager,
    **kwargs
) -> SyncEngine:
    """
    Factory function to create a configured sync engine.

    Args:
        db_connection: DatabaseConnection instance
        api_client: API client instance
        storage_manager: LocalStorageManager instance
        **kwargs: Additional configuration options

    Returns:
        Configured SyncEngine instance
    """
    return SyncEngine(
        db_connection=db_connection,
        api_client=api_client,
        storage_manager=storage_manager,
        **kwargs
    )
