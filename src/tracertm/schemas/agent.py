"""Pydantic schemas for agent session API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentSessionCreate(BaseModel):
    """Request to create an agent session."""

    project_id: str | None = Field(default=None, description="Optional project to scope the session")
    session_id: str | None = Field(default=None, description="Optional explicit session ID; otherwise generated")


class AgentSessionResponse(BaseModel):
    """Agent session metadata returned by API."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    sandbox_root: str
    project_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class AgentSessionListResponse(BaseModel):
    """Paginated list of agent sessions."""

    sessions: list[AgentSessionResponse]
    total: int
    limit: int
    offset: int


class AgentRunRequest(BaseModel):
    """Request to start an agent run workflow (Temporal)."""

    session_id: str = Field(..., description="Agent session ID")
    initial_messages_json: str | None = Field(default=None, description="JSON array of message dicts to start from")
    max_turns: int = Field(default=10, ge=1, le=100, description="Maximum agent turns")


class AgentRunResponse(BaseModel):
    """Response after starting an agent run workflow."""

    workflow_id: str
    run_id: str
    session_id: str
    status: str = "started"
