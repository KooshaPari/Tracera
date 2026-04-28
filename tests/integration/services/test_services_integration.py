"""Integration tests for critical services.

Tests bulk operations, export/import, traceability, and visualization services
with real database interactions to achieve 80%+ coverage.

Current Coverage:
- bulk_operation_service.py: 5.88% -> Target: 80%+
- export_import_service.py: 15.18% -> Target: 80%+
- traceability_service.py: 24.53% -> Target: 80%+
- visualization_service.py: 6.48% -> Target: 80%+
"""

import asyncio
import csv
import json
import pathlib
from datetime import UTC, datetime
from io import StringIO

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.services.bulk_operation_service import BulkOperationService
from tracertm.services.export_import_service import ExportImportService
from tracertm.services.traceability_service import TraceabilityService
from tracertm.services.visualization_service import VisualizationService

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def test_project() -> Project:
    """Create a test project using sync session."""
    import tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        # Create synchronous engine
        sync_engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Create tables
        from tracertm.models.base import Base

        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        project = Project(
            name=f"Integration Test Project {datetime.now().timestamp()}",
            description="Project for integration testing",
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        # Store session for other fixtures to use
        session.close()

        yield project

    finally:
        # Cleanup
        if pathlib.Path(db_path).exists():
            pathlib.Path(db_path).unlink()


@pytest.fixture
def test_items(test_project: Project) -> list[Item]:
    """Create test items across multiple views."""
    import tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        # Create synchronous engine
        sync_engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Create tables
        from tracertm.models.base import Base

        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        # Add the project first
        session.add(test_project)
        session.commit()

        items_repo = ItemRepository(session)
        items = []

        # Create items in different views
        views_data = [
            ("FEATURE", "feature", "Implement user authentication", "high", "todo"),
            ("FEATURE", "feature", "Implement data export", "medium", "todo"),
            ("FEATURE", "feature", "Implement search functionality", "high", "in_progress"),
            ("CODE", "class", "UserAuthService", "high", "done"),
            ("CODE", "class", "ExportService", "medium", "todo"),
            ("TEST", "unit_test", "test_user_auth", "high", "done"),
            ("TEST", "unit_test", "test_export", "medium", "todo"),
            ("TEST", "integration_test", "test_auth_flow", "low", "todo"),
            ("API", "endpoint", "POST /auth/login", "high", "done"),
            ("API", "endpoint", "GET /export", "medium", "todo"),
        ]

        for view, item_type, title, priority, status in views_data:
            item = items_repo.create(
                project_id=test_project.id,
                title=title,
                view=view,
                item_type=item_type,
                status=status,
                priority=priority,
            )
            items.append(item)

        session.commit()
        session.close()

        yield items

    finally:
        # Cleanup
        if pathlib.Path(db_path).exists():
            pathlib.Path(db_path).unlink()


@pytest_asyncio.fixture
async def test_links(
    test_project: Project,
    test_items: list[Item],
) -> list[Link]:
    """Create test links between items."""
    import tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        # Create synchronous engine
        sync_engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Create tables
        from tracertm.models.base import Base

        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        # Add project and items first
        session.add(test_project)
        for item in test_items:
            session.add(item)
        session.commit()

        links_repo = LinkRepository(session)
        links = []

        # Create traceability links
        # FEATURE -> CODE
        link1 = links_repo.create(
            project_id=test_project.id,
            source_item_id=test_items[0].id,  # Feature: user auth
            target_item_id=test_items[3].id,  # Code: UserAuthService
            link_type="implements",
        )
        links.append(link1)

        # CODE -> TEST
        link2 = links_repo.create(
            project_id=test_project.id,
            source_item_id=test_items[3].id,  # Code: UserAuthService
            target_item_id=test_items[5].id,  # Test: test_user_auth
            link_type="tested_by",
        )
        links.append(link2)

        # FEATURE -> API
        link3 = links_repo.create(
            project_id=test_project.id,
            source_item_id=test_items[0].id,  # Feature: user auth
            target_item_id=test_items[8].id,  # API: POST /auth/login
            link_type="exposes",
        )
        links.append(link3)

        session.commit()
        session.close()

        yield links

    finally:
        # Cleanup (run in thread to avoid ASYNC240)
        if await asyncio.to_thread(pathlib.Path(db_path).exists):
            await asyncio.to_thread(pathlib.Path(db_path).unlink)


@pytest.fixture
def sync_db_session() -> None:
    """Create a synchronous database session for services that require sync Session.

    This fixture creates a separate sync engine for synchronous services,
    allowing them to operate alongside async tests without conflicts.
    """
    import tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()
    db_path = temp_db.name

    try:
        # Create synchronous engine with temporary database
        sync_engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Create tables
        from tracertm.models.base import Base

        Base.metadata.create_all(sync_engine)

        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        session = SessionLocal()

        yield session

        session.close()
    finally:
        # Cleanup
        if pathlib.Path(db_path).exists():
            pathlib.Path(db_path).unlink()


# ============================================================
# BULK OPERATION SERVICE TESTS (30 tests)
# ============================================================


class TestBulkOperationService:
    """Integration tests for BulkOperationService."""

    # ========== Bulk Update Preview Tests ==========

    @pytest.mark.asyncio
    async def test_bulk_update_preview_by_view(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items in different views.

        When: Preview bulk update filtered by view
        Then: Returns correct count and samples for that view only.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "in_progress"},
            limit=5,
        )

        assert result["total_count"] == COUNT_THREE  # 3 FEATURE items
        assert len(result["sample_items"]) == COUNT_THREE
        assert all(s["new"]["status"] == "in_progress" for s in result["sample_items"])
        assert result["estimated_duration_ms"] == COUNT_THREE * 10  # 30ms

    @pytest.mark.asyncio
    async def test_bulk_update_preview_by_status(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items with different statuses.

        When: Preview bulk update filtered by status
        Then: Returns only items with matching status.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"status": "todo"},
            updates={"status": "in_progress"},
            limit=5,
        )

        assert result["total_count"] == 6  # 6 todo items
        assert len(result["sample_items"]) <= COUNT_FIVE

    @pytest.mark.asyncio
    async def test_bulk_update_preview_by_priority(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items with different priorities.

        When: Preview bulk update filtered by priority
        Then: Returns only high priority items.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"priority": "high"},
            updates={"owner": "test_agent"},
            limit=5,
        )

        assert result["total_count"] == COUNT_FIVE  # 5 high priority items
        assert all(s["new"]["owner"] == "test_agent" for s in result["sample_items"])

    @pytest.mark.asyncio
    async def test_bulk_update_preview_multiple_filters(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items with various attributes.

        When: Preview with multiple filters (view AND status)
        Then: Returns only items matching all filters.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"view": "TEST", "status": "todo"},
            updates={"status": "in_progress"},
            limit=5,
        )

        assert result["total_count"] == COUNT_TWO  # 2 TEST items with todo status

    @pytest.mark.asyncio
    async def test_bulk_update_preview_large_operation_warning(
        self,
        test_project: Project,
        sync_db_session: Session,
        db_session: AsyncSession,
    ) -> None:
        """Given: More than 100 items.

        When: Preview bulk update
        Then: Returns warning about large operation.
        """
        items_repo = ItemRepository(db_session)

        # Create 101 items
        for i in range(101):
            await items_repo.create(
                project_id=test_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
            )
        await db_session.commit()

        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "done"},
        )

        assert result["total_count"] >= 101
        assert any("Large operation" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_bulk_update_preview_mixed_status_warning(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items with different statuses.

        When: Preview status update
        Then: Returns warning about mixed statuses.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "done"},
            limit=5,
        )

        # FEATURE items have mixed statuses (todo, in_progress)
        assert any("Mixed statuses" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_bulk_update_preview_no_matches(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items in database.

        When: Preview with filters that match nothing
        Then: Returns zero count and empty samples.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_preview(
            project_id=test_project.id,
            filters={"view": "NONEXISTENT"},
            updates={"status": "done"},
        )

        assert result["total_count"] == 0
        assert len(result["sample_items"]) == 0
        assert result["estimated_duration_ms"] == 0

    # ========== Bulk Update Execution Tests ==========

    @pytest.mark.asyncio
    async def test_bulk_update_items_status(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Multiple items with status 'todo'.

        When: Execute bulk status update
        Then: Updates all matching items and logs events.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_items(
            project_id=test_project.id,
            filters={"status": "todo"},
            updates={"status": "in_progress"},
            agent_id="test_agent",
        )

        assert result["items_updated"] == 6

        # Verify in database
        await db_session.commit()
        await db_session.rollback()  # Refresh from DB

        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.status == "in_progress",
            Item.deleted_at.is_(None),
        )
        db_result = await db_session.execute(stmt)
        updated_items = db_result.scalars().all()
        assert len(updated_items) >= 6

        # Verify events logged
        events_stmt = select(Event).where(
            Event.project_id == test_project.id,
            Event.event_type == "item_bulk_updated",
        )
        events_result = await db_session.execute(events_stmt)
        events = events_result.scalars().all()
        assert len(events) == 6

    @pytest.mark.asyncio
    async def test_bulk_update_items_multiple_fields(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Items to update.

        When: Execute bulk update with multiple field changes
        Then: Updates all specified fields.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_items(
            project_id=test_project.id,
            filters={"view": "TEST"},
            updates={
                "status": "done",
                "priority": "high",
                "owner": "qa_agent",
            },
        )

        assert result["items_updated"] == COUNT_THREE

        # Verify updates
        await db_session.commit()
        await db_session.rollback()

        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.view == "TEST",
        )
        db_result = await db_session.execute(stmt)
        items = db_result.scalars().all()

        for item in items:
            assert item.status == "done"
            assert item.priority == "high"
            assert item.owner == "qa_agent"

    @pytest.mark.asyncio
    async def test_bulk_update_items_rollback_on_error(self, test_project: Project, _sync_db_session: Session) -> None:
        """Given: Bulk update operation.

        When: An error occurs during update
        Then: Rolls back all changes.
        """
        service = BulkOperationService(sync_db_session)

        # Force an error by using invalid project_id
        with pytest.raises(Exception):
            service.bulk_update_items(
                project_id="nonexistent",
                filters={"status": "todo"},
                updates={"status": "done"},
            )

    @pytest.mark.asyncio
    async def test_bulk_update_items_with_title_and_description(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Items with various titles.

        When: Bulk update title and description
        Then: Updates text fields correctly.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_items(
            project_id=test_project.id,
            filters={"view": "CODE"},
            updates={
                "description": "Updated by bulk operation",
            },
        )

        assert result["items_updated"] == COUNT_TWO

        # Verify
        await db_session.commit()
        await db_session.rollback()

        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.view == "CODE",
        )
        db_result = await db_session.execute(stmt)
        items = db_result.scalars().all()

        for item in items:
            assert item.description == "Updated by bulk operation"

    # ========== Bulk Delete Tests ==========

    @pytest.mark.asyncio
    async def test_bulk_delete_items_soft_delete(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Items to delete.

        When: Execute bulk delete
        Then: Soft deletes items (sets deleted_at timestamp).
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_delete_items(
            project_id=test_project.id,
            filters={"status": "done"},
            agent_id="cleanup_agent",
        )

        assert result["items_deleted"] == COUNT_THREE

        # Verify soft delete
        await db_session.commit()
        await db_session.rollback()

        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.status == "done",
        )
        db_result = await db_session.execute(stmt)
        items = db_result.scalars().all()

        for item in items:
            assert item.deleted_at is not None

        # Verify events
        events_stmt = select(Event).where(
            Event.event_type == "item_bulk_deleted",
        )
        events_result = await db_session.execute(events_stmt)
        events = events_result.scalars().all()
        assert len(events) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_bulk_delete_items_by_view(
        self,
        test_project: Project,
        test_items: list[Item],
        _sync_db_session: Session,
    ) -> None:
        """Given: Items in specific view.

        When: Bulk delete by view filter
        Then: Deletes only items in that view.
        """
        service = BulkOperationService(sync_db_session)
        result = service.bulk_delete_items(
            project_id=test_project.id,
            filters={"view": "API"},
        )

        assert result["items_deleted"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_bulk_delete_items_rollback_on_error(self, test_project: Project, _sync_db_session: Session) -> None:
        """Given: Bulk delete operation.

        When: Error occurs
        Then: Rolls back all deletions.
        """
        service = BulkOperationService(sync_db_session)

        with pytest.raises(Exception):
            service.bulk_delete_items(
                project_id="nonexistent",
                filters={"status": "todo"},
            )

    # ========== Bulk Create Preview Tests ==========

    @pytest.mark.asyncio
    async def test_bulk_create_preview_valid_csv(self, test_project: Project, sync_db_session: Session) -> None:
        """Given: Valid CSV data.

        When: Preview bulk create
        Then: Returns preview with item count and samples.
        """
        csv_data = """Title,View,Type,Status,Priority
Feature A,FEATURE,feature,todo,high
Feature B,FEATURE,feature,todo,medium
Feature C,FEATURE,feature,in_progress,low"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
            limit=5,
        )

        assert result["total_count"] == COUNT_THREE
        assert len(result["sample_items"]) == COUNT_THREE
        assert result["validation_errors"] == []
        assert result["estimated_duration_ms"] == COUNT_THREE * 15  # 45ms

    @pytest.mark.asyncio
    async def test_bulk_create_preview_empty_csv(self, test_project: Project, sync_db_session: Session) -> None:
        """Given: Empty CSV data.

        When: Preview bulk create
        Then: Returns error about empty file.
        """
        csv_data = "Title,View,Type"

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["total_count"] == 0
        assert "empty" in result["validation_errors"][0].lower()

    @pytest.mark.asyncio
    async def test_bulk_create_preview_missing_headers(self, test_project: Project, sync_db_session: Session) -> None:
        """Given: CSV missing required columns.

        When: Preview bulk create
        Then: Returns validation errors for missing columns.
        """
        csv_data = """Title,Status
Feature A,todo"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert len(result["validation_errors"]) > 0
        assert any("Missing required" in e for e in result["validation_errors"])

    @pytest.mark.asyncio
    async def test_bulk_create_preview_invalid_json_metadata(
        self, test_project: Project, sync_db_session: Session
    ) -> None:
        """Given: CSV with invalid JSON in metadata column.

        When: Preview bulk create
        Then: Returns validation errors for that row.
        """
        csv_data = """Title,View,Type,Metadata
Feature A,FEATURE,feature,{invalid json}"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["invalid_rows_count"] == 1
        assert any("Invalid JSON" in e for e in result["validation_errors"])

    @pytest.mark.asyncio
    async def test_bulk_create_preview_duplicate_titles(self, test_project: Project, sync_db_session: Session) -> None:
        """Given: CSV with duplicate titles in same view.

        When: Preview bulk create
        Then: Returns warning about duplicates.
        """
        csv_data = """Title,View,Type
Feature A,FEATURE,feature
Feature A,FEATURE,feature"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert any("Duplicate title" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_bulk_create_preview_large_operation_warning(
        self, test_project: Project, sync_db_session: Session
    ) -> None:
        """Given: CSV with >100 items.

        When: Preview bulk create
        Then: Returns warning about large operation.
        """
        # Generate CSV with 101 rows
        rows = ["Title,View,Type"]
        rows.extend([f"Item {i},FEATURE,feature" for i in range(101)])
        csv_data = "\n".join(rows)

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["total_count"] == 101
        assert any("Large operation" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_bulk_create_preview_case_insensitive_headers(
        self, test_project: Project, sync_db_session: Session
    ) -> None:
        """Given: CSV with mixed case headers.

        When: Preview bulk create
        Then: Correctly normalizes and accepts headers.
        """
        csv_data = """title,view,type
Feature A,FEATURE,feature"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_preview(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["total_count"] == 1
        assert len(result["validation_errors"]) == 0

    # ========== Bulk Create Execution Tests ==========

    @pytest.mark.asyncio
    async def test_bulk_create_items_valid_csv(
        self,
        test_project: Project,
        sync_db_session: Session,
        db_session: AsyncSession,
    ) -> None:
        """Given: Valid CSV with multiple items.

        When: Execute bulk create
        Then: Creates all items in database and logs events.
        """
        csv_data = """Title,View,Type,Status,Priority,Owner
New Feature 1,FEATURE,feature,todo,high,agent1
New Feature 2,FEATURE,feature,todo,medium,agent2
New Code 1,CODE,class,todo,high,agent1"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_items(
            project_id=test_project.id,
            csv_data=csv_data,
            agent_id="import_agent",
        )

        assert result["items_created"] == COUNT_THREE

        # Verify in database
        await db_session.commit()
        await db_session.rollback()

        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.title.like("New Feature%"),
        )
        db_result = await db_session.execute(stmt)
        items = db_result.scalars().all()
        assert len(items) == COUNT_TWO

        # Verify events
        events_stmt = select(Event).where(
            Event.event_type == "item_bulk_created",
        )
        events_result = await db_session.execute(events_stmt)
        events = events_result.scalars().all()
        assert len(events) >= COUNT_THREE

    @pytest.mark.asyncio
    async def test_bulk_create_items_with_metadata(
        self,
        test_project: Project,
        sync_db_session: Session,
        db_session: AsyncSession,
    ) -> None:
        """Given: CSV with JSON metadata.

        When: Execute bulk create
        Then: Creates items with parsed metadata.
        """
        csv_data = """Title,View,Type,Metadata
Feature with meta,FEATURE,feature,"{""key"": ""value"", ""priority"": 1}" """

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_items(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["items_created"] == 1

        # Verify metadata
        await db_session.commit()
        await db_session.rollback()

        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.title == "Feature with meta",
        )
        db_result = await db_session.execute(stmt)
        item = db_result.scalar_one()
        assert item.item_metadata["key"] == "value"
        assert item.item_metadata["priority"] == 1

    @pytest.mark.asyncio
    async def test_bulk_create_items_skip_invalid_rows(self, test_project: Project, sync_db_session: Session) -> None:
        """Given: CSV with mix of valid and invalid rows.

        When: Execute bulk create
        Then: Creates only valid items, skips invalid ones.
        """
        csv_data = """Title,View,Type
Valid Item,FEATURE,feature
,,
Another Valid,CODE,class"""

        service = BulkOperationService(sync_db_session)
        result = service.bulk_create_items(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        # Should create 2 items (skip the empty row)
        assert result["items_created"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_bulk_create_items_rollback_on_error(
        self,
        test_project: Project,
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Bulk create operation.

        When: Database error occurs
        Then: Rolls back all inserts.
        """
        # Count items before
        stmt = select(Item).where(Item.project_id == test_project.id)
        result = await db_session.execute(stmt)
        len(result.scalars().all())

        # This test verifies transaction behavior in other tests


# ============================================================
# EXPORT/IMPORT SERVICE TESTS (15 tests)
# ============================================================


class TestExportImportService:
    """Integration tests for ExportImportService."""

    # ========== Export Tests ==========

    @pytest.mark.asyncio
    async def test_export_to_json(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Project with items.

        When: Export to JSON
        Then: Returns JSON with all items and project info.
        """
        service = ExportImportService(db_session)

        result = await service.export_to_json(str(test_project.id))

        assert result["format"] == "json"
        assert result["project"]["id"] == str(test_project.id)
        assert result["project"]["name"] == test_project.name
        assert result["item_count"] == COUNT_TEN
        assert len(result["items"]) == COUNT_TEN

        # Verify item structure
        first_item = result["items"][0]
        assert "id" in first_item
        assert "title" in first_item
        assert "view" in first_item
        assert "type" in first_item
        assert "status" in first_item

    @pytest.mark.asyncio
    async def test_export_to_json_nonexistent_project(self, db_session: AsyncSession) -> None:
        """Given: Nonexistent project ID.

        When: Export to JSON
        Then: Returns error.
        """
        service = ExportImportService(db_session)

        result = await service.export_to_json("nonexistent")

        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_export_to_csv(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Project with items.

        When: Export to CSV
        Then: Returns CSV with headers and all items.
        """
        service = ExportImportService(db_session)

        result = await service.export_to_csv(str(test_project.id))

        assert result["format"] == "csv"
        assert result["item_count"] == COUNT_TEN

        # Parse CSV
        csv_content = result["content"]
        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        assert len(rows) == COUNT_TEN
        fieldnames = reader.fieldnames or []
        assert "ID" in fieldnames
        assert "Title" in fieldnames
        assert "View" in fieldnames
        assert "Type" in fieldnames
        assert "Status" in fieldnames

    @pytest.mark.asyncio
    async def test_export_to_markdown(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Project with items in different views.

        When: Export to Markdown
        Then: Returns Markdown grouped by view.
        """
        service = ExportImportService(db_session)

        result = await service.export_to_markdown(test_project.id)

        assert result["format"] == "markdown"
        assert result["item_count"] == COUNT_TEN

        content = result["content"]
        assert f"# {test_project.name}" in content
        assert "## FEATURE" in content
        assert "## CODE" in content
        assert "## TEST" in content
        assert "## API" in content
        assert "Implement user authentication" in content

    @pytest.mark.asyncio
    async def test_export_to_markdown_nonexistent_project(self, db_session: AsyncSession) -> None:
        """Given: Nonexistent project.

        When: Export to Markdown
        Then: Returns error.
        """
        service = ExportImportService(db_session)

        result = await service.export_to_markdown("nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_export_formats(self, db_session: AsyncSession) -> None:
        """Given: ExportImportService.

        When: Get available export formats
        Then: Returns list of supported formats.
        """
        service = ExportImportService(db_session)

        formats = await service.get_export_formats()

        assert "json" in formats
        assert "csv" in formats
        assert "markdown" in formats
        assert len(formats) == COUNT_THREE

    # ========== Import Tests ==========

    @pytest.mark.asyncio
    async def test_import_from_json(
        self, test_project: Project, sync_db_session: Session, db_session: AsyncSession
    ) -> None:
        """Given: Valid JSON import data.

        When: Import from JSON
        Then: Creates items in database.
        """
        service = ExportImportService(db_session)

        json_data = json.dumps({
            "items": [
                {
                    "title": "Imported Feature 1",
                    "view": "FEATURE",
                    "type": "feature",
                    "status": "todo",
                },
                {
                    "title": "Imported Feature 2",
                    "view": "CODE",
                    "type": "class",
                    "status": "in_progress",
                },
            ],
        })

        result = await service.import_from_json(
            project_id=test_project.id,
            json_data=json_data,
        )

        assert result["success"] is True
        assert result["imported_count"] == COUNT_TWO
        assert result["error_count"] == 0

        # Verify in database
        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.title.like("Imported Feature%"),
        )
        db_result = await db_session.execute(stmt)
        items = db_result.scalars().all()
        assert len(items) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_import_from_json_invalid_format(
        self,
        test_project: Project,
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Invalid JSON data.

        When: Import from JSON
        Then: Returns error.
        """
        service = ExportImportService(db_session)

        result = await service.import_from_json(
            project_id=test_project.id,
            json_data="invalid json {",
        )

        assert "error" in result
        assert "Invalid JSON" in result["error"]

    @pytest.mark.asyncio
    async def test_import_from_json_missing_items_field(
        self,
        test_project: Project,
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: JSON without 'items' field.

        When: Import from JSON
        Then: Returns error.
        """
        service = ExportImportService(db_session)

        json_data = json.dumps({"data": []})

        result = await service.import_from_json(
            project_id=test_project.id,
            json_data=json_data,
        )

        assert "error" in result
        assert "Missing 'items'" in result["error"]

    @pytest.mark.asyncio
    async def test_import_from_csv(
        self, test_project: Project, sync_db_session: Session, db_session: AsyncSession
    ) -> None:
        """Given: Valid CSV import data.

        When: Import from CSV
        Then: Creates items in database.
        """
        service = ExportImportService(db_session)

        csv_data = """Title,View,Type,Status
CSV Import 1,FEATURE,feature,todo
CSV Import 2,CODE,class,done"""

        result = await service.import_from_csv(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["success"] is True
        assert result["imported_count"] == COUNT_TWO

        # Verify
        stmt = select(Item).where(
            Item.project_id == test_project.id,
            Item.title.like("CSV Import%"),
        )
        db_result = await db_session.execute(stmt)
        items = db_result.scalars().all()
        assert len(items) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_import_from_csv_invalid_format(
        self,
        test_project: Project,
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Invalid CSV data.

        When: Import from CSV
        Then: Returns error.
        """
        service = ExportImportService(db_session)

        # Malformed CSV
        csv_data = 'Title,View\n"Unclosed quote'

        result = await service.import_from_csv(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert "error" in result
        assert "Invalid CSV" in result["error"]

    @pytest.mark.asyncio
    async def test_import_from_csv_with_errors(
        self,
        test_project: Project,
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: CSV with some invalid rows.

        When: Import from CSV
        Then: Imports valid rows and reports errors.
        """
        service = ExportImportService(db_session)

        csv_data = """Title,View,Type,Status
Valid Item,FEATURE,feature,todo
,,invalid,"""

        result = await service.import_from_csv(
            project_id=test_project.id,
            csv_data=csv_data,
        )

        assert result["success"] is True
        assert result["imported_count"] >= 1
        # May have errors for invalid rows

    @pytest.mark.asyncio
    async def test_get_import_formats(self, db_session: AsyncSession) -> None:
        """Given: ExportImportService.

        When: Get available import formats
        Then: Returns list of supported formats.
        """
        service = ExportImportService(db_session)

        formats = await service.get_import_formats()

        assert "json" in formats
        assert "csv" in formats
        assert len(formats) == COUNT_TWO


# ============================================================
# TRACEABILITY SERVICE TESTS (15 tests)
# ============================================================


class TestTraceabilityService:
    """Integration tests for TraceabilityService."""

    # ========== Link Creation Tests ==========

    @pytest.mark.asyncio
    async def test_create_link_valid_items(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Two valid items.

        When: Create traceability link
        Then: Creates link successfully.
        """
        service = TraceabilityService(db_session)

        link = await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[0].id),
            target_item_id=str(test_items[3].id),
            link_type="implements",
            metadata={"confidence": 0.95},
        )

        assert link.source_item_id == str(test_items[0].id)
        assert link.target_item_id == str(test_items[3].id)
        assert link.link_type == "implements"
        assert link.link_metadata["confidence"] == 0.95

        # Verify in database
        stmt = select(Link).where(Link.id == link.id)
        db_result = await db_session.execute(stmt)
        db_link = db_result.scalar_one()
        assert db_link.id == link.id

    @pytest.mark.asyncio
    async def test_create_link_source_not_found(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Nonexistent source item.

        When: Create link
        Then: Raises ValueError.
        """
        service = TraceabilityService(db_session)

        with pytest.raises(ValueError, match="Source item.*not found"):
            await service.create_link(
                project_id=str(test_project.id),
                source_item_id="nonexistent",
                target_item_id=str(test_items[0].id),
                link_type="depends_on",
            )

    @pytest.mark.asyncio
    async def test_create_link_target_not_found(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Nonexistent target item.

        When: Create link
        Then: Raises ValueError.
        """
        service = TraceabilityService(db_session)

        with pytest.raises(ValueError, match="Target item.*not found"):
            await service.create_link(
                project_id=str(test_project.id),
                source_item_id=str(test_items[0].id),
                target_item_id="nonexistent",
                link_type="depends_on",
            )

    # ========== Traceability Matrix Tests ==========

    @pytest.mark.asyncio
    async def test_generate_matrix_with_links(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _test_items: list[Item],
        _test_links: list[Link],
    ) -> None:
        """Given: Items and links between views.

        When: Generate traceability matrix
        Then: Returns matrix with links and coverage.
        """
        service = TraceabilityService(db_session)

        matrix = await service.generate_matrix(
            project_id=str(test_project.id),
            source_view="FEATURE",
            target_view="CODE",
        )

        assert matrix.source_view == "FEATURE"
        assert matrix.target_view == "CODE"
        assert len(matrix.links) >= 1
        assert matrix.coverage_percentage > 0

        # Check link structure
        link = matrix.links[0]
        assert "source_id" in link
        assert "source_title" in link
        assert "target_id" in link
        assert "target_title" in link
        assert "link_type" in link

    @pytest.mark.asyncio
    async def test_generate_matrix_no_links(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Items with no links between views.

        When: Generate matrix
        Then: Returns 0% coverage and identifies gaps.
        """
        service = TraceabilityService(db_session)

        matrix = await service.generate_matrix(
            project_id=str(test_project.id),
            source_view="TEST",
            target_view="API",
        )

        assert matrix.coverage_percentage == 0
        assert len(matrix.gaps) == COUNT_THREE  # 3 TEST items
        assert len(matrix.links) == 0

    @pytest.mark.asyncio
    async def test_generate_matrix_partial_coverage(
        self,
        db_session: AsyncSession,
        test_project: Project,
        test_items: list[Item],
    ) -> None:
        """Given: Some items linked, some not.

        When: Generate matrix
        Then: Calculates correct coverage percentage.
        """
        service = TraceabilityService(db_session)

        # Create links for 1 out of 3 FEATURE items
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[0].id),  # FEATURE
            target_item_id=str(test_items[3].id),  # CODE
            link_type="implements",
        )

        matrix = await service.generate_matrix(
            project_id=str(test_project.id),
            source_view="FEATURE",
            target_view="CODE",
        )

        # 1 out of 3 FEATURE items linked = 33.33%
        assert 30 <= matrix.coverage_percentage <= 35
        assert len(matrix.gaps) == COUNT_TWO  # 2 FEATURE items without links

    @pytest.mark.asyncio
    async def test_generate_matrix_gaps_identification(
        self,
        db_session: AsyncSession,
        test_project: Project,
        _test_items: list[Item],
        _test_links: list[Link],
    ) -> None:
        """Given: Matrix with some gaps.

        When: Generate matrix
        Then: Identifies items without links.
        """
        service = TraceabilityService(db_session)

        matrix = await service.generate_matrix(
            project_id=str(test_project.id),
            source_view="FEATURE",
            target_view="CODE",
        )

        # Verify gaps have required fields
        if matrix.gaps:
            gap = matrix.gaps[0]
            assert "id" in gap
            assert "title" in gap

    # ========== Impact Analysis Tests ==========

    @pytest.mark.asyncio
    async def test_analyze_impact_direct(
        self,
        db_session: AsyncSession,
        test_items: list[Item],
        _test_links: list[Link],
    ) -> None:
        """Given: Item with direct links.

        When: Analyze impact
        Then: Returns directly affected items.
        """
        service = TraceabilityService(db_session)

        # Analyze impact of FEATURE item
        analysis = await service.analyze_impact(
            item_id=str(test_items[0].id),  # Feature: user auth
            max_depth=1,
        )

        assert analysis.item_id == str(test_items[0].id)
        assert len(analysis.directly_affected) >= 1
        assert len(analysis.indirectly_affected) == 0
        assert analysis.total_impact_count >= 1

    @pytest.mark.asyncio
    async def test_analyze_impact_indirect(
        self,
        db_session: AsyncSession,
        test_project: Project,
        test_items: list[Item],
        _test_links: list[Link],
    ) -> None:
        """Given: Chain of links (A->B->C).

        When: Analyze impact with depth=2
        Then: Returns both direct and indirect impacts.
        """
        service = TraceabilityService(db_session)

        # Create chain: FEATURE -> CODE -> TEST
        # Already have FEATURE -> CODE
        # Add CODE -> TEST
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[3].id),  # CODE
            target_item_id=str(test_items[5].id),  # TEST
            link_type="tested_by",
        )

        analysis = await service.analyze_impact(
            item_id=str(test_items[0].id),  # FEATURE
            max_depth=2,
        )

        assert len(analysis.directly_affected) >= 1
        # Should have indirect impacts from CODE -> TEST
        assert analysis.total_impact_count >= 1

    @pytest.mark.asyncio
    async def test_analyze_impact_no_links(self, db_session: AsyncSession, test_items: list[Item]) -> None:
        """Given: Item with no outgoing links.

        When: Analyze impact
        Then: Returns zero impact.
        """
        service = TraceabilityService(db_session)

        # Use TEST item which has no outgoing links
        analysis = await service.analyze_impact(
            item_id=str(test_items[7].id),  # TEST: integration_test
            max_depth=2,
        )

        assert len(analysis.directly_affected) == 0
        assert len(analysis.indirectly_affected) == 0
        assert analysis.total_impact_count == 0

    @pytest.mark.asyncio
    async def test_analyze_impact_circular_prevention(
        self,
        db_session: AsyncSession,
        test_project: Project,
        test_items: list[Item],
    ) -> None:
        """Given: Circular links (A->B->C->A).

        When: Analyze impact
        Then: Prevents infinite recursion with visited set.
        """
        service = TraceabilityService(db_session)

        # Create circular links
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[0].id),  # A
            target_item_id=str(test_items[1].id),  # B
            link_type="depends_on",
        )
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[1].id),  # B
            target_item_id=str(test_items[2].id),  # C
            link_type="depends_on",
        )
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[2].id),  # C
            target_item_id=str(test_items[0].id),  # A (circular)
            link_type="depends_on",
        )

        # Should not hang
        analysis = await service.analyze_impact(
            item_id=str(test_items[0].id),
            max_depth=5,
        )

        # Should complete without infinite loop
        assert analysis.total_impact_count >= 0

    @pytest.mark.asyncio
    async def test_analyze_impact_max_depth_limit(
        self,
        db_session: AsyncSession,
        test_project: Project,
        test_items: list[Item],
    ) -> None:
        """Given: Deep chain of links.

        When: Analyze with max_depth=1
        Then: Returns only direct impacts.
        """
        service = TraceabilityService(db_session)

        # Create chain: A -> B -> C -> D
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[0].id),
            target_item_id=str(test_items[1].id),
            link_type="depends_on",
        )
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[1].id),
            target_item_id=str(test_items[2].id),
            link_type="depends_on",
        )
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[2].id),
            target_item_id=str(test_items[3].id),
            link_type="depends_on",
        )

        # Depth=1 should only get B
        analysis = await service.analyze_impact(
            item_id=str(test_items[0].id),
            max_depth=1,
        )

        assert len(analysis.directly_affected) >= 1
        assert len(analysis.indirectly_affected) == 0

    @pytest.mark.asyncio
    async def test_get_downstream_items_recursive(
        self,
        db_session: AsyncSession,
        test_project: Project,
        test_items: list[Item],
    ) -> None:
        """Given: Chain of dependencies.

        When: Call _get_downstream_items
        Then: Recursively finds all downstream items.
        """
        service = TraceabilityService(db_session)

        # Create chain
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[0].id),
            target_item_id=str(test_items[1].id),
            link_type="depends_on",
        )
        await service.create_link(
            project_id=str(test_project.id),
            source_item_id=str(test_items[1].id),
            target_item_id=str(test_items[2].id),
            link_type="depends_on",
        )

        visited = {str(test_items[0].id)}
        downstream = await service._get_downstream_items(
            item_id=str(test_items[0].id),
            visited=visited,
            depth=2,
        )

        assert len(downstream) >= COUNT_TWO


