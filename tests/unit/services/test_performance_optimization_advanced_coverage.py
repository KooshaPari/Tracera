"""Advanced tests for PerformanceOptimizationService - push to 85%+ coverage."""


import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.performance_optimization_service import (
    PerformanceOptimizationService,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_optimize_queries_with_recommendations(db_session: AsyncSession):
    """Test optimizing queries with recommendations."""
    service = PerformanceOptimizationService(db_session)

    result = await service.optimize_queries(project_id="proj1")

    assert isinstance(result, dict)
    assert result["project_id"] == "proj1"
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_caching_multiple_keys(db_session: AsyncSession):
    """Test enabling caching for multiple keys."""
    service = PerformanceOptimizationService(db_session)

    results = []
    for i in range(5):
        result = await service.enable_caching(f"key{i}", 300 + i * 100)
        results.append(result)

    for i, result in enumerate(results):
        assert result["enabled"] is True
        assert result["cache_key"] == f"key{i}"
        assert result["ttl_seconds"] == 300 + i * 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_operations_lifecycle(db_session: AsyncSession):
    """Test complete cache lifecycle."""
    service = PerformanceOptimizationService(db_session)

    # Enable cache
    enable_result = await service.enable_caching("lifecycle_key", 600)
    assert enable_result["enabled"] is True

    # Get stats
    stats = await service.get_cache_stats()
    assert isinstance(stats, dict)

    # Disable cache
    disable_result = await service.disable_caching("lifecycle_key")
    assert disable_result["enabled"] is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clear_cache_multiple_entries(db_session: AsyncSession):
    """Test clearing cache with multiple entries."""
    service = PerformanceOptimizationService(db_session)

    # Add multiple cache entries
    for i in range(10):
        await service.enable_caching(f"clear_key{i}")

    # Clear all
    result = await service.clear_cache()
    assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_optimize_queries_multiple_projects(db_session: AsyncSession):
    """Test optimizing queries for multiple projects."""
    service = PerformanceOptimizationService(db_session)

    results = []
    for i in range(3):
        result = await service.optimize_queries(f"proj{i}")
        results.append(result)

    for i, result in enumerate(results):
        assert result["project_id"] == f"proj{i}"
        assert "recommendations" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_ttl_edge_cases(db_session: AsyncSession):
    """Test cache with edge case TTL values."""
    service = PerformanceOptimizationService(db_session)

    # Very short TTL
    result1 = await service.enable_caching("short", 1)
    assert result1["ttl_seconds"] == 1

    # Very long TTL
    result2 = await service.enable_caching("long", 86400)
    assert result2["ttl_seconds"] == 86400

    # Default TTL
    result3 = await service.enable_caching("default")
    assert result3["ttl_seconds"] == 300
