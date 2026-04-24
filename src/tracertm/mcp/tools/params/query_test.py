"""Query and test management MCP tools."""

from __future__ import annotations

from typing import Any

try:
    from tracertm.mcp.core import mcp
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]


@mcp.tool(description="Unified saved query operations")
async def saved_query_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Saved query management - imports implementation only when called."""
    from tracertm.mcp.tools.param import saved_queries_manage

    return await saved_queries_manage(action, payload, ctx)


@mcp.tool(description="Unified test operations")
async def test_manage(
    action: str,
    payload: dict[str, object] | None,
    ctx: object | None,
) -> dict[str, object]:
    """Test management - imports implementation only when called."""
    from tracertm.mcp.tools.param import test_manage as impl

    return await impl(action, payload or {}, ctx)


__all__ = ["saved_query_manage", "test_manage"]
