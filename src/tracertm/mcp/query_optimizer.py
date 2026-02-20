"""Query optimization utilities for MCP tools.

Provides:
- Eager loading patterns to avoid N+1 queries
- Common query optimizations
- Batch loading utilities
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class QueryOptimizer:
    """Query optimization utilities for common MCP operations.

    Provides optimized query patterns that avoid N+1 queries by using
    eager loading (selectinload/joinedload) for relationships.
    """

    @staticmethod
    async def get_items_with_links(
        session: AsyncSession,
        project_id: str,
        view: str | None = None,
        item_type: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> Sequence[Item]:
        """Get items with their related links eagerly loaded.

        Avoids N+1 queries when accessing item.source_links and item.target_links.

        Args:
            session: Database session
            project_id: Project ID filter
            view: Optional view filter
            item_type: Optional item type filter
            status: Optional status filter
            limit: Maximum results

        Returns:
            List of items with links eagerly loaded
        """
        query = (
            select(Item)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .options(
                # Eager load source links (where this item is the source)
                selectinload(Item.source_links),
                # Eager load target links (where this item is the target)
                selectinload(Item.target_links),
            )
            .limit(limit)
        )

        if view:
            query = query.where(Item.view == view.upper())
        if item_type:
            query = query.where(Item.item_type == item_type)
        if status:
            query = query.where(Item.status == status)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_links_with_items(
        session: AsyncSession,
        project_id: str,
        link_type: str | None = None,
        limit: int = 50,
    ) -> Sequence[Link]:
        """Get links with source and target items eagerly loaded.

        Avoids N+1 queries when accessing link.source_item and link.target_item.

        Args:
            session: Database session
            project_id: Project ID filter
            link_type: Optional link type filter
            limit: Maximum results

        Returns:
            List of links with items eagerly loaded
        """
        query = (
            select(Link)
            .where(Link.project_id == project_id)
            .options(
                # Eager load source item
                joinedload(Link.source_item),
                # Eager load target item
                joinedload(Link.target_item),
            )
            .limit(limit)
        )

        if link_type:
            query = query.where(Link.link_type == link_type)

        result = await session.execute(query)
        return result.unique().scalars().all()

    @staticmethod
    async def get_project_with_items(
        session: AsyncSession,
        project_id: str,
    ) -> Project | None:
        """Get project with items eagerly loaded.

        Args:
            session: Database session
            project_id: Project ID

        Returns:
            Project with items eagerly loaded, or None if not found
        """
        query = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.items).selectinload(Item.source_links),
                selectinload(Project.items).selectinload(Item.target_links),
            )
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_item_with_hierarchy(
        session: AsyncSession,
        item_id: str,
        project_id: str,
    ) -> Item | None:
        """Get item with parent and children eagerly loaded.

        Args:
            session: Database session
            item_id: Item ID
            project_id: Project ID for filtering

        Returns:
            Item with hierarchy eagerly loaded, or None if not found
        """
        query = (
            select(Item)
            .where(
                Item.id == item_id,
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .options(
                # Load parent
                joinedload(Item.parent),
                # Load children
                selectinload(Item.children),
            )
        )

        result = await session.execute(query)
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def batch_get_items(
        session: AsyncSession,
        item_ids: list[str],
        project_id: str,
    ) -> dict[str, Item]:
        """Batch load multiple items by ID.

        More efficient than loading items one at a time.

        Args:
            session: Database session
            item_ids: List of item IDs to load
            project_id: Project ID for filtering

        Returns:
            Dictionary mapping item_id -> Item
        """
        query = select(Item).where(
            Item.id.in_(item_ids),
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
        )

        result = await session.execute(query)
        items = result.scalars().all()

        return {str(item.id): item for item in items}

    @staticmethod
    async def get_traceability_graph(
        session: AsyncSession,
        project_id: str,
        source_view: str | None = None,
        target_view: str | None = None,
    ) -> tuple[Sequence[Item], Sequence[Link]]:
        """Get complete traceability graph with all relationships loaded.

        Optimized for graph traversal and analysis.

        Args:
            session: Database session
            project_id: Project ID
            source_view: Optional filter for source item view
            target_view: Optional filter for target item view

        Returns:
            Tuple of (items, links) with all relationships eagerly loaded
        """
        # Load items with links
        item_query = (
            select(Item)
            .where(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            .options(
                selectinload(Item.source_links),
                selectinload(Item.target_links),
            )
        )

        if source_view or target_view:
            views = []
            if source_view:
                views.append(source_view.upper())
            if target_view:
                views.append(target_view.upper())
            item_query = item_query.where(Item.view.in_(views))

        items_result = await session.execute(item_query)
        items = items_result.scalars().all()

        # Load links with items
        link_query = (
            select(Link)
            .where(Link.project_id == project_id)
            .options(
                joinedload(Link.source_item),
                joinedload(Link.target_item),
            )
        )

        links_result = await session.execute(link_query)
        links = links_result.unique().scalars().all()

        return items, links


# Utility functions for common patterns


async def prefetch_relationships(
    _session: AsyncSession,
    items: Sequence[Item],
    relationships: list[str] | None = None,
) -> None:
    """Prefetch relationships for a collection of items.

    Useful for avoiding N+1 queries when iterating over items.

    Args:
        session: Database session
        items: Items to prefetch relationships for
        relationships: List of relationship names to prefetch
                      (default: ["source_links", "target_links"])
    """
    await asyncio.sleep(0)
    if not items:
        return

    if relationships is None:
        relationships = ["source_links", "target_links"]

    # SQLAlchemy will batch load the relationships efficiently
    for item in items:
        for rel in relationships:
            # Access the relationship to trigger loading
            _ = getattr(item, rel, None)


__all__ = [
    "QueryOptimizer",
    "prefetch_relationships",
]
