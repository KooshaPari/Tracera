"""Comprehensive tests for Analysis API endpoints (expanded).

Tests:
- GET /api/v1/analysis/impact/{item_id}
- GET /api/v1/analysis/cycles/{project_id}
- GET /api/v1/analysis/shortest-path
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import (
    COUNT_FIVE,
    COUNT_FOUR,
    COUNT_TEN,
    COUNT_THREE,
    COUNT_TWO,
    HTTP_OK,
    HTTP_UNPROCESSABLE_ENTITY,
)


@pytest.fixture
def mock_config_manager() -> None:
    """Mock ConfigManager for testing."""
    with patch("tracertm.api.main.ConfigManager") as mock:
        manager = MagicMock()
        manager.get.return_value = "sqlite+aiosqlite:///test.db"
        mock.return_value = manager
        yield manager


@pytest.fixture
def mock_db_connection() -> None:
    """Mock DatabaseConnection for testing."""
    with patch("tracertm.api.main.DatabaseConnection") as mock:
        connection = MagicMock()
        session = MagicMock(spec=AsyncSession)
        session.close = AsyncMock()
        connection.session = session
        mock.return_value = connection
        yield connection


@pytest.fixture
def client(mock_config_manager: Any, _mock_db_connection: Any) -> None:
    """Create test client with mocked dependencies."""
    from tracertm.api.main import app

    return TestClient(app)


class TestImpactAnalysisEndpoint:
    """Test GET /api/v1/analysis/impact/{item_id} endpoint (expanded)."""

    @pytest.mark.asyncio
    async def test_impact_analysis_deep_hierarchy(self, client: Any) -> None:
        """Test impact analysis with deep dependency hierarchy."""
        mock_result = MagicMock(
            root_item_id="item-1",
            total_affected=10,
            max_depth_reached=5,
            affected_items=[
                "item-2",
                "item-3",
                "item-4",
                "item-5",
                "item-6",
                "item-7",
                "item-8",
                "item-9",
                "item-10",
                "item-11",
            ],
        )

        with patch("tracertm.services.impact_analysis_service.ImpactAnalysisService") as mock_service:
            service_instance = MagicMock()
            service_instance.analyze_impact = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/impact/item-1?project_id=test")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["root_item_id"] == "item-1"
            assert data["total_affected"] == COUNT_TEN
            assert data["max_depth"] == COUNT_FIVE
            assert len(data["affected_items"]) == COUNT_TEN

    @pytest.mark.asyncio
    async def test_impact_analysis_no_dependencies(self, client: Any) -> None:
        """Test impact analysis for item with no dependencies."""
        mock_result = MagicMock(
            root_item_id="item-1",
            total_affected=0,
            max_depth_reached=0,
            affected_items=[],
        )

        with patch("tracertm.services.impact_analysis_service.ImpactAnalysisService") as mock_service:
            service_instance = MagicMock()
            service_instance.analyze_impact = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/impact/item-1?project_id=test")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total_affected"] == 0
            assert data["max_depth"] == 0
            assert len(data["affected_items"]) == 0

    @pytest.mark.asyncio
    async def test_impact_analysis_single_level(self, client: Any) -> None:
        """Test impact analysis with single level of dependencies."""
        mock_result = MagicMock(
            root_item_id="item-1",
            total_affected=3,
            max_depth_reached=1,
            affected_items=["item-2", "item-3", "item-4"],
        )

        with patch("tracertm.services.impact_analysis_service.ImpactAnalysisService") as mock_service:
            service_instance = MagicMock()
            service_instance.analyze_impact = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/impact/item-1?project_id=test")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["max_depth"] == 1
            assert data["total_affected"] == COUNT_THREE


class TestCycleDetectionEndpoint:
    """Test GET /api/v1/analysis/cycles/{project_id} endpoint (expanded)."""

    @pytest.mark.asyncio
    async def test_cycle_detection_no_cycles(self, client: Any) -> None:
        """Test cycle detection for project with no cycles."""
        mock_result = MagicMock(
            has_cycles=False,
            total_cycles=0,
            severity="none",
            affected_items=set(),
        )

        with patch("tracertm.services.cycle_detection_service.CycleDetectionService") as mock_service:
            service_instance = MagicMock()
            service_instance.detect_cycles = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/cycles/test-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["has_cycles"] is False
            assert data["total_cycles"] == 0
            assert data["severity"] == "none"
            assert len(data["affected_items"]) == 0

    @pytest.mark.asyncio
    async def test_cycle_detection_multiple_cycles(self, client: Any) -> None:
        """Test cycle detection with multiple cycles."""
        mock_result = MagicMock(
            has_cycles=True,
            total_cycles=3,
            severity="high",
            affected_items={"item-1", "item-2", "item-3", "item-4", "item-5"},
        )

        with patch("tracertm.services.cycle_detection_service.CycleDetectionService") as mock_service:
            service_instance = MagicMock()
            service_instance.detect_cycles = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/cycles/test-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["has_cycles"] is True
            assert data["total_cycles"] == COUNT_THREE
            assert data["severity"] == "high"
            assert len(data["affected_items"]) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_cycle_detection_low_severity(self, client: Any) -> None:
        """Test cycle detection with low severity."""
        mock_result = MagicMock(
            has_cycles=True,
            total_cycles=1,
            severity="low",
            affected_items={"item-1", "item-2"},
        )

        with patch("tracertm.services.cycle_detection_service.CycleDetectionService") as mock_service:
            service_instance = MagicMock()
            service_instance.detect_cycles = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/cycles/test-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["severity"] == "low"
            assert data["total_cycles"] == 1


class TestShortestPathEndpoint:
    """Test GET /api/v1/analysis/shortest-path endpoint (expanded)."""

    @pytest.mark.asyncio
    async def test_shortest_path_no_path(self, client: Any) -> None:
        """Test shortest path when no path exists."""
        mock_result = MagicMock(
            exists=False,
            distance=-1,
            path=[],
            link_types=[],
        )

        with patch("tracertm.services.shortest_path_service.ShortestPathService") as mock_service:
            service_instance = MagicMock()
            service_instance.find_shortest_path = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/shortest-path?project_id=test&source_id=item-1&target_id=item-999")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is False
            assert data["distance"] == -1
            assert len(data["path"]) == 0

    @pytest.mark.asyncio
    async def test_shortest_path_direct_link(self, client: Any) -> None:
        """Test shortest path with direct link."""
        mock_result = MagicMock(
            exists=True,
            distance=1,
            path=["item-1", "item-2"],
            link_types=["implements"],
        )

        with patch("tracertm.services.shortest_path_service.ShortestPathService") as mock_service:
            service_instance = MagicMock()
            service_instance.find_shortest_path = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/shortest-path?project_id=test&source_id=item-1&target_id=item-2")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == 1
            assert len(data["path"]) == COUNT_TWO
            assert len(data["link_types"]) == 1

    @pytest.mark.asyncio
    async def test_shortest_path_multiple_hops(self, client: Any) -> None:
        """Test shortest path with multiple hops."""
        mock_result = MagicMock(
            exists=True,
            distance=4,
            path=["item-1", "item-2", "item-3", "item-4", "item-5"],
            link_types=["implements", "tests", "depends_on", "blocks"],
        )

        with patch("tracertm.services.shortest_path_service.ShortestPathService") as mock_service:
            service_instance = MagicMock()
            service_instance.find_shortest_path = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/shortest-path?project_id=test&source_id=item-1&target_id=item-5")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == COUNT_FOUR
            assert len(data["path"]) == COUNT_FIVE
            assert len(data["link_types"]) == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_shortest_path_same_source_target(self, client: Any) -> None:
        """Test shortest path with same source and target."""
        mock_result = MagicMock(
            exists=True,
            distance=0,
            path=["item-1"],
            link_types=[],
        )

        with patch("tracertm.services.shortest_path_service.ShortestPathService") as mock_service:
            service_instance = MagicMock()
            service_instance.find_shortest_path = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/shortest-path?project_id=test&source_id=item-1&target_id=item-1")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == 0
            assert len(data["path"]) == 1

    @pytest.mark.asyncio
    async def test_shortest_path_missing_parameters(self, client: Any) -> None:
        """Test shortest path with missing required parameters."""
        # Missing source_id
        response = client.get("/api/v1/analysis/shortest-path?project_id=test&target_id=item-2")
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY  # FastAPI validation error

        # Missing target_id
        response = client.get("/api/v1/analysis/shortest-path?project_id=test&source_id=item-1")
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY  # FastAPI validation error

        # Missing project_id
        response = client.get("/api/v1/analysis/shortest-path?source_id=item-1&target_id=item-2")
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY  # FastAPI validation error
