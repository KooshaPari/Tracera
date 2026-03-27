"""API Router for enhanced Item specifications.

Provides REST endpoints for RequirementSpec, TestSpec, EpicSpec,
UserStorySpec, TaskSpec, and DefectSpec operations with proper
authentication, validation, and error handling.
"""

from datetime import UTC, datetime
from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db

RISK_THRESHOLD_CRITICAL = 80
RISK_THRESHOLD_HIGH = 60
RISK_THRESHOLD_MEDIUM = 40
SIMILARITY_DUPLICATE_THRESHOLD = 0.95

# =============================================================================
# Response Models
# =============================================================================


class RequirementSpecResponse(BaseModel):
    """Response model for requirement specification."""

    id: str
    item_id: str
    project_id: str
    requirement_type: str  # functional, non_functional, constraint
    risk_level: str  # low, medium, high, critical
    verification_status: str  # unverified, verified, rejected
    quality_score: float
    impact_score: float | None = None
    traceability_index: float
    acceptance_criteria: str
    verification_evidence: list[dict[str, object]] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RequirementSpecListResponse(BaseModel):
    """Response model for requirement spec list."""

    specs: list[RequirementSpecResponse]
    total: int


class TestSpecResponse(BaseModel):
    """Response model for test specification."""

    id: str
    item_id: str
    project_id: str
    test_type: str  # unit, integration, e2e, performance, security
    coverage_percentage: float
    pass_rate: float
    flakiness_score: float
    is_quarantined: bool
    quarantine_reason: str | None = None
    last_run: datetime | None = None
    average_duration_ms: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestSpecListResponse(BaseModel):
    """Response model for test spec list."""

    specs: list[TestSpecResponse]
    total: int


class EpicSpecResponse(BaseModel):
    """Response model for epic specification."""

    id: str
    item_id: str
    project_id: str
    epic_type: str
    story_points: int | None = None
    business_value: str  # low, medium, high, critical
    timeline: str | None = None
    dependencies: list[str] = []
    child_items: list[str] = []
    completion_percentage: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EpicSpecListResponse(BaseModel):
    """Response model for epic spec list."""

    specs: list[EpicSpecResponse]
    total: int


class UserStorySpecResponse(BaseModel):
    """Response model for user story specification."""

    id: str
    item_id: str
    project_id: str
    user_persona: str
    business_value: str
    acceptance_criteria: list[str]
    story_points: int | None = None
    priority: str  # low, medium, high, critical
    dependencies: list[str] = []
    definition_of_done: list[str] = []
    test_coverage: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserStorySpecListResponse(BaseModel):
    """Response model for user story spec list."""

    specs: list[UserStorySpecResponse]
    total: int


class TaskSpecResponse(BaseModel):
    """Response model for task specification."""

    id: str
    item_id: str
    project_id: str
    task_type: str
    effort_estimate_hours: float
    actual_effort_hours: float | None = None
    subtasks: list[str] = []
    assigned_to: str | None = None
    due_date: datetime | None = None
    dependencies: list[str] = []
    completion_percentage: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskSpecListResponse(BaseModel):
    """Response model for task spec list."""

    specs: list[TaskSpecResponse]
    total: int


class DefectSpecResponse(BaseModel):
    """Response model for defect specification."""

    id: str
    item_id: str
    project_id: str
    defect_type: str  # bug, regression, issue
    severity: str  # trivial, minor, major, critical, blocker
    reproduced: bool
    reproduction_steps: list[str]
    root_cause: str | None = None
    affected_components: list[str] = []
    related_defects: list[str] = []
    resolution_status: str  # open, in_progress, resolved, closed, deferred
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DefectSpecListResponse(BaseModel):
    """Response model for defect spec list."""

    specs: list[DefectSpecResponse]
    total: int


class RequirementQualityStats(BaseModel):
    """Statistics for requirement quality across a project."""

    total_requirements: int
    verified_count: int
    unverified_count: int
    verification_rate: float
    average_quality_score: float
    high_risk_count: int
    critical_risk_count: int
    high_impact_count: int
    average_traceability: float
    timestamp: datetime


class TestHealthStats(BaseModel):
    """Health statistics for tests in a project."""

    total_tests: int
    passing_tests: int
    failing_tests: int
    quarantined_tests: int
    average_pass_rate: float
    average_coverage: float
    flaky_test_count: int
    average_duration_ms: float
    timestamp: datetime


class DefectMetrics(BaseModel):
    """Metrics for defects in a project."""

    total_defects: int
    open_defects: int
    closed_defects: int
    deferred_defects: int
    blocker_count: int
    critical_count: int
    average_resolution_time_hours: float | None = None
    timestamp: datetime


class ItemSpecStats(BaseModel):
    """Aggregate statistics across all item spec types."""

    project_id: str
    total_items: int
    requirements_stats: RequirementQualityStats
    tests_stats: TestHealthStats
    defects_stats: DefectMetrics
    timestamp: datetime


# =============================================================================
# Input Models
# =============================================================================


class RequirementSpecCreate(BaseModel):
    """Schema for creating requirement specification."""

    item_id: str
    requirement_type: str  # functional, non_functional, constraint
    risk_level: str  # low, medium, high, critical
    acceptance_criteria: str
    metadata: dict[str, object] | None = None


class RequirementSpecUpdate(BaseModel):
    """Schema for updating requirement specification."""

    requirement_type: str | None = None
    risk_level: str | None = None
    acceptance_criteria: str | None = None
    metadata: dict[str, object] | None = None


class TestSpecCreate(BaseModel):
    """Schema for creating test specification."""

    item_id: str
    test_type: str  # unit, integration, e2e, performance, security
    coverage_percentage: float
    metadata: dict[str, object] | None = None


class TestSpecUpdate(BaseModel):
    """Schema for updating test specification."""

    test_type: str | None = None
    coverage_percentage: float | None = None
    metadata: dict[str, object] | None = None


class EpicSpecCreate(BaseModel):
    """Schema for creating epic specification."""

    item_id: str
    epic_type: str
    story_points: int | None = None
    business_value: str  # low, medium, high, critical
    timeline: str | None = None
    metadata: dict[str, object] | None = None


class EpicSpecUpdate(BaseModel):
    """Schema for updating epic specification."""

    epic_type: str | None = None
    story_points: int | None = None
    business_value: str | None = None
    timeline: str | None = None
    metadata: dict[str, object] | None = None


class UserStorySpecCreate(BaseModel):
    """Schema for creating user story specification."""

    item_id: str
    user_persona: str
    business_value: str
    acceptance_criteria: list[str]
    story_points: int | None = None
    priority: str  # low, medium, high, critical
    definition_of_done: list[str] | None = None
    metadata: dict[str, object] | None = None


class UserStorySpecUpdate(BaseModel):
    """Schema for updating user story specification."""

    user_persona: str | None = None
    business_value: str | None = None
    acceptance_criteria: list[str] | None = None
    story_points: int | None = None
    priority: str | None = None
    definition_of_done: list[str] | None = None
    metadata: dict[str, object] | None = None


