"""Request/Response logging middleware for TraceRTM API."""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses.

    Logs:
    - Request method, path, client IP
    - Response status code and processing time
    - Query parameters (sanitized)
    - User agent
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        log_request_body: bool = False,
        log_response_body: bool = False,
        skip_paths: list[str] | None = None,
    ) -> None:
        """Initialize request logging middleware.

        Args:
            app: ASGI application
            log_request_body: Whether to log request bodies (careful with sensitive data)
            log_response_body: Whether to log response bodies (careful with large payloads)
            skip_paths: List of path prefixes to skip logging (e.g., ["/health", "/metrics"])
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.skip_paths = skip_paths or ["/health", "/metrics", "/favicon.ico"]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request and log details."""
        # Skip logging for certain paths
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)

        # Extract request details
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        user_agent = request.headers.get("user-agent", "unknown")

        # Sanitize sensitive query parameters
        sanitized_params = self._sanitize_params(query_params)

        # Log request
        logger.info(
            "Request started: %s %s from %s | params=%s | user_agent=%s",
            method,
            path,
            client_ip,
            sanitized_params,
            user_agent[:100] if user_agent else "unknown",
        )

        # Optional: Log request body (be careful with sensitive data)
        if self.log_request_body and method in {"POST", "PUT", "PATCH"}:
            try:
                # Note: This consumes the request body, may need special handling
                # For production, consider using a custom body reader
                logger.debug("Request body logging enabled but not implemented for safety")
            except Exception as e:
                logger.debug("Could not log request body: %s", e)

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                "Request completed: %s %s | status=%d | duration=%.3fs",
                method,
                path,
                response.status_code,
                process_time,
            )

            # Add processing time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

        except Exception:
            # Log error
            process_time = time.time() - start_time
            logger.exception(
                "Request failed: %s %s | duration=%.3fs",
                method,
                path,
                process_time,
            )
            raise
        else:
            return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request.

        Checks X-Forwarded-For header first (for proxied requests),
        then falls back to direct client IP.
        """
        # Check for X-Forwarded-For header (from proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _sanitize_params(self, params: dict[str, str]) -> dict[str, str]:
        """Sanitize sensitive query parameters.

        Replaces values of sensitive parameters with ***REDACTED***
        """
        sensitive_keys = {
            "token",
            "api_key",
            "apikey",
            "api-key",
            "password",
            "secret",
            "auth",
            "authorization",
            "access_token",
            "refresh_token",
        }

        sanitized = {}
        for key, value in params.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value

        return sanitized


class StructuredRequestLogger:
    """Utility class for structured request logging.

    Provides methods to log request/response with structured context.
    Useful for integration with logging aggregation tools (ELK, Datadog, etc.).
    """

    def __init__(self, logger_name: str = "tracertm.api.requests") -> None:
        """Initialize structured request logger."""
        self.logger = logging.getLogger(logger_name)

    def log_request(
        self,
        request: Request,
        *,
        extra_context: dict[str, str] | None = None,
    ) -> None:
        """Log HTTP request with structured context.

        Args:
            request: FastAPI request object
            extra_context: Additional context to include in log
        """
        context = {
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown")[:100],
        }

        if extra_context:
            context.update(extra_context)

        self.logger.info("HTTP Request", extra=context)

    def log_response(
        self,
        request: Request,
        response: Response,
        duration: float,
        *,
        extra_context: dict[str, str] | None = None,
    ) -> None:
        """Log HTTP response with structured context.

        Args:
            request: FastAPI request object
            response: Response object
            duration: Request processing duration in seconds
            extra_context: Additional context to include in log
        """
        context = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": self._get_client_ip(request),
        }

        if extra_context:
            context.update(extra_context)

        # Use different log levels based on status code
        if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            self.logger.error("HTTP Response - Server Error", extra=context)
        elif response.status_code >= status.HTTP_400_BAD_REQUEST:
            self.logger.warning("HTTP Response - Client Error", extra=context)
        else:
            self.logger.info("HTTP Response - Success", extra=context)

    def log_error(
        self,
        request: Request,
        error: Exception,
        duration: float,
        *,
        extra_context: dict[str, str] | None = None,
    ) -> None:
        """Log request error with structured context.

        Args:
            request: FastAPI request object
            error: Exception that occurred
            duration: Request processing duration in seconds
            extra_context: Additional context to include in log
        """
        context = {
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error)[:200],
            "duration_ms": round(duration * 1000, 2),
            "client_ip": self._get_client_ip(request),
        }

        if extra_context:
            context.update(extra_context)

        self.logger.error("HTTP Request Failed", extra=context)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"


# Convenience function to create logging middleware
def create_logging_middleware(
    *,
    log_request_body: bool = False,
    log_response_body: bool = False,
    skip_paths: list[str] | None = None,
) -> Callable[[ASGIApp], RequestLoggingMiddleware]:
    """Create request logging middleware with custom configuration.

    Args:
        log_request_body: Whether to log request bodies
        log_response_body: Whether to log response bodies
        skip_paths: List of path prefixes to skip logging

    Returns:
        Middleware factory function
    """

    def middleware_factory(app: ASGIApp) -> RequestLoggingMiddleware:
        return RequestLoggingMiddleware(
            app,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
            skip_paths=skip_paths,
        )

    return middleware_factory
