"""Integration tests for Epic 4: Dependency Detection (Story 4.6, FR22, NFR-R2).

Functional Requirements Coverage:
    - FR-APP-003: Cycle Detection
    - FR-QUAL-003: Dependency Analysis

Epics:
    - EPIC-003: Traceability Matrix Core

Tests verify cycle detection, transitive dependency analysis, and missing
dependency detection in the traceability graph.
"""

from typing import Any

import pytest

from tests.test_constants import COUNT_TWO

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.cycle_detection_service import CycleDetectionService


@pytest.fixture
def temp_project_with_items(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up project with items and links for testing."""
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
        project = Project(name="test-project", description="Test project")
        session.add(project)
        session.commit()
        project_id = str(project.id)

        # Create test items
        items = {}
        for i in range(5):
            item = Item(
                project_id=project_id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            session.add(item)
            session.flush()
            items[f"item_{i}"] = item.id

        # Create links (item_0 -> item_1 -> item_2)
        link1 = Link(
            project_id=project_id,
            source_item_id=items["item_0"],
            target_item_id=items["item_1"],
            link_type="depends_on",
        )
        link2 = Link(
            project_id=project_id,
            source_item_id=items["item_1"],
            target_item_id=items["item_2"],
            link_type="depends_on",
        )
        session.add(link1)
        session.add(link2)
        session.commit()

    config_manager.set("current_project_id", project_id)
    config_manager.set("current_project_name", "test-project")

    return project_id, database_url, items


def test_detect_missing_dependencies(temp_project_with_items: Any) -> None:
    """Test missing dependency detection (Story 4.6, FR22)."""
    project_id, database_url, items = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Create a link to a non-existent item
        missing_link = Link(
            project_id=project_id,
            source_item_id=items["item_0"],
            target_item_id="non-existent-item-id",
            link_type="depends_on",
        )
        session.add(missing_link)
        session.commit()

        service = CycleDetectionService(session)
        result = service.detect_missing_dependencies(project_id, "depends_on")

        assert result["has_missing_dependencies"] is True
        assert result["missing_count"] >= 1
        assert any(dep["issue"] == "target_item_missing" for dep in result["missing_dependencies"])


def test_detect_orphans(temp_project_with_items: Any) -> None:
    """Test orphaned item detection (Story 4.6, FR22)."""
    project_id, database_url, items = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = CycleDetectionService(session)
        result = service.detect_orphans(project_id)

        # Items 3 and 4 should be orphans (no links)
        assert result["has_orphans"] is True
        assert result["orphan_count"] >= COUNT_TWO

        orphan_ids = {orphan["item_id"] for orphan in result["orphans"]}
        assert items["item_3"] in orphan_ids
        assert items["item_4"] in orphan_ids


def test_analyze_impact(temp_project_with_items: Any) -> None:
    """Test impact analysis (Story 4.6, FR22, NFR-R2)."""
    project_id, database_url, items = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        # Create additional dependency: item_2 -> item_3
        link3 = Link(
            project_id=project_id,
            source_item_id=items["item_2"],
            target_item_id=items["item_3"],
            link_type="depends_on",
        )
        session.add(link3)
        session.commit()

        service = CycleDetectionService(session)
        # Analyze impact of changing item_1 (should affect item_0 which depends on it)
        result = service.analyze_impact(project_id, items["item_1"], max_depth=5)

        assert result["total_affected"] >= 1  # item_0 depends on item_1
        assert result["root_item_id"] == items["item_1"]
        assert "affected_by_depth" in result
        assert "affected_by_view" in result
        assert len(result["affected_items"]) >= 1


def test_cycle_detection_integration(temp_project_with_items: Any) -> None:
    """Test cycle detection integration (Story 4.6, FR22)."""
    project_id, database_url, items = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = CycleDetectionService(session)

        # Initially no cycles
        result = service.detect_cycles(project_id, "depends_on")
        # detect_cycles returns SimpleNamespace; support both attr and dict-like in tests
        has_cycles = result.has_cycles if hasattr(result, "has_cycles") else result["has_cycles"]
        assert has_cycles is False

        # Create a cycle: item_2 -> item_0 (completing the cycle item_0 -> item_1 -> item_2 -> item_0)
        cycle_link = Link(
            project_id=project_id,
            source_item_id=items["item_2"],
            target_item_id=items["item_0"],
            link_type="depends_on",
        )
        session.add(cycle_link)
        session.commit()

        # Now should detect cycle
        result = service.detect_cycles(project_id, "depends_on")
        has_cycles = result.has_cycles if hasattr(result, "has_cycles") else result["has_cycles"]
        cycle_count = result.cycle_count if hasattr(result, "cycle_count") else result["cycle_count"]
        assert has_cycles is True
        assert cycle_count >= 1
