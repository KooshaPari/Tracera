"""
Unit tests for domain entities.
"""

from datetime import datetime

import pytest

from pheno.domain.entities.configuration import Configuration
from pheno.domain.entities.deployment import Deployment
from pheno.domain.entities.service import Service
from pheno.domain.entities.user import User
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
from pheno.domain.events.user import UserCreated, UserDeactivated, UserUpdated
from pheno.domain.exceptions.deployment import InvalidDeploymentStateError
from pheno.domain.exceptions.infrastructure import InvalidServiceStateError
from pheno.domain.exceptions.user import UserInactiveError
from pheno.domain.value_objects.common import ConfigKey, ConfigValue, Email
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironment,
    DeploymentStrategy,
)
from pheno.domain.value_objects.infrastructure import ServiceName, ServicePort


class TestUser:
    """
    Test User entity.
    """

    def test_create_user(self):
        """
        Test creating a user.
        """
        email = Email("user@example.com")
        user = User.create(email, "John Doe")

        assert user.email == email
        assert user.name == "John Doe"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_create_user_emits_event(self):
        """
        Test that creating a user emits UserCreated event.
        """
        email = Email("user@example.com")
        user = User.create(email, "John Doe")

        assert len(user.domain_events) == 1
        event = user.domain_events[0]
        assert isinstance(event, UserCreated)
        assert event.aggregate_id == user.id
        assert event.email == email.value
        assert event.name == "John Doe"

    def test_update_name(self):
        """
        Test updating user name.
        """
        user = User.create(Email("user@example.com"), "John Doe")
        user.clear_events()

        user.update_name("Jane Doe")

        assert user.name == "Jane Doe"
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], UserUpdated)

    def test_update_email(self):
        """
        Test updating user email.
        """
        user = User.create(Email("user@example.com"), "John Doe")
        user.clear_events()

        new_email = Email("new@example.com")
        user.update_email(new_email)

        assert user.email == new_email
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], UserUpdated)

    def test_deactivate_user(self):
        """
        Test deactivating a user.
        """
        user = User.create(Email("user@example.com"), "John Doe")
        user.clear_events()

        user.deactivate()

        assert user.is_active is False
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], UserDeactivated)

    def test_activate_user(self):
        """
        Test activating a deactivated user.
        """
        user = User.create(Email("user@example.com"), "John Doe")
        user.deactivate()
        user.clear_events()

        user.activate()

        assert user.is_active is True

    def test_cannot_update_inactive_user(self):
        """
        Test that inactive users cannot be updated.
        """
        user = User.create(Email("user@example.com"), "John Doe")
        user.deactivate()

        with pytest.raises(UserInactiveError):
            user.update_name("Jane Doe")


class TestDeployment:
    """
    Test Deployment entity.
    """

    def test_create_deployment(self):
        """
        Test creating a deployment.
        """
        env = DeploymentEnvironment("production")
        strategy = DeploymentStrategy("blue_green")
        deployment = Deployment.create(env, strategy)

        assert deployment.environment == env
        assert deployment.strategy == strategy
        assert deployment.status.value == "pending"
        assert deployment.started_at is None
        assert deployment.completed_at is None

    def test_create_deployment_emits_event(self):
        """
        Test that creating a deployment emits DeploymentCreated event.
        """
        env = DeploymentEnvironment("production")
        strategy = DeploymentStrategy("blue_green")
        deployment = Deployment.create(env, strategy)

        assert len(deployment.domain_events) == 1
        event = deployment.domain_events[0]
        assert isinstance(event, DeploymentCreated)
        assert event.aggregate_id == deployment.id

    def test_start_deployment(self):
        """
        Test starting a deployment.
        """
        deployment = Deployment.create(
            DeploymentEnvironment("production"), DeploymentStrategy("blue_green"),
        )
        deployment.clear_events()

        deployment.start()

        assert deployment.status.value == "in_progress"
        assert deployment.started_at is not None
        assert len(deployment.domain_events) == 1
        assert isinstance(deployment.domain_events[0], DeploymentStarted)

    def test_complete_deployment(self):
        """
        Test completing a deployment.
        """
        deployment = Deployment.create(
            DeploymentEnvironment("production"), DeploymentStrategy("blue_green"),
        )
        deployment.start()
        deployment.clear_events()

        deployment.complete()

        assert deployment.status.value == "completed"
        assert deployment.completed_at is not None
        assert len(deployment.domain_events) == 1
        assert isinstance(deployment.domain_events[0], DeploymentCompleted)

    def test_fail_deployment(self):
        """
        Test failing a deployment.
        """
        deployment = Deployment.create(
            DeploymentEnvironment("production"), DeploymentStrategy("blue_green"),
        )
        deployment.start()
        deployment.clear_events()

        deployment.fail("Test failure")

        assert deployment.status.value == "failed"
        assert len(deployment.domain_events) == 1
        event = deployment.domain_events[0]
        assert isinstance(event, DeploymentFailed)
        assert event.reason == "Test failure"

    def test_rollback_deployment(self):
        """
        Test rolling back a deployment.
        """
        deployment = Deployment.create(
            DeploymentEnvironment("production"), DeploymentStrategy("blue_green"),
        )
        deployment.start()
        deployment.clear_events()

        deployment.rollback("Test rollback")

        assert deployment.status.value == "rolled_back"
        assert len(deployment.domain_events) == 1
        event = deployment.domain_events[0]
        assert isinstance(event, DeploymentRolledBack)
        assert event.reason == "Test rollback"

    def test_cannot_start_completed_deployment(self):
        """
        Test that completed deployments cannot be started.
        """
        deployment = Deployment.create(
            DeploymentEnvironment("production"), DeploymentStrategy("blue_green"),
        )
        deployment.start()
        deployment.complete()

        with pytest.raises(InvalidDeploymentStateError):
            deployment.start()


