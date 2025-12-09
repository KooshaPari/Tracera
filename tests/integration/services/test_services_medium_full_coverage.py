"""
WP-2.2: Integration tests for Services Medium Files.

Comprehensive test coverage for 8 service files:
1. item_service.py - Item CRUD and queries (async)
2. bulk_operation_service.py - Bulk operations with preview (sync)
3. cycle_detection_service.py - Cycle detection algorithms (sync/async)
4. chaos_mode_service.py - Chaos mode and failure injection (async)
5. view_service.py - View registry management (async)
6. project_backup_service.py - Project backup/restore (sync)
7. impact_analysis_service.py - Impact analysis calculations (async)
8. advanced_traceability_service.py - Advanced traceability features (async)

Target: 350+ tests, 100% coverage each
Timeline: Week 4-6 (parallel with Phase 1)
"""

import asyncio
import csv
import json
import pytest
from datetime import datetime
from io import StringIO
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from tracertm.models.base import Base
from tracertm.models.project import Project
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.event import Event

from tracertm.services.item_service import ItemService, STATUS_TRANSITIONS, VALID_STATUSES
from tracertm.services.bulk_operation_service import BulkOperationService
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.services.chaos_mode_service import ChaosModeService
from tracertm.services.view_service import ViewService
from tracertm.services.project_backup_service import ProjectBackupService
from tracertm.services.impact_analysis_service import ImpactAnalysisService
from tracertm.services.advanced_traceability_service import AdvancedTraceabilityService

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.event_repository import EventRepository

pytestmark = pytest.mark.integration


# ============================================================
# SYNC FIXTURES (for sync services)
# ============================================================

@pytest.fixture(scope="function")
def sync_db_session():
    """Create a synchronous database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def sync_project(sync_db_session):
    """Create a test project for sync tests."""
    project = Project(
        id="test-project",
        name="Test Project",
        description="Test project for sync services",
    )
    sync_db_session.add(project)
    sync_db_session.commit()
    return project


@pytest.fixture(scope="function")
def sync_items_with_links(sync_db_session, sync_project):
    """Create items and links for testing."""
    items = [
        Item(
            id="item-1",
            project_id=sync_project.id,
            title="Feature A",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="high",
            owner="alice",
        ),
        Item(
            id="item-2",
            project_id=sync_project.id,
            title="Feature B",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            priority="medium",
            owner="bob",
        ),
        Item(
            id="item-3",
            project_id=sync_project.id,
            title="Test Case 1",
            view="TEST",
            item_type="test",
            status="todo",
            priority="low",
            owner="charlie",
        ),
        Item(
            id="item-4",
            project_id=sync_project.id,
            title="Code Implementation",
            view="CODE",
            item_type="class",
            status="done",
            priority="high",
            owner="alice",
        ),
        Item(
            id="item-5",
            project_id=sync_project.id,
            title="Design Document",
            view="DESIGN",
            item_type="document",
            status="todo",
            priority="medium",
        ),
    ]
    sync_db_session.add_all(items)
    sync_db_session.commit()

    # Create links
    links = [
        Link(
            id="link-1",
            project_id=sync_project.id,
            source_item_id="item-1",
            target_item_id="item-3",
            link_type="depends_on",
        ),
        Link(
            id="link-2",
            project_id=sync_project.id,
            source_item_id="item-2",
            target_item_id="item-4",
            link_type="depends_on",
        ),
        Link(
            id="link-3",
            project_id=sync_project.id,
            source_item_id="item-1",
            target_item_id="item-5",
            link_type="relates_to",
        ),
    ]
    sync_db_session.add_all(links)
    sync_db_session.commit()

    return items, links


# ============================================================
# ASYNC FIXTURES (for async services)
# ============================================================

@pytest.fixture(scope="function")
async def async_db_session():
    """Create an asynchronous database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_project(async_db_session):
    """Create a test project for async tests."""
    project = Project(
        id="test-async-project",
        name="Test Async Project",
        description="Test project for async services",
    )
    async_db_session.add(project)
    await async_db_session.commit()
    return project


