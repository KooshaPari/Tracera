"""Organizational Intelligence REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/org-intel", tags=["org_intel"])


@router.get("/health")
async def health():
    """Health check for the org_intel pillar."""
    return {"pillar": "org_intel", "status": "ok"}
