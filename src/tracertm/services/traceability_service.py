"""Traceability service for TraceRTM."""

from dataclasses import dataclass
from typing import Any

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

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def create_link(
        self,
        project_id: str,
        source_item_id: str,
        target_item_id: str,
        link_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> Link:
        """Create a traceability link with validation."""
        # Validate both items exist
        source = await self.items.get_by_id(source_item_id)
        target = await self.items.get_by_id(target_item_id)

        if not source:
            raise ValueError(f"Source item {source_item_id} not found")
        if not target:
            raise ValueError(f"Target item {target_item_id} not found")

        # Create link
        return await self.links.create(
            project_id=project_id,
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            link_type=link_type,
            link_metadata=metadata,
        )

    async def generate_matrix(
        self,
        project_id: str,
        source_view: str,
        target_view: str,
    ) -> TraceabilityMatrix:
        """Generate traceability matrix between two views."""
        # Get all items in both views
        source_items = await self.items.get_by_view(project_id, source_view)
        await self.items.get_by_view(project_id, target_view)

        # Get all links between these items
        all_links = []
        linked_source_ids: set[str] = set()

        for source_item in source_items:
            item_links = await self.links.get_by_source(source_item.id)
            for link in item_links:
                # Check if target is in target_view
                target = await self.items.get_by_id(link.target_item_id)
                if target and target.view == target_view:
                    all_links.append(
                        {
                            "source_id": source_item.id,
                            "source_title": source_item.title,
                            "target_id": target.id,
                            "target_title": target.title,
                            "link_type": link.link_type,
                        }
                    )
                    linked_source_ids.add(source_item.id)

        # Calculate coverage
        coverage = (
            len(linked_source_ids) / len(source_items) * 100 if source_items else 0
        )

        # Find gaps (source items without links)
        gaps = [
            {"id": item.id, "title": item.title}
            for item in source_items
            if item.id not in linked_source_ids
        ]

        return TraceabilityMatrix(
            source_view=source_view,
            target_view=target_view,
            links=all_links,
            coverage_percentage=coverage,
            gaps=gaps,
        )

    async def analyze_impact(
        self,
        item_id: str,
        max_depth: int = 2,
    ) -> ImpactAnalysis:
        """Analyze impact of changing an item."""
        # Get directly affected items (items linked from this one)
        direct_links = await self.links.get_by_source(item_id)
        directly_affected = []

        for link in direct_links:
            target = await self.items.get_by_id(link.target_item_id)
            if target:
                directly_affected.append(target)

        # Get indirectly affected (recursive, up to max_depth)
        indirectly_affected = []
        if max_depth > 1:
            visited = {item_id}
            for direct_item in directly_affected:
                visited.add(direct_item.id)

            for direct_item in directly_affected:
                indirect = await self._get_downstream_items(
                    direct_item.id,
                    visited,
                    max_depth - 1,
                )
                indirectly_affected.extend(indirect)

        return ImpactAnalysis(
            item_id=item_id,
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
            if link.target_item_id not in visited:
                visited.add(link.target_item_id)
                target = await self.items.get_by_id(link.target_item_id)
                if target:
                    downstream.append(target)
                    # Recurse
                    indirect = await self._get_downstream_items(
                        target.id,
                        visited,
                        depth - 1,
                    )
                    downstream.extend(indirect)

        return downstream
