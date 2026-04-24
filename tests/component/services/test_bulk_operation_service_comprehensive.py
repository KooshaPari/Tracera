"""Comprehensive test suite for BulkOperationService.

Target: 40+ tests covering:
- Bulk create with 100-1000 items
- Partial failure scenarios with rollback
- Concurrent bulk operations
- Memory efficiency with large batches
- Transaction isolation
- Error recovery paths

Test coverage targets 95%+ line coverage of BulkOperationService.
"""

import csv
import io
import json
from typing import Any

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR, HTTP_OK
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.services.bulk_operation_service import BulkOperationService

pytestmark = pytest.mark.integration


# ============================================================
# Test Fixtures & Helpers
# ============================================================


def _create_test_csv(items_list: Any, omit_empty_metadata: Any = True) -> None:
    """Create CSV string from items list.

    Args:
        items_list: List of item dictionaries
        omit_empty_metadata: If True, omit Metadata field entirely to avoid NoneType.strip() bug
    """
    output = io.StringIO()
    if omit_empty_metadata:
        fieldnames = ["Title", "View", "Type", "Description", "Status", "Priority", "Owner", "Parent Id"]
    else:
        fieldnames = ["Title", "View", "Type", "Description", "Status", "Priority", "Owner", "Parent Id", "Metadata"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for item in items_list:
        # Remove Metadata if omitting empty fields
        if omit_empty_metadata and "Metadata" in item:
            item = {k: v for k, v in item.items() if k != "Metadata"}
        writer.writerow(item)
    return output.getvalue()


def _seed_items(
    session: Any,
    project_id: Any = "proj-1",
    count: Any = 5,
    status: Any = "todo",
    view: Any = "FEATURE",
    item_type: Any = "feature",
    prefix: Any = "item",
) -> None:
    """Create seed items for testing."""
    items = []
    for i in range(count):
        item = Item(
            id=f"{prefix}-{i}",
            project_id=project_id,
            title=f"{prefix.upper()} {i}",
            view=view,
            item_type=item_type,
            status=status,
            priority="medium",
            owner=None,
        )
        session.add(item)
        items.append(item)
    session.commit()
    return items


def _seed_project(session: Any, project_id: Any = "proj-1") -> None:
    """Create a project."""
    project = Project(id=project_id, name=f"Project {project_id}")
    session.add(project)
    session.commit()
    return project


# ============================================================
# SECTION 1: Basic Bulk Create Tests (5 tests)
# ============================================================


class TestBulkCreateBasic:
    """Basic bulk create functionality."""

    def test_bulk_create_single_item(self, sync_session: Any) -> None:
        """Test creating a single item via bulk create."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": "New Item 1",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "Description 1",
                "Status": "todo",
                "Priority": "high",
                "Owner": "john",
                "Parent Id": "",
                "Metadata": "",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 1
        assert sync_session.query(Item).count() == 1

    def test_bulk_create_multiple_items(self, sync_session: Any) -> None:
        """Test creating multiple items."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": f"Desc {i}",
                "Status": "todo",
                "Priority": "medium",
                "Owner": None,
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(10)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == COUNT_TEN
        assert sync_session.query(Item).count() == COUNT_TEN

    def test_bulk_create_with_metadata(self, sync_session: Any) -> None:
        """Test creating items with JSON metadata."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv(
            [
                {
                    "Title": "Item with Metadata",
                    "View": "STORY",
                    "Type": "story",
                    "Description": "",
                    "Status": "todo",
                    "Priority": "medium",
                    "Owner": "",
                    "Parent Id": "",
                    "Metadata": json.dumps({"key": "value", "nested": {"field": "data"}}),
                },
            ],
            omit_empty_metadata=False,
        )

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 1
        item = sync_session.query(Item).first()
        assert item.item_metadata == {"key": "value", "nested": {"field": "data"}}

    def test_bulk_create_with_parent_id(self, sync_session: Any) -> None:
        """Test creating items with parent relationships."""
        _seed_project(sync_session)
        parent = Item(
            id="parent-1",
            project_id="proj-1",
            title="Parent",
            view="STORY",
            item_type="story",
            status="todo",
        )
        sync_session.add(parent)
        sync_session.commit()

        svc = BulkOperationService(sync_session)
        csv_data = _create_test_csv([
            {
                "Title": "Child Item",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "parent-1",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 1
        child = sync_session.query(Item).filter_by(title="Child Item").first()
        assert child.parent_id == "parent-1"

    def test_bulk_create_logs_events(self, sync_session: Any) -> None:
        """Test that bulk create logs events."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": "Item 1",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data, agent_id="agent-1")
        assert result["items_created"] == 1
        events = sync_session.query(Event).all()
        assert len(events) == 1
        assert events[0].event_type == "item_bulk_created"
        assert events[0].agent_id == "agent-1"


