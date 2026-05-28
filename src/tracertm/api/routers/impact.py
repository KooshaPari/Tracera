"""Impact analysis API routes for TraceRTM.

Exposes Cypher-backed forward and reverse impact traversal over the Neo4j
trace-link graph.

Endpoints
---------
GET /api/v1/impact/forward/{artifact_id}
    Return all artifacts *downstream* of the given artifact (forward impact).

GET /api/v1/impact/reverse/{artifact_id}
    Return all artifacts *upstream* of the given artifact (reverse impact).

Functional Requirements: FR-TRACE-003
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from tracertm.api.deps import auth_guard
from tracertm.api.handlers.impact import (
    get_neo4j_driver,
    query_forward_impact,
    query_reverse_impact,
)

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
