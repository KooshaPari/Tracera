"""
Deployment API routes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from pheno.adapters.api.dependencies import (
    get_complete_deployment_use_case,
    get_create_deployment_use_case,
    get_deployment_statistics_use_case,
    get_fail_deployment_use_case,
    get_get_deployment_use_case,
    get_list_deployments_use_case,
    get_rollback_deployment_use_case,
    get_start_deployment_use_case,
)
from pheno.application.dtos.deployment import (
    CreateDeploymentDTO,
    DeploymentDTO,
    DeploymentFilterDTO,
    DeploymentStatisticsDTO,
)
from pheno.application.use_cases.deployment import (
    CompleteDeploymentUseCase,
    CreateDeploymentUseCase,
    FailDeploymentUseCase,
    GetDeploymentStatisticsUseCase,
    GetDeploymentUseCase,
    ListDeploymentsUseCase,
    RollbackDeploymentUseCase,
    StartDeploymentUseCase,
)
from pheno.domain.exceptions.deployment import DeploymentNotFoundError

router = APIRouter(prefix="/deployments", tags=["deployments"])


class FailDeploymentRequest(BaseModel):
    """
    Request model for failing a deployment.
    """

    reason: str


class RollbackDeploymentRequest(BaseModel):
    """
    Request model for rolling back a deployment.
    """

    reason: str


@router.post("/", response_model=DeploymentDTO, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    dto: CreateDeploymentDTO,
    use_case: Annotated[CreateDeploymentUseCase, Depends(get_create_deployment_use_case)],
) -> DeploymentDTO:
    """
    Create a new deployment.
    """
    return await use_case.execute(dto)


@router.get("/{deployment_id}", response_model=DeploymentDTO)
async def get_deployment(
    deployment_id: str,
    use_case: Annotated[GetDeploymentUseCase, Depends(get_get_deployment_use_case)],
) -> DeploymentDTO:
    """
    Get a deployment by ID.
    """
    try:
        return await use_case.execute(deployment_id)
    except DeploymentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=list[DeploymentDTO])
async def list_deployments(
    use_case: Annotated[ListDeploymentsUseCase, Depends(get_list_deployments_use_case)],
    limit: int = 100,
    offset: int = 0,
) -> list[DeploymentDTO]:
    """
    List deployments with pagination.
    """
    filter_dto = DeploymentFilterDTO(limit=limit, offset=offset)
    return await use_case.execute(filter_dto)


@router.post("/{deployment_id}/start", response_model=DeploymentDTO)
async def start_deployment(
    deployment_id: str,
    use_case: Annotated[StartDeploymentUseCase, Depends(get_start_deployment_use_case)],
) -> DeploymentDTO:
    """
    Start a deployment.
    """
    try:
        return await use_case.execute(deployment_id)
    except DeploymentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{deployment_id}/complete", response_model=DeploymentDTO)
async def complete_deployment(
    deployment_id: str,
    use_case: Annotated[CompleteDeploymentUseCase, Depends(get_complete_deployment_use_case)],
) -> DeploymentDTO:
    """
    Complete a deployment.
    """
    try:
        return await use_case.execute(deployment_id)
    except DeploymentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{deployment_id}/fail", response_model=DeploymentDTO)
async def fail_deployment(
    deployment_id: str,
    request: FailDeploymentRequest,
    use_case: Annotated[FailDeploymentUseCase, Depends(get_fail_deployment_use_case)],
) -> DeploymentDTO:
    """
    Fail a deployment.
    """
    try:
        return await use_case.execute(deployment_id, request.reason)
    except DeploymentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{deployment_id}/rollback", response_model=DeploymentDTO)
async def rollback_deployment(
    deployment_id: str,
    request: RollbackDeploymentRequest,
    use_case: Annotated[RollbackDeploymentUseCase, Depends(get_rollback_deployment_use_case)],
) -> DeploymentDTO:
    """
    Rollback a deployment.
    """
    try:
        return await use_case.execute(deployment_id, request.reason)
    except DeploymentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/stats/summary", response_model=DeploymentStatisticsDTO)
async def get_deployment_statistics(
    use_case: Annotated[
        GetDeploymentStatisticsUseCase, Depends(get_deployment_statistics_use_case),
    ],
    environment: str | None = None,
) -> DeploymentStatisticsDTO:
    """
    Get deployment statistics.
    """
    return await use_case.execute(environment)
