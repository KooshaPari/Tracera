"""Traceability service for TraceRTM."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.item import Item
    from tracertm.models.link import Link
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


@dataclass
class TraceabilityMatrix:
    """Traceability matrix showing relationships between items."""

    source_view: str
    target_view: str
    links: list[dict[str, Any]]
    coverage_percentage: float
    gaps: list[dict[str, Any]]  # Items without links


@dataclass
class ImpactAnalysis:
    """Impact analysis for an item change."""

    item_id: str
    directly_affected: list[Item]
    indirectly_affected: list[Item]
    total_impact_count: int


class TraceabilityService:
    """Service for traceability operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def create_link(
        self,
        project_id: str | uuid.UUID,
        source_item_id: str | uuid.UUID,
        target_item_id: str | uuid.UUID,
        link_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> Link:
        """Create a traceability link with validation."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        sid = str(source_item_id) if isinstance(source_item_id, uuid.UUID) else source_item_id
        tid = str(target_item_id) if isinstance(target_item_id, uuid.UUID) else target_item_id
        # Validate both items exist
        source = await self.items.get_by_id(sid)
        target = await self.items.get_by_id(tid)

        if not source:
            msg = f"Source item {source_item_id} not found"
            raise ValueError(msg)
        if not target:
            msg = f"Target item {target_item_id} not found"
            raise ValueError(msg)

        # Create link
        return await self.links.create(
            project_id=pid,
            source_item_id=sid,
            target_item_id=tid,
            link_type=link_type,
            link_metadata=metadata,
        )

    async def generate_matrix(
        self,
        project_id: str | uuid.UUID,
        source_view: str,
        target_view: str,
    ) -> TraceabilityMatrix:
        """Generate traceability matrix between two views."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        # Get all items in both views
        source_items = await self.items.get_by_view(pid, source_view)
        await self.items.get_by_view(pid, target_view)

        # Get all links between these items
        all_links = []
        linked_source_ids: set[str] = set()

        for source_item in source_items:
            item_links = await self.links.get_by_source(str(source_item.id))
            for link in item_links:
                # Check if target is in target_view
                target = await self.items.get_by_id(str(link.target_item_id))
                if target and target.view == target_view:
                    all_links.append({
                        "source_id": str(source_item.id),
                        "source_title": source_item.title,
                        "target_id": str(target.id),
                        "target_title": target.title,
                        "link_type": link.link_type,
                    })
                    linked_source_ids.add(str(source_item.id))

        # Calculate coverage
        coverage = len(linked_source_ids) / len(source_items) * 100 if source_items else 0

        # Find gaps (source items without links)
        gaps = [
            {"id": str(item.id), "title": item.title} for item in source_items if str(item.id) not in linked_source_ids
        ]

        return TraceabilityMatrix(
            source_view=source_view,
            target_view=target_view,
            links=all_links,
            coverage_percentage=coverage,
            gaps=gaps,
        )

    async def find_gaps(
        self,
        project_id: str | uuid.UUID,
        source_view: str,
        target_view: str,
    ) -> list[dict[str, Any]]:
        """Find coverage gaps (source items without links to target view). Returns list of dicts with id, title, status, external_id."""
        matrix = await self.generate_matrix(
            project_id=project_id,
            source_view=source_view,
            target_view=target_view,
        )
        # Enrich gap dicts with status/external_id from items
        result: list[dict[str, Any]] = []
        for gap in matrix.gaps:
            item_id = gap.get("id")
            item = await self.items.get_by_id(str(item_id)) if item_id else None
            result.append({
                "id": item_id,
                "title": gap.get("title"),
                "status": getattr(item, "status", None) if item else None,
                "external_id": getattr(item, "external_id", None) if item else None,
            })
        return result

    async def analyze_impact(
        self,
        item_id: str | uuid.UUID,
        max_depth: int = 2,
    ) -> ImpactAnalysis:
        """Analyze impact of changing an item."""
        iid = str(item_id) if isinstance(item_id, uuid.UUID) else item_id
        # Get directly affected items (items linked from this one)
        direct_links = await self.links.get_by_source(iid)
        directly_affected = []

        for link in direct_links:
            target = await self.items.get_by_id(str(link.target_item_id))
            if target:
                directly_affected.append(target)

        # Get indirectly affected (recursive, up to max_depth)
        indirectly_affected = []
        if max_depth > 1:
            visited = {iid}
            visited.update(str(direct_item.id) for direct_item in directly_affected)

            for direct_item in directly_affected:
                indirect = await self._get_downstream_items(
                    str(direct_item.id),
                    visited,
                    max_depth - 1,
                )
                indirectly_affected.extend(indirect)

        return ImpactAnalysis(
            item_id=iid,
            directly_affected=directly_affected,
            indirectly_affected=indirectly_affected,
            total_impact_count=len(directly_affected) + len(indirectly_affected),
        )

    async def _get_downstream_items(
        self,
        item_id: str,
        visited: set[str],
        depth: int,
    ) -> list[Item]:
        """Recursively get downstream items."""
        if depth <= 0:
            return []

        links = await self.links.get_by_source(item_id)
        downstream = []

        for link in links:
            tid = str(link.target_item_id)
            if tid not in visited:
                visited.add(tid)
                target = await self.items.get_by_id(tid)
                if target:
                    downstream.append(target)
                    # Recurse
                    indirect = await self._get_downstream_items(
                        str(target.id),
                        visited,
                        depth - 1,
                    )
                    downstream.extend(indirect)

        return downstream
