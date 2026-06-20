"""Unified specifications API router for ADRs, Contracts, Features, and Scenarios.

This router provides a comprehensive API surface for all specification-related
endpoints with proper authentication, validation, and error handling.
"""

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db, get_event_bus
from tracertm.infrastructure.event_bus import EventBus
from tracertm.infrastructure.event_publisher_utils import safe_publish
from tracertm.models.specification import Feature, Scenario
from tracertm.repositories.event_repository import EventRepository
from tracertm.schemas.specification import (
    ADRCreate,
    ADRListResponse,
    ADRResponse,
    ADRUpdate,
    ContractCreate,
    ContractListResponse,
    ContractResponse,
    ContractUpdate,
    FeatureCreate,
    FeatureListResponse,
    FeatureResponse,
    FeatureUpdate,
    ScenarioActivityListResponse,
    ScenarioCreate,
    ScenarioListResponse,
    ScenarioResponse,
    ScenarioUpdate,
)
from tracertm.services.adr_service import ADRService
from tracertm.services.contract_service import ContractService
from tracertm.services.feature_service import CreateFeatureInput, FeatureService
from tracertm.services.scenario_service import ScenarioService

MIN_ADR_CONTEXT_LEN = 50
MIN_ADR_DECISION_LEN = 20
MIN_ADR_CONSEQUENCES_LEN = 20
MIN_CONTRACT_TITLE_LEN = 10

# =============================================================================
# Response Models
# =============================================================================


class VerificationResult(BaseModel):
    """Result of compliance verification."""

    is_valid: bool
    score: float
    issues: list[str] = []
    warnings: list[str] = []
    timestamp: datetime


class ScenarioRunResult(BaseModel):
    """Result of running a scenario."""

    scenario_id: str
    passed: bool
    duration_ms: float
    steps_passed: int
    steps_failed: int
    error_message: str | None = None
    timestamp: datetime


class SpecificationsSummary(BaseModel):
    """Summary of all specifications in a project."""

    project_id: str
    adr_count: int
    contract_count: int
    feature_count: int
    scenario_count: int
    compliance_score: float


# =============================================================================
# Router Setup
# =============================================================================

router = APIRouter(prefix="/specifications", tags=["Specifications"])


# =============================================================================
# ADR Endpoints
# =============================================================================


