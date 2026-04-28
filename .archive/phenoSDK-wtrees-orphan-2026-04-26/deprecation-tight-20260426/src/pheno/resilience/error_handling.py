"""
Error categorization, tracking, and handling utilities.
"""

from __future__ import annotations

import re
import traceback
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger("pheno.resilience.error_handling")


class ErrorCategory(Enum):
    """
    Categories for error classification.
    """

    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    SERIALIZATION = "serialization"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """
    Severity levels for errors.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class ErrorInfo:
    """
    Information about an error.
    """

    error_id: str
    exception: Exception
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    retryable: bool = True
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "error_id": self.error_id,
            "exception_type": type(self.exception).__name__,
            "exception_message": str(self.exception),
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "stack_trace": self.stack_trace,
            "retryable": self.retryable,
            "tags": list(self.tags),
            "metadata": self.metadata,
        }


class ErrorCategorizer:
    """
    Categorizes errors based on various heuristics.
    """

    def __init__(self):
        self._patterns: dict[ErrorCategory, list[re.Pattern]] = {}
        self._exception_mappings: dict[type[Exception], ErrorCategory] = {}
        self._custom_categorizers: list[Callable[[Exception], ErrorCategory | None]] = []

        self._setup_default_patterns()
        self._setup_default_mappings()

    def _setup_default_patterns(self) -> None:
        """
        Setup default error patterns.
        """
        self._patterns = {
            ErrorCategory.NETWORK: [
                re.compile(r"connection.*refused", re.IGNORECASE),
                re.compile(r"network.*unreachable", re.IGNORECASE),
                re.compile(r"timeout.*connection", re.IGNORECASE),
                re.compile(r"socket.*error", re.IGNORECASE),
                re.compile(r"connection.*reset", re.IGNORECASE),
            ],
            ErrorCategory.TIMEOUT: [
                re.compile(r"timeout", re.IGNORECASE),
                re.compile(r"timed.*out", re.IGNORECASE),
                re.compile(r"deadline.*exceeded", re.IGNORECASE),
            ],
            ErrorCategory.AUTHENTICATION: [
                re.compile(r"authentication.*failed", re.IGNORECASE),
                re.compile(r"invalid.*credentials", re.IGNORECASE),
                re.compile(r"login.*failed", re.IGNORECASE),
                re.compile(r"unauthorized", re.IGNORECASE),
            ],
            ErrorCategory.AUTHORIZATION: [
                re.compile(r"access.*denied", re.IGNORECASE),
                re.compile(r"permission.*denied", re.IGNORECASE),
                re.compile(r"forbidden", re.IGNORECASE),
                re.compile(r"insufficient.*privileges", re.IGNORECASE),
            ],
            ErrorCategory.VALIDATION: [
                re.compile(r"validation.*error", re.IGNORECASE),
                re.compile(r"invalid.*input", re.IGNORECASE),
                re.compile(r"missing.*required", re.IGNORECASE),
                re.compile(r"format.*error", re.IGNORECASE),
            ],
            ErrorCategory.RESOURCE: [
                re.compile(r"resource.*not.*found", re.IGNORECASE),
                re.compile(r"out.*of.*memory", re.IGNORECASE),
                re.compile(r"disk.*full", re.IGNORECASE),
                re.compile(r"quota.*exceeded", re.IGNORECASE),
            ],
            ErrorCategory.DATABASE: [
                re.compile(r"database.*error", re.IGNORECASE),
                re.compile(r"sql.*error", re.IGNORECASE),
                re.compile(r"constraint.*violation", re.IGNORECASE),
                re.compile(r"deadlock", re.IGNORECASE),
            ],
            ErrorCategory.EXTERNAL_SERVICE: [
                re.compile(r"service.*unavailable", re.IGNORECASE),
                re.compile(r"api.*error", re.IGNORECASE),
                re.compile(r"http.*error", re.IGNORECASE),
                re.compile(r"rate.*limit", re.IGNORECASE),
            ],
        }

    def _setup_default_mappings(self) -> None:
        """
        Setup default exception type mappings.
        """
        self._exception_mappings = {
            ConnectionError: ErrorCategory.NETWORK,
            TimeoutError: ErrorCategory.TIMEOUT,
            PermissionError: ErrorCategory.AUTHORIZATION,
            FileNotFoundError: ErrorCategory.RESOURCE,
            ValueError: ErrorCategory.VALIDATION,
            TypeError: ErrorCategory.VALIDATION,
            KeyError: ErrorCategory.VALIDATION,
            AttributeError: ErrorCategory.VALIDATION,
        }

    def add_pattern(self, category: ErrorCategory, pattern: str | re.Pattern) -> None:
        """
        Add a pattern for error categorization.
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)

        if category not in self._patterns:
            self._patterns[category] = []

        self._patterns[category].append(pattern)
        logger.debug(f"Added pattern for {category.value}: {pattern.pattern}")

    def add_exception_mapping(
        self, exception_type: type[Exception], category: ErrorCategory,
    ) -> None:
        """
        Add exception type to category mapping.
        """
        self._exception_mappings[exception_type] = category
        logger.debug(f"Mapped {exception_type.__name__} to {category.value}")

    def add_custom_categorizer(
        self, categorizer: Callable[[Exception], ErrorCategory | None],
    ) -> None:
        """
        Add custom categorizer function.
        """
        self._custom_categorizers.append(categorizer)
        logger.debug("Added custom error categorizer")

    def categorize(self, exception: Exception) -> ErrorCategory:
        """
        Categorize an exception.
        """
        # Try custom categorizers first
        for categorizer in self._custom_categorizers:
            try:
                category = categorizer(exception)
                if category:
                    return category
            except Exception as e:
                logger.warning(f"Custom categorizer failed: {e}")

        # Try exception type mapping
        exception_type = type(exception)
        for mapped_type, category in self._exception_mappings.items():
            if issubclass(exception_type, mapped_type):
                return category

        # Try pattern matching on error message
        error_message = str(exception)
        for category, patterns in self._patterns.items():
            for pattern in patterns:
                if pattern.search(error_message):
                    return category

        # Default to unknown
        return ErrorCategory.UNKNOWN

    def get_retryable_categories(self) -> set[ErrorCategory]:
        """
        Get categories that are typically retryable.
        """
        return {
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.EXTERNAL_SERVICE,
            ErrorCategory.RESOURCE,
        }

    def is_retryable(self, exception: Exception) -> bool:
        """
        Check if an exception is retryable.
        """
        category = self.categorize(exception)
        return category in self.get_retryable_categories()


