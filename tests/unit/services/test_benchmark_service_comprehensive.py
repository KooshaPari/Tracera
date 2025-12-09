"""
Comprehensive tests for BenchmarkService.

Tests all methods including:
- benchmark_view_query
- benchmark_all_views
- BenchmarkResult dataclass
- ViewPerformance dataclass

Coverage target: 90%+
"""

import pytest
import time
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.exc import DatabaseError
from tracertm.services.benchmark_service import (
    BenchmarkService,
    BenchmarkResult,
    ViewPerformance,
)


class TestBenchmarkViewQuery:
    """Test benchmark_view_query method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return BenchmarkService(mock_session)

    @pytest.mark.asyncio
    async def test_benchmark_success(self, service, mock_session):
        """Test successful view query benchmark."""
        # Mock query result
        mock_result = Mock()
        mock_result.fetchall.return_value = [("row1",), ("row2",), ("row3",)]
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await service.benchmark_view_query("traceability_matrix", limit=100)

        assert result.success is True
        assert result.row_count == 3
        assert result.duration_ms > 0
        assert result.operation == "query_traceability_matrix"
        assert result.metadata is not None
        assert result.metadata["view_name"] == "traceability_matrix"

    @pytest.mark.asyncio
    async def test_benchmark_meets_target(self, service, mock_session):
        """Test benchmark checks against performance target."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await service.benchmark_view_query("traceability_matrix")

        # Target for traceability_matrix is 50ms
        assert "meets_target" in result.metadata
        assert "target_ms" in result.metadata
        assert result.metadata["target_ms"] == 50

    @pytest.mark.asyncio
    async def test_benchmark_custom_limit(self, service, mock_session):
        """Test benchmark with custom row limit."""
        mock_result = Mock()
        mock_result.fetchall.return_value = [("row",)] * 50
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await service.benchmark_view_query("search_index", limit=50)

        assert result.row_count == 50
        assert result.metadata["limit"] == 50

    @pytest.mark.asyncio
    async def test_benchmark_error_handling(self, service, mock_session):
        """Test error handling during benchmark."""
        mock_session.execute = AsyncMock(side_effect=DatabaseError("DB error", None, None))

        result = await service.benchmark_view_query("invalid_view")

        assert result.success is False
        assert result.error is not None
        assert "DB error" in result.error
        assert result.row_count == 0
        assert result.duration_ms == 0

    @pytest.mark.asyncio
    async def test_benchmark_empty_result(self, service, mock_session):
        """Test benchmark with empty result set."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await service.benchmark_view_query("empty_view")

        assert result.success is True
        assert result.row_count == 0

    @pytest.mark.asyncio
    async def test_benchmark_unknown_view_uses_default_target(self, service, mock_session):
        """Test unknown view uses default performance target."""
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await service.benchmark_view_query("unknown_view")

        # Default target is 100ms
        assert result.metadata["target_ms"] == 100


class TestBenchmarkAllViews:
    """Test benchmark_all_views method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return BenchmarkService(mock_session)

    @pytest.mark.asyncio
    async def test_benchmark_all_views(self, service):
        """Test benchmarking all views."""
        # Mock benchmark_view_query to avoid actual DB calls
        async def mock_benchmark(view_name, limit=100):
            return BenchmarkResult(
                operation=f"query_{view_name}",
                duration_ms=25.0,
                row_count=10,
                success=True,
                metadata={
                    "view_name": view_name,
                    "limit": limit,
                    "target_ms": 50,
                    "meets_target": True,
                },
            )

        service.benchmark_view_query = mock_benchmark

        results = await service.benchmark_all_views()

        # Should return list of ViewPerformance objects
        assert isinstance(results, list)
        assert all(isinstance(r, ViewPerformance) for r in results)

    @pytest.mark.asyncio
    async def test_benchmark_all_includes_all_targets(self, service):
        """Test that all defined views are benchmarked."""
        async def mock_benchmark(view_name, limit=100):
            return BenchmarkResult(
                operation=f"query_{view_name}",
                duration_ms=25.0,
                row_count=10,
                success=True,
                metadata={
                    "view_name": view_name,
                    "limit": limit,
                    "target_ms": service.PERFORMANCE_TARGETS.get(view_name, 100),
                    "meets_target": True,
                },
            )

        service.benchmark_view_query = mock_benchmark

        results = await service.benchmark_all_views()

        # Should have results for all defined targets
        view_names = {r.view_name for r in results}
        for target_view in service.PERFORMANCE_TARGETS.keys():
            assert target_view in view_names


class TestPerformanceTargets:
    """Test PERFORMANCE_TARGETS configuration."""

    def test_targets_defined(self):
        """Test that performance targets are defined."""
        assert BenchmarkService.PERFORMANCE_TARGETS is not None
        assert len(BenchmarkService.PERFORMANCE_TARGETS) > 0

    def test_targets_reasonable(self):
        """Test that all targets are reasonable values."""
        for view, target_ms in BenchmarkService.PERFORMANCE_TARGETS.items():
            assert target_ms > 0
            assert target_ms < 1000  # No target should be > 1 second

    def test_critical_views_have_targets(self):
        """Test that critical views have defined targets."""
        critical_views = [
            "traceability_matrix",
            "search_index",
            "agent_interface",
        ]

        for view in critical_views:
            assert view in BenchmarkService.PERFORMANCE_TARGETS


class TestBenchmarkResult:
    """Test BenchmarkResult dataclass."""

    def test_benchmark_result_creation(self):
        """Test creating BenchmarkResult."""
        result = BenchmarkResult(
            operation="test_op",
            duration_ms=25.5,
            row_count=10,
            success=True,
        )

        assert result.operation == "test_op"
        assert result.duration_ms == 25.5
        assert result.row_count == 10
        assert result.success is True
        assert result.error is None
        assert result.metadata is None

    def test_benchmark_result_with_error(self):
        """Test BenchmarkResult with error."""
        result = BenchmarkResult(
            operation="test_op",
            duration_ms=0,
            row_count=0,
            success=False,
            error="Test error",
        )

        assert result.success is False
        assert result.error == "Test error"

    def test_benchmark_result_with_metadata(self):
        """Test BenchmarkResult with metadata."""
        metadata = {"view": "test", "limit": 100}
        result = BenchmarkResult(
            operation="test_op",
            duration_ms=10.0,
            row_count=5,
            success=True,
            metadata=metadata,
        )

        assert result.metadata == metadata


class TestViewPerformance:
    """Test ViewPerformance dataclass."""

    def test_view_performance_creation(self):
        """Test creating ViewPerformance."""
        vp = ViewPerformance(
            view_name="test_view",
            query_time_ms=45.0,
            row_count=100,
            size_bytes=1024,
            meets_target=True,
            target_ms=50.0,
        )

        assert vp.view_name == "test_view"
        assert vp.query_time_ms == 45.0
        assert vp.row_count == 100
        assert vp.size_bytes == 1024
        assert vp.meets_target is True
        assert vp.target_ms == 50.0

    def test_view_performance_not_meeting_target(self):
        """Test ViewPerformance when target not met."""
        vp = ViewPerformance(
            view_name="slow_view",
            query_time_ms=150.0,
            row_count=1000,
            size_bytes=10240,
            meets_target=False,
            target_ms=100.0,
        )

        assert vp.meets_target is False
        assert vp.query_time_ms > vp.target_ms