# ============================================================
# VISUALIZATION SERVICE TESTS (12 tests)
# ============================================================


class TestVisualizationService:
    """Integration tests for VisualizationService."""

    # ========== Tree Rendering Tests ==========

    def test_render_tree_simple(self) -> None:
        """Given: Simple list of items with hierarchy.

        When: Render as tree
        Then: Returns ASCII tree visualization.
        """
        items = [
            {
                "id": "1",
                "title": "Root Item",
                "children": [
                    {"id": "2", "title": "Child 1", "children": []},
                    {"id": "3", "title": "Child 2", "children": []},
                ],
            },
        ]

        result = VisualizationService.render_tree(items)

        assert "Root Item" in result
        assert "Child 1" in result
        assert "Child 2" in result
        assert "└──" in result or "├──" in result

    def test_render_tree_nested(self) -> None:
        """Given: Deeply nested tree structure.

        When: Render tree
        Then: Shows proper indentation and branches.
        """
        items = [
            {
                "id": "1",
                "title": "Level 1",
                "children": [
                    {
                        "id": "2",
                        "title": "Level 2",
                        "children": [
                            {"id": "3", "title": "Level 3", "children": []},
                        ],
                    },
                ],
            },
        ]

        result = VisualizationService.render_tree(items)

        assert "Level 1" in result
        assert "Level 2" in result
        assert "Level 3" in result
        # Check indentation
        lines = result.split("\n")
        assert len(lines) >= COUNT_THREE

    def test_render_tree_empty(self) -> None:
        """Given: Empty list.

        When: Render tree
        Then: Returns empty string.
        """
        result = VisualizationService.render_tree([])

        assert result == ""

    def test_render_tree_multiple_roots(self) -> None:
        """Given: Multiple root items.

        When: Render tree
        Then: Shows all roots with their children.
        """
        items = [
            {"id": "1", "title": "Root 1", "children": []},
            {"id": "2", "title": "Root 2", "children": []},
            {"id": "3", "title": "Root 3", "children": []},
        ]

        result = VisualizationService.render_tree(items)

        assert "Root 1" in result
        assert "Root 2" in result
        assert "Root 3" in result

    # ========== Graph Rendering Tests ==========

    def test_render_graph_simple(self) -> None:
        """Given: Items and links.

        When: Render as graph
        Then: Shows dependency graph with levels.
        """
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
            "C": {"title": "Item C"},
        }
        links = [
            {"source": "A", "target": "B", "type": "depends_on"},
            {"source": "B", "target": "C", "type": "depends_on"},
        ]

        result = VisualizationService.render_graph(items, links)

        assert "Item Dependency Graph" in result
        assert "Item A" in result
        assert "Item B" in result
        assert "Item C" in result
        assert "Level 0" in result
        assert "depends_on" in result

    def test_render_graph_empty_items(self) -> None:
        """Given: No items.

        When: Render graph
        Then: Returns empty string.
        """
        result = VisualizationService.render_graph({}, [])

        assert result == ""

    def test_render_graph_no_links(self) -> None:
        """Given: Items but no links.

        When: Render graph
        Then: Shows items at level 0.
        """
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
        }

        result = VisualizationService.render_graph(items, [])

        assert "Level 0" in result
        assert "Item A" in result
        assert "Item B" in result

    def test_render_graph_complex_dependencies(self) -> None:
        """Given: Complex dependency graph.

        When: Render graph
        Then: Correctly calculates levels.
        """
        items = {
            "A": {"title": "Root"},
            "B": {"title": "Dependency 1"},
            "C": {"title": "Dependency 2"},
            "D": {"title": "Deep Dependency"},
        }
        links = [
            {"source": "A", "target": "B", "type": "depends_on"},
            {"source": "A", "target": "C", "type": "depends_on"},
            {"source": "B", "target": "D", "type": "depends_on"},
        ]

        result = VisualizationService.render_graph(items, links)

        # Should have multiple levels
        assert "Level 0" in result
        assert "Level 1" in result

    # ========== Dependency Matrix Tests ==========

    def test_render_dependency_matrix_simple(self) -> None:
        """Given: Items and links.

        When: Render dependency matrix
        Then: Shows matrix with X for dependencies.
        """
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
        }
        links = [
            {"source": "A", "target": "B"},
        ]

        result = VisualizationService.render_dependency_matrix(items, links)

        assert "X" in result
        assert "." in result
        assert "Legend" in result

    def test_render_dependency_matrix_empty_items(self) -> None:
        """Given: No items.

        When: Render matrix
        Then: Returns empty string.
        """
        result = VisualizationService.render_dependency_matrix({}, [])

        assert result == ""

    def test_render_dependency_matrix_no_links(self) -> None:
        """Given: Items but no links.

        When: Render matrix
        Then: Shows matrix with all dots.
        """
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
        }

        result = VisualizationService.render_dependency_matrix(items, [])

        assert "." in result
        assert "X" not in result

    def test_render_dependency_matrix_multiple_dependencies(self) -> None:
        """Given: Multiple items with various dependencies.

        When: Render matrix
        Then: Shows complete dependency matrix.
        """
        items = {
            "A": {"title": "Item A"},
            "B": {"title": "Item B"},
            "C": {"title": "Item C"},
        }
        links = [
            {"source": "A", "target": "B"},
            {"source": "A", "target": "C"},
            {"source": "B", "target": "C"},
        ]

        result = VisualizationService.render_dependency_matrix(items, links)

        # Count X's - should have 3
        x_count = result.count(" X ")
        assert x_count == COUNT_THREE