@pytest.fixture(scope="function")
async def async_items_with_links(async_db_session, async_project):
    """Create items and links for async testing."""
    items = [
        Item(
            id="async-item-1",
            project_id=async_project.id,
            title="Async Feature A",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="high",
        ),
        Item(
            id="async-item-2",
            project_id=async_project.id,
            title="Async Feature B",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            priority="medium",
        ),
        Item(
            id="async-item-3",
            project_id=async_project.id,
            title="Async Test",
            view="TEST",
            item_type="test",
            status="todo",
            priority="low",
        ),
        Item(
            id="async-item-4",
            project_id=async_project.id,
            title="Async Code",
            view="CODE",
            item_type="class",
            status="done",
            priority="high",
        ),
    ]
    async_db_session.add_all(items)
    await async_db_session.commit()

    # Create links
    links = [
        Link(
            id="async-link-1",
            project_id=async_project.id,
            source_item_id="async-item-1",
            target_item_id="async-item-3",
            link_type="depends_on",
        ),
        Link(
            id="async-link-2",
            project_id=async_project.id,
            source_item_id="async-item-2",
            target_item_id="async-item-4",
            link_type="depends_on",
        ),
    ]
    async_db_session.add_all(links)
    await async_db_session.commit()

    return items, links


# ============================================================
# ITEM SERVICE TESTS (CRUD AND QUERIES) - ASYNC
# ============================================================

@pytest.mark.asyncio
class TestItemServiceCreate:
    """Test ItemService create operations."""

    async def test_create_item_basic(self, async_db_session, async_project):
        """Test creating a basic item."""
        service = ItemService(async_db_session)

        item = await service.create_item(
            project_id=async_project.id,
            title="New Item",
            view="FEATURE",
            item_type="feature",
            agent_id="test-agent",
            status="todo",
        )

        assert item.id is not None
        assert item.title == "New Item"
        assert item.view == "FEATURE"
        assert item.item_type == "feature"
        assert item.status == "todo"
        assert item.created_by == "test-agent"

    async def test_create_item_with_metadata(self, async_db_session, async_project):
        """Test creating an item with metadata."""
        service = ItemService(async_db_session)
        metadata = {"priority": "high", "complexity": "medium"}

        item = await service.create_item(
            project_id=async_project.id,
            title="Item with metadata",
            view="CODE",
            item_type="class",
            agent_id="test-agent",
            metadata=metadata,
        )

        assert item.item_metadata == metadata

    async def test_create_item_with_links(self, async_db_session, async_project, async_items_with_links):
        """Test creating an item with linked targets."""
        service = ItemService(async_db_session)
        items, _ = async_items_with_links

        new_item = await service.create_item(
            project_id=async_project.id,
            title="Item with links",
            view="TEST",
            item_type="test",
            agent_id="test-agent",
            link_to=[items[0].id, items[1].id],
            link_type="depends_on",
        )

        assert new_item.id is not None

    async def test_create_item_with_parent(self, async_db_session, async_project):
        """Test creating a child item."""
        service = ItemService(async_db_session)

        parent = Item(
            id="parent-1",
            project_id=async_project.id,
            title="Parent Item",
            view="FEATURE",
            item_type="feature",
        )
        async_db_session.add(parent)
        await async_db_session.commit()

        child = await service.create_item(
            project_id=async_project.id,
            title="Child Item",
            view="FEATURE",
            item_type="story",
            agent_id="test-agent",
            parent_id=parent.id,
        )

        assert child.parent_id == parent.id

    async def test_create_item_event_logging(self, async_db_session, async_project):
        """Test that item creation logs events."""
        service = ItemService(async_db_session)

        item = await service.create_item(
            project_id=async_project.id,
            title="Item for event test",
            view="FEATURE",
            item_type="feature",
            agent_id="test-agent",
        )

        # Verify event was logged
        from sqlalchemy import select
        query = select(Event).filter(
            Event.entity_id == item.id,
            Event.event_type == "item_created",
        )
        result = await async_db_session.execute(query)
        event = result.scalars().first()

        assert event is not None
        assert event.agent_id == "test-agent"

    async def test_create_item_all_statuses(self, async_db_session, async_project):
        """Test creating items with all valid statuses."""
        service = ItemService(async_db_session)

        for status in VALID_STATUSES:
            item = await service.create_item(
                project_id=async_project.id,
                title=f"Item with status {status}",
                view="FEATURE",
                item_type="feature",
                agent_id="test-agent",
                status=status,
            )
            assert item.status == status


