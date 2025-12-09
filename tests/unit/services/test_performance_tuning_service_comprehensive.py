"""
Comprehensive tests for PerformanceTuningService.

Tests all methods including:
- analyze_performance
- record_metric
- get_metrics
- get_metric_stats
- add_recommendation
- get_recommendations
- clear_recommendations
- configure_cache
- get_cache_config

Coverage target: 90%+
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from tracertm.services.performance_tuning_service import PerformanceTuningService


class TestAnalyzePerformance:
    """Test analyze_performance method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    @pytest.mark.asyncio
    async def test_analyze_basic(self, service):
        """Test basic performance analysis."""
        result = await service.analyze_performance()

        assert "timestamp" in result
        assert "metrics_collected" in result
        assert "cache_enabled" in result
        assert "cache_ttl" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_analyze_tracks_metrics_count(self, service):
        """Test analysis tracks number of metrics."""
        service.record_metric("test_metric", 100)
        service.record_metric("test_metric", 200)

        result = await service.analyze_performance()

        assert result["metrics_collected"] == 2

    @pytest.mark.asyncio
    async def test_analyze_shows_cache_config(self, service):
        """Test analysis shows cache configuration."""
        service.configure_cache(enabled=False, ttl_seconds=600)

        result = await service.analyze_performance()

        assert result["cache_enabled"] is False
        assert result["cache_ttl"] == 600


class TestRecordMetric:
    """Test record_metric method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    def test_record_basic_metric(self, service):
        """Test recording a basic metric."""
        service.record_metric("api_latency", 45.5)

        metrics = service.get_metrics("api_latency")
        assert len(metrics) == 1
        assert metrics[0]["name"] == "api_latency"
        assert metrics[0]["value"] == 45.5
        assert metrics[0]["unit"] == "ms"

    def test_record_metric_with_custom_unit(self, service):
        """Test recording metric with custom unit."""
        service.record_metric("memory_usage", 1024, unit="MB")

        metrics = service.get_metrics("memory_usage")
        assert metrics[0]["unit"] == "MB"
        assert metrics[0]["value"] == 1024

    def test_record_multiple_metrics(self, service):
        """Test recording multiple metrics."""
        service.record_metric("query_time", 10)
        service.record_metric("query_time", 20)
        service.record_metric("query_time", 15)

        metrics = service.get_metrics("query_time")
        assert len(metrics) == 3

    def test_record_metric_includes_timestamp(self, service):
        """Test recorded metrics include timestamp."""
        service.record_metric("test", 100)

        metrics = service.get_metrics("test")
        assert "timestamp" in metrics[0]
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(metrics[0]["timestamp"])


class TestGetMetrics:
    """Test get_metrics method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    def test_get_all_metrics(self, service):
        """Test getting all metrics."""
        service.record_metric("metric1", 10)
        service.record_metric("metric2", 20)
        service.record_metric("metric3", 30)

        metrics = service.get_metrics()
        assert len(metrics) == 3

    def test_get_metrics_filtered(self, service):
        """Test getting metrics filtered by name."""
        service.record_metric("api_latency", 10)
        service.record_metric("db_query", 20)
        service.record_metric("api_latency", 15)

        metrics = service.get_metrics("api_latency")
        assert len(metrics) == 2
        assert all(m["name"] == "api_latency" for m in metrics)

    def test_get_metrics_empty(self, service):
        """Test getting metrics when none exist."""
        metrics = service.get_metrics()
        assert len(metrics) == 0

    def test_get_metrics_nonexistent_name(self, service):
        """Test getting metrics with nonexistent name."""
        service.record_metric("metric1", 10)

        metrics = service.get_metrics("nonexistent")
        assert len(metrics) == 0


