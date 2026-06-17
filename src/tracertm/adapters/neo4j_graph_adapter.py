"""Neo4j implementation of GraphPort (Phase 1 migration, ``NFR-TRC-011``).

This adapter wraps the existing :mod:`tracertm.storage.neo4j_trace_link_writer`
to implement the canonical :class:`~tracertm.ports.GraphPort` contract. It ensures
all graph mutations flow through validated node/edge types before reaching Neo4j
(``NFR-TRC-010``).

The adapter translates canonical :class:`~tracertm.ports.GraphNode` and
:class:`~tracertm.ports.GraphEdge` value objects into the legacy
:class:`~tracertm.models.trace_link.Artifact` / :class:`~tracertm.models.trace_link.TraceLink`
format the writer understands. Vocabulary mapping is explicit and closed — unmapped
kinds raise :class:`~tracertm.ports.SchemaContractError` at the boundary rather than
silently inventing labels.

The adapter implements lazy driver initialization: the Neo4j driver is created
on first use, not in ``__init__``. This allows testing and inspection without
requiring a live database connection.

Examples
--------
>>> from tracertm.adapters import Neo4jGraphAdapter
>>> from tracertm.ports.graph_contract import GraphNode, NodeKind
>>> adapter = Neo4jGraphAdapter(
...     uri="bolt://localhost:7687",
...     user="neo4j",
...     password="your_password"
... )
>>> node = GraphNode(
...     kind=NodeKind.REQUIREMENT,
...     id="req-2026-001",
...     properties={
...         "project_id": "project-alpha",
...         "title": "Core System Requirement",
...         "description": "A fundamental requirement"
...     }
... )
>>> adapter.upsert_node(node)  # Driver created on first call
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Sequence

from tracertm.ports.graph_contract import (
    EdgeType,
    GraphEdge,
    GraphNode,
    GraphPort,
    NodeKind,
)

if TYPE_CHECKING:
    from neo4j import Driver

__all__ = ["Neo4jGraphAdapter", "Neo4jAdapterError"]


class Neo4jAdapterError(Exception):
    """Raised when the Neo4j driver is not available or cannot initialize."""


class Neo4jGraphAdapter:
    """Neo4j implementation of :class:`~tracertm.ports.GraphPort` (Phase 1).

    This adapter satisfies the ``GraphPort`` protocol by implementing all required
    methods: upsert_node, upsert_edge, upsert_nodes, upsert_edges, and neighbors.

    The driver is initialized lazily on the first graph operation, allowing the
    adapter to be instantiated without requiring a live database connection.

    Parameters
    ----------
    uri : str
        Neo4j connection URI (e.g., "bolt://localhost:7687" or "neo4j+ssc://...").
    user : str
        Neo4j username for authentication.
    password : str
        Neo4j password for authentication.

    Raises
    ------
    ImportError
        If the ``neo4j`` package is not installed.
    Neo4jAdapterError
        If the driver cannot connect to the database on first use.

    Notes
    -----
    This is a Phase 1 implementation (``NFR-TRC-011``) that wraps the existing
    trace-link writer. Future phases may replace the writer with direct Cypher
    query construction for better performance.
    """

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._driver: Driver | None = None
        self._validate_neo4j_available()

    @staticmethod
    def _validate_neo4j_available() -> None:
        """Raise ImportError if neo4j package is not installed."""
        try:
            import neo4j  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "Neo4j GraphPort adapter requires 'neo4j' package. "
                "Install it with: pip install neo4j"
            ) from e

    def _ensure_driver(self) -> Driver:
        """Lazily initialize and return the Neo4j driver.

        Returns
        -------
        Driver
            An initialized neo4j.Driver instance.

        Raises
        ------
        Neo4jAdapterError
            If the driver cannot connect or initialize.
        """
        if self._driver is not None:
            return self._driver

        try:
            import neo4j
        except ImportError as e:
            raise Neo4jAdapterError(
                "neo4j package is not installed"
            ) from e

        try:
            self._driver = neo4j.GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password),
                encrypted=True,
            )
        except Exception as e:
            raise Neo4jAdapterError(
                f"Failed to initialize Neo4j driver for {self._uri}: {e}"
            ) from e

        return self._driver

    def upsert_node(self, node: GraphNode) -> None:
        """Create or update a single canonical node.

        Validates the node against the schema contract, then delegates to the
        existing trace-link writer (``tracertm.storage.neo4j_trace_link_writer``).

        Parameters
        ----------
        node : GraphNode
            A typed, validated node to upsert.

        Raises
        ------
        SchemaContractError
            If the node violates the canonical schema.
        Neo4jAdapterError
            If the driver cannot connect or the write fails.
        """
        from tracertm.storage.neo4j_graph_port import (
            Neo4jGraphPort,
            GraphPortAdapterError,
        )

        try:
            driver = self._ensure_driver()
            port = Neo4jGraphPort(driver)
            port.upsert_node(node)
        except GraphPortAdapterError:
            raise
        except Exception as e:
            raise Neo4jAdapterError(f"Failed to upsert node {node.id}: {e}") from e

    def upsert_edge(self, edge: GraphEdge) -> None:
        """Create or update a single canonical, directed edge.

        Validates the edge against the schema contract (including endpoint kinds),
        then delegates to the existing trace-link writer.

        Parameters
        ----------
        edge : GraphEdge
            A typed, validated edge to upsert.

        Raises
        ------
        SchemaContractError
            If the edge violates the canonical schema.
        Neo4jAdapterError
            If the driver cannot connect or the write fails.
        """
        from tracertm.storage.neo4j_graph_port import (
            Neo4jGraphPort,
            GraphPortAdapterError,
        )

        try:
            driver = self._ensure_driver()
            port = Neo4jGraphPort(driver)
            port.upsert_edge(edge)
        except GraphPortAdapterError:
            raise
        except Exception as e:
            raise Neo4jAdapterError(
                f"Failed to upsert edge {edge.src.id}-[{edge.type.value}]->{edge.dst.id}: {e}"
            ) from e

    def upsert_nodes(self, nodes: Sequence[GraphNode]) -> None:
        """Bulk node upsert.

        Parameters
        ----------
        nodes : Sequence[GraphNode]
            A sequence of validated nodes to upsert.

        Raises
        ------
        SchemaContractError
            If any node violates the canonical schema.
        Neo4jAdapterError
            If the driver cannot connect or any write fails.
        """
        from tracertm.storage.neo4j_graph_port import (
            Neo4jGraphPort,
            GraphPortAdapterError,
        )

        try:
            driver = self._ensure_driver()
            port = Neo4jGraphPort(driver)
            port.upsert_nodes(nodes)
        except GraphPortAdapterError:
            raise
        except Exception as e:
            raise Neo4jAdapterError(
                f"Failed to upsert {len(nodes)} nodes: {e}"
            ) from e

    def upsert_edges(self, edges: Sequence[GraphEdge]) -> None:
        """Bulk edge upsert.

        Parameters
        ----------
        edges : Sequence[GraphEdge]
            A sequence of validated edges to upsert.

        Raises
        ------
        SchemaContractError
            If any edge violates the canonical schema.
        Neo4jAdapterError
            If the driver cannot connect or any write fails.
        """
        from tracertm.storage.neo4j_graph_port import (
            Neo4jGraphPort,
            GraphPortAdapterError,
        )

        try:
            driver = self._ensure_driver()
            port = Neo4jGraphPort(driver)
            port.upsert_edges(edges)
        except GraphPortAdapterError:
            raise
        except Exception as e:
            raise Neo4jAdapterError(
                f"Failed to upsert {len(edges)} edges: {e}"
            ) from e

    def neighbors(
        self,
        node: GraphNode,
        *,
        edge_type: EdgeType | None = None,
        direction: str = "out",
    ) -> Sequence[GraphEdge]:
        """Return edges incident to a node (impact/blast-radius queries).

        Parameters
        ----------
        node : GraphNode
            The node to query neighbors for.
        edge_type : EdgeType | None, optional
            If specified, filter results to only this edge type.
        direction : str, default "out"
            Direction of traversal: "out" (downstream), "in" (upstream), or "both".

        Returns
        -------
        Sequence[GraphEdge]
            A sequence of edges incident to the node.

        Raises
        ------
        ValueError
            If ``direction`` is not "out", "in", or "both".
        SchemaContractError
            If the node violates the canonical schema.
        Neo4jAdapterError
            If the driver cannot connect or the query fails.
        """
        from tracertm.storage.neo4j_graph_port import (
            Neo4jGraphPort,
            GraphPortAdapterError,
        )

        try:
            driver = self._ensure_driver()
            port = Neo4jGraphPort(driver)
            return port.neighbors(node, edge_type=edge_type, direction=direction)
        except GraphPortAdapterError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise Neo4jAdapterError(
                f"Failed to query neighbors for {node.id}: {e}"
            ) from e

    def close(self) -> None:
        """Close the underlying Neo4j driver connection.

        This method should be called when the adapter is no longer needed to
        gracefully shut down the database connection.
        """
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def __enter__(self) -> Neo4jGraphAdapter:
        """Context manager entry (for use with ``with`` statement)."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit (closes driver on exit)."""
        self.close()
