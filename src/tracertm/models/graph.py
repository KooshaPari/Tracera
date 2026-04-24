"""Graph model for TraceRTM."""

import uuid

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_graph_uuid() -> str:
    """Generate a UUID string for graph ID."""
    return str(uuid.uuid4())


class Graph(Base, TimestampMixin):
    """Graph model representing a projection of nodes and edges."""

    __tablename__ = "graphs"
    __table_args__ = (
        Index("idx_graphs_project_type", "project_id", "graph_type"),
        Index("idx_graphs_project_name", "project_id", "name", unique=True),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_graph_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    graph_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_item_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    graph_version: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    graph_rules: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)
    graph_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Graph(id={self.id!r}, type={self.graph_type!r}, name={self.name!r})>"
