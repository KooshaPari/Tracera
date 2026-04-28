"""Gap coverage tests for more low-coverage services.

Targets: query_optimization_service.py (22.58%), project_backup_service.py (11.90%),
         traceability_matrix_service.py (51.24%), shortest_path_service.py (55.23%),
         performance_tuning_service.py (59.77%), ingestion_service.py (75%).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO


class TestQueryOptimizationService:
    """Tests for QueryOptimizationService."""

    def test_query_optimization_service_import(self) -> None:
        """Test QueryOptimizationService can be imported."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        assert QueryOptimizationService is not None

    def test_query_optimization_service_init(self) -> None:
        """Test QueryOptimizationService initialization."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        assert service.session == mock_session
        assert service.items is not None
        assert service.links is not None
        assert service.query_cache == {}
        assert service.query_stats == []

    def test_rate_performance_excellent(self) -> None:
        """Test performance rating - excellent."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        assert service._rate_performance(0.05) == "Excellent"

    def test_rate_performance_good(self) -> None:
        """Test performance rating - good."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        assert service._rate_performance(0.3) == "Good"

    def test_rate_performance_fair(self) -> None:
        """Test performance rating - fair."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        assert service._rate_performance(0.7) == "Fair"

    def test_rate_performance_poor(self) -> None:
        """Test performance rating - poor."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        assert service._rate_performance(2.0) == "Poor"

    def test_suggest_optimizations_slow_query(self) -> None:
        """Test optimization suggestions for slow query."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        suggestions = service._suggest_optimizations(1.5, 50)

        assert any("indexes" in s.lower() for s in suggestions)

    def test_suggest_optimizations_large_result(self) -> None:
        """Test optimization suggestions for large result set."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        suggestions = service._suggest_optimizations(0.3, 15000)

        assert any("pagination" in s.lower() for s in suggestions)

    def test_suggest_optimizations_cache_candidate(self) -> None:
        """Test optimization suggestions for cache candidate."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        suggestions = service._suggest_optimizations(0.6, 50)

        assert any("caching" in s.lower() for s in suggestions)

    def test_cache_query(self) -> None:
        """Test caching a query result."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        service.cache_query("test-key", {"data": "value"}, ttl_seconds=60)

        assert "test-key" in service.query_cache
        assert service.query_cache["test-key"]["result"] == {"data": "value"}

    def test_get_cached_query_hit(self) -> None:
        """Test getting a cached query - cache hit."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        service.cache_query("test-key", {"data": "value"}, ttl_seconds=60)
        result = service.get_cached_query("test-key")

        assert result == {"data": "value"}

    def test_get_cached_query_miss(self) -> None:
        """Test getting a cached query - cache miss."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        result = service.get_cached_query("nonexistent-key")

        assert result is None

    def test_get_cached_query_expired(self) -> None:
        """Test getting an expired cached query."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        # Manually add expired cache entry
        service.query_cache["expired-key"] = {
            "result": {"data": "old"},
            "cached_at": "2020-01-01T00:00:00",  # Old date
            "ttl_seconds": 60,
        }

        result = service.get_cached_query("expired-key")

        assert result is None
        assert "expired-key" not in service.query_cache

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        service.cache_query("key1", "value1")
        service.cache_query("key2", "value2")

        count = service.clear_cache()

        assert count == COUNT_TWO
        assert len(service.query_cache) == 0

    def test_get_cache_stats(self) -> None:
        """Test getting cache statistics."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        service.cache_query("key1", "value1")
        service.query_stats = [{"execution_time_seconds": 0.1}]

        stats = service.get_cache_stats()

        assert stats["cached_queries"] == 1
        assert stats["total_queries_executed"] == 1
        assert "key1" in stats["cache_keys"]

    def test_get_query_statistics_empty(self) -> None:
        """Test getting query statistics when empty."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        stats = service.get_query_statistics()

        assert stats["total_queries"] == 0
        assert stats["average_execution_time"] == 0

    def test_get_query_statistics_with_data(self) -> None:
        """Test getting query statistics with data."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        service.query_stats = [
            {"execution_time_seconds": 0.1, "items_returned": 10},
            {"execution_time_seconds": 0.3, "items_returned": 20},
            {"execution_time_seconds": 0.2, "items_returned": 15},
        ]

        stats = service.get_query_statistics()

        assert stats["total_queries"] == COUNT_THREE
        assert stats["min_execution_time"] == 0.1
        assert stats["max_execution_time"] == 0.3
        assert stats["total_items_returned"] == 45

    def test_recommend_indexes_not_enough_data(self) -> None:
        """Test index recommendations with insufficient data."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        service.query_stats = [{"query_filters": {"status": "todo"}} for _ in range(5)]

        recommendations = service.recommend_indexes("project-123")

        # Not enough queries to make recommendations
        assert recommendations == []

    def test_recommend_indexes_status_heavy(self) -> None:
        """Test index recommendations for status-heavy queries."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        # More than 50% of queries filter by status
        service.query_stats = [{"query_filters": {"status": "todo"}} for _ in range(8)] + [
            {"query_filters": {"type": "task"}} for _ in range(4)
        ]

        recommendations = service.recommend_indexes("project-123")

        assert any("idx_item_status" in r for r in recommendations)

    def test_recommend_indexes_view_heavy(self) -> None:
        """Test index recommendations for view-heavy queries."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        # More than 50% of queries filter by view
        service.query_stats = [{"query_filters": {"view": "FEATURE"}} for _ in range(8)] + [
            {"query_filters": {"type": "task"}} for _ in range(4)
        ]

        recommendations = service.recommend_indexes("project-123")

        assert any("idx_item_view" in r for r in recommendations)

    @pytest.mark.asyncio
    async def test_analyze_query_performance(self) -> None:
        """Test analyzing query performance."""
        from tracertm.services.query_optimization_service import QueryOptimizationService

        mock_session = MagicMock()
        service = QueryOptimizationService(mock_session)

        # Mock items repository query
        mock_items = [MagicMock(), MagicMock()]
        service.items.query = AsyncMock(return_value=mock_items)

        result = await service.analyze_query_performance(
            "project-123",
            {"status": "todo"},
        )

        assert "execution_time_seconds" in result
        assert result["items_returned"] == COUNT_TWO
        assert "performance_rating" in result
        assert "optimization_suggestions" in result


