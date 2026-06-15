"""Evidence Management REST endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

router = APIRouter(prefix="/evidence", tags=["evidence"])

# In-memory storage
_evidence_items: dict[str, "EvidenceItem"] = {}


@dataclass
class EvidenceItem:
    id: str
    artifact_id: str
    kind: str
    url: str
    captured_at: datetime
    description: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class EvidenceCreate(BaseModel):
    artifact_id: str = Field(..., min_length=1)
    kind: str = Field(..., min_length=1)
    url: HttpUrl
    captured_at: datetime
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class EvidenceResponse(BaseModel):
    id: str
    artifact_id: str
    kind: str
    url: str
    captured_at: datetime
    description: Optional[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_evidence(cls, evidence: EvidenceItem) -> "EvidenceResponse":
        return cls(
            id=evidence.id,
            artifact_id=evidence.artifact_id,
            kind=evidence.kind,
            url=evidence.url,
            captured_at=evidence.captured_at,
            description=evidence.description,
            metadata=evidence.metadata,
            created_at=evidence.created_at,
            updated_at=evidence.updated_at,
        )


@router.get("/health")
async def health():
    """Health check for the evidence pillar."""
    return {"pillar": "evidence", "status": "ok"}


@router.get("", response_model=List[EvidenceResponse])
async def list_evidence():
    """List all evidence items."""
    return [EvidenceResponse.from_evidence(e) for e in _evidence_items.values()]


@router.post("", response_model=EvidenceResponse, status_code=201)
async def create_evidence(payload: EvidenceCreate):
    """Create a new evidence item."""
    evidence_id = str(uuid4())
    now = datetime.utcnow()
    evidence = EvidenceItem(
        id=evidence_id,
        artifact_id=payload.artifact_id,
        kind=payload.kind,
        url=str(payload.url),
        captured_at=payload.captured_at,
        description=payload.description,
        metadata=payload.metadata,
        created_at=now,
        updated_at=now,
    )
    _evidence_items[evidence_id] = evidence
    return EvidenceResponse.from_evidence(evidence)
