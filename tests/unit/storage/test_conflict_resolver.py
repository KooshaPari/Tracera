"""Unit tests for conflict resolver.

Tests conflict detection, resolution strategies, vector clocks,
backup creation, and conflict history management.
"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_THREE, COUNT_TWO
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


@pytest.fixture
def temp_db() -> None:
    """Create temporary SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture
def temp_backup_dir() -> None:
    """Create temporary directory for backups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def resolver(temp_db: Any, temp_backup_dir: Any) -> None:
    """Create conflict resolver instance."""
    return ConflictResolver(
        session=temp_db,
        backup_dir=temp_backup_dir,
        default_strategy=ConflictStrategy.LAST_WRITE_WINS,
    )


class TestVectorClock:
    """Test vector clock functionality."""

    def test_happens_before_same_client(self) -> None:
        """Test happens_before for same client."""
        clock1 = VectorClock(
            client_id="client-1",
            version=1,
            timestamp=datetime.now(UTC),
        )
        clock2 = VectorClock(
            client_id="client-1",
            version=2,
            timestamp=datetime.now(UTC),
        )

        assert clock1.happens_before(clock2)
        assert not clock2.happens_before(clock1)

    def test_happens_before_different_clients(self) -> None:
        """Test happens_before for different clients using timestamps."""
        now = datetime.now(UTC)
        clock1 = VectorClock(
            client_id="client-1",
            version=1,
            timestamp=now,
        )
        clock2 = VectorClock(
            client_id="client-2",
            version=1,
            timestamp=now + timedelta(seconds=10),
        )

        assert clock1.happens_before(clock2)
        assert not clock2.happens_before(clock1)

    def test_is_concurrent(self) -> None:
        """Test concurrent clocks detection."""
        now = datetime.now(UTC)
        clock1 = VectorClock(
            client_id="client-1",
            version=2,
            timestamp=now,
        )
        clock2 = VectorClock(
            client_id="client-2",
            version=2,
            timestamp=now,  # Same timestamp, different clients
        )

        assert clock1.is_concurrent(clock2)
        assert clock2.is_concurrent(clock1)

    def test_serialization(self) -> None:
        """Test vector clock serialization."""
        clock = VectorClock(
            client_id="client-1",
            version=5,
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            parent_version=4,
        )

        data = clock.to_dict()
        restored = VectorClock.from_dict(data)

        assert restored.client_id == clock.client_id
        assert restored.version == clock.version
        assert restored.timestamp == clock.timestamp
        assert restored.parent_version == clock.parent_version

    def test_timezone_aware(self) -> None:
        """Test that timestamps are always timezone-aware."""
        naive_dt = datetime(2024, 1, 1, 12, 0, 0)
        clock = VectorClock(
            client_id="client-1",
            version=1,
            timestamp=naive_dt,
        )

        assert clock.timestamp.tzinfo is not None


class TestEntityVersion:
    """Test entity version functionality."""

    def test_serialization(self) -> None:
        """Test entity version serialization."""
        clock = VectorClock(
            client_id="client-1",
            version=1,
            timestamp=datetime.now(UTC),
        )

        version = EntityVersion(
            entity_id="item-123",
            entity_type="item",
            data={"title": "Test Item", "status": "active"},
            vector_clock=clock,
            content_hash="abc123",
        )

        data = version.to_dict()
        restored = EntityVersion.from_dict(data)

        assert restored.entity_id == version.entity_id
        assert restored.entity_type == version.entity_type
        assert restored.data == version.data
        assert restored.content_hash == version.content_hash


class TestConflictDetection:
    """Test conflict detection logic."""

    def test_no_conflict_sequential_changes(self, resolver: Any) -> None:
        """Test no conflict when changes are sequential."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 1, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-1", 2, now + timedelta(seconds=10)),
        )

        conflict = resolver.detect_conflict(local, remote)
        assert conflict is None  # No conflict, remote is newer

    def test_conflict_concurrent_changes(self, resolver: Any) -> None:
        """Test conflict when changes are concurrent."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 2, now),
            content_hash="hash1",
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 2, now),
            content_hash="hash2",
        )

        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None
        assert conflict.entity_id == "item-1"
        assert conflict.status == ConflictStatus.UNRESOLVED

    def test_no_conflict_same_content(self, resolver: Any) -> None:
        """Test no conflict when content is identical."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Same"},
            vector_clock=VectorClock("client-1", 2, now),
            content_hash="same_hash",
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Same"},
            vector_clock=VectorClock("client-2", 2, now),
            content_hash="same_hash",
        )

        conflict = resolver.detect_conflict(local, remote)
        assert conflict is None


