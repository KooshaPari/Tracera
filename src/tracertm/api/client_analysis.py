"""Graph and analysis-related operations for the TraceRTM Python API client."""

from tracertm.models.link import Link


class ClientAnalysisMixin:
    """Mixin for TraceRTMClient to handle graph and analysis operations."""

    def compute_transitive_closure(self, start_id: str, link_types: list[str] | None = None) -> list[str]:
        """Compute reachable item IDs from a start node following links."""
        session = self._ensure_sync_session()
        visited = set()
        stack = [start_id]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            links = session.query(Link).filter(Link.source_item_id == current).all()
            for link in links:
                if link_types and link.link_type not in link_types:
                    continue
                stack.append(link.target_item_id)
        return list(visited)

    def find_path(self, start_id: str, end_id: str) -> list[str]:
        """Find a path between two items using BFS."""
        session = self._ensure_sync_session()
        from collections import deque

        queue = deque([[start_id]])
        visited = {start_id}
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == end_id:
                return path
            for link in session.query(Link).filter(Link.source_item_id == node).all():
                nxt = link.target_item_id
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append([*path, nxt])
        return []
