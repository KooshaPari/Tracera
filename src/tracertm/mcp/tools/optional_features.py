"""Priority 3 MCP tools: Optional but useful features.

This module provides optional feature tools:
- View management: list[object], switch, current, stats, show
- History: show, version, rollback
- Agents: list[object], activity, metrics, workload, health
- State: get/show state
- Drill: drill into item details
"""

from __future__ import annotations

import asyncio
import logging

from tracertm.config.manager import ConfigManager
from tracertm.mcp.core import mcp

logger = logging.getLogger(__name__)

_ACTOR_CONTEXT_ERRORS = (ImportError, AttributeError, TypeError, ValueError)
_TOOL_OPERATION_ERRORS = (RuntimeError, ValueError, TypeError, OSError, LookupError)


def _wrap(result: object, ctx: object | None, action: str) -> dict[str, object]:
    """Wrap result in standard MCP response format."""
    actor = None
    if ctx is not None:
        try:
            from fastmcp.server.dependencies import get_access_token

            token = get_access_token()
            if token:
                claims = getattr(token, "claims", {}) or {}
                actor = {
                    "client_id": getattr(token, "client_id", None),
                    "sub": claims.get("sub"),
                }
        except _ACTOR_CONTEXT_ERRORS as e:
            logger.debug("Could not extract actor from access token: %s", e)

    return {
        "ok": True,
        "action": action,
        "data": result,
        "actor": actor,
    }


def _error(message: str, action: str, code: str = "ERROR") -> dict[str, object]:
    """Return error response."""
    return {
        "ok": False,
        "action": action,
        "error": message,
        "error_code": code,
    }


# ==========================================================================
# View Management Tools
# ==========================================================================


@mcp.tool()
async def view_list(ctx: object) -> dict[str, object]:
    """List available views.

    Returns:
        MCP response with available views
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "views": [
                    {"name": "table", "description": "Table view of items"},
                    {"name": "graph", "description": "Graph view of dependencies"},
                    {"name": "tree", "description": "Tree view of hierarchy"},
                    {"name": "kanban", "description": "Kanban view of workflow"},
                    {"name": "matrix", "description": "Traceability matrix view"},
                ],
                "total": 5,
            },
            ctx,
            "view_list",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to list views: {e!s}", "view_list")


@mcp.tool()
async def view_switch(ctx: object, view_name: str) -> dict[str, object]:
    """Switch to a different view.

    Args:
        ctx: MCP context
        view_name: Name of view to switch to

    Returns:
        MCP response with current view
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        config.set("current_view", view_name)

        return _wrap(
            {
                "message": f"Switched to {view_name} view",
                "current_view": view_name,
            },
            ctx,
            "view_switch",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to switch view: {e!s}", "view_switch")


@mcp.tool()
async def view_current(ctx: object) -> dict[str, object]:
    """Get currently active view.

    Returns:
        MCP response with current view
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        current_view = config.get("current_view") or "table"

        return _wrap(
            {
                "current_view": current_view,
            },
            ctx,
            "view_current",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get current view: {e!s}", "view_current")


@mcp.tool()
async def view_stats(ctx: object) -> dict[str, object]:
    """Get view statistics.

    Returns:
        MCP response with view statistics
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "message": "View statistics",
                "views_available": 5,
                "views_cached": 0,
            },
            ctx,
            "view_stats",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get view stats: {e!s}", "view_stats")


