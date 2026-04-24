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
import contextlib
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from mcp.server.streamable_http import DEFAULT_NEGOTIATED_VERSION, MCP_SESSION_ID_HEADER

from tests.test_constants import COUNT_FIVE, COUNT_TEN, HTTP_OK
from tracertm.mcp.http_transport import (
    DEFAULT_MCP_PATH,
    create_progress_stream,
    create_standalone_http_app,
    get_transport_type,
    mount_mcp_to_fastapi,
    run_http_server,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

JSON_HEADERS = {"Accept": "application/json"}


async def open_mcp_session(client: AsyncClient) -> str:
    """Open a Streamable HTTP session and return session ID."""
    response = await client.post(
        "/api/v1/mcp",
        headers=JSON_HEADERS,
        json={
            "jsonrpc": "2.0",
            "id": "init",
            "method": "initialize",
            "params": {
                "protocolVersion": DEFAULT_NEGOTIATED_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "0.0.0"},
            },
        },
    )
    assert response.status_code == HTTP_OK
    session_id = response.headers.get(MCP_SESSION_ID_HEADER)
    assert session_id
    return session_id


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def fastapi_app() -> None:
    """Create a FastAPI app with mounted MCP."""
    app = FastAPI()
    mount_mcp_to_fastapi(app, path="/api/v1/mcp", transport="streamable-http")
    return app


@pytest_asyncio.fixture
async def fastapi_client(fastapi_app: Any) -> None:
    """Create an async HTTP client for FastAPI app."""
    async with fastapi_app.router.lifespan_context(fastapi_app):
        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test",
            follow_redirects=True,
        ) as client:
            yield client


# =============================================================================
# Standalone HTTP Server Tests
# =============================================================================


class TestStandaloneHTTPServer:
    """Test standalone MCP HTTP server."""

    def test_app_creation_disallowed(self) -> None:
        """Standalone HTTP app creation is disallowed."""
        with pytest.raises(RuntimeError, match="Standalone MCP is not allowed"):
            create_standalone_http_app(
                path=DEFAULT_MCP_PATH,
                transport="streamable-http",
                enable_cors=True,
            )

    @pytest.mark.asyncio
    async def test_run_http_server_disallowed(self) -> None:
        """Standalone HTTP server run is disallowed."""
        with pytest.raises(RuntimeError, match="Standalone MCP is not allowed"):
            await run_http_server()


# =============================================================================
# FastAPI Integration Tests
# =============================================================================


@pytest.mark.asyncio
class TestFastAPIIntegration:
    """Test MCP mounted to FastAPI app."""

    async def test_mounted_path(self, fastapi_client: Any) -> None:
        """Test that MCP is mounted at correct path."""
        session_id = await open_mcp_session(fastapi_client)
        response = await fastapi_client.post(
            "/api/v1/mcp",
            headers={**JSON_HEADERS, MCP_SESSION_ID_HEADER: session_id},
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1,
            },
        )

        assert response.status_code == HTTP_OK

    async def test_fastapi_middleware_integration(self, fastapi_app: Any) -> None:
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
                ),
            ],
        )
        mount_mcp_to_fastapi(test_app, path="/mcp")

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.options("/mcp")
            assert response.status_code in {200, 204, 307, 405}  # CORS or redirect


# =============================================================================
# SSE Progress Streaming Tests
# =============================================================================


@pytest.mark.asyncio
class TestSSEProgressStreaming:
    """Test SSE progress streaming functionality."""

    async def test_progress_stream_creation(self) -> None:
        """Test creating a progress stream."""

        async def mock_progress_generator() -> AsyncGenerator[dict[str, Any], None]:
            for i in range(5):
                yield {"progress": i, "total": 5, "message": f"Step {i}"}
                await asyncio.sleep(0.01)

        events = [event async for event in create_progress_stream("task-123", mock_progress_generator())]

        # Verify stream structure
        assert len(events) == 7  # start + 5 progress + complete
        assert events[0]["event"] == "stream_start"
        assert events[-1]["event"] == "stream_complete"

        # Verify progress events
        progress_events = [e for e in events if e["event"] == "progress"]
        assert len(progress_events) == COUNT_FIVE
        for i, event in enumerate(progress_events):
            assert event["data"]["task_id"] == "task-123"
            assert event["data"]["progress"] == i

    async def test_progress_stream_cancellation(self) -> None:
        """Test that cancelled streams emit cancellation event."""

        async def slow_generator() -> AsyncGenerator[dict[str, Any], None]:
            for i in range(100):
                yield {"progress": i}
                await asyncio.sleep(0.1)  # Slow to ensure cancellation

        events = []

        async def consume_stream() -> None:
            events.extend([event async for event in create_progress_stream("task-456", slow_generator())])

        task = asyncio.create_task(consume_stream())
        await asyncio.sleep(0.35)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        # Should have start, some progress, and cancellation
        assert events[0]["event"] == "stream_start"
        assert any(e["event"] == "stream_cancelled" for e in events)

    async def test_progress_stream_error_handling(self) -> None:
        """Test error handling in progress streams."""

        async def error_generator() -> AsyncGenerator[dict[str, Any], None]:
            yield {"progress": 1}
            msg = "Test error"
            raise ValueError(msg)
            yield {"progress": 2}  # Should never reach this

        events = [event async for event in create_progress_stream("task-789", error_generator())]

        # Should have start, progress, and error
        assert events[0]["event"] == "stream_start"
        assert any(e["event"] == "stream_error" for e in events)
        error_event = next(e for e in events if e["event"] == "stream_error")
        assert "Test error" in error_event["data"]["error"]


