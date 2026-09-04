"""HTTP clients for the Tracera REST API.

The SDK exposes two parallel clients:

* :class:`Tracera` — a synchronous client built on ``urllib.request`` from
  the standard library. Zero runtime dependencies.

* :class:`AsyncTracera` — an async client built on ``httpx``. Requires the
  optional ``async`` extra (``pip install tracera[async]``).

Both clients share the same surface: ``ingest_*`` family of helpers,
``query_*`` family of helpers, ``graph_*`` family of helpers, and the
``get_node`` / ``list_items`` accessors. They accept and return plain
dicts/lists so callers do not need to learn a new type system.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error as urllib_error
from urllib import parse, request

try:  # pragma: no cover — only imported when the [async] extra is installed.
    import httpx  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]


__all__ = [
    "AsyncTracera",
    "Tracera",
    "TraceraAPIError",
    "TraceraConfig",
    "TraceraError",
]


# -----------------------------------------------------------------------------
# Errors
# -----------------------------------------------------------------------------


class TraceraError(Exception):
    """Base class for all SDK-level errors."""


class TraceraAPIError(TraceraError):
    """A non-2xx response from the Tracera REST API.

    Attributes:
        status_code: HTTP status returned by the server.
        body: Raw response body (decoded as text when possible).
        url: URL the request was sent to.
    """

    def __init__(self, status_code: int, body: str, url: str) -> None:
        self.status_code = status_code
        self.body = body
        self.url = url
        msg = body if body else f"HTTP {status_code}"
        super().__init__(f"Tracera API error {status_code} for {url}: {msg}")


class _MissingAsyncDependency(TraceraError, ImportError):
    """Raised when the async client is used without the ``[async]`` extra."""


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


class TraceraConfig:
    """Runtime configuration shared by sync and async clients.

    The defaults match a Tracera server running locally on port 8080 with no
    authentication. ``base_url`` and ``token`` may also be provided via the
    ``TRACERA_BASE_URL`` and ``TRACERA_TOKEN`` environment variables.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.environ.get("TRACERA_BASE_URL")
            or "http://127.0.0.1:8080"
        ).rstrip("/")
        self.token = token or os.environ.get("TRACERA_TOKEN")
        self.timeout = float(timeout)

    def __repr__(self) -> str:  # pragma: no cover — trivial
        token_repr = "***" if self.token else None
        return f"TraceraConfig(base_url={self.base_url!r}, token={token_repr!r}, timeout={self.timeout!r})"


# -----------------------------------------------------------------------------
# Shared URL helpers
# -----------------------------------------------------------------------------


