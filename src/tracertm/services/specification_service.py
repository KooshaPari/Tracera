"""
Services for specification entities (ADR, Contract, Feature, Scenario, StepDefinition).
"""

from __future__ import annotations

import uuid
from datetime import date as date_type
from datetime import datetime
from typing import Any, Optional
import inspect

from sqlalchemy import select, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import update_with_retry
from tracertm.models.specification import ADR, Contract, Feature, Scenario


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


class ADRService:
    """Service for Architecture Decision Records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        title: str,
        context: str,
        decision: str,
        consequences: str,
        status: str = "proposed",
        decision_drivers: Optional[list[str]] = None,
        considered_options: Optional[list[dict]] = None,
        related_requirements: Optional[list[str]] = None,
        related_adrs: Optional[list[str]] = None,
        stakeholders: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        date_value: Optional[date_type] = None,
    ) -> ADR:
        """Create a new ADR."""
        # Generate sequential ADR number
        result = await self.session.execute(
            select(ADR)
            .where(ADR.project_id == project_id)
            .order_by(ADR.created_at.desc())
            .limit(1)
        )
        last_adr = await _maybe_await(result.scalar_one_or_none())

        if last_adr:
            try:
                last_num = int(last_adr.adr_number.replace("ADR-", ""))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        adr_number = f"ADR-{next_num:04d}"

        adr = ADR(
            id=str(uuid.uuid4()),
            project_id=project_id,
            adr_number=adr_number,
            title=title,
            status=status,
            context=context,
            decision=decision,
            consequences=consequences,
            decision_drivers=decision_drivers or [],
            considered_options=considered_options or [],
            related_requirements=related_requirements or [],
            related_adrs=related_adrs or [],
            stakeholders=stakeholders or [],
            tags=tags or [],
            date=date_value or datetime.now().date(),
            version=1,
        )

        self.session.add(adr)
        await self.session.flush()
        return adr

    async def get(self, adr_id: str) -> Optional[ADR]:
        """Get ADR by ID."""
        result = await self.session.execute(
            select(ADR).where(ADR.id == adr_id)
        )
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_project(
        self,
        project_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ADR], int]:
        """List ADRs for a project."""
        query = select(ADR).where(ADR.project_id == project_id)

        if status:
            query = query.where(ADR.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = await _maybe_await(total_result.scalar())
        total = total or 0

        # Apply pagination
        query = query.order_by(ADR.date.desc(), ADR.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())
        return list(rows), total

    async def update(self, adr_id: str, **updates: Any) -> Optional[ADR]:
        """Update an ADR with optimistic locking."""
        async def do_update() -> ADR:
            adr = await self.get(adr_id)
            if not adr:
                raise ValueError(f"ADR {adr_id} not found")

            for key, value in updates.items():
                if hasattr(adr, key) and value is not None:
                    setattr(adr, key, value)

            adr.version += 1
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
        return (result.rowcount or 0) > 0

    async def verify_compliance(
        self, adr_id: str, compliance_score: float, verified_at: Optional[datetime] = None
    ) -> Optional[ADR]:
        """Verify ADR compliance and update score."""
        adr = await self.get(adr_id)
        if not adr:
            return None

        adr.compliance_score = max(0.0, min(1.0, compliance_score))
        adr.last_verified_at = verified_at or datetime.now().isoformat()
        adr.version += 1

        self.session.add(adr)
        await self.session.flush()
        return adr

    async def link_requirements(
        self, adr_id: str, requirement_ids: list[str]
    ) -> Optional[ADR]:
        """Link requirements to an ADR."""
        adr = await self.get(adr_id)
        if not adr:
            return None

        adr.related_requirements = list(set(adr.related_requirements or []) | set(requirement_ids))
        adr.version += 1

        self.session.add(adr)
        await self.session.flush()
        return adr

    async def supersede(
        self, adr_id: str, superseded_by_number: str
    ) -> Optional[ADR]:
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

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        item_id: str,
        title: str,
        contract_type: str,
        preconditions: Optional[list[dict]] = None,
        postconditions: Optional[list[dict]] = None,
        invariants: Optional[list[dict]] = None,
        states: Optional[list[str]] = None,
        transitions: Optional[list[dict]] = None,
        executable_spec: Optional[str] = None,
        spec_language: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Contract:
        """Create a new Contract."""
        # Generate sequential contract number
        result = await self.session.execute(
            select(Contract)
            .where(Contract.project_id == project_id)
            .order_by(Contract.created_at.desc())
            .limit(1)
        )
        last_contract = await _maybe_await(result.scalar_one_or_none())

        if last_contract:
            try:
                last_num = int(last_contract.contract_number.replace("CONTRACT-", ""))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        contract_number = f"CONTRACT-{next_num:04d}"

        contract = Contract(
            id=str(uuid.uuid4()),
            project_id=project_id,
            item_id=item_id,
            contract_number=contract_number,
            title=title,
            contract_type=contract_type,
            status="draft",
            preconditions=preconditions or [],
            postconditions=postconditions or [],
            invariants=invariants or [],
            states=states or [],
            transitions=transitions or [],
            executable_spec=executable_spec,
            spec_language=spec_language,
            tags=tags or [],
            version=1,
        )

        self.session.add(contract)
        await self.session.flush()
        return contract

    async def get(self, contract_id: str) -> Optional[Contract]:
        """Get Contract by ID."""
        result = await self.session.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_project(
        self,
        project_id: str,
        contract_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
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
        total = total or 0

        # Apply pagination
        query = query.order_by(Contract.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())
        return list(rows), total

    async def list_by_item(self, item_id: str) -> list[Contract]:
        """List contracts for an item."""
        result = await self.session.execute(
            select(Contract)
            .where(Contract.item_id == item_id)
            .order_by(Contract.created_at.desc())
        )
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())
        return list(rows)

    async def update(self, contract_id: str, **updates: Any) -> Optional[Contract]:
        """Update a Contract with optimistic locking."""
        async def do_update() -> Contract:
            contract = await self.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")

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
        result = await self.session.execute(
            delete(Contract).where(Contract.id == contract_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def verify(
        self, contract_id: str, verification_result: dict[str, Any]
    ) -> Optional[Contract]:
        """Verify contract and store verification result."""
        contract = await self.get(contract_id)
        if not contract:
            return None

        contract.verification_result = verification_result
        contract.last_verified_at = datetime.now().isoformat()
        contract.version += 1

        self.session.add(contract)
        await self.session.flush()
        return contract

    async def execute_transition(
        self, contract_id: str, from_state: str, to_state: str
    ) -> Optional[Contract]:
        """Execute state transition in contract."""
        contract = await self.get(contract_id)
        if not contract:
            return None

        # Validate transition exists
        valid_transition = False
        for transition in contract.transitions or []:
            if (
                transition.get("from") == from_state
                and transition.get("to") == to_state
            ):
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
    """Service for BDD Features."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        as_a: Optional[str] = None,
        i_want: Optional[str] = None,
        so_that: Optional[str] = None,
        status: str = "draft",
        file_path: Optional[str] = None,
        tags: Optional[list[str]] = None,
        related_requirements: Optional[list[str]] = None,
        related_adrs: Optional[list[str]] = None,
    ) -> Feature:
        """Create a new Feature."""
        # Generate sequential feature number
        result = await self.session.execute(
            select(Feature)
            .where(Feature.project_id == project_id)
            .order_by(Feature.created_at.desc())
            .limit(1)
        )
        last_feature = await _maybe_await(result.scalar_one_or_none())

        if last_feature:
            try:
                last_num = int(last_feature.feature_number.replace("FEAT-", ""))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        feature_number = f"FEAT-{next_num:04d}"

        feature = Feature(
            id=str(uuid.uuid4()),
            project_id=project_id,
            feature_number=feature_number,
            name=name,
            description=description,
            as_a=as_a,
            i_want=i_want,
            so_that=so_that,
            status=status,
            file_path=file_path,
            tags=tags or [],
            related_requirements=related_requirements or [],
            related_adrs=related_adrs or [],
            version=1,
        )

        self.session.add(feature)
        await self.session.flush()
        return feature

    async def get(self, feature_id: str) -> Optional[Feature]:
        """Get Feature by ID."""
        result = await self.session.execute(
            select(Feature).where(Feature.id == feature_id)
        )
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_project(
        self,
        project_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Feature], int]:
        """List features for a project."""
        query = select(Feature).where(Feature.project_id == project_id)

        if status:
            query = query.where(Feature.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = await _maybe_await(total_result.scalar())
        total = total or 0

        # Apply pagination
        query = query.order_by(Feature.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())
        return list(rows), total

    async def update(self, feature_id: str, **updates: Any) -> Optional[Feature]:
        """Update a Feature with optimistic locking."""
        async def do_update() -> Feature:
            feature = await self.get(feature_id)
            if not feature:
                raise ValueError(f"Feature {feature_id} not found")

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
        result = await self.session.execute(
            delete(Feature).where(Feature.id == feature_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def get_with_scenarios(self, feature_id: str) -> Optional[dict[str, Any]]:
        """Get Feature with related scenarios."""
        feature = await self.get(feature_id)
        if not feature:
            return None

        # Get scenarios for this feature
        result = await self.session.execute(
            select(Scenario)
            .where(Scenario.feature_id == feature_id)
            .order_by(Scenario.created_at)
        )
        scalars = await _maybe_await(result.scalars())
        scenarios = list(await _maybe_await(scalars.all()))

        return {
            "feature": feature,
            "scenarios": scenarios,
            "scenario_count": len(scenarios),
        }

    async def calculate_pass_rate(self, feature_id: str) -> float:
        """Calculate average pass rate across scenarios."""
        result = await self.session.execute(
            select(func.avg(Scenario.pass_rate))
            .where(Scenario.feature_id == feature_id)
        )
        avg_pass_rate = await _maybe_await(result.scalar())
        avg_pass_rate = avg_pass_rate or 0.0
        return float(avg_pass_rate)


class ScenarioService:
    """Service for BDD Scenarios."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        feature_id: str,
        title: str,
        gherkin_text: str,
        description: Optional[str] = None,
        is_outline: bool = False,
        background: Optional[list[dict]] = None,
        given_steps: Optional[list[dict]] = None,
        when_steps: Optional[list[dict]] = None,
        then_steps: Optional[list[dict]] = None,
        examples: Optional[dict] = None,
        tags: Optional[list[str]] = None,
        requirement_ids: Optional[list[str]] = None,
        test_case_ids: Optional[list[str]] = None,
    ) -> Scenario:
        """Create a new Scenario."""
        # Get feature to find project context
        feature = await self.session.execute(
            select(Feature).where(Feature.id == feature_id)
        )
        feature_obj = await _maybe_await(feature.scalar_one_or_none())
        if not feature_obj:
            raise ValueError(f"Feature {feature_id} not found")

        # Generate sequential scenario number within feature
        result = await self.session.execute(
            select(Scenario)
            .where(Scenario.feature_id == feature_id)
            .order_by(Scenario.created_at.desc())
            .limit(1)
        )
        last_scenario = await _maybe_await(result.scalar_one_or_none())

        if last_scenario:
            try:
                last_num = int(last_scenario.scenario_number.split("-")[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1

        scenario_number = f"{feature_obj.feature_number}-SC-{next_num:03d}"

        scenario = Scenario(
            id=str(uuid.uuid4()),
            feature_id=feature_id,
            scenario_number=scenario_number,
            title=title,
            description=description,
            gherkin_text=gherkin_text,
            is_outline=is_outline,
            background=background or [],
            given_steps=given_steps or [],
            when_steps=when_steps or [],
            then_steps=then_steps or [],
            examples=examples,
            tags=tags or [],
            requirement_ids=requirement_ids or [],
            test_case_ids=test_case_ids or [],
            status="draft",
            pass_rate=0.0,
            version=1,
        )

        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def get(self, scenario_id: str) -> Optional[Scenario]:
        """Get Scenario by ID."""
        result = await self.session.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        return await _maybe_await(result.scalar_one_or_none())

    async def list_by_feature(
        self,
        feature_id: str,
        status: Optional[str] = None,
    ) -> list[Scenario]:
        """List scenarios for a feature."""
        query = select(Scenario).where(Scenario.feature_id == feature_id)

        if status:
            query = query.where(Scenario.status == status)

        result = await self.session.execute(
            query.order_by(Scenario.created_at)
        )
        scalars = await _maybe_await(result.scalars())
        rows = await _maybe_await(scalars.all())
        return list(rows)

    async def update(self, scenario_id: str, **updates: Any) -> Optional[Scenario]:
        """Update a Scenario with optimistic locking."""
        async def do_update() -> Scenario:
            scenario = await self.get(scenario_id)
            if not scenario:
                raise ValueError(f"Scenario {scenario_id} not found")

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
        result = await self.session.execute(
            delete(Scenario).where(Scenario.id == scenario_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def run(self, scenario_id: str, results: dict[str, Any]) -> Optional[Scenario]:
        """Run scenario and record results."""
        scenario = await self.get(scenario_id)
        if not scenario:
            return None

        # Calculate pass rate from step results
        total_steps = len(scenario.given_steps or []) + len(scenario.when_steps or []) + len(scenario.then_steps or [])
        if total_steps > 0:
            passed_steps = results.get("passed_steps", 0)
            pass_rate = passed_steps / total_steps
        else:
            pass_rate = 0.0

        scenario.pass_rate = pass_rate
        scenario.status = "executed"
        scenario.version += 1

        # Store run results in metadata
        if not scenario.metadata_:
            scenario.metadata_ = {}
        scenario.metadata_["last_run"] = results

        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def update_pass_rate(self, scenario_id: str, pass_rate: float) -> Optional[Scenario]:
        """Update scenario pass rate."""
        scenario = await self.get(scenario_id)
        if not scenario:
            return None

        scenario.pass_rate = max(0.0, min(1.0, pass_rate))
        scenario.version += 1

        self.session.add(scenario)
        await self.session.flush()
        return scenario

    async def link_test_cases(
        self, scenario_id: str, test_case_ids: list[str]
    ) -> Optional[Scenario]:
        """Link test cases to a scenario."""
        scenario = await self.get(scenario_id)
        if not scenario:
            return None

        scenario.test_case_ids = list(set(scenario.test_case_ids or []) | set(test_case_ids))
        scenario.version += 1

        self.session.add(scenario)
        await self.session.flush()
        return scenario


class StepDefinitionService:
    """Service for BDD Step Definitions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        project_id: str,
        step_pattern: str,
        step_type: str,
        implementation_code: str,
        language: str = "python",
        description: Optional[str] = None,
        parameters: Optional[list[dict]] = None,
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Create a new Step Definition."""
        step_definition = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "step_pattern": step_pattern,
            "step_type": step_type,  # given, when, then
            "implementation_code": implementation_code,
            "language": language,
            "description": description,
            "parameters": parameters or [],
            "tags": tags or [],
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
            "version": 1,
        }
        return step_definition

    async def find_matching(
        self,
        project_id: str,
        step_text: str,
        step_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Find step definitions matching text (mock implementation)."""
        # In a real implementation, this would query database with pattern matching
        # For now, return empty list as placeholder
        return []

    async def get(self, step_id: str) -> Optional[dict[str, Any]]:
        """Get Step Definition by ID."""
        # Placeholder implementation
        return None

    async def list_by_project(
        self,
        project_id: str,
        step_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """List step definitions for a project."""
        # Placeholder implementation
        return [], 0

    async def update(self, step_id: str, **updates: Any) -> Optional[dict[str, Any]]:
        """Update a Step Definition."""
        # Placeholder implementation
        return None

    async def delete(self, step_id: str) -> bool:
        """Delete a Step Definition."""
        # Placeholder implementation
        return False

    async def increment_usage(self, step_id: str) -> Optional[dict[str, Any]]:
        """Increment usage count for a step definition."""
        # Placeholder implementation
        return None
