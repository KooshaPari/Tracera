"""Feature Service for TraceRTM."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import update_with_retry
from tracertm.models.specification import Feature
from tracertm.repositories.event_repository import EventRepository


@dataclass
class CreateFeatureInput:
    """Input for creating a feature (optional fields)."""

    description: str | None = None
    as_a: str | None = None
    i_want: str | None = None
    so_that: str | None = None
    status: str = "draft"
    tags: list[str] | None = None
    related_requirements: list[str] | None = None


class FeatureService:
    """Service for BDD Features."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def _log_event(
        self,
        project_id: str,
        feature_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        repo = EventRepository(self.session)
        await repo.log(
            project_id=project_id,
            event_type=event_type,
            entity_type="feature",
            entity_id=feature_id,
            data=data,
        )

    async def create_feature(
        self,
        project_id: str,
        name: str,
        options: CreateFeatureInput | None = None,
    ) -> Feature:
        """Create a new Feature."""
        opts = options or CreateFeatureInput()
        # Simple numbering
        result = await self.session.execute(
            select(Feature).where(Feature.project_id == project_id).order_by(Feature.created_at.desc()).limit(1),
        )
        last = result.scalar_one_or_none()

        if last:
            try:
                last_num = int(last.feature_number.replace("FEAT-", ""))
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        feature_number = f"FEAT-{next_num:04d}"

        feature = Feature(
            project_id=project_id,
            feature_number=feature_number,
            name=name,
            description=opts.description,
            as_a=opts.as_a,
            i_want=opts.i_want,
            so_that=opts.so_that,
            status=opts.status,
            tags=opts.tags or [],
            related_requirements=opts.related_requirements or [],
        )

        self.session.add(feature)
        await self.session.flush()
        await self._log_event(
            project_id=project_id,
            feature_id=feature.id,
            event_type="created",
            data={
                "description": "Feature created",
                "name": feature.name,
                "status": feature.status,
            },
        )
        await self.session.commit()
        await self.session.refresh(feature)
        return feature

    async def get_feature(self, feature_id: str) -> Feature | None:
        """Get Feature by ID."""
        result = await self.session.execute(select(Feature).where(Feature.id == feature_id))
        return result.scalar_one_or_none()

    async def list_features(self, project_id: str, status: str | None = None) -> list[Feature]:
        """List Features for a project."""
        query = select(Feature).where(Feature.project_id == project_id)

        if status:
            query = query.where(Feature.status == status)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_feature(self, feature_id: str, **updates: object) -> Feature | None:
        """Update a Feature."""

        async def do_update() -> Feature:
            feature = await self.get_feature(feature_id)
            if not feature:
                msg = f"Feature {feature_id} not found"
                raise ValueError(msg)

            before = {key: getattr(feature, key, None) for key in updates}
            for key, value in updates.items():
                if hasattr(feature, key):
                    setattr(feature, key, value)

            feature.version += 1
            self.session.add(feature)
            await self._log_event(
                project_id=feature.project_id,
                feature_id=feature.id,
                event_type="updated",
                data={
                    "description": "Feature updated",
                    "changes": {key: {"from": before.get(key), "to": updates.get(key)} for key in updates},
                    "from_value": before.get("status"),
                    "to_value": updates.get("status"),
                },
            )
            await self.session.commit()
            await self.session.refresh(feature)
            return feature

        try:
            return await update_with_retry(do_update)
        except ValueError:
            return None

    async def delete_feature(self, feature_id: str) -> bool:
        """Delete a Feature."""
        feature = await self.get_feature(feature_id)
        if not feature:
            return False
        await self._log_event(
            project_id=feature.project_id,
            feature_id=feature_id,
            event_type="deleted",
            data={
                "description": "Feature deleted",
                "name": feature.name,
                "status": feature.status,
            },
        )
        result = await self.session.execute(delete(Feature).where(Feature.id == feature_id))
        await self.session.commit()
        return getattr(result, "rowcount", 0) > 0
