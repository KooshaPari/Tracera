"""Benchmarking service for materialized views and SSOT operations."""

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, ClassVar

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

TARGET_MS_INCREMENTAL = 1000
TARGET_MS_FULL = 5000


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark."""

    operation: str
    duration_ms: float
    row_count: int
    success: bool
    error: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ViewPerformance:
    """Performance metrics for a materialized view."""

    view_name: str
    query_time_ms: float
    row_count: int
    size_bytes: int
    meets_target: bool
    target_ms: float


class BenchmarkService:
    """Service for benchmarking materialized views and SSOT operations."""

    # Performance targets for each view (in milliseconds)
    PERFORMANCE_TARGETS: ClassVar[dict[str, int]] = {
        "traceability_matrix": 50,
        "impact_analysis": 100,
        "coverage_analysis": 50,
        "dependency_graph": 100,
        "timeline_view": 100,
        "status_dashboard": 50,
        "search_index": 20,
        "agent_interface": 30,
    }

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def benchmark_view_query(self, view_name: str, limit: int = 100) -> BenchmarkResult:
        """Benchmark a single materialized view query.

        Args:
            view_name: Name of the materialized view
            limit: Number of rows to fetch (default: 100)

        Returns:
            BenchmarkResult with timing and metadata
        """
        try:
            if view_name not in self.PERFORMANCE_TARGETS:
                return BenchmarkResult(
                    operation=f"query_{view_name}",
                    duration_ms=0,
                    row_count=0,
                    success=False,
                    error=f"Unknown view: {view_name}",
                )
            start_time = time.perf_counter()
            # view_name validated against PERFORMANCE_TARGETS allowlist; limit is a bound param
            stmt = text(f"SELECT * FROM {view_name} LIMIT :limit").bindparams(limit=limit)  # nosec B608
            result = await self.session.execute(stmt)
            rows = result.fetchall()

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return BenchmarkResult(
                operation=f"query_{view_name}",
                duration_ms=duration_ms,
                row_count=len(rows),
                success=True,
                metadata={
                    "view_name": view_name,
                    "limit": limit,
                    "target_ms": self.PERFORMANCE_TARGETS.get(view_name, 100),
                    "meets_target": duration_ms < self.PERFORMANCE_TARGETS.get(view_name, 100),
                },
            )
        except (OperationalError, ValueError) as e:
            return BenchmarkResult(
                operation=f"query_{view_name}",
                duration_ms=0,
                row_count=0,
                success=False,
                error=str(e),
            )

    async def benchmark_all_views(self) -> list[ViewPerformance]:
        """Benchmark all materialized views.

        Returns:
            List of ViewPerformance objects
        """
        results = []

        for view_name, target_ms in self.PERFORMANCE_TARGETS.items():
            # Benchmark query
            benchmark = await self.benchmark_view_query(view_name)

            # Get view size (view_name validated against PERFORMANCE_TARGETS allowlist)
            size_result = await self.session.execute(text(f"SELECT pg_total_relation_size('{view_name}')"))  # nosec B608
            size_bytes = size_result.scalar() or 0

            results.append(
                ViewPerformance(
                    view_name=view_name,
                    query_time_ms=benchmark.duration_ms,
                    row_count=benchmark.row_count,
                    size_bytes=size_bytes,
                    meets_target=benchmark.duration_ms < target_ms,
                    target_ms=target_ms,
                ),
            )

        return results

    async def benchmark_refresh_incremental(self) -> BenchmarkResult:
        """Benchmark incremental refresh operation.

        Returns:
            BenchmarkResult with timing
        """
        try:
            start_time = time.perf_counter()

            await self.session.execute(text("SELECT refresh_materialized_views_incremental()"))
            await self.session.commit()

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return BenchmarkResult(
                operation="refresh_incremental",
                duration_ms=duration_ms,
                row_count=0,
                success=True,
                metadata={
                    "target_ms": TARGET_MS_INCREMENTAL,
                    "meets_target": duration_ms < TARGET_MS_INCREMENTAL,
                },
            )
        except (OperationalError, ValueError) as e:
            return BenchmarkResult(
                operation="refresh_incremental",
                duration_ms=0,
                row_count=0,
                success=False,
                error=str(e),
            )

    async def benchmark_refresh_full(self) -> BenchmarkResult:
        """Benchmark full refresh operation.

        Returns:
            BenchmarkResult with timing
        """
        try:
            start_time = time.perf_counter()

            await self.session.execute(text("SELECT refresh_materialized_views_full()"))
            await self.session.commit()

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            return BenchmarkResult(
                operation="refresh_full",
                duration_ms=duration_ms,
                row_count=0,
                success=True,
                metadata={
                    "target_ms": TARGET_MS_FULL,
                    "meets_target": duration_ms < TARGET_MS_FULL,
                },
            )
        except (OperationalError, ValueError) as e:
            return BenchmarkResult(
                operation="refresh_full",
                duration_ms=0,
                row_count=0,
                success=False,
                error=str(e),
            )

    async def get_performance_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report.

        Returns:
            Dict with performance metrics for all views and operations
        """
        # Benchmark all views
        view_results = await self.benchmark_all_views()

        # Benchmark refresh operations
        incremental_result = await self.benchmark_refresh_incremental()
        full_result = await self.benchmark_refresh_full()

        # Calculate summary statistics
        total_views = len(view_results)
        views_meeting_target = sum(1 for v in view_results if v.meets_target)
        avg_query_time = sum(v.query_time_ms for v in view_results) / total_views if total_views > 0 else 0

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": {
                "total_views": total_views,
                "views_meeting_target": views_meeting_target,
                "target_compliance_rate": (views_meeting_target / total_views * 100 if total_views > 0 else 0),
                "avg_query_time_ms": avg_query_time,
            },
            "views": [
                {
                    "name": v.view_name,
                    "query_time_ms": v.query_time_ms,
                    "target_ms": v.target_ms,
                    "meets_target": v.meets_target,
                    "row_count": v.row_count,
                    "size_mb": v.size_bytes / (1024 * 1024),
                }
                for v in view_results
            ],
            "refresh_operations": {
                "incremental": {
                    "duration_ms": incremental_result.duration_ms,
                    "target_ms": 1000,
                    "meets_target": (
                        incremental_result.metadata.get("meets_target", False) if incremental_result.metadata else False
                    ),
                    "success": incremental_result.success,
                },
                "full": {
                    "duration_ms": full_result.duration_ms,
                    "target_ms": 5000,
                    "meets_target": (
                        full_result.metadata.get("meets_target", False) if full_result.metadata else False
                    ),
                    "success": full_result.success,
                },
            },
        }
