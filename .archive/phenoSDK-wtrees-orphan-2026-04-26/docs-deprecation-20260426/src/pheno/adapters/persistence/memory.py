"""
In-memory repository implementations for testing and development.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.application.ports.repositories import (
    ConfigurationRepository,
    DeploymentRepository,
    ServiceRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from pheno.domain.entities.configuration import Configuration
    from pheno.domain.entities.deployment import Deployment
    from pheno.domain.entities.service import Service
    from pheno.domain.entities.user import User
    from pheno.domain.value_objects.common import (
        ConfigKey,
        DeploymentId,
        Email,
        ServiceId,
        UserId,
    )
    from pheno.domain.value_objects.deployment import DeploymentEnvironment
    from pheno.domain.value_objects.infrastructure import ServiceName


def _value(obj):
    return getattr(obj, "value", obj)


class InMemoryUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository.
    """

    def __init__(self):
        self._users: dict[str, User] = {}

    async def save(self, user: User) -> None:
        """
        Save a user.
        """
        self._users[str(_value(user.id))] = user

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find a user by ID.
        """
        return self._users.get(str(_value(user_id)))

    async def find_by_email(self, email: Email) -> User | None:
        """
        Find a user by email.
        """
        for user in self._users.values():
            if _value(user.email) == _value(email):
                return user
        return None

    async def delete(self, user_id: UserId) -> None:
        """
        Delete a user.
        """
        self._users.pop(str(_value(user_id)), None)

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """
        Find all users with pagination.
        """
        users = list(self._users.values())
        return users[offset : offset + limit]

    async def count(self, active_only: bool = False) -> int:
        """
        Count users.
        """
        if active_only:
            return sum(1 for user in self._users.values() if getattr(user, "is_active", False))
        return len(self._users)


class InMemoryDeploymentRepository(DeploymentRepository):
    """
    In-memory implementation of DeploymentRepository.
    """

    def __init__(self):
        self._deployments: dict[str, Deployment] = {}

    async def save(self, deployment: Deployment) -> None:
        """
        Save a deployment.
        """
        self._deployments[str(_value(deployment.id))] = deployment

    async def find_by_id(self, deployment_id: DeploymentId) -> Deployment | None:
        """
        Find a deployment by ID.
        """
        return self._deployments.get(str(_value(deployment_id)))

    async def delete(self, deployment_id: DeploymentId) -> None:
        """
        Delete a deployment.
        """
        self._deployments.pop(str(_value(deployment_id)), None)

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Deployment]:
        """
        Find all deployments with pagination.
        """
        deployments = list(self._deployments.values())
        return deployments[offset : offset + limit]

    async def find_active(self) -> list[Deployment]:
        """
        Find active deployments.
        """
        return [
            d for d in self._deployments.values() if _value(d.status) in ["pending", "in_progress"]
        ]

    async def count(
        self,
        environment: DeploymentEnvironment | None = None,
        status: str | None = None,
    ) -> int:
        """
        Count deployments with optional filters.
        """
        deployments = self._deployments.values()

        if environment:
            deployments = [d for d in deployments if _value(d.environment) == _value(environment)]

        if status:
            deployments = [d for d in deployments if _value(d.status) == status]

        return len(list(deployments))


class InMemoryServiceRepository(ServiceRepository):
    """
    In-memory implementation of ServiceRepository.
    """

    def __init__(self):
        self._services: dict[str, Service] = {}

    async def save(self, service: Service) -> None:
        """
        Save a service.
        """
        self._services[str(_value(service.id))] = service

    async def find_by_id(self, service_id: ServiceId) -> Service | None:
        """
        Find a service by ID.
        """
        return self._services.get(str(_value(service_id)))

    async def find_by_name(self, name: ServiceName) -> Service | None:
        """
        Find a service by name.
        """
        for service in self._services.values():
            if _value(service.name) == _value(name):
                return service
        return None

    async def delete(self, service_id: ServiceId) -> None:
        """
        Delete a service.
        """
        self._services.pop(str(_value(service_id)), None)

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Service]:
        """
        Find all services with pagination.
        """
        services = list(self._services.values())
        return services[offset : offset + limit]

    async def find_running(self) -> list[Service]:
        """
        Find running services.
        """
        return [s for s in self._services.values() if _value(s.status) == "running"]


class InMemoryConfigurationRepository(ConfigurationRepository):
    """
    In-memory implementation of ConfigurationRepository.
    """

    def __init__(self):
        self._configurations: dict[str, Configuration] = {}

    async def save(self, configuration: Configuration) -> None:
        """
        Save a configuration.
        """
        self._configurations[str(_value(configuration.key))] = configuration

    async def find_by_id(self, config_id: str) -> Configuration | None:
        """
        Find a configuration by ID (key).
        """
        return self._configurations.get(config_id)

    async def find_by_key(self, key: ConfigKey) -> Configuration | None:
        """
        Find a configuration by key.
        """
        return self._configurations.get(str(_value(key)))

    async def delete(self, config_id: str) -> None:
        """
        Delete a configuration.
        """
        self._configurations.pop(config_id, None)

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Configuration]:
        """
        Find all configurations with pagination.
        """
        configs = list(self._configurations.values())
        return configs[offset : offset + limit]

    async def find_by_namespace(self, namespace: str) -> list[Configuration]:
        """
        Find configurations by namespace.
        """
        return [
            config for config in self._configurations.values() if config.key.namespace == namespace
        ]
