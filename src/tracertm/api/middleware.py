"""Middleware for TraceRTM API."""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from tracertm.core.context import current_user_id
from tracertm.services.workos_auth_service import verify_access_token


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to set HTTP cache headers for optimal browser caching.

    - Static assets: immutable with 1-year max-age
    - API GET endpoints: private with 60-second max-age
    - API mutations (POST/PUT/DELETE): no-store
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Apply Cache-Control headers based on request path and method.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/endpoint handler.

        Returns:
            The response with appropriate cache headers.
        """
        response = await call_next(request)

        path = request.url.path

        # Static assets - immutable with long cache
        if path.startswith(("/static", "/assets")):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        # API GET endpoints - short private cache
        elif path.startswith("/api") and request.method == "GET":
            # Skip caching for auth-related endpoints
            if "/auth" in path or "/cache" in path:
                response.headers["Cache-Control"] = "no-store"
            else:
                response.headers["Cache-Control"] = "private, max-age=60"
        # API mutations - no caching
        elif path.startswith("/api") and request.method in {"POST", "PUT", "DELETE", "PATCH"}:
            response.headers["Cache-Control"] = "no-store"

        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Best-effort middleware to populate user context from a bearer token.

    This middleware does not enforce authentication; it only extracts the user
    id when a valid bearer token is present.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Parse bearer token (if any) and set the current_user_id context.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/endpoint handler.

        Returns:
            The response from the downstream handler.
        """
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(None, 1)[1].strip()

        if token:
            try:
                # We verify the token here to extract the user ID
                # We do NOT enforce requirement here (endpoints do that)
                # But we populate the context if valid
                claims = verify_access_token(token)
                user_id = claims.get("sub")
                if user_id:
                    current_user_id.set(user_id)
                    # We might want to clean up the context var after request,
                    # but contextvars are request-scoped in asyncio usually.
            except Exception as e:
                # Ignore errors in middleware, let auth_guard handle them explicitly
                logging.getLogger(__name__).debug("Optional token verification failed: %s", e, exc_info=True)

        return await call_next(request)
