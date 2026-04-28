from pathlib import Path

from sqlalchemy import text

from tracertm.storage.local_storage import LocalStorageManager


def test_init_project_creates_trace_structure(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    project_path = tmp_path / "repo"
    project_path.mkdir()

    trace_dir, project_id = mgr.init_project(project_path, project_name="Proj")

    assert trace_dir.exists()
    assert (trace_dir / "project.yaml").exists()
    assert (trace_dir / "epics").is_dir()
    assert project_id


def test_register_project_and_index_roundtrip(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    project_path = tmp_path / "repo"
    project_path.mkdir()
    _trace_dir, _project_id = mgr.init_project(project_path, project_name="Proj")

    mgr.register_project(project_path)

    with mgr.get_session() as session:
        rows = session.execute(text("SELECT name FROM project_registry"))
        assert rows.fetchall()


def test_queue_sync_and_clear(tmp_path: Path) -> None:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    project_path = tmp_path / "repo"
    project_path.mkdir()
    mgr.init_project(project_path, project_name="Proj")

    mgr.queue_sync("item", "item-1", "create", {"foo": "bar"})
    pending = mgr.get_sync_queue()
    assert len(pending) == 1

    mgr.clear_sync_queue_entry(pending[0]["id"])
    pending_after = mgr.get_sync_queue()
    assert pending_after == []
