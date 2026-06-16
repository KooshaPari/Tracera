"""Targeted tests for performance optimizations on hot paths."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from tracertm.testing_factories import ItemFactoryConfig, create_item, create_link


@pytest.mark.asyncio
async def test_matrix_generate_fetches_items_once() -> None:
    """TraceabilityMatrixService should load project items in a single query."""
    from tracertm.services.traceability_matrix_service import TraceabilityMatrixService

    mock_session = MagicMock()
    service = TraceabilityMatrixService(mock_session)

    req = create_item(
        config=ItemFactoryConfig(title="Req 1", view="requirements", item_type="requirements"),
    )
    test_item = create_item(
        config=ItemFactoryConfig(title="Test 1", view="tests", item_type="tests"),
    )
    link = create_link(
        source_item_id=str(req.id),
        target_item_id=str(test_item.id),
        link_type="traces_to",
        project_id=str(req.project_id),
    )

    service.items.get_by_project = AsyncMock(return_value=[req, test_item])
    service.links.get_by_project = AsyncMock(return_value=[link])

    matrix = await service.generate_matrix(
        str(req.project_id),
        source_view="requirements",
        target_view="tests",
    )

    service.items.get_by_project.assert_awaited_once()
    assert len(matrix.rows) == 1
    assert len(matrix.columns) == 1
    assert matrix.matrix[0][0] == "traces_to"
    assert matrix.total_links == 1


@pytest.mark.asyncio
async def test_traceability_generate_matrix_uses_project_links() -> None:
    """TraceabilityService.generate_matrix should batch links via get_by_project."""
    from tracertm.services.traceability_service import TraceabilityService

    mock_session = MagicMock()
    service = TraceabilityService(mock_session)

    source = create_item(
        config=ItemFactoryConfig(title="Feature A", view="feature", item_type="feature"),
    )
    target = create_item(
        config=ItemFactoryConfig(title="Test A", view="test", item_type="test"),
    )
    link = create_link(
        source_item_id=str(source.id),
        target_item_id=str(target.id),
        link_type="tests",
        project_id=str(source.project_id),
    )

    service.items.get_by_view = AsyncMock(side_effect=[[source], [target]])
    service.links.get_by_project = AsyncMock(return_value=[link])
    service.links.get_by_source = AsyncMock()
    service.items.get_by_id = AsyncMock()

    matrix = await service.generate_matrix(
        str(source.project_id),
        source_view="feature",
        target_view="test",
    )

    service.links.get_by_project.assert_awaited_once()
    service.links.get_by_source.assert_not_awaited()
    service.items.get_by_id.assert_not_awaited()
    assert len(matrix.links) == 1
    assert matrix.links[0]["source_title"] == "Feature A"
    assert matrix.links[0]["target_title"] == "Test A"
    assert matrix.coverage_percentage == 100.0


@pytest.mark.asyncio
async def test_analyze_query_performance_uses_cache() -> None:
    """Repeated analyze_query_performance calls should not re-query the database."""
    from tracertm.services.query_optimization_service import QueryOptimizationService

    mock_session = MagicMock()
    service = QueryOptimizationService(mock_session)

    mock_items = [MagicMock(), MagicMock()]
    service.items.query = AsyncMock(return_value=mock_items)

    filters = {"status": "todo"}
    first = await service.analyze_query_performance("project-123", filters)
    second = await service.analyze_query_performance("project-123", filters)

    service.items.query.assert_awaited_once()
    assert first["items_returned"] == second["items_returned"] == 2
    assert first["execution_time_seconds"] >= 0
    assert second["execution_time_seconds"] == 0.0


def test_query_cache_key_is_stable() -> None:
    """Cache keys must be stable regardless of filter dict insertion order."""
    from tracertm.services.query_optimization_service import QueryOptimizationService

    key_a = QueryOptimizationService._query_cache_key("p1", {"status": "todo", "view": "feature"})
    key_b = QueryOptimizationService._query_cache_key("p1", {"view": "feature", "status": "todo"})
    assert key_a == key_b


@pytest.mark.asyncio
async def test_matrix_generate_1k_requirements_under_two_seconds() -> None:
    """PLAN target: RTM generation for ~1k requirements stays under 2s (in-process, mocked DB)."""
    from tracertm.services.traceability_matrix_service import TraceabilityMatrixService

    project_id = "proj-rtm-1k"
    mock_session = MagicMock()
    service = TraceabilityMatrixService(mock_session)

    requirements = [
        create_item(
            config=ItemFactoryConfig(
                title=f"Requirement {i}",
                view="requirements",
                item_type="requirements",
                project_id=project_id,
            ),
        )
        for i in range(1000)
    ]
    features = [
        create_item(
            config=ItemFactoryConfig(
                title=f"Feature {j}",
                view="feature",
                item_type="feature",
                project_id=project_id,
            ),
        )
        for j in range(10)
    ]
    links = [
        create_link(
            source_item_id=str(requirements[i].id),
            target_item_id=str(features[i % len(features)].id),
            link_type="traces_to",
            project_id=project_id,
        )
        for i in range(1000)
    ]

    service.items.get_by_project = AsyncMock(return_value=[*requirements, *features])
    service.links.get_by_project = AsyncMock(return_value=links)

    started = time.perf_counter()
    matrix = await service.generate_matrix(
        project_id,
        source_view="requirements",
        target_view="feature",
    )
    elapsed = time.perf_counter() - started

    service.items.get_by_project.assert_awaited_once()
    service.links.get_by_project.assert_awaited_once()
    assert len(matrix.rows) == 1000
    assert len(matrix.columns) == 10
    assert elapsed < 2.0
