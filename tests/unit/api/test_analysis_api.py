"""Comprehensive tests for Analysis API endpoints.

Tests impact analysis, cycle detection, and shortest path finding.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO, HTTP_OK
from tracertm.api.main import app

client = TestClient(app)


class TestImpactAnalysis:
    """Test impact analysis endpoint."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_simple(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis with simple dependency chain."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            root_item_id="item1",
            total_affected=3,
            max_depth_reached=2,
            affected_items=["item2", "item3", "item4"],
        )

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/impact/item1?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["root_item_id"] == "item1"
            assert data["total_affected"] == COUNT_THREE
            assert data["max_depth"] == COUNT_TWO
            assert len(data["affected_items"]) == COUNT_THREE

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_large_chain(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis with large dependency chain."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        affected = [f"item{i}" for i in range(2, 102)]  # 100 items
        mock_result = MagicMock(
            root_item_id="item1",
            total_affected=100,
            max_depth_reached=10,
            affected_items=affected,
        )

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/impact/item1?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total_affected"] == 100
            assert len(data["affected_items"]) == 100

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_no_dependencies(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis for isolated item with no dependencies."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            root_item_id="item1",
            total_affected=0,
            max_depth_reached=0,
            affected_items=[],
        )

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/impact/item1?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total_affected"] == 0
            assert data["affected_items"] == []

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_missing_item_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis requires item_id parameter."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/analysis/impact/?project_id=proj1")
        # Should fail due to missing item_id in path
        assert response.status_code in {404, 422}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_missing_project_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis requires project_id parameter."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/analysis/impact/item1")
        # Should fail due to missing project_id
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_item_not_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis returns 404 for non-existent item."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.side_effect = Exception("Item not found")
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/impact/nonexistent?project_id=proj1")
            # The exception is caught and returns 404
            assert response.status_code in {404, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_with_special_item_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test impact analysis with special characters in item ID."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        special_id = "item-123_uuid.ext"
        mock_result = MagicMock(
            root_item_id=special_id,
            total_affected=2,
            max_depth_reached=1,
            affected_items=["item2", "item3"],
        )

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(f"/api/v1/analysis/impact/{special_id}?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["root_item_id"] == special_id


class TestCycleDetection:
    """Test cycle detection endpoint."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_detect_cycles_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test cycle detection finds cycles."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            has_cycles=True,
            total_cycles=2,
            severity="high",
            affected_items={"item1", "item2", "item3", "item4"},
        )

        with patch("tracertm.api.main.cycle_detection_service.CycleDetectionService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.detect_cycles.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/cycles/proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["has_cycles"] is True
            assert data["total_cycles"] == COUNT_TWO
            assert data["severity"] == "high"
            assert len(data["affected_items"]) == COUNT_FOUR

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_detect_cycles_not_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test cycle detection when no cycles exist."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            has_cycles=False,
            total_cycles=0,
            severity="none",
            affected_items=set(),
        )

        with patch("tracertm.api.main.cycle_detection_service.CycleDetectionService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.detect_cycles.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/cycles/proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["has_cycles"] is False
            assert data["total_cycles"] == 0
            assert data["severity"] == "none"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_detect_cycles_multiple_cycles(self, mock_auth: Any, mock_db: Any) -> None:
        """Test cycle detection with multiple cycles."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            has_cycles=True,
            total_cycles=5,
            severity="critical",
            affected_items={f"item{i}" for i in range(1, 11)},
        )

        with patch("tracertm.api.main.cycle_detection_service.CycleDetectionService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.detect_cycles.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/cycles/proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["has_cycles"] is True
            assert data["total_cycles"] == COUNT_FIVE
            assert data["severity"] == "critical"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_detect_cycles_severity_levels(self, mock_auth: Any, mock_db: Any) -> None:
        """Test cycle detection severity levels."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            mock_result = MagicMock(
                has_cycles=True,
                total_cycles=1,
                severity=severity,
                affected_items={"item1", "item2"},
            )

            with patch("tracertm.api.main.cycle_detection_service.CycleDetectionService") as mock_service_class:
                mock_service = MagicMock()
                mock_service.detect_cycles.return_value = mock_result
                mock_service_class.return_value = mock_service

                response = client.get("/api/v1/analysis/cycles/proj1")
                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["severity"] == severity

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_detect_cycles_missing_project_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test cycle detection requires project_id."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/analysis/cycles/")
        # Should fail due to missing project_id in path
        assert response.status_code in {404, 422}


class TestShortestPath:
    """Test shortest path finding endpoint."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_simple(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path with simple dependency chain."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            exists=True,
            distance=2,
            path=["item1", "item2", "item3"],
            link_types=["depends_on", "depends_on"],
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item3")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == COUNT_TWO
            assert len(data["path"]) == COUNT_THREE
            assert len(data["link_types"]) == COUNT_TWO

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_long_chain(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path with long dependency chain."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        path = [f"item{i}" for i in range(1, 11)]  # 10 items
        link_types = ["depends_on"] * 9  # 9 links

        mock_result = MagicMock(
            exists=True,
            distance=9,
            path=path,
            link_types=link_types,
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item10")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["distance"] == 9

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_not_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path when no path exists."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            exists=False,
            distance=None,
            path=[],
            link_types=[],
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item999")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is False
            assert data["distance"] is None
            assert data["path"] == []

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_direct_link(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path with direct link between items."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            exists=True,
            distance=1,
            path=["item1", "item2"],
            link_types=["depends_on"],
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item2")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == 1
            assert len(data["path"]) == COUNT_TWO

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_missing_source_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path requires source_id parameter."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&target_id=item2")
        # Missing source_id should cause an error
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_missing_target_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path requires target_id parameter."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1")
        # Missing target_id should cause an error
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_missing_project_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path requires project_id parameter."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/analysis/shortest-path?source_id=item1&target_id=item2")
        # Missing project_id should cause an error
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_multiple_link_types(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path with various link types."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            exists=True,
            distance=3,
            path=["item1", "item2", "item3", "item4"],
            link_types=["depends_on", "related_to", "blocks"],
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item4")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["link_types"] == ["depends_on", "related_to", "blocks"]

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_self_reference(self, mock_auth: Any, mock_db: Any) -> None:
        """Test shortest path from item to itself."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            exists=True,
            distance=0,
            path=["item1"],
            link_types=[],
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["distance"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
