"""Item management MCP tools.

Provides tools for creating, reading, updating, deleting, and querying items.
Items represent traceable artifacts: requirements, features, tests, etc.


Functional Requirements: FR-MCP-002, FR-APP-001
"""

from __future__ import annotations

import contextlib
import uuid
from datetime import UTC, datetime
from typing import TypedDict

from fastmcp.exceptions import ToolError
from sqlalchemy import func, select
from sqlalchemy.orm.exc import StaleDataError

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import get_session
from tracertm.mcp.tools.base_async import (
    get_mcp_session,
    require_project,
    wrap_success,
)
from tracertm.models.item import Item


class CreateItemOptions(TypedDict, total=False):
    """Optional fields for create_item. MCP clients send as one object."""

    description: str | None
    status: str
    priority: str
    owner: str | None
    parent_id: str | None
    metadata: dict[str, object] | None


class UpdateItemOptions(TypedDict, total=False):
    """Optional fields for update_item. MCP clients send as one object."""

    title: str | None
    description: str | None
    status: str | None
    priority: str | None
    owner: str | None
    metadata: dict[str, object] | None


class QueryItemsFilters(TypedDict, total=False):
    """Filters for query_items. MCP clients send as one object."""

    view: str | None
    item_type: str | None
    status: str | None
    owner: str | None


def _item_to_dict(item: Item) -> dict[str, object]:
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
    options: CreateItemOptions | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Create a new traceable item.

    Args:
        title: Item title (required)
        view: View category (FEATURE, REQUIREMENT, TEST, etc.)
        item_type: Specific type within the view
        options: Optional dict with description, status, priority, owner, parent_id, metadata
        ctx: MCP context

    Returns:
        Created item details
    """
    project_id = await require_project()

    if not title or not view or not item_type:
        msg = "title, view, and item_type are required."
        raise ToolError(msg)

    view = view.upper()
    opts = options or {}
    description = opts.get("description")
    status = opts.get("status", "todo")
    priority = opts.get("priority", "medium")
    owner = opts.get("owner")
    parent_id = opts.get("parent_id")
    metadata = opts.get("metadata")

    async with get_mcp_session() as session:
        count_result = await session.execute(
            select(func.count(Item.id)).filter(Item.project_id == project_id, Item.view == view),
        )
        count = count_result.scalar() or 0
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
        await session.commit()

        return wrap_success(_item_to_dict(item), "create", ctx)


@mcp.tool(description="Get an item by ID")
async def get_item(
    item_id: str,
    ctx: object | None = None,
) -> dict[str, object]:
    """Get a single item by ID (supports prefix matching).

    Args:
        item_id: Item ID or external ID prefix

    Returns:
        Item details
    """
    if not item_id:
        msg = "item_id is required."
        raise ToolError(msg)

    project_id = await require_project()

    async with get_mcp_session() as session:
        # Try exact ID match
        result = await session.execute(
            select(Item).filter(
                Item.project_id == project_id,
                Item.id == item_id,
                Item.deleted_at.is_(None),
            ),
        )
        item = result.scalar_one_or_none()

        # Try external_id prefix match
        if not item:
            result = await session.execute(
                select(Item).filter(
                    Item.project_id == project_id,
                    Item.external_id.ilike(f"{item_id}%"),
                    Item.deleted_at.is_(None),
                ),
            )
            item = result.scalar_one_or_none()

        if not item:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        return wrap_success(_item_to_dict(item), "get", ctx)


def _apply_item_updates(item: Item, opts: UpdateItemOptions) -> None:
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


@mcp.tool(description="Update an existing item")
async def update_item(
    item_id: str,
    options: UpdateItemOptions | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Update an existing item's fields.

    Args:
        item_id: Item ID to update (required)
        options: Optional dict with title, description, status, priority, owner, metadata
        ctx: MCP context

    Returns:
        Updated item details
    """
    if not item_id:
        msg = "item_id is required."
        raise ToolError(msg)

    project_id = await require_project()
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
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        _apply_item_updates(item, opts)

        try:
            session.commit()
        except StaleDataError as err:
            session.rollback()
            msg = "Item was modified by another process. Please retry."
            raise ToolError(msg) from err

        return wrap_success(_item_to_dict(item), "update", ctx)


@mcp.tool(description="Delete an item (soft delete)")
async def delete_item(
    item_id: str,
    ctx: object | None = None,
) -> dict[str, object]:
    """Soft-delete an item by setting deleted_at timestamp.

    Args:
        item_id: Item ID to delete

    Returns:
        Confirmation of deletion
    """
    if not item_id:
        msg = "item_id is required."
        raise ToolError(msg)

    project_id = await require_project()

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
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        item.deleted_at = datetime.now(UTC)
        item.updated_at = datetime.now(UTC)
        session.commit()

        return wrap_success(
            {"id": item.id, "external_id": item.external_id, "deleted": True},
            "delete",
            ctx,
        )


@mcp.tool(description="Query items with filters")
async def query_items(
    filters: QueryItemsFilters | None = None,
    limit: int = 50,
    ctx: object | None = None,
) -> dict[str, object]:
    """Query items with optional filters.

    Args:
        filters: Optional dict with view, item_type, status, owner
        limit: Maximum results (default 50, max 500)
        ctx: MCP context

    Returns:
        List of matching items
    """
    project_id = await require_project()
    limit = min(limit, 500)
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
    ctx: object | None = None,
) -> dict[str, object]:
    """Get a summary of items in a view, grouped by status.

    Args:
        view: View to summarize (FEATURE, REQUIREMENT, TEST, etc.)

    Returns:
        Summary with counts by status and sample items
    """
    if not view:
        msg = "view is required."
        raise ToolError(msg)

    project_id = await require_project()
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

        # Get sample items
        samples = (
            session
            .query(Item)
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
                "status_counts": {str(row[0]): int(row[1]) for row in status_counts},
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
    ctx: object | None = None,
) -> dict[str, object]:
    """Bulk update item status by filter.

    Args:
        view: Filter by view (optional)
        status: Filter by current status (optional)
        new_status: New status to set (required)

    Returns:
        Count of updated items
    """
    if not new_status:
        msg = "new_status is required."
        raise ToolError(msg)

    project_id = await require_project()

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
            item.updated_at = datetime.now(UTC)
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
    "bulk_update_items",
    "create_item",
    "delete_item",
    "get_item",
    "query_items",
    "summarize_view",
    "update_item",
]
