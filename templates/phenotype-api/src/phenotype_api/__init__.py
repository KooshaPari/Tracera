"""Phenotype API utilities.

Provides FastAPI app factory with standard middleware and error handling.
"""

from .api import create_app, ErrorResponse, RequestIdMiddleware

__all__ = ["create_app", "ErrorResponse", "RequestIdMiddleware"]
