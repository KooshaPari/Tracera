"""GraphChange model for TraceRTM."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_graph_change_uuid() -> str:
    """Generate a UUID string for graph change ID."""
    return str(uuid.uuid4())


class GraphChange(Base, TimestampMixin):
    """Graph change log for LLM-friendly patches and audits."""

    __tablename__ = "graph_changes"
    __table_args__ = (
        Index("idx_graph_changes_project_graph", "project_id", "graph_id"),
        Index("idx_graph_changes_project_type", "project_id", "change_type"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_graph_change_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    graph_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("graphs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    change_type: Mapped[str] = mapped_column(String(100), nullable=False)
    change_payload: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<GraphChange(id={self.id!r}, type={self.change_type!r})>"
