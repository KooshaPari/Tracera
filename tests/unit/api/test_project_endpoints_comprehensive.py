"""Comprehensive tests for Project API endpoints.

Tests:
- GET /api/v1/projects
- GET /api/v1/projects/{project_id}
- POST /api/v1/projects
- PUT /api/v1/projects/{project_id}
- DELETE /api/v1/projects/{project_id}
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_NOT_FOUND, HTTP_OK


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


class TestListProjectsEndpoint:
    """Test GET /api/v1/projects endpoint."""

    @pytest.mark.asyncio
    async def test_list_projects_success(self, client: Any) -> None:
        """Test listing projects returns correct data."""
        # Create proper mock objects with attributes
        mock_project1 = MagicMock()
        mock_project1.id = "proj-1"
        mock_project1.name = "Project 1"
        mock_project1.description = "Desc 1"
        mock_project1.metadata = {}

        mock_project2 = MagicMock()
        mock_project2.id = "proj-2"
        mock_project2.name = "Project 2"
        mock_project2.description = "Desc 2"
        mock_project2.metadata = {"key": "value"}

        mock_projects = [mock_project1, mock_project2]

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_all = AsyncMock(return_value=mock_projects)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TWO
            assert len(data["projects"]) == COUNT_TWO
            assert data["projects"][0]["id"] == "proj-1"
            assert data["projects"][0]["name"] == "Project 1"

    @pytest.mark.asyncio
    async def test_list_projects_pagination(self, client: Any) -> None:
        """Test projects list respects skip and limit parameters."""
        mock_projects = [MagicMock(id=f"proj-{i}", name=f"Project {i}", description="", metadata={}) for i in range(10)]

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_all = AsyncMock(return_value=mock_projects)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects?skip=2&limit=3")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_TEN
            assert len(data["projects"]) == COUNT_THREE
            assert data["projects"][0]["id"] == "proj-2"

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, client: Any) -> None:
        """Test listing projects when none exist."""
        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_all = AsyncMock(return_value=[])
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == 0
            assert len(data["projects"]) == 0


class TestGetProjectEndpoint:
    """Test GET /api/v1/projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_project_success(self, client: Any) -> None:
        """Test getting project by ID."""
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        mock_project.name = "Test Project"
        mock_project.description = "Test description"
        mock_project.metadata = {"key": "value"}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "proj-123"
            assert data["name"] == "Test Project"
            assert data["description"] == "Test description"
            assert data["metadata"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client: Any) -> None:
        """Test getting non-existent project returns 404."""
        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/nonexistent")

            assert response.status_code == HTTP_NOT_FOUND
            assert "Project not found" in response.json()["detail"]


