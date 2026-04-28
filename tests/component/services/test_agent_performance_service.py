from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.project import Project
from tracertm.services.agent_performance_service import AgentPerformanceService

pytestmark = pytest.mark.integration


async def _seed_agent(
    async_session: Any, agent_id: Any = "agent-1", project_id: Any = "proj-1", last_activity: Any = None
) -> None:
    existing = await async_session.get(Project, project_id)
    if not existing:
        project = Project(id=project_id, name=f"Proj-{project_id}-{datetime.now(UTC).timestamp()}")
        async_session.add(project)
    agent = Agent(
        id=agent_id,
        project_id=project_id,
        name="Agent One",
        agent_type="ai_agent",
        status="active",
        last_activity_at=last_activity or datetime.now(UTC).isoformat(),
    )
    async_session.add(agent)
    await async_session.commit()
    return agent


async def _event(async_session: Any, project_id: Any, agent_id: Any, event_type: Any, created_at: Any = None) -> None:
    evt = Event(
        project_id=project_id,
        event_type=event_type,
        entity_type="item",
        entity_id="i-1",
        agent_id=agent_id,
        data={"foo": "bar"},
    )
    if created_at:
        evt.created_at = created_at
    async_session.add(evt)
    await async_session.commit()
    return evt


@pytest.mark.asyncio
async def test_get_agent_stats_filters_time_window(async_session: Any) -> None:
    await _seed_agent(async_session)
    now = datetime.now(UTC)
    await _event(async_session, "proj-1", "agent-1", "updated", created_at=now)
    await _event(async_session, "proj-1", "agent-1", "updated", created_at=now - timedelta(hours=30))

    svc = AgentPerformanceService(async_session)
    stats = await svc.get_agent_stats("agent-1", time_window_hours=24)

    assert stats["total_events"] == 1
    assert stats["event_types"]["updated"] == 1


@pytest.mark.asyncio
async def test_get_agent_stats_missing_agent(async_session: Any) -> None:
    svc = AgentPerformanceService(async_session)
    stats = await svc.get_agent_stats("missing")
    assert stats == {"error": "Agent not found"}


@pytest.mark.asyncio
async def test_get_agent_workload_classifies_levels(async_session: Any) -> None:
    await _seed_agent(async_session)
    now = datetime.now(UTC)
    # 12 events in last 24h => events_per_hour = 0.5, still "Idle" threshold (<=1)
    for _ in range(2):
        await _event(async_session, "proj-1", "agent-1", "updated", created_at=now - timedelta(hours=2))

    svc = AgentPerformanceService(async_session)
    workload = await svc.get_agent_workload("agent-1")

    assert workload["workload"] in {"Idle", "Light"}
    assert workload["total_events_24h"] == COUNT_TWO


@pytest.mark.asyncio
async def test_recommend_agent_assignment_picks_lowest_workload(async_session: Any) -> None:
    await _seed_agent(async_session, agent_id="agent-1", project_id="proj-2")
    await _seed_agent(async_session, agent_id="agent-2", project_id="proj-2")
    now = datetime.now(UTC)
    # Give agent-1 more events to make agent-2 the recommended one
    await _event(async_session, "proj-2", "agent-1", "updated", created_at=now)
    await _event(async_session, "proj-2", "agent-1", "updated", created_at=now)

    svc = AgentPerformanceService(async_session)
    rec = await svc.recommend_agent_assignment("proj-2")

    assert rec["recommended_agent_id"] == "agent-2"
    assert "reason" in rec
