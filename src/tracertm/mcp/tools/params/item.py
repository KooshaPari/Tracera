"""Item management MCP tools."""

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

    mcp = _StubMCP()

from .common import _call_tool, _maybe_select_project, _wrap, item_tools


@mcp.tool(description="Unified item operations")
async def item_manage(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Unified item management tool.

    Actions:
    - create: Create new item (requires: title, item_type; optional: view, description, status, priority, owner, parent_id, metadata)
    - get: Retrieve item (requires: item_id)
    - update: Update item (requires: item_id; optional: title, description, status, priority, owner, metadata)
    - delete: Delete item (requires: item_id)
    - query: Query items (optional: view, item_type, status, owner, limit)
    - summarize_view: Summarize items in view (requires: view)
    - bulk_update: Bulk update items (requires: view, status, new_status)
    """
    return await _item_manage_impl(action, payload, ctx)


async def _item_manage_impl(  # noqa: C901
    action: str,
    payload: dict[str, Any] | None,
    ctx: Any | None,
) -> dict[str, Any]:
    """Implementation of item management via action dispatch."""
    payload = payload or {}
    action = action.lower()
    await _maybe_select_project(payload, ctx)

    async def _create() -> Any:
        return await _call_tool(
            item_tools,
            "create_item",
            title=payload.get("title"),
            view=payload.get("view"),
            item_type=payload.get("item_type"),
            description=payload.get("description"),
            status=payload.get("status", "todo"),
            priority=payload.get("priority", "medium"),
            owner=payload.get("owner"),
            parent_id=payload.get("parent_id"),
            metadata=payload.get("metadata"),
            ctx=ctx,
        )

    async def _get() -> Any:
        return await _call_tool(
            item_tools,
            "get_item",
            item_id=payload.get("item_id"),
            ctx=ctx,
        )

    async def _update() -> Any:
        return await _call_tool(
            item_tools,
            "update_item",
            item_id=payload.get("item_id"),
            title=payload.get("title"),
            description=payload.get("description"),
            status=payload.get("status"),
            priority=payload.get("priority"),
            owner=payload.get("owner"),
            metadata=payload.get("metadata"),
            ctx=ctx,
        )

    async def _delete() -> Any:
        return await _call_tool(
            item_tools,
            "delete_item",
            item_id=payload.get("item_id"),
            ctx=ctx,
        )

    async def _query() -> Any:
        return await _call_tool(
            item_tools,
            "query_items",
            view=payload.get("view"),
            item_type=payload.get("item_type"),
            status=payload.get("status"),
            owner=payload.get("owner"),
            limit=payload.get("limit", 50),
            ctx=ctx,
        )

    async def _summarize_view() -> Any:
        return await _call_tool(
            item_tools,
            "summarize_view",
            view=payload.get("view"),
            ctx=ctx,
        )

    async def _bulk_update() -> Any:
        return await _call_tool(
            item_tools,
            "bulk_update_items",
            view=payload.get("view"),
            status=payload.get("status"),
            new_status=payload.get("new_status"),
            ctx=ctx,
        )

    handlers: dict[str, Any] = {
        "create": _create,
        "get": _get,
        "update": _update,
        "delete": _delete,
        "query": _query,
        "summarize_view": _summarize_view,
        "bulk_update": _bulk_update,
    }
    if action not in handlers:
        raise ToolError(f"Unknown item action: {action}")
    result = await handlers[action]()
    return _wrap(result, ctx, action)
