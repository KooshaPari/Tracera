"""
Item management MCP tools.

Provides tools for creating, reading, updating, deleting, and querying items.
Items represent traceable artifacts: requirements, features, tests, etc.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastmcp.exceptions import ToolError
from sqlalchemy import func, select
from sqlalchemy.orm.exc import StaleDataError

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base_async import (
    get_mcp_session,
    require_project,
    wrap_success,
)
from tracertm.models.item import Item


def _item_to_dict(item: Item) -> dict[str, Any]:
    """Convert an Item model to a dictionary."""
    return {
        "id": item.id,
        "external_id": item.external_id,
        "title": item.title,
        "description": item.description,
        "view": item.view,
        "item_type": item.item_type,
        "status": item.status,
        "priority": item.priority,
        "owner": item.owner,
        "parent_id": item.parent_id,
        "metadata": item.item_metadata,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


@mcp.tool(description="Create a new item")
async def create_item(
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
    """Create a new traceable item.

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

    Returns:
        Created item details
    """
    project_id = await require_project()

    if not title or not view or not item_type:
        raise ToolError("title, view, and item_type are required.")

    view = view.upper()

    async with get_mcp_session() as session:
        # Generate external ID
        count_result = await session.execute(
            select(func.count(Item.id)).filter(
                Item.project_id == project_id, Item.view == view
            )
        )
        count = count_result.scalar()
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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(item)
        await session.commit()

        return wrap_success(_item_to_dict(item), "create", ctx)


@mcp.tool(description="Get an item by ID")
async def get_item(
    item_id: str,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a single item by ID (supports prefix matching).

    Args:
        item_id: Item ID or external ID prefix

    Returns:
        Item details
    """
    if not item_id:
        raise ToolError("item_id is required.")

    project_id = await require_project()

    async with get_mcp_session() as session:
        # Try exact ID match
        result = await session.execute(
            select(Item).filter(
                Item.project_id == project_id,
                Item.id == item_id,
                Item.deleted_at.is_(None),
            )
        )
        item = result.scalar_one_or_none()

        # Try external_id prefix match
        if not item:
            result = await session.execute(
                select(Item).filter(
                    Item.project_id == project_id,
                    Item.external_id.ilike(f"{item_id}%"),
                    Item.deleted_at.is_(None),
                )
            )
            item = result.scalar_one_or_none()

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        return wrap_success(_item_to_dict(item), "get", ctx)


@mcp.tool(description="Update an existing item")
async def update_item(
    item_id: str,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
    metadata: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Update an existing item's fields.

    Args:
        item_id: Item ID to update (required)
        title: New title
        description: New description
        status: New status
        priority: New priority
        owner: New owner
        metadata: Metadata to merge (updates only specified keys)

    Returns:
        Updated item details
    """
    if not item_id:
        raise ToolError("item_id is required.")

    project_id = require_project()

    with get_session() as session:
        item = (
            session.query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .filter(
                (Item.id == item_id) | (Item.external_id.ilike(f"{item_id}%"))
            )
            .first()
        )

        if not item:
            raise ToolError(f"Item not found: {item_id}")

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

        item.updated_at = datetime.utcnow()

        try:
            session.commit()
        except StaleDataError:
            session.rollback()
            raise ToolError("Item was modified by another process. Please retry.")

        return wrap_success(_item_to_dict(item), "update", ctx)


@mcp.tool(description="Delete an item (soft delete)")
async def delete_item(
    item_id: str,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Soft-delete an item by setting deleted_at timestamp.

    Args:
        item_id: Item ID to delete

    Returns:
        Confirmation of deletion
    """
    if not item_id:
        raise ToolError("item_id is required.")

    project_id = require_project()

    with get_session() as session:
        item = (
            session.query(Item)
            .filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .filter(
                (Item.id == item_id) | (Item.external_id.ilike(f"{item_id}%"))
            )
            .first()
        )

        if not item:
            raise ToolError(f"Item not found: {item_id}")

        item.deleted_at = datetime.utcnow()
        item.updated_at = datetime.utcnow()
        session.commit()

        return wrap_success(
            {"id": item.id, "external_id": item.external_id, "deleted": True},
            "delete",
            ctx,
        )


@mcp.tool(description="Query items with filters")
async def query_items(
    view: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    limit: int = 50,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Query items with optional filters.

    Args:
        view: Filter by view (FEATURE, REQUIREMENT, TEST, etc.)
        item_type: Filter by item type
        status: Filter by status
        owner: Filter by owner
        limit: Maximum results (default 50, max 500)

    Returns:
        List of matching items
    """
    project_id = require_project()
    limit = min(limit, 500)

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

        items = query.limit(limit).all()

        return wrap_success(
            {
                "items": [_item_to_dict(i) for i in items],
                "count": len(items),
                "limit": limit,
            },
            "query",
            ctx,
        )


@mcp.tool(description="Summarize items in a view")
async def summarize_view(
    view: str,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get a summary of items in a view, grouped by status.

    Args:
        view: View to summarize (FEATURE, REQUIREMENT, TEST, etc.)

    Returns:
        Summary with counts by status and sample items
    """
    if not view:
        raise ToolError("view is required.")

    project_id = require_project()
    view = view.upper()

    with get_session() as session:
        # Get counts by status
        status_counts = (
            session.query(Item.status, func.count(Item.id))
            .filter(
                Item.project_id == project_id,
                Item.view == view,
                Item.deleted_at.is_(None),
            )
            .group_by(Item.status)
            .all()
        )

        # Get sample items
        samples = (
            session.query(Item)
            .filter(
                Item.project_id == project_id,
                Item.view == view,
                Item.deleted_at.is_(None),
            )
            .order_by(Item.updated_at.desc())
            .limit(5)
            .all()
        )

        return wrap_success(
            {
                "view": view,
                "status_counts": {status: count for status, count in status_counts},
                "total": sum(count for _, count in status_counts),
                "samples": [_item_to_dict(i) for i in samples],
            },
            "summarize_view",
            ctx,
        )


@mcp.tool(description="Bulk update items by filter")
async def bulk_update_items(
    view: str | None = None,
    status: str | None = None,
    new_status: str | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Bulk update item status by filter.

    Args:
        view: Filter by view (optional)
        status: Filter by current status (optional)
        new_status: New status to set (required)

    Returns:
        Count of updated items
    """
    if not new_status:
        raise ToolError("new_status is required.")

    project_id = require_project()

    with get_session() as session:
        query = session.query(Item).filter(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        if view:
            query = query.filter(Item.view == view.upper())
        if status:
            query = query.filter(Item.status == status)

        items = query.all()
        count = 0

        for item in items:
            item.status = new_status
            item.updated_at = datetime.utcnow()
            count += 1

        session.commit()

        return wrap_success(
            {
                "updated_count": count,
                "new_status": new_status,
                "filters": {"view": view, "status": status},
            },
            "bulk_update",
            ctx,
        )


__all__ = [
    "create_item",
    "get_item",
    "update_item",
    "delete_item",
    "query_items",
    "summarize_view",
    "bulk_update_items",
]