class TestConflictResolution:
    """Test conflict resolution strategies."""

    def test_last_write_wins_local_newer(self, resolver: Any) -> None:
        """Test last-write-wins with local version newer."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local Newer"},
            vector_clock=VectorClock("client-1", 2, now + timedelta(seconds=10)),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote Older"},
            vector_clock=VectorClock("client-2", 2, now),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        result = resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)

        assert result.version == local
        assert result.strategy_used == ConflictStrategy.LAST_WRITE_WINS

    def test_last_write_wins_remote_newer(self, resolver: Any) -> None:
        """Test last-write-wins with remote version newer."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local Older"},
            vector_clock=VectorClock("client-1", 2, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote Newer"},
            vector_clock=VectorClock("client-2", 2, now + timedelta(seconds=10)),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        result = resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)

        assert result.version == remote
        assert result.strategy_used == ConflictStrategy.LAST_WRITE_WINS

    def test_local_wins_strategy(self, resolver: Any) -> None:
        """Test local-wins always picks local."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 1, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 2, now + timedelta(seconds=10)),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        result = resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)

        assert result.version == local

    def test_remote_wins_strategy(self, resolver: Any) -> None:
        """Test remote-wins always picks remote."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 2, now + timedelta(seconds=10)),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 1, now),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)

        assert result.version == remote

    def test_manual_resolution(self, resolver: Any) -> None:
        """Test manual conflict resolution."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local", "priority": "high"},
            vector_clock=VectorClock("client-1", 2, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote", "status": "done"},
            vector_clock=VectorClock("client-2", 2, now),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        # Merge both changes
        merged_data = {
            "title": "Merged",
            "priority": "high",
            "status": "done",
        }

        result = resolver.resolve_manual(conflict, merged_data, merged_by="user-123")

        assert result.version.data == merged_data
        assert result.version.vector_clock.version == COUNT_THREE  # Incremented
        assert result.strategy_used == ConflictStrategy.MANUAL

    def test_manual_strategy_requires_merged_content(self, resolver: Any) -> None:
        """Test that MANUAL strategy requires resolve_manual()."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 1, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 1, now),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        with pytest.raises(ValueError, match="MANUAL strategy requires"):
            resolver.resolve(conflict, ConflictStrategy.MANUAL)


