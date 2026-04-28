"""
Deployment-related domain events.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DeploymentCreated:
    """
    Event emitted when a deployment is created.
    """

    aggregate_id: str
    deployment_id: str
    environment: str
    strategy: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "DeploymentCreated"


@dataclass(frozen=True)
class DeploymentStarted:
    """
    Event emitted when a deployment starts.
    """

    aggregate_id: str
    deployment_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "DeploymentStarted"


@dataclass(frozen=True)
class DeploymentCompleted:
    """
    Event emitted when a deployment completes successfully.
    """

    aggregate_id: str
    deployment_id: str
    duration_seconds: float
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "DeploymentCompleted"


@dataclass(frozen=True)
class DeploymentFailed:
    """
    Event emitted when a deployment fails.
    """

    aggregate_id: str
    deployment_id: str
    error_message: str
    duration_seconds: float
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "DeploymentFailed"


@dataclass(frozen=True)
class DeploymentRolledBack:
    """
    Event emitted when a deployment is rolled back.
    """

    aggregate_id: str
    deployment_id: str
    reason: str | None = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "DeploymentRolledBack"
