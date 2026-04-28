"""Data Transfer Objects (DTOs) for the application layer.

DTOs are used to transfer data between layers without exposing domain entities. They are
simple dataclasses with validation and serialization support.
"""

from .configuration import (
    ConfigurationDTO,
    ConfigurationFilterDTO,
    CreateConfigurationDTO,
    UpdateConfigurationDTO,
)
from .deployment import (
    CreateDeploymentDTO,
    DeploymentDTO,
    DeploymentFilterDTO,
    DeploymentStatisticsDTO,
    UpdateDeploymentDTO,
)
from .service import (
    CreateServiceDTO,
    ServiceDTO,
    ServiceFilterDTO,
    ServiceHealthDTO,
    UpdateServiceDTO,
)
from .user import (
    CreateUserDTO,
    UpdateUserDTO,
    UserDTO,
    UserFilterDTO,
)

__all__ = [
    "ConfigurationDTO",
    "ConfigurationFilterDTO",
    # Configuration DTOs
    "CreateConfigurationDTO",
    # Deployment DTOs
    "CreateDeploymentDTO",
    # Service DTOs
    "CreateServiceDTO",
    # User DTOs
    "CreateUserDTO",
    "DeploymentDTO",
    "DeploymentFilterDTO",
    "DeploymentStatisticsDTO",
    "ServiceDTO",
    "ServiceFilterDTO",
    "ServiceHealthDTO",
    "UpdateConfigurationDTO",
    "UpdateDeploymentDTO",
    "UpdateServiceDTO",
    "UpdateUserDTO",
    "UserDTO",
    "UserFilterDTO",
]
