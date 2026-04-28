"""
Generic error handling and categorization.
"""

import logging
import time
import traceback
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """
    Error severity levels.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """
    Generic error categories.
    """

    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM_ERROR = "system_error"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for error handling.

    Attributes:
        operation_name: Name of the operation that failed
        operation_id: Unique identifier for this operation
        timestamp: When the error occurred
        user_context: User-specific context
        system_context: System-specific context
        previous_errors: History of previous errors in this operation
    """

    operation_name: str
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    user_context: dict[str, Any] = field(default_factory=dict)
    system_context: dict[str, Any] = field(default_factory=dict)
    previous_errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ErrorMetrics:
    """Metrics for error tracking.

    Attributes:
        total_errors: Total number of errors
        errors_by_category: Count of errors by category
        errors_by_severity: Count of errors by severity
        successful_operations: Count of successful operations
        retry_attempts: Total retry attempts
        circuit_breaker_activations: Times circuit breaker opened
    """

    total_errors: int = 0
    errors_by_category: dict[str, int] = field(default_factory=dict)
    errors_by_severity: dict[str, int] = field(default_factory=dict)
    successful_operations: int = 0
    retry_attempts: int = 0
    circuit_breaker_activations: int = 0


@dataclass
class ErrorInfo:
    """Detailed error information.

    Attributes:
        exception: The exception that occurred
        category: Error category
        severity: Error severity
        context: Error context
        traceback_str: Formatted traceback
        metadata: Additional metadata
        retry_count: Number of retries attempted
        original_exception: Original exception if wrapped
    """

    exception: Exception
    category: ErrorCategory
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    context: ErrorContext | None = None
    traceback_str: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    original_exception: Exception | None = None

    def __post_init__(self):
        if self.traceback_str is None and self.exception:
            self.traceback_str = traceback.format_exc()

        if self.original_exception is None and self.exception:
            self.original_exception = self.exception


class ErrorHandler:
    """Generic error handler with categorization and custom handlers.

    This class provides:
    - Automatic error categorization
    - Severity determination
    - Custom error handlers per category
    - Error statistics tracking

    Example:
        >>> handler = ErrorHandler()
        >>> handler.register_handler(
        ...     ErrorCategory.NETWORK,
        ...     lambda error: print(f"Network error: {error.exception}")
        ... )
        >>> error_info = handler.create_error_info(ConnectionError("Failed"))
        >>> await handler.handle_error(error_info)
    """

    def __init__(self):
        self.error_handlers: dict[ErrorCategory, list[Callable]] = {}
        self.error_stats: dict[str, int] = {}
        self.metrics = ErrorMetrics()

    def register_handler(self, category: ErrorCategory, handler: Callable[[ErrorInfo], Any]):
        """Register a custom error handler for a specific category.

        Args:
            category: Error category to handle
            handler: Callable that takes ErrorInfo and returns Any
        """
        if category not in self.error_handlers:
            self.error_handlers[category] = []
        self.error_handlers[category].append(handler)

    def categorize_error(
        self, exception: Exception, context: ErrorContext | None = None,
    ) -> ErrorCategory:
        """Automatically categorize an error based on type and message.

        Args:
            exception: The exception to categorize
            context: Optional error context

        Returns:
            ErrorCategory enum value
        """
        error_str = str(exception).lower()
        error_type = type(exception).__name__.lower()

        # Network errors
        if any(kw in error_str for kw in ["connection", "network", "dns", "socket"]) or any(
            kw in error_type for kw in ["connection", "timeout"]
        ):
            return ErrorCategory.NETWORK

        # Timeout errors
        if "timeout" in error_str or "timeout" in error_type:
            return ErrorCategory.TIMEOUT

        # Authentication errors
        if any(kw in error_str for kw in ["unauthorized", "authentication", "login", "token"]):
            return ErrorCategory.AUTHENTICATION

        # Authorization errors
        if any(kw in error_str for kw in ["forbidden", "permission", "access denied"]):
            return ErrorCategory.AUTHORIZATION

        # Validation errors
        if any(kw in error_type for kw in ["value", "validation", "argument"]) or any(
            kw in error_str for kw in ["invalid", "required", "mismatch"]
        ):
            return ErrorCategory.VALIDATION

        # Rate limit errors
        if any(kw in error_str for kw in ["rate limit", "quota", "too many"]):
            return ErrorCategory.RATE_LIMIT

        # Resource errors
        if any(kw in error_str for kw in ["memory", "disk", "resource"]):
            return ErrorCategory.RESOURCE_EXHAUSTED

        # Configuration errors
        if any(kw in error_str for kw in ["config", "setting", "env"]):
            return ErrorCategory.CONFIGURATION

        # System errors
        if any(kw in error_type for kw in ["system", "os"]):
            return ErrorCategory.SYSTEM_ERROR

        return ErrorCategory.UNKNOWN

    def determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on exception and category.

        Args:
            exception: The exception
            category: Error category

        Returns:
            ErrorSeverity enum value
        """
        # Critical errors
        if isinstance(exception, (RuntimeError, SystemError)):
            return ErrorSeverity.CRITICAL

        # High severity for authentication/authorization
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.HIGH

        # Medium severity for network, timeout, rate limit
        if category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT, ErrorCategory.RATE_LIMIT]:
            return ErrorSeverity.MEDIUM

        # Low severity for validation and configuration
        if category in [ErrorCategory.VALIDATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.LOW

        return ErrorSeverity.MEDIUM

    def create_error_info(
        self, exception: Exception, context: ErrorContext | None = None,
    ) -> ErrorInfo:
        """Create detailed error information.

        Args:
            exception: The exception
            context: Optional error context

        Returns:
            ErrorInfo object with categorization and severity
        """
        category = self.categorize_error(exception, context)
        severity = self.determine_severity(exception, category)

        return ErrorInfo(exception=exception, category=category, severity=severity, context=context)

    async def handle_error(self, error_info: ErrorInfo) -> dict[str, Any]:
        """Handle an error using registered handlers.

        Args:
            error_info: Error information

        Returns:
            Dictionary with handler results
        """
        # Update statistics
        self.metrics.total_errors += 1
        category_key = error_info.category.value
        severity_key = error_info.severity.value

        self.error_stats[category_key] = self.error_stats.get(category_key, 0) + 1
        self.metrics.errors_by_category[category_key] = (
            self.metrics.errors_by_category.get(category_key, 0) + 1
        )
        self.metrics.errors_by_severity[severity_key] = (
            self.metrics.errors_by_severity.get(severity_key, 0) + 1
        )

        results = []

        # Get handlers for this category
        handlers = self.error_handlers.get(error_info.category, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(error_info)
                else:
                    result = handler(error_info)
                results.append(result)
            except Exception as e:
                logger.exception(f"Error handler failed: {e}")
                results.append({"error": str(e)})

        return {
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "handler_results": results,
            "error_message": str(error_info.exception),
        }

    def get_metrics(self) -> ErrorMetrics:
        """Get current error metrics.

        Returns:
            ErrorMetrics object
        """
        return self.metrics

    def reset_metrics(self):
        """
        Reset error metrics.
        """
        self.metrics = ErrorMetrics()
        self.error_stats.clear()


# Import asyncio for async handler check
import asyncio
