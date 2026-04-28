"""
PyDevKit - Python Development Toolkit

A comprehensive collection of utilities for Python development including:
- HTTP utilities (client, retries, headers, auth)
- Configuration management (env, YAML/JSON, validation)
- Security utilities (hashing, encryption, JWT)
- Data structures (LRU cache, priority queue, bloom filter)
- String utilities (slugify, sanitize, templating)
- Date/time utilities (parsing, formatting, timezones)
- File utilities (path handling, temp files, locks)
- Async utilities (event bus, task queue, semaphores)
- Validation utilities (email, URL, phone, custom)
- Functional utilities (compose, pipe, curry, memoize)
- Rate limiting (token bucket, sliding window)
- Structured error handling and API errors
- Concurrency utilities with Redis/in-memory locking
- Tracing and observability
- Monitoring and performance analytics
"""

from . import (
    async_utils,
    concurrency,
    config,
    correlation_id,
    data_structures,
    errors,
    fs,
    functional,
    http,
    monitoring,
    performance,
    rate_limiting,
    security,
    strings,
    tracing,
    validation,
)
from . import datetime as dt
from . import logging as logging_utils

# Concurrency
from .concurrency import (
    acquire_repo_lock,
    acquire_wd_lock,
    release_repo_lock,
    release_wd_lock,
)

# Config
from .config import ConfigManager, EnvLoader, get_config, load_env_file

# Correlation IDs
from .correlation_id import (
    clear_correlation_id,
    correlation_context,
    get_correlation_id,
    get_or_create_correlation_id,
    set_correlation_id,
)

# Data Structures
from .data_structures import BloomFilter, LRUCache, PriorityQueue

# Errors
from .errors import (
    ApiError,
    AuthenticationError,
    ConfigurationError,
    ErrorHandler,
    ErrorSeverity,
    NetworkError,
    RetryConfig,
    StructuredError,
    ValidationError,
    ZenMCPError,
    normalize_error,
)

# Functional
from .functional import compose, curry, memoize, pipe

# HTTP
from .http import RetryStrategy, exponential_backoff
from .http.httpx_client import (
    async_request_with_retries,
    create_async_client,
    create_client,
    request_with_retries,
)

# Logging
from .logging import (
    ProgressLogger,
    console,
    get_logger,
    print_banner,
    print_error,
    print_info,
    print_status,
    print_success,
    print_warning,
    quiet_mode,
    setup_logging,
)

# Performance
from .performance import (
    CompressionResult,
    MemoryMonitor,
    MemoryStats,
    PerformanceMonitor,
)

# Rate Limiting
from .rate_limiting import RateLimiter, SlidingWindowRateLimiter

# Security
from .security import PIIScanner, create_jwt, hash_password, verify_jwt, verify_password

# Strings
from .strings import Template, sanitize_html, slugify

# Validation
from .validation import Validator, is_email, is_url

__version__ = "0.1.0"
__all__ = [
    "ApiError",
    "AuthenticationError",
    "BloomFilter",
    "CompressionResult",
    "ConfigManager",
    "ConfigurationError",
    "EnvLoader",
    "ErrorHandler",
    "ErrorSeverity",
    # Key exports
    "HTTPClient",
    "LRUCache",
    "MemoryMonitor",
    "MemoryStats",
    "NetworkError",
    "PIIScanner",
    "PerformanceMonitor",
    "PriorityQueue",
    "ProgressLogger",
    "RateLimiter",
    "RetryConfig",
    "RetryStrategy",
    "SlidingWindowRateLimiter",
    "StructuredError",
    "Template",
    "ValidationError",
    "Validator",
    "ZenMCPError",
    "acquire_repo_lock",
    "acquire_wd_lock",
    "async_request_with_retries",
    "async_utils",
    "clear_correlation_id",
    "compose",
    "concurrency",
    "config",
    "console",
    "correlation_context",
    "correlation_id",
    "create_async_client",
    # httpx factories/helpers
    "create_client",
    "create_jwt",
    "curry",
    "data_structures",
    "dt",
    "errors",
    "exponential_backoff",
    "fs",
    "functional",
    "get_config",
    "get_correlation_id",
    "get_logger",
    "get_or_create_correlation_id",
    "hash_password",
    # Modules
    "http",
    "is_email",
    "is_url",
    "load_env_file",
    "logging_utils",
    "memoize",
    "monitoring",
    "normalize_error",
    "performance",
    "pipe",
    "print_banner",
    "print_error",
    "print_info",
    "print_status",
    "print_success",
    "print_warning",
    "quiet_mode",
    "rate_limiting",
    "release_repo_lock",
    "release_wd_lock",
    "request_with_retries",
    "sanitize_html",
    "security",
    "set_correlation_id",
    "setup_logging",
    "slugify",
    "strings",
    "tracing",
    "validation",
    "verify_jwt",
    "verify_password",
]