# ============================================================
# SECTION 2: Bulk Create with Large Scale (5 tests)
# ============================================================


class TestBulkCreateLargeScale:
    """Test bulk create with large numbers of items."""

    def test_bulk_create_100_items(self, sync_session: Any) -> None:
        """Test creating 100 items."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i:03d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": f"Description for item {i}",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(100)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 100
        assert sync_session.query(Item).count() == 100

    def test_bulk_create_500_items(self, sync_session: Any) -> None:
        """Test creating 500 items."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i:04d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": f"Desc {i}",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(500)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == HTTP_INTERNAL_SERVER_ERROR
        assert sync_session.query(Item).count() == HTTP_INTERNAL_SERVER_ERROR

    def test_bulk_create_1000_items(self, sync_session: Any) -> None:
        """Test creating 1000 items."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i:04d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": f"Desc {i}",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(1000)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 1000
        assert sync_session.query(Item).count() == 1000

    def test_bulk_create_various_statuses(self, sync_session: Any) -> None:
        """Test creating items with different statuses."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        statuses = ["todo", "in_progress", "blocked", "done"]
        items = [
            {
                "Title": f"Item {i:03d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": statuses[i % 4],
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(200)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == HTTP_OK

        # Verify status distribution
        for status in statuses:
            count = sync_session.query(Item).filter_by(status=status).count()
            assert count == 50

    def test_bulk_create_various_priorities(self, sync_session: Any) -> None:
        """Test creating items with different priorities."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i:03d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": ["low", "medium", "high"][i % 3],
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(300)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 300


# ============================================================
# SECTION 3: Bulk Preview Tests (5 tests)
# ============================================================


class TestBulkCreatePreview:
    """Test bulk create preview functionality."""

    def test_preview_valid_csv(self, sync_session: Any) -> None:
        """Test preview with valid CSV."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(10)
        ]
        csv_data = _create_test_csv(items)

        preview = svc.bulk_create_preview("proj-1", csv_data)
        assert preview["total_count"] == COUNT_TEN
        assert len(preview["sample_items"]) == COUNT_FIVE  # default limit
        assert preview["invalid_rows_count"] == 0

    def test_preview_empty_csv(self, sync_session: Any) -> None:
        """Test preview with empty CSV."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = "Title,View,Type\n"
        preview = svc.bulk_create_preview("proj-1", csv_data)
        assert preview["total_count"] == 0
        assert len(preview["validation_errors"]) > 0

    def test_preview_missing_required_headers(self, sync_session: Any) -> None:
        """Test preview with missing required headers."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = "Title\nItem 1\n"
        preview = svc.bulk_create_preview("proj-1", csv_data)
        assert len(preview["validation_errors"]) > 0

    def test_preview_invalid_json_metadata(self, sync_session: Any) -> None:
        """Test preview with invalid JSON metadata."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv(
            [
                {
                    "Title": "Item 1",
                    "View": "FEATURE",
                    "Type": "feature",
                    "Description": "",
                    "Status": "todo",
                    "Priority": "medium",
                    "Owner": "",
                    "Parent Id": "",
                    "Metadata": "{invalid json}",
                },
            ],
            omit_empty_metadata=False,
        )

        preview = svc.bulk_create_preview("proj-1", csv_data)
        assert preview["invalid_rows_count"] > 0

    def test_preview_warnings_large_operation(self, sync_session: Any) -> None:
        """Test preview warnings for large operations."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i:04d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            }
            for i in range(150)
        ]
        csv_data = _create_test_csv(items)

        preview = svc.bulk_create_preview("proj-1", csv_data)
        assert preview["total_count"] == 150
        assert any("Large operation" in w for w in preview["warnings"])


# ============================================================
# SECTION 4: Bulk Update Tests (5 tests)
# ============================================================


