"""CRUD Validators.

Generic validators for DTOs and business rules. Standardizes validation patterns across
the application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel, ValidationError

from pheno.domain.exceptions.base import DomainException
from pheno.observability.logging import get_logger

logger = get_logger(__name__)

# Type variables
DTOType = TypeVar("DTOType", bound=BaseModel)


class DTOValidator(ABC, Generic[DTOType]):
    """Abstract base class for DTO validation.

    Provides standard patterns for:
    - Field validation
    - Business rule validation
    - Cross-field validation
    - Custom validation logic
    """

    @abstractmethod
    def validate(self, dto: DTOType) -> None:
        """Validate DTO.

        Args:
            dto: DTO to validate

        Raises:
            ValidationError: If validation fails
        """

    def validate_field(self, dto: DTOType, field_name: str, value: Any) -> None:
        """Validate a specific field.

        Args:
            dto: DTO being validated
            field_name: Name of the field
            value: Field value

        Raises:
            ValidationError: If field validation fails
        """

    def validate_business_rules(self, dto: DTOType) -> None:
        """Validate business rules.

        Args:
            dto: DTO to validate

        Raises:
            ValidationError: If business rules are violated
        """


class BusinessRuleValidator(ABC, Generic[DTOType]):
    """Abstract base class for business rule validation.

    Provides standard patterns for:
    - Complex business logic validation
    - Cross-entity validation
    - External system validation
    - Conditional validation
    """

    @abstractmethod
    async def validate(self, dto: DTOType, context: dict[str, Any] | None = None) -> None:
        """Validate business rules.

        Args:
            dto: DTO to validate
            context: Additional context for validation

        Raises:
            DomainException: If business rules are violated
        """

    async def validate_creation(
        self, dto: DTOType, context: dict[str, Any] | None = None,
    ) -> None:
        """
        Validate business rules for creation.
        """
        await self.validate(dto, context)

    async def validate_update(self, dto: DTOType, context: dict[str, Any] | None = None) -> None:
        """
        Validate business rules for update.
        """
        await self.validate(dto, context)

    async def validate_deletion(
        self, dto: DTOType, context: dict[str, Any] | None = None,
    ) -> None:
        """
        Validate business rules for deletion.
        """
        await self.validate(dto, context)


class FieldValidator:
    """Generic field validator with common validation patterns.

    Provides standard validation for common field types and patterns.
    """

    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email format.
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email

    @staticmethod
    def validate_uuid(uuid_str: str) -> str:
        """
        Validate UUID format.
        """
        try:
            UUID(uuid_str)
            return uuid_str
        except ValueError:
            raise ValueError("Invalid UUID format")

    @staticmethod
    def validate_positive_number(value: float) -> int | float:
        """
        Validate positive number.
        """
        if value <= 0:
            raise ValueError("Value must be positive")
        return value

    @staticmethod
    def validate_non_empty_string(value: str) -> str:
        """
        Validate non-empty string.
        """
        if not value or not value.strip():
            raise ValueError("String cannot be empty")
        return value.strip()

    @staticmethod
    def validate_enum_value(value: Any, enum_class: type[Enum]) -> Any:
        """
        Validate enum value.
        """
        if value not in enum_class:
            raise ValueError(f"Value must be one of {list(enum_class)}")
        return value

    @staticmethod
    def validate_length(value: str, min_length: int = 0, max_length: int | None = None) -> str:
        """
        Validate string length.
        """
        if len(value) < min_length:
            raise ValueError(f"String must be at least {min_length} characters long")
        if max_length is not None and len(value) > max_length:
            raise ValueError(f"String must be at most {max_length} characters long")
        return value


class ValidationErrorHandler:
    """Handles validation errors and converts them to appropriate exceptions.

    Provides standard error handling patterns for different validation scenarios.
    """

    @staticmethod
    def handle_validation_error(error: ValidationError) -> DomainException:
        """Handle Pydantic validation error.

        Args:
            error: Pydantic validation error

        Returns:
            Domain exception
        """
        error_messages = []
        for err in error.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            message = err["msg"]
            error_messages.append(f"{field}: {message}")

        return DomainException(f"Validation error: {'; '.join(error_messages)}")

    @staticmethod
    def handle_business_rule_error(error: DomainException) -> DomainException:
        """Handle business rule validation error.

        Args:
            error: Business rule validation error

        Returns:
            Domain exception
        """
        return error

    @staticmethod
    def handle_field_error(field_name: str, error: Exception) -> DomainException:
        """Handle field validation error.

        Args:
            field_name: Name of the field
            error: Field validation error

        Returns:
            Domain exception
        """
        return DomainException(f"Field '{field_name}' validation error: {error!s}")


class CompositeValidator(Generic[DTOType]):
    """Composite validator that combines multiple validation strategies.

    Provides a single interface for all validation operations.
    """

    def __init__(
        self,
        dto_validators: list[DTOValidator[DTOType]] | None = None,
        business_rule_validators: list[BusinessRuleValidator[DTOType]] | None = None,
    ):
        """Initialize composite validator.

        Args:
            dto_validators: List of DTO validators
            business_rule_validators: List of business rule validators
        """
        self.dto_validators = dto_validators or []
        self.business_rule_validators = business_rule_validators or []

    async def validate(
        self,
        dto: DTOType,
        context: dict[str, Any] | None = None,
        validate_dto: bool = True,
        validate_business_rules: bool = True,
    ) -> None:
        """Validate DTO using all validators.

        Args:
            dto: DTO to validate
            context: Additional context for validation
            validate_dto: Whether to run DTO validators
            validate_business_rules: Whether to run business rule validators

        Raises:
            ValidationError: If DTO validation fails
            DomainException: If business rule validation fails
        """
        # Run DTO validators
        if validate_dto:
            for validator in self.dto_validators:
                try:
                    validator.validate(dto)
                except Exception as e:
                    if isinstance(e, ValidationError):
                        raise
                    raise ValidationError(
                        [{"loc": ("dto",), "msg": str(e), "type": "value_error"}],
                    )

        # Run business rule validators
        if validate_business_rules:
            for validator in self.business_rule_validators:
                try:
                    await validator.validate(dto, context)
                except DomainException:
                    raise
                except Exception as e:
                    raise DomainException(f"Business rule validation error: {e!s}")

    def add_dto_validator(self, validator: DTOValidator[DTOType]) -> None:
        """
        Add DTO validator.
        """
        self.dto_validators.append(validator)

    def add_business_rule_validator(self, validator: BusinessRuleValidator[DTOType]) -> None:
        """
        Add business rule validator.
        """
        self.business_rule_validators.append(validator)

    def remove_dto_validator(self, validator: DTOValidator[DTOType]) -> None:
        """
        Remove DTO validator.
        """
        if validator in self.dto_validators:
            self.dto_validators.remove(validator)

    def remove_business_rule_validator(self, validator: BusinessRuleValidator[DTOType]) -> None:
        """
        Remove business rule validator.
        """
        if validator in self.business_rule_validators:
            self.business_rule_validators.remove(validator)
