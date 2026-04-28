"""Repository Factory for creating repository implementations.

This factory provides a centralized way to create repository instances based on
configuration or environment.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, TypeVar

from pheno.adapters.persistence.memory import (
    InMemoryConfigurationRepository,
    InMemoryDeploymentRepository,
    InMemoryServiceRepository,
    InMemoryUserRepository,
)

if TYPE_CHECKING:
    from pheno.application.ports.repositories import (
        ConfigurationRepository,
        DeploymentRepository,
        ServiceRepository,
        UserRepository,
    )

T = TypeVar("T")


class RepositoryType(Enum):
    """
    Supported repository types.
    """

    IN_MEMORY = "in_memory"
    SQLALCHEMY = "sqlalchemy"
    MONGODB = "mongodb"
    REDIS = "redis"


class RepositoryFactory:
    """Factory for creating repository implementations.

    This factory allows switching between different repository implementations (in-
    memory, SQLAlchemy, MongoDB, etc.) based on configuration.
    """

    def __init__(self, repository_type: RepositoryType = RepositoryType.IN_MEMORY):
        """Initialize the repository factory.

        Args:
            repository_type: Type of repository to create
        """
        self.repository_type = repository_type

    def create_user_repository(self) -> UserRepository:
        """Create a user repository.

        Returns:
            User repository implementation
        """
        if self.repository_type == RepositoryType.IN_MEMORY:
            return InMemoryUserRepository()
        if self.repository_type == RepositoryType.SQLALCHEMY:
            # Future: SQLAlchemy implementation
            raise NotImplementedError("SQLAlchemy repository not yet implemented")
        if self.repository_type == RepositoryType.MONGODB:
            # Future: MongoDB implementation
            raise NotImplementedError("MongoDB repository not yet implemented")
        if self.repository_type == RepositoryType.REDIS:
            # Future: Redis implementation
            raise NotImplementedError("Redis repository not yet implemented")
        raise ValueError(f"Unknown repository type: {self.repository_type}")

    def create_deployment_repository(self) -> DeploymentRepository:
        """Create a deployment repository.

        Returns:
            Deployment repository implementation
        """
        if self.repository_type == RepositoryType.IN_MEMORY:
            return InMemoryDeploymentRepository()
        if self.repository_type == RepositoryType.SQLALCHEMY:
            raise NotImplementedError("SQLAlchemy repository not yet implemented")
        if self.repository_type == RepositoryType.MONGODB:
            raise NotImplementedError("MongoDB repository not yet implemented")
        if self.repository_type == RepositoryType.REDIS:
            raise NotImplementedError("Redis repository not yet implemented")
        raise ValueError(f"Unknown repository type: {self.repository_type}")

    def create_service_repository(self) -> ServiceRepository:
        """Create a service repository.

        Returns:
            Service repository implementation
        """
        if self.repository_type == RepositoryType.IN_MEMORY:
            return InMemoryServiceRepository()
        if self.repository_type == RepositoryType.SQLALCHEMY:
            raise NotImplementedError("SQLAlchemy repository not yet implemented")
        if self.repository_type == RepositoryType.MONGODB:
            raise NotImplementedError("MongoDB repository not yet implemented")
        if self.repository_type == RepositoryType.REDIS:
            raise NotImplementedError("Redis repository not yet implemented")
        raise ValueError(f"Unknown repository type: {self.repository_type}")

    def create_configuration_repository(self) -> ConfigurationRepository:
        """Create a configuration repository.

        Returns:
            Configuration repository implementation
        """
        if self.repository_type == RepositoryType.IN_MEMORY:
            return InMemoryConfigurationRepository()
        if self.repository_type == RepositoryType.SQLALCHEMY:
            raise NotImplementedError("SQLAlchemy repository not yet implemented")
        if self.repository_type == RepositoryType.MONGODB:
            raise NotImplementedError("MongoDB repository not yet implemented")
        if self.repository_type == RepositoryType.REDIS:
            raise NotImplementedError("Redis repository not yet implemented")
        raise ValueError(f"Unknown repository type: {self.repository_type}")

    def create_all(
        self,
    ) -> tuple[
        UserRepository,
        DeploymentRepository,
        ServiceRepository,
        ConfigurationRepository,
    ]:
        """Create all repositories.

        Returns:
            Tuple of all repository implementations
        """
        return (
            self.create_user_repository(),
            self.create_deployment_repository(),
            self.create_service_repository(),
            self.create_configuration_repository(),
        )

    @classmethod
    def from_config(cls, config: dict) -> RepositoryFactory:
        """Create factory from configuration dictionary.

        Args:
            config: Configuration dictionary with 'repository_type' key

        Returns:
            Configured repository factory
        """
        repo_type_str = config.get("repository_type", "in_memory")
        repo_type = RepositoryType(repo_type_str)
        return cls(repo_type)

    @classmethod
    def from_env(cls) -> RepositoryFactory:
        """Create factory from environment variables.

        Returns:
            Configured repository factory
        """
        import os

        repo_type_str = os.getenv("PHENO_REPOSITORY_TYPE", "in_memory")
        repo_type = RepositoryType(repo_type_str)
        return cls(repo_type)
