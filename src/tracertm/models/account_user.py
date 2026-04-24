"""AccountUser model for many-to-many relationship between accounts and users."""

from __future__ import annotations

from collections import UserString
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from datetime import datetime

    from tracertm.models.account import Account
else:
    datetime = __import__("datetime").datetime


class AccountRole(UserString):
    """Account user role enumeration."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class AccountUser(Base, TimestampMixin):
    """Join table for account-user relationships.

    Represents a user's membership in an account with a specific role.
    """

    __tablename__ = "account_users"
    __table_args__: tuple[UniqueConstraint, ...] = (UniqueConstraint("account_id", "user_id", name="uc_account_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=AccountRole.MEMBER)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    account: Mapped[Account] = relationship("Account", back_populates="account_users")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<AccountUser(account_id={self.account_id!r}, user_id={self.user_id!r}, role={self.role!r})>"
