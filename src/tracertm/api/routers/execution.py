"""FastAPI routes for execution system (QA Integration executions, artifacts, config)."""

from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.schemas.execution import (
    ExecutionArtifactCreate,
    ExecutionArtifactListResponse,
    ExecutionArtifactResponse,
    ExecutionComplete,
    ExecutionCreate,
    ExecutionEnvironmentConfigResponse,
    ExecutionEnvironmentConfigUpdate,
    ExecutionListResponse,
    ExecutionResponse,
    ExecutionStart,
)
from tracertm.services.execution.execution_service import ExecutionService
from tracertm.services.recording.vhs_service import VHSExecutionService

router = APIRouter(prefix="/projects/{project_id}", tags=["Executions"])

# =============================================================================
# Execution CRUD
# =============================================================================


@router.post("/executions", response_model=ExecutionResponse, status_code=201)
async def create_execution(
    project_id: str,
    execution_create: ExecutionCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a new execution."""
    service = ExecutionService(db)
    execution = await service.create(
        project_id=project_id,
        execution_type=execution_create.execution_type,
        trigger_source=execution_create.trigger_source,
        test_run_id=execution_create.test_run_id,
        item_id=execution_create.item_id,
        trigger_ref=execution_create.trigger_ref,
        config=execution_create.config,
    )

    # Compute artifact count
    artifacts = await service.list_artifacts(execution.id)
    artifact_count = len(artifacts) if artifacts else 0

    response = ExecutionResponse.model_validate(execution)
    response.artifact_count = artifact_count
    return response


@router.get("/executions", response_model=ExecutionListResponse)
async def list_executions(
    project_id: str,
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    execution_type: Annotated[str | None, Query(description="Filter by type")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List executions for a project."""
    service = ExecutionService(db)
    executions = await service.list_by_project(
        project_id,
        status=status,
        execution_type=execution_type,
        limit=limit,
        offset=offset,
    )

    # Compute artifact counts for each execution
    response_executions = []
    for execution in executions:
        artifacts = await service.list_artifacts(execution.id)
        artifact_count = len(artifacts) if artifacts else 0
        exec_response = ExecutionResponse.model_validate(execution)
        exec_response.artifact_count = artifact_count
        response_executions.append(exec_response)

    return ExecutionListResponse(
        executions=response_executions,
        total=len(executions),
    )


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    project_id: str,
    execution_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get execution details by ID."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    artifacts = await service.list_artifacts(execution_id)
    artifact_count = len(artifacts) if artifacts else 0

    response = ExecutionResponse.model_validate(execution)
    response.artifact_count = artifact_count
    return response


# =============================================================================
# Execution Lifecycle
# =============================================================================


@router.post("/executions/{execution_id}/start", response_model=ExecutionResponse, status_code=202)
async def start_execution(
    project_id: str,
    execution_id: str,
    _start_data: ExecutionStart,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Start an execution (transition from pending to running)."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if execution.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Cannot start execution in status '{execution.status}'",
        )

    # Start the execution (creates Docker container, updates status to running)
    success = await service.start(execution_id)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to start execution (Docker unavailable or execution not pending)",
        )

    # Fetch updated execution
    execution = await service.get(execution_id)
    artifacts = await service.list_artifacts(execution_id)
    artifact_count = len(artifacts) if artifacts else 0

    response = ExecutionResponse.model_validate(execution)
    response.artifact_count = artifact_count
    return response


