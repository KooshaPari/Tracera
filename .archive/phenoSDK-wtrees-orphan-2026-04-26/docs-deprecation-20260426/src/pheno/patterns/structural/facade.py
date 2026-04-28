"""Facade Pattern implementations for simplifying complex subsystems.

Facades provide a simplified interface to complex subsystems, making them easier to use.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pheno.application.ports.repositories import (
        ConfigurationRepository,
        DeploymentRepository,
        ServiceRepository,
        UserRepository,
    )
    from pheno.patterns.creational.use_case_factory import UseCaseFactory


class RepositoryFacade:
    """Facade for all repositories.

    Provides a single interface to access all repositories,
    simplifying dependency management.

    Example:
        facade = RepositoryFacade(user_repo, deployment_repo, service_repo, config_repo)
        user = await facade.users.find_by_id(user_id)
    """

    def __init__(
        self,
        user_repository: UserRepository,
        deployment_repository: DeploymentRepository,
        service_repository: ServiceRepository,
        configuration_repository: ConfigurationRepository,
    ):
        """Initialize the repository facade.

        Args:
            user_repository: User repository
            deployment_repository: Deployment repository
            service_repository: Service repository
            configuration_repository: Configuration repository
        """
        self.users = user_repository
        self.deployments = deployment_repository
        self.services = service_repository
        self.configurations = configuration_repository


class UseCaseFacade:
    """Facade for all use cases.

    Provides a single interface to access all use cases,
    organized by domain.

    Example:
        facade = UseCaseFacade(use_case_factory)
        user = await facade.users.create(dto)
    """

    def __init__(self, use_case_factory: UseCaseFactory):
        """Initialize the use case facade.

        Args:
            use_case_factory: Factory for creating use cases
        """
        self._factory = use_case_factory

        # User use cases
        self.users = UserUseCases(use_case_factory)

        # Deployment use cases
        self.deployments = DeploymentUseCases(use_case_factory)

        # Service use cases
        self.services = ServiceUseCases(use_case_factory)

        # Configuration use cases
        self.configurations = ConfigurationUseCases(use_case_factory)


class UserUseCases:
    """
    User use cases facade.
    """

    def __init__(self, factory: UseCaseFactory):
        self._factory = factory

    @property
    def create(self):
        return self._factory.create_user_use_case()

    @property
    def update(self):
        return self._factory.update_user_use_case()

    @property
    def get(self):
        return self._factory.get_user_use_case()

    @property
    def list(self):
        return self._factory.list_users_use_case()

    @property
    def deactivate(self):
        return self._factory.deactivate_user_use_case()


class DeploymentUseCases:
    """
    Deployment use cases facade.
    """

    def __init__(self, factory: UseCaseFactory):
        self._factory = factory

    @property
    def create(self):
        return self._factory.create_deployment_use_case()

    @property
    def start(self):
        return self._factory.start_deployment_use_case()

    @property
    def complete(self):
        return self._factory.complete_deployment_use_case()

    @property
    def fail(self):
        return self._factory.fail_deployment_use_case()

    @property
    def rollback(self):
        return self._factory.rollback_deployment_use_case()

    @property
    def get(self):
        return self._factory.get_deployment_use_case()

    @property
    def list(self):
        return self._factory.list_deployments_use_case()

    @property
    def statistics(self):
        return self._factory.get_deployment_statistics_use_case()


class ServiceUseCases:
    """
    Service use cases facade.
    """

    def __init__(self, factory: UseCaseFactory):
        self._factory = factory

    @property
    def create(self):
        return self._factory.create_service_use_case()

    @property
    def start(self):
        return self._factory.start_service_use_case()

    @property
    def stop(self):
        return self._factory.stop_service_use_case()

    @property
    def get(self):
        return self._factory.get_service_use_case()

    @property
    def list(self):
        return self._factory.list_services_use_case()

    @property
    def health(self):
        return self._factory.get_service_health_use_case()


class ConfigurationUseCases:
    """
    Configuration use cases facade.
    """

    def __init__(self, factory: UseCaseFactory):
        self._factory = factory

    @property
    def create(self):
        return self._factory.create_configuration_use_case()

    @property
    def update(self):
        return self._factory.update_configuration_use_case()

    @property
    def get(self):
        return self._factory.get_configuration_use_case()

    @property
    def list(self):
        return self._factory.list_configurations_use_case()