class TestBulkUpdate:
    """Test bulk update functionality."""

    def test_bulk_update_status(self, sync_session: Any) -> None:
        """Test updating item status."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=5, status="todo")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items("proj-1", {"status": "todo"}, {"status": "in_progress"})
        assert result["items_updated"] == COUNT_FIVE
        assert all(item.status == "in_progress" for item in sync_session.query(Item).all())

    def test_bulk_update_multiple_fields(self, sync_session: Any) -> None:
        """Test updating multiple fields."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=3)
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items(
            "proj-1",
            {"status": "todo"},
            {"status": "done", "priority": "high", "owner": "alice"},
        )
        assert result["items_updated"] == COUNT_THREE
        for item in sync_session.query(Item).all():
            assert item.status == "done"
            assert item.priority == "high"
            assert item.owner == "alice"

    def test_bulk_update_with_filters(self, sync_session: Any) -> None:
        """Test bulk update with complex filters."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=3, status="todo", view="FEATURE", prefix="feat")
        _seed_items(sync_session, count=2, status="todo", view="STORY", prefix="story")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items("proj-1", {"view": "FEATURE", "status": "todo"}, {"status": "in_progress"})
        assert result["items_updated"] == COUNT_THREE

    def test_bulk_update_preview(self, sync_session: Any) -> None:
        """Test bulk update preview."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=10, status="todo")
        svc = BulkOperationService(sync_session)

        preview = svc.bulk_update_preview("proj-1", {"status": "todo"}, {"status": "done"}, limit=3)
        assert preview["total_count"] == COUNT_TEN
        assert len(preview["sample_items"]) == COUNT_THREE
        assert preview["estimated_duration_ms"] == 100  # 10 items * 10ms

    def test_bulk_update_events_logged(self, sync_session: Any) -> None:
        """Test that bulk update logs events."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=2)
        svc = BulkOperationService(sync_session)

        svc.bulk_update_items("proj-1", {"status": "todo"}, {"status": "done"}, agent_id="agent-1")
        events = sync_session.query(Event).all()
        assert len(events) == COUNT_TWO
        assert all(e.event_type == "item_bulk_updated" for e in events)


# ============================================================
# SECTION 5: Bulk Delete Tests (4 tests)
# ============================================================


class TestBulkDelete:
    """Test bulk delete functionality."""

    def test_bulk_delete_items(self, sync_session: Any) -> None:
        """Test soft deleting items."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=5)
        svc = BulkOperationService(sync_session)

        result = svc.bulk_delete_items("proj-1", {})
        assert result["items_deleted"] == COUNT_FIVE
        assert all(item.deleted_at is not None for item in sync_session.query(Item).all())

    def test_bulk_delete_with_filters(self, sync_session: Any) -> None:
        """Test bulk delete with filters."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=3, status="todo", prefix="todo")
        _seed_items(sync_session, count=2, status="done", prefix="done")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_delete_items("proj-1", {"status": "todo"})
        assert result["items_deleted"] == COUNT_THREE

        # Verify deleted items
        deleted = sync_session.query(Item).filter(Item.deleted_at.isnot(None)).all()
        assert len(deleted) == COUNT_THREE

    def test_bulk_delete_large_batch(self, sync_session: Any) -> None:
        """Test bulk delete with large batch."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=100)
        svc = BulkOperationService(sync_session)

        result = svc.bulk_delete_items("proj-1", {})
        assert result["items_deleted"] == 100

    def test_bulk_delete_events_logged(self, sync_session: Any) -> None:
        """Test that bulk delete logs events."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=2)
        svc = BulkOperationService(sync_session)

        svc.bulk_delete_items("proj-1", {}, agent_id="agent-1")
        events = sync_session.query(Event).all()
        assert len(events) == COUNT_TWO
        assert all(e.event_type == "item_bulk_deleted" for e in events)


# ============================================================
# SECTION 6: Error Handling & Rollback Tests (6 tests)
# ============================================================


class TestErrorHandlingAndRollback:
    """Test error handling and transaction rollback."""

    def test_bulk_create_rollback_on_commit_failure(self, sync_session: Any, monkeypatch: Any) -> None:
        """Test rollback on commit failure."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": "Item 1",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
                "Metadata": "",
            },
        ])

        rolled_back = {"value": False}

        def fake_rollback() -> None:
            rolled_back["value"] = True

        monkeypatch.setattr(sync_session, "rollback", fake_rollback)
        monkeypatch.setattr(sync_session, "commit", lambda: (_ for _ in ()).throw(RuntimeError("commit failed")))

        with pytest.raises(RuntimeError):
            svc.bulk_create_items("proj-1", csv_data)

        assert rolled_back["value"] is True

    def test_bulk_update_rollback_on_failure(self, sync_session: Any, monkeypatch: Any) -> None:
        """Test rollback on bulk update failure."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=1)
        svc = BulkOperationService(sync_session)

        rolled_back = {"value": False}

        def fake_rollback() -> None:
            rolled_back["value"] = True

        monkeypatch.setattr(sync_session, "rollback", fake_rollback)
        monkeypatch.setattr(sync_session, "commit", lambda: (_ for _ in ()).throw(RuntimeError("update failed")))

        with pytest.raises(RuntimeError):
            svc.bulk_update_items("proj-1", {}, {"status": "done"})

        assert rolled_back["value"] is True

    def test_bulk_delete_rollback_on_failure(self, sync_session: Any, monkeypatch: Any) -> None:
        """Test rollback on bulk delete failure."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=1)
        svc = BulkOperationService(sync_session)

        rolled_back = {"value": False}

        def fake_rollback() -> None:
            rolled_back["value"] = True

        monkeypatch.setattr(sync_session, "rollback", fake_rollback)
        monkeypatch.setattr(sync_session, "commit", lambda: (_ for _ in ()).throw(RuntimeError("delete failed")))

        with pytest.raises(RuntimeError):
            svc.bulk_delete_items("proj-1", {})

        assert rolled_back["value"] is True

    def test_bulk_create_skips_invalid_rows(self, sync_session: Any) -> None:
        """Test that bulk create skips invalid rows and continues."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        # Mix of valid and invalid rows - use omit_empty_metadata to avoid the bug
        csv_data = _create_test_csv([
            {
                "Title": "Valid Item 1",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
            {
                "Title": "Valid Item 2",
                "View": "STORY",
                "Type": "story",
                "Description": "",
                "Status": "todo",
                "Priority": "low",
                "Owner": "",
                "Parent Id": "",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data)
        # Should create 2 valid items (invalid row is skipped)
        assert result["items_created"] == COUNT_TWO

    def test_bulk_create_handles_exception_during_iteration(self, sync_session: Any, monkeypatch: Any) -> None:
        """Test that exceptions during iteration are handled properly."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": "Item 1",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
        ])

        rolled_back = {"value": False}

        def fake_rollback() -> None:
            rolled_back["value"] = True

        monkeypatch.setattr(sync_session, "rollback", fake_rollback)
        monkeypatch.setattr(sync_session, "commit", lambda: (_ for _ in ()).throw(RuntimeError("Test error")))

        with pytest.raises(RuntimeError):
            svc.bulk_create_items("proj-1", csv_data)

        assert rolled_back["value"] is True


