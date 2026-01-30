from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db, auth_guard
from tracertm.schemas.specification import (
    ContractCreate,
    ContractRead,
    ContractUpdate,
    ContractActivityListResponse,
)
from tracertm.services.contract_service import ContractService
from tracertm.repositories.event_repository import EventRepository

router = APIRouter(prefix="/contracts", tags=["Contracts"])

@router.post("/", response_model=ContractRead, status_code=201)
async def create_contract(
    contract: ContractCreate,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ContractService(db)
    return await service.create_contract(
        project_id=contract.project_id,
        item_id=contract.item_id,
        title=contract.title,
        contract_type=contract.contract_type,
        status=contract.status,
        preconditions=contract.preconditions,
        postconditions=contract.postconditions,
        invariants=contract.invariants,
        tags=contract.tags,
    )

@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(
    contract_id: str,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ContractService(db)
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/{contract_id}/activities", response_model=ContractActivityListResponse)
async def get_contract_activities(
    contract_id: str,
    limit: int = Query(100, description="Max activities to return"),
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    repo = EventRepository(db)
    events = await repo.get_by_entity(contract_id, limit=limit)
    activities = [
        {
            "id": str(event.id),
            "contract_id": contract_id,
            "activity_type": event.event_type,
            "from_value": event.data.get("from_value") if isinstance(event.data, dict) else None,
            "to_value": event.data.get("to_value") if isinstance(event.data, dict) else None,
            "description": event.data.get("description") if isinstance(event.data, dict) else None,
            "performed_by": event.data.get("performed_by") if isinstance(event.data, dict) else None,
            "metadata": event.data if isinstance(event.data, dict) else {},
            "created_at": event.created_at,
        }
        for event in events
        if event.entity_type == "contract"
    ]
    return {"activities": activities}

@router.put("/{contract_id}", response_model=ContractRead)
async def update_contract(
    contract_id: str,
    updates: ContractUpdate,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ContractService(db)
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    updated_contract = await service.update_contract(contract_id, **update_data)
    if not updated_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return updated_contract

@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: str,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ContractService(db)
    success = await service.delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return None

@router.get("/", response_model=List[ContractRead])
async def list_contracts(
    project_id: str = Query(..., description="Project ID"),
    item_id: Optional[str] = Query(None, description="Filter by Item ID"),
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    service = ContractService(db)
    return await service.list_contracts(project_id, item_id)
