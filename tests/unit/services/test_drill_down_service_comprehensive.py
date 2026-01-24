"""
Comprehensive tests for DrillDownService.

Tests all public methods with various scenarios:
- Service initialization with and without db_session
- drill() method with empty, single, and nested items
- Error handling and edge cases
- Database interactions and drill-down depth handling

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

from tracertm.services.drill_down_service import DrillDownService


class TestDrillDownServiceInitialization:
    """Test service initialization."""

    def test_initialization_with_db_session(self):
        """Test service initializes with db_session."""
        mock_session = Mock()
        service = DrillDownService(mock_session)
        assert service is not None
        assert service.db_session == mock_session

    def test_initialization_without_db_session(self):
        """Test service initializes without db_session."""
        service = DrillDownService()
        assert service is not None
        assert service.db_session is None

    def test_initialization_with_none_session(self):
        """Test service handles explicit None db_session."""
        service = DrillDownService(None)
        assert service is not None
        assert service.db_session is None


class TestDrillDownServiceDrillMethod:
    """Test drill() method - core functionality."""

    @pytest.fixture
    def service_with_mock_session(self):
        """Create service with mocked db_session."""
        mock_session = AsyncMock()
        service = DrillDownService(mock_session)
        return service

    @pytest.mark.asyncio
    async def test_drill_returns_dict(self, service_with_mock_session):
        """Test drill returns a dictionary."""
        result = await service_with_mock_session.drill()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_has_status_key(self, service_with_mock_session):
        """Test drill result contains status key."""
        result = await service_with_mock_session.drill()
        assert "status" in result
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_drill_has_items_key(self, service_with_mock_session):
        """Test drill result contains items key."""
        result = await service_with_mock_session.drill()
        assert "items" in result
        assert isinstance(result["items"], list)

    @pytest.mark.asyncio
    async def test_drill_empty_items(self, service_with_mock_session):
        """Test drill with no items."""
        result = await service_with_mock_session.drill()
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_drill_with_item_id_arg(self, service_with_mock_session):
        """Test drill with item_id argument."""
        result = await service_with_mock_session.drill("item-1")
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_drill_with_depth_kwarg(self, service_with_mock_session):
        """Test drill with depth kwarg."""
        result = await service_with_mock_session.drill(depth=2)
        assert isinstance(result, dict)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_drill_with_multiple_kwargs(self, service_with_mock_session):
        """Test drill with multiple kwargs."""
        result = await service_with_mock_session.drill(
            item_id="item-1",
            depth=3,
            include_metadata=True,
            max_items=50
        )
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_drill_with_args_and_kwargs(self, service_with_mock_session):
        """Test drill with both args and kwargs."""
        result = await service_with_mock_session.drill(
            "item-1",
            "item-2",
            depth=2,
            filter="active"
        )
        assert isinstance(result, dict)


class TestDrillDownServiceWithoutSession:
    """Test service behavior without db_session."""

    @pytest.fixture
    def service_no_session(self):
        """Create service without db_session."""
        return DrillDownService()

    @pytest.mark.asyncio
    async def test_drill_without_session(self, service_no_session):
        """Test drill works without db_session."""
        result = await service_no_session.drill()
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_drill_multiple_calls_without_session(self, service_no_session):
        """Test multiple drill calls without db_session."""
        result1 = await service_no_session.drill()
        result2 = await service_no_session.drill()
        assert result1 == result2
        assert result1["status"] == "ok"


class TestDrillDownServiceErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_drill_with_none_arg(self):
        """Test drill with None argument."""
        service = DrillDownService()
        result = await service.drill(None)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_empty_string(self):
        """Test drill with empty string."""
        service = DrillDownService()
        result = await service.drill("")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_invalid_item_id(self):
        """Test drill with invalid item ID format."""
        service = DrillDownService()
        result = await service.drill("invalid@#$%id")
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_drill_with_negative_depth(self):
        """Test drill with negative depth."""
        service = DrillDownService()
        result = await service.drill(depth=-1)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_zero_depth(self):
        """Test drill with zero depth."""
        service = DrillDownService()
        result = await service.drill(depth=0)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_very_large_depth(self):
        """Test drill with very large depth value."""
        service = DrillDownService()
        result = await service.drill(depth=1000)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_many_kwargs(self):
        """Test drill with many kwargs."""
        service = DrillDownService()
        kwargs = {f"param_{i}": f"value_{i}" for i in range(50)}
        result = await service.drill(**kwargs)
        assert isinstance(result, dict)


class TestDrillDownServiceIntegration:
    """Integration tests with mocked repositories."""

    @pytest.fixture
    def service_with_repos(self):
        """Service with mocked repositories."""
        mock_session = AsyncMock()
        service = DrillDownService(mock_session)
        service.items_repo = AsyncMock()
        service.links_repo = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_drill_with_mocked_item_repo(self, service_with_repos):
        """Test drill with mocked item repository."""
        service_with_repos.items_repo.get_by_id = AsyncMock(
            return_value={"id": "item-1", "title": "Test Item"}
        )
        result = await service_with_repos.drill("item-1")
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_drill_with_mocked_link_repo(self, service_with_repos):
        """Test drill with mocked link repository."""
        service_with_repos.links_repo.get_by_source = AsyncMock(
            return_value=[
                {"id": "link-1", "target_id": "item-2"},
                {"id": "link-2", "target_id": "item-3"}
            ]
        )
        result = await service_with_repos.drill("item-1", depth=2)
        assert isinstance(result, dict)
        assert isinstance(result.get("items"), list)


class TestDrillDownServiceConcurrency:
    """Test concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_drill_calls(self):
        """Test multiple concurrent drill calls."""
        service = DrillDownService()
        tasks = [service.drill() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)
        assert all(r["status"] == "ok" for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_with_different_items(self):
        """Test concurrent drill calls with different item IDs."""
        service = DrillDownService()
        tasks = [
            service.drill(f"item-{i}", depth=i)
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        assert len(results) == 5
        assert all(r["status"] == "ok" for r in results)


class TestDrillDownServiceReturnValues:
    """Test return value structure and content."""

    @pytest.mark.asyncio
    async def test_drill_return_structure(self):
        """Test drill returns properly structured result."""
        service = DrillDownService()
        result = await service.drill()
        assert isinstance(result, dict)
        assert len(result) == 2  # status and items
        assert set(result.keys()) == {"status", "items"}

    @pytest.mark.asyncio
    async def test_drill_items_list_type(self):
        """Test items is always a list."""
        service = DrillDownService()
        result = await service.drill()
        assert isinstance(result["items"], list)

    @pytest.mark.asyncio
    async def test_drill_status_value(self):
        """Test status is always 'ok'."""
        service = DrillDownService()
        result = await service.drill()
        assert result["status"] == "ok"
        assert isinstance(result["status"], str)


class TestDrillDownServiceStateManagement:
    """Test state management and side effects."""

    @pytest.mark.asyncio
    async def test_service_state_not_modified(self):
        """Test service state is not modified by drill."""
        service = DrillDownService()
        initial_db = service.db_session
        await service.drill()
        assert service.db_session == initial_db

    @pytest.mark.asyncio
    async def test_multiple_instances_independent(self):
        """Test multiple service instances are independent."""
        service1 = DrillDownService()
        service2 = DrillDownService()
        result1 = await service1.drill()
        result2 = await service2.drill()
        assert result1 == result2  # Same content
        assert service1 is not service2  # Different objects


class TestDrillDownServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_drill_with_special_characters(self):
        """Test drill with special characters."""
        service = DrillDownService()
        result = await service.drill(
            "item!@#$%^&*()",
            filter="<script>alert('xss')</script>"
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_unicode(self):
        """Test drill with unicode characters."""
        service = DrillDownService()
        result = await service.drill(
            "🚀 item",
            description="测试项目"
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_very_long_item_id(self):
        """Test drill with very long item ID."""
        service = DrillDownService()
        long_id = "x" * 1000
        result = await service.drill(long_id)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_numeric_values(self):
        """Test drill with numeric values as string."""
        service = DrillDownService()
        result = await service.drill("12345", depth=999)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_consistency(self):
        """Test drill returns consistent results."""
        service = DrillDownService()
        results = [await service.drill("item-1") for _ in range(5)]
        # All results should be identical
        assert all(r == results[0] for r in results)


class TestDrillDownServiceDeepNesting:
    """Test deep drilling scenarios."""

    @pytest.mark.asyncio
    async def test_drill_single_level(self):
        """Test drill with single depth level."""
        service = DrillDownService()
        result = await service.drill("item-1", depth=1)
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_drill_moderate_depth(self):
        """Test drill with moderate depth."""
        service = DrillDownService()
        result = await service.drill("item-1", depth=5)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_deep_nesting(self):
        """Test drill with deep nesting."""
        service = DrillDownService()
        result = await service.drill("item-1", depth=10)
        assert isinstance(result, dict)


class TestDrillDownServiceDataTypes:
    """Test handling of different data types."""

    @pytest.mark.asyncio
    async def test_drill_with_boolean_kwargs(self):
        """Test drill with boolean kwargs."""
        service = DrillDownService()
        result = await service.drill(
            include_children=True,
            include_parents=False,
            recursive=True
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_list_kwargs(self):
        """Test drill with list kwargs."""
        service = DrillDownService()
        result = await service.drill(
            filters=["active", "published"],
            exclude_ids=["id-1", "id-2", "id-3"]
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_dict_kwargs(self):
        """Test drill with dict kwargs."""
        service = DrillDownService()
        result = await service.drill(
            metadata={"key": "value", "nested": {"data": 123}},
            config={"depth": 2, "limit": 100}
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_drill_with_mixed_types(self):
        """Test drill with mixed data types."""
        service = DrillDownService()
        result = await service.drill(
            "item-1",
            depth=2,
            active=True,
            tags=["tag1", "tag2"],
            metadata={"key": "value"}
        )
        assert isinstance(result, dict)
