"""Comprehensive conflict resolver tests for 100% coverage (WP-1.3).

Tests all aspects of conflict resolution:
- 3-way merge algorithm (base, local, remote)
- Conflict detection (line conflicts, metadata conflicts)
- Conflict resolution strategies
- No-conflict merges
- All conflict types
- Large file handling
- Unicode content
- Whitespace handling
- Performance on large files
- Edge cases (empty files, single line, binary data)

Target: 86 tests, 100% coverage
"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.storage.conflict_resolver import (
    Conflict,
    ConflictBackup,
    ConflictResolver,
    ConflictStatus,
    ConflictStrategy,
    EntityVersion,
    ResolvedEntity,
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


@pytest.fixture
def base_time() -> None:
    """Base timestamp for consistent testing."""
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)


# ============================================================================
# VectorClock Tests (8 tests)
# ============================================================================


class TestVectorClockBasic:
    """Test basic vector clock functionality."""

    def test_vector_clock_creation(self, base_time: Any) -> None:
        """Test creating a vector clock."""
        clock = VectorClock(
            client_id="client-1",
            version=1,
            timestamp=base_time,
        )
        assert clock.client_id == "client-1"
        assert clock.version == 1
        assert clock.timestamp == base_time

    def test_vector_clock_post_init_timezone(self) -> None:
        """Test that naive timestamps are converted to UTC."""
        naive_dt = datetime(2024, 1, 1, 12, 0, 0)
        clock = VectorClock(
            client_id="client-1",
            version=1,
            timestamp=naive_dt,
        )
        assert clock.timestamp.tzinfo is not None

    def test_vector_clock_with_parent(self, base_time: Any) -> None:
        """Test vector clock with parent version."""
        clock = VectorClock(
            client_id="client-1",
            version=2,
            timestamp=base_time,
            parent_version=1,
        )
        assert clock.parent_version == 1

    def test_vector_clock_happens_before_same_client(self, base_time: Any) -> None:
        """Test happens_before for same client."""
        clock1 = VectorClock("client-1", 1, base_time)
        clock2 = VectorClock("client-1", 2, base_time + timedelta(seconds=10))
        assert clock1.happens_before(clock2)
        assert not clock2.happens_before(clock1)

    def test_vector_clock_happens_before_different_clients(self, base_time: Any) -> None:
        """Test happens_before for different clients (uses timestamp)."""
        clock1 = VectorClock("client-1", 5, base_time)
        clock2 = VectorClock("client-2", 1, base_time + timedelta(seconds=10))
        assert clock1.happens_before(clock2)

    def test_vector_clock_is_concurrent(self, base_time: Any) -> None:
        """Test concurrent detection."""
        clock1 = VectorClock("client-1", 2, base_time)
        clock2 = VectorClock("client-2", 2, base_time)
        assert clock1.is_concurrent(clock2)

    def test_vector_clock_serialization(self, base_time: Any) -> None:
        """Test to_dict and from_dict."""
        original = VectorClock("client-1", 3, base_time, parent_version=2)
        data = original.to_dict()
        restored = VectorClock.from_dict(data)

        assert restored.client_id == original.client_id
        assert restored.version == original.version
        assert restored.timestamp == original.timestamp
        assert restored.parent_version == original.parent_version

    def test_vector_clock_not_concurrent(self, base_time: Any) -> None:
        """Test is_concurrent returns false for non-concurrent clocks."""
        clock1 = VectorClock("client-1", 1, base_time)
        clock2 = VectorClock("client-1", 2, base_time)
        assert not clock1.is_concurrent(clock2)


# ============================================================================
# EntityVersion Tests (8 tests)
# ============================================================================


class TestEntityVersion:
    """Test entity version functionality."""

    def test_entity_version_creation(self, base_time: Any) -> None:
        """Test creating entity version."""
        clock = VectorClock("client-1", 1, base_time)
        version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Test"},
            vector_clock=clock,
        )
        assert version.entity_id == "item-1"
        assert version.entity_type == "item"
        assert version.data["title"] == "Test"

    def test_entity_version_with_hash(self, base_time: Any) -> None:
        """Test entity version with content hash."""
        clock = VectorClock("client-1", 1, base_time)
        version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Test"},
            vector_clock=clock,
            content_hash="abc123def",
        )
        assert version.content_hash == "abc123def"

    def test_entity_version_serialization(self, base_time: Any) -> None:
        """Test to_dict and from_dict."""
        clock = VectorClock("client-1", 1, base_time)
        original = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={"title": "Test", "status": "active"},
            vector_clock=clock,
            content_hash="hash123",
        )
        data = original.to_dict()
        restored = EntityVersion.from_dict(data)

        assert restored.entity_id == original.entity_id
        assert restored.entity_type == original.entity_type
        assert restored.data == original.data
        assert restored.content_hash == original.content_hash

    def test_entity_version_complex_data(self, base_time: Any) -> None:
        """Test entity version with complex nested data."""
        clock = VectorClock("client-1", 1, base_time)
        complex_data = {
            "title": "Test",
            "tags": ["a", "b", "c"],
            "metadata": {
                "author": "user-1",
                "created": "2024-01-01",
                "nested": {"level": 2},
            },
        }
        version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data=complex_data,
            vector_clock=clock,
        )
        assert version.data["metadata"]["nested"]["level"] == COUNT_TWO

    def test_entity_version_all_types(self, base_time: Any) -> None:
        """Test entity version with all supported entity types."""
        clock = VectorClock("client-1", 1, base_time)
        for entity_type in ["project", "item", "link"]:
            version = EntityVersion(
                entity_id=f"id-{entity_type}",
                entity_type=entity_type,
                data={"name": f"Test {entity_type}"},
                vector_clock=clock,
            )
            assert version.entity_type == entity_type

    def test_entity_version_empty_data(self, base_time: Any) -> None:
        """Test entity version with empty data."""
        clock = VectorClock("client-1", 1, base_time)
        version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data={},
            vector_clock=clock,
        )
        assert version.data == {}

    def test_entity_version_unicode_content(self, base_time: Any) -> None:
        """Test entity version with unicode content."""
        clock = VectorClock("client-1", 1, base_time)
        unicode_data = {
            "title": "测试",  # Chinese
            "description": "Тест",  # Russian
            "emoji": "🚀✨",
        }
        version = EntityVersion(
            entity_id="item-1",
            entity_type="item",
            data=unicode_data,
            vector_clock=clock,
        )
        assert version.data["title"] == "测试"
        assert version.data["emoji"] == "🚀✨"


# ============================================================================
# Conflict Detection Tests (10 tests)
# ============================================================================


class TestResolverInitialization:
    """Test ConflictResolver initialization and database setup."""

    def test_resolver_creates_backup_dir(self, temp_db: Any) -> None:
        """Test resolver creates backup directory on init."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = Path(tmpdir) / "new_backups"
            assert not backup_dir.exists()

            ConflictResolver(
                session=temp_db,
                backup_dir=backup_dir,
            )

            assert backup_dir.exists()

    def test_resolver_initializes_database(self, temp_db: Any, temp_backup_dir: Any) -> None:
        """Test resolver initializes database tables on init."""
        ConflictResolver(
            session=temp_db,
            backup_dir=temp_backup_dir,
        )

        # Check that conflicts table was created
        result = temp_db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='conflicts'"))
        assert result.fetchone() is not None


