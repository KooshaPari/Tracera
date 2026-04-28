"""
Domain Exceptions - Business Rule Violations

Domain exceptions represent violations of business rules and invariants.
They should be raised when domain logic constraints are violated.

Exception Hierarchy:
    DomainError (base)
    ├── ValidationError (invalid input/state)
    ├── BusinessRuleViolation (business logic violation)
    ├── EntityNotFoundError (entity doesn't exist)
    ├── EntityAlreadyExistsError (duplicate entity)
    ├── InvalidStateTransitionError (illegal state change)
    └── InvariantViolationError (domain invariant broken)

Example:
    >>> from pheno.domain.exceptions import ValidationError
    >>>
    >>> if not email:
    ...     raise ValidationError("Email cannot be empty")
"""

from pheno.domain.exceptions.base import (
    BusinessRuleViolation,
    DomainError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    InvariantViolationError,
    ValidationError,
)
from pheno.domain.exceptions.deployment import (
    DeploymentAlreadyExistsError,
    DeploymentNotFoundError,
    InvalidDeploymentStateError,
)
from pheno.domain.exceptions.infrastructure import (
    InvalidServiceStateError,
    PortAlreadyInUseError,
    ServiceAlreadyExistsError,
    ServiceNotFoundError,
)
from pheno.domain.exceptions.user import (
    UserAlreadyExistsError,
    UserInactiveError,
    UserNotFoundError,
)

__all__ = [
    "BusinessRuleViolation",
    "DeploymentAlreadyExistsError",
    # Deployment exceptions
    "DeploymentNotFoundError",
    # Base exceptions
    "DomainError",
    "EntityAlreadyExistsError",
    "EntityNotFoundError",
    "InvalidDeploymentStateError",
    "InvalidServiceStateError",
    "InvalidStateTransitionError",
    "InvariantViolationError",
    "PortAlreadyInUseError",
    "ServiceAlreadyExistsError",
    # Infrastructure exceptions
    "ServiceNotFoundError",
    "UserAlreadyExistsError",
    "UserInactiveError",
    # User exceptions
    "UserNotFoundError",
    "ValidationError",
]
