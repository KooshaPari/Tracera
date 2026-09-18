"""Item repository for TraceRTM."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item


class ItemRepository:
    """Repository for item lookups used by analysis routes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        item_id: str | uuid.UUID,
        project_id: str | uuid.UUID | None = None,
    ) -> Item | None:
        """Return a non-deleted item by id, optionally scoped to a project."""
        stmt = select(Item).where(Item.id == item_id, Item.deleted_at.is_(None))
        if project_id is not None:
            stmt = stmt.where(Item.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
