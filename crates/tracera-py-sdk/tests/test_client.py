"""SDK request contracts; HTTP is mocked so these do not certify a live backend."""

import io
import json
from urllib.error import HTTPError

import httpx
import pytest

from tracera import AsyncTracera, Tracera, TraceraAPIError


def test_sync_graph_request_keeps_payload_and_auth(monkeypatch):
    captured = {}

    def respond(request, *, timeout):
        captured.update(
            url=request.full_url,
            headers=dict(request.header_items()),
            body=json.loads(request.data),
            timeout=timeout,
        )
        return io.BytesIO(b'{"nodes":[{"id":"node-1"}]}')

    monkeypatch.setattr("tracera.client.request.urlopen", respond)
    client = Tracera(base_url="https://example.test/", token="test-token")
    assert client.graph("ancestors", node_id="node-1", depth=2) == {"nodes": [{"id": "node-1"}]}
    assert captured["url"] == "https://example.test/api/v1/graph/ancestors/node-1"
    assert captured["headers"]["Authorization"] == "Bearer test-token"
    assert captured["body"] == {"depth": 2, "direction": "both"}


def test_sync_rejected_request_preserves_status_and_body(monkeypatch):
    def reject(request, *, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO(b"wrong workspace"))

    monkeypatch.setattr("tracera.client.request.urlopen", reject)
    with pytest.raises(TraceraAPIError) as error:
        Tracera(base_url="https://example.test").get_node("node-1")
    assert error.value.status_code == 403
    assert error.value.body == "wrong workspace"


def test_invalid_graph_path_rejected_before_network():
    with pytest.raises(ValueError, match="source and target"):
        Tracera().graph("path", source="node-1")


async def test_async_query_keeps_auth_and_body():
    captured = []

    def respond(request):
        captured.append(request)
        return httpx.Response(200, json={"items": ["matched"]})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(respond),
        base_url="https://example.test",
        headers={"Authorization": "Bearer test-token"},
    ) as http:
        client = AsyncTracera(client=http)
        assert await client.query_search("needle", top_k=4) == {"items": ["matched"]}
        await client.aclose()
        assert not http.is_closed, "Caller-owned transport must remain usable"
    request = captured[0]
    assert request.url.path == "/api/v1/search"
    assert request.headers["Authorization"] == "Bearer test-token"
    assert json.loads(request.content) == {"query": "needle", "top_k": 4}


async def test_async_rejected_request_preserves_status_and_body():
    def reject(request):
        return httpx.Response(409, text="conflicting graph")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(reject), base_url="https://example.test"
    ) as http:
        with pytest.raises(TraceraAPIError) as error:
            await AsyncTracera(client=http).get_node("node-1")
    assert error.value.status_code == 409
    assert error.value.body == "conflicting graph"
