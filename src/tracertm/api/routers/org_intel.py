"""Organizational Intelligence REST endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/org-intel", tags=["org_intel"])

# In-memory storage
_teams: dict[str, "Team"] = {}


@dataclass
class Team:
    id: str
    name: str
    description: str
    members: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class TeamResponse(BaseModel):
    id: str
    name: str
    description: str
    members: List[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_team(cls, team: Team) -> "TeamResponse":
        return cls(
            id=team.id,
            name=team.name,
            description=team.description,
            members=team.members,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )


class MetricsResponse(BaseModel):
    total_artifacts: int
    coverage_ratio: float
    open_gaps: int


@router.get("/health")
async def health():
    """Health check for the org_intel pillar."""
    return {"pillar": "org_intel", "status": "ok"}


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get organizational metrics stub."""
    # Stub values - in reality these would be computed from actual data
    return MetricsResponse(
        total_artifacts=len(_teams) * 10,  # placeholder
        coverage_ratio=0.75,
        open_gaps=3,
    )


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams():
    """List all teams."""
    # Return some default teams if empty
    if not _teams:
        default_teams = [
            Team(id=str(uuid4()), name="Platform Team", description="Core platform engineering"),
            Team(id=str(uuid4()), name="Product Team", description="Product feature development"),
            Team(id=str(uuid4()), name="Security Team", description="Security and compliance"),
        ]
        for t in default_teams:
            _teams[t.id] = t
    return [TeamResponse.from_team(t) for t in _teams.values()]
