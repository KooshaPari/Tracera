"""
Deployment DTOs for data transfer between layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pheno.domain.entities.deployment import Deployment
from pheno.domain.value_objects.common import DeploymentId
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStrategy,
)


@dataclass(frozen=True)
class CreateDeploymentDTO:
    """
    DTO for creating a new deployment.
    """

    environment: str
    strategy: str

    def to_domain_params(self) -> tuple[DeploymentEnvironment, DeploymentStrategy]:
        """
        Convert to domain entity creation parameters.
        """
        return (
            DeploymentEnvironment(self.environment),
            DeploymentStrategy(self.strategy),
        )


@dataclass(frozen=True)
class UpdateDeploymentDTO:
    """
    DTO for updating a deployment.
    """

    deployment_id: str
    status: str | None = None

    def get_deployment_id(self) -> DeploymentId:
        """
        Get the deployment ID as a domain value object.
        """
        return DeploymentId(self.deployment_id)

    def get_status(self) -> DeploymentStatus | None:
        """
        Get the status as a domain value object.
        """
        return DeploymentStatus(self.status) if self.status else None


@dataclass(frozen=True)
class DeploymentDTO:
    """
    DTO for deployment data.
    """

    id: str
    environment: str
    strategy: str
    status: str
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def from_entity(cls, deployment: Deployment) -> DeploymentDTO:
        """
        Create DTO from domain entity.
        """
        return cls(
            id=str(deployment.id.value),
            environment=deployment.environment.value,
            strategy=deployment.strategy.value,
            status=deployment.status.value,
            created_at=deployment.created_at,
            updated_at=deployment.updated_at,
            started_at=deployment.started_at,
            completed_at=deployment.completed_at,
        )


@dataclass(frozen=True)
class DeploymentFilterDTO:
    """
    DTO for filtering deployments.
    """

    environment: str | None = None
    status: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class DeploymentStatisticsDTO:
    """
    DTO for deployment statistics.
    """

    total: int
    pending: int
    in_progress: int
    completed: int
    failed: int
    rolled_back: int
