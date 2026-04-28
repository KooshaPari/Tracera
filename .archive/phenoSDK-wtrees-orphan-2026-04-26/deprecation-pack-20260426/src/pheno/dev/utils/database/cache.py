"""
Simple in-memory query cache with TTL support.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class QueryCache:
    """
    Simple in-memory cache keyed by operation parameters.
    """

    def __init__(self, ttl: int = 30, max_size: int = 1000) -> None:
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        value, timestamp = entry
        if time.time() - timestamp < self.ttl:
            return value
        self._cache.pop(key, None)
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, time.time())
        if len(self._cache) > self.max_size:
            items = sorted(self._cache.items(), key=lambda item: item[1][1])
            for expired_key, _ in items[: len(self._cache) - self.max_size]:
                self._cache.pop(expired_key, None)

    def invalidate(self, pattern: str | None = None) -> None:
        if pattern is None:
            self._cache.clear()
            return
        keys = [key for key in self._cache if pattern in key]
        for key in keys:
            self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    @staticmethod
    def make_key(operation: str, **kwargs: Any) -> str:
        payload = {"op": operation, **kwargs}
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode()).hexdigest()


__all__ = ["QueryCache"]
