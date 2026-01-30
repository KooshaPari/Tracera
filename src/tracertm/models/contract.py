"""
Contract (Design by Contract) model.
"""

from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Contract(Base, TimestampMixin):
    """Formal specification contract."""

    __tablename__ = "contracts"
    __table_args__: dict[str, Any] = {"extend_existing": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    project_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    contract_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False)  # api, function, etc.
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    # Contract Definition
    preconditions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    postconditions: Mapped[List[dict]] = mapped_column(JSON, default=list)
    invariants: Mapped[List[dict]] = mapped_column(JSON, default=list)

    # State Machine
    states: Mapped[List[str]] = mapped_column(JSON, default=list)
    transitions: Mapped[List[dict]] = mapped_column(JSON, default=list)

    # Executable Spec
    executable_spec: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    spec_language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Verification
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    verification_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Metadata
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    version: Mapped[int] = mapped_column(default=1)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    project = relationship("Project", backref="contracts")
    item = relationship("Item", backref="contracts")
