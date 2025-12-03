"""Extreme coverage tests for PerformanceOptimizationService - push to 90%+."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.performance_optimization_service import (
    PerformanceOptimizationService,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_optimize_queries_empty_recommendations(db_session: AsyncSession):
    """Test optimizing queries with empty recommendations."""
    service = PerformanceOptimizationService(db_session)

    result = await service.optimize_queries(project_id="proj_empty")

    assert isinstance(result, dict)
    assert result["project_id"] == "proj_empty"
    assert "recommendations" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_caching_zero_ttl(db_session: AsyncSession):
    """Test enabling cache with zero TTL."""
    service = PerformanceOptimizationService(db_session)

    result = await service.enable_caching("zero_ttl", 0)

    assert result["enabled"] is True
    assert result["ttl_seconds"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_caching_negative_ttl(db_session: AsyncSession):
    """Test enabling cache with negative TTL."""
    service = PerformanceOptimizationService(db_session)

    result = await service.enable_caching("negative_ttl", -100)

    assert result["enabled"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_disable_caching_nonexistent_key(db_session: AsyncSession):
    """Test disabling cache for nonexistent key."""
    service = PerformanceOptimizationService(db_session)

    result = await service.disable_caching("nonexistent_key")

    assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clear_cache_empty(db_session: AsyncSession):
    """Test clearing empty cache."""
    service = PerformanceOptimizationService(db_session)

    result = await service.clear_cache()

    assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_cache_stats_empty(db_session: AsyncSession):
    """Test getting cache stats when empty."""
    service = PerformanceOptimizationService(db_session)

    result = await service.get_cache_stats()

    assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_optimize_queries_large_project(db_session: AsyncSession):
    """Test optimizing queries for large project."""
    service = PerformanceOptimizationService(db_session)

    result = await service.optimize_queries(project_id="large_proj")

    assert isinstance(result, dict)
    assert result["project_id"] == "large_proj"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_operations_stress(db_session: AsyncSession):
    """Test cache operations under stress."""
    service = PerformanceOptimizationService(db_session)

    # Enable many caches
    for i in range(100):
        result = await service.enable_caching(f"stress_key_{i}", 300)
        assert result["enabled"] is True

    # Get stats
    stats = await service.get_cache_stats()
    assert isinstance(stats, dict)

    # Clear all
    clear_result = await service.clear_cache()
    assert isinstance(clear_result, dict)