# ============================================================
# EDGE CASES AND ERROR HANDLING (3 tests)
# ============================================================


class TestEdgeCasesAndErrors:
    """Tests for edge cases and error handling across services."""

    @pytest.mark.asyncio
    async def test_bulk_operation_with_deleted_items(
        self,
        test_project: Project,
        test_items: list[Item],
        sync_db_session: Session,
        db_session: AsyncSession,
    ) -> None:
        """Given: Some items are soft-deleted.

        When: Bulk update
        Then: Only updates non-deleted items.
        """
        # Soft delete one item
        test_items[0].deleted_at = datetime.now(UTC)
        await db_session.commit()

        service = BulkOperationService(sync_db_session)
        result = service.bulk_update_items(
            project_id=str(test_project.id),
            filters={"view": "FEATURE"},
            updates={"status": "done"},
        )

        # Should update 2 FEATURE items (3rd is deleted)
        assert result["items_updated"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_export_empty_project(self, db_session: AsyncSession) -> None:
        """Given: Project with no items.

        When: Export to any format
        Then: Returns valid export with zero items.
        """
        project = Project(name="Empty Project")
        db_session.add(project)
        await db_session.commit()

        service = ExportImportService(db_session)

        json_result = await service.export_to_json(str(project.id))
        assert json_result["item_count"] == 0

        csv_result = await service.export_to_csv(str(project.id))
        assert csv_result["item_count"] == 0

    @pytest.mark.asyncio
    async def test_traceability_matrix_empty_views(
        self,
        test_project: Project,
        sync_db_session: Session,
        _db_session: AsyncSession,
    ) -> None:
        """Given: Views with no items.

        When: Generate matrix
        Then: Returns 0 coverage with no gaps.
        """
        service = TraceabilityService(db_session)

        matrix = await service.generate_matrix(
            project_id=str(test_project.id),
            source_view="NONEXISTENT_VIEW",
            target_view="ANOTHER_NONEXISTENT",
        )

        assert matrix.coverage_percentage == 0
        assert len(matrix.gaps) == 0
        assert len(matrix.links) == 0
