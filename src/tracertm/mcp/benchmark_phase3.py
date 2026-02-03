"""
Phase 3 Database Optimization Benchmark.

Compares performance before/after optimizations:
- Connection pooling
- Query caching
- Eager loading
"""

import asyncio
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from tracertm.database.connection import DatabaseConnection
from tracertm.mcp.database_manager import get_database_manager
from tracertm.mcp.query_optimizer import QueryOptimizer
from tracertm.models.item import Item


class BenchmarkRunner:
    """Run performance benchmarks comparing old vs new implementation."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.results: dict[str, Any] = {}

    def benchmark_sync_queries(self, project_id: str, iterations: int = 100):
        """Benchmark old synchronous queries without pooling."""
        print("\n=== Benchmarking OLD implementation (sync, no pooling) ===")

        # Create new connection for each iteration (simulates old behavior)
        times = []
        for i in range(iterations):
            start = time.perf_counter()

            db = DatabaseConnection(self.database_url)
            db.connect()
            session = Session(db.engine)

            # Query items
            items = session.query(Item).filter(Item.project_id == project_id, Item.deleted_at.is_(None)).limit(50).all()

            # N+1 query: Access links for each item
            for item in items[:10]:  # Just first 10 to keep it reasonable
                _ = len(item.source_links or [])
                _ = len(item.target_links or [])

            session.close()
            db.close()

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")

        self.results["old_implementation"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "iterations": iterations,
        }

    async def benchmark_async_pooled(self, project_id: str, iterations: int = 100):
        """Benchmark new async queries with connection pooling."""
        print("\n=== Benchmarking NEW implementation (async + pooling) ===")

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
                    .limit(50)
                )

                result = await session.execute(query)
                items = result.scalars().all()

                # N+1 query: Access links
                for item in items[:10]:
                    _ = len(item.source_links or [])
                    _ = len(item.target_links or [])

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")

        self.results["pooled_implementation"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "iterations": iterations,
        }

    async def benchmark_eager_loading(self, project_id: str, iterations: int = 100):
        """Benchmark with eager loading (no N+1)."""
        print("\n=== Benchmarking EAGER LOADING (no N+1) ===")

        db_manager = await get_database_manager()

        times = []
        for i in range(iterations):
            start = time.perf_counter()

            async with db_manager.session() as session:
                # Use QueryOptimizer for eager loading
                items = await QueryOptimizer.get_items_with_links(
                    session,
                    project_id,
                    limit=50,
                )

                # Access links (already loaded)
                for item in items[:10]:
                    src_links = getattr(item, "source_links", None) or []
                    tgt_links = getattr(item, "target_links", None) or []
                    _ = len(src_links)
                    _ = len(tgt_links)

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")

        self.results["eager_loading"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "iterations": iterations,
        }

    async def benchmark_with_cache(self, project_id: str, iterations: int = 100):
        """Benchmark with query caching."""
        print("\n=== Benchmarking WITH CACHING ===")

        from tracertm.mcp.cache import get_query_cache

        cache = get_query_cache()
        await cache.clear()  # Start fresh

        db_manager = await get_database_manager()

        times = []
        cache_hits = 0

        for i in range(iterations):
            start = time.perf_counter()

            # Simulate cached query pattern
            cache_key = f"benchmark_query_{i % 10}"  # 10 unique queries

            cached = await cache.get(cache_key, project_id=project_id)

            if cached is None:
                async with db_manager.session() as session:
                    items = await QueryOptimizer.get_items_with_links(
                        session,
                        project_id,
                        limit=50,
                    )
                    await cache.set(cache_key, items, ttl=300, project_id=project_id)
            else:
                items = cached
                cache_hits += 1

            # Access data
            for item in items[:10]:
                src_links = getattr(item, "source_links", None) or []
                _ = len(src_links)

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        hit_rate = cache_hits / iterations

        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
        print(f"  Cache hit rate: {hit_rate:.1%}")

        self.results["with_caching"] = {
            "avg_ms": avg_time,
            "min_ms": min_time,
            "max_ms": max_time,
            "cache_hits": cache_hits,
            "hit_rate": hit_rate,
            "iterations": iterations,
        }

    def print_summary(self):
        """Print comparison summary."""
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)

        if "old_implementation" in self.results and "pooled_implementation" in self.results:
            old_avg = self.results["old_implementation"]["avg_ms"]
            pooled_avg = self.results["pooled_implementation"]["avg_ms"]
            pooling_improvement = ((old_avg - pooled_avg) / old_avg) * 100

            print("\nConnection Pooling Impact:")
            print(f"  Old (no pooling):  {old_avg:.2f}ms")
            print(f"  New (with pool):   {pooled_avg:.2f}ms")
            print(f"  Improvement:       {pooling_improvement:+.1f}%")

        if "pooled_implementation" in self.results and "eager_loading" in self.results:
            pooled_avg = self.results["pooled_implementation"]["avg_ms"]
            eager_avg = self.results["eager_loading"]["avg_ms"]
            eager_improvement = ((pooled_avg - eager_avg) / pooled_avg) * 100

            print("\nEager Loading Impact:")
            print(f"  Without eager:     {pooled_avg:.2f}ms")
            print(f"  With eager:        {eager_avg:.2f}ms")
            print(f"  Improvement:       {eager_improvement:+.1f}%")

        if "eager_loading" in self.results and "with_caching" in self.results:
            eager_avg = self.results["eager_loading"]["avg_ms"]
            cache_avg = self.results["with_caching"]["avg_ms"]
            cache_improvement = ((eager_avg - cache_avg) / eager_avg) * 100
            hit_rate = self.results["with_caching"]["hit_rate"]

            print("\nCaching Impact:")
            print(f"  Without cache:     {eager_avg:.2f}ms")
            print(f"  With cache:        {cache_avg:.2f}ms")
            print(f"  Improvement:       {cache_improvement:+.1f}%")
            print(f"  Cache hit rate:    {hit_rate:.1%}")

        if "old_implementation" in self.results and "with_caching" in self.results:
            old_avg = self.results["old_implementation"]["avg_ms"]
            final_avg = self.results["with_caching"]["avg_ms"]
            total_improvement = ((old_avg - final_avg) / old_avg) * 100

            print(f"\n{'=' * 70}")
            print("TOTAL IMPROVEMENT (Old → Fully Optimized)")
            print(f"{'=' * 70}")
            print(f"  Before:            {old_avg:.2f}ms")
            print(f"  After:             {final_avg:.2f}ms")
            print(f"  Total improvement: {total_improvement:+.1f}%")
            print()

            if total_improvement >= 50:
                print("✓ Target of 50% improvement ACHIEVED!")
            else:
                print(f"⚠ Target of 50% improvement not met (achieved {total_improvement:.1f}%)")

        print("=" * 70)


async def run_benchmark(database_url: str, project_id: str):
    """Run full benchmark suite."""
    print("=" * 70)
    print("MCP DATABASE OPTIMIZATION BENCHMARK - PHASE 3")
    print("=" * 70)
    print(f"\nDatabase: {database_url}")
    print(f"Project ID: {project_id}")
    print("Iterations per test: 100")

    runner = BenchmarkRunner(database_url)

    # Run benchmarks
    runner.benchmark_sync_queries(project_id, iterations=100)
    await runner.benchmark_async_pooled(project_id, iterations=100)
    await runner.benchmark_eager_loading(project_id, iterations=100)
    await runner.benchmark_with_cache(project_id, iterations=100)

    # Print summary
    runner.print_summary()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python benchmark_phase3.py <database_url> <project_id>")
        sys.exit(1)

    database_url = sys.argv[1]
    project_id = sys.argv[2]

    asyncio.run(run_benchmark(database_url, project_id))
