"""Unit tests for Neo4jGraphAdapter (NFR-TRC-011 Phase 1).

Tests verify that:
1. The adapter implements GraphPort protocol (duck-typing)
2. The adapter raises ImportError when neo4j is not installed
3. The adapter initializes the driver lazily (not in __init__)
4. Each method delegates correctly to the underlying writer
5. The adapter name and module match expectations
"""

from __future__ import annotations

import sys
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from tracertm.adapters.neo4j_graph_adapter import (
    Neo4jGraphAdapter,
    Neo4jAdapterError,
)
from tracertm.ports.graph_contract import (
    GraphEdge,
    GraphNode,
    NodeKind,
    EdgeType,
)


class TestNeo4jGraphAdapterProtocolCompliance:
    """Verify that Neo4jGraphAdapter implements the GraphPort protocol."""

    def test_adapter_has_upsert_node_method(self) -> None:
        """Verify adapter has upsert_node method."""
        assert hasattr(Neo4jGraphAdapter, "upsert_node")
        assert callable(getattr(Neo4jGraphAdapter, "upsert_node"))

    def test_adapter_has_upsert_edge_method(self) -> None:
        """Verify adapter has upsert_edge method."""
        assert hasattr(Neo4jGraphAdapter, "upsert_edge")
        assert callable(getattr(Neo4jGraphAdapter, "upsert_edge"))

    def test_adapter_has_upsert_nodes_method(self) -> None:
        """Verify adapter has upsert_nodes method."""
        assert hasattr(Neo4jGraphAdapter, "upsert_nodes")
        assert callable(getattr(Neo4jGraphAdapter, "upsert_nodes"))

    def test_adapter_has_upsert_edges_method(self) -> None:
        """Verify adapter has upsert_edges method."""
        assert hasattr(Neo4jGraphAdapter, "upsert_edges")
        assert callable(getattr(Neo4jGraphAdapter, "upsert_edges"))

    def test_adapter_has_neighbors_method(self) -> None:
        """Verify adapter has neighbors method (impact/blast-radius query)."""
        assert hasattr(Neo4jGraphAdapter, "neighbors")
        assert callable(getattr(Neo4jGraphAdapter, "neighbors"))

    def test_adapter_method_signatures_match_protocol(self) -> None:
        """Verify method signatures include all required parameters."""
        import inspect

        # upsert_node(node: GraphNode) -> None
        sig = inspect.signature(Neo4jGraphAdapter.upsert_node)
        assert "node" in sig.parameters

        # neighbors(node, edge_type=None, direction="out") -> Sequence[GraphEdge]
        sig_neighbors = inspect.signature(Neo4jGraphAdapter.neighbors)
        assert "node" in sig_neighbors.parameters
        assert "edge_type" in sig_neighbors.parameters
        assert "direction" in sig_neighbors.parameters


class TestNeo4jGraphAdapterInitialization:
    """Verify adapter initialization (with lazy driver)."""

    def test_adapter_initializes_with_uri_user_password(self) -> None:
        """Verify adapter accepts connection parameters."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password123",
        )
        assert adapter._uri == "bolt://localhost:7687"
        assert adapter._user == "neo4j"
        assert adapter._password == "password123"

    def test_adapter_driver_is_none_after_init(self) -> None:
        """Verify driver is None before first use (lazy initialization)."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password123",
        )
        assert adapter._driver is None

    def test_adapter_raises_on_missing_neo4j_package(self) -> None:
        """Verify adapter raises ImportError if neo4j is not installed.

        This test mocks the import of neo4j to simulate it being unavailable.
        """
        # Create a module mock that raises ImportError
        with patch.dict(sys.modules, {"neo4j": None}):
            with pytest.raises(ImportError, match="neo4j"):
                Neo4jGraphAdapter(
                    uri="bolt://localhost:7687",
                    user="neo4j",
                    password="password",
                )


