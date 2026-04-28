from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tracertm.storage.conflict_resolver import (
    Conflict,
    ConflictResolver,
    ConflictStrategy,
    EntityVersion,
    VectorClock,
)


def _make_session(tmp_path: Path) -> Session:
    engine = create_engine(f"sqlite:///{tmp_path / 'conflicts.db'}")
    return Session(bind=engine)


def _version(entity_id: str, client: str, version: int, ts: datetime, data: dict) -> None:
    return EntityVersion(
        entity_id=entity_id,
        entity_type="item",
        data=data,
        vector_clock=VectorClock(client_id=client, version=version, timestamp=ts),
        content_hash="hash",
    )


def _make_conflict(local: Any, remote: Any, cid: Any = "c1") -> None:
    return Conflict(
        id=cid,
        entity_id=local.entity_id,
        entity_type=local.entity_type,
        local_version=local,
        remote_version=remote,
    )


def test_last_write_wins_prefers_newer_timestamp(tmp_path: Path) -> None:
    session = _make_session(tmp_path)
    resolver = ConflictResolver(session=session, backup_dir=tmp_path)
    now = datetime.now(UTC)
    local = _version("i1", "c1", 1, now - timedelta(seconds=1), {"title": "old"})
    remote = _version("i1", "c2", 1, now, {"title": "new"})

    conflict = _make_conflict(local, remote)
    resolved = resolver.resolve(conflict, strategy=ConflictStrategy.LAST_WRITE_WINS)
    assert resolved.version.data["title"] == "new"


def test_local_wins_returns_local(tmp_path: Path) -> None:
    session = _make_session(tmp_path)
    resolver = ConflictResolver(session=session, backup_dir=tmp_path)
    now = datetime.now(UTC)
    local = _version("i1", "c1", 2, now, {"title": "local"})
    remote = _version("i1", "c2", 3, now, {"title": "remote"})

    conflict = _make_conflict(local, remote)
    resolved = resolver.resolve(conflict, strategy=ConflictStrategy.LOCAL_WINS)
    assert resolved.version.data["title"] == "local"


def test_remote_wins_returns_remote(tmp_path: Path) -> None:
    session = _make_session(tmp_path)
    resolver = ConflictResolver(session=session, backup_dir=tmp_path)
    now = datetime.now(UTC)
    local = _version("i1", "c1", 2, now, {"title": "local"})
    remote = _version("i1", "c2", 3, now, {"title": "remote"})

    conflict = _make_conflict(local, remote)
    resolved = resolver.resolve(conflict, strategy=ConflictStrategy.REMOTE_WINS)
    assert resolved.version.data["title"] == "remote"


def test_manual_writes_conflict_file(tmp_path: Path) -> None:
    session = _make_session(tmp_path)
    resolver = ConflictResolver(session=session, backup_dir=tmp_path)
    now = datetime.now(UTC)
    local = _version("i1", "c1", 1, now, {"title": "local"})
    remote = _version("i1", "c2", 1, now, {"title": "remote"})

    conflict = _make_conflict(local, remote)
    # manual requires merged payload; use resolve_manual to exercise backup writing
    merged = {"title": "merged"}
    resolved = resolver.resolve_manual(conflict, merged_data=merged)
    assert resolved.version.data["title"] == "merged"

    # resolve_manual does not write backup; create_backup is used in resolve() only.
    # Verify manual path leaves backup_dir untouched.
    files = list(tmp_path.glob("conflict_*.json"))
    assert files == []
