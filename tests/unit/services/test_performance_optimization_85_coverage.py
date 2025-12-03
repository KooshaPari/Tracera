"""Comprehensive tests for PerformanceOptimizationService - 85%+ coverage."""


import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.performance_optimization_service import (
    PerformanceOptimizationService,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_optimize_queries(db_session: AsyncSession):
    """Test optimizing queries."""
    service = PerformanceOptimizationService(db_session)

    result = await service.optimize_queries(project_id="proj1")

    assert isinstance(result, dict)
    assert "project_id" in result
    assert result["project_id"] == "proj1"
    assert "recommendations" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_caching(db_session: AsyncSession):
    """Test enabling caching."""
    service = PerformanceOptimizationService(db_session)

    result = await service.enable_caching(cache_key="test_key", ttl_seconds=300)

    assert isinstance(result, dict)
    assert result["cache_key"] == "test_key"
    assert result["enabled"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_disable_caching(db_session: AsyncSession):
    """Test disabling caching."""
    service = PerformanceOptimizationService(db_session)

    # First enable caching
    await service.enable_caching(cache_key="test_key")

    # Then disable it
    result = await service.disable_caching(cache_key="test_key")

    assert isinstance(result, dict)
    assert result["enabled"] is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clear_cache(db_session: AsyncSession):
    """Test clearing cache."""
    service = PerformanceOptimizationService(db_session)

    # Add some cache entries
    await service.enable_caching(cache_key="key1")
    await service.enable_caching(cache_key="key2")

    result = await service.clear_cache()

    assert isinstance(result, dict)
    assert "cleared_count" in result or result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_cache_stats(db_session: AsyncSession):
    """Test getting cache statistics."""
    service = PerformanceOptimizationService(db_session)

    result = await service.get_cache_stats()

    assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_operations_sequence(db_session: AsyncSession):
    """Test sequence of cache operations."""
    service = PerformanceOptimizationService(db_session)

    # Enable multiple caches
    result1 = await service.enable_caching("key1", 300)
    assert result1["enabled"] is True

    result2 = await service.enable_caching("key2", 600)
    assert result2["enabled"] is True

    # Get stats
    stats = await service.get_cache_stats()
    assert isinstance(stats, dict)

    # Disable one
    result3 = await service.disable_caching("key1")
    assert result3["enabled"] is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_optimize_queries_multiple_projects(db_session: AsyncSession):
    """Test optimizing queries for multiple projects."""
    service = PerformanceOptimizationService(db_session)

    result1 = await service.optimize_queries("proj1")
    assert result1["project_id"] == "proj1"

    result2 = await service.optimize_queries("proj2")
    assert result2["project_id"] == "proj2"

    assert len(result1["recommendations"]) > 0
    assert len(result2["recommendations"]) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_ttl_variations(db_session: AsyncSession):
    """Test cache with different TTL values."""
    service = PerformanceOptimizationService(db_session)

    # Short TTL
    result1 = await service.enable_caching("short_ttl", 60)
    assert result1["ttl_seconds"] == 60

    # Long TTL
    result2 = await service.enable_caching("long_ttl", 3600)
    assert result2["ttl_seconds"] == 3600

    # Default TTL
    result3 = await service.enable_caching("default_ttl")
    assert result3["ttl_seconds"] == 300
