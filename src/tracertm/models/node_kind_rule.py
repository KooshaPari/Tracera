"""NodeKindRule model for TraceRTM."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_node_kind_rule_uuid() -> str:
    """Generate a UUID string for node kind rule ID."""
    return str(uuid.uuid4())


class NodeKindRule(Base, TimestampMixin):
    """Rule registry for allowed edge types per node kind."""

    __tablename__ = "node_kind_rules"
    __table_args__ = (
        Index("idx_node_kind_rules_project_kind", "project_id", "node_kind_id"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_node_kind_rule_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_kind_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("node_kinds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rule_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<NodeKindRule(id={self.id!r}, node_kind_id={self.node_kind_id!r})>"
