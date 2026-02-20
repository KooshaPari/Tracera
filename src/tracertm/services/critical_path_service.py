"""Critical path service for TraceRTM project scheduling."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository


@dataclass
class CriticalPathResult:
    """Result of critical path analysis."""

    project_id: str
    critical_path: list[str]  # Item IDs in critical path
    path_length: int  # Number of items in path
    total_duration: int  # Total duration (number of hops)
    critical_items: set[str]  # All items on critical path
    slack_times: dict[str, int]  # Slack time for each item


class CriticalPathService:
    """Service for calculating critical path in project networks.

    Functional Requirements:
    - FR-RPT-002

    User Stories:
    - US-GRAPH-002

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

    async def calculate_critical_path(
        self,
        project_id: str,
        link_types: list[str] | None = None,
    ) -> CriticalPathResult:
        """Calculate critical path using topological sort and dynamic programming.

        Args:
            project_id: Project ID
            link_types: Optional list of link types to follow

        Returns:
            CriticalPathResult with critical path information

        Complexity: O(V + E) where V = items, E = links
        """
        # Build adjacency list and reverse adjacency list
        adjacency_list: dict[str, list[str]] = {}
        reverse_adjacency: dict[str, list[str]] = {}
        in_degree: dict[str, int] = {}

        # Get all items in project
        items = await self.items.get_by_project(project_id)
        for item in items:
            item_id = str(item.id)
            adjacency_list[item_id] = []
            reverse_adjacency[item_id] = []
            in_degree[item_id] = 0

        # Get all links in project
        links = await self.links.get_by_project(project_id)
        for link in links:
            # Filter by link types if specified
            if link_types and link.link_type not in link_types:
                continue

            source = str(link.source_item_id)
            target = str(link.target_item_id)

            adjacency_list[source].append(target)
            reverse_adjacency[target].append(source)
            in_degree[target] += 1

        # Topological sort using Kahn's algorithm
        queue = [node for node in in_degree if in_degree[node] == 0]
        topo_order = []

        while queue:
            node = queue.pop(0)
            topo_order.append(node)

            for neighbor in adjacency_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Calculate earliest start and finish times
        earliest_start: dict[str, int] = dict.fromkeys(adjacency_list, 0)
        earliest_finish: dict[str, int] = dict.fromkeys(adjacency_list, 1)

        for node in topo_order:
            for neighbor in adjacency_list[node]:
                earliest_start[neighbor] = max(earliest_start[neighbor], earliest_finish[node])
                earliest_finish[neighbor] = earliest_start[neighbor] + 1

        # Calculate latest start and finish times (backward pass)
        max_finish = max(earliest_finish.values()) if earliest_finish else 0
        latest_finish: dict[str, int] = dict.fromkeys(adjacency_list, max_finish)
        latest_start: dict[str, int] = dict.fromkeys(adjacency_list, max_finish - 1)

        for node in reversed(topo_order):
            if adjacency_list[node]:
                latest_finish[node] = min(latest_start[neighbor] for neighbor in adjacency_list[node])
            latest_start[node] = latest_finish[node] - 1

        # Calculate slack times
        slack_times: dict[str, int] = {}
        critical_items: set[str] = set()

        for node in adjacency_list:
            slack = latest_start[node] - earliest_start[node]
            slack_times[node] = slack

            if slack == 0:
                critical_items.add(node)

        # Find critical path (path with all slack = 0)
        critical_path = self._find_critical_path(
            adjacency_list,
            critical_items,
            topo_order,
        )

        return CriticalPathResult(
            project_id=project_id,
            critical_path=critical_path,
            path_length=len(critical_path),
            total_duration=max_finish,
            critical_items=critical_items,
            slack_times=slack_times,
        )

    def _find_critical_path(
        self,
        adjacency_list: dict[str, list[str]],
        critical_items: set[str],
        _topo_order: list[str],
    ) -> list[str]:
        """Find the critical path from start to end nodes.

        Complexity: O(V + E)
        """
        # Find start nodes (no predecessors in critical items)
        start_nodes = [
            node
            for node in critical_items
            if not any(
                neighbor in critical_items
                for neighbors in adjacency_list.values()
                for neighbor in neighbors
                if node in neighbors
            )
        ]

        if not start_nodes:
            return []

        # DFS to find path
        path = []

        def dfs(node: str, current_path: list[str]) -> bool:
            current_path.append(node)

            # Check if this is an end node
            if not any(neighbor in critical_items for neighbor in adjacency_list.get(node, [])):
                path.extend(current_path)
                return True

            # Try neighbors
            for neighbor in adjacency_list.get(node, []):
                if neighbor in critical_items and dfs(neighbor, current_path):
                    return True

            current_path.pop()
            return False

        for start in start_nodes:
            if dfs(start, []):
                break

        return path