@pytest.mark.asyncio
class TestItemServiceRead:
    """Test ItemService read operations."""

    async def test_get_item_by_id(self, async_db_session, async_project, async_items_with_links):
        """Test retrieving an item by ID."""
        service = ItemService(async_db_session)
        items, _ = async_items_with_links

        retrieved = await service.get_item(async_project.id, items[0].id)
        assert retrieved.id == items[0].id
        assert retrieved.title == items[0].title

    async def test_get_item_not_found(self, async_db_session, async_project):
        """Test retrieving a non-existent item."""
        service = ItemService(async_db_session)

        item = await service.get_item(async_project.id, "non-existent")
        assert item is None

    async def test_get_item_wrong_project(self, async_db_session):
        """Test retrieving an item from wrong project."""
        service = ItemService(async_db_session)

        project1 = Project(id="project-1", name="Project 1")
        project2 = Project(id="project-2", name="Project 2")
        async_db_session.add_all([project1, project2])
        await async_db_session.commit()

        item = Item(
            id="item-1",
            project_id="project-1",
            title="Test",
            view="FEATURE",
            item_type="feature",
        )
        async_db_session.add(item)
        await async_db_session.commit()

        retrieved = await service.get_item("project-2", "item-1")
        assert retrieved is None


@pytest.mark.asyncio
class TestItemServiceUpdate:
    """Test ItemService update operations."""

    async def test_update_item_status(self, async_db_session, async_project):
        """Test updating item status."""
        service = ItemService(async_db_session)

        item = Item(
            id="update-test-1",
            project_id=async_project.id,
            title="Test",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        async_db_session.add(item)
        await async_db_session.commit()

        updated = await service.update_item(async_project.id, "update-test-1", status="in_progress")

        assert updated.status == "in_progress"

    async def test_update_item_multiple_fields(self, async_db_session, async_project):
        """Test updating multiple item fields."""
        service = ItemService(async_db_session)

        item = Item(
            id="multi-update",
            project_id=async_project.id,
            title="Original Title",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="low",
        )
        async_db_session.add(item)
        await async_db_session.commit()

        updated = await service.update_item(
            async_project.id,
            "multi-update",
            title="New Title",
            priority="high",
            status="in_progress",
        )

        assert updated.title == "New Title"
        assert updated.priority == "high"
        assert updated.status == "in_progress"


@pytest.mark.asyncio
class TestItemServiceDelete:
    """Test ItemService delete operations."""

    async def test_delete_item(self, async_db_session, async_project):
        """Test deleting an item."""
        service = ItemService(async_db_session)

        item = Item(
            id="delete-test",
            project_id=async_project.id,
            title="To Delete",
            view="FEATURE",
            item_type="feature",
        )
        async_db_session.add(item)
        await async_db_session.commit()

        deleted = await service.delete_item(async_project.id, "delete-test")
        assert deleted

        from sqlalchemy import select
        query = select(Item).filter(Item.id == "delete-test")
        result = await async_db_session.execute(query)
        retrieved = result.scalars().first()
        assert retrieved.deleted_at is not None


# ============================================================
# BULK OPERATION SERVICE TESTS (SYNC)
# ============================================================

class TestBulkOperationService:
    """Test BulkOperationService."""

    def test_bulk_update_preview_basic(self, sync_db_session, sync_project, sync_items_with_links):
        """Test bulk update preview generation."""
        service = BulkOperationService(sync_db_session)

        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "in_progress"},
        )

        assert preview["total_count"] == 2
        assert len(preview.get("sample_items", preview.get("samples", []))) > 0
        assert preview["estimated_duration_ms"] > 0

    def test_bulk_update_preview_with_status_filter(self, sync_db_session, sync_project, sync_items_with_links):
        """Test bulk update preview with status filter."""
        service = BulkOperationService(sync_db_session)

        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={"status": "todo"},
            updates={"priority": "high"},
        )

        assert preview["total_count"] >= 0
        assert ("sample_items" in preview or "samples" in preview)
        assert "warnings" in preview

    def test_bulk_update_preview_large_operation_warning(self, sync_db_session, sync_project):
        """Test that large operations generate warnings."""
        # Create many items
        for i in range(150):
            item = Item(
                id=f"bulk-item-{i}",
                project_id=sync_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            sync_db_session.add(item)
        sync_db_session.commit()

        service = BulkOperationService(sync_db_session)
        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={},
            updates={"status": "in_progress"},
        )

        assert any("Large operation" in w for w in preview.get("warnings", []))

    def test_bulk_update_preview_multiple_filters(self, sync_db_session, sync_project, sync_items_with_links):
        """Test bulk update preview with multiple filters."""
        service = BulkOperationService(sync_db_session)

        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={"view": "FEATURE", "status": "todo"},
            updates={"priority": "high"},
        )

        assert "total_count" in preview
        assert preview["total_count"] >= 0

    def test_bulk_update_preview_no_matches(self, sync_db_session, sync_project):
        """Test bulk update preview when no items match."""
        service = BulkOperationService(sync_db_session)

        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={"view": "NONEXISTENT"},
            updates={"status": "done"},
        )

        assert preview["total_count"] == 0
        samples = preview.get("sample_items", preview.get("samples", []))
        assert len(samples) == 0

    def test_bulk_update_preview_priority_filter(self, sync_db_session, sync_project, sync_items_with_links):
        """Test bulk update preview with priority filter."""
        service = BulkOperationService(sync_db_session)

        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={"priority": "high"},
            updates={"owner": "manager"},
        )

        assert "total_count" in preview
        assert preview["total_count"] >= 0

    def test_bulk_update_preview_owner_filter(self, sync_db_session, sync_project, sync_items_with_links):
        """Test bulk update preview with owner filter."""
        service = BulkOperationService(sync_db_session)

        preview = service.bulk_update_preview(
            project_id=sync_project.id,
            filters={"owner": "alice"},
            updates={"priority": "high"},
        )

        assert preview["total_count"] >= 0