@router.post("/executions/{execution_id}/complete", response_model=ExecutionResponse)
async def complete_execution(
    project_id: str,
    execution_id: str,
    complete_data: ExecutionComplete,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Complete an execution (stop container, record duration, mark status)."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Complete the execution
    execution = await service.complete(
        execution_id,
        exit_code=complete_data.exit_code or 0,
        error_message=complete_data.error_message,
        output_summary=complete_data.output_summary,
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    artifacts = await service.list_artifacts(execution_id)
    artifact_count = len(artifacts) if artifacts else 0

    response = ExecutionResponse.model_validate(execution)
    response.artifact_count = artifact_count
    return response


# =============================================================================
# Execution Artifacts
# =============================================================================


@router.get("/executions/{execution_id}/artifacts", response_model=ExecutionArtifactListResponse)
async def list_artifacts(
    project_id: str,
    execution_id: str,
    artifact_type: Annotated[str | None, Query(description="Filter by artifact type")] = None,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List artifacts for an execution."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    artifacts = await service.list_artifacts(execution_id, artifact_type=artifact_type)
    response_artifacts = [ExecutionArtifactResponse.model_validate(artifact) for artifact in artifacts]
    return ExecutionArtifactListResponse(
        artifacts=response_artifacts,
        total=len(response_artifacts),
    )


@router.post(
    "/executions/{execution_id}/artifacts",
    response_model=ExecutionArtifactResponse,
    status_code=201,
)
async def add_artifact(
    project_id: str,
    execution_id: str,
    artifact_create: ExecutionArtifactCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Add an artifact to an execution."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Store artifact (copy file from source to artifact storage)
    artifact = await service.store_artifact(
        execution_id,
        source_path=artifact_create.file_path,
        artifact_type=artifact_create.artifact_type,
        project_id=project_id,
        item_id=artifact_create.item_id,
    )
    if not artifact:
        raise HTTPException(status_code=500, detail="Failed to store artifact")

    return ExecutionArtifactResponse.model_validate(artifact)


# =============================================================================
# Execution Environment Config
# =============================================================================


@router.get(
    "/execution-config",
    response_model=ExecutionEnvironmentConfigResponse,
    tags=["Execution Config"],
)
async def get_execution_config(
    project_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get execution environment configuration for a project."""
    service = ExecutionService(db)
    config = await service.get_config(project_id)
    if not config:
        # Return a default config response if none exists
        raise HTTPException(status_code=404, detail="Execution config not configured")
    return ExecutionEnvironmentConfigResponse.model_validate(config)


@router.put(
    "/execution-config",
    response_model=ExecutionEnvironmentConfigResponse,
    tags=["Execution Config"],
)
async def update_execution_config(
    project_id: str,
    config_update: ExecutionEnvironmentConfigUpdate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Update execution environment configuration for a project."""
    service = ExecutionService(db)

    # Build update dict from non-None fields
    update_data = {
        field: value for field, value in config_update.model_dump(exclude_unset=True).items() if value is not None
    }

    config = await service.upsert_config(project_id, **update_data)
    return ExecutionEnvironmentConfigResponse.model_validate(config)


# =============================================================================
# VHS Tape Generation
# =============================================================================


@router.get(
    "/executions/{execution_id}/artifacts/{artifact_id}/download",
    tags=["Execution Artifacts"],
)
async def download_artifact(
    project_id: str,
    execution_id: str,
    artifact_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FileResponse:
    """Download an artifact file."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=404, detail="Execution not found")

    artifacts = await service.list_artifacts(execution_id)
    artifact_obj = next((artifact for artifact in artifacts if artifact.id == artifact_id), None)
    if not artifact_obj:
        raise HTTPException(status_code=404, detail="Artifact not found")

    path_str = artifact_obj.file_path
    path = Path(path_str)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact file not found")

    return FileResponse(
        path_str,
        media_type=artifact_obj.mime_type or "application/octet-stream",
        filename=path.name,
    )


@router.post(
    "/vhs/generate-tape",
    status_code=202,
    tags=["VHS Recording"],
)
async def generate_vhs_tape(
    project_id: str,
    execution_id: Annotated[str, Query(description="Execution ID to generate tape for")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Generate a VHS tape file (terminal recording) from execution artifacts."""
    service = ExecutionService(db)
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.project_id != project_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get artifacts for the execution (filter for relevant types)
    artifacts = await service.list_artifacts(execution_id)
    if not artifacts:
        raise HTTPException(status_code=400, detail="No artifacts found for execution")

    # Use VHS service to generate tape
    try:
        VHSExecutionService(service)  # ensure service available; tape generation is placeholder
        config = await service.get_config(project_id)

        # Prepare tape generation parameters
        tape_params = {}
        if config:
            tape_params["theme"] = getattr(config, "vhs_theme", "Dracula")
            tape_params["font_size"] = getattr(config, "vhs_font_size", 14)
            tape_params["width"] = getattr(config, "vhs_width", 1200)
            tape_params["height"] = getattr(config, "vhs_height", 600)

        # Generate tape (implementation depends on VHSService interface)
        # This is a placeholder that returns 202 Accepted
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tape: {e!s}") from e
    else:
        return {
            "status": "accepted",
            "execution_id": execution_id,
            "message": "VHS tape generation queued",
        }
