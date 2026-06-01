"""Canonical typed-graph schema contract + ``GraphPort`` (Pillar-A spine).

Implements ``FR-TRC-018`` (Canonical Typed-Graph Schema Contract) and the
companion ``NFR-TRC-010`` (all graph writes go through exactly one contract; no
service writes Neo4j directly). See ``docs/TRACERA_PLATFORM_RND.md`` §3.3.

Why this exists
---------------
Today the node/edge kinds drift across the ~12 trace/impact services and the
Neo4j writer. This module makes the schema *one* enumerated, validated contract
so that schema drift becomes impossible: any node/edge that is not part of the
canonical vocabulary is rejected before it can reach the graph.

This module is intentionally dependency-free (stdlib only) so it can be imported
by any pillar (A/B/C/D) and mirrored by the HexaKit Rust canonical ports without
dragging in a graph driver.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


class NodeKind(str, Enum):
    """Canonical graph node kinds. The closed vocabulary of the SSOT.

    Spans all four pillars: traceability (A), SDLC/PM (B), evidence (C),
    multi-repo org intelligence (D). Adding a kind is a deliberate contract
    change, not an ad-hoc string a service invents.
    """

    # Pillar A -- traceability core
    REQUIREMENT = "Requirement"
    SPEC = "Spec"
    ADR = "ADR"
    CODE = "Code"
    TEST = "Test"
    PR = "PR"
    COMMIT = "Commit"
    # Pillar B -- SDLC / program management
    RELEASE = "Release"
    PORTFOLIO = "Portfolio"
    OKR = "OKR"
    ROADMAP = "Roadmap"
    # Pillar C -- evidence & verification
    EVIDENCE = "Evidence"
    JOURNEY = "Journey"
    KEYFRAME = "Keyframe"
    # Pillar D -- multi-repo org intelligence
    REPO = "Repo"
    TEAM = "Team"


class EdgeType(str, Enum):
    """Canonical graph edge types (relationship vocabulary of the SSOT)."""

    TRACES_TO = "TRACES_TO"
    VERIFIES = "VERIFIES"
    IMPACTS = "IMPACTS"
    DEPENDS_ON = "DEPENDS_ON"
    DUPLICATES = "DUPLICATES"
    IMPLEMENTS = "IMPLEMENTS"
    COVERS = "COVERS"
    EVIDENCES = "EVIDENCES"
    BELONGS_TO = "BELONGS_TO"
    RELEASES = "RELEASES"


CANONICAL_NODE_KINDS: frozenset[NodeKind] = frozenset(NodeKind)
CANONICAL_EDGE_TYPES: frozenset[EdgeType] = frozenset(EdgeType)

# Which (source kind) -[edge]-> (target kind) combinations are meaningful.
# Keeping this explicit is what prevents schema drift (FR-TRC-018 / NFR-TRC-010).
# A value of ``None`` for either endpoint means "any canonical node kind".
_ALLOWED_EDGE_ENDPOINTS: dict[EdgeType, tuple[frozenset[NodeKind] | None, frozenset[NodeKind] | None]] = {
    EdgeType.TRACES_TO: (None, None),
    EdgeType.IMPLEMENTS: (
        frozenset({NodeKind.CODE, NodeKind.PR, NodeKind.COMMIT}),
        frozenset({NodeKind.REQUIREMENT, NodeKind.SPEC, NodeKind.ADR}),
    ),
    EdgeType.COVERS: (
        frozenset({NodeKind.TEST}),
        frozenset({NodeKind.REQUIREMENT, NodeKind.CODE, NodeKind.SPEC}),
    ),
    EdgeType.VERIFIES: (
        frozenset({NodeKind.EVIDENCE, NodeKind.KEYFRAME, NodeKind.JOURNEY, NodeKind.TEST}),
        frozenset({NodeKind.REQUIREMENT, NodeKind.CODE}),
    ),
    EdgeType.EVIDENCES: (
        frozenset({NodeKind.EVIDENCE, NodeKind.KEYFRAME}),
        None,
    ),
    EdgeType.IMPACTS: (None, None),
    EdgeType.DEPENDS_ON: (None, None),
    EdgeType.DUPLICATES: (None, None),
    EdgeType.BELONGS_TO: (None, None),
    EdgeType.RELEASES: (
        frozenset({NodeKind.RELEASE}),
        None,
    ),
}


class SchemaContractError(ValueError):
    """Raised when a node/edge violates the canonical schema contract.

    This is the enforcement mechanism behind ``NFR-TRC-010``: a write that does
    not conform to the contract is rejected rather than silently corrupting the
    graph vocabulary.
    """


@dataclass(frozen=True, slots=True)
class GraphNode:
    """A typed node addressed by a stable id within its kind."""

    kind: NodeKind
    id: str
    properties: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """A typed, directed edge between two canonical nodes."""

    type: EdgeType
    src: GraphNode
    dst: GraphNode
    properties: Mapping[str, Any] = field(default_factory=dict)


def validate_node(node: GraphNode) -> GraphNode:
    """Validate a node against the contract; return it unchanged if valid."""
    if not isinstance(node.kind, NodeKind):
        raise SchemaContractError(f"non-canonical node kind: {node.kind!r}")
    if not node.id or not str(node.id).strip():
        raise SchemaContractError(f"node of kind {node.kind.value} has empty id")
    return node


def validate_edge(edge: GraphEdge) -> GraphEdge:
    """Validate an edge (type + endpoint kinds) against the contract."""
    if not isinstance(edge.type, EdgeType):
        raise SchemaContractError(f"non-canonical edge type: {edge.type!r}")
    validate_node(edge.src)
    validate_node(edge.dst)
    allowed = _ALLOWED_EDGE_ENDPOINTS.get(edge.type)
    if allowed is not None:
        allowed_src, allowed_dst = allowed
        if allowed_src is not None and edge.src.kind not in allowed_src:
            raise SchemaContractError(
                f"{edge.type.value} cannot originate from {edge.src.kind.value}"
            )
        if allowed_dst is not None and edge.dst.kind not in allowed_dst:
            raise SchemaContractError(
                f"{edge.type.value} cannot point to {edge.dst.kind.value}"
            )
    return edge


@runtime_checkable
class GraphPort(Protocol):
    """The sole writer/reader contract for graph truth (``FR-TRC-018``).

    Every pillar writes the graph *only* through an implementation of this port
    (``NFR-TRC-010``). Concrete adapters (e.g. a Neo4j adapter wrapping the
    existing ``storage/neo4j_trace_link_writer.py``) live in the storage layer;
    this protocol is what the application services depend on.

    Implementations MUST run :func:`validate_node` / :func:`validate_edge`
    before persisting, so that the canonical schema is enforced at the only
    write boundary.
    """

    def upsert_node(self, node: GraphNode) -> None:
        """Create or update a single canonical node."""
        ...

    def upsert_edge(self, edge: GraphEdge) -> None:
        """Create or update a single canonical, directed edge."""
        ...

    def upsert_nodes(self, nodes: Sequence[GraphNode]) -> None:
        """Bulk node upsert (graduates ``feat/trc013`` bulk ingestion)."""
        ...

    def upsert_edges(self, edges: Sequence[GraphEdge]) -> None:
        """Bulk edge upsert."""
        ...

    def neighbors(
        self,
        node: GraphNode,
        *,
        edge_type: EdgeType | None = None,
        direction: str = "out",
    ) -> Sequence[GraphEdge]:
        """Return edges incident to ``node`` (impact/blast-radius queries)."""
        ...