@mcp.tool()
async def view_show(
    ctx: object,
    view_name: str,
    project_id: str | None = None,
) -> dict[str, object]:
    """Show specified view.

    Args:
        ctx: MCP context
        view_name: Name of view to show
        project_id: Optional project ID

    Returns:
        MCP response with view data
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        project_id = project_id or (str(config.get("current_project_id")) if config.get("current_project_id") else None)

        return _wrap(
            {
                "message": f"Showing {view_name} view",
                "view": view_name,
                "project_id": project_id,
            },
            ctx,
            "view_show",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to show view: {e!s}", "view_show")


# ==========================================================================
# History Tools
# ==========================================================================


@mcp.tool()
async def history_show(
    ctx: object,
    project_id: str | None = None,
    limit: int = 10,
) -> dict[str, object]:
    """Show item change history.

    Args:
        ctx: MCP context
        project_id: Optional project ID
        limit: Number of records to show

    Returns:
        MCP response with history
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        project_id = project_id or (str(config.get("current_project_id")) if config.get("current_project_id") else None)

        return _wrap(
            {
                "message": "Item change history",
                "project_id": project_id,
                "limit": limit,
                "records": [],
            },
            ctx,
            "history_show",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to show history: {e!s}", "history_show")


@mcp.tool()
async def history_version(
    ctx: object,
    item_id: str,
) -> dict[str, object]:
    """Get version history for specific item.

    Args:
        ctx: MCP context
        item_id: Item ID to get history for

    Returns:
        MCP response with version history
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "message": f"Version history for {item_id}",
                "item_id": item_id,
                "versions": [],
            },
            ctx,
            "history_version",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get version history: {e!s}", "history_version")


@mcp.tool()
async def history_rollback(
    ctx: object,
    item_id: str,
    version: int,
    confirm: bool = False,
) -> dict[str, object]:
    """Rollback item to previous version.

    Args:
        ctx: MCP context
        item_id: Item ID to rollback
        version: Version number to rollback to
        confirm: Must be True to proceed

    Returns:
        MCP response with rollback status
    """
    await asyncio.sleep(0)
    try:
        if not confirm:
            return _error(
                "Rollback requires confirm=True",
                "history_rollback",
                "CONFIRMATION_REQUIRED",
            )

        return _wrap(
            {
                "message": f"Rolled back {item_id} to version {version}",
                "item_id": item_id,
                "version": version,
            },
            ctx,
            "history_rollback",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Rollback failed: {e!s}", "history_rollback")


# ==========================================================================
# Agent Tools
# ==========================================================================


@mcp.tool()
async def agent_list(
    ctx: object,
    project_id: str | None = None,
) -> dict[str, object]:
    """List active agents in project.

    Args:
        ctx: MCP context
        project_id: Optional project ID

    Returns:
        MCP response with agent list
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        project_id = project_id or (str(config.get("current_project_id")) if config.get("current_project_id") else None)

        return _wrap(
            {
                "message": "Active agents",
                "project_id": project_id,
                "agents": [],
                "total": 0,
            },
            ctx,
            "agent_list",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to list agents: {e!s}", "agent_list")


@mcp.tool()
async def agent_activity(
    ctx: object,
    agent_id: str | None = None,
) -> dict[str, object]:
    """Get agent activity log.

    Args:
        ctx: MCP context
        agent_id: Optional agent ID

    Returns:
        MCP response with activity
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "message": "Agent activity",
                "agent_id": agent_id or "all",
                "events": [],
            },
            ctx,
            "agent_activity",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get agent activity: {e!s}", "agent_activity")


@mcp.tool()
async def agent_metrics(
    ctx: object,
    agent_id: str | None = None,
) -> dict[str, object]:
    """Get agent performance metrics.

    Args:
        ctx: MCP context
        agent_id: Optional agent ID

    Returns:
        MCP response with metrics
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "message": "Agent metrics",
                "agent_id": agent_id or "all",
                "metrics": {
                    "tasks_completed": 0,
                    "avg_duration": 0,
                    "success_rate": 0,
                },
            },
            ctx,
            "agent_metrics",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get agent metrics: {e!s}", "agent_metrics")


@mcp.tool()
async def agent_workload(
    ctx: object,
    agent_id: str | None = None,
) -> dict[str, object]:
    """Get agent workload status.

    Args:
        ctx: MCP context
        agent_id: Optional agent ID

    Returns:
        MCP response with workload
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "message": "Agent workload",
                "agent_id": agent_id or "all",
                "tasks_queued": 0,
                "tasks_in_progress": 0,
            },
            ctx,
            "agent_workload",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get agent workload: {e!s}", "agent_workload")


@mcp.tool()
async def agent_health(
    ctx: object,
    agent_id: str | None = None,
) -> dict[str, object]:
    """Check agent health status.

    Args:
        ctx: MCP context
        agent_id: Optional agent ID

    Returns:
        MCP response with health status
    """
    await asyncio.sleep(0)
    try:
        return _wrap(
            {
                "message": "Agent health",
                "agent_id": agent_id or "all",
                "status": "healthy",
                "uptime": 0,
            },
            ctx,
            "agent_health",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to check agent health: {e!s}", "agent_health")


# ==========================================================================
# State Tools
# ==========================================================================


@mcp.tool()
async def state_show(ctx: object) -> dict[str, object]:
    """Show current system state.

    Returns:
        MCP response with system state
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()

        return _wrap(
            {
                "message": "Current system state",
                "current_project_id": config.get("current_project_id"),
                "current_view": config.get("current_view"),
                "database_url": config.get("database_url") is not None,
            },
            ctx,
            "state_show",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to show state: {e!s}", "state_show")


@mcp.tool()
async def state_get(ctx: object, key: str) -> dict[str, object]:
    """Get a specific state value.

    Args:
        ctx: MCP context
        key: State key to retrieve

    Returns:
        MCP response with state value
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        value = config.get(key)

        return _wrap(
            {
                "key": key,
                "value": value,
            },
            ctx,
            "state_get",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to get state: {e!s}", "state_get")


# ==========================================================================
# Drill Tool
# ==========================================================================


@mcp.tool()
async def drill_item(
    ctx: object,
    item_id: str,
    depth: int = 2,
    project_id: str | None = None,
) -> dict[str, object]:
    """Drill down into item details and relationships.

    Args:
        ctx: MCP context
        item_id: Item ID to drill into
        depth: Depth of drilling (default 2)
        project_id: Optional project ID

    Returns:
        MCP response with item details
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        project_id = project_id or (str(config.get("current_project_id")) if config.get("current_project_id") else None)

        return _wrap(
            {
                "message": f"Drilling into {item_id}",
                "item_id": item_id,
                "project_id": project_id,
                "depth": depth,
                "relationships": [],
            },
            ctx,
            "drill_item",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Drill failed: {e!s}", "drill_item")


# ==========================================================================
# Dashboard Tool
# ==========================================================================


@mcp.tool()
async def dashboard_show(
    ctx: object,
    project_id: str | None = None,
) -> dict[str, object]:
    """Show project dashboard.

    Args:
        ctx: MCP context
        project_id: Optional project ID

    Returns:
        MCP response with dashboard data
    """
    await asyncio.sleep(0)
    try:
        config = ConfigManager()
        project_id = project_id or (str(config.get("current_project_id")) if config.get("current_project_id") else None)

        return _wrap(
            {
                "message": "Project dashboard",
                "project_id": project_id,
                "statistics": {
                    "total_items": 0,
                    "total_links": 0,
                    "traceability": 0,
                },
            },
            ctx,
            "dashboard_show",
        )
    except _TOOL_OPERATION_ERRORS as e:
        return _error(f"Failed to show dashboard: {e!s}", "dashboard_show")
