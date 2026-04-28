"""
Unit tests for common value objects.
"""

from uuid import uuid4

import pytest

from pheno.domain.exceptions import ValidationError
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


class TestEmail:
    """
    Tests for Email value object.
    """

    def test_valid_email(self):
        """
        Test creating a valid email.
        """
        email = Email("user@example.com")
        assert email.value == "user@example.com"
        assert str(email) == "user@example.com"

    def test_email_domain(self):
        """
        Test getting email domain.
        """
        email = Email("user@example.com")
        assert email.domain == "example.com"

    def test_email_local_part(self):
        """
        Test getting email local part.
        """
        email = Email("user@example.com")
        assert email.local_part == "user"

    def test_empty_email_raises_error(self):
        """
        Test that empty email raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Email cannot be empty"):
            Email("")

    def test_invalid_email_format_raises_error(self):
        """
        Test that invalid email format raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Invalid email format"):
            Email("not-an-email")

    def test_email_without_domain_raises_error(self):
        """
        Test that email without domain raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Invalid email format"):
            Email("user@")

    def test_email_immutability(self):
        """
        Test that email is immutable.
        """
        email = Email("user@example.com")
        with pytest.raises(AttributeError):
            email.value = "new@example.com"  # type: ignore

    def test_email_equality(self):
        """
        Test email equality based on value.
        """
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3

    def test_email_hashable(self):
        """
        Test that email is hashable.
        """
        email1 = Email("user@example.com")
        email2 = Email("user@example.com")

        email_set = {email1, email2}
        assert len(email_set) == 1


class TestPort:
    """
    Tests for Port value object.
    """

    def test_valid_port(self):
        """
        Test creating a valid port.
        """
        port = Port(8080)
        assert port.value == 8080
        assert str(port) == "8080"
        assert int(port) == 8080

    def test_port_range_validation(self):
        """
        Test port range validation.
        """
        Port(1)  # Minimum valid port
        Port(65535)  # Maximum valid port

        with pytest.raises(ValidationError, match="Port must be between"):
            Port(0)

        with pytest.raises(ValidationError, match="Port must be between"):
            Port(65536)

    def test_port_type_validation(self):
        """
        Test port type validation.
        """
        with pytest.raises(ValidationError, match="Port must be an integer"):
            Port("8080")  # type: ignore

    def test_is_privileged(self):
        """
        Test privileged port detection.
        """
        assert Port(80).is_privileged()
        assert Port(443).is_privileged()
        assert not Port(8080).is_privileged()

    def test_is_ephemeral(self):
        """
        Test ephemeral port detection.
        """
        assert Port(49152).is_ephemeral()
        assert Port(65535).is_ephemeral()
        assert not Port(8080).is_ephemeral()

    def test_port_immutability(self):
        """
        Test that port is immutable.
        """
        port = Port(8080)
        with pytest.raises(AttributeError):
            port.value = 9090  # type: ignore


class TestURL:
    """
    Tests for URL value object.
    """

    def test_valid_url(self):
        """
        Test creating a valid URL.
        """
        url = URL("https://example.com/path")
        assert url.value == "https://example.com/path"
        assert str(url) == "https://example.com/path"

    def test_url_components(self):
        """
        Test URL component extraction.
        """
        url = URL("https://example.com:8080/path?query=value")
        assert url.scheme == "https"
        assert url.host == "example.com:8080"
        assert url.path == "/path"

    def test_is_secure(self):
        """
        Test secure URL detection.
        """
        assert URL("https://example.com").is_secure()
        assert URL("wss://example.com").is_secure()
        assert not URL("http://example.com").is_secure()
        assert not URL("ws://example.com").is_secure()

    def test_empty_url_raises_error(self):
        """
        Test that empty URL raises ValidationError.
        """
        with pytest.raises(ValidationError, match="URL cannot be empty"):
            URL("")

    def test_invalid_url_format_raises_error(self):
        """
        Test that invalid URL format raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Invalid URL format"):
            URL("not-a-url")

        with pytest.raises(ValidationError, match="Invalid URL format"):
            URL("://example.com")


