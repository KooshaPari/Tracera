"""
Base domain exceptions.
"""


class DomainError(Exception):
    """
    Base exception for all domain errors.
    """

    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)


class ValidationError(DomainError):
    """
    Raised when input validation fails.
    """


class BusinessRuleViolation(DomainError):
    """
    Raised when a business rule is violated.
    """


class EntityNotFoundError(DomainError):
    """
    Raised when an entity is not found.
    """

    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = f"{entity_type} with ID '{entity_id}' not found"
        super().__init__(message)


class EntityAlreadyExistsError(DomainError):
    """
    Raised when attempting to create a duplicate entity.
    """

    def __init__(self, entity_type: str, identifier: str):
        self.entity_type = entity_type
        self.identifier = identifier
        message = f"{entity_type} with identifier '{identifier}' already exists"
        super().__init__(message)


class InvalidStateTransitionError(DomainError):
    """
    Raised when an invalid state transition is attempted.
    """

    def __init__(self, entity_type: str, current_state: str, new_state: str):
        self.entity_type = entity_type
        self.current_state = current_state
        self.new_state = new_state
        message = f"Invalid state transition for {entity_type}: {current_state} -> {new_state}"
        super().__init__(message)


class InvariantViolationError(DomainError):
    """
    Raised when a domain invariant is violated.
    """