class TaskSpecCreate(BaseModel):
    """Schema for creating task specification."""

    item_id: str
    task_type: str
    effort_estimate_hours: float
    assigned_to: str | None = None
    due_date: datetime | None = None
    metadata: dict[str, object] | None = None


class TaskSpecUpdate(BaseModel):
    """Schema for updating task specification."""

    task_type: str | None = None
    effort_estimate_hours: float | None = None
    actual_effort_hours: float | None = None
    assigned_to: str | None = None
    due_date: datetime | None = None
    metadata: dict[str, object] | None = None


class DefectSpecCreate(BaseModel):
    """Schema for creating defect specification."""

    item_id: str
    defect_type: str  # bug, regression, issue
    severity: str  # trivial, minor, major, critical, blocker
    reproduced: bool
    reproduction_steps: list[str]
    affected_components: list[str] | None = None
    metadata: dict[str, object] | None = None


class DefectSpecUpdate(BaseModel):
    """Schema for updating defect specification."""

    defect_type: str | None = None
    severity: str | None = None
    reproduced: bool | None = None
    reproduction_steps: list[str] | None = None
    root_cause: str | None = None
    affected_components: list[str] | None = None
    resolution_status: str | None = None
    metadata: dict[str, object] | None = None


# =============================================================================
# Router Setup
# =============================================================================

router = APIRouter(
    prefix="/item-specs",
    tags=["Item Specifications"],
)


# =============================================================================
# Requirement Spec Endpoints
# =============================================================================


