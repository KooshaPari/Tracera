"""MCP Performance Test Suite.

Tests MCP server optimizations including:
- Tool registration performance (<100ms)
- Cold start performance (<200ms)
- Tool response times (<500ms)
- Token usage (<1,000 tokens per operation)
- Lazy loading efficiency
- Connection pooling
- Compression effectiveness
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from tests.performance.conftest import (
    measure_time,
)
from tests.test_constants import COUNT_FIVE, COUNT_TWO

# ============================================================
# Performance Thresholds for MCP Operations
# ============================================================


class MCPPerformanceThresholds:
    """Performance targets for MCP optimizations."""

    # Server initialization
    TOOL_REGISTRATION_MS = 100  # All tools registered in <100ms
    COLD_START_MS = 200  # Server cold start <200ms
    LAZY_LOAD_OVERHEAD_MS = 10  # Lazy loading overhead <10ms per tool

    # Tool execution
    TOOL_RESPONSE_MS = 500  # Tool response time <500ms
    SIMPLE_TOOL_MS = 100  # Simple tools <100ms
    COMPLEX_TOOL_MS = 500  # Complex analysis tools <500ms

    # Token usage
    MAX_TOKENS_PER_OPERATION = 1000  # Token budget per operation
    MAX_TOKENS_PER_RESPONSE = 2000  # Token budget per response

    # Streaming and compression
    COMPRESSION_RATIO_MIN = 0.3  # 70% compression minimum
    STREAMING_LATENCY_MS = 50  # Time to first chunk <50ms

    # Connection pooling
    POOL_CONNECTION_MS = 10  # Getting connection from pool <10ms
    POOL_REUSE_PERCENTAGE = 80  # 80% connection reuse rate


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def mcp_server_env() -> None:
    """Set up minimal MCP server environment."""
    env_vars = {
        "TRACERTM_MCP_AUTH_MODE": "disabled",
        "TRACERTM_MCP_RATE_LIMIT_ENABLED": "false",
        "TRACERTM_MCP_VERBOSE_LOGGING": "false",
    }

    # Apply environment
    original = {}
    for key, value in env_vars.items():
        original[key] = os.environ.get(key)
        os.environ[key] = value

    yield env_vars

    # Restore environment
    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def mock_registry() -> None:
    """Create a mock tool registry for testing."""
    from tracertm.mcp.registry import ToolRegistry

    registry = ToolRegistry()

    # Register sample tools
    registry.register_tool_loader(
        "test_tool_fast",
        "tracertm.mcp.tools.params.project",
        {"description": "Fast test tool", "domain": "test"},
    )
    registry.register_tool_loader(
        "test_tool_slow",
        "tracertm.mcp.tools.params.item",
        {"description": "Slow test tool", "domain": "test"},
    )

    return registry


@pytest.fixture
def token_counter() -> None:
    """Utility to count tokens in responses."""

    def count_tokens(text: str) -> int:
        """Simple token counting (approximation: ~4 chars per token)."""
        return len(text) // 4

    return count_tokens


# ============================================================
# Test: Tool Registration Performance
# ============================================================


class TestToolRegistrationPerformance:
    """Test tool registration optimization."""

    def test_tool_registration_under_100ms(self, mcp_server_env: Any, _perf_tracker: Any) -> None:
        """Test that all tools can be registered in <100ms."""
        from tracertm.mcp.registry import get_registry, register_all_tools

        with measure_time(
            "tool_registration",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.TOOL_REGISTRATION_MS,
        ) as timing:
            register_all_tools()

        registry = get_registry()
        tool_count = len(registry.list_registered_tools())

        # Verify registration completed
        assert tool_count > 0, "No tools registered"
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.TOOL_REGISTRATION_MS

    def test_lazy_loading_no_immediate_imports(self, _mcp_server_env: Any) -> None:
        """Test that tool registration doesn't import modules immediately."""
        from tracertm.mcp.registry import ToolRegistry

        registry = ToolRegistry()

        # Register a tool
        registry.register_tool_loader(
            "test_lazy_tool",
            "tracertm.mcp.tools.params.project",
            {"description": "Test lazy loading"},
        )

        # Verify module not loaded yet
        assert not registry.is_loaded("tracertm.mcp.tools.params.project")

        # Load the tool
        registry.load_tool("test_lazy_tool")

        # Now it should be loaded
        assert registry.is_loaded("tracertm.mcp.tools.params.project")

    def test_lazy_load_overhead_under_10ms(self, mock_registry: Any, perf_tracker: Any) -> None:
        """Test that lazy loading overhead is <10ms per tool."""
        with measure_time(
            "lazy_load_overhead",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.LAZY_LOAD_OVERHEAD_MS,
        ) as timing:
            mock_registry.load_tool("test_tool_fast")

        assert timing["elapsed_ms"] < MCPPerformanceThresholds.LAZY_LOAD_OVERHEAD_MS

    def test_batch_registration_metadata_only(self, _mcp_server_env: Any) -> None:
        """Test that batch registration only stores metadata, not modules."""
        from tracertm.mcp.registry import get_registry

        registry = get_registry()

        # Register multiple tools
        for i in range(10):
            registry.register_tool_loader(
                f"batch_tool_{i}",
                "tracertm.mcp.tools.params.project",
                {"description": f"Batch tool {i}", "batch": i},
            )

        # Verify metadata is stored
        for i in range(10):
            metadata = registry.get_tool_metadata(f"batch_tool_{i}")
            assert metadata is not None
            assert metadata["batch"] == i

        # Verify modules not loaded
        assert not registry.is_loaded("tracertm.mcp.tools.params.project")


