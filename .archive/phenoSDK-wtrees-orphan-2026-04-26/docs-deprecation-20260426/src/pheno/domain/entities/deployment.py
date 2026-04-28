"""
Deployment entity.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime

from pheno.domain.base import AggregateRoot
from pheno.domain.events import (
    DeploymentCompleted,
    DeploymentCreated,
    DeploymentFailed,
    DeploymentRolledBack,
    DeploymentStarted,
)
from pheno.domain.exceptions import (
    InvalidDeploymentStateError,
    ValidationError,
)
from pheno.domain.value_objects import (
    DeploymentEnvironment,
    DeploymentId,
    DeploymentStatus,
    DeploymentStrategy,
)
from pheno.domain.value_objects.deployment import DeploymentStatusEnum


@dataclass
class Deployment(AggregateRoot):
    """Deployment aggregate root.

    Represents a deployment of an application to an environment.
    Manages deployment lifecycle and state transitions.

    Business Rules:
        - Deployment must have valid environment and strategy
        - State transitions must follow valid paths
        - Only active deployments can be completed or failed
        - Terminal states cannot transition
        - Deployment emits events for all state changes
    """

    environment: DeploymentEnvironment = field(default=None)
    strategy: DeploymentStrategy = field(default=None)
    status: DeploymentStatus = field(default=None)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None

    @classmethod
    def create(
        cls,
        environment: DeploymentEnvironment,
        strategy: DeploymentStrategy,
    ) -> tuple["Deployment", DeploymentCreated]:
        """Factory method to create a new deployment.

        Args:
            environment: Deployment environment
            strategy: Deployment strategy

        Returns:
            Tuple of (Deployment entity, DeploymentCreated event)
        """
        deployment_id = DeploymentId.generate()

        deployment = cls(
            id=str(deployment_id),
            environment=environment,
            strategy=strategy,
            status=DeploymentStatus(DeploymentStatusEnum.PENDING),
        )

        event = DeploymentCreated(
            aggregate_id=str(deployment_id),
            deployment_id=str(deployment_id),
            environment=str(environment),
            strategy=str(strategy),
        )

        deployment.add_event(event)
        return deployment, event

    def start(self) -> "Deployment":
        """Start the deployment.

        Returns:
            Updated deployment entity

        Raises:
            InvalidDeploymentStateError: If deployment cannot be started
        """
        new_status = DeploymentStatus(DeploymentStatusEnum.IN_PROGRESS)

        if not self.status.can_transition_to(new_status):
            raise InvalidDeploymentStateError(str(self.status), str(new_status))

        now = datetime.utcnow()
        started_deployment = replace(
            self,
            status=new_status,
            started_at=now,
            updated_at=now,
        )

        event = DeploymentStarted(
            aggregate_id=str(self.id),
            deployment_id=str(self.id),
        )

        started_deployment.add_event(event)
        return started_deployment

    def complete(self) -> "Deployment":
        """Mark deployment as completed.

        Returns:
            Updated deployment entity

        Raises:
            InvalidDeploymentStateError: If deployment cannot be completed
            ValidationError: If deployment was never started
        """
        if not self.started_at:
            raise ValidationError("Cannot complete deployment that was never started")

        new_status = DeploymentStatus(DeploymentStatusEnum.COMPLETED)

        if not self.status.can_transition_to(new_status):
            raise InvalidDeploymentStateError(str(self.status), str(new_status))

        now = datetime.utcnow()
        duration = (now - self.started_at).total_seconds()

        completed_deployment = replace(
            self,
            status=new_status,
            completed_at=now,
            updated_at=now,
        )

        event = DeploymentCompleted(
            aggregate_id=str(self.id),
            deployment_id=str(self.id),
            duration_seconds=duration,
        )

        completed_deployment.add_event(event)
        return completed_deployment

    def fail(self, error_message: str) -> "Deployment":
        """Mark deployment as failed.

        Args:
            error_message: Error message describing the failure

        Returns:
            Updated deployment entity

        Raises:
            InvalidDeploymentStateError: If deployment cannot be failed
            ValidationError: If error message is empty
        """
        if not error_message or not error_message.strip():
            raise ValidationError("Error message cannot be empty")

        if not self.started_at:
            raise ValidationError("Cannot fail deployment that was never started")

        new_status = DeploymentStatus(DeploymentStatusEnum.FAILED)

        if not self.status.can_transition_to(new_status):
            raise InvalidDeploymentStateError(str(self.status), str(new_status))

        now = datetime.utcnow()
        duration = (now - self.started_at).total_seconds()

        failed_deployment = replace(
            self,
            status=new_status,
            error_message=error_message.strip(),
            completed_at=now,
            updated_at=now,
        )

        event = DeploymentFailed(
            aggregate_id=str(self.id),
            deployment_id=str(self.id),
            error_message=error_message.strip(),
            duration_seconds=duration,
        )

        failed_deployment.add_event(event)
        return failed_deployment

    def rollback(self, reason: str | None = None) -> "Deployment":
        """Rollback the deployment.

        Args:
            reason: Optional reason for rollback

        Returns:
            Updated deployment entity

        Raises:
            InvalidDeploymentStateError: If deployment cannot be rolled back
            ValidationError: If strategy doesn't support rollback
        """
        if not self.strategy.supports_rollback():
            raise ValidationError(f"Deployment strategy {self.strategy} does not support rollback")

        new_status = DeploymentStatus(DeploymentStatusEnum.ROLLING_BACK)

        if not self.status.can_transition_to(new_status):
            raise InvalidDeploymentStateError(str(self.status), str(new_status))

        rolling_back_deployment = replace(
            self,
            status=new_status,
            updated_at=datetime.utcnow(),
        )

        # Immediately transition to rolled back
        rolled_back_status = DeploymentStatus(DeploymentStatusEnum.ROLLED_BACK)
        rolled_back_deployment = replace(
            rolling_back_deployment,
            status=rolled_back_status,
            completed_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        event = DeploymentRolledBack(
            aggregate_id=str(self.id),
            deployment_id=str(self.id),
            reason=reason,
        )

        rolled_back_deployment.add_event(event)
        return rolled_back_deployment

    def is_terminal(self) -> bool:
        """
        Check if deployment is in a terminal state.
        """
        return self.status.is_terminal()

    def is_active(self) -> bool:
        """
        Check if deployment is actively running.
        """
        return self.status.is_active()

    def duration_seconds(self) -> float | None:
        """
        Get deployment duration in seconds.
        """
        if not self.started_at:
            return None

        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

    def __str__(self) -> str:
        return f"Deployment({self.id}, {self.environment}, {self.status})"
