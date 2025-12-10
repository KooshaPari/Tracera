"""
Agent model for TraceRTM.
"""

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_agent_uuid() -> str:
    """Generate a UUID string for agent ID."""
    return str(uuid.uuid4())


class Agent(Base, TimestampMixin):
    """
    Agent model for tracking AI agent activity.

    Agents register themselves and log their activities.
    """

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(255), primary_key=True, default=generate_agent_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False, default="generic")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    # Flexible metadata fields expected by tests
    config: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    capabilities: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)
    agent_metadata: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    last_activity_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (Index("idx_agents_project_status", "project_id", "status"),)

    def __init__(self, **kwargs):
        """
        Accept flexible kwargs used by tests (config, capabilities, agent_type).
        """
        if "agent_type" not in kwargs:
            kwargs["agent_type"] = "generic"
        if "config" not in kwargs:
            kwargs["config"] = {}
        if "capabilities" not in kwargs:
            kwargs["capabilities"] = []
        if "agent_metadata" not in kwargs:
            kwargs["agent_metadata"] = kwargs.get("config", {})
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Agent(id={self.id!r}, name={self.name!r})>"