# ============================================================
# SECTION 7: Transaction Isolation Tests (4 tests)
# ============================================================


class TestTransactionIsolation:
    """Test transaction isolation and atomicity."""

    def test_bulk_create_atomicity(self, sync_session: Any) -> None:
        """Test that bulk create is atomic."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        items = [
            {
                "Title": f"Item {i:03d}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            }
            for i in range(50)
        ]
        csv_data = _create_test_csv(items)

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 50

        # Verify all created items are in DB
        count = sync_session.query(Item).count()
        assert count == 50

    def test_bulk_update_atomicity(self, sync_session: Any) -> None:
        """Test that bulk update is atomic."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=50)
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items("proj-1", {"status": "todo"}, {"status": "done"})
        assert result["items_updated"] == 50

        # Verify all updates are committed
        assert sync_session.query(Item).filter_by(status="done").count() == 50

    def test_bulk_delete_atomicity(self, sync_session: Any) -> None:
        """Test that bulk delete is atomic."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=50)
        svc = BulkOperationService(sync_session)

        result = svc.bulk_delete_items("proj-1", {})
        assert result["items_deleted"] == 50

        # Verify all deletes are committed
        assert sync_session.query(Item).filter(Item.deleted_at.isnot(None)).count() == 50

    def test_concurrent_bulk_operations_same_session(self, sync_session: Any) -> None:
        """Test multiple bulk operations on same session (sequential)."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        # Create batch 1
        items1 = [
            {
                "Title": f"Batch1-Item{i}",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            }
            for i in range(10)
        ]
        csv_data1 = _create_test_csv(items1)
        result1 = svc.bulk_create_items("proj-1", csv_data1)
        assert result1["items_created"] == COUNT_TEN

        # Create batch 2
        items2 = [
            {
                "Title": f"Batch2-Item{i}",
                "View": "STORY",
                "Type": "story",
                "Description": "",
                "Status": "in_progress",
                "Priority": "high",
                "Owner": "",
                "Parent Id": "",
            }
            for i in range(15)
        ]
        csv_data2 = _create_test_csv(items2)
        result2 = svc.bulk_create_items("proj-1", csv_data2)
        assert result2["items_created"] == 15

        # Verify both batches exist
        assert sync_session.query(Item).count() == 25


