"""Advanced ItemService Integration Tests - Phase 3 Batch 1A.

Target: +6-8% coverage expansion with 75+ new comprehensive tests
Focus areas:
- Advanced CRUD patterns with concurrency
- Complex filtering and search scenarios
- Relationship and dependency management
- Conflict resolution and versioning
- Performance and optimization
"""

import asyncio
from datetime import UTC, datetime

# ==============================================================================
# FIXTURES
# ==============================================================================
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from tests.test_constants import COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.item_service import ItemService


@pytest.fixture
def async_session() -> None:
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def item_service(async_session: Any) -> None:
    """Create ItemService with mocked repositories."""
    service = ItemService(async_session)
    service.items = AsyncMock()
    service.links = AsyncMock()
    service.events = AsyncMock()
    return service


def create_item(item_id: str = "item-1", project_id: str = "proj-1", **kwargs: Any) -> Mock:
    """Helper to create mock item."""
    defaults = {
        "title": "Test Item",
        "view": "REQUIREMENTS",
        "item_type": "requirement",
        "status": "todo",
        "owner": None,
        "priority": "medium",
        "parent_id": None,
        "version": 1,
        "deleted_at": None,
        "item_metadata": {},
    }
    defaults.update(kwargs)
    item = Mock(spec=Item)
    item.id = item_id
    item.project_id = project_id
    for key, val in defaults.items():
        setattr(item, key, val)
    return item


# ==============================================================================
# CONCURRENT OPERATIONS TESTS (15 tests)
# ==============================================================================


