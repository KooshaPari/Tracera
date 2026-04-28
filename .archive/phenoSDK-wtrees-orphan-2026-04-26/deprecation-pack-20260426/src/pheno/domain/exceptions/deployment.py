"""
Deployment-related domain exceptions.
"""

from pheno.domain.exceptions.base import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidStateTransitionError,
)


class DeploymentNotFoundError(EntityNotFoundError):
    """
    Raised when a deployment is not found.
    """

    def __init__(self, deployment_id: str):
        super().__init__("Deployment", deployment_id)


class DeploymentAlreadyExistsError(EntityAlreadyExistsError):
    """
    Raised when attempting to create a duplicate deployment.
    """

    def __init__(self, identifier: str):
        super().__init__("Deployment", identifier)


class InvalidDeploymentStateError(InvalidStateTransitionError):
    """
    Raised when an invalid deployment state transition is attempted.
    """

    def __init__(self, current_state: str, new_state: str):
        super().__init__("Deployment", current_state, new_state)
