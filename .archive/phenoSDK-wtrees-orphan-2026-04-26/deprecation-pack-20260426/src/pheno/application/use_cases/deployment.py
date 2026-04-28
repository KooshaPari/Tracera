"""
Deployment use cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.application.dtos.deployment import (
    CreateDeploymentDTO,
    DeploymentDTO,
    DeploymentFilterDTO,
    DeploymentStatisticsDTO,
)
from pheno.domain.entities.deployment import Deployment
from pheno.domain.exceptions.deployment import (
    DeploymentNotFoundError,
)
from pheno.domain.value_objects.common import DeploymentId

if TYPE_CHECKING:
    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import DeploymentRepository


class CreateDeploymentUseCase:
    """
    Use case for creating a new deployment.
    """

    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_publisher: EventPublisher,
    ):
        self.deployment_repository = deployment_repository
        self.event_publisher = event_publisher

    async def execute(self, dto: CreateDeploymentDTO) -> DeploymentDTO:
        """
        Create a new deployment.
        """
        # Create deployment entity
        environment, strategy = dto.to_domain_params()
        deployment = Deployment.create(environment, strategy)
        if isinstance(deployment, tuple):
            deployment = deployment[0]

        # Save to repository
        await self.deployment_repository.save(deployment)

        # Publish domain events
        for event in deployment.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        deployment.clear_events()

        return DeploymentDTO.from_entity(deployment)


class StartDeploymentUseCase:
    """
    Use case for starting a deployment.
    """

    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_publisher: EventPublisher,
    ):
        self.deployment_repository = deployment_repository
        self.event_publisher = event_publisher

    async def execute(self, deployment_id: str) -> DeploymentDTO:
        """
        Start a deployment.
        """
        # Find deployment
        deployment = await self.deployment_repository.find_by_id(DeploymentId(deployment_id))
        if not deployment:
            raise DeploymentNotFoundError(deployment_id)

        # Start deployment
        deployment.start()

        # Save to repository
        await self.deployment_repository.save(deployment)

        # Publish domain events
        for event in deployment.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        deployment.clear_events()

        return DeploymentDTO.from_entity(deployment)


class CompleteDeploymentUseCase:
    """
    Use case for completing a deployment.
    """

    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_publisher: EventPublisher,
    ):
        self.deployment_repository = deployment_repository
        self.event_publisher = event_publisher

    async def execute(self, deployment_id: str) -> DeploymentDTO:
        """
        Complete a deployment.
        """
        # Find deployment
        deployment = await self.deployment_repository.find_by_id(DeploymentId(deployment_id))
        if not deployment:
            raise DeploymentNotFoundError(deployment_id)

        # Complete deployment
        deployment.complete()

        # Save to repository
        await self.deployment_repository.save(deployment)

        # Publish domain events
        for event in deployment.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        deployment.clear_events()

        return DeploymentDTO.from_entity(deployment)


class FailDeploymentUseCase:
    """
    Use case for failing a deployment.
    """

    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_publisher: EventPublisher,
    ):
        self.deployment_repository = deployment_repository
        self.event_publisher = event_publisher

    async def execute(self, deployment_id: str, reason: str) -> DeploymentDTO:
        """
        Fail a deployment.
        """
        # Find deployment
        deployment = await self.deployment_repository.find_by_id(DeploymentId(deployment_id))
        if not deployment:
            raise DeploymentNotFoundError(deployment_id)

        # Fail deployment
        deployment.fail(reason)

        # Save to repository
        await self.deployment_repository.save(deployment)

        # Publish domain events
        for event in deployment.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        deployment.clear_events()

        return DeploymentDTO.from_entity(deployment)


class RollbackDeploymentUseCase:
    """
    Use case for rolling back a deployment.
    """

    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        event_publisher: EventPublisher,
    ):
        self.deployment_repository = deployment_repository
        self.event_publisher = event_publisher

    async def execute(self, deployment_id: str, reason: str) -> DeploymentDTO:
        """
        Rollback a deployment.
        """
        # Find deployment
        deployment = await self.deployment_repository.find_by_id(DeploymentId(deployment_id))
        if not deployment:
            raise DeploymentNotFoundError(deployment_id)

        # Rollback deployment
        deployment.rollback(reason)

        # Save to repository
        await self.deployment_repository.save(deployment)

        # Publish domain events
        for event in deployment.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        deployment.clear_events()

        return DeploymentDTO.from_entity(deployment)


class GetDeploymentUseCase:
    """
    Use case for getting a deployment by ID.
    """

    def __init__(self, deployment_repository: DeploymentRepository):
        self.deployment_repository = deployment_repository

    async def execute(self, deployment_id: str) -> DeploymentDTO:
        """
        Get a deployment by ID.
        """
        deployment = await self.deployment_repository.find_by_id(DeploymentId(deployment_id))
        if not deployment:
            raise DeploymentNotFoundError(deployment_id)

        return DeploymentDTO.from_entity(deployment)


class ListDeploymentsUseCase:
    """
    Use case for listing deployments.
    """

    def __init__(self, deployment_repository: DeploymentRepository):
        self.deployment_repository = deployment_repository

    async def execute(self, filter_dto: DeploymentFilterDTO) -> list[DeploymentDTO]:
        """
        List deployments with optional filters.
        """
        deployments = await self.deployment_repository.find_all(
            limit=filter_dto.limit,
            offset=filter_dto.offset,
        )
        return [DeploymentDTO.from_entity(d) for d in deployments]


class GetDeploymentStatisticsUseCase:
    """
    Use case for getting deployment statistics.
    """

    def __init__(self, deployment_repository: DeploymentRepository):
        self.deployment_repository = deployment_repository

    async def execute(self, environment: str | None = None) -> DeploymentStatisticsDTO:
        """
        Get deployment statistics.
        """
        from pheno.domain.value_objects.deployment import DeploymentEnvironment

        env = DeploymentEnvironment(environment) if environment else None

        # Get counts for each status
        total = await self.deployment_repository.count(environment=env)
        pending = await self.deployment_repository.count(environment=env, status="pending")
        in_progress = await self.deployment_repository.count(environment=env, status="in_progress")
        completed = await self.deployment_repository.count(environment=env, status="completed")
        failed = await self.deployment_repository.count(environment=env, status="failed")
        rolled_back = await self.deployment_repository.count(environment=env, status="rolled_back")

        return DeploymentStatisticsDTO(
            total=total,
            pending=pending,
            in_progress=in_progress,
            completed=completed,
            failed=failed,
            rolled_back=rolled_back,
        )
