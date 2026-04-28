"""Async base utilities for MCP tools with optimized database access.

Provides:
- Async database session management with shared connection pool
- RLS context setting per session
- Query caching with TTL
- Response formatting
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, cast

from fastmcp.exceptions import ToolError

from tracertm.config.manager import ConfigManager
from tracertm.mcp.cache import get_query_cache
from tracertm.mcp.database_adapter import get_async_engine, get_mcp_session

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from sqlalchemy.ext.asyncio import AsyncSession

# Module-level config manager (lazy initialized)
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get or create the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# Re-export get_mcp_session for convenience
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with RLS context.

    This is an alias for get_mcp_session() for backward compatibility.

    Usage:
        async with get_async_session() as session:
            result = await session.execute(query)

    Features:
    - Shares connection pool with FastAPI
    - Sets RLS context automatically
    - Automatic commit/rollback
    """
    async with get_mcp_session() as session:
        yield session


async def get_current_project_id() -> str | None:
    """Get the currently selected project ID from config.

    Returns:
        Project ID if set, None otherwise
    """
    await asyncio.sleep(0)
    config = get_config_manager()
    value = config.get("current_project_id")
    return str(value) if value else None


async def require_project() -> str:
    """Get current project ID or raise ToolError if not set.

    Returns:
        Current project ID

    Raises:
        ToolError: If no project is currently selected
    """
    project_id = await get_current_project_id()
    if not project_id:
        msg = "No project selected. Use project_manage(action='select', payload={'project_id': '...'}) first."
        raise ToolError(
            msg,
        )
    return project_id


async def set_current_project(project_id: str) -> None:
    """Set the current project ID in config.

    Args:
        project_id: Project ID to set as current
    """
    await asyncio.sleep(0)
    config = get_config_manager()
    config.set("current_project_id", project_id)


# Response envelope utilities


def wrap_success(data: object, action: str, ctx: object | None = None) -> dict[str, object]:
    """Wrap a successful response in the standard envelope."""
    return {
        "ok": True,
        "action": action,
        "data": data,
        "actor": extract_actor(ctx),
    }


def wrap_error(error: str, action: str, ctx: object | None = None) -> dict[str, object]:
    """Wrap an error response in the standard envelope."""
    return {
        "ok": False,
        "action": action,
        "error": error,
        "actor": extract_actor(ctx),
    }


def extract_actor(ctx: object | None) -> dict[str, object] | None:
    """Extract actor information from the MCP context."""
    if ctx is None:
        return None

    try:
        from fastmcp.server.dependencies import get_access_token
    except Exception:
        return None

    token = get_access_token()
    if token is None:
        return None

    claims = getattr(token, "claims", {}) or {}
    return {
        "client_id": getattr(token, "client_id", None),
        "sub": claims.get("sub"),
        "email": claims.get("email"),
        "auth_type": claims.get("auth_type"),
        "scopes": getattr(token, "scopes", None),
        "project_id": claims.get("project_id"),
        "project_ids": claims.get("project_ids"),
    }


def resolve_project_from_token(
    payload: dict[str, object],
    ctx: object | None,
) -> str | None:
    """Resolve project_id from token claims with access control.

    Priority:
    1. Explicit project_id in payload (validated against token)
    2. Single project_id from token claims
    3. None (caller must handle)

    Raises ToolError if:
    - Token has project restrictions and explicit project_id is not allowed
    - Token has multiple projects but no explicit project_id provided
    """
    project_id = payload.get("project_id")

    if ctx is None:
        return str(project_id) if project_id else None

    try:
        from fastmcp.server.dependencies import get_access_token

        token = get_access_token()
    except Exception:
        return str(project_id) if project_id else None

    if token is None:
        return str(project_id) if project_id else None

    claims = getattr(token, "claims", {}) or {}
    if not isinstance(claims, dict):
        claims = {}

    # Build list of allowed project IDs from token
    allowed: list[str] = []
    if claims.get("project_id"):
        allowed.append(str(claims["project_id"]))

    project_ids = claims.get("project_ids")
    if isinstance(project_ids, str):
        allowed.extend([p.strip() for p in project_ids.split(",") if p.strip()])
    elif isinstance(project_ids, (list, tuple, set)):
        allowed.extend([str(p) for p in project_ids if p])

    # If token has project restrictions, enforce them
    if allowed:
        if project_id:
            if project_id not in allowed:
                msg = "Project access denied for requested project_id."
                raise ToolError(msg)
            return str(project_id) if project_id else None
        if len(allowed) == 1:
            return allowed[0]
        msg = "project_id required for this request (multiple projects available)."
        raise ToolError(msg)

    return str(project_id) if project_id else None


# Cache utilities


async def cached_query(
    cache_key: str,
    compute_fn: object,
    ttl: int = 300,
    _invalidate_on_write: bool = False,
    **cache_key_args: object,
) -> object:
    """Execute a query with caching.

    Args:
        cache_key: Cache key prefix (e.g., "project_list", "item_query")
        compute_fn: Async function that computes the result
        ttl: Time to live in seconds (default 5 minutes)
        invalidate_on_write: If True, invalidate this cache key on writes
        **cache_key_args: object: Additional arguments for cache key generation

    Returns:
        Cached or computed result
    """
    cache = get_query_cache()
    return await cache.get_or_compute(
        cache_key,
        cast("Callable[..., Any]", compute_fn),
        ttl=ttl,
        **cache_key_args,
    )


def invalidate_cache(prefix: str | None = None) -> None:
    """Invalidate cache entries.

    Args:
        prefix: Cache key prefix to invalidate (e.g., "item_", "project_")
               If None, clears entire cache
    """
    from tracertm.mcp.cache import invalidate_cache as _invalidate

    _invalidate(prefix)


__all__ = [
    "cached_query",
    "extract_actor",
    "get_async_engine",  # Direct export from database_adapter
    "get_async_session",
    "get_config_manager",
    "get_current_project_id",
    "get_mcp_session",  # Direct export from database_adapter
    "invalidate_cache",
    "require_project",
    "resolve_project_from_token",
    "set_current_project",
    "wrap_error",
    "wrap_success",
]
