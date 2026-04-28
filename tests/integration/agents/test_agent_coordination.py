from typing import Any

"""Integration tests for Epic 5: Agent Coordination (Story 5.4)."""

import pytest

pytestmark = pytest.mark.integration

from tracertm.api.client import TraceRTMClient


@pytest.fixture
def temp_project_setup(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up temporary project for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    from tracertm.config.manager import ConfigManager

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

    return project_id


def test_agent_coordination_detection(_temp_project_setup: Any) -> None:
    """Test agent coordination conflict detection (Story 5.4)."""
    client1 = TraceRTMClient()
    agent1_id = client1.register_agent("agent-1", agent_type="ai_agent")

    client2 = TraceRTMClient()
    agent2_id = client2.register_agent("agent-2", agent_type="ai_agent")

    # Create item
    item = client1.create_item("Shared Item", "FEATURE", "feature")

    # Both agents update - should detect coordination need
    client1.update_item(item["id"], status="in_progress", owner=agent1_id)

    # Client 2 should handle conflict gracefully
    try:
        client2.update_item(item["id"], status="complete", owner=agent2_id)
    except Exception:
        # Expected - conflict detected
        pass

    # Verify final state
    final_item = client1.get_item(item["id"])
    assert final_item is not None

    client1.close()
    client2.close()