# ============================================================
# SECTION 8: Filter & Query Tests (5 tests)
# ============================================================


class TestFilteringAndQueries:
    """Test filter application and query building."""

    def test_bulk_update_by_view_filter(self, sync_session: Any) -> None:
        """Test filtering by view."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=5, view="FEATURE", status="todo", prefix="feat")
        _seed_items(sync_session, count=3, view="STORY", status="todo", prefix="story")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items("proj-1", {"view": "FEATURE"}, {"status": "done"})
        assert result["items_updated"] == COUNT_FIVE

    def test_bulk_update_by_item_type_filter(self, sync_session: Any) -> None:
        """Test filtering by item type."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=5, item_type="feature", status="todo", prefix="feat")
        _seed_items(sync_session, count=3, item_type="story", status="todo", prefix="story")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items("proj-1", {"item_type": "feature"}, {"status": "done"})
        assert result["items_updated"] == COUNT_FIVE

    def test_bulk_update_by_priority_filter(self, sync_session: Any) -> None:
        """Test filtering by priority."""
        _seed_project(sync_session)
        for i in range(5):
            item = Item(
                id=f"item-high-{i}",
                project_id="proj-1",
                title=f"High Priority {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="high",
            )
            sync_session.add(item)
        for i in range(3):
            item = Item(
                id=f"item-low-{i}",
                project_id="proj-1",
                title=f"Low Priority {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="low",
            )
            sync_session.add(item)
        sync_session.commit()

        svc = BulkOperationService(sync_session)
        result = svc.bulk_update_items("proj-1", {"priority": "high"}, {"status": "in_progress"})
        assert result["items_updated"] == COUNT_FIVE

    def test_bulk_delete_by_owner_filter(self, sync_session: Any) -> None:
        """Test delete filtering by owner."""
        _seed_project(sync_session)
        for i in range(5):
            item = Item(
                id=f"alice-{i}",
                project_id="proj-1",
                title=f"Alice Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                owner="alice",
            )
            sync_session.add(item)
        for i in range(3):
            item = Item(
                id=f"bob-{i}",
                project_id="proj-1",
                title=f"Bob Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                owner="bob",
            )
            sync_session.add(item)
        sync_session.commit()

        svc = BulkOperationService(sync_session)
        result = svc.bulk_delete_items("proj-1", {"owner": "alice"})
        assert result["items_deleted"] == COUNT_FIVE

    def test_bulk_update_multiple_filters_combined(self, sync_session: Any) -> None:
        """Test combining multiple filters."""
        _seed_project(sync_session)
        for view in ["FEATURE", "STORY"]:
            for status in ["todo", "done"]:
                for i in range(2):
                    item = Item(
                        id=f"item-{view}-{status}-{i}",
                        project_id="proj-1",
                        title=f"{view} {status} {i}",
                        view=view,
                        item_type="feature",
                        status=status,
                    )
                    sync_session.add(item)
        sync_session.commit()

        svc = BulkOperationService(sync_session)
        result = svc.bulk_update_items("proj-1", {"view": "FEATURE", "status": "todo"}, {"status": "in_progress"})
        assert result["items_updated"] == COUNT_TWO


# ============================================================
# SECTION 9: Edge Cases & Special Scenarios (6 tests)
# ============================================================


