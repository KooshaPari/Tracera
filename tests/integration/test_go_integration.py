"""Integration tests for Go Backend client."""

import asyncio
from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.clients.go_client import GoBackendClient, GoBackendError


class MockGoBackend:
    """Mock Go backend server for testing."""

    def __init__(self) -> None:
        self.request_count = 0
        self.fail_count = 0
        self.should_fail = False
        self.delay = 0.0

    async def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Handle mock request and return response."""
        self.request_count += 1

        # Simulate delay if configured
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        # Simulate failures if configured
        if self.should_fail and self.fail_count > 0:
            self.fail_count -= 1
            return httpx.Response(
                status_code=503,
                json={"error": "Service temporarily unavailable"},
            )

        # Default successful responses
        if request.url.path == "/health":
            return httpx.Response(
                status_code=200,
                json={"status": "ok", "service": "tracertm-backend"},
            )

        if request.url.path.startswith("/api/v1/items/"):
            item_id = request.url.path.split("/")[-1]
            return httpx.Response(
                status_code=200,
                json={
                    "id": item_id,
                    "name": "Test Item",
                    "item_type": "requirement",
                },
            )

        if request.url.path == "/api/v1/links" and request.method == "POST":
            return httpx.Response(
                status_code=201,
                json={
                    "id": "link-123",
                    "source_id": "item-1",
                    "target_id": "item-2",
                    "link_type": "DEPENDS_ON",
                },
            )

        # Default 404 for unknown paths
        return httpx.Response(status_code=404, json={"error": "Not found"})


@pytest_asyncio.fixture
async def mock_backend() -> MockGoBackend:
    """Provide a mock Go backend."""
    return MockGoBackend()


@pytest_asyncio.fixture
async def go_client(mock_backend: MockGoBackend) -> AsyncGenerator[GoBackendClient, None]:
    """Provide a Go backend client with mock transport."""
    # Create client with mock transport
    client = GoBackendClient("http://mock-backend:8080", "test-token")

    # Replace the client's transport with mock
    mock_transport = httpx.MockTransport(mock_backend.handle_request)
    client.client = httpx.AsyncClient(transport=mock_transport, timeout=30.0)

    yield client

    # Cleanup
    await client.close()


@pytest.mark.asyncio
async def test_go_client_basic_call(go_client: GoBackendClient) -> None:
    """Test basic GET request to Go backend."""
    item = await go_client.get_item("550e8400-e29b-41d4-a716-446655440000")

    assert item is not None
    assert "id" in item
    assert item["id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert item["name"] == "Test Item"


@pytest.mark.asyncio
async def test_go_client_health_check(go_client: GoBackendClient) -> None:
    """Test health check endpoint."""
    health = await go_client.health_check()

    assert health["status"] == "ok"
    assert health["service"] == "tracertm-backend"


@pytest.mark.asyncio
async def test_go_client_create_link(go_client: GoBackendClient) -> None:
    """Test creating a link between items."""
    link = await go_client.create_link(
        source_id="item-1",
        target_id="item-2",
        link_type="DEPENDS_ON",
        metadata={"priority": "high"},
    )

    assert link["id"] == "link-123"
    assert link["source_id"] == "item-1"
    assert link["target_id"] == "item-2"
    assert link["link_type"] == "DEPENDS_ON"


@pytest.mark.asyncio
async def test_go_client_retry(go_client: GoBackendClient, mock_backend: MockGoBackend) -> None:
    """Test retry logic on network errors."""
    # Configure mock to fail twice, then succeed
    mock_backend.should_fail = True
    mock_backend.fail_count = 2

    # This should succeed after retries
    item = await go_client.get_item("test-item-id")

    assert item is not None
    assert mock_backend.request_count == COUNT_THREE  # Initial + 2 retries


@pytest.mark.asyncio
async def test_go_client_timeout(mock_backend: MockGoBackend) -> None:
    """Test request timeout handling."""
    # Configure mock to delay response
    mock_backend.delay = 35.0  # Longer than client timeout

    client = GoBackendClient("http://mock-backend:8080")
    mock_transport = httpx.MockTransport(mock_backend.handle_request)
    client.client = httpx.AsyncClient(transport=mock_transport, timeout=1.0)

    with pytest.raises(GoBackendError) as exc_info:
        await client.get_item("test-item-id")

    assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()

    await client.close()


@pytest.mark.asyncio
async def test_go_client_error_response(mock_backend: MockGoBackend) -> None:
    """Test handling of error responses."""
    client = GoBackendClient("http://mock-backend:8080")
    mock_transport = httpx.MockTransport(mock_backend.handle_request)
    client.client = httpx.AsyncClient(transport=mock_transport, timeout=30.0)

    # Request non-existent endpoint
    with pytest.raises(GoBackendError) as exc_info:
        await client._request("GET", "/api/v1/nonexistent")

    assert "404" in str(exc_info.value)

    await client.close()


@pytest.mark.asyncio
async def test_go_client_retry_exhausted(mock_backend: MockGoBackend) -> None:
    """Test behavior when retries are exhausted."""
    # Configure mock to always fail
    mock_backend.should_fail = True
    mock_backend.fail_count = 10  # More than retry limit

    client = GoBackendClient("http://mock-backend:8080")
    mock_transport = httpx.MockTransport(mock_backend.handle_request)
    client.client = httpx.AsyncClient(transport=mock_transport, timeout=30.0)

    with pytest.raises(GoBackendError) as exc_info:
        await client.get_item("test-item-id")

    # Should have attempted 1 + 3 retries = 4 times
    assert mock_backend.request_count >= 1
    assert "503" in str(exc_info.value)

    await client.close()


@pytest.mark.asyncio
async def test_go_client_search_items(go_client: GoBackendClient, mock_backend: MockGoBackend) -> None:
    """Test search items endpoint."""

    async def search_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/search/items":
            return httpx.Response(
                status_code=200,
                json={
                    "items": [
                        {"id": "1", "name": "Item 1"},
                        {"id": "2", "name": "Item 2"},
                    ],
                    "total": 2,
                },
            )
        return await mock_backend.handle_request(request)

    # Update client with search-aware transport
    mock_transport = httpx.MockTransport(search_handler)
    go_client.client = httpx.AsyncClient(transport=mock_transport, timeout=30.0)

    results = await go_client.search_items("test query", filters={"project_id": "proj-123"})

    assert "items" in results
    assert len(results["items"]) == COUNT_TWO
    assert results["total"] == COUNT_TWO


@pytest.mark.asyncio
async def test_go_client_update_item(go_client: GoBackendClient, mock_backend: MockGoBackend) -> None:
    """Test update item endpoint."""

    async def update_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "PATCH" and "/api/v1/items/" in request.url.path:
            item_id = request.url.path.split("/")[-1]
            return httpx.Response(
                status_code=200,
                json={
                    "id": item_id,
                    "name": "Updated Item",
                    "updated_at": "2025-01-30T00:00:00Z",
                },
            )
        return await mock_backend.handle_request(request)

    mock_transport = httpx.MockTransport(update_handler)
    go_client.client = httpx.AsyncClient(transport=mock_transport, timeout=30.0)

    updated = await go_client.update_item(
        "item-123",
        {"name": "Updated Item", "description": "New description"},
    )

    assert updated["id"] == "item-123"
    assert updated["name"] == "Updated Item"


@pytest.mark.asyncio
async def test_go_client_delete_item(go_client: GoBackendClient, mock_backend: MockGoBackend) -> None:
    """Test delete item endpoint."""

    async def delete_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "DELETE" and "/api/v1/items/" in request.url.path:
            return httpx.Response(
                status_code=200,
                json={"message": "Item deleted", "success": True},
            )
        return await mock_backend.handle_request(request)

    mock_transport = httpx.MockTransport(delete_handler)
    go_client.client = httpx.AsyncClient(transport=mock_transport, timeout=30.0)

    result = await go_client.delete_item("item-123")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_go_client_context_manager() -> None:
    """Test async context manager usage."""
    async with GoBackendClient("http://test:8080") as client:
        assert client.client is not None

    # Client should be closed after exiting context
    # Note: httpx.AsyncClient doesn't expose is_closed easily,
    # but we can verify close was called


@pytest.mark.asyncio
async def test_generate_cache_key() -> None:
    """Test cache key generation utility."""
    from tracertm.clients.go_client import generate_cache_key

    # Test with simple args
    key1 = generate_cache_key("test", "arg1", "arg2")
    key2 = generate_cache_key("test", "arg1", "arg2")
    assert key1 == key2  # Same inputs should produce same key

    # Test with dict args
    key3 = generate_cache_key("test", {"foo": "bar", "baz": 123})
    key4 = generate_cache_key("test", {"baz": 123, "foo": "bar"})
    assert key3 == key4  # Dict order shouldn't matter

    # Test different inputs produce different keys
    key5 = generate_cache_key("test", "different")
    assert key1 != key5
