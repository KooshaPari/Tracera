"""Domain errors - Pure domain errors with no external dependencies.

Following ADR-001 dependency rule:
- domain/ contains ZERO external dependencies
- Only standard library imports allowed
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain errors.

    Domain errors represent business rule violations.
    They should be descriptive and actionable.
    """

    def __init__(self, message: str, code: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}


class EntityNotFoundError(DomainError):
    """Raised when an entity cannot be found."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            code="ENTITY_NOT_FOUND",
            context={"entity_type": entity_type, "entity_id": entity_id},
        )


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated."""

    def __init__(self, rule: str, details: str) -> None:
        super().__init__(
            message=f"Business rule violated: {rule}",
            code="BUSINESS_RULE_VIOLATION",
            context={"rule": rule, "details": details},
        )


class InvalidStateTransitionError(DomainError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self,
        entity_type: str,
        current_state: str,
        attempted_state: str
    ) -> None:
        super().__init__(
            message=f"Invalid state transition for {entity_type}: {current_state} -> {attempted_state}",
            code="INVALID_STATE_TRANSITION",
            context={
                "entity_type": entity_type,
                "current_state": current_state,
                "attempted_state": attempted_state,
            },
        )


# Re-export for convenience
__all__ = [
    "DomainError",
    "EntityNotFoundError",
    "BusinessRuleViolationError",
    "InvalidStateTransitionError",
]
