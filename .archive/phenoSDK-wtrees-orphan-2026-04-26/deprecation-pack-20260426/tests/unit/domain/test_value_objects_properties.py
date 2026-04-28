"""
Property-based tests for domain value objects using Hypothesis.
"""

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from pheno.domain.exceptions.base import ValidationError
from pheno.domain.value_objects.common import Email, Port
from tests.utils.factories import (
    config_key_strategy,
    config_value_strategy,
    deployment_environment_strategy,
    deployment_strategy_strategy,
    email_strategy,
    port_strategy,
    service_name_strategy,
    service_port_strategy,
)


@pytest.mark.unit
@pytest.mark.domain
class TestEmailProperties:
    """
    Property-based tests for Email value object.
    """

    @given(email_strategy())
    def test_email_roundtrip(self, email):
        """
        Test that email value can be retrieved.
        """
        assert isinstance(email.value, str)
        assert "@" in email.value

    @given(email_strategy())
    def test_email_has_parts(self, email):
        """
        Test that email has local part and domain.
        """
        assert email.local_part is not None
        assert email.domain is not None
        assert len(email.local_part) > 0
        assert len(email.domain) > 0

    @given(email_strategy(), email_strategy())
    def test_email_equality_reflexive(self, email1, email2):
        """
        Test email equality is reflexive.
        """
        assert email1 == email1
        if email1.value == email2.value:
            assert email1 == email2

    @given(st.text())
    def test_invalid_email_raises_error(self, text):
        """
        Test that invalid emails raise ValidationError.
        """
        assume("@" not in text or "." not in text.split("@")[-1])
        with pytest.raises(ValidationError):
            Email(text)


@pytest.mark.unit
@pytest.mark.domain
class TestPortProperties:
    """
    Property-based tests for Port value object.
    """

    @given(port_strategy())
    def test_port_in_valid_range(self, port):
        """
        Test that port is in valid range.
        """
        assert 1 <= port.value <= 65535

    @given(port_strategy())
    def test_port_privileged_or_not(self, port):
        """
        Test port privileged status is consistent.
        """
        if port.value < 1024:
            assert port.is_privileged is True
        else:
            assert port.is_privileged is False

    @given(port_strategy())
    def test_port_ephemeral_or_not(self, port):
        """
        Test port ephemeral status is consistent.
        """
        if port.value >= 49152:
            assert port.is_ephemeral is True
        else:
            assert port.is_ephemeral is False

    @given(st.integers())
    def test_invalid_port_raises_error(self, value):
        """
        Test that invalid ports raise ValidationError.
        """
        assume(value < 1 or value > 65535)
        with pytest.raises(ValidationError):
            Port(value)


@pytest.mark.unit
@pytest.mark.domain
class TestConfigKeyProperties:
    """
    Property-based tests for ConfigKey value object.
    """

    @given(config_key_strategy())
    def test_config_key_roundtrip(self, key):
        """
        Test that config key value can be retrieved.
        """
        assert isinstance(key.value, str)
        assert len(key.value) > 0

    @given(config_key_strategy())
    def test_config_key_parts(self, key):
        """
        Test that config key has valid parts.
        """
        if "." in key.value:
            assert key.namespace is not None
            assert key.name is not None
            assert f"{key.namespace}.{key.name}" == key.value
        else:
            assert key.namespace is None
            assert key.name == key.value


@pytest.mark.unit
@pytest.mark.domain
class TestConfigValueProperties:
    """
    Property-based tests for ConfigValue value object.
    """

    @given(config_value_strategy())
    def test_config_value_has_type(self, value):
        """
        Test that config value has a type.
        """
        assert value.value_type in ["string", "int", "bool", "float"]

    @given(config_value_strategy())
    def test_config_value_type_matches(self, value):
        """
        Test that config value type matches actual type.
        """
        if value.value_type == "string":
            assert isinstance(value.value, str)
        elif value.value_type == "int":
            assert isinstance(value.value, int)
        elif value.value_type == "bool":
            assert isinstance(value.value, bool)
        elif value.value_type == "float":
            assert isinstance(value.value, float)


@pytest.mark.unit
@pytest.mark.domain
class TestDeploymentValueObjectProperties:
    """
    Property-based tests for deployment value objects.
    """

    @given(deployment_environment_strategy())
    def test_deployment_environment_valid(self, env):
        """
        Test that deployment environment is valid.
        """
        assert env.value in [
            "development",
            "staging",
            "production",
            "testing",
        ]

    @given(deployment_strategy_strategy())
    def test_deployment_strategy_valid(self, strategy):
        """
        Test that deployment strategy is valid.
        """
        assert strategy.value in [
            "blue_green",
            "rolling",
            "canary",
            "recreate",
        ]


@pytest.mark.unit
@pytest.mark.domain
class TestServiceValueObjectProperties:
    """
    Property-based tests for service value objects.
    """

    @given(service_name_strategy())
    def test_service_name_valid_format(self, name):
        """
        Test that service name has valid format.
        """
        assert name.value.islower()
        assert not name.value.startswith("-")
        assert not name.value.endswith("-")
        assert "--" not in name.value

    @given(service_port_strategy())
    def test_service_port_valid(self, port):
        """
        Test that service port is valid.
        """
        assert 1 <= port.port <= 65535
        assert port.protocol in ["http", "https", "tcp", "udp", "grpc"]

    @given(service_port_strategy())
    def test_service_port_string_representation(self, port):
        """
        Test service port string representation.
        """
        port_str = str(port)
        assert str(port.port) in port_str
        assert port.protocol in port_str
