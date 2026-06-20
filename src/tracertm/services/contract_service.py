"""Contract Service for TraceRTM.

Functional Requirements: FR-VERIF-010
"""

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import update_with_retry
from tracertm.models.specification import Contract
from tracertm.repositories.event_repository import EventRepository


class ContractService:
    """Service for Contract Management."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def _log_event(
        self,
        project_id: str,
        contract_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        repo = EventRepository(self.session)
        await repo.log(
            project_id=project_id,
            event_type=event_type,
            entity_type="contract",
            entity_id=contract_id,
            data=data,
        )

    async def create_contract(
        self,
        project_id: str,
        item_id: str,
        title: str,
        contract_type: str,
        preconditions: list[dict] | None = None,
        postconditions: list[dict] | None = None,
        invariants: list[dict] | None = None,
        status: str = "draft",
        tags: list[str] | None = None,
    ) -> Contract:
        """Create a new Contract."""
        # Simple numbering
        result = await self.session.execute(
            select(Contract).where(Contract.project_id == project_id).order_by(Contract.created_at.desc()).limit(1),
        )
        last = result.scalar_one_or_none()

        if last:
            try:
                last_num = int(last.contract_number.replace("CTR-", ""))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        contract_number = f"CTR-{next_num:04d}"

        contract = Contract(
            project_id=project_id,
            item_id=item_id,
            contract_number=contract_number,
            title=title,
            contract_type=contract_type,
            status=status,
            preconditions=preconditions or [],
            postconditions=postconditions or [],
            invariants=invariants or [],
            tags=tags or [],
        )

        self.session.add(contract)
        await self.session.flush()
        await self._log_event(
            project_id=project_id,
            contract_id=contract.id,
            event_type="created",
            data={
                "description": "Contract created",
                "title": contract.title,
                "status": contract.status,
                "contract_type": contract.contract_type,
            },
        )
        await self.session.commit()
        await self.session.refresh(contract)
        return contract

    async def get_contract(self, contract_id: str) -> Contract | None:
        """Get Contract by ID."""
        result = await self.session.execute(select(Contract).where(Contract.id == contract_id))
        return result.scalar_one_or_none()

    async def list_contracts(self, project_id: str, item_id: str | None = None) -> list[Contract]:
        """List Contracts for a project or specific item."""
        query = select(Contract).where(Contract.project_id == project_id)

        if item_id:
            query = query.where(Contract.item_id == item_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_contract(self, contract_id: str, **updates: object) -> Contract | None:
        """Update a Contract."""

        async def do_update() -> Contract:
            contract = await self.get_contract(contract_id)
            if not contract:
                msg = f"Contract {contract_id} not found"
                raise ValueError(msg)

            before = {key: getattr(contract, key, None) for key in updates}
            for key, value in updates.items():
                if hasattr(contract, key):
                    setattr(contract, key, value)

            contract.version += 1
            self.session.add(contract)
            await self._log_event(
                project_id=contract.project_id,
                contract_id=contract.id,
                event_type="updated",
                data={
                    "description": "Contract updated",
                    "changes": {key: {"from": before.get(key), "to": updates.get(key)} for key in updates},
                    "from_value": before.get("status"),
                    "to_value": updates.get("status"),
                },
            )
            await self.session.commit()
            await self.session.refresh(contract)
            return contract

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete_contract(self, contract_id: str) -> bool:
        """Delete a Contract."""
        contract = await self.get_contract(contract_id)
        if not contract:
            return False
        await self._log_event(
            project_id=contract.project_id,
            contract_id=contract_id,
            event_type="deleted",
            data={
                "description": "Contract deleted",
                "title": contract.title,
                "status": contract.status,
            },
        )
        result = await self.session.execute(delete(Contract).where(Contract.id == contract_id))
        await self.session.commit()
        return getattr(result, "rowcount", 0) > 0
