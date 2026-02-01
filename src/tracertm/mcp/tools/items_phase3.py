"""
Phase 3 optimized item management MCP tools.

Demonstrates Phase 3 optimizations:
- Connection pooling via DatabaseManager
- Query caching with TTL
- Eager loading to avoid N+1 queries
- Query performance tracking
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastmcp.exceptions import ToolError
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import StaleDataError

from tracertm.mcp.core import mcp
from tracertm.mcp.query_optimizer import QueryOptimizer
from tracertm.mcp.tools.base_async import (
    cached_query,
    get_async_session,
    invalidate_cache,
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


@mcp.tool(description="[PHASE3] Create item with cache invalidation")
async def create_item_phase3(
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
    """Create item with connection pooling and cache invalidation.

    Args:
        title: Item title (required)
        view: View category (FEATURE, REQUIREMENT, TEST, etc.)
        item_type: Specific type within the view
        description: Detailed description
        status: Item status
        priority: Priority level
        owner: Owner/assignee
        parent_id: Parent item ID
        metadata: Additional metadata

    Returns:
        Created item details
    """
    project_id = require_project()

    if not title or not view or not item_type:
        raise ToolError("title, view, and item_type are required.")

    view = view.upper()

    async with get_async_session() as session:
        # Generate external ID
        count_query = select(func.count(Item.id)).where(
            Item.project_id == project_id,
            Item.view == view,
        )
        result = await session.execute(count_query)
        count = result.scalar()
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

        # Invalidate caches
        invalidate_cache(f"item_query_{project_id}")
        invalidate_cache(f"item_view_{project_id}_{view}")

        return wrap_success(_item_to_dict(item), "create_phase3", ctx)


@mcp.tool(description="[PHASE3] Get item with eager loading")
async def get_item_phase3(
    item_id: str,
    include_links: bool = True,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Get item with optimized eager loading.

    Args:
        item_id: Item ID or external ID prefix
        include_links: Include source/target links

    Returns:
        Item details with relationships
    """
    if not item_id:
        raise ToolError("item_id is required.")

    project_id = require_project()

    async def _fetch_item():
        async with get_async_session() as session:
            if include_links:
                query = (
                    select(Item)
                    .where(
                        Item.project_id == project_id,
                        Item.id == item_id,
                        Item.deleted_at.is_(None),
                    )
                    .options(
                        selectinload(Item.source_links),
                        selectinload(Item.target_links),
                    )
                )
            else:
                query = select(Item).where(
                    Item.project_id == project_id,
                    Item.id == item_id,
                    Item.deleted_at.is_(None),
                )

            result = await session.execute(query)
            item = result.scalar_one_or_none()

            if not item:
                query = select(Item).where(
                    Item.project_id == project_id,
                    Item.external_id.ilike(f"{item_id}%"),
                    Item.deleted_at.is_(None),
                )
                result = await session.execute(query)
                item = result.scalar_one_or_none()

            return item

    item = await cached_query(
        f"item_get_{project_id}",
        _fetch_item,
        ttl=300,
        item_id=item_id,
        include_links=include_links,
    )

    if not item:
        raise ToolError(f"Item not found: {item_id}")

    result = _item_to_dict(item)

    if include_links:
        result["source_links_count"] = len(item.source_links) if item.source_links else 0
        result["target_links_count"] = len(item.target_links) if item.target_links else 0

    return wrap_success(result, "get_phase3", ctx)


@mcp.tool(description="[PHASE3] Query items with caching")
async def query_items_phase3(
    view: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    limit: int = 50,
    include_links: bool = False,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """Query items with result caching and eager loading.

    Args:
        view: Filter by view
        item_type: Filter by item type
        status: Filter by status
        owner: Filter by owner
        limit: Maximum results (max 500)
        include_links: Eager load links

    Returns:
        List of matching items
    """
    project_id = require_project()
    limit = min(limit, 500)

    async def _query_items():
        async with get_async_session() as session:
            if include_links:
                items = await QueryOptimizer.get_items_with_links(
                    session,
                    project_id,
                    view=view,
                    item_type=item_type,
                    status=status,
                    limit=limit,
                )
            else:
                query = select(Item).where(
                    Item.project_id == project_id,
                    Item.deleted_at.is_(None),
                )

                if view:
                    query = query.where(Item.view == view.upper())
                if item_type:
                    query = query.where(Item.item_type == item_type)
                if status:
                    query = query.where(Item.status == status)
                if owner:
                    query = query.where(Item.owner == owner)

                query = query.limit(limit)
                result = await session.execute(query)
                items = result.scalars().all()

            return items

    items = await cached_query(
        f"item_query_{project_id}",
        _query_items,
        ttl=300,
        view=view,
        item_type=item_type,
        status=status,
        owner=owner,
        limit=limit,
        include_links=include_links,
    )

    return wrap_success(
        {
            "items": [_item_to_dict(i) for i in items],
            "count": len(items),
            "limit": limit,
        },
        "query_phase3",
        ctx,
    )


@mcp.tool(description="[PHASE3] Get database metrics")
async def get_db_metrics_phase3(ctx: Any | None = None) -> dict[str, Any]:
    """Get database and cache performance metrics."""
    from tracertm.mcp.cache import get_query_cache
    from tracertm.mcp.database_manager import get_database_manager

    db_manager = await get_database_manager()
    cache = get_query_cache()

    health = await db_manager.health_check()
    pool_status = await db_manager.get_pool_status()
    cache_stats = cache.get_stats()

    return wrap_success(
        {
            "database": health,
            "pool": pool_status,
            "cache": cache_stats,
        },
        "db_metrics_phase3",
        ctx,
    )


__all__ = [
    "create_item_phase3",
    "get_item_phase3",
    "query_items_phase3",
    "get_db_metrics_phase3",
]
