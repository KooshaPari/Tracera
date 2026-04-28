# INTG-A5 – LRU Cache & Vector Search Integration

**Status:** ✅ Design Complete
**Date:** 2025-10-14
**Owner:** SDK Architecture Guild
**Consumers:** Morph caching layer, Router embedding/vector pipelines

---

## 1. Objectives

1. Provide a reusable LRU cache utility that Morph and Router can depend on for adapter-level memoization.
2. Extend `pheno.vector.search` with semantic search helper APIs aligning with Morph requirements.
3. Ensure cache+vector features include observability hooks and configuration toggles defined in INTG-A4.

---

## 2. LRU Cache Design

### Module Layout

```
src/pheno/utilities/cache/
├── __init__.py
├── base.py           # existing interfaces
├── lru.py            # new LRU implementation
└── metrics.py
```

### API

```python
class LruCache(CacheProtocol):
    def __init__(
        self,
        *,
        max_entries: int = 1024,
        ttl: float | None = None,
        namespace: str = "default",
        metrics: MetricsCollector | None = None,
    ) -> None: ...

    async def get(self, key: Hashable) -> Any | None: ...
    async def set(self, key: Hashable, value: Any, *, ttl: float | None = None) -> None: ...
    async def delete(self, key: Hashable) -> None: ...
    async def clear(self) -> None: ...
```

- Uses `collections.OrderedDict` protected by asyncio Lock.
- TTL enforced per-entry; background prune coroutine optional.
- Metrics collector exposes cache hits/misses via `pheno.observability`.

### Configuration

- Controlled by `pheno.cache.strategy` toggle (`lru`, `redis`, `none`).
- Additional env vars: `PHENO_CACHE_LRU_MAX_ENTRIES`, `PHENO_CACHE_LRU_TTL_SECONDS`.

---

## 3. Vector Search Enhancements

### Namespace Update

```
src/pheno/vector/search/
├── __init__.py
├── client.py
├── embeddings.py
├── semantic.py        # new helper utilities
└── settings.py
```

### API

```python
async def semantic_search(
    query: str,
    *,
    collection: str,
    top_k: int = 10,
    filters: Mapping[str, Any] | None = None,
    cache: CacheProtocol | None = None,
) -> list[SearchResult]:
    """Perform semantic search leveraging configured provider and cache."""
```

- Integrates with `pheno.embeddings.provider` to generate embeddings.
- Uses `CacheProtocol` for embedding reuse.
- Exposes telemetry fields: `vector.collection`, `vector.top_k`, `vector.latency_ms`.

### Providers

- Vertex AI (default), Pinecone, Weaviate.
- Provide failover logic; support Morph-specific local fallback hooking into offline embedding provider.

---

## 4. Observability

- Cache metrics: hits, misses, evictions, TTL expirations (`pheno.cache.metrics`).
- Vector telemetry: request count, provider latency, cache hit rate.
- Attach OpenTelemetry attributes for correlation (`component=pheno.vector.search`).

---

## 5. Testing

- Unit tests covering eviction policy, TTL behaviour, concurrency.
- Integration tests with Vertex AI mocked provider verifying semantic search returns expected ordering.
- Morph replay tests to ensure embedding cache hit rate improves over baseline.

---

## 6. Deliverables

- [x] Design spec (this document).
- [ ] Implementation & tests.
- [ ] Documentation updates (INTG-A6).
- [ ] Performance benchmarks recorded in integration status reports.

Approved 2025-10-14.
