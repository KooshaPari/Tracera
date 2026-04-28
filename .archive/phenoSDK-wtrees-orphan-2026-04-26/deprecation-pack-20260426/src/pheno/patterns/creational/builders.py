"""Builder Pattern implementations for creating complex domain objects.

Builders provide a fluent interface for constructing objects step by step, especially
useful for objects with many optional parameters.
"""

from __future__ import annotations

from typing import Any

from pheno.domain.entities.configuration import Configuration
from pheno.domain.entities.deployment import Deployment
from pheno.domain.entities.service import Service
from pheno.domain.entities.user import User
from pheno.domain.value_objects.common import ConfigKey, ConfigValue, Email
from pheno.domain.value_objects.deployment import (
    DeploymentEnvironment,
    DeploymentStrategy,
)
from pheno.domain.value_objects.infrastructure import ServiceName, ServicePort


class UserBuilder:
    """Builder for creating User entities with a fluent interface.

    Example:
        user = (UserBuilder()
                .with_email("user@example.com")
                .with_name("John Doe")
                .build())
    """

    def __init__(self):
        self._email: str | None = None
        self._name: str | None = None

    def with_email(self, email: str) -> UserBuilder:
        """
        Set the user email.
        """
        self._email = email
        return self

    def with_name(self, name: str) -> UserBuilder:
        """
        Set the user name.
        """
        self._name = name
        return self

    def build(self) -> User:
        """Build the user entity.

        Returns:
            Created user entity

        Raises:
            ValueError: If required fields are missing
        """
        if not self._email:
            raise ValueError("Email is required")
        if not self._name:
            raise ValueError("Name is required")

        email_vo = Email(self._email)
        return User.create(email_vo, self._name)

    def reset(self) -> UserBuilder:
        """
        Reset the builder to initial state.
        """
        self._email = None
        self._name = None
        return self


class DeploymentBuilder:
    """Builder for creating Deployment entities with a fluent interface.

    Example:
        deployment = (DeploymentBuilder()
                      .with_environment("production")
                      .with_strategy("blue_green")
                      .build())
    """

    def __init__(self):
        self._environment: str | None = None
        self._strategy: str | None = None

    def with_environment(self, environment: str) -> DeploymentBuilder:
        """
        Set the deployment environment.
        """
        self._environment = environment
        return self

    def with_strategy(self, strategy: str) -> DeploymentBuilder:
        """
        Set the deployment strategy.
        """
        self._strategy = strategy
        return self

    def for_production(self) -> DeploymentBuilder:
        """
        Configure for production environment.
        """
        self._environment = "production"
        return self

    def for_staging(self) -> DeploymentBuilder:
        """
        Configure for staging environment.
        """
        self._environment = "staging"
        return self

    def for_development(self) -> DeploymentBuilder:
        """
        Configure for development environment.
        """
        self._environment = "development"
        return self

    def with_blue_green_strategy(self) -> DeploymentBuilder:
        """
        Use blue-green deployment strategy.
        """
        self._strategy = "blue_green"
        return self

    def with_rolling_strategy(self) -> DeploymentBuilder:
        """
        Use rolling deployment strategy.
        """
        self._strategy = "rolling"
        return self

    def with_canary_strategy(self) -> DeploymentBuilder:
        """
        Use canary deployment strategy.
        """
        self._strategy = "canary"
        return self

    def build(self) -> Deployment:
        """Build the deployment entity.

        Returns:
            Created deployment entity

        Raises:
            ValueError: If required fields are missing
        """
        if not self._environment:
            raise ValueError("Environment is required")
        if not self._strategy:
            raise ValueError("Strategy is required")

        env_vo = DeploymentEnvironment(self._environment)
        strategy_vo = DeploymentStrategy(self._strategy)
        return Deployment.create(env_vo, strategy_vo)

    def reset(self) -> DeploymentBuilder:
        """
        Reset the builder to initial state.
        """
        self._environment = None
        self._strategy = None
        return self


