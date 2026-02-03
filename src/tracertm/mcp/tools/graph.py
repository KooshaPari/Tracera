"""
Graph analysis MCP tools.

Provides tools for cycle detection and shortest path finding
in the traceability graph.
"""

from __future__ import annotations

from typing import Any

from fastmcp.exceptions import ToolError

from tracertm.core.database import get_session as get_async_session
from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import (
    require_project,
    wrap_success,
)
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.services.shortest_path_service import ShortestPathService


@mcp.tool(description="Detect cycles in the traceability graph")
async def detect_cycles(
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Find dependency cycles in the current project's link graph.

    Cycles indicate circular dependencies that may need resolution.

    Returns:
        List of detected cycles with involved items
    """
    project_id = require_project()

    async with get_async_session() as session:
        service = CycleDetectionService(session)
        cycles = await service.detect_cycles(project_id=project_id)

        return wrap_success(
            {
                "project_id": project_id,
                "cycle_count": len(cycles) if cycles else 0,
                "cycles": cycles if cycles else [],
            },
            "detect_cycles",
            ctx,
        )


@mcp.tool(description="Find shortest path between two items")
async def shortest_path(
    source_id: str,
    target_id: str,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Find the shortest path between two items in the link graph.

    Uses BFS to find the shortest sequence of links connecting
    the source to the target.

    Args:
        source_id: Starting item ID (required)
        target_id: Destination item ID (required)

    Returns:
        Path as list of items and links, or indication if no path exists
    """
    if not source_id or not target_id:
        raise ToolError("source_id and target_id are required.")

    project_id = require_project()

    async with get_async_session() as session:
        service = ShortestPathService(session)
        path = await service.find_shortest_path(
            project_id=project_id,
            source_id=source_id,
            target_id=target_id,
        )

        if path is None:
            return wrap_success(
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "path_exists": False,
                    "path": None,
                    "length": None,
                },
                "shortest_path",
                ctx,
            )

        to_dict = getattr(path, "to_dict", None)
        path_val = to_dict() if callable(to_dict) else path
        path_len: int | None = None
        if hasattr(path, "__len__"):
            try:
                path_len = len(path)  # type: ignore[arg-type]
            except TypeError:
                pass
        return wrap_success(
            {
                "source_id": source_id,
                "target_id": target_id,
                "path_exists": True,
                "path": path_val,
                "length": path_len,
            },
            "shortest_path",
            ctx,
        )


__all__ = [
    "detect_cycles",
    "shortest_path",
]
