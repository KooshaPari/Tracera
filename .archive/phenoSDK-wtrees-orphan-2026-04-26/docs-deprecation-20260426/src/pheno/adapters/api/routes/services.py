"""
Service API routes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from pheno.adapters.api.dependencies import (
    get_create_service_use_case,
    get_get_service_use_case,
    get_list_services_use_case,
    get_service_health_use_case,
    get_start_service_use_case,
    get_stop_service_use_case,
)
from pheno.application.dtos.service import (
    CreateServiceDTO,
    ServiceDTO,
    ServiceFilterDTO,
    ServiceHealthDTO,
)
from pheno.application.use_cases.service import (
    CreateServiceUseCase,
    GetServiceHealthUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
    StartServiceUseCase,
    StopServiceUseCase,
)
from pheno.domain.exceptions.infrastructure import (
    ServiceAlreadyExistsError,
    ServiceNotFoundError,
)

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/", response_model=ServiceDTO, status_code=status.HTTP_201_CREATED)
async def create_service(
    dto: CreateServiceDTO,
    use_case: Annotated[CreateServiceUseCase, Depends(get_create_service_use_case)],
) -> ServiceDTO:
    """
    Create a new service.
    """
    try:
        return await use_case.execute(dto)
    except ServiceAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{service_id}", response_model=ServiceDTO)
async def get_service(
    service_id: str,
    use_case: Annotated[GetServiceUseCase, Depends(get_get_service_use_case)],
) -> ServiceDTO:
    """
    Get a service by ID.
    """
    try:
        return await use_case.execute(service_id)
    except ServiceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=list[ServiceDTO])
async def list_services(
    use_case: Annotated[ListServicesUseCase, Depends(get_list_services_use_case)],
    limit: int = 100,
    offset: int = 0,
) -> list[ServiceDTO]:
    """
    List services with pagination.
    """
    filter_dto = ServiceFilterDTO(limit=limit, offset=offset)
    return await use_case.execute(filter_dto)


@router.post("/{service_id}/start", response_model=ServiceDTO)
async def start_service(
    service_id: str,
    use_case: Annotated[StartServiceUseCase, Depends(get_start_service_use_case)],
) -> ServiceDTO:
    """
    Start a service.
    """
    try:
        return await use_case.execute(service_id)
    except ServiceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{service_id}/stop", response_model=ServiceDTO)
async def stop_service(
    service_id: str,
    use_case: Annotated[StopServiceUseCase, Depends(get_stop_service_use_case)],
) -> ServiceDTO:
    """
    Stop a service.
    """
    try:
        return await use_case.execute(service_id)
    except ServiceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/health/status", response_model=ServiceHealthDTO)
async def get_service_health(
    use_case: Annotated[GetServiceHealthUseCase, Depends(get_service_health_use_case)],
) -> ServiceHealthDTO:
    """
    Get service health status.
    """
    return await use_case.execute()
