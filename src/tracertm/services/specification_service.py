"""Services for specification entities (ADR, Contract, Feature, Scenario, StepDefinition)."""

from __future__ import annotations

import inspect
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from datetime import date as date_type
from typing import TYPE_CHECKING, Any

from sqlalchemy import delete, func, select

from tracertm.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    SCORE_MAX,
    SCORE_MIN,
    SEQUENCE_PADDING,
    SEQUENCE_START,
    VERSION_INCREMENT,
    VERSION_INITIAL,
    ZERO,
)
from tracertm.core.concurrency import update_with_retry
from tracertm.models.specification import ADR, Contract, Feature, Scenario

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ADROptions:
    """Optional parameters for ADR creation."""

    status: str = "proposed"
    decision_drivers: list[str] | None = None
    considered_options: list[dict] | None = None
    related_requirements: list[str] | None = None
    related_adrs: list[str] | None = None
    stakeholders: list[str] | None = None
    tags: list[str] | None = None
    date_value: date_type | None = None


@dataclass
class ADRContent:
    """Core content for ADR creation."""

    title: str
    context: str
    decision: str
    consequences: str


@dataclass
class ContractOptions:
    """Optional parameters for Contract creation."""

    preconditions: list[dict] | None = None
    postconditions: list[dict] | None = None
    invariants: list[dict] | None = None
    states: list[str] | None = None
    transitions: list[dict] | None = None
    executable_spec: str | None = None
    spec_language: str | None = None
    tags: list[str] | None = None


@dataclass
class ContractContent:
    """Core content for Contract creation."""

    item_id: str
    title: str
    contract_type: str


@dataclass
class FeatureOptions:
    """Optional parameters for Feature creation."""

    description: str | None = None
    as_a: str | None = None
    i_want: str | None = None
    so_that: str | None = None
    status: str = "draft"
    file_path: str | None = None
    tags: list[str] | None = None
    related_requirements: list[str] | None = None
    related_adrs: list[str] | None = None


@dataclass
class FeatureContent:
    """Core content for Feature creation."""

    name: str


@dataclass
class ScenarioOptions:
    """Optional parameters for Scenario creation."""

    description: str | None = None
    is_outline: bool = False
    background: list[dict] | None = None
    given: list[dict] | None = None
    when: list[dict] | None = None
    then: list[dict] | None = None
    and_: list[dict] | None = None
    but: list[dict] | None = None
    examples: dict | None = None
    tags: list[str] | None = None
    requirement_ids: list[str] | None = None
    test_case_ids: list[str] | None = None


@dataclass
class ScenarioContent:
    """Core content for Scenario creation."""

    title: str
    gherkin_text: str


@dataclass
class StepDefinitionOptions:
    """Optional parameters for StepDefinition creation."""

    language: str = "python"
    description: str | None = None
    parameters: list[dict] | None = None
    tags: list[str] | None = None


@dataclass
class StepDefinitionContent:
    """Core content for StepDefinition creation."""

    step_pattern: str
    step_type: str
    implementation_code: str


async def _maybe_await(value: object) -> object:
    if inspect.isawaitable(value):
        return await value
    return value