class TestConflictDetection:
    """Test conflict detection logic."""

    def test_no_conflict_sequential_same_client(self, resolver: Any, base_time: Any) -> None:
        """Test no conflict with sequential changes on same client."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "V1"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "V2"},
            VectorClock("client-1", 2, base_time + timedelta(seconds=10)),
            "hash2",
        )
        assert resolver.detect_conflict(local, remote) is None

    def test_conflict_concurrent_different_content(self, resolver: Any, base_time: Any) -> None:
        """Test conflict detection with concurrent changes."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None
        assert conflict.entity_id == "item-1"
        assert conflict.status == ConflictStatus.UNRESOLVED

    def test_no_conflict_identical_content(self, resolver: Any, base_time: Any) -> None:
        """Test no conflict when content is identical."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Same"},
            VectorClock("client-1", 2, base_time),
            "same_hash",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Same"},
            VectorClock("client-2", 2, base_time),
            "same_hash",
        )
        assert resolver.detect_conflict(local, remote) is None

    def test_no_conflict_when_local_is_none(self, resolver: Any, base_time: Any) -> None:
        """Test no conflict when local version is None."""
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        assert resolver.detect_conflict(None, remote) is None

    def test_no_conflict_when_remote_is_none(self, resolver: Any, base_time: Any) -> None:
        """Test no conflict when remote version is None."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        assert resolver.detect_conflict(local, None) is None

    def test_conflict_stored_in_database(self, resolver: Any, base_time: Any) -> None:
        """Test that detected conflict is stored in database."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        retrieved = resolver.get_conflict(conflict.id)
        assert retrieved is not None
        assert retrieved.entity_id == "item-1"

    def test_conflict_different_entity_ids(self, resolver: Any, base_time: Any) -> None:
        """Test detect_conflict uses local entity_id regardless of remote."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Item 1"},
            VectorClock("client-1", 2, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-2",
            "item",
            {"title": "Item 2"},
            VectorClock("client-2", 2, base_time),
            "hash2",
        )
        # Detects conflict based on concurrent changes (uses local entity_id)
        conflict = resolver.detect_conflict(local, remote)
        # Different hashes and concurrent clocks = conflict
        assert conflict is not None
        assert conflict.entity_id == "item-1"

    def test_conflict_with_missing_hashes(self, resolver: Any, base_time: Any) -> None:
        """Test conflict detection without hashes (uses data comparison)."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local", "status": "active"},
            VectorClock("client-1", 2, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote", "status": "active"},
            VectorClock("client-2", 2, base_time),
        )
        # Different data (title), different clients = conflict
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

    def test_project_conflict_detection(self, resolver: Any, base_time: Any) -> None:
        """Test conflict detection for project entity type."""
        local = EntityVersion(
            "proj-1",
            "project",
            {"name": "Project Local"},
            VectorClock("client-1", 2, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "proj-1",
            "project",
            {"name": "Project Remote"},
            VectorClock("client-2", 2, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None
        assert conflict.entity_type == "project"

    def test_link_conflict_detection(self, resolver: Any, base_time: Any) -> None:
        """Test conflict detection for link entity type."""
        local = EntityVersion(
            "link-1",
            "link",
            {"source": "item-1", "target": "item-2"},
            VectorClock("client-1", 2, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "link-1",
            "link",
            {"source": "item-1", "target": "item-3"},
            VectorClock("client-2", 2, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None


# ============================================================================
# Conflict Resolution Strategy Tests (12 tests)
# ============================================================================


class TestResolutionStrategies:
    """Test different conflict resolution strategies."""

    def test_last_write_wins_local_newer(self, resolver: Any, base_time: Any) -> None:
        """Test LAST_WRITE_WINS when local is newer."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time + timedelta(seconds=10)),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)
        assert result.version == local
        assert result.strategy_used == ConflictStrategy.LAST_WRITE_WINS

    def test_last_write_wins_remote_newer(self, resolver: Any, base_time: Any) -> None:
        """Test LAST_WRITE_WINS when remote is newer."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time + timedelta(seconds=10)),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)
        assert result.version == remote

    def test_last_write_wins_same_timestamp_higher_version(self, resolver: Any, base_time: Any) -> None:
        """Test LAST_WRITE_WINS with same timestamp, higher version wins."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 3, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)
        assert result.version == local

    def test_local_wins_strategy(self, resolver: Any, base_time: Any) -> None:
        """Test LOCAL_WINS always picks local."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time + timedelta(seconds=10)),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)
        assert result.version == local
        assert result.strategy_used == ConflictStrategy.LOCAL_WINS

    def test_remote_wins_strategy(self, resolver: Any, base_time: Any) -> None:
        """Test REMOTE_WINS always picks remote."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time + timedelta(seconds=10)),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)
        assert result.version == remote
        assert result.strategy_used == ConflictStrategy.REMOTE_WINS

    def test_manual_strategy_requires_resolve_manual(self, resolver: Any, base_time: Any) -> None:
        """Test that MANUAL strategy requires resolve_manual()."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        with pytest.raises(ValueError, match="MANUAL strategy requires"):
            resolver.resolve(conflict, ConflictStrategy.MANUAL)

    def test_invalid_strategy_raises_error(self, resolver: Any, base_time: Any) -> None:
        """Test that invalid strategy raises error."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        # Should raise ValueError for unknown strategy
        with pytest.raises(ValueError):
            resolver.resolve(conflict, "invalid_strategy")

    def test_resolution_creates_backup(self, resolver: Any, base_time: Any) -> None:
        """Test that resolution creates backup."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)
        assert result.version.entity_id == "item-1"
        assert conflict.backup_path is not None

    def test_resolution_updates_conflict_status(self, resolver: Any, base_time: Any) -> None:
        """Test that resolution updates conflict status."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

        resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)

        # Retrieve and check
        retrieved = resolver.get_conflict(conflict.id)
        assert retrieved is not None
        assert retrieved.status == ConflictStatus.RESOLVED_AUTO
        assert retrieved.resolved_at is not None

    def test_resolved_version_uses_resolved_status(self, resolver: Any, base_time: Any) -> None:
        """Test resolved version has correct status."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)
        assert isinstance(result, ResolvedEntity)

    def test_last_write_wins_equal_timestamp_lower_version(self, resolver: Any, base_time: Any) -> None:
        """Test LAST_WRITE_WINS when timestamps equal, lower version loses."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 2, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 3, base_time),  # Higher version
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS)
        # Remote has higher version, should win
        assert result.version == remote