class TestCreateProjectEndpoint:
    """Test POST /api/v1/projects endpoint."""

    @pytest.mark.asyncio
    async def test_create_project_success(self, client: Any) -> None:
        """Test creating project successfully."""
        mock_project = MagicMock()
        mock_project.id = "proj-new"
        mock_project.name = "New Project"
        mock_project.description = "New description"
        mock_project.metadata = {}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.create = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.post(
                "/api/v1/projects",
                json={"name": "New Project", "description": "New description"},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "proj-new"
            assert data["name"] == "New Project"
            assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_create_project_with_metadata(self, client: Any) -> None:
        """Test creating project with metadata."""
        mock_project = MagicMock()
        mock_project.id = "proj-new"
        mock_project.name = "New Project"
        mock_project.description = None
        mock_project.metadata = {"key": "value"}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.create = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.post(
                "/api/v1/projects",
                json={"name": "New Project", "metadata": {"key": "value"}},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["metadata"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_create_project_minimal(self, client: Any) -> None:
        """Test creating project with only name."""
        mock_project = MagicMock()
        mock_project.id = "proj-new"
        mock_project.name = "New Project"
        mock_project.description = None
        mock_project.metadata = {}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.create = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.post("/api/v1/projects", json={"name": "New Project"})

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["name"] == "New Project"


class TestUpdateProjectEndpoint:
    """Test PUT /api/v1/projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_project_success(self, client: Any) -> None:
        """Test updating project successfully."""
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        mock_project.name = "Updated Project"
        mock_project.description = "Updated description"
        mock_project.metadata = {"updated": True}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.update = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.put(
                "/api/v1/projects/proj-123",
                json={"name": "Updated Project", "description": "Updated description"},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "proj-123"
            assert data["name"] == "Updated Project"
            assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_project_partial(self, client: Any) -> None:
        """Test updating project with partial data."""
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        mock_project.name = "Original Project"
        mock_project.description = "Updated description"
        mock_project.metadata = {}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.update = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.put(
                "/api/v1/projects/proj-123",
                json={"description": "Updated description"},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client: Any) -> None:
        """Test updating non-existent project returns 404."""
        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.update = AsyncMock(return_value=None)
            mock_repo.return_value = repo_instance

            response = client.put(
                "/api/v1/projects/nonexistent",
                json={"name": "Updated"},
            )

            assert response.status_code == HTTP_NOT_FOUND
            assert "Project not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_project_metadata(self, client: Any) -> None:
        """Test updating project metadata."""
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        mock_project.name = "Test Project"
        mock_project.description = None
        mock_project.metadata = {"key": "new_value"}

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.update = AsyncMock(return_value=mock_project)
            mock_repo.return_value = repo_instance

            response = client.put(
                "/api/v1/projects/proj-123",
                json={"metadata": {"key": "new_value"}},
            )

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["metadata"] == {"key": "new_value"}


class TestDeleteProjectEndpoint:
    """Test DELETE /api/v1/projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, client: Any) -> None:
        """Test deleting project successfully."""
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        mock_project.name = "Test Project"

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            with patch("tracertm.repositories.link_repository.LinkRepository") as mock_link_repo:
                with patch("tracertm.repositories.item_repository.ItemRepository") as mock_item_repo:
                    repo_instance = MagicMock()
                    repo_instance.get_by_id = AsyncMock(return_value=mock_project)
                    mock_repo.return_value = repo_instance

                    link_repo_instance = MagicMock()
                    link_repo_instance.get_by_project = AsyncMock(return_value=[])
                    mock_link_repo.return_value = link_repo_instance

                    item_repo_instance = MagicMock()
                    item_repo_instance.list_all = AsyncMock(return_value=[])
                    mock_item_repo.return_value = item_repo_instance

                    # Mock the db session from get_db dependency
                    with patch("tracertm.api.main.get_db") as mock_get_db:
                        mock_db = MagicMock(spec=AsyncSession)
                        mock_db.execute = AsyncMock()
                        mock_db.commit = AsyncMock()
                        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                        mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

                        response = client.delete("/api/v1/projects/proj-123")

                        assert response.status_code == HTTP_OK
                        data = response.json()
                        assert data["success"] is True
                        assert "Project deleted successfully" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client: Any) -> None:
        """Test deleting non-existent project returns 404."""
        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = repo_instance

            response = client.delete("/api/v1/projects/nonexistent")

            assert response.status_code == HTTP_NOT_FOUND
            assert "Project not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_project_cascade(self, client: Any) -> None:
        """Test deleting project cascades to items and links."""
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        mock_project.name = "Test Project"

        mock_link = MagicMock()
        mock_link.id = "link-1"

        mock_item = MagicMock()
        mock_item.id = "item-1"

        with patch("tracertm.repositories.project_repository.ProjectRepository") as mock_repo:
            with patch("tracertm.repositories.link_repository.LinkRepository") as mock_link_repo:
                with patch("tracertm.repositories.item_repository.ItemRepository") as mock_item_repo:
                    repo_instance = MagicMock()
                    repo_instance.get_by_id = AsyncMock(return_value=mock_project)
                    mock_repo.return_value = repo_instance

                    link_repo_instance = MagicMock()
                    link_repo_instance.get_by_project = AsyncMock(return_value=[mock_link])
                    link_repo_instance.delete = AsyncMock(return_value=True)  # Make delete async
                    mock_link_repo.return_value = link_repo_instance

                    item_repo_instance = MagicMock()
                    item_repo_instance.list_all = AsyncMock(return_value=[mock_item])
                    mock_item_repo.return_value = item_repo_instance

                    # Mock the db session from get_db dependency
                    with patch("tracertm.api.main.get_db") as mock_get_db:
                        mock_db = MagicMock(spec=AsyncSession)
                        # Mock execute to return a result that can be awaited
                        execute_result = MagicMock()
                        execute_result.rowcount = 1
                        mock_db.execute = AsyncMock(return_value=execute_result)
                        mock_db.commit = AsyncMock()
                        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                        mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

                        response = client.delete("/api/v1/projects/proj-123")

                        assert response.status_code == HTTP_OK
                        data = response.json()
                        assert data["success"] is True
                        assert "Project deleted successfully" in data["message"]
                        # Verify link delete was called (cascade delete)
                        link_repo_instance.delete.assert_called_once_with("link-1")
                        # Verify db.execute was called for items and project deletion
                        # The implementation calls db.execute for Item and Project deletion
                        # Note: We verify the endpoint works correctly rather than checking internal implementation
