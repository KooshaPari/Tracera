from typing import Any

"""Integration tests for Epic 6: Project Switching & Isolation (Stories 6.3, 6.4)."""

import time

import pytest

from tests.test_constants import HTTP_INTERNAL_SERVER_ERROR

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.api.client import TraceRTMClient
from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.project import Project


@pytest.fixture
def multi_project_setup(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up multiple projects for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    config_manager = ConfigManager()

    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"
    config_manager.set("database_url", database_url)

    db = DatabaseConnection(database_url)
    db.connect()
    db.create_tables()

    with Session(db.engine) as session:
        # Create project 1
        project1 = Project(name="project-1", description="Project 1")
        session.add(project1)
        session.commit()
        project1_id = str(project1.id)

        # Create project 2
        project2 = Project(name="project-2", description="Project 2")
        session.add(project2)
        session.commit()
        project2_id = str(project2.id)

    config_manager.set("current_project_id", project1_id)
    config_manager.set("current_project_name", "project-1")

    return project1_id, project2_id, database_url


def test_project_switching_speed(multi_project_setup: Any) -> None:
    """Test project switching completes in <500ms (Story 6.3, FR47)."""
    _project1_id, project2_id, _database_url = multi_project_setup

    config_manager = ConfigManager()

    # Switch to project 2
    start_time = time.time()
    config_manager.set("current_project_id", project2_id)
    config_manager.set("current_project_name", "project-2")
    elapsed = (time.time() - start_time) * 1000  # Convert to ms

    assert elapsed < HTTP_INTERNAL_SERVER_ERROR, f"Project switch took {elapsed}ms, expected <500ms"

    # Verify switch
    assert config_manager.get("current_project_id") == project2_id
    assert config_manager.get("current_project_name") == "project-2"


def test_project_isolation(multi_project_setup: Any) -> None:
    """Test project data isolation (Story 6.4, FR48)."""
    project1_id, project2_id, _database_url = multi_project_setup

    config_manager = ConfigManager()

    # Create items in project 1
    config_manager.set("current_project_id", project1_id)
    client1 = TraceRTMClient()
    client1.register_agent("agent-1", agent_type="ai_agent")
    item1 = client1.create_item("Project 1 Item", "FEATURE", "feature")

    # Switch to project 2
    config_manager.set("current_project_id", project2_id)
    client2 = TraceRTMClient()
    client2.register_agent("agent-2", agent_type="ai_agent")
    item2 = client2.create_item("Project 2 Item", "FEATURE", "feature")

    # Verify isolation - project 1 items not visible in project 2
    items2 = client2.query_items()
    assert len(items2) == 1
    assert items2[0]["id"] == item2["id"]
    assert items2[0]["id"] != item1["id"]

    # Switch back to project 1
    config_manager.set("current_project_id", project1_id)
    items1 = client1.query_items()
    assert len(items1) == 1
    assert items1[0]["id"] == item1["id"]

    client1.close()
    client2.close()
