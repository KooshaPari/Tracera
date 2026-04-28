"""
Configuration API routes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from pheno.adapters.api.dependencies import (
    get_create_configuration_use_case,
    get_get_configuration_use_case,
    get_list_configurations_use_case,
    get_update_configuration_use_case,
)
from pheno.application.dtos.configuration import (
    ConfigurationDTO,
    ConfigurationFilterDTO,
    CreateConfigurationDTO,
    UpdateConfigurationDTO,
)
from pheno.application.use_cases.configuration import (
    CreateConfigurationUseCase,
    GetConfigurationUseCase,
    ListConfigurationsUseCase,
    UpdateConfigurationUseCase,
)

router = APIRouter(prefix="/config", tags=["configuration"])


@router.post("/", response_model=ConfigurationDTO, status_code=status.HTTP_201_CREATED)
async def create_configuration(
    dto: CreateConfigurationDTO,
    use_case: Annotated[CreateConfigurationUseCase, Depends(get_create_configuration_use_case)],
) -> ConfigurationDTO:
    """
    Create a new configuration.
    """
    return await use_case.execute(dto)


@router.get("/{key}", response_model=ConfigurationDTO)
async def get_configuration(
    key: str,
    use_case: Annotated[GetConfigurationUseCase, Depends(get_get_configuration_use_case)],
) -> ConfigurationDTO:
    """
    Get a configuration by key.
    """
    try:
        return await use_case.execute(key)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{key}", response_model=ConfigurationDTO)
async def update_configuration(
    key: str,
    dto: UpdateConfigurationDTO,
    use_case: Annotated[UpdateConfigurationUseCase, Depends(get_update_configuration_use_case)],
) -> ConfigurationDTO:
    """
    Update a configuration.
    """
    try:
        # Override key from path
        dto = UpdateConfigurationDTO(key=key, value=dto.value, description=dto.description)
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=list[ConfigurationDTO])
async def list_configurations(
    use_case: Annotated[ListConfigurationsUseCase, Depends(get_list_configurations_use_case)],
    limit: int = 100,
    offset: int = 0,
) -> list[ConfigurationDTO]:
    """
    List configurations with pagination.
    """
    filter_dto = ConfigurationFilterDTO(limit=limit, offset=offset)
    return await use_case.execute(filter_dto)
