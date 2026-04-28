"""
User DTOs for data transfer between layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pheno.domain.entities.user import User
from pheno.domain.value_objects.common import Email, UserId


def _value(obj):
    return getattr(obj, "value", obj)


@dataclass(frozen=True)
class CreateUserDTO:
    """
    DTO for creating a new user.
    """

    email: str
    name: str

    def to_domain_params(self) -> tuple[Email, str]:
        """
        Convert to domain entity creation parameters.
        """
        return Email(self.email), self.name


@dataclass(frozen=True)
class UpdateUserDTO:
    """
    DTO for updating a user.
    """

    user_id: str
    name: str | None = None
    email: str | None = None

    def get_user_id(self) -> UserId:
        """
        Get the user ID as a domain value object.
        """
        return UserId(self.user_id)

    def get_email(self) -> Email | None:
        """
        Get the email as a domain value object.
        """
        return Email(self.email) if self.email else None


@dataclass(frozen=True)
class UserDTO:
    """
    DTO for user data.
    """

    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> UserDTO:
        """
        Create DTO from domain entity.
        """
        return cls(
            id=str(_value(user.id)),
            email=str(_value(user.email)),
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


@dataclass(frozen=True)
class UserFilterDTO:
    """
    DTO for filtering users.
    """

    email: str | None = None
    name: str | None = None
    is_active: bool | None = None
    limit: int = 100
    offset: int = 0
