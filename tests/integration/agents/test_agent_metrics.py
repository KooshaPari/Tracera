from typing import Any

"""Integration tests for Epic 5: Agent Metrics (Story 5.6)."""

from datetime import UTC, datetime, timedelta

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.services.agent_metrics_service import AgentMetricsService


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


def test_metrics_calculation(temp_project_setup: Any) -> None:
    """Test agent metrics calculation (Story 5.6)."""
    project_id, database_url = temp_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Create agent
        agent = Agent(
            project_id=project_id,
            name="test-agent",
            agent_type="ai_agent",
            status="active",
            last_activity_at=datetime.now(UTC).isoformat(),
        )
        session.add(agent)
        session.commit()
        agent_id = str(agent.id)

        # Create some events
        for i in range(10):
            event = Event(
                project_id=project_id,
                event_type="item_created",
                entity_type="item",
                entity_id=f"item-{i}",
                agent_id=agent_id,
                data={"title": f"Item {i}"},
            )
            session.add(event)
        session.commit()

        # Calculate metrics
        service = AgentMetricsService(session)
        since = datetime.now(UTC) - timedelta(hours=1)
        metrics = service.calculate_metrics(project_id, agent_id, since)

        assert "metrics" in metrics
        assert len(metrics["metrics"]) > 0

        agent_metrics = metrics["metrics"][0]
        assert agent_metrics["total_operations"] == COUNT_TEN
        assert agent_metrics["agent_id"] == agent_id

    db.close()


def test_workload_calculation(temp_project_setup: Any) -> None:
    """Test agent workload calculation (Story 5.6)."""
    project_id, database_url = temp_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Create agent
        agent = Agent(
            project_id=project_id,
            name="test-agent",
            agent_type="ai_agent",
            status="active",
        )
        session.add(agent)
        session.commit()
        agent_id = str(agent.id)

        # Create items assigned to agent
        for i in range(5):
            item = Item(
                project_id=project_id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo" if i < COUNT_THREE else "in_progress",
                owner=agent_id,
            )
            session.add(item)
        session.commit()

        # Calculate workload
        service = AgentMetricsService(session)
        workload = service.get_agent_workload(project_id, agent_id)

        assert workload["agent_id"] == agent_id
        assert workload["total_items"] == COUNT_FIVE
        assert "by_status" in workload

    db.close()