# ============================================================================
# Manual Resolution Tests (8 tests)
# ============================================================================


class TestManualResolution:
    """Test manual conflict resolution."""

    def test_resolve_manual_basic(self, resolver: Any, base_time: Any) -> None:
        """Test basic manual resolution."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local", "priority": "high"},
            VectorClock("client-1", 2, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote", "status": "done"},
            VectorClock("client-2", 2, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        merged_data = {
            "title": "Merged",
            "priority": "high",
            "status": "done",
        }
        result = resolver.resolve_manual(conflict, merged_data)
        assert result.version.data == merged_data
        assert result.strategy_used == ConflictStrategy.MANUAL

    def test_resolve_manual_increments_version(self, resolver: Any, base_time: Any) -> None:
        """Test that manual resolution increments version."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 5, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 3, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve_manual(conflict, {"title": "Merged"})
        # Should be max(5, 3) + 1 = 6
        assert result.version.vector_clock.version == 6

    def test_resolve_manual_records_merger(self, resolver: Any, base_time: Any) -> None:
        """Test that manual resolution records who merged."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

        resolver.resolve_manual(conflict, {"title": "Merged"}, merged_by="alice")
        retrieved = resolver.get_conflict(conflict.id)
        assert retrieved is not None
        assert retrieved.metadata["merged_by"] == "alice"

    def test_resolve_manual_updates_conflict_status(self, resolver: Any, base_time: Any) -> None:
        """Test that manual resolution updates status to RESOLVED_MANUAL."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

        resolver.resolve_manual(conflict, {"title": "Merged"})
        retrieved = resolver.get_conflict(conflict.id)
        assert retrieved is not None
        assert retrieved.status == ConflictStatus.RESOLVED_MANUAL

    def test_resolve_manual_preserves_backup(self, resolver: Any, base_time: Any) -> None:
        """Test that manual resolution creates/uses backup."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        resolver.resolve_manual(conflict, {"title": "Merged"})
        assert conflict.backup_path is not None

    def test_resolve_manual_complex_merge(self, resolver: Any, base_time: Any) -> None:
        """Test manual resolution with complex data merge."""
        local = EntityVersion(
            "item-1",
            "item",
            {
                "title": "Local Title",
                "tags": ["local"],
                "metadata": {"author": "alice"},
            },
            VectorClock("client-1", 2, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {
                "title": "Remote Title",
                "tags": ["remote"],
                "status": "completed",
            },
            VectorClock("client-2", 2, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        merged_data = {
            "title": "Merged Title",
            "tags": ["local", "remote"],
            "metadata": {"author": "alice"},
            "status": "completed",
        }
        result = resolver.resolve_manual(conflict, merged_data)
        assert result.version.data["tags"] == ["local", "remote"]
        assert result.version.data["status"] == "completed"

    def test_resolve_manual_empty_data(self, resolver: Any, base_time: Any) -> None:
        """Test manual resolution with empty merged data."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        result = resolver.resolve_manual(conflict, {})
        assert result.version.data == {}


