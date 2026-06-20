"""System tools (benchmark, chaos) MCP tools."""

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


@mcp.tool(description="Unified benchmark operations")
async def benchmark_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Benchmark management - imports implementation only when called."""
    from tracertm.mcp.tools.param import benchmark_manage as impl

    return await impl(action, payload, ctx)


@mcp.tool(description="Unified chaos operations")
async def chaos_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Chaos management - imports implementation only when called."""
    from tracertm.mcp.tools.param import chaos_manage as impl

    return await impl(action, payload, ctx)


__all__ = ["benchmark_manage", "chaos_manage"]
