"""
User-related domain exceptions.
"""

from pheno.domain.exceptions.base import (
    BusinessRuleViolation,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class UserNotFoundError(EntityNotFoundError):
    """
    Raised when a user is not found.
    """

    def __init__(self, user_id: str):
        super().__init__("User", user_id)


class UserAlreadyExistsError(EntityAlreadyExistsError):
    """
    Raised when attempting to create a duplicate user.
    """

    def __init__(self, email: str):
        super().__init__("User", email)


class UserInactiveError(BusinessRuleViolation):
    """
    Raised when attempting to perform an action on an inactive user.
    """

    def __init__(self, user_id: str):
        message = f"User '{user_id}' is inactive and cannot perform this action"
        super().__init__(message)