class TestConflictBackup:
    """Test conflict backup functionality."""

    def test_create_backup(self, resolver: Any) -> None:
        """Test backup creation."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 1, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 1, now),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        backup_path = resolver.create_backup(conflict)

        assert backup_path.exists()
        assert (backup_path / "local.json").exists()
        assert (backup_path / "remote.json").exists()
        assert (backup_path / "conflict.json").exists()

        # Verify content
        with Path(backup_path / "local.json").open(encoding="utf-8") as f:
            local_data = json.load(f)
            assert local_data["data"]["title"] == "Local"

        with Path(backup_path / "remote.json").open(encoding="utf-8") as f:
            remote_data = json.load(f)
            assert remote_data["data"]["title"] == "Remote"

    def test_backup_manager_list(self, temp_backup_dir: Any) -> None:
        """Test listing backups."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create test backups
        item_dir = temp_backup_dir / "item" / "item-1_20240101_120000"
        item_dir.mkdir(parents=True)

        conflict_meta = {
            "conflict_id": "test-1",
            "entity_id": "item-1",
            "entity_type": "item",
            "detected_at": "2024-01-01T12:00:00+00:00",
        }

        with Path(item_dir / "conflict.json").open("w", encoding="utf-8") as f:
            json.dump(conflict_meta, f)

        backups = backup_mgr.list_backups()

        assert len(backups) == 1
        assert backups[0]["conflict_id"] == "test-1"

    def test_backup_manager_load(self, temp_backup_dir: Any) -> None:
        """Test loading backup."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create test backup
        backup_path = temp_backup_dir / "item" / "item-1_test"
        backup_path.mkdir(parents=True)

        local_version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 1, datetime.now(UTC)),
        )

        remote_version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 1, datetime.now(UTC)),
        )

        with Path(backup_path / "local.json").open("w", encoding="utf-8") as f:
            json.dump(local_version.to_dict(), f)

        with Path(backup_path / "remote.json").open("w", encoding="utf-8") as f:
            json.dump(remote_version.to_dict(), f)

        loaded = backup_mgr.load_backup(backup_path)

        assert loaded is not None
        local, remote = loaded
        assert local.entity_id == "item-1"
        assert remote.entity_id == "item-1"


class TestConflictQueries:
    """Test conflict querying and statistics."""

    def test_list_unresolved(self, resolver: Any) -> None:
        """Test listing unresolved conflicts."""
        now = datetime.now(UTC)

        # Create and store conflicts
        for i in range(3):
            local = EntityVersion(
                entity_id=f"item-{i}",
                entity_type="item",
                data={"title": f"Local {i}"},
                vector_clock=VectorClock("client-1", 1, now),
                content_hash=f"hash-local-{i}",
            )

            remote = EntityVersion(
                entity_id=f"item-{i}",
                entity_type="item",
                data={"title": f"Remote {i}"},
                vector_clock=VectorClock("client-2", 1, now),
                content_hash=f"hash-remote-{i}",
            )

            resolver.detect_conflict(local, remote)

        unresolved = resolver.list_unresolved()
        assert len(unresolved) == COUNT_THREE

    def test_list_unresolved_by_type(self, resolver: Any) -> None:
        """Test filtering unresolved by entity type."""
        now = datetime.now(UTC)

        # Create item conflict
        item_local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Item"},
            vector_clock=VectorClock("client-1", 1, now),
            content_hash="hash1",
        )

        item_remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Item Remote"},
            vector_clock=VectorClock("client-2", 1, now),
            content_hash="hash2",
        )

        # Create project conflict
        project_local = EntityVersion(
            entity_id="proj-1",
            entity_type="project",
            data={"name": "Project"},
            vector_clock=VectorClock("client-1", 1, now),
            content_hash="hash3",
        )

        project_remote = EntityVersion(
            entity_id="proj-1",
            entity_type="project",
            data={"name": "Project Remote"},
            vector_clock=VectorClock("client-2", 1, now),
            content_hash="hash4",
        )

        resolver.detect_conflict(item_local, item_remote)
        resolver.detect_conflict(project_local, project_remote)

        item_conflicts = resolver.list_unresolved(entity_type="item")
        project_conflicts = resolver.list_unresolved(entity_type="project")

        assert len(item_conflicts) == 1
        assert len(project_conflicts) == 1

    def test_get_conflict_stats(self, resolver: Any) -> None:
        """Test conflict statistics."""
        now = datetime.now(UTC)

        # Create and resolve conflicts
        for i in range(2):
            local = EntityVersion(
                entity_id=f"item-{i}",
                entity_type="item",
                data={"title": f"Local {i}"},
                vector_clock=VectorClock("client-1", 1, now),
                content_hash=f"hash-{i}",
            )

            remote = EntityVersion(
                entity_id=f"item-{i}",
                entity_type="item",
                data={"title": f"Remote {i}"},
                vector_clock=VectorClock("client-2", 1, now),
                content_hash=f"hash-remote-{i}",
            )

            conflict = resolver.detect_conflict(local, remote)
            if i == 0:
                resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)

        stats = resolver.get_conflict_stats()

        assert stats["total"] == COUNT_TWO
        assert stats["by_status"][ConflictStatus.UNRESOLVED.value] == 1
        assert stats["by_status"][ConflictStatus.RESOLVED_AUTO.value] == 1


class TestUtilities:
    """Test utility functions."""

    def test_format_conflict_summary(self) -> None:
        """Test conflict summary formatting."""
        now = datetime.now(UTC)

        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Local"},
            vector_clock=VectorClock("client-1", 1, now),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Remote"},
            vector_clock=VectorClock("client-2", 2, now),
        )

        conflict = Conflict(
            id="test-conflict",
            entity_id="item-1",
            entity_type="item",
            local_version=local,
            remote_version=remote,
        )

        summary = format_conflict_summary(conflict)

        assert "item-1" in summary
        assert "v1" in summary
        assert "v2" in summary
        assert "unresolved" in summary.lower()

    def test_compare_versions(self) -> None:
        """Test version comparison."""
        local = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={
                "title": "Item",
                "status": "active",
                "priority": "high",
            },
            vector_clock=VectorClock("client-1", 1, datetime.now(UTC)),
        )

        remote = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={
                "title": "Item Modified",
                "status": "active",
                "owner": "user-1",
            },
            vector_clock=VectorClock("client-2", 1, datetime.now(UTC)),
        )

        diff = compare_versions(local, remote)

        assert "owner" in diff["added"]
        assert "priority" in diff["removed"]
        assert "title" in diff["modified"]
        assert "status" not in diff["modified"]  # Same value
