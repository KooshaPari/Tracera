"""
Traceability analysis MCP tools.

Provides tools for gap analysis, impact analysis, traceability matrix,
and project health metrics.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError
from sqlalchemy import func

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import (
    get_session,
    require_project,
    wrap_success,
)
from tracertm.core.database import get_session as get_async_session
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.traceability_service import TraceabilityService
from tracertm.services.traceability_matrix_service import TraceabilityMatrixService
from tracertm.services.impact_analysis_service import ImpactAnalysisService


@mcp.tool(description="Find coverage gaps between views")
async def find_gaps(
    from_view: str,
    to_view: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Find items in from_view that have no links to items in to_view.

    Args:
        from_view: Source view (e.g., REQUIREMENT)
        to_view: Target view (e.g., TEST)

    Returns:
        List of unlinked items (gaps)
    """
    if not from_view or not to_view:
        raise ToolError("from_view and to_view are required.")

    project_id = require_project()
    from_view = from_view.upper()
    to_view = to_view.upper()

    async with get_async_session() as session:
        service = TraceabilityService(session)
        gaps = await service.find_gaps(
            project_id=project_id,
            source_view=from_view,
            target_view=to_view,
        )

        return wrap_success(
            {
                "from_view": from_view,
                "to_view": to_view,
                "gap_count": len(gaps),
                "gaps": [
                    {
                        "id": item.id,
                        "external_id": item.external_id,
                        "title": item.title,
                        "status": item.status,
                    }
                    for item in gaps
                ],
            },
            "find_gaps",
            ctx,
        )


@mcp.tool(description="Generate traceability matrix")
async def get_trace_matrix(
    source_view: str | None = None,
    target_view: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Generate a traceability matrix showing links between views.

    Args:
        source_view: Optional filter for source items' view
        target_view: Optional filter for target items' view

    Returns:
        Matrix with coverage statistics and link details
    """
    project_id = require_project()

    async with get_async_session() as session:
        service = TraceabilityMatrixService(session)
        matrix = await service.generate_matrix(
            project_id=project_id,
            source_view=source_view.upper() if source_view else None,
            target_view=target_view.upper() if target_view else None,
        )

        return wrap_success(
            {
                "source_view": source_view,
                "target_view": target_view,
                "matrix": matrix.to_dict() if hasattr(matrix, "to_dict") else matrix,
            },
            "trace_matrix",
            ctx,
        )


@mcp.tool(description="Analyze downstream impact of an item")
async def analyze_impact(
    item_id: str,
    max_depth: int = 5,
    link_types: list[str] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Analyze downstream impact of changes to an item.

    Uses BFS to find all items that depend on the given item.

    Args:
        item_id: Item ID to analyze (required)
        max_depth: Maximum traversal depth (default 5)
        link_types: Optional filter for specific link types

    Returns:
        Impact tree with affected items by depth
    """
    if not item_id:
        raise ToolError("item_id is required.")

    project_id = require_project()

    async with get_async_session() as session:
        service = ImpactAnalysisService(session)
        impact = await service.analyze_impact(
            project_id=project_id,
            item_id=item_id,
            max_depth=max_depth,
            link_types=link_types,
        )

        return wrap_success(
            {
                "root_item_id": item_id,
                "max_depth": max_depth,
                "link_types": link_types,
                "impact": impact.to_dict() if hasattr(impact, "to_dict") else impact,
            },
            "impact",
            ctx,
        )


@mcp.tool(description="Analyze upstream dependencies of an item")
async def analyze_reverse_impact(
    item_id: str,
    max_depth: int = 5,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Analyze upstream dependencies of an item.

    Uses BFS to find all items that the given item depends on.

    Args:
        item_id: Item ID to analyze (required)
        max_depth: Maximum traversal depth (default 5)

    Returns:
        Dependency tree with upstream items by depth
    """
    if not item_id:
        raise ToolError("item_id is required.")

    project_id = require_project()

    async with get_async_session() as session:
        service = ImpactAnalysisService(session)
        impact = await service.analyze_reverse_impact(
            project_id=project_id,
            item_id=item_id,
            max_depth=max_depth,
        )

        return wrap_success(
            {
                "root_item_id": item_id,
                "max_depth": max_depth,
                "dependencies": impact.to_dict() if hasattr(impact, "to_dict") else impact,
            },
            "reverse_impact",
            ctx,
        )


@mcp.tool(description="Get project health metrics")
async def project_health(
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get high-level health metrics for the current project.

    Returns:
        Metrics including item count, link count, coverage, complexity
    """
    project_id = require_project()

    with get_session() as session:
        # Count items by view
        view_counts = (
            session.query(Item.view, func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .group_by(Item.view)
            .all()
        )

        # Count items by status
        status_counts = (
            session.query(Item.status, func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .group_by(Item.status)
            .all()
        )

        # Count links by type
        link_counts = (
            session.query(Link.link_type, func.count(Link.id))
            .filter(Link.project_id == project_id)
            .group_by(Link.link_type)
            .all()
        )

        # Total counts
        total_items = sum(count for _, count in view_counts)
        total_links = sum(count for _, count in link_counts)

        # Calculate link density
        link_density = total_links / total_items if total_items > 0 else 0

        # Items without any links
        items_with_links = (
            session.query(func.count(func.distinct(Link.source_id)))
            .filter(Link.project_id == project_id)
            .scalar()
        )
        orphan_count = total_items - (items_with_links or 0)

        return wrap_success(
            {
                "project_id": project_id,
                "total_items": total_items,
                "total_links": total_links,
                "link_density": round(link_density, 2),
                "orphan_items": orphan_count,
                "by_view": {view: count for view, count in view_counts},
                "by_status": {status: count for status, count in status_counts},
                "by_link_type": {ltype: count for ltype, count in link_counts},
            },
            "project_health",
            ctx,
        )


__all__ = [
    "find_gaps",
    "get_trace_matrix",
    "analyze_impact",
    "analyze_reverse_impact",
    "project_health",
]
