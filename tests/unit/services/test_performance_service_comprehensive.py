"""
Comprehensive tests for PerformanceService.

Tests all methods: analyze_query_performance, get_slow_queries,
get_cache_stats, recommend_optimizations, get_project_statistics.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy import func

from tracertm.services.performance_service import PerformanceService


class TestAnalyzeQueryPerformance:
    """Test analyze_query_performance method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked session."""
        session = AsyncMock()
        service = PerformanceService(session)
        return service

    @pytest.mark.asyncio
    async def test_analyze_empty_project(self, service):
        """Test analyzing project with no items."""
        # Mock count queries
        items_result = Mock()
        items_result.scalar.return_value = 0
        links_result = Mock()
        links_result.scalar.return_value = 0

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.analyze_query_performance("proj-1")

        assert result["item_count"] == 0
        assert result["link_count"] == 0
        assert result["density"] == 0.0
        assert result["complexity"] == "low"

    @pytest.mark.asyncio
    async def test_analyze_low_density(self, service):
        """Test analyzing project with low link density."""
        items_result = Mock()
        items_result.scalar.return_value = 100
        links_result = Mock()
        links_result.scalar.return_value = 50

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.analyze_query_performance("proj-1")

        assert result["item_count"] == 100
        assert result["link_count"] == 50
        # density = 50 / (100 * 99) = 0.00505...
        assert result["density"] < 0.1
        assert result["complexity"] == "low"

    @pytest.mark.asyncio
    async def test_analyze_medium_density(self, service):
        """Test analyzing project with medium link density."""
        items_result = Mock()
        items_result.scalar.return_value = 10
        links_result = Mock()
        links_result.scalar.return_value = 20

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.analyze_query_performance("proj-1")

        # density = 20 / (10 * 9) = 0.222...
        assert result["density"] > 0.1
        assert result["density"] < 0.5
        assert result["complexity"] == "medium"

    @pytest.mark.asyncio
    async def test_analyze_high_density(self, service):
        """Test analyzing project with high link density."""
        items_result = Mock()
        items_result.scalar.return_value = 5
        links_result = Mock()
        links_result.scalar.return_value = 15

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.analyze_query_performance("proj-1")

        # density = 15 / (5 * 4) = 0.75
        assert result["density"] > 0.5
        assert result["complexity"] == "high"

    @pytest.mark.asyncio
    async def test_analyze_handles_none_counts(self, service):
        """Test analyzing handles None counts from database."""
        items_result = Mock()
        items_result.scalar.return_value = None
        links_result = Mock()
        links_result.scalar.return_value = None

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.analyze_query_performance("proj-1")

        assert result["item_count"] == 0
        assert result["link_count"] == 0


class TestGetSlowQueries:
    """Test get_slow_queries method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return PerformanceService(session)

    @pytest.mark.asyncio
    async def test_get_slow_queries_returns_empty(self, service):
        """Test get_slow_queries returns empty list."""
        result = await service.get_slow_queries()

        assert result == []


class TestGetCacheStats:
    """Test get_cache_stats method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return PerformanceService(session)

    @pytest.mark.asyncio
    async def test_get_cache_stats(self, service):
        """Test get_cache_stats returns stats."""
        result = await service.get_cache_stats()

        assert result["cache_enabled"] is True
        assert result["cache_size"] == 1000
        assert result["cache_ttl"] == 3600


class TestRecommendOptimizations:
    """Test recommend_optimizations method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return PerformanceService(session)

    @pytest.mark.asyncio
    async def test_no_recommendations_for_small_project(self, service):
        """Test no recommendations for small project."""
        items_result = Mock()
        items_result.scalar.return_value = 100
        links_result = Mock()
        links_result.scalar.return_value = 50

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.recommend_optimizations("proj-1")

        assert result == []

    @pytest.mark.asyncio
    async def test_recommends_archiving_for_large_items(self, service):
        """Test recommendation for large item count."""
        items_result = Mock()
        items_result.scalar.return_value = 15000
        links_result = Mock()
        links_result.scalar.return_value = 1000

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.recommend_optimizations("proj-1")

        assert "Consider archiving old items" in result

    @pytest.mark.asyncio
    async def test_recommends_refactoring_for_high_density(self, service):
        """Test recommendation for high link density."""
        items_result = Mock()
        items_result.scalar.return_value = 5
        links_result = Mock()
        links_result.scalar.return_value = 15  # density > 0.5

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.recommend_optimizations("proj-1")

        assert any("refactoring" in r for r in result)

    @pytest.mark.asyncio
    async def test_recommends_caching_for_many_links(self, service):
        """Test recommendation for large link count."""
        items_result = Mock()
        items_result.scalar.return_value = 1000
        links_result = Mock()
        links_result.scalar.return_value = 60000

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.recommend_optimizations("proj-1")

        assert any("caching" in r for r in result)

    @pytest.mark.asyncio
    async def test_multiple_recommendations(self, service):
        """Test multiple recommendations."""
        items_result = Mock()
        items_result.scalar.return_value = 20000  # Large items
        links_result = Mock()
        links_result.scalar.return_value = 100000  # Many links, high density

        service.session.execute = AsyncMock(side_effect=[items_result, links_result])

        result = await service.recommend_optimizations("proj-1")

        assert len(result) >= 2


class TestGetProjectStatistics:
    """Test get_project_statistics method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return PerformanceService(session)

    @pytest.mark.asyncio
    async def test_get_statistics_basic(self, service):
        """Test getting basic project statistics."""
        # Mock count queries
        items_result = Mock()
        items_result.scalar.return_value = 50
        links_result = Mock()
        links_result.scalar.return_value = 25

        # Mock view distribution
        views_result = Mock()
        views_result.all.return_value = [("REQ", 30), ("DESIGN", 20)]

        # Mock status distribution
        status_result = Mock()
        status_result.all.return_value = [("active", 40), ("done", 10)]

        service.session.execute = AsyncMock(
            side_effect=[items_result, links_result, views_result, status_result]
        )

        result = await service.get_project_statistics("proj-1")

        assert result["item_count"] == 50
        assert result["link_count"] == 25
        assert result["views"]["REQ"] == 30
        assert result["views"]["DESIGN"] == 20
        assert result["statuses"]["active"] == 40
        assert result["statuses"]["done"] == 10

    @pytest.mark.asyncio
    async def test_get_statistics_includes_complexity(self, service):
        """Test statistics include complexity analysis."""
        items_result = Mock()
        items_result.scalar.return_value = 100
        links_result = Mock()
        links_result.scalar.return_value = 50

        views_result = Mock()
        views_result.all.return_value = []

        status_result = Mock()
        status_result.all.return_value = []

        service.session.execute = AsyncMock(
            side_effect=[items_result, links_result, views_result, status_result]
        )

        result = await service.get_project_statistics("proj-1")

        assert "density" in result
        assert "complexity" in result


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_session_and_repo(self):
        """Test initialization creates session and projects repo."""
        session = AsyncMock()
        service = PerformanceService(session)

        assert service.session == session
        assert service.projects is not None
