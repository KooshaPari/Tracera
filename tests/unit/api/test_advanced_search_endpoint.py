"""Comprehensive tests for Advanced Search API endpoint.

Tests:
- POST /api/v1/projects/{project_id}/search/advanced
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO, HTTP_OK


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


class TestAdvancedSearchEndpoint:
    """Test POST /api/v1/projects/{project_id}/search/advanced endpoint."""

    @pytest.mark.asyncio
    async def test_advanced_search_with_query(self, client: Any) -> None:
        """Test advanced search with query parameter."""
        mock_results = [
            {"id": "item-1", "title": "Test Item", "view": "FEATURE"},
            {"id": "item-2", "title": "Another Item", "view": "FEATURE"},
        ]

        with patch("tracertm.services.search_service.SearchService") as mock_service:
            service_instance = MagicMock()
            service_instance.search = AsyncMock(return_value=mock_results)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/search/advanced",
                json={"query": "test"},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["project_id"] == "proj-123"
            assert data["query"] == "test"
            assert len(data["results"]) == COUNT_TWO
            assert data["total"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_advanced_search_with_filters(self, client: Any) -> None:
        """Test advanced search with filters."""
        mock_results = [
            {"id": "item-1", "title": "Test Item", "view": "FEATURE", "status": "todo"},
        ]

        with patch("tracertm.services.search_service.SearchService") as mock_service:
            service_instance = MagicMock()
            service_instance.search = AsyncMock(return_value=mock_results)
            mock_service.return_value = service_instance

            filters = {"view": "FEATURE", "status": "todo"}
            response = client.post(
                "/api/v1/projects/proj-123/search/advanced",
                json={"filters": filters},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["project_id"] == "proj-123"
            assert len(data["results"]) == 1

    @pytest.mark.asyncio
    async def test_advanced_search_with_query_and_filters(self, client: Any) -> None:
        """Test advanced search with both query and filters."""
        mock_results = [
            {"id": "item-1", "title": "Test Item", "view": "FEATURE"},
        ]

        with patch("tracertm.services.search_service.SearchService") as mock_service:
            service_instance = MagicMock()
            service_instance.search = AsyncMock(return_value=mock_results)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/search/advanced",
                json={"query": "test", "filters": {"view": "FEATURE"}},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["query"] == "test"
            assert len(data["results"]) == 1

    @pytest.mark.asyncio
    async def test_advanced_search_empty_results(self, client: Any) -> None:
        """Test advanced search returns empty results when no matches."""
        mock_results = []

        with patch("tracertm.services.search_service.SearchService") as mock_service:
            service_instance = MagicMock()
            service_instance.search = AsyncMock(return_value=mock_results)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/search/advanced",
                json={"query": "nonexistent"},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert len(data["results"]) == 0
            assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_advanced_search_no_query_no_filters(self, client: Any) -> None:
        """Test advanced search with no query or filters."""
        mock_results = [
            {"id": "item-1", "title": "Item 1"},
            {"id": "item-2", "title": "Item 2"},
        ]

        with patch("tracertm.services.search_service.SearchService") as mock_service:
            service_instance = MagicMock()
            service_instance.search = AsyncMock(return_value=mock_results)
            mock_service.return_value = service_instance

            response = client.post("/api/v1/projects/proj-123/search/advanced", json={})

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["query"] is None
            assert len(data["results"]) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_advanced_search_response_structure(self, client: Any) -> None:
        """Test advanced search response has expected structure."""
        mock_results = [{"id": "item-1", "title": "Test"}]

        with patch("tracertm.services.search_service.SearchService") as mock_service:
            service_instance = MagicMock()
            service_instance.search = AsyncMock(return_value=mock_results)
            mock_service.return_value = service_instance

            response = client.post("/api/v1/projects/proj-123/search/advanced", json={})

            assert response.status_code == HTTP_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "project_id" in data
            assert "query" in data
            assert "filters" in data
            assert "results" in data
            assert "total" in data
            assert isinstance(data["results"], list)