class ErrorHandler:
    """
    Handles errors with configurable strategies.
    """

    def __init__(self, categorizer: ErrorCategorizer | None = None):
        self.categorizer = categorizer or ErrorCategorizer()
        self._handlers: dict[ErrorCategory, Callable[[ErrorInfo], Any]] = {}
        self._default_handler: Callable[[ErrorInfo], Any] | None = None
        self._error_tracker: ErrorTracker | None = None

    def set_handler(self, category: ErrorCategory, handler: Callable[[ErrorInfo], Any]) -> None:
        """
        Set handler for specific error category.
        """
        self._handlers[category] = handler
        logger.debug(f"Set handler for {category.value}")

    def set_default_handler(self, handler: Callable[[ErrorInfo], Any]) -> None:
        """
        Set default error handler.
        """
        self._default_handler = handler
        logger.debug("Set default error handler")

    def set_error_tracker(self, tracker: ErrorTracker) -> None:
        """
        Set error tracker.
        """
        self._error_tracker = tracker
        logger.debug("Set error tracker")

    def handle_error(self, exception: Exception, context: dict[str, Any] | None = None) -> Any:
        """
        Handle an error.
        """
        # Categorize the error
        category = self.categorizer.categorize(exception)

        # Determine severity
        severity = self._determine_severity(exception, category)

        # Create error info
        error_info = ErrorInfo(
            error_id=f"err_{datetime.now().timestamp()}",
            exception=exception,
            category=category,
            severity=severity,
            timestamp=datetime.now(),
            context=context or {},
            stack_trace=traceback.format_exc(),
            retryable=self.categorizer.is_retryable(exception),
            tags=self._extract_tags(exception),
        )

        # Track the error
        if self._error_tracker:
            self._error_tracker.track_error(error_info)

        # Get appropriate handler
        handler = self._handlers.get(category, self._default_handler)

        if handler:
            try:
                return handler(error_info)
            except Exception as e:
                logger.exception(f"Error handler failed: {e}")
                return self._default_error_response(error_info)
        else:
            logger.warning(f"No handler found for error category {category.value}")
            return self._default_error_response(error_info)

    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """
        Determine error severity.
        """
        # Critical errors
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.CRITICAL

        # High severity
        if category in [ErrorCategory.DATABASE, ErrorCategory.RESOURCE]:
            return ErrorSeverity.HIGH

        # Medium severity
        if category in [ErrorCategory.NETWORK, ErrorCategory.EXTERNAL_SERVICE]:
            return ErrorSeverity.MEDIUM

        # Low severity
        if category in [ErrorCategory.VALIDATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.LOW

        return ErrorSeverity.MEDIUM

    def _extract_tags(self, exception: Exception) -> set[str]:
        """
        Extract tags from exception.
        """
        tags = set()

        # Add exception type
        tags.add(f"type:{type(exception).__name__}")

        # Add error message keywords
        message = str(exception).lower()
        if "timeout" in message:
            tags.add("timeout")
        if "connection" in message:
            tags.add("connection")
        if "auth" in message:
            tags.add("auth")
        if "permission" in message:
            tags.add("permission")

        return tags

    def _default_error_response(self, error_info: ErrorInfo) -> dict[str, Any]:
        """
        Default error response when no handler is available.
        """
        return {
            "error": True,
            "error_id": error_info.error_id,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "message": str(error_info.exception),
            "retryable": error_info.retryable,
            "timestamp": error_info.timestamp.isoformat(),
        }


class ErrorTracker:
    """
    Tracks and analyzes errors.
    """

    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self._errors: deque = deque(maxlen=max_errors)
        self._category_counts: dict[ErrorCategory, int] = defaultdict(int)
        self._severity_counts: dict[ErrorSeverity, int] = defaultdict(int)
        self._hourly_counts: dict[int, int] = defaultdict(int)
        self._error_patterns: dict[str, int] = defaultdict(int)

    def track_error(self, error_info: ErrorInfo) -> None:
        """
        Track an error.
        """
        self._errors.append(error_info)

        # Update counters
        self._category_counts[error_info.category] += 1
        self._severity_counts[error_info.severity] += 1
        self._hourly_counts[error_info.timestamp.hour] += 1

        # Track error patterns
        error_key = f"{error_info.category.value}:{type(error_info.exception).__name__}"
        self._error_patterns[error_key] += 1

        logger.debug(f"Tracked error: {error_info.error_id}")

    def get_error_count(self) -> int:
        """
        Get total error count.
        """
        return len(self._errors)

    def get_errors_by_category(self, category: ErrorCategory) -> list[ErrorInfo]:
        """
        Get errors by category.
        """
        return [error for error in self._errors if error.category == category]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[ErrorInfo]:
        """
        Get errors by severity.
        """
        return [error for error in self._errors if error.severity == severity]

    def get_recent_errors(self, count: int = 10) -> list[ErrorInfo]:
        """
        Get recent errors.
        """
        return list(self._errors)[-count:]

    def get_error_rate(self, hours: int = 1) -> float:
        """
        Get error rate per hour.
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        recent_errors = [
            error for error in self._errors if error.timestamp.timestamp() > cutoff_time
        ]
        return len(recent_errors) / hours

    def get_top_error_categories(self, limit: int = 5) -> list[tuple]:
        """
        Get top error categories by count.
        """
        return sorted(self._category_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_top_error_patterns(self, limit: int = 5) -> list[tuple]:
        """
        Get top error patterns by count.
        """
        return sorted(self._error_patterns.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_error_distribution_by_hour(self) -> dict[int, int]:
        """
        Get error distribution by hour of day.
        """
        return dict(self._hourly_counts)

    def clear_errors(self) -> None:
        """
        Clear all tracked errors.
        """
        self._errors.clear()
        self._category_counts.clear()
        self._severity_counts.clear()
        self._hourly_counts.clear()
        self._error_patterns.clear()
        logger.info("Cleared all tracked errors")


@dataclass(slots=True)
class ErrorMetrics:
    """
    Metrics for error analysis.
    """

    total_errors: int = 0
    errors_by_category: dict[ErrorCategory, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_severity: dict[ErrorSeverity, int] = field(default_factory=lambda: defaultdict(int))
    error_rate_per_hour: float = 0.0
    retryable_error_rate: float = 0.0
    critical_error_rate: float = 0.0
    top_categories: list[tuple] = field(default_factory=list)
    top_patterns: list[tuple] = field(default_factory=list)
    hourly_distribution: dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            "total_errors": self.total_errors,
            "errors_by_category": {
                cat.value: count for cat, count in self.errors_by_category.items()
            },
            "errors_by_severity": {
                sev.value: count for sev, count in self.errors_by_severity.items()
            },
            "error_rate_per_hour": self.error_rate_per_hour,
            "retryable_error_rate": self.retryable_error_rate,
            "critical_error_rate": self.critical_error_rate,
            "top_categories": [(cat.value, count) for cat, count in self.top_categories],
            "top_patterns": self.top_patterns,
            "hourly_distribution": self.hourly_distribution,
        }


class ErrorAnalyzer:
    """
    Analyzes error patterns and trends.
    """

    def __init__(self, error_tracker: ErrorTracker):
        self.error_tracker = error_tracker

    def analyze_errors(self, hours: int = 24) -> ErrorMetrics:
        """
        Analyze errors and return metrics.
        """
        # Get recent errors
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        recent_errors = [
            error
            for error in self.error_tracker._errors
            if error.timestamp.timestamp() > cutoff_time
        ]

        if not recent_errors:
            return ErrorMetrics()

        # Calculate metrics
        total_errors = len(recent_errors)
        errors_by_category = defaultdict(int)
        errors_by_severity = defaultdict(int)
        retryable_count = 0
        critical_count = 0

        for error in recent_errors:
            errors_by_category[error.category] += 1
            errors_by_severity[error.severity] += 1

            if error.retryable:
                retryable_count += 1

            if error.severity == ErrorSeverity.CRITICAL:
                critical_count += 1

        # Calculate rates
        error_rate_per_hour = total_errors / hours
        retryable_error_rate = retryable_count / total_errors if total_errors > 0 else 0.0
        critical_error_rate = critical_count / total_errors if total_errors > 0 else 0.0

        # Get top categories and patterns
        top_categories = self.error_tracker.get_top_error_categories(5)
        top_patterns = self.error_tracker.get_top_error_patterns(5)
        hourly_distribution = self.error_tracker.get_error_distribution_by_hour()

        return ErrorMetrics(
            total_errors=total_errors,
            errors_by_category=dict(errors_by_category),
            errors_by_severity=dict(errors_by_severity),
            error_rate_per_hour=error_rate_per_hour,
            retryable_error_rate=retryable_error_rate,
            critical_error_rate=critical_error_rate,
            top_categories=top_categories,
            top_patterns=top_patterns,
            hourly_distribution=hourly_distribution,
        )

    def detect_error_spikes(self, threshold: float = 2.0) -> list[dict[str, Any]]:
        """
        Detect error spikes in the data.
        """
        spikes = []

        # Group errors by hour
        hourly_errors = defaultdict(list)
        for error in self.error_tracker._errors:
            hour_key = error.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_errors[hour_key].append(error)

        # Calculate average error rate
        if len(hourly_errors) < 2:
            return spikes

        error_counts = [len(errors) for errors in hourly_errors.values()]
        avg_error_rate = sum(error_counts) / len(error_counts)

        # Find spikes
        for hour, errors in hourly_errors.items():
            if len(errors) > avg_error_rate * threshold:
                spikes.append(
                    {
                        "timestamp": hour,
                        "error_count": len(errors),
                        "expected_count": avg_error_rate,
                        "spike_factor": len(errors) / avg_error_rate,
                        "top_categories": self._get_top_categories_for_errors(errors),
                    },
                )

        return sorted(spikes, key=lambda x: x["error_count"], reverse=True)

    def _get_top_categories_for_errors(self, errors: list[ErrorInfo]) -> list[tuple]:
        """
        Get top categories for a list of errors.
        """
        category_counts = defaultdict(int)
        for error in errors:
            category_counts[error.category] += 1

        return sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