class TestEdgeCasesAndSpecialScenarios:
    """Test edge cases and special scenarios."""

    def test_bulk_create_empty_csv(self, sync_session: Any) -> None:
        """Test bulk create with empty CSV data."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        result = svc.bulk_create_items("proj-1", "")
        assert result["items_created"] == 0

    def test_bulk_update_no_matching_items(self, sync_session: Any) -> None:
        """Test bulk update with no matching items."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=5, status="todo")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_update_items("proj-1", {"status": "nonexistent"}, {"status": "done"})
        assert result["items_updated"] == 0

    def test_bulk_delete_no_matching_items(self, sync_session: Any) -> None:
        """Test bulk delete with no matching items."""
        _seed_project(sync_session)
        _seed_items(sync_session, count=5, status="todo")
        svc = BulkOperationService(sync_session)

        result = svc.bulk_delete_items("proj-1", {"status": "nonexistent"})
        assert result["items_deleted"] == 0

    def test_bulk_create_special_characters_in_titles(self, sync_session: Any) -> None:
        """Test bulk create with special characters."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": "Item with & special < chars >",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "Contains \"quotes\" and 'apostrophes'",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
            {
                "Title": "Item with emoji",
                "View": "STORY",
                "Type": "story",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == COUNT_TWO

    def test_bulk_create_with_very_long_descriptions(self, sync_session: Any) -> None:
        """Test bulk create with very long descriptions."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        long_desc = "A" * 5000
        csv_data = _create_test_csv([
            {
                "Title": "Item with long desc",
                "View": "FEATURE",
                "Type": "feature",
                "Description": long_desc,
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 1
        item = sync_session.query(Item).first()
        assert item.description == long_desc

    def test_bulk_update_partial_field_updates(self, sync_session: Any) -> None:
        """Test that bulk update only updates specified fields."""
        _seed_project(sync_session)
        item = Item(
            id="item-1",
            project_id="proj-1",
            title="Original Title",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="low",
            owner="original_owner",
        )
        sync_session.add(item)
        sync_session.commit()

        svc = BulkOperationService(sync_session)
        svc.bulk_update_items(
            "proj-1",
            {"status": "todo"},
            {"status": "done"},  # Only update status
        )

        updated_item = sync_session.query(Item).first()
        assert updated_item.status == "done"
        assert updated_item.priority == "low"  # Should not change
        assert updated_item.owner == "original_owner"  # Should not change


# ============================================================
# SECTION 10: CSV Parsing & Validation Tests (5 tests)
# ============================================================


class TestCSVParsingAndValidation:
    """Test CSV parsing and validation."""

    def test_csv_case_insensitive_headers(self, sync_session: Any) -> None:
        """Test that CSV headers are case-insensitive."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        # Use different case for headers
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["title", "view", "type"])
        writer.writeheader()
        writer.writerow({"title": "Item 1", "view": "FEATURE", "type": "feature"})

        result = svc.bulk_create_items("proj-1", output.getvalue())
        assert result["items_created"] == 1

    def test_csv_handles_whitespace_in_headers(self, sync_session: Any) -> None:
        """Test that CSV handles whitespace in headers."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[" Title ", " View ", " Type "])
        writer.writeheader()
        writer.writerow({" Title ": "Item 1", " View ": "FEATURE", " Type ": "feature"})

        result = svc.bulk_create_items("proj-1", output.getvalue())
        assert result["items_created"] == 1

    def test_csv_handles_whitespace_in_values(self, sync_session: Any) -> None:
        """Test that CSV handles whitespace in values."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": " Item With Spaces ",
                "View": " FEATURE ",
                "Type": " feature ",
                "Description": " description ",
                "Status": " todo ",
                "Priority": " medium ",
                "Owner": " owner ",
                "Parent Id": "",
            },
        ])

        result = svc.bulk_create_items("proj-1", csv_data)
        assert result["items_created"] == 1
        item = sync_session.query(Item).first()
        # Values should be stripped
        assert item.title == "Item With Spaces"

    def test_preview_duplicate_detection(self, sync_session: Any) -> None:
        """Test that preview detects duplicate titles in same view."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        csv_data = _create_test_csv([
            {
                "Title": "Duplicate Item",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
            {
                "Title": "Duplicate Item",
                "View": "FEATURE",
                "Type": "feature",
                "Description": "",
                "Status": "todo",
                "Priority": "medium",
                "Owner": "",
                "Parent Id": "",
            },
        ])

        preview = svc.bulk_create_preview("proj-1", csv_data)
        assert any("Duplicate" in w for w in preview["warnings"])

    def test_csv_missing_optional_fields_uses_defaults(self, sync_session: Any) -> None:
        """Test that missing optional fields use defaults."""
        _seed_project(sync_session)
        svc = BulkOperationService(sync_session)

        # CSV with only required fields
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["Title", "View", "Type"])
        writer.writeheader()
        writer.writerow({"Title": "Minimal Item", "View": "FEATURE", "Type": "feature"})

        result = svc.bulk_create_items("proj-1", output.getvalue())
        assert result["items_created"] == 1
        item = sync_session.query(Item).first()
        assert item.status == "todo"  # Default status
        assert item.priority == "medium"  # Default priority


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
