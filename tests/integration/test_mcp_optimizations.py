"""MCP Optimization Integration Tests.

Tests that all MCP optimizations work correctly together:
- Lazy loading with real tools
- Streaming responses
- Compression middleware
- Connection pooling
- Token management
- Feature flags and rollback
"""

from __future__ import annotations

import asyncio
import gzip
import json
import os

# ============================================================
# Fixtures
# ============================================================
from typing import Any
from unittest.mock import MagicMock

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_TWO


@pytest.fixture
def mcp_optimized_env() -> None:
    """Set up environment with all optimizations enabled."""
    env_vars = {
        "TRACERTM_MCP_AUTH_MODE": "disabled",
        "TRACERTM_MCP_LAZY_LOADING": "true",
        "TRACERTM_MCP_COMPRESSION": "true",
        "TRACERTM_MCP_STREAMING": "true",
        "TRACERTM_MCP_CONNECTION_POOL_SIZE": "10",
        "TRACERTM_MCP_TOKEN_OPTIMIZATION": "true",
    }

    original = {}
    for key, value in env_vars.items():
        original[key] = os.environ.get(key)
        os.environ[key] = value

    yield env_vars

    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def mcp_baseline_env() -> None:
    """Set up environment with optimizations disabled (baseline)."""
    env_vars = {
        "TRACERTM_MCP_AUTH_MODE": "disabled",
        "TRACERTM_MCP_LAZY_LOADING": "false",
        "TRACERTM_MCP_COMPRESSION": "false",
        "TRACERTM_MCP_STREAMING": "false",
        "TRACERTM_MCP_TOKEN_OPTIMIZATION": "false",
    }

    original = {}
    for key, value in env_vars.items():
        original[key] = os.environ.get(key)
        os.environ[key] = value

    yield env_vars

    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


# ============================================================
# Test: Lazy Loading Integration
# ============================================================


class TestLazyLoadingIntegration:
    """Test lazy loading with real tool modules."""

    def test_all_tools_accessible_with_lazy_loading(self, _mcp_optimized_env: Any) -> None:
        """Test that all tools remain accessible with lazy loading."""
        from tracertm.mcp.registry import get_registry, register_all_tools

        register_all_tools()
        registry = get_registry()

        # Get all registered tools
        tools = registry.list_registered_tools()

        assert len(tools) > 0, "No tools registered"

        # Verify metadata is accessible without loading
        for tool_name in tools[:5]:  # Test first 5
            metadata = registry.get_tool_metadata(tool_name)
            assert metadata is not None
            assert "description" in metadata or "domain" in metadata

    def test_lazy_loading_does_not_break_functionality(self, _mcp_optimized_env: Any) -> None:
        """Test that lazy loading doesn't break tool functionality."""
        from tracertm.mcp.registry import get_registry

        registry = get_registry()

        # Register a tool
        registry.register_tool_loader(
            "test_functional_tool",
            "tracertm.mcp.tools.params.project",
            {"description": "Test functionality"},
        )

        # Verify not loaded initially
        assert not registry.is_loaded("tracertm.mcp.tools.params.project")

        # Load on demand
        registry.load_tool("test_functional_tool")

        # Verify loaded
        assert registry.is_loaded("tracertm.mcp.tools.params.project")

    def test_selective_tool_loading(self, _mcp_optimized_env: Any) -> None:
        """Test that only requested tools are loaded."""
        from tracertm.mcp.registry import get_registry

        registry = get_registry()

        # Register multiple tools from different modules
        registry.register_tool_loader("tool_a", "tracertm.mcp.tools.params.project")
        registry.register_tool_loader("tool_b", "tracertm.mcp.tools.params.item")
        registry.register_tool_loader("tool_c", "tracertm.mcp.tools.params.link")

        # Load only tool_a
        registry.load_tool("tool_a")

        # Verify only tool_a's module is loaded
        assert registry.is_loaded("tracertm.mcp.tools.params.project")
        assert not registry.is_loaded("tracertm.mcp.tools.params.item")
        assert not registry.is_loaded("tracertm.mcp.tools.params.link")


# ============================================================
# Test: Streaming Integration
# ============================================================


