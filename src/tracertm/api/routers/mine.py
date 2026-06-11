"""Requirement miner API routes.

Exposes a read-only endpoint that accepts raw source text or file paths and
returns extracted candidate Requirement statements with confidence scores.

Endpoints
---------
POST /api/v1/mine/requirements
    Accept ``text`` (raw source text) and/or ``paths`` (absolute/relative
    file paths readable by the server process).  Returns a list of
    ``CandidateRequirementOut`` records sorted descending by confidence.

Functional Requirements: FR-TRC-011
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from tracertm.api.deps import auth_guard
from tracertm.services.requirement_miner import (
    CandidateRequirement,
    MinerConfig,
    mine_files,
    mine_text,
)

router = APIRouter(prefix="/mine", tags=["mine"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class MineRequirementsRequest(BaseModel):
    """Request body for the requirement miner endpoint.

    Supply ``text`` for inline source text, ``paths`` for server-side file
    paths, or both.  At least one of the two must be non-empty.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    text: str | None = Field(
        default=None,
        description="Raw source text to mine (code, markdown, docstring, spec).",
    )
    paths: list[str] = Field(
        default_factory=list,
        description="Server-readable file paths to mine.",
    )
    min_confidence: float = Field(
        default=0.45,
        gt=0.0,
        le=1.0,
        description="Filter candidates below this confidence threshold.",
    )
    include_markers: bool = Field(
        default=True,
        description="Whether to include TODO/SPEC/FIXME comment markers.",
    )
    deduplicate: bool = Field(
        default=True,
        description="De-duplicate candidates by normalised text.",
    )


class CandidateRequirementOut(BaseModel):
    """Serialisable candidate requirement."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    text: str
    confidence: float
    source_ref: str
    tags: list[str]


class MineRequirementsResponse(BaseModel):
    """Response for the requirement miner endpoint."""

    model_config = ConfigDict(strict=True, extra="forbid")

    total: int
    candidates: list[CandidateRequirementOut]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _candidate_to_out(c: CandidateRequirement) -> CandidateRequirementOut:
    return CandidateRequirementOut(
        id=str(c.id),
        text=c.text,
        confidence=c.confidence,
        source_ref=c.source_ref,
        tags=list(c.tags),
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/requirements",
    response_model=MineRequirementsResponse,
    summary="Mine candidate requirements from source artifacts",
    description=(
        "Accepts raw source text and/or server-readable file paths. "
        "Returns candidate Requirement statements extracted by heuristic "
        "pattern matching (modal verbs, FR/NFR tags, spec markers), each "
        "annotated with a confidence score in [0.0, 1.0]. "
        "FR-TRC-011."
    ),
)
async def mine_requirements(
    body: MineRequirementsRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
) -> MineRequirementsResponse:
    """Extract candidate requirements from text and/or file paths."""
    config = MinerConfig(
        min_confidence=body.min_confidence,
        include_markers=body.include_markers,
        deduplicate=body.deduplicate,
    )

    candidates: list[CandidateRequirement] = []

    if body.text:
        candidates.extend(mine_text(body.text, source_ref="inline", config=config))

    if body.paths:
        candidates.extend(mine_files(body.paths, config=config))

    # Re-sort merged list descending by confidence.
    candidates.sort(key=lambda c: (-c.confidence, c.text))

    return MineRequirementsResponse(
        total=len(candidates),
        candidates=[_candidate_to_out(c) for c in candidates],
    )
