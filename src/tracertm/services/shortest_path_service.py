"""Shortest path service for TraceRTM using Dijkstra's algorithm."""

import heapq
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.services.cache_service import CacheService

logger = logging.getLogger(__name__)


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
    """Service for finding shortest paths using Dijkstra's algorithm with Redis caching."""

    def __init__(self, session: AsyncSession, cache: CacheService | None = None) -> None:
        """Initialize shortest path service.

        Args:
            session: Database session
            cache: Optional cache service for performance optimization
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.cache = cache

    async def find_shortest_path(
        self,
        project_id: str | uuid.UUID,
        source_id: str | uuid.UUID,
        target_id: str | uuid.UUID,
        link_types: list[str] | None = None,
    ) -> PathResult:
        """Find shortest path between two items using Dijkstra's algorithm with caching.

        Caching Strategy:
        - Cache key: tracertm:graph:{project_id}:path:{source_id}:{target_id}:{link_types_key}
        - TTL: 300 seconds (5 minutes)
        - Invalidation: Automatic via event handlers clearing graph:{project_id} prefix
        - Performance: 10x faster with cache (<200ms vs 2s+)

        Args:
            project_id: Project ID
            source_id: Source item ID
            target_id: Target item ID
            link_types: Optional list of link types to follow

        Returns:
            PathResult with shortest path information

        Complexity: O((V + E) log V) where V = items, E = links (without cache)
                   O(1) with cache hit
        """
        project_id = str(project_id)
        source_id = str(source_id)
        target_id = str(target_id)
        # Check cache first
        if self.cache:
            # Generate cache key including link_types filter
            # Format: tracertm:graph:{project_id}:path:{source_id}:{target_id}:{link_types_key}
            # This aligns with event handler invalidation pattern: graph:{project_id}
            link_types_key = ":".join(sorted(link_types)) if link_types else "all"
            cache_key = f"tracertm:graph:{project_id}:path:{source_id}:{target_id}:{link_types_key}"

            try:
                cached = await self.cache.get(cache_key)
                if cached:
                    logger.debug("Cache hit for path %s -> %s in project %s", source_id, target_id, project_id)
                    # Reconstruct PathResult from cached data
                    return PathResult(
                        source_id=cached["source_id"],
                        target_id=cached["target_id"],
                        path=cached["path"],
                        distance=cached["distance"],
                        link_types=cached["link_types"],
                        exists=cached["exists"],
                    )
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Cache read failed for path %s -> %s: %s", source_id, target_id, e)

        # Compute path (existing logic)
        result = await self._compute_path(project_id, source_id, target_id, link_types)

        # Cache for 5 minutes (300 seconds)
        if self.cache and result.exists:
            try:
                cache_data = {
                    "source_id": result.source_id,
                    "target_id": result.target_id,
                    "path": result.path,
                    "distance": result.distance,
                    "link_types": result.link_types,
                    "exists": result.exists,
                }
                link_types_key = ":".join(sorted(link_types)) if link_types else "all"
                cache_key = f"tracertm:graph:{project_id}:path:{source_id}:{target_id}:{link_types_key}"
                await self.cache.set(cache_key, cache_data, ttl_seconds=300)
                logger.debug("Cached path %s -> %s in project %s", source_id, target_id, project_id)
            except (ValueError, TypeError, OperationalError) as e:
                logger.warning("Cache write failed for path %s -> %s: %s", source_id, target_id, e)

        return result

    async def _compute_path(
        self,
        project_id: str | uuid.UUID,
        source_id: str | uuid.UUID,
        target_id: str | uuid.UUID,
        link_types: list[str] | None = None,
    ) -> PathResult:
        """Internal method to compute shortest path using Dijkstra's algorithm.

        Args:
            project_id: Project ID
            source_id: Source item ID
            target_id: Target item ID
            link_types: Optional list of link types to follow

        Returns:
            PathResult with shortest path information
        """
        project_id = str(project_id)
        source_id = str(source_id)
        target_id = str(target_id)
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
            all_nodes.update(neighbor for neighbor, _ in neighbors)

        distances: dict[str, float] = {node: float("inf") for node in all_nodes}
        distances[source_id] = 0

        previous: dict[str, str | None] = dict.fromkeys(all_nodes)
        link_types_used: dict[str, str] = {}

        # Priority queue: (distance, node)
        pq = [(0, source_id)]
        visited: set[Any] = set()

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
            path_current: str | None = current
            while path_current is not None:
                path.append(path_current)
                if path_current in link_types_used:
                    link_types_path.append(link_types_used[path_current])
                path_current = previous.get(path_current)

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
        project_id: str | uuid.UUID,
        source_id: str | uuid.UUID,
        link_types: list[str] | None = None,
    ) -> dict[str, PathResult]:
        """Find shortest paths from source to all reachable items with caching.

        Caching Strategy:
        - Cache key: tracertm:graph:{project_id}:all_paths:{source_id}:{link_types_key}
        - TTL: 300 seconds (5 minutes)
        - Invalidation: Automatic via event handlers clearing graph:{project_id} prefix
        - Performance: 10x faster with cache (<200ms vs 2s+)

        Args:
            project_id: Project ID
            source_id: Source item ID
            link_types: Optional list of link types to follow

        Returns:
            Dict mapping target IDs to PathResult objects

        Complexity: O((V + E) log V) without cache, O(1) with cache hit
        """
        project_id = str(project_id)
        source_id = str(source_id)
        # Check cache first
        if self.cache:
            # Format: tracertm:graph:{project_id}:all_paths:{source_id}:{link_types_key}
            # This aligns with event handler invalidation pattern: graph:{project_id}
            link_types_key = ":".join(sorted(link_types)) if link_types else "all"
            cache_key = f"tracertm:graph:{project_id}:all_paths:{source_id}:{link_types_key}"

            try:
                cached = await self.cache.get(cache_key)
                if cached:
                    logger.debug("Cache hit for all paths from %s in project %s", source_id, project_id)
                    # Reconstruct PathResult objects from cached data
                    results = {}
                    for target_id, data in cached.items():  # type: ignore[attr-defined]
                        results[target_id] = PathResult(
                            source_id=data["source_id"],
                            target_id=data["target_id"],
                            path=data["path"],
                            distance=data["distance"],
                            link_types=data["link_types"],
                            exists=data["exists"],
                        )
                    return results
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Cache read failed for all paths from %s: %s", source_id, e)

        # Compute paths (existing logic)
        results = await self._compute_all_paths(project_id, source_id, link_types)

        # Cache for 5 minutes (300 seconds)
        if self.cache:
            try:
                cache_data = {}
                for target_id, result in results.items():
                    cache_data[target_id] = {
                        "source_id": result.source_id,
                        "target_id": result.target_id,
                        "path": result.path,
                        "distance": result.distance,
                        "link_types": result.link_types,
                        "exists": result.exists,
                    }
                link_types_key = ":".join(sorted(link_types)) if link_types else "all"
                cache_key = f"tracertm:graph:{project_id}:all_paths:{source_id}:{link_types_key}"
                await self.cache.set(cache_key, cache_data, ttl_seconds=300)
                logger.debug("Cached all paths from %s in project %s", source_id, project_id)
            except (ValueError, TypeError, OperationalError) as e:
                logger.warning("Cache write failed for all paths from %s: %s", source_id, e)

        return results

    async def _compute_all_paths(
        self,
        project_id: str | uuid.UUID,
        source_id: str | uuid.UUID,
        link_types: list[str] | None = None,
    ) -> dict[str, PathResult]:
        """Internal method to compute all shortest paths from source.

        Args:
            project_id: Project ID
            source_id: Source item ID
            link_types: Optional list of link types to follow

        Returns:
            Dict mapping target IDs to PathResult objects
        """
        project_id = str(project_id)
        source_id = str(source_id)
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
        distances: dict[str, float] = {node: float("inf") for node in adjacency_list}
        distances[source_id] = 0

        previous: dict[str, str | None] = dict.fromkeys(adjacency_list)
        link_types_used: dict[str, str] = {}

        pq = [(0, source_id)]
        visited: set[Any] = set()

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

            path_current: str | None = current
            while path_current is not None:
                path.append(path_current)
                if path_current in link_types_used:
                    link_types_path.append(link_types_used[path_current])
                path_current = previous[path_current]

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
