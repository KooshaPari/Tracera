"""Behavior of the sync and async Tracera clients without a live server.

Collected by pytest from ``testpaths = ["tests"]`` in this package. The
ci-agents test-py job runs that suite with plugin autoload disabled.
"""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import patch
from urllib import error as urllib_error
from urllib.request import Request

import pytest

from tracera import AsyncTracera, Tracera, TraceraAPIError, TraceraConfig, TraceraError


def test_config_prefers_explicit_values_over_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TRACERA_BASE_URL", "http://env.example")
    monkeypatch.setenv("TRACERA_TOKEN", "env-token")
    config = TraceraConfig(base_url="http://explicit.example/", token="explicit", timeout=5)
    assert config.base_url == "http://explicit.example"
    assert config.token == "explicit"
    assert config.timeout == 5.0


def test_config_reads_environment_when_arguments_are_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TRACERA_BASE_URL", "http://env.example/")
    monkeypatch.setenv("TRACERA_TOKEN", "env-token")
    config = TraceraConfig()
    assert config.base_url == "http://env.example"
    assert config.token == "env-token"
    assert config.timeout == 30.0


def test_api_error_includes_status_body_and_url() -> None:
    err = TraceraAPIError(404, "missing", "http://127.0.0.1:8080/api/v1/items/1")
    assert err.status_code == 404
    assert err.body == "missing"
    text = str(err)
    assert "404" in text
    assert "missing" in text
    assert "http://127.0.0.1:8080/api/v1/items/1" in text


def test_get_node_returns_decoded_json_and_sends_bearer_token() -> None:
    client = Tracera(base_url="http://tracera.test", token="secret")
    payload = json.dumps({"id": 7, "name": "node"}).encode()

    class _Response:
        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return payload

    captured: dict[str, object] = {}

    def _urlopen(req: Request, timeout: float) -> _Response:
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["auth"] = req.get_header("Authorization")
        captured["timeout"] = timeout
        return _Response()

    with patch("tracera.client.request.urlopen", _urlopen):
        body = client.get_node(7)

    assert body == {"id": 7, "name": "node"}
    assert captured["url"] == "http://tracera.test/api/v1/items/7"
    assert captured["method"] == "GET"
    assert captured["auth"] == "Bearer secret"
    assert captured["timeout"] == 30.0


def test_http_error_becomes_api_error() -> None:
    client = Tracera(base_url="http://tracera.test")

    def _urlopen(req: Request, timeout: float) -> object:
        del timeout
        raise urllib_error.HTTPError(
            req.full_url,
            503,
            "unavailable",
            hdrs=None,  # type: ignore[arg-type]
            fp=BytesIO(b"down"),
        )

    with patch("tracera.client.request.urlopen", _urlopen), pytest.raises(TraceraAPIError) as exc:
        client.healthz()

    assert exc.value.status_code == 503
    assert exc.value.body == "down"


def test_url_error_becomes_connection_error() -> None:
    client = Tracera(base_url="http://tracera.test")

    def _urlopen(req: object, timeout: float) -> object:
        del req, timeout
        raise urllib_error.URLError("refused")

    with (
        patch("tracera.client.request.urlopen", _urlopen),
        pytest.raises(TraceraError, match="connection error"),
    ):
        client.healthz()


@pytest.mark.asyncio
async def test_async_get_node_returns_json() -> None:
    import respx

    with respx.mock(base_url="http://tracera.test") as router:
        router.get("/api/v1/items/7").respond(200, json={"id": 7})
        async with AsyncTracera(base_url="http://tracera.test", token="secret") as client:
            body = await client.get_node(7)

    assert body == {"id": 7}
