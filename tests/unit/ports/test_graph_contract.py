"""Unit tests for the canonical typed-graph schema contract.

Covers ``FR-TRC-018`` / ``NFR-TRC-010`` (single contract; drift impossible).
Tests GraphPort protocol structure, method signatures, and contract enforcement.
"""

from __future__ import annotations

import inspect
from typing import Sequence

import pytest

from tracertm.ports.graph_contract import (
    CANONICAL_EDGE_TYPES,
    CANONICAL_NODE_KINDS,
    EdgeType,
    GraphEdge,
    GraphNode,
    GraphPort,
    NodeKind,
    SchemaContractError,
    validate_edge,
    validate_node,
)


def _node(kind: NodeKind, id_: str = "x", **props) -> GraphNode:
    return GraphNode(kind=kind, id=id_, properties=props)


class MockGraphPort:
    """Reference implementation of GraphPort for contract validation."""

    def __init__(self) -> None:
        self.nodes: dict[tuple[NodeKind, str], GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def upsert_node(self, node: GraphNode) -> None:
        """Create or update a single canonical node."""
        validated = validate_node(node)
        self.nodes[(validated.kind, validated.id)] = validated

    def upsert_edge(self, edge: GraphEdge) -> None:
        """Create or update a single canonical, directed edge."""
        validated = validate_edge(edge)
        self.edges.append(validated)

    def upsert_nodes(self, nodes: Sequence[GraphNode]) -> None:
        """Bulk node upsert."""
        for n in nodes:
            self.upsert_node(n)

    def upsert_edges(self, edges: Sequence[GraphEdge]) -> None:
        """Bulk edge upsert."""
        for e in edges:
            self.upsert_edge(e)

    def neighbors(
        self,
        node: GraphNode,
        *,
        edge_type: EdgeType | None = None,
        direction: str = "out",
    ) -> Sequence[GraphEdge]:
        """Return edges incident to ``node``."""
        if direction == "out":
            results = [e for e in self.edges if e.src == node]
        elif direction == "in":
            results = [e for e in self.edges if e.dst == node]
        else:
            raise ValueError(f"invalid direction: {direction}")
        if edge_type is not None:
            results = [e for e in results if e.type == edge_type]
        return results


# ============================================================================
# Protocol validation tests
# ============================================================================


def test_graph_port_protocol_is_runtime_checkable():
    """Verify GraphPort is a runtime_checkable Protocol for isinstance checks."""
    mock = MockGraphPort()
    assert isinstance(mock, GraphPort)


def test_graph_port_has_upsert_node_method():
    """Verify GraphPort defines upsert_node(node: GraphNode) -> None."""
    assert hasattr(GraphPort, "upsert_node")
    sig = inspect.signature(GraphPort.upsert_node)
    params = list(sig.parameters.keys())
    assert "node" in params


def test_graph_port_has_upsert_edge_method():
    """Verify GraphPort defines upsert_edge(edge: GraphEdge) -> None."""
    assert hasattr(GraphPort, "upsert_edge")
    sig = inspect.signature(GraphPort.upsert_edge)
    params = list(sig.parameters.keys())
    assert "edge" in params


def test_graph_port_has_upsert_nodes_batch_method():
    """Verify GraphPort defines upsert_nodes(nodes: Sequence[GraphNode]) -> None."""
    assert hasattr(GraphPort, "upsert_nodes")
    sig = inspect.signature(GraphPort.upsert_nodes)
    params = list(sig.parameters.keys())
    assert "nodes" in params


def test_graph_port_has_upsert_edges_batch_method():
    """Verify GraphPort defines upsert_edges(edges: Sequence[GraphEdge]) -> None."""
    assert hasattr(GraphPort, "upsert_edges")
    sig = inspect.signature(GraphPort.upsert_edges)
    params = list(sig.parameters.keys())
    assert "edges" in params


def test_graph_port_has_neighbors_method():
    """Verify GraphPort defines neighbors with node, edge_type, direction params."""
    assert hasattr(GraphPort, "neighbors")
    sig = inspect.signature(GraphPort.neighbors)
    params = list(sig.parameters.keys())
    assert "node" in params
    assert "edge_type" in params
    assert "direction" in params
    # Check they are keyword-only after node
    assert sig.parameters["edge_type"].kind == inspect.Parameter.KEYWORD_ONLY
    assert sig.parameters["direction"].kind == inspect.Parameter.KEYWORD_ONLY


def test_graph_port_methods_have_type_annotations():
    """Verify all GraphPort methods have proper type hints."""
    for name in ["upsert_node", "upsert_edge", "upsert_nodes", "upsert_edges", "neighbors"]:
        method = getattr(GraphPort, name)
        sig = inspect.signature(method)
        assert sig.return_annotation != inspect.Signature.empty or any(
            p.annotation != inspect.Parameter.empty for p in sig.parameters.values()
        ), f"{name} lacks type annotations"


# ============================================================================
# Mock implementation tests
# ============================================================================


def test_mock_graph_port_satisfies_protocol():
    """Verify MockGraphPort is a valid GraphPort implementation."""
    mock = MockGraphPort()
    assert isinstance(mock, GraphPort)


def test_mock_graph_port_upsert_node_stores_node():
    """Verify MockGraphPort.upsert_node stores validated nodes."""
    mock = MockGraphPort()
    node = _node(NodeKind.CODE, "graph_contract.py", title="Graph Contract Module")
    mock.upsert_node(node)
    assert (NodeKind.CODE, "graph_contract.py") in mock.nodes
    assert mock.nodes[(NodeKind.CODE, "graph_contract.py")].id == "graph_contract.py"


def test_mock_graph_port_upsert_node_validates_before_storing():
    """Verify MockGraphPort validates nodes before storing."""
    mock = MockGraphPort()
    with pytest.raises(SchemaContractError):
        mock.upsert_node(GraphNode(kind=NodeKind.CODE, id="   "))


def test_mock_graph_port_upsert_nodes_batch():
    """Verify MockGraphPort.upsert_nodes stores multiple nodes."""
    mock = MockGraphPort()
    nodes = [
        _node(NodeKind.CODE, "mod.py"),
        _node(NodeKind.REQUIREMENT, "FR-TRC-018"),
        _node(NodeKind.TEST, "test_graph.py"),
    ]
    mock.upsert_nodes(nodes)
    assert len(mock.nodes) == 3


def test_mock_graph_port_upsert_edge_stores_edge():
    """Verify MockGraphPort.upsert_edge stores validated edges."""
    mock = MockGraphPort()
    edge = GraphEdge(
        type=EdgeType.IMPLEMENTS,
        src=_node(NodeKind.CODE, "graph_contract.py"),
        dst=_node(NodeKind.REQUIREMENT, "FR-TRC-018"),
    )
    mock.upsert_edge(edge)
    assert len(mock.edges) == 1
    assert mock.edges[0].type == EdgeType.IMPLEMENTS


def test_mock_graph_port_upsert_edge_validates_before_storing():
    """Verify MockGraphPort validates edges before storing."""
    mock = MockGraphPort()
    edge = GraphEdge(
        type=EdgeType.IMPLEMENTS,
        src=_node(NodeKind.REQUIREMENT, "FR-TRC-018"),
        dst=_node(NodeKind.REQUIREMENT, "FR-TRC-019"),
    )
    with pytest.raises(SchemaContractError):
        mock.upsert_edge(edge)


def test_mock_graph_port_upsert_edges_batch():
    """Verify MockGraphPort.upsert_edges stores multiple edges."""
    mock = MockGraphPort()
    edges = [
        GraphEdge(
            type=EdgeType.IMPLEMENTS,
            src=_node(NodeKind.CODE, "mod.py"),
            dst=_node(NodeKind.REQUIREMENT, "FR-TRC-018"),
        ),
        GraphEdge(
            type=EdgeType.COVERS,
            src=_node(NodeKind.TEST, "test_graph.py"),
            dst=_node(NodeKind.CODE, "mod.py"),
        ),
    ]
    mock.upsert_edges(edges)
    assert len(mock.edges) == 2


def test_mock_graph_port_neighbors_returns_outgoing_by_default():
    """Verify neighbors() returns outgoing edges (direction='out') by default."""
    mock = MockGraphPort()
    code_node = _node(NodeKind.CODE, "mod.py")
    req_node = _node(NodeKind.REQUIREMENT, "FR-TRC-018")
    edge = GraphEdge(type=EdgeType.IMPLEMENTS, src=code_node, dst=req_node)
    mock.upsert_edge(edge)

    neighbors = mock.neighbors(code_node)
    assert len(neighbors) == 1
    assert neighbors[0].dst == req_node


def test_mock_graph_port_neighbors_filters_by_direction_in():
    """Verify neighbors() can filter by direction='in' (incoming edges)."""
    mock = MockGraphPort()
    code_node = _node(NodeKind.CODE, "mod.py")
    req_node = _node(NodeKind.REQUIREMENT, "FR-TRC-018")
    edge = GraphEdge(type=EdgeType.IMPLEMENTS, src=code_node, dst=req_node)
    mock.upsert_edge(edge)

    incoming = mock.neighbors(req_node, direction="in")
    assert len(incoming) == 1
    assert incoming[0].src == code_node


def test_mock_graph_port_neighbors_filters_by_edge_type():
    """Verify neighbors() can filter by edge_type parameter."""
    mock = MockGraphPort()
    code_node = _node(NodeKind.CODE, "mod.py")
    req_node = _node(NodeKind.REQUIREMENT, "FR-TRC-018")
    test_node = _node(NodeKind.TEST, "test.py")

    mock.upsert_edge(GraphEdge(type=EdgeType.IMPLEMENTS, src=code_node, dst=req_node))
    mock.upsert_edge(GraphEdge(type=EdgeType.COVERS, src=test_node, dst=code_node))

    implements_only = mock.neighbors(code_node, edge_type=EdgeType.IMPLEMENTS)
    assert len(implements_only) == 1
    assert implements_only[0].type == EdgeType.IMPLEMENTS


# ============================================================================
# Multiple implementations and strategy pattern tests
# ============================================================================


class AlternativeGraphPort:
    """An alternative GraphPort implementation for strategy pattern testing."""

    def __init__(self) -> None:
        self.store: list[tuple[str, str]] = []

    def upsert_node(self, node: GraphNode) -> None:
        validated = validate_node(node)
        self.store.append(("node", validated.id))

    def upsert_edge(self, edge: GraphEdge) -> None:
        validated = validate_edge(edge)
        self.store.append(("edge", f"{validated.src.id}-{validated.dst.id}"))

    def upsert_nodes(self, nodes: Sequence[GraphNode]) -> None:
        for n in nodes:
            self.upsert_node(n)

    def upsert_edges(self, edges: Sequence[GraphEdge]) -> None:
        for e in edges:
            self.upsert_edge(e)

    def neighbors(
        self,
        node: GraphNode,
        *,
        edge_type: EdgeType | None = None,
        direction: str = "out",
    ) -> Sequence[GraphEdge]:
        return []


def test_multiple_graph_port_implementations_are_interchangeable():
    """Verify strategy pattern: any GraphPort impl is usable at call site."""

    def write_requirement_link(port: GraphPort, code_id: str, req_id: str) -> None:
        code = _node(NodeKind.CODE, code_id)
        req = _node(NodeKind.REQUIREMENT, req_id)
        port.upsert_nodes([code, req])
        port.upsert_edge(GraphEdge(type=EdgeType.IMPLEMENTS, src=code, dst=req))

    mock1 = MockGraphPort()
    write_requirement_link(mock1, "mod.py", "FR-TRC-018")
    assert len(mock1.nodes) == 2

    alt = AlternativeGraphPort()
    write_requirement_link(alt, "mod.py", "FR-TRC-018")
    assert len(alt.store) == 3


# ============================================================================
# Existing validation tests (from original suite)
# ============================================================================


def test_canonical_vocabulary_is_closed_and_nonempty():
    assert CANONICAL_NODE_KINDS == frozenset(NodeKind)
    assert CANONICAL_EDGE_TYPES == frozenset(EdgeType)
    assert NodeKind.REQUIREMENT in CANONICAL_NODE_KINDS
    assert EdgeType.TRACES_TO in CANONICAL_EDGE_TYPES


def test_validate_node_accepts_canonical_node():
    n = _node(NodeKind.REQUIREMENT, "FR-TRC-018")
    assert validate_node(n) is n


def test_validate_node_rejects_empty_id():
    with pytest.raises(SchemaContractError):
        validate_node(GraphNode(kind=NodeKind.CODE, id="   "))


def test_validate_edge_accepts_valid_endpoints():
    edge = GraphEdge(
        type=EdgeType.IMPLEMENTS,
        src=_node(NodeKind.CODE, "mod.py"),
        dst=_node(NodeKind.REQUIREMENT, "FR-TRC-018"),
    )
    assert validate_edge(edge) is edge


def test_validate_edge_rejects_bad_source_kind():
    # A Requirement cannot IMPLEMENTS another node.
    edge = GraphEdge(
        type=EdgeType.IMPLEMENTS,
        src=_node(NodeKind.REQUIREMENT, "FR-TRC-018"),
        dst=_node(NodeKind.REQUIREMENT, "FR-TRC-019"),
    )
    with pytest.raises(SchemaContractError):
        validate_edge(edge)


def test_validate_edge_rejects_bad_target_kind():
    # COVERS must point at Requirement/Code/Spec, not a PR.
    edge = GraphEdge(
        type=EdgeType.COVERS,
        src=_node(NodeKind.TEST, "t1"),
        dst=_node(NodeKind.PR, "pr-1"),
    )
    with pytest.raises(SchemaContractError):
        validate_edge(edge)


def test_open_ended_edges_allow_any_endpoints():
    edge = GraphEdge(
        type=EdgeType.TRACES_TO,
        src=_node(NodeKind.PR, "pr-1"),
        dst=_node(NodeKind.OKR, "okr-1"),
    )
    assert validate_edge(edge) is edge


def test_graph_port_is_runtime_checkable_protocol():
    class _InMemoryGraph:
        def __init__(self) -> None:
            self.nodes: list[GraphNode] = []
            self.edges: list[GraphEdge] = []

        def upsert_node(self, node):
            self.nodes.append(validate_node(node))

        def upsert_edge(self, edge):
            self.edges.append(validate_edge(edge))

        def upsert_nodes(self, nodes):
            for n in nodes:
                self.upsert_node(n)

        def upsert_edges(self, edges):
            for e in edges:
                self.upsert_edge(e)

        def neighbors(self, node, *, edge_type=None, direction="out"):
            return [
                e
                for e in self.edges
                if (e.src == node if direction == "out" else e.dst == node)
                and (edge_type is None or e.type == edge_type)
            ]

    g = _InMemoryGraph()
    assert isinstance(g, GraphPort)
    g.upsert_edge(
        GraphEdge(
            type=EdgeType.IMPLEMENTS,
            src=_node(NodeKind.CODE, "graph_contract.py"),
            dst=_node(NodeKind.REQUIREMENT, "FR-TRC-018"),
        )
    )
    assert len(g.neighbors(_node(NodeKind.CODE, "graph_contract.py"))) == 1
