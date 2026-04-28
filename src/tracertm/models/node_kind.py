"""NodeKind model for TraceRTM."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_node_kind_uuid() -> str:
    """Generate a UUID string for node kind ID."""
    return str(uuid.uuid4())


class NodeKind(Base, TimestampMixin):
    """Node kind catalog for items.

    Kinds describe the semantic type (feature, screen, api_endpoint, etc.).
    """

    __tablename__ = "node_kinds"
    __table_args__ = (
        Index("idx_node_kinds_project_name", "project_id", "name", unique=True),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_node_kind_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<NodeKind(id={self.id!r}, name={self.name!r})>"
