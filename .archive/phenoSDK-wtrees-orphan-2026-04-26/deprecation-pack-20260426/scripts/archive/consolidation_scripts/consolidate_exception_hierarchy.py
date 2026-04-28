#!/usr/bin/env python3
"""
Exception Hierarchy Consolidation Script.

This script consolidates all duplicate exception classes into a unified hierarchy.

Actions performed:
1. Consolidate all exception classes into a single hierarchy
2. Remove duplicate exception definitions
3. Create unified exception system
4. Update imports across the codebase
"""

import shutil
from pathlib import Path


class ExceptionHierarchyConsolidator:
    """Consolidates exception hierarchy."""

    def __init__(self, base_path: str = "src/pheno"):
        """Initialize consolidator.

        Args:
            base_path: Base path for pheno modules
        """
        self.base_path = Path(base_path)
        self.removed_files: list[str] = []
        self.consolidated_exceptions: dict[str, str] = {}

    def consolidate_exception_hierarchy(self) -> None:
        """Consolidate exception hierarchy."""
        print("🔧 Consolidating exception hierarchy...")

        # Files to remove (duplicate exception functionality)
        duplicate_exception_files = [
            "exceptions/exceptions.py",  # Old exceptions
            "exceptions/unified.py",  # Duplicate unified exceptions
            "exceptions/handlers.py",  # Move to base
            "exceptions/types.py",  # Move to base
        ]

        for file_path in duplicate_exception_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                self._remove_file(full_path)
                print(f"  ❌ Removed: {file_path}")

        # Consolidate exception functionality
        self._consolidate_exception_functionality()

    def consolidate_duplicate_exceptions(self) -> None:
        """Consolidate duplicate exception classes across modules."""
        print("🔧 Consolidating duplicate exception classes...")

        # Find and consolidate duplicate exception classes
        duplicate_exceptions = [
            "ErrorCategory",
            "ErrorContext",
            "ValidationError",
            "AuthenticationError",
            "AuthorizationError",
            "ConfigurationError",
            "ResourceNotFoundError",
            "NetworkError",
            "RateLimitError",
            "ExternalServiceError",
            "DatabaseError",
            "InternalError",
        ]

        for exception_name in duplicate_exceptions:
            self._consolidate_exception_class(exception_name)

    def create_unified_exception_system(self) -> None:
        """Create unified exception system."""
        print("🏗️  Creating unified exception system...")

        # Create the unified exception system
        unified_exceptions_content = '''"""
Unified Exception System for Pheno SDK.

This module provides a comprehensive, unified exception hierarchy consolidating
all error handling across the pheno-sdk codebase.

Exception Hierarchy:
====================

PhenoException (base)
├── RetryableError
│   ├── NetworkError
│   ├── RateLimitError
│   ├── DatabaseConnectionError
│   └── IntegrationError
│       ├── ExternalServiceError
│       └── APIError
├── NonRetryableError
│   ├── ValidationError
│   │   ├── SchemaValidationError
│   │   └── FieldValidationError
│   ├── NotFoundError
│   │   ├── EntityNotFoundError
│   │   └── ResourceNotFoundError
│   ├── AuthenticationError
│   │   ├── InvalidCredentialsError
│   │   ├── TokenExpiredError
│   │   └── MissingAuthenticationError
│   ├── AuthorizationError
│   │   ├── PermissionDeniedError
│   │   ├── InsufficientPermissionsError
│   │   └── UnauthorizedAccessError
│   ├── ConfigurationError
│   │   ├── MissingConfigurationError
│   │   └── InvalidConfigurationError
│   ├── ConstraintViolationError
│   │   ├── UniqueConstraintError
│   │   ├── ForeignKeyError
│   │   ├── CheckConstraintError
│   │   └── NotNullConstraintError
│   └── BusinessRuleViolation
│       ├── InvalidStateTransitionError
│       └── DomainError
└── InternalError
    └── NotImplementedError

Error Categories:
=================
- NETWORK: Network and communication errors
- AUTHENTICATION: Authentication failures
- AUTHORIZATION: Permission and authorization failures
- VALIDATION: Input validation failures
- RESOURCE_NOT_FOUND: Resource/entity not found
- RATE_LIMIT: Rate limiting
- EXTERNAL_SERVICE: External API/service failures
- CONFIGURATION: Configuration problems
- DATABASE: Database operation failures
- BUSINESS_RULE: Business logic violations
- INTERNAL: Internal system errors
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ErrorCategory(Enum):
    """Categories of errors for consistent handling and routing."""

    # Network and communication errors
    NETWORK = "network"

    # Authentication and authorization
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"

    # Validation and input errors
    VALIDATION = "validation"

    # Resource and entity errors
    RESOURCE_NOT_FOUND = "resource_not_found"

    # Rate limiting
    RATE_LIMIT = "rate_limit"

    # External services
    EXTERNAL_SERVICE = "external_service"

    # Configuration errors
    CONFIGURATION = "configuration"

    # Database errors
    DATABASE = "database"

    # Business logic errors
    BUSINESS_RULE = "business_rule"

    # Internal errors
    INTERNAL = "internal"


@dataclass
class ErrorContext:
    """Rich context information for exceptions."""

    component: str = "unknown"
    operation: str = "unknown"
    entity_type: str | None = None
    entity_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "operation": self.operation,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


# HTTP status code mapping for error categories
ERROR_STATUS_MAP = {
    ErrorCategory.NETWORK: 503,
    ErrorCategory.AUTHENTICATION: 401,
    ErrorCategory.AUTHORIZATION: 403,
    ErrorCategory.VALIDATION: 400,
    ErrorCategory.RESOURCE_NOT_FOUND: 404,
    ErrorCategory.RATE_LIMIT: 429,
    ErrorCategory.EXTERNAL_SERVICE: 502,
    ErrorCategory.CONFIGURATION: 500,
    ErrorCategory.DATABASE: 500,
    ErrorCategory.BUSINESS_RULE: 422,
    ErrorCategory.INTERNAL: 500,
}


class PhenoException(Exception):
    """Base exception for all Pheno SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        category: ErrorCategory | None = None,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.category = category or ErrorCategory.INTERNAL
        self.context = context or ErrorContext()
        self.cause = cause
        self.retryable = retryable
        self.timestamp = datetime.now(UTC)

    @property
    def http_status(self) -> int:
        """Get HTTP status code for this error."""
        return ERROR_STATUS_MAP.get(self.category, 500)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "error": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "status": self.http_status,
            "retryable": self.retryable,
            "context": self.context.to_dict(),
            "timestamp": self.timestamp.isoformat(),
        }

    def to_api_error(self) -> dict[str, Any]:
        """Convert to legacy API error format."""
        return {
            "code": self.error_code,
            "message": self.message,
            "status": self.http_status,
            "details": self.context.to_dict(),
        }


class RetryableError(PhenoException):
    """Base class for retryable errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, retryable=True, **kwargs)


class NonRetryableError(PhenoException):
    """Base class for non-retryable errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, retryable=False, **kwargs)


# Network and communication errors
class NetworkError(RetryableError):
    """Network communication error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class RateLimitError(RetryableError):
    """Rate limiting error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RATE_LIMIT,
            **kwargs
        )


class DatabaseConnectionError(RetryableError):
    """Database connection error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            **kwargs
        )


# Integration errors
class IntegrationError(RetryableError):
    """Integration error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            **kwargs
        )


class ExternalServiceError(IntegrationError):
    """External service error."""
    pass


class APIError(IntegrationError):
    """API error."""
    pass


# Validation errors
class ValidationError(NonRetryableError):
    """Input validation error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )


class SchemaValidationError(ValidationError):
    """Schema validation error."""
    pass


class FieldValidationError(ValidationError):
    """Field validation error."""
    pass


# Resource/entity errors
class NotFoundError(NonRetryableError):
    """Resource not found error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RESOURCE_NOT_FOUND,
            **kwargs
        )


class EntityNotFoundError(NotFoundError):
    """Entity not found error."""
    pass


class ResourceNotFoundError(NotFoundError):
    """Resource not found error."""
    pass


# Authentication errors
class AuthenticationError(NonRetryableError):
    """Authentication error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            **kwargs
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error."""
    pass


class TokenExpiredError(AuthenticationError):
    """Token expired error."""
    pass


class MissingAuthenticationError(AuthenticationError):
    """Missing authentication error."""
    pass


# Authorization errors
class AuthorizationError(NonRetryableError):
    """Authorization error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHORIZATION,
            **kwargs
        )


class PermissionDeniedError(AuthorizationError):
    """Permission denied error."""
    pass


class InsufficientPermissionsError(AuthorizationError):
    """Insufficient permissions error."""
    pass


class UnauthorizedAccessError(AuthorizationError):
    """Unauthorized access error."""
    pass


# Configuration errors
class ConfigurationError(NonRetryableError):
    """Configuration error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )


class MissingConfigurationError(ConfigurationError):
    """Missing configuration error."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration error."""
    pass


# Database constraint errors
class ConstraintViolationError(NonRetryableError):
    """Database constraint violation error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            **kwargs
        )


class UniqueConstraintError(ConstraintViolationError):
    """Unique constraint violation error."""
    pass


class ForeignKeyError(ConstraintViolationError):
    """Foreign key constraint error."""
    pass


class CheckConstraintError(ConstraintViolationError):
    """Check constraint error."""
    pass


class NotNullConstraintError(ConstraintViolationError):
    """Not null constraint error."""
    pass


# Business logic errors
class BusinessRuleViolation(NonRetryableError):
    """Business rule violation error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.BUSINESS_RULE,
            **kwargs
        )


class InvalidStateTransitionError(BusinessRuleViolation):
    """Invalid state transition error."""
    pass


class DomainError(BusinessRuleViolation):
    """Domain error."""
    pass


# Internal errors
class InternalError(NonRetryableError):
    """Internal system error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.INTERNAL,
            **kwargs
        )


class NotImplementedError(InternalError):
    """Not implemented error."""
    pass


# Database errors
class DatabaseError(RetryableError):
    """Database error."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            **kwargs
        )


# Utility functions
def is_retryable(error: Exception) -> bool:
    """Check if an error is retryable."""
    if isinstance(error, PhenoException):
        return error.retryable
    return False


def normalize_error(
    err: Exception | str,
    fallback_message: str = "Internal server error",
    component: str = "unknown",
    operation: str = "unknown",
) -> PhenoException:
    """Normalize any exception to PhenoException."""
    if isinstance(err, PhenoException):
        return err

    if isinstance(err, str):
        message = err
    else:
        message = str(err)

    context = ErrorContext(
        component=component,
        operation=operation,
    )

    return InternalError(
        message or fallback_message,
        context=context,
        cause=err if isinstance(err, Exception) else None,
    )


def normalize_postgres_error(
    err: Exception,
    fallback_message: str = "Database error",
) -> PhenoException:
    """Normalize PostgreSQL errors to PhenoException."""
    error_message = str(err)

    # Map common PostgreSQL errors
    if "unique constraint" in error_message.lower():
        return UniqueConstraintError(
            f"Unique constraint violation: {error_message}",
            context=ErrorContext(component="database", operation="insert"),
        )
    elif "foreign key" in error_message.lower():
        return ForeignKeyError(
            f"Foreign key constraint violation: {error_message}",
            context=ErrorContext(component="database", operation="insert"),
        )
    elif "not null" in error_message.lower():
        return NotNullConstraintError(
            f"Not null constraint violation: {error_message}",
            context=ErrorContext(component="database", operation="insert"),
        )
    elif "check constraint" in error_message.lower():
        return CheckConstraintError(
            f"Check constraint violation: {error_message}",
            context=ErrorContext(component="database", operation="insert"),
        )
    else:
        return DatabaseError(
            error_message or fallback_message,
            context=ErrorContext(component="database", operation="unknown"),
        )


# Backward compatibility aliases
ZenMCPError = PhenoException
StructuredError = PhenoException
ErrorHandlingError = InternalError


__all__ = [
    # Base classes
    "PhenoException",
    "RetryableError",
    "NonRetryableError",
    "ErrorCategory",
    "ErrorContext",

    # Network errors
    "NetworkError",
    "RateLimitError",
    "DatabaseConnectionError",

    # Integration errors
    "IntegrationError",
    "ExternalServiceError",
    "APIError",

    # Validation errors
    "ValidationError",
    "SchemaValidationError",
    "FieldValidationError",

    # Resource errors
    "NotFoundError",
    "EntityNotFoundError",
    "ResourceNotFoundError",

    # Authentication errors
    "AuthenticationError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "MissingAuthenticationError",

    # Authorization errors
    "AuthorizationError",
    "PermissionDeniedError",
    "InsufficientPermissionsError",
    "UnauthorizedAccessError",

    # Configuration errors
    "ConfigurationError",
    "MissingConfigurationError",
    "InvalidConfigurationError",

    # Database constraint errors
    "ConstraintViolationError",
    "UniqueConstraintError",
    "ForeignKeyError",
    "CheckConstraintError",
    "NotNullConstraintError",

    # Business logic errors
    "BusinessRuleViolation",
    "InvalidStateTransitionError",
    "DomainError",

    # Internal errors
    "InternalError",
    "NotImplementedError",
    "DatabaseError",

    # Utility functions
    "is_retryable",
    "normalize_error",
    "normalize_postgres_error",

    # Backward compatibility
    "ZenMCPError",
    "StructuredError",
    "ErrorHandlingError",
    "ERROR_STATUS_MAP",
]
'''

        # Write unified exceptions
        unified_file = self.base_path / "exceptions" / "unified_exceptions.py"
        unified_file.write_text(unified_exceptions_content)
        print(f"  ✅ Created unified exceptions: {unified_file}")

        # Update main exceptions init
        self._update_exceptions_init()

    def _consolidate_exception_functionality(self) -> None:
        """Consolidate exception functionality."""
        print("  🔄 Consolidating exception functionality...")

        # Keep the best exception implementation
        base_exceptions = self.base_path / "exceptions" / "base.py"
        if base_exceptions.exists():
            print(f"    ✅ Keeping base exceptions: {base_exceptions}")

        # Create unified exception system
        self.create_unified_exception_system()

    def _consolidate_exception_class(self, exception_name: str) -> None:
        """Consolidate a specific exception class."""
        print(f"  🔄 Consolidating {exception_name}...")

        # Find all files containing this exception class
        files_with_exception = []
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if f"class {exception_name}" in content:
                    files_with_exception.append(py_file)
            except Exception:
                pass

        if len(files_with_exception) > 1:
            print(
                f"    ⚠️  Found {len(files_with_exception)} files with {exception_name}",
            )
            # Keep the one in exceptions/ directory, remove others
            for file_path in files_with_exception:
                if "exceptions/" not in str(file_path):
                    # Remove duplicate definition
                    self._remove_duplicate_class_from_file(file_path, exception_name)
                    print(f"    ❌ Removed {exception_name} from {file_path}")

    def _remove_duplicate_class_from_file(
        self, file_path: Path, class_name: str,
    ) -> None:
        """Remove duplicate class definition from file."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Find class definition
            class_start = None
            class_end = None
            indent_level = None

            for i, line in enumerate(lines):
                if f"class {class_name}" in line and ":" in line:
                    class_start = i
                    indent_level = len(line) - len(line.lstrip())
                    break

            if class_start is not None:
                # Find end of class
                for i in range(class_start + 1, len(lines)):
                    line = lines[i]
                    if line.strip() and not line.startswith(
                        " " * ((indent_level or 0) + 1),
                    ):
                        class_end = i
                        break

                if class_end is None:
                    class_end = len(lines)

                # Remove class definition
                new_lines = lines[:class_start] + lines[class_end:]
                file_path.write_text("\n".join(new_lines))

        except Exception as e:
            print(f"    ⚠️  Could not remove {class_name} from {file_path}: {e}")

    def _update_exceptions_init(self) -> None:
        """Update exceptions __init__.py."""
        print("  🔄 Updating exceptions __init__.py...")

        init_content = '''"""
