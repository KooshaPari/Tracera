"""Impact analysis service for TraceRTM."""

from collections import deque
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


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
    """Service for impact analysis operations using BFS algorithm."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def analyze_impact(
        self,
        item_id: str,
        max_depth: int = 10,
        link_types: list[str] | None = None,
    ) -> ImpactAnalysisResult:
        """
        Analyze impact of changing an item using BFS.

        Args:
            item_id: ID of the item to analyze
            max_depth: Maximum depth to traverse (default: 10)
            link_types: Optional list of link types to follow (default: all)

        Returns:
            ImpactAnalysisResult with complete impact analysis

        Complexity: O(V + E) where V = items, E = links
        """
        # Get root item
        root_item = await self.items.get_by_id(item_id)
        if not root_item:
            raise ValueError(f"Item {item_id} not found")

        visited: set[str] = set()
        impact_nodes: list[ImpactNode] = []
        queue = deque([(item_id, 0, [item_id], None)])

        # BFS traversal
        while queue:
            current_id, depth, path, link_type = queue.popleft()

            # Skip if already visited or max depth exceeded
            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Get item
            item = await self.items.get_by_id(current_id)
            if not item:
                continue

            # Add to impact nodes (skip root)
            if depth > 0:
                impact_nodes.append(
                    ImpactNode(
                        item=item,
                        depth=depth,
                        path=path,
                        link_type=link_type,
                    )
                )

            # Get downstream links
            links = await self.links.get_by_source(current_id)
            for link in links:
                # Filter by link types if specified
                if link_types and link.link_type not in link_types:
                    continue

                if link.target_item_id not in visited:
                    queue.append((
                        link.target_item_id,
                        depth + 1,
                        [*path, link.target_item_id],
                        link.link_type,
                    ))

        # Calculate statistics
        affected_by_depth: dict[int, int] = {}
        affected_by_view: dict[str, int] = {}

        for node in impact_nodes:
            # Count by depth
            affected_by_depth[node.depth] = affected_by_depth.get(node.depth, 0) + 1
            # Count by view
            affected_by_view[node.item.view] = affected_by_view.get(node.item.view, 0) + 1

        # Find critical paths (paths to leaf nodes)
        critical_paths = self._find_critical_paths(impact_nodes)

        return ImpactAnalysisResult(
            root_item_id=item_id,
            root_item_title=root_item.title,
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

    def _find_critical_paths(self, nodes: list[ImpactNode]) -> list[list[str]]:
        """Find critical paths (paths to leaf nodes)."""
        # Build adjacency list
        children: dict[str, set[str]] = {}
        for node in nodes:
            if len(node.path) >= 2:
                parent = node.path[-2]
                if parent not in children:
                    children[parent] = set()
                children[parent].add(str(node.item.id))

        # Find leaf nodes (nodes with no children)
        return [node.path for node in nodes if node.item.id not in children]

    async def analyze_reverse_impact(
        self,
        item_id: str,
        max_depth: int = 10,
    ) -> ImpactAnalysisResult:
        """
        Analyze reverse impact (what depends on this item).

        This finds all items that link TO this item (upstream dependencies).

        Complexity: O(V + E) where V = items, E = links
        """
        # Get root item
        root_item = await self.items.get_by_id(item_id)
        if not root_item:
            raise ValueError(f"Item {item_id} not found")

        visited: set[str] = set()
        impact_nodes: list[ImpactNode] = []
        queue = deque([(item_id, 0, [item_id], None)])

        # BFS traversal (reverse direction)
        while queue:
            current_id, depth, path, link_type = queue.popleft()

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Get item
            item = await self.items.get_by_id(current_id)
            if not item:
                continue

            # Add to impact nodes (skip root)
            if depth > 0:
                impact_nodes.append(
                    ImpactNode(
                        item=item,
                        depth=depth,
                        path=path,
                        link_type=link_type,
                    )
                )

            # Get upstream links (links pointing TO this item)
            links = await self.links.get_by_target(current_id)
            for link in links:
                if link.source_item_id not in visited:
                    queue.append((
                        link.source_item_id,
                        depth + 1,
                        [*path, link.source_item_id],
                        link.link_type,
                    ))

        # Calculate statistics
        affected_by_depth: dict[int, int] = {}
        affected_by_view: dict[str, int] = {}

        for node in impact_nodes:
            affected_by_depth[node.depth] = affected_by_depth.get(node.depth, 0) + 1
            affected_by_view[node.item.view] = affected_by_view.get(node.item.view, 0) + 1

        critical_paths = self._find_critical_paths(impact_nodes)

        return ImpactAnalysisResult(
            root_item_id=item_id,
            root_item_title=root_item.title,
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
