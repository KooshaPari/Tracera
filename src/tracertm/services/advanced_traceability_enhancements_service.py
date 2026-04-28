"""Service for advanced traceability enhancements."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


class AdvancedTraceabilityEnhancementsService:
    """Service for advanced traceability features."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def detect_circular_dependencies(
        self,
        project_id: str,
    ) -> dict[str, Any]:
        """Detect circular dependencies in the project."""
        items = await self.items.query(project_id, {})
        cycles = []

        for item in items:
            visited: set[str] = set()
            rec_stack: set[str] = set()

            if self._has_cycle(str(item.id), visited, rec_stack, items):
                cycles.append(str(item.id))

        return {
            "project_id": project_id,
            "has_cycles": len(cycles) > 0,
            "cycle_count": len(cycles),
            "items_in_cycles": cycles,
        }

    def _has_cycle(self, item_id: str, visited: set[Any], rec_stack: set[Any], items: list[object]) -> bool:
        """Check if item has cycle using DFS."""
        visited.add(item_id)
        rec_stack.add(item_id)

        # Find outgoing links
        for item in items:
            if hasattr(item, "id") and item.id == item_id:
                for link in getattr(item, "outgoing_links", []):
                    target_id = link.target_item_id if hasattr(link, "target_item_id") else None

                    if target_id not in visited:
                        if self._has_cycle(target_id, visited, rec_stack, items):
                            return True
                    elif target_id in rec_stack:
                        return True

        rec_stack.remove(item_id)
        return False

    async def coverage_gap_analysis(
        self,
        project_id: str,
        source_view: str,
        target_view: str,
    ) -> dict[str, Any]:
        """Analyze coverage gaps between two views."""
        items = await self.items.query(project_id, {})

        source_items = [i for i in items if hasattr(i, "view") and i.view == source_view]
        target_items = [i for i in items if hasattr(i, "view") and i.view == target_view]

        covered = 0
        uncovered = []

        for source in source_items:
            has_link = False
            for target in target_items:
                # Check if there's a link
                if hasattr(source, "outgoing_links"):
                    for link in source.outgoing_links:
                        if hasattr(link, "target_item_id") and link.target_item_id == target.id:
                            has_link = True
                            break

            if has_link:
                covered += 1
            else:
                uncovered.append(source.id)

        coverage_percent = (covered / len(source_items) * 100) if source_items else 0

        return {
            "source_view": source_view,
            "target_view": target_view,
            "total_source_items": len(source_items),
            "covered_items": covered,
            "uncovered_items": len(uncovered),
            "coverage_percent": coverage_percent,
            "uncovered_item_ids": uncovered,
        }

    async def bidirectional_link_analysis(
        self,
        project_id: str,
        item_id: str,
    ) -> dict[str, Any]:
        """Analyze bidirectional links for an item."""
        item = await self.items.get_by_id(item_id)

        if not item:
            return {"error": "Item not found"}

        # Get incoming links
        incoming: list[str] = []
        all_items = await self.items.query(project_id, {})

        for other_item in all_items:
            if hasattr(other_item, "outgoing_links"):
                incoming.extend(
                    {
                        "source_id": other_item.id,
                        "link_type": (link.link_type if hasattr(link, "link_type") else "unknown"),
                    }
                    for link in getattr(other_item, "outgoing_links", [])
                    if hasattr(link, "target_item_id") and link.target_item_id == item_id
                )

        # Get outgoing links
        outgoing = [
            {
                "target_id": (link.target_item_id if hasattr(link, "target_item_id") else None),
                "link_type": (link.link_type if hasattr(link, "link_type") else "unknown"),
            }
            for link in getattr(item, "outgoing_links", [])
        ]

        return {
            "item_id": item_id,
            "incoming_links": len(incoming),
            "outgoing_links": len(outgoing),
            "incoming": incoming,
            "outgoing": outgoing,
            "total_connections": len(incoming) + len(outgoing),
        }

    async def traceability_matrix_generation(
        self,
        project_id: str,
        source_view: str,
        target_view: str,
    ) -> dict[str, Any]:
        """Generate traceability matrix between two views."""
        items = await self.items.query(project_id, {})

        source_items = [i for i in items if hasattr(i, "view") and i.view == source_view]
        target_items = [i for i in items if hasattr(i, "view") and i.view == target_view]

        matrix = []

        for source in source_items:
            row = {
                "source_id": source.id,
                "source_title": source.title if hasattr(source, "title") else "Unknown",
                "targets": [],
            }

            for link in getattr(source, "outgoing_links", []):
                target_id = link.target_item_id if hasattr(link, "target_item_id") else None
                if target_id in [t.id for t in target_items]:
                    row.setdefault("targets", [])
                    if isinstance(row["targets"], list):
                        row["targets"].append({
                            "target_id": target_id,
                            "link_type": (link.link_type if hasattr(link, "link_type") else "unknown"),
                        })

            matrix.append(row)

        return {
            "source_view": source_view,
            "target_view": target_view,
            "matrix": matrix,
            "total_rows": len(matrix),
            "total_columns": len(target_items),
        }

    async def impact_propagation_analysis(
        self,
        project_id: str,
        item_id: str,
        max_depth: int = 5,
    ) -> dict[str, Any]:
        """Analyze impact propagation through the dependency graph."""
        item = await self.items.get_by_id(item_id)

        if not item:
            return {"error": "Item not found"}

        # BFS to find all impacted items
        visited: set[str] = set()
        queue = [(item_id, 0)]
        impact_levels = {}

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)
            impact_levels[current_id] = depth

            # Find items that depend on current item
            all_items = await self.items.query(project_id, {})
            to_add = [
                (str(other_item.id), depth + 1)
                for other_item in all_items
                for link in getattr(other_item, "outgoing_links", [])
                if (
                    hasattr(link, "target_item_id")
                    and link.target_item_id == current_id
                    and other_item.id not in visited
                )
            ]
            queue.extend(to_add)

        return {
            "item_id": item_id,
            "total_impacted": len(visited) - 1,
            "impact_levels": impact_levels,
            "max_depth_reached": max(impact_levels.values()) if impact_levels else 0,
        }
