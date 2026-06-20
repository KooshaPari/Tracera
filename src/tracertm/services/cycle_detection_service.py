"""Cycle detection service for Epic 4 (FR22).

Prevents circular dependencies in depends_on relationships.
"""

from __future__ import annotations

import asyncio
import operator
import uuid
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.models.link import Link

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


class CycleDetectionService:
    """Service for detecting cycles in dependency graphs.

    Functional Requirements:
    - FR-RPT-004

    User Stories:
    - US-GRAPH-004

    Epics:
    - EPIC-006
    """

    def __init__(
        self,
        session: Session | AsyncSession,
        items: ItemRepository | None = None,
        links: LinkRepository | None = None,
    ) -> None:
        """Initialize cycle detection service."""
        self.session = session
        # Accept repository instances for easier testing
        # If not provided, create them (only for AsyncSession)
        if isinstance(session, AsyncSession):
            self.items = items if items is not None else ItemRepository(session)
            self.links = links if links is not None else LinkRepository(session)
        else:
            # For sync Session, rely on passed instances or None
            self.items = items
            self.links = links

    def has_cycle(
        self,
        project_id: str | uuid.UUID,
        source_id: str | uuid.UUID,
        target_id: str | uuid.UUID,
        link_type: str = "depends_on",
    ) -> bool:
        """Check if adding a link would create a cycle (FR22).

        Args:
            project_id: Project ID
            source_id: Source item ID
            target_id: Target item ID
            link_type: Link type (default: depends_on)

        Returns:
            True if adding the link would create a cycle
        """
        if link_type != "depends_on":
            # Only check cycles for depends_on relationships
            return False

        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        sid = str(source_id) if isinstance(source_id, uuid.UUID) else source_id
        tid = str(target_id) if isinstance(target_id, uuid.UUID) else target_id
        # Build dependency graph
        graph = self._build_dependency_graph(pid, link_type)

        # Check if target can reach source (would create cycle)
        return self._can_reach(graph, tid, sid)

    def detect_cycles(
        self,
        project_id: str | uuid.UUID,
        link_type: str = "depends_on",
        link_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Detect all cycles in the dependency graph (sync version).

        Args:
        project_id: Project ID
        link_type: Link type to check (default: depends_on) - used if link_types not provided
        link_types: Optional list of link types to check (overrides link_type)

        Returns:
        Dictionary with cycle information

        Functional Requirements:
        - FR-RPT-004

        User Stories:
        - US-GRAPH-004

        Epics:
        - EPIC-006
        """
        project_id = str(project_id)
        types_to_check = link_types if link_types is not None else [link_type]

        if isinstance(self.session, AsyncSession):
            # Run async graph build in a blocking manner for sync callers
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    graph = {}
                else:
                    graph = loop.run_until_complete(self._build_dependency_graph_async(project_id, types_to_check))
            except RuntimeError:
                graph = asyncio.get_event_loop().run_until_complete(
                    self._build_dependency_graph_async(project_id, types_to_check),
                )
        else:
            graph = self._build_dependency_graph(project_id, link_type)

        cycles = self._find_cycles(graph)
        affected = {node for cycle in cycles for node in cycle}
        severity = "high" if cycles else "none"

        return {
            "has_cycles": len(cycles) > 0,
            "cycle_count": len(cycles),
            "total_cycles": len(cycles),
            "cycles": cycles,
            "affected_items": list(affected),
            "severity": severity,
        }

    async def detect_cycles_async(
        self,
        project_id: str | uuid.UUID,
        link_type: str = "depends_on",
        link_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Detect all cycles in the dependency graph (async version).

        Args:
            project_id: Project ID
            link_type: Link type to check (default: depends_on) - used if link_types not provided
            link_types: Optional list of link types to check (overrides link_type)

        Returns:
            Dictionary with cycle information
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        # Use link_types if provided, otherwise use single link_type
        types_to_check = link_types if link_types is not None else [link_type]

        # Build graph using repositories if available (async)
        if isinstance(self.session, AsyncSession) and self.links is not None:
            graph = await self._build_dependency_graph_async(pid, types_to_check)
        else:
            # Fallback to sync version
            graph = self._build_dependency_graph(pid, link_type)

        cycles = self._find_cycles(graph)
        affected = {node for cycle in cycles for node in cycle}
        severity = "high" if cycles else "none"

        return {
            "has_cycles": len(cycles) > 0,
            "cycle_count": len(cycles),
            "total_cycles": len(cycles),
            "cycles": cycles,
            "affected_items": list(affected),
            "severity": severity,
        }

    def _build_dependency_graph(self, project_id: str, link_type: str) -> dict[str, set[str]]:
        """Build dependency graph from links (sync version)."""
        if isinstance(self.session, AsyncSession):
            # Async sessions are handled in _build_dependency_graph_async; return empty to avoid sync querying
            return {}

        graph: dict[str, set[str]] = {}
        session = cast("Session", self.session)

        try:
            links = (
                session
                .query(Link)
                .filter(
                    Link.project_id == project_id,
                    Link.link_type == link_type,
                )
                .all()
            )
        except OperationalError:
            # Table may not exist yet; treat as no links/no cycles
            return {}

        for link in links:
            src = str(link.source_item_id)
            tgt = str(link.target_item_id)
            if src not in graph:
                graph[src] = set()
            graph[src].add(tgt)
            if tgt not in graph:
                graph[tgt] = set()

        return graph

    async def _build_dependency_graph_async(self, project_id: str, link_types: list[str]) -> dict[str, set[str]]:
        """Build dependency graph from links (async version using repositories)."""
        graph: dict[str, set[str]] = {}

        # Fetch links from repository and build graph
        links = await self.links.get_by_project(project_id)
        for link in links:
            if link.link_type in link_types:
                src = str(link.source_item_id)
                tgt = str(link.target_item_id)
                if src not in graph:
                    graph[src] = set()
                graph[src].add(tgt)
                if tgt not in graph:
                    graph[tgt] = set()

        return graph

    def _can_reach(self, graph: dict[str, set[str]], start: str, target: str) -> bool:
        """Check if target is reachable from start using DFS."""
        if start == target:
            return True

        visited: set[str] = set()
        stack = [start]

        while stack:
            node = stack.pop()
            if node == target:
                return True

            if node in visited:
                continue
            visited.add(node)

            # Add neighbors to stack
            if node in graph:
                stack.extend(neighbor for neighbor in graph[node] if neighbor not in visited)

        return False

    def _find_cycles(self, graph: dict[str, set[str]]) -> list[list[str]]:
        """Find all cycles in the graph using DFS."""
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = [*path[cycle_start:], node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Visit neighbors
            if node in graph:
                for neighbor in graph[node]:
                    dfs(neighbor)

            path.pop()
            rec_stack.remove(node)

        # Check all nodes
        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def detect_missing_dependencies(self, project_id: str | uuid.UUID, link_type: str = "depends_on") -> dict[str, Any]:
        """Detect missing dependencies (items that reference non-existent items) (Story 4.6, FR22).

        Args:
            project_id: Project ID
            link_type: Link type to check (default: depends_on)

        Returns:
            Dictionary with missing dependency information
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        session = cast("Session", self.session)
        # Get all links of the specified type
        links = (
            session
            .query(Link)
            .filter(
                Link.project_id == pid,
                Link.link_type == link_type,
            )
            .all()
        )

        # Get all item IDs in the project
        item_ids = {
            item.id
            for item in session
            .query(Item.id)
            .filter(
                Item.project_id == pid,
                Item.deleted_at.is_(None),
            )
            .all()
        }

        missing_deps = []
        for link in links:
            # Check if source item exists
            if link.source_item_id not in item_ids:
                missing_deps.append({
                    "link_id": link.id,
                    "source_item_id": link.source_item_id,
                    "target_item_id": link.target_item_id,
                    "issue": "source_item_missing",
                })

            # Check if target item exists
            if link.target_item_id not in item_ids:
                missing_deps.append({
                    "link_id": link.id,
                    "source_item_id": link.source_item_id,
                    "target_item_id": link.target_item_id,
                    "issue": "target_item_missing",
                })

        return {
            "has_missing_dependencies": len(missing_deps) > 0,
            "missing_count": len(missing_deps),
            "missing_dependencies": missing_deps,
        }

    def detect_orphans(self, project_id: str | uuid.UUID, link_type: str | None = None) -> dict[str, Any]:
        """Detect orphaned items (items with no links) (Story 4.6, FR22).

        Args:
            project_id: Project ID
            link_type: Optional link type filter (None = all link types)

        Returns:
            Dictionary with orphan information
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        session = cast("Session", self.session)
        # Get all items
        items = (
            session
            .query(Item)
            .filter(
                Item.project_id == pid,
                Item.deleted_at.is_(None),
            )
            .all()
        )

        # Get all linked item IDs
        query = session.query(Link).filter(Link.project_id == pid)
        if link_type:
            query = query.filter(Link.link_type == link_type)

        links = query.all()
        linked_item_ids: set[str] = set()
        for link in links:
            linked_item_ids.add(link.source_item_id)
            linked_item_ids.add(link.target_item_id)

        # Find orphans (items with no links)
        orphans = [
            {
                "item_id": item.id,
                "item_title": item.title,
                "view": item.view,
                "item_type": item.item_type,
                "status": item.status,
            }
            for item in items
            if item.id not in linked_item_ids
        ]

        return {
            "has_orphans": len(orphans) > 0,
            "orphan_count": len(orphans),
            "orphans": orphans,
        }

    def analyze_impact(
        self,
        project_id: str | uuid.UUID,
        item_id: str | uuid.UUID,
        max_depth: int = 10,
        link_type: str = "depends_on",
    ) -> dict[str, Any]:
        """Analyze impact of changing an item (Story 4.6, FR22, NFR-R2).

        Shows all items that would be affected if the given item changes.

        Args:
            project_id: Project ID
            item_id: Item ID to analyze
            max_depth: Maximum depth to traverse
            link_type: Link type to follow (default: depends_on)

        Returns:
            Dictionary with impact analysis
        """
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        iid = str(item_id) if isinstance(item_id, uuid.UUID) else item_id
        sess = cast("Session", self.session)
        # Build reverse dependency graph (what depends on each item)
        graph = self._build_dependency_graph(pid, link_type)
        reverse_graph: dict[str, set[str]] = {}

        # Build reverse graph (target -> sources)
        for source, targets in graph.items():
            for target in targets:
                if target not in reverse_graph:
                    reverse_graph[target] = set()
                reverse_graph[target].add(source)

        # BFS from item_id to find all items that depend on it
        visited: set[str] = set()
        affected_items: list[dict] = []
        queue: list[tuple[str, int, list[str]]] = [(iid, 0, [iid])]

        while queue:
            current_id, depth, path = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)
            # Get item details
            item = sess.query(Item).filter(Item.id == current_id, Item.project_id == pid).first()

            if item and depth > 0:  # Skip root item
                affected_items.append({
                    "item_id": item.id,
                    "item_title": item.title,
                    "view": item.view,
                    "item_type": item.item_type,
                    "status": item.status,
                    "depth": depth,
                    "path": path,
                })

            # Add dependents to queue
            if current_id in reverse_graph:
                queue.extend(
                    (dependent_id, depth + 1, [*path, dependent_id])
                    for dependent_id in reverse_graph[current_id]
                    if dependent_id not in visited
                )

        # Get root item
        root_item = sess.query(Item).filter(Item.id == iid, Item.project_id == pid).first()

        # Group by depth and view
        affected_by_depth: dict[int, int] = {}
        affected_by_view: dict[str, int] = {}

        for affected in affected_items:
            depth = affected["depth"]
            view = affected["view"]
            affected_by_depth[depth] = affected_by_depth.get(depth, 0) + 1
            affected_by_view[view] = affected_by_view.get(view, 0) + 1

        return {
            "root_item_id": item_id,
            "root_item_title": root_item.title if root_item else "Unknown",
            "total_affected": len(affected_items),
            "max_depth_reached": max(affected_items, key=operator.itemgetter("depth"))["depth"]
            if affected_items
            else 0,
            "affected_by_depth": affected_by_depth,
            "affected_by_view": affected_by_view,
            "affected_items": affected_items[:50],  # Limit to first 50 for performance
        }
