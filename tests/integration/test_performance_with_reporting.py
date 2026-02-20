"""Performance benchmarks with detailed reporting and metric analysis.

This extended test suite captures performance metrics with more granular
timing data and generates comprehensive performance reports.
"""

import json
import time
from datetime import datetime
from pathlib import Path

# ============================================================================
# Metrics Collection and Reporting
# ============================================================================
from typing import Any
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class PerformanceReporter:
    """Generates detailed performance reports with analysis."""

    def __init__(self, output_dir: str = "performance_reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metrics = {}

    def record_test(self, test_name: str, duration_ms: float, item_count: int, details: dict | None = None) -> None:
        """Record test metrics."""
        if test_name not in self.metrics:
            self.metrics[test_name] = {
                "runs": [],
                "item_count": item_count,
                "details": details or {},
            }

        self.metrics[test_name]["runs"].append({
            "timestamp": datetime.now().isoformat(),
            "duration_ms": round(duration_ms, 2),
            "per_item_ms": round(duration_ms / max(item_count, 1), 2),
        })

    def generate_json_report(self, filename: str = "performance_metrics.json") -> None:
        """Generate JSON report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "tests": {},
        }

        total_duration = 0
        total_items = 0

        for test_name, data in self.metrics.items():
            runs = data["runs"]
            durations = [r["duration_ms"] for r in runs]
            per_items = [r["per_item_ms"] for r in runs]

            summary = {
                "item_count": data["item_count"],
                "runs": len(runs),
                "total_duration_ms": round(sum(durations), 2),
                "avg_duration_ms": round(sum(durations) / len(durations), 2),
                "min_duration_ms": round(min(durations), 2),
                "max_duration_ms": round(max(durations), 2),
                "avg_per_item_ms": round(sum(per_items) / len(per_items), 2),
            }

            report["tests"][test_name] = {
                "summary": summary,
                "runs": runs,
                "details": data["details"],
            }

            total_duration += summary["total_duration_ms"]
            total_items += data["item_count"]

        report["summary"] = {
            "total_duration_ms": round(total_duration, 2),
            "total_items_processed": total_items,
            "test_count": len(self.metrics),
        }

        filepath = self.output_dir / filename
        with Path(filepath).open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return filepath

    def generate_text_report(self, filename: str = "performance_report.txt") -> None:
        """Generate human-readable text report."""
        lines = [
            "=" * 80,
            "PERFORMANCE BENCHMARK REPORT",
            "=" * 80,
            f"Generated: {datetime.now().isoformat()}",
            "",
        ]

        # Overall summary
        total_duration = sum(sum(r["duration_ms"] for r in data["runs"]) for data in self.metrics.values())
        total_items = sum(data["item_count"] for data in self.metrics.values())

        lines.extend([
            "OVERALL SUMMARY",
            "-" * 80,
            f"Total Tests: {len(self.metrics)}",
            f"Total Items Processed: {total_items:,}",
            f"Total Duration: {total_duration:.2f}ms ({total_duration / 1000:.2f}s)",
            f"Average Per Item: {total_duration / max(total_items, 1):.4f}ms",
            "",
        ])

        # Per-test details
        lines.extend([
            "PER-TEST BREAKDOWN",
            "-" * 80,
        ])

        for test_name, data in sorted(self.metrics.items()):
            runs = data["runs"]
            durations = [r["duration_ms"] for r in runs]
            per_items = [r["per_item_ms"] for r in runs]

            lines.extend([
                "",
                f"Test: {test_name}",
                f"  Items: {data['item_count']}",
                f"  Runs: {len(runs)}",
                f"  Duration: {sum(durations):.2f}ms (avg: {sum(durations) / len(durations):.2f}ms)",
                f"  Per Item: avg={sum(per_items) / len(per_items):.4f}ms, min={min(per_items):.4f}ms, max={max(per_items):.4f}ms",
            ])

            if data["details"]:
                for key, value in data["details"].items():
                    lines.append(f"    {key}: {value}")

        lines.extend([
            "",
            "=" * 80,
        ])

        filepath = self.output_dir / filename
        Path(filepath).write_text("\n".join(lines), encoding="utf-8")

        return filepath


@pytest.fixture
def reporter() -> None:
    """Fixture to provide performance reporter."""
    return PerformanceReporter()


# ============================================================================
# Detailed Performance Tests
# ============================================================================


class TestDetailedBulkPerformance:
    """Detailed performance tests with fine-grained metrics."""

    def test_bulk_create_with_metadata(self, db_session: Any, reporter: Any) -> None:
        """Test bulk creation with metadata tracking."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        start = time.perf_counter()

        items = []
        for i in range(500):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                item_metadata={
                    "created_batch": True,
                    "batch_index": i,
                    "priority_score": i % 5,
                },
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_bulk_create_with_metadata",
            duration_ms,
            500,
            {"metadata_size": "large", "batch_size": 500},
        )

    def test_bulk_update_with_version_tracking(self, db_session: Any, reporter: Any) -> None:
        """Test bulk update with version tracking."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create items
        items = []
        for i in range(300):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                version=1,
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Update with version tracking
        start = time.perf_counter()

        for item in items:
            item.status = "in_progress"
            item.version = 2

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_bulk_update_with_version_tracking",
            duration_ms,
            300,
            {"version_increment": 1},
        )

    def test_bulk_delete_simulation(self, db_session: Any, reporter: Any) -> None:
        """Test bulk deletion simulation (soft delete with timestamp)."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create items
        items = []
        for i in range(400):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=project.id,
                title=f"Test Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Soft delete
        start = time.perf_counter()

        for item in items:
            item.deleted_at = datetime.now()

        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_bulk_delete_simulation",
            duration_ms,
            400,
            {"operation": "soft_delete"},
        )


