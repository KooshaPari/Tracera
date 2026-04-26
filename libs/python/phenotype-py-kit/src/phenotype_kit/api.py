"""FastAPI app factory with standard middleware and error handling.

Provides a factory function to create FastAPI applications with consistent
middleware stack (CORS, request ID injection, structured logging) and
error handling patterns.

Example:
    >>> from fastapi import FastAPI
    >>> from phenotype_kit import create_app
    >>>
    >>> app = create_app(
    ...     title="My Service",
    ...     version="1.0.0",
    ...     cors_origins=["http://localhost:3000"],
    ... )
"""

import uuid
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from structlog import get_logger

logger = get_logger(__name__)


class RequestIdMiddleware:
    """Middleware to inject request IDs into request context."""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> any:
        """Add request ID to request and response.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            Response with request ID header
        """
        # Get or generate request ID
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Log request
        logger.info(
            "request_received",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )

        # Call next handler
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["x-request-id"] = request_id

        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            request_id=request_id,
        )

        return response


class ErrorResponse:
    """Standard error response format."""

    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ):
        """Initialize error response.

        Args:
            error: Error type/name
            message: Human-readable error message
            status_code: HTTP status code
            details: Optional additional error details
        """
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "error": self.error,
            "message": self.message,
            "details": self.details,
        }


def create_app(
    title: str = "Phenotype Service",
    version: str = "0.1.0",
    description: str | None = None,
    cors_origins: list[str] | None = None,
    enable_request_id: bool = True,
) -> FastAPI:
    """Create a FastAPI application with standard configuration.

    Sets up CORS, request ID middleware, and error handling.

    Args:
        title: API title for OpenAPI docs
        version: API version
        description: Optional API description
        cors_origins: List of CORS origins (default: ["*"])
        enable_request_id: Whether to add request ID middleware

    Returns:
        Configured FastAPI application
    """
    # Create app
    app = FastAPI(
        title=title,
        version=version,
        description=description,
    )

    # Default CORS origins
    if cors_origins is None:
        cors_origins = ["*"]

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request ID middleware
    if enable_request_id:
        app.add_middleware(RequestIdMiddleware)

    # Add health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint.

        Returns:
            Status dict with service info
        """
        return {
            "status": "healthy",
            "service": title,
            "version": version,
        }

    # Add standard error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions with structured error response.

        Args:
            request: The incoming request
            exc: The raised exception

        Returns:
            JSON error response
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            "unhandled_exception",
            error_type=type(exc).__name__,
            error_message=str(exc),
            request_id=request_id,
            exc_info=exc,
        )

        error_response = ErrorResponse(
            error=type(exc).__name__,
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"request_id": request_id},
        )

        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict(),
        )

    return app
