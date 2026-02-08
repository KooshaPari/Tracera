from types import SimpleNamespace
from typing import Never

import pytest

from tracertm.models.item import Item
from tracertm.services.bulk_operation_service import BulkOperationService

pytestmark = pytest.mark.integration


def _seed_items(session, project_id="proj-1", count=5, status="todo", view="FEATURE"):
    items = []
    for i in range(count):
        item = Item(
            id=f"item-{i}",
            project_id=project_id,
            title=f"Item {i}",
            view=view,
            item_type="feature",
            status=status,
            priority="medium",
            owner=None,
        )
        session.add(item)
        items.append(item)
    session.commit()
    return items


def test_bulk_update_preview_warnings(sync_session) -> None:
    _seed_items(sync_session, count=120)
    svc = BulkOperationService(sync_session)  # type: ignore[arg-type]

    preview = svc.bulk_update_preview(
        project_id="proj-1", filters={"status": "todo"}, updates={"status": "done"}, limit=3,
    )

    assert preview["total_count"] == 120
    assert preview["estimated_duration_ms"] == 1200
    assert any("Large operation" in w for w in preview["warnings"])


def test_bulk_update_items_commits_and_logs(sync_session) -> None:
    items = _seed_items(sync_session, count=2)
    svc = BulkOperationService(sync_session)

    result = svc.bulk_update_items(
        project_id="proj-1", filters={"status": "todo"}, updates={"status": "in_progress"}, agent_id="agent-1",
    )

    assert result == {"items_updated": 2}
    refreshed = sync_session.query(Item).all()
    assert all(i.status == "in_progress" for i in refreshed)
    # Events logged
    from tracertm.models.event import Event

    assert sync_session.query(Event).count() == 2


def test_bulk_update_items_rollback_on_failure(sync_session, monkeypatch) -> None:
    _seed_items(sync_session, count=1)
    svc = BulkOperationService(sync_session)

    rolled_back = SimpleNamespace(value=False)

    def fake_rollback() -> None:
        rolled_back.value = True

    def failing_commit() -> Never:
        msg = "commit fail"
        raise RuntimeError(msg)

    monkeypatch.setattr(sync_session, "rollback", fake_rollback)
    monkeypatch.setattr(sync_session, "commit", failing_commit)

    with pytest.raises(RuntimeError):
        svc.bulk_update_items("proj-1", {"status": "todo"}, {"status": "done"})

    assert rolled_back.value is True


def test_bulk_delete_items_marks_deleted(sync_session) -> None:
    items = _seed_items(sync_session, count=3, status="todo")
    svc = BulkOperationService(sync_session)

    result = svc.bulk_delete_items("proj-1", {"status": "todo"})
    assert result["items_deleted"] == 3
    assert all(item.deleted_at is not None for item in items)
