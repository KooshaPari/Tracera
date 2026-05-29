"""Neo4j projection writer for the canonical TraceLink domain.

This module is the *write-side* of FR-TRACE-003: it projects the
SQL-resident :mod:`tracertm.models.trace_link` value objects
(:class:`Artifact`, :class:`Requirement`, :class:`TraceLink`) into the
Neo4j graph using the declarative DDL defined by
:class:`tracertm.models.trace_link.Neo4jSchema`.

Design notes
------------
* All write operations use idempotent ``MERGE`` clauses so the projection
  is safe to replay from the SQL system of record (or from an event log).
  ``MERGE`` matches on the *node-key* ``(project_id, id)`` for artifacts
  and on the full triple ``(source, target, link_type)`` for trace edges.
* The writer accepts a ``neo4j.Driver`` (sync) — async callers should
  ``run_in_executor`` or use the async equivalent. We keep the surface
  sync because:

  1. The schema apply path runs at startup, not in a request loop.
  2. The first miner / RAG consumer (PR follow-up) batches writes via
     UNWIND, so per-call async overhead is not on the hot path.

* All MERGEs set ``updated_at = datetime()`` on both create and match so
  the projection retains a last-touched timestamp without requiring the
  caller to thread one through.

Functional Requirements: FR-TRACE-003 (Neo4j projection of the
traceability graph).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tracertm.models.trace_link import (
    Artifact,
    Neo4jSchema,
    Requirement,
    TraceLink,
)

if TYPE_CHECKING:
    from neo4j import Driver

__all__ = [
    "apply_schema",
    "write_artifact",
    "write_requirement",
    "write_link",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _artifact_properties(artifact: Artifact) -> dict[str, Any]:
    """Flatten an :class:`Artifact` into a Cypher-friendly property map.

    UUIDs are stringified (Neo4j has no native UUID type) and ``metadata``
    is left as a dict — the driver serialises it to a Neo4j map property.
    Datetimes are passed through; the driver converts them to
    ``DateTime`` values.
    """
    props: dict[str, Any] = {
        "id": str(artifact.id),
        "project_id": str(artifact.project_id),
        "kind": artifact.kind.value,
        "title": artifact.title,
        "description": artifact.description,
        "external_id": artifact.external_id,
        # Neo4j map properties must be primitive — JSON-encode nested dicts.
        "metadata_json": _safe_json(artifact.metadata),
        # Always pass created_at/updated_at so the Cypher coalesce() can fire.
        "created_at": artifact.created_at,
        "updated_at": artifact.updated_at,
    }
    return props


def _requirement_properties(req: Requirement) -> dict[str, Any]:
    """Extend the base artifact property map with Requirement-only fields."""
    props = _artifact_properties(req)
    props.update(
        {
            "status": req.status.value,
            "priority": req.priority,
            "rationale": req.rationale,
            "acceptance_criteria": list(req.acceptance_criteria),
            "verification_method": (
                req.verification_method.value
                if req.verification_method is not None
                else None
            ),
        }
    )
    return props


def _safe_json(value: dict[str, Any]) -> str:
    """JSON-encode ``value`` so it can be stored as a Neo4j string property.

    We keep nested metadata as an opaque JSON blob rather than a Neo4j
    map so that the SQL system-of-record stays canonical and we don't
    have to round-trip arbitrarily nested structures through Cypher.
    """
    import json

    return json.dumps(value, sort_keys=True, default=str)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def apply_schema(driver: Driver) -> None:
    """Apply :class:`Neo4jSchema` DDL to the target database.

    Runs every constraint and index statement from
    :meth:`Neo4jSchema.all_statements`. All statements use
    ``IF NOT EXISTS`` so this method is idempotent and safe to call at
    every application startup.

    Args:
        driver: An open ``neo4j.Driver`` connected to the target instance.
    """
    with driver.session() as session:
        for stmt in Neo4jSchema.all_statements():
            session.run(stmt)


def write_artifact(driver: Driver, artifact: Artifact) -> None:
    """Project an :class:`Artifact` node into Neo4j.

    Idempotent: matches on the ``(project_id, id)`` node key. The node
    receives both the umbrella ``:Artifact`` label and the kind-specific
    label (e.g. ``:Test``, ``:Code``) so kind-specific queries can use
    the narrower label without a property filter.

    Args:
        driver: An open ``neo4j.Driver``.
        artifact: The artifact value object to project.
    """
    kind_label = Neo4jSchema.node_label_for(artifact.kind)
    # Property names are static; ``kind_label`` is derived from a
    # validated enum value so it cannot inject arbitrary Cypher.
    # Neo4j 5.x requires ON CREATE SET / ON MATCH SET before any bare SET.
    cypher = (
        "MERGE (a:Artifact {project_id: $project_id, id: $id}) "
        "ON CREATE SET a.created_at = coalesce($created_at, datetime()) "
        f"ON MATCH SET a.updated_at = coalesce($updated_at, datetime()) "
        f"SET a:{kind_label}, "
        "    a.title = $title, "
        "    a.description = $description, "
        "    a.external_id = $external_id, "
        "    a.kind = $kind, "
        "    a.metadata_json = $metadata_json, "
        "    a.updated_at = coalesce($updated_at, datetime())"
    )
    with driver.session() as session:
        session.run(cypher, **_artifact_properties(artifact))


def write_requirement(driver: Driver, requirement: Requirement) -> None:
    """Project a :class:`Requirement` node into Neo4j.

    Idempotent on ``(project_id, id)``. Sets both ``:Artifact`` and
    ``:Requirement`` labels and persists the ISO 29148 lifecycle fields
    (``status``, ``priority``, ``rationale``, ``acceptance_criteria``,
    ``verification_method``).

    Args:
        driver: An open ``neo4j.Driver``.
        requirement: The requirement value object to project.
    """
    # Neo4j 5.x: ON CREATE SET / ON MATCH SET must precede any bare SET.
    cypher = (
        "MERGE (r:Artifact {project_id: $project_id, id: $id}) "
        "ON CREATE SET r.created_at = coalesce($created_at, datetime()) "
        "ON MATCH SET r.updated_at = coalesce($updated_at, datetime()) "
        "SET r:Requirement, "
        "    r.title = $title, "
        "    r.description = $description, "
        "    r.external_id = $external_id, "
        "    r.kind = $kind, "
        "    r.metadata_json = $metadata_json, "
        "    r.status = $status, "
        "    r.priority = $priority, "
        "    r.rationale = $rationale, "
        "    r.acceptance_criteria = $acceptance_criteria, "
        "    r.verification_method = $verification_method, "
        "    r.updated_at = coalesce($updated_at, datetime())"
    )
    with driver.session() as session:
        session.run(cypher, **_requirement_properties(requirement))


def write_link(driver: Driver, link: TraceLink) -> None:
    """Project a :class:`TraceLink` edge into Neo4j.

    Idempotent: matches on the (source, target, link_type) triple inside
    a single project. Updates ``confidence``, ``rationale``, ``metadata``
    and ``updated_at`` on every call.

    The relationship label is taken from
    :meth:`Neo4jSchema.relationship_label_for`, which returns the enum's
    value (already SCREAMING_SNAKE).

    Both endpoint nodes are ``MERGE``d on the ``:Artifact`` super-label so
    a link can be written even if the source/target artifact projection
    has not run yet — the endpoints will be created as bare Artifact
    nodes and back-filled by a later ``write_artifact`` / ``write_requirement``.

    Args:
        driver: An open ``neo4j.Driver``.
        link: The trace link value object to project.

    Raises:
        ValueError: If the link is a self-loop (already rejected by the
            :class:`TraceLink` model validator, but re-checked here for
            defence-in-depth at the persistence boundary).
    """
    if link.source_artifact_id == link.target_artifact_id:
        msg = "TraceLink source and target must differ"
        raise ValueError(msg)

    rel_label = Neo4jSchema.relationship_label_for(link.link_type)
    # ``rel_label`` comes from a validated enum value, so f-string
    # interpolation cannot inject arbitrary Cypher.
    # Neo4j 5.x: ON CREATE SET / ON MATCH SET must precede any bare SET.
    cypher = (
        "MERGE (src:Artifact {project_id: $project_id, id: $source_id}) "
        "MERGE (tgt:Artifact {project_id: $project_id, id: $target_id}) "
        f"MERGE (src)-[l:{rel_label} {{id: $link_id}}]->(tgt) "
        "ON CREATE SET l.created_at = coalesce($created_at, datetime()) "
        "ON MATCH SET l.updated_at = coalesce($updated_at, datetime()) "
        "SET l.project_id = $project_id, "
        "    l.confidence = $confidence, "
        "    l.rationale = $rationale, "
        "    l.metadata_json = $metadata_json, "
        "    l.updated_at = coalesce($updated_at, datetime())"
    )
    params: dict[str, Any] = {
        "project_id": str(link.project_id),
        "source_id": str(link.source_artifact_id),
        "target_id": str(link.target_artifact_id),
        "link_id": str(link.id),
        "confidence": float(link.confidence),
        "rationale": link.rationale,
        "metadata_json": _safe_json(link.metadata),
    }
    if link.created_at is not None:
        params["created_at"] = link.created_at
    else:
        params["created_at"] = None
    if link.updated_at is not None:
        params["updated_at"] = link.updated_at
    else:
        params["updated_at"] = None

    with driver.session() as session:
        session.run(cypher, **params)