class ADRService:
    """Service for Architecture Decision Records.

    Functional Requirements:
    - FR-QUAL-001
    - FR-QUAL-002
    - FR-QUAL-003
    - FR-QUAL-004

    User Stories:
    - US-SPEC-002
    - US-SPEC-003
    - US-SPEC-004
    - US-SPEC-005

    Epics:
    - EPIC-002
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        content: ADRContent,
        options: ADROptions | None = None,
    ) -> ADR:
        """Create a new ADR.

        Functional Requirements:
        - FR-QUAL-001
        - FR-QUAL-005

        User Stories:
        - US-FEAT-001
        - US-SPEC-002

        Epics:
        - EPIC-002
        - EPIC-005
        """
        opts = options or ADROptions()
        # Generate sequential ADR number
        result = await self.session.execute(
            select(ADR).where(ADR.project_id == project_id).order_by(ADR.created_at.desc()).limit(1),
        )
        last_adr = await _maybe_await(result.scalar_one_or_none())

        if last_adr:
            try:
                last_num = int(str(last_adr.adr_number).replace("ADR-", ""))  # type: ignore[attr-defined]
                next_num = last_num + VERSION_INCREMENT
            except ValueError:
                next_num = SEQUENCE_START
        else:
            next_num = SEQUENCE_START

        adr_number = f"ADR-{next_num:0{SEQUENCE_PADDING}d}"

        adr = ADR(
            id=str(uuid.uuid4()),
            project_id=project_id,
            adr_number=adr_number,
            title=content.title,
            status=opts.status,
            context=content.context,
            decision=content.decision,
            consequences=content.consequences,
            decision_drivers=opts.decision_drivers or [],
            considered_options=opts.considered_options or [],
            related_requirements=opts.related_requirements or [],
            related_adrs=opts.related_adrs or [],
            stakeholders=opts.stakeholders or [],
            tags=opts.tags or [],
            date=opts.date_value or datetime.now(UTC).date(),
            version=VERSION_INITIAL,
        )

        self.session.add(adr)
        await self.session.flush()
        return adr

    async def get(self, adr_id: str) -> ADR | None:
        """Get ADR by ID."""
        result = await self.session.execute(select(ADR).where(ADR.id == adr_id))
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        skip: int = DEFAULT_OFFSET,
        limit: int = DEFAULT_LIMIT,
    ) -> tuple[list[ADR], int]:
        """List ADRs for a project."""
        query = select(ADR).where(ADR.project_id == project_id)

        if status:
            query = query.where(ADR.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = await _maybe_await(total_result.scalar())
        total = total or ZERO

        # Apply pagination
        query = query.order_by(ADR.date.desc(), ADR.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        scalars = await _maybe_await(result.scalars())
        rows = list(await _maybe_await(scalars.all()))  # type: ignore[call-overload,attr-defined]
        return rows, total  # type: ignore[return-value]

    async def update(self, adr_id: str, **updates: object) -> ADR | None:
        """Update an ADR with optimistic locking.

        Functional Requirements:
        - FR-QUAL-003
        - FR-QUAL-007

        User Stories:
        - US-FEAT-003
        - US-SPEC-004

        Epics:
        - EPIC-002
        - EPIC-005
        """

        async def do_update() -> ADR:
            adr = await self.get(adr_id)
            if not adr:
                msg = f"ADR {adr_id} not found"
                raise ValueError(msg)

            for key, value in updates.items():
                if hasattr(adr, key) and value is not None:
                    setattr(adr, key, value)

            adr.version += VERSION_INCREMENT
            self.session.add(adr)
            await self.session.flush()
            return adr

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete(self, adr_id: str) -> bool:
        """Delete an ADR."""
        result = await self.session.execute(delete(ADR).where(ADR.id == adr_id))
        await self.session.flush()
        return (getattr(result, "rowcount", ZERO) or ZERO) > ZERO

    async def verify_compliance(
        self,
        adr_id: str,
        compliance_score: float,
        verified_at: datetime | None = None,
    ) -> ADR | None:
        """Verify ADR compliance and update score."""
        adr = await self.get(adr_id)
        if not adr:
            return None

        adr.compliance_score = max(0.0, min(1.0, compliance_score))
        adr.last_verified_at = verified_at or datetime.now(UTC).isoformat()
        adr.version += 1

        self.session.add(adr)
        await self.session.flush()
        return adr

    async def link_requirements(self, adr_id: str, requirement_ids: list[str]) -> ADR | None:
        """Link requirements to an ADR."""
        adr = await self.get(adr_id)
        if not adr:
            return None

        adr.related_requirements = list(set(adr.related_requirements or []) | set(requirement_ids))
        adr.version += 1

        self.session.add(adr)
        await self.session.flush()
        return adr

    async def supersede(self, adr_id: str, superseded_by_number: str) -> ADR | None:
        """Mark ADR as superseded by another."""
        adr = await self.get(adr_id)
        if not adr:
            return None

        adr.superseded_by = superseded_by_number
        adr.status = "superseded"
        adr.version += 1

        self.session.add(adr)
        await self.session.flush()
        return adr


class ContractService:
    """Service for Design-by-Contract specifications."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        content: ContractContent,
        options: ContractOptions | None = None,
    ) -> Contract:
        """Create a new Contract.

        Functional Requirements:
        - FR-QUAL-001
        - FR-QUAL-005

        User Stories:
        - US-FEAT-001
        - US-SPEC-002

        Epics:
        - EPIC-002
        - EPIC-005
        """
        opts = options or ContractOptions()
        # Generate sequential contract number
        result = await self.session.execute(
            select(Contract).where(Contract.project_id == project_id).order_by(Contract.created_at.desc()).limit(1),
        )
        last_contract = await _maybe_await(result.scalar_one_or_none())

        if last_contract:
            try:
                last_num = int(str(last_contract.contract_number).replace("CONTRACT-", ""))  # type: ignore[attr-defined]
                next_num = last_num + VERSION_INCREMENT
            except ValueError:
                next_num = SEQUENCE_START
        else:
            next_num = SEQUENCE_START

        contract_number = f"CONTRACT-{next_num:0{SEQUENCE_PADDING}d}"

        contract = Contract(
            id=str(uuid.uuid4()),
            project_id=project_id,
            item_id=content.item_id,
            contract_number=contract_number,
            title=content.title,
            contract_type=content.contract_type,
            status="draft",
            preconditions=opts.preconditions or [],
            postconditions=opts.postconditions or [],
            invariants=opts.invariants or [],
            states=opts.states or [],
            transitions=opts.transitions or [],
            executable_spec=opts.executable_spec,
            spec_language=opts.spec_language,
            tags=opts.tags or [],
            version=VERSION_INITIAL,
        )

        self.session.add(contract)
        await self.session.flush()
        return contract

    async def get(self, contract_id: str) -> Contract | None:
        """Get Contract by ID."""
        result = await self.session.execute(select(Contract).where(Contract.id == contract_id))
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_project(
        self,
        project_id: str,
        contract_type: str | None = None,
        status: str | None = None,
        skip: int = DEFAULT_OFFSET,
        limit: int = DEFAULT_LIMIT,
    ) -> tuple[list[Contract], int]:
        """List contracts for a project."""
        query = select(Contract).where(Contract.project_id == project_id)

        if contract_type:
            query = query.where(Contract.contract_type == contract_type)

        if status:
            query = query.where(Contract.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = await _maybe_await(total_result.scalar())
        total = total or ZERO

        # Apply pagination
        query = query.order_by(Contract.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        scalars = await _maybe_await(result.scalars())
        rows = list(await _maybe_await(scalars.all()))  # type: ignore[call-overload,attr-defined]
        return rows, total  # type: ignore[return-value]

    async def list_by_item(self, item_id: str) -> list[Contract]:
        """List contracts for an item."""
        result = await self.session.execute(
            select(Contract).where(Contract.item_id == item_id).order_by(Contract.created_at.desc()),
        )
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())  # type: ignore[attr-defined]
        return list(rows)  # type: ignore[call-overload]

    async def update(self, contract_id: str, **updates: object) -> Contract | None:
        """Update a Contract with optimistic locking.

        Functional Requirements:
        - FR-QUAL-003
        - FR-QUAL-007

        User Stories:
        - US-FEAT-003
        - US-SPEC-004

        Epics:
        - EPIC-002
        - EPIC-005
        """

        async def do_update() -> Contract:
            contract = await self.get(contract_id)
            if not contract:
                msg = f"Contract {contract_id} not found"
                raise ValueError(msg)

            for key, value in updates.items():
                if hasattr(contract, key) and value is not None:
                    setattr(contract, key, value)

            contract.version += 1
            self.session.add(contract)
            await self.session.flush()
            return contract

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete(self, contract_id: str) -> bool:
        """Delete a Contract."""
        result = await self.session.execute(delete(Contract).where(Contract.id == contract_id))
        await self.session.flush()
        return (getattr(result, "rowcount", ZERO) or ZERO) > ZERO

    async def verify(self, contract_id: str, verification_result: dict[str, Any]) -> Contract | None:
        """Verify contract and store verification result."""
        contract = await self.get(contract_id)
        if not contract:
            return None

        contract.verification_result = verification_result
        contract.last_verified_at = datetime.now(UTC).isoformat()
        contract.version += 1

        self.session.add(contract)
        await self.session.flush()
        return contract

    async def execute_transition(self, contract_id: str, from_state: str, to_state: str) -> Contract | None:
        """Execute state transition in contract."""
        contract = await self.get(contract_id)
        if not contract:
            return None

        # Validate transition exists
        valid_transition = False
        for transition in contract.transitions or []:
            if transition.get("from") == from_state and transition.get("to") == to_state:
                valid_transition = True
                break

        if not valid_transition:
            return None

        # Update contract state (store in metadata)
        if not contract.metadata_:
            contract.metadata_ = {}

        contract.metadata_["current_state"] = to_state
        contract.version += 1

        self.session.add(contract)
        await self.session.flush()
        return contract


class FeatureService:
    """Service for BDD Features.

    Functional Requirements:
    - FR-QUAL-005
    - FR-QUAL-006
    - FR-QUAL-007
    - FR-QUAL-008

    User Stories:
    - US-FEAT-001
    - US-FEAT-002
    - US-FEAT-003
    - US-FEAT-004

    Epics:
    - EPIC-005
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        content: FeatureContent,
        options: FeatureOptions | None = None,
    ) -> Feature:
        """Create a new Feature.

        Functional Requirements:
        - FR-QUAL-001
        - FR-QUAL-005

        User Stories:
        - US-FEAT-001
        - US-SPEC-002

        Epics:
        - EPIC-002
        - EPIC-005
        """
        opts = options or FeatureOptions()
        # Generate sequential feature number
        result = await self.session.execute(
            select(Feature).where(Feature.project_id == project_id).order_by(Feature.created_at.desc()).limit(1),
        )
        last_feature = await _maybe_await(result.scalar_one_or_none())

        if last_feature:
            try:
                last_num = int(str(last_feature.feature_number).replace("FEAT-", ""))  # type: ignore[attr-defined]
                next_num = last_num + VERSION_INCREMENT
            except ValueError:
                next_num = SEQUENCE_START
        else:
            next_num = SEQUENCE_START

        feature_number = f"FEAT-{next_num:0{SEQUENCE_PADDING}d}"

        feature = Feature(
            id=str(uuid.uuid4()),
            project_id=project_id,
            feature_number=feature_number,
            name=content.name,
            description=opts.description,
            as_a=opts.as_a,
            i_want=opts.i_want,
            so_that=opts.so_that,
            status=opts.status,
            file_path=opts.file_path,
            tags=opts.tags or [],
            related_requirements=opts.related_requirements or [],
            related_adrs=opts.related_adrs or [],
            version=VERSION_INITIAL,
        )

        self.session.add(feature)
        await self.session.flush()
        return feature

    async def get(self, feature_id: str) -> Feature | None:
        """Get Feature by ID."""
        result = await self.session.execute(select(Feature).where(Feature.id == feature_id))
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        skip: int = DEFAULT_OFFSET,
        limit: int = DEFAULT_LIMIT,
    ) -> tuple[list[Feature], int]:
        """List features for a project."""
        query = select(Feature).where(Feature.project_id == project_id)

        if status:
            query = query.where(Feature.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = await _maybe_await(total_result.scalar())
        total = total or ZERO

        # Apply pagination
        query = query.order_by(Feature.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        scalars = await _maybe_await(result.scalars())
        rows = list(await _maybe_await(scalars.all()))  # type: ignore[call-overload,attr-defined]
        return rows, total  # type: ignore[return-value]

    async def update(self, feature_id: str, **updates: object) -> Feature | None:
        """Update a Feature with optimistic locking.

        Functional Requirements:
        - FR-QUAL-003
        - FR-QUAL-007

        User Stories:
        - US-FEAT-003
        - US-SPEC-004

        Epics:
        - EPIC-002
        - EPIC-005
        """

        async def do_update() -> Feature:
            feature = await self.get(feature_id)
            if not feature:
                msg = f"Feature {feature_id} not found"
                raise ValueError(msg)

            for key, value in updates.items():
                if hasattr(feature, key) and value is not None:
                    setattr(feature, key, value)

            feature.version += 1
            self.session.add(feature)
            await self.session.flush()
            return feature

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete(self, feature_id: str) -> bool:
        """Delete a Feature."""
        result = await self.session.execute(delete(Feature).where(Feature.id == feature_id))
        await self.session.flush()
        return (getattr(result, "rowcount", ZERO) or ZERO) > ZERO

    async def get_with_scenarios(self, feature_id: str) -> dict[str, Any] | None:
        """Get Feature with related scenarios."""
        feature = await self.get(feature_id)
        if not feature:
            return None

        # Get scenarios for this feature
        result = await self.session.execute(
            select(Scenario).where(Scenario.feature_id == feature_id).order_by(Scenario.created_at),
        )
        scalars = await _maybe_await(result.scalars())
        scenarios = list(await _maybe_await(scalars.all()))  # type: ignore[call-overload,attr-defined]

        return {
            "feature": feature,
            "scenarios": scenarios,
            "scenario_count": len(scenarios),
        }

    async def calculate_pass_rate(self, feature_id: str) -> float:
        """Calculate average pass rate across scenarios."""
        result = await self.session.execute(
            select(func.avg(Scenario.pass_rate)).where(Scenario.feature_id == feature_id),
        )
        avg_pass_rate = await _maybe_await(result.scalar())
        avg_pass_rate = avg_pass_rate or SCORE_MIN
        return float(avg_pass_rate)  # type: ignore[arg-type]


class ScenarioService:
    """Service for BDD Scenarios."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        feature_id: str,
        content: ScenarioContent,
        options: ScenarioOptions | None = None,
    ) -> Scenario:
        """Create a new Scenario.

        Functional Requirements:
        - FR-QUAL-001
        - FR-QUAL-005

        User Stories:
        - US-FEAT-001
        - US-SPEC-002

        Epics:
        - EPIC-002
        - EPIC-005
        """
        opts = options or ScenarioOptions()
        # Get feature to find project context
        feature = await self.session.execute(select(Feature).where(Feature.id == feature_id))
        feature_obj = await _maybe_await(feature.scalar_one_or_none())
        if not feature_obj:
            msg = f"Feature {feature_id} not found"
            raise ValueError(msg)

        # Generate sequential scenario number within feature
        result = await self.session.execute(
            select(Scenario).where(Scenario.feature_id == feature_id).order_by(Scenario.created_at.desc()).limit(1),
        )
        last_scenario = await _maybe_await(result.scalar_one_or_none())

        if last_scenario:
            try:
                last_num = int(str(last_scenario.scenario_number).split("-")[-1])  # type: ignore[attr-defined]
                next_num = last_num + VERSION_INCREMENT
            except (ValueError, IndexError):
                next_num = SEQUENCE_START
        else:
            next_num = SEQUENCE_START

        scenario_number = f"{feature_obj.feature_number!s}-SC-{next_num:03d}"  # type: ignore[attr-defined]

        scenario = Scenario(
            id=str(uuid.uuid4()),
            feature_id=feature_id,
            scenario_number=scenario_number,
            title=content.title,
            description=opts.description,
            gherkin_text=content.gherkin_text,
            is_outline=opts.is_outline,
            background=opts.background or [],
            given_steps=opts.given or [],
            when_steps=opts.when or [],
            then_steps=opts.then or [],
            examples=opts.examples,
            tags=opts.tags or [],
            requirement_ids=opts.requirement_ids or [],
            test_case_ids=opts.test_case_ids or [],
            status="draft",
            pass_rate=SCORE_MIN,
            version=VERSION_INITIAL,
        )

        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def get(self, scenario_id: str) -> Scenario | None:
        """Get Scenario by ID."""
        result = await self.session.execute(select(Scenario).where(Scenario.id == scenario_id))
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_feature(
        self,
        feature_id: str,
        status: str | None = None,
    ) -> list[Scenario]:
        """List scenarios for a feature."""
        query = select(Scenario).where(Scenario.feature_id == feature_id)

        if status:
            query = query.where(Scenario.status == status)

        result = await self.session.execute(query.order_by(Scenario.created_at))
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())  # type: ignore[attr-defined]
        return list(rows)  # type: ignore[call-overload]

    async def update(self, scenario_id: str, **updates: object) -> Scenario | None:
        """Update a Scenario with optimistic locking.

        Functional Requirements:
        - FR-QUAL-003
        - FR-QUAL-007

        User Stories:
        - US-FEAT-003
        - US-SPEC-004

        Epics:
        - EPIC-002
        - EPIC-005
        """

        async def do_update() -> Scenario:
            scenario = await self.get(scenario_id)
            if not scenario:
                msg = f"Scenario {scenario_id} not found"
                raise ValueError(msg)

            for key, value in updates.items():
                if hasattr(scenario, key) and value is not None:
                    setattr(scenario, key, value)

            scenario.version += 1
            self.session.add(scenario)
            await self.session.flush()
            return scenario

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete(self, scenario_id: str) -> bool:
        """Delete a Scenario."""
        result = await self.session.execute(delete(Scenario).where(Scenario.id == scenario_id))
        await self.session.flush()
        return (getattr(result, "rowcount", ZERO) or ZERO) > ZERO

    async def run(self, scenario_id: str, results: dict[str, Any]) -> Scenario | None:
        """Run scenario and record results."""
        scenario = await self.get(scenario_id)
        if not scenario:
            return None

        # Calculate pass rate from step results
        total_steps = len(scenario.given_steps or []) + len(scenario.when_steps or []) + len(scenario.then_steps or [])
        if total_steps > ZERO:
            passed_steps = results.get("passed_steps", ZERO)
            pass_rate = passed_steps / total_steps
        else:
            pass_rate = SCORE_MIN

        scenario.pass_rate = pass_rate
        scenario.status = "executed"
        scenario.version += VERSION_INCREMENT

        # Store run results in metadata
        if not scenario.metadata_:
            scenario.metadata_ = {}
        scenario.metadata_["last_run"] = results

        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def update_pass_rate(self, scenario_id: str, pass_rate: float) -> Scenario | None:
        """Update scenario pass rate."""
        scenario = await self.get(scenario_id)
        if not scenario:
            return None

        scenario.pass_rate = max(SCORE_MIN, min(SCORE_MAX, pass_rate))
        scenario.version += VERSION_INCREMENT

        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def link_test_cases(self, scenario_id: str, test_case_ids: list[str]) -> Scenario | None:
        """Link test cases to a scenario."""
        scenario = await self.get(scenario_id)
        if not scenario:
            return None

        scenario.test_case_ids = list(set(scenario.test_case_ids or []) | set(test_case_ids))
        scenario.version += VERSION_INCREMENT

        self.session.add(scenario)
        await self.session.flush()
        return scenario


