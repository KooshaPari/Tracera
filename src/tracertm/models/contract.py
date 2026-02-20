"""Contract (Design by Contract) model."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Contract(Base, TimestampMixin):
    """Formal specification contract."""

    __tablename__ = "contracts"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False)  # api, function, etc.
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    # Contract Definition
    preconditions: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    postconditions: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    invariants: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)

    # State Machine
    states: Mapped[list[str]] = mapped_column(JSON, default=list)
    transitions: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)

    # Executable Spec
    executable_spec: Mapped[str | None] = mapped_column(Text, nullable=True)
    spec_language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Verification
    last_verified_at: Mapped[datetime | None] = mapped_column(String(50), nullable=True)
    verification_result: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    # Metadata
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", backref="contracts")
    item = relationship("Item", backref="contracts")
