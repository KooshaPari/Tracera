"""Project repository for TraceRTM."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.project import Project


class ProjectRepository:
    """Repository for Project CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        description: str | None = None,
        metadata: dict | None = None,
    ) -> Project:
        """Create new project."""
        project = Project(
            id=str(uuid4()),
            name=name,
            description=description,
            project_metadata=metadata or {},
        )
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: str) -> Project | None:
        """Get project by ID."""
        # Use raw SQL to avoid model column mismatches with database schema
        from sqlalchemy import text
        result = await self.session.execute(
            text("SELECT id, name, metadata, created_at, updated_at FROM projects WHERE id = :project_id AND deleted_at IS NULL"),
            {"project_id": project_id}
        )
        row = result.fetchone()
        if not row:
            return None
        
        # Create a Project-like object that works with the actual schema
        project = type('Project', (), {})()  # type: ignore
        project.id = str(row.id)
        project.name = row.name
        project.project_metadata = row.metadata if row.metadata else {}
        project.metadata = project.project_metadata  # Alias for compatibility
        project.created_at = row.created_at
        project.updated_at = row.updated_at
        # Add description property that reads from metadata
        project.description = None
        if isinstance(project.project_metadata, dict):
            project.description = project.project_metadata.get("description")
        return project

    async def get_by_name(self, name: str) -> Project | None:
        """Get project by name."""
        result = await self.session.execute(select(Project).where(Project.name == name))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Project]:
        """Get all projects."""
        # Use raw SQL to avoid model column mismatches with database schema
        from sqlalchemy import text
        result = await self.session.execute(
            text("SELECT id, name, metadata, created_at, updated_at FROM projects WHERE deleted_at IS NULL")
        )
        projects = []
        for row in result:
            # Create a Project-like object that works with the actual schema
            # Use type: ignore to bypass SQLAlchemy model validation
            project = type('Project', (), {})()  # type: ignore
            project.id = str(row.id)
            project.name = row.name
            project.project_metadata = row.metadata if row.metadata else {}
            project.metadata = project.project_metadata  # Alias for compatibility
            project.created_at = row.created_at
            project.updated_at = row.updated_at
            # Add description property that reads from metadata
            project.description = None
            if isinstance(project.project_metadata, dict):
                project.description = project.project_metadata.get("description")
            projects.append(project)
        return projects

    async def update(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        metadata: dict | None = None,
    ) -> Project | None:
        """Update project."""
        project = await self.get_by_id(project_id)
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