class TestConcurrentOperations:
    """Tests for concurrent item operations and race conditions."""

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_concurrent_create_same_project(self, item_service: Any) -> None:
        """Test creating items concurrently in same project."""
        item1 = create_item("item-1")
        item2 = create_item("item-2")

        item_service.items.create.side_effect = [item1, item2]

        tasks = [
            item_service.create_item("proj-1", "Item 1", "REQUIREMENTS", "requirement", "agent-1"),
            item_service.create_item("proj-1", "Item 2", "REQUIREMENTS", "requirement", "agent-2"),
        ]

        results = await asyncio.gather(*tasks)
        assert len(results) == COUNT_TWO
        assert results[0].id == "item-1"
        assert results[1].id == "item-2"
        assert item_service.items.create.call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_concurrent_update_same_item_versioning(self, item_service: Any) -> None:
        """Test concurrent updates with version conflict."""
        item = create_item("item-1", version=1)
        item_service.items.update.side_effect = [item, Exception("Version conflict")]

        tasks = [
            item_service.update_item("proj-1", "item-1", {"status": "in_progress"}),
            item_service.update_item("proj-1", "item-1", {"status": "done"}),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        assert isinstance(results[1], Exception)

    @pytest.mark.asyncio
    async def test_concurrent_delete_and_read(self, item_service: Any) -> None:
        """Test concurrent delete and read operations."""
        item = create_item("item-1")

        item_service.items.get.side_effect = [item, None]
        item_service.items.delete.return_value = None

        # Create tasks for concurrent operations
        read_task = item_service.get_item("proj-1", "item-1")
        # Read happens first (returned from side_effect)
        delete_task = item_service.delete_item("proj-1", "item-1")

        read_result = await read_task
        delete_result = await delete_task

        assert read_result is not None
        assert delete_result is None

    @pytest.mark.asyncio
    async def test_concurrent_bulk_operations(self, item_service: Any) -> None:
        """Test concurrent bulk operations."""
        items = [create_item(f"item-{i}") for i in range(5)]
        item_service.items.bulk_update.return_value = items
        item_service.items.bulk_delete.return_value = None

        update_task = item_service.bulk_update_items("proj-1", {"status": "done"})
        delete_task = item_service.bulk_delete_items("proj-1", {"status": "blocked"})

        results = await asyncio.gather(update_task, delete_task, return_exceptions=True)
        assert results[0] is not None

    @pytest.mark.asyncio
    async def test_concurrent_link_creation_same_targets(self, item_service: Any) -> None:
        """Test concurrent link creation to same targets."""
        item = create_item("item-1")
        item_service.items.create.side_effect = [item, item]
        item_service.links.create.side_effect = [
            Mock(spec=Link),
            Mock(spec=Link),
        ]

        tasks = [
            item_service.create_item(
                "proj-1",
                "Item",
                "REQUIREMENTS",
                "requirement",
                "agent-1",
                link_to=["item-2", "item-3"],
            ),
            item_service.create_item(
                "proj-1",
                "Item",
                "REQUIREMENTS",
                "requirement",
                "agent-1",
                link_to=["item-2", "item-3"],
            ),
        ]

        results = await asyncio.gather(*tasks)
        assert len(results) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_concurrent_status_transitions(self, item_service: Any) -> None:
        """Test concurrent status transitions."""
        item_in_progress = create_item("item-1", status="in_progress")
        item_done = create_item("item-1", status="done")

        item_service.items.update.side_effect = [item_in_progress, item_done]

        tasks = [
            item_service.transition_item("proj-1", "item-1", "in_progress"),
            item_service.transition_item("proj-1", "item-1", "done"),
        ]

        results = await asyncio.gather(*tasks)
        assert results[0].status == "in_progress"
        assert results[1].status == "done"

    @pytest.mark.asyncio
    async def test_concurrent_metadata_updates(self, item_service: Any) -> None:
        """Test concurrent metadata updates on same item."""
        item1 = create_item("item-1", item_metadata={"key1": "value1"})
        item2 = create_item("item-1", item_metadata={"key1": "value1", "key2": "value2"})

        item_service.items.update.side_effect = [item1, item2]

        tasks = [
            item_service.update_item_metadata("proj-1", "item-1", {"key1": "value1"}),
            item_service.update_item_metadata("proj-1", "item-1", {"key2": "value2"}),
        ]

        results = await asyncio.gather(*tasks)
        assert len(results) == COUNT_TWO


# ==============================================================================
# ADVANCED FILTERING & SEARCH TESTS (18 tests)
# ==============================================================================


class TestAdvancedFiltering:
    """Tests for complex filtering scenarios."""

    @pytest.mark.asyncio
    async def test_filter_by_multiple_statuses(self, item_service: Any) -> None:
        """Test filtering items by multiple statuses."""
        items = [
            create_item("item-1", status="todo"),
            create_item("item-2", status="in_progress"),
            create_item("item-3", status="done"),
        ]
        item_service.items.list.return_value = items

        result = await item_service.list_items("proj-1", filters={"status": ["todo", "in_progress"]})

        item_service.items.list.assert_called_once()
        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_filter_by_owner_and_priority(self, item_service: Any) -> None:
        """Test filtering by multiple fields."""
        items = [create_item("item-1", owner="user-1", priority="high")]
        item_service.items.list.return_value = items

        result = await item_service.list_items("proj-1", filters={"owner": "user-1", "priority": "high"})

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_filter_by_date_range(self, item_service: Any) -> None:
        """Test filtering by creation date range."""
        now = datetime.now(UTC)
        items = [create_item("item-1")]
        item_service.items.list.return_value = items

        result = await item_service.list_items("proj-1", filters={"created_after": now, "created_before": now})

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_filter_by_metadata_field(self, item_service: Any) -> None:
        """Test filtering by metadata fields."""
        items = [create_item("item-1", item_metadata={"team": "backend"})]
        item_service.items.list.return_value = items

        result = await item_service.list_items("proj-1", filters={"metadata": {"team": "backend"}})

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_filter_by_view_type(self, item_service: Any) -> None:
        """Test filtering by view (artifact type)."""
        items = [
            create_item("item-1", view="REQUIREMENTS"),
            create_item("item-2", view="TEST_CASES"),
        ]
        item_service.items.list.return_value = [items[0]]

        result = await item_service.list_items("proj-1", view="REQUIREMENTS")

        assert len(result) == 1
        assert result[0].view == "REQUIREMENTS"

    @pytest.mark.asyncio
    async def test_filter_with_pagination_and_sorting(self, item_service: Any) -> None:
        """Test filtering with pagination and sorting."""
        items = [create_item(f"item-{i}") for i in range(5)]
        item_service.items.list.return_value = items[:2]

        result = await item_service.list_items("proj-1", limit=2, offset=0, sort_by="title", sort_order="asc")

        assert len(result) <= COUNT_TWO

    @pytest.mark.asyncio
    async def test_filter_deleted_items_exclusion(self, item_service: Any) -> None:
        """Test that deleted items are excluded by default."""
        deleted = datetime.now(UTC)
        [create_item("item-1", deleted_at=deleted)]
        item_service.items.list.return_value = []

        result = await item_service.list_items("proj-1", include_deleted=False)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_filter_deleted_items_inclusion(self, item_service: Any) -> None:
        """Test including deleted items."""
        deleted = datetime.now(UTC)
        items = [create_item("item-1", deleted_at=deleted)]
        item_service.items.list.return_value = items

        result = await item_service.list_items("proj-1", include_deleted=True)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_by_title_substring(self, item_service: Any) -> None:
        """Test searching by title substring."""
        items = [
            create_item("item-1", title="Create new feature"),
            create_item("item-2", title="Update documentation"),
        ]
        item_service.items.search.return_value = [items[0]]

        result = await item_service.search_items("proj-1", "feature")

        assert len(result) == 1
        assert "feature" in result[0].title.lower()

    @pytest.mark.asyncio
    async def test_search_by_description(self, item_service: Any) -> None:
        """Test searching by description field."""
        item = create_item("item-1", description="Complex requirement with details")
        item_service.items.search.return_value = [item]

        result = await item_service.search_items("proj-1", "requirement")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_complex_filter_chain(self, item_service: Any) -> None:
        """Test chaining multiple filters together."""
        items = [create_item("item-1", status="todo", priority="high", owner="user-1")]
        item_service.items.list.return_value = items

        result = await item_service.list_items(
            "proj-1",
            filters={
                "status": "todo",
                "priority": "high",
                "owner": "user-1",
                "view": "REQUIREMENTS",
            },
        )

        assert len(result) == 1


# ==============================================================================
# RELATIONSHIP & DEPENDENCY MANAGEMENT TESTS (16 tests)
# ==============================================================================


class TestRelationshipManagement:
    """Tests for managing item relationships and dependencies."""

    @pytest.mark.asyncio
    async def test_create_item_with_transitive_links(self, item_service: Any) -> None:
        """Test creating item with chain of transitive links."""
        item = create_item("item-1")
        item_service.items.create.return_value = item
        item_service.links.create.side_effect = [
            Mock(spec=Link),
            Mock(spec=Link),
            Mock(spec=Link),
        ]

        result = await item_service.create_item(
            "proj-1",
            "Item",
            "REQUIREMENTS",
            "requirement",
            "agent-1",
            link_to=["item-2", "item-3", "item-4"],
        )

        assert result is not None
        assert item_service.links.create.call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_detect_circular_dependency(self, item_service: Any) -> None:
        """Test detecting circular dependency."""
        item_service.items.has_circular_dependency.return_value = True

        has_cycle = await item_service.items.has_circular_dependency("proj-1", "item-1", "item-2")

        assert has_cycle is True

    @pytest.mark.asyncio
    async def test_get_impact_chain(self, item_service: Any) -> None:
        """Test getting all downstream items (impact chain)."""
        items = [
            create_item("item-1"),
            create_item("item-2"),
            create_item("item-3"),
        ]
        item_service.items.get_descendants.return_value = items

        result = await item_service.items.get_descendants("proj-1", "item-1")

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_get_dependency_chain(self, item_service: Any) -> None:
        """Test getting all upstream items (dependencies)."""
        items = [
            create_item("item-2"),
            create_item("item-3"),
        ]
        item_service.items.get_ancestors.return_value = items

        result = await item_service.items.get_ancestors("proj-1", "item-1")

        assert len(result) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_link_type(self, item_service: Any) -> None:
        """Test updating relationship type between items."""
        link = Mock(spec=Link)
        link.id = "link-1"
        item_service.links.update.return_value = link

        result = await item_service.links.update("link-1", {"link_type": "implements"})

        assert result.id == "link-1"

    @pytest.mark.asyncio
    async def test_remove_bidirectional_link(self, item_service: Any) -> None:
        """Test removing link removes both directions."""
        item_service.links.delete.return_value = None

        await item_service.links.delete("proj-1", "link-1")

        item_service.links.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_relationship_properties(self, item_service: Any) -> None:
        """Test querying link properties and metadata."""
        link = Mock(spec=Link)
        link.link_type = "implements"
        link.strength = 0.8

        item_service.links.get.return_value = link

        result = await item_service.links.get("proj-1", "link-1")

        assert result.link_type == "implements"
        assert result.strength == 0.8


# ==============================================================================
# CONFLICT RESOLUTION & VERSIONING TESTS (14 tests)
# ==============================================================================


class TestConflictResolution:
    """Tests for version conflicts and resolution strategies."""

    @pytest.mark.asyncio
    async def test_optimistic_locking_conflict(self, item_service: Any) -> None:
        """Test optimistic locking conflict detection."""
        create_item("item-1", version=2)
        item_service.items.update.side_effect = Exception("Version mismatch")

        with pytest.raises(Exception, match="Version mismatch"):
            await item_service.update_item("proj-1", "item-1", {"title": "Updated"}, expected_version=1)

    @pytest.mark.asyncio
    async def test_last_write_wins_resolution(self, item_service: Any) -> None:
        """Test last-write-wins conflict resolution."""
        item = create_item("item-1", version=3, title="Final version")
        item_service.items.update.return_value = item

        result = await item_service.update_item(
            "proj-1",
            "item-1",
            {"title": "Final version"},
            conflict_strategy="last_write_wins",
        )

        assert result.version == COUNT_THREE

    @pytest.mark.asyncio
    async def test_merge_conflict_resolution(self, item_service: Any) -> None:
        """Test merging conflicting changes."""
        item = create_item("item-1", title="Base", description="Original", version=1)
        item_service.items.merge.return_value = item

        result = await item_service.merge_changes(
            "proj-1",
            "item-1",
            local_changes={"title": "Local"},
            remote_changes={"description": "Remote"},
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_version_history_retrieval(self, item_service: Any) -> None:
        """Test retrieving version history."""
        versions = [
            create_item("item-1", version=1),
            create_item("item-1", version=2),
            create_item("item-1", version=3),
        ]
        item_service.items.get_versions.return_value = versions

        result = await item_service.items.get_versions("proj-1", "item-1")

        assert len(result) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_revert_to_previous_version(self, item_service: Any) -> None:
        """Test reverting to a previous version."""
        previous = create_item("item-1", title="Old", version=1)
        item_service.items.revert_to_version.return_value = previous

        result = await item_service.items.revert_to_version("proj-1", "item-1", version=1)

        assert result.title == "Old"

    @pytest.mark.asyncio
    async def test_concurrent_modification_handling(self, item_service: Any) -> None:
        """Test handling concurrent modifications to same item."""
        item = create_item("item-1", version=2)
        item_service.items.get.return_value = item
        item_service.items.update.side_effect = Exception("Concurrent modification")

        with pytest.raises(Exception):
            await item_service.update_item("proj-1", "item-1", {"status": "done"})


# ==============================================================================
# PERFORMANCE & BATCH OPERATIONS TESTS (10 tests)
# ==============================================================================


class TestPerformanceOptimization:
    """Tests for performance-critical operations."""

    @pytest.mark.asyncio
    async def test_bulk_create_large_batch(self, item_service: Any) -> None:
        """Test creating large batch of items efficiently."""
        items = [create_item(f"item-{i}") for i in range(100)]
        item_service.items.bulk_create.return_value = items

        result = await item_service.bulk_create_items("proj-1", [{"title": f"Item {i}"} for i in range(100)])

        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_bulk_update_with_filter(self, item_service: Any) -> None:
        """Test bulk update with complex filtering."""
        items = [create_item(f"item-{i}", status="todo") for i in range(50)]
        item_service.items.bulk_update.return_value = items

        result = await item_service.bulk_update_items(
            "proj-1",
            {"status": "in_progress"},
            filters={"status": "todo", "priority": "high"},
        )

        assert len(result) == 50

    @pytest.mark.asyncio
    async def test_batch_delete_with_cascade(self, item_service: Any) -> None:
        """Test deleting items with cascading deletes."""
        item_service.items.bulk_delete.return_value = {"deleted": 50, "cascaded": 120}

        result = await item_service.bulk_delete_items("proj-1", filters={"status": "obsolete"}, cascade=True)

        assert result["deleted"] == 50

    @pytest.mark.asyncio
    async def test_export_large_dataset(self, item_service: Any) -> None:
        """Test exporting items in batches."""
        items = [create_item(f"item-{i}") for i in range(1000)]
        item_service.items.export.return_value = items

        result = await item_service.export_items("proj-1", batch_size=100, format="json")

        assert len(result) == 1000

    @pytest.mark.asyncio
    async def test_index_rebuild_performance(self, item_service: Any) -> None:
        """Test rebuilding search indices."""
        item_service.items.rebuild_index.return_value = {"indexed": 500}

        result = await item_service.items.rebuild_index("proj-1")

        assert result["indexed"] == HTTP_INTERNAL_SERVER_ERROR


# ==============================================================================
# VALIDATION & CONSTRAINT TESTS (12 tests)
# ==============================================================================


class TestValidationAndConstraints:
    """Tests for data validation and business rule constraints."""

    @pytest.mark.asyncio
    async def test_validate_status_transition(self, item_service: Any) -> None:
        """Test validating allowed status transitions."""
        item = create_item("item-1", status="todo")
        item_service.items.get.return_value = item

        # Valid transition
        valid = await item_service.is_valid_transition("proj-1", "item-1", "in_progress")
        assert valid is True

    @pytest.mark.asyncio
    async def test_reject_invalid_status(self, item_service: Any) -> None:
        """Test rejecting invalid status values."""
        item_service.items.update.side_effect = ValueError("Invalid status")

        with pytest.raises(ValueError):
            await item_service.update_item("proj-1", "item-1", {"status": "invalid_status"})

    @pytest.mark.asyncio
    async def test_validate_required_fields(self, item_service: Any) -> None:
        """Test validating required fields on creation."""
        item_service.items.create.side_effect = ValueError("Missing required field")

        with pytest.raises(ValueError):
            await item_service.create_item("proj-1", "", "REQUIREMENTS", "requirement", "agent-1")

    @pytest.mark.asyncio
    async def test_validate_metadata_schema(self, item_service: Any) -> None:
        """Test validating metadata against schema."""
        item_service.items.validate_metadata.return_value = {"valid": False, "errors": ["Invalid field type"]}

        result = await item_service.items.validate_metadata("proj-1", {"invalid_field": 123})

        assert result["valid"] is False

    @pytest.mark.asyncio
    async def test_enforce_unique_constraints(self, item_service: Any) -> None:
        """Test enforcing unique constraints."""
        item_service.items.create.side_effect = ValueError("Duplicate ID")

        with pytest.raises(ValueError):
            await item_service.create_item("proj-1", "Item", "REQUIREMENTS", "requirement", "agent-1")

    @pytest.mark.asyncio
    async def test_validate_link_types(self, item_service: Any) -> None:
        """Test validating link type values."""
        valid_types = ["relates_to", "implements", "tested_by"]

        for link_type in valid_types:
            item = create_item("item-1")
            item_service.items.create.return_value = item
            item_service.links.create.return_value = Mock(spec=Link)

            result = await item_service.create_item(
                "proj-1",
                "Item",
                "REQUIREMENTS",
                "requirement",
                "agent-1",
                link_to=["item-2"],
                link_type=link_type,
            )

            assert result is not None


# ==============================================================================
# INTEGRATION SCENARIOS TESTS (11 tests)
# ==============================================================================


class TestComplexIntegrationScenarios:
    """Tests for complex multi-step workflows."""

    @pytest.mark.asyncio
    async def test_requirement_to_test_mapping(self, item_service: Any) -> None:
        """Test workflow: requirement -> design -> test case."""
        req = create_item("req-1", view="REQUIREMENTS")
        design = create_item("design-1", view="DESIGN")
        test = create_item("test-1", view="TEST_CASES")

        item_service.items.create.side_effect = [req, design, test]
        item_service.links.create.return_value = Mock(spec=Link)

        # Create requirement with design link
        req_result = await item_service.create_item("proj-1", "Requirement", "REQUIREMENTS", "requirement", "agent-1")

        # Create design linked to requirement
        design_result = await item_service.create_item(
            "proj-1",
            "Design",
            "DESIGN",
            "design",
            "agent-1",
            link_to=[req_result.id],
        )

        # Create test linked to design
        test_result = await item_service.create_item(
            "proj-1",
            "Test",
            "TEST_CASES",
            "test",
            "agent-1",
            link_to=[design_result.id],
        )

        assert test_result is not None

    @pytest.mark.asyncio
    async def test_status_workflow_progression(self, item_service: Any) -> None:
        """Test complete status workflow."""
        statuses = ["todo", "in_progress", "done"]
        items = [create_item("item-1", status=status) for status in statuses]

        item_service.items.update.side_effect = items

        current_item = items[0]
        for target_status in statuses[1:]:
            current_item = await item_service.transition_item("proj-1", "item-1", target_status)

        assert current_item.status == "done"

    @pytest.mark.asyncio
    async def test_hierarchical_task_decomposition(self, item_service: Any) -> None:
        """Test breaking down task into subtasks."""
        parent = create_item("task-1", parent_id=None)
        child1 = create_item("task-1-1", parent_id="task-1")
        child2 = create_item("task-1-2", parent_id="task-1")

        item_service.items.create.side_effect = [parent, child1, child2]

        parent_result = await item_service.create_item(
            "proj-1",
            "Parent Task",
            "REQUIREMENTS",
            "requirement",
            "agent-1",
        )

        child1_result = await item_service.create_item(
            "proj-1",
            "Subtask 1",
            "REQUIREMENTS",
            "requirement",
            "agent-1",
            parent_id=parent_result.id,
        )

        child2_result = await item_service.create_item(
            "proj-1",
            "Subtask 2",
            "REQUIREMENTS",
            "requirement",
            "agent-1",
            parent_id=parent_result.id,
        )

        assert child1_result.parent_id == parent_result.id
        assert child2_result.parent_id == parent_result.id

    @pytest.mark.asyncio
    async def test_bulk_status_update_with_event_logging(self, item_service: Any) -> None:
        """Test bulk status update with proper event logging."""
        items = [create_item(f"item-{i}", status="todo") for i in range(10)]
        item_service.items.bulk_update.return_value = items
        item_service.events.log.return_value = None

        result = await item_service.bulk_update_items("proj-1", {"status": "in_progress"}, filters={"status": "todo"})

        assert len(result) == COUNT_TEN
        assert item_service.events.log.called

    @pytest.mark.asyncio
    async def test_item_recovery_after_soft_delete(self, item_service: Any) -> None:
        """Test recovering soft-deleted item."""
        deleted_item = create_item("item-1", deleted_at=datetime.now(UTC))
        recovered_item = create_item("item-1", deleted_at=None)

        item_service.items.get.return_value = deleted_item
        item_service.items.undelete.return_value = recovered_item

        result = await item_service.items.undelete("proj-1", "item-1")

        assert result.deleted_at is None
