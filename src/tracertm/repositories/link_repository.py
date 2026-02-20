"""Link repository for TraceRTM."""

import uuid
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.link import Link


class LinkRepository:
    """Repository for Link CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str | uuid.UUID,
        source_item_id: str | uuid.UUID,
        target_item_id: str | uuid.UUID,
        link_type: str,
        graph_id: str | None = None,
        link_metadata: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Link:
        """Create new link."""
        if graph_id is None:
            from sqlalchemy import select

            from tracertm.models.graph import Graph
            from tracertm.models.item_view import ItemView
            from tracertm.models.view import View

            graph_result = await self.session.execute(
                select(Graph.id)
                .join(View, View.name == Graph.graph_type)
                .join(ItemView, ItemView.view_id == View.id)
                .where(
                    Graph.project_id == project_id,
                    ItemView.item_id == source_item_id,
                    ItemView.is_primary.is_(True),
                )
                .limit(1),
            )
            graph_id = graph_result.scalar_one_or_none()

        if graph_id is None:
            from sqlalchemy import select

            from tracertm.models.graph import Graph

            fallback = await self.session.execute(
                select(Graph.id).where(Graph.project_id == project_id, Graph.graph_type == "default"),
            )
            graph_id = fallback.scalar_one_or_none()

        if graph_id is None:
            msg = "graph_id is required and could not be resolved"
            raise ValueError(msg)

        # Handle both parameter names for compatibility
        final_metadata = link_metadata or metadata or {}
        link = Link(
            id=str(uuid4()),
            project_id=str(project_id) if isinstance(project_id, uuid.UUID) else project_id,
            graph_id=graph_id,
            source_item_id=str(source_item_id) if isinstance(source_item_id, uuid.UUID) else source_item_id,
            target_item_id=str(target_item_id) if isinstance(target_item_id, uuid.UUID) else target_item_id,
            link_type=link_type,
            link_metadata=final_metadata,
        )
        self.session.add(link)
        await self.session.flush()
        await self.session.refresh(link)
        return link

    async def get_by_id(self, link_id: str | uuid.UUID) -> Link | None:
        """Get link by ID."""
        result = await self.session.execute(select(Link).where(Link.id == link_id))
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: str | uuid.UUID, graph_id: str | None = None) -> list[Link]:
        """Get all links in a project."""
        # Links can be in a project if either source or target item is in that project
        query = select(Link).where(Link.project_id == project_id)
        if graph_id:
            query = query.where(Link.graph_id == graph_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_source(self, source_item_id: str | uuid.UUID, graph_id: str | None = None) -> list[Link]:
        """Get all links from source item."""
        query = select(Link).where(Link.source_item_id == source_item_id)
        if graph_id:
            query = query.where(Link.graph_id == graph_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_target(self, target_item_id: str | uuid.UUID, graph_id: str | None = None) -> list[Link]:
        """Get all links to target item."""
        query = select(Link).where(Link.target_item_id == target_item_id)
        if graph_id:
            query = query.where(Link.graph_id == graph_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_item(self, item_id: str | uuid.UUID, graph_id: str | None = None) -> list[Link]:
        """Get all links connected to item (source or target)."""
        query = select(Link).where((Link.source_item_id == item_id) | (Link.target_item_id == item_id))
        if graph_id:
            query = query.where(Link.graph_id == graph_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete(self, link_id: str | uuid.UUID) -> bool:
        """Delete link."""
        result = await self.session.execute(delete(Link).where(Link.id == link_id))
        return getattr(result, "rowcount", 0) > 0

    async def delete_by_item(self, item_id: str | uuid.UUID) -> int:
        """Delete all links connected to item."""
        result = await self.session.execute(
            delete(Link).where((Link.source_item_id == item_id) | (Link.target_item_id == item_id)),
        )
        return getattr(result, "rowcount", 0)

    async def get_all(self) -> list[Link]:
        """Get all links."""
        result = await self.session.execute(select(Link))
        return list(result.scalars().all())

    async def get_by_type(self, link_type: str) -> list[Link]:
        """Get all links of a specific type."""
        result = await self.session.execute(select(Link).where(Link.link_type == link_type))
        return list(result.scalars().all())
