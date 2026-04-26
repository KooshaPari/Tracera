"""Phenotype logging utilities.

Provides structured logging configuration using structlog.
"""

from .logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
