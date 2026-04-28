"""
Unit tests for Deployment entity.
"""


import pytest

from pheno.domain.entities import Deployment
from pheno.domain.events import (
    DeploymentCompleted,
    DeploymentCreated,
    DeploymentFailed,
    DeploymentRolledBack,
    DeploymentStarted,
)
from pheno.domain.exceptions import (
    InvalidDeploymentStateError,
    ValidationError,
)
from pheno.domain.value_objects import (
    DeploymentEnvironment,
    DeploymentStrategy,
)
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironmentEnum,
    DeploymentStatusEnum,
    DeploymentStrategyEnum,
)


class TestDeploymentCreation:
    """
    Tests for Deployment creation.
    """

    def test_create_deployment(self):
        """
        Test creating a new deployment.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.BLUE_GREEN)

        deployment, event = Deployment.create(
            environment=environment,
            strategy=strategy,
        )

        assert deployment.environment == environment
        assert deployment.strategy == strategy
        assert deployment.status.value == DeploymentStatusEnum.PENDING
        assert deployment.started_at is None
        assert deployment.completed_at is None

    def test_create_deployment_emits_event(self):
        """
        Test that deployment creation emits DeploymentCreated event.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.STAGING)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.CANARY)

        deployment, event = Deployment.create(
            environment=environment,
            strategy=strategy,
        )

        assert isinstance(event, DeploymentCreated)
        assert event.deployment_id == str(deployment.id)
        assert event.environment == str(environment)
        assert event.strategy == str(strategy)


class TestDeploymentStart:
    """
    Tests for starting deployment.
    """

    def test_start_deployment(self):
        """
        Test starting a deployment.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)

        started_deployment = deployment.start()

        assert started_deployment.status.value == DeploymentStatusEnum.IN_PROGRESS
        assert started_deployment.started_at is not None

    def test_start_deployment_emits_event(self):
        """
        Test that starting deployment emits DeploymentStarted event.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.BLUE_GREEN)
        deployment, _ = Deployment.create(environment, strategy)

        started_deployment = deployment.start()
        events = started_deployment.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, DeploymentStarted)
        assert event.deployment_id == str(deployment.id)

    def test_start_already_started_deployment_raises_error(self):
        """
        Test that starting already started deployment raises error.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()

        with pytest.raises(InvalidDeploymentStateError):
            started_deployment.start()


class TestDeploymentComplete:
    """
    Tests for completing deployment.
    """

    def test_complete_deployment(self):
        """
        Test completing a deployment.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.BLUE_GREEN)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()

        completed_deployment = started_deployment.complete()

        assert completed_deployment.status.value == DeploymentStatusEnum.COMPLETED
        assert completed_deployment.completed_at is not None

    def test_complete_deployment_emits_event(self):
        """
        Test that completing deployment emits DeploymentCompleted event.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.CANARY)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()

        completed_deployment = started_deployment.complete()
        events = completed_deployment.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, DeploymentCompleted)
        assert event.deployment_id == str(deployment.id)
        assert event.duration_seconds >= 0

    def test_complete_not_started_deployment_raises_error(self):
        """
        Test that completing not started deployment raises error.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)

        with pytest.raises(ValidationError, match="never started"):
            deployment.complete()

    def test_complete_already_completed_deployment_raises_error(self):
        """
        Test that completing already completed deployment raises error.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.BLUE_GREEN)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()
        completed_deployment = started_deployment.complete()

        with pytest.raises(InvalidDeploymentStateError):
            completed_deployment.complete()


class TestDeploymentFail:
    """
    Tests for failing deployment.
    """

    def test_fail_deployment(self):
        """
        Test failing a deployment.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()

        failed_deployment = started_deployment.fail("Connection timeout")

        assert failed_deployment.status.value == DeploymentStatusEnum.FAILED
        assert failed_deployment.error_message == "Connection timeout"
        assert failed_deployment.completed_at is not None

    def test_fail_deployment_emits_event(self):
        """
        Test that failing deployment emits DeploymentFailed event.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.CANARY)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()

        failed_deployment = started_deployment.fail("Database error")
        events = failed_deployment.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, DeploymentFailed)
        assert event.deployment_id == str(deployment.id)
        assert event.error_message == "Database error"
        assert event.duration_seconds >= 0

    def test_fail_deployment_with_empty_message_raises_error(self):
        """
        Test that failing with empty message raises error.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()

        with pytest.raises(ValidationError, match="Error message cannot be empty"):
            started_deployment.fail("")

    def test_fail_not_started_deployment_raises_error(self):
        """
        Test that failing not started deployment raises error.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)

        with pytest.raises(ValidationError, match="never started"):
            deployment.fail("Some error")


class TestDeploymentRollback:
    """
    Tests for rolling back deployment.
    """

    def test_rollback_deployment(self):
        """
        Test rolling back a deployment.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.BLUE_GREEN)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()
        failed_deployment = started_deployment.fail("Error occurred")

        rolled_back_deployment = failed_deployment.rollback("Critical bug found")

        assert rolled_back_deployment.status.value == DeploymentStatusEnum.ROLLED_BACK
        assert rolled_back_deployment.completed_at is not None

    def test_rollback_deployment_emits_event(self):
        """
        Test that rolling back deployment emits DeploymentRolledBack event.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.CANARY)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()
        failed_deployment = started_deployment.fail("Error")

        rolled_back_deployment = failed_deployment.rollback("Rollback reason")
        events = rolled_back_deployment.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, DeploymentRolledBack)
        assert event.deployment_id == str(deployment.id)
        assert event.reason == "Rollback reason"

    def test_rollback_with_unsupported_strategy_raises_error(self):
        """
        Test that rollback with unsupported strategy raises error.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.RECREATE)
        deployment, _ = Deployment.create(environment, strategy)
        started_deployment = deployment.start()
        failed_deployment = started_deployment.fail("Error")

        with pytest.raises(ValidationError, match="does not support rollback"):
            failed_deployment.rollback()


class TestDeploymentState:
    """
    Tests for deployment state queries.
    """

    def test_is_terminal(self):
        """
        Test is_terminal method.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)

        assert not deployment.is_terminal()

        started = deployment.start()
        assert not started.is_terminal()

        completed = started.complete()
        assert completed.is_terminal()

    def test_is_active(self):
        """
        Test is_active method.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)

        assert not deployment.is_active()

        started = deployment.start()
        assert started.is_active()

        completed = started.complete()
        assert not completed.is_active()

    def test_duration_seconds(self):
        """
        Test duration_seconds method.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.ROLLING)
        deployment, _ = Deployment.create(environment, strategy)

        assert deployment.duration_seconds() is None

        started = deployment.start()
        duration = started.duration_seconds()
        assert duration is not None
        assert duration >= 0


class TestDeploymentStringRepresentation:
    """
    Tests for deployment string representation.
    """

    def test_deployment_str(self):
        """
        Test deployment string representation.
        """
        environment = DeploymentEnvironment(DeploymentEnvironmentEnum.PRODUCTION)
        strategy = DeploymentStrategy(DeploymentStrategyEnum.BLUE_GREEN)
        deployment, _ = Deployment.create(environment, strategy)

        deployment_str = str(deployment)

        assert "Deployment" in deployment_str
        assert str(deployment.id) in deployment_str
        assert str(environment) in deployment_str
