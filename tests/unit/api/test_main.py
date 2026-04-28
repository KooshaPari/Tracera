"""Comprehensive tests for tracertm.api.main module.

Tests FastAPI application setup, endpoints, middleware, and error handling.
Coverage target: 80%+ of 59 statements
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
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_OK,
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


class TestAppInitialization:
    """Test FastAPI application initialization and configuration."""

    def test_app_metadata(self) -> None:
        """Test app has correct metadata."""
        from tracertm.api.main import app

        assert app.title == "TraceRTM API"
        assert app.description == "Traceability Requirements Tracking Management API"
        assert app.version == "1.0.0"

    def test_cors_middleware_configured(self) -> None:
        """Test CORS middleware is properly configured."""
        from tracertm.api.main import app

        # Find CORS middleware in the middleware stack
        middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                middleware_found = True
                # Verify CORS settings
                assert middleware.kwargs.get("allow_origins") == ["*"]
                assert middleware.kwargs.get("allow_credentials") is True
                assert middleware.kwargs.get("allow_methods") == ["*"]
                assert middleware.kwargs.get("allow_headers") == ["*"]
                break

        assert middleware_found, "CORS middleware not found"


class TestHealthCheckEndpoint:
    """Test health check endpoint functionality."""

    def test_health_check_success(self, client: Any) -> None:
        """Test health check returns correct status."""
        response = client.get("/health")

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["service"] == "TraceRTM API"

    def test_health_check_response_format(self, client: Any) -> None:
        """Test health check response has expected structure."""
        response = client.get("/health")
        data = response.json()

        assert isinstance(data, dict)
        assert "status" in data
        assert "version" in data
        assert "service" in data


class TestDatabaseDependency:
    """Test database session dependency injection."""

    @pytest.mark.asyncio
    async def test_get_db_success(self) -> None:
        """Test get_db creates and yields session successfully."""
        from tracertm.api.main import get_db

        with patch("tracertm.api.main.ConfigManager") as mock_config:
            with patch("tracertm.api.main.DatabaseConnection") as mock_db:
                # Setup mocks
                config_manager = MagicMock()
                config_manager.get.return_value = "sqlite+aiosqlite:///test.db"
                mock_config.return_value = config_manager

                db_conn = MagicMock()
                session = MagicMock(spec=AsyncSession)
                session.close = AsyncMock()
                db_conn.session = session
                db_conn.connect = MagicMock()
                mock_db.return_value = db_conn

                # Execute generator
                gen = get_db()
                yielded_session = await anext(gen)

                # Assertions
                assert yielded_session == session
                db_conn.connect.assert_called_once()

                # Cleanup
                try:
                    await anext(gen)
                except StopAsyncIteration:
                    pass
                session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_no_database_configured(self) -> None:
        """Test get_db raises HTTPException when database not configured."""
        from fastapi import HTTPException

        from tracertm.api.main import get_db

        with patch("tracertm.api.main.ConfigManager") as mock_config:
            # Setup config to return None
            config_manager = MagicMock()
            config_manager.get.return_value = None
            mock_config.return_value = config_manager

            # Should raise HTTPException
            gen = get_db()
            with pytest.raises(HTTPException) as exc_info:
                await anext(gen)

            assert exc_info.value.status_code == HTTP_INTERNAL_SERVER_ERROR
            assert "Database not configured" in exc_info.value.detail


class TestItemsEndpoints:
    """Test /api/v1/items endpoints."""

    @pytest.mark.asyncio
    async def test_list_items_success(self, client: Any) -> None:
        """Test listing items returns correct data."""
        mock_items = [
            MagicMock(id="item-1", title="Test Item 1", view="FEATURE", status="todo"),
            MagicMock(id="item-2", title="Test Item 2", view="FEATURE", status="in_progress"),
        ]

        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_project = AsyncMock(return_value=mock_items)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/items?project_id=test-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TWO
            assert len(data["items"]) == COUNT_TWO
            assert data["items"][0]["id"] == "item-1"
            assert data["items"][0]["title"] == "Test Item 1"

    @pytest.mark.asyncio
    async def test_list_items_pagination(self, client: Any) -> None:
        """Test items list respects skip and limit parameters."""
        mock_items = [MagicMock(id=f"item-{i}", title=f"Item {i}", view="FEATURE", status="todo") for i in range(10)]

        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_project = AsyncMock(return_value=mock_items)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/items?project_id=test&skip=2&limit=3")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TEN
            assert len(data["items"]) == COUNT_THREE  # Limited to 3
            assert data["items"][0]["id"] == "item-2"  # Skipped 2

    @pytest.mark.asyncio
    async def test_get_item_success(self, client: Any) -> None:
        """Test getting single item by ID."""
        from datetime import datetime

        mock_item = MagicMock(
            id="item-123",
            title="Test Item",
            description="Test description",
            view="FEATURE",
            status="todo",
            created_at=datetime(2024, 1, 1, 12, 0),
            updated_at=datetime(2024, 1, 2, 12, 0),
        )

        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=mock_item)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/items/item-123")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "item-123"
            assert data["title"] == "Test Item"
            assert data["description"] == "Test description"
            assert "created_at" in data
            assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, client: Any) -> None:
        """Test getting non-existent item returns 404."""
        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/items/nonexistent")

            assert response.status_code == HTTP_NOT_FOUND
            assert "Item not found" in response.json()["detail"]


class TestLinksEndpoints:
    """Test /api/v1/links endpoints."""

    @pytest.mark.asyncio
    async def test_list_links_success(self, client: Any) -> None:
        """Test listing links returns correct data."""
        mock_links = [
            MagicMock(id="link-1", source_item_id="item-1", target_item_id="item-2", link_type="implements"),
            MagicMock(id="link-2", source_item_id="item-2", target_item_id="item-3", link_type="tests"),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_project = AsyncMock(return_value=mock_links)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/links?project_id=test-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TWO
            assert len(data["links"]) == COUNT_TWO
            assert data["links"][0]["type"] == "implements"


class TestAnalysisEndpoints:
    """Test /api/v1/analysis endpoints."""

    @pytest.mark.asyncio
    async def test_impact_analysis_success(self, client: Any) -> None:
        """Test impact analysis endpoint."""
        mock_result = MagicMock(
            root_item_id="item-1",
            total_affected=5,
            max_depth_reached=3,
            affected_items=["item-2", "item-3", "item-4"],
        )

        with patch("tracertm.services.impact_analysis_service.ImpactAnalysisService") as mock_service:
            service_instance = MagicMock()
            service_instance.analyze_impact = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/impact/item-1?project_id=test")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["root_item_id"] == "item-1"
            assert data["total_affected"] == COUNT_FIVE
            assert data["max_depth"] == COUNT_THREE

    @pytest.mark.asyncio
    async def test_cycle_detection_success(self, client: Any) -> None:
        """Test cycle detection endpoint."""
        mock_result = MagicMock(
            has_cycles=True,
            total_cycles=2,
            severity="high",
            affected_items={"item-1", "item-2", "item-3"},
        )

        with patch("tracertm.services.cycle_detection_service.CycleDetectionService") as mock_service:
            service_instance = MagicMock()
            service_instance.detect_cycles = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/cycles/test-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["has_cycles"] is True
            assert data["total_cycles"] == COUNT_TWO
            assert data["severity"] == "high"

    @pytest.mark.asyncio
    async def test_shortest_path_success(self, client: Any) -> None:
        """Test shortest path endpoint."""
        mock_result = MagicMock(
            exists=True,
            distance=3,
            path=["item-1", "item-2", "item-3", "item-4"],
            link_types=["implements", "tests", "depends_on"],
        )

        with patch("tracertm.services.shortest_path_service.ShortestPathService") as mock_service:
            service_instance = MagicMock()
            service_instance.find_shortest_path = AsyncMock(return_value=mock_result)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/analysis/shortest-path?project_id=test&source_id=item-1&target_id=item-4")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["exists"] is True
            assert data["distance"] == COUNT_THREE
            assert len(data["path"]) == COUNT_FOUR


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_endpoint_returns_404(self, client: Any) -> None:
        """Test accessing invalid endpoint returns 404."""
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == HTTP_NOT_FOUND

    @pytest.mark.asyncio
    async def test_database_error_handling(self, client: Any) -> None:
        """Test database errors are handled gracefully."""
        with patch("tracertm.repositories.item_repository.ItemRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_project = AsyncMock(side_effect=Exception("Database connection failed"))
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/items?project_id=test")

            # Should return 500 error
            assert response.status_code == HTTP_INTERNAL_SERVER_ERROR