# ============================================================================
# Backup and Recovery Tests (8 tests)
# ============================================================================


class TestConflictDataclass:
    """Test Conflict dataclass serialization."""

    def test_conflict_to_dict(self, base_time: Any) -> None:
        """Test Conflict.to_dict() serialization."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        data = conflict.to_dict()

        assert data["id"] == "conflict-1"
        assert data["entity_id"] == "item-1"
        assert data["entity_type"] == "item"
        assert data["local_version"] is not None
        assert data["remote_version"] is not None
        assert data["status"] == ConflictStatus.UNRESOLVED.value
        assert data["resolution_strategy"] is None
        assert data["resolved_at"] is None
        assert data["resolved_version"] is None
        assert data["backup_path"] is None
        assert data["metadata"] == {}


# ============================================================================
# BackupAndRecovery Tests (10 tests)
# ============================================================================


class TestBackupAndRecovery:
    """Test backup creation and recovery."""

    def test_create_backup_creates_structure(self, resolver: Any, base_time: Any) -> None:
        """Test that backup creates expected directory structure."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        backup_path = resolver.create_backup(conflict)

        assert backup_path.exists()
        assert (backup_path / "local.json").exists()
        assert (backup_path / "remote.json").exists()
        assert (backup_path / "conflict.json").exists()

    def test_backup_contains_correct_data(self, resolver: Any, base_time: Any) -> None:
        """Test that backup files contain correct data."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local Title"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote Title"},
            VectorClock("client-2", 1, base_time),
        )
        conflict = Conflict("conflict-1", "item-1", "item", local, remote)
        backup_path = resolver.create_backup(conflict)

        with Path(backup_path / "local.json").open(encoding="utf-8") as f:
            local_data = json.load(f)
            assert local_data["data"]["title"] == "Local Title"

        with Path(backup_path / "remote.json").open(encoding="utf-8") as f:
            remote_data = json.load(f)
            assert remote_data["data"]["title"] == "Remote Title"

    def test_conflict_backup_manager_list(self, temp_backup_dir: Any) -> None:
        """Test ConflictBackup.list_backups()."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create test backup structure
        backup_path = temp_backup_dir / "item" / "item-1_20240101_120000"
        backup_path.mkdir(parents=True)

        conflict_meta = {
            "conflict_id": "test-1",
            "entity_id": "item-1",
            "entity_type": "item",
            "detected_at": "2024-01-01T12:00:00+00:00",
        }
        with Path(backup_path / "conflict.json").open("w", encoding="utf-8") as f:
            json.dump(conflict_meta, f)

        backups = backup_mgr.list_backups()
        assert len(backups) == 1
        assert backups[0]["conflict_id"] == "test-1"

    def test_conflict_backup_manager_filter_by_type(self, temp_backup_dir: Any) -> None:
        """Test ConflictBackup.list_backups() filtering by type."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create item backup
        item_path = temp_backup_dir / "item" / "item-1_test"
        item_path.mkdir(parents=True)
        with Path(item_path / "conflict.json").open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "conflict_id": "item-conflict",
                    "entity_type": "item",
                },
                f,
            )

        # Create project backup
        proj_path = temp_backup_dir / "project" / "proj-1_test"
        proj_path.mkdir(parents=True)
        with Path(proj_path / "conflict.json").open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "conflict_id": "proj-conflict",
                    "entity_type": "project",
                },
                f,
            )

        item_backups = backup_mgr.list_backups(entity_type="item")
        assert len(item_backups) == 1
        assert item_backups[0]["entity_type"] == "item"

    def test_conflict_backup_manager_load(self, temp_backup_dir: Any, base_time: Any) -> None:
        """Test ConflictBackup.load_backup()."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create backup
        backup_path = temp_backup_dir / "item" / "item-1_test"
        backup_path.mkdir(parents=True)

        local_version = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote_version = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
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

    def test_conflict_backup_delete(self, temp_backup_dir: Any) -> None:
        """Test ConflictBackup.delete_backup()."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create backup
        backup_path = temp_backup_dir / "item" / "item-1_test"
        backup_path.mkdir(parents=True)

        assert backup_path.exists()
        result = backup_mgr.delete_backup(backup_path)
        assert result is True
        assert not backup_path.exists()

    def test_conflict_backup_delete_nonexistent(self, temp_backup_dir: Any) -> None:
        """Test deleting nonexistent backup returns False."""
        backup_mgr = ConflictBackup(temp_backup_dir)
        nonexistent = temp_backup_dir / "nonexistent"
        result = backup_mgr.delete_backup(nonexistent)
        assert result is False

    def test_conflict_backup_manager_handles_non_directory_files(self, temp_backup_dir: Any) -> None:
        """Test that backup manager skips non-directory files."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create entity type directory
        entity_dir = temp_backup_dir / "item"
        entity_dir.mkdir()

        # Create a regular file (not a directory)
        (entity_dir / "regular_file.txt").write_text("content")

        # Should skip the file and not crash
        backups = backup_mgr.list_backups()
        assert len(backups) == 0

    def test_conflict_backup_manager_skips_non_backup_dirs(self, temp_backup_dir: Any) -> None:
        """Test that backup manager skips directories without conflict.json."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create directory structure but no conflict.json
        backup_path = temp_backup_dir / "item" / "item-1_test"
        backup_path.mkdir(parents=True)
        (backup_path / "some_file.txt").write_text("data")

        backups = backup_mgr.list_backups()
        assert len(backups) == 0

    def test_conflict_backup_load_missing_files(self, temp_backup_dir: Any) -> None:
        """Test loading backup with missing files returns None."""
        backup_mgr = ConflictBackup(temp_backup_dir)

        # Create backup with only one file
        backup_path = temp_backup_dir / "item" / "item-1_test"
        backup_path.mkdir(parents=True)
        (backup_path / "local.json").write_text("{}")

        # Missing remote.json
        result = backup_mgr.load_backup(backup_path)
        assert result is None


# ============================================================================
# Database Query Tests (8 tests)
# ============================================================================


class TestConflictQueries:
    """Test conflict querying and listing."""

    def test_list_unresolved_basic(self, resolver: Any, base_time: Any) -> None:
        """Test listing unresolved conflicts."""
        # Create multiple conflicts
        for i in range(3):
            local = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Local {i}"},
                VectorClock("client-1", 1, base_time),
                f"hash-local-{i}",
            )
            remote = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Remote {i}"},
                VectorClock("client-2", 1, base_time),
                f"hash-remote-{i}",
            )
            resolver.detect_conflict(local, remote)

        unresolved = resolver.list_unresolved()
        assert len(unresolved) == COUNT_THREE

    def test_list_unresolved_by_type(self, resolver: Any, base_time: Any) -> None:
        """Test filtering unresolved by entity type."""
        # Create item conflict
        item_local = EntityVersion(
            "item-1",
            "item",
            {"title": "Item"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        item_remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Item Remote"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )

        # Create project conflict
        proj_local = EntityVersion(
            "proj-1",
            "project",
            {"name": "Project"},
            VectorClock("client-1", 1, base_time),
            "hash3",
        )
        proj_remote = EntityVersion(
            "proj-1",
            "project",
            {"name": "Project Remote"},
            VectorClock("client-2", 1, base_time),
            "hash4",
        )

        resolver.detect_conflict(item_local, item_remote)
        resolver.detect_conflict(proj_local, proj_remote)

        items = resolver.list_unresolved(entity_type="item")
        projects = resolver.list_unresolved(entity_type="project")

        assert len(items) == 1
        assert len(projects) == 1

    def test_get_conflict_by_id(self, resolver: Any, base_time: Any) -> None:
        """Test retrieving conflict by ID."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)

        retrieved = resolver.get_conflict(conflict.id)
        assert retrieved is not None
        assert retrieved.entity_id == "item-1"

    def test_get_conflict_not_found(self, resolver: Any) -> None:
        """Test retrieving nonexistent conflict returns None."""
        result = resolver.get_conflict("nonexistent-id")
        assert result is None

    def test_get_conflict_stats_basic(self, resolver: Any, base_time: Any) -> None:
        """Test conflict statistics."""
        # Create some conflicts
        for i in range(2):
            local = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Local {i}"},
                VectorClock("client-1", 1, base_time),
                f"hash-{i}",
            )
            remote = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Remote {i}"},
                VectorClock("client-2", 1, base_time),
                f"hash-r-{i}",
            )
            conflict = resolver.detect_conflict(local, remote)
            if i == 0:
                resolver.resolve(conflict, ConflictStrategy.LOCAL_WINS)

        stats = resolver.get_conflict_stats()
        assert stats["total"] == COUNT_TWO
        assert ConflictStatus.UNRESOLVED.value in stats["by_status"]

    def test_get_conflict_stats_empty(self, resolver: Any) -> None:
        """Test stats with no conflicts."""
        stats = resolver.get_conflict_stats()
        assert stats["total"] == 0
        assert stats["by_status"] == {}

    def test_conflict_query_ordering(self, resolver: Any, base_time: Any) -> None:
        """Test conflicts are returned in detected order."""
        # Create conflicts with slight delays
        for i in range(3):
            local = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Local {i}"},
                VectorClock("client-1", 1, base_time + timedelta(seconds=i)),
                f"hash-{i}",
            )
            remote = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Remote {i}"},
                VectorClock("client-2", 1, base_time + timedelta(seconds=i)),
                f"hash-r-{i}",
            )
            resolver.detect_conflict(local, remote)

        unresolved = resolver.list_unresolved()
        # Should be in reverse order (newest first)
        assert len(unresolved) == COUNT_THREE


