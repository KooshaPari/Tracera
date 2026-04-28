"""Validation types and exceptions for pheno-integration.

This module defines the fundamental types and exceptions used throughout the integration
validation system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ValidationStatus(Enum):
    """
    Validation status.
    """

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

    def __str__(self) -> str:
        return self.value


@dataclass
class ValidationResult:
    """
    Validation result.
    """

    test_id: str
    test_name: str
    status: ValidationStatus
    start_time: datetime
    end_time: datetime | None = None
    duration: float | None = None
    error: Exception | None = None
    error_message: str | None = None
    error_traceback: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.
        """
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "error_message": self.error_message,
            "error_traceback": self.error_traceback,
            "details": self.details,
            "metrics": self.metrics,
        }


@dataclass
class ValidationConfig:
    """
    Validation configuration.
    """

    timeout: float = 300.0  # 5 minutes
    verbose: bool = False
    parallel: bool = True
    max_workers: int = 4
    retry_count: int = 3
    retry_delay: float = 1.0
    include_patterns: list[str] = field(default_factory=lambda: ["*"])
    exclude_patterns: list[str] = field(default_factory=lambda: ["test_*"])
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationTest:
    """
    Integration test definition.
    """

    name: str
    description: str
    test_function: callable
    dependencies: list[str] = field(default_factory=list)
    timeout: float | None = None
    retry_count: int = 1
    expected_result: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not hasattr(self, "test_id"):
            self.test_id = str(uuid.uuid4())


@dataclass
class PerformanceMetrics:
    """
    Performance metrics.
    """

    test_name: str
    duration: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    latency: float
    error_rate: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.
        """
        return {
            "test_name": self.test_name,
            "duration": self.duration,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "throughput": self.throughput,
            "latency": self.latency,
            "error_rate": self.error_rate,
            "metadata": self.metadata,
        }


# Exception hierarchy
class ValidationError(Exception):
    """
    Base exception for validation errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class IntegrationError(ValidationError):
    """
    Raised when integration validation fails.
    """


class PerformanceError(ValidationError):
    """
    Raised when performance validation fails.
    """


class MigrationError(ValidationError):
    """
    Raised when migration validation fails.
    """


class ConfigurationError(ValidationError):
    """
    Raised when configuration validation fails.
    """
