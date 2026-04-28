"""
Unit tests for domain value objects.
"""

from uuid import UUID

import pytest

from pheno.domain.exceptions.base import ValidationError
from pheno.domain.value_objects.common import (
    URL,
    ConfigKey,
    ConfigValue,
    Email,
    Port,
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


class TestEmail:
    """
    Test Email value object.
    """

    def test_create_valid_email(self):
        """
        Test creating a valid email.
        """
        email = Email("user@example.com")
        assert email.value == "user@example.com"
        assert email.local_part == "user"
        assert email.domain == "example.com"

    def test_create_invalid_email(self):
        """
        Test creating an invalid email raises ValidationError.
        """
        with pytest.raises(ValidationError):
            Email("invalid-email")

    def test_email_equality(self):
        """
        Test email equality.
        """
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3

    def test_email_immutability(self):
        """
        Test that email is immutable.
        """
        email = Email("user@example.com")
        with pytest.raises(AttributeError):
            email.value = "new@example.com"


class TestPort:
    """
    Test Port value object.
    """

    def test_create_valid_port(self):
        """
        Test creating a valid port.
        """
        port = Port(8080)
        assert port.value == 8080

    def test_create_invalid_port_too_low(self):
        """
        Test creating a port below valid range.
        """
        with pytest.raises(ValidationError):
            Port(0)

    def test_create_invalid_port_too_high(self):
        """
        Test creating a port above valid range.
        """
        with pytest.raises(ValidationError):
            Port(65536)

    def test_is_privileged(self):
        """
        Test privileged port detection.
        """
        assert Port(80).is_privileged is True
        assert Port(443).is_privileged is True
        assert Port(1024).is_privileged is False
        assert Port(8080).is_privileged is False

    def test_is_ephemeral(self):
        """
        Test ephemeral port detection.
        """
        assert Port(49152).is_ephemeral is True
        assert Port(65535).is_ephemeral is True
        assert Port(49151).is_ephemeral is False
        assert Port(8080).is_ephemeral is False


class TestURL:
    """
    Test URL value object.
    """

    def test_create_valid_url(self):
        """
        Test creating a valid URL.
        """
        url = URL("https://example.com/path")
        assert url.value == "https://example.com/path"
        assert url.scheme == "https"
        assert url.host == "example.com"
        assert url.path == "/path"

    def test_create_invalid_url(self):
        """
        Test creating an invalid URL.
        """
        with pytest.raises(ValidationError):
            URL("not-a-url")


class TestConfigKey:
    """
    Test ConfigKey value object.
    """

    def test_create_valid_config_key(self):
        """
        Test creating a valid config key.
        """
        key = ConfigKey("app.database.host")
        assert key.value == "app.database.host"
        assert key.namespace == "app.database"
        assert key.name == "host"

    def test_create_simple_config_key(self):
        """
        Test creating a simple config key without namespace.
        """
        key = ConfigKey("debug")
        assert key.value == "debug"
        assert key.namespace is None
        assert key.name == "debug"


class TestConfigValue:
    """
    Test ConfigValue value object.
    """

    def test_create_string_value(self):
        """
        Test creating a string config value.
        """
        value = ConfigValue("test")
        assert value.value == "test"
        assert value.value_type == "string"

    def test_create_int_value(self):
        """
        Test creating an int config value.
        """
        value = ConfigValue(42)
        assert value.value == 42
        assert value.value_type == "int"

    def test_create_bool_value(self):
        """
        Test creating a bool config value.
        """
        value = ConfigValue(True)
        assert value.value is True
        assert value.value_type == "bool"


class TestUserId:
    """
    Test UserId value object.
    """

    def test_create_user_id(self):
        """
        Test creating a user ID.
        """
        user_id = UserId()
        assert isinstance(user_id.value, UUID)

    def test_create_user_id_from_string(self):
        """
        Test creating a user ID from string.
        """
        uuid_str = "12345678-1234-5678-1234-567812345678"
        user_id = UserId(uuid_str)
        assert str(user_id.value) == uuid_str


class TestDeploymentStatus:
    """
    Test DeploymentStatus value object.
    """

    def test_create_valid_status(self):
        """
        Test creating a valid deployment status.
        """
        status = DeploymentStatus("pending")
        assert status.value == "pending"

    def test_create_invalid_status(self):
        """
        Test creating an invalid deployment status.
        """
        with pytest.raises(ValidationError):
            DeploymentStatus("invalid")

    def test_can_transition_to(self):
        """
        Test status transition validation.
        """
        pending = DeploymentStatus("pending")
        assert pending.can_transition_to("in_progress") is True
        assert pending.can_transition_to("completed") is False


class TestDeploymentEnvironment:
    """
    Test DeploymentEnvironment value object.
    """

    def test_create_valid_environment(self):
        """
        Test creating a valid environment.
        """
        env = DeploymentEnvironment("production")
        assert env.value == "production"

    def test_create_invalid_environment(self):
        """
        Test creating an invalid environment.
        """
        with pytest.raises(ValidationError):
            DeploymentEnvironment("invalid")


class TestDeploymentStrategy:
    """
    Test DeploymentStrategy value object.
    """

    def test_create_valid_strategy(self):
        """
        Test creating a valid strategy.
        """
        strategy = DeploymentStrategy("blue_green")
        assert strategy.value == "blue_green"

    def test_create_invalid_strategy(self):
        """
        Test creating an invalid strategy.
        """
        with pytest.raises(ValidationError):
            DeploymentStrategy("invalid")


class TestServiceStatus:
    """
    Test ServiceStatus value object.
    """

    def test_create_valid_status(self):
        """
        Test creating a valid service status.
        """
        status = ServiceStatus("running")
        assert status.value == "running"

    def test_create_invalid_status(self):
        """
        Test creating an invalid service status.
        """
        with pytest.raises(ValidationError):
            ServiceStatus("invalid")

    def test_can_transition_to(self):
        """
        Test status transition validation.
        """
        stopped = ServiceStatus("stopped")
        assert stopped.can_transition_to("running") is True
        assert stopped.can_transition_to("failed") is False


class TestServicePort:
    """
    Test ServicePort value object.
    """

    def test_create_valid_service_port(self):
        """
        Test creating a valid service port.
        """
        port = ServicePort(8080, "http")
        assert port.port == 8080
        assert port.protocol == "http"

    def test_create_invalid_port(self):
        """
        Test creating an invalid port.
        """
        with pytest.raises(ValidationError):
            ServicePort(0, "http")

    def test_create_invalid_protocol(self):
        """
        Test creating an invalid protocol.
        """
        with pytest.raises(ValidationError):
            ServicePort(8080, "invalid")


class TestServiceName:
    """
    Test ServiceName value object.
    """

    def test_create_valid_service_name(self):
        """
        Test creating a valid service name.
        """
        name = ServiceName("my-service")
        assert name.value == "my-service"

    def test_create_invalid_service_name_uppercase(self):
        """
        Test creating a service name with uppercase.
        """
        with pytest.raises(ValidationError):
            ServiceName("MyService")

    def test_create_invalid_service_name_special_chars(self):
        """
        Test creating a service name with special characters.
        """
        with pytest.raises(ValidationError):
            ServiceName("my_service!")

    def test_create_invalid_service_name_too_long(self):
        """
        Test creating a service name that's too long.
        """
        with pytest.raises(ValidationError):
            ServiceName("a" * 64)