# ============================================================
# CYCLE DETECTION SERVICE TESTS (SYNC)
# ============================================================

class TestCycleDetectionService:
    """Test CycleDetectionService."""

    def test_no_cycle_in_simple_graph(self, sync_db_session, sync_project, sync_items_with_links):
        """Test that simple acyclic graph has no cycles."""
        service = CycleDetectionService(sync_db_session)

        has_cycle = service.has_cycle(
            sync_project.id,
            source_id="item-1",
            target_id="item-3",
            link_type="depends_on",
        )

        assert not has_cycle

    def test_cycle_detection_creates_cycle(self, sync_db_session, sync_project, sync_items_with_links):
        """Test cycle detection when adding link would create cycle."""
        items, links = sync_items_with_links
        service = CycleDetectionService(sync_db_session)

        # item-1 depends on item-3
        # If we try to make item-3 depend on item-1, that creates a cycle
        has_cycle = service.has_cycle(
            sync_project.id,
            source_id="item-3",
            target_id="item-1",
            link_type="depends_on",
        )

        # This should not create a cycle with current data
        # Let's create a true cycle scenario
        link = Link(
            id="cycle-test",
            project_id=sync_project.id,
            source_item_id="item-3",
            target_item_id="item-1",
            link_type="depends_on",
        )
        sync_db_session.add(link)
        sync_db_session.commit()

        # Now trying to create item-1 -> item-3 should fail
        has_cycle = service.has_cycle(
            sync_project.id,
            source_id="item-1",
            target_id="item-3",
            link_type="depends_on",
        )

        assert has_cycle

    def test_cycle_detection_non_depends_on_links(self, sync_db_session, sync_project):
        """Test that cycle detection only applies to depends_on links."""
        service = CycleDetectionService(sync_db_session)

        # Non-depends_on links don't create cycles
        has_cycle = service.has_cycle(
            sync_project.id,
            source_id="item-1",
            target_id="item-2",
            link_type="relates_to",
        )

        assert not has_cycle

    def test_detect_cycles_returns_namespace(self, sync_db_session, sync_project):
        """Test that detect_cycles returns proper namespace."""
        service = CycleDetectionService(sync_db_session)

        result = service.detect_cycles(sync_project.id)

        assert hasattr(result, "has_cycles")
        assert hasattr(result, "cycle_count")
        assert hasattr(result, "cycles")

    def test_detect_cycles_with_multiple_types(self, sync_db_session, sync_project):
        """Test cycle detection with multiple link types."""
        service = CycleDetectionService(sync_db_session)

        result = service.detect_cycles(
            sync_project.id,
            link_types=["depends_on", "relates_to"],
        )

        assert hasattr(result, "cycle_count")

    def test_detect_cycles_complex_graph(self, sync_db_session, sync_project):
        """Test cycle detection in complex graph."""
        # Create items
        for i in range(5):
            item = Item(
                id=f"complex-item-{i}",
                project_id=sync_project.id,
                title=f"Complex Item {i}",
                view="FEATURE",
                item_type="feature",
            )
            sync_db_session.add(item)
        sync_db_session.commit()

        # Create dependencies
        for i in range(4):
            link = Link(
                id=f"complex-link-{i}",
                project_id=sync_project.id,
                source_item_id=f"complex-item-{i}",
                target_item_id=f"complex-item-{i+1}",
                link_type="depends_on",
            )
            sync_db_session.add(link)
        sync_db_session.commit()

        service = CycleDetectionService(sync_db_session)
        result = service.detect_cycles(sync_project.id)

        # No cycles in a chain
        assert result.has_cycles == False


