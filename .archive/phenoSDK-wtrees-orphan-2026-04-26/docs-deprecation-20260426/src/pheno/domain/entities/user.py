"""
User entity.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime

from pheno.domain.base import AggregateRoot
from pheno.domain.events import UserCreated, UserDeactivated, UserUpdated
from pheno.domain.exceptions import UserInactiveError, ValidationError
from pheno.domain.value_objects import Email, UserId


@dataclass
class User(AggregateRoot):
    """User aggregate root.

    Represents a user in the system with identity, email, and name.
    Users can be active or inactive.

    Business Rules:
        - Email must be unique
        - Name cannot be empty
        - Inactive users cannot perform actions
        - User creation emits UserCreated event
        - User updates emit UserUpdated event
        - User deactivation emits UserDeactivated event
    """

    email: Email = field(default=None)
    name: str = field(default="")
    is_active: bool = True

    def __post_init__(self):
        """
        Validate user invariants.
        """
        super().__init__()
        if not self.name or not self.name.strip():
            raise ValidationError("User name cannot be empty")

    @classmethod
    def create(cls, email: Email, name: str) -> tuple["User", UserCreated]:
        """Factory method to create a new user.

        Args:
            email: User email address
            name: User name

        Returns:
            Tuple of (User entity, UserCreated event)

        Raises:
            ValidationError: If name is empty
        """
        if not name or not name.strip():
            raise ValidationError("User name cannot be empty")

        user_id = UserId.generate()

        user = cls(
            id=str(user_id),
            email=email,
            name=name.strip(),
            is_active=True,
        )

        event = UserCreated(
            aggregate_id=str(user_id),
            user_id=str(user_id),
            email=str(email),
            name=user.name,
        )

        user.add_event(event)
        return user, event

    def update_name(self, new_name: str) -> "User":
        """Update user name.

        Args:
            new_name: New user name

        Returns:
            Updated user entity

        Raises:
            ValidationError: If name is empty
            UserInactiveError: If user is inactive
        """
        if not self.is_active:
            raise UserInactiveError(str(self.id))

        if not new_name or not new_name.strip():
            raise ValidationError("User name cannot be empty")

        updated_user = replace(
            self,
            name=new_name.strip(),
            updated_at=datetime.utcnow(),
        )

        event = UserUpdated(
            aggregate_id=str(self.id),
            user_id=str(self.id),
            field="name",
            old_value=self.name,
            new_value=new_name.strip(),
        )

        updated_user.add_event(event)
        return updated_user

    def update_email(self, new_email: Email) -> "User":
        """Update user email.

        Args:
            new_email: New email address

        Returns:
            Updated user entity

        Raises:
            UserInactiveError: If user is inactive
        """
        if not self.is_active:
            raise UserInactiveError(str(self.id))

        updated_user = replace(
            self,
            email=new_email,
            updated_at=datetime.utcnow(),
        )

        event = UserUpdated(
            aggregate_id=str(self.id),
            user_id=str(self.id),
            field="email",
            old_value=str(self.email),
            new_value=str(new_email),
        )

        updated_user.add_event(event)
        return updated_user

    def deactivate(self) -> "User":
        """Deactivate user.

        Returns:
            Deactivated user entity

        Raises:
            ValidationError: If user is already inactive
        """
        if not self.is_active:
            raise ValidationError(f"User {self.id} is already inactive")

        deactivated_user = replace(
            self,
            is_active=False,
            updated_at=datetime.utcnow(),
        )

        event = UserDeactivated(
            aggregate_id=str(self.id),
            user_id=str(self.id),
        )

        deactivated_user.add_event(event)
        return deactivated_user

    def activate(self) -> "User":
        """Activate user.

        Returns:
            Activated user entity

        Raises:
            ValidationError: If user is already active
        """
        if self.is_active:
            raise ValidationError(f"User {self.id} is already active")

        activated_user = replace(
            self,
            is_active=True,
            updated_at=datetime.utcnow(),
        )

        event = UserUpdated(
            aggregate_id=str(self.id),
            user_id=str(self.id),
            field="is_active",
            old_value=False,
            new_value=True,
        )

        activated_user.add_event(event)
        return activated_user

    def __str__(self) -> str:
        return f"User({self.id}, {self.email}, {self.name})"
