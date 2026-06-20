"""BDD feature/scenario API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.event_repository import EventRepository
from tracertm.schemas.specification import (
    FeatureActivityListResponse,
    FeatureCreate,
    FeatureRead,
    ScenarioActivityListResponse,
    ScenarioCreate,
    ScenarioRead,
)
from tracertm.services.feature_service import CreateFeatureInput, FeatureService
from tracertm.services.scenario_service import ScenarioService

router = APIRouter(prefix="/features", tags=["BDD Features"])

# =============================================================================
# Features
# =============================================================================


@router.post("/", response_model=FeatureRead, status_code=201)
async def create_feature(
    feature: FeatureCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a new BDD feature.

    Functional Requirements:
    - FR-QUAL-005

    User Stories:
    - US-FEAT-001

    Epics:
    - EPIC-005
    """
    service = FeatureService(db)
    options = CreateFeatureInput(
        description=feature.description,
        as_a=feature.as_a,
        i_want=feature.i_want,
        so_that=feature.so_that,
        status=feature.status,
        tags=feature.tags,
        related_requirements=feature.related_requirements,
    )
    return await service.create_feature(
        project_id=feature.project_id,
        name=feature.name,
        options=options,
    )


@router.get("/{feature_id}", response_model=FeatureRead)
async def get_feature(
    feature_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return a BDD feature by id.

    Functional Requirements:
    - FR-QUAL-006

    User Stories:
    - US-FEAT-002

    Epics:
    - EPIC-005
    """
    service = FeatureService(db)
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Simple way to attach scenarios (could be optimized with a join)
    scenario_service = ScenarioService(db)
    scenarios = await scenario_service.list_scenarios(feature_id)

    # We need to manually construct the response or rely on ORM lazy loading if configured (not in async usually)
    # Using Pydantic's from_attributes with pre-populated object is trickier with async ORM unless joined loaded.
    # For now, let's just return the feature and let the frontend fetch scenarios separately if needed,
    # OR manually patch it. The schema expects 'scenarios'.

    # Re-wrap to include scenarios
    feature_dict = {c.name: getattr(feature, c.name) for c in feature.__table__.columns}
    feature_dict["scenarios"] = scenarios
    return feature_dict


@router.get("/{feature_id}/activities", response_model=FeatureActivityListResponse)
async def get_feature_activities(
    feature_id: str,
    limit: Annotated[int, Query(description="Max activities to return")] = 100,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List feature activity events."""
    repo = EventRepository(db)
    events = await repo.get_by_entity(feature_id, limit=limit)
    activities = [
        {
            "id": str(event.id),
            "feature_id": feature_id,
            "activity_type": event.event_type,
            "from_value": event.data.get("from_value") if isinstance(event.data, dict) else None,
            "to_value": event.data.get("to_value") if isinstance(event.data, dict) else None,
            "description": event.data.get("description") if isinstance(event.data, dict) else None,
            "performed_by": event.data.get("performed_by") if isinstance(event.data, dict) else None,
            "metadata": event.data if isinstance(event.data, dict) else {},
            "created_at": event.created_at,
        }
        for event in events
        if event.entity_type == "feature"
    ]
    return {"activities": activities}


@router.delete("/{feature_id}", status_code=204)
async def delete_feature(
    feature_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a BDD feature by id."""
    service = FeatureService(db)
    success = await service.delete_feature(feature_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feature not found")


@router.get("/", response_model=list[FeatureRead])
async def list_features(
    project_id: Annotated[str, Query(description="Project ID")],
    status: Annotated[str | None, Query(description="Filter by status")] = None,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List BDD features for a project.

    Functional Requirements:
    - FR-QUAL-008

    User Stories:
    - US-FEAT-004

    Epics:
    - EPIC-005
    """
    service = FeatureService(db)
    return await service.list_features(project_id, status)


# =============================================================================
# Scenarios
# =============================================================================


@router.post("/{feature_id}/scenarios", response_model=ScenarioRead, status_code=201)
async def create_scenario(
    feature_id: str,
    scenario: ScenarioCreate,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a BDD scenario for a feature."""
    service = ScenarioService(db)
    # Validate feature exists
    feat_service = FeatureService(db)
    if not await feat_service.get_feature(feature_id):
        raise HTTPException(status_code=404, detail="Feature not found")

    return await service.create_scenario(
        feature_id=feature_id,
        title=scenario.title,
        gherkin_text=scenario.gherkin_text,
        description=scenario.description,
        given_steps=scenario.given_steps,
        when_steps=scenario.when_steps,
        then_steps=scenario.then_steps,
        status=scenario.status,
        tags=scenario.tags,
        is_outline=scenario.is_outline,
        examples=scenario.examples,
    )


@router.get("/scenarios/{scenario_id}", response_model=ScenarioRead)
async def get_scenario(
    scenario_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return a BDD scenario by id."""
    service = ScenarioService(db)
    scenario = await service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.get("/scenarios/{scenario_id}/activities", response_model=ScenarioActivityListResponse)
async def get_scenario_activities(
    scenario_id: str,
    limit: Annotated[int, Query(description="Max activities to return")] = 100,
    _claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List scenario activity events."""
    repo = EventRepository(db)
    events = await repo.get_by_entity(scenario_id, limit=limit)
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
    return {"activities": activities}


@router.delete("/scenarios/{scenario_id}", status_code=204)
async def delete_scenario(
    scenario_id: str,
    _claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a BDD scenario by id."""
    service = ScenarioService(db)
    success = await service.delete_scenario(scenario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
