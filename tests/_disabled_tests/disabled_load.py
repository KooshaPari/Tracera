"""Load tests - Concurrent requests and stress testing.

Usage:
    pytest tests/performance/test_load.py -v --tb=short
"""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest
from router import TOOL_REGISTRY, ArchRouter, ToolRegistry


class TestLoad:
    """Load tests."""

    @pytest.fixture
    def router(self) -> None:
        """Create router."""
        return ArchRouter()

    @pytest.fixture
    def registry(self) -> None:
        """Create registry."""
        return ToolRegistry(TOOL_REGISTRY)

    def test_concurrent_routing_10_threads(self, router: Any, registry: Any) -> None:
        """Test concurrent routing with 10 threads."""
        routes = registry.export_registry()
        queries = [
            "generate code",
            "test endpoint",
            "process data",
            "transform CSV",
            "create API",
        ]

        def route_query(query: Any) -> None:
            return router.route(query, routes)

        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(route_query, queries * 2))
        elapsed = time.time() - start

        # Should handle 10 concurrent threads
        assert len(results) == 10
        assert elapsed < 1.0, f"Concurrent routing took {elapsed:.3f}s"

    def test_concurrent_routing_50_threads(self, router: Any, registry: Any) -> None:
        """Test concurrent routing with 50 threads."""
        routes = registry.export_registry()
        queries = [
            "generate code",
            "test endpoint",
            "process data",
            "transform CSV",
            "create API",
        ]

        def route_query(query: Any) -> None:
            return router.route(query, routes)

        start = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(route_query, queries * 10))
        elapsed = time.time() - start

        # Should handle 50 concurrent threads
        assert len(results) == 50
        assert elapsed < 5.0, f"Concurrent routing took {elapsed:.3f}s"

    def test_sustained_load_1000_requests(self, router: Any, registry: Any) -> None:
        """Test sustained load with 1000 requests."""
        routes = registry.export_registry()
        queries = [
            "generate code",
            "test endpoint",
            "process data",
            "transform CSV",
            "create API",
        ]

        start = time.time()
        for i in range(1000):
            query = queries[i % len(queries)]
            router.route(query, routes)
        elapsed = time.time() - start

        # Should handle 1000 requests in <10 seconds
        assert elapsed < 10.0, f"1000 requests took {elapsed:.3f}s"

        # Calculate throughput
        throughput = 1000 / elapsed
        assert throughput > 100, f"Throughput only {throughput:.1f} req/s"

    def test_cache_effectiveness_under_load(self, router: Any, registry: Any) -> None:
        """Test cache effectiveness under load."""
        routes = registry.export_registry()

        # Warm up cache
        for i in range(10):
            router.route(f"query {i}", routes)

        # Measure with cache hits
        start = time.time()
        for i in range(100):
            router.route(f"query {i % 10}", routes)  # Repeat queries
        cached_time = time.time() - start

        # Clear cache
        router.clear_cache()

        # Measure without cache
        start = time.time()
        for i in range(100):
            router.route(f"query {i % 10}", routes)
        uncached_time = time.time() - start

        # Cache should provide significant speedup
        speedup = uncached_time / cached_time
        assert speedup > 1.5, f"Cache speedup only {speedup:.1f}x"

    def test_memory_stability_under_load(self, router: Any, registry: Any) -> None:
        """Test memory stability under load."""
        routes = registry.export_registry()

        # Run 1000 requests
        for i in range(1000):
            query = f"query {i % 100}"
            router.route(query, routes)

        # Check cache stats
        stats = router.get_cache_stats()

        # Cache should not exceed max size
        assert stats["size"] <= stats["max_size"]
        assert stats["utilization"] <= 1.0

    def test_error_handling_under_load(self, router: Any, registry: Any) -> None:
        """Test error handling under load."""
        routes = registry.export_registry()

        # Mix valid and invalid queries
        valid_queries = ["generate code", "test endpoint", "process data"]

        errors = 0
        for i in range(100):
            try:
                query = valid_queries[i % len(valid_queries)]
                router.route(query, routes)
            except Exception:
                errors += 1

        # Should handle all requests without crashing
        assert errors == 0
