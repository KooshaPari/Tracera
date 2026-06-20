"""Graph analysis MCP tools.

Provides tools for cycle detection and shortest path finding
in the traceability graph.


Functional Requirements: FR-MCP-002, FR-QUAL-007
"""

from __future__ import annotations

import contextlib
from typing import cast

from fastmcp.exceptions import ToolError

from tracertm.database.async_connection import get_session as get_async_session
from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import (
    require_project,
    wrap_success,
)
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.services.shortest_path_service import ShortestPathService


@mcp.tool(description="Detect cycles in the traceability graph")
async def detect_cycles(
    ctx: object | None = None,
) -> dict[str, object]:
    """Find dependency cycles in the current project's link graph.

    Cycles indicate circular dependencies that may need resolution.

    Returns:
        List of detected cycles with involved items
    """
    project_id = require_project()

    async with get_async_session() as session:
        service = CycleDetectionService(session)
        cycles = service.detect_cycles(project_id=project_id)

        return cast(
            "dict[str, object]",
            wrap_success(
                {
                    "project_id": project_id,
                    "cycle_count": len(cycles) if cycles else 0,
                    "cycles": cycles or [],
                },
                "detect_cycles",
                ctx,
                lean=False,
            ),
        )


@mcp.tool(description="Find shortest path between two items")
async def shortest_path(
    source_id: str,
    target_id: str,
    ctx: object | None = None,
) -> dict[str, object]:
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
        msg = "source_id and target_id are required."
        raise ToolError(msg)

    project_id = require_project()

    async with get_async_session() as session:
        service = ShortestPathService(session)
        path = await service.find_shortest_path(
            project_id=project_id,
            source_id=source_id,
            target_id=target_id,
        )

        if path is None:
            return cast(
                "dict[str, object]",
                wrap_success(
                    {
                        "source_id": source_id,
                        "target_id": target_id,
                        "path_exists": False,
                        "path": None,
                        "length": None,
                    },
                    "shortest_path",
                    ctx,
                    lean=False,
                ),
            )

        to_dict = getattr(path, "to_dict", None)
        path_val = to_dict() if callable(to_dict) else path
        path_len: int | None = None
        if hasattr(path, "__len__"):
            with contextlib.suppress(TypeError):
                path_len = len(path)
        return cast(
            "dict[str, object]",
            wrap_success(
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "path_exists": True,
                    "path": path_val,
                    "length": path_len,
                },
                "shortest_path",
                ctx,
                lean=False,
            ),
        )


__all__ = [
    "detect_cycles",
    "shortest_path",
]
