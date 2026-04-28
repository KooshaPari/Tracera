"""Graph snapshot and diff service.

Functional Requirements: FR-QUAL-007
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import func, select

from tracertm.models.graph import Graph
from tracertm.models.graph_snapshot import GraphSnapshot
from tracertm.services.graph_service import GraphService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _stable_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash_payload(payload: object) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


class GraphSnapshotService:
    """Create, fetch, and diff graph snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.graph_service = GraphService(session)

    async def create_snapshot(
        self,
        project_id: str,
        graph_id: str,
        created_by: str | None = None,
        description: str | None = None,
    ) -> GraphSnapshot:
        """Create snapshot."""
        graph = await self.session.execute(select(Graph).where(Graph.id == graph_id, Graph.project_id == project_id))
        graph_obj = graph.scalar_one_or_none()
        if not graph_obj:
            msg = "Graph not found"
            raise ValueError(msg)

        data = await self.graph_service.get_graph(
            project_id=project_id,
            graph_id=graph_id,
            include_nodes=True,
            include_links=True,
        )

        nodes = sorted(data.get("nodes", []), key=lambda n: n.get("id", ""))
        links = sorted(data.get("links", []), key=lambda link: link.get("id", ""))

        snapshot_payload = {
            "graph": data.get("graph"),
            "nodes": nodes,
            "links": links,
        }
        snapshot_hash = _hash_payload(snapshot_payload)

        latest_version = await self.session.execute(
            select(func.max(GraphSnapshot.version)).where(
                GraphSnapshot.project_id == project_id,
                GraphSnapshot.graph_id == graph_id,
            ),
        )
        next_version = (latest_version.scalar_one() or 0) + 1

        snapshot = GraphSnapshot(
            project_id=project_id,
            graph_id=graph_id,
            version=next_version,
            snapshot_json=snapshot_payload,
            snapshot_hash=snapshot_hash,
            created_by=created_by,
            description=description,
        )
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def get_snapshot(
        self,
        project_id: str,
        graph_id: str,
        version: int | None = None,
    ) -> GraphSnapshot | None:
        """Get snapshot."""
        query = select(GraphSnapshot).where(
            GraphSnapshot.project_id == project_id,
            GraphSnapshot.graph_id == graph_id,
        )
        if version is not None:
            query = query.where(GraphSnapshot.version == version)
        else:
            query = query.order_by(GraphSnapshot.version.desc())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def diff_snapshots(
        self,
        project_id: str,
        graph_id: str,
        from_version: int,
        to_version: int,
    ) -> dict[str, Any]:
        """Diff snapshots."""
        from_snapshot = await self.get_snapshot(project_id, graph_id, from_version)
        to_snapshot = await self.get_snapshot(project_id, graph_id, to_version)
        if not from_snapshot or not to_snapshot:
            msg = "Snapshots not found"
            raise ValueError(msg)

        from_nodes_raw = (from_snapshot.snapshot_json or {}).get("nodes")
        to_nodes_raw = (to_snapshot.snapshot_json or {}).get("nodes")
        from_nodes_list = from_nodes_raw if isinstance(from_nodes_raw, list) else []
        to_nodes_list = to_nodes_raw if isinstance(to_nodes_raw, list) else []
        from_nodes = {str(cast("dict[str, Any]", n).get("id", "")) for n in from_nodes_list}
        to_nodes = {str(cast("dict[str, Any]", n).get("id", "")) for n in to_nodes_list}

        from_links_raw = (from_snapshot.snapshot_json or {}).get("links")
        to_links_raw = (to_snapshot.snapshot_json or {}).get("links")
        from_links_list = from_links_raw if isinstance(from_links_raw, list) else []
        to_links_list = to_links_raw if isinstance(to_links_raw, list) else []
        from_links = {str(cast("dict[str, Any]", link).get("id", "")) for link in from_links_list}
        to_links = {str(cast("dict[str, Any]", link).get("id", "")) for link in to_links_list}

        return {
            "from_version": from_version,
            "to_version": to_version,
            "nodes": {
                "added": sorted(to_nodes - from_nodes),
                "removed": sorted(from_nodes - to_nodes),
            },
            "links": {
                "added": sorted(to_links - from_links),
                "removed": sorted(from_links - to_links),
            },
        }
