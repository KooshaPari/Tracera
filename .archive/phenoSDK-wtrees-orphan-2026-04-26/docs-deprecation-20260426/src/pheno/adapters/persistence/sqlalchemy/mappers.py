"""Mappers for converting between domain entities and ORM models.

These mappers maintain the separation between domain and infrastructure by translating
between the two representations.
"""

from __future__ import annotations

from pheno.domain.entities.configuration import Configuration
from pheno.domain.entities.deployment import Deployment
from pheno.domain.entities.service import Service
from pheno.domain.entities.user import User
from pheno.domain.value_objects.common import ConfigKey, ConfigValue, Email, UserId
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironment,
    DeploymentId,
    DeploymentStatus,
    DeploymentStrategy,
)
from pheno.domain.value_objects.infrastructure import (
    ServiceId,
    ServiceName,
    ServicePort,
    ServiceStatus,
)

from .models import ConfigurationModel, DeploymentModel, ServiceModel, UserModel


class UserMapper:
    """
    Mapper for User entity and UserModel.
    """

    def to_model(self, entity: User) -> UserModel:
        """Convert User entity to UserModel.

        Args:
            entity: User domain entity

        Returns:
            UserModel ORM model
        """
        return UserModel(
            id=str(entity.id.value),
            email=entity.email.value,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, model: UserModel) -> User:
        """Convert UserModel to User entity.

        Args:
            model: UserModel ORM model

        Returns:
            User domain entity
        """
        # Reconstruct the entity (bypassing factory to preserve state)
        user = object.__new__(User)
        user._id = UserId(model.id)
        user._email = Email(model.email)
        user._name = model.name
        user._is_active = model.is_active
        user._created_at = model.created_at
        user._updated_at = model.updated_at
        user._domain_events = []

        return user


class DeploymentMapper:
    """
    Mapper for Deployment entity and DeploymentModel.
    """

    def to_model(self, entity: Deployment) -> DeploymentModel:
        """Convert Deployment entity to DeploymentModel.

        Args:
            entity: Deployment domain entity

        Returns:
            DeploymentModel ORM model
        """
        return DeploymentModel(
            id=str(entity.id.value),
            environment=entity.environment.value,
            strategy=entity.strategy.value,
            status=entity.status.value,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, model: DeploymentModel) -> Deployment:
        """Convert DeploymentModel to Deployment entity.

        Args:
            model: DeploymentModel ORM model

        Returns:
            Deployment domain entity
        """
        # Reconstruct the entity
        deployment = object.__new__(Deployment)
        deployment._id = DeploymentId(model.id)
        deployment._environment = DeploymentEnvironment(model.environment)
        deployment._strategy = DeploymentStrategy(model.strategy)
        deployment._status = DeploymentStatus(model.status)
        deployment._started_at = model.started_at
        deployment._completed_at = model.completed_at
        deployment._created_at = model.created_at
        deployment._updated_at = model.updated_at
        deployment._domain_events = []

        return deployment


class ServiceMapper:
    """
    Mapper for Service entity and ServiceModel.
    """

    def to_model(self, entity: Service) -> ServiceModel:
        """Convert Service entity to ServiceModel.

        Args:
            entity: Service domain entity

        Returns:
            ServiceModel ORM model
        """
        return ServiceModel(
            id=str(entity.id.value),
            name=entity.name.value,
            port=entity.port.port,
            protocol=entity.port.protocol,
            status=entity.status.value,
            started_at=entity.started_at,
            stopped_at=entity.stopped_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, model: ServiceModel) -> Service:
        """Convert ServiceModel to Service entity.

        Args:
            model: ServiceModel ORM model

        Returns:
            Service domain entity
        """
        # Reconstruct the entity
        service = object.__new__(Service)
        service._id = ServiceId(model.id)
        service._name = ServiceName(model.name)
        service._port = ServicePort(model.port, model.protocol)
        service._status = ServiceStatus(model.status)
        service._started_at = model.started_at
        service._stopped_at = model.stopped_at
        service._created_at = model.created_at
        service._updated_at = model.updated_at
        service._domain_events = []

        return service


class ConfigurationMapper:
    """
    Mapper for Configuration entity and ConfigurationModel.
    """

    def to_model(self, entity: Configuration) -> ConfigurationModel:
        """Convert Configuration entity to ConfigurationModel.

        Args:
            entity: Configuration domain entity

        Returns:
            ConfigurationModel ORM model
        """
        return ConfigurationModel(
            key=entity.key.value,
            value=entity.value.value,
            value_type=entity.value.value_type,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, model: ConfigurationModel) -> Configuration:
        """Convert ConfigurationModel to Configuration entity.

        Args:
            model: ConfigurationModel ORM model

        Returns:
            Configuration domain entity
        """
        # Reconstruct the entity
        config = object.__new__(Configuration)
        config._key = ConfigKey(model.key)
        config._value = ConfigValue(model.value)
        config._description = model.description
        config._created_at = model.created_at
        config._updated_at = model.updated_at

        return config
