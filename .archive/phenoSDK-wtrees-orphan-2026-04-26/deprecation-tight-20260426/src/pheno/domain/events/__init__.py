"""
Domain Events - Things That Happened

Domain events represent significant occurrences in the domain that domain experts
care about. They are immutable facts about the past.

Characteristics:
    - Immutable (frozen dataclasses)
    - Past tense naming (UserCreated, not CreateUser)
    - Contain all relevant data
    - Include timestamp
    - Include aggregate ID

Example:
    >>> from pheno.domain.events import UserCreated
    >>>
    >>> event = UserCreated(
    ...     aggregate_id="user-123",
    ...     user_id="user-123",
    ...     email="user@example.com",
    ...     name="John Doe"
    ... )
"""

from pheno.domain.events.deployment import (
    DeploymentCompleted,
    DeploymentCreated,
    DeploymentFailed,
    DeploymentRolledBack,
    DeploymentStarted,
)
from pheno.domain.events.infrastructure import (
    ServiceCreated,
    ServiceFailed,
    ServiceStarted,
    ServiceStopped,
)
from pheno.domain.events.user import (
    UserCreated,
    UserDeactivated,
    UserUpdated,
)

__all__ = [
    "DeploymentCompleted",
    # Deployment events
    "DeploymentCreated",
    "DeploymentFailed",
    "DeploymentRolledBack",
    "DeploymentStarted",
    # Infrastructure events
    "ServiceCreated",
    "ServiceFailed",
    "ServiceStarted",
    "ServiceStopped",
    # User events
    "UserCreated",
    "UserDeactivated",
    "UserUpdated",
]