class TestConfigKey:
    """
    Tests for ConfigKey value object.
    """

    def test_valid_config_key(self):
        """
        Test creating a valid config key.
        """
        key = ConfigKey("database.url")
        assert key.value == "database.url"
        assert str(key) == "database.url"

    def test_config_key_parts(self):
        """
        Test config key parts extraction.
        """
        key = ConfigKey("database.connection.url")
        assert key.parts == ["database", "connection", "url"]

    def test_config_key_namespace(self):
        """
        Test config key namespace extraction.
        """
        key = ConfigKey("database.url")
        assert key.namespace == "database"

        key_no_namespace = ConfigKey("simple")
        assert key_no_namespace.namespace is None

    def test_empty_config_key_raises_error(self):
        """
        Test that empty config key raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Config key cannot be empty"):
            ConfigKey("")

    def test_invalid_config_key_format_raises_error(self):
        """
        Test that invalid config key format raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Invalid config key format"):
            ConfigKey("invalid key!")

        with pytest.raises(ValidationError, match="Invalid config key format"):
            ConfigKey("invalid@key")


class TestConfigValue:
    """
    Tests for ConfigValue value object.
    """

    def test_config_value_as_string(self):
        """
        Test config value as string.
        """
        value = ConfigValue("test")
        assert value.as_string() == "test"
        assert str(value) == "test"

    def test_config_value_as_int(self):
        """
        Test config value as integer.
        """
        value = ConfigValue("42")
        assert value.as_int() == 42

        value_int = ConfigValue(42)
        assert value_int.as_int() == 42

    def test_config_value_as_int_invalid(self):
        """
        Test config value as integer with invalid value.
        """
        value = ConfigValue("not-a-number")
        with pytest.raises(ValidationError, match="Cannot convert"):
            value.as_int()

    def test_config_value_as_bool(self):
        """
        Test config value as boolean.
        """
        assert ConfigValue(True).as_bool() is True
        assert ConfigValue(False).as_bool() is False
        assert ConfigValue("true").as_bool() is True
        assert ConfigValue("1").as_bool() is True
        assert ConfigValue("yes").as_bool() is True
        assert ConfigValue("on").as_bool() is True
        assert ConfigValue("false").as_bool() is False
        assert ConfigValue("0").as_bool() is False


class TestUserId:
    """
    Tests for UserId value object.
    """

    def test_valid_user_id(self):
        """
        Test creating a valid user ID.
        """
        user_id = UserId(str(uuid4()))
        assert user_id.value
        assert str(user_id) == user_id.value

    def test_generate_user_id(self):
        """
        Test generating a new user ID.
        """
        user_id = UserId.generate()
        assert user_id.value
        # Verify it's a valid UUID
        assert len(user_id.value) == 36

    def test_empty_user_id_raises_error(self):
        """
        Test that empty user ID raises ValidationError.
        """
        with pytest.raises(ValidationError, match="User ID cannot be empty"):
            UserId("")

    def test_invalid_user_id_format_raises_error(self):
        """
        Test that invalid user ID format raises ValidationError.
        """
        with pytest.raises(ValidationError, match="Invalid user ID format"):
            UserId("not-a-uuid")


class TestServiceId:
    """
    Tests for ServiceId value object.
    """

    def test_valid_service_id(self):
        """
        Test creating a valid service ID.
        """
        service_id = ServiceId(str(uuid4()))
        assert service_id.value
        assert str(service_id) == service_id.value

    def test_generate_service_id(self):
        """
        Test generating a new service ID.
        """
        service_id = ServiceId.generate()
        assert service_id.value


class TestDeploymentId:
    """
    Tests for DeploymentId value object.
    """

    def test_valid_deployment_id(self):
        """
        Test creating a valid deployment ID.
        """
        deployment_id = DeploymentId(str(uuid4()))
        assert deployment_id.value
        assert str(deployment_id) == deployment_id.value

    def test_generate_deployment_id(self):
        """
        Test generating a new deployment ID.
        """
        deployment_id = DeploymentId.generate()
        assert deployment_id.value
