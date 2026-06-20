from typing import Any

import pytest

from tracertm.services.cache_service import CacheService


class _FakeRedis:
    def __init__(self) -> None:
        self.store = {}

    def ping(self) -> bool:
        return True

    def get(self, key: Any) -> None:
        return self.store.get(key)

    def setex(self, key: Any, ttl: Any, _value: Any) -> bool:
        self.store[key] = value
        return True

    def delete(self, key: Any) -> int:
        return 1 if self.store.pop(key, None) is not None else 0


@pytest.mark.asyncio
async def test_cache_service_basic_set_get(_monkeypatch: Any) -> None:
    svc = CacheService(redis_url=None)
    svc.redis_client = _FakeRedis()
    svc.stats = {"hits": 0, "misses": 0, "evictions": 0}

    assert await svc.get("missing") is None
    assert await svc.set("k", {"v": 1}, ttl_seconds=1) is True
    assert await svc.get("k") == {"v": 1}
    assert await svc.delete("k") is True
    assert await svc.get("k") is None


@pytest.mark.asyncio
async def test_cache_service_misses_without_client(_monkeypatch: Any) -> None:
    svc = CacheService(redis_url=None)
    svc.redis_client = None
    svc.stats = {"hits": 0, "misses": 0, "evictions": 0}

    assert await svc.get("x") is None
    assert await svc.set("x", 1) is False
