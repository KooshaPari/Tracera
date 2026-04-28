"""
Compatibility wrapper exposing correlation ID utilities at the package root.
"""

from .tracing.correlation_id import (
    CorrelationIdFilter,
    clear_correlation_id,
    correlation_context,
    generate_correlation_id,
    get_correlation_id,
    get_or_create_correlation_id,
    set_correlation_id,
    setup_correlation_logging,
)

__all__ = [
    "CorrelationIdFilter",
    "clear_correlation_id",
    "correlation_context",
    "generate_correlation_id",
    "get_correlation_id",
    "get_or_create_correlation_id",
    "set_correlation_id",
    "setup_correlation_logging",
]
