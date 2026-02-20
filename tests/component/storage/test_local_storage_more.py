from pathlib import Path

import pytest
from sqlalchemy import text

from tracertm.storage.local_storage import LocalStorageManager


def test_register_project_requires_trace_dir(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    with pytest.raises(ValueError):
        mgr.register_project(tmp_path / "missing")


def test_register_project_is_idempotent(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    repo = tmp_path / "repo"
    repo.mkdir()
    _trace_dir, project_id = mgr.init_project(repo, project_name="Proj")

    first = mgr.register_project(repo)
    second = mgr.register_project(repo)
    assert first == second == project_id

    with mgr.engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM project_registry")).scalar()
        assert count == 1


def test_queue_sync_records_entry(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    repo = tmp_path / "repo"
    repo.mkdir()
    mgr.init_project(repo, project_name="Proj")

    mgr.queue_sync("item", "item-1", "create", {"a": 1})
    pending = mgr.get_sync_queue()
    assert any(p["entity_id"] == "item-1" for p in pending)
