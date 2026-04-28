from typing import Any

"""Integration tests for Epic 7: Performance Optimizations (Stories 7.3-7.9)."""

import time

import pytest

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.project import Project


@pytest.fixture
def large_project_setup(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up project with many items for performance testing."""
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
        project = Project(name="large-project", description="Large project")
        session.add(project)
        session.commit()
        project_id = str(project.id)

        # Create 100 items for performance testing
        items = []
        for i in range(100):
            item = Item(
                project_id=project_id,
                title=f"Item {i}",
                description=f"Description for item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo" if i % 3 == 0 else "in_progress" if i % 3 == 1 else "complete",
            )
            items.append(item)
            session.add(item)

        session.commit()

    return project_id, database_url


def test_search_performance(large_project_setup: Any) -> None:
    """Test search performance (Story 7.3, FR60)."""
    project_id, database_url = large_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Direct SQL query for performance test
        from sqlalchemy import or_

        # Test search speed
        start_time = time.time()
        items = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                or_(
                    Item.title.ilike("%Item%"),
                    Item.description.ilike("%Item%"),
                ),
            )
            .limit(50)
            .all()
        )
        elapsed = time.time() - start_time

        # Should complete in reasonable time (<1s for 100 items)
        assert elapsed < 1.0, f"Search took {elapsed}s, expected <1s"
        assert len(items) > 0


def test_progress_calculation_performance(large_project_setup: Any) -> None:
    """Test progress calculation performance (Story 7.6, FR68)."""
    project_id, database_url = large_project_setup

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Get first item
        session.query(Item).filter(Item.project_id == project_id).first()

        # Simple progress calculation (count complete vs total)
        start_time = time.time()
        from sqlalchemy import func

        total = (
            session.query(func.count(Item.id)).filter(Item.project_id == project_id, Item.deleted_at.is_(None)).scalar()
        ) or 0
        complete = (
            session
            .query(func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
                Item.status == "complete",
            )
            .scalar()
        ) or 0
        completion = (complete / total * 100) if total > 0 else 0
        elapsed = time.time() - start_time

        # Should complete quickly (<100ms)
        assert elapsed < 0.1, f"Progress calculation took {elapsed}s, expected <0.1s"
        assert 0 <= completion <= 100
