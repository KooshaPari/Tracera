"""
Deployment-related value objects.
"""

from dataclasses import dataclass
from enum import StrEnum

from pheno.domain.base import ValueObject
from pheno.domain.exceptions import ValidationError


class DeploymentStatusEnum(StrEnum):
    """
    Deployment status enumeration.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class DeploymentStatus(ValueObject):
    """
    Deployment status value object.
    """

    value: DeploymentStatusEnum

    def __post_init__(self):
        """
        Validate deployment status.
        """
        if not isinstance(self.value, DeploymentStatusEnum):
            raise ValidationError(
                f"Invalid deployment status: {self.value}. "
                f"Must be one of {[s.value for s in DeploymentStatusEnum]}",
            )

    def __str__(self) -> str:
        return self.value.value

    def is_terminal(self) -> bool:
        """
        Check if status is terminal (no further transitions).
        """
        return self.value in (
            DeploymentStatusEnum.COMPLETED,
            DeploymentStatusEnum.FAILED,
            DeploymentStatusEnum.CANCELLED,
            DeploymentStatusEnum.ROLLED_BACK,
        )

    def is_active(self) -> bool:
        """
        Check if deployment is actively running.
        """
        return self.value in (
            DeploymentStatusEnum.IN_PROGRESS,
            DeploymentStatusEnum.ROLLING_BACK,
        )

    def can_transition_to(self, new_status: "DeploymentStatus") -> bool:
        """
        Check if transition to new status is valid.
        """
        valid_transitions = {
            DeploymentStatusEnum.PENDING: [
                DeploymentStatusEnum.IN_PROGRESS,
                DeploymentStatusEnum.CANCELLED,
            ],
            DeploymentStatusEnum.IN_PROGRESS: [
                DeploymentStatusEnum.COMPLETED,
                DeploymentStatusEnum.FAILED,
                DeploymentStatusEnum.ROLLING_BACK,
            ],
            DeploymentStatusEnum.FAILED: [
                DeploymentStatusEnum.ROLLING_BACK,
            ],
            DeploymentStatusEnum.ROLLING_BACK: [
                DeploymentStatusEnum.ROLLED_BACK,
                DeploymentStatusEnum.FAILED,
            ],
        }

        allowed = valid_transitions.get(self.value, [])
        return new_status.value in allowed


class DeploymentEnvironmentEnum(StrEnum):
    """
    Deployment environment enumeration.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


@dataclass(frozen=True)
class DeploymentEnvironment(ValueObject):
    """
    Deployment environment value object.
    """

    value: DeploymentEnvironmentEnum

    def __post_init__(self):
        """
        Validate deployment environment.
        """
        if not isinstance(self.value, DeploymentEnvironmentEnum):
            raise ValidationError(
                f"Invalid deployment environment: {self.value}. "
                f"Must be one of {[e.value for e in DeploymentEnvironmentEnum]}",
            )

    def __str__(self) -> str:
        return self.value.value

    def is_production(self) -> bool:
        """
        Check if environment is production.
        """
        return self.value == DeploymentEnvironmentEnum.PRODUCTION

    def requires_approval(self) -> bool:
        """
        Check if environment requires approval.
        """
        return self.value in (
            DeploymentEnvironmentEnum.STAGING,
            DeploymentEnvironmentEnum.PRODUCTION,
        )


class DeploymentStrategyEnum(StrEnum):
    """
    Deployment strategy enumeration.
    """

    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"
    A_B_TESTING = "a_b_testing"


@dataclass(frozen=True)
class DeploymentStrategy(ValueObject):
    """
    Deployment strategy value object.
    """

    value: DeploymentStrategyEnum

    def __post_init__(self):
        """
        Validate deployment strategy.
        """
        if not isinstance(self.value, DeploymentStrategyEnum):
            raise ValidationError(
                f"Invalid deployment strategy: {self.value}. "
                f"Must be one of {[s.value for s in DeploymentStrategyEnum]}",
            )

    def __str__(self) -> str:
        return self.value.value

    def supports_rollback(self) -> bool:
        """
        Check if strategy supports rollback.
        """
        return self.value in (
            DeploymentStrategyEnum.BLUE_GREEN,
            DeploymentStrategyEnum.CANARY,
        )

    def requires_health_checks(self) -> bool:
        """
        Check if strategy requires health checks.
        """
        return self.value in (
            DeploymentStrategyEnum.CANARY,
            DeploymentStrategyEnum.ROLLING,
            DeploymentStrategyEnum.A_B_TESTING,
        )
