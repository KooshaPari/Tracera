from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.services.agent_monitoring_service import AgentMonitoringService

pytestmark = pytest.mark.integration


def _agent(
    session: Any, agent_id: Any, last_activity: Any = None, status: Any = "active", agent_type: Any = "automation"
) -> None:
    agent = Agent(
        id=agent_id,
        project_id="proj-1",
        name=f"Agent {agent_id}",
        status=status,
        agent_type=agent_type,
        last_activity_at=last_activity,
    )
    session.add(agent)
    session.commit()
    return agent


def test_check_agent_health_classifies_states(sync_session: Any) -> None:
    now = datetime.now(datetime.UTC)
    _agent(sync_session, "a-healthy", last_activity=now.isoformat())
    _agent(sync_session, "a-idle", last_activity=(now - timedelta(hours=2)).isoformat())
    _agent(sync_session, "a-stale", last_activity=(now - timedelta(hours=30)).isoformat())
    _agent(sync_session, "a-none", last_activity=None)

    svc = AgentMonitoringService(sync_session)
    statuses = {entry["agent_id"]: entry for entry in svc.check_agent_health("proj-1")}

    assert statuses["a-healthy"]["health"] == "healthy"
    assert statuses["a-idle"]["health"] == "idle"
    assert statuses["a-stale"]["health"] == "stale"
    assert statuses["a-none"]["health"] == "no_activity"


def test_check_agent_health_returns_empty_for_missing_agent(sync_session: Any) -> None:
    svc = AgentMonitoringService(sync_session)
    assert svc.check_agent_health("proj-1", agent_id="missing") == []


def test_get_alerts_composes_from_metrics_and_errors(sync_session: Any, monkeypatch: Any) -> None:
    now = datetime.now(datetime.UTC)
    _agent(sync_session, "a-stale", last_activity=(now - timedelta(hours=25)).isoformat())

    # Inject metrics with high conflict rate
    def fake_metrics_service(_session: Any) -> None:
        return SimpleNamespace(
            calculate_metrics=lambda project_id, _since: {
                "metrics": [{"agent_id": "a-stale", "agent_name": "Agent stale", "conflict_rate": 12.5}],
            },
        )

    monkeypatch.setattr(
        "tracertm.services.agent_metrics_service.AgentMetricsService",
        fake_metrics_service,
    )

    # Add error events to trigger error_rate alert
    error_event = Event(
        project_id="proj-1",
        event_type="error",
        entity_type="system",
        entity_id="sys-1",
        created_at=datetime.now(datetime.UTC),
    )
    sync_session.add(error_event)
    sync_session.commit()

    svc = AgentMonitoringService(sync_session)
    alerts = svc.get_alerts("proj-1", alert_types=["stale", "high_conflict_rate", "error_rate"])

    alert_types = {alert["type"] for alert in alerts}
    assert {"stale_agent", "high_conflict_rate", "error_rate"} <= alert_types
