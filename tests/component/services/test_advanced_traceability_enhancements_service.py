from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from tracertm.services.advanced_traceability_enhancements_service import (
    AdvancedTraceabilityEnhancementsService,
)


@pytest.mark.asyncio
async def test_detect_circular_dependencies(monkeypatch, async_session) -> None:  # noqa: ARG001
    items = [
        SimpleNamespace(id="a", outgoing_links=[SimpleNamespace(target_item_id="b")]),
        SimpleNamespace(id="b", outgoing_links=[SimpleNamespace(target_item_id="a")]),
    ]
    svc = AdvancedTraceabilityEnhancementsService(async_session)
    # Use AsyncMock to return awaitable
    svc.items.query = AsyncMock(return_value=items)  # type: ignore[assignment]

    result = await svc.detect_circular_dependencies("proj-1")
    assert result["has_cycles"] is True
    assert result["cycle_count"] >= 1


@pytest.mark.asyncio
async def test_coverage_gap_analysis(monkeypatch, async_session) -> None:  # noqa: ARG001
    items = [
        SimpleNamespace(id="s1", view="FEATURE", outgoing_links=[]),
        SimpleNamespace(id="t1", view="TEST"),
    ]
    svc = AdvancedTraceabilityEnhancementsService(async_session)
    # Use AsyncMock to return awaitable
    svc.items.query = AsyncMock(return_value=items)  # type: ignore[assignment]

    gaps = await svc.coverage_gap_analysis("proj-1", "FEATURE", "TEST")
    assert gaps["total_source_items"] == 1
    assert gaps["coverage_percent"] == 0


@pytest.mark.asyncio
async def test_bidirectional_link_analysis(monkeypatch, async_session) -> None:  # noqa: ARG001
    item = SimpleNamespace(id="i1", outgoing_links=[SimpleNamespace(target_item_id="i2", link_type="depends_on")])
    other = SimpleNamespace(id="i2", outgoing_links=[])

    svc = AdvancedTraceabilityEnhancementsService(async_session)
    # Use AsyncMock to return awaitable
    svc.items.get_by_id = AsyncMock(side_effect=lambda iid: item if iid == "i1" else None)  # type: ignore[assignment]
    svc.items.query = AsyncMock(return_value=[item, other])  # type: ignore[assignment]

    analysis = await svc.bidirectional_link_analysis("proj-1", "i1")
    assert analysis["outgoing"]