class TestGetMetricStats:
    """Test get_metric_stats method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    def test_get_stats_basic(self, service):
        """Test getting basic metric statistics."""
        service.record_metric("api_latency", 10)
        service.record_metric("api_latency", 20)
        service.record_metric("api_latency", 30)

        stats = service.get_metric_stats("api_latency")

        assert stats["metric_name"] == "api_latency"
        assert stats["count"] == 3
        assert stats["average"] == 20.0
        assert stats["min"] == 10
        assert stats["max"] == 30
        assert stats["unit"] == "ms"

    def test_get_stats_single_value(self, service):
        """Test stats with single value."""
        service.record_metric("test", 42.5)

        stats = service.get_metric_stats("test")

        assert stats["count"] == 1
        assert stats["average"] == 42.5
        assert stats["min"] == 42.5
        assert stats["max"] == 42.5

    def test_get_stats_no_metrics(self, service):
        """Test stats when no metrics exist."""
        stats = service.get_metric_stats("nonexistent")

        assert "error" in stats
        assert "No metrics found" in stats["error"]

    def test_get_stats_preserves_unit(self, service):
        """Test that stats preserve the metric unit."""
        service.record_metric("memory", 100, unit="GB")
        service.record_metric("memory", 200, unit="GB")

        stats = service.get_metric_stats("memory")

        assert stats["unit"] == "GB"


class TestRecommendations:
    """Test recommendation methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    def test_add_recommendation(self, service):
        """Test adding a recommendation."""
        service.add_recommendation("Enable caching for faster queries")

        recs = service.get_recommendations()
        assert len(recs) == 1
        assert "Enable caching" in recs[0]

    def test_add_duplicate_recommendation(self, service):
        """Test adding duplicate recommendation is ignored."""
        service.add_recommendation("Use indexes")
        service.add_recommendation("Use indexes")

        recs = service.get_recommendations()
        assert len(recs) == 1

    def test_add_multiple_recommendations(self, service):
        """Test adding multiple recommendations."""
        service.add_recommendation("Recommendation 1")
        service.add_recommendation("Recommendation 2")
        service.add_recommendation("Recommendation 3")

        recs = service.get_recommendations()
        assert len(recs) == 3

    def test_get_recommendations_empty(self, service):
        """Test getting recommendations when none exist."""
        recs = service.get_recommendations()
        assert len(recs) == 0

    def test_clear_recommendations(self, service):
        """Test clearing recommendations."""
        service.add_recommendation("Rec 1")
        service.add_recommendation("Rec 2")

        count = service.clear_recommendations()

        assert count == 2
        assert len(service.get_recommendations()) == 0

    def test_clear_recommendations_empty(self, service):
        """Test clearing when no recommendations exist."""
        count = service.clear_recommendations()

        assert count == 0


class TestCacheConfiguration:
    """Test cache configuration methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    def test_configure_cache_defaults(self, service):
        """Test cache has default configuration."""
        config = service.get_cache_config()

        assert config["enabled"] is True
        assert config["ttl_seconds"] == 300
        assert config["max_size"] == 1000

    def test_configure_cache_custom(self, service):
        """Test configuring cache with custom values."""
        result = service.configure_cache(
            enabled=False,
            ttl_seconds=600,
            max_size=2000,
        )

        assert result["enabled"] is False
        assert result["ttl_seconds"] == 600
        assert result["max_size"] == 2000

    def test_configure_cache_partial(self, service):
        """Test partial cache configuration."""
        service.configure_cache(enabled=False)

        config = service.get_cache_config()
        assert config["enabled"] is False

    def test_get_cache_config(self, service):
        """Test getting cache configuration."""
        service.configure_cache(ttl_seconds=500)

        config = service.get_cache_config()

        assert "enabled" in config
        assert "ttl_seconds" in config
        assert "max_size" in config
        assert config["ttl_seconds"] == 500


class TestIntegration:
    """Integration tests combining multiple features."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return PerformanceTuningService(AsyncMock())

    @pytest.mark.asyncio
    async def test_complete_workflow(self, service):
        """Test complete performance tuning workflow."""
        # Record metrics
        service.record_metric("api_latency", 50)
        service.record_metric("api_latency", 75)
        service.record_metric("db_query", 100)

        # Add recommendations
        service.add_recommendation("Optimize slow queries")
        service.add_recommendation("Enable caching")

        # Configure cache
        service.configure_cache(enabled=True, ttl_seconds=600)

        # Analyze performance
        analysis = await service.analyze_performance()

        assert analysis["metrics_collected"] == 3
        assert analysis["recommendations"] == 2
        assert analysis["cache_enabled"] is True
        assert analysis["cache_ttl"] == 600

    def test_metric_lifecycle(self, service):
        """Test metric recording and analysis lifecycle."""
        # Record various metrics
        for i in range(10):
            service.record_metric("query_time", i * 10)

        # Get statistics
        stats = service.get_metric_stats("query_time")

        assert stats["count"] == 10
        assert stats["min"] == 0
        assert stats["max"] == 90

    def test_recommendation_lifecycle(self, service):
        """Test recommendation lifecycle."""
        # Add recommendations based on metrics
        service.record_metric("query_time", 500)
        service.add_recommendation("Query is slow, add index")

        service.record_metric("memory_usage", 2000, unit="MB")
        service.add_recommendation("High memory usage, optimize")

        recs = service.get_recommendations()
        assert len(recs) == 2

        # Clear and verify
        count = service.clear_recommendations()
        assert count == 2
        assert len(service.get_recommendations()) == 0
