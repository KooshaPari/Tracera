"""
Custom validator framework.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationRule:
    """
    Validation rule.
    """

    validator: Callable[[Any], bool]
    message: str


class Validator:
    """Custom validator builder.

    Example:
        validator = Validator()
        validator.add_rule(lambda x: len(x) > 3, "Must be longer than 3")
        validator.add_rule(lambda x: x.isalnum(), "Must be alphanumeric")

        result = validator.validate("abc123")
    """

    def __init__(self):
        self.rules: list[ValidationRule] = []

    def add_rule(self, validator: Callable[[Any], bool], message: str) -> "Validator":
        """
        Add validation rule.
        """
        self.rules.append(ValidationRule(validator, message))
        return self

    def validate(self, value: Any) -> tuple[bool, list[str]]:
        """Validate value against all rules.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for rule in self.rules:
            if not rule.validator(value):
                errors.append(rule.message)

        return len(errors) == 0, errors


def validate(value: Any, *rules: ValidationRule) -> tuple[bool, list[str]]:
    """
    Quick validation function.
    """
    validator = Validator()
    for rule in rules:
        validator.add_rule(rule.validator, rule.message)
    return validator.validate(value)
