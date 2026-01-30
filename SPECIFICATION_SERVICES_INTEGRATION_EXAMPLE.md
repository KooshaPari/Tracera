# Specification Services Integration Example

Complete examples showing how to integrate specification services with tRPC routers and the application.

## Table of Contents

1. [tRPC Router Integration](#trpc-router-integration)
2. [Service Dependency Injection](#service-dependency-injection)
3. [Request/Response Types](#requestresponse-types)
4. [Error Handling](#error-handling)
5. [Real-World Workflows](#real-world-workflows)

---

## tRPC Router Integration

### ADR Router

```python
# src/tracertm/api/routers/adr_router.py

from typing import Optional, Annotated
from datetime import date as date_type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.core.context import get_current_user
from tracertm.schemas.adr import ADRCreate, ADRUpdate, ADRResponse
from tracertm.services.specification_service import ADRService


class ADRRouter:
    """Router for ADR endpoints."""

    def __init__(self):
        self.service = None

    async def _get_service(
        self, session: AsyncSession = Depends(get_db)
    ) -> ADRService:
        """Get ADR service instance."""
        return ADRService(session)

    async def create_adr(
        self,
        project_id: str,
        input: ADRCreate,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ADRResponse:
        """Create a new ADR."""
        service = ADRService(session)

        adr = await service.create(
            project_id=project_id,
            title=input.title,
            context=input.context,
            decision=input.decision,
            consequences=input.consequences,
            status=input.status,
            decision_drivers=input.decision_drivers,
            considered_options=input.considered_options,
            related_requirements=input.related_requirements,
            related_adrs=input.related_adrs,
            stakeholders=input.stakeholders,
            tags=input.tags,
            date_value=input.date,
        )

        await session.commit()
        await session.refresh(adr)
        return ADRResponse.from_orm(adr)

    async def get_adr(
        self,
        adr_id: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
    ) -> ADRResponse:
        """Get an ADR by ID."""
        service = ADRService(session)
        adr = await service.get(adr_id)

        if not adr:
            raise ValueError(f"ADR {adr_id} not found")

        return ADRResponse.from_orm(adr)

    async def list_adrs(
        self,
        project_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
    ) -> dict:
        """List ADRs for a project."""
        service = ADRService(session)
        adrs, total = await service.list_by_project(
            project_id=project_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        return {
            "items": [ADRResponse.from_orm(adr) for adr in adrs],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def update_adr(
        self,
        adr_id: str,
        input: ADRUpdate,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ADRResponse:
        """Update an ADR."""
        service = ADRService(session)

        updates = input.model_dump(exclude_unset=True)
        adr = await service.update(adr_id, **updates)

        if not adr:
            raise ValueError(f"ADR {adr_id} not found")

        await session.commit()
        await session.refresh(adr)
        return ADRResponse.from_orm(adr)

    async def delete_adr(
        self,
        adr_id: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> dict:
        """Delete an ADR."""
        service = ADRService(session)
        success = await service.delete(adr_id)

        if not success:
            raise ValueError(f"ADR {adr_id} not found")

        await session.commit()
        return {"success": True}

    async def verify_compliance(
        self,
        adr_id: str,
        compliance_score: float,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ADRResponse:
        """Verify ADR compliance."""
        service = ADRService(session)
        adr = await service.verify_compliance(adr_id, compliance_score)

        if not adr:
            raise ValueError(f"ADR {adr_id} not found")

        await session.commit()
        await session.refresh(adr)
        return ADRResponse.from_orm(adr)

    async def link_requirements(
        self,
        adr_id: str,
        requirement_ids: list[str],
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ADRResponse:
        """Link requirements to an ADR."""
        service = ADRService(session)
        adr = await service.link_requirements(adr_id, requirement_ids)

        if not adr:
            raise ValueError(f"ADR {adr_id} not found")

        await session.commit()
        await session.refresh(adr)
        return ADRResponse.from_orm(adr)

    async def supersede(
        self,
        adr_id: str,
        superseded_by_number: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ADRResponse:
        """Mark ADR as superseded."""
        service = ADRService(session)
        adr = await service.supersede(adr_id, superseded_by_number)

        if not adr:
            raise ValueError(f"ADR {adr_id} not found")

        await session.commit()
        await session.refresh(adr)
        return ADRResponse.from_orm(adr)
```

### Feature/Scenario Router

```python
# src/tracertm/api/routers/feature_router.py

from typing import Optional, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.core.context import get_current_user
from tracertm.schemas.feature import FeatureCreate, FeatureUpdate, FeatureResponse
from tracertm.schemas.scenario import ScenarioCreate, ScenarioResponse
from tracertm.services.specification_service import (
    FeatureService,
    ScenarioService,
)


class FeatureRouter:
    """Router for Feature endpoints."""

    async def create_feature(
        self,
        project_id: str,
        input: FeatureCreate,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> FeatureResponse:
        """Create a new Feature."""
        service = FeatureService(session)

        feature = await service.create(
            project_id=project_id,
            name=input.name,
            description=input.description,
            as_a=input.as_a,
            i_want=input.i_want,
            so_that=input.so_that,
            status=input.status or "draft",
            file_path=input.file_path,
            tags=input.tags,
            related_requirements=input.related_requirements,
            related_adrs=input.related_adrs,
        )

        await session.commit()
        await session.refresh(feature)
        return FeatureResponse.from_orm(feature)

    async def get_feature_with_scenarios(
        self,
        feature_id: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
    ) -> dict:
        """Get Feature with related scenarios."""
        service = FeatureService(session)
        feature_data = await service.get_with_scenarios(feature_id)

        if not feature_data:
            raise ValueError(f"Feature {feature_id} not found")

        return {
            "feature": FeatureResponse.from_orm(feature_data["feature"]),
            "scenarios": [
                ScenarioResponse.from_orm(s) for s in feature_data["scenarios"]
            ],
            "scenario_count": feature_data["scenario_count"],
            "pass_rate": await service.calculate_pass_rate(feature_id),
        }

    async def calculate_feature_metrics(
        self,
        feature_id: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
    ) -> dict:
        """Calculate feature metrics."""
        feature_service = FeatureService(session)
        scenario_service = ScenarioService(session)

        feature = await feature_service.get(feature_id)
        if not feature:
            raise ValueError(f"Feature {feature_id} not found")

        feature_data = await feature_service.get_with_scenarios(feature_id)
        pass_rate = await feature_service.calculate_pass_rate(feature_id)

        scenarios = feature_data["scenarios"]
        executed_scenarios = [s for s in scenarios if s.status == "executed"]

        return {
            "feature_id": feature_id,
            "feature_number": feature.feature_number,
            "total_scenarios": len(scenarios),
            "executed_scenarios": len(executed_scenarios),
            "pass_rate": pass_rate,
            "scenarios": [
                {
                    "id": s.id,
                    "title": s.title,
                    "status": s.status,
                    "pass_rate": s.pass_rate,
                }
                for s in scenarios
            ],
        }


class ScenarioRouter:
    """Router for Scenario endpoints."""

    async def create_scenario(
        self,
        feature_id: str,
        input: ScenarioCreate,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ScenarioResponse:
        """Create a new Scenario."""
        service = ScenarioService(session)

        scenario = await service.create(
            feature_id=feature_id,
            title=input.title,
            gherkin_text=input.gherkin_text,
            description=input.description,
            is_outline=input.is_outline or False,
            background=input.background,
            given_steps=input.given_steps,
            when_steps=input.when_steps,
            then_steps=input.then_steps,
            examples=input.examples,
            tags=input.tags,
            requirement_ids=input.requirement_ids,
            test_case_ids=input.test_case_ids,
        )

        await session.commit()
        await session.refresh(scenario)
        return ScenarioResponse.from_orm(scenario)

    async def run_scenario(
        self,
        scenario_id: str,
        results: dict,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ScenarioResponse:
        """Run a scenario and record results."""
        service = ScenarioService(session)

        scenario = await service.run(scenario_id, results)

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        await session.commit()
        await session.refresh(scenario)
        return ScenarioResponse.from_orm(scenario)

    async def link_test_cases(
        self,
        scenario_id: str,
        test_case_ids: list[str],
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ScenarioResponse:
        """Link test cases to a scenario."""
        service = ScenarioService(session)

        scenario = await service.link_test_cases(scenario_id, test_case_ids)

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        await session.commit()
        await session.refresh(scenario)
        return ScenarioResponse.from_orm(scenario)
```

### Contract Router

```python
# src/tracertm/api/routers/contract_router.py

from typing import Optional, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.core.context import get_current_user
from tracertm.schemas.contract import ContractCreate, ContractResponse
from tracertm.services.specification_service import ContractService


class ContractRouter:
    """Router for Contract endpoints."""

    async def create_contract(
        self,
        project_id: str,
        item_id: str,
        input: ContractCreate,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ContractResponse:
        """Create a new Contract."""
        service = ContractService(session)

        contract = await service.create(
            project_id=project_id,
            item_id=item_id,
            title=input.title,
            contract_type=input.contract_type,
            preconditions=input.preconditions,
            postconditions=input.postconditions,
            invariants=input.invariants,
            states=input.states,
            transitions=input.transitions,
            executable_spec=input.executable_spec,
            spec_language=input.spec_language,
            tags=input.tags,
        )

        await session.commit()
        await session.refresh(contract)
        return ContractResponse.from_orm(contract)

    async def verify_contract(
        self,
        contract_id: str,
        verification_result: dict,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ContractResponse:
        """Verify a contract."""
        service = ContractService(session)

        contract = await service.verify(contract_id, verification_result)

        if not contract:
            raise ValueError(f"Contract {contract_id} not found")

        await session.commit()
        await session.refresh(contract)
        return ContractResponse.from_orm(contract)

    async def execute_transition(
        self,
        contract_id: str,
        from_state: str,
        to_state: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
        current_user = Depends(get_current_user),
    ) -> ContractResponse:
        """Execute state transition."""
        service = ContractService(session)

        contract = await service.execute_transition(
            contract_id, from_state, to_state
        )

        if not contract:
            raise ValueError(
                f"Invalid transition from {from_state} to {to_state}"
            )

        await session.commit()
        await session.refresh(contract)
        return ContractResponse.from_orm(contract)

    async def get_contracts_by_item(
        self,
        item_id: str,
        session: Annotated[AsyncSession, Depends(get_db)] = None,
    ) -> list[ContractResponse]:
        """Get all contracts for an item."""
        service = ContractService(session)
        contracts = await service.list_by_item(item_id)
        return [ContractResponse.from_orm(c) for c in contracts]
```

---

## Service Dependency Injection

### Setup in Main Application

```python
# src/tracertm/api/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.api.routers.adr_router import ADRRouter
from tracertm.api.routers.feature_router import FeatureRouter, ScenarioRouter
from tracertm.api.routers.contract_router import ContractRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    print("Application started")
    yield
    # Shutdown
    print("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="TraceRTM Specification API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Initialize routers
    adr_router = ADRRouter()
    feature_router = FeatureRouter()
    scenario_router = ScenarioRouter()
    contract_router = ContractRouter()

    # Register endpoints
    app.add_api_route(
        "/projects/{project_id}/adrs",
        adr_router.create_adr,
        methods=["POST"],
    )
    app.add_api_route(
        "/projects/{project_id}/adrs",
        adr_router.list_adrs,
        methods=["GET"],
    )
    app.add_api_route(
        "/adrs/{adr_id}",
        adr_router.get_adr,
        methods=["GET"],
    )
    app.add_api_route(
        "/adrs/{adr_id}",
        adr_router.update_adr,
        methods=["PATCH"],
    )
    app.add_api_route(
        "/adrs/{adr_id}",
        adr_router.delete_adr,
        methods=["DELETE"],
    )
    app.add_api_route(
        "/adrs/{adr_id}/verify-compliance",
        adr_router.verify_compliance,
        methods=["POST"],
    )
    app.add_api_route(
        "/adrs/{adr_id}/link-requirements",
        adr_router.link_requirements,
        methods=["POST"],
    )
    app.add_api_route(
        "/adrs/{adr_id}/supersede",
        adr_router.supersede,
        methods=["POST"],
    )

    # Feature endpoints
    app.add_api_route(
        "/projects/{project_id}/features",
        feature_router.create_feature,
        methods=["POST"],
    )
    app.add_api_route(
        "/features/{feature_id}/with-scenarios",
        feature_router.get_feature_with_scenarios,
        methods=["GET"],
    )
    app.add_api_route(
        "/features/{feature_id}/metrics",
        feature_router.calculate_feature_metrics,
        methods=["GET"],
    )

    # Scenario endpoints
    app.add_api_route(
        "/features/{feature_id}/scenarios",
        scenario_router.create_scenario,
        methods=["POST"],
    )
    app.add_api_route(
        "/scenarios/{scenario_id}/run",
        scenario_router.run_scenario,
        methods=["POST"],
    )
    app.add_api_route(
        "/scenarios/{scenario_id}/link-test-cases",
        scenario_router.link_test_cases,
        methods=["POST"],
    )

    # Contract endpoints
    app.add_api_route(
        "/projects/{project_id}/items/{item_id}/contracts",
        contract_router.create_contract,
        methods=["POST"],
    )
    app.add_api_route(
        "/contracts/{contract_id}/verify",
        contract_router.verify_contract,
        methods=["POST"],
    )
    app.add_api_route(
        "/contracts/{contract_id}/transition",
        contract_router.execute_transition,
        methods=["POST"],
    )
    app.add_api_route(
        "/items/{item_id}/contracts",
        contract_router.get_contracts_by_item,
        methods=["GET"],
    )

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Request/Response Types

### ADR Schemas

```python
# src/tracertm/schemas/adr.py

from typing import Optional, List
from datetime import date as date_type
from pydantic import BaseModel, Field


class ADRCreate(BaseModel):
    """Request body for creating ADR."""
    title: str
    context: str
    decision: str
    consequences: str
    status: Optional[str] = "proposed"
    decision_drivers: Optional[List[str]] = []
    considered_options: Optional[List[dict]] = []
    related_requirements: Optional[List[str]] = []
    related_adrs: Optional[List[str]] = []
    stakeholders: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    date: Optional[date_type] = None


class ADRUpdate(BaseModel):
    """Request body for updating ADR."""
    title: Optional[str] = None
    context: Optional[str] = None
    decision: Optional[str] = None
    consequences: Optional[str] = None
    status: Optional[str] = None
    decision_drivers: Optional[List[str]] = None
    considered_options: Optional[List[dict]] = None
    related_requirements: Optional[List[str]] = None
    related_adrs: Optional[List[str]] = None
    stakeholders: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    class Config:
        extra = "forbid"


class ADRResponse(BaseModel):
    """Response body for ADR."""
    id: str
    project_id: str
    adr_number: str
    title: str
    status: str
    context: str
    decision: str
    consequences: str
    decision_drivers: List[str]
    considered_options: List[dict]
    related_requirements: List[str]
    related_adrs: List[str]
    compliance_score: float
    stakeholders: List[str]
    tags: List[str]
    version: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
```

### Feature/Scenario Schemas

```python
# src/tracertm/schemas/feature.py

from typing import Optional, List
from pydantic import BaseModel


class FeatureCreate(BaseModel):
    """Request body for creating Feature."""
    name: str
    description: Optional[str] = None
    as_a: Optional[str] = None
    i_want: Optional[str] = None
    so_that: Optional[str] = None
    status: Optional[str] = "draft"
    file_path: Optional[str] = None
    tags: Optional[List[str]] = []
    related_requirements: Optional[List[str]] = []
    related_adrs: Optional[List[str]] = []


class FeatureResponse(BaseModel):
    """Response body for Feature."""
    id: str
    project_id: str
    feature_number: str
    name: str
    description: Optional[str]
    as_a: Optional[str]
    i_want: Optional[str]
    so_that: Optional[str]
    status: str
    file_path: Optional[str]
    tags: List[str]
    related_requirements: List[str]
    related_adrs: List[str]
    version: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# src/tracertm/schemas/scenario.py

class ScenarioCreate(BaseModel):
    """Request body for creating Scenario."""
    title: str
    gherkin_text: str
    description: Optional[str] = None
    is_outline: Optional[bool] = False
    background: Optional[List[dict]] = []
    given_steps: Optional[List[dict]] = []
    when_steps: Optional[List[dict]] = []
    then_steps: Optional[List[dict]] = []
    examples: Optional[dict] = None
    tags: Optional[List[str]] = []
    requirement_ids: Optional[List[str]] = []
    test_case_ids: Optional[List[str]] = []


class ScenarioResponse(BaseModel):
    """Response body for Scenario."""
    id: str
    feature_id: str
    scenario_number: str
    title: str
    gherkin_text: str
    description: Optional[str]
    is_outline: bool
    background: List[dict]
    given_steps: List[dict]
    when_steps: List[dict]
    then_steps: List[dict]
    examples: Optional[dict]
    status: str
    pass_rate: float
    tags: List[str]
    requirement_ids: List[str]
    test_case_ids: List[str]
    version: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
```

---

## Error Handling

### Custom Exception Handling

```python
# src/tracertm/api/exception_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors (not found, invalid state, etc.)."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request",
            "message": str(exc),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        },
    )


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers."""
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
```

---

## Real-World Workflows

### Complete Specification Management Workflow

```python
# Example workflow: Create and manage specifications

async def complete_specification_workflow(
    session: AsyncSession,
    project_id: str,
):
    """Complete workflow for managing specifications."""
    from tracertm.services.specification_service import (
        ADRService,
        FeatureService,
        ScenarioService,
        ContractService,
    )

    adr_service = ADRService(session)
    feature_service = FeatureService(session)
    scenario_service = ScenarioService(session)
    contract_service = ContractService(session)

    # Step 1: Create ADR for authentication architecture
    adr = await adr_service.create(
        project_id=project_id,
        title="JWT-based Authentication",
        context="Need secure user authentication",
        decision="Use JWT tokens with refresh tokens",
        consequences="Stateless authentication, requires token management",
        stakeholders=["Backend", "Frontend", "Security"],
    )
    print(f"Created {adr.adr_number}: {adr.title}")

    # Step 2: Create Feature for login
    feature = await feature_service.create(
        project_id=project_id,
        name="User Login",
        as_a="User",
        i_want="to login with email and password",
        so_that="I can access my account",
        related_adrs=[adr.adr_number],
    )
    print(f"Created {feature.feature_number}: {feature.name}")

    # Step 3: Create Scenarios for login feature
    scenario1 = await scenario_service.create(
        feature_id=feature.id,
        title="Successful login",
        gherkin_text="""
Given user is on login page
When user enters valid email and password
And user clicks login button
Then user is redirected to dashboard
And authentication token is issued
""",
        given_steps=[
            {"text": "user is on login page", "status": "pending"}
        ],
        when_steps=[
            {"text": "user enters valid email and password", "status": "pending"},
            {"text": "user clicks login button", "status": "pending"},
        ],
        then_steps=[
            {"text": "user is redirected to dashboard", "status": "pending"},
            {"text": "authentication token is issued", "status": "pending"},
        ],
        requirement_ids=["REQ-AUTH-001"],
    )

    scenario2 = await scenario_service.create(
        feature_id=feature.id,
        title="Failed login with wrong password",
        gherkin_text="""
Given user is on login page
When user enters valid email and wrong password
And user clicks login button
Then error message is displayed
And user remains on login page
""",
        given_steps=[
            {"text": "user is on login page", "status": "pending"}
        ],
        when_steps=[
            {"text": "user enters valid email and wrong password", "status": "pending"},
            {"text": "user clicks login button", "status": "pending"},
        ],
        then_steps=[
            {"text": "error message is displayed", "status": "pending"},
            {"text": "user remains on login page", "status": "pending"},
        ],
        requirement_ids=["REQ-AUTH-002"],
    )
    print(f"Created {scenario1.scenario_number}: {scenario1.title}")
    print(f"Created {scenario2.scenario_number}: {scenario2.title}")

    # Step 4: Create Contract for authentication API
    contract = await contract_service.create(
        project_id=project_id,
        item_id=feature.id,
        title="Authentication API Contract",
        contract_type="api",
        preconditions=[
            {"name": "email", "type": "string", "required": True},
            {"name": "password", "type": "string", "required": True},
        ],
        postconditions=[
            {"name": "token", "type": "string", "required": True},
            {"name": "user_id", "type": "string", "required": True},
        ],
        states=["READY", "AUTHENTICATING", "AUTHENTICATED", "ERROR"],
        transitions=[
            {"from": "READY", "to": "AUTHENTICATING"},
            {"from": "AUTHENTICATING", "to": "AUTHENTICATED"},
            {"from": "AUTHENTICATING", "to": "ERROR"},
            {"from": "ERROR", "to": "READY"},
        ],
    )
    print(f"Created {contract.contract_number}: {contract.title}")

    # Step 5: Run scenarios and collect results
    await scenario_service.run(
        scenario1.id,
        {"passed_steps": 5, "failed_steps": 0, "execution_time": 2.3},
    )
    await scenario_service.run(
        scenario2.id,
        {"passed_steps": 4, "failed_steps": 0, "execution_time": 1.8},
    )

    # Step 6: Calculate metrics
    feature_data = await feature_service.get_with_scenarios(feature.id)
    pass_rate = await feature_service.calculate_pass_rate(feature.id)

    print(f"\nFeature metrics:")
    print(f"  Total scenarios: {feature_data['scenario_count']}")
    print(f"  Pass rate: {pass_rate * 100:.1f}%")

    # Step 7: Verify contract
    await contract_service.verify(
        contract.id,
        {
            "status": "passed",
            "checks": 8,
            "passed": 8,
            "failed": 0,
            "timestamp": datetime.now().isoformat(),
        },
    )

    # Step 8: Verify ADR compliance
    await adr_service.verify_compliance(
        adr.id,
        compliance_score=0.90,
    )

    # Commit all changes
    await session.commit()

    return {
        "adr": adr,
        "feature": feature,
        "scenarios": [scenario1, scenario2],
        "contract": contract,
        "pass_rate": pass_rate,
    }
```

---

## Testing Integration

### Test Helper Functions

```python
# tests/conftest.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.specification_service import (
    ADRService,
    FeatureService,
    ScenarioService,
    ContractService,
)


@pytest.fixture
async def adr_service(session: AsyncSession) -> ADRService:
    """Create ADR service for testing."""
    return ADRService(session)


@pytest.fixture
async def feature_service(session: AsyncSession) -> FeatureService:
    """Create Feature service for testing."""
    return FeatureService(session)


@pytest.fixture
async def scenario_service(session: AsyncSession) -> ScenarioService:
    """Create Scenario service for testing."""
    return ScenarioService(session)


@pytest.fixture
async def contract_service(session: AsyncSession) -> ContractService:
    """Create Contract service for testing."""
    return ContractService(session)


# tests/integration/test_specification_workflow.py

@pytest.mark.asyncio
async def test_complete_workflow(
    session: AsyncSession,
    adr_service: ADRService,
    feature_service: FeatureService,
    scenario_service: ScenarioService,
):
    """Test complete specification workflow."""
    # Create ADR
    adr = await adr_service.create(
        project_id="proj-1",
        title="Test ADR",
        context="Test context",
        decision="Test decision",
        consequences="Test consequences",
    )

    # Create Feature
    feature = await feature_service.create(
        project_id="proj-1",
        name="Test Feature",
        related_adrs=[adr.adr_number],
    )

    # Create Scenario
    scenario = await scenario_service.create(
        feature_id=feature.id,
        title="Test Scenario",
        gherkin_text="Given ... When ... Then ...",
    )

    # Run scenario
    await scenario_service.run(
        scenario.id,
        {"passed_steps": 3, "failed_steps": 0},
    )

    # Verify data
    feature_data = await feature_service.get_with_scenarios(feature.id)
    assert feature_data["scenario_count"] == 1
    assert feature_data["scenarios"][0].pass_rate == 1.0

    await session.commit()
```

---

## Summary

This integration guide shows how to:
1. Create routers for each service
2. Expose endpoints using FastAPI
3. Handle dependency injection
4. Define request/response schemas
5. Implement error handling
6. Use services in real workflows
7. Test integrated functionality

All services follow consistent patterns for easy integration and maintenance.
