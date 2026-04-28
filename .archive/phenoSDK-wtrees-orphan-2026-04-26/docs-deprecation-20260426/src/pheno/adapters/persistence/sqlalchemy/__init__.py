"""SQLAlchemy persistence adapters.

This package contains SQLAlchemy-based repository implementations for production
database persistence.
"""

from .models import Base, ConfigurationModel, DeploymentModel, ServiceModel, UserModel
from .repositories import (
    SQLAlchemyConfigurationRepository,
    SQLAlchemyDeploymentRepository,
    SQLAlchemyServiceRepository,
    SQLAlchemyUserRepository,
)
from .session import create_engine_from_config, get_session

__all__ = [
    # Models
    "Base",
    "ConfigurationModel",
    "DeploymentModel",
    "SQLAlchemyConfigurationRepository",
    "SQLAlchemyDeploymentRepository",
    "SQLAlchemyServiceRepository",
    # Repositories
    "SQLAlchemyUserRepository",
    "ServiceModel",
    "UserModel",
    "create_engine_from_config",
    # Session management
    "get_session",
]
