"""
Infrastructure-related domain exceptions.
"""

from pheno.domain.exceptions.base import (
    BusinessRuleViolation,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidStateTransitionError,
)


class ServiceNotFoundError(EntityNotFoundError):
    """
    Raised when a service is not found.
    """

    def __init__(self, service_id: str):
        super().__init__("Service", service_id)


class ServiceAlreadyExistsError(EntityAlreadyExistsError):
    """
    Raised when attempting to create a duplicate service.
    """

    def __init__(self, service_name: str):
        super().__init__("Service", service_name)


class InvalidServiceStateError(InvalidStateTransitionError):
    """
    Raised when an invalid service state transition is attempted.
    """

    def __init__(self, current_state: str, new_state: str):
        super().__init__("Service", current_state, new_state)


class PortAlreadyInUseError(BusinessRuleViolation):
    """
    Raised when attempting to use a port that's already in use.
    """

    def __init__(self, port: int, service_name: str):
        message = f"Port {port} is already in use by service '{service_name}'"
        super().__init__(message)
        self.port = port
        self.service_name = service_name
