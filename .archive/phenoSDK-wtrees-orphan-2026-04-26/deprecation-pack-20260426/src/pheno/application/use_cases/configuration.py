"""
Configuration use cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.application.dtos.configuration import (
    ConfigurationDTO,
    ConfigurationFilterDTO,
    CreateConfigurationDTO,
    UpdateConfigurationDTO,
)
from pheno.domain.entities.configuration import Configuration
from pheno.domain.value_objects.common import ConfigKey

if TYPE_CHECKING:
    from pheno.application.ports.repositories import ConfigurationRepository


class CreateConfigurationUseCase:
    """
    Use case for creating a new configuration.
    """

    def __init__(self, configuration_repository: ConfigurationRepository):
        self.configuration_repository = configuration_repository

    async def execute(self, dto: CreateConfigurationDTO) -> ConfigurationDTO:
        """
        Create a new configuration.
        """
        # Create configuration entity
        key, value, description = dto.to_domain_params()
        configuration = Configuration.create(key, value, description)
        if isinstance(configuration, tuple):
            configuration = configuration[0]

        # Save to repository
        await self.configuration_repository.save(configuration)

        return ConfigurationDTO.from_entity(configuration)


class UpdateConfigurationUseCase:
    """
    Use case for updating a configuration.
    """

    def __init__(self, configuration_repository: ConfigurationRepository):
        self.configuration_repository = configuration_repository

    async def execute(self, dto: UpdateConfigurationDTO) -> ConfigurationDTO:
        """
        Update a configuration.
        """
        # Find configuration
        config_key = dto.get_config_key()
        configuration = await self.configuration_repository.find_by_key(config_key)
        if not configuration:
            raise ValueError(f"Configuration not found: {config_key.value}")

        # Update configuration
        if dto.value is not None:
            config_value = dto.get_config_value()
            if config_value:
                configuration.update_value(config_value)
        if dto.description is not None:
            configuration.update_description(dto.description)

        # Save to repository
        await self.configuration_repository.save(configuration)

        return ConfigurationDTO.from_entity(configuration)


class GetConfigurationUseCase:
    """
    Use case for getting a configuration by key.
    """

    def __init__(self, configuration_repository: ConfigurationRepository):
        self.configuration_repository = configuration_repository

    async def execute(self, key: str) -> ConfigurationDTO:
        """
        Get a configuration by key.
        """
        configuration = await self.configuration_repository.find_by_key(ConfigKey(key))
        if not configuration:
            raise ValueError(f"Configuration not found: {key}")

        return ConfigurationDTO.from_entity(configuration)


class ListConfigurationsUseCase:
    """
    Use case for listing configurations.
    """

    def __init__(self, configuration_repository: ConfigurationRepository):
        self.configuration_repository = configuration_repository

    async def execute(self, filter_dto: ConfigurationFilterDTO) -> list[ConfigurationDTO]:
        """
        List configurations with optional filters.
        """
        configurations = await self.configuration_repository.find_all(
            limit=filter_dto.limit,
            offset=filter_dto.offset,
        )
        return [ConfigurationDTO.from_entity(c) for c in configurations]
