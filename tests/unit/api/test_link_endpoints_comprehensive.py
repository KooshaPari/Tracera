"""Comprehensive tests for Link API endpoints.

Functional Requirements Coverage:
    - FR-APP-007: Retrieve Traceability Link (GET /links/{id})
    - FR-APP-008: Update Traceability Link (PUT /links/{id})
    - FR-APP-010: List Traceability Links (GET /links)

Epics:
    - EPIC-003: Application & Tracking

Tests:
- GET /api/v1/links
- PUT /api/v1/links/{link_id}
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, HTTP_NOT_FOUND, HTTP_OK


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


class TestListLinksEndpoint:
    """Test GET /api/v1/links endpoint (expanded tests)."""

    @pytest.mark.asyncio
    async def test_list_links_empty_project(self, client: Any) -> None:
        """Test listing links for project with no links."""
        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_project = AsyncMock(return_value=[])
            mock_repo.return_value = repo_instance

            response = client.get("/api/v1/links?project_id=empty-project")

            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == 0
            assert len(data["links"]) == 0

    @pytest.mark.asyncio
    async def test_list_links_pagination_edge_cases(self, client: Any) -> None:
        """Test link list pagination with edge cases."""
        mock_links = [
            MagicMock(
                id=f"link-{i}",
                source_item_id=f"item-{i}",
                target_item_id=f"item-{i + 1}",
                link_type="implements",
            )
            for i in range(5)
        ]

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_project = AsyncMock(return_value=mock_links)
            mock_repo.return_value = repo_instance

            # Test skip beyond total
            response = client.get("/api/v1/links?project_id=test&skip=10&limit=5")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_FIVE
            assert len(data["links"]) == 0  # Empty because skip > total

            # Test limit larger than total
            response = client.get("/api/v1/links?project_id=test&skip=0&limit=100")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == COUNT_FIVE
            assert len(data["links"]) == COUNT_FIVE


class TestUpdateLinkEndpoint:
    """Test PUT /api/v1/links/{link_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_link_type_success(self, client: Any) -> None:
        """Test updating link type successfully."""
        mock_link = MagicMock()
        mock_link.id = "link-123"
        mock_link.source_item_id = "item-1"
        mock_link.target_item_id = "item-2"
        mock_link.link_type = "implements"  # Initial value
        mock_link.metadata = {}

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=mock_link)
            mock_repo.return_value = repo_instance

            # Mock the db session from get_db dependency
            with patch("tracertm.api.main.get_db") as mock_get_db:
                mock_db = MagicMock(spec=AsyncSession)
                mock_db.flush = AsyncMock()
                mock_db.refresh = AsyncMock()
                mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

                response = client.put(
                    "/api/v1/links/link-123",
                    json={"link_type": "tests"},
                )

                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["id"] == "link-123"
                assert data["type"] == "tests"
                # Verify link_type was updated
                assert mock_link.link_type == "tests"

    @pytest.mark.asyncio
    async def test_update_link_metadata_success(self, client: Any) -> None:
        """Test updating link metadata successfully."""
        mock_link = MagicMock()
        mock_link.id = "link-123"
        mock_link.source_item_id = "item-1"
        mock_link.target_item_id = "item-2"
        mock_link.link_type = "implements"
        mock_link.metadata = {}

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=mock_link)
            mock_repo.return_value = repo_instance

            # Mock the db session from get_db dependency
            with patch("tracertm.api.main.get_db") as mock_get_db:
                mock_db = MagicMock(spec=AsyncSession)
                mock_db.flush = AsyncMock()
                mock_db.refresh = AsyncMock()
                mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

                response = client.put(
                    "/api/v1/links/link-123",
                    json={"metadata": {"key": "value"}},
                )

                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["metadata"] == {"key": "value"}
                # Verify metadata was updated
                assert mock_link.metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_update_link_both_fields(self, client: Any) -> None:
        """Test updating both link_type and metadata."""
        mock_link = MagicMock()
        mock_link.id = "link-123"
        mock_link.source_item_id = "item-1"
        mock_link.target_item_id = "item-2"
        mock_link.link_type = "implements"
        mock_link.metadata = {}

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=mock_link)
            mock_repo.return_value = repo_instance

            # Mock the db session from get_db dependency
            with patch("tracertm.api.main.get_db") as mock_get_db:
                mock_db = MagicMock(spec=AsyncSession)
                mock_db.flush = AsyncMock()
                mock_db.refresh = AsyncMock()
                mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

                response = client.put(
                    "/api/v1/links/link-123",
                    json={"link_type": "tests", "metadata": {"key": "value"}},
                )

                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["type"] == "tests"
                assert data["metadata"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_update_link_not_found(self, client: Any) -> None:
        """Test updating non-existent link returns 404."""
        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = repo_instance

            response = client.put(
                "/api/v1/links/nonexistent",
                json={"link_type": "tests"},
            )

            assert response.status_code == HTTP_NOT_FOUND
            assert "Link not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_link_no_changes(self, client: Any) -> None:
        """Test updating link with no changes."""
        mock_link = MagicMock(
            id="link-123",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="implements",
            metadata={},
        )

        with patch("tracertm.repositories.link_repository.LinkRepository") as mock_repo:
            repo_instance = MagicMock()
            repo_instance.get_by_id = AsyncMock(return_value=mock_link)
            mock_repo.return_value = repo_instance

            # Mock the db session from get_db dependency
            with patch("tracertm.api.main.get_db") as mock_get_db:
                mock_db = MagicMock(spec=AsyncSession)
                mock_db.flush = AsyncMock()
                mock_db.refresh = AsyncMock()
                mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                mock_get_db.return_value.__aexit__ = AsyncMock(return_value=None)

                # Update with no parameters (should still work)
                response = client.put("/api/v1/links/link-123", json={})

                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["id"] == "link-123"
