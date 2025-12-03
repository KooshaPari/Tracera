"""Shortest path service for TraceRTM using Dijkstra's algorithm."""

import heapq
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


@dataclass
class PathResult:
    """Result of shortest path calculation."""

    source_id: str
    target_id: str
    path: list[str]  # Item IDs in path
    distance: int  # Number of hops
    link_types: list[str]  # Types of links in path
    exists: bool  # Whether path exists


class ShortestPathService:
    """Service for finding shortest paths using Dijkstra's algorithm."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def find_shortest_path(
        self,
        project_id: str,
        source_id: str,
        target_id: str,
        link_types: list[str] | None = None,
    ) -> PathResult:
        """
        Find shortest path between two items using Dijkstra's algorithm.

        Args:
            project_id: Project ID
            source_id: Source item ID
            target_id: Target item ID
            link_types: Optional list of link types to follow

        Returns:
            PathResult with shortest path information

        Complexity: O((V + E) log V) where V = items, E = links
        """
        # Build adjacency list
        adjacency_list: dict[str, list[tuple[str, str]]] = {}

        # Get all items in project
        items = await self.items.get_by_project(project_id)
        for item in items:
            adjacency_list[str(item.id)] = []

        # Get all links in project
        links = await self.links.get_by_project(project_id)
        for link in links:
            # Filter by link types if specified
            if link_types and link.link_type not in link_types:
                continue

            source = str(link.source_item_id)
            target = str(link.target_item_id)

            if source not in adjacency_list:
                adjacency_list[source] = []

            adjacency_list[source].append((target, link.link_type))

        # Dijkstra's algorithm
        # Initialize distances for all nodes (including target)
        all_nodes = set(adjacency_list.keys())
        for neighbors in adjacency_list.values():
            for neighbor, _ in neighbors:
                all_nodes.add(neighbor)

        distances: dict[str, int] = {node: float("inf") for node in all_nodes}
        distances[source_id] = 0

        previous: dict[str, str | None] = dict.fromkeys(all_nodes)
        link_types_used: dict[str, str] = {}

        # Priority queue: (distance, node)
        pq = [(0, source_id)]
        visited: set = set()

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue

            visited.add(current_node)

            # If we reached the target, we can stop
            if current_node == target_id:
                break

            # Check neighbors
            for neighbor, link_type in adjacency_list.get(current_node, []):
                if neighbor not in visited:
                    new_distance = current_distance + 1

                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current_node
                        link_types_used[neighbor] = link_type
                        heapq.heappush(pq, (new_distance, neighbor))

        # Reconstruct path
        path: list[str] = []
        link_types_path: list[str] = []
        current = target_id

        # Check if path exists first
        path_exists = distances.get(target_id, float("inf")) != float("inf")

        if path_exists:
            while current is not None:
                path.append(current)
                if current in link_types_used:
                    link_types_path.append(link_types_used[current])
                current = previous.get(current)

            path.reverse()
            link_types_path.reverse()

        return PathResult(
            source_id=source_id,
            target_id=target_id,
            path=path if path_exists else [],
            distance=int(distances[target_id]) if path_exists else -1,
            link_types=link_types_path,
            exists=path_exists,
        )

    async def find_all_shortest_paths(
        self,
        project_id: str,
        source_id: str,
        link_types: list[str] | None = None,
    ) -> dict[str, PathResult]:
        """
        Find shortest paths from source to all reachable items.

        Args:
            project_id: Project ID
            source_id: Source item ID
            link_types: Optional list of link types to follow

        Returns:
            Dict mapping target IDs to PathResult objects

        Complexity: O((V + E) log V)
        """
        # Build adjacency list
        adjacency_list: dict[str, list[tuple[str, str]]] = {}

        # Get all items in project
        items = await self.items.get_by_project(project_id)
        for item in items:
            adjacency_list[str(item.id)] = []

        # Get all links in project
        links = await self.links.get_by_project(project_id)
        for link in links:
            # Filter by link types if specified
            if link_types and link.link_type not in link_types:
                continue

            source = str(link.source_item_id)
            target = str(link.target_item_id)

            if source not in adjacency_list:
                adjacency_list[source] = []

            adjacency_list[source].append((target, link.link_type))

        # Dijkstra's algorithm from source
        distances: dict[str, int] = {node: float("inf") for node in adjacency_list}
        distances[source_id] = 0

        previous: dict[str, str | None] = dict.fromkeys(adjacency_list)
        link_types_used: dict[str, str] = {}

        pq = [(0, source_id)]
        visited: set = set()

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue

            visited.add(current_node)

            for neighbor, link_type in adjacency_list.get(current_node, []):
                if neighbor not in visited:
                    new_distance = current_distance + 1

                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current_node
                        link_types_used[neighbor] = link_type
                        heapq.heappush(pq, (new_distance, neighbor))

        # Build results for all items
        results: dict[str, PathResult] = {}

        for target_id in adjacency_list:
            # Reconstruct path
            path: list[str] = []
            link_types_path: list[str] = []
            current = target_id

            while current is not None:
                path.append(current)
                if current in link_types_used:
                    link_types_path.append(link_types_used[current])
                current = previous[current]

            path.reverse()
            link_types_path.reverse()

            path_exists = distances[target_id] != float("inf")

            results[target_id] = PathResult(
                source_id=source_id,
                target_id=target_id,
                path=path if path_exists else [],
                distance=int(distances[target_id]) if path_exists else -1,
                link_types=link_types_path,
                exists=path_exists,
            )

        return results
