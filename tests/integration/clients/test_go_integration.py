from typing import Any

"""Integration tests for Go Backend Client."""

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from aiohttp import web

from tests.test_constants import COUNT_TEN, COUNT_THREE
from tracertm.clients.go_client import GoBackendClient, GoBackendError, generate_cache_key


@pytest.fixture
async def mock_go_server(aiohttp_server: Any, _aiohttp_client: Any) -> None:
    """Create a mock Go backend server."""
    request_count = {"count": 0}

    async def health_handler(_request: Any) -> None:
        return web.json_response({"status": "healthy", "service": "go-backend"})

    async def get_item_handler(request: Any) -> None:
        item_id = request.match_info["item_id"]
        return web.json_response({
            "id": item_id,
            "title": "Test Item",
            "type": "requirement",
            "project_id": "proj-123",
        })

    async def create_link_handler(request: Any) -> None:
        data = await request.json()
        return web.json_response({
            "id": "link-123",
            "source_id": data["source_id"],
            "target_id": data["target_id"],
            "link_type": data["link_type"],
            "metadata": data.get("metadata", {}),
        })

    async def search_items_handler(request: Any) -> None:
        query = request.query.get("q", "")
        return web.json_response({"results": [{"id": "item-1", "title": f"Result for {query}"}], "total": 1})

    async def retry_handler(_request: Any) -> None:
        request_count["count"] += 1
        if request_count["count"] < COUNT_THREE:
            return web.Response(status=503, text="Service Unavailable")
        return web.json_response({"status": "success", "attempt": request_count["count"]})

    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/api/v1/items/{item_id}", get_item_handler)
    app.router.add_post("/api/v1/links", create_link_handler)
    app.router.add_get("/api/v1/search/items", search_items_handler)
    app.router.add_get("/test/retry", retry_handler)

    return await aiohttp_server(app)


@pytest.mark.asyncio
async def test_go_client_health_check(mock_go_server: Any) -> None:
    """Test health check endpoint."""
    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        result = await client.health_check()
        assert result["status"] == "healthy"
        assert result["service"] == "go-backend"


@pytest.mark.asyncio
async def test_go_client_get_item(mock_go_server: Any) -> None:
    """Test getting an item by ID."""
    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        result = await client.get_item("item-456")
        assert result["id"] == "item-456"
        assert result["title"] == "Test Item"
        assert result["type"] == "requirement"


@pytest.mark.asyncio
async def test_go_client_create_link(mock_go_server: Any) -> None:
    """Test creating a link between items."""
    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        result = await client.create_link(
            source_id="item-1",
            target_id="item-2",
            link_type="DEPENDS_ON",
            metadata={"weight": 1.0},
        )
        assert result["id"] == "link-123"
        assert result["source_id"] == "item-1"
        assert result["target_id"] == "item-2"
        assert result["link_type"] == "DEPENDS_ON"
        assert result["metadata"]["weight"] == 1.0


@pytest.mark.asyncio
async def test_go_client_search_items(mock_go_server: Any) -> None:
    """Test searching for items."""
    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        result = await client.search_items("test query", filters={"project_id": "proj-123"})
        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert "test query" in result["results"][0]["title"]


@pytest.mark.asyncio
async def test_go_client_retry_logic(mock_go_server: Any) -> None:
    """Test that client retries on network errors."""
    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        # This endpoint fails twice then succeeds
        result = await client._request("GET", "/test/retry")
        assert result["status"] == "success"
        assert result["attempt"] >= COUNT_THREE  # Should have retried at least 3 times


@pytest.mark.asyncio
async def test_go_client_connection_pooling() -> None:
    """Test that connection pooling works correctly."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        GoBackendClient("http://localhost:8080")

        # Verify client was created with correct limits
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["timeout"] == 30.0
        assert call_kwargs["limits"].max_connections == 100
        assert call_kwargs["limits"].max_keepalive_connections == 20


@pytest.mark.asyncio
async def test_go_client_service_token_injection() -> None:
    """Test that service token is properly injected."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        async with GoBackendClient("http://localhost:8080", "test-token") as client:
            await client._request("GET", "/test")

            # Verify Authorization header was set
            call_args = mock_client.request.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_go_client_error_handling() -> None:
    """Test error handling for various HTTP errors."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Simulate 404 error
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404",
            request=AsyncMock(),
            response=mock_response,
        )
        mock_client.request.return_value = mock_response

        async with GoBackendClient("http://localhost:8080") as client:
            with pytest.raises(GoBackendError) as exc_info:
                await client._request("GET", "/nonexistent")
            assert "404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_go_client_timeout() -> None:
    """Test request timeout behavior."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Simulate timeout
        mock_client.request.side_effect = httpx.TimeoutException("Request timed out")

        async with GoBackendClient("http://localhost:8080") as client:
            # Tenacity will retry TimeoutException
            with pytest.raises(httpx.TimeoutException):
                await client._request("GET", "/slow-endpoint")


@pytest.mark.asyncio
async def test_go_client_context_manager() -> None:
    """Test async context manager properly closes client."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        async with GoBackendClient("http://localhost:8080"):
            pass

        mock_client.aclose.assert_called_once()


def test_generate_cache_key() -> None:
    """Test cache key generation."""
    key1 = generate_cache_key("prefix", "GET", "/path", {"foo": "bar"})
    key2 = generate_cache_key("prefix", "GET", "/path", {"foo": "bar"})
    key3 = generate_cache_key("prefix", "GET", "/path", {"foo": "baz"})

    assert key1 == key2, "Same inputs should generate same key"
    assert key1 != key3, "Different inputs should generate different keys"
    assert key1.startswith("prefix:"), "Cache key should include prefix"


@pytest.mark.asyncio
async def test_go_client_concurrent_requests() -> None:
    """Test handling of concurrent requests."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client

        async with GoBackendClient("http://localhost:8080") as client:
            # Make 10 concurrent requests
            tasks = [client._request("GET", f"/test/{i}") for i in range(10)]
            results = await asyncio.gather(*tasks)

            assert len(results) == COUNT_TEN
            assert all(r["status"] == "ok" for r in results)
            assert mock_client.request.call_count == COUNT_TEN


@pytest.mark.asyncio
async def test_go_client_update_item(mock_go_server: Any) -> None:
    """Test updating an item."""

    async def update_handler(request: Any) -> None:
        from aiohttp import web

        item_id = request.match_info["item_id"]
        data = await request.json()
        return web.json_response({
            "id": item_id,
            "title": data.get("title", "Updated"),
            "description": data.get("description", ""),
        })

    # Add update endpoint to mock server
    mock_go_server._app.router.add_patch("/api/v1/items/{item_id}", update_handler)

    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        result = await client.update_item("item-789", {"title": "New Title", "description": "New Desc"})
        assert result["id"] == "item-789"
        assert result["title"] == "New Title"
        assert result["description"] == "New Desc"


@pytest.mark.asyncio
async def test_go_client_delete_item(mock_go_server: Any) -> None:
    """Test deleting an item."""

    async def delete_handler(request: Any) -> None:
        from aiohttp import web

        item_id = request.match_info["item_id"]
        return web.json_response({"success": True, "id": item_id})

    # Add delete endpoint to mock server
    mock_go_server._app.router.add_delete("/api/v1/items/{item_id}", delete_handler)

    base_url = f"http://{mock_go_server.host}:{mock_go_server.port}"
    async with GoBackendClient(base_url) as client:
        result = await client.delete_item("item-999")
        assert result["success"] is True
        assert result["id"] == "item-999"
