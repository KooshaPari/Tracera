"""Scenario Service for TraceRTM.

Functional Requirements: FR-VERIF-005
"""

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import update_with_retry
from tracertm.models.specification import Feature, Scenario
from tracertm.repositories.event_repository import EventRepository


class ScenarioService:
    """Service for BDD Scenarios."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def _get_project_id(self, feature_id: str) -> str | None:
        result = await self.session.execute(select(Feature).where(Feature.id == feature_id))
        feature = result.scalar_one_or_none()
        return feature.project_id if feature else None

    async def _log_event(
        self,
        project_id: str,
        scenario_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        repo = EventRepository(self.session)
        await repo.log(
            project_id=project_id,
            event_type=event_type,
            entity_type="scenario",
            entity_id=scenario_id,
            data=data,
        )

    async def create_scenario(
        self,
        feature_id: str,
        title: str,
        gherkin_text: str,
        description: str | None = None,
        given_steps: list[dict] | None = None,
        when_steps: list[dict] | None = None,
        then_steps: list[dict] | None = None,
        status: str = "draft",
        tags: list[str] | None = None,
        is_outline: bool = False,
        examples: dict | None = None,
    ) -> Scenario:
        """Create a new Scenario."""
        # Simple numbering relative to feature or global? Let's do global per project logic implicitly
        # Or just simple SCEN-XXXX for now.

        # We need to find the project ID via feature to scope properly, but for speed just counting total scenarios
        # or just random ID. Let's do a simple count on the table for now.
        result = await self.session.execute(select(Scenario).order_by(Scenario.created_at.desc()).limit(1))
        last = result.scalar_one_or_none()

        if last:
            try:
                last_num = int(last.scenario_number.replace("SCEN-", ""))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        scenario_number = f"SCEN-{next_num:04d}"

        scenario = Scenario(
            feature_id=feature_id,
            scenario_number=scenario_number,
            title=title,
            description=description,
            gherkin_text=gherkin_text,
            given_steps=given_steps or [],
            when_steps=when_steps or [],
            then_steps=then_steps or [],
            status=status,
            tags=tags or [],
            is_outline=is_outline,
            examples=examples,
        )

        self.session.add(scenario)
        await self.session.flush()
        project_id = await self._get_project_id(feature_id)
        if project_id:
            await self._log_event(
                project_id=project_id,
                scenario_id=scenario.id,
                event_type="created",
                data={
                    "description": "Scenario created",
                    "title": scenario.title,
                    "status": scenario.status,
                },
            )
        await self.session.commit()
        await self.session.refresh(scenario)
        return scenario

    async def get_scenario(self, scenario_id: str) -> Scenario | None:
        """Get Scenario by ID."""
        result = await self.session.execute(select(Scenario).where(Scenario.id == scenario_id))
        return result.scalar_one_or_none()

    async def list_scenarios(self, feature_id: str) -> list[Scenario]:
        """List Scenarios for a Feature."""
        query = select(Scenario).where(Scenario.feature_id == feature_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_scenario(self, scenario_id: str, **updates: object) -> Scenario | None:
        """Update a Scenario."""

        async def do_update() -> Scenario:
            scenario = await self.get_scenario(scenario_id)
            if not scenario:
                msg = f"Scenario {scenario_id} not found"
                raise ValueError(msg)

            before = {key: getattr(scenario, key, None) for key in updates}
            for key, value in updates.items():
                if hasattr(scenario, key):
                    setattr(scenario, key, value)

            scenario.version += 1
            self.session.add(scenario)
            project_id = await self._get_project_id(scenario.feature_id)
            if project_id:
                await self._log_event(
                    project_id=project_id,
                    scenario_id=scenario.id,
                    event_type="updated",
                    data={
                        "description": "Scenario updated",
                        "changes": {key: {"from": before.get(key), "to": updates.get(key)} for key in updates},
                        "from_value": before.get("status"),
                        "to_value": updates.get("status"),
                    },
                )
            await self.session.commit()
            await self.session.refresh(scenario)
            return scenario

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a Scenario."""
        scenario = await self.get_scenario(scenario_id)
        if not scenario:
            return False
        project_id = await self._get_project_id(scenario.feature_id)
        if project_id:
            await self._log_event(
                project_id=project_id,
                scenario_id=scenario_id,
                event_type="deleted",
                data={
                    "description": "Scenario deleted",
                    "title": scenario.title,
                    "status": scenario.status,
                },
            )
        result = await self.session.execute(delete(Scenario).where(Scenario.id == scenario_id))
        await self.session.commit()
        return (getattr(result, "rowcount", 0) or 0) > 0
