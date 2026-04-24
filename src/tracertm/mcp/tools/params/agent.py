"""Agent and progress management MCP tools."""

from __future__ import annotations

from typing import Any

try:
    from tracertm.mcp.core import mcp
except Exception:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]


# Register @mcp.tool decorators here to avoid duplicates with param.py
@mcp.tool(description="Unified agent operations")
async def agent_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Agent management - imports implementation only when called."""
    from tracertm.mcp.tools.param import agents_manage

    return await agents_manage(action, payload, ctx)


@mcp.tool(description="Unified progress operations")
async def progress_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Progress management - imports implementation only when called."""
    from tracertm.mcp.tools.param import progress_manage as impl

    return await impl(action, payload, ctx)


__all__ = ["agent_manage", "progress_manage"]
