"""Tests for missing PerformanceOptimizationService methods."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.performance_optimization_service import (
    PerformanceOptimizationService,
)



@pytest.mark.unit
@pytest.mark.asyncio
async def test_bulk_operation_optimization(db_session: AsyncSession):
    """Test bulk operation optimization."""
    service = PerformanceOptimizationService(db_session)

    result = await service.bulk_operation_optimization(
        project_id="proj1",
        batch_size=500
    )

    assert result["project_id"] == "proj1"
    assert result["recommended_batch_size"] == 500
    assert "optimization_tips" in result
    assert len(result["optimization_tips"]) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_bulk_operation_optimization_default_batch(db_session: AsyncSession):
    """Test bulk operation with default batch size."""
    service = PerformanceOptimizationService(db_session)

    result = await service.bulk_operation_optimization(project_id="proj1")

    assert result["recommended_batch_size"] == 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_index_optimization(db_session: AsyncSession):
    """Test index optimization."""
    service = PerformanceOptimizationService(db_session)

    result = await service.index_optimization(project_id="proj1")

    assert result["project_id"] == "proj1"
    assert "optimization_commands" in result
    assert len(result["optimization_commands"]) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_plan_analysis(db_session: AsyncSession):
    """Test query plan analysis."""
    service = PerformanceOptimizationService(db_session)

    query = "SELECT * FROM items WHERE project_id = 'proj1'"
    result = await service.query_plan_analysis(query)

    assert result["query"] == query
    assert "analysis" in result
    assert "recommendations" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_plan_analysis_complex_query(db_session: AsyncSession):
    """Test query plan analysis with complex query."""
    service = PerformanceOptimizationService(db_session)

    query = """
        SELECT i.*, l.* FROM items i
        LEFT JOIN links l ON i.id = l.source_item_id
        WHERE i.project_id = 'proj1' AND i.status = 'active'
    """
    result = await service.query_plan_analysis(query)

    assert result["query"] == query
    assert result["analysis"]["optimization_possible"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_optimization_report(db_session: AsyncSession):
    """Test getting comprehensive optimization report."""
    service = PerformanceOptimizationService(db_session)

    result = await service.get_optimization_report(project_id="proj1")

    assert result["project_id"] == "proj1"
    assert "query_optimization" in result
    assert "cache_stats" in result
    assert "bulk_operation_optimization" in result
    assert "index_optimization" in result
    assert "generated_at" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_optimization_report_multiple_projects(db_session: AsyncSession):
    """Test getting optimization reports for multiple projects."""
    service = PerformanceOptimizationService(db_session)

    for i in range(5):
        result = await service.get_optimization_report(project_id=f"proj{i}")

        assert result["project_id"] == f"proj{i}"
        assert "generated_at" in result
