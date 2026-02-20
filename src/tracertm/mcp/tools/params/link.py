"""Link management MCP tools."""

from __future__ import annotations

from typing import Any

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

from .common import _call_tool, _maybe_select_project, _wrap, link_tools


@mcp.tool(description="Unified link operations")
async def link_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified link management tool.

    Actions:
    - create: Create link between items (requires: source_id, target_id, link_type; optional: metadata)
    - list: List links for item (requires: item_id; optional: link_type, limit)
    - show: Show links for item in view (requires: item_id; optional: view)
    """
    payload = payload or {}
    action = action.lower()

    await _maybe_select_project(payload, ctx)

    if action == "create":
        result = await _call_tool(
            link_tools,
            "create_link",
            source_id=payload.get("source_id"),
            target_id=payload.get("target_id"),
            link_type=payload.get("link_type"),
            metadata=payload.get("metadata"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "list":
        result = await _call_tool(
            link_tools,
            "list_links",
            item_id=payload.get("item_id"),
            link_type=payload.get("link_type"),
            limit=payload.get("limit", 50),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "show":
        result = await _call_tool(
            link_tools,
            "show_links",
            item_id=payload.get("item_id"),
            view=payload.get("view"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)

    msg = f"Unknown link action: {action}"
    raise ToolError(msg)
