import types

import pytest

from pheno.utilities.cache import aiocache_adapter


@pytest.mark.asyncio
async def test_aiocache_adapter_missing(monkeypatch):
    monkeypatch.setattr(aiocache_adapter, "caches", None, raising=False)
    with pytest.raises(RuntimeError):
        aiocache_adapter.AiocacheAdapter()


@pytest.mark.asyncio
async def test_aiocache_adapter_basic(monkeypatch):
    class DummyCache:
        def __init__(self):
            self.store = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, ttl=None):
            self.store[key] = value

        async def delete(self, key):
            self.store.pop(key, None)

        async def clear(self):
            self.store.clear()

    dummy = DummyCache()
    monkeypatch.setattr(
        aiocache_adapter,
        "caches",
        types.SimpleNamespace(get=lambda name: dummy),
        raising=False,
    )

    adapter = aiocache_adapter.AiocacheAdapter()
    await adapter.set("key", "value")
    assert await adapter.get("key") == "value"
    await adapter.delete("key")
    assert await adapter.get("key") is None