class TestProjectBackupService:
    """Tests for ProjectBackupService."""

    def test_project_backup_service_import(self) -> None:
        """Test ProjectBackupService can be imported."""
        from tracertm.services.project_backup_service import ProjectBackupService

        assert ProjectBackupService is not None

    def test_project_backup_service_init(self) -> None:
        """Test ProjectBackupService initialization."""
        from tracertm.services.project_backup_service import ProjectBackupService

        mock_session = MagicMock()
        service = ProjectBackupService(mock_session)

        assert service.session == mock_session


class TestTraceabilityMatrixService:
    """Tests for TraceabilityMatrixService."""

    def test_traceability_matrix_service_import(self) -> None:
        """Test TraceabilityMatrixService can be imported."""
        from tracertm.services.traceability_matrix_service import TraceabilityMatrixService

        assert TraceabilityMatrixService is not None


class TestShortestPathService:
    """Tests for ShortestPathService."""

    def test_shortest_path_service_import(self) -> None:
        """Test ShortestPathService can be imported."""
        from tracertm.services.shortest_path_service import ShortestPathService

        assert ShortestPathService is not None


class TestPerformanceTuningService:
    """Tests for PerformanceTuningService."""

    def test_performance_tuning_service_import(self) -> None:
        """Test PerformanceTuningService can be imported."""
        from tracertm.services.performance_tuning_service import PerformanceTuningService

        assert PerformanceTuningService is not None


class TestIngestionService:
    """Tests for IngestionService."""

    def test_ingestion_service_import(self) -> None:
        """Test IngestionService can be imported."""
        from tracertm.services.ingestion_service import IngestionService

        assert IngestionService is not None

    def test_ingestion_service_init(self) -> None:
        """Test IngestionService initialization."""
        from tracertm.services.ingestion_service import IngestionService

        service = IngestionService()
        assert service.db_session is None

    @pytest.mark.asyncio
    async def test_ingestion_service_ingest(self) -> None:
        """Test IngestionService ingest method."""
        from tracertm.services.ingestion_service import IngestionService

        service = IngestionService()
        result = await service.ingest([{"data": "test"}])

        assert isinstance(result, dict)
