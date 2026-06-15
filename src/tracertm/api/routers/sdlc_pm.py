"""SDLC Project Management REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/sdlc-pm", tags=["sdlc_pm"])


@router.get("/health")
async def health():
    """Health check for the sdlc_pm pillar."""
    return {"pillar": "sdlc_pm", "status": "ok"}
