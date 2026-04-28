"""
Configuration entity.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime

from pheno.domain.base import Entity
from pheno.domain.exceptions import ValidationError
from pheno.domain.value_objects import ConfigKey, ConfigValue


@dataclass
class Configuration(Entity):
    """Configuration entity.

    Represents a configuration key-value pair in the system.
    Configurations can be updated and have a history of changes.

    Business Rules:
        - Configuration key must be unique
        - Configuration value can be any type
        - Configuration tracks creation and update times
        - Previous value is stored on update
    """

    key: ConfigKey = field(default=None)
    value: ConfigValue = field(default=None)
    previous_value: ConfigValue | None = None
    description: str | None = None

    def __post_init__(self):
        """
        Validate configuration invariants.
        """
        super().__init__()
        # No additional validation needed for now

    @classmethod
    def create(
        cls,
        key: ConfigKey,
        value: ConfigValue,
        description: str | None = None,
    ) -> "Configuration":
        """Factory method to create a new configuration.

        Args:
            key: Configuration key
            value: Configuration value
            description: Optional description

        Returns:
            Configuration entity
        """
        return cls(
            key=key,
            value=value,
            description=description,
        )

    def update_value(self, new_value: ConfigValue) -> "Configuration":
        """Update configuration value.

        Args:
            new_value: New configuration value

        Returns:
            Updated configuration entity
        """
        return replace(
            self,
            value=new_value,
            previous_value=self.value,
            updated_at=datetime.utcnow(),
        )


    def update_description(self, new_description: str) -> "Configuration":
        """Update configuration description.

        Args:
            new_description: New description

        Returns:
            Updated configuration entity

        Raises:
            ValidationError: If description is empty
        """
        if not new_description or not new_description.strip():
            raise ValidationError("Description cannot be empty")

        return replace(
            self,
            description=new_description.strip(),
            updated_at=datetime.utcnow(),
        )


    def has_changed(self) -> bool:
        """
        Check if configuration has been updated.
        """
        return self.previous_value is not None

    def get_namespace(self) -> str | None:
        """
        Get configuration namespace from key.
        """
        return self.key.namespace

    def __str__(self) -> str:
        return f"Configuration({self.key}, {self.value})"
