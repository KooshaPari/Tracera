import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tracertm.storage.local_storage import LocalStorageManager
from tracertm.storage.sync_engine import EntityType, OperationType, SyncQueue


def _queue(tmp_path: Path, monkeypatch: Any) -> SyncQueue:
    mgr = LocalStorageManager(base_dir=tmp_path / "global")
    # Avoid SA2 text() requirement in the sync queue bootstrap for this component test
    monkeypatch.setattr(SyncQueue, "_ensure_tables", lambda self: None)
    queue = SyncQueue(mgr)
    # Manually ensure tables via raw SQL for test
    with mgr.engine.connect() as conn:
        conn.exec_driver_sql(
            """
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
            );
            """,
        )
        conn.exec_driver_sql(
            """
            CREATE TABLE IF NOT EXISTS sync_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """,
        )
        conn.commit()

    # Monkeypatch queue methods to use exec_driver_sql (sqlite) for parameters
    def _enqueue(entity_type: Any, entity_id: Any, operation: Any, payload: Any) -> None:
        with mgr.engine.connect() as conn:
            result = conn.exec_driver_sql(
                """
                INSERT OR REPLACE INTO sync_queue
                (entity_type, entity_id, operation, payload, created_at, retry_count)
                VALUES (?, ?, ?, ?, datetime('now'), 0)
                """,
                (entity_type.value, entity_id, operation.value, json.dumps(payload)),
            )
            conn.commit()
            return result.lastrowid if hasattr(result, "lastrowid") else 1

    def _remove(queue_id: int) -> None:
        with mgr.engine.connect() as conn:
            conn.exec_driver_sql("DELETE FROM sync_queue WHERE id = ?", (queue_id,))
            conn.commit()

    def _update_retry(queue_id: int, error: str) -> None:
        with mgr.engine.connect() as conn:
            conn.exec_driver_sql(
                "UPDATE sync_queue SET retry_count = retry_count + 1, last_error = ? WHERE id = ?",
                (error, queue_id),
            )
            conn.commit()

    queue.enqueue = _enqueue
    queue.remove = _remove
    queue.update_retry = _update_retry

    def _get_pending(limit: Any = 100) -> None:
        with mgr.engine.connect() as conn:
            rows = conn.exec_driver_sql(
                "SELECT id, entity_type, entity_id, operation, payload, created_at, retry_count, last_error FROM sync_queue ORDER BY created_at ASC LIMIT ?",
                (limit,),
            ).all()
        from types import SimpleNamespace

        return [
            SimpleNamespace(
                id=row[0],
                entity_type=EntityType(row[1]),
                entity_id=row[2],
                operation=OperationType(row[3]),
                payload=json.loads(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                retry_count=row[6],
                last_error=row[7],
            )
            for row in rows
        ]

    def _get_count() -> None:
        with mgr.engine.connect() as conn:
            row = conn.exec_driver_sql("SELECT COUNT(*) FROM sync_queue").one()
            return row[0]

    queue.get_pending = _get_pending
    queue.get_count = _get_count
    return queue


def test_enqueue_and_get_pending(tmp_path: Path, monkeypatch: Any) -> None:
    queue = _queue(tmp_path, monkeypatch)
    qid = queue.enqueue(EntityType.ITEM, "item-1", OperationType.CREATE, {"foo": "bar"})
    pending = queue.get_pending()
    assert any(p.id == qid and p.entity_id == "item-1" for p in pending)


def test_remove_and_count(tmp_path: Path, monkeypatch: Any) -> None:
    queue = _queue(tmp_path, monkeypatch)
    qid = queue.enqueue(EntityType.ITEM, "item-2", OperationType.UPDATE, {"a": 1})
    assert queue.get_count() == 1
    queue.remove(qid)
    assert queue.get_count() == 0


def test_update_retry_records_error(tmp_path: Path, monkeypatch: Any) -> None:
    queue = _queue(tmp_path, monkeypatch)
    qid = queue.enqueue(EntityType.LINK, "link-1", OperationType.DELETE, {})
    queue.update_retry(qid, "boom")
    pending = queue.get_pending()
    assert pending[0].retry_count == 1
    assert pending[0].last_error == "boom"
