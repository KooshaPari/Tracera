"""ADR Service for TraceRTM."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import update_with_retry
from tracertm.models.specification import ADR
from tracertm.repositories.event_repository import EventRepository


class ADRService:
    """Service for Architecture Decision Records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def _log_event(
        self,
        project_id: str,
        adr_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        repo = EventRepository(self.session)
        await repo.log(
            project_id=project_id,
            event_type=event_type,
            entity_type="adr",
            entity_id=adr_id,
            data=data,
        )

    async def create_adr(
        self,
        project_id: str,
        title: str,
        context: str,
        decision: str,
        consequences: str,
        status: str = "proposed",
        decision_drivers: list[str] | None = None,
        considered_options: list[dict] | None = None,
        related_requirements: list[str] | None = None,
        related_adrs: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> ADR:
        """Create a new ADR."""
        # Generate ADR number (simplistic implementation)
        # Ideally this should be robust against concurrency or use a sequence
        result = await self.session.execute(
            select(ADR).where(ADR.project_id == project_id).order_by(ADR.created_at.desc()).limit(1),
        )
        last_adr = result.scalar_one_or_none()

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
            tags=tags or [],
            date=datetime.now(UTC).date(),
        )

        self.session.add(adr)
        await self.session.flush()
        await self._log_event(
            project_id=project_id,
            adr_id=adr.id,
            event_type="created",
            data={
                "description": "ADR created",
                "title": adr.title,
                "status": adr.status,
            },
        )
        await self.session.commit()
        await self.session.refresh(adr)
        return adr

    async def get_adr(self, adr_id: str) -> ADR | None:
        """Get ADR by ID."""
        result = await self.session.execute(select(ADR).where(ADR.id == adr_id))
        return result.scalar_one_or_none()

    async def list_adrs(self, project_id: str, status: str | None = None) -> list[ADR]:
        """List ADRs for a project."""
        query = select(ADR).where(ADR.project_id == project_id).order_by(ADR.adr_number.desc())

        if status:
            query = query.where(ADR.status == status)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_adr(self, adr_id: str, **updates: object) -> ADR | None:
        """Update an ADR."""

        async def do_update() -> ADR:
            adr = await self.get_adr(adr_id)
            if not adr:
                msg = f"ADR {adr_id} not found"
                raise ValueError(msg)

            before = {key: getattr(adr, key, None) for key in updates}
            for key, value in updates.items():
                if hasattr(adr, key):
                    setattr(adr, key, value)

            adr.version += 1
            self.session.add(adr)
            await self._log_event(
                project_id=adr.project_id,
                adr_id=adr.id,
                event_type="updated",
                data={
                    "description": "ADR updated",
                    "changes": {key: {"from": before.get(key), "to": updates.get(key)} for key in updates},
                    "from_value": before.get("status"),
                    "to_value": updates.get("status"),
                },
            )
            await self.session.commit()
            await self.session.refresh(adr)
            return adr

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete_adr(self, adr_id: str) -> bool:
        """Delete an ADR."""
        adr = await self.get_adr(adr_id)
        if not adr:
            return False
        await self._log_event(
            project_id=adr.project_id,
            adr_id=adr_id,
            event_type="deleted",
            data={
                "description": "ADR deleted",
                "title": adr.title,
                "status": adr.status,
            },
        )
        result = await self.session.execute(delete(ADR).where(ADR.id == adr_id))
        await self.session.commit()
        return getattr(result, "rowcount", 0) > 0
