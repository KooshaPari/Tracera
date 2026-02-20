"""Advanced traceability service for multi-level analysis."""

import uuid
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

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def find_all_paths(
        self,
        source_id: str | uuid.UUID,
        target_id: str | uuid.UUID,
        max_depth: int = 10,
    ) -> list[TraceabilityPath]:
        """Find all paths between two items."""
        source_id = str(source_id)
        target_id = str(target_id)
        paths = []
        visited: set[str] = set()

        async def dfs(current: str, target: str, path: list[str], depth: int) -> None:
            if depth > max_depth:
                return

            if current == target:
                paths.append(
                    TraceabilityPath(
                        source_id=source_id,
                        target_id=target_id,
                        path=path,
                        distance=len(path) - 1,
                    ),
                )
                return

            # Get outgoing links
            links = await self.links.get_by_source(current)
            for link in links:
                tid = str(link.target_item_id)
                if tid not in visited:
                    visited.add(tid)
                    await dfs(
                        tid,
                        target,
                        [*path, tid],
                        depth + 1,
                    )
                    visited.remove(tid)

        await dfs(source_id, target_id, [source_id], 0)
        return paths

    async def transitive_closure(
        self,
        project_id: str,
    ) -> dict[str, set[str]]:
        """Compute transitive closure of all links."""
        # Get all items; use str ids so closure keys are str
        items = await self.items.query(project_id, {})
        closure: dict[str, set[str]] = {str(item.id): set() for item in items}

        # For each item, find all reachable items
        for item in items:
            visited: set[str] = set()
            item_key = str(item.id)

            async def dfs(
                current_id: str,
                visited_set: set[str] = visited,
                closure_key: str = item_key,
            ) -> None:
                if current_id in visited_set:
                    return
                visited_set.add(current_id)

                links = await self.links.get_by_source(current_id)
                for link in links:
                    tid = str(link.target_item_id)
                    closure[closure_key].add(tid)
                    await dfs(tid, visited_set, closure_key)

            await dfs(str(item.id))

        return closure

    async def bidirectional_impact(
        self,
        entity_id: str | uuid.UUID,
    ) -> dict[str, Any]:
        """Analyze impact in both directions."""
        eid = str(entity_id) if isinstance(entity_id, uuid.UUID) else entity_id
        # Forward impact (what does this affect)
        forward_links = await self.links.get_by_source(eid)
        forward_impact = [link.target_item_id for link in forward_links]

        # Backward impact (what affects this)
        backward_links = await self.links.get_by_target(eid)
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
        cycles: list[list[str]] = []

        for item in items:
            visited: set[str] = set()
            rec_stack: set[str] = set()
            item_id = item.id  # Capture loop variable

            async def dfs(
                current_id: str,
                path: list[str],
                visited_set: set[str] = visited,
                rec_stack_set: set[str] = rec_stack,
            ) -> None:
                visited_set.add(current_id)
                rec_stack_set.add(current_id)
                path.append(current_id)

                links = await self.links.get_by_source(current_id)
                for link in links:
                    tid = str(link.target_item_id)
                    if tid not in visited_set:
                        await dfs(tid, path.copy(), visited_set, rec_stack_set)
                    elif tid in rec_stack_set:
                        # Found cycle
                        cycle_start = path.index(tid)
                        cycle = [*path[cycle_start:], tid]
                        if cycle not in cycles:
                            cycles.append(cycle)

                rec_stack_set.remove(current_id)

            if item_id not in visited:
                await dfs(str(item_id), [])

        return cycles
