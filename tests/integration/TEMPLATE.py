"""Template for Integration Tests - Copy this file to create new test modules.

This template provides the standard structure for writing real integration tests
that exercise actual services with a real (SQLite) database.

DO:
  ✅ Use real database fixtures (db_session from conftest.py)
  ✅ Test error paths and edge cases, not just happy path
  ✅ Clean up after tests (database handles this automatically)
  ✅ Test service interactions (not isolated units)
  ✅ Name tests clearly: test_<action>_<condition>_<expected_result>

DON'T:
  ❌ Mock the service layer (that defeats the purpose)
  ❌ Mock database queries (use real SQLite in-memory)
  ❌ Skip teardown/cleanup
  ❌ Write tests that pass but don't test real code
  ❌ Leave uncommitted database changes

Coverage Goal: Every service method should have at least one integration test.
"""

from typing import Any

import pytest

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestMyService:
    """Test suite for MyService - Replace with actual service name."""

    async def test_create_item_in_existing_project(self, db_session: Any) -> None:
        """Test creating an item in an existing project - happy path."""
        # Setup: Create a project
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Test Project")
        assert project.id is not None

        # Action: Create an item
        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=str(project.id),
            title="Test Item",
            view="FEATURE",
            item_type="feature",
        )

        # Assert: Verify item was created
        assert item.id is not None
        assert item.title == "Test Item"
        assert str(item.project_id) == str(project.id)

    async def test_create_item_with_invalid_project_id_raises_error(self, db_session: Any) -> None:
        """Test creating an item with non-existent project raises error."""
        item_repo = ItemRepository(db_session)

        # Should raise error for non-existent project
        with pytest.raises(ValueError, match="Project not found"):
            await item_repo.create(
                project_id="99999",  # Non-existent ID
                title="Test Item",
                view="FEATURE",
                item_type="feature",
            )

    async def test_retrieve_item_after_creation(self, db_session: Any) -> None:
        """Test retrieving an item after creation - round-trip test."""
        # Setup
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Test Project")

        item_repo = ItemRepository(db_session)
        created_item = await item_repo.create(
            project_id=str(project.id),
            title="Test Item",
            view="FEATURE",
            item_type="feature",
        )

        # Action: Retrieve the item
        retrieved_item = await item_repo.get_by_id(created_item.id, project_id=str(project.id))

        # Assert: Verify round-trip
        assert retrieved_item is not None
        assert retrieved_item.id == created_item.id
        assert retrieved_item.title == "Test Item"

    async def test_update_item_attributes(self, db_session: Any) -> None:
        """Test updating item attributes."""
        # Setup
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Test Project")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=str(project.id),
            title="Original Title",
            view="FEATURE",
            item_type="feature",
        )

        # Action: Update item (expected_version from current item)
        updated_item = await item_repo.update(
            item.id,
            item.version,
            title="Updated Title",
        )

        # Assert
        assert updated_item.title == "Updated Title"

        # Verify persistence by retrieving again
        verified = await item_repo.get_by_id(item.id, project_id=str(project.id))
        assert verified is not None and verified.title == "Updated Title"

    async def test_delete_item_removes_from_database(self, db_session: Any) -> None:
        """Test deleting an item removes it from database."""
        # Setup
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Test Project")

        item_repo = ItemRepository(db_session)
        item = await item_repo.create(
            project_id=str(project.id),
            title="To Delete",
            view="FEATURE",
            item_type="feature",
        )
        item_id = item.id

        # Action: Delete item
        await item_repo.delete(item_id)

        # Assert: Item no longer exists
        retrieved = await item_repo.get_by_id(item_id, project_id=str(project.id))
        assert retrieved is None

    async def test_list_items_returns_all_items(self, db_session: Any) -> None:
        """Test listing items returns all created items."""
        # Setup
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Test Project")

        item_repo = ItemRepository(db_session)
        await item_repo.create(project_id=str(project.id), title="Item 1", view="FEATURE", item_type="feature")
        await item_repo.create(project_id=str(project.id), title="Item 2", view="FEATURE", item_type="bug")
        await item_repo.create(project_id=str(project.id), title="Item 3", view="FEATURE", item_type="feature")

        # Action: List items
        items = await item_repo.list_all(project_id=str(project.id))

        # Assert
        assert len(items) == 3
        assert any(i.title == "Item 1" for i in items)
        assert any(i.title == "Item 2" for i in items)
        assert any(i.title == "Item 3" for i in items)

    async def test_filter_items_by_type(self, db_session: Any) -> None:
        """Test filtering items by type."""
        # Setup
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Test Project")

        item_repo = ItemRepository(db_session)
        await item_repo.create(project_id=str(project.id), title="Feature 1", view="FEATURE", item_type="feature")
        await item_repo.create(project_id=str(project.id), title="Bug 1", view="FEATURE", item_type="bug")
        await item_repo.create(project_id=str(project.id), title="Feature 2", view="FEATURE", item_type="feature")

        # Action: List all and filter by type in test
        items = await item_repo.list_all(project_id=str(project.id))
        features = [i for i in items if i.item_type == "feature"]

        # Assert
        assert len(features) == 2
        assert all(i.item_type == "feature" for i in features)

    async def test_service_error_handling_on_invalid_input(self, db_session: Any) -> None:
        """Test service handles invalid input gracefully."""
        item_repo = ItemRepository(db_session)

        # Test missing required field (empty title)
        with pytest.raises(ValueError):
            await item_repo.create(
                project_id="1",
                title="",
                view="FEATURE",
                item_type="feature",
            )

        # Test invalid type (if validated by repo)
        with pytest.raises(ValueError):
            await item_repo.create(
                project_id="1",
                title="Test",
                view="FEATURE",
                item_type="invalid_type",
            )


# ============================================================================
# INSTRUCTIONS FOR AGENTS
# ============================================================================
#
# 1. COPY THIS FILE to your work package directory:
#    cp TEMPLATE.py test_your_service.py
#
# 2. REPLACE:
#    - "MyService" with your service name
#    - "ProjectRepository/ItemRepository" with your actual repository
#    - Test data with your actual entity types
#    - Assertions with what you're testing
#
# 3. FOR EACH SERVICE METHOD, add a test:
#    - Happy path (normal operation)
#    - Error path (invalid input, missing data)
#    - Edge case (boundary conditions, limits)
#    - Persistence (verify database changes stick)
#
# 4. RUN YOUR TESTS:
#    pytest tests/integration/test_your_service.py -v
#
# 5. CHECK COVERAGE:
#    pytest tests/integration/test_your_service.py \
#        --cov=src/tracertm/services/your_service \
#        --cov-report=term-missing
#
# 6. AIM FOR:
#    - 100% line coverage
#    - All error paths tested
#    - All service methods called with real data
#
# 7. COMMIT WITH:
#    git add tests/integration/test_your_service.py
#    git commit -m "WP-X.Y: [N tests], coverage [%]"
#
# ============================================================================