# =============================================================================
# Transport Selection Tests
# =============================================================================


class TestTransportSelection:
    """Test transport type selection logic."""

    def test_default_transport(self, monkeypatch: Any) -> None:
        """Test default transport is http."""
        monkeypatch.delenv("TRACERTM_MCP_TRANSPORT", raising=False)
        transport = get_transport_type()
        assert transport == "http"

    def test_env_transport_http(self, monkeypatch: Any) -> None:
        """Test HTTP transport from environment."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "http")
        transport = get_transport_type()
        assert transport == "http"

    def test_env_transport_streamable_http(self, monkeypatch: Any) -> None:
        """Test streamable-http transport from environment."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "streamable-http")
        transport = get_transport_type()
        assert transport == "streamable-http"

    def test_env_transport_sse(self, monkeypatch: Any) -> None:
        """Test SSE transport from environment."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "sse")
        transport = get_transport_type()
        assert transport == "sse"

    def test_invalid_transport_fallback(self, monkeypatch: Any) -> None:
        """Test fallback to http for invalid transport."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "invalid")
        transport = get_transport_type()
        assert transport == "http"

    def test_case_insensitive_transport(self, monkeypatch: Any) -> None:
        """Test transport is case-insensitive."""
        monkeypatch.setenv("TRACERTM_MCP_TRANSPORT", "HTTP")
        transport = get_transport_type()
        assert transport == "http"


# =============================================================================
# Concurrent Requests Tests
# =============================================================================


@pytest.mark.asyncio
class TestConcurrentRequests:
    """Test handling of concurrent requests."""

    async def test_concurrent_tool_calls(self, fastapi_client: Any) -> None:
        """Test multiple concurrent tool calls."""
        session_id = await open_mcp_session(fastapi_client)
        # Create multiple requests
        tasks = [
            fastapi_client.post(
                "/api/v1/mcp",
                headers={**JSON_HEADERS, MCP_SESSION_ID_HEADER: session_id},
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
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == i

    async def test_request_isolation(self, fastapi_client: Any) -> None:
        """Test that concurrent requests are isolated."""
        session_id = await open_mcp_session(fastapi_client)
        # Send requests with different IDs simultaneously
        task1 = fastapi_client.post(
            "/api/v1/mcp",
            headers={**JSON_HEADERS, MCP_SESSION_ID_HEADER: session_id},
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": "request-1",
            },
        )

        task2 = fastapi_client.post(
            "/api/v1/mcp",
            headers={**JSON_HEADERS, MCP_SESSION_ID_HEADER: session_id},
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


@pytest.mark.asyncio
@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics of HTTP transport."""

    async def test_throughput(self, fastapi_client: Any) -> None:
        """Test request throughput."""
        import time

        session_id = await open_mcp_session(fastapi_client)
        start = time.time()
        num_requests = 100

        tasks = [
            fastapi_client.post(
                "/api/v1/mcp",
                headers={**JSON_HEADERS, MCP_SESSION_ID_HEADER: session_id},
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

        # Reasonable throughput threshold (adjust based on requirements)
        assert throughput > COUNT_TEN  # At least 10 req/s

    async def test_response_time(self, fastapi_client: Any) -> None:
        """Test average response time."""
        import time

        session_id = await open_mcp_session(fastapi_client)
        times = []

        for i in range(20):
            start = time.time()
            await fastapi_client.post(
                "/api/v1/mcp",
                headers={**JSON_HEADERS, MCP_SESSION_ID_HEADER: session_id},
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": i,
                },
            )
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)

        # Response time should be reasonable
        assert avg_time < 0.5  # Less than 500ms on average
