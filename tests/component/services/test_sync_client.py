import asyncio
from datetime import UTC, datetime, timezone
from typing import Never

import httpx
import pytest

from tracertm.api.sync_client import ApiConfig, ApiError, AuthenticationError, SyncClient

pytestmark = pytest.mark.integration


class _DummyTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler) -> None:
        self.handler = handler

    async def handle_async_request(self, request):
        return await self.handler(request)


def _client_with(handler):
    transport = _DummyTransport(handler)
    client = SyncClient(ApiConfig(base_url="https://example.test"))
    client._client = httpx.AsyncClient(transport=transport, base_url="https://example.test")
    return client


@pytest.mark.asyncio
async def test_upload_changes_success() -> None:
    async def handler(request):
        assert request.url.path == "/api/sync/upload"
        return httpx.Response(
            200, json={"applied": ["1"], "conflicts": [], "server_time": datetime.now(UTC).isoformat(), "errors": []},
        )

    client = _client_with(handler)
    result = await client.upload_changes([])
    assert result.applied == ["1"]
    assert result.conflicts == []


@pytest.mark.asyncio
async def test_upload_changes_rate_limit_retry_then_fail(monkeypatch) -> None:
    calls = {"count": 0}

    async def handler(request):  # noqa: ARG001
        calls["count"] += 1
        return httpx.Response(429, json={"error": "rate limit"})

    # Avoid real sleeping
    async def _noop(*args, **kwargs) -> None:  # noqa: ARG001
        return None

    monkeypatch.setattr(asyncio, "sleep", _noop)

    cfg = ApiConfig(base_url="https://example.test", max_retries=1)
    client = SyncClient(cfg)
    client._client = httpx.AsyncClient(transport=_DummyTransport(handler), base_url=cfg.base_url)

    with pytest.raises(ApiError):
        await client.upload_changes([])
    assert calls["count"] == 1


@pytest.mark.asyncio
async def test_upload_changes_auth_error() -> None:
    async def handler(request):  # noqa: ARG001
        return httpx.Response(401, json={"error": "unauthorized"})

    client = _client_with(handler)
    with pytest.raises(AuthenticationError):
        await client.upload_changes([])


@pytest.mark.asyncio
async def test_get_status_success() -> None:
    now = datetime.now(UTC)

    async def handler(request):  # noqa: ARG001
        return httpx.Response(
            200,
            json={
                "last_sync": now.isoformat(),
                "pending_changes": 2,
                "online": True,
                "server_time": now.isoformat(),
                "conflicts_pending": 1,
            },
        )

    client = _client_with(handler)
    status = await client.get_sync_status()
    assert status.pending_changes == 2
    assert status.online is True
    assert status.conflicts_pending == 1


@pytest.mark.asyncio
async def test_get_status_network_error(monkeypatch) -> None:
    from tracertm.api.sync_client import NetworkError

    async def handler(request) -> Never:  # noqa: ARG001
        msg = "timeout"
        raise httpx.ConnectTimeout(msg)

    async def _noop(*args, **kwargs) -> None:  # noqa: ARG001
        return None

    monkeypatch.setattr(asyncio, "sleep", _noop)

    cfg = ApiConfig(base_url="https://example.test", max_retries=1)
    client = SyncClient(cfg)
    client._client = httpx.AsyncClient(transport=_DummyTransport(handler), base_url=cfg.base_url)

    with pytest.raises(NetworkError):
        await client.get_sync_status()