class TestNeo4jGraphAdapterLazyInitialization:
    """Verify lazy driver initialization on first call."""

    def test_adapter_creates_driver_on_first_call(self) -> None:
        """Verify driver is created on first graph operation."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        # Mock the GraphDatabase.driver to return a fake driver
        with patch("neo4j.GraphDatabase.driver") as mock_driver_factory:
            mock_driver = MagicMock()
            mock_driver_factory.return_value = mock_driver

            # Patch the storage port to avoid actual Neo4j calls
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                node = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                adapter.upsert_node(node)

                # Verify driver was created
                mock_driver_factory.assert_called_once()
                assert adapter._driver is not None

    def test_adapter_reuses_driver_on_subsequent_calls(self) -> None:
        """Verify driver is reused, not recreated on subsequent calls."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver") as mock_driver_factory:
            mock_driver = MagicMock()
            mock_driver_factory.return_value = mock_driver

            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                node1 = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                node2 = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-002",
                    properties={"project_id": "proj-001"},
                )

                adapter.upsert_node(node1)
                adapter.upsert_node(node2)

                # Driver factory called only once
                assert mock_driver_factory.call_count == 1


class TestNeo4jGraphAdapterUpsertOperations:
    """Verify upsert operations delegate to underlying port."""

    def test_upsert_node_calls_underlying_port(self) -> None:
        """Verify upsert_node delegates to Neo4jGraphPort."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                node = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                adapter.upsert_node(node)

                mock_port.upsert_node.assert_called_once_with(node)

    def test_upsert_edge_calls_underlying_port(self) -> None:
        """Verify upsert_edge delegates to Neo4jGraphPort."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                src = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                dst = GraphNode(
                    kind=NodeKind.CODE,
                    id="code-001",
                    properties={"project_id": "proj-001"},
                )
                edge = GraphEdge(
                    type=EdgeType.IMPLEMENTS,
                    src=src,
                    dst=dst,
                    properties={"project_id": "proj-001", "link_id": "link-001"},
                )
                adapter.upsert_edge(edge)

                mock_port.upsert_edge.assert_called_once_with(edge)

    def test_upsert_nodes_calls_underlying_port(self) -> None:
        """Verify upsert_nodes delegates to Neo4jGraphPort."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                nodes = [
                    GraphNode(
                        kind=NodeKind.REQUIREMENT,
                        id="req-001",
                        properties={"project_id": "proj-001"},
                    ),
                    GraphNode(
                        kind=NodeKind.REQUIREMENT,
                        id="req-002",
                        properties={"project_id": "proj-001"},
                    ),
                ]
                adapter.upsert_nodes(nodes)

                mock_port.upsert_nodes.assert_called_once_with(nodes)

    def test_upsert_edges_calls_underlying_port(self) -> None:
        """Verify upsert_edges delegates to Neo4jGraphPort."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                src = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                dst = GraphNode(
                    kind=NodeKind.CODE,
                    id="code-001",
                    properties={"project_id": "proj-001"},
                )
                edges = [
                    GraphEdge(
                        type=EdgeType.IMPLEMENTS,
                        src=src,
                        dst=dst,
                        properties={"project_id": "proj-001", "link_id": "link-001"},
                    ),
                ]
                adapter.upsert_edges(edges)

                mock_port.upsert_edges.assert_called_once_with(edges)


class TestNeo4jGraphAdapterNeighborsQuery:
    """Verify neighbors (impact/blast-radius) query."""

    def test_neighbors_calls_underlying_port(self) -> None:
        """Verify neighbors delegates to Neo4jGraphPort."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port.neighbors.return_value = []
                mock_port_cls.return_value = mock_port

                node = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                adapter.neighbors(node, edge_type=EdgeType.IMPLEMENTS, direction="out")

                mock_port.neighbors.assert_called_once_with(
                    node, edge_type=EdgeType.IMPLEMENTS, direction="out"
                )

    def test_neighbors_respects_direction_parameter(self) -> None:
        """Verify neighbors respects direction parameter."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port.neighbors.return_value = []
                mock_port_cls.return_value = mock_port

                node = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                for direction in ["out", "in", "both"]:
                    adapter.neighbors(node, direction=direction)
                    mock_port.neighbors.assert_called_with(
                        node, edge_type=None, direction=direction
                    )


