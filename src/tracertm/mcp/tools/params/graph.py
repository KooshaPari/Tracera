"""Graph analysis MCP tools."""

from __future__ import annotations

from typing import Any

from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except Exception:  # pragma: no cover

    class _StubMCP:
        def tool(self, *args: Any, **kwargs: Any):
            def decorator(fn):
                return fn

            return decorator

    mcp = _StubMCP()  # type: ignore[assignment]

from .common import _call_tool, _maybe_select_project, _wrap, graph_tools


@mcp.tool(description="Unified graph analysis")
async def graph_analyze(
    kind: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified graph analysis tool.

    Analysis kinds:
    - detect_cycles: Detect cycles in dependency graph
    - shortest_path: Find shortest path between items (requires: source_id, target_id)
    """
    payload = payload or {}
    kind = kind.lower()

    await _maybe_select_project(payload, ctx)

    if kind == "detect_cycles":
        result = await _call_tool(graph_tools, "detect_cycles", ctx=ctx)
        return _wrap(result, ctx, kind)
    if kind == "shortest_path":
        result = await _call_tool(
            graph_tools, "shortest_path",
            source_id=payload.get("source_id"),
            target_id=payload.get("target_id"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)

    raise ToolError(f"Unknown graph analysis kind: {kind}")
