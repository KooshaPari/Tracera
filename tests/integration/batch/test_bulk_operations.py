from typing import Any

"""Integration tests for Epic 2: Bulk Operations (Story 2.8, FR14)."""

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.services.bulk_operation_service import BulkOperationService


@pytest.fixture
def temp_project_with_items(tmp_path: Any, monkeypatch: Any) -> None:
    """Set up project with multiple items for testing."""
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
        for i in range(10):
            item = Item(
                project_id=project_id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo" if i % 2 == 0 else "in_progress",
                priority="medium",
            )
            session.add(item)

        session.commit()

    config_manager.set("current_project_id", project_id)
    config_manager.set("current_project_name", "test-project")

    return project_id, database_url


def test_bulk_update_preview(temp_project_with_items: Any) -> None:
    """Test bulk update preview (Story 2.8, FR14)."""
    project_id, database_url = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = BulkOperationService(session)

        # Preview bulk update
        preview = service.bulk_update_preview(
            project_id,
            {"status": "todo"},
            {"status": "in_progress"},
        )

        assert preview["total_count"] == COUNT_FIVE  # 5 items with status=todo
        assert len(preview["sample_items"]) <= COUNT_FIVE
        assert "updates" in preview
        assert "estimated_duration_ms" in preview


def test_bulk_update_atomicity(temp_project_with_items: Any) -> None:
    """Test bulk update atomicity (Story 2.8, FR14)."""
    project_id, database_url = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = BulkOperationService(session)

        # Perform bulk update
        result = service.bulk_update_items(
            project_id,
            {"status": "todo"},
            {"status": "in_progress"},
        )

        assert result["items_updated"] == COUNT_FIVE

        # Verify all items were updated
        updated_items = session.query(Item).filter(Item.project_id == project_id, Item.status == "in_progress").count()
        assert updated_items == COUNT_TEN  # All 10 items should now be in_progress


def test_bulk_delete_atomicity(temp_project_with_items: Any) -> None:
    """Test bulk delete atomicity (Story 2.8, FR14)."""
    project_id, database_url = temp_project_with_items

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = BulkOperationService(session)

        # Perform bulk delete
        result = service.bulk_delete_items(
            project_id,
            {"status": "todo"},
        )

        assert result["items_deleted"] == COUNT_FIVE

        # Verify items are soft-deleted
        active_items = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .count()
        )
        assert active_items == COUNT_FIVE  # Only in_progress items remain


def test_bulk_create_preview(temp_project_with_items: Any) -> None:
    """Test bulk create preview from CSV (Story 2.8, FR14, FR74)."""
    project_id, database_url = temp_project_with_items

    # Create CSV data
    csv_data = """Title,View,Type,Status,Priority,Description
Feature 1,FEATURE,feature,todo,high,First feature
Feature 2,FEATURE,feature,in_progress,medium,Second feature
Task 1,FEATURE,task,todo,low,First task
"""

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = BulkOperationService(session)

        # Preview bulk create
        preview = service.bulk_create_preview(project_id, csv_data)

        assert preview["total_count"] == COUNT_THREE
        assert len(preview["sample_items"]) == COUNT_THREE
        assert "validation_errors" in preview
        assert "warnings" in preview
        assert "estimated_duration_ms" in preview

        # Check sample items
        assert preview["sample_items"][0]["title"] == "Feature 1"
        assert preview["sample_items"][0]["view"] == "FEATURE"
        assert preview["sample_items"][0]["type"] == "feature"
        assert preview["sample_items"][0]["status"] == "todo"


def test_bulk_create_preview_with_validation_errors(temp_project_with_items: Any) -> None:
    """Test bulk create preview with validation errors (Story 2.8, FR14, FR74)."""
    project_id, database_url = temp_project_with_items

    # Create CSV data with errors
    csv_data = """Title,View,Type,Status
Valid Item,FEATURE,feature,todo
,FEATURE,feature,todo
Invalid View,INVALID,feature,todo
"""

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = BulkOperationService(session)

        # Preview bulk create
        preview = service.bulk_create_preview(project_id, csv_data)

        # Should have 2 valid items (INVALID is a valid view string per schema, just not a standard view)
        # 1 invalid row (empty title)
        assert preview["total_count"] == COUNT_TWO
        # Should have validation errors
        assert len(preview["validation_errors"]) > 0
        assert preview["invalid_rows_count"] == 1


def test_bulk_create_items_atomicity(temp_project_with_items: Any) -> None:
    """Test bulk create atomicity from CSV (Story 2.8, FR14, FR74)."""
    project_id, database_url = temp_project_with_items

    # Get initial count
    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        initial_count = session.query(Item).filter(Item.project_id == project_id).count()

        # Create CSV data
        csv_data = """Title,View,Type,Status,Priority,Description
New Feature 1,FEATURE,feature,todo,high,First new feature
New Feature 2,FEATURE,feature,in_progress,medium,Second new feature
New Task 1,FEATURE,task,todo,low,First new task
"""

        service = BulkOperationService(session)

        # Perform bulk create
        result = service.bulk_create_items(project_id, csv_data)

        assert result["items_created"] == COUNT_THREE

        # Verify items were created
        final_count = session.query(Item).filter(Item.project_id == project_id).count()
        assert final_count == initial_count + 3

        # Verify specific items
        item1 = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.title == "New Feature 1",
            )
            .first()
        )
        assert item1 is not None
        assert item1.view == "FEATURE"
        assert item1.item_type == "feature"
        assert item1.status == "todo"
        assert item1.priority == "high"


def test_bulk_create_with_metadata(temp_project_with_items: Any) -> None:
    """Test bulk create with metadata from CSV (Story 2.8, FR14, FR74)."""
    project_id, database_url = temp_project_with_items

    # Create CSV data with metadata
    csv_data = """Title,View,Type,Status,Metadata
Feature with Metadata,FEATURE,feature,todo,"{""tags"": [""auth"", ""security""], ""priority"": ""high""}"
"""

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        service = BulkOperationService(session)

        # Perform bulk create
        result = service.bulk_create_items(project_id, csv_data)

        assert result["items_created"] == 1

        # Verify item with metadata
        item = (
            session
            .query(Item)
            .filter(
                Item.project_id == project_id,
                Item.title == "Feature with Metadata",
            )
            .first()
        )
        assert item is not None
        assert item.item_metadata.get("tags") == ["auth", "security"]
        assert item.item_metadata.get("priority") == "high"


def test_bulk_create_skips_invalid_rows(temp_project_with_items: Any) -> None:
    """Test that bulk create skips invalid rows and creates valid ones (Story 2.8, FR14, FR74)."""
    project_id, database_url = temp_project_with_items

    # Create CSV data with mix of valid and invalid rows
    csv_data = """Title,View,Type,Status
Valid Item 1,FEATURE,feature,todo
,FEATURE,feature,todo
Valid Item 2,FEATURE,feature,in_progress
Invalid View,INVALID,feature,todo
Valid Item 3,FEATURE,feature,done
"""

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        initial_count = session.query(Item).filter(Item.project_id == project_id).count()

        service = BulkOperationService(session)

        # Perform bulk create
        result = service.bulk_create_items(project_id, csv_data)

        # Should create 4 valid items (INVALID is a valid view string per schema, just not a standard view)
        # Skip 1 invalid row (empty title)
        assert result["items_created"] == COUNT_FOUR

        # Verify final count
        final_count = session.query(Item).filter(Item.project_id == project_id).count()
        assert final_count == initial_count + 4
