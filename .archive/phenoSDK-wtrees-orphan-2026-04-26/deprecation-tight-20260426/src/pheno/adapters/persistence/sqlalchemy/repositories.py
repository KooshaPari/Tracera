"""SQLAlchemy repository implementations.

These repositories implement the repository ports using SQLAlchemy for database
persistence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from pheno.application.ports.repositories import (
    ConfigurationRepository,
    DeploymentRepository,
    ServiceRepository,
    UserRepository,
)
from pheno.domain.value_objects.common import ConfigKey, Email, UserId

from .mappers import (
    ConfigurationMapper,
    DeploymentMapper,
    ServiceMapper,
    UserMapper,
)
from .models import ConfigurationModel, DeploymentModel, ServiceModel, UserModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from pheno.domain.entities.configuration import Configuration
    from pheno.domain.entities.deployment import Deployment
    from pheno.domain.entities.service import Service
    from pheno.domain.entities.user import User
    from pheno.domain.value_objects.deployment import (
        DeploymentEnvironment,
        DeploymentId,
    )
    from pheno.domain.value_objects.infrastructure import (
        ServiceId,
        ServiceName,
    )


class SQLAlchemyUserRepository(UserRepository):
    """
    SQLAlchemy implementation of UserRepository.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.mapper = UserMapper()

    async def save(self, user: User) -> None:
        """
        Save a user.
        """
        model = self.mapper.to_model(user)
        self.session.add(model)
        await self.session.flush()

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find a user by ID.
        """
        stmt = select(UserModel).where(UserModel.id == str(user_id.value))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.to_entity(model)

    async def find_by_email(self, email: Email) -> User | None:
        """
        Find a user by email.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.to_entity(model)

    async def delete(self, user_id: UserId) -> None:
        """
        Delete a user.
        """
        stmt = select(UserModel).where(UserModel.id == str(user_id.value))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """
        Find all users with pagination.
        """
        stmt = select(UserModel).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def count(self, active_only: bool = False) -> int:
        """
        Count users.
        """
        from sqlalchemy import func

        stmt = select(func.count(UserModel.id))
        if active_only:
            stmt = stmt.where(UserModel.is_active)

        result = await self.session.execute(stmt)
        return result.scalar_one()


class SQLAlchemyDeploymentRepository(DeploymentRepository):
    """
    SQLAlchemy implementation of DeploymentRepository.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.mapper = DeploymentMapper()

    async def save(self, deployment: Deployment) -> None:
        """
        Save a deployment.
        """
        model = self.mapper.to_model(deployment)
        self.session.add(model)
        await self.session.flush()

    async def find_by_id(self, deployment_id: DeploymentId) -> Deployment | None:
        """
        Find a deployment by ID.
        """
        stmt = select(DeploymentModel).where(DeploymentModel.id == str(deployment_id.value))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.to_entity(model)

    async def delete(self, deployment_id: DeploymentId) -> None:
        """
        Delete a deployment.
        """
        stmt = select(DeploymentModel).where(DeploymentModel.id == str(deployment_id.value))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Deployment]:
        """
        Find all deployments with pagination.
        """
        stmt = select(DeploymentModel).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_active(self) -> list[Deployment]:
        """
        Find active deployments.
        """
        stmt = select(DeploymentModel).where(DeploymentModel.status.in_(["pending", "in_progress"]))
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def count(
        self,
        environment: DeploymentEnvironment | None = None,
        status: str | None = None,
    ) -> int:
        """
        Count deployments with optional filters.
        """
        from sqlalchemy import func

        stmt = select(func.count(DeploymentModel.id))

        if environment:
            stmt = stmt.where(DeploymentModel.environment == environment.value)

        if status:
            stmt = stmt.where(DeploymentModel.status == status)

        result = await self.session.execute(stmt)
        return result.scalar_one()


class SQLAlchemyServiceRepository(ServiceRepository):
    """
    SQLAlchemy implementation of ServiceRepository.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.mapper = ServiceMapper()

    async def save(self, service: Service) -> None:
        """
        Save a service.
        """
        model = self.mapper.to_model(service)
        self.session.add(model)
        await self.session.flush()

    async def find_by_id(self, service_id: ServiceId) -> Service | None:
        """
        Find a service by ID.
        """
        stmt = select(ServiceModel).where(ServiceModel.id == str(service_id.value))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.to_entity(model)

    async def find_by_name(self, name: ServiceName) -> Service | None:
        """
        Find a service by name.
        """
        stmt = select(ServiceModel).where(ServiceModel.name == name.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.to_entity(model)

    async def delete(self, service_id: ServiceId) -> None:
        """
        Delete a service.
        """
        stmt = select(ServiceModel).where(ServiceModel.id == str(service_id.value))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Service]:
        """
        Find all services with pagination.
        """
        stmt = select(ServiceModel).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_running(self) -> list[Service]:
        """
        Find running services.
        """
        stmt = select(ServiceModel).where(ServiceModel.status == "running")
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]


class SQLAlchemyConfigurationRepository(ConfigurationRepository):
    """
    SQLAlchemy implementation of ConfigurationRepository.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.mapper = ConfigurationMapper()

    async def save(self, configuration: Configuration) -> None:
        """
        Save a configuration.
        """
        model = self.mapper.to_model(configuration)
        self.session.add(model)
        await self.session.flush()

    async def find_by_id(self, config_id: str) -> Configuration | None:
        """
        Find a configuration by ID (key).
        """
        return await self.find_by_key(ConfigKey(config_id))

    async def find_by_key(self, key: ConfigKey) -> Configuration | None:
        """
        Find a configuration by key.
        """
        stmt = select(ConfigurationModel).where(ConfigurationModel.key == key.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.to_entity(model)

    async def delete(self, config_id: str) -> None:
        """
        Delete a configuration.
        """
        stmt = select(ConfigurationModel).where(ConfigurationModel.key == config_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[Configuration]:
        """
        Find all configurations with pagination.
        """
        stmt = select(ConfigurationModel).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_namespace(self, namespace: str) -> list[Configuration]:
        """
        Find configurations by namespace.
        """
        stmt = select(ConfigurationModel).where(ConfigurationModel.key.like(f"{namespace}.%"))
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]
