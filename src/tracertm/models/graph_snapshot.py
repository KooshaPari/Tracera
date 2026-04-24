"""GraphSnapshot model for TraceRTM."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_graph_snapshot_uuid() -> str:
    """Generate a UUID string for graph snapshot ID."""
    return str(uuid.uuid4())


class GraphSnapshot(Base, TimestampMixin):
    """Immutable graph snapshot for versioned export and diffs."""

    __tablename__ = "graph_snapshots"
    __table_args__ = (
        Index("idx_graph_snapshots_project_graph", "project_id", "graph_id"),
        Index("idx_graph_snapshots_project_version", "project_id", "version"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_graph_snapshot_uuid)
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

    version: Mapped[int] = mapped_column(nullable=False)
    snapshot_json: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)
    snapshot_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<GraphSnapshot(id={self.id!r}, version={self.version!r})>"
