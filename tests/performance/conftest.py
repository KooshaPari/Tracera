"""Performance testing configuration and fixtures.

Provides setup for benchmark tests, performance measurements, and baselines.
"""

import asyncio
import contextlib
import json
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio

# ============================================================
# Performance Thresholds and Baselines
# ============================================================


@dataclass
class PerformanceBaseline:
    """Performance baseline metrics for operations."""

    operation: str
    avg_time_ms: float
    p95_time_ms: float
    p99_time_ms: float
    throughput_ops_sec: float
    max_memory_mb: float
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PerformanceThresholds:
    """Performance thresholds for different operations."""

    # Item operations (single)
    ITEM_CREATE_MS = 50  # Single item creation
    ITEM_UPDATE_MS = 40  # Single item update
    ITEM_QUERY_MS = 20  # Single item query
    ITEM_DELETE_MS = 30  # Single item deletion

    # Link operations (single)
    LINK_CREATE_MS = 60  # Single link creation
    LINK_QUERY_MS = 30  # Single link query
    LINK_DELETE_MS = 40  # Single link deletion

    # Bulk operations
    BULK_CREATE_ITEMS_1000_SEC = 5.0  # Create 1000 items in 5 seconds
    BULK_UPDATE_ITEMS_1000_SEC = 4.0  # Update 1000 items in 4 seconds
    BULK_DELETE_ITEMS_1000_SEC = 3.0  # Delete 1000 items in 3 seconds

    # Query operations
    QUERY_ALL_ITEMS_1000_MS = 100  # Query 1000 items
    GRAPH_TRAVERSAL_1000_NODES_MS = 500  # Traverse 1000-node graph

    # Concurrent operations
    CONCURRENT_ITEMS_100_USERS_SEC = 2.0  # 100 concurrent item creates
    CONCURRENT_LINKS_50_USERS_SEC = 1.5  # 50 concurrent link operations

    # Database query performance
    DB_INDEX_LOOKUP_MS = 5  # Indexed column lookup
    DB_JOIN_QUERY_MS = 20  # Query with joins
    DB_AGGREGATION_QUERY_MS = 50  # Aggregation query


# ============================================================
# Benchmark Fixtures
# ============================================================


@pytest.fixture(scope="session")
def performance_baselines_file() -> Path:
    """Get path to performance baselines file."""
    return Path(__file__).parent / "performance_baselines.json"


@pytest.fixture
def perf_tracker() -> None:
    """Track performance metrics during tests."""

    class PerfTracker:
        def __init__(self) -> None:
            self.measurements: list[dict[str, Any]] = []

        def record(self, name: str, elapsed_ms: float, items_count: int = 1) -> None:
            """Record a performance measurement."""
            self.measurements.append({
                "name": name,
                "elapsed_ms": elapsed_ms,
                "items_count": items_count,
                "throughput_per_sec": (items_count / elapsed_ms * 1000) if elapsed_ms > 0 else 0,
                "timestamp": time.time(),
            })

        def get_summary(self) -> dict[str, Any]:
            """Get summary of measurements."""
            if not self.measurements:
                return {}

            return {
                "total_measurements": len(self.measurements),
                "total_items_processed": sum(m["items_count"] for m in self.measurements),
                "total_time_sec": sum(m["elapsed_ms"] for m in self.measurements) / 1000,
                "avg_throughput": sum(m["throughput_per_sec"] for m in self.measurements) / len(self.measurements),
            }

        def report(self) -> str:
            """Generate performance report."""
            summary = self.get_summary()
            lines = ["Performance Summary", "=" * 50]
            for key, value in summary.items():
                if isinstance(value, float):
                    lines.append(f"{key}: {value:.2f}")
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)

    return PerfTracker()


# ============================================================
# Timing Utilities
# ============================================================


@contextlib.contextmanager
def measure_time(name: str, perf_tracker: Any = None, threshold_ms: float | None = None) -> None:
    """Context manager to measure execution time.

    Args:
        name: Operation name
        perf_tracker: Optional PerfTracker to record measurement
        threshold_ms: Optional threshold to assert against

    Yields:
        Timing info dict
    """
    start = time.perf_counter()
    timing = {"name": name, "start": start}

    try:
        yield timing
    finally:
        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000
        timing["elapsed_ms"] = elapsed_ms
        timing["elapsed_sec"] = elapsed

        if perf_tracker:
            perf_tracker.record(name, elapsed_ms)

        if threshold_ms is not None and elapsed_ms > threshold_ms:
            pytest.fail(f"{name} exceeded threshold: {elapsed_ms:.2f}ms > {threshold_ms:.2f}ms")


def assert_performance(elapsed_ms: float, threshold_ms: float, operation_name: str) -> None:
    """Assert that operation completed within performance threshold.

    Args:
        elapsed_ms: Elapsed time in milliseconds
        threshold_ms: Maximum allowed time in milliseconds
        operation_name: Name of operation for error message

    Raises:
        AssertionError: If operation exceeded threshold
    """
    assert elapsed_ms <= threshold_ms, (
        f"{operation_name} performance degradation: {elapsed_ms:.2f}ms > {threshold_ms:.2f}ms threshold"
    )


# ============================================================
# Data Generation
# ============================================================


class PerfDataGenerator:
    """Generate test data for performance testing."""

    @staticmethod
    def create_items(count: int, project_id: str = "perf-proj") -> list[dict[str, Any]]:
        """Generate test items."""
        return [
            {
                "id": f"item-{i}",
                "project_id": project_id,
                "title": f"Performance Test Item {i}",
                "view": "FEATURE",
                "item_type": "feature",
                "status": "todo",
                "priority": "medium",
                "description": f"Test item for performance benchmarking {i}" * 10,
                "version": 1,
            }
            for i in range(count)
        ]

    @staticmethod
    def create_links(count: int, project_id: str = "perf-proj") -> list[dict[str, Any]]:
        """Generate test links."""
        return [
            {
                "id": f"link-{i}",
                "project_id": project_id,
                "source_id": f"item-{i % 100}",
                "target_id": f"item-{(i + 1) % 100}",
                "link_type": "depends_on",
                "description": f"Test link {i}",
            }
            for i in range(count)
        ]


# ============================================================
# Performance Database Fixtures
# ============================================================


@pytest.fixture
def sync_engine() -> None:
    """Synchronous SQLAlchemy engine for performance tests."""
    import tempfile

    from sqlalchemy import create_engine

    from tracertm.models.base import Base

    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = temp_db.name
    temp_db.close()

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    # Create tables
    if Base is not None:
        Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    try:
        Base.metadata.drop_all(engine)
        engine.dispose()
    finally:
        try:
            Path(db_path).unlink()
        except Exception:
            pass


@pytest.fixture
def perf_sync_db_engine(sync_engine: Any) -> None:
    """Alias for sync_engine fixture (backward compatibility)."""
    return sync_engine


# pytest-benchmark is registered in the root conftest.py
