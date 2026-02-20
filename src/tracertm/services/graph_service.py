"""Graph service for retrieving graph projections."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.graph import Graph
from tracertm.models.graph_node import GraphNode
from tracertm.models.item import Item
from tracertm.models.link import Link


class GraphService:
    """Service for graph projections.

    Functional Requirements:
    - FR-RPT-005
    - FR-RPT-006

    User Stories:
    - US-GRAPH-005
    - US-GRAPH-006

    Epics:
    - EPIC-006
    """

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize."""
        self.db_session = db_session

    async def get_graph(
        self,
        project_id: str | None = None,
        graph_id: str | None = None,
        graph_type: str | None = None,
        include_nodes: bool = True,
        include_links: bool = True,
    ) -> dict[str, Any]:
        """Get graph."""
        if not isinstance(self.db_session, AsyncSession):
            return {"nodes": [], "links": []}

        graph = None
        if graph_id:
            result = await self.db_session.execute(select(Graph).where(Graph.id == graph_id))
            graph = result.scalar_one_or_none()
        elif graph_type and project_id:
            result = await self.db_session.execute(
                select(Graph)
                .where(Graph.project_id == project_id, Graph.graph_type == graph_type)
                .order_by(Graph.name),
            )
            graph = result.scalars().first()

        if not graph:
            return {"nodes": [], "links": []}

        nodes: list[dict[str, Any]] = []
        links: list[dict[str, Any]] = []

        if include_nodes:
            items_result = await self.db_session.execute(
                select(Item).join(GraphNode, GraphNode.item_id == Item.id).where(GraphNode.graph_id == graph.id),
            )
            item_rows: Sequence[Item] = items_result.scalars().all()
            nodes = [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "view": item.view,
                    "item_type": item.item_type,
                    "node_kind_id": item.node_kind_id,
                    "status": item.status,
                    "priority": item.priority,
                    "owner": item.owner,
                    "parent_id": item.parent_id,
                    "metadata": item.item_metadata,
                }
                for item in item_rows
            ]

        if include_links:
            links_result = await self.db_session.execute(select(Link).where(Link.graph_id == graph.id))
            link_rows: Sequence[Link] = links_result.scalars().all()
            links = [
                {
                    "id": link.id,
                    "source_item_id": link.source_item_id,
                    "target_item_id": link.target_item_id,
                    "link_type": link.link_type,
                    "graph_id": link.graph_id,
                    "metadata": link.link_metadata,
                }
                for link in link_rows
            ]

        return {
            "graph": {
                "id": graph.id,
                "project_id": graph.project_id,
                "name": graph.name,
                "graph_type": graph.graph_type,
                "description": graph.description,
                "root_item_id": graph.root_item_id,
                "graph_version": graph.graph_version,
                "graph_rules": graph.graph_rules,
                "metadata": graph.graph_metadata,
            },
            "nodes": nodes,
            "links": links,
        }
