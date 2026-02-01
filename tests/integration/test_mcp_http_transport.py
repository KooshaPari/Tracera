"""Integration tests for MCP HTTP transport layer.

Tests the FastMCP 3.0 HTTP/SSE transport implementation including:
- JSON-RPC 2.0 message format
- SSE streaming for progress updates
- Dual transport support (STDIO + HTTP)
- FastAPI router integration
- Standalone HTTP server
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from tracertm.mcp.http_transport import (
    create_standalone_http_app,
    mount_mcp_to_fastapi,
    create_progress_stream,
    get_transport_type,
    DEFAULT_MCP_PATH,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def standalone_app():
    """Create a standalone MCP HTTP app."""
    return create_standalone_http_app(
        path=DEFAULT_MCP_PATH,
        transport="streamable-http",
        enable_cors=True,
    )


@pytest.fixture
def fastapi_app():
    """Create a FastAPI app with mounted MCP."""
    app = FastAPI()
    mount_mcp_to_fastapi(app, path="/api/v1/mcp", transport="streamable-http")
    return app


@pytest.fixture
async def standalone_client(standalone_app):
    """Create an async HTTP client for standalone app."""
    async with AsyncClient(app=standalone_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def fastapi_client(fastapi_app):
    """Create an async HTTP client for FastAPI app."""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client


# =============================================================================
# Standalone HTTP Server Tests
# =============================================================================


class TestStandaloneHTTPServer:
    """Test standalone MCP HTTP server."""

    async def test_app_creation(self, standalone_app):
        """Test that standalone app is created successfully."""
        assert standalone_app is not None
        assert hasattr(standalone_app, "routes")

    async def test_tools_list_jsonrpc(self, standalone_client):
        """Test tools/list via JSON-RPC 2.0."""
        response = await standalone_client.post(
            DEFAULT_MCP_PATH,
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify JSON-RPC 2.0 format
        assert data["jsonrpc"] == "2.0"
        assert "result" in data or "error" in data
        assert data["id"] == 1

        # If successful, verify tools are returned
        if "result" in data:
            assert "tools" in data["result"]
            assert isinstance(data["result"]["tools"], list)

    async def test_invalid_method(self, standalone_client):
        """Test error handling for invalid method."""
        response = await standalone_client.post(
            DEFAULT_MCP_PATH,
            json={
                "jsonrpc": "2.0",
                "method": "invalid/method",
                "id": 2,
            },
        )

        assert response.status_code == 200  # JSON-RPC returns 200 with error
        data = response.json()

        assert data["jsonrpc"] == "2.0"
        assert "error" in data
        assert data["id"] == 2

    async def test_malformed_request(self, standalone_client):
        """Test error handling for malformed request."""
        response = await standalone_client.post(
            DEFAULT_MCP_PATH,
            json={"not": "valid"},
        )

        # May return 4xx or 200 with error depending on FastMCP version
        assert response.status_code in (200, 400, 422)


# =============================================================================
# FastAPI Integration Tests
# =============================================================================


class TestFastAPIIntegration:
    """Test MCP mounted to FastAPI app."""

    async def test_mounted_path(self, fastapi_client):
        """Test that MCP is mounted at correct path."""
        response = await fastapi_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1,
            },
        )

        assert response.status_code == 200

    async def test_fastapi_middleware_integration(self, fastapi_app):
        """Test that FastAPI middleware can be applied."""
        # Verify middleware stack exists
        assert hasattr(fastapi_app, "middleware_stack")

        # Test with middleware
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware

        test_app = FastAPI(
            middleware=[
                Middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_methods=["*"],
                )
            ]
        )
        mount_mcp_to_fastapi(test_app, path="/mcp")

        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.options("/mcp")
            assert response.status_code in (200, 204, 405)  # CORS or not supported


# =============================================================================
# SSE Progress Streaming Tests
# =============================================================================


class TestSSEProgressStreaming:
    """Test SSE progress streaming functionality."""

    async def test_progress_stream_creation(self):
        """Test creating a progress stream."""

        async def mock_progress_generator() -> AsyncGenerator[dict[str, Any], None]:
            for i in range(5):
                yield {"progress": i, "total": 5, "message": f"Step {i}"}
                await asyncio.sleep(0.01)

        events = []
        async for event in create_progress_stream("task-123", mock_progress_generator()):
            events.append(event)

        # Verify stream structure
        assert len(events) == 7  # start + 5 progress + complete
        assert events[0]["event"] == "stream_start"
        assert events[-1]["event"] == "stream_complete"

        # Verify progress events
        progress_events = [e for e in events if e["event"] == "progress"]
        assert len(progress_events) == 5
        for i, event in enumerate(progress_events):
            assert event["data"]["task_id"] == "task-123"
            assert event["data"]["progress"] == i

    async def test_progress_stream_cancellation(self):
        """Test that cancelled streams emit cancellation event."""

        async def slow_generator() -> AsyncGenerator[dict[str, Any], None]:
            for i in range(100):
                yield {"progress": i}
                await asyncio.sleep(0.1)  # Slow to ensure cancellation

        events = []
        try:
            async for event in create_progress_stream("task-456", slow_generator()):
                events.append(event)
                if len(events) >= 3:  # Cancel after a few events
                    raise asyncio.CancelledError()
        except asyncio.CancelledError:
            pass

        # Should have start, some progress, and cancellation
        assert events[0]["event"] == "stream_start"
        assert any(e["event"] == "stream_cancelled" for e in events)

    async def test_progress_stream_error_handling(self):
        """Test error handling in progress streams."""

        async def error_generator() -> AsyncGenerator[dict[str, Any], None]:
            yield {"progress": 1}
            raise ValueError("Test error")
            yield {"progress": 2}  # Should never reach this

        events = []
        async for event in create_progress_stream("task-789", error_generator()):
            events.append(event)

        # Should have start, progress, and error
        assert events[0]["event"] == "stream_start"
        assert any(e["event"] == "stream_error" for e in events)
        error_event = [e for e in events if e["event"] == "stream_error"][0]
        assert "Test error" in error_event["data"]["error"]


# =============================================================================
# Transport Selection Tests
# =============================================================================


class TestTransportSelection:
    """Test transport type selection logic."""

    def test_default_transport(self, monkeypatch):
        """Test default transport is stdio."""
        monkeypatch.delenv("TRACERTM_MCP_TRANSPORT", raising=False)
        transport = get_transport_type()
        assert transport == "stdio"

    def test_env_transport_http(self, monkeypatch):
        """Test HTTP transport from environment."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "http")
        transport = get_transport_type()
        assert transport == "http"

    def test_env_transport_streamable_http(self, monkeypatch):
        """Test streamable-http transport from environment."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "streamable-http")
        transport = get_transport_type()
        assert transport == "streamable-http"

    def test_env_transport_sse(self, monkeypatch):
        """Test SSE transport from environment."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "sse")
        transport = get_transport_type()
        assert transport == "sse"

    def test_invalid_transport_fallback(self, monkeypatch):
        """Test fallback to stdio for invalid transport."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "invalid")
        transport = get_transport_type()
        assert transport == "stdio"

    def test_case_insensitive_transport(self, monkeypatch):
        """Test transport is case-insensitive."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "HTTP")
        transport = get_transport_type()
        assert transport == "http"


