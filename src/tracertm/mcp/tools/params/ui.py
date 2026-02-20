"""UI and design integration MCP tools."""

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


@mcp.tool(description="Unified TUI operations")
async def tui_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """TUI management - imports implementation only when called."""
    from tracertm.mcp.tools.param import tui_manage as impl

    return await impl(action, payload, ctx)


@mcp.tool(description="Unified design integration operations")
async def design_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Design management - imports implementation only when called."""
    from tracertm.mcp.tools.param import design_manage as impl

    return await impl(action, payload, ctx)


__all__ = ["design_manage", "tui_manage"]
