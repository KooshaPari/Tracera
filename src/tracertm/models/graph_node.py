"""GraphNode model for TraceRTM."""

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin


class GraphNode(Base, TimestampMixin):
    """Join table mapping nodes (items) into graphs."""

    __tablename__ = "graph_nodes"
    __table_args__ = (
        Index("idx_graph_nodes_graph", "graph_id"),
        Index("idx_graph_nodes_item", "item_id"),
        Index("idx_graph_nodes_project_graph", "project_id", "graph_id"),
        {"extend_existing": True},
    )

    graph_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("graphs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<GraphNode(graph_id={self.graph_id!r}, item_id={self.item_id!r})>"
