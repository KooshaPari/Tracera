"""Quality analysis API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.schemas.specification import RequirementQualityRead
from tracertm.services.requirement_quality_service import RequirementQualityService

router: APIRouter = APIRouter(prefix="/quality", tags=["Quality"])


@router.post("/items/{item_id}/analyze", response_model=RequirementQualityRead)
async def analyze_quality(
    item_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Run requirement quality analysis for an item."""
    service = RequirementQualityService(db)
    try:
        return await service.analyze_quality(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/items/{item_id}", response_model=RequirementQualityRead)
async def get_quality(
    item_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return the latest quality analysis for an item.

    Functional Requirements:
    - FR-APP-002

    User Stories:
    - US-ITEM-002

    Epics:
    - EPIC-003
    """
    service = RequirementQualityService(db)
    quality = await service.get_quality(item_id)
    if not quality:
        raise HTTPException(status_code=404, detail="Quality analysis not found")
    return quality
