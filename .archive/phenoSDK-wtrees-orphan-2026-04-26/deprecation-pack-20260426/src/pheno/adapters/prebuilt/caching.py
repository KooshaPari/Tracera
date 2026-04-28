"""Prebuilt caching adapters."""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any

from .base import BasePrebuiltAdapter


class InMemoryCacheAdapter(BasePrebuiltAdapter):
    """Lightweight in-memory cache with TTL support."""

    name = "in_memory"
    category = "cache"

    def __init__(self, *, max_entries: int = 1024, default_ttl: int | None = None, **config: Any):
        super().__init__(max_entries=max_entries, default_ttl=default_ttl, **config)
        self._store: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl_seconds = ttl if ttl is not None else self._config.get("default_ttl")
        expires_at = time.time() + ttl_seconds if ttl_seconds else None
        self._store[key] = (value, expires_at)
        self._store.move_to_end(key)
        if len(self._store) > self._config["max_entries"]:
            self._store.popitem(last=False)

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at and expires_at < time.time():
            self._store.pop(key, None)
            return None
        self._store.move_to_end(key)
        return value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class RedisCacheAdapter(BasePrebuiltAdapter):
    """Adapter for Redis used as a cache."""

    name = "redis"
    category = "cache"

    def __init__(self, **config: Any):
        defaults = {"host": "127.0.0.1", "port": 6379, "db": 0}
        defaults.update(config)
        super().__init__(**defaults)
        self._client: Any | None = None

    def connect(self) -> None:
        redis_pkg = self._require("redis")

        def _client() -> Any:
            return redis_pkg.Redis(**self._config)

        self._client = self._wrap_errors("connect", _client)
        super().connect()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self.ensure_connected()
        self._wrap_errors("set", lambda: self._client.set(name=key, value=value, ex=ttl))

    def get(self, key: str) -> Any:
        self.ensure_connected()
        return self._wrap_errors("get", lambda: self._client.get(name=key))

    def delete(self, key: str) -> None:
        self.ensure_connected()
        self._wrap_errors("delete", lambda: self._client.delete(key))

    def clear(self) -> None:
        if self._client is not None:
            self._client.flushdb()

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
        super().close()


class MemcachedAdapter(BasePrebuiltAdapter):
    """Adapter using ``pymemcache``."""

    name = "memcached"
    category = "cache"

    def __init__(self, *, server: str = "127.0.0.1", port: int = 11211, **config: Any):
        super().__init__(server=server, port=port, **config)
        self._client: Any | None = None

    def connect(self) -> None:
        pymemcache = self._require("pymemcache.client.base", install_hint="pymemcache")

        def _client() -> Any:
            return pymemcache.Client((self._config["server"], self._config["port"]))

        self._client = self._wrap_errors("connect", _client)
        super().connect()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self.ensure_connected()
        self._wrap_errors("set", lambda: self._client.set(key, value, expire=ttl))

    def get(self, key: str) -> Any:
        self.ensure_connected()
        return self._wrap_errors("get", lambda: self._client.get(key))

    def delete(self, key: str) -> None:
        self.ensure_connected()
        self._wrap_errors("delete", lambda: self._client.delete(key))

    def clear(self) -> None:
        if self._client is not None:
            self._client.flush_all()

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # pragma: no cover
                pass
            self._client = None
        super().close()


__all__ = [
    "InMemoryCacheAdapter",
    "MemcachedAdapter",
    "RedisCacheAdapter",
]