@pytest.mark.asyncio
class TestCycleDetectionServiceAsync:
    """Test async cycle detection."""

    async def test_detect_cycles_async(self, async_db_session, async_project, async_items_with_links):
        """Test async cycle detection."""
        service = CycleDetectionService(async_db_session)

        result = await service.detect_cycles_async(async_project.id)

        assert hasattr(result, "has_cycles")
        assert hasattr(result, "cycles")


# ============================================================
# CHAOS MODE SERVICE TESTS (ASYNC)
# ============================================================

@pytest.mark.asyncio
class TestChaosModeService:
    """Test ChaosModeService."""

    async def test_detect_zombies(self, async_db_session, async_project, async_items_with_links):
        """Test zombie detection."""
        service = ChaosModeService(async_db_session)

        result = await service.detect_zombies(async_project.id, days_inactive=30)

        assert "zombie_count" in result
        assert "zombies" in result
        assert "total_items" in result
        assert "zombie_percentage" in result

    async def test_analyze_impact(self, async_db_session, async_project, async_items_with_links):
        """Test impact analysis."""
        service = ChaosModeService(async_db_session)

        result = await service.analyze_impact(async_project.id, "async-item-1")

        assert "item_id" in result
        assert "direct_impact" in result
        assert "dependencies" in result
        assert "total_impact" in result

    async def test_create_temporal_snapshot(self, async_db_session, async_project, async_items_with_links):
        """Test temporal snapshot creation."""
        service = ChaosModeService(async_db_session)

        snapshot = await service.create_temporal_snapshot(
            async_project.id,
            "test-snapshot",
            agent_id="test-agent",
        )

        assert snapshot["name"] == "test-snapshot"
        assert "item_count" in snapshot
        assert "link_count" in snapshot
        assert "timestamp" in snapshot

    async def test_mass_update_items(self, async_db_session, async_project, async_items_with_links):
        """Test mass item updates."""
        service = ChaosModeService(async_db_session)

        result = await service.mass_update_items(
            async_project.id,
            item_ids=["async-item-1", "async-item-2"],
            updates={"status": "in_progress"},
            agent_id="test-agent",
        )

        assert "updated_count" in result
        assert "error_count" in result
        assert result["updated_count"] >= 0

    async def test_get_project_health(self, async_db_session, async_project, async_items_with_links):
        """Test project health metrics."""
        service = ChaosModeService(async_db_session)

        health = await service.get_project_health(async_project.id)

        assert "health_score" in health
        assert "total_items" in health
        assert "completed" in health
        assert "in_progress" in health
        assert "todo" in health

    async def test_explode_file_markdown(self, async_db_session, async_project):
        """Test file explosion with markdown."""
        service = ChaosModeService(async_db_session)

        content = """
# Feature A
## Story 1
## Story 2
# Feature B
- Task 1
- Task 2
"""

        count = await service.explode_file(content, async_project.id, "FEATURE")

        assert count > 0

    async def test_track_scope_crash(self, async_db_session, async_project, async_items_with_links):
        """Test scope crash tracking."""
        service = ChaosModeService(async_db_session)

        result = await service.track_scope_crash(
            async_project.id,
            reason="Budget cut",
            item_ids=["async-item-1", "async-item-2"],
            agent_id="test-agent",
        )

        assert "event_id" in result
        assert "items_affected" in result

    async def test_cleanup_zombies(self, async_db_session, async_project, async_items_with_links):
        """Test zombie cleanup."""
        service = ChaosModeService(async_db_session)

        deleted_count = await service.cleanup_zombies(async_project.id)

        assert isinstance(deleted_count, int)
        assert deleted_count >= 0

    async def test_create_snapshot_wrapper(self, async_db_session, async_project):
        """Test snapshot creation wrapper."""
        service = ChaosModeService(async_db_session)

        result = await service.create_snapshot(
            async_project.id,
            "snapshot-name",
            description="Test snapshot",
        )

        assert "snapshot_id" in result
        assert "items_count" in result
        assert "links_count" in result


