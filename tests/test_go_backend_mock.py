"""Test demonstrating Python cross-service mocks for the Go backend.

Uses respx to mock Go HTTP API endpoints.
"""

import pytest
import respx
from httpx import Response

from tracertm.clients.go_client import GoBackendClient, GoBackendError


@pytest.mark.asyncio
async def test_go_backend_mock_get_item() -> None:
    """Test mocking the Go backend's GET /api/v1/items/{id} endpoint."""
    base_url = "http://localhost:8080"
    client = GoBackendClient(base_url=base_url, service_token="test-token")
    item_id = "test-item-123"

    async with respx.mock(base_url=base_url) as respx_mock:
        # Mock successful response
        respx_mock.get(f"/api/v1/items/{item_id}").mock(
            return_value=Response(200, json={"id": item_id, "title": "Mocked Go Item", "status": "active"}),
        )

        item = await client.get_item(item_id)
        assert item["id"] == item_id
        assert item["title"] == "Mocked Go Item"


@pytest.mark.asyncio
async def test_go_backend_mock_error() -> None:
    """Test mocking a Go backend error response."""
    base_url = "http://localhost:8080"
    client = GoBackendClient(base_url=base_url, service_token="test-token")
    item_id = "error-item"

    async with respx.mock(base_url=base_url) as respx_mock:
        # Mock 404 response
        respx_mock.get(f"/api/v1/items/{item_id}").mock(return_value=Response(404, text="Not Found"))

        with pytest.raises(GoBackendError) as excinfo:
            await client.get_item(item_id)

        assert "404" in str(excinfo.value)


@pytest.mark.asyncio
async def test_go_backend_mock_create_link() -> None:
    """Test mocking the Go backend's POST /api/v1/links endpoint."""
    base_url = "http://localhost:8080"
    client = GoBackendClient(base_url=base_url, service_token="test-token")

    async with respx.mock(base_url=base_url) as respx_mock:
        respx_mock.post("/api/v1/links").mock(return_value=Response(201, json={"id": "link-123", "status": "created"}))

        result = await client.create_link("source-1", "target-1", "depends_on")
        assert result["id"] == "link-123"
        assert result["status"] == "created"
