"""System tools (benchmark, chaos) MCP tools."""

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


@mcp.tool(description="Unified benchmark operations")
async def benchmark_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Benchmark management - imports implementation only when called."""
    from tracertm.mcp.tools.param import benchmark_manage as impl
    return await impl(action, payload, ctx)


@mcp.tool(description="Unified chaos operations")
async def chaos_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Chaos management - imports implementation only when called."""
    from tracertm.mcp.tools.param import chaos_manage as impl
    return await impl(action, payload, ctx)


__all__ = ["benchmark_manage", "chaos_manage"]
