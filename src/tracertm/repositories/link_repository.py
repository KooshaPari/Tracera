"""Link repository for TraceRTM."""

from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.link import Link


class LinkRepository:
    """Repository for Link CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        source_item_id: str,
        target_item_id: str,
        link_type: str,
        link_metadata: dict | None = None,
    ) -> Link:
        """Create new link."""
        link = Link(
            id=str(uuid4()),
            project_id=project_id,
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            link_type=link_type,
            link_metadata=link_metadata or {},
        )
        self.session.add(link)
        await self.session.flush()
        await self.session.refresh(link)
        return link

    async def get_by_id(self, link_id: str) -> Link | None:
        """Get link by ID."""
        result = await self.session.execute(select(Link).where(Link.id == link_id))
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: str) -> list[Link]:
        """Get all links in a project."""
        # Links table doesn't have project_id column, so we need to join with items
        from sqlalchemy import text
        result = await self.session.execute(
            text("""
                SELECT DISTINCT l.id, l.source_id, l.target_id, l.link_type, l.created_at, l.metadata
                FROM links l
                INNER JOIN items i1 ON l.source_id = i1.id
                INNER JOIN items i2 ON l.target_id = i2.id
                WHERE (i1.project_id = :project_id OR i2.project_id = :project_id)
                  AND i1.deleted_at IS NULL
                  AND i2.deleted_at IS NULL
                  AND l.deleted_at IS NULL
            """),
            {"project_id": project_id}
        )
        links = []
        for row in result:
            # Create Link object with proper attributes
            link = type('Link', (), {})()  # type: ignore
            link.id = str(row.id)
            link.source_item_id = str(row.source_id)
            link.target_item_id = str(row.target_id)
            link.link_type = row.link_type
            link.link_metadata = row.metadata or {}
            link.created_at = row.created_at
            links.append(link)
        return links

    async def get_by_source(self, source_item_id: str) -> list[Link]:
        """Get all links from source item."""
        result = await self.session.execute(
            select(Link).where(Link.source_item_id == source_item_id)
        )
        return list(result.scalars().all())

    async def get_by_target(self, target_item_id: str) -> list[Link]:
        """Get all links to target item."""
        result = await self.session.execute(
            select(Link).where(Link.target_item_id == target_item_id)
        )
        return list(result.scalars().all())

    async def get_by_item(self, item_id: str) -> list[Link]:
        """Get all links connected to item (source or target)."""
        result = await self.session.execute(
            select(Link).where(
                (Link.source_item_id == item_id) | (Link.target_item_id == item_id)
            )
        )
        return list(result.scalars().all())

    async def delete(self, link_id: str) -> bool:
        """Delete link."""
        result = await self.session.execute(delete(Link).where(Link.id == link_id))
        return result.rowcount > 0

    async def delete_by_item(self, item_id: str) -> int:
        """Delete all links connected to item."""
        result = await self.session.execute(
            delete(Link).where(
                (Link.source_item_id == item_id) | (Link.target_item_id == item_id)
            )
        )
        return result.rowcount

    async def get_all(self) -> list[Link]:
        """Get all links."""
        result = await self.session.execute(select(Link))
        return list(result.scalars().all())

    async def get_by_type(self, link_type: str) -> list[Link]:
        """Get all links of a specific type."""
        result = await self.session.execute(
            select(Link).where(Link.link_type == link_type)
        )
        return list(result.scalars().all())
