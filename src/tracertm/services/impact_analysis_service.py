"""Impact analysis service for TraceRTM."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.item import Item

# Minimum path length to derive parent (path[-2])
_MIN_PATH_LEN_FOR_PARENT = 2


@dataclass
class ImpactNode:
    """Node in impact analysis graph."""

    item: Item
    depth: int
    path: list[str]  # Path from root to this node
    link_type: str | None = None


@dataclass
class ImpactAnalysisResult:
    """Result of impact analysis."""

    root_item_id: str
    root_item_title: str
    total_affected: int
    max_depth_reached: int
    affected_by_depth: dict[int, int]  # depth -> count
    affected_by_view: dict[str, int]  # view -> count
    affected_items: list[dict[str, Any]]
    critical_paths: list[list[str]]  # Paths to leaf nodes


class ImpactAnalysisService:
    """Service for impact analysis operations using BFS algorithm.

    Functional Requirements:
    - FR-RPT-003

    User Stories:
    - US-GRAPH-003

    Epics:
    - EPIC-006
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def _forward_bfs_step(
        self,
        current_id: str,
        depth: int,
        path: list[str],
        link_type: str | None,
        link_types: list[str] | None,
    ) -> tuple[ImpactNode | None, list[tuple[str, int, list[str], str | None]]]:
        """Process one forward BFS step; return (node or None, next queue entries)."""
        item = await self.items.get_by_id(current_id)
        if not item:
            return None, []
        node = ImpactNode(item=item, depth=depth, path=path, link_type=link_type) if depth > 0 else None
        links = await self.links.get_by_source(current_id)
        next_entries = []
        for link in links:
            if link_types and link.link_type not in link_types:
                continue
            next_entries.append((
                link.target_item_id,
                depth + 1,
                [*path, link.target_item_id],
                link.link_type,
            ))
        return node, next_entries

    async def _bfs_impact(
        self,
        item_id: str,
        max_depth: int,
        max_items: int = 1000,
        link_types: list[str] | None = None,
    ) -> tuple[list[ImpactNode], str]:
        """BFS from item_id along outgoing links; returns (impact_nodes, root_title)."""
        root_item = await self.items.get_by_id(item_id)
        if not root_item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        visited: set[str] = set()
        impact_nodes: list[ImpactNode] = []
        queue = deque([(item_id, 0, [item_id], None)])

        while queue and len(impact_nodes) < max_items:
            current_id, depth, path, link_type = queue.popleft()
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)

            node, next_entries = await self._forward_bfs_step(current_id, depth, path, link_type, link_types)
            if node is not None:
                impact_nodes.append(node)
                if len(impact_nodes) >= max_items:
                    break
            for entry in next_entries:
                if entry[0] not in visited:
                    queue.append(entry)

        return impact_nodes, root_item.title

    def _build_impact_result(
        self,
        item_id: str,
        root_title: str,
        impact_nodes: list[ImpactNode],
    ) -> ImpactAnalysisResult:
        """Build ImpactAnalysisResult from impact nodes."""
        affected_by_depth: dict[int, int] = {}
        affected_by_view: dict[str, int] = {}
        for node in impact_nodes:
            affected_by_depth[node.depth] = affected_by_depth.get(node.depth, 0) + 1
            affected_by_view[node.item.view] = affected_by_view.get(node.item.view, 0) + 1
        critical_paths = self._find_critical_paths(impact_nodes)
        return ImpactAnalysisResult(
            root_item_id=item_id,
            root_item_title=root_title,
            total_affected=len(impact_nodes),
            max_depth_reached=max(
                (node.depth for node in impact_nodes),
                default=0,
            ),
            affected_by_depth=affected_by_depth,
            affected_by_view=affected_by_view,
            affected_items=[
                {
                    "id": node.item.id,
                    "title": node.item.title,
                    "view": node.item.view,
                    "item_type": node.item.item_type,
                    "status": node.item.status,
                    "depth": node.depth,
                    "path": node.path,
                    "link_type": node.link_type,
                }
                for node in impact_nodes
            ],
            critical_paths=critical_paths,
        )

    async def analyze_impact(
        self,
        item_id: str,
        max_depth: int = 10,
        max_items: int = 1000,
        link_types: list[str] | None = None,
    ) -> ImpactAnalysisResult:
        """Analyze impact of changing an item using BFS.

        Args:
            item_id: ID of the item to analyze
            max_depth: Maximum depth to traverse (default: 10)
            max_items: Maximum total items to include in analysis (default: 1000)
            link_types: Optional list of link types to follow (default: all)

        Returns:
            ImpactAnalysisResult with complete impact analysis
        """
        impact_nodes, root_title = await self._bfs_impact(item_id, max_depth, max_items, link_types)
        return self._build_impact_result(item_id, root_title, impact_nodes)

    def _find_critical_paths(self, nodes: list[ImpactNode]) -> list[list[str]]:
        """Find critical paths (paths to leaf nodes)."""
        # Build adjacency list
        children: dict[str, set[str]] = {}
        for node in nodes:
            if len(node.path) >= _MIN_PATH_LEN_FOR_PARENT:
                parent = node.path[-2]
                if parent not in children:
                    children[parent] = set()
                children[parent].add(str(node.item.id))

        # Find leaf nodes (nodes with no children)
        return [node.path for node in nodes if node.item.id not in children]

    async def _reverse_bfs_step(
        self,
        current_id: str,
        depth: int,
        path: list[str],
        link_type: str | None,
    ) -> tuple[ImpactNode | None, list[tuple[str, int, list[str], str | None]]]:
        """Process one reverse BFS step: load item and links; return (node or None, next queue entries)."""
        item = await self.items.get_by_id(current_id)
        if not item:
            return None, []
        node = ImpactNode(item=item, depth=depth, path=path, link_type=link_type) if depth > 0 else None
        links = await self.links.get_by_target(current_id)
        next_entries = [
            (link.source_item_id, depth + 1, [*path, link.source_item_id], link.link_type) for link in links
        ]
        return node, next_entries

    async def _bfs_reverse_impact(
        self,
        item_id: str,
        max_depth: int,
        max_items: int = 1000,
    ) -> tuple[list[ImpactNode], str]:
        """BFS from item_id along incoming links; returns (impact_nodes, root_title)."""
        root_item = await self.items.get_by_id(item_id)
        if not root_item:
            msg = f"Item {item_id} not found"
            raise ValueError(msg)

        visited: set[str] = set()
        impact_nodes: list[ImpactNode] = []
        queue = deque([(item_id, 0, [item_id], None)])

        while queue and len(impact_nodes) < max_items:
            current_id, depth, path, link_type = queue.popleft()
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)

            node, next_entries = await self._reverse_bfs_step(current_id, depth, path, link_type)
            if node is not None:
                impact_nodes.append(node)
                if len(impact_nodes) >= max_items:
                    break
            for entry in next_entries:
                if entry[0] not in visited:
                    queue.append(entry)

        return impact_nodes, root_item.title

    def _build_reverse_impact_result(
        self,
        item_id: str,
        root_title: str,
        impact_nodes: list[ImpactNode],
    ) -> ImpactAnalysisResult:
        """Build ImpactAnalysisResult from reverse-impact nodes."""
        affected_by_depth: dict[int, int] = {}
        affected_by_view: dict[str, int] = {}
        for node in impact_nodes:
            affected_by_depth[node.depth] = affected_by_depth.get(node.depth, 0) + 1
            affected_by_view[node.item.view] = affected_by_view.get(node.item.view, 0) + 1
        critical_paths = self._find_critical_paths(impact_nodes)
        return ImpactAnalysisResult(
            root_item_id=item_id,
            root_item_title=root_title,
            total_affected=len(impact_nodes),
            max_depth_reached=max((node.depth for node in impact_nodes), default=0),
            affected_by_depth=affected_by_depth,
            affected_by_view=affected_by_view,
            affected_items=[
                {
                    "id": node.item.id,
                    "title": node.item.title,
                    "view": node.item.view,
                    "item_type": node.item.item_type,
                    "status": node.item.status,
                    "depth": node.depth,
                    "path": node.path,
                    "link_type": node.link_type,
                }
                for node in impact_nodes
            ],
            critical_paths=critical_paths,
        )

    async def analyze_reverse_impact(
        self,
        item_id: str,
        max_depth: int = 10,
        max_items: int = 1000,
    ) -> ImpactAnalysisResult:
        """Analyze reverse impact (what depends on this item).

        This finds all items that link TO this item (upstream dependencies).

        Complexity: O(V + E) where V = items, E = links
        """
        impact_nodes, root_title = await self._bfs_reverse_impact(item_id, max_depth, max_items)
        return self._build_reverse_impact_result(item_id, root_title, impact_nodes)