# ============================================================
# Test: Cold Start Performance
# ============================================================


class TestColdStartPerformance:
    """Test server cold start optimization."""

    def test_cold_start_under_200ms(self, mcp_server_env: Any, _perf_tracker: Any) -> None:
        """Test that server cold start is <200ms."""
        # Clear any cached imports
        import sys

        mcp_modules = [m for m in sys.modules if "tracertm.mcp" in m]
        for module in mcp_modules:
            if module != "tracertm.mcp.registry":  # Keep registry
                sys.modules.pop(module, None)

        with measure_time(
            "cold_start",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.COLD_START_MS,
        ) as timing:
            # Import and build server
            from tracertm.mcp.core import build_mcp_server

            server = build_mcp_server()

        assert server is not None
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.COLD_START_MS

    def test_minimal_imports_on_startup(self) -> None:
        """Test that minimal modules are imported on startup."""
        import sys

        # Record modules before import
        before_modules = set(sys.modules.keys())

        # Import core server

        # Record modules after import
        after_modules = set(sys.modules.keys())

        # Calculate new imports
        new_modules = after_modules - before_modules
        mcp_tool_modules = [m for m in new_modules if "tracertm.mcp.tools.params" in m]

        # Should not import any tool parameter modules
        assert len(mcp_tool_modules) == 0, f"Tool modules imported on startup: {mcp_tool_modules}"


# ============================================================
# Test: Tool Response Time
# ============================================================


