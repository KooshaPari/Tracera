"""Service for GitHub Projects auto-linking and synchronization."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.clients.github_client import GitHubClient
from tracertm.repositories.github_project_repository import GitHubProjectRepository


@dataclass
class LinkProjectParams:
    """Parameters for linking a GitHub Project to a TraceRTM project."""

    project_id: str
    github_repo_id: int
    github_repo_owner: str
    github_repo_name: str
    github_project_id: str
    github_project_number: int
    auto_sync: bool = True


class GitHubProjectService:
    """Service for GitHub Projects operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize service.

        Args:
            db: SQLAlchemy async session for database operations.
        """
        self.db = db
        self.repo = GitHubProjectRepository(db)

    async def auto_link_projects_for_repo(
        self,
        project_id: str,
        github_repo_owner: str,
        github_repo_name: str,
        github_repo_id: int,
        client: GitHubClient,
    ) -> list[dict]:
        """Auto-discover and link GitHub Projects for a repository.

        Args:
            project_id: TraceRTM project ID.
            github_repo_owner: Repository owner (user or org).
            github_repo_name: Repository name.
            github_repo_id: GitHub repository ID.
            client: Authenticated GitHubClient.

        Returns:
            List of linked GitHub Projects.
        """
        # List Projects v2 for the repository owner
        is_org = True  # Assume org for now, could be determined dynamically
        try:
            projects = await client.list_projects_graphql(owner=github_repo_owner, is_org=is_org)
        except (ValueError, KeyError, OperationalError):
            # If org fails, try as user
            projects = await client.list_projects_graphql(owner=github_repo_owner, is_org=False)

        linked_projects = []

        for project in projects:
            # Check if project is already linked
            existing = await self.repo.get_by_id(str(project.get("id") or ""))
            if existing and existing.project_id == project_id:
                linked_projects.append({
                    "id": existing.id,
                    "github_project_id": existing.github_project_id,
                    "title": project.get("title"),
                    "already_linked": True,
                })
                continue

            # Create new link
            github_project = await self.repo.create(
                project_id=project_id,
                github_repo_id=github_repo_id,
                github_repo_owner=github_repo_owner,
                github_repo_name=github_repo_name,
                github_project_id=str(project.get("id") or ""),
                github_project_number=project.get("number", 0),
                auto_sync=True,
            )

            linked_projects.append({
                "id": github_project.id,
                "github_project_id": github_project.github_project_id,
                "title": project.get("title"),
                "already_linked": False,
            })

        await self.db.commit()
        return linked_projects

    async def list_projects_for_repo(
        self,
        github_repo_id: int,
    ) -> list[dict]:
        """List all GitHub Projects linked to a repository."""
        projects = await self.repo.get_by_repo(github_repo_id)
        return [
            {
                "id": p.id,
                "project_id": p.project_id,
                "github_project_id": p.github_project_id,
                "github_project_number": p.github_project_number,
                "auto_sync": p.auto_sync,
                "sync_config": p.sync_config,
            }
            for p in projects
        ]

    async def link_project(self, params: LinkProjectParams) -> dict[str, Any]:
        """Manually link a GitHub Project to a TraceRTM project."""
        github_project = await self.repo.create(
            project_id=params.project_id,
            github_repo_id=params.github_repo_id,
            github_repo_owner=params.github_repo_owner,
            github_repo_name=params.github_repo_name,
            github_project_id=params.github_project_id,
            github_project_number=params.github_project_number,
            auto_sync=params.auto_sync,
        )

        await self.db.commit()

        return {
            "id": github_project.id,
            "project_id": github_project.project_id,
            "github_project_id": github_project.github_project_id,
        }

    async def unlink_project(self, github_project_id: str) -> bool:
        """Unlink a GitHub Project from a TraceRTM project."""
        result = await self.repo.delete(github_project_id)
        if result:
            await self.db.commit()
        return result
