"""Exception handlers for TraceRTM API.

Centralized error handling for:
- Redis service failures
- GitHub/Linear integration errors (auth, rate limits, not found)
- Unhandled exceptions

All handlers follow CLAUDE.md: fail clearly with named items, no silent degradation.
"""

import logging
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from tracertm.clients.github_client import (
    GitHubAuthError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)
from tracertm.clients.linear_client import (
    LinearAuthError,
    LinearNotFoundError,
    LinearRateLimitError,
)
from tracertm.services.cache_service import RedisUnavailableError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RedisUnavailableError)
    async def redis_unavailable_handler(_request: Request, exc: RedisUnavailableError) -> JSONResponse:
        """Required service Redis down: fail clearly with named item (CLAUDE.md)."""
        logger.error("Redis unavailable: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc)},
        )

    @app.exception_handler(GitHubAuthError)
    @app.exception_handler(LinearAuthError)
    async def integration_auth_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Integration token expired/invalid: 401 + code so frontend can show reconnect (no full logout)."""
        logger.warning("Integration auth error: %s", exc)
        return JSONResponse(
            status_code=401,
            content={
                "detail": str(exc) or "Integration token expired or invalid. Please reconnect in Settings.",
                "code": "integration_auth_required",
            },
        )

    @app.exception_handler(GitHubRateLimitError)
    async def github_rate_limit_handler(_request: Request, exc: GitHubRateLimitError) -> JSONResponse:
        """GitHub rate limit: 429 + Retry-After for loud/graceful handling."""
        now = datetime.now(UTC)
        reset = exc.reset_at.replace(tzinfo=UTC) if getattr(exc.reset_at, "tzinfo", None) is None else exc.reset_at
        delta = (reset - now).total_seconds()
        retry_after = max(1, int(delta)) if delta > 0 else 60
        logger.warning("GitHub rate limit: retry after %s s", retry_after)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "GitHub rate limit exceeded. Please try again later.",
                "code": "rate_limited",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    @app.exception_handler(LinearRateLimitError)
    async def linear_rate_limit_handler(_request: Request, _exc: LinearRateLimitError) -> JSONResponse:
        """Linear rate limit: 429 + Retry-After."""
        retry_after = 60
        logger.warning("Linear rate limit: retry after %s s", retry_after)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Linear rate limit exceeded. Please try again later.",
                "code": "rate_limited",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    @app.exception_handler(GitHubNotFoundError)
    @app.exception_handler(LinearNotFoundError)
    async def integration_not_found_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Integration resource not found: 404 + code for frontend toast."""
        logger.info("Integration not found: %s", exc)
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(exc) or "Resource not found.",
                "code": "integration_not_found",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        """Log unhandled exceptions and return a safe 500 response (no traceback leak)."""
        if isinstance(exc, HTTPException):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        logger.error("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