def _join(base: str, path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return base + path


# -----------------------------------------------------------------------------
# Sync client — stdlib only
# -----------------------------------------------------------------------------


class Tracera:
    """Synchronous client over the Tracera REST API.

    Instances are cheap to construct. The client keeps a small number of
    configuration values (base URL, token, timeout) but does not maintain
    persistent connections — every call opens a fresh ``urllib`` request.
    Use a single :class:`Tracera` instance per logical scope.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
        config: TraceraConfig | None = None,
    ) -> None:
        self.config = config or TraceraConfig(
            base_url=base_url, token=token, timeout=timeout
        )

    # ---- request primitives -------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = _join(self.config.base_url, path)
        if params:
            url = url + "?" + parse.urlencode(params, doseq=True)

        data: bytes | None = None
        headers: dict[str, str] = {"Accept": "application/json"}
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"

        req = request.Request(url=url, data=data, method=method, headers=headers)
        try:
            with request.urlopen(req, timeout=self.config.timeout) as resp:
                raw = resp.read()
        except urllib_error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise TraceraAPIError(exc.code, body, url) from exc
        except urllib_error.URLError as exc:
            raise TraceraError(f"connection error for {url}: {exc.reason}") from exc

        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return raw.decode("utf-8", errors="replace")

    # ---- ingest -------------------------------------------------------------

    def ingest_github(self, payload: dict[str, Any]) -> Any:
        """POST a GitHub webhook payload to ``/ingest/github``."""
        return self._request("POST", "/ingest/github", json_body=payload)

    def ingest_jira(self, payload: dict[str, Any]) -> Any:
        """POST a Jira webhook payload to ``/ingest/jira``."""
        return self._request("POST", "/ingest/jira", json_body=payload)

    def ingest_agileplus(self, payload: dict[str, Any]) -> Any:
        """POST an AgilePlus payload to ``/ingest/agileplus``."""
        return self._request("POST", "/ingest/agileplus", json_body=payload)

    # ---- query --------------------------------------------------------------

    def query(
        self,
        kind: str,
        query: str,
        top_k: int = 10,
        **extra: Any,
    ) -> Any:
        """POST to ``/api/v1/<kind>`` with a ``{"query": ..., "top_k": ...}`` body.

        ``kind`` must be one of ``infer``, ``suggest``, ``classify``,
        ``search``, ``confidence``.
        """
        if kind not in ("infer", "suggest", "classify", "search", "confidence"):
            raise ValueError(f"unknown query kind {kind!r}")
        body = {"query": query, "top_k": top_k, **extra}
        return self._request("POST", f"/api/v1/{kind}", json_body=body)

    def query_infer(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return self.query("infer", query, top_k, **extra)

    def query_suggest(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return self.query("suggest", query, top_k, **extra)

    def query_classify(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return self.query("classify", query, top_k, **extra)

    def query_search(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return self.query("search", query, top_k, **extra)

    # ---- graph --------------------------------------------------------------

    def graph(
        self,
        op: str,
        *,
        node_id: str | int | None = None,
        depth: int = 3,
        direction: str = "both",
        source: str | None = None,
        target: str | None = None,
    ) -> Any:
        """Run a graph operation.

        ``op`` is one of: ``ancestors``, ``descendants``, ``impact``,
        ``dependencies``, ``traverse``, ``full``, ``cycles``, ``orphans``,
        ``path``.

        For ``path``, ``source`` and ``target`` are required and ``node_id``
        is ignored.
        """
        if op not in (
            "ancestors",
            "descendants",
            "impact",
            "dependencies",
            "traverse",
            "full",
            "cycles",
            "orphans",
            "path",
        ):
            raise ValueError(f"unknown graph op {op!r}")

        if op in ("ancestors", "descendants", "impact", "dependencies", "traverse"):
            if node_id is None:
                raise ValueError(f"node_id is required for graph op {op!r}")
            return self._request(
                "POST",
                f"/api/v1/graph/{op}/{node_id}",
                json_body={"depth": depth, "direction": direction},
            )
        if op == "full":
            return self._request(
                "POST", "/api/v1/graph/full", json_body={"max_depth": depth}
            )
        if op in ("cycles", "orphans"):
            return self._request("POST", f"/api/v1/graph/{op}", json_body={})
        # path
        if source is None or target is None:
            raise ValueError("source and target are required for graph op 'path'")
        return self._request(
            "POST",
            "/api/v1/graph/path",
            json_body={"source": source, "target": target, "max_depth": depth},
        )

    # ---- items / nodes ------------------------------------------------------

    def get_node(self, node_id: str | int) -> Any:
        """GET ``/api/v1/items/{id}`` and return the decoded JSON body."""
        return self._request("GET", f"/api/v1/items/{node_id}")

    def list_items(self, **params: Any) -> Any:
        """GET ``/api/v1/items`` with optional query parameters."""
        return self._request("GET", "/api/v1/items", params=params or None)

    # ---- health -------------------------------------------------------------

    def healthz(self) -> Any:
        """Return the body of ``/healthz`` — used to check server reachability."""
        return self._request("GET", "/healthz")

    def __enter__(self) -> "Tracera":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


# -----------------------------------------------------------------------------
# Async client — httpx-based
# -----------------------------------------------------------------------------


class AsyncTracera:
    """Asynchronous client over the Tracera REST API.

    Requires the ``[async]`` extra (``pip install tracera[async]``), which
    pulls in ``httpx``.

    The class mirrors :class:`Tracera` so callers can switch between the two
    with no learning curve. Use as an async context manager::

        async with AsyncTracera(base_url="...") as client:
            node = await client.get_node(123)
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
        config: TraceraConfig | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if httpx is None:
            raise _MissingAsyncDependency(
                "AsyncTracera requires the 'httpx' package. "
                "Install with: pip install 'tracera[async]'"
            )
        self.config = config or TraceraConfig(
            base_url=base_url, token=token, timeout=timeout
        )
        self._owns_client = client is None
        self._client = client or self._build_client()

    def _build_client(self) -> httpx.AsyncClient:
        headers = {"Accept": "application/json"}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        return httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=headers,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncTracera":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    # ---- request primitive --------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            resp = await self._client.request(
                method,
                path,
                json=json_body,
                params=params or None,
            )
        except httpx.HTTPError as exc:  # type: ignore[misc]
            raise TraceraError(f"connection error for {method} {path}: {exc}") from exc

        if resp.status_code >= 400:
            raise TraceraAPIError(resp.status_code, resp.text, str(resp.url))

        if not resp.content:
            return None
        # Try JSON, fall back to text so callers always get *something* useful.
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text

    # ---- ingest -------------------------------------------------------------

    async def ingest_github(self, payload: dict[str, Any]) -> Any:
        return await self._request("POST", "/ingest/github", json_body=payload)

    async def ingest_jira(self, payload: dict[str, Any]) -> Any:
        return await self._request("POST", "/ingest/jira", json_body=payload)

    async def ingest_agileplus(self, payload: dict[str, Any]) -> Any:
        return await self._request("POST", "/ingest/agileplus", json_body=payload)

    # ---- query --------------------------------------------------------------

    async def query(
        self,
        kind: str,
        query: str,
        top_k: int = 10,
        **extra: Any,
    ) -> Any:
        if kind not in ("infer", "suggest", "classify", "search", "confidence"):
            raise ValueError(f"unknown query kind {kind!r}")
        body = {"query": query, "top_k": top_k, **extra}
        return await self._request("POST", f"/api/v1/{kind}", json_body=body)

    async def query_infer(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return await self.query("infer", query, top_k, **extra)

    async def query_suggest(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return await self.query("suggest", query, top_k, **extra)

    async def query_classify(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return await self.query("classify", query, top_k, **extra)

    async def query_search(self, query: str, top_k: int = 10, **extra: Any) -> Any:
        return await self.query("search", query, top_k, **extra)

    # ---- graph --------------------------------------------------------------

    async def graph(
        self,
        op: str,
        *,
        node_id: str | int | None = None,
        depth: int = 3,
        direction: str = "both",
        source: str | None = None,
        target: str | None = None,
    ) -> Any:
        if op not in (
            "ancestors",
            "descendants",
            "impact",
            "dependencies",
            "traverse",
            "full",
            "cycles",
            "orphans",
            "path",
        ):
            raise ValueError(f"unknown graph op {op!r}")

        if op in ("ancestors", "descendants", "impact", "dependencies", "traverse"):
            if node_id is None:
                raise ValueError(f"node_id is required for graph op {op!r}")
            return await self._request(
                "POST",
                f"/api/v1/graph/{op}/{node_id}",
                json_body={"depth": depth, "direction": direction},
            )
        if op == "full":
            return await self._request(
                "POST", "/api/v1/graph/full", json_body={"max_depth": depth}
            )
        if op in ("cycles", "orphans"):
            return await self._request("POST", f"/api/v1/graph/{op}", json_body={})
        if source is None or target is None:
            raise ValueError("source and target are required for graph op 'path'")
        return await self._request(
            "POST",
            "/api/v1/graph/path",
            json_body={"source": source, "target": target, "max_depth": depth},
        )

    # ---- items / nodes ------------------------------------------------------

    async def get_node(self, node_id: str | int) -> Any:
        return await self._request("GET", f"/api/v1/items/{node_id}")

    async def list_items(self, **params: Any) -> Any:
        return await self._request("GET", "/api/v1/items", params=params or None)

    # ---- health -------------------------------------------------------------

    async def healthz(self) -> Any:
        return await self._request("GET", "/healthz")