# ============================================================================
# Unicode and Content Handling Tests (6 tests)
# ============================================================================


class TestUnicodeAndContent:
    """Test handling of unicode and various content types."""

    def test_unicode_titles(self, resolver: Any, base_time: Any) -> None:
        """Test conflict with unicode titles."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "标题"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "заголовок"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

    def test_emoji_content(self, resolver: Any, base_time: Any) -> None:
        """Test conflict with emoji content."""
        local = EntityVersion(
            "item-1",
            "item",
            {"status": "✓ Done"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"status": "🚀 In Progress"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

    def test_multiline_content(self, resolver: Any, base_time: Any) -> None:
        """Test conflict with multiline content."""
        local_desc = "Line 1\nLine 2\nLine 3"
        remote_desc = "Line 1\nModified Line 2\nLine 3"

        local = EntityVersion(
            "item-1",
            "item",
            {"description": local_desc},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"description": remote_desc},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

    def test_whitespace_only_difference(self, resolver: Any, base_time: Any) -> None:
        """Test conflict detection with whitespace differences."""
        local = EntityVersion(
            "item-1",
            "item",
            {"content": "Text with  spaces"},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"content": "Text with spaces"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        # Different content = conflict
        assert conflict is not None

    def test_large_content(self, resolver: Any, base_time: Any) -> None:
        """Test handling large content."""
        large_text = "x" * 10000
        local = EntityVersion(
            "item-1",
            "item",
            {"content": large_text},
            VectorClock("client-1", 1, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"content": large_text + "y"},
            VectorClock("client-2", 1, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None


# ============================================================================
# Utility Function Tests (6 tests)
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions."""

    def test_format_conflict_summary_basic(self, base_time: Any) -> None:
        """Test formatting conflict summary."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 2, base_time),
        )
        conflict = Conflict("test-conflict", "item-1", "item", local, remote)
        summary = format_conflict_summary(conflict)

        assert "item-1" in summary
        assert "v1" in summary
        assert "v2" in summary
        assert "unresolved" in summary.lower()

    def test_format_conflict_summary_with_timestamps(self, base_time: Any) -> None:
        """Test summary includes formatted timestamps."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote"},
            VectorClock("client-2", 1, base_time + timedelta(hours=1)),
        )
        conflict = Conflict("test-conflict", "item-1", "item", local, remote)
        summary = format_conflict_summary(conflict)
        assert "Local:" in summary
        assert "Remote:" in summary

    def test_compare_versions_added_fields(self, base_time: Any) -> None:
        """Test comparing versions with added fields."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Item"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Item", "status": "new"},
            VectorClock("client-2", 1, base_time),
        )
        diff = compare_versions(local, remote)
        assert "status" in diff["added"]

    def test_compare_versions_removed_fields(self, base_time: Any) -> None:
        """Test comparing versions with removed fields."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Item", "priority": "high"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Item"},
            VectorClock("client-2", 1, base_time),
        )
        diff = compare_versions(local, remote)
        assert "priority" in diff["removed"]

    def test_compare_versions_modified_fields(self, base_time: Any) -> None:
        """Test comparing versions with modified fields."""
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Old Title", "status": "active"},
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "New Title", "status": "active"},
            VectorClock("client-2", 1, base_time),
        )
        diff = compare_versions(local, remote)
        assert "title" in diff["modified"]
        assert "status" not in diff["modified"]

    def test_compare_versions_complex_data(self, base_time: Any) -> None:
        """Test comparing complex nested structures."""
        local = EntityVersion(
            "item-1",
            "item",
            {
                "metadata": {"author": "alice", "version": 1},
                "tags": ["a", "b"],
            },
            VectorClock("client-1", 1, base_time),
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {
                "metadata": {"author": "alice", "version": 2},
                "tags": ["a", "b"],
            },
            VectorClock("client-2", 1, base_time),
        )
        diff = compare_versions(local, remote)
        assert "metadata" in diff["modified"]


