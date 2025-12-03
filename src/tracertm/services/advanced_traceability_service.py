"""Advanced traceability service for multi-level analysis."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


@dataclass
class TraceabilityPath:
    """A path in the traceability graph."""

    source_id: str
    target_id: str
    path: list[str]
    distance: int


@dataclass
class ImpactAnalysis:
    """Impact analysis result."""

    entity_id: str
    direct_impact: list[str]
    indirect_impact: list[str]
    total_impact: int
    impact_depth: int


class AdvancedTraceabilityService:
    """Service for advanced traceability analysis."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def find_all_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10,
    ) -> list[TraceabilityPath]:
        """Find all paths between two items."""
        paths = []
        visited = set()

        async def dfs(current: str, target: str, path: list[str], depth: int):
            if depth > max_depth:
                return

            if current == target:
                paths.append(
                    TraceabilityPath(
                        source_id=source_id,
                        target_id=target_id,
                        path=path,
                        distance=len(path) - 1,
                    )
                )
                return

            # Get outgoing links
            links = await self.links.get_by_source(current)
            for link in links:
                if link.target_item_id not in visited:
                    visited.add(link.target_item_id)
                    await dfs(
                        link.target_item_id,
                        target,
                        [*path, link.target_item_id],
                        depth + 1,
                    )
                    visited.remove(link.target_item_id)

        await dfs(source_id, target_id, [source_id], 0)
        return paths

    async def transitive_closure(
        self,
        project_id: str,
    ) -> dict[str, set[str]]:
        """Compute transitive closure of all links."""
        # Get all items
        items = await self.items.query(project_id, {})
        closure: dict[str, set[str]] = {item.id: set() for item in items}

        # For each item, find all reachable items
        for item in items:
            visited = set()

            async def dfs(current_id: str):
                if current_id in visited:
                    return
                visited.add(current_id)

                links = await self.links.get_by_source(current_id)
                for link in links:
                    closure[item.id].add(link.target_item_id)
                    await dfs(link.target_item_id)

            await dfs(item.id)

        return closure

    async def bidirectional_impact(
        self,
        entity_id: str,
    ) -> dict[str, Any]:
        """Analyze impact in both directions."""
        # Forward impact (what does this affect)
        forward_links = await self.links.get_by_source(entity_id)
        forward_impact = [link.target_item_id for link in forward_links]

        # Backward impact (what affects this)
        backward_links = await self.links.get_by_target(entity_id)
        backward_impact = [link.source_item_id for link in backward_links]

        return {
            "entity_id": entity_id,
            "forward_impact": forward_impact,
            "backward_impact": backward_impact,
            "total_impact": len(forward_impact) + len(backward_impact),
        }

    async def coverage_gaps(
        self,
        project_id: str,
        source_view: str,
        target_view: str,
    ) -> list[str]:
        """Find items in source view with no links to target view."""
        # Get all items in source view
        source_items = await self.items.get_by_view(project_id, source_view)

        gaps = []
        for item in source_items:
            links = await self.links.get_by_source(item.id)

            # Check if any link goes to target view
            has_target_link = False
            for link in links:
                target = await self.items.get_by_id(link.target_item_id)
                if target and target.view == target_view:
                    has_target_link = True
                    break

            if not has_target_link:
                gaps.append(item.id)

        return gaps

    async def circular_dependency_check(
        self,
        project_id: str,
    ) -> list[list[str]]:
        """Find circular dependencies."""
        items = await self.items.query(project_id, {})
        cycles = []

        for item in items:
            visited = set()
            rec_stack = set()

            async def dfs(current_id: str, path: list[str]):
                visited.add(current_id)
                rec_stack.add(current_id)
                path.append(current_id)

                links = await self.links.get_by_source(current_id)
                for link in links:
                    if link.target_item_id not in visited:
                        await dfs(link.target_item_id, path.copy())
                    elif link.target_item_id in rec_stack:
                        # Found cycle
                        cycle_start = path.index(link.target_item_id)
                        cycle = [*path[cycle_start:], link.target_item_id]
                        if cycle not in cycles:
                            cycles.append(cycle)

                rec_stack.remove(current_id)

            if item.id not in visited:
                await dfs(item.id, [])

        return cycles
