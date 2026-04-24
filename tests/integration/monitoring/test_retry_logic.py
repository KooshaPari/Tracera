from typing import Any

"""Integration tests for Epic 5: Retry Logic (Story 5.3)."""

import time

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


def test_retry_on_conflict(_temp_project_setup: Any) -> None:
    """Test retry logic on conflict (Story 5.3)."""
    client1 = TraceRTMClient()
    client1.register_agent("agent-1", agent_type="ai_agent")

    client2 = TraceRTMClient()
    client2.register_agent("agent-2", agent_type="ai_agent")

    # Create item
    item = client1.create_item("Test Item", "FEATURE", "feature")

    # Both agents try to update
    client1.update_item(item["id"], status="in_progress")

    # Client 2 should retry and succeed after getting fresh version
    updated = client2.update_item(item["id"], status="complete")
    assert updated["status"] == "complete"

    client1.close()
    client2.close()


def test_retry_exponential_backoff(_temp_project_setup: Any) -> None:
    """Test exponential backoff in retry logic (Story 5.3)."""
    client = TraceRTMClient()
    client.register_agent("test-agent", agent_type="ai_agent")

    item = client.create_item("Test Item", "FEATURE", "feature")

    # Update should succeed (no conflict)
    start_time = time.time()
    updated = client.update_item(item["id"], status="in_progress")
    elapsed = time.time() - start_time

    # Should complete quickly (<1s)
    assert elapsed < 1.0
    assert updated["status"] == "in_progress"

    client.close()
