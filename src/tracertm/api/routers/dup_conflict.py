"""Duplicate and conflict detection API routes.

Exposes read-only quality-gate endpoints over an in-memory graph payload.

Endpoints
---------
POST /api/v1/quality/duplicates
    Detect near-duplicate requirements from a submitted list.

POST /api/v1/quality/conflicts
    Detect conflicting TraceLink pairs from a submitted list.

Functional Requirements: FR-TRC-012
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from tracertm.api.deps import auth_guard
from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.dup_conflict_detector import (
    ConflictFinding,
    DuplicateFinding,
    detect_conflicting_links,
    detect_duplicate_requirements,
)

router = APIRouter(prefix="/quality", tags=["quality"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class ArtifactPayload(BaseModel):
    """Wire format for an artifact submitted to the duplicates endpoint."""

    id: str
    project_id: str
    kind: ArtifactKind = ArtifactKind.REQUIREMENT
    title: str
    description: str | None = None
    external_id: str | None = None


class TraceLinkPayload(BaseModel):
    """Wire format for a TraceLink submitted to the conflicts endpoint."""

    id: str
    project_id: str
    source_artifact_id: str
    target_artifact_id: str
    link_type: TraceLinkType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    rationale: str | None = None


class DuplicatesRequest(BaseModel):
    """Request body for the duplicates endpoint."""

    artifacts: list[ArtifactPayload]
    threshold: float = Field(default=0.75, gt=0.0, le=1.0)


class ConflictsRequest(BaseModel):
    """Request body for the conflicts endpoint."""

    links: list[TraceLinkPayload]


class DuplicateFindingOut(BaseModel):
    """Serialisable duplicate finding."""

    artifact_a_id: str
    artifact_a_title: str
    artifact_b_id: str
    artifact_b_title: str
    similarity: float


class ConflictFindingOut(BaseModel):
    """Serialisable conflict finding."""

    link_a_id: str
    link_b_id: str
    source_artifact_id: str
    target_artifact_id: str
    link_type_a: str
    link_type_b: str
    confidence: float


class DuplicatesResponse(BaseModel):
    """Response for the duplicates endpoint."""

    threshold: float
    total: int
    findings: list[DuplicateFindingOut]


class ConflictsResponse(BaseModel):
    """Response for the conflicts endpoint."""

    total: int
    findings: list[ConflictFindingOut]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _finding_to_out(f: DuplicateFinding) -> DuplicateFindingOut:
    return DuplicateFindingOut(
        artifact_a_id=str(f.artifact_a_id),
        artifact_a_title=f.artifact_a_title,
        artifact_b_id=str(f.artifact_b_id),
        artifact_b_title=f.artifact_b_title,
        similarity=f.similarity,
    )


def _conflict_to_out(c: ConflictFinding) -> ConflictFindingOut:
    return ConflictFindingOut(
        link_a_id=str(c.link_a_id),
        link_b_id=str(c.link_b_id),
        source_artifact_id=str(c.source_artifact_id),
        target_artifact_id=str(c.target_artifact_id),
        link_type_a=c.link_type_a.value,
        link_type_b=c.link_type_b.value,
        confidence=c.confidence,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/duplicates",
    response_model=DuplicatesResponse,
    summary="Detect near-duplicate requirements",
    description=(
        "Accepts a list of Artifact/Requirement objects and returns pairs "
        "whose token-Jaccard similarity meets or exceeds *threshold*. "
        "FR-TRC-012."
    ),
)
async def detect_duplicates(
    body: DuplicatesRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> DuplicatesResponse:
    """Detect near-duplicate requirements via token-Jaccard similarity."""
    import uuid

    artifacts = [
        Artifact(
            id=uuid.UUID(a.id),
            project_id=uuid.UUID(a.project_id),
            kind=a.kind,
            title=a.title,
            description=a.description,
            external_id=a.external_id,
        )
        for a in body.artifacts
    ]
    findings = detect_duplicate_requirements(artifacts, threshold=body.threshold)
    return DuplicatesResponse(
        threshold=body.threshold,
        total=len(findings),
        findings=[_finding_to_out(f) for f in findings],
    )


@router.post(
    "/conflicts",
    response_model=ConflictsResponse,
    summary="Detect conflicting TraceLinks",
    description=(
        "Accepts a list of TraceLink objects and returns pairs that are "
        "mutually exclusive on the same (source, target) artifact pair. "
        "FR-TRC-012."
    ),
)
async def detect_conflicts(
    body: ConflictsRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> ConflictsResponse:
    """Detect mutually-exclusive TraceLink pairs."""
    import uuid

    links = [
        TraceLink(
            id=uuid.UUID(lp.id),
            project_id=uuid.UUID(lp.project_id),
            source_artifact_id=uuid.UUID(lp.source_artifact_id),
            target_artifact_id=uuid.UUID(lp.target_artifact_id),
            link_type=lp.link_type,
            confidence=lp.confidence,
            rationale=lp.rationale,
        )
        for lp in body.links
    ]
    findings = detect_conflicting_links(links)
    return ConflictsResponse(
        total=len(findings),
        findings=[_conflict_to_out(c) for c in findings],
    )
