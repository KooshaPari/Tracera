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
            text("SELECT id, name, description, project_metadata, created_at, updated_at FROM projects WHERE id = :project_id"),
            {"project_id": project_id}
        )
        row = result.fetchone()
        if not row:
            return None
        
        # Access row using positional indexing to avoid SQLAlchemy column name mapping issues
        project = type('Project', (), {})()  # type: ignore
        project.id = str(row[0])
        project.name = row[1]
        project.description = row[2] if len(row) > 2 else None
        project.project_metadata = row[3] if len(row) > 3 and row[3] else {}
        project.metadata = project.project_metadata  # Alias for compatibility
        project.created_at = row[4] if len(row) > 4 else None
        project.updated_at = row[5] if len(row) > 5 else None
        return project

    async def get_by_name(self, name: str) -> Project | None:
        """Get project by name."""
        # Use raw SQL to avoid model column mismatches
        from sqlalchemy import text
        result = await self.session.execute(
            text("SELECT id, name, description, project_metadata, created_at, updated_at FROM projects WHERE name = :name"),
            {"name": name}
        )
        row = result.fetchone()
        if not row:
            return None
        
        # Create a Project-like object that works with the actual schema
        # Use positional indexing to avoid SQLAlchemy column name mapping issues
        project = type('Project', (), {})()  # type: ignore
        project.id = str(row[0])
        project.name = row[1]
        project.description = row[2] if len(row) > 2 else None
        project.project_metadata = row[3] if len(row) > 3 and row[3] else {}
        project.metadata = project.project_metadata  # Alias for compatibility
        project.created_at = row[4] if len(row) > 4 else None
        project.updated_at = row[5] if len(row) > 5 else None
        return project

    async def get_all(self) -> list[Project]:
        """Get all projects."""
        # Use raw SQL to avoid model column mismatches with database schema
        from sqlalchemy import text
        result = await self.session.execute(
            text("SELECT id, name, description, project_metadata, created_at, updated_at FROM projects")
        )
        projects = []
        for row in result:
            # Create a Project-like object that works with the actual schema
            # Use positional indexing to avoid SQLAlchemy column name mapping issues
            project = type('Project', (), {})()  # type: ignore
            project.id = str(row[0])
            project.name = row[1]
            project.description = row[2] if len(row) > 2 else None
            project.project_metadata = row[3] if len(row) > 3 and row[3] else {}
            project.metadata = project.project_metadata  # Alias for compatibility
            project.created_at = row[4] if len(row) > 4 else None
            project.updated_at = row[5] if len(row) > 5 else None
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
