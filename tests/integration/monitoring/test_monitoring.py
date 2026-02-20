from typing import Any

"""Integration tests for Epic 5: Agent Monitoring (Story 5.8)."""

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.agent import Agent
from tracertm.services.agent_monitoring_service import AgentMonitoringService


@pytest.fixture
def temp_project_setup(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up temporary project for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    config_manager = ConfigManager()

    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"
    config_manager.set("database_url", database_url)

    from sqlalchemy.orm import Session

    from tracertm.database.connection import DatabaseConnection
    from tracertm.models.project import Project

    db = DatabaseConnection(database_url)
    db.connect()
    db.create_tables()

    with Session(db.engine) as session:
        project = Project(name="test-project", description="Test project")
        session.add(project)
        session.commit()
        project_id = str(project.id)

    config_manager.set("current_project_id", project_id)
    config_manager.set("current_project_name", "test-project")

    return project_id, database_url


def test_health_check(temp_project_setup: Any) -> None:
    """Test agent health check (Story 5.8)."""
    project_id, database_url = temp_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Create agent with recent activity
        agent = Agent(
            project_id=project_id,
            name="healthy-agent",
            agent_type="ai_agent",
            status="active",
            last_activity_at=datetime.now(UTC).isoformat(),
        )
        session.add(agent)
        session.commit()
        agent_id = str(agent.id)

        # Check health
        service = AgentMonitoringService(session)
        health = service.check_agent_health(project_id, agent_id)

        assert len(health) == 1
        assert health[0]["agent_id"] == agent_id
        assert health[0]["health"] in {"healthy", "idle", "stale", "unknown"}

    db.close()


def test_alerts_generation(temp_project_setup: Any) -> None:
    """Test alert generation (Story 5.8)."""
    project_id, database_url = temp_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Create stale agent
        stale_time = (datetime.now(UTC) - timedelta(hours=25)).isoformat()
        agent = Agent(
            project_id=project_id,
            name="stale-agent",
            agent_type="ai_agent",
            status="active",
            last_activity_at=stale_time,
        )
        session.add(agent)
        session.commit()

        # Get alerts
        service = AgentMonitoringService(session)
        alerts = service.get_alerts(project_id, alert_types=["stale"])

        assert len(alerts) > 0
        assert any("stale" in alert.get("type", "") for alert in alerts)

    db.close()
