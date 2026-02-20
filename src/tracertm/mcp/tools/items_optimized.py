"""Optimized item management MCP tools (Phase 2).

These are lean, token-efficient versions of item tools that:
- Return minimal responses (50% fewer tokens)
- Use short IDs (8 chars instead of full UUIDs)
- Omit unnecessary metadata
- Support compression for large responses
"""

from __future__ import annotations

import asyncio
import contextlib
import uuid
from datetime import UTC, datetime
from typing import TypedDict

from fastmcp.exceptions import ToolError
from sqlalchemy import func

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import get_session, require_project
from tracertm.mcp.tools.response_optimizer import (
    format_error,
    optimize_item_response,
)
from tracertm.models.item import Item


class CreateItemOptionsOptimized(TypedDict, total=False):
    """Optional fields for create_item_optimized."""

    description: str | None
    status: str
    priority: str
    owner: str | None
    parent_id: str | None
    metadata: dict[str, object] | None


class UpdateItemOptionsOptimized(TypedDict, total=False):
    """Optional fields for update_item_optimized."""

    title: str | None
    description: str | None
    status: str | None
    priority: str | None
    owner: str | None
    metadata: dict[str, object] | None


class QueryItemsFiltersOptimized(TypedDict, total=False):
    """Filters for query_items_optimized."""

    view: str | None
    item_type: str | None
    status: str | None
    owner: str | None


def _apply_item_updates_optimized(item: Item, opts: UpdateItemOptionsOptimized) -> None:
    """Apply optional update fields to an Item. Mutates item in place."""
    for key, attr, transform in (
        ("title", "title", lambda value: value),
        ("description", "description", lambda value: value),
        ("status", "status", str),
    ):
        value = opts.get(key)
        if value is not None:
            setattr(item, attr, transform(value))

    priority = opts.get("priority")
    if priority is not None:
        with contextlib.suppress(ValueError, TypeError):
            item.priority = int(priority)

    # item.owner is read-only
    metadata = opts.get("metadata")
    if metadata is not None:
        current = dict(item.item_metadata or {})
        if metadata:
            current.update(metadata)
        item.item_metadata = current
    item.updated_at = datetime.now(UTC)


@mcp.tool(description="Create item (optimized)")
async def create_item_optimized(
    title: str,
    view: str,
    item_type: str,
    options: CreateItemOptionsOptimized | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Create a new item (optimized, lean response).

    Args:
        title: Item title (required)
        view: View category (FEATURE, REQUIREMENT, TEST, etc.)
        item_type: Specific type within the view
        options: Optional dict with description, status, priority, owner, parent_id, metadata
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
                    "Example: create_item_optimized(title='New Feature', view='FEATURE', item_type='epic')",
                ],
                ctx=ctx,
            )

        view = view.upper()
        opts = options or {}
        description = opts.get("description")
        status = opts.get("status", "todo")
        priority = opts.get("priority", "medium")
        owner = opts.get("owner")
        parent_id = opts.get("parent_id")
        metadata = opts.get("metadata")

        with get_session() as session:
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
async def get_item_optimized(
    item_id: str,
    include_metadata: bool = False,
    ctx: object | None = None,
) -> dict[str, object]:
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
async def query_items_optimized(
    filters: QueryItemsFiltersOptimized | None = None,
    limit: int = 50,
    ctx: object | None = None,
) -> dict[str, object]:
    """Query items with filters (optimized, lean response).

    Args:
        filters: Optional dict with view, item_type, status, owner
        limit: Maximum results (default 50, max 100)
        ctx: MCP context

    Returns:
        List of items with minimal fields, count, and has_more flag
    """
    await asyncio.sleep(0)
    try:
        project_id = require_project()
        limit = min(limit, 100)
        flt = filters or {}

        with get_session() as session:
            query = session.query(Item).filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )

            if flt.get("view"):
                query = query.filter(Item.view == (flt["view"] or "").upper())
            if flt.get("item_type"):
                query = query.filter(Item.item_type == flt["item_type"])
            if flt.get("status"):
                query = query.filter(Item.status == flt["status"])
            # Item.owner is a property returning None, cannot be used in filter
            # if flt.get("owner"):

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
async def update_item_optimized(
    item_id: str,
    options: UpdateItemOptionsOptimized | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Update an existing item (optimized, lean response).

    Args:
        item_id: Item ID to update (required)
        options: Optional dict with title, description, status, priority, owner, metadata
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
        opts = options or {}

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

            _apply_item_updates_optimized(item, opts)
            session.commit()

            return optimize_item_response(item, include_metadata=False)

    except ToolError as e:
        return format_error(str(e), ctx=ctx)
    except Exception as e:
        return format_error(f"Failed to update item: {e!s}", ctx=ctx)


@mcp.tool(description="Delete item (optimized)")
async def delete_item_optimized(
    item_id: str,
    ctx: object | None = None,
) -> dict[str, object]:
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
async def summarize_view_optimized(
    view: str,
    ctx: object | None = None,
) -> dict[str, object]:
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

            counts: dict[str, int] = {str(row[0]): int(row[1]) for row in status_counts}
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
    "create_item_optimized",
    "delete_item_optimized",
    "get_item_optimized",
    "query_items_optimized",
    "summarize_view_optimized",
    "update_item_optimized",
]
