"""Repository for Linear App Installation operations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.linear_app import LinearAppInstallation


class LinearAppInstallationRepository:
    """Repository for Linear App installation operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db: SQLAlchemy async session for database operations.
        """
        self.db = db

    async def create(
        self,
        account_id: str,
        workspace_id: str,
        workspace_name: str,
        integration_credential_id: str | None = None,
        scopes: list[str] | None = None,
    ) -> LinearAppInstallation:
        """Create a new Linear App installation."""
        installation = LinearAppInstallation(
            account_id=account_id,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            integration_credential_id=integration_credential_id,
            scopes=scopes or [],
        )
        self.db.add(installation)
        await self.db.flush()
        return installation

    async def get_by_id(self, installation_id: str) -> LinearAppInstallation | None:
        """Get installation by ID."""
        result = await self.db.execute(select(LinearAppInstallation).where(LinearAppInstallation.id == installation_id))
        return result.scalar_one_or_none()

    async def get_by_workspace_id(self, workspace_id: str) -> LinearAppInstallation | None:
        """Get installation by Linear workspace ID."""
        result = await self.db.execute(
            select(LinearAppInstallation).where(LinearAppInstallation.workspace_id == workspace_id),
        )
        return result.scalar_one_or_none()

    async def list_by_account(self, account_id: str) -> list[LinearAppInstallation]:
        """List all installations for an account."""
        result = await self.db.execute(
            select(LinearAppInstallation)
            .where(LinearAppInstallation.account_id == account_id)
            .where(LinearAppInstallation.suspended_at.is_(None))
            .order_by(LinearAppInstallation.created_at.desc()),
        )
        return list(result.scalars().all())

    async def update(
        self,
        installation_id: str,
        integration_credential_id: str | None = None,
        scopes: list[str] | None = None,
        suspended_at: bool | None = None,
    ) -> LinearAppInstallation | None:
        """Update an installation."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        if integration_credential_id is not None:
            installation.integration_credential_id = integration_credential_id
        if scopes is not None:
            installation.scopes = scopes
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
