from types import SimpleNamespace
from typing import Any

import pytest

from tests.test_constants import COUNT_FIVE
from tracertm.core.concurrency import ConcurrencyError
from tracertm.services.bulk_service import BulkOperationService, BulkPreview

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_preview_bulk_update_warns_on_large_operation(async_session: Any, monkeypatch: Any) -> None:
    service = BulkOperationService(async_session)

    fake_items = [SimpleNamespace(id=f"item-{i}", title=f"Item {i}", status="todo", version=1) for i in range(120)]

    async def fake_query(project_id: Any, _filters: Any) -> None:
        return fake_items

    monkeypatch.setattr(service.items, "query", fake_query)

    preview: BulkPreview = await service.preview_bulk_update(
        project_id="proj-1",
        filters={"status": "todo"},
        updates={"status": "complete"},
    )

    assert preview.total_count == 120
    assert any("Large operation" in w for w in preview.validation_warnings)
    assert preview.estimated_duration_ms == 120 * 10
    assert len(preview.sample_items) == COUNT_FIVE


@pytest.mark.asyncio
async def test_execute_bulk_update_handles_conflicts_and_logs(async_session: Any, monkeypatch: Any) -> None:
    service = BulkOperationService(async_session)

    item_ok = SimpleNamespace(id="ok", version=1, status="todo")
    item_conflict = SimpleNamespace(id="conflict", version=2, status="todo")

    async def fake_query(project_id: Any, _filters: Any) -> None:
        return [item_ok, item_conflict]

    async def fake_update(item_id: Any, expected_version: Any, **updates: Any) -> None:
        if item_id == "conflict":
            msg = "version mismatch"
            raise ConcurrencyError(msg)
        item_ok.status = updates["status"]
        item_ok.version += 1
        return item_ok

    logged = {}

    async def fake_log(**data: Any) -> None:
        logged.update(data)

    monkeypatch.setattr(service.items, "query", fake_query)
    monkeypatch.setattr(service.items, "update", fake_update)
    monkeypatch.setattr(service.events, "log", fake_log)

    result = await service.execute_bulk_update(
        project_id="proj-1",
        filters={"status": "todo"},
        updates={"status": "in_progress"},
        agent_id="agent-1",
        skip_preview=True,
    )

    assert len(result) == 1
    assert logged["event_type"] == "bulk_update"
    assert logged["data"]["conflict_count"] == 1


@pytest.mark.asyncio
async def test_execute_bulk_update_blocks_on_warnings(async_session: Any, monkeypatch: Any) -> None:
    service = BulkOperationService(async_session)

    fake_preview = BulkPreview(
        total_count=10,
        sample_items=[],
        validation_warnings=["danger"],
        estimated_duration_ms=100,
    )

    async def fake_preview_fn(project_id: Any, filters: Any, _updates: Any) -> None:
        return fake_preview

    monkeypatch.setattr(service, "preview_bulk_update", fake_preview_fn)

    with pytest.raises(ValueError):
        await service.execute_bulk_update(
            "proj-1",
            filters={},
            updates={"status": "complete"},
            agent_id="agent-1",
            skip_preview=False,
        )
