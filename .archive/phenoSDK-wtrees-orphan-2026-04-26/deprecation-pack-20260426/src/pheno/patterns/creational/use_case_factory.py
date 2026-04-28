"""Use Case Factory for creating application use cases with dependencies.

This factory encapsulates the creation of use cases with their required dependencies,
following the dependency injection pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

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

if TYPE_CHECKING:
    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import (
        ConfigurationRepository,
        DeploymentRepository,
        ServiceRepository,
        UserRepository,
    )

T = TypeVar("T")


class UseCaseFactory:
    """Factory for creating use cases with their dependencies.

    This factory centralizes use case creation and ensures all dependencies are properly
    injected.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        deployment_repository: DeploymentRepository,
        service_repository: ServiceRepository,
        configuration_repository: ConfigurationRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize the use case factory.

        Args:
            user_repository: User repository implementation
            deployment_repository: Deployment repository implementation
            service_repository: Service repository implementation
            configuration_repository: Configuration repository implementation
            event_publisher: Event publisher implementation
        """
        self.user_repository = user_repository
        self.deployment_repository = deployment_repository
        self.service_repository = service_repository
        self.configuration_repository = configuration_repository
        self.event_publisher = event_publisher

    # ========== User Use Cases ==========

    def create_user_use_case(self) -> CreateUserUseCase:
        """
        Create a CreateUserUseCase instance.
        """
        return CreateUserUseCase(self.user_repository, self.event_publisher)

    def update_user_use_case(self) -> UpdateUserUseCase:
        """
        Create an UpdateUserUseCase instance.
        """
        return UpdateUserUseCase(self.user_repository, self.event_publisher)

    def get_user_use_case(self) -> GetUserUseCase:
        """
        Create a GetUserUseCase instance.
        """
        return GetUserUseCase(self.user_repository)

    def list_users_use_case(self) -> ListUsersUseCase:
        """
        Create a ListUsersUseCase instance.
        """
        return ListUsersUseCase(self.user_repository)

    def deactivate_user_use_case(self) -> DeactivateUserUseCase:
        """
        Create a DeactivateUserUseCase instance.
        """
        return DeactivateUserUseCase(self.user_repository, self.event_publisher)

    # ========== Deployment Use Cases ==========

    def create_deployment_use_case(self) -> CreateDeploymentUseCase:
        """
        Create a CreateDeploymentUseCase instance.
        """
        return CreateDeploymentUseCase(self.deployment_repository, self.event_publisher)

    def start_deployment_use_case(self) -> StartDeploymentUseCase:
        """
        Create a StartDeploymentUseCase instance.
        """
        return StartDeploymentUseCase(self.deployment_repository, self.event_publisher)

    def complete_deployment_use_case(self) -> CompleteDeploymentUseCase:
        """
        Create a CompleteDeploymentUseCase instance.
        """
        return CompleteDeploymentUseCase(self.deployment_repository, self.event_publisher)

    def fail_deployment_use_case(self) -> FailDeploymentUseCase:
        """
        Create a FailDeploymentUseCase instance.
        """
        return FailDeploymentUseCase(self.deployment_repository, self.event_publisher)

    def rollback_deployment_use_case(self) -> RollbackDeploymentUseCase:
        """
        Create a RollbackDeploymentUseCase instance.
        """
        return RollbackDeploymentUseCase(self.deployment_repository, self.event_publisher)

    def get_deployment_use_case(self) -> GetDeploymentUseCase:
        """
        Create a GetDeploymentUseCase instance.
        """
        return GetDeploymentUseCase(self.deployment_repository)

    def list_deployments_use_case(self) -> ListDeploymentsUseCase:
        """
        Create a ListDeploymentsUseCase instance.
        """
        return ListDeploymentsUseCase(self.deployment_repository)

    def get_deployment_statistics_use_case(self) -> GetDeploymentStatisticsUseCase:
        """
        Create a GetDeploymentStatisticsUseCase instance.
        """
        return GetDeploymentStatisticsUseCase(self.deployment_repository)

    # ========== Service Use Cases ==========

    def create_service_use_case(self) -> CreateServiceUseCase:
        """
        Create a CreateServiceUseCase instance.
        """
        return CreateServiceUseCase(self.service_repository, self.event_publisher)

    def start_service_use_case(self) -> StartServiceUseCase:
        """
        Create a StartServiceUseCase instance.
        """
        return StartServiceUseCase(self.service_repository, self.event_publisher)

    def stop_service_use_case(self) -> StopServiceUseCase:
        """
        Create a StopServiceUseCase instance.
        """
        return StopServiceUseCase(self.service_repository, self.event_publisher)

    def get_service_use_case(self) -> GetServiceUseCase:
        """
        Create a GetServiceUseCase instance.
        """
        return GetServiceUseCase(self.service_repository)

    def list_services_use_case(self) -> ListServicesUseCase:
        """
        Create a ListServicesUseCase instance.
        """
        return ListServicesUseCase(self.service_repository)

    def get_service_health_use_case(self) -> GetServiceHealthUseCase:
        """
        Create a GetServiceHealthUseCase instance.
        """
        return GetServiceHealthUseCase(self.service_repository)

    # ========== Configuration Use Cases ==========

    def create_configuration_use_case(self) -> CreateConfigurationUseCase:
        """
        Create a CreateConfigurationUseCase instance.
        """
        return CreateConfigurationUseCase(self.configuration_repository)

    def update_configuration_use_case(self) -> UpdateConfigurationUseCase:
        """
        Create an UpdateConfigurationUseCase instance.
        """
        return UpdateConfigurationUseCase(self.configuration_repository)

    def get_configuration_use_case(self) -> GetConfigurationUseCase:
        """
        Create a GetConfigurationUseCase instance.
        """
        return GetConfigurationUseCase(self.configuration_repository)

    def list_configurations_use_case(self) -> ListConfigurationsUseCase:
        """
        Create a ListConfigurationsUseCase instance.
        """
        return ListConfigurationsUseCase(self.configuration_repository)

    # ========== Generic Use Case Creation ==========

    def create(self, use_case_class: type[T]) -> T:
        """Create a use case instance by class.

        Args:
            use_case_class: The use case class to instantiate

        Returns:
            Instance of the use case

        Raises:
            ValueError: If use case class is not recognized
        """
        # Map use case classes to factory methods
        use_case_map = {
            CreateUserUseCase: self.create_user_use_case,
            UpdateUserUseCase: self.update_user_use_case,
            GetUserUseCase: self.get_user_use_case,
            ListUsersUseCase: self.list_users_use_case,
            DeactivateUserUseCase: self.deactivate_user_use_case,
            CreateDeploymentUseCase: self.create_deployment_use_case,
            StartDeploymentUseCase: self.start_deployment_use_case,
            CompleteDeploymentUseCase: self.complete_deployment_use_case,
            FailDeploymentUseCase: self.fail_deployment_use_case,
            RollbackDeploymentUseCase: self.rollback_deployment_use_case,
            GetDeploymentUseCase: self.get_deployment_use_case,
            ListDeploymentsUseCase: self.list_deployments_use_case,
            GetDeploymentStatisticsUseCase: self.get_deployment_statistics_use_case,
            CreateServiceUseCase: self.create_service_use_case,
            StartServiceUseCase: self.start_service_use_case,
            StopServiceUseCase: self.stop_service_use_case,
            GetServiceUseCase: self.get_service_use_case,
            ListServicesUseCase: self.list_services_use_case,
            GetServiceHealthUseCase: self.get_service_health_use_case,
            CreateConfigurationUseCase: self.create_configuration_use_case,
            UpdateConfigurationUseCase: self.update_configuration_use_case,
            GetConfigurationUseCase: self.get_configuration_use_case,
            ListConfigurationsUseCase: self.list_configurations_use_case,
        }

        factory_method = use_case_map.get(use_case_class)
        if not factory_method:
            raise ValueError(f"Unknown use case class: {use_case_class}")

        return factory_method()
