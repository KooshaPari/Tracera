"""Go Backend HTTP client with retry logic and connection pooling."""

import hashlib
import json
import os
import types
from collections.abc import Mapping
from typing import Self

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class GoBackendError(Exception):
    """Base exception for Go backend client errors."""


def _raise_type_error(result_type: type) -> None:
    """Raise a GoBackendError for unexpected response type.

    Args:
        result_type: The unexpected result type

    Raises:
        GoBackendError: Always raised with type information
    """
    msg = f"Unexpected response type: {result_type}"
    raise GoBackendError(msg)


class GoBackendClient:
    """Async HTTP client for Go backend communication.

    Features:
    - Connection pooling for efficient resource usage
    - Automatic retries on network errors (3 attempts with exponential backoff)
    - 30-second timeout per request
    - Service token authentication
    """

    def __init__(self, base_url: str, service_token: str | None = None) -> None:
        """Initialize the Go backend client.

        Args:
            base_url: Base URL of the Go backend (e.g., http://localhost:8080)
            service_token: Optional service token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.service_token = service_token or os.getenv("GO_SERVICE_TOKEN", "")

        # Configure httpx client with connection pooling
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        path: str,
        json_data: dict[str, object] | None = None,
        params: Mapping[str, str | int] | None = None,
    ) -> dict[str, object]:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path (should start with /)
            json_data: Optional JSON request body
            params: Optional query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            GoBackendError: If request fails after all retries
        """
        url = f"{self.base_url}{path}"

        # Prepare headers
        headers = {}
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"

        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
            )

            # Raise for HTTP errors
            response.raise_for_status()

            # Parse JSON response
            result = response.json()
            if isinstance(result, dict):
                return result

            _raise_type_error(type(result))

        except httpx.HTTPStatusError as e:
            msg = f"Request failed with status {e.response.status_code}: {e.response.text}"
            raise GoBackendError(msg) from e
        except (httpx.NetworkError, httpx.TimeoutException):
            # These will be retried by tenacity
            raise
        except Exception as e:
            msg = f"Unexpected error during request: {e!s}"
            raise GoBackendError(msg) from e

    async def get_item(self, item_id: str) -> dict[str, object]:
        """Get an item by ID from Go backend.

        Args:
            item_id: Item UUID

        Returns:
            Item data as dictionary
        """
        return await self._request("GET", f"/api/v1/items/{item_id}")

    async def create_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create a link between two items.

        Args:
            source_id: Source item UUID
            target_id: Target item UUID
            link_type: Type of link (e.g., "DEPENDS_ON", "IMPLEMENTS")
            metadata: Optional metadata for the link

        Returns:
            Created link data as dictionary
        """
        payload = {
            "source_id": source_id,
            "target_id": target_id,
            "link_type": link_type,
            "metadata": metadata or {},
        }
        return await self._request("POST", "/api/v1/links", json_data=dict(payload))

    async def search_items(self, query: str, filters: dict[str, str] | None = None) -> dict[str, object]:
        """Search items in Go backend.

        Args:
            query: Search query string
            filters: Optional filters (project_id, item_type, etc.)

        Returns:
            Search results as dictionary
        """
        params: dict[str, str] = {"q": query}
        if filters:
            params.update(filters)

        return await self._request("GET", "/api/v1/search/items", params=params)

    async def get_project_items(self, project_id: str, item_type: str | None = None) -> dict[str, object]:
        """Get all items for a project.

        Args:
            project_id: Project UUID
            item_type: Optional filter by item type

        Returns:
            List of items as dictionary
        """
        params: dict[str, str] = {}
        if item_type:
            params["type"] = item_type

        return await self._request("GET", f"/api/v1/projects/{project_id}/items", params=params)

    async def update_item(self, item_id: str, update_data: dict[str, object]) -> dict[str, object]:
        """Update an item.

        Args:
            item_id: Item UUID
            update_data: Fields to update

        Returns:
            Updated item data as dictionary
        """
        return await self._request("PATCH", f"/api/v1/items/{item_id}", json_data=update_data)

    async def delete_item(self, item_id: str) -> dict[str, object]:
        """Delete an item.

        Args:
            item_id: Item UUID

        Returns:
            Deletion confirmation as dictionary
        """
        return await self._request("DELETE", f"/api/v1/items/{item_id}")

    async def get_graph_data(
        self, project_id: str, root_item_id: str | None = None, depth: int = 3
    ) -> dict[str, object]:
        """Get graph data for visualization.

        Args:
            project_id: Project UUID
            root_item_id: Optional root item to start from
            depth: Maximum traversal depth

        Returns:
            Graph data (nodes and edges) as dictionary
        """
        params: dict[str, str | int] = {"depth": depth}
        if root_item_id:
            params["root_id"] = root_item_id

        return await self._request("GET", f"/api/v1/projects/{project_id}/graph", params=params)

    async def health_check(self) -> dict[str, object]:
        """Check Go backend health.

        Returns:
            Health status as dictionary
        """
        return await self._request("GET", "/health")

    async def close(self) -> None:
        """Close the HTTP client and release connections."""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()


def generate_cache_key(prefix: str, *args: object) -> str:
    """Generate a consistent cache key from arguments.

    Args:
        prefix: Cache key prefix (e.g., "go_client")
        *args: Variable arguments to include in hash

    Returns:
        Cache key string
    """
    h = hashlib.sha256()
    h.update(prefix.encode())
    for arg in args:
        if isinstance(arg, dict):
            h.update(json.dumps(arg, sort_keys=True).encode())
        else:
            h.update(str(arg).encode())

    return f"{prefix}:{h.hexdigest()[:32]}"
