"""Factory Pattern implementations for creating domain entities.

Factories encapsulate the creation logic for complex domain objects, ensuring they are
created in a valid state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pheno.domain.entities.configuration import Configuration
from pheno.domain.entities.deployment import Deployment
from pheno.domain.entities.service import Service
from pheno.domain.entities.user import User
from pheno.domain.value_objects.common import ConfigKey, ConfigValue, Email
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironment,
    DeploymentStrategy,
)
from pheno.domain.value_objects.infrastructure import ServiceName, ServicePort

T = TypeVar("T")


class EntityFactory(ABC, Generic[T]):
    """Abstract factory for creating domain entities.

    This provides a common interface for all entity factories.
    """

    @abstractmethod
    def create(self, *args, **kwargs) -> T:
        """
        Create a new entity.
        """

    @abstractmethod
    def create_from_dict(self, data: dict) -> T:
        """
        Create entity from dictionary data.
        """


class UserFactory(EntityFactory[User]):
    """Factory for creating User entities.

    Encapsulates the creation logic and validation for users.
    """

    def create(self, email: str, name: str) -> User:
        """Create a new user.

        Args:
            email: User email address
            name: User full name

        Returns:
            Created user entity
        """
        email_vo = Email(email)
        return User.create(email_vo, name)

    def create_from_dict(self, data: dict) -> User:
        """Create user from dictionary data.

        Args:
            data: Dictionary containing user data

        Returns:
            Created user entity
        """
        return self.create(
            email=data["email"],
            name=data["name"],
        )

    def create_batch(self, users_data: list[dict]) -> list[User]:
        """Create multiple users from a list of dictionaries.

        Args:
            users_data: List of user data dictionaries

        Returns:
            List of created user entities
        """
        return [self.create_from_dict(data) for data in users_data]


class DeploymentFactory(EntityFactory[Deployment]):
    """Factory for creating Deployment entities.

    Encapsulates the creation logic and validation for deployments.
    """

    def create(self, environment: str, strategy: str) -> Deployment:
        """Create a new deployment.

        Args:
            environment: Deployment environment (production, staging, etc.)
            strategy: Deployment strategy (blue_green, rolling, etc.)

        Returns:
            Created deployment entity
        """
        env_vo = DeploymentEnvironment(environment)
        strategy_vo = DeploymentStrategy(strategy)
        return Deployment.create(env_vo, strategy_vo)

    def create_from_dict(self, data: dict) -> Deployment:
        """Create deployment from dictionary data.

        Args:
            data: Dictionary containing deployment data

        Returns:
            Created deployment entity
        """
        return self.create(
            environment=data["environment"],
            strategy=data["strategy"],
        )

    def create_production_deployment(self, strategy: str = "blue_green") -> Deployment:
        """Create a production deployment with default settings.

        Args:
            strategy: Deployment strategy (default: blue_green)

        Returns:
            Created deployment entity
        """
        return self.create("production", strategy)

    def create_staging_deployment(self, strategy: str = "rolling") -> Deployment:
        """Create a staging deployment with default settings.

        Args:
            strategy: Deployment strategy (default: rolling)

        Returns:
            Created deployment entity
        """
        return self.create("staging", strategy)


class ServiceFactory(EntityFactory[Service]):
    """Factory for creating Service entities.

    Encapsulates the creation logic and validation for services.
    """

    def create(self, name: str, port: int, protocol: str = "http") -> Service:
        """Create a new service.

        Args:
            name: Service name
            port: Service port number
            protocol: Service protocol (default: http)

        Returns:
            Created service entity
        """
        name_vo = ServiceName(name)
        port_vo = ServicePort(port, protocol)
        return Service.create(name_vo, port_vo)

    def create_from_dict(self, data: dict) -> Service:
        """Create service from dictionary data.

        Args:
            data: Dictionary containing service data

        Returns:
            Created service entity
        """
        return self.create(
            name=data["name"],
            port=data["port"],
            protocol=data.get("protocol", "http"),
        )

    def create_http_service(self, name: str, port: int = 8080) -> Service:
        """Create an HTTP service with default settings.

        Args:
            name: Service name
            port: Service port (default: 8080)

        Returns:
            Created service entity
        """
        return self.create(name, port, "http")

    def create_grpc_service(self, name: str, port: int = 50051) -> Service:
        """Create a gRPC service with default settings.

        Args:
            name: Service name
            port: Service port (default: 50051)

        Returns:
            Created service entity
        """
        return self.create(name, port, "grpc")


class ConfigurationFactory(EntityFactory[Configuration]):
    """Factory for creating Configuration entities.

    Encapsulates the creation logic and validation for configurations.
    """

    def create(
        self,
        key: str,
        value: any,
        description: str | None = None,
    ) -> Configuration:
        """Create a new configuration.

        Args:
            key: Configuration key
            value: Configuration value
            description: Optional description

        Returns:
            Created configuration entity
        """
        key_vo = ConfigKey(key)
        value_vo = ConfigValue(value)
        return Configuration.create(key_vo, value_vo, description)

    def create_from_dict(self, data: dict) -> Configuration:
        """Create configuration from dictionary data.

        Args:
            data: Dictionary containing configuration data

        Returns:
            Created configuration entity
        """
        return self.create(
            key=data["key"],
            value=data["value"],
            description=data.get("description"),
        )

    def create_batch(self, configs_data: list[dict]) -> list[Configuration]:
        """Create multiple configurations from a list of dictionaries.

        Args:
            configs_data: List of configuration data dictionaries

        Returns:
            List of created configuration entities
        """
        return [self.create_from_dict(data) for data in configs_data]

    def create_from_env(self, prefix: str = "PHENO_") -> list[Configuration]:
        """Create configurations from environment variables.

        Args:
            prefix: Environment variable prefix (default: PHENO_)

        Returns:
            List of created configuration entities
        """
        import os

        configs = []
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower().replace("_", ".")
                configs.append(self.create(config_key, value))

        return configs
