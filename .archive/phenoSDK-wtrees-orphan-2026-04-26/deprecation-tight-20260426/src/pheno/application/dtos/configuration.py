"""
Configuration DTOs for data transfer between layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pheno.domain.entities.configuration import Configuration
from pheno.domain.value_objects.common import ConfigKey, ConfigValue


@dataclass(frozen=True)
class CreateConfigurationDTO:
    """
    DTO for creating a new configuration.
    """

    key: str
    value: Any
    description: str | None = None

    def to_domain_params(self) -> tuple[ConfigKey, ConfigValue, str | None]:
        """
        Convert to domain entity creation parameters.
        """
        return (
            ConfigKey(self.key),
            ConfigValue(self.value),
            self.description,
        )


@dataclass(frozen=True)
class UpdateConfigurationDTO:
    """
    DTO for updating a configuration.
    """

    key: str
    value: Any | None = None
    description: str | None = None

    def get_config_key(self) -> ConfigKey:
        """
        Get the config key as a domain value object.
        """
        return ConfigKey(self.key)

    def get_config_value(self) -> ConfigValue | None:
        """
        Get the config value as a domain value object.
        """
        return ConfigValue(self.value) if self.value is not None else None


@dataclass(frozen=True)
class ConfigurationDTO:
    """
    DTO for configuration data.
    """

    key: str
    value: Any
    description: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, config: Configuration) -> ConfigurationDTO:
        """
        Create DTO from domain entity.
        """
        return cls(
            key=config.key.value,
            value=config.value.value,
            description=config.description,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )


@dataclass(frozen=True)
class ConfigurationFilterDTO:
    """
    DTO for filtering configurations.
    """

    namespace: str | None = None
    key_pattern: str | None = None
    limit: int = 100
    offset: int = 0
