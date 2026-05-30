"""Impact analysis API routes for TraceRTM.

Exposes Cypher-backed forward and reverse impact traversal over the Neo4j
trace-link graph, plus in-memory blast-radius / risk-weighted scoring.

Endpoints
---------
GET /api/v1/impact/forward/{artifact_id}
    Return all artifacts *downstream* of the given artifact (forward impact).

GET /api/v1/impact/reverse/{artifact_id}
    Return all artifacts *upstream* of the given artifact (reverse impact).

GET /api/v1/impact/blast-radius/{artifact_id}
    Return risk-weighted blast-radius score for the given artifact (FR-TRC-015).

Functional Requirements: FR-TRACE-003, FR-TRC-015
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from tracertm.api.deps import auth_guard
from tracertm.api.handlers.impact import (
    get_neo4j_driver,
    query_forward_impact,
    query_reverse_impact,
)
from tracertm.services.blast_radius_service import BlastRadiusResult, compute_blast_radius

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("/forward/{artifact_id}", summary="Forward impact of an artifact")
async def forward_impact(
    artifact_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    driver: Annotated[Any, Depends(get_neo4j_driver)],
) -> dict[str, Any]:
    """Return artifacts that are *affected by* changes to ``artifact_id``.

    Follows all outgoing trace-link relationships from the given artifact
    (unbounded depth, all relationship types) and returns every distinct
    downstream artifact.

    Args:
        artifact_id: UUID of the source artifact.

    Returns:
        JSON body with ``artifact_id``, ``direction``, ``total``, and
        ``affected`` list.
    """
    affected = await query_forward_impact(driver, artifact_id)
    return {
        "artifact_id": artifact_id,
        "direction": "forward",
        "total": len(affected),
        "affected": affected,
    }


@router.get("/reverse/{artifact_id}", summary="Reverse impact on an artifact")
async def reverse_impact(
    artifact_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    driver: Annotated[Any, Depends(get_neo4j_driver)],
) -> dict[str, Any]:
    """Return artifacts that *affect* the given ``artifact_id``.

    Follows all incoming trace-link relationships to the given artifact
    (unbounded depth, all relationship types) and returns every distinct
    upstream artifact that needs re-validation when the target changes.

    Args:
        artifact_id: UUID of the target artifact.

    Returns:
        JSON body with ``artifact_id``, ``direction``, ``total``, and
        ``upstream`` list.
    """
    upstream = await query_reverse_impact(driver, artifact_id)
    return {
        "artifact_id": artifact_id,
        "direction": "reverse",
        "total": len(upstream),
        "upstream": upstream,
    }


@router.get(
    "/blast-radius/{artifact_id}",
    summary="Risk-weighted blast-radius score for an artifact (FR-TRC-015)",
    response_model=None,
)
async def blast_radius(
    artifact_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    driver: Annotated[Any, Depends(get_neo4j_driver)],
    depth: int = Query(default=5, ge=1, le=20, description="Maximum traversal depth"),
) -> dict[str, Any]:
    """Compute risk-weighted blast-radius for ``artifact_id``.

    Uses the forward impact traversal (Neo4j trace-link graph) to determine
    the reachable downstream artifact set, then applies per-ArtifactKind risk
    weights and link-confidence factors to produce a normalised 0–100 score.

    A ``CRITICAL`` score (≥ 75) means changes to this artifact risk cascading
    regressions across a large, high-weight downstream surface.

    Args:
        artifact_id: UUID of the artifact whose change-impact is assessed.
        depth: Maximum BFS hops (default 5, max 20).

    Returns:
        JSON body with ``artifact_id``, ``blast_radius_score`` (0–100),
        ``risk_level`` (LOW/MEDIUM/HIGH/CRITICAL), ``affected_count``,
        ``affected_artifacts``, and ``critical_path``.
    """
    import uuid as _uuid

    from tracertm.models.trace_link import Artifact as _Artifact, ArtifactKind as _ArtifactKind, TraceLink as _TraceLink, TraceLinkType as _TraceLinkType

    # Retrieve the forward impact set from Neo4j.
    affected_rows = await query_forward_impact(driver, artifact_id)

    # Build a lightweight in-memory graph for the pure-function scorer.
    # Each Neo4j row gives us the downstream artifact; we synthesise a single
    # IMPLEMENTS link from artifact_id to each direct descendant so the
    # risk-weighting accounts for ArtifactKind differences.
    _proj_id = _uuid.uuid4()

    def _make_artifact(row: dict[str, Any]) -> _Artifact:
        kind = _ArtifactKind(row["kind"]) if row.get("kind") in _ArtifactKind.__members__ else _ArtifactKind.CODE
        return _Artifact(
            id=_uuid.UUID(row["id"]) if row.get("id") else _uuid.uuid4(),
            project_id=_proj_id,
            kind=kind,
            title=row.get("title", row.get("id", "unknown")),
            external_id=row.get("external_id"),
        )

    src_artifact_uuid = _uuid.UUID(artifact_id)
    artifacts: dict[str, _Artifact] = {}
    graph: dict[str, list[_TraceLink]] = {}

    for row in affected_rows:
        tgt_id = row.get("id", "")
        if not tgt_id:
            continue
        art = _make_artifact(row)
        artifacts[tgt_id] = art
        link = _TraceLink(
            id=_uuid.uuid4(),
            project_id=_proj_id,
            source_artifact_id=src_artifact_uuid,
            target_artifact_id=art.id,
            link_type=_TraceLinkType.IMPLEMENTS,
            confidence=1.0,
        )
        graph.setdefault(artifact_id, []).append(link)

    result = compute_blast_radius(artifact_id, graph, artifacts, depth=depth)

    return {
        "artifact_id": result.artifact_id,
        "blast_radius_score": result.blast_radius_score,
        "risk_level": result.risk_level,
        "affected_count": len(result.affected_artifacts),
        "affected_artifacts": result.affected_artifacts,
        "critical_path": result.critical_path,
    }