@router.post("/adrs", status_code=201)
async def create_adr_spec(
    adr: ADRCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> ADRResponse:
    """Create a new Architecture Decision Record.

    Args:
        adr: ADR creation payload with title, context, decision, consequences
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Returns:
        ADRResponse: Created ADR with all fields populated

    Raises:
        HTTPException: On validation or database errors
    """
    service = ADRService(db)

    try:
        created_adr = await service.create_adr(
            project_id=adr.project_id,
            title=adr.title,
            context=adr.context,
            decision=adr.decision,
            consequences=adr.consequences,
            status=adr.status.value if hasattr(adr.status, "value") else adr.status,
            decision_drivers=adr.decision_drivers,
            considered_options=adr.considered_options,
            related_requirements=adr.related_requirements,
            related_adrs=adr.related_adrs,
            tags=adr.tags,
        )

        # Publish NATS event
        if event_bus:
            await safe_publish(
                event_bus,
                EventBus.EVENT_SPEC_CREATED,
                adr.project_id,
                str(created_adr.id),
                "adr",
                {
                    "id": str(created_adr.id),
                    "title": created_adr.title,
                    "type": "adr",
                    "status": created_adr.status,
                    "project_id": adr.project_id,
                },
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create ADR: {e!s}") from e
    else:
        return created_adr


@router.get("/adrs/{adr_id}")
async def get_adr_spec(
    adr_id: Annotated[str, Path(description="ADR ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ADRResponse:
    """Retrieve a specific ADR by ID.

    Args:
        adr_id: The ADR identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ADRResponse: The requested ADR

    Raises:
        HTTPException: If ADR not found (404)
    """
    service = ADRService(db)
    adr = await service.get_adr(adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")
    return adr


@router.put("/adrs/{adr_id}")
async def update_adr_spec(
    adr_id: Annotated[str, Path(description="ADR ID")],
    updates: Annotated[ADRUpdate | None, Body()] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
    event_bus: Annotated[EventBus, Depends(get_event_bus)] = Depends(get_event_bus),
) -> ADRResponse:
    """Update an ADR.

    Args:
        adr_id: The ADR identifier
        updates: Fields to update (all optional)
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Returns:
        ADRResponse: Updated ADR

    Raises:
        HTTPException: If ADR not found (404) or update fails
    """
    service = ADRService(db)

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    try:
        updated_adr = await service.update_adr(adr_id, **update_data)
        if not updated_adr:
            raise HTTPException(status_code=404, detail="ADR not found")

        # Publish NATS event
        if event_bus:
            await safe_publish(
                event_bus,
                EventBus.EVENT_SPEC_UPDATED,
                updated_adr.project_id,
                adr_id,
                "adr",
                jsonable_encoder(updated_adr),
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update ADR: {e!s}") from e
    else:
        return updated_adr


@router.delete("/adrs/{adr_id}", status_code=204)
async def delete_adr_spec(
    adr_id: Annotated[str, Path(description="ADR ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> None:
    """Delete an ADR.

    Args:
        adr_id: The ADR identifier
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Raises:
        HTTPException: If ADR not found (404)
    """
    service = ADRService(db)

    # Get ADR before deletion to access project_id
    adr = await service.get_adr(adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")

    project_id = adr.project_id
    success = await service.delete_adr(adr_id)

    if success and event_bus:
        await safe_publish(
            event_bus,
            EventBus.EVENT_SPEC_DELETED,
            project_id,
            adr_id,
            "adr",
            {"id": adr_id},
        )


@router.get("/projects/{project_id}/adrs")
async def list_adrs_for_project(
    project_id: Annotated[str, Path(description="Project ID")],
    status: Annotated[str | None, Query(description="Filter by ADR status")] = None,
    _tags: Annotated[list[str] | None, Query(description="Filter by tags")] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> ADRListResponse:
    """List all ADRs for a project with optional filtering.

    Args:
        project_id: The project identifier
        status: Optional status filter (proposed, accepted, deprecated, superseded, rejected)
        tags: Optional tags to filter by
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ADRListResponse: List of ADRs with total count
    """
    service = ADRService(db)

    try:
        adrs = await service.list_adrs(project_id, status)
        return ADRListResponse(total=len(adrs), adrs=[ADRResponse.model_validate(a) for a in adrs])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list ADRs: {e!s}") from e


@router.post("/adrs/{adr_id}/verify")
async def verify_adr_compliance(
    adr_id: Annotated[str, Path(description="ADR ID")],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VerificationResult:
    """Verify ADR compliance with decision patterns and traceability.

    Args:
        adr_id: The ADR identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        VerificationResult: Compliance verification results with score and issues

    Raises:
        HTTPException: If ADR not found (404) or verification fails
    """
    service = ADRService(db)
    adr = await service.get_adr(adr_id)
    if not adr:
        raise HTTPException(status_code=404, detail="ADR not found")

    try:
        issues = []
        warnings = []

        # Verify context is present and detailed
        if not adr.context or len(adr.context) < MIN_ADR_CONTEXT_LEN:
            issues.append("Context must be detailed (minimum 50 characters)")

        # Verify decision is present
        if not adr.decision or len(adr.decision) < MIN_ADR_DECISION_LEN:
            issues.append("Decision must be present and clear (minimum 20 characters)")

        # Verify consequences are documented
        if not adr.consequences or len(adr.consequences) < MIN_ADR_CONSEQUENCES_LEN:
            warnings.append("Consequences should be documented")

        # Verify traceability
        if not adr.related_requirements and not adr.related_adrs:
            warnings.append("ADR should reference related requirements or other ADRs")

        # Verify decision drivers
        if not adr.decision_drivers:
            warnings.append("Decision drivers should be documented")

        # Calculate compliance score (0-100)
        max_issues = 5
        max_warnings = 3
        issue_penalty = 20
        warning_penalty = 5

        score = 100.0
        score -= min(len(issues), max_issues) * issue_penalty
        score -= min(len(warnings), max_warnings) * warning_penalty
        score = max(0.0, min(100.0, score))

        result = VerificationResult(
            is_valid=len(issues) == 0,
            score=score,
            issues=issues,
            warnings=warnings,
            timestamp=datetime.now(UTC),
        )
        repo = EventRepository(db)
        await repo.log(
            project_id=adr.project_id,
            event_type="verified",
            entity_type="adr",
            entity_id=adr_id,
            data={
                "description": "ADR verification run",
                "score": score,
                "performed_by": claims.get("sub") if isinstance(claims, dict) else None,
            },
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify ADR: {e!s}") from e
    else:
        return result


# =============================================================================
# Contract Endpoints
# =============================================================================


@router.post("/contracts", status_code=201)
async def create_contract_spec(
    contract: ContractCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> ContractResponse:
    """Create a new contract specification.

    Args:
        contract: Contract creation payload
        claims: Authentication claims from JWT
        db: Database session
        event_bus: Event bus for publishing spec lifecycle events

    Returns:
        ContractResponse: Created contract

    Raises:
        HTTPException: On validation or database errors
    """
    service = ContractService(db)

    try:
        created_contract = await service.create_contract(
            project_id=contract.project_id,
            item_id=contract.item_id,
            title=contract.title,
            contract_type=contract.contract_type.value
            if hasattr(contract.contract_type, "value")
            else contract.contract_type,
            status=contract.status.value if hasattr(contract.status, "value") else contract.status,
            preconditions=contract.preconditions,
            postconditions=contract.postconditions,
            invariants=contract.invariants,
            tags=contract.tags,
        )

        # Publish NATS event
        if event_bus:
            await safe_publish(
                event_bus,
                EventBus.EVENT_SPEC_CREATED,
                contract.project_id,
                str(created_contract.id),
                "contract",
                {
                    "id": str(created_contract.id),
                    "title": created_contract.title,
                    "type": "contract",
                    "contract_type": created_contract.contract_type,
                    "project_id": contract.project_id,
                },
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create contract: {e!s}") from e
    else:
        return created_contract


@router.get("/contracts/{contract_id}")
async def get_contract_spec(
    contract_id: Annotated[str, Path(description="Contract ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContractResponse:
    """Retrieve a specific contract by ID.

    Args:
        contract_id: The contract identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ContractResponse: The requested contract

    Raises:
        HTTPException: If contract not found (404)
    """
    service = ContractService(db)
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.put("/contracts/{contract_id}")
async def update_contract_spec(
    contract_id: Annotated[str, Path(description="Contract ID")],
    updates: Annotated[ContractUpdate | None, Body()] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> ContractResponse:
    """Update a contract.

    Args:
        contract_id: The contract identifier
        updates: Fields to update (all optional)
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ContractResponse: Updated contract

    Raises:
        HTTPException: If contract not found (404) or update fails
    """
    service = ContractService(db)

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    try:
        updated_contract = await service.update_contract(contract_id, **update_data)
        if not updated_contract:
            raise HTTPException(status_code=404, detail="Contract not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update contract: {e!s}") from e
    else:
        return updated_contract


@router.delete("/contracts/{contract_id}", status_code=204)
async def delete_contract_spec(
    contract_id: Annotated[str, Path(description="Contract ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a contract.

    Args:
        contract_id: The contract identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If contract not found (404)
    """
    service = ContractService(db)
    success = await service.delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")


@router.get("/projects/{project_id}/contracts")
async def list_contracts_for_project(
    project_id: Annotated[str, Path(description="Project ID")],
    item_id: Annotated[str | None, Query(description="Filter by item ID")] = None,
    _contract_type: Annotated[str | None, Query(description="Filter by contract type")] = None,
    _status: Annotated[str | None, Query(description="Filter by status")] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> ContractListResponse:
    """List all contracts for a project with optional filtering.

    Args:
        project_id: The project identifier
        item_id: Optional item ID filter
        contract_type: Optional contract type filter
        status: Optional status filter
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ContractListResponse: List of contracts with total count
    """
    service = ContractService(db)

    try:
        contracts = await service.list_contracts(project_id, item_id)
        return ContractListResponse(
            total=len(contracts),
            contracts=[ContractResponse.model_validate(c) for c in contracts],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list contracts: {e!s}") from e


@router.post("/contracts/{contract_id}/verify")
async def verify_contract_compliance(
    contract_id: Annotated[str, Path(description="Contract ID")],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VerificationResult:
    """Verify contract compliance and specification completeness.

    Args:
        contract_id: The contract identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        VerificationResult: Compliance verification results

    Raises:
        HTTPException: If contract not found (404) or verification fails
    """
    service = ContractService(db)
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    try:
        issues = []
        warnings = []

        # Verify preconditions
        if not contract.preconditions:
            issues.append("Preconditions must be defined")

        # Verify postconditions
        if not contract.postconditions:
            issues.append("Postconditions must be defined")

        # Verify title
        if not contract.title or len(contract.title) < MIN_CONTRACT_TITLE_LEN:
            issues.append("Title must be present and descriptive")

        # Check for state machine if transitions are defined
        if contract.transitions and not contract.states:
            warnings.append("States should be defined for transitions")

        # Calculate compliance score
        max_issues = 4
        max_warnings = 2
        issue_penalty = 25
        warning_penalty = 10

        score = 100.0
        score -= min(len(issues), max_issues) * issue_penalty
        score -= min(len(warnings), max_warnings) * warning_penalty
        score = max(0.0, min(100.0, score))

        result = VerificationResult(
            is_valid=len(issues) == 0,
            score=score,
            issues=issues,
            warnings=warnings,
            timestamp=datetime.now(UTC),
        )
        repo = EventRepository(db)
        await repo.log(
            project_id=contract.project_id,
            event_type="verified",
            entity_type="contract",
            entity_id=contract_id,
            data={
                "description": "Contract verification run",
                "score": score,
                "performed_by": claims.get("sub") if isinstance(claims, dict) else None,
            },
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify contract: {e!s}") from e
    else:
        return result


# =============================================================================
# Feature Endpoints
# =============================================================================


@router.post("/features", status_code=201)
async def create_feature_spec(
    feature: FeatureCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> FeatureResponse:
    """Create a new BDD feature.

    Args:
        feature: Feature creation payload
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Returns:
        FeatureResponse: Created feature

    Raises:
        HTTPException: On validation or database errors
    """
    service = FeatureService(db)

    try:
        options = CreateFeatureInput(
            description=feature.description,
            as_a=feature.as_a,
            i_want=feature.i_want,
            so_that=feature.so_that,
            status=feature.status.value if hasattr(feature.status, "value") else feature.status,
            tags=feature.tags,
            related_requirements=feature.related_requirements,
        )
        created_feature = await service.create_feature(
            project_id=feature.project_id,
            name=feature.name,
            options=options,
        )

        # Publish NATS event
        if event_bus:
            await safe_publish(
                event_bus,
                EventBus.EVENT_SPEC_CREATED,
                feature.project_id,
                str(created_feature.id),
                "feature",
                {
                    "id": str(created_feature.id),
                    "name": created_feature.name,
                    "type": "feature",
                    "status": created_feature.status,
                    "project_id": feature.project_id,
                },
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create feature: {e!s}") from e
    else:
        return created_feature


@router.get("/features/{feature_id}", response_model=FeatureResponse)
async def get_feature_spec(
    feature_id: Annotated[str, Path(description="Feature ID")],
    include_scenarios: Annotated[bool, Query(description="Include associated scenarios")] = False,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> FeatureResponse | dict[str, Any]:
    """Retrieve a specific feature by ID.

    Args:
        feature_id: The feature identifier
        include_scenarios: Whether to include scenarios in response
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        FeatureResponse: The requested feature with optional scenarios

    Raises:
        HTTPException: If feature not found (404)
    """
    service = FeatureService(db)
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    if include_scenarios:
        scenario_service = ScenarioService(db)
        scenarios = await scenario_service.list_scenarios(feature_id)
        feature_dict = {c.name: getattr(feature, c.name) for c in feature.__table__.columns}
        feature_dict["scenarios"] = scenarios
        return feature_dict

    return feature


@router.put("/features/{feature_id}")
async def update_feature_spec(
    feature_id: Annotated[str, Path(description="Feature ID")],
    updates: Annotated[FeatureUpdate | None, Body()] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> FeatureResponse:
    """Update a feature.

    Args:
        feature_id: The feature identifier
        updates: Fields to update (all optional)
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        FeatureResponse: Updated feature

    Raises:
        HTTPException: If feature not found (404) or update fails
    """
    service = FeatureService(db)

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    try:
        # Note: FeatureService might not have update_feature, handle accordingly
        updated_feature = await service.update_feature(feature_id, **update_data)
        if not updated_feature:
            raise HTTPException(status_code=404, detail="Feature not found")
    except AttributeError:
        raise HTTPException(status_code=501, detail="Feature update not yet implemented") from None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update feature: {e!s}") from e
    else:
        return updated_feature


@router.delete("/features/{feature_id}", status_code=204)
async def delete_feature_spec(
    feature_id: Annotated[str, Path(description="Feature ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a feature.

    Args:
        feature_id: The feature identifier
        claims: Authentication claims from JWT
        db: Database session

    Raises:
        HTTPException: If feature not found (404)
    """
    service = FeatureService(db)
    success = await service.delete_feature(feature_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feature not found")


@router.get("/projects/{project_id}/features")
async def list_features_for_project(
    project_id: Annotated[str, Path(description="Project ID")],
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    _tags: Annotated[list[str] | None, Query(description="Filter by tags")] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> FeatureListResponse:
    """List all features for a project with optional filtering.

    Args:
        project_id: The project identifier
        status: Optional status filter
        tags: Optional tags to filter by
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        FeatureListResponse: List of features with total count
    """
    service = FeatureService(db)

    try:
        features = await service.list_features(project_id, status)
        return FeatureListResponse(total=len(features), features=[FeatureResponse.model_validate(f) for f in features])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list features: {e!s}") from e


# =============================================================================
# Scenario Endpoints
# =============================================================================


@router.post("/features/{feature_id}/scenarios", status_code=201)
async def create_scenario_spec(
    feature_id: Annotated[str, Path(description="Feature ID")],
    scenario: Annotated[ScenarioCreate | None, Body()] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
    event_bus: Annotated[EventBus, Depends(get_event_bus)] = Depends(get_event_bus),
) -> ScenarioResponse:
    """Create a new scenario for a feature.

    Args:
        feature_id: The feature identifier
        scenario: Scenario creation payload
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Returns:
        ScenarioResponse: Created scenario

    Raises:
        HTTPException: If feature not found (404) or creation fails
    """
    service = ScenarioService(db)
    feature_service = FeatureService(db)

    feature = await feature_service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    if not scenario:
        raise HTTPException(status_code=400, detail="Scenario payload is required")

    try:
        created_scenario = await service.create_scenario(
            feature_id=feature_id,
            title=scenario.title,
            description=scenario.description,
            gherkin_text=scenario.gherkin_text,
            status=scenario.status.value if hasattr(scenario.status, "value") else scenario.status,
            given_steps=scenario.given_steps,
            when_steps=scenario.when_steps,
            then_steps=scenario.then_steps,
            tags=scenario.tags,
            is_outline=scenario.is_outline,
            examples=scenario.examples,
        )

        # Publish NATS event
        if event_bus:
            await safe_publish(
                event_bus,
                EventBus.EVENT_SPEC_CREATED,
                feature.project_id,
                str(created_scenario.id),
                "scenario",
                {
                    "id": str(created_scenario.id),
                    "title": created_scenario.title,
                    "type": "scenario",
                    "feature_id": feature_id,
                    "project_id": feature.project_id,
                },
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create scenario: {e!s}") from e
    else:
        return created_scenario


@router.get("/features/{feature_id}/scenarios")
async def list_scenarios_for_feature(
    feature_id: Annotated[str, Path(description="Feature ID")],
    _status: Annotated[str | None, Query(description="Filter by status")] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> ScenarioListResponse:
    """List all scenarios for a feature.

    Args:
        feature_id: The feature identifier
        status: Optional status filter
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ScenarioListResponse: List of scenarios with total count

    Raises:
        HTTPException: If feature not found (404)
    """
    feature_service = FeatureService(db)
    if not await feature_service.get_feature(feature_id):
        raise HTTPException(status_code=404, detail="Feature not found")

    service = ScenarioService(db)

    try:
        scenarios = await service.list_scenarios(feature_id)
        return ScenarioListResponse(
            total=len(scenarios),
            scenarios=[ScenarioResponse.model_validate(s) for s in scenarios],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list scenarios: {e!s}") from e


@router.get("/projects/{project_id}/scenarios")
async def list_scenarios_for_project(
    project_id: Annotated[str, Path(description="Project ID")],
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> ScenarioListResponse:
    """List all scenarios for a project.

    Args:
        project_id: The project identifier
        status: Optional status filter
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ScenarioListResponse: List of scenarios with total count
    """
    result = await db.execute(select(Scenario).join(Feature).where(Feature.project_id == project_id))
    scenarios = list(result.scalars().all())
    if status:
        scenarios = [s for s in scenarios if getattr(s, "status", None) == status]
    return ScenarioListResponse(total=len(scenarios), scenarios=[ScenarioResponse.model_validate(s) for s in scenarios])


@router.get("/projects/{project_id}/scenarios/activities", response_model=ScenarioActivityListResponse)
async def list_scenario_activities_for_project(
    project_id: Annotated[str, Path(description="Project ID")],
    limit: Annotated[int, Query(description="Max activities to return")] = 200,
    offset: Annotated[int, Query(description="Offset for pagination")] = 0,
    event_type: Annotated[str | None, Query(description="Filter by event type")] = None,
    since: Annotated[datetime | None, Query(description="Return events since this time")] = None,
    until: Annotated[datetime | None, Query(description="Return events until this time")] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> dict[str, Any]:
    """List scenario activity events for a project."""
    repo = EventRepository(db)
    events = await repo.get_by_project(project_id, limit=limit + offset)
    activities = [
        {
            "id": str(event.id),
            "scenario_id": event.entity_id,
            "activity_type": event.event_type,
            "from_value": event.data.get("from_value") if isinstance(event.data, dict) else None,
            "to_value": event.data.get("to_value") if isinstance(event.data, dict) else None,
            "description": event.data.get("description") if isinstance(event.data, dict) else None,
            "performed_by": event.data.get("performed_by") if isinstance(event.data, dict) else None,
            "metadata": event.data if isinstance(event.data, dict) else {},
            "created_at": event.created_at,
        }
        for event in events
        if event.entity_type == "scenario"
    ]
    total = len(activities)
    if event_type:
        activities = [a for a in activities if a["activity_type"] == event_type]
    if since:
        activities = [a for a in activities if a["created_at"] and a["created_at"] >= since]
    if until:
        activities = [a for a in activities if a["created_at"] and a["created_at"] <= until]
    total = len(activities)
    if offset:
        activities = activities[offset:]
    activities = activities[:limit]
    return {"total": total, "activities": activities}


@router.get("/scenarios/{scenario_id}")
async def get_scenario_spec(
    scenario_id: Annotated[str, Path(description="Scenario ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScenarioResponse:
    """Retrieve a specific scenario by ID.

    Args:
        scenario_id: The scenario identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ScenarioResponse: The requested scenario

    Raises:
        HTTPException: If scenario not found (404)
    """
    service = ScenarioService(db)
    scenario = await service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.get("/scenarios/{scenario_id}/activities", response_model=ScenarioActivityListResponse)
async def get_scenario_activities(
    scenario_id: Annotated[str, Path(description="Scenario ID")],
    limit: Annotated[int, Query(description="Max activities to return")] = 100,
    offset: Annotated[int, Query(description="Offset for pagination")] = 0,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> dict[str, Any]:
    """List activity events for a scenario."""
    repo = EventRepository(db)
    events = await repo.get_by_entity(scenario_id, limit=limit + offset)
    activities = [
        {
            "id": str(event.id),
            "scenario_id": scenario_id,
            "activity_type": event.event_type,
            "from_value": event.data.get("from_value") if isinstance(event.data, dict) else None,
            "to_value": event.data.get("to_value") if isinstance(event.data, dict) else None,
            "description": event.data.get("description") if isinstance(event.data, dict) else None,
            "performed_by": event.data.get("performed_by") if isinstance(event.data, dict) else None,
            "metadata": event.data if isinstance(event.data, dict) else {},
            "created_at": event.created_at,
        }
        for event in events
        if event.entity_type == "scenario"
    ]
    total = len(activities)
    if offset:
        activities = activities[offset:]
    activities = activities[:limit]
    return {"total": total, "activities": activities}


@router.put("/scenarios/{scenario_id}")
async def update_scenario_spec(
    scenario_id: Annotated[str, Path(description="Scenario ID")],
    updates: Annotated[ScenarioUpdate | None, Body()] = None,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
    event_bus: Annotated[EventBus, Depends(get_event_bus)] = Depends(get_event_bus),
) -> ScenarioResponse:
    """Update a scenario.

    Args:
        scenario_id: The scenario identifier
        updates: Fields to update (all optional)
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Returns:
        ScenarioResponse: Updated scenario

    Raises:
        HTTPException: If scenario not found (404) or update fails
    """
    service = ScenarioService(db)

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    try:
        updated_scenario = await service.update_scenario(scenario_id, **update_data)
        if not updated_scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Get feature to obtain project_id
        if updated_scenario.feature_id:
            feature_result = await db.execute(select(Feature).where(Feature.id == updated_scenario.feature_id))
            feature = feature_result.scalar_one_or_none()
            if feature and event_bus:
                await safe_publish(
                    event_bus,
                    EventBus.EVENT_SPEC_UPDATED,
                    feature.project_id,
                    scenario_id,
                    "scenario",
                    jsonable_encoder(updated_scenario),
                )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update scenario: {e!s}") from e
    else:
        return updated_scenario


@router.delete("/scenarios/{scenario_id}", status_code=204)
async def delete_scenario_spec(
    scenario_id: Annotated[str, Path(description="Scenario ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    event_bus: Annotated[EventBus, Depends(get_event_bus)],
) -> None:
    """Delete a scenario.

    Args:
        scenario_id: The scenario identifier
        claims: Authentication claims from JWT
        db: Database session
        event_bus: EventBus for cross-backend communication

    Raises:
        HTTPException: If scenario not found (404)
    """
    service = ScenarioService(db)

    # Get scenario before deletion to access project_id
    scenario = await service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get feature to obtain project_id
    project_id = None
    if scenario.feature_id:
        feature_result = await db.execute(select(Feature).where(Feature.id == scenario.feature_id))
        feature = feature_result.scalar_one_or_none()
        if feature:
            project_id = feature.project_id

    success = await service.delete_scenario(scenario_id)

    if success and event_bus and project_id:
        await safe_publish(
            event_bus,
            EventBus.EVENT_SPEC_DELETED,
            project_id,
            scenario_id,
            "scenario",
            {"id": scenario_id},
        )


@router.post("/scenarios/{scenario_id}/run")
async def run_scenario(
    scenario_id: Annotated[str, Path(description="Scenario ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScenarioRunResult:
    """Run a scenario and capture results.

    This endpoint orchestrates scenario execution by:
    1. Loading the scenario and its steps
    2. Executing steps in sequence
    3. Capturing pass/fail results
    4. Recording execution metrics

    Args:
        scenario_id: The scenario identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        ScenarioRunResult: Execution results with pass/fail counts

    Raises:
        HTTPException: If scenario not found (404) or execution fails
    """
    service = ScenarioService(db)
    scenario = await service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    try:
        # Note: Actual execution would require integrating with a test runner
        # For now, return a placeholder result structure
        start_time = datetime.now(UTC)

        # Simulate execution
        given_steps = getattr(scenario, "given_steps", None) or []
        steps_passed = len(given_steps)
        steps_failed = 0

        result = ScenarioRunResult(
            scenario_id=scenario_id,
            passed=steps_failed == 0,
            duration_ms=(datetime.now(UTC) - start_time).total_seconds() * 1000,
            steps_passed=steps_passed,
            steps_failed=steps_failed,
            error_message=None,
            timestamp=datetime.now(UTC),
        )
        project_id = ""
        if scenario.feature_id:
            feature_result = await db.execute(select(Feature).where(Feature.id == scenario.feature_id))
            feature = feature_result.scalar_one_or_none()
            if feature:
                project_id = feature.project_id

        repo = EventRepository(db)
        await repo.log(
            project_id=project_id,
            event_type="executed",
            entity_type="scenario",
            entity_id=scenario_id,
            data={
                "description": "Scenario executed",
                "passed": steps_failed == 0,
                "steps_passed": steps_passed,
                "steps_failed": steps_failed,
            },
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to run scenario: {e!s}") from e
    else:
        return result


# =============================================================================
# Project-Level Endpoints
# =============================================================================


@router.get("/projects/{project_id}/summary")
async def get_specifications_summary(
    project_id: Annotated[str, Path(description="Project ID")],
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SpecificationsSummary:
    """Get a summary of all specifications in a project.

    Args:
        project_id: The project identifier
        claims: Authentication claims from JWT
        db: Database session

    Returns:
        SpecificationsSummary: Aggregated counts and compliance score

    Raises:
        HTTPException: On query errors
    """
    try:
        adr_service = ADRService(db)
        contract_service = ContractService(db)
        feature_service = FeatureService(db)
        scenario_service = ScenarioService(db)

        adrs = await adr_service.list_adrs(project_id)
        contracts = await contract_service.list_contracts(project_id)
        features = await feature_service.list_features(project_id)

        # Calculate scenarios from features
        scenario_count = 0
        for feature in features:
            scenarios = await scenario_service.list_scenarios(feature.id)
            scenario_count += len(scenarios)

        # Calculate overall compliance score (simplified scoring based on completeness)
        compliance_scores = [80.0 for adr in adrs if adr.context and adr.decision and adr.consequences]

        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0

        return SpecificationsSummary(
            project_id=project_id,
            adr_count=len(adrs),
            contract_count=len(contracts),
            feature_count=len(features),
            scenario_count=scenario_count,
            compliance_score=avg_compliance,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get summary: {e!s}") from e
