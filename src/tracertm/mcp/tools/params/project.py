"""Project management MCP tools."""

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

from .common import _call_tool, _wrap, project_tools


@mcp.tool(description="Unified project operations")
async def project_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Unified project management tool.

    Actions:
    - create: Create new project (requires: name, description)
    - list: List all projects
    - select: Select active project (requires: project_id)
    - snapshot: Create project snapshot (requires: project_id, label)
    """
    payload = payload or {}
    action = action.lower()

    if action == "create":
        result = await _call_tool(
            project_tools,
            "create_project",
            name=(payload.get("name") or ""),
            description=payload.get("description"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "list":
        result = await _call_tool(project_tools, "list_projects", ctx=ctx)
        return _wrap(result, ctx, action)
    if action == "select":
        result = await _call_tool(
            project_tools,
            "select_project",
            project_id=payload.get("project_id"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)
    if action == "snapshot":
        result = await _call_tool(
            project_tools,
            "snapshot_project",
            project_id=payload.get("project_id"),
            label=payload.get("label"),
            ctx=ctx,
        )
        return _wrap(result, ctx, action)

    msg = f"Unknown project action: {action}"
    raise ToolError(msg)
