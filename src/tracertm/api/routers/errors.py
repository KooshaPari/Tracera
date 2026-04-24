"""Error aggregation router for frontend error reporting.

This module provides endpoints for:
- Collecting errors from frontend (React error boundaries, unhandled exceptions)
- Aggregating and logging errors for monitoring and debugging

Extracted as part of Phase 6 error aggregation implementation.
"""

import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router: APIRouter = APIRouter(prefix="/api", tags=["errors"])

logger = logging.getLogger(__name__)


class FrontendErrorPayload(BaseModel):
    """Frontend error report payload."""

    type: str = Field(
        default="react_error",
        description="Error type (e.g., 'react_error', 'unhandled_exception')",
    )
    message: str = Field(description="Error message")
    stack: str = Field(default="", description="JavaScript stack trace")
    componentStack: str = Field(
        default="",
        description="React component stack trace (for React errors)",
    )
    boundaryName: str = Field(
        default="Unknown",
        description="Name of the error boundary that caught the error",
    )
    timestamp: str = Field(description="ISO 8601 timestamp when error occurred")
    url: str = Field(default="", description="URL where error occurred")
    userAgent: str = Field(default="", description="Browser user agent string")


class ErrorResponse(BaseModel):
    """Response for error reporting endpoint."""

    status: str = Field(default="received", description="Status of error report")
    message: str = Field(default="Error report received", description="Response message")


@router.post("/errors", response_model=ErrorResponse, status_code=202)
async def report_frontend_error(
    payload: FrontendErrorPayload,
    request: Request,
) -> dict[str, str]:
    r"""Report an error from the frontend.

    This endpoint receives error reports from the frontend application,
    typically from React error boundaries, unhandled exceptions, or other
    client-side error handlers. Errors are logged for monitoring and debugging.

    Args:
        payload: Frontend error report containing error details and context
        request: FastAPI request object for additional context

    Returns:
        Confirmation that error report was received (202 Accepted)

    Example:
        ```javascript
        const errorReport = {
          type: 'react_error',
          message: 'Cannot read property "foo" of undefined',
          stack: 'Error: Cannot read property "foo" of undefined\n  at ...',
          componentStack: 'in MyComponent\n  in ErrorBoundary',
          boundaryName: 'MainAppBoundary',
          timestamp: '2025-02-06T10:30:45.123Z',
          url: 'https://app.example.com/projects/123',
          userAgent: 'Mozilla/5.0 ...',
        };

        fetch('/api/errors', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(errorReport),
        });
        ```
    """
    # Extract additional context from request
    client_ip = request.client.host if request.client else "unknown"

    # Log error with full context for aggregation and monitoring
    # Avoid using reserved field names in extra dict (e.g., 'message' is used by LogRecord)
    logger.error(
        "Frontend error reported: %s",
        payload.message,
        extra={
            "error_type": payload.type,
            "error_message": payload.message,
            "component_stack": payload.componentStack[:200],  # Truncate for logs
            "js_stack": payload.stack[:200],  # Truncate for logs
            "boundary_name": payload.boundaryName,
            "url": payload.url,
            "user_agent": payload.userAgent[:100],  # Truncate for logs
            "client_ip": client_ip,
        },
    )

    # Also log detailed information for detailed debugging
    logger.debug(
        "Detailed error report from %s",
        payload.boundaryName,
        extra={
            "full_error_type": payload.type,
            "full_error_message": payload.message,
            "full_component_stack": payload.componentStack,
            "full_js_stack": payload.stack,
            "full_user_agent": payload.userAgent,
            "client_ip": client_ip,
        },
    )

    # Return 202 Accepted - error is queued for processing but not immediately persisted
    return {
        "status": "received",
        "message": "Error report received and will be processed",
    }
