"""Phenotype Python Kit - Shared utilities for Phenotype projects.

Provides base configurations, logging, testing utilities, and FastAPI app factory
for consistent initialization across Phenotype services and tools.

Modules:
    config: BaseSettings factory with environment variable loading
    logging: Structured JSON logging setup with structlog
    testing: Shared pytest fixtures and test utilities
    api: FastAPI app factory with standard middleware and error handling
"""

from phenotype_kit.config import BaseConfig, get_settings
from phenotype_kit.logging import configure_logging, get_logger
from phenotype_kit.api import create_app

__all__ = [
    "BaseConfig",
    "get_settings",
    "configure_logging",
    "get_logger",
    "create_app",
]

__version__ = "0.1.0"
