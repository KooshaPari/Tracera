import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace

from tracertm.services.chaos_mode_service import ChaosModeService

pytestmark = pytest.mark.integration


class _FakeItem(SimpleNamespace):
    pass


class _FakeLink(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_detect_zombies_finds_orphan_stale(monkeypatch, async_session):
    stale_item = _FakeItem(
        id="i1",
        title="Stale",
        status="todo",
        updated_at=datetime.utcnow() - timedelta(days=40),
    )
    fresh_item = _FakeItem(
        id="i2",
        title="Fresh",
        status="todo",
        updated_at=datetime.utcnow(),
    )

    svc = ChaosModeService(async_session)
    async def fake_items(project_id, filters):
        return [stale_item, fresh_item]

    async def empty_links(item_id):
        return []

    monkeypatch.setattr(svc.items, "query", fake_items)
    monkeypatch.setattr(svc.links, "get_by_source", empty_links)
    monkeypatch.setattr(svc.links, "get_by_target", empty_links)

    result = await svc.detect_zombies("proj-1", days_inactive=30)

    assert result["zombie_count"] == 1
    assert result["zombies"][0]["item_id"] == "i1"


@pytest.mark.asyncio
async def test_analyze_impact_returns_error_when_missing(monkeypatch, async_session):
    svc = ChaosModeService(async_session)
    async def get_none(item_id):
        return None

    monkeypatch.setattr(svc.items, "get_by_id", get_none)

    result = await svc.analyze_impact("proj", "missing")
    assert result["error"] == "Item not found"


@pytest.mark.asyncio
async def test_analyze_impact_counts_links(monkeypatch, async_session):
    item = _FakeItem(id="i1", title="Item", status="todo")
    direct = [_FakeLink(target_item_id="i2", link_type="depends_on")]
    deps = [_FakeLink(source_item_id="i3", target_item_id="i1", link_type="blocks")]

    svc = ChaosModeService(async_session)
    async def get_item(item_id):
        return item

    async def get_by_source(iid):
        return direct if iid == "i1" else []

    async def get_by_target(iid):
        return deps if iid == "i1" else []

    monkeypatch.setattr(svc.items, "get_by_id", get_item)
    monkeypatch.setattr(svc.links, "get_by_source", get_by_source)
    monkeypatch.setattr(svc.links, "get_by_target", get_by_target)

    result = await svc.analyze_impact("proj", "i1")
    assert result["direct_impact"] == 1
    assert result["dependencies"] == 1
    assert result["total_impact"] >= 1