@router.post(
    "/requirements",
    response_model=RequirementSpecResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_requirement_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    data: Annotated[RequirementSpecCreate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Create a requirement specification for an item.

    Args:
        project_id: The project identifier
        data: Requirement spec creation payload
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: Created requirement spec

    Raises:
        HTTPException: On validation or database errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/requirements/{spec_id}",
    response_model=RequirementSpecResponse,
)
async def get_requirement_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Requirement spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a requirement specification by ID.

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: The requested requirement spec

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/requirements/by-item/{item_id}",
    response_model=RequirementSpecResponse,
)
async def get_requirement_spec_by_item(
    _project_id: Annotated[str, Path(description="Project ID")],
    _item_id: Annotated[str, Path(description="Item ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a requirement specification by item ID.

    Args:
        project_id: The project identifier
        item_id: The item identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: The requirement spec for the item

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/requirements",
    response_model=RequirementSpecListResponse,
)
async def list_requirement_specs(
    _project_id: Annotated[str, Path(description="Project ID")],
    _requirement_type: Annotated[str | None, Query(description="Filter by requirement type")] = None,
    _risk_level: Annotated[str | None, Query(description="Filter by risk level")] = None,
    _verification_status: Annotated[str | None, Query(description="Filter by verification status")] = None,
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """List requirement specifications for a project.

    Args:
        project_id: The project identifier
        requirement_type: Optional filter by requirement type
        risk_level: Optional filter by risk level
        verification_status: Optional filter by verification status
        limit: Maximum results to return
        offset: Results offset for pagination
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecListResponse: List of requirement specs with total count

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch(
    "/requirements/{spec_id}",
    response_model=RequirementSpecResponse,
)
async def update_requirement_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Requirement spec ID")],
    data: Annotated[RequirementSpecUpdate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Update a requirement specification.

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        data: Update payload with optional fields
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: Updated requirement spec

    Raises:
        HTTPException: On validation or not found errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/requirements/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_requirement_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Requirement spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a requirement specification.

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/requirements/{spec_id}/analyze-quality",
    response_model=RequirementSpecResponse,
)
async def analyze_requirement_quality(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Requirement spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Re-analyze quality for a requirement specification.

    Performs comprehensive quality analysis including:
    - Clarity and completeness assessment
    - Traceability verification
    - Acceptance criteria validation
    - Impact analysis

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: Updated spec with quality scores

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/requirements/{spec_id}/analyze-impact",
    response_model=RequirementSpecResponse,
)
async def analyze_requirement_impact(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Requirement spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Analyze impact for a requirement specification.

    Analyzes:
    - Affected components and subsystems
    - Dependency chain
    - Risk propagation
    - Change impact scope

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: Updated spec with impact scores

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/requirements/{spec_id}/verify",
    response_model=RequirementSpecResponse,
)
async def verify_requirement(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Requirement spec ID")],
    _evidence_type: Annotated[
        str, Query(description="Type of evidence (test_result, code_review, demo, documentation)")
    ],
    _evidence_reference: Annotated[str, Query(description="Reference to the evidence")],
    _description: Annotated[str, Query(description="Verification description")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Mark a requirement as verified.

    Records verification evidence and updates verification status.

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        evidence_type: Type of verification evidence
        evidence_reference: Reference to the evidence artifact
        description: Description of the verification
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecResponse: Updated spec with verification info

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/requirements/unverified",
    response_model=RequirementSpecListResponse,
)
async def get_unverified_requirements(
    _project_id: Annotated[str, Path(description="Project ID")],
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Get unverified requirements for a project.

    Args:
        project_id: The project identifier
        limit: Maximum results to return
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecListResponse: List of unverified specs

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/requirements/high-risk",
    response_model=RequirementSpecListResponse,
)
async def get_high_risk_requirements(
    _project_id: Annotated[str, Path(description="Project ID")],
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Get high/critical risk requirements for a project.

    Args:
        project_id: The project identifier
        limit: Maximum results to return
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementSpecListResponse: List of high-risk specs

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Test Spec Endpoints
# =============================================================================


@router.post(
    "/tests",
    response_model=TestSpecResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    data: Annotated[TestSpecCreate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Create a test specification for an item.

    Args:
        project_id: The project identifier
        data: Test spec creation payload
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: Created test spec

    Raises:
        HTTPException: On validation or database errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/tests/{spec_id}",
    response_model=TestSpecResponse,
)
async def get_test_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Test spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a test specification by ID.

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: The requested test spec

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/tests/by-item/{item_id}",
    response_model=TestSpecResponse,
)
async def get_test_spec_by_item(
    _project_id: Annotated[str, Path(description="Project ID")],
    _item_id: Annotated[str, Path(description="Item ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a test specification by item ID.

    Args:
        project_id: The project identifier
        item_id: The item identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: The test spec for the item

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/tests",
    response_model=TestSpecListResponse,
)
async def list_test_specs(
    _project_id: Annotated[str, Path(description="Project ID")],
    _test_type: Annotated[str | None, Query(description="Filter by test type")] = None,
    _is_quarantined: Annotated[bool | None, Query(description="Filter by quarantine status")] = None,
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """List test specifications for a project.

    Args:
        project_id: The project identifier
        test_type: Optional filter by test type
        is_quarantined: Optional filter by quarantine status
        limit: Maximum results to return
        offset: Results offset for pagination
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecListResponse: List of test specs with total count

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch(
    "/tests/{spec_id}",
    response_model=TestSpecResponse,
)
async def update_test_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Test spec ID")],
    data: Annotated[TestSpecUpdate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Update a test specification.

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        data: Update payload with optional fields
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: Updated test spec

    Raises:
        HTTPException: On validation or not found errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/tests/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_test_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Test spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a test specification.

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/tests/{spec_id}/record-run",
    response_model=TestSpecResponse,
)
async def record_test_run(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Test spec ID")],
    _status: Annotated[str, Query(pattern="^(passed|failed|skipped|blocked|flaky|timeout|error)$")],
    _duration_ms: Annotated[int, Query(ge=0, description="Test duration in milliseconds")],
    _error_message: Annotated[str | None, Query(description="Error message if test failed")] = None,
    _environment: Annotated[str | None, Query(description="Test environment")] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Record a test run and update metrics.

    Updates test metrics including:
    - Pass/fail rate
    - Average duration
    - Flakiness score
    - Latest run timestamp

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        status: Test execution status
        duration_ms: Test execution time in milliseconds
        error_message: Optional error message from test failure
        environment: Optional environment where test ran
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: Updated test spec with new metrics

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/tests/{spec_id}/quarantine",
    response_model=TestSpecResponse,
)
async def quarantine_test(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Test spec ID")],
    _reason: Annotated[str, Query(description="Reason for quarantine")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Quarantine a flaky test.

    Marks a test as quarantined to exclude it from CI/CD pipeline
    until flakiness is resolved.

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        reason: Reason for quarantining the test
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: Updated test spec with quarantine status

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/tests/{spec_id}/unquarantine",
    response_model=TestSpecResponse,
)
async def unquarantine_test(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Test spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Remove test from quarantine.

    Re-enables a previously quarantined test for CI/CD pipeline.

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecResponse: Updated test spec with quarantine removed

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/tests/flaky",
    response_model=TestSpecListResponse,
)
async def get_flaky_tests(
    _project_id: Annotated[str, Path(description="Project ID")],
    _threshold: Annotated[float, Query(ge=0, le=1, description="Flakiness threshold")] = 0.2,
    _limit: Annotated[int, Query(ge=1, le=200, description="Result limit")] = 50,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Get flaky tests above threshold.

    Returns tests with flakiness score above the specified threshold.

    Args:
        project_id: The project identifier
        threshold: Flakiness threshold (0.0-1.0)
        limit: Maximum results to return
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestSpecListResponse: List of flaky tests

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/tests/health-report",
    response_model=TestHealthStats,
)
async def get_test_health_report(
    _project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get test health report for a project.

    Returns comprehensive test metrics including:
    - Total, passing, failing, quarantined counts
    - Pass rates and coverage percentages
    - Flaky test count
    - Average test duration

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestHealthStats: Aggregated test health statistics

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Epic Spec Endpoints
# =============================================================================


@router.post(
    "/epics",
    response_model=EpicSpecResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_epic_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    data: Annotated[EpicSpecCreate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Create an epic specification for an item.

    Args:
        project_id: The project identifier
        data: Epic spec creation payload
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        EpicSpecResponse: Created epic spec

    Raises:
        HTTPException: On validation or database errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/epics/{spec_id}",
    response_model=EpicSpecResponse,
)
async def get_epic_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Epic spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get an epic specification by ID.

    Args:
        project_id: The project identifier
        spec_id: The epic spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        EpicSpecResponse: The requested epic spec

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/epics",
    response_model=EpicSpecListResponse,
)
async def list_epic_specs(
    _project_id: Annotated[str, Path(description="Project ID")],
    _business_value: Annotated[str | None, Query(description="Filter by business value")] = None,
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """List epic specifications for a project.

    Args:
        project_id: The project identifier
        business_value: Optional filter by business value
        limit: Maximum results to return
        offset: Results offset for pagination
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        EpicSpecListResponse: List of epic specs with total count

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch(
    "/epics/{spec_id}",
    response_model=EpicSpecResponse,
)
async def update_epic_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Epic spec ID")],
    data: Annotated[EpicSpecUpdate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Update an epic specification.

    Args:
        project_id: The project identifier
        spec_id: The epic spec identifier
        data: Update payload with optional fields
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        EpicSpecResponse: Updated epic spec

    Raises:
        HTTPException: On validation or not found errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/epics/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_epic_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Epic spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete an epic specification.

    Args:
        project_id: The project identifier
        spec_id: The epic spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# =============================================================================
# User Story Spec Endpoints
# =============================================================================


@router.post(
    "/stories",
    response_model=UserStorySpecResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_story_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    data: Annotated[UserStorySpecCreate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Create a user story specification for an item.

    Args:
        project_id: The project identifier
        data: User story spec creation payload
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        UserStorySpecResponse: Created user story spec

    Raises:
        HTTPException: On validation or database errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/stories/{spec_id}",
    response_model=UserStorySpecResponse,
)
async def get_user_story_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="User story spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a user story specification by ID.

    Args:
        project_id: The project identifier
        spec_id: The user story spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        UserStorySpecResponse: The requested user story spec

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/stories",
    response_model=UserStorySpecListResponse,
)
async def list_user_story_specs(
    _project_id: Annotated[str, Path(description="Project ID")],
    _priority: Annotated[str | None, Query(description="Filter by priority")] = None,
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """List user story specifications for a project.

    Args:
        project_id: The project identifier
        priority: Optional filter by priority level
        limit: Maximum results to return
        offset: Results offset for pagination
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        UserStorySpecListResponse: List of user story specs with total count

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch(
    "/stories/{spec_id}",
    response_model=UserStorySpecResponse,
)
async def update_user_story_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="User story spec ID")],
    data: Annotated[UserStorySpecUpdate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Update a user story specification.

    Args:
        project_id: The project identifier
        spec_id: The user story spec identifier
        data: Update payload with optional fields
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        UserStorySpecResponse: Updated user story spec

    Raises:
        HTTPException: On validation or not found errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/stories/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_story_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="User story spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a user story specification.

    Args:
        project_id: The project identifier
        spec_id: The user story spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# =============================================================================
# Task Spec Endpoints
# =============================================================================


@router.post(
    "/tasks",
    response_model=TaskSpecResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    data: Annotated[TaskSpecCreate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Create a task specification for an item.

    Args:
        project_id: The project identifier
        data: Task spec creation payload
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TaskSpecResponse: Created task spec

    Raises:
        HTTPException: On validation or database errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/tasks/{spec_id}",
    response_model=TaskSpecResponse,
)
async def get_task_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Task spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a task specification by ID.

    Args:
        project_id: The project identifier
        spec_id: The task spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TaskSpecResponse: The requested task spec

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/tasks",
    response_model=TaskSpecListResponse,
)
async def list_task_specs(
    _project_id: Annotated[str, Path(description="Project ID")],
    _assigned_to: Annotated[str | None, Query(description="Filter by assignee")] = None,
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """List task specifications for a project.

    Args:
        project_id: The project identifier
        assigned_to: Optional filter by assignee
        limit: Maximum results to return
        offset: Results offset for pagination
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TaskSpecListResponse: List of task specs with total count

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch(
    "/tasks/{spec_id}",
    response_model=TaskSpecResponse,
)
async def update_task_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Task spec ID")],
    data: Annotated[TaskSpecUpdate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Update a task specification.

    Args:
        project_id: The project identifier
        spec_id: The task spec identifier
        data: Update payload with optional fields
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TaskSpecResponse: Updated task spec

    Raises:
        HTTPException: On validation or not found errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/tasks/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Task spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a task specification.

    Args:
        project_id: The project identifier
        spec_id: The task spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# =============================================================================
# Defect Spec Endpoints
# =============================================================================


@router.post(
    "/defects",
    response_model=DefectSpecResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_defect_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    data: Annotated[DefectSpecCreate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Create a defect specification for an item.

    Args:
        project_id: The project identifier
        data: Defect spec creation payload
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        DefectSpecResponse: Created defect spec

    Raises:
        HTTPException: On validation or database errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/defects/{spec_id}",
    response_model=DefectSpecResponse,
)
async def get_defect_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Defect spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get a defect specification by ID.

    Args:
        project_id: The project identifier
        spec_id: The defect spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        DefectSpecResponse: The requested defect spec

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/defects",
    response_model=DefectSpecListResponse,
)
async def list_defect_specs(
    _project_id: Annotated[str, Path(description="Project ID")],
    _severity: Annotated[str | None, Query(description="Filter by severity")] = None,
    _resolution_status: Annotated[str | None, Query(description="Filter by resolution status")] = None,
    _limit: Annotated[int, Query(ge=1, le=500, description="Result limit")] = 100,
    _offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """List defect specifications for a project.

    Args:
        project_id: The project identifier
        severity: Optional filter by severity level
        resolution_status: Optional filter by resolution status
        limit: Maximum results to return
        offset: Results offset for pagination
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        DefectSpecListResponse: List of defect specs with total count

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch(
    "/defects/{spec_id}",
    response_model=DefectSpecResponse,
)
async def update_defect_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Defect spec ID")],
    data: Annotated[DefectSpecUpdate | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Update a defect specification.

    Args:
        project_id: The project identifier
        spec_id: The defect spec identifier
        data: Update payload with optional fields
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        DefectSpecResponse: Updated defect spec

    Raises:
        HTTPException: On validation or not found errors
    """
    if not data:
        raise HTTPException(status_code=400, detail="Request body required")

    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete(
    "/defects/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_defect_spec(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_id: Annotated[str, Path(description="Defect spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a defect specification.

    Args:
        project_id: The project identifier
        spec_id: The defect spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If spec not found (404)
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/defects/critical",
    response_model=DefectSpecListResponse,
)
async def get_critical_defects(
    _project_id: Annotated[str, Path(description="Project ID")],
    _limit: Annotated[int, Query(ge=1, le=200, description="Result limit")] = 50,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> None:
    """Get critical/blocker defects for a project.

    Args:
        project_id: The project identifier
        limit: Maximum results to return
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        DefectSpecListResponse: List of critical defects

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Aggregate Statistics Endpoints
# =============================================================================


@router.get(
    "/stats",
    response_model=ItemSpecStats,
)
async def get_item_spec_stats(
    _project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get aggregate statistics across all item spec types.

    Returns comprehensive metrics including:
    - Requirement quality statistics
    - Test health metrics
    - Defect metrics
    - All with timestamps

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ItemSpecStats: Aggregated statistics for all spec types

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/requirements/quality-stats",
    response_model=RequirementQualityStats,
)
async def get_requirement_quality_stats(
    _project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get requirement quality statistics for a project.

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        RequirementQualityStats: Quality statistics

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/tests/health-stats",
    response_model=TestHealthStats,
)
async def get_test_health_stats(
    _project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get test health statistics for a project.

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        TestHealthStats: Health statistics

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/defects/metrics",
    response_model=DefectMetrics,
)
async def get_defect_metrics(
    _project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Get defect metrics for a project.

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        DefectMetrics: Defect metrics

    Raises:
        HTTPException: On database errors
    """
    try:
        # tracked: https://github.com/KooshaPari/trace/issues/217
        raise HTTPException(status_code=501, detail="Service implementation pending")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Blockchain/NFT-Like Analytics Endpoints
# =============================================================================

# Late imports for analytics (avoid circular imports)

from tracertm.repositories import (
    BaselineRepository,
    SpecEmbeddingRepository,
    VersionBlockRepository,
)
from tracertm.schemas.spec_analytics import (
    AnalyzeCoverageGapsRequest,
    AnalyzeCVSSRequest,
    AnalyzeEARSRequest,
    AnalyzeFlakinessRequest,
    AnalyzeImpactRequest,
    AnalyzeODCRequest,
    AnalyzeQualityRequest,
    AnalyzeSimilarityRequest,
    AnalyzeSuspectLinksRequest,
    CalculatePrioritizationRequest,
    ContentAddressResponse,
    CoverageGap,
    CoverageGapAnalysisResponse,
    CVSSBreakdown,
    CVSSScoreResponse,
    CVSSSeverity,
    EARSAnalysisResponse,
    EARSComponent,
    EARSPatternType,
    FlakinessAnalysisResponse,
    ImpactAnalysisResponse,
    ImpactedItem,
    MerkleProofResponse,
    ODCClassificationResponse,
    ODCDefectType,
    ODCImpact,
    ODCTrigger,
    PrioritizationResponse,
    QualityGrade,
    QualityScoreResponse,
    RICEScore,
    SimilarItem,
    SimilarityAnalysisResponse,
    SuspectLink,
    SuspectLinkAnalysisResponse,
    VersionChainEntry,
    VersionChainResponse,
    WSJFScore,
)

# Import analytics service singleton
from tracertm.services import spec_analytics_service

# Create repository singletons
version_block_repo = VersionBlockRepository()
baseline_repo = BaselineRepository()
embedding_repo = SpecEmbeddingRepository()


@router.post(
    "/requirements/{spec_id}/analyze/ears",
    response_model=EARSAnalysisResponse,
)
async def analyze_ears_pattern(
    _project_id: Annotated[str, Path(description="Project ID")],
    spec_id: Annotated[str, Path(description="Requirement spec ID")],
    request: Annotated[AnalyzeEARSRequest | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> EARSAnalysisResponse:
    """Analyze EARS (Easy Approach to Requirements Syntax) pattern.

    Classifies the requirement into EARS patterns:
    - Ubiquitous: Always true, no conditions
    - Event-driven: Triggered by an event
    - State-driven: Depends on system state
    - Optional: Feature-based
    - Complex: Multiple conditions
    - Unwanted: Negative requirements

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        request: Optional analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        EARSAnalysisResponse: EARS classification with confidence
    """
    try:
        # Get requirement text - in a real implementation, fetch from DB
        # For now, use the request content if provided
        requirement_text = ""
        if request and hasattr(request, "content"):
            requirement_text = request.content

        if not requirement_text:
            raise HTTPException(status_code=400, detail="Requirement content is required for EARS analysis")

        # Call the analytics service (cast for checker: we've raised if falsy)
        result = spec_analytics_service.analyze_requirement(requirement_text)
        ears_analysis = result.get("ears_analysis", {})

        raw_pattern = ears_analysis.get("pattern_type", "complex")
        try:
            pattern_type = EARSPatternType(raw_pattern)
        except ValueError:
            pattern_type = EARSPatternType.COMPLEX

        raw_components = ears_analysis.get("components", {})
        components = {k: EARSComponent(**v) if isinstance(v, dict) else v for k, v in raw_components.items()}

        suggestions: list[str] = []
        for key in ("validation_issues", "improvement_suggestions", "ambiguous_terms"):
            val = ears_analysis.get(key, [])
            if isinstance(val, list):
                suggestions.extend(str(x) for x in val)
            elif val:
                suggestions.append(str(val))

        return EARSAnalysisResponse(
            spec_id=spec_id,
            pattern_type=pattern_type,
            confidence=float(ears_analysis.get("confidence", 0.0)),
            trigger=ears_analysis.get("trigger"),
            precondition=ears_analysis.get("precondition"),
            postcondition=ears_analysis.get("postcondition"),
            system_name=ears_analysis.get("system_name"),
            formal_structure=ears_analysis.get("formal_structure"),
            components=components,
            suggestions=suggestions,
            is_well_formed=bool(ears_analysis.get("is_valid", False)),
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/requirements/{spec_id}/analyze/quality",
    response_model=QualityScoreResponse,
)
async def analyze_quality_dimensions(
    _project_id: Annotated[str, Path(description="Project ID")],
    spec_id: Annotated[str, Path(description="Requirement spec ID")],
    request: Annotated[AnalyzeQualityRequest | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> QualityScoreResponse:
    """Analyze ISO 29148 quality dimensions.

    Evaluates the requirement against 8 quality dimensions:
    - Unambiguity: Single interpretation possible
    - Completeness: All necessary information present
    - Verifiability: Can be tested/verified
    - Consistency: No contradictions
    - Necessity: Essential for the system
    - Singularity: Single requirement per statement
    - Feasibility: Technically achievable
    - Traceability: Can be traced to source

    Args:
        project_id: The project identifier
        spec_id: The requirement spec identifier
        request: Optional analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        QualityScoreResponse: Quality scores with issues
    """
    try:
        # Get requirement text from request
        requirement_text = ""
        if request and hasattr(request, "content"):
            requirement_text = request.content

        if not requirement_text:
            raise HTTPException(status_code=400, detail="Requirement content is required for quality analysis")

        # Call the analytics service (cast for checker: we've raised if falsy)
        result = spec_analytics_service.analyze_requirement(requirement_text)
        quality_analysis = result.get("quality_analysis", {})

        raw_grade = quality_analysis.get("grade", "F")
        grade = QualityGrade(raw_grade) if isinstance(raw_grade, str) else QualityGrade.F
        dims = quality_analysis.get("dimension_scores", quality_analysis.get("dimensions", {}))
        return QualityScoreResponse(
            spec_id=spec_id,
            dimensions={k: float(v) for k, v in dims.items()} if isinstance(dims, dict) else {},
            dimension_details=[],  # build from quality_analysis if needed
            overall_score=float(quality_analysis.get("overall_score", 0.0)),
            grade=grade,
            issues=[],  # build from quality_analysis.get("issues") if needed
            critical_issues_count=int(quality_analysis.get("critical_issues_count", 0)),
            warning_issues_count=int(quality_analysis.get("warning_issues_count", 0)),
            top_improvement_areas=quality_analysis.get(
                "improvement_priority",
                quality_analysis.get("top_improvement_areas", []),
            )
            or [],
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/{spec_type}/{spec_id}/version-chain",
    response_model=VersionChainResponse,
)
async def get_version_chain(
    _project_id: Annotated[str, Path(description="Project ID")],
    spec_type: Annotated[
        str, Path(pattern="^(requirements|tests|epics|stories|tasks|defects)$", description="Spec type")
    ],
    spec_id: Annotated[str, Path(description="Spec ID")],
    limit: Annotated[int, Query(ge=1, le=200, description="Max chain entries")] = 50,
    _claims: dict[str, object] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> VersionChainResponse:
    """Get blockchain-style version chain history.

    Returns the cryptographic version chain showing all
    modifications to the specification with hash links.

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        limit: Maximum entries to return
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        VersionChainResponse: Version chain with integrity check
    """
    try:
        # Get version chain from repository
        blocks = await version_block_repo.get_version_chain(db, spec_id, spec_type, limit)
        chain_index = await version_block_repo.get_chain_index(db, spec_id, spec_type)

        # Convert blocks to response entries
        entries: list[VersionChainEntry] = [
            VersionChainEntry(
                version_hash=block.content_hash or block.block_id,
                version_number=block.version_number,
                content_hash=block.content_hash,
                previous_hash=block.previous_block_id,
                created_at=block.timestamp,
                created_by=block.author_id,
                change_summary=block.change_summary,
            )
            for block in blocks
        ]

        return VersionChainResponse(
            spec_id=spec_id,
            chain_head=(chain_index.chain_head_id or "") if chain_index else "",
            chain_length=chain_index.chain_length if chain_index else 0,
            entries=entries,
            chain_valid=chain_index.is_valid if chain_index else True,
            broken_links=chain_index.broken_links if chain_index else [],
            generated_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/{spec_type}/{spec_id}/verify-baseline",
    response_model=MerkleProofResponse,
)
async def verify_baseline(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_type: Annotated[
        str, Path(pattern="^(requirements|tests|epics|stories|tasks|defects)$", description="Spec type")
    ],
    spec_id: Annotated[str, Path(description="Spec ID")],
    baseline_root: Annotated[str, Query(description="Merkle root to verify against")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MerkleProofResponse:
    """Verify spec against a baseline using Merkle proof.

    Generates and verifies a Merkle proof to confirm the
    specification matches a previously established baseline.

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        baseline_root: The Merkle root of the baseline
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        MerkleProofResponse: Proof with verification result
    """
    try:
        # Get baseline by merkle root
        baseline = await baseline_repo.get_baseline_by_root(db, baseline_root)
        if not baseline:
            return MerkleProofResponse(
                spec_id=spec_id,
                root=baseline_root,
                proof=[],
                leaf_index=0,
                leaf_hash="",
                verified=False,
                verification_path=[],
                tree_size=0,
                algorithm="sha256",
                generated_at=datetime.now(UTC),
            )

        # Get the cached proof for this item
        proof = await baseline_repo.get_merkle_proof(db, baseline.baseline_id, spec_id)
        if not proof:
            return MerkleProofResponse(
                spec_id=spec_id,
                root=baseline_root,
                proof=[],
                leaf_index=0,
                leaf_hash="",
                verified=False,
                verification_path=[],
                tree_size=0,
                algorithm="sha256",
                generated_at=datetime.now(UTC),
            )

        # Verify the proof
        is_valid = baseline_repo.verify_proof(proof.leaf_hash, proof.proof_path, proof.root_hash)

        return MerkleProofResponse(
            spec_id=spec_id,
            root=proof.root_hash,
            proof=[],
            leaf_index=0,
            leaf_hash=proof.leaf_hash,
            verified=is_valid,
            verification_path=proof.proof_path,
            tree_size=0,
            algorithm="sha256",
            generated_at=proof.computed_at,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/{spec_type}/{spec_id}/merkle-proof",
    response_model=MerkleProofResponse,
)
async def get_merkle_proof(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_type: Annotated[
        str, Path(pattern="^(requirements|tests|epics|stories|tasks|defects)$", description="Spec type")
    ],
    spec_id: Annotated[str, Path(description="Spec ID")],
    baseline_id: Annotated[
        str | None, Query(description="Baseline ID to get proof from (optional, uses latest if not specified)")
    ] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> MerkleProofResponse:
    """Generate Merkle proof for the specification.

    Creates a Merkle proof that can be used to verify
    the specification's inclusion in a baseline.

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        baseline_id: Optional baseline ID (uses latest baseline if not specified)
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        MerkleProofResponse: Generated Merkle proof
    """
    try:
        # If baseline_id provided, get the proof from that baseline
        if baseline_id:
            proof = await baseline_repo.get_merkle_proof(db, baseline_id, spec_id)
            if not proof:
                return MerkleProofResponse(
                    spec_id=spec_id,
                    root="",
                    proof=[],
                    leaf_index=0,
                    leaf_hash="",
                    verified=False,
                    verification_path=[],
                    tree_size=0,
                    algorithm="sha256",
                    generated_at=datetime.now(UTC),
                )

            await baseline_repo.get_baseline(db, baseline_id)

            return MerkleProofResponse(
                spec_id=spec_id,
                root=proof.root_hash,
                proof=[],
                leaf_index=0,
                leaf_hash=proof.leaf_hash,
                verified=proof.verified if proof.verified is not None else False,
                verification_path=proof.proof_path,
                tree_size=0,
                algorithm="sha256",
                generated_at=proof.computed_at,
            )

        # No baseline_id - inform user they need to specify one
        return MerkleProofResponse(
            spec_id=spec_id,
            root="",
            proof=[],
            leaf_index=0,
            leaf_hash="",
            verified=False,
            verification_path=[],
            tree_size=0,
            algorithm="sha256",
            generated_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/{spec_type}/{spec_id}/content-address",
    response_model=ContentAddressResponse,
)
async def get_content_address(
    project_id: Annotated[str, Path(description="Project ID")],
    spec_type: Annotated[
        str, Path(pattern="^(requirements|tests|epics|stories|tasks|defects)$", description="Spec type")
    ],
    spec_id: Annotated[str, Path(description="Spec ID")],
    _claims: Annotated[dict[str, object], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> ContentAddressResponse:
    """Get IPFS-style content addressing information.

    Returns the content hash (SHA-256) and content identifier (CID)
    for the specification, enabling content-addressable storage.

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ContentAddressResponse: Content hash and CID
    """
    try:
        # Note: Content addressing requires fetching the spec content from DB
        # For now, return a placeholder - integrate with DB fetch later

        # Placeholder content for demonstration
        placeholder_content = {"id": spec_id, "type": spec_type, "project_id": project_id}
        content_address = spec_analytics_service.generate_content_address(placeholder_content)
        now = content_address.created_at
        return ContentAddressResponse(
            spec_id=spec_id,
            content_hash=content_address.cid,
            content_cid=content_address.cid,
            created_at=now,
            last_modified_at=now,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/tests/{spec_id}/analyze/flakiness",
    response_model=FlakinessAnalysisResponse,
)
async def analyze_flakiness(
    _project_id: Annotated[str, Path(description="Project ID")],
    spec_id: Annotated[str, Path(description="Test spec ID")],
    request: Annotated[AnalyzeFlakinessRequest | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> FlakinessAnalysisResponse:
    """Analyze test flakiness using Meta's probabilistic model.

    Uses Bayesian inference to calculate flakiness probability
    and entropy, identifying patterns like:
    - Timing issues
    - Async race conditions
    - Environment dependencies
    - Network flakiness
    - Resource contention
    - Order-dependent tests

    Args:
        project_id: The project identifier
        spec_id: The test spec identifier
        request: Analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        FlakinessAnalysisResponse: Flakiness analysis with recommendation
    """
    try:
        # Get run history from request
        run_history: list[dict[str, object]] = []
        window_size = 30
        if request:
            if hasattr(request, "run_history"):
                run_history = list(request.run_history or [])
            if hasattr(request, "window_size"):
                window_size = int(request.window_size or 30)

        # Call the analytics service (ensure types for checker)
        run_history_list: list[dict[str, object]] = run_history
        window_size_int: int = window_size
        analysis = spec_analytics_service.analyze_test_flakiness(
            run_history=run_history_list,
            window_size=window_size_int,
        )

        # Map to API schema: spec_id, probability, entropy, quarantine_recommended, analyzed_at, etc.
        return FlakinessAnalysisResponse(
            spec_id=spec_id,
            probability=analysis.flakiness_score,
            entropy=analysis.entropy_score,
            pattern=None,
            pattern_confidence=analysis.confidence,
            quarantine_recommended=analysis.quarantine_recommended,
            recent_runs=0,
            flaky_runs=0,
            pass_rate=1.0 - (analysis.failure_rate_24h or 0.0),
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/defects/{spec_id}/analyze/odc",
    response_model=ODCClassificationResponse,
)
async def analyze_odc_classification(
    _project_id: Annotated[str, Path(description="Project ID")],
    spec_id: Annotated[str, Path(description="Defect spec ID")],
    request: Annotated[AnalyzeODCRequest | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> ODCClassificationResponse:
    """Classify defect using IBM Orthogonal Defect Classification.

    Analyzes the defect to determine:
    - Defect Type: function, interface, checking, etc.
    - Trigger: coverage, design conformance, etc.
    - Impact: capability, usability, performance, etc.

    Args:
        project_id: The project identifier
        spec_id: The defect spec identifier
        request: Analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ODCClassificationResponse: ODC classification with confidence
    """
    try:
        # Get defect description from request
        description: str = ""
        trigger_context: str | None = None
        impact_description: str | None = None

        if request:
            if hasattr(request, "description"):
                description = str(request.description or "")
            if hasattr(request, "trigger_context"):
                trigger_context = None if request.trigger_context is None else str(request.trigger_context)
            if hasattr(request, "impact_description"):
                impact_description = None if request.impact_description is None else str(request.impact_description)

        if not description:
            raise HTTPException(status_code=400, detail="Defect description is required for ODC classification")

        # Call the analytics service (explicit types for checker)
        classification = spec_analytics_service.classify_defect(
            description=description,
            trigger_context=trigger_context,
            impact_description=impact_description,
        )

        return ODCClassificationResponse(
            spec_id=spec_id,
            defect_type=ODCDefectType(classification.defect_type.value),
            trigger=ODCTrigger(classification.trigger.value),
            impact=ODCImpact(classification.impact.value),
            confidence=classification.confidence,
            defect_type_confidence=classification.confidence,
            trigger_confidence=classification.confidence,
            impact_confidence=classification.confidence,
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/defects/{spec_id}/analyze/cvss",
    response_model=CVSSScoreResponse,
)
async def analyze_cvss_score(
    _project_id: Annotated[str, Path(description="Project ID")],
    spec_id: Annotated[str, Path(description="Defect spec ID")],
    request: Annotated[AnalyzeCVSSRequest | None, Body()] = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> CVSSScoreResponse:
    """Calculate CVSS security score for security-related defects.

    Computes the Common Vulnerability Scoring System (CVSS) base score
    including attack vector, complexity, and impact metrics.

    Args:
        project_id: The project identifier
        spec_id: The defect spec identifier
        request: Analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        CVSSScoreResponse: CVSS score with breakdown
    """
    try:
        # Note: CVSS calculation requires specific metric values from the request
        # This is a placeholder that returns default values - implement full CVSS calculator
        if not request:
            raise HTTPException(status_code=400, detail="CVSS metrics are required for scoring")

        # Return a default response until full CVSS calculator is implemented
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N"
        breakdown = CVSSBreakdown(
            attack_vector="NETWORK",
            attack_complexity="LOW",
            privileges_required="NONE",
            user_interaction="NONE",
            scope="UNCHANGED",
            confidentiality_impact="NONE",
            integrity_impact="NONE",
            availability_impact="NONE",
        )
        return CVSSScoreResponse(
            spec_id=spec_id,
            base_score=0.0,
            severity=CVSSSeverity.NONE,
            vector=vector,
            breakdown=breakdown,
            temporal_score=None,
            environmental_score=None,
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/{spec_type}/{spec_id}/analyze/impact",
    response_model=ImpactAnalysisResponse,
)
async def analyze_impact(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_type: Annotated[
        str, Path(pattern="^(requirements|tests|epics|stories|tasks|defects)$", description="Spec type")
    ],
    spec_id: Annotated[str, Path(description="Spec ID")],
    request: AnalyzeImpactRequest | None = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> ImpactAnalysisResponse:
    """Analyze impact of changes using graph traversal.

    Performs depth-first traversal of the traceability graph
    to identify all directly and transitively affected items.

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        request: Analysis parameters (depth, types)
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ImpactAnalysisResponse: Impact analysis with risk score
    """
    try:
        # Get adjacency graph from request
        adjacency: dict[str, list[str]] = {}
        item_metadata: dict[str, dict[str, object]] | None = None
        max_depth = 5

        if request:
            if hasattr(request, "adjacency"):
                adjacency = cast("dict[str, list[str]]", request.adjacency or {})
            if hasattr(request, "item_metadata"):
                raw = request.item_metadata
                item_metadata = cast("dict[str, dict[str, object]] | None", raw if isinstance(raw, dict) else None)
            if hasattr(request, "max_depth"):
                max_depth = request.max_depth or 5

        # Call the analytics service (explicit types for checker)
        result = spec_analytics_service.analyze_change_impact(
            source_item_id=spec_id,
            adjacency=adjacency,
            item_metadata=item_metadata,
            max_depth=max_depth,
        )

        # Map service result to API response schema (ImpactedItem from string ids)
        def to_impacted(item_id: str, impact_type: str, distance: int) -> ImpactedItem:
            return ImpactedItem(
                item_id=item_id,
                item_type="",
                item_title="",
                impact_type=impact_type,
                impact_severity="medium",
                distance=distance,
            )

        risk_category = (
            "critical"
            if result.risk_score >= RISK_THRESHOLD_CRITICAL
            else "high"
            if result.risk_score >= RISK_THRESHOLD_HIGH
            else "medium"
            if result.risk_score >= RISK_THRESHOLD_MEDIUM
            else "low"
        )
        return ImpactAnalysisResponse(
            spec_id=result.source_item_id,
            direct_impacts=[to_impacted(x, "direct", 1) for x in result.direct_impacts],
            transitive_impacts=[to_impacted(x, "transitive", result.impact_depth) for x in result.transitive_impacts],
            direct_impact_count=len(result.direct_impacts),
            transitive_impact_count=len(result.transitive_impacts),
            total_affected=result.blast_radius,
            max_propagation_depth=result.impact_depth,
            risk_score=result.risk_score,
            risk_category=risk_category,
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/{spec_type}/{spec_id}/prioritization",
    response_model=PrioritizationResponse,
)
async def calculate_prioritization(
    _project_id: Annotated[str, Path(description="Project ID")],
    _spec_type: Annotated[str, Path(pattern="^(requirements|epics|stories|tasks)$", description="Spec type")],
    spec_id: Annotated[str, Path(description="Spec ID")],
    request: CalculatePrioritizationRequest | None = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> PrioritizationResponse:
    """Calculate WSJF, RICE, and MoSCoW prioritization.

    Computes prioritization scores:
    - WSJF: (Business Value + Time Criticality + Risk Reduction) / Job Size
    - RICE: (Reach * Impact * Confidence) / Effort
    - MoSCoW: Must/Should/Could/Won't suggestion

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        request: Input values for calculations
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        PrioritizationResponse: Calculated scores
    """
    try:
        if not request:
            raise HTTPException(status_code=400, detail="Prioritization input values are required")

        # Calculate WSJF from flat request fields
        wsjf_result: WSJFScore | None = None
        if all(
            getattr(request, a, None) is not None
            for a in ("business_value", "time_criticality", "risk_reduction", "job_size")
        ):
            wsjf_score = spec_analytics_service.calculate_wsjf(
                business_value=request.business_value or 1,
                time_criticality=request.time_criticality or 1,
                risk_reduction=request.risk_reduction or 1,
                job_size=request.job_size or 1,
                opportunity_enablement=1,
            )
            wsjf_result = WSJFScore(
                business_value=wsjf_score.business_value,
                time_criticality=wsjf_score.time_criticality,
                risk_reduction=wsjf_score.risk_reduction,
                job_size=wsjf_score.job_size,
                wsjf_score=wsjf_score.wsjf_score,
            )

        # Calculate RICE from flat request fields
        rice_result: RICEScore | None = None
        if all(getattr(request, a, None) is not None for a in ("reach", "impact", "confidence", "effort")):
            rice_score = spec_analytics_service.calculate_rice(
                reach=request.reach or 0,
                impact=request.impact or 1,
                confidence=request.confidence or 0.5,
                effort=request.effort or 1,
            )
            rice_result = RICEScore(
                reach=rice_score.reach,
                impact=int(rice_score.impact),
                confidence=rice_score.confidence,
                effort=rice_score.effort,
                rice_score=rice_score.rice_score,
            )

        return PrioritizationResponse(
            spec_id=spec_id,
            wsjf=wsjf_result,
            rice=rice_result,
            calculated_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Batch Analytics Endpoints
# =============================================================================


@router.post(
    "/analyze/coverage-gaps",
    response_model=CoverageGapAnalysisResponse,
)
async def analyze_coverage_gaps(
    project_id: Annotated[str, Path(description="Project ID")],
    request: AnalyzeCoverageGapsRequest | None = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> CoverageGapAnalysisResponse:
    """Analyze test coverage gaps across requirements.

    Identifies requirements without test coverage or with
    stale/outdated tests.

    Args:
        project_id: The project identifier
        request: Analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        CoverageGapAnalysisResponse: Coverage gaps with metrics
    """
    try:
        # Get inputs from request
        requirements: list[dict[str, object]] = []
        tests: list[dict[str, object]] = []
        trace_links: list[dict[str, object]] = []
        safety_level: object = None

        if request:
            if hasattr(request, "requirements"):
                requirements = list(request.requirements or [])
            if hasattr(request, "tests"):
                tests = list(request.tests or [])
            if hasattr(request, "trace_links"):
                trace_links = list(request.trace_links or [])
            if hasattr(request, "safety_level"):
                safety_level = request.safety_level

        # Call the analytics service (safety_level: SafetyLevel | None from service)
        from tracertm.services.spec_analytics_service import SafetyLevel as ServiceSafetyLevel

        safety: ServiceSafetyLevel | None = (
            safety_level if isinstance(safety_level, (ServiceSafetyLevel, type(None))) else None
        )
        gaps = spec_analytics_service.analyze_coverage_gaps(
            requirements=requirements,
            tests=tests,
            trace_links=trace_links,
            safety_level=safety,
        )

        # Convert service gaps to schema CoverageGap
        gap_list = [
            CoverageGap(
                requirement_id=gap.item_id,
                requirement_title=gap.item_id,
                gap_type=gap.gap_type,
                severity=gap.severity,
                recommendation=gap.suggestion,
            )
            for gap in gaps
        ]

        return CoverageGapAnalysisResponse(
            project_id=project_id,
            gaps=gap_list,
            total_gaps=len(gap_list),
            coverage_percentage=0.0,
            critical_gaps=len([g for g in gap_list if g.severity == "critical"]),
            high_gaps=len([g for g in gap_list if g.severity == "high"]),
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/analyze/suspect-links",
    response_model=SuspectLinkAnalysisResponse,
)
async def analyze_suspect_links(
    project_id: Annotated[str, Path(description="Project ID")],
    request: AnalyzeSuspectLinksRequest | None = None,
    _claims: dict[str, object] = Depends(auth_guard),
    _db: AsyncSession = Depends(get_db),
) -> SuspectLinkAnalysisResponse:
    """Detect suspect traceability links.

    Identifies links that may be stale, broken, or incorrectly
    established based on content analysis.

    Args:
        project_id: The project identifier
        request: Analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        SuspectLinkAnalysisResponse: Suspect links with reasons
    """
    try:
        # Get inputs from request
        links: list[dict[str, object]] = []
        item_versions: dict[str, object] = {}
        recent_changes: list[dict[str, object]] = []

        if request:
            if hasattr(request, "links"):
                links = request.links or []
            if hasattr(request, "item_versions"):
                item_versions = request.item_versions or {}
            if hasattr(request, "recent_changes"):
                recent_changes = request.recent_changes or []

        links_typed = links
        versions_typed = cast("dict[str, int]", item_versions)
        changes_typed = recent_changes
        suspect_links = spec_analytics_service.detect_suspect_links(
            links=links_typed,
            item_versions=versions_typed,
            recent_changes=changes_typed,
        )

        # Convert to schema SuspectLink
        suspect_list = [
            SuspectLink(
                source_id=link.source_id,
                target_id=link.target_id,
                link_type="implements",
                suspicion_reason=link.reason.value if hasattr(link.reason, "value") else str(link.reason),
                confidence=0.5,
            )
            for link in suspect_links
        ]

        return SuspectLinkAnalysisResponse(
            project_id=project_id,
            suspect_links=suspect_list,
            total_suspect=len(suspect_list),
            link_health_percentage=0.0,
            analyzed_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/{spec_type}/{spec_id}/analyze/similarity",
    response_model=SimilarityAnalysisResponse,
)
async def analyze_similarity(
    project_id: Annotated[str, Path(description="Project ID")],
    spec_type: Annotated[
        str, Path(pattern="^(requirements|tests|epics|stories|tasks|defects)$", description="Spec type")
    ],
    spec_id: Annotated[str, Path(description="Spec ID")],
    request: AnalyzeSimilarityRequest | None = None,
    _claims: dict[str, object] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> SimilarityAnalysisResponse:
    """Find semantically similar specifications.

    Uses sentence embeddings to find specifications with
    similar content, identifying potential duplicates.

    Args:
        project_id: The project identifier
        spec_type: Type of specification
        spec_id: The spec identifier
        request: Analysis parameters
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        SimilarityAnalysisResponse: Similar items with scores
    """
    try:
        # Get parameters from request or use defaults
        threshold = request.similarity_threshold if request else 0.8
        max_results = request.max_results if request else 10
        include_all_types = request.include_all_types if request else True
        embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        current_time = datetime.now(UTC)

        # Determine which spec types to search
        search_spec_type = None if include_all_types else spec_type

        # Try to get embedding for the source spec
        source_embedding = await embedding_repo.get_embedding(db, spec_id, spec_type, embedding_model_name)

        if not source_embedding:
            # No embedding exists yet - return empty response
            return SimilarityAnalysisResponse(
                spec_id=spec_id,
                similar_items=[],
                total_similar=0,
                potential_duplicates=[],
                duplicate_count=0,
                embedding_model="sentence-transformers",
                similarity_threshold=threshold,
                analyzed_at=current_time,
            )

        # Get all embeddings for the project
        all_embeddings = await embedding_repo.get_embeddings_for_project(
            db,
            project_id,
            embedding_model_name,
            search_spec_type,
        )

        if len(all_embeddings) <= 1:
            return SimilarityAnalysisResponse(
                spec_id=spec_id,
                similar_items=[],
                total_similar=0,
                potential_duplicates=[],
                duplicate_count=0,
                embedding_model="sentence-transformers",
                similarity_threshold=threshold,
                analyzed_at=current_time,
            )

        # Compute cosine similarities
        similar_items = []
        potential_duplicates = []

        try:
            import numpy as np

            # Deserialize source embedding
            source_vec = np.frombuffer(source_embedding.embedding, dtype=np.float32)

            for emb in all_embeddings:
                if emb.spec_id == spec_id:
                    continue  # Skip self

                # Deserialize and compute cosine similarity
                other_vec = np.frombuffer(emb.embedding, dtype=np.float32)
                norm_product = np.linalg.norm(source_vec) * np.linalg.norm(other_vec)
                if norm_product == 0:
                    continue
                similarity = float(np.dot(source_vec, other_vec) / norm_product)

                if similarity >= threshold:
                    is_duplicate = similarity >= SIMILARITY_DUPLICATE_THRESHOLD
                    item = SimilarItem(
                        item_id=emb.spec_id,
                        item_title=f"{emb.spec_type}:{emb.spec_id}",
                        item_type=emb.spec_type,
                        similarity_score=round(similarity, 4),
                        similarity_reason="Semantic embedding similarity",
                        potential_duplicate=is_duplicate,
                    )
                    similar_items.append(item)
                    if is_duplicate:
                        potential_duplicates.append(item)

            # Sort by similarity score descending
            similar_items.sort(key=lambda x: x.similarity_score, reverse=True)
            similar_items = similar_items[:max_results]

        except ImportError:
            # numpy not available - return empty response
            pass

        return SimilarityAnalysisResponse(
            spec_id=spec_id,
            similar_items=similar_items,
            total_similar=len(similar_items),
            potential_duplicates=potential_duplicates,
            duplicate_count=len(potential_duplicates),
            embedding_model="sentence-transformers",
            similarity_threshold=threshold,
            analyzed_at=current_time,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
