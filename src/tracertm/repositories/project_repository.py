"""Project repository for TraceRTM."""

import uuid
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.project import Project


class ProjectRepository:
    """Repository for Project CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        name: str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
        account_id: str | None = None,
    ) -> Project:
        """Create new project."""
        project = Project(
            id=str(uuid4()),
            name=name,
            description=description,
            project_metadata=metadata or {},
            account_id=account_id,
        )
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: str | uuid.UUID) -> Project | None:
        """Get project by ID."""
        query = select(Project).where(Project.id == project_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Project | None:
        """Get project by name."""
        query = select(Project).where(Project.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Project]:
        """Get all projects."""
        query = select(Project)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        project_id: str | uuid.UUID,
        name: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Project | None:
        """Update project."""
        # Get project using ORM for tracking
        query = select(Project).where(Project.id == project_id)
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if metadata is not None:
            project.project_metadata = metadata

        await self.session.flush()
        await self.session.refresh(project)
        return project
