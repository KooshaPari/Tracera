"""Legacy auth refresh compatibility router for TraceRTM."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/refresh")
async def refresh_access_token_endpoint(payload: dict[str, Any]):
    """Refresh access tokens."""
    from tracertm.api.security import verify_refresh_token

    refresh_token = payload.get("refresh_token") if payload else None
    if not refresh_token or not isinstance(refresh_token, str):
        raise HTTPException(status_code=400, detail="Missing refresh_token")

    result = verify_refresh_token(refresh_token)
    if not isinstance(result, dict):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token"),
        "token_type": result.get("token_type", "bearer"),
        "expires_in": result.get("expires_in"),
    }
