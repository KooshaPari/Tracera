"""Traceability quality scoring API route.

Exposes a read-only GET endpoint over an in-memory graph snapshot.

Endpoint
--------
GET /api/v1/quality/score
    Accept artifact + link arrays in request body (JSON) and return the full
    :class:`~tracertm.services.traceability_score_service.TraceabilityScoreReport`.

Functional Requirements: FR-TRC-017
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from tracertm.api.deps import auth_guard
from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.traceability_score_service import (
    PerRequirementScore,
    TraceabilityScoreReport,
    score_traceability,
)

router: APIRouter = APIRouter(prefix="/quality", tags=["Quality"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ArtifactIn(BaseModel):
    """Minimal artifact payload for the scoring endpoint."""

    id: uuid.UUID
    project_id: uuid.UUID
    kind: ArtifactKind
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    external_id: str | None = None


class TraceLinkIn(BaseModel):
    """Minimal trace link payload for the scoring endpoint."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    project_id: uuid.UUID
    source_artifact_id: uuid.UUID
    target_artifact_id: uuid.UUID
    link_type: TraceLinkType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    rationale: str | None = None


class ScoreRequest(BaseModel):
    """Request body: graph snapshot to score."""

    artifacts: list[ArtifactIn] = Field(default_factory=list)
    links: list[TraceLinkIn] = Field(default_factory=list)


class PerRequirementScoreOut(BaseModel):
    """Per-requirement metrics in the response."""

    requirement_id: uuid.UUID
    title: str
    has_satisfies: bool
    has_verifies: bool
    is_orphan: bool
    link_count: int


class ScoreResponse(BaseModel):
    """Traceability health score response."""

    total_requirements: int
    total_artifacts: int
    total_links: int
    impl_coverage: float
    test_coverage: float
    orphan_req_pct: float
    orphan_art_pct: float
    avg_confidence: float
    composite: int
    orphan_requirements: list[PerRequirementScoreOut]
    unverified_requirements: list[PerRequirementScoreOut]
    per_requirement: list[PerRequirementScoreOut]


def _prs_to_out(prs: PerRequirementScore) -> PerRequirementScoreOut:
    return PerRequirementScoreOut(
        requirement_id=prs.requirement_id,
        title=prs.title,
        has_satisfies=prs.has_satisfies,
        has_verifies=prs.has_verifies,
        is_orphan=prs.is_orphan,
        link_count=prs.link_count,
    )


def _report_to_response(report: TraceabilityScoreReport) -> ScoreResponse:
    return ScoreResponse(
        total_requirements=report.total_requirements,
        total_artifacts=report.total_artifacts,
        total_links=report.total_links,
        impl_coverage=report.impl_coverage,
        test_coverage=report.test_coverage,
        orphan_req_pct=report.orphan_req_pct,
        orphan_art_pct=report.orphan_art_pct,
        avg_confidence=report.avg_confidence,
        composite=report.composite,
        orphan_requirements=[_prs_to_out(r) for r in report.orphan_requirements],
        unverified_requirements=[_prs_to_out(r) for r in report.unverified_requirements],
        per_requirement=[_prs_to_out(r) for r in report.per_requirement],
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get("/score", response_model=ScoreResponse)
async def get_traceability_score(
    body: ScoreRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> ScoreResponse:
    """Compute and return the traceability health score for a graph snapshot.

    Supply the artifact list and trace-link list in the request body; the
    service computes all metrics in-memory (no DB access required).

    Functional Requirements: FR-TRC-017
    """
    # Convert request payloads to domain value objects
    artifacts = [
        Artifact(
            id=a.id,
            project_id=a.project_id,
            kind=a.kind,
            title=a.title,
            description=a.description,
            external_id=a.external_id,
        )
        for a in body.artifacts
    ]
    links = [
        TraceLink(
            id=lnk.id,
            project_id=lnk.project_id,
            source_artifact_id=lnk.source_artifact_id,
            target_artifact_id=lnk.target_artifact_id,
            link_type=lnk.link_type,
            confidence=lnk.confidence,
            rationale=lnk.rationale,
        )
        for lnk in body.links
    ]

    report = score_traceability(artifacts, links)
    return _report_to_response(report)
