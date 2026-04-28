"""
Utilities to backfill embeddings using the progressive embedding service.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from pheno.plugins.supabase import (
    get_supabase,
    get_vector_embedding_service,
    get_vector_search_service,
)
from pheno.vector.pipelines.progressive import ProgressiveEmbeddingService

if TYPE_CHECKING:
    from collections.abc import Iterable


async def backfill_embeddings(
    entity_types: Iterable[str] | None = None,
    *,
    limit: int | None = None,
    supabase_client=None,
) -> dict[str, str]:
    """
    Ensure embeddings exist for the specified entity types.
    """
    supabase = supabase_client or get_supabase()
    embedding_service = get_vector_embedding_service()
    progressive = ProgressiveEmbeddingService(supabase, embedding_service)

    search = get_vector_search_service(supabase, cache=False)
    search_entities = entity_types or list(search.vector_search.searchable_entities.keys())
    return await progressive.ensure_embeddings_for_search(
        list(search_entities),
        limit=limit,
        background=False,
    )


def run_backfill(
    entity_types: Iterable[str] | None = None, *, limit: int | None = None, supabase_client=None,
) -> dict[str, str]:
    """
    Run backfill synchronously.
    """
    return asyncio.run(
        backfill_embeddings(entity_types, limit=limit, supabase_client=supabase_client),
    )


__all__ = ["backfill_embeddings", "run_backfill"]
