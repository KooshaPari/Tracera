from types import SimpleNamespace
from unittest.mock import AsyncMock
from tests.test_constants import COUNT_TWO


import pytest

from tracertm.services.advanced_traceability_service import AdvancedTraceabilityService


class _Item(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_find_all_paths(monkeypatch, async_session) -> None:  # noqa: ARG001
    svc = AdvancedTraceabilityService(async_session)
    path_links = [
        SimpleNamespace(target_item_id="i2"),
        SimpleNamespace(target_item_id="i3"),
    ]
    # Use AsyncMock for async method
    svc.links.get_by_source = AsyncMock(side_effect=lambda src: path_links if src == "i1" else [])  # type: ignore[assignment]

    paths = await svc.find_all_paths("i1", "i2", max_depth=3)
    assert any(p.target_id == "i2" for p in paths)


@pytest.mark.asyncio
async def test_coverage_gaps(monkeypatch, async_session) -> None:
    source_item = _Item(id="s1", view="FEATURE")
    target_item = _Item(id="t1", view="TEST")

    async def get_by_view(project_id, view, status=None, limit=100, offset=0):  # noqa: ARG001
        return [source_item] if view == "FEATURE" else [target_item]

    async def get_by_source(item_id):
        return [] if item_id == "s1" else []

    async def get_by_id(item_id):
        return target_item if item_id == "t1" else None

    svc = AdvancedTraceabilityService(async_session)
    monkeypatch.setattr(svc.items, "get_by_view", get_by_view)
    monkeypatch.setattr(svc.links, "get_by_source", get_by_source)
    monkeypatch.setattr(svc.items, "get_by_id", get_by_id)

    gaps = await svc.coverage_gaps("proj-1", "FEATURE", "TEST")
    assert "s1" in gaps


@pytest.mark.asyncio
async def test_circular_dependency_check(monkeypatch, async_session) -> None:
    items = [
        _Item(id="a"),
        _Item(id="b"),
    ]

    async def get_by_source(node):
        if node == "a":
            return [SimpleNamespace(target_item_id="b")]
        if node == "b":
            return [SimpleNamespace(target_item_id="a")]
        return []

    svc = AdvancedTraceabilityService(async_session)
    # Use AsyncMock for async method
    svc.items.query = AsyncMock(return_value=items)  # type: ignore[assignment]
    monkeypatch.setattr(svc.links, "get_by_source", get_by_source)

    cycles = await svc.circular_dependency_check("proj-1")
    assert cycles and len(cycles[0]) >= COUNT_TWO
