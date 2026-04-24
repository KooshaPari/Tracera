"""Cache utility API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from tracertm.api.deps import auth_guard, get_cache_service
from tracertm.services.cache_service import CacheService

router = APIRouter(prefix="/api/v1", tags=["cache"])


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


@router.get("/cache/stats")
async def cache_stats(
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, Any]:
    """Get cache statistics for monitoring."""
    stats = await cache.get_stats()
    healthy = await cache.health_check()
    return {
        "healthy": healthy,
        "hits": stats.hits,
        "misses": stats.misses,
        "hit_rate": round(stats.hit_rate, 2),
        "total_size_bytes": stats.total_size_bytes,
        "evictions": stats.evictions,
    }


@router.post("/cache/clear")
async def cache_clear(
    prefix: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    cache: CacheService = Depends(get_cache_service),
) -> dict[str, Any]:
    """Clear cache (admin only). Optionally specify a prefix to clear."""
    ensure_write_permission(claims, action="clear_cache")

    if prefix:
        deleted = await cache.clear_prefix(prefix)
        return {"cleared": True, "prefix": prefix, "keys_deleted": deleted}

    await cache.clear()
    return {"cleared": True, "all": True}