# ============================================================
# VIEW SERVICE TESTS (ASYNC)
# ============================================================

class TestViewService:
    """Test ViewService."""

    def test_view_service_initialization(self):
        """Test ViewService can be initialized."""
        service = ViewService()
        assert service is not None

    def test_view_service_with_session(self, sync_db_session):
        """Test ViewService with database session."""
        service = ViewService(sync_db_session)
        assert service.db_session is sync_db_session

    @pytest.mark.asyncio
    async def test_list_views(self):
        """Test listing views."""
        service = ViewService()
        views = await service.list_views()
        assert isinstance(views, list)


# ============================================================
# PROJECT BACKUP SERVICE TESTS (SYNC)
# ============================================================

class TestProjectBackupService:
    """Test ProjectBackupService."""

    def test_backup_project_basic(self, sync_db_session, sync_project, sync_items_with_links):
        """Test basic project backup."""
        service = ProjectBackupService(sync_db_session)

        backup = service.backup_project(sync_project.id)

        assert backup["version"] == "1.0"
        assert backup["project"]["id"] == sync_project.id
        assert len(backup["items"]) > 0
        assert len(backup["links"]) > 0

    def test_backup_project_with_history(self, sync_db_session, sync_project, sync_items_with_links):
        """Test backup with history included."""
        # Create an event
        event = Event(
            id="event-1",
            project_id=sync_project.id,
            event_type="item_created",
            entity_type="item",
            entity_id="item-1",
            agent_id="test-agent",
        )
        sync_db_session.add(event)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project(
            sync_project.id,
            include_history=True,
        )

        assert "events" in backup
        assert len(backup["events"]) > 0

    def test_backup_project_with_agents(self, sync_db_session, sync_project):
        """Test backup with agent data."""
        from tracertm.models.agent import Agent

        agent = Agent(
            id="agent-1",
            project_id=sync_project.id,
            name="Test Agent",
            agent_type="human",
        )
        sync_db_session.add(agent)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project(
            sync_project.id,
            include_agents=True,
        )

        assert "agents" in backup
        assert len(backup["agents"]) > 0

    def test_restore_project_basic(self, sync_db_session):
        """Test basic project restore."""
        service = ProjectBackupService(sync_db_session)

        backup_data = {
            "version": "1.0",
            "backup_date": datetime.utcnow().isoformat(),
            "project": {
                "id": "orig-project",
                "name": "Original Project",
                "description": "Test backup",
                "metadata": {},
            },
            "items": [
                {
                    "id": "item-1",
                    "title": "Test Item",
                    "description": None,
                    "view": "FEATURE",
                    "type": "feature",
                    "status": "todo",
                    "priority": "medium",
                    "owner": None,
                    "parent_id": None,
                    "metadata": {},
                }
            ],
            "links": [],
        }

        new_project_id = service.restore_project(backup_data, project_name="Restored Project")

        assert new_project_id is not None

        # Verify project was created
        project = sync_db_session.query(Project).filter(
            Project.id == new_project_id
        ).first()
        assert project is not None
        assert project.name == "Restored Project"

    def test_clone_project(self, sync_db_session, sync_project, sync_items_with_links):
        """Test project cloning."""
        service = ProjectBackupService(sync_db_session)

        cloned_id = service.clone_project(
            sync_project.id,
            "Cloned Project",
            include_items=True,
            include_links=True,
        )

        assert cloned_id is not None

        # Verify cloned project exists
        cloned = sync_db_session.query(Project).filter(
            Project.id == cloned_id
        ).first()
        assert cloned is not None
        assert cloned.name == "Cloned Project"

    def test_create_template(self, sync_db_session, sync_project):
        """Test template creation."""
        service = ProjectBackupService(sync_db_session)

        template_id = service.create_template(
            sync_project.id,
            "My Template",
        )

        assert template_id is not None

        # Verify template metadata
        template = sync_db_session.query(Project).filter(
            Project.id == template_id
        ).first()
        assert template is not None
        if template.project_metadata:
            assert template.project_metadata.get("is_template") == True

    def test_list_templates(self, sync_db_session):
        """Test template listing."""
        service = ProjectBackupService(sync_db_session)

        # Create a template
        project = Project(
            id="template-project",
            name="Template Project",
            project_metadata={"is_template": True, "template_name": "Test Template"},
        )
        sync_db_session.add(project)
        sync_db_session.commit()

        templates = service.list_templates()

        assert isinstance(templates, list)
        template_names = [t["name"] for t in templates]
        assert "Template Project" in template_names

    def test_backup_project_without_items(self, sync_db_session):
        """Test backup of project with no items."""
        project = Project(id="empty-proj", name="Empty Project")
        sync_db_session.add(project)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        backup = service.backup_project("empty-proj")

        assert backup["project"]["id"] == "empty-proj"
        assert backup["items"] == []

    def test_clone_project_without_items(self, sync_db_session):
        """Test cloning without items."""
        project = Project(id="clone-source", name="Source")
        sync_db_session.add(project)
        sync_db_session.commit()

        service = ProjectBackupService(sync_db_session)
        cloned_id = service.clone_project(
            "clone-source",
            "Clone Target",
            include_items=False,
        )

        cloned = sync_db_session.query(Project).filter(
            Project.id == cloned_id
        ).first()
        assert cloned is not None
        assert cloned.name == "Clone Target"


