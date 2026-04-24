"""Graph validation service for enforcing graph rules.

Functional Requirements: FR-QUAL-009
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from tracertm.models.edge_type import EdgeType
from tracertm.models.graph import Graph
from tracertm.models.graph_node import GraphNode
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.node_kind_rule import NodeKindRule

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GraphValidationService:
    """Validate graph integrity and rules."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def validate_graph(self, project_id: str, graph_id: str) -> dict[str, Any]:
        """Validate graph."""
        graph = await self.session.execute(select(Graph).where(Graph.id == graph_id, Graph.project_id == project_id))
        graph_obj = graph.scalar_one_or_none()
        if not graph_obj:
            return {"errors": ["graph_not_found"], "warnings": []}

        nodes_result = await self.session.execute(
            select(Item).join(GraphNode, GraphNode.item_id == Item.id).where(GraphNode.graph_id == graph_id),
        )
        nodes = list(nodes_result.scalars().all())
        node_ids = {n.id for n in nodes}
        node_kind_by_id = {n.id: n.node_kind_id for n in nodes}

        links_result = await self.session.execute(select(Link).where(Link.graph_id == graph_id))
        links = list(links_result.scalars().all())

        edge_types_result = await self.session.execute(select(EdgeType).where(EdgeType.project_id == project_id))
        edge_types = {e.name for e in edge_types_result.scalars().all()}

        rules_result = await self.session.execute(select(NodeKindRule).where(NodeKindRule.project_id == project_id))
        rules = list(rules_result.scalars().all())
        rule_map: dict[Any, dict[str, Any]] = {r.node_kind_id: (r.rule_metadata or {}) for r in rules}

        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []

        for link in links:
            if link.link_type not in edge_types:
                errors.append({
                    "type": "unknown_edge_type",
                    "link_id": link.id,
                    "link_type": link.link_type,
                })

            if link.source_item_id not in node_ids or link.target_item_id not in node_ids:
                errors.append({
                    "type": "link_to_missing_node",
                    "link_id": link.id,
                    "source": link.source_item_id,
                    "target": link.target_item_id,
                })
                continue

            source_kind = node_kind_by_id.get(link.source_item_id)
            allowed_edges = rule_map.get(source_kind, {}).get("allowed_edges", ["*"])
            if "*" not in allowed_edges and link.link_type not in allowed_edges:
                warnings.append({
                    "type": "edge_not_allowed_for_source_kind",
                    "link_id": link.id,
                    "link_type": link.link_type,
                    "source_kind_id": source_kind,
                })

        return {
            "graph_id": graph_id,
            "project_id": project_id,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "node_count": len(nodes),
                "link_count": len(links),
                "error_count": len(errors),
                "warning_count": len(warnings),
            },
        }
