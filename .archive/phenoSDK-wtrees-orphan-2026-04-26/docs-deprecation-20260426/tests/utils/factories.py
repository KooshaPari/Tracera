"""Test data factories using Hypothesis for property-based testing.

This module provides factories for generating test data with various properties and
constraints.
"""

import string

from hypothesis import strategies as st
from hypothesis.strategies import composite

from pheno.domain.value_objects.common import ConfigKey, ConfigValue, Email, Port
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

# ========== Basic Strategies ==========


@composite
def email_strategy(draw):
    """
    Generate valid email addresses.
    """
    local_part = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "._-", min_size=1, max_size=64,
        ).filter(lambda x: x[0] not in ".-" and x[-1] not in ".-"),
    )

    domain = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "-", min_size=1, max_size=63,
        ).filter(lambda x: x[0] != "-" and x[-1] != "-"),
    )

    tld = draw(st.sampled_from(["com", "org", "net", "edu", "io"]))

    return Email(f"{local_part}@{domain}.{tld}")


@composite
def port_strategy(draw):
    """
    Generate valid port numbers.
    """
    port_num = draw(st.integers(min_value=1, max_value=65535))
    return Port(port_num)


@composite
def config_key_strategy(draw):
    """
    Generate valid configuration keys.
    """
    parts = draw(
        st.lists(
            st.text(alphabet=string.ascii_lowercase + string.digits + "_", min_size=1, max_size=20),
            min_size=1,
            max_size=5,
        ),
    )
    return ConfigKey(".".join(parts))


@composite
def config_value_strategy(draw):
    """
    Generate valid configuration values.
    """
    value_type = draw(st.sampled_from(["string", "int", "bool", "float"]))

    if value_type == "string":
        value = draw(st.text(min_size=0, max_size=100))
    elif value_type == "int":
        value = draw(st.integers())
    elif value_type == "bool":
        value = draw(st.booleans())
    else:  # float
        value = draw(st.floats(allow_nan=False, allow_infinity=False))

    return ConfigValue(value)


# ========== Deployment Strategies ==========


@composite
def deployment_environment_strategy(draw):
    """
    Generate valid deployment environments.
    """
    env = draw(
        st.sampled_from(
            [
                "development",
                "staging",
                "production",
                "testing",
            ],
        ),
    )
    return DeploymentEnvironment(env)


@composite
def deployment_strategy_strategy(draw):
    """
    Generate valid deployment strategies.
    """
    strategy = draw(
        st.sampled_from(
            [
                "blue_green",
                "rolling",
                "canary",
                "recreate",
            ],
        ),
    )
    return DeploymentStrategy(strategy)


@composite
def deployment_status_strategy(draw):
    """
    Generate valid deployment statuses.
    """
    status = draw(
        st.sampled_from(
            [
                "pending",
                "in_progress",
                "completed",
                "failed",
                "rolled_back",
            ],
        ),
    )
    return DeploymentStatus(status)


# ========== Service Strategies ==========


@composite
def service_name_strategy(draw):
    """
    Generate valid service names.
    """
    name = draw(
        st.text(
            alphabet=string.ascii_lowercase + string.digits + "-", min_size=1, max_size=63,
        ).filter(lambda x: x[0] not in "-" and x[-1] not in "-" and "--" not in x),
    )
    return ServiceName(name)


@composite
def service_port_strategy(draw):
    """
    Generate valid service ports.
    """
    port_num = draw(st.integers(min_value=1, max_value=65535))
    protocol = draw(st.sampled_from(["http", "https", "tcp", "udp", "grpc"]))
    return ServicePort(port_num, protocol)


@composite
def service_status_strategy(draw):
    """
    Generate valid service statuses.
    """
    status = draw(
        st.sampled_from(
            [
                "stopped",
                "starting",
                "running",
                "stopping",
                "failed",
            ],
        ),
    )
    return ServiceStatus(status)


# ========== User Name Strategy ==========


@composite
def user_name_strategy(draw):
    """
    Generate valid user names.
    """
    first_name = draw(st.text(alphabet=string.ascii_letters, min_size=1, max_size=50))
    last_name = draw(st.text(alphabet=string.ascii_letters, min_size=1, max_size=50))
    return f"{first_name} {last_name}"


# ========== DTO Strategies ==========


@composite
def create_user_dto_strategy(draw):
    """
    Generate CreateUserDTO instances.
    """
    from pheno.application.dtos.user import CreateUserDTO

    email = draw(email_strategy())
    name = draw(user_name_strategy())

    return CreateUserDTO(email=email.value, name=name)


@composite
def create_deployment_dto_strategy(draw):
    """
    Generate CreateDeploymentDTO instances.
    """
    from pheno.application.dtos.deployment import CreateDeploymentDTO

    environment = draw(deployment_environment_strategy())
    strategy = draw(deployment_strategy_strategy())

    return CreateDeploymentDTO(environment=environment.value, strategy=strategy.value)


@composite
def create_service_dto_strategy(draw):
    """
    Generate CreateServiceDTO instances.
    """
    from pheno.application.dtos.service import CreateServiceDTO

    name = draw(service_name_strategy())
    port = draw(service_port_strategy())

    return CreateServiceDTO(name=name.value, port=port.port, protocol=port.protocol)


@composite
def create_configuration_dto_strategy(draw):
    """
    Generate CreateConfigurationDTO instances.
    """
    from pheno.application.dtos.configuration import CreateConfigurationDTO

    key = draw(config_key_strategy())
    value = draw(config_value_strategy())
    description = draw(st.one_of(st.none(), st.text(max_size=200)))

    return CreateConfigurationDTO(key=key.value, value=value.value, description=description)