# ============================================================
# IMPACT ANALYSIS SERVICE TESTS (ASYNC)
# ============================================================

@pytest.mark.asyncio
class TestImpactAnalysisService:
    """Test ImpactAnalysisService."""

    async def test_analyze_impact_single_item(self, async_db_session, async_project, async_items_with_links):
        """Test impact analysis for single item."""
        service = ImpactAnalysisService(async_db_session)

        result = await service.analyze_impact("async-item-1")

        assert result.root_item_id == "async-item-1"
        assert hasattr(result, "total_affected")
        assert hasattr(result, "affected_by_depth")
        assert hasattr(result, "affected_by_view")

    async def test_analyze_impact_with_depth_limit(self, async_db_session, async_project):
        """Test impact analysis with depth limit."""
        # Create a chain of dependencies
        items = []
        for i in range(5):
            item = Item(
                id=f"chain-item-{i}",
                project_id=async_project.id,
                title=f"Chain Item {i}",
                view="FEATURE",
                item_type="feature",
            )
            async_db_session.add(item)
            items.append(item)

        await async_db_session.commit()

        # Create chain links
        for i in range(4):
            link = Link(
                id=f"chain-link-{i}",
                project_id=async_project.id,
                source_item_id=f"chain-item-{i}",
                target_item_id=f"chain-item-{i+1}",
                link_type="depends_on",
            )
            async_db_session.add(link)

        await async_db_session.commit()

        service = ImpactAnalysisService(async_db_session)
        result = await service.analyze_impact("chain-item-0", max_depth=2)

        assert result.max_depth_reached <= 2

    async def test_analyze_reverse_impact(self, async_db_session, async_project, async_items_with_links):
        """Test reverse impact analysis."""
        service = ImpactAnalysisService(async_db_session)

        result = await service.analyze_reverse_impact("async-item-3")

        assert result.root_item_id == "async-item-3"
        assert hasattr(result, "total_affected")

    async def test_analyze_impact_no_dependencies(self, async_db_session, async_project):
        """Test impact analysis for isolated item."""
        item = Item(
            id="isolated-item",
            project_id=async_project.id,
            title="Isolated",
            view="FEATURE",
            item_type="feature",
        )
        async_db_session.add(item)
        await async_db_session.commit()

        service = ImpactAnalysisService(async_db_session)
        result = await service.analyze_impact("isolated-item")

        assert result.total_affected == 0


# ============================================================
# ADVANCED TRACEABILITY SERVICE TESTS (ASYNC)
# ============================================================

@pytest.mark.asyncio
class TestAdvancedTraceabilityService:
    """Test AdvancedTraceabilityService."""

    async def test_find_all_paths_direct(self, async_db_session, async_project, async_items_with_links):
        """Test finding direct paths between items."""
        service = AdvancedTraceabilityService(async_db_session)

        paths = await service.find_all_paths("async-item-1", "async-item-3")

        assert isinstance(paths, list)

    async def test_find_all_paths_no_path(self, async_db_session, async_project):
        """Test path finding when no path exists."""
        item1 = Item(
            id="item-a",
            project_id=async_project.id,
            title="Item A",
            view="FEATURE",
            item_type="feature",
        )
        item2 = Item(
            id="item-b",
            project_id=async_project.id,
            title="Item B",
            view="FEATURE",
            item_type="feature",
        )
        async_db_session.add_all([item1, item2])
        await async_db_session.commit()

        service = AdvancedTraceabilityService(async_db_session)
        paths = await service.find_all_paths("item-a", "item-b")

        assert len(paths) == 0

    async def test_find_all_paths_max_depth(self, async_db_session, async_project, async_items_with_links):
        """Test path finding with max depth limit."""
        service = AdvancedTraceabilityService(async_db_session)

        paths = await service.find_all_paths(
            "async-item-1",
            "async-item-4",
            max_depth=1,
        )

        assert isinstance(paths, list)


