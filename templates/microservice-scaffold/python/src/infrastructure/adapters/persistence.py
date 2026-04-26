"""PostgreSQL adapter - wraps SQLAlchemy (Wrap-Over pattern)."""
import json
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..domain.entities import Entity
from ..domain.ports import Repository
from ..domain.errors import NotFoundError
from ..logging import logger


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


class EntityModel(Base):
    """SQLAlchemy entity model."""

    __tablename__ = "entities"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class PostgresRepository(Repository):
    """PostgreSQL repository adapter."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entity: Entity) -> None:
        """Save an entity."""
        try:
            model = EntityModel(
                id=entity.id,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
            self._session.add(model)
            await self._session.commit()
            logger.info("entity_saved", id=str(entity.id))
        except Exception as e:
            await self._session.rollback()
            logger.error("entity_save_failed", id=str(entity.id), error=str(e))
            raise

    async def find_by_id(self, id: UUID) -> Entity | None:
        """Find an entity by ID."""
        result = await self._session.get(EntityModel, id)
        if result is None:
            return None
        return Entity(id=result.id, created_at=result.created_at, updated_at=result.updated_at)

    async def delete(self, id: UUID) -> None:
        """Delete an entity."""
        result = await self._session.get(EntityModel, id)
        if result is None:
            raise NotFoundError(str(id))
        await self._session.delete(result)
        await self._session.commit()

    async def list(self, page: int = 1, page_size: int = 20) -> list[Entity]:
        """List entities with pagination."""
        offset = (page - 1) * page_size
        result = await self._session.execute(
            f"SELECT * FROM entities ORDER BY created_at DESC LIMIT {page_size} OFFSET {offset}"
        )
        rows = result.fetchall()
        return [
            Entity(id=row[0], created_at=row[1], updated_at=row[2])
            for row in rows
        ]


class PostgresAdapter:
    """PostgreSQL adapter factory."""

    def __init__(self, database_url: str):
        self._engine = create_async_engine(database_url, echo=False)
        self._session_maker = async_sessionmaker(self._engine, class_=AsyncSession)

    async def create_session(self) -> AsyncSession:
        """Create a new session."""
        return self._session_maker()

    async def close(self) -> None:
        """Close the adapter."""
        await self._engine.dispose()
