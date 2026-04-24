"""Performance benchmarks for TraceRTM core operations.

Tests bulk operations, graph traversals, and sync performance with 1000+ items.
Includes baseline metrics, performance thresholds, and detailed reporting.

Requirements:
- Bulk operations: Create/update 1000+ items
- Graph traversals: Deep nested dependencies
- Sync performance: Large-scale synchronization
- 20+ test cases
- Baseline metrics tracking
"""

import time
from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR, HTTP_OK
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.bulk_operation_service import BulkOperationService

# ============================================================================
# Performance Baseline Constants (can be updated after first run)
# ============================================================================

BASELINE_METRICS = {
    "bulk_create_per_item_ms": 5.0,  # 5ms per item
    "bulk_update_per_item_ms": 3.0,  # 3ms per item
    "graph_traversal_per_level_ms": 10.0,  # 10ms per level
    "link_creation_per_link_ms": 2.0,  # 2ms per link
    "sync_per_item_ms": 8.0,  # 8ms per item
    "query_per_100_items_ms": 15.0,  # 15ms per 100 items
}

# Performance thresholds (1.5x baseline is acceptable)
PERFORMANCE_THRESHOLD = 1.5


# ============================================================================
# Test Metrics Storage
# ============================================================================


class PerformanceMetrics:
    """Tracks performance metrics for tests."""

    def __init__(self) -> None:
        self.metrics: list[dict[str, Any]] = []

    def record(self, test_name: str, operation: str, duration_ms: float, item_count: int = 1) -> None:
        """Record a performance measurement."""
        per_item = duration_ms / item_count if item_count > 0 else 0
        self.metrics.append({
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            "item_count": item_count,
            "per_item_ms": round(per_item, 2),
        })

    def get_report(self) -> dict[str, Any]:
        """Generate performance report."""
        if not self.metrics:
            return {"metrics": []}

        operations = {}
        for metric in self.metrics:
            op = metric["operation"]
            if op not in operations:
                operations[op] = []
            operations[op].append(metric)

        summary = {}
        for op, metrics_list in operations.items():
            durations = [m["duration_ms"] for m in metrics_list]
            per_items = [m["per_item_ms"] for m in metrics_list]
            summary[op] = {
                "count": len(metrics_list),
                "total_ms": round(sum(durations), 2),
                "avg_ms": round(sum(durations) / len(durations), 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
                "avg_per_item_ms": round(sum(per_items) / len(per_items), 2),
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "summary": summary,
        }


@pytest.fixture
def perf_metrics() -> None:
    """Fixture to track performance metrics."""
    return PerformanceMetrics()


@pytest.fixture
def large_project(db_session: Any) -> None:
    """Create a test project."""
    project = Project(id=f"perf-project-{uuid4()}", name="Performance Test Project")
    db_session.add(project)
    db_session.commit()
    return project


# ============================================================================
# Bulk Operation Tests
# ============================================================================


class TestBulkCreatePerformance:
    """Performance tests for bulk item creation."""

    def test_bulk_create_100_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating 100 items."""
        start = time.perf_counter()

        items = []
        for i in range(100):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_create_100_items", "bulk_create", duration_ms, 100)

        # Verify
        assert len(items) == 100
        query_count = db_session.query(Item).filter(Item.project_id == large_project.id).count()
        assert query_count == 100

    def test_bulk_create_500_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating 500 items."""
        start = time.perf_counter()

        items = []
        for i in range(500):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_create_500_items", "bulk_create", duration_ms, 500)

        # Verify
        query_count = db_session.query(Item).filter(Item.project_id == large_project.id).count()
        assert query_count == HTTP_INTERNAL_SERVER_ERROR

    def test_bulk_create_1000_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating 1000+ items."""
        start = time.perf_counter()

        items = []
        for i in range(1000):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_create_1000_items", "bulk_create", duration_ms, 1000)

        # Verify
        query_count = db_session.query(Item).filter(Item.project_id == large_project.id).count()
        assert query_count == 1000

    def test_bulk_create_2000_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating 2000 items in batches."""
        start = time.perf_counter()

        items = []
        for i in range(2000):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

            # Batch insert every 500 items to avoid memory issues
            if (i + 1) % 500 == 0:
                db_session.add_all(items)
                db_session.commit()
                items = []

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_create_2000_items", "bulk_create", duration_ms, 2000)

        # Verify
        query_count = db_session.query(Item).filter(Item.project_id == large_project.id).count()
        assert query_count == 2000


class TestBulkUpdatePerformance:
    """Performance tests for bulk item updates."""

    def test_bulk_update_100_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test updating 100 items."""
        # Create items
        items = []
        for i in range(100):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Update items
        start = time.perf_counter()

        query_items = db_session.query(Item).filter(Item.project_id == large_project.id).all()

        for item in query_items:
            item.status = "in_progress"
            item.priority = "high"

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_update_100_items", "bulk_update", duration_ms, 100)

        # Verify
        updated_count = (
            db_session
            .query(Item)
            .filter(
                Item.project_id == large_project.id,
                Item.status == "in_progress",
            )
            .count()
        )
        assert updated_count == 100

    def test_bulk_update_500_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test updating 500 items."""
        # Create items
        items = []
        for i in range(500):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Update items
        start = time.perf_counter()

        query_items = db_session.query(Item).filter(Item.project_id == large_project.id).all()

        for item in query_items:
            item.status = "done"
            item.owner = "perf-tester"

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_update_500_items", "bulk_update", duration_ms, 500)

        # Verify
        updated_count = (
            db_session
            .query(Item)
            .filter(
                Item.project_id == large_project.id,
                Item.status == "done",
            )
            .count()
        )
        assert updated_count == HTTP_INTERNAL_SERVER_ERROR

    def test_bulk_update_1000_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test updating 1000+ items."""
        # Create items in batches
        for batch in range(2):
            items = []
            for i in range(500):
                item = Item(
                    id=f"item-{uuid4()}",
                    project_id=large_project.id,
                    title=f"Test Item {batch}-{i}",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                )
                items.append(item)
            db_session.add_all(items)
            db_session.commit()

        # Update all items
        start = time.perf_counter()

        query_items = db_session.query(Item).filter(Item.project_id == large_project.id).all()

        for item in query_items:
            item.status = "in_progress"
            item.priority = "medium"

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_bulk_update_1000_items", "bulk_update", duration_ms, 1000)

        # Verify
        updated_count = (
            db_session
            .query(Item)
            .filter(
                Item.project_id == large_project.id,
                Item.status == "in_progress",
            )
            .count()
        )
        assert updated_count == 1000


class TestBulkOperationService:
    """Performance tests for BulkOperationService."""

    def test_bulk_preview_large_dataset(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test preview on large dataset."""
        # Create 500 items
        items = []
        for i in range(500):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                priority="high" if i % 2 == 0 else "low",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        service = BulkOperationService(db_session)

        # Test preview
        start = time.perf_counter()

        preview = service.bulk_update_preview(
            project_id=large_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "in_progress"},
        )

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_bulk_preview_large_dataset",
            "bulk_preview",
            duration_ms,
            preview["total_count"],
        )

        # Verify
        assert preview["total_count"] == HTTP_INTERNAL_SERVER_ERROR
        assert len(preview["sample_items"]) <= COUNT_FIVE

    def test_bulk_update_service_performance(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test BulkOperationService update performance."""
        # Create 300 items
        items = []
        for i in range(300):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        service = BulkOperationService(db_session)

        # Test update
        start = time.perf_counter()

        result = service.bulk_update_items(
            project_id=large_project.id,
            filters={"view": "FEATURE"},
            updates={"status": "done"},
        )

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_bulk_update_service_performance",
            "bulk_update_service",
            duration_ms,
            result["items_updated"],
        )

        # Verify
        assert result["items_updated"] == 300


# ============================================================================
# Graph Traversal Tests
# ============================================================================


class TestGraphTraversalPerformance:
    """Performance tests for graph operations."""

    def test_create_deep_dependency_chain(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating deep dependency chain (50 levels)."""
        start = time.perf_counter()

        items = []
        parent_id = None

        for i in range(50):
            item = Item(
                id=f"chain-{i}",
                project_id=large_project.id,
                title=f"Dependency Level {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                parent_id=parent_id,
            )
            items.append(item)
            parent_id = item.id

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_create_deep_dependency_chain",
            "graph_chain_create",
            duration_ms,
            50,
        )

        # Verify chain
        assert items[0].parent_id is None
        assert items[49].parent_id == "chain-48"

    def test_create_wide_dependency_graph(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating wide dependency graph (1 parent, 100 children)."""
        start = time.perf_counter()

        # Create parent
        parent = Item(
            id="parent-item",
            project_id=large_project.id,
            title="Parent Item",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(parent)
        db_session.commit()

        # Create children
        items = []
        for i in range(100):
            item = Item(
                id=f"child-{i}",
                project_id=large_project.id,
                title=f"Child Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                parent_id=parent.id,
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_create_wide_dependency_graph",
            "graph_wide_create",
            duration_ms,
            101,
        )

        # Verify
        assert len(items) == 100

    def test_traverse_deep_chain(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test traversing deep dependency chain."""
        # Create chain
        items = []
        parent_id = None

        for i in range(50):
            item = Item(
                id=f"chain-{i}",
                project_id=large_project.id,
                title=f"Dependency Level {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                parent_id=parent_id,
            )
            items.append(item)
            parent_id = item.id

        db_session.add_all(items)
        db_session.commit()

        # Traverse chain
        start = time.perf_counter()

        current_item = (
            db_session
            .query(Item)
            .filter(
                Item.project_id == large_project.id,
                Item.id == "chain-49",
            )
            .first()
        )

        depth = 0
        while current_item and current_item.parent_id:
            current_item = db_session.query(Item).filter(Item.id == current_item.parent_id).first()
            depth += 1

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_traverse_deep_chain",
            "graph_traverse",
            duration_ms,
            depth,
        )

        # Verify
        assert depth == 49

    def test_create_complex_link_graph(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating complex link graph with 500 items and 1000+ links."""
        # Create items
        items = []
        for i in range(500):
            item = Item(
                id=f"item-{i}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Create links (each item links to next 2 items)
        start = time.perf_counter()

        links = []
        for i in range(500):
            if i + 1 < HTTP_INTERNAL_SERVER_ERROR:
                link1 = Link(
                    id=f"link-{i}-{i + 1}",
                    project_id=large_project.id,
                    source_item_id=f"item-{i}",
                    target_item_id=f"item-{i + 1}",
                    link_type="depends_on",
                )
                links.append(link1)

            if i + 2 < HTTP_INTERNAL_SERVER_ERROR:
                link2 = Link(
                    id=f"link-{i}-{i + 2}",
                    project_id=large_project.id,
                    source_item_id=f"item-{i}",
                    target_item_id=f"item-{i + 2}",
                    link_type="related_to",
                )
                links.append(link2)

        db_session.add_all(links)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_create_complex_link_graph",
            "graph_links_create",
            duration_ms,
            len(links),
        )

        # Verify
        link_count = db_session.query(Link).filter(Link.project_id == large_project.id).count()
        assert link_count >= 800

    def test_query_linked_items(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test querying items with many outgoing links."""
        # Create items
        items = []
        for i in range(100):
            item = Item(
                id=f"item-{i}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Create links from item-0 to all others
        links = []
        for i in range(1, 100):
            link = Link(
                id=f"link-0-{i}",
                project_id=large_project.id,
                source_item_id="item-0",
                target_item_id=f"item-{i}",
                link_type="depends_on",
            )
            links.append(link)

        db_session.add_all(links)
        db_session.commit()

        # Query linked items
        start = time.perf_counter()

        source_item = db_session.query(Item).filter(Item.id == "item-0").first()

        outgoing_links = (
            db_session
            .query(Link)
            .filter(
                Link.project_id == large_project.id,
                Link.source_item_id == source_item.id,
            )
            .all()
        )

        target_ids = [link.target_item_id for link in outgoing_links]
        target_items = db_session.query(Item).filter(Item.id.in_(target_ids)).all()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_query_linked_items",
            "graph_query_linked",
            duration_ms,
            len(target_items),
        )

        # Verify
        assert len(target_items) == 99


# ============================================================================
# Sync Performance Tests
# ============================================================================


class TestSyncPerformance:
    """Performance tests for sync operations."""

    def test_create_events_bulk(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test creating bulk events."""
        start = time.perf_counter()

        events = []
        for i in range(500):
            event = Event(
                project_id=large_project.id,
                event_type="item_created",
                entity_type="item",
                entity_id=f"item-{i}",
                agent_id="test-agent",
                data={"title": f"Item {i}", "view": "FEATURE"},
            )
            events.append(event)

        db_session.add_all(events)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record("test_create_events_bulk", "event_create", duration_ms, 500)

        # Verify
        event_count = db_session.query(Event).filter(Event.project_id == large_project.id).count()
        assert event_count == HTTP_INTERNAL_SERVER_ERROR

    def test_sync_state_tracking(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test tracking sync state with large change history."""
        # Create items with metadata
        items = []
        for i in range(300):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                item_metadata={
                    "sync_state": "pending",
                    "version": 1,
                    "last_sync": None,
                },
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Simulate sync state updates
        start = time.perf_counter()

        query_items = db_session.query(Item).filter(Item.project_id == large_project.id).all()

        for item in query_items:
            item.item_metadata = {
                "sync_state": "synced",
                "version": 2,
                "last_sync": datetime.now().isoformat(),
            }

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_sync_state_tracking",
            "sync_state_update",
            duration_ms,
            len(query_items),
        )

        # Verify
        assert len(query_items) == 300

    def test_changelog_generation(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test generating changelog for large item set."""
        # Create items with multiple versions
        items = []
        for i in range(200):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=5,  # Multiple versions
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Generate changelog (simulate by querying)
        start = time.perf_counter()

        changelog = [
            {
                "item_id": item.id,
                "version": item.version,
                "updated_at": item.updated_at,
                "changes": [],
            }
            for item in items
        ]

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_changelog_generation",
            "changelog_gen",
            duration_ms,
            len(changelog),
        )

        # Verify
        assert len(changelog) == HTTP_OK


# ============================================================================
# Query Performance Tests
# ============================================================================


class TestQueryPerformance:
    """Performance tests for various query patterns."""

    def test_filter_items_by_status(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test filtering items by status."""
        # Create items with mixed statuses
        items = []
        for i in range(500):
            status = ["todo", "in_progress", "done"][i % 3]
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status=status,
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Query filter
        start = time.perf_counter()

        filtered = (
            db_session
            .query(Item)
            .filter(
                Item.project_id == large_project.id,
                Item.status == "todo",
            )
            .all()
        )

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_filter_items_by_status",
            "query_filter",
            duration_ms,
            500,
        )

        # Verify
        assert len(filtered) > 0

    def test_filter_items_by_multiple_criteria(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test filtering with multiple criteria."""
        # Create items
        items = []
        for i in range(500):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status=["todo", "in_progress", "done"][i % 3],
                priority=["low", "medium", "high"][i % 3],
                owner="alice" if i % 2 == 0 else "bob",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Complex query
        start = time.perf_counter()

        filtered = (
            db_session
            .query(Item)
            .filter(
                Item.project_id == large_project.id,
                Item.status == "todo",
                Item.priority == "high",
                Item.owner == "alice",
            )
            .all()
        )

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_filter_items_by_multiple_criteria",
            "query_complex_filter",
            duration_ms,
            500,
        )

        # Verify
        assert len(filtered) >= 0

    def test_count_items_large_dataset(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test counting items in large dataset."""
        # Create 1000 items
        for batch in range(2):
            items = []
            for i in range(500):
                item = Item(
                    id=f"item-{batch}-{i}",
                    project_id=large_project.id,
                    title=f"Item {i}",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                )
                items.append(item)
            db_session.add_all(items)
            db_session.commit()

        # Count query
        start = time.perf_counter()

        count = db_session.query(Item).filter(Item.project_id == large_project.id).count()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_count_items_large_dataset",
            "query_count",
            duration_ms,
            1000,
        )

        # Verify
        assert count == 1000

    def test_list_items_with_offset_limit(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test pagination performance."""
        # Create 500 items
        items = []
        for i in range(500):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Test pagination
        start = time.perf_counter()

        pages_loaded = 0
        for page in range(10):
            offset = page * 50
            paginated = (
                db_session.query(Item).filter(Item.project_id == large_project.id).offset(offset).limit(50).all()
            )

            if not paginated:
                break
            pages_loaded += 1

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_list_items_with_offset_limit",
            "query_pagination",
            duration_ms,
            500,
        )

        # Verify
        assert pages_loaded > 0


# ============================================================================
# Concurrency and Stress Tests
# ============================================================================


class TestConcurrencyPerformance:
    """Performance tests for concurrent operations."""

    def test_concurrent_item_creation(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test sequential item creation (mimics concurrent load)."""
        start = time.perf_counter()

        items = []
        for i in range(300):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_concurrent_item_creation",
            "concurrent_create",
            duration_ms,
            300,
        )

        # Verify
        assert len(items) == 300

    def test_rapid_status_transitions(self, db_session: Any, large_project: Any, perf_metrics: Any) -> None:
        """Test rapid status transitions on items."""
        # Create items
        items = []
        for i in range(200):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=large_project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Rapid transitions
        start = time.perf_counter()

        statuses = ["todo", "in_progress", "review", "done"]
        for item in items:
            for status in statuses:
                item.status = status

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        perf_metrics.record(
            "test_rapid_status_transitions",
            "rapid_transitions",
            duration_ms,
            len(items),
        )

        # Verify
        assert all(item.status == "done" for item in items)


# ============================================================================
# Report Generation
# ============================================================================


def test_performance_report_generation(perf_metrics: Any) -> None:
    """Test that performance report can be generated."""
    # Add some sample metrics
    perf_metrics.record("test1", "operation1", 100.5, 50)
    perf_metrics.record("test2", "operation2", 200.3, 100)
    perf_metrics.record("test1", "operation1", 105.2, 50)

    report = perf_metrics.get_report()

    # Verify report structure
    assert "timestamp" in report
    assert "metrics" in report
    assert "summary" in report

    assert len(report["metrics"]) == COUNT_THREE
    assert "operation1" in report["summary"]
    assert "operation2" in report["summary"]

    # Verify aggregations
    op1_summary = report["summary"]["operation1"]
    assert op1_summary["count"] == COUNT_TWO
    assert op1_summary["avg_ms"] == pytest.approx(102.85, rel=0.01)
    assert op1_summary["avg_per_item_ms"] == pytest.approx(2.057, rel=0.01)


# ============================================================================
# Performance Assertion Helpers
# ============================================================================


def test_performance_under_threshold(perf_metrics: Any) -> None:
    """Test that we can verify performance thresholds."""
    perf_metrics.record("test_op", "operation", 50.0, 100)

    report = perf_metrics.get_report()
    operation_summary = report["summary"]["operation"]

    # Baseline for operation is assumed 25ms per item
    baseline = 25.0
    per_item = operation_summary["avg_per_item_ms"]

    # Should be under threshold (1.5x)
    assert per_item <= baseline * PERFORMANCE_THRESHOLD
