"""Repository for GitHub Project operations."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.github_project import GitHubProject


class GitHubProjectRepository:
    """Repository for GitHub Project operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db: SQLAlchemy async session for database operations.
        """
        self.db = db

    async def create(
        self,
        project_id: str | uuid.UUID,
        github_repo_id: int,
        github_repo_owner: str,
        github_repo_name: str,
        github_project_id: str,
        github_project_number: int,
        auto_sync: bool = True,
        sync_config: dict[str, Any] | None = None,
    ) -> GitHubProject:
        """Create a new GitHub Project link."""
        project_id_str = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        github_project = GitHubProject(
            project_id=project_id_str,
            github_repo_id=github_repo_id,
            github_repo_owner=github_repo_owner,
            github_repo_name=github_repo_name,
            github_project_id=github_project_id,
            github_project_number=github_project_number,
            auto_sync=auto_sync,
            sync_config=sync_config or {},
        )
        self.db.add(github_project)
        await self.db.flush()
        return github_project

    async def get_by_id(self, github_project_id: str) -> GitHubProject | None:
        """Get GitHub Project by ID."""
        result = await self.db.execute(select(GitHubProject).where(GitHubProject.id == github_project_id))
        return result.scalar_one_or_none()

    async def get_by_project_id(self, project_id: str | uuid.UUID) -> list[GitHubProject]:
        """Get all GitHub Projects for a TraceRTM project."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        result = await self.db.execute(select(GitHubProject).where(GitHubProject.project_id == pid))
        return list(result.scalars().all())

    async def get_by_repo(self, github_repo_id: int) -> list[GitHubProject]:
        """Get all GitHub Projects for a GitHub repository."""
        result = await self.db.execute(select(GitHubProject).where(GitHubProject.github_repo_id == github_repo_id))
        return list(result.scalars().all())

    async def update(
        self,
        github_project_id: str,
        auto_sync: bool | None = None,
        sync_config: dict[str, Any] | None = None,
    ) -> GitHubProject | None:
        """Update a GitHub Project link."""
        github_project = await self.get_by_id(github_project_id)
        if not github_project:
            return None

        if auto_sync is not None:
            github_project.auto_sync = auto_sync
        if sync_config is not None:
            github_project.sync_config = sync_config

        await self.db.flush()
        return github_project

    async def delete(self, github_project_id: str) -> bool:
        """Delete a GitHub Project link."""
        github_project = await self.get_by_id(github_project_id)
        if not github_project:
            return False

        await self.db.delete(github_project)
        await self.db.flush()
        return True
