"""Link management MCP tools.

Provides tools for creating and querying traceability links between items.
Links represent relationships: satisfies, implements, tests, depends_on, etc.


Functional Requirements: FR-MCP-002, FR-APP-002
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from fastmcp.exceptions import ToolError

from tracertm.mcp.core import mcp
from tracertm.mcp.tools.base import (
    get_session,
    require_project,
    wrap_success,
)
from tracertm.models.item import Item
from tracertm.models.link import Link

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _link_to_dict(link: Link, include_items: bool = False) -> dict[str, object]:
    """Convert a Link model to a dictionary."""
    result = {
        "id": link.id,
        "source_id": link.source_item_id,
        "target_id": link.target_item_id,
        "link_type": link.link_type,
        "metadata": link.link_metadata,
        "created_at": link.created_at.isoformat() if link.created_at else None,
    }
    if include_items:
        src = getattr(link, "source", None)
        tgt = getattr(link, "target", None)
        if src is not None:
            result["source"] = {
                "id": getattr(src, "id", None),
                "external_id": getattr(src, "external_id", None),
                "title": getattr(src, "title", None),
                "view": getattr(src, "view", None),
            }
        if tgt is not None:
            result["target"] = {
                "id": getattr(tgt, "id", None),
                "external_id": getattr(tgt, "external_id", None),
                "title": getattr(tgt, "title", None),
                "view": getattr(tgt, "view", None),
            }
    return result


def _resolve_item_id(session: Session, project_id: str, item_ref: str) -> str | None:
    """Resolve an item reference (ID or external_id prefix) to an actual ID."""
    # Try exact ID match
    item = (
        session
        .query(Item.id)
        .filter(
            Item.project_id == project_id,
            Item.id == item_ref,
            Item.deleted_at.is_(None),
        )
        .first()
    )
    if item:
        return item[0]

    # Try external_id prefix match
    item = (
        session
        .query(Item.id)
        .filter(
            Item.project_id == project_id,
            Item.external_id.ilike(f"{item_ref}%"),
            Item.deleted_at.is_(None),
        )
        .first()
    )
    return item[0] if item else None


@mcp.tool(description="Create a traceability link between items")
async def create_link(
    source_id: str,
    target_id: str,
    link_type: str,
    metadata: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Create a link between two items.

    Args:
        source_id: Source item ID or external_id (required)
        target_id: Target item ID or external_id (required)
        link_type: Type of link (satisfies, implements, tests, depends_on, etc.)
        metadata: Optional metadata for the link

    Returns:
        Created link details
    """
    await asyncio.sleep(0)
    if not source_id or not target_id or not link_type:
        msg = "source_id, target_id, and link_type are required."
        raise ToolError(msg)

    project_id = require_project()

    with get_session() as session:
        # Resolve item references
        resolved_source = _resolve_item_id(session, project_id, source_id)
        resolved_target = _resolve_item_id(session, project_id, target_id)

        if not resolved_source:
            msg = f"Source item not found: {source_id}"
            raise ToolError(msg)
        if not resolved_target:
            msg = f"Target item not found: {target_id}"
            raise ToolError(msg)

        # Check for duplicate link
        existing = (
            session
            .query(Link)
            .filter(
                Link.project_id == project_id,
                Link.source_item_id == resolved_source,
                Link.target_item_id == resolved_target,
                Link.link_type == link_type,
            )
            .first()
        )
        if existing:
            msg = f"Link already exists: {source_id} -> {target_id} ({link_type})"
            raise ToolError(msg)

        link = Link(
            id=str(uuid.uuid4()),
            project_id=project_id,
            source_id=resolved_source,
            target_id=resolved_target,
            link_type=link_type,
            link_metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
        session.add(link)
        session.commit()

        return wrap_success(_link_to_dict(link), "create", ctx)  # type: ignore[return-value]


@mcp.tool(description="List links with optional filters")
async def list_links(
    item_id: str | None = None,
    link_type: str | None = None,
    limit: int = 50,
    ctx: object | None = None,
) -> dict[str, object]:
    """List links with optional filters.

    Args:
        item_id: Filter links involving this item (as source or target)
        link_type: Filter by link type
        limit: Maximum results (default 50, max 500)

    Returns:
        List of matching links
    """
    await asyncio.sleep(0)
    project_id = require_project()
    limit = min(limit, 500)

    with get_session() as session:
        query = session.query(Link).filter(Link.project_id == project_id)

        if item_id:
            resolved_id = _resolve_item_id(session, project_id, item_id)
            if resolved_id:
                query = query.filter((Link.source_item_id == resolved_id) | (Link.target_item_id == resolved_id))
            else:
                # No matches
                return wrap_success({"links": [], "count": 0}, "list", ctx)  # type: ignore[return-value]

        if link_type:
            query = query.filter(Link.link_type == link_type)

        links = query.limit(limit).all()

        return wrap_success(  # type: ignore[return-value]
            {
                "links": [_link_to_dict(lnk) for lnk in links],
                "count": len(links),
                "limit": limit,
            },
            "list",
            ctx,
        )


@mcp.tool(description="Show links for an item grouped by direction")
async def show_links(
    item_id: str,
    view: str | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Show all links for an item, grouped as incoming and outgoing.

    Args:
        item_id: Item ID or external_id (required)
        view: Optional filter for linked items' view

    Returns:
        Links grouped by direction with item details
    """
    await asyncio.sleep(0)
    if not item_id:
        msg = "item_id is required."
        raise ToolError(msg)

    project_id = require_project()

    with get_session() as session:
        resolved_id = _resolve_item_id(session, project_id, item_id)
        if not resolved_id:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        # Get the item
        item = session.query(Item).filter(Item.id == resolved_id).first()
        if not item:
            msg = f"Item not found: {item_id}"
            raise ToolError(msg)

        # Outgoing links (this item is source)
        outgoing_query = (
            session
            .query(Link)
            .join(Item, Link.target_item_id == Item.id)
            .filter(
                Link.project_id == project_id,
                Link.source_item_id == resolved_id,
                Item.deleted_at.is_(None),
            )
        )
        if view:
            outgoing_query = outgoing_query.filter(Item.view == view.upper())
        outgoing = outgoing_query.all()

        # Incoming links (this item is target)
        incoming_query = (
            session
            .query(Link)
            .join(Item, Link.source_item_id == Item.id)
            .filter(
                Link.project_id == project_id,
                Link.target_item_id == resolved_id,
                Item.deleted_at.is_(None),
            )
        )
        if view:
            incoming_query = incoming_query.filter(Item.view == view.upper())
        incoming = incoming_query.all()

        # Build result with item details
        def link_with_item(link: Link, direction: str) -> dict[str, object]:
            other_id = link.target_item_id if direction == "outgoing" else link.source_item_id
            other = session.query(Item).filter(Item.id == other_id).first()
            return {
                "link_id": link.id,
                "link_type": link.link_type,
                "direction": direction,
                "item": {
                    "id": other.id if other else other_id,
                    "external_id": other.external_id if other else None,
                    "title": other.title if other else None,
                    "view": other.view if other else None,
                    "status": other.status if other else None,
                },
            }

        return wrap_success(  # type: ignore[return-value]
            {
                "item": {
                    "id": item.id,
                    "external_id": item.external_id,
                    "title": item.title,
                    "view": item.view,
                },
                "outgoing": [link_with_item(lnk, "outgoing") for lnk in outgoing],
                "incoming": [link_with_item(lnk, "incoming") for lnk in incoming],
                "outgoing_count": len(outgoing),
                "incoming_count": len(incoming),
            },
            "show",
            ctx,
        )


__all__ = [
    "create_link",
    "list_links",
    "show_links",
]
