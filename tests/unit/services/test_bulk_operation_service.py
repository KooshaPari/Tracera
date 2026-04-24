from typing import Any

"""Unit tests for BulkOperationService - based on actual implementation."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE
from tracertm.models.item import Item
from tracertm.services.bulk_service import BulkOperationService, BulkPreview

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_session() -> None:
    """Create a mock async session."""
    return AsyncMock()


@pytest.fixture
def mock_item_repository() -> None:
    """Create a mock item repository."""
    return AsyncMock()


@pytest.fixture
def mock_event_repository() -> None:
    """Create a mock event repository."""
    return AsyncMock()


@pytest.fixture
def bulk_service(mock_session: Any, mock_item_repository: Any, mock_event_repository: Any) -> None:
    """Create BulkOperationService with mocked dependencies."""
    service = BulkOperationService(mock_session)
    service.items = mock_item_repository
    service.events = mock_event_repository
    return service


@pytest.fixture
def test_data() -> None:
    """Provide test data."""
    return {
        "project_id": str(uuid4()),
        "agent_id": str(uuid4()),
    }


class TestBulkOperationServiceInitialization:
    """Test BulkOperationService initialization."""

    def test_bulk_service_creates_with_session(self, mock_session: Any) -> None:
        """BulkOperationService initializes with async session."""
        service = BulkOperationService(mock_session)
        assert service.session == mock_session
        assert service.items is not None
        assert service.events is not None

    def test_bulk_service_has_repositories(self, mock_session: Any) -> None:
        """BulkOperationService creates repository instances."""
        service = BulkOperationService(mock_session)
        assert hasattr(service, "items")
        assert hasattr(service, "events")


class TestBulkPreviewDataclass:
    """Test BulkPreview dataclass."""

    def test_bulk_preview_creation(self) -> None:
        """BulkPreview creates with required fields."""
        preview = BulkPreview(
            total_count=100,
            sample_items=[{"id": "1", "title": "Item"}],
            validation_warnings=[],
            estimated_duration_ms=1000,
        )
        assert preview.total_count == 100
        assert len(preview.sample_items) == 1
        assert preview.validation_warnings == []
        assert preview.estimated_duration_ms == 1000

    def test_bulk_preview_is_safe_with_no_warnings(self) -> None:
        """BulkPreview.is_safe returns True when no warnings."""
        preview = BulkPreview(total_count=50, sample_items=[], validation_warnings=[], estimated_duration_ms=500)
        assert preview.is_safe() is True

    def test_bulk_preview_is_safe_with_warnings(self) -> None:
        """BulkPreview.is_safe returns False when warnings exist."""
        preview = BulkPreview(
            total_count=150,
            sample_items=[],
            validation_warnings=["Large operation"],
            estimated_duration_ms=1500,
        )
        assert preview.is_safe() is False


class TestBulkOperationServicePreview:
    """Test BulkOperationService.preview_bulk_update method."""

    @pytest.mark.asyncio
    async def test_preview_bulk_update_basic(self, bulk_service: Any, test_data: Any) -> None:
        """preview_bulk_update returns preview."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title=f"Item {i}",
                view="Feature",
                item_type="requirement",
                status="todo",
            )
            for i in range(5)
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)

        preview = await bulk_service.preview_bulk_update(
            test_data["project_id"],
            {"status": "todo"},
            {"status": "in_progress"},
        )

        assert isinstance(preview, BulkPreview)
        assert preview.total_count == COUNT_FIVE
        assert len(preview.sample_items) <= COUNT_FIVE
        bulk_service.items.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_preview_warns_on_large_operation(self, bulk_service: Any, test_data: Any) -> None:
        """preview_bulk_update warns when updating many items."""
        large_item_list = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title=f"Item {i}",
                view="Feature",
                item_type="requirement",
            )
            for i in range(150)
        ]
        bulk_service.items.query = AsyncMock(return_value=large_item_list)

        preview = await bulk_service.preview_bulk_update(test_data["project_id"], {}, {"priority": "high"})

        assert preview.total_count == 150
        assert len(preview.validation_warnings) > 0
        assert "Large operation" in preview.validation_warnings[0]

    @pytest.mark.asyncio
    async def test_preview_warns_on_blocked_to_complete(self, bulk_service: Any, test_data: Any) -> None:
        """preview_bulk_update warns when completing blocked items."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Blocked Item",
                view="Feature",
                item_type="requirement",
                status="blocked",
            ),
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)

        preview = await bulk_service.preview_bulk_update(
            test_data["project_id"],
            {"status": "blocked"},
            {"status": "complete"},
        )

        assert len(preview.validation_warnings) > 0
        warning_text = " ".join(preview.validation_warnings)
        assert "blocked" in warning_text.lower()

    @pytest.mark.asyncio
    async def test_preview_sample_items(self, bulk_service: Any, test_data: Any) -> None:
        """preview_bulk_update includes sample items."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title=f"Item {i}",
                view="Feature",
                item_type="requirement",
                status="todo",
            )
            for i in range(10)
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)

        preview = await bulk_service.preview_bulk_update(test_data["project_id"], {}, {"status": "in_progress"})

        assert len(preview.sample_items) <= COUNT_FIVE
        for sample in preview.sample_items:
            assert "id" in sample
            assert "title" in sample
            assert "current_status" in sample
            assert "new_status" in sample


