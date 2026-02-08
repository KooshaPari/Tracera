"""Authentication context middleware."""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from tracertm.core.context import current_user_id
from tracertm.services.workos_auth_service import verify_access_token


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Populate auth context when a bearer token is present."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Set current_user_id from bearer token when available.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/endpoint handler.

        Returns:
            Downstream response.
        """
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(None, 1)[1].strip()

        if token:
            try:
                claims = verify_access_token(token)
                user_id = claims.get("sub")
                if user_id:
                    current_user_id.set(user_id)
            except Exception as exc:
                logging.getLogger(__name__).debug("Optional token verification failed: %s", exc, exc_info=True)

        return await call_next(request)
