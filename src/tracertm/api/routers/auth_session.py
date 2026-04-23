"""Authentication session API endpoints for TraceRTM."""

from __future__ import annotations

import secrets
from typing import Any

from fastapi import APIRouter

from tracertm.api.handlers.auth import AuthCallbackPayload, auth_callback_endpoint

router = APIRouter(prefix="/api/v1", tags=["auth-session"])


@router.get("/csrf-token")
async def get_csrf_token() -> dict[str, Any]:
    """Get CSRF token for client-side requests."""
    token = secrets.token_urlsafe(32)
    return {
        "token": token,
        "valid": True,
    }


@router.post("/auth/callback")
async def auth_callback(payload: AuthCallbackPayload):
    """Exchange authorization code for user data and tokens (B2B flow)."""
    return await auth_callback_endpoint(payload)
