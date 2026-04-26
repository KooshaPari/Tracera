"""Domain entities - core business objects with identity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Entity:
    """Base entity with identity and timestamps."""

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id


@dataclass
class Example(Entity):
    """Example domain entity."""

    name: str = ""
    description: str | None = None
    active: bool = True

    def validate(self) -> None:
        """Validate domain rules."""
        if not self.name or not self.name.strip():
            from .errors import ValidationError
            raise ValidationError(field="name", message="Name is required")
        if len(self.name) > 100:
            from .errors import ValidationError
            raise ValidationError(field="name", message="Name must be less than 100 characters")

    def deactivate(self) -> None:
        """Deactivate the entity."""
        self.active = False
        self.touch()