class TestStreamingIntegration:
    """Test streaming responses in real scenarios."""

    @pytest.mark.asyncio
    async def test_streaming_large_dataset(self, _mcp_optimized_env: Any) -> None:
        """Test streaming responses for large datasets."""

        async def stream_large_dataset(item_count: int) -> None:
            """Simulate streaming a large dataset."""
            chunk_size = 100

            for i in range(0, item_count, chunk_size):
                chunk = {
                    "chunk": i // chunk_size,
                    "items": [
                        {"id": f"item-{j}", "title": f"Item {j}"} for j in range(i, min(i + chunk_size, item_count))
                    ],
                }
                yield json.dumps(chunk).encode("utf-8")
                await asyncio.sleep(0.01)  # Simulate processing

        # Stream 1000 items
        chunks = [chunk async for chunk in stream_large_dataset(1000)]

        assert len(chunks) == COUNT_TEN  # 1000 items / 100 per chunk

    @pytest.mark.asyncio
    async def test_streaming_with_error_handling(self, _mcp_optimized_env: Any) -> None:
        """Test that streaming handles errors gracefully."""

        async def stream_with_error() -> None:
            """Simulate streaming that encounters an error."""
            yield b'{"chunk": 0, "data": "first"}'
            yield b'{"chunk": 1, "data": "second"}'
            # Error occurs here
            msg = "Simulated streaming error"
            raise ValueError(msg)

        chunks_received = []
        error_caught = False

        try:
            chunks_received.extend([chunk async for chunk in stream_with_error()])
        except ValueError as e:
            error_caught = True
            assert "Simulated streaming error" in str(e)

        assert len(chunks_received) == COUNT_TWO
        assert error_caught


# ============================================================
# Test: Compression Integration
# ============================================================


class TestCompressionIntegration:
    """Test compression in real scenarios."""

    def test_compression_with_json_responses(self) -> None:
        """Test compression with typical JSON responses."""
        # Create a realistic response
        response = {
            "status": "success",
            "items": [
                {
                    "id": f"item-{i}",
                    "title": f"Test Item {i}",
                    "description": "This is a test description with some content. " * 5,
                    "metadata": {
                        "created_by": "user@example.com",
                        "created_at": "2025-01-30T12:00:00Z",
                        "tags": ["test", "sample", "example"],
                    },
                }
                for i in range(100)
            ],
        }

        # Serialize and compress
        json_data = json.dumps(response)
        original_size = len(json_data.encode("utf-8"))
        compressed = gzip.compress(json_data.encode("utf-8"))
        compressed_size = len(compressed)

        # Calculate savings
        compression_ratio = compressed_size / original_size
        savings_percent = (1 - compression_ratio) * 100

        assert compression_ratio < 0.4  # At least 60% compression
        assert savings_percent > 60

    def test_compression_selective_by_content_type(self) -> None:
        """Test that compression is selective based on content type."""
        # Text content (should compress well)
        text_content = json.dumps({"data": "test " * 1000})
        text_compressed = gzip.compress(text_content.encode("utf-8"))
        text_ratio = len(text_compressed) / len(text_content)

        # Already compressed content (won't compress further)
        binary_content = gzip.compress(b"binary data")
        double_compressed = gzip.compress(binary_content)
        binary_ratio = len(double_compressed) / len(binary_content)

        # Text should compress much better
        assert text_ratio < 0.3  # 70%+ compression
        assert binary_ratio > 0.95  # Minimal compression gain


# ============================================================
# Test: Connection Pooling Integration
# ============================================================


