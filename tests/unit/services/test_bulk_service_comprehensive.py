"""
Comprehensive tests for BulkOperationService.

Tests all methods: preview_bulk_update, execute_bulk_update, BulkPreview.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import asdict

from tracertm.services.bulk_service import BulkOperationService, BulkPreview
from tracertm.core.concurrency import ConcurrencyError


class TestBulkPreview:
    """Test BulkPreview dataclass."""

    def test_is_safe_with_no_warnings(self):
        """Test is_safe returns True when no warnings."""
        preview = BulkPreview(
            total_count=10,
            sample_items=[],
            validation_warnings=[],
            estimated_duration_ms=100,
        )
        assert preview.is_safe() is True

    def test_is_safe_with_warnings(self):
        """Test is_safe returns False when warnings exist."""
        preview = BulkPreview(
            total_count=200,
            sample_items=[],
            validation_warnings=["Large operation: 200 items will be updated"],
            estimated_duration_ms=2000,
        )
        assert preview.is_safe() is False

    def test_dataclass_fields(self):
        """Test BulkPreview has correct fields."""
        preview = BulkPreview(
            total_count=5,
            sample_items=[{"id": "1"}],
            validation_warnings=["warning"],
            estimated_duration_ms=50,
        )
        assert preview.total_count == 5
        assert preview.sample_items == [{"id": "1"}]
        assert preview.validation_warnings == ["warning"]
        assert preview.estimated_duration_ms == 50


class TestPreviewBulkUpdate:
    """Test preview_bulk_update method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = BulkOperationService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_preview_no_items(self, service):
        """Test preview with no matching items."""
        service.items.query = AsyncMock(return_value=[])

        result = await service.preview_bulk_update(
            project_id="proj-1",
            filters={"status": "todo"},
            updates={"status": "in_progress"},
        )

        assert result.total_count == 0
        assert result.sample_items == []
        assert result.validation_warnings == []
        assert result.estimated_duration_ms == 0

    @pytest.mark.asyncio
    async def test_preview_small_operation(self, service):
        """Test preview with small number of items."""
        item = Mock()
        item.id = "item-1"
        item.title = "Test Item"
        item.status = "todo"

        service.items.query = AsyncMock(return_value=[item])

        result = await service.preview_bulk_update(
            project_id="proj-1",
            filters={"status": "todo"},
            updates={"status": "in_progress"},
        )

        assert result.total_count == 1
        assert len(result.sample_items) == 1
        assert result.sample_items[0]["id"] == "item-1"
        assert result.sample_items[0]["current_status"] == "todo"
        assert result.sample_items[0]["new_status"] == "in_progress"
        assert result.validation_warnings == []

    @pytest.mark.asyncio
    async def test_preview_large_operation_warning(self, service):
        """Test preview generates warning for large operation."""
        items = []
        for i in range(150):
            item = Mock()
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.status = "todo"
            items.append(item)

        service.items.query = AsyncMock(return_value=items)

        result = await service.preview_bulk_update(
            project_id="proj-1",
            filters={},
            updates={"status": "done"},
        )

        assert result.total_count == 150
        assert len(result.sample_items) == 5  # Only first 5
        assert len(result.validation_warnings) == 1
        assert "150 items" in result.validation_warnings[0]

    @pytest.mark.asyncio
    async def test_preview_blocked_to_complete_warning(self, service):
        """Test preview warns about completing blocked items."""
        blocked_item = Mock()
        blocked_item.id = "item-1"
        blocked_item.title = "Blocked"
        blocked_item.status = "blocked"

        normal_item = Mock()
        normal_item.id = "item-2"
        normal_item.title = "Normal"
        normal_item.status = "in_progress"

        service.items.query = AsyncMock(return_value=[blocked_item, normal_item])

        result = await service.preview_bulk_update(
            project_id="proj-1",
            filters={},
            updates={"status": "complete"},
        )

        assert any("blocked items" in w for w in result.validation_warnings)

    @pytest.mark.asyncio
    async def test_preview_estimated_duration(self, service):
        """Test estimated duration calculation."""
        items = [Mock(id=f"item-{i}", title=f"Item {i}", status="todo") for i in range(25)]

        service.items.query = AsyncMock(return_value=items)

        result = await service.preview_bulk_update(
            project_id="proj-1",
            filters={},
            updates={"status": "done"},
        )

        # 10ms per item
        assert result.estimated_duration_ms == 250

    @pytest.mark.asyncio
    async def test_preview_sample_shows_updates(self, service):
        """Test sample items show new status from updates."""
        item = Mock()
        item.id = "item-1"
        item.title = "Test"
        item.status = "todo"

        service.items.query = AsyncMock(return_value=[item])

        result = await service.preview_bulk_update(
            project_id="proj-1",
            filters={},
            updates={"status": "done", "priority": "high"},
        )

        assert result.sample_items[0]["new_status"] == "done"


