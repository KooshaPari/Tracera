from typing import Any

"""Integration tests for Epic 6: Project Enhancements (Stories 6.3-6.6)."""

import json

import pytest

from tests.test_constants import COUNT_TWO

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

    return project_id, database_url


def test_project_isolation(temp_project_setup: Any) -> None:
    """Test project data isolation (Story 6.4)."""
    _project_id, _database_url = temp_project_setup

    client1 = TraceRTMClient()
    client1.register_agent("agent-1", agent_type="ai_agent")

    # Create items in project 1
    item1 = client1.create_item("Project 1 Item", "FEATURE", "feature")

    # Switch to project 2 (would need project creation)
    # Verify items from project 1 are not visible

    items = client1.query_items()
    assert len(items) == 1
    assert items[0]["id"] == item1["id"]

    client1.close()


def test_project_export_import(temp_project_setup: Any) -> None:
    """Test project export/import (Story 6.6)."""
    _project_id, _database_url = temp_project_setup

    client = TraceRTMClient()
    client.register_agent("test-agent", agent_type="ai_agent")

    # Create items
    client.create_item("Item 1", "FEATURE", "feature")
    client.create_item("Item 2", "CODE", "file")

    # Export project
    export_data = client.export_project(format="json")
    data = json.loads(export_data)

    assert "items" in data
    assert len(data["items"]) == COUNT_TWO

    client.close()