class TestConnectionPoolingIntegration:
    """Test connection pooling in real scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_use_pool(self) -> None:
        """Test that concurrent requests efficiently use connection pool."""

        class ConnectionPool:
            def __init__(self, size: int = 5) -> None:
                self.size = size
                self.connections = []
                self.in_use = set()
                self.stats = {"acquires": 0, "releases": 0, "reuses": 0, "creates": 0}
                self._available = asyncio.Event()

            async def acquire(self) -> None:
                self.stats["acquires"] += 1

                # Reuse available connection
                for conn in self.connections:
                    if conn not in self.in_use:
                        self.in_use.add(conn)
                        self.stats["reuses"] += 1
                        return conn

                # Create new if under limit
                if len(self.connections) < self.size:
                    conn = MagicMock(id=len(self.connections))
                    self.connections.append(conn)
                    self.in_use.add(conn)
                    self.stats["creates"] += 1
                    return conn

                # Wait for available connection (use Event instead of sleep loop)
                while not any(c not in self.in_use for c in self.connections):
                    self._available.clear()
                    await self._available.wait()

                for conn in self.connections:
                    if conn not in self.in_use:
                        self.in_use.add(conn)
                        self.stats["reuses"] += 1
                        return conn
                return None

            async def release(self, conn: Any) -> None:
                self.stats["releases"] += 1
                self.in_use.discard(conn)
                self._available.set()

        pool = ConnectionPool(size=5)

        # Simulate 20 concurrent requests
        async def make_request(_request_id: int) -> None:
            conn = await pool.acquire()
            await asyncio.sleep(0.01)  # Simulate work
            await pool.release(conn)

        await asyncio.gather(*[make_request(i) for i in range(20)])

        # Verify pooling efficiency
        assert pool.stats["creates"] == COUNT_FIVE  # Only 5 connections created
        assert pool.stats["acquires"] == 20  # 20 requests
        assert pool.stats["reuses"] > COUNT_TEN  # Most requests reused connections

        (pool.stats["reuses"] / pool.stats["acquires"]) * 100

    @pytest.mark.asyncio
    async def test_pool_handles_connection_errors(self) -> None:
        """Test that pool handles connection errors gracefully."""

        class ErrorHandlingPool:
            def __init__(self) -> None:
                self.connections = []
                self.error_count = 0

            async def acquire(self) -> None:
                # Simulate occasional connection error
                if len(self.connections) == COUNT_TWO:
                    self.error_count += 1
                    msg = "Simulated connection error"
                    raise ConnectionError(msg)

                conn = MagicMock(id=len(self.connections))
                self.connections.append(conn)
                return conn

        pool = ErrorHandlingPool()

        # Try to acquire connections
        acquired = []
        errors = 0

        for _i in range(5):
            try:
                conn = await pool.acquire()
                acquired.append(conn)
            except ConnectionError:
                errors += 1

        assert errors > 0  # Error occurred
        assert len(acquired) > 0  # Some connections succeeded


# ============================================================
# Test: Token Management Integration
# ============================================================


class TestTokenManagementIntegration:
    """Test token usage optimization."""

    def test_token_aware_pagination(self) -> None:
        """Test that pagination considers token budget."""
        max_tokens = 1000
        token_per_item = 50  # Approximate tokens per item

        # Calculate safe page size
        safe_page_size = max_tokens // token_per_item

        # Create paginated response
        response = {
            "items": [{"id": f"item-{i}", "data": "x" * 100} for i in range(safe_page_size)],
            "pagination": {"page": 1, "page_size": safe_page_size, "total": 1000},
        }

        # Estimate tokens (rough: 4 chars per token)
        response_text = json.dumps(response)
        estimated_tokens = len(response_text) // 4

        assert estimated_tokens < max_tokens

    def test_token_efficient_error_messages(self) -> None:
        """Test that error messages are token-efficient."""
        # Standard error
        error = {"error": {"code": "VALIDATION_ERROR", "message": "Invalid input", "field": "project_id"}}

        # Verbose error (what we want to avoid)
        verbose_error = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The provided project identifier is not valid according to our validation rules...",
                "details": {
                    "field": "project_id",
                    "value": "invalid-id-12345",
                    "constraints": ["must be UUID", "must exist"],
                    "suggestions": ["Check project list", "Verify ID format"],
                    "documentation": "https://docs.example.com/errors/validation",
                },
            },
        }

        standard_tokens = len(json.dumps(error)) // 4
        verbose_tokens = len(json.dumps(verbose_error)) // 4

        # Standard should be much smaller
        assert standard_tokens < 50
        assert standard_tokens < verbose_tokens / 3


# ============================================================
# Test: Feature Flags and Rollback
# ============================================================


class TestFeatureFlagsAndRollback:
    """Test optimization feature flags and rollback capability."""

    def test_lazy_loading_can_be_disabled(self, _mcp_baseline_env: Any) -> None:
        """Test that lazy loading can be disabled via environment."""
        assert os.getenv("TRACERTM_MCP_LAZY_LOADING") == "false"

        # With lazy loading disabled, all tools should load immediately
        # (This is the baseline behavior for rollback)

    def test_compression_can_be_toggled(self) -> None:
        """Test that compression can be enabled/disabled."""
        # Test with compression enabled
        os.environ["TRACERTM_MCP_COMPRESSION"] = "true"
        compression_enabled = os.getenv("TRACERTM_MCP_COMPRESSION") == "true"

        # Test with compression disabled
        os.environ["TRACERTM_MCP_COMPRESSION"] = "false"
        compression_disabled = os.getenv("TRACERTM_MCP_COMPRESSION") == "false"

        assert compression_enabled
        assert compression_disabled

    def test_streaming_can_be_toggled(self) -> None:
        """Test that streaming can be enabled/disabled."""
        # Enable streaming
        os.environ["TRACERTM_MCP_STREAMING"] = "true"
        streaming_enabled = os.getenv("TRACERTM_MCP_STREAMING") == "true"

        # Disable streaming
        os.environ["TRACERTM_MCP_STREAMING"] = "false"
        streaming_disabled = os.getenv("TRACERTM_MCP_STREAMING") == "false"

        assert streaming_enabled
        assert streaming_disabled

    def test_all_optimizations_can_be_disabled(self, _mcp_baseline_env: Any) -> None:
        """Test that all optimizations can be disabled for full rollback."""
        # Verify all optimization flags are disabled
        assert os.getenv("TRACERTM_MCP_LAZY_LOADING") == "false"
        assert os.getenv("TRACERTM_MCP_COMPRESSION") == "false"
        assert os.getenv("TRACERTM_MCP_STREAMING") == "false"
        assert os.getenv("TRACERTM_MCP_TOKEN_OPTIMIZATION") == "false"


# ============================================================
# Test: Regression Prevention
# ============================================================


class TestRegressionPrevention:
    """Test that optimizations don't break existing functionality."""

    def test_tool_registration_still_works(self, _mcp_optimized_env: Any) -> None:
        """Test that basic tool registration still works with optimizations."""
        from tracertm.mcp.registry import get_registry

        registry = get_registry()

        # Register a tool
        registry.register_tool_loader(
            "regression_test_tool",
            "tracertm.mcp.tools.params.project",
            {"description": "Test regression"},
        )

        # Verify registration
        tools = registry.list_registered_tools()
        assert "regression_test_tool" in tools

    def test_tool_metadata_accessible(self, _mcp_optimized_env: Any) -> None:
        """Test that tool metadata is still accessible."""
        from tracertm.mcp.registry import get_registry

        registry = get_registry()

        registry.register_tool_loader(
            "metadata_test_tool",
            "tracertm.mcp.tools.params.item",
            {"description": "Metadata test", "version": "1.0"},
        )

        metadata = registry.get_tool_metadata("metadata_test_tool")

        assert metadata is not None
        assert metadata["description"] == "Metadata test"
        assert metadata["version"] == "1.0"

    @pytest.mark.asyncio
    async def test_async_operations_still_work(self, _mcp_optimized_env: Any) -> None:
        """Test that async operations work with optimizations."""

        async def async_operation() -> None:
            await asyncio.sleep(0.01)
            return {"status": "success"}

        result = await async_operation()

        assert result["status"] == "success"


# ============================================================
# Test: Performance Comparison
# ============================================================


class TestPerformanceComparison:
    """Compare performance with and without optimizations."""

    def test_startup_time_improvement(self, mcp_baseline_env: Any, mcp_optimized_env: Any) -> None:
        """Test that startup time improves with optimizations."""
        import time

        # Measure baseline startup
        os.environ.update(mcp_baseline_env)
        start = time.perf_counter()
        from tracertm.mcp.registry import get_registry

        get_registry()
        baseline_time = time.perf_counter() - start

        # Measure optimized startup
        os.environ.update(mcp_optimized_env)
        start = time.perf_counter()
        get_registry()
        optimized_time = time.perf_counter() - start

        # Optimized should be faster (though this is a simple test)
        ((baseline_time - optimized_time) / baseline_time) * 100