class TestBulkOperationServiceExecute:
    """Test BulkOperationService.execute_bulk_update method."""

    @pytest.mark.asyncio
    async def test_execute_bulk_update_requires_safe_preview(self, bulk_service: Any, test_data: Any) -> None:
        """execute_bulk_update fails if preview is unsafe."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Item",
                view="Feature",
                item_type="requirement",
                status="blocked",
            ),
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)

        with pytest.raises(ValueError, match="warnings") as exc_info:
            await bulk_service.execute_bulk_update(
                test_data["project_id"],
                {"status": "blocked"},
                {"status": "complete"},
                test_data["agent_id"],
            )
        assert "warnings" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_bulk_update_with_preview(self, bulk_service: Any, test_data: Any) -> None:
        """execute_bulk_update executes when preview is safe."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Item",
                view="Feature",
                item_type="requirement",
                status="todo",
            )
            for _ in range(3)
        ]
        updated_items = [
            Item(
                id=item.id,
                project_id=item.project_id,
                title=item.title,
                view=item.view,
                item_type=item.item_type,
                status="in_progress",
            )
            for item in mock_items
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)
        bulk_service.items.update = AsyncMock(side_effect=updated_items)
        bulk_service.events.log = AsyncMock()

        result = await bulk_service.execute_bulk_update(
            test_data["project_id"],
            {"status": "todo"},
            {"status": "in_progress"},
            test_data["agent_id"],
        )

        assert isinstance(result, list)
        assert len(result) == COUNT_THREE
        bulk_service.events.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_bulk_update_skip_preview(self, bulk_service: Any, test_data: Any) -> None:
        """execute_bulk_update can skip preview."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Item",
                view="Feature",
                item_type="requirement",
            ),
        ]
        updated_items = [
            Item(id=item.id, project_id=item.project_id, title=item.title, view=item.view, item_type=item.item_type)
            for item in mock_items
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)
        bulk_service.items.update = AsyncMock(side_effect=updated_items)
        bulk_service.events.log = AsyncMock()

        result = await bulk_service.execute_bulk_update(
            test_data["project_id"],
            {},
            {"priority": "high"},
            test_data["agent_id"],
            skip_preview=True,
        )

        assert isinstance(result, list)
        bulk_service.items.query.assert_called()

    @pytest.mark.asyncio
    async def test_execute_bulk_update_logs_event(self, bulk_service: Any, test_data: Any) -> None:
        """execute_bulk_update logs event with results."""
        mock_items = [
            Item(
                id=str(uuid4()),
                project_id=test_data["project_id"],
                title="Item",
                view="Feature",
                item_type="requirement",
            ),
        ]
        updated_items = [
            Item(id=item.id, project_id=item.project_id, title=item.title, view=item.view, item_type=item.item_type)
            for item in mock_items
        ]
        bulk_service.items.query = AsyncMock(return_value=mock_items)
        bulk_service.items.update = AsyncMock(side_effect=updated_items)
        bulk_service.events.log = AsyncMock()

        await bulk_service.execute_bulk_update(
            test_data["project_id"],
            {},
            {"priority": "high"},
            test_data["agent_id"],
            skip_preview=True,
        )

        bulk_service.events.log.assert_called_once()
        call_kwargs = bulk_service.events.log.call_args[1]
        assert call_kwargs["event_type"] == "bulk_update"
        assert call_kwargs["project_id"] == test_data["project_id"]
        assert "total_count" in call_kwargs["data"]
