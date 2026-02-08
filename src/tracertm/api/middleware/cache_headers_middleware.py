"""Cache headers middleware."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


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
            The response with cache headers set.
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
