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
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    agent_metadata: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    last_activity_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (Index("idx_agents_project_status", "project_id", "status"),)

    def __repr__(self) -> str:
        return f"<Agent(id={self.id!r}, name={self.name!r})>"
