"""Comprehensive tests for BenchmarkService - 85%+ coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.benchmark_service import (
    BenchmarkResult,
    BenchmarkService,
    ViewPerformance,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_view_query_success():
    """Test successful view query benchmark."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    # Mock the session execute
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(1, 2, 3), (4, 5, 6)]

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = mock_result
        result = await service.benchmark_view_query("test_view", limit=100)

        assert isinstance(result, BenchmarkResult)
        assert result.operation == "query_test_view"
        assert result.success is True
        assert result.row_count == 2
        assert result.metadata["view_name"] == "test_view"
        assert result.metadata["limit"] == 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_view_query_error():
    """Test view query benchmark with error."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.side_effect = Exception("Query failed")
        result = await service.benchmark_view_query("nonexistent_view")

        assert result.success is False
        assert result.error == "Query failed"
        assert result.row_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_all_views():
    """Test benchmarking all views."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(1, 2, 3)]
    mock_result.scalar.return_value = 1024000

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = mock_result
        results = await service.benchmark_all_views()

        assert isinstance(results, list)
        assert len(results) == len(service.PERFORMANCE_TARGETS)
        for result in results:
            assert isinstance(result, ViewPerformance)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_refresh_incremental_success():
    """Test incremental refresh benchmark."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock):
        with patch.object(mock_session, 'commit', new_callable=AsyncMock):
            result = await service.benchmark_refresh_incremental()

            assert result.operation == "refresh_incremental"
            assert result.success is True
            assert result.metadata["target_ms"] == 1000


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_refresh_incremental_error():
    """Test incremental refresh benchmark with error."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.side_effect = Exception("Refresh failed")
        result = await service.benchmark_refresh_incremental()

        assert result.success is False
        assert result.error == "Refresh failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_refresh_full_success():
    """Test full refresh benchmark."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock):
        with patch.object(mock_session, 'commit', new_callable=AsyncMock):
            result = await service.benchmark_refresh_full()

            assert result.operation == "refresh_full"
            assert result.success is True
            assert result.metadata["target_ms"] == 5000


@pytest.mark.unit
@pytest.mark.asyncio
async def test_benchmark_refresh_full_error():
    """Test full refresh benchmark with error."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.side_effect = Exception("Full refresh failed")
        result = await service.benchmark_refresh_full()

        assert result.success is False
        assert result.error == "Full refresh failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_performance_report():
    """Test getting performance report."""
    mock_session = MagicMock(spec=AsyncSession)
    service = BenchmarkService(mock_session)

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [(1, 2, 3)]
    mock_result.scalar.return_value = 1024000

    with patch.object(mock_session, 'execute', new_callable=AsyncMock) as mock_execute:
        with patch.object(mock_session, 'commit', new_callable=AsyncMock):
            mock_execute.return_value = mock_result
            report = await service.get_performance_report()

            assert isinstance(report, dict)
            assert "timestamp" in report
            assert "summary" in report
            assert "views" in report
            assert "refresh_operations" in report
            assert report["summary"]["total_views"] == len(service.PERFORMANCE_TARGETS)