# =============================================================================
# Concurrent Requests Tests
# =============================================================================


class TestConcurrentRequests:
    """Test handling of concurrent requests."""

    async def test_concurrent_tool_calls(self, standalone_client):
        """Test multiple concurrent tool calls."""
        # Create multiple requests
        tasks = [
            standalone_client.post(
                DEFAULT_MCP_PATH,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": i,
                },
            )
            for i in range(10)
        ]

        # Execute concurrently
        responses = await asyncio.gather(*tasks)

        # Verify all succeeded
        for i, response in enumerate(responses):
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == i

    async def test_request_isolation(self, standalone_client):
        """Test that concurrent requests are isolated."""
        # Send requests with different IDs simultaneously
        task1 = standalone_client.post(
            DEFAULT_MCP_PATH,
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "request-1",
            },
        )

        task2 = standalone_client.post(
            DEFAULT_MCP_PATH,
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "request-2",
            },
        )

        response1, response2 = await asyncio.gather(task1, task2)

        # Verify responses match requests
        data1 = response1.json()
        data2 = response2.json()

        assert data1["id"] == "request-1"
        assert data2["id"] == "request-2"


# =============================================================================
# Performance Tests
# =============================================================================


@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics of HTTP transport."""

    async def test_throughput(self, standalone_client):
        """Test request throughput."""
        import time

        start = time.time()
        num_requests = 100

        tasks = [
            standalone_client.post(
                DEFAULT_MCP_PATH,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": i,
                },
            )
            for i in range(num_requests)
        ]

        await asyncio.gather(*tasks)
        elapsed = time.time() - start

        throughput = num_requests / elapsed
        print(f"\nThroughput: {throughput:.2f} requests/second")

        # Reasonable throughput threshold (adjust based on requirements)
        assert throughput > 10  # At least 10 req/s

    async def test_response_time(self, standalone_client):
        """Test average response time."""
        import time

        times = []

        for i in range(20):
            start = time.time()
            await standalone_client.post(
                DEFAULT_MCP_PATH,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": i,
                },
            )
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"\nAverage response time: {avg_time*1000:.2f}ms")

        # Response time should be reasonable
        assert avg_time < 0.5  # Less than 500ms on average
