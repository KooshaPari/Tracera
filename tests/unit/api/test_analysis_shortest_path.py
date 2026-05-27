"""Tests for analysis shortest-path API."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO, HTTP_OK
from tracertm.api.main import app

client = TestClient(app)


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

        with patch(
            "tracertm.api.main.shortest_path_service.ShortestPathService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(
                "/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item3"
            )
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

        with patch(
            "tracertm.api.main.shortest_path_service.ShortestPathService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(
                "/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item10"
            )
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

        with patch(
            "tracertm.api.main.shortest_path_service.ShortestPathService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(
                "/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item999"
            )
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

        with patch(
            "tracertm.api.main.shortest_path_service.ShortestPathService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(
                "/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item2"
            )
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

        with patch(
            "tracertm.api.main.shortest_path_service.ShortestPathService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(
                "/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item4"
            )
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

        with patch(
            "tracertm.api.main.shortest_path_service.ShortestPathService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get(
                "/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item1"
            )
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["distance"] == 0
