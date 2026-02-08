from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from tracertm.services.advanced_analytics_service import AdvancedAnalyticsService

pytestmark = pytest.mark.integration


class _Item(SimpleNamespace):
    pass


class _Event(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_project_metrics_counts_status_and_view(monkeypatch, async_session) -> None:
    items = [
        _Item(status="todo", view="FEATURE"),
        _Item(status="done", view="FEATURE"),
        _Item(status="done", view="BUG"),
    ]

    svc = AdvancedAnalyticsService(async_session)

    async def fake_query(project_id, filters):  # noqa: ARG001
        return items

    monkeypatch.setattr(svc.items, "query", fake_query)

    metrics = await svc.project_metrics("proj-1")

    assert metrics["total_items"] == 3
    assert metrics["by_status"]["done"] == 2
    assert metrics["by_view"]["FEATURE"] == 2
    assert metrics["completion_rate"] == pytest.approx(66.66, rel=0.1)


@pytest.mark.asyncio
async def test_team_analytics_counts_agents(monkeypatch, async_session) -> None:
    events = [
        _Event(agent_id="a1"),
        _Event(agent_id="a1"),
        _Event(agent_id="a2"),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_events(project_id):  # noqa: ARG001
        return events

    monkeypatch.setattr(svc.events, "get_by_project", fake_events)

    data = await svc.team_analytics("proj-1")
    assert data["total_agents"] == 2
    assert data["total_events"] == 3
    assert data["agent_activity"]["a1"] == 2


@pytest.mark.asyncio
async def test_trend_analysis_filters_by_days(monkeypatch, async_session) -> None:
    now = datetime.now(datetime.UTC)
    events = [
        _Event(created_at=now),
        _Event(created_at=now - timedelta(days=2)),
        _Event(created_at=now - timedelta(days=40)),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_query(project_id, filters):  # noqa: ARG001
        return []

    monkeypatch.setattr(svc.items, "query", fake_query)

    async def fake_events(project_id):  # noqa: ARG001
        return events

    monkeypatch.setattr(svc.events, "get_by_project", fake_events)

    trend = await svc.trend_analysis("proj-1", days=7)
    assert trend["total_events"] == 3  # all events returned
    assert len(trend["daily_events"]) == 2  # only two inside 7-day window


@pytest.mark.asyncio
async def test_dependency_metrics_handles_missing_links(monkeypatch, async_session) -> None:
    items = [
        _Item(outgoing_links=[_Item(link_type="depends_on"), _Item(link_type="blocks")]),
        _Item(outgoing_links=[]),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_query_items(project_id, filters):  # noqa: ARG001
        return items

    monkeypatch.setattr(svc.items, "query", fake_query_items)

    deps = await svc.dependency_metrics("proj-1")
    assert deps["total_links"] == 2
    assert deps["average_links_per_item"] == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_quality_metrics_counts_descriptions(monkeypatch, async_session) -> None:
    items = [
        _Item(description="desc", outgoing_links=[1]),
        _Item(description=None, outgoing_links=[]),
    ]
    svc = AdvancedAnalyticsService(async_session)

    async def fake_query_items2(project_id, filters):  # noqa: ARG001
        return items

    monkeypatch.setattr(svc.items, "query", fake_query_items2)

    quality = await svc.quality_metrics("proj-1")
    assert quality["items_with_description"] == 1
    assert quality["items_with_links"] == 1
