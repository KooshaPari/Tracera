"""UI and design integration MCP tools."""

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

    mcp = _StubMCP()


@mcp.tool(description="Unified TUI operations")
async def tui_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """TUI management - imports implementation only when called."""
    from tracertm.mcp.tools.param import tui_manage as impl

    return await impl(action, payload, ctx)


@mcp.tool(description="Unified design integration operations")
async def design_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Design management - imports implementation only when called."""
    from tracertm.mcp.tools.param import design_manage as impl

    return await impl(action, payload, ctx)


__all__ = ["design_manage", "tui_manage"]
