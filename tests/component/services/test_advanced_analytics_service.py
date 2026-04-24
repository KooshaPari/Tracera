from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.services.advanced_analytics_service import AdvancedAnalyticsService

pytestmark = pytest.mark.integration


class _Item(SimpleNamespace):
    pass


class _Event(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_project_metrics_counts_status_and_view(monkeypatch: Any, async_session: Any) -> None:
    items = [
        _Item(status="todo", view="FEATURE"),
        _Item(status="done", view="FEATURE"),
        _Item(status="done", view="BUG"),
    ]

    svc = AdvancedAnalyticsService(async_session)

    async def fake_query(project_id: Any, _filters: Any) -> None:
        return items

    monkeypatch.setattr(svc.items, "query", fake_query)

    metrics = await svc.project_metrics("proj-1")

    assert metrics["total_items"] == COUNT_THREE
    assert metrics["by_status"]["done"] == COUNT_TWO
    assert metrics["by_view"]["FEATURE"] == COUNT_TWO
    assert metrics["completion_rate"] == pytest.approx(66.66, rel=0.1)


@pytest.mark.asyncio
async def test_team_analytics_counts_agents(monkeypatch: Any, async_session: Any) -> None:
    events = [
        _Event(agent_id="a1"),
        _Event(agent_id="a1"),
        _Event(agent_id="a2"),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_events(_project_id: Any) -> None:
        return events

    monkeypatch.setattr(svc.events, "get_by_project", fake_events)

    data = await svc.team_analytics("proj-1")
    assert data["total_agents"] == COUNT_TWO
    assert data["total_events"] == COUNT_THREE
    assert data["agent_activity"]["a1"] == COUNT_TWO


@pytest.mark.asyncio
async def test_trend_analysis_filters_by_days(monkeypatch: Any, async_session: Any) -> None:
    now = datetime.now(datetime.UTC)
    events = [
        _Event(created_at=now),
        _Event(created_at=now - timedelta(days=2)),
        _Event(created_at=now - timedelta(days=40)),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_query(project_id: Any, _filters: Any) -> None:
        return []

    monkeypatch.setattr(svc.items, "query", fake_query)

    async def fake_events(_project_id: Any) -> None:
        return events

    monkeypatch.setattr(svc.events, "get_by_project", fake_events)

    trend = await svc.trend_analysis("proj-1", days=7)
    assert trend["total_events"] == COUNT_THREE  # all events returned
    assert len(trend["daily_events"]) == COUNT_TWO  # only two inside 7-day window


@pytest.mark.asyncio
async def test_dependency_metrics_handles_missing_links(monkeypatch: Any, async_session: Any) -> None:
    items = [
        _Item(outgoing_links=[_Item(link_type="depends_on"), _Item(link_type="blocks")]),
        _Item(outgoing_links=[]),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_query_items(project_id: Any, _filters: Any) -> None:
        return items

    monkeypatch.setattr(svc.items, "query", fake_query_items)

    deps = await svc.dependency_metrics("proj-1")
    assert deps["total_links"] == COUNT_TWO
    assert deps["average_links_per_item"] == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_quality_metrics_counts_descriptions(monkeypatch: Any, async_session: Any) -> None:
    items = [
        _Item(description="desc", outgoing_links=[1]),
        _Item(description=None, outgoing_links=[]),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_query_items2(project_id: Any, _filters: Any) -> None:
        return items

    monkeypatch.setattr(svc.items, "query", fake_query_items2)

    quality = await svc.quality_metrics("proj-1")
    assert quality["items_with_description"] == 1
    assert quality["items_with_links"] == 1
