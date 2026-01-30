from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db, auth_guard
from tracertm.schemas.specification import RequirementQualityRead
from tracertm.services.requirement_quality_service import RequirementQualityService

router = APIRouter(prefix="/quality", tags=["Quality"])

@router.post("/items/{item_id}/analyze", response_model=RequirementQualityRead)
async def analyze_quality(
    item_id: str,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = RequirementQualityService(db)
    try:
        return await service.analyze_quality(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/items/{item_id}", response_model=RequirementQualityRead)
async def get_quality(
    item_id: str,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = RequirementQualityService(db)
    quality = await service.get_quality(item_id)
    if not quality:
        raise HTTPException(status_code=404, detail="Quality analysis not found")
    return quality