class ServiceBuilder:
    """Builder for creating Service entities with a fluent interface.

    Example:
        service = (ServiceBuilder()
                   .with_name("api-server")
                   .with_port(8080)
                   .with_http_protocol()
                   .build())
    """

    def __init__(self):
        self._name: str | None = None
        self._port: int | None = None
        self._protocol: str = "http"

    def with_name(self, name: str) -> ServiceBuilder:
        """
        Set the service name.
        """
        self._name = name
        return self

    def with_port(self, port: int) -> ServiceBuilder:
        """
        Set the service port.
        """
        self._port = port
        return self

    def with_protocol(self, protocol: str) -> ServiceBuilder:
        """
        Set the service protocol.
        """
        self._protocol = protocol
        return self

    def with_http_protocol(self) -> ServiceBuilder:
        """
        Use HTTP protocol.
        """
        self._protocol = "http"
        return self

    def with_https_protocol(self) -> ServiceBuilder:
        """
        Use HTTPS protocol.
        """
        self._protocol = "https"
        return self

    def with_grpc_protocol(self) -> ServiceBuilder:
        """
        Use gRPC protocol.
        """
        self._protocol = "grpc"
        return self

    def with_tcp_protocol(self) -> ServiceBuilder:
        """
        Use TCP protocol.
        """
        self._protocol = "tcp"
        return self

    def as_http_service(self, name: str, port: int = 8080) -> ServiceBuilder:
        """
        Configure as HTTP service with defaults.
        """
        self._name = name
        self._port = port
        self._protocol = "http"
        return self

    def as_grpc_service(self, name: str, port: int = 50051) -> ServiceBuilder:
        """
        Configure as gRPC service with defaults.
        """
        self._name = name
        self._port = port
        self._protocol = "grpc"
        return self

    def build(self) -> Service:
        """Build the service entity.

        Returns:
            Created service entity

        Raises:
            ValueError: If required fields are missing
        """
        if not self._name:
            raise ValueError("Name is required")
        if not self._port:
            raise ValueError("Port is required")

        name_vo = ServiceName(self._name)
        port_vo = ServicePort(self._port, self._protocol)
        return Service.create(name_vo, port_vo)

    def reset(self) -> ServiceBuilder:
        """
        Reset the builder to initial state.
        """
        self._name = None
        self._port = None
        self._protocol = "http"
        return self


class ConfigurationBuilder:
    """Builder for creating Configuration entities with a fluent interface.

    Example:
        config = (ConfigurationBuilder()
                  .with_key("app.debug")
                  .with_value(True)
                  .with_description("Debug mode")
                  .build())
    """

    def __init__(self):
        self._key: str | None = None
        self._value: Any = None
        self._description: str | None = None

    def with_key(self, key: str) -> ConfigurationBuilder:
        """
        Set the configuration key.
        """
        self._key = key
        return self

    def with_value(self, value: Any) -> ConfigurationBuilder:
        """
        Set the configuration value.
        """
        self._value = value
        return self

    def with_description(self, description: str) -> ConfigurationBuilder:
        """
        Set the configuration description.
        """
        self._description = description
        return self

    def with_string_value(self, value: str) -> ConfigurationBuilder:
        """
        Set a string value.
        """
        self._value = value
        return self

    def with_int_value(self, value: int) -> ConfigurationBuilder:
        """
        Set an integer value.
        """
        self._value = value
        return self

    def with_bool_value(self, value: bool) -> ConfigurationBuilder:
        """
        Set a boolean value.
        """
        self._value = value
        return self

    def with_float_value(self, value: float) -> ConfigurationBuilder:
        """
        Set a float value.
        """
        self._value = value
        return self

    def build(self) -> Configuration:
        """Build the configuration entity.

        Returns:
            Created configuration entity

        Raises:
            ValueError: If required fields are missing
        """
        if not self._key:
            raise ValueError("Key is required")
        if self._value is None:
            raise ValueError("Value is required")

        key_vo = ConfigKey(self._key)
        value_vo = ConfigValue(self._value)
        return Configuration.create(key_vo, value_vo, self._description)

    def reset(self) -> ConfigurationBuilder:
        """
        Reset the builder to initial state.
        """
        self._key = None
        self._value = None
        self._description = None
        return self