Unified Exception System for Pheno SDK.

This module provides a comprehensive, unified exception hierarchy consolidating
all error handling across the pheno-sdk codebase.
"""

from __future__ import annotations

# Import everything from unified exceptions
from .unified_exceptions import *

__all__ = [
    # Re-export everything from unified_exceptions
    *__all__,
]
'''

        init_file = self.base_path / "exceptions" / "__init__.py"
        init_file.write_text(init_content)
        print("    ✅ Updated exceptions __init__.py")

    def generate_consolidation_report(self) -> None:
        """Generate consolidation report."""
        print("\n📊 Exception Hierarchy Consolidation Report")
        print("=" * 60)
        print(f"Files removed: {len(self.removed_files)}")
        print(f"Exceptions consolidated: {len(self.consolidated_exceptions)}")

        print("\nRemoved files:")
        for file_path in self.removed_files:
            print(f"  - {file_path}")

        print("\nConsolidated exceptions:")
        for old_exception, new_exception in self.consolidated_exceptions.items():
            print(f"  - {old_exception} → {new_exception}")

    def run_consolidation(self) -> None:
        """Run full exception hierarchy consolidation process."""
        print("🚀 Starting exception hierarchy consolidation...")
        print("=" * 60)

        # Step 1: Consolidate exception hierarchy
        self.consolidate_exception_hierarchy()

        # Step 2: Consolidate duplicate exceptions
        self.consolidate_duplicate_exceptions()

        # Step 3: Generate report
        self.generate_consolidation_report()

        print("\n✅ Exception hierarchy consolidation complete!")
        print("Next steps:")
        print("1. Update imports across the codebase")
        print("2. Run tests to ensure functionality is preserved")
        print("3. Update documentation")
        print("4. Continue with other duplicate class consolidation")

    def _remove_file(self, file_path: Path) -> None:
        """Remove a file and track it."""
        try:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            self.removed_files.append(str(file_path))
        except Exception as e:
            print(f"    ⚠️  Could not remove {file_path}: {e}")


def main():
    """Main consolidation function."""
    consolidator = ExceptionHierarchyConsolidator()
    consolidator.run_consolidation()


if __name__ == "__main__":
    main()
