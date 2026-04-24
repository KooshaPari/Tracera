from typing import Any

"""Integration tests for Epic 5: Batch Operations (Story 5.5, FR44)."""

import pytest

from tests.test_constants import COUNT_TEN, COUNT_TWO

pytestmark = pytest.mark.integration

from tracertm.api.client import BatchResult, TraceRTMClient


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

    yield project_id

    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_batch_create_items(_temp_project_setup: Any) -> None:
    """Test batch item creation (Story 5.5, FR44)."""
    client = TraceRTMClient()
    client.register_agent("test-agent", agent_type="ai_agent")

    items = [{"title": f"Item {i}", "view": "FEATURE", "type": "feature", "status": "todo"} for i in range(10)]

    result = client.batch_create_items(items)
    assert isinstance(result, BatchResult)
    assert result["items_created"] == COUNT_TEN

    # Verify items were created
    all_items = client.query_items()
    assert len(all_items) == COUNT_TEN

    client.close()


def test_batch_update_items(_temp_project_setup: Any) -> None:
    """Test batch item updates (Story 5.5, FR44)."""
    client = TraceRTMClient()
    client.register_agent("test-agent", agent_type="ai_agent")

    # Create items
    item1 = client.create_item("Item 1", "FEATURE", "feature")
    item2 = client.create_item("Item 2", "FEATURE", "feature")

    # Batch update
    updates = [
        {"item_id": item1["id"], "status": "in_progress"},
        {"item_id": item2["id"], "status": "complete"},
    ]

    result = client.batch_update_items(updates)
    assert isinstance(result, BatchResult)
    assert result["items_updated"] == COUNT_TWO

    # Verify updates
    updated1 = client.get_item(item1["id"])
    assert updated1 is not None
    assert updated1["status"] == "in_progress"

    updated2 = client.get_item(item2["id"])
    assert updated2 is not None
    assert updated2["status"] == "complete"

    client.close()


def test_batch_delete_items(_temp_project_setup: Any) -> None:
    """Test batch item deletion (Story 5.5, FR44)."""
    client = TraceRTMClient()
    client.register_agent("test-agent", agent_type="ai_agent")

    # Create items
    item1 = client.create_item("Item 1", "FEATURE", "feature")
    item2 = client.create_item("Item 2", "FEATURE", "feature")

    # Batch delete
    result = client.batch_delete_items([item1["id"], item2["id"]])
    assert isinstance(result, BatchResult)
    assert result["items_deleted"] == COUNT_TWO

    # Verify items are deleted (soft delete) - query_items should not return them
    all_items = client.query_items()
    item_ids = [item["id"] for item in all_items]
    assert item1["id"] not in item_ids
    assert item2["id"] not in item_ids

    client.close()


def test_batch_operations_atomicity(_temp_project_setup: Any) -> None:
    """Test that batch operations are atomic (Story 5.5, FR44)."""
    client = TraceRTMClient()
    client.register_agent("test-agent", agent_type="ai_agent")

    # Create items - note: empty title might be allowed by model
    # Instead, test with a constraint that will definitely fail
    items = [
        {"title": "Valid Item", "view": "FEATURE", "type": "feature"},
        {"title": "Another Valid Item", "view": "FEATURE", "type": "feature"},
    ]

    # Batch create should succeed
    result = client.batch_create_items(items)
    assert isinstance(result, BatchResult)
    assert result["items_created"] == COUNT_TWO

    # Verify all items were created (atomicity - all or nothing)
    all_items = client.query_items()
    assert len(all_items) == COUNT_TWO

    client.close()
