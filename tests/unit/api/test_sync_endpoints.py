"""Comprehensive tests for Sync API endpoints.

Tests:
- GET /api/v1/projects/{project_id}/sync/status
- POST /api/v1/projects/{project_id}/sync
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import HTTP_OK


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


class TestSyncStatusEndpoint:
    """Test GET /api/v1/projects/{project_id}/sync/status endpoint."""

    @pytest.mark.asyncio
    async def test_get_sync_status_success(self, client: Any) -> None:
        """Test getting sync status returns correct data."""
        response = client.get("/api/v1/projects/proj-123/sync/status")

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["project_id"] == "proj-123"
        assert "status" in data
        assert "last_synced" in data
        assert "pending_changes" in data
        assert isinstance(data["pending_changes"], int)

    @pytest.mark.asyncio
    async def test_get_sync_status_response_structure(self, client: Any) -> None:
        """Test sync status response has expected structure."""
        response = client.get("/api/v1/projects/proj-123/sync/status")

        assert response.status_code == HTTP_OK
        data = response.json()
        assert isinstance(data, dict)
        assert "project_id" in data
        assert "status" in data
        assert "last_synced" in data
        assert "pending_changes" in data


class TestSyncExecuteEndpoint:
    """Test POST /api/v1/projects/{project_id}/sync endpoint."""

    @pytest.mark.asyncio
    async def test_sync_execute_success(self, client: Any) -> None:
        """Test executing sync returns correct data."""
        mock_sync_result = {"synced": True, "items_synced": 5, "links_synced": 3}

        with patch("tracertm.services.sync_service.SyncService") as mock_service:
            service_instance = MagicMock()
            service_instance.sync = AsyncMock(return_value=mock_sync_result)
            mock_service.return_value = service_instance

            response = client.post("/api/v1/projects/proj-123/sync")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["project_id"] == "proj-123"
            assert data["status"] == "synced"
            assert "result" in data
            assert data["result"]["synced"] is True

    @pytest.mark.asyncio
    async def test_sync_execute_response_structure(self, client: Any) -> None:
        """Test sync execute response has expected structure."""
        mock_sync_result = {"synced": True}

        with patch("tracertm.services.sync_service.SyncService") as mock_service:
            service_instance = MagicMock()
            service_instance.sync = AsyncMock(return_value=mock_sync_result)
            mock_service.return_value = service_instance

            response = client.post("/api/v1/projects/proj-123/sync")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "project_id" in data
            assert "status" in data
            assert "result" in data

    @pytest.mark.asyncio
    async def test_sync_execute_different_projects(self, client: Any) -> None:
        """Test sync works for different project IDs."""
        mock_sync_result = {"synced": True}

        with patch("tracertm.services.sync_service.SyncService") as mock_service:
            service_instance = MagicMock()
            service_instance.sync = AsyncMock(return_value=mock_sync_result)
            mock_service.return_value = service_instance

            # Test with different project IDs
            for project_id in ["proj-1", "proj-2", "proj-abc"]:
                response = client.post(f"/api/v1/projects/{project_id}/sync")
                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["project_id"] == project_id
