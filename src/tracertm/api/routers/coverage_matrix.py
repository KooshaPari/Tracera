"""Coverage matrix export API route.

Exposes a read-only GET endpoint that builds and exports a requirement
coverage matrix from an in-memory graph snapshot.

Endpoint
--------
GET /api/v1/coverage/matrix?format=csv|json
    Accepts artifact + link arrays as a JSON request body and returns the
    coverage matrix in the requested format.

Formats
-------
* ``csv``  — RFC 4180 CSV with Content-Disposition attachment header.
* ``json`` — Structured JSON (default).

PDF is a planned future format (excluded from v1 — heavy dep on
reportlab/WeasyPrint).

Functional Requirements: FR-TRC-014
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, Field

from tracertm.api.deps import auth_guard
from tracertm.models.trace_link import Artifact, ArtifactKind, TraceLink, TraceLinkType
from tracertm.services.coverage_matrix_service import (
    build_coverage_matrix,
    export_csv,
    export_json,
)

router: APIRouter = APIRouter(prefix="/coverage", tags=["Coverage"])


# ---------------------------------------------------------------------------
# Request / Response schemas (reuse ArtifactIn / TraceLinkIn pattern from
# traceability_score router — same graph snapshot contract)
# ---------------------------------------------------------------------------


class ArtifactIn(BaseModel):
    """Minimal artifact payload for the matrix endpoint."""

    id: uuid.UUID
    project_id: uuid.UUID
    kind: ArtifactKind
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    external_id: str | None = None


class TraceLinkIn(BaseModel):
    """Minimal trace link payload for the matrix endpoint."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    project_id: uuid.UUID
    source_artifact_id: uuid.UUID
    target_artifact_id: uuid.UUID
    link_type: TraceLinkType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    rationale: str | None = None


class MatrixRequest(BaseModel):
    """Request body: graph snapshot to export as a coverage matrix."""

    artifacts: list[ArtifactIn] = Field(default_factory=list)
    links: list[TraceLinkIn] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get("/matrix")
async def get_coverage_matrix(
    body: MatrixRequest,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    format: Literal["csv", "json"] = "json",  # noqa: A002  # query param name matches FR spec
) -> Response:
    """Export a requirement coverage matrix in CSV or JSON format.

    Supply the artifact list and trace-link list in the request body.
    The service computes the matrix in-memory (no DB access).

    Query Parameters
    ----------------
    format : ``"csv"`` | ``"json"`` (default ``"json"``)

    Returns
    -------
    * ``format=json`` — ``application/json`` body with ``meta`` summary and
      ``rows`` array.
    * ``format=csv``  — ``text/csv`` attachment
      (``Content-Disposition: attachment; filename="coverage_matrix.csv"``).

    Functional Requirements: FR-TRC-014
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

    report = build_coverage_matrix(artifacts, links)

    if format == "csv":
        csv_text = export_csv(report)
        return PlainTextResponse(
            content=csv_text,
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="coverage_matrix.csv"'
            },
        )

    # default: json
    json_text = export_json(report)
    return Response(content=json_text, media_type="application/json")
