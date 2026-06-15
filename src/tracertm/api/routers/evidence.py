"""Evidence Management REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/health")
async def health():
    """Health check for the evidence pillar."""
    return {"pillar": "evidence", "status": "ok"}
