"""Conflict resolution system for TraceRTM local storage.

Handles conflicts that arise during sync between local and remote changes,
implementing multiple resolution strategies and maintaining conflict history.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConflictStrategy(Enum):
    """Strategies for resolving conflicts between local and remote changes."""

    LAST_WRITE_WINS = "last_write_wins"  # Default: newest version wins
    LOCAL_WINS = "local_wins"  # Always prefer local changes
    REMOTE_WINS = "remote_wins"  # Always prefer server changes
    MANUAL = "manual"  # Create conflict file for user review


class ConflictStatus(Enum):
    """Status of a conflict resolution."""

    UNRESOLVED = "unresolved"
    RESOLVED_AUTO = "resolved_auto"
    RESOLVED_MANUAL = "resolved_manual"
    FAILED = "failed"


EntityType = Literal["project", "item", "link"]


@dataclass
class VectorClock:
    """Vector clock for ordering changes across distributed clients.

    Provides partial ordering of events in a distributed system where
    wall-clock time may not be reliable.
    """

    client_id: str
    version: int
    timestamp: datetime
    parent_version: int | None = None

    def __post_init__(self) -> None:
        """Ensure timestamp is timezone-aware."""
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=UTC)

    def happens_before(self, other: "VectorClock") -> bool:
        """Check if this clock happens before another.

        Returns:
            True if this change definitely happened before other
        """
        # Same client: compare versions
        if self.client_id == other.client_id:
            return self.version < other.version

        # Different clients: use timestamps (may be unreliable)
        return self.timestamp < other.timestamp

    def is_concurrent(self, other: "VectorClock") -> bool:
        """Check if two clocks are concurrent (conflict).

        Returns:
            True if neither happens before the other
        """
        return not (self.happens_before(other) or other.happens_before(self))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "client_id": self.client_id,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "parent_version": self.parent_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VectorClock":
        """Deserialize from dictionary."""
        return cls(
            client_id=data["client_id"],
            version=data["version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            parent_version=data.get("parent_version"),
        )


@dataclass
class EntityVersion:
    """Represents a version of an entity (project, item, or link)."""

    entity_id: str
    entity_type: EntityType
    data: dict[str, Any]
    vector_clock: VectorClock
    content_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "data": self.data,
            "vector_clock": self.vector_clock.to_dict(),
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntityVersion":
        """Deserialize from dictionary."""
        return cls(
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            data=data["data"],
            vector_clock=VectorClock.from_dict(data["vector_clock"]),
            content_hash=data.get("content_hash"),
        )


@dataclass
class Conflict:
    """Represents a conflict between local and remote entity versions."""

    id: str
    entity_id: str
    entity_type: EntityType
    local_version: EntityVersion
    remote_version: EntityVersion
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: ConflictStatus = ConflictStatus.UNRESOLVED
    resolution_strategy: ConflictStrategy | None = None
    resolved_at: datetime | None = None
    resolved_version: EntityVersion | None = None
    backup_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "local_version": self.local_version.to_dict(),
            "remote_version": self.remote_version.to_dict(),
            "detected_at": self.detected_at.isoformat(),
            "status": self.status.value,
            "resolution_strategy": (self.resolution_strategy.value if self.resolution_strategy else None),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_version": (self.resolved_version.to_dict() if self.resolved_version else None),
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "metadata": self.metadata,
        }


@dataclass
class ResolvedEntity:
    """Result of conflict resolution."""

    entity_id: str
    entity_type: EntityType
    version: EntityVersion
    strategy_used: ConflictStrategy
    conflict_id: str


class ConflictResolver:
    """Main conflict resolution logic for TraceRTM.

    Handles detection, resolution, and storage of conflicts between
    local and remote entity versions.
    """

    def __init__(
        self,
        session: Session,
        backup_dir: Path | None = None,
        default_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS,
    ) -> None:
        """Initialize conflict resolver.

        Args:
            session: SQLAlchemy database session
            backup_dir: Directory for storing conflict backups (defaults to ~/.tracertm/conflicts)
            default_strategy: Default resolution strategy
        """
        self.session = session
        self.default_strategy = default_strategy
        self.backup_dir = backup_dir or Path.home() / ".tracertm" / "conflicts"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Ensure conflicts table exists
        self._ensure_conflicts_table()

    def _ensure_conflicts_table(self) -> None:
        """Create conflicts table if it doesn't exist."""
        # Create table (compatible with both SQLite and PostgreSQL)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS conflicts (
            id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            local_version TEXT NOT NULL,
            remote_version TEXT NOT NULL,
            detected_at TEXT NOT NULL,
            status TEXT NOT NULL,
            resolution_strategy TEXT,
            resolved_at TEXT,
            resolved_version TEXT,
            backup_path TEXT,
            metadata TEXT
        )
        """
        self.session.execute(text(create_table_sql))

        # Create indexes separately (works for both SQLite and PostgreSQL)
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conflicts_entity ON conflicts (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_conflicts_status ON conflicts (status)",
            "CREATE INDEX IF NOT EXISTS idx_conflicts_detected ON conflicts (detected_at)",
        ]

        for index_sql in indexes:
            try:
                self.session.execute(text(index_sql))
            except SQLAlchemyError as e:
                # Index might already exist, ignore
                logger.debug("Index creation skipped (may already exist): %s", e)

        self.session.commit()

    def detect_conflict(self, local: EntityVersion, remote: EntityVersion) -> Conflict | None:
        """Detect if there's a conflict between local and remote versions.

        A conflict exists when:
        1. Both versions exist (not just create/delete)
        2. Vector clocks are concurrent (neither happens before the other)
        3. Content differs (different hashes or data)

        Args:
            local: Local entity version
            remote: Remote entity version

        Returns:
            Conflict object if conflict detected, None otherwise
        """
        # No conflict if one doesn't exist
        if not local or not remote:
            return None

        # Check if clocks are concurrent
        if not local.vector_clock.is_concurrent(remote.vector_clock):
            return None

        # Check if content actually differs
        if local.content_hash and remote.content_hash:
            if local.content_hash == remote.content_hash:
                return None
        # Fallback to data comparison
        elif local.data == remote.data:
            return None

        # We have a conflict
        conflict_id = f"conflict_{local.entity_id}_{int(datetime.now(UTC).timestamp())}"

        conflict = Conflict(
            id=conflict_id,
            entity_id=local.entity_id,
            entity_type=local.entity_type,
            local_version=local,
            remote_version=remote,
        )

        logger.warning(
            "Conflict detected for %s %s: local v%s vs remote v%s",
            local.entity_type,
            local.entity_id,
            local.vector_clock.version,
            remote.vector_clock.version,
        )

        # Store conflict in database
        self._store_conflict(conflict)

        return conflict

    def resolve(self, conflict: Conflict, strategy: ConflictStrategy | None = None) -> ResolvedEntity:
        """Resolve a conflict using the specified strategy.

        Args:
            conflict: Conflict to resolve
            strategy: Resolution strategy (defaults to instance default)

        Returns:
            Resolved entity with winning version

        Raises:
            ValueError: If MANUAL strategy used without providing merged content
        """
        strategy = strategy or self.default_strategy

        # Create backup before resolution
        backup_path = self.create_backup(conflict)
        conflict.backup_path = backup_path

        # Apply resolution strategy
        if strategy == ConflictStrategy.LAST_WRITE_WINS:
            resolved_version = self._resolve_last_write_wins(conflict)
        elif strategy == ConflictStrategy.LOCAL_WINS:
            resolved_version = conflict.local_version
        elif strategy == ConflictStrategy.REMOTE_WINS:
            resolved_version = conflict.remote_version
        elif strategy == ConflictStrategy.MANUAL:
            msg = "MANUAL strategy requires calling resolve_manual() with merged content"
            raise ValueError(msg)
        else:
            msg = f"Unknown strategy: {strategy}"
            raise ValueError(msg)

        # Update conflict record
        conflict.status = ConflictStatus.RESOLVED_AUTO
        conflict.resolution_strategy = strategy
        conflict.resolved_at = datetime.now(UTC)
        conflict.resolved_version = resolved_version

        self._update_conflict(conflict)

        logger.info(
            "Resolved conflict %s using %s, winner: %s",
            conflict.id,
            strategy.value,
            "local" if resolved_version == conflict.local_version else "remote",
        )

        return ResolvedEntity(
            entity_id=conflict.entity_id,
            entity_type=conflict.entity_type,
            version=resolved_version,
            strategy_used=strategy,
            conflict_id=conflict.id,
        )

    def _resolve_last_write_wins(self, conflict: Conflict) -> EntityVersion:
        """Resolve using last-write-wins strategy (newest timestamp)."""
        local_ts = conflict.local_version.vector_clock.timestamp
        remote_ts = conflict.remote_version.vector_clock.timestamp

        if local_ts > remote_ts:
            return conflict.local_version
        if remote_ts > local_ts:
            return conflict.remote_version
        # Timestamps equal, use version number
        if conflict.local_version.vector_clock.version > conflict.remote_version.vector_clock.version:
            return conflict.local_version
        return conflict.remote_version

    def resolve_manual(
        self,
        conflict: Conflict,
        merged_data: dict[str, Any],
        merged_by: str = "user",
    ) -> ResolvedEntity:
        """Resolve conflict manually with user-provided merged content.

        Args:
            conflict: Conflict to resolve
            merged_data: User-merged entity data
            merged_by: Identifier of who performed the merge

        Returns:
            Resolved entity with merged version
        """
        # Create backup before resolution
        if not conflict.backup_path:
            conflict.backup_path = self.create_backup(conflict)

        # Create new version from merged data
        # Use higher version number from either side + 1
        new_version = (
            max(
                conflict.local_version.vector_clock.version,
                conflict.remote_version.vector_clock.version,
            )
            + 1
        )

        merged_clock = VectorClock(
            client_id=conflict.local_version.vector_clock.client_id,
            version=new_version,
            timestamp=datetime.now(UTC),
            parent_version=conflict.local_version.vector_clock.version,
        )

        resolved_version = EntityVersion(
            entity_id=conflict.entity_id,
            entity_type=conflict.entity_type,
            data=merged_data,
            vector_clock=merged_clock,
        )

        # Update conflict record
        conflict.status = ConflictStatus.RESOLVED_MANUAL
        conflict.resolution_strategy = ConflictStrategy.MANUAL
        conflict.resolved_at = datetime.now(UTC)
        conflict.resolved_version = resolved_version
        conflict.metadata["merged_by"] = merged_by

        self._update_conflict(conflict)

        logger.info("Manually resolved conflict %s by %s, version=%s", conflict.id, merged_by, new_version)

        return ResolvedEntity(
            entity_id=conflict.entity_id,
            entity_type=conflict.entity_type,
            version=resolved_version,
            strategy_used=ConflictStrategy.MANUAL,
            conflict_id=conflict.id,
        )

    def create_backup(self, conflict: Conflict) -> Path:
        """Create backup files for conflicting versions.

        Args:
            conflict: Conflict to backup

        Returns:
            Path to backup directory
        """
        # Create timestamped backup directory
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_dir / conflict.entity_type / f"{conflict.entity_id}_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Save local version
        local_path = backup_dir / "local.json"
        with local_path.open("w") as f:
            json.dump(conflict.local_version.to_dict(), f, indent=2)

        # Save remote version
        remote_path = backup_dir / "remote.json"
        with remote_path.open("w") as f:
            json.dump(conflict.remote_version.to_dict(), f, indent=2)

        # Save conflict metadata
        meta_path = backup_dir / "conflict.json"
        with meta_path.open("w") as f:
            json.dump(
                {
                    "conflict_id": conflict.id,
                    "entity_id": conflict.entity_id,
                    "entity_type": conflict.entity_type,
                    "detected_at": conflict.detected_at.isoformat(),
                    "local_version": conflict.local_version.vector_clock.version,
                    "remote_version": conflict.remote_version.vector_clock.version,
                },
                f,
                indent=2,
            )

        logger.info("Created conflict backup at %s", backup_dir)
        return backup_dir

    def list_unresolved(self, entity_type: EntityType | None = None) -> list[Conflict]:
        """List all unresolved conflicts.

        Args:
            entity_type: Optional filter by entity type

        Returns:
            List of unresolved conflicts
        """
        query = "SELECT * FROM conflicts WHERE status = :status"
        params = {"status": ConflictStatus.UNRESOLVED.value}

        if entity_type:
            query += " AND entity_type = :entity_type"
            params["entity_type"] = entity_type

        query += " ORDER BY detected_at DESC"

        result = self.session.execute(text(query), params)
        rows = result.fetchall()

        conflicts = []
        for row in rows:
            conflict = self._row_to_conflict(row)
            conflicts.append(conflict)

        return conflicts

    def get_conflict(self, conflict_id: str) -> Conflict | None:
        """Get conflict by ID.

        Args:
            conflict_id: Conflict identifier

        Returns:
            Conflict object or None if not found
        """
        result = self.session.execute(text("SELECT * FROM conflicts WHERE id = :id"), {"id": conflict_id})
        row = result.fetchone()

        if not row:
            return None

        return self._row_to_conflict(row)

    def _store_conflict(self, conflict: Conflict) -> None:
        """Store conflict in database."""
        self.session.execute(
            text(
                """
                INSERT INTO conflicts (
                    id, entity_id, entity_type, local_version, remote_version,
                    detected_at, status, resolution_strategy, resolved_at,
                    resolved_version, backup_path, metadata
                ) VALUES (
                    :id, :entity_id, :entity_type, :local_version, :remote_version,
                    :detected_at, :status, :resolution_strategy, :resolved_at,
                    :resolved_version, :backup_path, :metadata
                )
                """,
            ),
            {
                "id": conflict.id,
                "entity_id": conflict.entity_id,
                "entity_type": conflict.entity_type,
                "local_version": json.dumps(conflict.local_version.to_dict()),
                "remote_version": json.dumps(conflict.remote_version.to_dict()),
                "detected_at": conflict.detected_at.isoformat(),
                "status": conflict.status.value,
                "resolution_strategy": (conflict.resolution_strategy.value if conflict.resolution_strategy else None),
                "resolved_at": (conflict.resolved_at.isoformat() if conflict.resolved_at else None),
                "resolved_version": (
                    json.dumps(conflict.resolved_version.to_dict()) if conflict.resolved_version else None
                ),
                "backup_path": (str(conflict.backup_path) if conflict.backup_path else None),
                "metadata": json.dumps(conflict.metadata),
            },
        )
        self.session.commit()

    def _update_conflict(self, conflict: Conflict) -> None:
        """Update conflict in database."""
        self.session.execute(
            text(
                """
                UPDATE conflicts SET
                    status = :status,
                    resolution_strategy = :resolution_strategy,
                    resolved_at = :resolved_at,
                    resolved_version = :resolved_version,
                    backup_path = :backup_path,
                    metadata = :metadata
                WHERE id = :id
                """,
            ),
            {
                "id": conflict.id,
                "status": conflict.status.value,
                "resolution_strategy": (conflict.resolution_strategy.value if conflict.resolution_strategy else None),
                "resolved_at": (conflict.resolved_at.isoformat() if conflict.resolved_at else None),
                "resolved_version": (
                    json.dumps(conflict.resolved_version.to_dict()) if conflict.resolved_version else None
                ),
                "backup_path": (str(conflict.backup_path) if conflict.backup_path else None),
                "metadata": json.dumps(conflict.metadata),
            },
        )
        self.session.commit()

    def _row_to_conflict(self, row: Any) -> Conflict:
        """Convert database row to Conflict object."""
        return Conflict(
            id=row.id,
            entity_id=row.entity_id,
            entity_type=row.entity_type,
            local_version=EntityVersion.from_dict(json.loads(row.local_version)),
            remote_version=EntityVersion.from_dict(json.loads(row.remote_version)),
            detected_at=datetime.fromisoformat(row.detected_at),
            status=ConflictStatus(row.status),
            resolution_strategy=(ConflictStrategy(row.resolution_strategy) if row.resolution_strategy else None),
            resolved_at=(datetime.fromisoformat(row.resolved_at) if row.resolved_at else None),
            resolved_version=(
                EntityVersion.from_dict(json.loads(row.resolved_version)) if row.resolved_version else None
            ),
            backup_path=Path(row.backup_path) if row.backup_path else None,
            metadata=json.loads(row.metadata) if row.metadata else {},
        )

    def get_conflict_stats(self) -> dict[str, Any]:
        """Get statistics about conflicts.

        Returns:
            Dict with conflict statistics
        """
        result = self.session.execute(
            text(
                """
                SELECT
                    status,
                    entity_type,
                    COUNT(*) as count
                FROM conflicts
                GROUP BY status, entity_type
                """,
            ),
        )

        stats: dict[str, Any] = {
            "by_status": {},
            "by_entity_type": {},
            "total": 0,
        }

        for row in result:
            status = row.status
            entity_type = row.entity_type
            count = row.count

            if status not in stats["by_status"]:
                stats["by_status"][status] = 0
            stats["by_status"][status] += count

            if entity_type not in stats["by_entity_type"]:
                stats["by_entity_type"][entity_type] = 0
            stats["by_entity_type"][entity_type] += count

            stats["total"] += count

        return stats


class ConflictBackup:
    """Helper class for managing conflict backups."""

    def __init__(self, backup_dir: Path) -> None:
        """Initialize conflict backup manager.

        Args:
            backup_dir: Directory for storing backups
        """
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def list_backups(self, entity_type: EntityType | None = None) -> list[dict[str, Any]]:
        """List all conflict backups.

        Args:
            entity_type: Optional filter by entity type

        Returns:
            List of backup metadata
        """
        backups = []

        search_dirs = [self.backup_dir / entity_type] if entity_type else list(self.backup_dir.iterdir())

        for type_dir in search_dirs:
            if not type_dir.is_dir():
                continue

            for backup_dir in type_dir.iterdir():
                if not backup_dir.is_dir():
                    continue

                meta_path = backup_dir / "conflict.json"
                if meta_path.exists():
                    with meta_path.open() as f:
                        metadata = json.load(f)
                        metadata["backup_path"] = str(backup_dir)
                        backups.append(metadata)

        # Sort by detected_at (newest first)
        backups.sort(key=lambda x: x.get("detected_at", ""), reverse=True)

        return backups

    def load_backup(self, backup_path: Path) -> tuple[EntityVersion, EntityVersion] | None:
        """Load local and remote versions from backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            Tuple of (local_version, remote_version) or None if not found
        """
        local_path = backup_path / "local.json"
        remote_path = backup_path / "remote.json"

        if not (local_path.exists() and remote_path.exists()):
            return None

        with local_path.open() as f:
            local_version = EntityVersion.from_dict(json.load(f))

        with remote_path.open() as f:
            remote_version = EntityVersion.from_dict(json.load(f))

        return local_version, remote_version

    def delete_backup(self, backup_path: Path) -> bool:
        """Delete a backup directory.

        Args:
            backup_path: Path to backup directory

        Returns:
            True if deleted successfully
        """
        if not backup_path.exists():
            return False

        import shutil

        shutil.rmtree(backup_path)
        logger.info("Deleted backup at %s", backup_path)
        return True


# Utility functions for CLI/TUI integration


def format_conflict_summary(conflict: Conflict) -> str:
    """Format conflict as human-readable summary.

    Args:
        conflict: Conflict to format

    Returns:
        Formatted string
    """
    local_v = conflict.local_version.vector_clock.version
    remote_v = conflict.remote_version.vector_clock.version
    local_ts = conflict.local_version.vector_clock.timestamp.strftime("%Y-%m-%d %H:%M")
    remote_ts = conflict.remote_version.vector_clock.timestamp.strftime("%Y-%m-%d %H:%M")

    return (
        f"Conflict: {conflict.entity_type} '{conflict.entity_id}'\n"
        f"  Local:  v{local_v} @ {local_ts}\n"
        f"  Remote: v{remote_v} @ {remote_ts}\n"
        f"  Status: {conflict.status.value}\n"
        f"  Detected: {conflict.detected_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )


def compare_versions(local: EntityVersion, remote: EntityVersion) -> dict[str, list[str]]:
    """Compare two entity versions and identify differences.

    Args:
        local: Local version
        remote: Remote version

    Returns:
        Dict with 'added', 'removed', 'modified' keys containing field names
    """
    differences: dict[str, list[str]] = {"added": [], "removed": [], "modified": []}

    local_data = local.data
    remote_data = remote.data

    # Find added/removed keys
    local_keys = set(local_data.keys())
    remote_keys = set(remote_data.keys())

    differences["added"] = list(remote_keys - local_keys)
    differences["removed"] = list(local_keys - remote_keys)

    # Find modified values
    for key in local_keys & remote_keys:
        if local_data[key] != remote_data[key]:
            differences["modified"].append(key)

    return differences
