"""Account model for TraceRTM.

Accounts represent workspaces/organizations that can have multiple users.
"""

from collections import UserString
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin, generate_uuid
from tracertm.models.types import JSONType

if TYPE_CHECKING:
    from tracertm.models.account_user import AccountUser


class AccountType(UserString):
    """Account type enumeration."""

    PERSONAL = "personal"
    ORGANIZATION = "organization"


class Account(Base, TimestampMixin):
    """Account model representing a workspace/organization.

    An account can have multiple users and projects.
    """

    __tablename__ = "accounts"
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False, default=AccountType.PERSONAL)

    # Metadata
    account_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSONType, nullable=False, default=dict)

    # Relationships
    account_users: Mapped[list["AccountUser"]] = relationship(
        "AccountUser",
        back_populates="account",
        cascade="all, delete-orphan",
    )
    # projects: Mapped[list["Project"]] = relationship(
    #     "Project", back_populates="account", cascade="all, delete-orphan"

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "account_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "account_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Account(id={self.id!r}, name={self.name!r}, slug={self.slug!r})>"
