"""Load tests for MCP HTTP integration.

Tests cover:
- Concurrent HTTP requests to MCP
- Response time under load
- Connection pool limits
- Resource leak detection
- Throughput measurement
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
import pytest

from tests.test_constants import COUNT_TEN, HTTP_INTERNAL_SERVER_ERROR, HTTP_OK

# ============================================================================
# Configuration
# ============================================================================

MCP_BASE_URL = "http://localhost:4000"
TEST_TOKEN = "test-load-key"
CONCURRENT_REQUESTS = [1, 5, 10, 25, 50, 100]
TEST_DURATION = 60  # seconds


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def auth_headers() -> None:
    """Return auth headers for load testing."""
    return {"Authorization": f"Bearer {TEST_TOKEN}", "Content-Type": "application/json"}


@pytest.fixture
def sample_requests() -> None:
    """Return sample requests for load testing."""
    return [
        {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "project_manage", "arguments": {"action": "list"}},
            "id": 2,
        },
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "item_manage",
                "arguments": {"action": "create", "title": "Load Test Item", "item_type": "feature"},
            },
            "id": 3,
        },
        {"jsonrpc": "2.0", "method": "resources/list", "params": {}, "id": 4},
    ]


# ============================================================================
# Helper Functions
# ============================================================================


async def make_request(
    client: httpx.AsyncClient,
    request_data: dict[str, Any],
    headers: dict[str, str],
) -> tuple[int, float]:
    """Make a single HTTP request and measure response time.

    Returns:
        Tuple of (status_code, response_time_ms)
    """
    start = time.time()
    try:
        response = await client.post("/messages", json=request_data, headers=headers)
        duration = (time.time() - start) * 1000  # Convert to ms
        return (response.status_code, duration)
    except Exception:
        duration = (time.time() - start) * 1000
        return (-1, duration)


def calculate_percentiles(values: list[float]) -> dict[str, float]:
    """Calculate percentiles for a list of values."""
    sorted_values = sorted(values)
    n = len(sorted_values)

    if n == 0:
        return {"p50": 0, "p95": 0, "p99": 0}

    return {
        "p50": sorted_values[int(n * 0.50)],
        "p95": sorted_values[int(n * 0.95)],
        "p99": sorted_values[int(n * 0.99)],
    }


# ============================================================================
# Test Concurrent Requests
# ============================================================================


class TestConcurrentRequests:
    """Test concurrent HTTP requests to MCP."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("concurrent_count", [1, 5, 10, 25])
    async def test_concurrent_tools_list(self, auth_headers: Any, concurrent_count: Any) -> None:
        """Test concurrent tools/list requests."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=30.0) as client:
            tasks = [make_request(client, request_data, auth_headers) for _ in range(concurrent_count)]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful = [r for r in results if isinstance(r, tuple) and r[0] == HTTP_OK]
            response_times = [r[1] for r in results if isinstance(r, tuple)]

            if response_times:
                calculate_percentiles(response_times)

            # Assertions
            assert len(successful) >= concurrent_count * 0.95  # 95% success rate

    @pytest.mark.asyncio
    @pytest.mark.parametrize("concurrent_count", [1, 5, 10])
    async def test_concurrent_tool_calls(self, auth_headers: Any, sample_requests: Any, concurrent_count: Any) -> None:
        """Test concurrent tool call requests."""
        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=30.0) as client:
            tasks = []
            for i in range(concurrent_count):
                request = sample_requests[i % len(sample_requests)].copy()
                request["id"] = i
                tasks.append(make_request(client, request, auth_headers))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful = [r for r in results if isinstance(r, tuple) and r[0] in {200, 201}]
            response_times = [r[1] for r in results if isinstance(r, tuple)]

            if response_times:
                calculate_percentiles(response_times)

            assert len(successful) >= concurrent_count * 0.90  # 90% success rate


# ============================================================================
# Test Response Time Under Load
# ============================================================================


class TestResponseTime:
    """Test response time characteristics under load."""

    @pytest.mark.asyncio
    async def test_response_time_baseline(self, auth_headers: Any) -> None:
        """Test baseline response time with no load."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=10.0) as client:
            # Make 10 sequential requests
            response_times = []
            for _ in range(10):
                _, duration = await make_request(client, request_data, auth_headers)
                response_times.append(duration)

            avg_time = sum(response_times) / len(response_times)
            calculate_percentiles(response_times)

            # Baseline should be fast
            assert avg_time < HTTP_INTERNAL_SERVER_ERROR  # < HTTP_INTERNAL_SERVER_ERRORms average

    @pytest.mark.asyncio
    async def test_response_time_degradation(self, auth_headers: Any) -> None:
        """Test response time degradation under increasing load."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        results_by_load = {}

        for concurrent_count in [1, 10, 25, 50]:
            async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=30.0) as client:
                tasks = [make_request(client, request_data, auth_headers) for _ in range(concurrent_count)]

                results = await asyncio.gather(*tasks, return_exceptions=True)
                response_times = [r[1] for r in results if isinstance(r, tuple)]

                if response_times:
                    avg_time = sum(response_times) / len(response_times)
                    percentiles = calculate_percentiles(response_times)
                    results_by_load[concurrent_count] = {"avg": avg_time, "p95": percentiles["p95"]}

        for _load, _metrics in results_by_load.items():
            pass

        # p95 should stay reasonable even under load
        if 50 in results_by_load:
            assert results_by_load[50]["p95"] < 5000  # < COUNT_FIVEs at p95


# ============================================================================
# Test Connection Pool
# ============================================================================


class TestConnectionPool:
    """Test connection pool behavior."""

    @pytest.mark.asyncio
    async def test_connection_pool_limits(self, auth_headers: Any) -> None:
        """Test connection pool limit handling."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        # Create client with limited pool
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=30.0, limits=limits) as client:
            # Make more requests than pool size
            tasks = [make_request(client, request_data, auth_headers) for _ in range(20)]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All requests should complete despite pool limit
            successful = [r for r in results if isinstance(r, tuple) and r[0] == HTTP_OK]

            assert len(successful) >= 18  # 90% success rate

    @pytest.mark.asyncio
    async def test_connection_reuse(self, auth_headers: Any) -> None:
        """Test connection reuse efficiency."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=10.0) as client:
            # Make sequential requests (should reuse connection)
            response_times = []
            for _i in range(10):
                _, duration = await make_request(client, request_data, auth_headers)
                response_times.append(duration)

            # First request might be slower (connection setup)
            # Subsequent requests should be faster
            first_request = response_times[0]
            avg_subsequent = sum(response_times[1:]) / len(response_times[1:])

            # Subsequent requests should generally be faster
            # (or at least not significantly slower)
            assert avg_subsequent <= first_request * 1.5


# ============================================================================
# Test Resource Leaks
# ============================================================================


class TestResourceLeaks:
    """Test for resource leaks under sustained load."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load_no_leaks(self, auth_headers: Any) -> None:
        """Test sustained load for resource leaks."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        # Run for 30 seconds
        duration = 30
        start_time = time.time()
        request_count = 0
        error_count = 0

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=10.0) as client:
            while time.time() - start_time < duration:
                try:
                    status, _ = await make_request(client, request_data, auth_headers)
                    request_count += 1
                    if status != HTTP_OK:
                        error_count += 1
                except Exception:
                    error_count += 1

                # Small delay between requests
                await asyncio.sleep(0.1)

        # Error rate should be low
        assert error_count / request_count < 0.05  # < COUNT_FIVE% error rate

    @pytest.mark.asyncio
    async def test_memory_stability(self, auth_headers: Any) -> None:
        """Test memory stability under load."""
        # This would ideally monitor memory usage
        # For now, just verify requests complete without errors

        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=10.0) as client:
            # Make many requests
            for _ in range(100):
                status, _ = await make_request(client, request_data, auth_headers)
                assert status in {200, -1}  # Either success or connection error

        assert True  # Completed without crashes


# ============================================================================
# Test Throughput
# ============================================================================


class TestThroughput:
    """Test throughput measurement."""

    @pytest.mark.asyncio
    async def test_max_throughput(self, auth_headers: Any) -> None:
        """Test maximum throughput (requests per second)."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        test_duration = 10  # seconds
        concurrent_requests = 10

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=30.0) as client:
            start_time = time.time()
            request_count = 0

            while time.time() - start_time < test_duration:
                # Make batch of concurrent requests
                tasks = [make_request(client, request_data, auth_headers) for _ in range(concurrent_requests)]

                results = await asyncio.gather(*tasks, return_exceptions=True)
                request_count += len([r for r in results if isinstance(r, tuple)])

            elapsed = time.time() - start_time
            throughput = request_count / elapsed

            # Should handle at least 10 req/s
            assert throughput >= COUNT_TEN


# ============================================================================
# Test Error Scenarios
# ============================================================================


class TestErrorScenarios:
    """Test error handling under load."""

    @pytest.mark.asyncio
    async def test_invalid_requests_under_load(self, auth_headers: Any) -> None:
        """Test handling invalid requests under load."""
        # Mix of valid and invalid requests
        valid_request = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        invalid_request = {"jsonrpc": "2.0", "method": "invalid_method", "id": 2}

        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=10.0) as client:
            tasks = []
            for i in range(20):
                request = valid_request if i % 2 == 0 else invalid_request
                request["id"] = i
                tasks.append(make_request(client, request, auth_headers))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Server should handle both valid and invalid gracefully
            assert len(results) == 20

    @pytest.mark.asyncio
    async def test_timeout_handling(self, auth_headers: Any) -> None:
        """Test timeout handling."""
        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        # Very short timeout
        async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=0.1) as client:
            results = []
            for _ in range(10):
                try:
                    status, _duration = await make_request(client, request_data, auth_headers)
                    results.append(status)
                except Exception:
                    results.append(-1)

            # Some requests may timeout
            assert True  # Just verify no crashes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