class TestDetailedGraphPerformance:
    """Detailed graph operation performance."""

    def test_hierarchical_tree_creation(self, db_session: Any, reporter: Any) -> None:
        """Test creating a binary tree structure."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        start = time.perf_counter()

        # Create binary tree (depth 7 = 127 nodes)
        items = []
        item_map = {}

        def create_tree(level: Any, index: Any, parent_id: Any = None) -> None:
            item_id = f"item-{level}-{index}"
            item = Item(
                id=item_id,
                project_id=project.id,
                title=f"Node {level}-{index}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                parent_id=parent_id,
            )
            items.append(item)
            item_map[item_id] = item

            if level < 6:  # Max depth
                create_tree(level + 1, index * 2, item_id)
                create_tree(level + 1, index * 2 + 1, item_id)

        create_tree(0, 0)

        db_session.add_all(items)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_hierarchical_tree_creation",
            duration_ms,
            len(items),
            {"tree_depth": 7, "structure": "binary_tree"},
        )

    def test_mesh_network_creation(self, db_session: Any, reporter: Any) -> None:
        """Test creating a mesh network of links (N items, N^2 potential links)."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create items
        items = []
        for i in range(30):  # 30 items = 900 potential links
            item = Item(
                id=f"item-{i}",
                project_id=project.id,
                title=f"Node {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Create mesh links
        start = time.perf_counter()

        links = []
        for i in range(30):
            for j in range(i + 1, 30):
                link = Link(
                    id=f"link-{i}-{j}",
                    project_id=project.id,
                    source_item_id=f"item-{i}",
                    target_item_id=f"item-{j}",
                    link_type="related_to",
                )
                links.append(link)

        db_session.add_all(links)
        db_session.commit()

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_mesh_network_creation",
            duration_ms,
            len(links),
            {"nodes": 30, "potential_links": 435},
        )

    def test_graph_traversal_bfs(self, db_session: Any, reporter: Any) -> None:
        """Test breadth-first traversal performance."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create star graph (1 center, 200 periphery)
        center = Item(
            id="center",
            project_id=project.id,
            title="Center Node",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(center)
        db_session.commit()

        items = []
        for i in range(200):
            item = Item(
                id=f"node-{i}",
                project_id=project.id,
                title=f"Node {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Create star links
        links = []
        for i in range(200):
            link = Link(
                id=f"link-center-{i}",
                project_id=project.id,
                source_item_id="center",
                target_item_id=f"node-{i}",
                link_type="depends_on",
            )
            links.append(link)

        db_session.add_all(links)
        db_session.commit()

        # BFS traversal
        start = time.perf_counter()

        visited = set()
        queue = ["center"]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)

            # Query outgoing links
            outgoing = (
                db_session
                .query(Link)
                .filter(
                    Link.source_item_id == current_id,
                    Link.project_id == project.id,
                )
                .all()
            )

            queue.extend(link.target_item_id for link in outgoing if link.target_item_id not in visited)

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_graph_traversal_bfs",
            duration_ms,
            len(visited),
            {"traversal_type": "breadth_first", "nodes_visited": len(visited)},
        )


class TestDetailedQueryPerformance:
    """Detailed query performance benchmarks."""

    def test_range_query_performance(self, db_session: Any, reporter: Any) -> None:
        """Test range queries on large datasets."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create items with numeric metadata
        items = []
        for i in range(800):
            item = Item(
                id=f"item-{uuid4()}",
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
                item_metadata={"score": i, "timestamp": i * 1000},
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Range query (simulated by filtering)
        start = time.perf_counter()

        # In real scenario, this would be a database range query
        all_items = db_session.query(Item).filter(Item.project_id == project.id).all()

        filtered = [item for item in all_items if 200 <= item.item_metadata.get("score", 0) <= 600]

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_range_query_performance",
            duration_ms,
            len(filtered),
            {"query_type": "range", "range": "200-600", "result_count": len(filtered)},
        )

    def test_join_query_performance(self, db_session: Any, reporter: Any) -> None:
        """Test join query performance with items and links."""
        project = Project(id=f"proj-{uuid4()}", name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create items
        items = []
        for i in range(250):
            item = Item(
                id=f"item-{i}",
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            items.append(item)

        db_session.add_all(items)
        db_session.commit()

        # Create many links
        links = []
        for i in range(250):
            for j in range(5):  # Each item has 5 outgoing links
                if i + j + 1 < 250:
                    link = Link(
                        id=f"link-{i}-{j}",
                        project_id=project.id,
                        source_item_id=f"item-{i}",
                        target_item_id=f"item-{i + j + 1}",
                        link_type="depends_on",
                    )
                    links.append(link)

        db_session.add_all(links)
        db_session.commit()

        # Join query
        start = time.perf_counter()

        # Get items with link counts
        from sqlalchemy import and_, func

        item_links = (
            db_session
            .query(Item.id, Item.title, func.count(Link.id).label("link_count"))
            .outerjoin(Link, and_(Item.id == Link.source_item_id, Link.project_id == project.id))
            .filter(Item.project_id == project.id)
            .group_by(Item.id)
            .all()
        )

        duration_ms = (time.perf_counter() - start) * 1000
        reporter.record_test(
            "test_join_query_performance",
            duration_ms,
            len(item_links),
            {"query_type": "join_with_aggregation", "result_count": len(item_links)},
        )


# ============================================================================
# Session Fixture for Detailed Tests
# ============================================================================


@pytest.fixture
def db_session_for_perf(db_session: Any) -> None:
    """Provide database session for performance tests."""
    return db_session


# ============================================================================
# Report Generation Tests
# ============================================================================


def test_generate_performance_reports(reporter: Any) -> None:
    """Test that performance reports can be generated."""
    # Simulate some test runs
    reporter.record_test("test_1", 100.0, 50)
    reporter.record_test("test_1", 105.0, 50)
    reporter.record_test("test_2", 200.0, 100)

    # Generate reports
    json_path = reporter.generate_json_report()
    text_path = reporter.generate_text_report()

    # Verify files exist
    assert json_path.exists()
    assert text_path.exists()

    # Verify JSON structure
    with Path(json_path).open(encoding="utf-8") as f:
        data = json.load(f)
        assert "timestamp" in data
        assert "tests" in data
        assert "test_1" in data["tests"]
        assert data["tests"]["test_1"]["summary"]["runs"] == COUNT_TWO

    # Verify text report
    text_content = text_path.read_text()
    assert "PERFORMANCE BENCHMARK REPORT" in text_content
    assert "test_1" in text_content
    assert "test_2" in text_content
