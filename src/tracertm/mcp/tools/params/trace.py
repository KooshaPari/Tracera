"""Traceability and quality analysis MCP tools."""

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

from .common import _call_tool, _maybe_select_project, _wrap, trace_tools


@mcp.tool(description="Unified traceability analysis")
async def trace_analyze(
    kind: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified traceability analysis tool.

    Analysis kinds:
    - gaps: Find gaps between views (requires: from_view, to_view)
    - trace_matrix: Get traceability matrix (requires: source_view, target_view)
    - impact: Analyze impact of item (requires: item_id; optional: max_depth, link_types)
    - reverse_impact: Analyze reverse impact (requires: item_id; optional: max_depth)
    - project_health: Analyze project health
    """
    payload = payload or {}
    kind = kind.lower()

    await _maybe_select_project(payload, ctx)

    if kind == "gaps":
        result = await _call_tool(
            trace_tools, "find_gaps",
            from_view=payload.get("from_view"),
            to_view=payload.get("to_view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "trace_matrix":
        result = await _call_tool(
            trace_tools, "get_trace_matrix",
            source_view=payload.get("source_view"),
            target_view=payload.get("target_view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "impact":
        result = await _call_tool(
            trace_tools, "analyze_impact",
            item_id=payload.get("item_id"),
            max_depth=payload.get("max_depth", 5),
            link_types=payload.get("link_types"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "reverse_impact":
        result = await _call_tool(
            trace_tools, "analyze_reverse_impact",
            item_id=payload.get("item_id"),
            max_depth=payload.get("max_depth", 5),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "project_health":
        result = await _call_tool(trace_tools, "project_health", ctx=ctx)
        return _wrap(result, ctx, kind)

    raise ToolError(f"Unknown trace analysis kind: {kind}")


@mcp.tool(description="Unified quality analysis")
async def quality_analyze(
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified quality analysis tool.

    Analyzes quality metrics for items.
    Optional: item_id for specific item analysis
    """
    payload = payload or {}
    try:
        from tracertm.mcp.tools import specifications as spec_tools
    except Exception:

        class _SpecStub:
            async def analyze_quality(self, **kwargs):
                raise ToolError("Specification tools unavailable")

        spec_tools = _SpecStub()  # type: ignore

    result = await _call_tool(spec_tools, "analyze_quality", item_id=payload.get("item_id"))
    return _wrap(result, ctx, "quality.analyze")