class TestNeo4jGraphAdapterContextManager:
    """Verify context manager support for resource cleanup."""

    def test_adapter_supports_context_manager(self) -> None:
        """Verify adapter can be used with 'with' statement."""
        with patch("neo4j.GraphDatabase.driver"):
            with Neo4jGraphAdapter(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="password",
            ) as adapter:
                assert adapter is not None

    def test_adapter_closes_driver_on_context_exit(self) -> None:
        """Verify driver is closed when exiting context."""
        with patch("neo4j.GraphDatabase.driver") as mock_driver_factory:
            mock_driver = MagicMock()
            mock_driver_factory.return_value = mock_driver

            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port_cls.return_value = mock_port

                with Neo4jGraphAdapter(
                    uri="bolt://localhost:7687",
                    user="neo4j",
                    password="password",
                ) as adapter:
                    node = GraphNode(
                        kind=NodeKind.REQUIREMENT,
                        id="req-001",
                        properties={"project_id": "proj-001"},
                    )
                    adapter.upsert_node(node)

                # After exiting context, driver should be closed
                mock_driver.close.assert_called_once()


class TestNeo4jGraphAdapterErrorHandling:
    """Verify error handling and exception propagation."""

    def test_adapter_raises_neo4j_adapter_error_on_driver_failure(self) -> None:
        """Verify adapter raises Neo4jAdapterError if driver fails."""
        adapter = Neo4jGraphAdapter(
            uri="bolt://invalid:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver") as mock_driver_factory:
            mock_driver_factory.side_effect = RuntimeError("Connection failed")

            with pytest.raises(Neo4jAdapterError, match="Failed to initialize"):
                node = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                adapter.upsert_node(node)

    def test_adapter_propagates_schema_contract_error(self) -> None:
        """Verify adapter propagates SchemaContractError from port."""
        from tracertm.ports.graph_contract import SchemaContractError

        adapter = Neo4jGraphAdapter(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
        )

        with patch("neo4j.GraphDatabase.driver"):
            with patch(
                "tracertm.adapters.neo4j_graph_adapter.Neo4jGraphPort"
            ) as mock_port_cls:
                mock_port = MagicMock()
                mock_port.upsert_node.side_effect = SchemaContractError(
                    "Invalid node kind"
                )
                mock_port_cls.return_value = mock_port

                node = GraphNode(
                    kind=NodeKind.REQUIREMENT,
                    id="req-001",
                    properties={"project_id": "proj-001"},
                )
                with pytest.raises(SchemaContractError):
                    adapter.upsert_node(node)


class TestNeo4jGraphAdapterModuleExports:
    """Verify module-level exports and discoverability."""

    def test_adapter_exported_from_adapters_module(self) -> None:
        """Verify Neo4jGraphAdapter is exported from tracertm.adapters."""
        from tracertm.adapters import Neo4jGraphAdapter as Exported

        assert Exported is Neo4jGraphAdapter

    def test_adapter_error_exported_from_module(self) -> None:
        """Verify Neo4jAdapterError is exported."""
        from tracertm.adapters.neo4j_graph_adapter import Neo4jAdapterError

        assert issubclass(Neo4jAdapterError, Exception)

    def test_adapter_has_docstring(self) -> None:
        """Verify adapter class has comprehensive docstring."""
        assert Neo4jGraphAdapter.__doc__ is not None
        assert "NFR-TRC-011" in Neo4jGraphAdapter.__doc__
        assert "GraphPort" in Neo4jGraphAdapter.__doc__

    def test_adapter_methods_have_docstrings(self) -> None:
        """Verify all public methods have docstrings."""
        public_methods = [
            "upsert_node",
            "upsert_edge",
            "upsert_nodes",
            "upsert_edges",
            "neighbors",
            "close",
        ]
        for method_name in public_methods:
            method = getattr(Neo4jGraphAdapter, method_name)
            assert method.__doc__ is not None, f"{method_name} missing docstring"
