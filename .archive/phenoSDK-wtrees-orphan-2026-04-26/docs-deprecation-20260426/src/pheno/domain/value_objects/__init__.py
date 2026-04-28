"""
Domain Value Objects - Immutable domain primitives

Value objects are immutable objects that represent descriptive aspects of the domain
with no conceptual identity. They are defined only by their attributes.

Characteristics:
    - Immutable (frozen dataclasses)
    - No identity (equality based on attributes)
    - Self-validating (validation in __post_init__)
    - Type-safe (full type hints)

Example:
    >>> email = Email("user@example.com")
    >>> port = Port(8080)
    >>> config_key = ConfigKey("database.url")
"""

from pheno.domain.value_objects.common import (
    URL,
    ConfigKey,
    ConfigValue,
    DeploymentId,
    Email,
    Port,
    ServiceId,
    UserId,
)
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStrategy,
)
from pheno.domain.value_objects.infrastructure import (
    ServiceName,
    ServicePort,
    ServiceStatus,
)

__all__ = [
    "URL",
    "ConfigKey",
    "ConfigValue",
    "DeploymentEnvironment",
    "DeploymentId",
    # Deployment value objects
    "DeploymentStatus",
    "DeploymentStrategy",
    # Common value objects
    "Email",
    "Port",
    "ServiceId",
    "ServiceName",
    "ServicePort",
    # Infrastructure value objects
    "ServiceStatus",
    "UserId",
]
