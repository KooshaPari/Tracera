from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any
from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.event_repository import EventRepository
from tracertm.schemas.specification import (
    ADRActivityListResponse,
    ADRCreate,
    ADRResponse,
    ADRUpdate,
)
from tracertm.services.adr_service import ADRService

router = APIRouter(prefix="/adrs", tags=["ADRs"])


@router.post("/", response_model=ADRResponse, status_code=201)
async def create_adr(
    adr: ADRCreate,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ADRService(db)
    return await service.create_adr(
        project_id=adr.project_id,
        title=adr.title,
        context=adr.context,
        decision=adr.decision,
        consequences=adr.consequences,
        status=adr.status,
        decision_drivers=adr.decision_drivers,
        considered_options=adr.considered_options,
        related_requirements=adr.related_requirements,
        related_adrs=adr.related_adrs,
        tags=adr.tags,
    )


@router.get("/{adr_id}", response_model=ADRResponse)
async def get_adr(
    adr_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ADRService(db)
    adr = await service.get_adr(adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    return adr


@router.get("/{adr_id}/activities", response_model=ADRActivityListResponse)
async def get_adr_activities(
    adr_id: str,
    limit: int = Query(100, description="Max activities to return"),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    repo = EventRepository(db)
    events = await repo.get_by_entity(adr_id, limit=limit)
    activities = [
        {
            "id": str(event.id),
            "adr_id": adr_id,
            "activity_type": event.event_type,
            "from_value": event.data.get("from_value") if isinstance(event.data, dict[str, Any]) else None,
            "to_value": event.data.get("to_value") if isinstance(event.data, dict[str, Any]) else None,
            "description": event.data.get("description") if isinstance(event.data, dict[str, Any]) else None,
            "performed_by": event.data.get("performed_by") if isinstance(event.data, dict[str, Any]) else None,
            "metadata": event.data if isinstance(event.data, dict[str, Any]) else {},
            "created_at": event.created_at,
        }
        for event in events
        if event.entity_type == "adr"
    ]
    return {"activities": activities}


@router.put("/{adr_id}", response_model=ADRResponse)
async def update_adr(
    adr_id: str,
    updates: ADRUpdate,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ADRService(db)
    # Filter out None values
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    updated_adr = await service.update_adr(adr_id, **update_data)
    if not updated_adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    return updated_adr


@router.delete("/{adr_id}", status_code=204)
async def delete_adr(
    adr_id: str,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ADRService(db)
    success = await service.delete_adr(adr_id)
    if not success:
        raise HTTPException(status_code=404, detail="ADR not found")


@router.get("/", response_model=list[ADRResponse])
async def list_adrs(
    project_id: str = Query(..., description="Project ID"),
    status: str | None = Query(None, description="Filter by status"),
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ADRService(db)
    return await service.list_adrs(project_id, status)
