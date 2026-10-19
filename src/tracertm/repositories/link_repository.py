"""Link repository for TraceRTM."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.link import Link


class LinkRepository:
    """Repository for trace-link graph queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_source(
        self,
        source_item_id: str | uuid.UUID,
        graph_id: str | None = None,
    ) -> list[Link]:
        """Return outbound links from the given source item."""
        stmt = select(Link).where(Link.source_item_id == source_item_id)
        if graph_id is not None:
            stmt = stmt.where(Link.graph_id == graph_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_target(
        self,
        target_item_id: str | uuid.UUID,
        graph_id: str | None = None,
    ) -> list[Link]:
        """Return inbound links to the given target item."""
        stmt = select(Link).where(Link.target_item_id == target_item_id)
        if graph_id is not None:
            stmt = stmt.where(Link.graph_id == graph_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
