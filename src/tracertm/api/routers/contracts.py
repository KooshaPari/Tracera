"""Contract specification API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.event_repository import EventRepository
from tracertm.schemas.specification import (
    ContractActivityListResponse,
    ContractCreate,
    ContractRead,
    ContractUpdate,
)
from tracertm.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractRead, status_code=201)
async def create_contract(
    contract: ContractCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a new contract spec."""
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
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return a contract spec by id."""
    service = ContractService(db)
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/{contract_id}/activities", response_model=ContractActivityListResponse)
async def get_contract_activities(
    contract_id: str,
    limit: Annotated[int, Query(description="Max activities to return")] = 100,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List contract activity events."""
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
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Update contract spec fields."""
    service = ContractService(db)
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    updated_contract = await service.update_contract(contract_id, **update_data)
    if not updated_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return updated_contract


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a contract spec by id."""
    service = ContractService(db)
    success = await service.delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")


@router.get("/", response_model=list[ContractRead])
async def list_contracts(
    project_id: Annotated[str, Query(description="Project ID")],
    item_id: Annotated[str | None, Query(description="Filter by Item ID")] = None,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List contract specs for a project."""
    service = ContractService(db)
    return await service.list_contracts(project_id, item_id)
