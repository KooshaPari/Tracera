from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pheno.utilities.cache.base import CacheProtocol
    from pheno.vector.search.semantic import SemanticSearch
    from pheno.vector.stores.base import SearchResult


async def semantic_search(
    query: str,
    *,
    search: SemanticSearch,
    top_k: int = 10,
    filters: Mapping[str, object] | None = None,
    cache: CacheProtocol | None = None,
) -> list[SearchResult]:
    """
    Perform semantic search with optional caching.
    """

    cache_key = None
    if cache is not None:
        filters_tuple = tuple(sorted((k, repr(v)) for k, v in (filters or {}).items()))
        cache_key = ("vector.semantic", query, top_k, filters_tuple)
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached

    results = await search.search(query, k=top_k, filter_dict=dict(filters or {}))

    if cache is not None and cache_key is not None:
        await cache.set(cache_key, results)

    return results
