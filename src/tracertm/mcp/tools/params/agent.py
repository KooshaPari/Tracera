"""Agent and progress management MCP tools."""

from __future__ import annotations

from typing import Any

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover
    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn):
                return fn
            return decorator
    mcp = _StubMCP()  # type: ignore[assignment]


# Register @mcp.tool decorators here to avoid duplicates with param.py
@mcp.tool(description="Unified agent operations")
async def agent_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Agent management - imports implementation only when called."""
    from tracertm.mcp.tools.param import agents_manage
    return await agents_manage(action, payload, ctx)


@mcp.tool(description="Unified progress operations")
async def progress_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Progress management - imports implementation only when called."""
    from tracertm.mcp.tools.param import progress_manage as impl
    return await impl(action, payload, ctx)


__all__ = ["agent_manage", "progress_manage"]