class TestService:
    """
    Test Service entity.
    """

    def test_create_service(self):
        """
        Test creating a service.
        """
        name = ServiceName("my-service")
        port = ServicePort(8080, "http")
        service = Service.create(name, port)

        assert service.name == name
        assert service.port == port
        assert service.status.value == "stopped"
        assert service.started_at is None
        assert service.stopped_at is None

    def test_create_service_emits_event(self):
        """
        Test that creating a service emits ServiceCreated event.
        """
        name = ServiceName("my-service")
        port = ServicePort(8080, "http")
        service = Service.create(name, port)

        assert len(service.domain_events) == 1
        event = service.domain_events[0]
        assert isinstance(event, ServiceCreated)
        assert event.aggregate_id == service.id

    def test_start_service(self):
        """
        Test starting a service.
        """
        service = Service.create(ServiceName("my-service"), ServicePort(8080, "http"))
        service.clear_events()

        service.start()

        assert service.status.value == "running"
        assert service.started_at is not None
        assert len(service.domain_events) == 1
        assert isinstance(service.domain_events[0], ServiceStarted)

    def test_stop_service(self):
        """
        Test stopping a service.
        """
        service = Service.create(ServiceName("my-service"), ServicePort(8080, "http"))
        service.start()
        service.clear_events()

        service.stop()

        assert service.status.value == "stopped"
        assert service.stopped_at is not None
        assert len(service.domain_events) == 1
        assert isinstance(service.domain_events[0], ServiceStopped)

    def test_fail_service(self):
        """
        Test failing a service.
        """
        service = Service.create(ServiceName("my-service"), ServicePort(8080, "http"))
        service.start()
        service.clear_events()

        service.fail("Test failure")

        assert service.status.value == "failed"
        assert len(service.domain_events) == 1
        event = service.domain_events[0]
        assert isinstance(event, ServiceFailed)
        assert event.reason == "Test failure"

    def test_cannot_stop_stopped_service(self):
        """
        Test that stopped services cannot be stopped again.
        """
        service = Service.create(ServiceName("my-service"), ServicePort(8080, "http"))

        with pytest.raises(InvalidServiceStateError):
            service.stop()


class TestConfiguration:
    """
    Test Configuration entity.
    """

    def test_create_configuration(self):
        """
        Test creating a configuration.
        """
        key = ConfigKey("app.debug")
        value = ConfigValue(True)
        config = Configuration.create(key, value, "Debug mode")

        assert config.key == key
        assert config.value == value
        assert config.description == "Debug mode"

    def test_update_value(self):
        """
        Test updating configuration value.
        """
        config = Configuration.create(ConfigKey("app.debug"), ConfigValue(True), "Debug mode")

        new_value = ConfigValue(False)
        config.update_value(new_value)

        assert config.value == new_value

    def test_update_description(self):
        """
        Test updating configuration description.
        """
        config = Configuration.create(ConfigKey("app.debug"), ConfigValue(True), "Debug mode")

        config.update_description("New description")

        assert config.description == "New description"