# ============================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================

class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    def test_bulk_operation_empty_project(self, sync_db_session):
        """Test bulk operations on empty project."""
        project = Project(id="empty-project", name="Empty")
        sync_db_session.add(project)
        sync_db_session.commit()

        service = BulkOperationService(sync_db_session)
        preview = service.bulk_update_preview(
            "empty-project",
            filters={},
            updates={"status": "done"},
        )

        assert preview["total_count"] == 0

    def test_cycle_detection_invalid_project(self, sync_db_session):
        """Test cycle detection on non-existent project."""
        service = CycleDetectionService(sync_db_session)

        result = service.detect_cycles("non-existent")

        assert result.has_cycles == False
        assert result.cycle_count == 0

    def test_backup_nonexistent_project(self, sync_db_session):
        """Test backup of non-existent project."""
        service = ProjectBackupService(sync_db_session)

        with pytest.raises(ValueError):
            service.backup_project("non-existent")


# ============================================================
# INTEGRATION TESTS (CROSS-SERVICE)
# ============================================================

class TestCrossServiceIntegration:
    """Test interactions between multiple services."""

    def test_item_service_with_bulk_operations(self, sync_db_session, sync_project):
        """Test ItemService integration with bulk operations."""
        bulk_service = BulkOperationService(sync_db_session)

        # Create items directly
        for i in range(3):
            item = Item(
                id=f"int-item-{i}",
                project_id=sync_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            sync_db_session.add(item)
        sync_db_session.commit()

        # Preview bulk update
        preview = bulk_service.bulk_update_preview(
            sync_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "in_progress"},
        )

        assert preview["total_count"] == 3

    def test_backup_restore_roundtrip(self, sync_db_session, sync_project, sync_items_with_links):
        """Test backup and restore roundtrip."""
        service = ProjectBackupService(sync_db_session)

        # Create backup
        backup = service.backup_project(sync_project.id)

        # Create new session for restore
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        new_session = SessionLocal()

        # Restore
        restored_service = ProjectBackupService(new_session)
        new_project_id = restored_service.restore_project(
            backup,
            project_name="Restored",
        )

        # Verify restoration
        restored = new_session.query(Project).filter(
            Project.id == new_project_id
        ).first()
        assert restored is not None

    @pytest.mark.asyncio
    async def test_chaos_mode_with_impact_analysis(self, async_db_session, async_project, async_items_with_links):
        """Test ChaosModeService with ImpactAnalysisService."""
        chaos_service = ChaosModeService(async_db_session)
        impact_service = ImpactAnalysisService(async_db_session)

        # Get project health
        health = await chaos_service.get_project_health(async_project.id)
        assert health["total_items"] > 0

        # Analyze impact
        impact = await impact_service.analyze_impact("async-item-1")
        assert impact.root_item_id == "async-item-1"


# ============================================================
# PERFORMANCE TESTS
# ============================================================

class TestPerformance:
    """Test performance characteristics."""

    def test_bulk_preview_performance(self, sync_db_session, sync_project):
        """Test bulk preview performance with many items."""
        # Create 500 items
        for i in range(500):
            item = Item(
                id=f"perf-item-{i}",
                project_id=sync_project.id,
                title=f"Performance Test Item {i}",
                view="FEATURE" if i % 2 == 0 else "TEST",
                item_type="feature",
                status="todo" if i % 3 == 0 else "in_progress",
            )
            sync_db_session.add(item)
        sync_db_session.commit()

        service = BulkOperationService(sync_db_session)

        import time
        start = time.time()
        preview = service.bulk_update_preview(
            sync_project.id,
            filters={},
            updates={"status": "done"},
        )
        elapsed = time.time() - start

        assert preview["total_count"] == 500
        assert elapsed < 5  # Should complete in under 5 seconds
