"""FastAPI dependencies for dependency injection.

This module provides FastAPI dependency functions that integrate with the hexagonal
architecture DI container.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from pheno.adapters.container import Container
from pheno.adapters.container_config import get_container as get_global_container
from pheno.application.ports.events import EventPublisher
from pheno.application.ports.repositories import (
    ConfigurationRepository,
    DeploymentRepository,
    ServiceRepository,
    UserRepository,
)
from pheno.application.use_cases.configuration import (
    CreateConfigurationUseCase,
    GetConfigurationUseCase,
    ListConfigurationsUseCase,
    UpdateConfigurationUseCase,
)
from pheno.application.use_cases.deployment import (
    CompleteDeploymentUseCase,
    CreateDeploymentUseCase,
    FailDeploymentUseCase,
    GetDeploymentStatisticsUseCase,
    GetDeploymentUseCase,
    ListDeploymentsUseCase,
    RollbackDeploymentUseCase,
    StartDeploymentUseCase,
)
from pheno.application.use_cases.service import (
    CreateServiceUseCase,
    GetServiceHealthUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
    StartServiceUseCase,
    StopServiceUseCase,
)
from pheno.application.use_cases.user import (
    CreateUserUseCase,
    DeactivateUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)

def get_container() -> Container:
    """
    Get the global DI container.
    """
    return get_global_container()


# Repository dependencies
def get_user_repository(container: Annotated[Container, Depends(get_container)]) -> UserRepository:
    """
    Get user repository from container.
    """
    return container.resolve(UserRepository)


def get_deployment_repository(
    container: Annotated[Container, Depends(get_container)],
) -> DeploymentRepository:
    """
    Get deployment repository from container.
    """
    return container.resolve(DeploymentRepository)


def get_service_repository(
    container: Annotated[Container, Depends(get_container)],
) -> ServiceRepository:
    """
    Get service repository from container.
    """
    return container.resolve(ServiceRepository)


def get_configuration_repository(
    container: Annotated[Container, Depends(get_container)],
) -> ConfigurationRepository:
    """
    Get configuration repository from container.
    """
    return container.resolve(ConfigurationRepository)


def get_event_publisher(container: Annotated[Container, Depends(get_container)]) -> EventPublisher:
    """
    Get event publisher from container.
    """
    return container.resolve(EventPublisher)


# User use case dependencies
def get_create_user_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CreateUserUseCase:
    """
    Get create user use case.
    """
    return CreateUserUseCase(user_repo, event_pub)


def get_update_user_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> UpdateUserUseCase:
    """
    Get update user use case.
    """
    return UpdateUserUseCase(user_repo, event_pub)


def get_get_user_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserUseCase:
    """
    Get get user use case.
    """
    return GetUserUseCase(user_repo)


def get_list_users_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> ListUsersUseCase:
    """
    Get list users use case.
    """
    return ListUsersUseCase(user_repo)


def get_deactivate_user_use_case(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> DeactivateUserUseCase:
    """
    Get deactivate user use case.
    """
    return DeactivateUserUseCase(user_repo, event_pub)


# Deployment use case dependencies
def get_create_deployment_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CreateDeploymentUseCase:
    """
    Get create deployment use case.
    """
    return CreateDeploymentUseCase(deployment_repo, event_pub)


def get_start_deployment_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> StartDeploymentUseCase:
    """
    Get start deployment use case.
    """
    return StartDeploymentUseCase(deployment_repo, event_pub)


def get_complete_deployment_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CompleteDeploymentUseCase:
    """
    Get complete deployment use case.
    """
    return CompleteDeploymentUseCase(deployment_repo, event_pub)


def get_fail_deployment_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> FailDeploymentUseCase:
    """
    Get fail deployment use case.
    """
    return FailDeploymentUseCase(deployment_repo, event_pub)


def get_rollback_deployment_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> RollbackDeploymentUseCase:
    """
    Get rollback deployment use case.
    """
    return RollbackDeploymentUseCase(deployment_repo, event_pub)


def get_get_deployment_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
) -> GetDeploymentUseCase:
    """
    Get get deployment use case.
    """
    return GetDeploymentUseCase(deployment_repo)


def get_list_deployments_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
) -> ListDeploymentsUseCase:
    """
    Get list deployments use case.
    """
    return ListDeploymentsUseCase(deployment_repo)


def get_deployment_statistics_use_case(
    deployment_repo: Annotated[DeploymentRepository, Depends(get_deployment_repository)],
) -> GetDeploymentStatisticsUseCase:
    """
    Get deployment statistics use case.
    """
    return GetDeploymentStatisticsUseCase(deployment_repo)


# Service use case dependencies
def get_create_service_use_case(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> CreateServiceUseCase:
    """
    Get create service use case.
    """
    return CreateServiceUseCase(service_repo, event_pub)


def get_start_service_use_case(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> StartServiceUseCase:
    """
    Get start service use case.
    """
    return StartServiceUseCase(service_repo, event_pub)


def get_stop_service_use_case(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
    event_pub: Annotated[EventPublisher, Depends(get_event_publisher)],
) -> StopServiceUseCase:
    """
    Get stop service use case.
    """
    return StopServiceUseCase(service_repo, event_pub)


def get_get_service_use_case(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
) -> GetServiceUseCase:
    """
    Get get service use case.
    """
    return GetServiceUseCase(service_repo)


def get_list_services_use_case(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
) -> ListServicesUseCase:
    """
    Get list services use case.
    """
    return ListServicesUseCase(service_repo)


def get_service_health_use_case(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
) -> GetServiceHealthUseCase:
    """
    Get service health use case.
    """
    return GetServiceHealthUseCase(service_repo)


# Configuration use case dependencies
def get_create_configuration_use_case(
    config_repo: Annotated[ConfigurationRepository, Depends(get_configuration_repository)],
) -> CreateConfigurationUseCase:
    """
    Get create configuration use case.
    """
    return CreateConfigurationUseCase(config_repo)


def get_update_configuration_use_case(
    config_repo: Annotated[ConfigurationRepository, Depends(get_configuration_repository)],
) -> UpdateConfigurationUseCase:
    """
    Get update configuration use case.
    """
    return UpdateConfigurationUseCase(config_repo)


def get_get_configuration_use_case(
    config_repo: Annotated[ConfigurationRepository, Depends(get_configuration_repository)],
) -> GetConfigurationUseCase:
    """
    Get get configuration use case.
    """
    return GetConfigurationUseCase(config_repo)


def get_list_configurations_use_case(
    config_repo: Annotated[ConfigurationRepository, Depends(get_configuration_repository)],
) -> ListConfigurationsUseCase:
    """
    Get list configurations use case.
    """
    return ListConfigurationsUseCase(config_repo)
