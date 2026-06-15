"""SDLC Project Management REST endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sdlc-pm", tags=["sdlc_pm"])

# In-memory storage
_sprints: dict[str, "Sprint"] = {}
_stories: dict[str, "Story"] = {}


@dataclass
class Sprint:
    id: str
    name: str
    goal: str
    start_date: datetime
    end_date: datetime
    status: str = "planned"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Story:
    id: str
    sprint_id: Optional[str]
    title: str
    description: str
    status: str = "backlog"
    story_points: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class SprintCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    goal: str = Field(..., min_length=1)
    start_date: datetime
    end_date: datetime


class SprintResponse(BaseModel):
    id: str
    name: str
    goal: str
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_sprint(cls, sprint: Sprint) -> "SprintResponse":
        return cls(
            id=sprint.id,
            name=sprint.name,
            goal=sprint.goal,
            start_date=sprint.start_date,
            end_date=sprint.end_date,
            status=sprint.status,
            created_at=sprint.created_at,
            updated_at=sprint.updated_at,
        )


class StoryResponse(BaseModel):
    id: str
    sprint_id: Optional[str]
    title: str
    description: str
    status: str
    story_points: Optional[int]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_story(cls, story: Story) -> "StoryResponse":
        return cls(
            id=story.id,
            sprint_id=story.sprint_id,
            title=story.title,
            description=story.description,
            status=story.status,
            story_points=story.story_points,
            created_at=story.created_at,
            updated_at=story.updated_at,
        )


@router.get("/health")
async def health():
    """Health check for the sdlc_pm pillar."""
    return {"pillar": "sdlc_pm", "status": "ok"}


@router.get("/sprints", response_model=List[SprintResponse])
async def list_sprints():
    """List all sprints."""
    return [SprintResponse.from_sprint(s) for s in _sprints.values()]


@router.get("/stories", response_model=List[StoryResponse])
async def list_stories():
    """List all stories."""
    return [StoryResponse.from_story(s) for s in _stories.values()]


@router.post("/sprints", response_model=SprintResponse, status_code=201)
async def create_sprint(payload: SprintCreate):
    """Create a new sprint."""
    sprint_id = str(uuid4())
    now = datetime.utcnow()
    sprint = Sprint(
        id=sprint_id,
        name=payload.name,
        goal=payload.goal,
        start_date=payload.start_date,
        end_date=payload.end_date,
        created_at=now,
        updated_at=now,
    )
    _sprints[sprint_id] = sprint
    return SprintResponse.from_sprint(sprint)
