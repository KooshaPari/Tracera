"""Chaos Test: External API (Go Backend Client) Resilience.

Tests that the GoBackendClient handles network timeouts, connection errors,
and HTTP failures correctly -- retrying with exponential backoff on transient
errors and raising GoBackendError on permanent failures.

Uses unittest.mock to simulate httpx failures without a live Go backend.
"""

from typing import Any, Never
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.clients.go_client import GoBackendClient, GoBackendError


@pytest.fixture
def go_client() -> None:
    """Build a GoBackendClient with a mocked httpx.AsyncClient."""
    client = GoBackendClient(base_url="http://fake-go:8080", service_token="test-token")
    client.client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.mark.chaos
class TestNetworkTimeoutResilience:
    """GoBackendClient must retry on TimeoutException and ultimately raise if all retries fail."""

    @pytest.mark.asyncio
    async def test_timeout_triggers_retry_and_raises(self, go_client: Any) -> None:
        """Three consecutive timeouts must exhaust retries and raise TimeoutException."""
        go_client.client.request = AsyncMock(side_effect=httpx.TimeoutException("read timed out"))

        # The tenacity decorator retries 3 times on TimeoutException, then reraises
        with pytest.raises(httpx.TimeoutException):
            await go_client.get_item("some-uuid")

        # Should have been called 3 times (initial + 2 retries)
        assert go_client.client.request.await_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_timeout_recovery_on_second_attempt(self, go_client: Any) -> None:
        """If the second attempt succeeds after a timeout, the result is returned."""
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"id": "item-1", "title": "Recovered"}
        success_response.raise_for_status = MagicMock()

        go_client.client.request = AsyncMock(
            side_effect=[
                httpx.TimeoutException("timed out"),
                success_response,
            ],
        )

        result = await go_client.get_item("item-1")
        assert result == {"id": "item-1", "title": "Recovered"}
        assert go_client.client.request.await_count == COUNT_TWO


@pytest.mark.chaos
class TestNetworkErrorResilience:
    """GoBackendClient must retry on NetworkError (connection refused, reset, etc.)."""

    @pytest.mark.asyncio
    async def test_connection_refused_retries_and_raises(self, go_client: Any) -> None:
        """ConnectionRefused (NetworkError subclass) must trigger retries."""
        go_client.client.request = AsyncMock(side_effect=httpx.NetworkError("Connection refused"))

        with pytest.raises(httpx.NetworkError):
            await go_client.search_items("test query")

        # 3 attempts total
        assert go_client.client.request.await_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_network_recovery_on_third_attempt(self, go_client: Any) -> None:
        """Network error resolves on third attempt -- client must return success."""
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"items": []}
        success_response.raise_for_status = MagicMock()

        go_client.client.request = AsyncMock(
            side_effect=[
                httpx.NetworkError("Connection reset"),
                httpx.NetworkError("Connection reset"),
                success_response,
            ],
        )

        result = await go_client.search_items("query")
        assert result == {"items": []}
        assert go_client.client.request.await_count == COUNT_THREE


@pytest.mark.chaos
class TestHTTPErrorHandling:
    """Non-retryable HTTP errors (4xx, 5xx) must raise GoBackendError immediately."""

    @pytest.mark.asyncio
    async def test_http_500_raises_go_backend_error(self, go_client: Any) -> None:
        """500 Internal Server Error must raise GoBackendError (not retried as an HTTP status error)."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        go_client.client.request = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response,
            ),
        )

        with pytest.raises(GoBackendError, match="Request failed with status 500"):
            await go_client.get_item("item-1")

        # HTTPStatusError is NOT retried -- only 1 call
        assert go_client.client.request.await_count == 1

    @pytest.mark.asyncio
    async def test_http_404_raises_go_backend_error(self, go_client: Any) -> None:
        """404 Not Found must raise GoBackendError (not retried)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        go_client.client.request = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found",
                request=MagicMock(),
                response=mock_response,
            ),
        )

        with pytest.raises(GoBackendError, match="Request failed with status 404"):
            await go_client.update_item("missing-id", {"title": "new"})

        assert go_client.client.request.await_count == 1

    @pytest.mark.asyncio
    async def test_unexpected_exception_raises_go_backend_error(self, go_client: Any) -> None:
        """Completely unexpected exceptions must raise GoBackendError."""
        go_client.client.request = AsyncMock(side_effect=RuntimeError("something bizarre happened"))

        with pytest.raises(GoBackendError, match="Unexpected error"):
            await go_client.health_check()

        assert go_client.client.request.await_count == 1


@pytest.mark.chaos
class TestClientLifecycle:
    """Verify client close/context-manager behaviour under failure conditions."""

    @pytest.mark.asyncio
    async def test_close_disposes_client(self, go_client: Any) -> None:
        """close() must call aclose() on the underlying httpx client."""
        go_client.client.aclose = AsyncMock()
        await go_client.close()
        go_client.client.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_context_manager_closes_on_exception(self) -> Never:
        """Async with GoBackendClient must close even if body raises."""
        client = GoBackendClient(base_url="http://fake:8080")
        client.client = AsyncMock(spec=httpx.AsyncClient)
        client.client.aclose = AsyncMock()

        with pytest.raises(ValueError, match="boom"):
            async with client:
                msg = "boom"
                raise ValueError(msg)

        client.client.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_auth_header_set_when_token_provided(self, go_client: Any) -> None:
        """Requests must include Authorization header when service_token is set."""
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"status": "ok"}
        success_response.raise_for_status = MagicMock()
        go_client.client.request = AsyncMock(return_value=success_response)

        await go_client.health_check()

        call_kwargs = go_client.client.request.call_args
        headers = call_kwargs.kwargs.get("headers", {})
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
