"""Cypher-based impact analysis handlers for TraceRTM.

Implements forward and reverse impact traversal over the Neo4j trace-link
graph using the canonical :class:`tracertm.models.trace_link.TraceLink`
relationship model.

Functional Requirements: FR-TRACE-003 (Neo4j projection query layer)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from neo4j import AsyncDriver

__all__ = [
    "get_neo4j_driver",
    "query_forward_impact",
    "query_reverse_impact",
]


def _neo4j_driver() -> AsyncDriver:
    """Create an async Neo4j driver from environment variables.

    Environment variables read:
    * ``NEO4J_URI``  — bolt/neo4j URI (default: ``neo4j://localhost:7687``)
    * ``NEO4J_USER`` — username (default: ``neo4j``)
    * ``NEO4J_PASSWORD`` — password (default: ``neo4j``)

    Returns:
        An open :class:`neo4j.AsyncDriver`.
    """
    from neo4j import AsyncGraphDatabase

    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "neo4j")
    return AsyncGraphDatabase.driver(uri, auth=(user, password))


async def get_neo4j_driver() -> AsyncDriver:
    """FastAPI dependency that yields a fresh async Neo4j driver per request.

    The driver is closed after the request completes.  For production usage,
    replace this with a module-level singleton; the interface is intentionally
    identical so callers need no changes.

    Yields:
        An open :class:`neo4j.AsyncDriver`.
    """
    driver = _neo4j_driver()
    try:
        yield driver
    finally:
        await driver.close()


# ---------------------------------------------------------------------------
# Cypher queries
# ---------------------------------------------------------------------------

# Forward impact: starting from ``artifact_id``, follow all outgoing trace
# relationships any number of hops and collect the downstream artifacts.
_FORWARD_CYPHER = """
MATCH (src:Artifact {id: $artifact_id})
MATCH (src)-[l*1..]->(affected:Artifact)
WHERE affected.id <> src.id
WITH DISTINCT affected, [rel IN l | type(rel)] AS link_types
RETURN
    affected.id          AS id,
    affected.project_id  AS project_id,
    affected.kind        AS kind,
    affected.title       AS title,
    affected.external_id AS external_id,
    link_types
ORDER BY affected.kind, affected.id
"""

# Reverse impact: starting from ``artifact_id``, follow all *incoming* trace
# relationships any number of hops and collect the upstream artifacts.
_REVERSE_CYPHER = """
MATCH (tgt:Artifact {id: $artifact_id})
MATCH (upstream:Artifact)-[l*1..]->(tgt)
WHERE upstream.id <> tgt.id
WITH DISTINCT upstream, [rel IN l | type(rel)] AS link_types
RETURN
    upstream.id          AS id,
    upstream.project_id  AS project_id,
    upstream.kind        AS kind,
    upstream.title       AS title,
    upstream.external_id AS external_id,
    link_types
ORDER BY upstream.kind, upstream.id
"""


def _row_to_artifact(record: Any) -> dict[str, Any]:
    """Convert a Neo4j result record to a JSON-serialisable artifact dict."""
    return {
        "id": record["id"],
        "project_id": record["project_id"],
        "kind": record["kind"],
        "title": record["title"],
        "external_id": record["external_id"],
        "via_link_types": list(record["link_types"]),
    }


async def query_forward_impact(
    driver: AsyncDriver,
    artifact_id: str,
) -> list[dict[str, Any]]:
    """Run the forward impact Cypher query and return affected artifacts.

    Traverses all *outgoing* :class:`~tracertm.models.trace_link.TraceLink`
    relationships from ``artifact_id`` (unbounded depth) to collect every
    downstream artifact that is transitively affected when the source artifact
    changes.

    Args:
        driver: An open :class:`neo4j.AsyncDriver`.
        artifact_id: UUID string of the source artifact.

    Returns:
        List of artifact dicts, each containing ``id``, ``project_id``,
        ``kind``, ``title``, ``external_id``, and ``via_link_types``.
    """
    async with driver.session() as session:
        result = await session.run(_FORWARD_CYPHER, artifact_id=artifact_id)
        records = await result.data()
    return [_row_to_artifact(r) for r in records]


async def query_reverse_impact(
    driver: AsyncDriver,
    artifact_id: str,
) -> list[dict[str, Any]]:
    """Run the reverse impact Cypher query and return upstream artifacts.

    Traverses all *incoming* :class:`~tracertm.models.trace_link.TraceLink`
    relationships to ``artifact_id`` (unbounded depth) to collect every
    upstream artifact that needs re-validation when the target artifact
    changes.

    Args:
        driver: An open :class:`neo4j.AsyncDriver`.
        artifact_id: UUID string of the target artifact.

    Returns:
        List of artifact dicts, each containing ``id``, ``project_id``,
        ``kind``, ``title``, ``external_id``, and ``via_link_types``.
    """
    async with driver.session() as session:
        result = await session.run(_REVERSE_CYPHER, artifact_id=artifact_id)
        records = await result.data()
    return [_row_to_artifact(r) for r in records]