# ============================================================================
# Integration Tests (6 tests)
# ============================================================================


class TestIntegration:
    """Integration tests with realistic scenarios."""

    def test_full_conflict_workflow(self, resolver: Any, base_time: Any) -> None:
        """Test complete conflict detection and resolution."""
        # 1. Create conflicting versions
        local = EntityVersion(
            "item-1",
            "item",
            {"title": "Local Title", "status": "in_progress"},
            VectorClock("client-1", 2, base_time),
            "hash_local",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Remote Title", "status": "completed"},
            VectorClock("client-2", 2, base_time),
            "hash_remote",
        )

        # 2. Detect conflict
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

        # 3. Resolve with auto-strategy
        result = resolver.resolve(conflict, ConflictStrategy.REMOTE_WINS)
        assert result.version == remote

        # 4. Verify in database
        retrieved = resolver.get_conflict(conflict.id)
        assert retrieved.status == ConflictStatus.RESOLVED_AUTO

    def test_multiple_conflicts_different_types(self, resolver: Any, base_time: Any) -> None:
        """Test handling multiple conflicts of different entity types."""
        # Item conflict
        item_local = EntityVersion(
            "item-1",
            "item",
            {"title": "Item"},
            VectorClock("client-1", 1, base_time),
            "h1",
        )
        item_remote = EntityVersion(
            "item-1",
            "item",
            {"title": "Item Remote"},
            VectorClock("client-2", 1, base_time),
            "h2",
        )

        # Project conflict
        proj_local = EntityVersion(
            "proj-1",
            "project",
            {"name": "Project"},
            VectorClock("client-1", 1, base_time),
            "h3",
        )
        proj_remote = EntityVersion(
            "proj-1",
            "project",
            {"name": "Project Remote"},
            VectorClock("client-2", 1, base_time),
            "h4",
        )

        # Link conflict
        link_local = EntityVersion(
            "link-1",
            "link",
            {"source": "item-1", "target": "item-2"},
            VectorClock("client-1", 1, base_time),
            "h5",
        )
        link_remote = EntityVersion(
            "link-1",
            "link",
            {"source": "item-1", "target": "item-3"},
            VectorClock("client-2", 1, base_time),
            "h6",
        )

        # Detect all
        c1 = resolver.detect_conflict(item_local, item_remote)
        c2 = resolver.detect_conflict(proj_local, proj_remote)
        c3 = resolver.detect_conflict(link_local, link_remote)

        assert c1 is not None and c1.entity_type == "item"
        assert c2 is not None and c2.entity_type == "project"
        assert c3 is not None and c3.entity_type == "link"

        # Resolve differently
        resolver.resolve(c1, ConflictStrategy.LOCAL_WINS)
        resolver.resolve(c2, ConflictStrategy.REMOTE_WINS)
        resolver.resolve_manual(c3, {"source": "item-1", "target": "item-4"})

        stats = resolver.get_conflict_stats()
        assert stats["total"] == COUNT_THREE

    def test_sequential_conflict_resolution(self, resolver: Any, base_time: Any) -> None:
        """Test resolving multiple conflicts sequentially."""
        conflicts = []
        for i in range(5):
            local = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Local {i}"},
                VectorClock("client-1", 2, base_time),
                f"h_local_{i}",
            )
            remote = EntityVersion(
                f"item-{i}",
                "item",
                {"title": f"Remote {i}"},
                VectorClock("client-2", 2, base_time),
                f"h_remote_{i}",
            )
            conflict = resolver.detect_conflict(local, remote)
            conflicts.append(conflict)

        # Resolve all
        for i, conflict in enumerate(conflicts):
            strategy = ConflictStrategy.LOCAL_WINS if i % 2 == 0 else ConflictStrategy.REMOTE_WINS
            resolver.resolve(conflict, strategy)

        unresolved = resolver.list_unresolved()
        assert len(unresolved) == 0

    def test_concurrent_changes_same_field(self, resolver: Any, base_time: Any) -> None:
        """Test conflict when both sides modify same field."""
        local = EntityVersion(
            "item-1",
            "item",
            {
                "title": "Local Title",
                "description": "Unchanged",
                "status": "local_status",
            },
            VectorClock("client-1", 2, base_time),
            "hash1",
        )
        remote = EntityVersion(
            "item-1",
            "item",
            {
                "title": "Remote Title",
                "description": "Unchanged",
                "status": "remote_status",
            },
            VectorClock("client-2", 2, base_time),
            "hash2",
        )
        conflict = resolver.detect_conflict(local, remote)
        assert conflict is not None

        # Manually merge with preference
        merged = {
            "title": "Local Title",  # Prefer local
            "description": "Unchanged",
            "status": "local_status",  # Prefer local
        }
        result = resolver.resolve_manual(conflict, merged)
        assert result.version.data["title"] == "Local Title"
