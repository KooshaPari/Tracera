"""Linear App Installation model for account-level Linear integrations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin, generate_uuid
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from datetime import datetime

    from tracertm.models.account import Account
    from tracertm.models.integration import IntegrationCredential
else:
    datetime = __import__("datetime").datetime


class LinearAppInstallation(Base, TimestampMixin):
    """Linear App Installation model.

    Represents a Linear OAuth installation at the account level.
    Similar to GitHub App but uses OAuth flow.
    """

    __tablename__ = "linear_app_installations"
    __table_args__: tuple[Index, ...] = (
        Index("ix_linear_app_installations_account", "account_id"),
        Index("ix_linear_app_installations_workspace_id", "workspace_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    # Linear installation details
    workspace_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    workspace_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # OAuth token (encrypted, stored in IntegrationCredential)
    integration_credential_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Installation metadata
    scopes: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Status
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    account: Mapped[Account] = relationship("Account")
    credential: Mapped[IntegrationCredential | None] = relationship(
        "IntegrationCredential",
        foreign_keys=[integration_credential_id],
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<LinearAppInstallation(id={self.id!r}, workspace_id={self.workspace_id!r}, account_id={self.account_id!r})>"


LinearApp = LinearAppInstallation
