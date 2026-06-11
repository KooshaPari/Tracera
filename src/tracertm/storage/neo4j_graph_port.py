"""Neo4j ``GraphPort`` adapter — sole typed write boundary (Pillar-A Phase 0).

Wraps the existing :mod:`tracertm.storage.neo4j_trace_link_writer` so every
graph mutation flows through :class:`~tracertm.ports.graph_contract.GraphPort`
validation before reaching Neo4j (``NFR-TRC-010``).

The adapter translates canonical :class:`GraphNode` / :class:`GraphEdge` value
objects into the legacy :class:`~tracertm.models.trace_link.Artifact` /
:class:`~tracertm.models.trace_link.TraceLink` wire format the writer already
understands. Vocabulary mapping is explicit and closed — unmapped kinds raise
:class:`~tracertm.ports.graph_contract.SchemaContractError` at the boundary
rather than silently inventing labels.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Mapping, Sequence

from tracertm.models.trace_link import (
    Artifact,
    ArtifactKind,
    Requirement,
    RequirementStatus,
    TraceLink,
    TraceLinkType,
)
from tracertm.ports.graph_contract import (
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeKind,
    SchemaContractError,
    validate_edge,
    validate_node,
)
from tracertm.storage import neo4j_trace_link_writer as _writer

if TYPE_CHECKING:
    from neo4j import Driver

__all__ = ["Neo4jGraphPort", "GraphPortAdapterError"]

# Canonical NodeKind → legacy ArtifactKind (trace-link projection subset).
_NODE_KIND_TO_ARTIFACT: dict[NodeKind, ArtifactKind] = {
    NodeKind.REQUIREMENT: ArtifactKind.REQUIREMENT,
    NodeKind.SPEC: ArtifactKind.DESIGN,
    NodeKind.ADR: ArtifactKind.RATIONALE,
    NodeKind.CODE: ArtifactKind.CODE,
    NodeKind.TEST: ArtifactKind.TEST,
    NodeKind.PR: ArtifactKind.CODE,
    NodeKind.COMMIT: ArtifactKind.CODE,
    NodeKind.EVIDENCE: ArtifactKind.EVIDENCE,
}

# Canonical EdgeType → legacy TraceLinkType.
_EDGE_TO_TRACE: dict[EdgeType, TraceLinkType] = {
    EdgeType.IMPLEMENTS: TraceLinkType.IMPLEMENTS,
    EdgeType.VERIFIES: TraceLinkType.VERIFIES,
    EdgeType.DUPLICATES: TraceLinkType.DUPLICATES,
    EdgeType.COVERS: TraceLinkType.SATISFIES,
    EdgeType.TRACES_TO: TraceLinkType.DERIVES_FROM,
    EdgeType.EVIDENCES: TraceLinkType.VERIFIES,
    EdgeType.IMPACTS: TraceLinkType.CONFLICTS_WITH,
    EdgeType.DEPENDS_ON: TraceLinkType.REFINES,
    EdgeType.BELONGS_TO: TraceLinkType.DERIVES_FROM,
    EdgeType.RELEASES: TraceLinkType.SATISFIES,
}


class GraphPortAdapterError(SchemaContractError):
    """Raised when a canonical node/edge cannot be projected to Neo4j."""


def _require_project_id(properties: Mapping[str, Any]) -> uuid.UUID:
    raw = properties.get("project_id")
    if raw is None:
        raise GraphPortAdapterError("GraphNode.properties must include project_id")
    return uuid.UUID(str(raw))


def _graph_node_to_artifact(node: GraphNode) -> Artifact | Requirement:
    """Map a validated canonical node to an Artifact/Requirement value object."""
    kind = _NODE_KIND_TO_ARTIFACT.get(node.kind)
    if kind is None:
        raise GraphPortAdapterError(
            f"NodeKind {node.kind.value} is not yet projectable to Neo4j"
        )
    props = dict(node.properties)
    project_id = _require_project_id(props)
    title = str(props.get("title") or node.id)
    common: dict[str, Any] = {
        "id": uuid.UUID(str(node.id)),
        "project_id": project_id,
        "kind": kind,
        "title": title,
        "description": props.get("description"),
        "external_id": props.get("external_id"),
        "metadata": dict(props.get("metadata") or {}),
        "created_at": props.get("created_at"),
        "updated_at": props.get("updated_at"),
    }
    if node.kind is NodeKind.REQUIREMENT:
        status_raw = props.get("status", RequirementStatus.DRAFT.value)
        return Requirement(
            **common,
            status=RequirementStatus(str(status_raw)),
            priority=props.get("priority"),
            rationale=props.get("rationale"),
            acceptance_criteria=list(props.get("acceptance_criteria") or []),
            verification_method=props.get("verification_method"),
        )
    return Artifact(**common)


def _graph_edge_to_trace_link(edge: GraphEdge) -> TraceLink:
    """Map a validated canonical edge to a TraceLink value object."""
    link_type = _EDGE_TO_TRACE.get(edge.type)
    if link_type is None:
        raise GraphPortAdapterError(
            f"EdgeType {edge.type.value} is not yet projectable to Neo4j"
        )
    props = dict(edge.properties)
    project_id = _require_project_id(props)
    confidence = float(props.get("confidence", 1.0))
    return TraceLink(
        project_id=project_id,
        source_artifact_id=uuid.UUID(str(edge.src.id)),
        target_artifact_id=uuid.UUID(str(edge.dst.id)),
        link_type=link_type,
        confidence=confidence,
        rationale=props.get("rationale"),
        metadata=dict(props.get("metadata") or {}),
        id=uuid.UUID(str(props["link_id"])) if props.get("link_id") else uuid.uuid4(),
        created_at=props.get("created_at"),
        updated_at=props.get("updated_at"),
    )


class Neo4jGraphPort:
    """``GraphPort`` implementation backed by Neo4j via the trace-link writer."""

    def __init__(self, driver: Driver) -> None:
        self._driver = driver

    def upsert_node(self, node: GraphNode) -> None:
        validated = validate_node(node)
        artifact = _graph_node_to_artifact(validated)
        if isinstance(artifact, Requirement):
            _writer.write_requirement(self._driver, artifact)
        else:
            _writer.write_artifact(self._driver, artifact)

    def upsert_edge(self, edge: GraphEdge) -> None:
        validated = validate_edge(edge)
        link = _graph_edge_to_trace_link(validated)
        _writer.write_link(self._driver, link)

    def upsert_nodes(self, nodes: Sequence[GraphNode]) -> None:
        for node in nodes:
            self.upsert_node(node)

    def upsert_edges(self, edges: Sequence[GraphEdge]) -> None:
        for edge in edges:
            self.upsert_edge(edge)

    def neighbors(
        self,
        node: GraphNode,
        *,
        edge_type: EdgeType | None = None,
        direction: str = "out",
    ) -> Sequence[GraphEdge]:
        """Return incident edges for impact/blast-radius queries."""
        validated = validate_node(node)
        if direction not in ("out", "in", "both"):
            raise ValueError(f"direction must be out|in|both, got {direction!r}")

        rel_filter = ""
        params: dict[str, Any] = {"node_id": str(validated.id)}
        if edge_type is not None:
            trace_type = _EDGE_TO_TRACE.get(edge_type)
            if trace_type is None:
                return ()
            rel_filter = "AND type(r) = $rel_type"
            params["rel_type"] = trace_type.value

        if direction == "out":
            pattern = "(n:Artifact {id: $node_id})-[r]->(m:Artifact)"
            src_id_key, dst_id_key = "src_id", "dst_id"
            src_kind_key, dst_kind_key = "src_kind", "dst_kind"
            return_clause = (
                "type(r) AS rel_type, n.id AS src_id, m.id AS dst_id, "
                "n.kind AS src_kind, m.kind AS dst_kind, "
                "r.confidence AS confidence, r.rationale AS rationale"
            )
        elif direction == "in":
            pattern = "(n:Artifact {id: $node_id})<-[r]-(m:Artifact)"
            src_id_key, dst_id_key = "src_id", "dst_id"
            src_kind_key, dst_kind_key = "src_kind", "dst_kind"
            return_clause = (
                "type(r) AS rel_type, m.id AS src_id, n.id AS dst_id, "
                "m.kind AS src_kind, n.kind AS dst_kind, "
                "r.confidence AS confidence, r.rationale AS rationale"
            )
        else:
            pattern = "(n:Artifact {id: $node_id})-[r]-(m:Artifact)"
            src_id_key, dst_id_key = "src_id", "dst_id"
            src_kind_key, dst_kind_key = "src_kind", "dst_kind"
            return_clause = (
                "type(r) AS rel_type, "
                "CASE WHEN startNode(r) = n THEN n.id ELSE m.id END AS src_id, "
                "CASE WHEN startNode(r) = n THEN m.id ELSE n.id END AS dst_id, "
                "CASE WHEN startNode(r) = n THEN n.kind ELSE m.kind END AS src_kind, "
                "CASE WHEN startNode(r) = n THEN m.kind ELSE n.kind END AS dst_kind, "
                "r.confidence AS confidence, r.rationale AS rationale"
            )

        cypher = f"MATCH {pattern} WHERE true {rel_filter} RETURN {return_clause}"

        trace_to_edge = {v: k for k, v in _EDGE_TO_TRACE.items()}
        artifact_to_node = {v: k for k, v in _NODE_KIND_TO_ARTIFACT.items()}

        edges: list[GraphEdge] = []
        with self._driver.session() as session:
            for record in session.run(cypher, **params):
                rel = record["rel_type"]
                canonical_edge = trace_to_edge.get(TraceLinkType(rel))
                if canonical_edge is None:
                    continue
                src_kind = artifact_to_node.get(ArtifactKind(record[src_kind_key]))
                dst_kind = artifact_to_node.get(ArtifactKind(record[dst_kind_key]))
                if src_kind is None or dst_kind is None:
                    continue
                edges.append(
                    GraphEdge(
                        type=canonical_edge,
                        src=GraphNode(kind=src_kind, id=str(record[src_id_key])),
                        dst=GraphNode(kind=dst_kind, id=str(record[dst_id_key])),
                        properties={
                            "confidence": record.get("confidence"),
                            "rationale": record.get("rationale"),
                        },
                    )
                )
        return edges
