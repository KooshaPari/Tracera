"""Repository for GitHub App Installation operations."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.github_app_installation import GitHubAppInstallation


class GitHubAppInstallationRepository:
    """Repository for GitHub App installation operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db: SQLAlchemy async session for database operations.
        """
        self.db = db

    async def create(
        self,
        account_id: str,
        installation_id: int,
        account_login: str,
        target_type: str,
        target_id: int,
        permissions: dict[str, Any],
        repository_selection: str = "all",
    ) -> GitHubAppInstallation:
        """Create a new GitHub App installation."""
        installation = GitHubAppInstallation(
            account_id=account_id,
            installation_id=installation_id,
            account_login=account_login,
            target_type=target_type,
            target_id=target_id,
            permissions=permissions,
            repository_selection=repository_selection,
        )
        self.db.add(installation)
        await self.db.flush()
        return installation

    async def get_by_id(self, installation_id: str) -> GitHubAppInstallation | None:
        """Get installation by ID."""
        result = await self.db.execute(select(GitHubAppInstallation).where(GitHubAppInstallation.id == installation_id))
        return result.scalar_one_or_none()

    async def get_by_github_installation_id(self, github_installation_id: int) -> GitHubAppInstallation | None:
        """Get installation by GitHub's installation ID."""
        result = await self.db.execute(
            select(GitHubAppInstallation).where(GitHubAppInstallation.installation_id == github_installation_id),
        )
        return result.scalar_one_or_none()

    async def list_by_account(self, account_id: str) -> list[GitHubAppInstallation]:
        """List all installations for an account."""
        result = await self.db.execute(
            select(GitHubAppInstallation)
            .where(GitHubAppInstallation.account_id == account_id)
            .where(GitHubAppInstallation.suspended_at.is_(None))
            .order_by(GitHubAppInstallation.created_at.desc()),
        )
        return list(result.scalars().all())

    async def update(
        self,
        installation_id: str,
        permissions: dict[str, Any] | None = None,
        suspended_at: bool | None = None,
    ) -> GitHubAppInstallation | None:
        """Update an installation."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        if permissions is not None:
            installation.permissions = permissions
        if suspended_at is not None:
            installation.suspended_at = datetime.now(UTC) if suspended_at else None

        await self.db.flush()
        return installation

    async def delete(self, installation_id: str) -> bool:
        """Delete an installation."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return False

        await self.db.delete(installation)
        await self.db.flush()
        return True
