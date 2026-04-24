"""GitHub App Installation model for account-level GitHub App installations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin, generate_uuid
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from datetime import datetime

    from tracertm.models.account import Account
else:
    datetime = __import__("datetime").datetime


class GitHubAppInstallation(Base, TimestampMixin):
    """GitHub App Installation model.

    Represents a GitHub App installation at the account level.
    Each installation is tied to an account and can access repos for that account.
    """

    __tablename__ = "github_app_installations"
    __table_args__: tuple[Index, ...] = (
        Index("ix_github_app_installations_account", "account_id"),
        Index("ix_github_app_installations_installation_id", "installation_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    # GitHub installation details
    installation_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    account_login: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Organization or User
    target_id: Mapped[int] = mapped_column(nullable=False)

    # Installation metadata
    permissions: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)
    repository_selection: Mapped[str] = mapped_column(String(50), nullable=False, default="all")  # all or selected

    # Status
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    account: Mapped[Account] = relationship("Account")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<GitHubAppInstallation(id={self.id!r}, installation_id={self.installation_id!r}, account_id={self.account_id!r})>"
