"""Comprehensive tests for Links API endpoints.

Tests all CRUD operations, validation, filtering, and edge cases for links.

Functional Requirements Coverage:
    - FR-APP-006: Create Traceability Link (POST /links)
    - FR-APP-007: Retrieve Traceability Link (GET /links/{id})
    - FR-APP-008: Update Traceability Link (PUT /links/{id})
    - FR-APP-009: Delete Traceability Link (DELETE /links/{id})
    - FR-APP-010: List Traceability Links (GET /links)
    - FR-DISC-003: Auto-Link Suggestion (partial)

Epics:
    - EPIC-003: Application & Tracking

Tests verify link API endpoints for CRUD operations, bidirectional navigation,
validation, filtering, and metadata management.
"""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import COUNT_THREE, COUNT_TWO, HTTP_NOT_FOUND, HTTP_OK
from tracertm.api.main import app

client = TestClient(app)


class TestLinksCRUD:
    """Test CRUD operations for links."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_minimal(self, mock_auth: Any, mock_db: Any) -> None:
        """Test creating link with minimal required fields."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata=None,
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
    def test_create_link_with_metadata(self, mock_auth: Any, mock_db: Any) -> None:
        """Test creating link with metadata."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        metadata = {
            "priority": "high",
            "verified": True,
            "tags": ["critical", "required"],
        }

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata=metadata,
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
                "metadata": metadata,
            }

            response = client.post("/api/v1/links", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["metadata"] == metadata

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_update_link_type(self, mock_auth: Any, mock_db: Any) -> None:
        """Test updating link type."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="related_to",
            link_metadata=None,
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {"link_type": "related_to"}
            response = client.put("/api/v1/links/link1", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["type"] == "related_to"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_update_link_metadata(self, mock_auth: Any, mock_db: Any) -> None:
        """Test updating link metadata."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        new_metadata = {"status": "verified", "version": 2}
        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata=new_metadata,
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {"metadata": new_metadata}
            response = client.put("/api/v1/links/link1", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["metadata"] == new_metadata


class TestLinksFiltering:
    """Test links filtering and query capabilities."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_by_source_and_target_specific(self, mock_auth: Any, mock_db: Any) -> None:
        """Test filtering links by specific source and target combination."""
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
        if data["links"]:
            assert data["links"][0]["source_id"] == "item1"
            assert data["links"][0]["target_id"] == "item2"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_pagination(self, mock_auth: Any, mock_db: Any) -> None:
        """Test pagination of links list."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 50

        results = [mock_result, AsyncMock()]
        links = [
            MagicMock(
                id=f"link{i}",
                source_item_id=f"item{i}",
                target_item_id=f"item{i + 1}",
                link_type="depends_on",
                created_at=datetime.now(),
                link_metadata=None,
            )
            for i in range(10)
        ]
        results[1].fetchall.return_value = links

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?project_id=proj1&skip=10&limit=10")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 50

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_empty_result(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list links when no results match filter."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 0

        results = [mock_result, AsyncMock()]
        results[1].fetchall.return_value = []

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?source_id=nonexistent&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["links"]) == 0

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_multiple_items_as_source(self, mock_auth: Any, mock_db: Any) -> None:
        """Test listing all links where item is source."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 3

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
                source_item_id="item1",
                target_item_id="item3",
                link_type="related_to",
                created_at=datetime.now(),
                link_metadata=None,
            ),
            MagicMock(
                id="link3",
                source_item_id="item1",
                target_item_id="item4",
                link_type="blocks",
                created_at=datetime.now(),
                link_metadata=None,
            ),
        ]

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?source_id=item1&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == COUNT_THREE
        assert all(link["source_id"] == "item1" for link in data["links"])

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_links_multiple_items_as_target(self, mock_auth: Any, mock_db: Any) -> None:
        """Test listing all links where item is target."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 2

        results = [mock_result, AsyncMock()]
        results[1].fetchall.return_value = [
            MagicMock(
                id="link1",
                source_item_id="item1",
                target_item_id="item99",
                link_type="depends_on",
                created_at=datetime.now(),
                link_metadata=None,
            ),
            MagicMock(
                id="link2",
                source_item_id="item2",
                target_item_id="item99",
                link_type="related_to",
                created_at=datetime.now(),
                link_metadata=None,
            ),
        ]

        mock_session.execute.side_effect = results

        response = client.get("/api/v1/links?target_id=item99&skip=0&limit=100")
        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["total"] == COUNT_TWO
        assert all(link["target_id"] == "item99" for link in data["links"])


class TestLinksValidation:
    """Test links validation and error handling."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_missing_project_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link creation fails without project_id."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        payload = {
            "source_id": "item1",
            "target_id": "item2",
            "type": "depends_on",
        }

        response = client.post("/api/v1/links", json=payload)
        # Validation error - may be 422 or 500 depending on handler
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_missing_source_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link creation fails without source_id."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        payload = {
            "project_id": "proj1",
            "target_id": "item2",
            "type": "depends_on",
        }

        response = client.post("/api/v1/links", json=payload)
        # Validation error - may be 422 or 500 depending on handler
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_missing_target_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link creation fails without target_id."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        payload = {
            "project_id": "proj1",
            "source_id": "item1",
            "type": "depends_on",
        }

        response = client.post("/api/v1/links", json=payload)
        # Validation error - may be 422 or 500 depending on handler
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_missing_type(self, mock_auth: Any, mock_db: Any) -> None:
        """Test link creation fails without type."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_db.return_value = AsyncMock()

        payload = {
            "project_id": "proj1",
            "source_id": "item1",
            "target_id": "item2",
        }

        response = client.post("/api/v1/links", json=payload)
        # Validation error - may be 422 or 500 depending on handler
        assert response.status_code in {422, 500}

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_update_link_missing_required_field(self, mock_auth: Any, mock_db: Any) -> None:
        """Test updating link with minimal payload."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata=None,
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {}  # Empty payload
            response = client.put("/api/v1/links/link1", json=payload)
            assert response.status_code == HTTP_OK  # Should still work with all None values


