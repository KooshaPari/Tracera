"""Prebuilt HTTP client adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import AdapterOperationError, BasePrebuiltAdapter, MissingDependencyError

if TYPE_CHECKING:
    from collections.abc import Mapping


class RequestsHTTPAdapter(BasePrebuiltAdapter):
    """Adapter that wraps a ``requests.Session`` instance."""

    name = "requests"
    category = "http"

    def __init__(self, **config: Any):
        super().__init__(**config)
        self._session: Any | None = None

    def connect(self) -> None:
        def _connect() -> Any:
            requests = self._require("requests")
            session = requests.Session()
            headers: Mapping[str, str] = self._config.get("headers", {})
            if headers:
                session.headers.update(dict(headers))
            return session

        self._session = self._wrap_errors("connect", _connect)
        super().connect()

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        self.ensure_connected()
        if self._session is None:  # pragma: no cover - defensive
            raise AdapterOperationError("requests session not initialised")
        timeout = kwargs.pop("timeout", self._config.get("timeout"))
        return self._wrap_errors("request", lambda: self._session.request(method, url, timeout=timeout, **kwargs))

    async def arequest(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - sync only
        raise AdapterOperationError("requests adapter does not support async usage")

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None
        super().close()


class HttpxHTTPAdapter(BasePrebuiltAdapter):
    """Adapter for the httpx client supporting sync and async usage."""

    name = "httpx"
    category = "http"

    def __init__(self, **config: Any):
        super().__init__(**config)
        self._client: Any | None = None
        self._async_client: Any | None = None

    def connect(self) -> None:
        httpx = self._require("httpx")
        def _create_sync() -> Any:
            return httpx.Client(timeout=self._config.get("timeout", 10), headers=self._config.get("headers"))

        def _create_async() -> Any:
            return httpx.AsyncClient(timeout=self._config.get("timeout", 10), headers=self._config.get("headers"))

        self._client = self._wrap_errors("connect", _create_sync)
        self._async_client = self._wrap_errors("aconnect", _create_async)
        super().connect()

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        self.ensure_connected()
        if self._client is None:
            raise AdapterOperationError("httpx client not initialised")
        return self._wrap_errors("request", lambda: self._client.request(method, url, **kwargs))

    async def arequest(self, method: str, url: str, **kwargs: Any) -> Any:
        self.ensure_connected()
        if self._async_client is None:
            raise AdapterOperationError("httpx async client not initialised")
        try:
            return await self._async_client.request(method, url, **kwargs)
        except MissingDependencyError:
            raise
        except Exception as exc:
            raise AdapterOperationError(f"httpx async request failed: {exc}") from exc

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
        super().close()

    async def close_async(self) -> None:
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
        self._connected = False


class AiohttpHTTPAdapter(BasePrebuiltAdapter):
    """Adapter for aiohttp sessions."""

    name = "aiohttp"
    category = "http"

    def __init__(self, **config: Any):
        super().__init__(**config)
        self._session: Any | None = None

    def connect(self) -> None:  # pragma: no cover - primarily async
        # Adapter requires async usage; provide a helpful error for sync contexts.
        raise AdapterOperationError("Use 'await connect_async()' with the aiohttp adapter")

    async def connect_async(self) -> None:
        aiohttp = self._require("aiohttp")
        timeout = (
            aiohttp.ClientTimeout(total=self._config.get("timeout"))
            if self._config.get("timeout")
            else None
        )
        try:
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._config.get("headers"),
            )
        except MissingDependencyError:
            raise
        except Exception as exc:  # pragma: no cover - depends on event loop
            raise AdapterOperationError(f"aiohttp session creation failed: {exc}") from exc
        self._connected = True

    async def arequest(self, method: str, url: str, **kwargs: Any) -> Any:
        if self._session is None:
            await self.connect_async()
        assert self._session is not None  # mypy hint
        try:
            async with self._session.request(method, url, **kwargs) as resp:
                return await resp.text()
        except Exception as exc:  # pragma: no cover - network operations are hard to unit test
            raise AdapterOperationError(f"aiohttp request failed: {exc}") from exc

    def request(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - async only
        raise AdapterOperationError("aiohttp adapter only supports async requests")

    async def close_async(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None
        self._connected = False

    def close(self) -> None:  # pragma: no cover - async only
        raise AdapterOperationError("Call 'await close_async()' for aiohttp adapter")

__all__ = [
    "AiohttpHTTPAdapter",
    "HttpxHTTPAdapter",
    "RequestsHTTPAdapter",
]
