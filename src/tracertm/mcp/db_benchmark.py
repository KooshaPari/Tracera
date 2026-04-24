"""MCP Database Optimization Benchmark.

Compares performance before/after optimizations:
- Connection pooling
- Query caching
- Eager loading
"""

import asyncio
import time
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from tracertm.database.connection import DatabaseConnection
from tracertm.mcp.database_manager import get_database_manager
from tracertm.mcp.query_optimizer import QueryOptimizer
from tracertm.models.item import Item

# Target improvement percentage for benchmark success
_TARGET_IMPROVEMENT_PCT = 50
# Minimum CLI args: script name, database_url, project_id
_MIN_CLI_ARGS = 3
# Database query limits
_QUERY_LIMIT = 50
# Progress update frequency
_PROGRESS_UPDATE_FREQ = 10
# Number of items to process for N+1 query simulation
_ITEMS_TO_PROCESS = 10
# Number of unique cache keys
_UNIQUE_CACHE_KEYS = 10
# Cache TTL in seconds
_CACHE_TTL_SECONDS = 300


class BenchmarkRunner:
    """Run performance benchmarks comparing old vs new implementation."""

    def __init__(self, database_url: str) -> None:
        """Initialize benchmark runner.

        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.results: dict[str, object] = {}

    def benchmark_sync_queries(
        self, project_id: str, iterations: int = _PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ
    ) -> None:
        """Benchmark old synchronous queries without pooling."""
        # Create new connection for each iteration (simulates old behavior)
        times = []
        for i in range(iterations):
            start = time.perf_counter()

            db = DatabaseConnection(self.database_url)
            db.connect()
            session = Session(db.engine)

            # Query items
            items: list[Item] = (
                session
                .query(Item)
                .filter(Item.project_id == project_id, Item.deleted_at.is_(None))
                .limit(_QUERY_LIMIT)
                .all()
            )

            # N+1 query: Access links for each item
            for item in items[:_ITEMS_TO_PROCESS]:  # Just first N items to keep it reasonable
                _ = len(item.source_links or [])
                _ = len(item.target_links or [])

            session.close()
            db.close()

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % _PROGRESS_UPDATE_FREQ == 0:
                pass

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results["old_implementation"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "iterations": iterations,
        }

    async def benchmark_async_pooled(
        self,
        project_id: str,
        iterations: int = _PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ,
    ) -> None:
        """Benchmark new async queries with connection pooling."""
        db_manager = await get_database_manager()

        times = []
        for i in range(iterations):
            start = time.perf_counter()

            async with db_manager.session() as session:
                # Query items
                query = (
                    select(Item)
                    .where(
                        Item.project_id == project_id,
                        Item.deleted_at.is_(None),
                    )
                    .limit(_QUERY_LIMIT)
                )

                result = await session.execute(query)
                items = result.scalars().all()

                # N+1 query: Access links
                for item in items[:_ITEMS_TO_PROCESS]:
                    _ = len(item.source_links or [])
                    _ = len(item.target_links or [])

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % _PROGRESS_UPDATE_FREQ == 0:
                pass

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results["pooled_implementation"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "iterations": iterations,
        }

    async def benchmark_eager_loading(
        self,
        project_id: str,
        iterations: int = _PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ,
    ) -> None:
        """Benchmark with eager loading (no N+1)."""
        db_manager = await get_database_manager()

        times = []
        for i in range(iterations):
            start = time.perf_counter()

            async with db_manager.session() as session:
                # Use QueryOptimizer for eager loading
                items = await QueryOptimizer.get_items_with_links(
                    session,
                    project_id,
                    limit=_QUERY_LIMIT,
                )

                # Access links (already loaded)
                for item in items[:_ITEMS_TO_PROCESS]:
                    src_links = getattr(item, "source_links", None) or []
                    tgt_links = getattr(item, "target_links", None) or []
                    _ = len(src_links)
                    _ = len(tgt_links)

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % _PROGRESS_UPDATE_FREQ == 0:
                pass

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results["eager_loading"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "iterations": iterations,
        }

    async def benchmark_with_cache(self, project_id: str, iterations: int = 100) -> None:
        """Benchmark with query caching."""
        from tracertm.mcp.cache import get_query_cache

        cache = get_query_cache()
        await cache.clear()  # Start fresh

        db_manager = await get_database_manager()

        times = []
        cache_hits = 0

        for i in range(iterations):
            start = time.perf_counter()

            # Simulate cached query pattern
            cache_key = f"benchmark_query_{i % _UNIQUE_CACHE_KEYS}"  # N unique queries

            cached = await cache.get(cache_key, project_id=project_id)

            if cached is None:
                async with db_manager.session() as session:
                    items = await QueryOptimizer.get_items_with_links(
                        session,
                        project_id,
                        limit=50,
                    )
                    await cache.set(cache_key, items, ttl=_CACHE_TTL_SECONDS, project_id=project_id)
            else:
                items = cast("list[Item]", cached)
                cache_hits += 1

            # Access data
            for item in items[:_ITEMS_TO_PROCESS]:
                src_links = getattr(item, "source_links", None) or []
                _ = len(src_links)

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % _PROGRESS_UPDATE_FREQ == 0:
                pass

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        hit_rate = cache_hits / iterations

        self.results["with_caching"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "cache_hits": cache_hits,
            "hit_rate": hit_rate,
            "iterations": iterations,
        }

    def print_summary(self) -> None:
        """Print comparison summary."""
        if "old_implementation" in self.results and "pooled_implementation" in self.results:
            old_avg = cast("dict[str, object]", self.results["old_implementation"])["avg_ms"]
            pooled_avg = cast("dict[str, object]", self.results["pooled_implementation"])["avg_ms"]
            ((old_avg - pooled_avg) / old_avg) * 100  # type: ignore[operator]

        if "pooled_implementation" in self.results and "eager_loading" in self.results:
            pooled_avg = cast("dict[str, object]", self.results["pooled_implementation"])["avg_ms"]
            eager_avg = cast("dict[str, object]", self.results["eager_loading"])["avg_ms"]
            ((pooled_avg - eager_avg) / pooled_avg) * 100  # type: ignore[operator]

        if "eager_loading" in self.results and "with_caching" in self.results:
            eager_avg = cast("dict[str, object]", self.results["eager_loading"])["avg_ms"]
            cache_avg = cast("dict[str, object]", self.results["with_caching"])["avg_ms"]
            ((eager_avg - cache_avg) / eager_avg) * 100  # type: ignore[operator]
            cast("dict[str, object]", self.results["with_caching"])["hit_rate"]

        if "old_implementation" in self.results and "with_caching" in self.results:
            old_avg = cast("dict[str, object]", self.results["old_implementation"])["avg_ms"]
            final_avg = cast("dict[str, object]", self.results["with_caching"])["avg_ms"]
            total_improvement = ((old_avg - final_avg) / old_avg) * 100  # type: ignore[operator]

            if total_improvement >= _TARGET_IMPROVEMENT_PCT:
                pass


async def run_benchmark(database_url: str, project_id: str) -> None:
    """Run full benchmark suite."""
    runner = BenchmarkRunner(database_url)

    # Run benchmarks
    runner.benchmark_sync_queries(project_id, iterations=_PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ)
    await runner.benchmark_async_pooled(project_id, iterations=_PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ)
    await runner.benchmark_eager_loading(project_id, iterations=_PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ)
    await runner.benchmark_with_cache(project_id, iterations=_PROGRESS_UPDATE_FREQ * _PROGRESS_UPDATE_FREQ)

    # Print summary
    runner.print_summary()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < _MIN_CLI_ARGS:
        sys.exit(1)

    database_url = sys.argv[1]
    project_id = sys.argv[2]

    asyncio.run(run_benchmark(database_url, project_id))
