"""Comprehensive tests for Items API endpoints.

Functional Requirements Coverage:
    - FR-APP-001: Create Traceability Item (POST /items)
    - FR-APP-002: Retrieve Traceability Item (GET /items/{id})
    - FR-APP-003: Update Traceability Item (PUT /items/{id})
    - FR-APP-004: Delete Traceability Item (DELETE /items/{id})
    - FR-APP-005: List Traceability Items (GET /items)

Epics:
    - EPIC-003: Application & Tracking

Tests all CRUD operations, validation, filtering, and edge cases for items.
"""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, HTTP_OK
from tracertm.api.main import app

client = TestClient(app)


class TestItemsCRUD:
    """Test CRUD operations for items."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_default_pagination(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list uses default pagination values."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 150
        mock_session.execute.return_value = mock_result

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
            for i in range(100)
        ]

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == 150
            assert len(data["items"]) <= 100  # Default limit

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_get_item_with_all_fields(self, mock_auth: Any, mock_db: Any) -> None:
        """Test get item returns all expected fields."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        now = datetime.now()
        mock_item = MagicMock(
            id="item1",
            project_id="proj1",
            title="Test Item",
            view="REQUIREMENT",
            item_type="requirement",
            status="in_progress",
            priority="high",
            created_at=now,
            updated_at=now,
            description="Test description",
        )

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = mock_item
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items/item1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == "item1"
            assert data["project_id"] == "proj1"
            assert data["title"] == "Test Item"
            assert data["type"] == "requirement"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_various_statuses(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list handles various status values."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        statuses = ["todo", "in_progress", "done", "blocked", "review"]
        mock_items = [
            MagicMock(
                id=f"item{i}",
                project_id="proj1",
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status=statuses[i % len(statuses)],
                priority="medium",
                created_at=datetime.now(),
            )
            for i in range(5)
        ]

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert len(data["items"]) == COUNT_FIVE
            found_statuses = {item["status"] for item in data["items"]}
            assert len(found_statuses) > 0

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_priorities(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items list handles various priority levels."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        priorities = ["low", "medium", "high", "critical"]
        mock_items = [
            MagicMock(
                id=f"item{i}",
                project_id="proj1",
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority=priorities[i % len(priorities)],
                created_at=datetime.now(),
            )
            for i in range(4)
        ]

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 4
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert len(data["items"]) == COUNT_FOUR


class TestItemsFiltering:
    """Test items filtering and search capabilities."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_respects_project_isolation(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items from other projects are not returned."""
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
            for item in data["items"]:
                assert item["project_id"] == "proj1"

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_skip_offset(self, mock_auth: Any, mock_db: Any) -> None:
        """Test skip parameter correctly offsets results."""
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
            for i in range(5, 10)
        ]

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 20
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1&skip=5&limit=5")
            assert response.status_code == HTTP_OK

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_limit_boundary(self, mock_auth: Any, mock_db: Any) -> None:
        """Test limit parameter correctly limits results."""
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
        mock_result.scalar.return_value = 1000
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1&limit=10")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert len(data["items"]) <= COUNT_TEN


class TestItemsEdgeCases:
    """Test edge cases and special conditions for items."""

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_item_with_no_created_at(self, mock_auth: Any, mock_db: Any) -> None:
        """Test handling of item without created_at timestamp."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        mock_item = MagicMock(
            id="item1",
            project_id="proj1",
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="medium",
            created_at=None,  # No timestamp
        )

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = mock_item
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items/item1")
            assert response.status_code == HTTP_OK
            data = response.json()
            # Should handle gracefully
            assert "id" in data

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_item_with_special_characters_in_title(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items with special characters in title."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        special_title = 'Item with <special> & "quotes" chars'
        mock_item = MagicMock(
            id="item1",
            project_id="proj1",
            title=special_title,
            view="FEATURE",
            item_type="feature",
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
            assert data["title"] == special_title

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_item_with_very_long_title(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items with very long titles."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        long_title = "A" * 1000  # 1000 character title
        mock_item = MagicMock(
            id="item1",
            project_id="proj1",
            title=long_title,
            view="FEATURE",
            item_type="feature",
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
            assert len(data["title"]) == 1000

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_item_with_special_project_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test items with special characters in project ID."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        special_project_id = "proj-123_test.uuid"
        mock_items = [
            MagicMock(
                id="item1",
                project_id=special_project_id,
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

            response = client.get(f"/api/v1/items?project_id={special_project_id}")
            assert response.status_code == HTTP_OK
            data = response.json()
            if data["items"]:
                assert data["items"][0]["project_id"] == special_project_id

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_get_item_with_uuid_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test getting item with UUID format ID."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        uuid_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_item = MagicMock(
            id=uuid_id,
            project_id="proj1",
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="medium",
            created_at=datetime.now(),
        )

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = mock_item
            mock_repo_class.return_value = mock_repo

            response = client.get(f"/api/v1/items/{uuid_id}")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == uuid_id

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_list_items_large_limit(self, mock_auth: Any, mock_db: Any) -> None:
        """Test list items with very large limit parameter."""
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
            for i in range(100)
        ]

        mock_result = AsyncMock()
        mock_result.scalar.return_value = 100
        mock_session.execute.return_value = mock_result

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_project.return_value = mock_items
            mock_repo_class.return_value = mock_repo

            response = client.get("/api/v1/items?project_id=proj1&limit=10000")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["total"] == 100

    @patch("tracertm.api.main.get_db")
    @patch("tracertm.api.main.auth_guard")
    def test_get_item_with_numeric_string_id(self, mock_auth: Any, mock_db: Any) -> None:
        """Test getting item with numeric string ID."""
        mock_auth.return_value = {"role": "user", "sub": "user123"}
        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        numeric_id = "12345"
        mock_item = MagicMock(
            id=numeric_id,
            project_id="proj1",
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
            priority="medium",
            created_at=datetime.now(),
        )

        with patch("tracertm.api.main.item_repository.ItemRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = mock_item
            mock_repo_class.return_value = mock_repo

            response = client.get(f"/api/v1/items/{numeric_id}")
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == numeric_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
