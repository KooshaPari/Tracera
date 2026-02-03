"""Graph QA report service."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.graph import Graph
from tracertm.models.graph_node import GraphNode
from tracertm.models.item import Item
from tracertm.models.link import Link


class GraphReportService:
    """Generate QA reports for graph coverage and integrity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def build_report(self, project_id: str, graph_id: str) -> dict[str, Any]:
        graph_result = await self.session.execute(
            select(Graph).where(Graph.id == graph_id, Graph.project_id == project_id)
        )
        graph = graph_result.scalar_one_or_none()
        if not graph:
            return {"errors": ["graph_not_found"]}

        nodes_result = await self.session.execute(
            select(Item).join(GraphNode, GraphNode.item_id == Item.id).where(GraphNode.graph_id == graph_id)
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

        # Missing mappings for user requirements
        mapping_graph = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "mapping",
            )
        )
        mapping_graph_obj = mapping_graph.scalar_one_or_none()
        mapping_links: list[Link] = []
        if mapping_graph_obj:
            mapping_links_result = await self.session.execute(select(Link).where(Link.graph_id == mapping_graph_obj.id))
            mapping_links = list(mapping_links_result.scalars().all())
        mapping_linked = set()
        for link in mapping_links:
            mapping_linked.add(link.source_item_id)
            mapping_linked.add(link.target_item_id)

        missing_mappings: list[str] = []
        if graph.graph_type == "user_requirements":
            for node_id, kind in node_kind_by_id.items():
                if kind in {"capability", "expectation", "acceptance_check"} and node_id not in mapping_linked:
                    missing_mappings.append(node_id)

        # API endpoints unreachable from journey or mapping graphs
        unreachable_api: list[str] = []
        tech_graph = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "technical_requirements",
            )
        )
        tech_graph_obj = tech_graph.scalar_one_or_none()
        journey_graph = await self.session.execute(
            select(Graph).where(
                Graph.project_id == project_id,
                Graph.graph_type == "journey",
            )
        )
        journey_graph_obj = journey_graph.scalar_one_or_none()

        if tech_graph_obj:
            tech_nodes_result = await self.session.execute(
                select(Item)
                .join(GraphNode, GraphNode.item_id == Item.id)
                .where(GraphNode.graph_id == tech_graph_obj.id)
            )
            tech_nodes = list(tech_nodes_result.scalars().all())
            api_nodes = [n.id for n in tech_nodes if n.item_type == "api_endpoint"]

            covered_nodes = set()
            if journey_graph_obj:
                journey_nodes_result = await self.session.execute(
                    select(GraphNode.item_id).where(GraphNode.graph_id == journey_graph_obj.id)
                )
                covered_nodes.update([row[0] for row in journey_nodes_result.all()])
            if mapping_graph_obj:
                mapping_nodes_result = await self.session.execute(
                    select(GraphNode.item_id).where(GraphNode.graph_id == mapping_graph_obj.id)
                )
                covered_nodes.update([row[0] for row in mapping_nodes_result.all()])

            unreachable_api = sorted([n for n in api_nodes if n not in covered_nodes])

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