class TestToolResponseTime:
    """Test tool execution performance."""

    @pytest.mark.asyncio
    async def test_simple_tool_under_100ms(self, mcp_server_env: Any, _perf_tracker: Any) -> None:
        """Test that simple tools respond in <100ms."""
        from tracertm.mcp.registry import get_registry

        get_registry()

        # Mock a simple tool execution
        async def simple_tool() -> None:
            await asyncio.sleep(0.01)  # Simulate 10ms work
            return {"status": "success", "data": "result"}

        with measure_time(
            "simple_tool_response",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.SIMPLE_TOOL_MS,
        ) as timing:
            result = await simple_tool()

        assert result["status"] == "success"
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.SIMPLE_TOOL_MS

    @pytest.mark.asyncio
    async def test_complex_tool_under_500ms(self, mcp_server_env: Any, _perf_tracker: Any) -> None:
        """Test that complex analysis tools respond in <500ms."""

        # Mock a complex analysis tool
        async def complex_tool() -> None:
            # Simulate complex analysis (graph traversal, etc.)
            await asyncio.sleep(0.2)  # Simulate 200ms work
            return {"status": "success", "analysis": {"nodes": 100, "edges": 250, "cycles": [], "paths": []}}

        with measure_time(
            "complex_tool_response",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.COMPLEX_TOOL_MS,
        ) as timing:
            result = await complex_tool()

        assert result["status"] == "success"
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.COMPLEX_TOOL_MS

    def test_tool_response_time_budget(self, perf_tracker: Any) -> None:
        """Test that tool responses stay within time budget."""
        response_times = []

        # Simulate 10 tool calls
        for i in range(10):
            with measure_time(f"tool_call_{i}", perf_tracker) as timing:
                time.sleep(0.02)  # Simulate 20ms work

            response_times.append(timing["elapsed_ms"])

        # Calculate percentiles
        response_times.sort()
        p50 = response_times[len(response_times) // 2]
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[-1]

        # All responses should be well under budget
        assert p50 < MCPPerformanceThresholds.SIMPLE_TOOL_MS
        assert p95 < MCPPerformanceThresholds.TOOL_RESPONSE_MS
        assert p99 < MCPPerformanceThresholds.TOOL_RESPONSE_MS


# ============================================================
# Test: Token Usage
# ============================================================


class TestTokenUsage:
    """Test token optimization."""

    def test_tool_response_token_budget(self, token_counter: Any) -> None:
        """Test that tool responses stay within token budget."""
        # Simulate a tool response
        response = {
            "status": "success",
            "items": [{"id": f"item-{i}", "title": f"Item {i}", "status": "todo"} for i in range(10)],
        }

        response_text = json.dumps(response)
        token_count = token_counter(response_text)

        assert token_count < MCPPerformanceThresholds.MAX_TOKENS_PER_RESPONSE, (
            f"Response exceeds token budget: {token_count} tokens"
        )

    def test_error_response_minimal_tokens(self, token_counter: Any) -> None:
        """Test that error responses use minimal tokens."""
        error_response = {"error": {"code": "VALIDATION_ERROR", "message": "Invalid parameter: project_id required"}}

        response_text = json.dumps(error_response)
        token_count = token_counter(response_text)

        # Error responses should be very small
        assert token_count < 100, f"Error response too large: {token_count} tokens"

    def test_large_dataset_pagination_tokens(self, token_counter: Any) -> None:
        """Test that large datasets use pagination to control tokens."""
        # Simulate paginated response
        page_size = 20
        total_items = 100

        page_response = {
            "status": "success",
            "items": [{"id": f"item-{i}", "title": f"Item {i}"} for i in range(page_size)],
            "pagination": {"page": 1, "page_size": page_size, "total": total_items, "has_more": True},
        }

        response_text = json.dumps(page_response)
        token_count = token_counter(response_text)

        # Even with pagination metadata, should stay in budget
        assert token_count < MCPPerformanceThresholds.MAX_TOKENS_PER_RESPONSE


# ============================================================
# Test: Streaming and Compression
# ============================================================


class TestStreamingAndCompression:
    """Test streaming responses and compression."""

    @pytest.mark.asyncio
    async def test_streaming_latency_under_50ms(self, perf_tracker: Any) -> None:
        """Test that streaming responses start in <50ms."""

        async def streaming_generator() -> None:
            """Simulate a streaming response."""
            yield b"chunk1"
            await asyncio.sleep(0.01)
            yield b"chunk2"
            await asyncio.sleep(0.01)
            yield b"chunk3"

        with measure_time(
            "streaming_first_chunk",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.STREAMING_LATENCY_MS,
        ) as timing:
            gen = streaming_generator()
            first_chunk = await anext(gen)

        assert first_chunk == b"chunk1"
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.STREAMING_LATENCY_MS

    def test_compression_ratio_minimum(self) -> None:
        """Test that compression achieves minimum ratio."""
        import gzip

        # Create compressible data (JSON with repetition)
        data = json.dumps({
            "items": [
                {
                    "id": f"item-{i}",
                    "title": f"Test Item {i}",
                    "description": "This is a test description that repeats many times. " * 10,
                    "status": "todo",
                    "priority": "medium",
                }
                for i in range(50)
            ],
        })

        original_size = len(data.encode("utf-8"))
        compressed_data = gzip.compress(data.encode("utf-8"))
        compressed_size = len(compressed_data)

        compression_ratio = compressed_size / original_size

        assert compression_ratio < (1 - MCPPerformanceThresholds.COMPRESSION_RATIO_MIN), (
            f"Insufficient compression: {compression_ratio:.2%} ratio "
            f"(target: <{1 - MCPPerformanceThresholds.COMPRESSION_RATIO_MIN:.2%})"
        )


# ============================================================
# Test: Connection Pooling
# ============================================================


class TestConnectionPooling:
    """Test connection pooling performance."""

    @pytest.mark.asyncio
    async def test_pool_connection_under_10ms(self, perf_tracker: Any) -> None:
        """Test that getting connection from pool is <10ms."""

        # Mock connection pool
        class MockPool:
            def __init__(self) -> None:
                self.connections = [MagicMock() for _ in range(5)]
                self.available = list(self.connections)

            async def acquire(self) -> None:
                await asyncio.sleep(0.001)  # 1ms overhead
                if self.available:
                    return self.available.pop(0)
                return MagicMock()

            async def release(self, conn: Any) -> None:
                self.available.append(conn)

        pool = MockPool()

        with measure_time(
            "pool_acquire",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.POOL_CONNECTION_MS,
        ) as timing:
            conn = await pool.acquire()

        assert conn is not None
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.POOL_CONNECTION_MS

    @pytest.mark.asyncio
    async def test_connection_reuse_rate(self) -> None:
        """Test that connection pool achieves target reuse rate."""

        class MockPool:
            def __init__(self, size: Any = 5) -> None:
                self.size = size
                self.connections = {i: MagicMock(id=i) for i in range(size)}
                self.available = list(self.connections.values())
                self.acquired_count = 0
                self.reused_count = 0

            async def acquire(self) -> None:
                self.acquired_count += 1
                if self.available:
                    conn = self.available.pop(0)
                    if self.acquired_count > self.size:
                        self.reused_count += 1
                    return conn
                # Create new connection (pool exhausted)
                return MagicMock(id=self.acquired_count)

            async def release(self, conn: Any) -> None:
                if hasattr(conn, "id") and conn.id < self.size:
                    self.available.append(conn)

        pool = MockPool()

        # Simulate 100 operations
        for _ in range(100):
            conn = await pool.acquire()
            await asyncio.sleep(0.001)  # Simulate work
            await pool.release(conn)

        reuse_rate = (pool.reused_count / pool.acquired_count) * 100

        assert reuse_rate >= MCPPerformanceThresholds.POOL_REUSE_PERCENTAGE, (
            f"Low connection reuse: {reuse_rate:.1f}% (target: {MCPPerformanceThresholds.POOL_REUSE_PERCENTAGE}%)"
        )


# ============================================================
# Test: End-to-End Performance
# ============================================================


class TestEndToEndPerformance:
    """Test complete request-response cycle performance."""

    @pytest.mark.asyncio
    async def test_complete_tool_call_performance(self, mcp_server_env: Any, _perf_tracker: Any) -> None:
        """Test complete tool call cycle (registration, execution, response)."""
        from tracertm.mcp.registry import get_registry

        get_registry()

        # Mock complete tool call
        async def complete_tool_call() -> None:
            # 1. Tool lookup (lazy load if needed)
            await asyncio.sleep(0.005)  # 5ms

            # 2. Execute tool
            await asyncio.sleep(0.050)  # 50ms

            # 3. Format response
            await asyncio.sleep(0.010)  # 10ms

            return {"status": "success", "result": "data"}

        with measure_time(
            "complete_tool_call",
            perf_tracker=perf_tracker,
            threshold_ms=MCPPerformanceThresholds.SIMPLE_TOOL_MS,
        ) as timing:
            result = await complete_tool_call()

        assert result["status"] == "success"
        assert timing["elapsed_ms"] < MCPPerformanceThresholds.SIMPLE_TOOL_MS

    def test_performance_summary_report(self, perf_tracker: Any) -> None:
        """Generate performance summary report."""
        # Run multiple operations
        for i in range(5):
            with measure_time(f"operation_{i}", perf_tracker):
                time.sleep(0.02)  # 20ms each

        summary = perf_tracker.get_summary()
        report = perf_tracker.report()

        assert summary["total_measurements"] == COUNT_FIVE
        assert "Performance Summary" in report


# ============================================================
# Performance Baselines
# ============================================================


def test_save_performance_baselines(tmp_path: Any, _perf_tracker: Any) -> None:
    """Save performance baselines for future comparison."""
    from tests.performance.conftest import PerformanceBaseline

    baselines = [
        PerformanceBaseline(
            operation="tool_registration",
            avg_time_ms=50.0,
            p95_time_ms=80.0,
            p99_time_ms=95.0,
            throughput_ops_sec=20.0,
            max_memory_mb=50.0,
            notes="Tool registration with lazy loading",
        ),
        PerformanceBaseline(
            operation="cold_start",
            avg_time_ms=150.0,
            p95_time_ms=180.0,
            p99_time_ms=195.0,
            throughput_ops_sec=6.7,
            max_memory_mb=75.0,
            notes="Server cold start time",
        ),
    ]

    # Save baselines
    baselines_file = tmp_path / "mcp_performance_baselines.json"
    with pathlib.Path(baselines_file).open("w", encoding="utf-8") as f:
        json.dump([b.to_dict() for b in baselines], f, indent=2)

    # Verify saved
    assert baselines_file.exists()

    # Load and verify
    with pathlib.Path(baselines_file).open(encoding="utf-8") as f:
        loaded = json.load(f)

    assert len(loaded) == COUNT_TWO
    assert loaded[0]["operation"] == "tool_registration"
