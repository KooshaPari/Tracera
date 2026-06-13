"""Unit tests for the Neo4j ``GraphPort`` adapter."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from tracertm.ports.graph_contract import (
    EdgeType,
    GraphEdge,
    GraphNode,
    GraphPort,
    NodeKind,
    SchemaContractError,
)
from tracertm.storage.neo4j_graph_port import GraphPortAdapterError, Neo4jGraphPort

_PROJECT = str(uuid.uuid4())
_CODE_ID = str(uuid.uuid4())
_REQ_ID = str(uuid.uuid4())


def _node(kind: NodeKind, id_: str, **props) -> GraphNode:
    base = {"project_id": _PROJECT, "title": f"{kind.value}-{id_}"}
    base.update(props)
    return GraphNode(kind=kind, id=id_, properties=base)


def test_neo4j_graph_port_satisfies_graph_port_protocol():
    driver = MagicMock()
    assert isinstance(Neo4jGraphPort(driver), GraphPort)


def test_upsert_node_validates_before_write():
    driver = MagicMock()
    port = Neo4jGraphPort(driver)
    with pytest.raises(SchemaContractError):
        port.upsert_node(GraphNode(kind=NodeKind.CODE, id="   ", properties={"project_id": _PROJECT}))


@patch("tracertm.storage.neo4j_graph_port._writer.write_artifact")
def test_upsert_code_node_delegates_to_writer(mock_write: MagicMock):
    driver = MagicMock()
    port = Neo4jGraphPort(driver)
    node = _node(NodeKind.CODE, _CODE_ID)
    port.upsert_node(node)
    mock_write.assert_called_once()
    assert mock_write.call_args[0][0] is driver
    artifact = mock_write.call_args[0][1]
    assert artifact.kind.value == "code"
    assert str(artifact.id) == _CODE_ID


@patch("tracertm.storage.neo4j_graph_port._writer.write_requirement")
def test_upsert_requirement_node_delegates_to_writer(mock_write: MagicMock):
    driver = MagicMock()
    port = Neo4jGraphPort(driver)
    node = _node(NodeKind.REQUIREMENT, _REQ_ID, status="draft")
    port.upsert_node(node)
    mock_write.assert_called_once()
    req = mock_write.call_args[0][1]
    assert req.kind.value == "requirement"


def test_upsert_unmapped_node_kind_raises():
    driver = MagicMock()
    port = Neo4jGraphPort(driver)
    with pytest.raises(GraphPortAdapterError, match="not yet projectable"):
        port.upsert_node(_node(NodeKind.TEAM, str(uuid.uuid4())))


@patch("tracertm.storage.neo4j_graph_port._writer.write_link")
def test_upsert_edge_maps_canonical_type(mock_write: MagicMock):
    driver = MagicMock()
    port = Neo4jGraphPort(driver)
    edge = GraphEdge(
        type=EdgeType.IMPLEMENTS,
        src=_node(NodeKind.CODE, _CODE_ID),
        dst=_node(NodeKind.REQUIREMENT, _REQ_ID),
        properties={"project_id": _PROJECT, "confidence": 0.9, "rationale": "implements"},
    )
    port.upsert_edge(edge)
    mock_write.assert_called_once()
    link = mock_write.call_args[0][1]
    assert link.link_type.value == "IMPLEMENTS"
    assert link.confidence == 0.9


def test_upsert_edge_rejects_invalid_endpoint_kinds():
    driver = MagicMock()
    port = Neo4jGraphPort(driver)
    edge = GraphEdge(
        type=EdgeType.IMPLEMENTS,
        src=_node(NodeKind.REQUIREMENT, _REQ_ID),
        dst=_node(NodeKind.REQUIREMENT, str(uuid.uuid4())),
        properties={"project_id": _PROJECT},
    )
    with pytest.raises(SchemaContractError):
        port.upsert_edge(edge)


def test_neighbors_returns_mapped_edges():
    driver = MagicMock()
    session = MagicMock()
    session.run.return_value = [
        {
            "rel_type": "IMPLEMENTS",
            "src_id": _CODE_ID,
            "dst_id": _REQ_ID,
            "src_kind": "code",
            "dst_kind": "requirement",
            "confidence": 1.0,
            "rationale": "ok",
        }
    ]

    @contextmanager
    def _session():
        yield session

    driver.session.return_value = _session()
    port = Neo4jGraphPort(driver)
    edges = port.neighbors(_node(NodeKind.CODE, _CODE_ID))
    assert len(edges) == 1
    assert edges[0].type is EdgeType.IMPLEMENTS
    assert edges[0].dst.kind is NodeKind.REQUIREMENT