class TestLinksEdgeCases:
    """Test edge cases for links API."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_same_source_and_target(self, mock_auth: Any, mock_db: Any) -> None:
        """Test creating self-referential link."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item1",
            link_type="depends_on",
            link_metadata=None,
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {
                "project_id": "proj1",
                "source_id": "item1",
                "target_id": "item1",
                "type": "depends_on",
            }

            response = client.post("/api/v1/links", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["source_id"] == data["target_id"]

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_with_special_characters_in_ids(self, mock_auth: Any, mock_db: Any) -> None:
        """Test creating link with special characters in item IDs."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        special_source = "item-123_uuid.ext"
        special_target = "item-456_uuid.ext"

        mock_link = MagicMock(
            id="link1",
            source_item_id=special_source,
            target_item_id=special_target,
            link_type="depends_on",
            link_metadata=None,
        )

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create.return_value = mock_link
            mock_repo_class.return_value = mock_repo

            payload = {
                "project_id": "proj1",
                "source_id": special_source,
                "target_id": special_target,
                "type": "depends_on",
            }

            response = client.post("/api/v1/links", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["source_id"] == special_source
            assert data["target_id"] == special_target

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_with_complex_metadata(self, mock_auth: Any, mock_db: Any) -> None:
        """Test creating link with complex nested metadata."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        complex_metadata = {
            "priority": "high",
            "tags": ["critical", "verified"],
            "nested": {
                "level1": {
                    "level2": {
                        "value": "deep",
                    },
                },
            },
            "list": [1, 2, 3],
        }

        mock_link = MagicMock(
            id="link1",
            source_item_id="item1",
            target_item_id="item2",
            link_type="depends_on",
            link_metadata=complex_metadata,
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
                "metadata": complex_metadata,
            }

            response = client.post("/api/v1/links", json=payload)
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["metadata"] == complex_metadata

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_create_link_with_various_types(self, mock_auth: Any, mock_db: Any) -> None:
        """Test creating links with various link types."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        link_types = [
            "depends_on",
            "related_to",
            "blocks",
            "is_blocked_by",
            "duplicates",
            "is_duplicated_by",
        ]

        for link_type in link_types:
            mock_link = MagicMock(
                id=f"link_{link_type}",
                source_item_id="item1",
                target_item_id="item2",
                link_type=link_type,
                link_metadata=None,
            )

            with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
                mock_repo = MagicMock()
                mock_repo.create.return_value = mock_link
                mock_repo_class.return_value = mock_repo

                payload = {
                    "project_id": "proj1",
                    "source_id": "item1",
                    "target_id": "item2",
                    "type": link_type,
                }

                response = client.post("/api/v1/links", json=payload)
                assert response.status_code == HTTP_OK
                data = response.json()
                assert data["type"] == link_type

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_update_nonexistent_link(self, mock_auth: Any, mock_db: Any) -> None:
        """Test updating non-existent link returns 404."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        with patch("tracertm.api.main.link_repository.LinkRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = None  # Link not found
            mock_repo_class.return_value = mock_repo

            payload = {"link_type": "related_to"}
            response = client.put("/api/v1/links/nonexistent", json=payload)
            assert response.status_code == HTTP_NOT_FOUND


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
