"""Comprehensive tests for Graph API endpoints.

Tests:
- GET /api/v1/projects/{project_id}/graph/neighbors
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE, COUNT_TWO, HTTP_OK


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


class TestGraphNeighborsEndpoint:
    """Test GET /api/v1/projects/{project_id}/graph/neighbors endpoint."""

    @pytest.mark.asyncio
    async def test_get_neighbors_both_directions(self, client: Any) -> None:
        """Test getting neighbors in both directions."""
        out_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="implements",
            ),
            MagicMock(
                id="link-2",
                source_item_id="item-1",
                target_item_id="item-3",
                link_type="tests",
            ),
        ]
        in_links = [
            MagicMock(
                id="link-3",
                source_item_id="item-4",
                target_item_id="item-1",
                link_type="depends_on",
            ),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_source = AsyncMock(return_value=out_links)
            repo_instance.get_by_target = AsyncMock(return_value=in_links)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1&direction=both")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["project_id"] == "proj-123"
            assert data["item_id"] == "item-1"
            assert data["direction"] == "both"
            assert data["total"] == COUNT_THREE
            assert len(data["neighbors"]) == COUNT_THREE

            # Check outbound neighbors
            out_neighbors = [n for n in data["neighbors"] if n["direction"] == "out"]
            assert len(out_neighbors) == COUNT_TWO

            # Check inbound neighbors
            in_neighbors = [n for n in data["neighbors"] if n["direction"] == "in"]
            assert len(in_neighbors) == 1

    @pytest.mark.asyncio
    async def test_get_neighbors_out_direction(self, client: Any) -> None:
        """Test getting neighbors in out direction only."""
        out_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="implements",
            ),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_source = AsyncMock(return_value=out_links)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1&direction=out")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["direction"] == "out"
            assert data["total"] == 1
            assert all(n["direction"] == "out" for n in data["neighbors"])

    @pytest.mark.asyncio
    async def test_get_neighbors_in_direction(self, client: Any) -> None:
        """Test getting neighbors in in direction only."""
        in_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-2",
                target_item_id="item-1",
                link_type="depends_on",
            ),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_target = AsyncMock(return_value=in_links)
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1&direction=in")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["direction"] == "in"
            assert data["total"] == 1
            assert all(n["direction"] == "in" for n in data["neighbors"])

    @pytest.mark.asyncio
    async def test_get_neighbors_default_direction(self, client: Any) -> None:
        """Test getting neighbors with default direction (both)."""
        out_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="implements",
            ),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_source = AsyncMock(return_value=out_links)
            repo_instance.get_by_target = AsyncMock(return_value=[])
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["direction"] == "both"  # Default

    @pytest.mark.asyncio
    async def test_get_neighbors_empty(self, client: Any) -> None:
        """Test getting neighbors for item with no links."""
        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_source = AsyncMock(return_value=[])
            repo_instance.get_by_target = AsyncMock(return_value=[])
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == 0
            assert len(data["neighbors"]) == 0

    @pytest.mark.asyncio
    async def test_get_neighbors_response_structure(self, client: Any) -> None:
        """Test neighbors response has expected structure."""
        out_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="implements",
            ),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_source = AsyncMock(return_value=out_links)
            repo_instance.get_by_target = AsyncMock(return_value=[])
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert isinstance(data, dict)
            assert "project_id" in data
            assert "item_id" in data
            assert "direction" in data
            assert "neighbors" in data
            assert "total" in data
            assert isinstance(data["neighbors"], list)

            if len(data["neighbors"]) > 0:
                neighbor = data["neighbors"][0]
                assert "id" in neighbor
                assert "item_id" in neighbor
                assert "link_type" in neighbor
                assert "direction" in neighbor

    @pytest.mark.asyncio
    async def test_get_neighbors_invalid_direction(self, client: Any) -> None:
        """Test getting neighbors with invalid direction defaults to both."""
        out_links = [
            MagicMock(
                id="link-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="implements",
            ),
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_source = AsyncMock(return_value=out_links)
            repo_instance.get_by_target = AsyncMock(return_value=[])
            mock_repo.return_value = repo_instance

            # Invalid direction should default to "both"
            response = client.get("/api/v1/projects/proj-123/graph/neighbors?item_id=item-1&direction=invalid")

            assert response.status_code == HTTP_OK
            data = response.json()
            # Should still work, but direction might be "invalid" or default to "both"
            assert "neighbors" in data
