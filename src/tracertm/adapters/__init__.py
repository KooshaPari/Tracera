"""Canonical port adapters (concrete implementations of platform contracts).

This module houses all adapter implementations that satisfy :mod:`tracertm.ports`
protocols. Each adapter is a swappable strategy for a particular port.

Adapters can have external dependencies (Neo4j driver, ML libraries, etc.) that
are not allowed in the port definitions themselves.

Provided Adapters
-----------------
- :class:`Neo4jGraphAdapter` — Neo4j-backed implementation of :class:`~tracertm.ports.GraphPort`
  (Phase 1 migration from existing writer, per ``NFR-TRC-011``)

Examples
--------
>>> from tracertm.adapters import Neo4jGraphAdapter
>>> adapter = Neo4jGraphAdapter(uri="bolt://localhost:7687", user="neo4j", password="password")
>>> from tracertm.ports.graph_contract import GraphNode, NodeKind
>>> node = GraphNode(kind=NodeKind.REQUIREMENT, id="req-001", properties={"project_id": "p1"})
>>> adapter.upsert_node(node)
"""

from __future__ import annotations

__all__ = ["Neo4jGraphAdapter"]

try:
    from tracertm.adapters.neo4j_graph_adapter import Neo4jGraphAdapter
except ImportError:
    # neo4j driver not installed; defer error to first use
    Neo4jGraphAdapter = None  # type: ignore
