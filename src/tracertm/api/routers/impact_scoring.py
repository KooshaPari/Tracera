"""Blast-radius / risk-weighted impact scoring endpoints — FR-TRC-015.

POST /api/v1/impact/blast-radius
    Compute risk-weighted blast radius for an artifact over an in-memory
    TraceLink graph supplied in the request body (pure function, no DB).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from tracertm.api.deps import auth_guard
from tracertm.models.trace_link import Artifact, TraceLink
from tracertm.services.blast_radius_service import BlastRadiusResult, compute_blast_radius

router = APIRouter(prefix="/impact", tags=["impact"])


class BlastRadiusRequest(BaseModel):
    """Request body for blast-radius scoring."""

    model_config = ConfigDict(strict=True, extra="forbid")

    artifact_id: str = Field(min_length=1)
    artifacts: list[Artifact] = Field(default_factory=list)
    links: list[TraceLink] = Field(default_factory=list)
    depth: int = Field(default=5, ge=1, le=20)


@router.post("/blast-radius")
async def blast_radius(
    body: BlastRadiusRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> BlastRadiusResult:
    """Compute risk-weighted blast radius for the given artifact.

    The trace-link graph and artifact metadata are supplied in the request so
    the endpoint is a pure read-only computation over caller-provided data.
    """
    artifacts_map: dict[str, Artifact] = {str(a.id): a for a in body.artifacts}
    graph: dict[str, list[TraceLink]] = {}
    for link in body.links:
        source_id = str(link.source_artifact_id)
        graph.setdefault(source_id, []).append(link)

    return compute_blast_radius(
        body.artifact_id,
        graph,
        artifacts_map,
        depth=body.depth,
    )
