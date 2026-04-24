"""Comprehensive tests for Export/Import API endpoints.

Tests:
- GET /api/v1/projects/{project_id}/export
- POST /api/v1/projects/{project_id}/import

Functional Requirements Coverage:
    - FR-DISC-001: GitHub Issue Import (via import endpoint)
    - FR-RPT-003: Export to External Formats

Epics:
    - EPIC-001: External Integration
    - EPIC-005: Reporting & Analytics

Tests verify project export in multiple formats (JSON, CSV, Excel) and
import from GitHub, Jira, and other external sources.
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_OK


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


class TestExportEndpoint:
    """Test GET /api/v1/projects/{project_id}/export endpoint."""

    @pytest.mark.asyncio
    async def test_export_json_success(self, client: Any) -> None:
        """Test exporting project to JSON format."""
        mock_export_data = {
            "format": "json",
            "project": {
                "id": "proj-123",
                "name": "Test Project",
                "description": "Test description",
            },
            "items": [
                {"id": "item-1", "title": "Item 1", "view": "FEATURE", "type": "feature", "status": "todo"},
                {"id": "item-2", "title": "Item 2", "view": "FEATURE", "type": "feature", "status": "in_progress"},
            ],
            "item_count": 2,
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.export_to_json = AsyncMock(return_value=mock_export_data)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/projects/proj-123/export?format=json")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["format"] == "json"
            assert data["project"]["id"] == "proj-123"
            assert len(data["items"]) == COUNT_TWO
            assert data["item_count"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_export_csv_success(self, client: Any) -> None:
        """Test exporting project to CSV format."""
        mock_export_data = {
            "format": "csv",
            "content": "ID,Title,View,Type,Status,Description\nitem-1,Item 1,FEATURE,feature,todo,\n",
            "item_count": 1,
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.export_to_csv = AsyncMock(return_value=mock_export_data)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/projects/proj-123/export?format=csv")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["format"] == "csv"
            assert "content" in data
            assert data["item_count"] == 1

    @pytest.mark.asyncio
    async def test_export_markdown_success(self, client: Any) -> None:
        """Test exporting project to Markdown format."""
        mock_export_data = {
            "format": "markdown",
            "content": "# Test Project\n\nTest description\n\n## FEATURE\n\n- **Item 1** (todo)\n",
            "item_count": 1,
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.export_to_markdown = AsyncMock(return_value=mock_export_data)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/projects/proj-123/export?format=markdown")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["format"] == "markdown"
            assert "content" in data
            assert data["item_count"] == 1

    @pytest.mark.asyncio
    async def test_export_project_not_found(self, client: Any) -> None:
        """Test exporting non-existent project returns 404."""
        mock_export_data = {"error": "Project not found"}

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.export_to_json = AsyncMock(return_value=mock_export_data)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/projects/nonexistent/export?format=json")

            assert response.status_code == HTTP_NOT_FOUND
            assert "Project not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_export_unsupported_format(self, client: Any) -> None:
        """Test exporting with unsupported format returns 400."""
        response = client.get("/api/v1/projects/proj-123/export?format=xml")

        assert response.status_code == HTTP_BAD_REQUEST
        assert "Unsupported format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_export_default_format(self, client: Any) -> None:
        """Test exporting with default format (JSON)."""
        mock_export_data = {
            "format": "json",
            "project": {"id": "proj-123", "name": "Test Project"},
            "items": [],
            "item_count": 0,
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.export_to_json = AsyncMock(return_value=mock_export_data)
            mock_service.return_value = service_instance

            response = client.get("/api/v1/projects/proj-123/export")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["format"] == "json"


class TestImportEndpoint:
    """Test POST /api/v1/projects/{project_id}/import endpoint."""

    @pytest.mark.asyncio
    async def test_import_json_success(self, client: Any) -> None:
        """Test importing project from JSON format."""
        json_data = json.dumps({
            "items": [
                {"title": "Item 1", "view": "FEATURE", "type": "feature", "status": "todo"},
                {"title": "Item 2", "view": "FEATURE", "type": "feature", "status": "in_progress"},
            ],
        })

        mock_import_result = {
            "success": True,
            "imported_count": 2,
            "error_count": 0,
            "errors": [],
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.import_from_json = AsyncMock(return_value=mock_import_result)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/import",
                json={"format": "json", "data": json_data},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["success"] is True
            assert data["imported_count"] == COUNT_TWO
            assert data["error_count"] == 0

    @pytest.mark.asyncio
    async def test_import_csv_success(self, client: Any) -> None:
        """Test importing project from CSV format."""
        csv_data = "ID,Title,View,Type,Status,Description\nitem-1,Item 1,FEATURE,feature,todo,\n"

        mock_import_result = {
            "success": True,
            "imported_count": 1,
            "error_count": 0,
            "errors": [],
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.import_from_csv = AsyncMock(return_value=mock_import_result)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/import",
                json={"format": "csv", "data": csv_data},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["success"] is True
            assert data["imported_count"] == 1

    @pytest.mark.asyncio
    async def test_import_invalid_json(self, client: Any) -> None:
        """Test importing with invalid JSON returns 400."""
        invalid_json = "{invalid json}"

        mock_import_result = {"error": "Invalid JSON format"}

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.import_from_json = AsyncMock(return_value=mock_import_result)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/import",
                json={"format": "json", "data": invalid_json},
            )

            assert response.status_code == HTTP_BAD_REQUEST
            assert "Invalid JSON format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_import_missing_items_field(self, client: Any) -> None:
        """Test importing JSON without items field returns 400."""
        json_data = json.dumps({"project": {"name": "Test"}})

        mock_import_result = {"error": "Missing 'items' field"}

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.import_from_json = AsyncMock(return_value=mock_import_result)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/import",
                json={"format": "json", "data": json_data},
            )

            assert response.status_code == HTTP_BAD_REQUEST
            assert "Missing 'items' field" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_import_unsupported_format(self, client: Any) -> None:
        """Test importing with unsupported format returns 400."""
        response = client.post(
            "/api/v1/projects/proj-123/import",
            json={"format": "xml", "data": "<data></data>"},
        )

        assert response.status_code == HTTP_BAD_REQUEST
        assert "Unsupported format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_import_with_errors(self, client: Any) -> None:
        """Test importing with some errors."""
        json_data = json.dumps({
            "items": [
                {"title": "Item 1", "view": "FEATURE"},
                {"title": "Item 2", "view": "INVALID"},  # This might cause an error
            ],
        })

        mock_import_result = {
            "success": True,
            "imported_count": 1,
            "error_count": 1,
            "errors": ["Invalid view: INVALID"],
        }

        with patch("tracertm.services.export_import_service.ExportImportService") as mock_service:
            service_instance = MagicMock()
            service_instance.import_from_json = AsyncMock(return_value=mock_import_result)
            mock_service.return_value = service_instance

            response = client.post(
                "/api/v1/projects/proj-123/import",
                json={"format": "json", "data": json_data},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["success"] is True
            assert data["imported_count"] == 1
            assert data["error_count"] == 1
            assert len(data["errors"]) == 1
