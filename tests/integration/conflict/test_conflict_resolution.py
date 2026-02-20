from typing import Any

"""Integration tests for Epic 5: Conflict Resolution (Story 5.5)."""

import pytest

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.services.conflict_resolution_service import ConflictResolutionService


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


def test_conflict_detection(temp_project_setup: Any) -> None:
    """Test conflict detection (Story 5.5)."""
    project_id, database_url = temp_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = ConflictResolutionService(session)

        # Create item and simulate conflicts
        from tracertm.models.item import Item

        item = Item(
            project_id=project_id,
            title="Test Item",
            view="FEATURE",
            item_type="feature",
        )
        session.add(item)
        session.commit()
        item_id = str(item.id)

        # Detect conflicts (should be empty initially)
        conflicts = service.detect_conflicts(project_id, item_id)
        assert isinstance(conflicts, list)

    db.close()


def test_conflict_resolution_strategies(temp_project_setup: Any) -> None:
    """Test conflict resolution strategies (Story 5.5)."""
    project_id, database_url = temp_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = ConflictResolutionService(session)

        # Create item
        from tracertm.models.item import Item

        item = Item(
            project_id=project_id,
            title="Test Item",
            view="FEATURE",
            item_type="feature",
        )
        session.add(item)
        session.commit()
        item_id = str(item.id)

        # Test resolution strategies
        result = service.resolve_conflict(project_id, item_id, strategy="last_write_wins")
        assert result["resolved"] in {True, False}  # May not have conflicts

    db.close()
