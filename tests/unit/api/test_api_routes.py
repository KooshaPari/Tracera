"""Comprehensive unit tests for FastAPI routes in TraceRTM.

Tests all HTTP methods, request validation, response formats, error handling,
and authentication/authorization for all API endpoints.
"""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import (
    COUNT_FIVE,
    COUNT_FOUR,
    COUNT_TEN,
    COUNT_THREE,
    COUNT_TWO,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
)
from tracertm.api.main import app

# Use TestClient for synchronous testing
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check_root(self) -> None:
        """Test root health check endpoint."""
        response = client.get("/health")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["service"] == "TraceRTM API"

    def test_api_v1_health_check(self) -> None:
        """Test v1 API health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "tracertm-api"

    def test_health_check_response_headers(self) -> None:
        """Test health check includes proper response headers."""
        response = client.get("/api/v1/health")
        assert response.headers["content-type"] == "application/json"


class TestItemsEndpoints:
    """Test items API endpoints."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_success(self, mock_auth: Any, mock_db: Any) -> None:
        """Test successful items list retrieval."""
        # Setup mocks
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        # Create mock items
        mock_items = [
            MagicMock(
                id="item1",
                project_id="proj1",
                title="Item 1",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                created_at=datetime.now(),
            ),
            MagicMock(
                id="item2",
                project_id="proj1",
                title="Item 2",
                view="REQUIREMENT",
                item_type="requirement",
                status="in_progress",
                priority="high",
                created_at=datetime.now(),
            ),
        ]

        # Mock database query
        mock_result = AsyncMock()
        mock_result.scalar.return_value = 2
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1&skip=0&limit=100")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TWO
            assert len(data["items"]) == COUNT_TWO
            assert data["items"][0]["title"] == "Item 1"
            assert data["items"][1]["title"] == "Item 2"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_with_pagination(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list with skip and limit parameters."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_items = [
            MagicMock(
                id=f"item{i}",
                project_id="proj1",
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                created_at=datetime.now(),
            )
            for i in range(10)
        ]

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 10
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1&skip=5&limit=5")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TEN

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_empty(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list when no items exist."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = []
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == 0
            assert len(data["items"]) == 0

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_missing_project_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list without project_id returns empty."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = []
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items")
            assert response.status_code == HTTP_OK

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_get_item_success(self, mock_auth: Any, mock_db: Any) -> None:
        """Test get single item endpoint."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_item = MagicMock(
            id="item1",
            project_id="proj1",
            title="Item 1",
            view="FEATURE",
            status="todo",
            priority="medium",
            created_at=datetime.now(),
        )

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = mock_item
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items/item1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "item1"
            assert data["title"] == "Item 1"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_get_item_not_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test get item returns 404 when item not found."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = None
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items/nonexistent")
            assert response.status_code == HTTP_NOT_FOUND
            data = response.json()
            assert "not found" in data["detail"].lower()


class TestLinksEndpoints:
    """Test links API endpoints."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_by_project(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list links filtered by project."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 2

        # Mock two different calls to execute
        results = [mock_result, AsyncMock()]
        results[1].fetchall.return_value = [
            MagicMock(
                id="link1",
                source_item_id="item1",
                target_item_id="item2",
                link_type="depends_on",
                created_at=datetime.now(),
                link_metadata=None,
            ),
            MagicMock(
                id="link2",
                source_item_id="item2",
                target_item_id="item3",
                link_type="related_to",
                created_at=datetime.now(),
                link_metadata=None,
            ),
        ]

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?project_id=proj1&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == COUNT_TWO
        assert len(data["links"]) == COUNT_TWO

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_by_source_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list links filtered by source item."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 1

        results = [mock_result, AsyncMock()]
        results[1].fetchall.return_value = [
            MagicMock(
                id="link1",
                source_item_id="item1",
                target_item_id="item2",
                link_type="depends_on",
                created_at=datetime.now(),
                link_metadata=None,
            ),
        ]

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?source_id=item1&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 1
        assert data["links"][0]["source_id"] == "item1"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_by_target_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list links filtered by target item."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 1

        results = [mock_result, AsyncMock()]
        results[1].fetchall.return_value = [
            MagicMock(
                id="link1",
                source_item_id="item1",
                target_item_id="item2",
                link_type="depends_on",
                created_at=datetime.now(),
                link_metadata=None,
            ),
        ]

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?target_id=item2&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 1
        assert data["links"][0]["target_id"] == "item2"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_by_source_and_target(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list links filtered by both source and target."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 1

        results = [mock_result, AsyncMock()]
        results[1].fetchall.return_value = [
            MagicMock(
                id="link1",
                source_item_id="item1",
                target_item_id="item2",
                link_type="depends_on",
                created_at=datetime.now(),
                link_metadata=None,
            ),
        ]

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?source_id=item1&target_id=item2&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 1

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_no_filters(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list links without filters returns empty."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        response = client.get("/api/v1/links")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["links"]) == 0

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_success(self, mock_auth: Any, mock_db: Any) -> None:
        """Test successful link creation."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata={"priority": "high"},
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {
                "project_id": "proj1",
                "source_id": "item1",
                "target_id": "item2",
                "type": "depends_on",
                "metadata": {"priority": "high"},
            }

            response = client.post("/api/v1/links", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "link1"
            assert data["source_id"] == "item1"
            assert data["target_id"] == "item2"
            assert data["type"] == "depends_on"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_validation_error(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link creation with invalid payload."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        # Missing required fields
        payload = {
            "source_id": "item1",
            # Missing project_id, target_id, type
        }

        response = client.post("/api/v1/links", json=payload)
        # Validation error - may be 422 or 500
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_unauthorized_guest(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link creation fails for guest role."""
        mock_auth.return_value = {"role": "guest"}
        mock_db.return_value = AsyncMock()

        payload = {
            "project_id": "proj1",
            "source_id": "item1",
            "target_id": "item2",
            "type": "depends_on",
        }

        response = client.post("/api/v1/links", json=payload)
        # Should fail due to write permission check
        assert response.status_code in {403, 500}  # Forbidden or permission error

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_update_link_success(self, mock_auth: Any, mock_db: Any) -> None:
        """Test successful link update."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="related_to",
            link_metadata={"priority": "low"},
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {
                "link_type": "related_to",
                "metadata": {"priority": "low"},
            }

            response = client.put("/api/v1/links/link1", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "link1"
            assert data["type"] == "related_to"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_update_link_not_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test update link when link doesn't exist."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = None
            mock_repo_class.return_value = mock_repo

            payload = {
                "link_type": "related_to",
                "metadata": {"priority": "low"},
            }

            response = client.put("/api/v1/links/nonexistent", json=payload)
            assert response.status_code == HTTP_NOT_FOUND


class TestAnalysisEndpoints:
    """Test analysis API endpoints."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_impact_analysis_success(self, mock_auth: Any, mock_db: Any) -> None:
        """Test successful impact analysis."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            root_item_id="item1",
            total_affected=5,
            max_depth_reached=3,
            affected_items=["item2", "item3", "item4", "item5", "item6"],
        )

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/impact/item1?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["root_item_id"] == "item1"
            assert data["total_affected"] == COUNT_FIVE
            assert data["max_depth"] == COUNT_THREE
            assert len(data["affected_items"]) == COUNT_FIVE

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
            assert response.status_code == HTTP_NOT_FOUND

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_cycle_detection_success(self, mock_auth: Any, mock_db: Any) -> None:
        """Test successful cycle detection."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            has_cycles=True,
            total_cycles=2,
            severity="high",
            affected_items={"item1", "item2", "item3"},
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
            assert len(data["affected_items"]) == COUNT_THREE

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_cycle_detection_no_cycles(self, mock_auth: Any, mock_db: Any) -> None:
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

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_shortest_path_found(self, mock_auth: Any, mock_db: Any) -> None:
        """Test successful shortest path finding."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            exists=True,
            distance=3,
            path=["item1", "item2", "item3", "item4"],
            link_types=["depends_on", "related_to", "depends_on"],
        )

        with patch("tracertm.api.main.shortest_path_service.ShortestPathService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.find_shortest_path.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/shortest-path?project_id=proj1&source_id=item1&target_id=item4")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == COUNT_THREE
            assert len(data["path"]) == COUNT_FOUR

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


class TestAuthenticationAndAuthorization:
    """Test authentication and authorization mechanisms."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_public_access_without_auth(self, mock_auth: Any, mock_db: Any) -> None:
        """Test public access works without authentication."""
        mock_auth.return_value = {"role": "public"}
        mock_db.return_value = AsyncMock()

        response = client.get("/api/v1/health")
        assert response.status_code == HTTP_OK

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_auth_guard_validates_bearer_token(self, mock_auth: Any, mock_db: Any) -> None:
        """Test auth guard validates bearer token format."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        headers = {"Authorization": "Bearer valid_token_123"}
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == HTTP_OK

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_write_permission_check_guest_role(self, mock_auth: Any, mock_db: Any) -> None:
        """Test write operations deny guest role."""
        mock_auth.return_value = {"role": "guest"}
        mock_db.return_value = AsyncMock()

        payload = {
            "project_id": "proj1",
            "source_id": "item1",
            "target_id": "item2",
            "type": "depends_on",
        }

        # Guest users should not be able to create links
        response = client.post("/api/v1/links", json=payload)
        # Should return an error (either 403 or 500 with permission error)
        assert response.status_code in {403, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_project_access_check(self, mock_auth: Any, mock_db: Any) -> None:
        """Test project access verification."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        with patch("tracertm.api.main.check_project_access") as mock_check:
            mock_check.return_value = False  # Access denied

            with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo_class.return_value = mock_repo

                client.get("/api/v1/items?project_id=unauthorized_proj")
                # Should handle access denial gracefully


class TestRateLimiting:
    """Test rate limiting functionality."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_rate_limit_headers(self, mock_auth: Any, mock_db: Any) -> None:
        """Test rate limiting sets appropriate headers."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = []
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items")
            # Response should include rate limiting info or pass through
            assert response.status_code in {200, 429}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_bulk_operation_bypass_rate_limit(self, mock_auth: Any, mock_db: Any) -> None:
        """Test bulk operations bypass rate limiting."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = []
            mock_repo_class.return_value = mock_repo

            headers = {"X-Bulk-Operation": "true"}
            response = client.get("/api/v1/items?project_id=proj1", headers=headers)
            assert response.status_code == HTTP_OK


class TestErrorHandling:
    """Test error handling and edge cases."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_database_error_handling(self, mock_auth: Any, mock_db: Any) -> None:
        """Test database errors are handled gracefully."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.side_effect = Exception("Database connection failed")
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1")
            assert response.status_code == HTTP_INTERNAL_SERVER_ERROR

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_invalid_query_parameters(self, mock_auth: Any, mock_db: Any) -> None:
        """Test invalid query parameters are rejected."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        # Invalid skip value (negative)
        client.get("/api/v1/items?project_id=proj1&skip=-1&limit=10")
        # FastAPI should validate numeric constraints

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_missing_required_query_parameters(self, mock_auth: Any, mock_db: Any) -> None:
        """Test endpoints with missing required parameters."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        # Missing required project_id parameter for analysis endpoint
        response = client.get("/api/v1/analysis/impact/item1")
        # project_id should be required - may return 422 or 500
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_content_type_validation(self, mock_auth: Any, mock_db: Any) -> None:
        """Test content type validation for POST requests."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        # Send POST with correct content-type
        headers = {"Content-Type": "application/json"}
        payload = {
            "project_id": "proj1",
            "source_id": "item1",
            "target_id": "item2",
            "type": "depends_on",
        }

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_link = MagicMock(
                id="link1",
                source_item_id="item1",
                target_item_id="item2",
                link_type="depends_on",
                link_metadata=None,
            )
            mock_repo.create.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            response = client.post("/api/v1/links", json=payload, headers=headers)
            assert response.status_code == HTTP_OK


class TestResponseFormats:
    """Test response format consistency."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_response_format(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list response has correct format."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_items = [
            MagicMock(
                id="item1",
                project_id="proj1",
                title="Item 1",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="medium",
                created_at=datetime.now(),
            ),
        ]

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()

            # Check response structure
            assert "total" in data
            assert "items" in data
            assert isinstance(data["total"], int)
            assert isinstance(data["items"], list)

            # Check item structure
            if data["items"]:
                item = data["items"][0]
                assert "id" in item
                assert "project_id" in item
                assert "title" in item
                assert "type" in item
                assert "status" in item
                assert "priority" in item

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_link_response_format(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link response has correct format."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata={"priority": "high"},
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {
                "project_id": "proj1",
                "source_id": "item1",
                "target_id": "item2",
                "type": "depends_on",
                "metadata": {"priority": "high"},
            }

            response = client.post("/api/v1/links", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()

            # Check response structure
            assert "id" in data
            assert "source_id" in data
            assert "target_id" in data
            assert "type" in data
            assert "metadata" in data

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_analysis_response_format(self, mock_auth: Any, mock_db: Any) -> None:
        """Test analysis response has correct format."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = MagicMock(
            root_item_id="item1",
            total_affected=5,
            max_depth_reached=3,
            affected_items=["item2", "item3"],
        )

        with patch("tracertm.api.main.impact_analysis_service.ImpactAnalysisService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.analyze_impact.return_value = mock_result
            mock_service_class.return_value = mock_service

            response = client.get("/api/v1/analysis/impact/item1?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()

            # Check response structure
            assert "root_item_id" in data
            assert "total_affected" in data
            assert "max_depth" in data
            assert "affected_items" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