class StepDefinitionService:
    """Service for BDD Step Definitions."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        content: StepDefinitionContent,
        options: StepDefinitionOptions | None = None,
    ) -> dict[str, Any]:
        """Create a new Step Definition.

        Functional Requirements:
        - FR-QUAL-001
        - FR-QUAL-005

        User Stories:
        - US-FEAT-001
        - US-SPEC-002

        Epics:
        - EPIC-002
        - EPIC-005
        """
        opts = options or StepDefinitionOptions()
        return {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "step_pattern": content.step_pattern,
            "step_type": content.step_type,  # given, when, then
            "implementation_code": content.implementation_code,
            "language": opts.language,
            "description": opts.description,
            "parameters": opts.parameters or [],
            "tags": opts.tags or [],
            "usage_count": ZERO,
            "created_at": datetime.now(UTC).isoformat(),
            "version": VERSION_INITIAL,
        }

    async def find_matching(
        self,
        _project_id: str,
        _step_text: str,
        _step_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Find step definitions matching text (mock implementation)."""
        # In a real implementation, this would query database with pattern matching
        # For now, return empty list as placeholder
        return []

    async def get(self, _step_id: str) -> dict[str, Any] | None:
        """Get Step Definition by ID."""
        # Placeholder implementation
        return None

    async def list_by_project(
        self,
        _project_id: str,
        _step_type: str | None = None,
        _skip: int = DEFAULT_OFFSET,
        _limit: int = DEFAULT_LIMIT,
    ) -> tuple[list[dict[str, Any]], int]:
        """List step definitions for a project."""
        # Placeholder implementation
        return [], 0

    async def update(self, _step_id: str, **_updates: object) -> dict[str, Any] | None:
        """Update a Step Definition.

        Functional Requirements:
        - FR-QUAL-003
        - FR-QUAL-007

        User Stories:
        - US-FEAT-003
        - US-SPEC-004

        Epics:
        - EPIC-002
        - EPIC-005
        """
        # Placeholder implementation
        return None

    async def delete(self, _step_id: str) -> bool:
        """Delete a Step Definition."""
        # Placeholder implementation
        return False

    async def increment_usage(self, _step_id: str) -> dict[str, Any] | None:
        """Increment usage count for a step definition."""
        # Placeholder implementation
        return None
