"""Graph QA report service.

Functional Requirements: FR-RPT-004
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from tracertm.models.graph import Graph
from tracertm.models.graph_node import GraphNode
from tracertm.models.item import Item
from tracertm.models.link import Link

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GraphReportService:
    """Generate QA reports for graph coverage and integrity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def _fetch_graph(self, project_id: str, graph_id: str) -> Graph | None:
        """Load graph by id and project; return None if not found."""
        result = await self.session.execute(select(Graph).where(Graph.id == graph_id, Graph.project_id == project_id))
        return result.scalar_one_or_none()

    async def _fetch_nodes_links_orphans(self, graph_id: str) -> tuple[set[str], dict[str, str], list[Link], list[str]]:
        """Return (node_ids, node_kind_by_id, links, orphan_nodes)."""
        nodes_result = await self.session.execute(
            select(Item).join(GraphNode, GraphNode.item_id == Item.id).where(GraphNode.graph_id == graph_id),
        )
        nodes = list(nodes_result.scalars().all())
        node_ids = {n.id for n in nodes}
        node_kind_by_id = {n.id: n.item_type for n in nodes}

        links_result = await self.session.execute(select(Link).where(Link.graph_id == graph_id))
        links = list(links_result.scalars().all())
        linked_nodes = set()
        for link in links:
            linked_nodes.add(link.source_item_id)
            linked_nodes.add(link.target_item_id)
        orphan_nodes = sorted([n for n in node_ids if n not in linked_nodes])
        return node_ids, node_kind_by_id, links, orphan_nodes

    async def _fetch_missing_mappings(
        self,
        project_id: str,
        graph_type: str,
        node_kind_by_id: dict[str, str],
    ) -> list[str]:
        """Return node ids that are required but not in mapping graph."""
        mapping_result = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "mapping",
            ),
        )
        mapping_graph_obj = mapping_result.scalar_one_or_none()
        mapping_linked: set[str] = set()
        if mapping_graph_obj:
            mapping_links_result = await self.session.execute(select(Link).where(Link.graph_id == mapping_graph_obj.id))
            for link in mapping_links_result.scalars().all():
                mapping_linked.add(link.source_item_id)
                mapping_linked.add(link.target_item_id)

        if graph_type != "user_requirements":
            return []
        required_kinds = {"capability", "expectation", "acceptance_check"}
        return [nid for nid, kind in node_kind_by_id.items() if kind in required_kinds and nid not in mapping_linked]

    async def _fetch_unreachable_api(self, project_id: str, mapping_graph_obj: Graph | None) -> list[str]:
        """Return sorted list of API endpoint node ids not covered by journey or mapping."""
        tech_result = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "technical_requirements",
            ),
        )
        tech_graph_obj = tech_result.scalar_one_or_none()
        if not tech_graph_obj:
            return []

        journey_result = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "journey",
            ),
        )
        journey_graph_obj = journey_result.scalar_one_or_none()

        tech_nodes_result = await self.session.execute(
            select(Item).join(GraphNode, GraphNode.item_id == Item.id).where(GraphNode.graph_id == tech_graph_obj.id),
        )
        tech_nodes = list(tech_nodes_result.scalars().all())
        api_nodes = [n.id for n in tech_nodes if n.item_type == "api_endpoint"]

        covered_nodes: set[str] = set()
        if journey_graph_obj:
            journey_nodes_result = await self.session.execute(
                select(GraphNode.item_id).where(GraphNode.graph_id == journey_graph_obj.id),
            )
            covered_nodes.update(row[0] for row in journey_nodes_result.all())
        if mapping_graph_obj:
            mapping_nodes_result = await self.session.execute(
                select(GraphNode.item_id).where(GraphNode.graph_id == mapping_graph_obj.id),
            )
            covered_nodes.update(row[0] for row in mapping_nodes_result.all())

        return sorted([n for n in api_nodes if n not in covered_nodes])

    async def build_report(self, project_id: str, graph_id: str) -> dict[str, Any]:
        """Build report."""
        graph = await self._fetch_graph(project_id, graph_id)
        if not graph:
            return {"errors": ["graph_not_found"]}

        node_ids, node_kind_by_id, links, orphan_nodes = await self._fetch_nodes_links_orphans(graph_id)
        missing_mappings = await self._fetch_missing_mappings(project_id, graph.graph_type, node_kind_by_id)

        mapping_result = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "mapping",
            ),
        )
        mapping_graph_obj = mapping_result.scalar_one_or_none()
        unreachable_api = await self._fetch_unreachable_api(project_id, mapping_graph_obj)

        return {
            "graph_id": graph_id,
            "project_id": project_id,
            "graph_type": graph.graph_type,
            "orphan_nodes": orphan_nodes,
            "missing_mappings": missing_mappings,
            "unreachable_api_endpoints": unreachable_api,
            "summary": {
                "node_count": len(node_ids),
                "link_count": len(links),
                "orphan_count": len(orphan_nodes),
                "missing_mapping_count": len(missing_mappings),
                "unreachable_api_count": len(unreachable_api),
            },
        }