class TestExecuteBulkUpdate:
    """Test execute_bulk_update method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = BulkOperationService(session)
        service.items = AsyncMock()
        service.events = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_execute_success(self, service):
        """Test successful bulk update execution."""
        item = Mock()
        item.id = "item-1"
        item.title = "Test"
        item.status = "todo"
        item.version = 1

        updated_item = Mock()
        updated_item.id = "item-1"
        updated_item.status = "done"

        service.items.query = AsyncMock(return_value=[item])
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        result = await service.execute_bulk_update(
            project_id="proj-1",
            filters={"status": "todo"},
            updates={"status": "done"},
            agent_id="agent-1",
            skip_preview=True,
        )

        assert len(result) == 1
        assert result[0].status == "done"
        service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_preview_safe(self, service):
        """Test execute with preview when safe."""
        item = Mock()
        item.id = "item-1"
        item.title = "Test"
        item.status = "todo"
        item.version = 1

        updated_item = Mock()

        service.items.query = AsyncMock(return_value=[item])
        service.items.update = AsyncMock(return_value=updated_item)
        service.events.log = AsyncMock()

        result = await service.execute_bulk_update(
            project_id="proj-1",
            filters={},
            updates={"status": "in_progress"},
            agent_id="agent-1",
            skip_preview=False,
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_execute_with_preview_unsafe(self, service):
        """Test execute fails when preview has warnings."""
        items = [Mock(id=f"item-{i}", title=f"Item {i}", status="todo") for i in range(150)]

        service.items.query = AsyncMock(return_value=items)

        with pytest.raises(ValueError, match="warnings"):
            await service.execute_bulk_update(
                project_id="proj-1",
                filters={},
                updates={"status": "done"},
                agent_id="agent-1",
                skip_preview=False,
            )

    @pytest.mark.asyncio
    async def test_execute_handles_conflicts(self, service):
        """Test execute handles concurrency conflicts."""
        item1 = Mock()
        item1.id = "item-1"
        item1.title = "Item 1"
        item1.status = "todo"
        item1.version = 1

        item2 = Mock()
        item2.id = "item-2"
        item2.title = "Item 2"
        item2.status = "todo"
        item2.version = 1

        updated_item = Mock()

        service.items.query = AsyncMock(return_value=[item1, item2])
        service.items.update = AsyncMock(side_effect=[
            updated_item,
            ConcurrencyError("Version mismatch"),
        ])
        service.events.log = AsyncMock()

        result = await service.execute_bulk_update(
            project_id="proj-1",
            filters={},
            updates={"status": "done"},
            agent_id="agent-1",
            skip_preview=True,
        )

        # Only one succeeded
        assert len(result) == 1

        # Event log should include conflict count
        call_args = service.events.log.call_args
        assert call_args.kwargs["data"]["conflict_count"] == 1

    @pytest.mark.asyncio
    async def test_execute_logs_event(self, service):
        """Test execute logs bulk operation event."""
        item = Mock()
        item.id = "item-1"
        item.version = 1

        service.items.query = AsyncMock(return_value=[item])
        service.items.update = AsyncMock(return_value=Mock())
        service.events.log = AsyncMock()

        await service.execute_bulk_update(
            project_id="proj-1",
            filters={"view": "REQ"},
            updates={"status": "done"},
            agent_id="agent-1",
            skip_preview=True,
        )

        service.events.log.assert_called_once()
        call_kwargs = service.events.log.call_args.kwargs
        assert call_kwargs["event_type"] == "bulk_update"
        assert call_kwargs["agent_id"] == "agent-1"
        assert call_kwargs["data"]["filters"] == {"view": "REQ"}


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_repositories(self):
        """Test initialization creates repositories."""
        session = AsyncMock()
        service = BulkOperationService(session)

        assert service.session == session
        assert service.items is not None
        assert service.events is not None
