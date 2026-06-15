"""Canonical platform ports (hexagonal driven ports) for Tracera.

This package is the Python mirror of the canonical port contracts described in
``docs/TRACERA_PLATFORM_RND.md`` (the 4-pillar platform blueprint, PR #493) and
registered as requirements ``FR-TRC-018`` / ``FR-TRC-019`` in
``docs/requirements/tracera-frnfr.md``.

Pillar-A spine (Phase 0) deliverables scaffolded here:

* :mod:`tracertm.ports.graph_contract` -- the single canonical typed-graph schema
  contract (node kinds, edge types) plus the :class:`GraphPort` protocol that is
  intended to be the *sole* writer of graph truth (``NFR-TRC-010``).
* :mod:`tracertm.ports.scorer` -- the pluggable :class:`ScorerPort` strategy
  interface for requirement<->artifact agreement scoring, with a dependency-free
  reference implementation (:class:`JaccardScorer`). Embedding/visual strategies
  (SentenceTransformer / SigLIP / VLM) plug in behind the same port.

These are *contracts and scaffolding only*; wiring the ~12 existing trace/impact
services onto ``GraphPort`` is the migration tracked by ``EPIC-TRC-A-SPINE``.
"""

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
from tracertm.ports.scorer import (
    JaccardScorer,
    ScorerPort,
    ScoreResult,
)

__all__ = [
    # graph contract
    "NodeKind",
    "EdgeType",
    "GraphNode",
    "GraphEdge",
    "GraphPort",
    "SchemaContractError",
    "CANONICAL_NODE_KINDS",
    "CANONICAL_EDGE_TYPES",
    "validate_node",
    "validate_edge",
    # scorer
    "ScorerPort",
    "ScoreResult",
    "JaccardScorer",
]
