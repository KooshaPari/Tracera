"""Query and test management MCP tools."""

from __future__ import annotations

from typing import Any

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover

    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn: Any) -> Any:
                return fn

            return decorator

    mcp = _StubMCP()


@mcp.tool(description="Unified saved query operations")
async def saved_query_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Saved query management - imports implementation only when called."""
    from tracertm.mcp.tools.param import saved_queries_manage

    return await saved_queries_manage(action, payload, ctx)


@mcp.tool(description="Unified test operations")
async def test_manage(
    action: str,
    payload: dict[str, Any] | None,
    ctx: Any | None,
) -> dict[str, Any]:
    """Test management - imports implementation only when called."""
    from tracertm.mcp.tools.param import test_manage as impl

    return await impl(action, payload or {}, ctx)


__all__ = ["saved_query_manage", "test_manage"]
