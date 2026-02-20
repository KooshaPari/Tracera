"""Performance tests - Latency, throughput, and resource usage.

Usage:
    pytest tests/performance/test_performance.py -v --tb=short
"""

import time
from typing import Any

import pytest
from router import TOOL_REGISTRY, ArchRouter, ToolRegistry


class TestPerformance:
    """Performance tests."""

    @pytest.fixture
    def router(self) -> None:
        """Create router."""
        return ArchRouter()

    @pytest.fixture
    def registry(self) -> None:
        """Create registry."""
        return ToolRegistry(TOOL_REGISTRY)

    def test_router_initialization_time(self, _router: Any) -> None:
        """Test router initialization time."""
        start = time.time()
        ArchRouter()
        elapsed = time.time() - start

        # Should initialize in <100ms
        assert elapsed < 0.1, f"Router init took {elapsed:.3f}s"

    def test_registry_initialization_time(self, _registry: Any) -> None:
        """Test registry initialization time."""
        start = time.time()
        ToolRegistry(TOOL_REGISTRY)
        elapsed = time.time() - start

        # Should initialize in <50ms
        assert elapsed < 0.05, f"Registry init took {elapsed:.3f}s"

    def test_routing_latency(self, router: Any, registry: Any) -> None:
        """Test routing latency."""
        routes = registry.export_registry()
        query = "generate FastAPI endpoint"

        start = time.time()
        result = router.route(query, routes)
        elapsed = time.time() - start

        # Should route in <50ms
        assert elapsed < 0.05, f"Routing took {elapsed:.3f}s"
        assert result.route is not None

    def test_batch_routing_latency(self, router: Any, registry: Any) -> None:
        """Test batch routing latency."""
        routes = registry.export_registry()
        queries = [
            "generate code",
            "test endpoint",
            "process data",
            "transform CSV",
            "create API",
        ]

        start = time.time()
        results = router.batch_route(queries, routes)
        elapsed = time.time() - start

        # Should batch route 5 queries in <300ms
        assert elapsed < 0.3, f"Batch routing took {elapsed:.3f}s"
        assert len(results) == 5

    def test_cache_hit_latency(self, router: Any, registry: Any) -> None:
        """Test cache hit latency."""
        routes = registry.export_registry()
        query = "generate endpoint"

        # First call (cache miss)
        router.route(query, routes)

        # Second call (cache hit)
        start = time.time()
        result = router.route(query, routes)
        elapsed = time.time() - start

        # Cache hit should be <5ms
        assert elapsed < 0.005, f"Cache hit took {elapsed:.3f}s"
        assert result.cached is True

    def test_registry_lookup_latency(self, registry: Any) -> None:
        """Test registry lookup latency."""
        start = time.time()
        route = registry.get_route("data_processing")
        elapsed = time.time() - start

        # Should lookup in <1ms
        assert elapsed < 0.001, f"Registry lookup took {elapsed:.3f}s"
        assert route is not None

    def test_registry_list_routes_latency(self, registry: Any) -> None:
        """Test registry list routes latency."""
        start = time.time()
        routes = registry.list_routes()
        elapsed = time.time() - start

        # Should list routes in <1ms
        assert elapsed < 0.001, f"List routes took {elapsed:.3f}s"
        assert len(routes) > 0

    def test_cache_memory_usage(self, router: Any, registry: Any) -> None:
        """Test cache memory usage."""
        routes = registry.export_registry()

        # Fill cache with 100 queries
        for i in range(100):
            query = f"query {i}"
            router.route(query, routes)

        stats = router.get_cache_stats()
        assert stats["size"] == 100
        assert stats["utilization"] == 0.1  # 100/1000

    def test_throughput_queries_per_second(self, router: Any, registry: Any) -> None:
        """Test throughput (queries per second)."""
        routes = registry.export_registry()
        query = "generate endpoint"

        start = time.time()
        count = 0
        while time.time() - start < 1.0:  # Run for 1 second
            router.route(query, routes)
            count += 1

        # Should handle >20 queries per second
        assert count > 20, f"Only {count} queries/sec"
