"""API authn/authz middleware.

Centralized request-time checks for auth headers and optional scope requirements.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi import HTTPException, status

from tracertm.api.deps import auth_guard, extract_scopes


PUBLIC_PREFIXES = (
    "/health",
    "/healthz",
    "/ready",
    "/readyz",
    "/docs",
    "/redoc",
    "/openapi.json",
)

SCOPE_RULES_BY_METHOD: dict[str, set[str]] = {
    "GET": {"tracera:read"},
    "HEAD": {"tracera:read"},
    "POST": {"tracera:write"},
    "PUT": {"tracera:write"},
    "PATCH": {"tracera:write"},
    "DELETE": {"tracera:delete", "tracera:write"},
}

SCOPE_RULES_BY_PATH_PREFIX: dict[str, set[str]] = {
    "/api/v1/traceability/": {"tracera:traceability"},
    "/api/v1/sdlc-pm/": {"tracera:sdlc"},
    "/api/v1/evidence/": {"tracera:evidence"},
    "/api/v1/org-intel/": {"tracera:org"},
    "/api/v1/impact/": {"tracera:impact"},
    "/api/v1/ingest/": {"tracera:ingest"},
    "/api/v1/items/": {"tracera:items"},
    "/api/v1/auth/": {"tracera:auth"},
}

_MAX_PATH_BYTES = 2048
_MAX_QUERY_BYTES = 2048
_MAX_BODY_BYTES = 1_048_576


class ApiAuthzMiddleware(BaseHTTPMiddleware):
    """Enforce API authn/authz rules before endpoint handlers run."""

    def _is_public(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES)

    def _validate_request_shape(self, request: Request) -> HTTPException | None:
        path = request.url.path
        query = request.url.query or ""

        if len(path) > _MAX_PATH_BYTES:
            return HTTPException(
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                detail="Request path too long",
            )

        if len(query) > _MAX_QUERY_BYTES:
            return HTTPException(
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                detail="Query string too long",
            )

        for idx, char in enumerate((path + "?" + query)):
            if ord(char) < 32:
                return HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Control character in request target at position {idx}",
                )

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > _MAX_BODY_BYTES:
                    return HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Request body exceeds hard size limit",
                    )
            except ValueError:
                return HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Content-Length header value",
                )

        return None

    def _required_scopes(self, path: str, method: str) -> set[str]:
        required = set(SCOPE_RULES_BY_METHOD.get(method.upper(), set()))
        for prefix, scopes in SCOPE_RULES_BY_PATH_PREFIX.items():
            if path.startswith(prefix):
                required.update(scopes)
        return required

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()

        if self._is_public(path):
            return await call_next(request)

        shape_error = self._validate_request_shape(request)
        if shape_error:
            return JSONResponse(
                status_code=shape_error.status_code,
                content={"detail": shape_error.detail},
            )

        # All non-public API calls are currently subject to token checks.
        try:
            claims = await auth_guard(authorization=request.headers.get("Authorization"))
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        request.state.claims = claims

        required_scopes = self._required_scopes(path, method)
        if not required_scopes:
            return await call_next(request)

        token_scopes = extract_scopes(claims)
        if not token_scopes:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Token scope missing for protected route"},
            )

        if not token_scopes.intersection(required_scopes):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Token scope insufficient for this route"},
            )

        return await call_next(request)
