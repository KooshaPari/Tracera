"""Advanced streaming utilities for large MCP operations.

Provides async generators for streaming large result sets in batches,
reducing token usage and improving response times.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from fastmcp.exceptions import ToolError

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import get_session, require_project
from tracertm.mcp.tools.response_optimizer import (
    optimize_item_response,
    optimize_link_response,
)
from tracertm.models.item import Item
from tracertm.models.link import Link


def stream_query_results(
    query: Any,
    batch_size: int = 50,
    optimizer_func: Callable[..., Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Stream query results in batches.

    Args:
        query: SQLAlchemy query object
        batch_size: Number of items per batch
        optimizer_func: Optional function to optimize each item

    Yields:
        Batches of results with metadata
    """
    total = query.count()
    total_batches = (total + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        offset = batch_num * batch_size
        batch_items = query.offset(offset).limit(batch_size).all()

        if optimizer_func:
            batch_items = [optimizer_func(item) for item in batch_items]

        yield {
            "batch": batch_num + 1,
            "total_batches": total_batches,
            "items": batch_items,
            "count": len(batch_items),
            "has_more": batch_num + 1 < total_batches,
        }


@mcp.tool(description="Stream items query with batching")
def stream_items(
    view: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    batch_size: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Stream items in batches to reduce token usage.

    For large result sets (>100 items), this streams batches progressively.
    Use this instead of query_items for large queries.

    Args:
        view: Filter by view
        item_type: Filter by item type
        status: Filter by status
        batch_size: Items per batch (default 50)
        ctx: MCP context

    Returns:
        First batch with metadata for subsequent batches
    """
    project_id = require_project()
    batch_size = min(max(batch_size, 10), 100)  # Clamp 10-100

    with get_session() as session:
        query = session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        if view:
            query = query.filter(Item.view == view.upper())
        if item_type:
            query = query.filter(Item.item_type == item_type)
        if status:
            query = query.filter(Item.status == status)

        total = query.count()
        total_batches = (total + batch_size - 1) // batch_size

        # Return first batch
        first_batch = query.limit(batch_size).all()
        items = [optimize_item_response(item) for item in first_batch]

        return {
            "items": items,
            "batch": 1,
            "total": total,
            "total_batches": total_batches,
            "batch_size": batch_size,
            "has_more": total > batch_size,
            "filters": {"view": view, "item_type": item_type, "status": status},
            "next_batch_hint": "Call get_items_batch(batch=2, ...) to get next batch",
        }


@mcp.tool(description="Get a specific batch of items")
def get_items_batch(
    batch: int,
    view: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    batch_size: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a specific batch of items (for continuation of stream_items).

    Args:
        batch: Batch number (1-indexed)
        view: Filter by view (must match initial query)
        item_type: Filter by item type (must match initial query)
        status: Filter by status (must match initial query)
        batch_size: Items per batch (must match initial query)
        ctx: MCP context

    Returns:
        Requested batch with navigation metadata
    """
    project_id = require_project()
    batch_size = min(max(batch_size, 10), 100)
    offset = (batch - 1) * batch_size

    with get_session() as session:
        query = session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        if view:
            query = query.filter(Item.view == view.upper())
        if item_type:
            query = query.filter(Item.item_type == item_type)
        if status:
            query = query.filter(Item.status == status)

        total = query.count()
        total_batches = (total + batch_size - 1) // batch_size

        if batch < 1 or batch > total_batches:
            raise ToolError(f"Invalid batch {batch}. Valid range: 1-{total_batches}")

        batch_items = query.offset(offset).limit(batch_size).all()
        items = [optimize_item_response(item) for item in batch_items]

        return {
            "items": items,
            "batch": batch,
            "total": total,
            "total_batches": total_batches,
            "has_more": batch < total_batches,
            "has_prev": batch > 1,
        }


@mcp.tool(description="Stream links query with batching")
def stream_links(
    link_type: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    batch_size: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Stream links in batches to reduce token usage.

    Args:
        link_type: Filter by link type
        source_id: Filter by source item ID
        target_id: Filter by target item ID
        batch_size: Links per batch (default 50)
        ctx: MCP context

    Returns:
        First batch with metadata for subsequent batches
    """
    project_id = require_project()
    batch_size = min(max(batch_size, 10), 100)

    with get_session() as session:
        query = session.query(Link).filter(Link.project_id == project_id)

        if link_type:
            query = query.filter(Link.link_type == link_type)
        if source_id:
            query = query.filter(Link.source_item_id.like(f"{source_id}%"))
        if target_id:
            query = query.filter(Link.target_item_id.like(f"{target_id}%"))

        total = query.count()
        total_batches = (total + batch_size - 1) // batch_size

        # Return first batch
        first_batch = query.limit(batch_size).all()
        links = [optimize_link_response(link) for link in first_batch]

        return {
            "links": links,
            "batch": 1,
            "total": total,
            "total_batches": total_batches,
            "batch_size": batch_size,
            "has_more": total > batch_size,
            "filters": {
                "link_type": link_type,
                "source_id": source_id,
                "target_id": target_id,
            },
            "next_batch_hint": "Call get_links_batch(batch=2, ...) to get next batch",
        }


@mcp.tool(description="Get a specific batch of links")
def get_links_batch(
    batch: int,
    link_type: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    batch_size: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a specific batch of links (for continuation of stream_links).

    Args:
        batch: Batch number (1-indexed)
        link_type: Filter by link type (must match initial query)
        source_id: Filter by source ID (must match initial query)
        target_id: Filter by target ID (must match initial query)
        batch_size: Links per batch (must match initial query)
        ctx: MCP context

    Returns:
        Requested batch with navigation metadata
    """
    project_id = require_project()
    batch_size = min(max(batch_size, 10), 100)
    offset = (batch - 1) * batch_size

    with get_session() as session:
        query = session.query(Link).filter(Link.project_id == project_id)

        if link_type:
            query = query.filter(Link.link_type == link_type)
        if source_id:
            query = query.filter(Link.source_item_id.like(f"{source_id}%"))
        if target_id:
            query = query.filter(Link.target_item_id.like(f"{target_id}%"))

        total = query.count()
        total_batches = (total + batch_size - 1) // batch_size

        if batch < 1 or batch > total_batches:
            raise ToolError(f"Invalid batch {batch}. Valid range: 1-{total_batches}")

        batch_links = query.offset(offset).limit(batch_size).all()
        links = [optimize_link_response(link) for link in batch_links]

        return {
            "links": links,
            "batch": batch,
            "total": total,
            "total_batches": total_batches,
            "has_more": batch < total_batches,
            "has_prev": batch > 1,
        }


@mcp.tool(description="Stream traceability matrix with batching")
def stream_matrix(
    source_view: str | None = None,
    target_view: str | None = None,
    batch_size: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Stream traceability matrix rows in batches.

    For large matrices, this returns results in manageable batches
    to reduce token usage.

    Args:
        source_view: Filter by source view
        target_view: Filter by target view
        batch_size: Rows per batch (default 50)
        ctx: MCP context

    Returns:
        First batch of matrix rows with summary statistics
    """
    project_id = require_project()
    batch_size = min(max(batch_size, 10), 100)

    with get_session() as session:
        # Get items
        item_query = session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )
        if source_view:
            item_query = item_query.filter(Item.view == source_view.upper())

        items = item_query.all()
        item_lookup = {str(item.id): item for item in items}

        # Get links
        links = (
            session
            .query(Link)
            .filter(Link.project_id == project_id)
            .all()
        )

        # Build matrix rows
        rows = []
        for item in items:
            item_id = str(item.id)
            outgoing_links = [link for link in links if str(link.source_item_id) == item_id]

            for link in outgoing_links:
                target = item_lookup.get(str(link.target_item_id))
                if target and (not target_view or target.view == target_view.upper()):
                    rows.append({
                        "source": str(item.id)[:8],
                        "target": str(link.target_item_id)[:8],
                        "type": link.link_type,
                    })

        total_rows = len(rows)
        total_batches = (total_rows + batch_size - 1) // batch_size
        first_batch = rows[:batch_size]

        return {
            "rows": first_batch,
            "batch": 1,
            "total_rows": total_rows,
            "total_batches": total_batches,
            "batch_size": batch_size,
            "has_more": total_rows > batch_size,
            "filters": {"source_view": source_view, "target_view": target_view},
            "next_batch_hint": "Call get_matrix_batch(batch=2, ...) to get next batch",
        }


@mcp.tool(description="Get a specific batch of matrix rows")
def get_matrix_batch(
    batch: int,
    source_view: str | None = None,
    target_view: str | None = None,
    batch_size: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a specific batch of matrix rows (for continuation of stream_matrix).

    Args:
        batch: Batch number (1-indexed)
        source_view: Filter by source view (must match initial query)
        target_view: Filter by target view (must match initial query)
        batch_size: Rows per batch (must match initial query)
        ctx: MCP context

    Returns:
        Requested batch of matrix rows
    """
    project_id = require_project()
    batch_size = min(max(batch_size, 10), 100)
    offset = (batch - 1) * batch_size

    with get_session() as session:
        # Get items
        item_query = session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )
        if source_view:
            item_query = item_query.filter(Item.view == source_view.upper())

        items = item_query.all()
        item_lookup = {str(item.id): item for item in items}

        # Get links
        links = (
            session
            .query(Link)
            .filter(Link.project_id == project_id)
            .all()
        )

        # Build matrix rows
        rows = []
        for item in items:
            item_id = str(item.id)
            outgoing_links = [link for link in links if str(link.source_item_id) == item_id]

            for link in outgoing_links:
                target = item_lookup.get(str(link.target_item_id))
                if target and (not target_view or target.view == target_view.upper()):
                    rows.append({
                        "source": str(item.id)[:8],
                        "target": str(link.target_item_id)[:8],
                        "type": link.link_type,
                    })

        total_rows = len(rows)
        total_batches = (total_rows + batch_size - 1) // batch_size

        if batch < 1 or batch > total_batches:
            raise ToolError(f"Invalid batch {batch}. Valid range: 1-{total_batches}")

        batch_rows = rows[offset : offset + batch_size]

        return {
            "rows": batch_rows,
            "batch": batch,
            "total_rows": total_rows,
            "total_batches": total_batches,
            "has_more": batch < total_batches,
            "has_prev": batch > 1,
        }


__all__ = [
    "get_items_batch",
    "get_links_batch",
    "get_matrix_batch",
    "stream_items",
    "stream_links",
    "stream_matrix",
    "stream_query_results",
]
