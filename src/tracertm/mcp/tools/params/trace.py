"""Traceability and quality analysis MCP tools."""

from __future__ import annotations

from typing import Any, Never

from fastmcp.exceptions import ToolError

try:
    from tracertm.mcp.core import mcp
except ImportError:

    class _StubMCP:
        def tool(self, *_args: object, **_kwargs: object) -> object:
            def decorator(fn: object) -> object:
                return fn

            return decorator

    mcp: Any = _StubMCP()  # type: ignore[no-redef]

from .common import _call_tool, _maybe_select_project, _wrap, trace_tools


@mcp.tool(description="Unified traceability analysis")
async def trace_analyze(
    kind: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified traceability analysis tool.

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
            trace_tools,
            "find_gaps",
            from_view=payload.get("from_view"),
            to_view=payload.get("to_view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "trace_matrix":
        result = await _call_tool(
            trace_tools,
            "get_trace_matrix",
            source_view=payload.get("source_view"),
            target_view=payload.get("target_view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "impact":
        result = await _call_tool(
            trace_tools,
            "analyze_impact",
            item_id=payload.get("item_id"),
            max_depth=payload.get("max_depth", 5),
            link_types=payload.get("link_types"),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "reverse_impact":
        result = await _call_tool(
            trace_tools,
            "analyze_reverse_impact",
            item_id=payload.get("item_id"),
            max_depth=payload.get("max_depth", 5),
            ctx=ctx,
        )
        return _wrap(result, ctx, kind)
    if kind == "project_health":
        result = await _call_tool(trace_tools, "project_health", ctx=ctx)
        return _wrap(result, ctx, kind)

    msg = f"Unknown trace analysis kind: {kind}"
    raise ToolError(msg)


@mcp.tool(description="Unified quality analysis")
async def quality_analyze(
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified quality analysis tool.

    Analyzes quality metrics for items.
    Optional: item_id for specific item analysis
    """
    payload = payload or {}
    try:
        from tracertm.mcp.tools import specifications as spec_tools
    except ImportError:

        class _SpecStub:
            async def analyze_quality(self, **_kwargs: object) -> Never:
                msg = "Specification tools unavailable"
                raise ToolError(msg)

        spec_tools: object = _SpecStub()  # type: ignore[no-redef]

    result = await _call_tool(spec_tools, "analyze_quality", item_id=payload.get("item_id"))
    return _wrap(result, ctx, "quality.analyze")
