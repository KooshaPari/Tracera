"""Optimized item management MCP tools (Phase 2).

These are lean, token-efficient versions of item tools that:
- Return minimal responses (50% fewer tokens)
- Use short IDs (8 chars instead of full UUIDs)
- Omit unnecessary metadata
- Support compression for large responses
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from fastmcp.exceptions import ToolError
from sqlalchemy import func

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import get_session, require_project
from tracertm.mcp.tools.response_optimizer import (
    format_error,
    optimize_item_response,
)
from tracertm.models.item import Item


@mcp.tool(description="Create item (optimized)")
async def create_item_v2(
    title: str,
    view: str,
    item_type: str,
    description: str | None = None,
    status: str = "todo",
    priority: str = "medium",
    owner: str | None = None,
    parent_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Create a new item (optimized, lean response).

    This is a token-optimized version of create_item that returns
    minimal response data (50% fewer tokens).

    Args:
        title: Item title (required)
        view: View category (FEATURE, REQUIREMENT, TEST, etc.)
        item_type: Specific type within the view
        description: Detailed description
        status: Item status (todo, in_progress, done, etc.)
        priority: Priority level (low, medium, high, critical)
        owner: Owner/assignee
        parent_id: Parent item ID for hierarchical items
        metadata: Additional metadata as key-value pairs
        ctx: MCP context

    Returns:
        Created item with minimal fields (id, title, view, type, status)
    """
    await asyncio.sleep(0)
    try:
        project_id = require_project()

        if not title or not view or not item_type:
            return format_error(
                "title, view, and item_type are required",
                action="create_item",
                category="validation",
                suggestions=[
                    "Provide title, view, and item_type parameters",
                    "Example: create_item_v2(title='New Feature', view='FEATURE', item_type='epic')",
                ],
                ctx=ctx,
            )

        view = view.upper()

        with get_session() as session:
            # Generate external ID
            count = session.query(func.count(Item.id)).filter(Item.project_id == project_id, Item.view == view).scalar()
            external_id = f"{view[:3].upper()}-{count + 1}"

            item = Item(
                id=str(uuid.uuid4()),
                external_id=external_id,
                project_id=project_id,
                title=title,
                description=description or "",
                view=view,
                item_type=item_type,
                status=status,
                priority=priority,
                owner=owner,
                parent_id=parent_id,
                item_metadata=metadata or {},
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            session.add(item)
            session.commit()

            # Return lean response
            return optimize_item_response(item, include_metadata=False)

    except ToolError as e:
        return format_error(str(e), action="create_item", ctx=ctx)
    except Exception as e:
        return format_error(
            f"Failed to create item: {e!s}",
            action="create_item",
            category="error",
            ctx=ctx,
        )


@mcp.tool(description="Get item (optimized)")
async def get_item_v2(
    item_id: str,
    include_metadata: bool = False,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a single item by ID (optimized, lean response).

    This returns minimal item data by default. Set include_metadata=True
    to include the full item_metadata field.

    Args:
        item_id: Item ID or external ID prefix
        include_metadata: Include item metadata (default False)
        ctx: MCP context

    Returns:
        Item with minimal fields (id, title, view, type, status)
    """
    await asyncio.sleep(0)
    try:
        if not item_id:
            return format_error(
                "item_id is required",
                category="validation",
                suggestions=["Provide an item_id parameter"],
                ctx=ctx,
            )

        project_id = require_project()

        with get_session() as session:
            # Try exact ID match
            item = (
                session
                .query(Item)
                .filter(
                    Item.project_id == project_id,
                    Item.id == item_id,
                    Item.deleted_at.is_(None),
                )
                .first()
            )

            # Try external_id prefix match
            if not item:
                item = (
                    session
                    .query(Item)
                    .filter(
                        Item.project_id == project_id,
                        Item.external_id.ilike(f"{item_id}%"),
                        Item.deleted_at.is_(None),
                    )
                    .first()
                )

            if not item:
                return format_error(
                    f"Item not found: {item_id}",
                    category="not_found",
                    ctx=ctx,
                )

            return optimize_item_response(item, include_metadata=include_metadata)

    except ToolError as e:
        return format_error(str(e), ctx=ctx)
    except Exception as e:
        return format_error(f"Failed to get item: {e!s}", ctx=ctx)


@mcp.tool(description="Query items (optimized)")
async def query_items_v2(
    view: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    limit: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Query items with filters (optimized, lean response).

    Returns minimal item data by default. For large queries (>50 items),
    use stream_items instead for better token efficiency.

    Args:
        view: Filter by view (FEATURE, REQUIREMENT, TEST, etc.)
        item_type: Filter by item type
        status: Filter by status
        owner: Filter by owner
        limit: Maximum results (default 50, max 100)
        ctx: MCP context

    Returns:
        List of items with minimal fields, count, and has_more flag
    """
    await asyncio.sleep(0)
    try:
        project_id = require_project()
        limit = min(limit, 100)

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
            if owner:
                query = query.filter(Item.owner == owner)

            # Get total count for has_more
            total = query.count()
            items = query.limit(limit).all()

            return {
                "items": [optimize_item_response(i) for i in items],
                "count": len(items),
                "total": total,
                "has_more": total > limit,
            }

    except ToolError as e:
        return format_error(str(e), ctx=ctx)
    except Exception as e:
        return format_error(f"Failed to query items: {e!s}", ctx=ctx)


@mcp.tool(description="Update item (optimized)")
async def update_item_v2(
    item_id: str,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
    metadata: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Update an existing item (optimized, lean response).

    Args:
        item_id: Item ID to update (required)
        title: New title
        description: New description
        status: New status
        priority: New priority
        owner: New owner
        metadata: Metadata to merge
        ctx: MCP context

    Returns:
        Updated item with minimal fields
    """
    await asyncio.sleep(0)
    try:
        if not item_id:
            return format_error(
                "item_id is required",
                category="validation",
                ctx=ctx,
            )

        project_id = require_project()

        with get_session() as session:
            item = (
                session
                .query(Item)
                .filter(
                    Item.project_id == project_id,
                    Item.deleted_at.is_(None),
                )
                .filter((Item.id == item_id) | (Item.external_id.ilike(f"{item_id}%")))
                .first()
            )

            if not item:
                return format_error(
                    f"Item not found: {item_id}",
                    category="not_found",
                    ctx=ctx,
                )

            # Update fields if provided
            if title is not None:
                item.title = title
            if description is not None:
                item.description = description
            if status is not None:
                item.status = status
            if priority is not None:
                item.priority = priority
            if owner is not None:
                item.owner = owner
            if metadata is not None:
                # Merge metadata
                current = item.item_metadata or {}
                current.update(metadata)
                item.item_metadata = current

            item.updated_at = datetime.now(UTC)

            session.commit()

            return optimize_item_response(item, include_metadata=False)

    except ToolError as e:
        return format_error(str(e), ctx=ctx)
    except Exception as e:
        return format_error(f"Failed to update item: {e!s}", ctx=ctx)


@mcp.tool(description="Delete item (optimized)")
async def delete_item_v2(
    item_id: str,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Soft-delete an item (optimized, lean response).

    Args:
        item_id: Item ID to delete
        ctx: MCP context

    Returns:
        Minimal confirmation (id and deleted flag)
    """
    await asyncio.sleep(0)
    try:
        if not item_id:
            return format_error(
                "item_id is required",
                category="validation",
                ctx=ctx,
            )

        project_id = require_project()

        with get_session() as session:
            item = (
                session
                .query(Item)
                .filter(
                    Item.project_id == project_id,
                    Item.deleted_at.is_(None),
                )
                .filter((Item.id == item_id) | (Item.external_id.ilike(f"{item_id}%")))
                .first()
            )

            if not item:
                return format_error(
                    f"Item not found: {item_id}",
                    category="not_found",
                    ctx=ctx,
                )

            item.deleted_at = datetime.now(UTC)
            item.updated_at = datetime.now(UTC)
            session.commit()

            return {
                "id": str(item.id)[:8],
                "deleted": True,
            }

    except ToolError as e:
        return format_error(str(e), ctx=ctx)
    except Exception as e:
        return format_error(f"Failed to delete item: {e!s}", ctx=ctx)


@mcp.tool(description="Summarize view (optimized)")
async def summarize_view_v2(
    view: str,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a summary of items in a view (optimized, lean response).

    Args:
        view: View to summarize (FEATURE, REQUIREMENT, TEST, etc.)
        ctx: MCP context

    Returns:
        Summary with counts by status (no sample items by default)
    """
    await asyncio.sleep(0)
    try:
        if not view:
            return format_error(
                "view is required",
                category="validation",
                ctx=ctx,
            )

        project_id = require_project()
        view = view.upper()

        with get_session() as session:
            # Get counts by status
            status_counts = (
                session
                .query(Item.status, func.count(Item.id))
                .filter(
                    Item.project_id == project_id,
                    Item.view == view,
                    Item.deleted_at.is_(None),
                )
                .group_by(Item.status)
                .all()
            )

            counts = dict(status_counts)
            total = sum(counts.values())

            return {
                "view": view,
                "total": total,
                "by_status": counts,
            }

    except ToolError as e:
        return format_error(str(e), ctx=ctx)
    except Exception as e:
        return format_error(f"Failed to summarize view: {e!s}", ctx=ctx)


__all__ = [
    "create_item_v2",
    "delete_item_v2",
    "get_item_v2",
    "query_items_v2",
    "summarize_view_v2",
    "update_item_v2",
]
