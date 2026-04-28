"""Integrations for pheno-logging with external logging libraries.

This module provides adapters and integrations for popular logging libraries:
- structlog: Structured logging with context
- stdlib: Python standard library logging
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import-time helpers
    from .morph import (
        configure_morph_logging,
        get_morph_logger,
        get_pheno_structured_logger,
        morph_log_context,
    )
    from .structlog_adapter import (
        StructlogAdapter,
        configure_structlog_for_pheno,
        get_structlog_logger,
    )

__all__ = [
    "StructlogAdapter",
    "configure_morph_logging",
    "configure_structlog_for_pheno",
    "get_morph_logger",
    "get_pheno_structured_logger",
    "get_structlog_logger",
    "morph_log_context",
]


def __getattr__(name: str):
    """
    Lazy import for integrations.
    """
    if name in ("StructlogAdapter", "configure_structlog_for_pheno", "get_structlog_logger"):
        from .structlog_adapter import (  # type: ignore import-not-found
            StructlogAdapter,
            configure_structlog_for_pheno,
            get_structlog_logger,
        )

        return {
            "StructlogAdapter": StructlogAdapter,
            "configure_structlog_for_pheno": configure_structlog_for_pheno,
            "get_structlog_logger": get_structlog_logger,
        }[name]

    if name in (
        "configure_morph_logging",
        "get_morph_logger",
        "morph_log_context",
        "get_pheno_structured_logger",
    ):
        from .morph import (  # type: ignore import-not-found
            configure_morph_logging,
            get_morph_logger,
            get_pheno_structured_logger,
            morph_log_context,
        )

        return {
            "configure_morph_logging": configure_morph_logging,
            "get_morph_logger": get_morph_logger,
            "morph_log_context": morph_log_context,
            "get_pheno_structured_logger": get_pheno_structured_logger,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
