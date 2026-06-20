"""Repository for Account model operations."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.account import Account
from tracertm.models.account_user import AccountRole, AccountUser


class AccountRepository:
    """Repository for account operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize account repository.

        Args:
            db: SQLAlchemy async session for database operations.
        """
        self.db = db

    async def create(
        self,
        name: str,
        slug: str,
        account_type: str = "personal",
        metadata: dict[str, Any] | None = None,
    ) -> Account:
        """Create a new account."""
        account = Account(
            name=name,
            slug=slug,
            account_type=account_type,
            account_metadata=metadata or {},
        )
        self.db.add(account)
        await self.db.flush()
        return account

    async def get_by_id(self, account_id: str) -> Account | None:
        """Get account by ID."""
        result = await self.db.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Account | None:
        """Get account by slug."""
        result = await self.db.execute(select(Account).where(Account.slug == slug))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> list[Account]:
        """List all accounts for a user."""
        result = await self.db.execute(
            select(Account).join(AccountUser).where(AccountUser.user_id == user_id).order_by(Account.created_at.desc()),
        )
        return list(result.scalars().all())

    async def update(
        self,
        account_id: str,
        name: str | None = None,
        slug: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Account | None:
        """Update an account."""
        account = await self.get_by_id(account_id)
        if not account:
            return None

        if name is not None:
            account.name = name
        if slug is not None:
            account.slug = slug
        if metadata is not None:
            account.account_metadata = metadata

        await self.db.flush()
        return account

    async def delete(self, account_id: str) -> bool:
        """Delete an account."""
        account = await self.get_by_id(account_id)
        if not account:
            return False

        await self.db.delete(account)
        await self.db.flush()
        return True

    async def add_user(
        self,
        account_id: str,
        user_id: str,
        role: str = AccountRole.MEMBER,
    ) -> AccountUser:
        """Add a user to an account."""
        account_user = AccountUser(
            account_id=account_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(account_user)
        await self.db.flush()
        return account_user

    async def remove_user(self, account_id: str, user_id: str) -> bool:
        """Remove a user from an account."""
        result = await self.db.execute(
            select(AccountUser).where(
                AccountUser.account_id == account_id,
                AccountUser.user_id == user_id,
            ),
        )
        account_user = result.scalar_one_or_none()
        if not account_user:
            return False

        await self.db.delete(account_user)
        await self.db.flush()
        return True

    async def get_user_role(self, account_id: str, user_id: str) -> str | None:
        """Get user's role in an account."""
        result = await self.db.execute(
            select(AccountUser.role).where(
                AccountUser.account_id == account_id,
                AccountUser.user_id == user_id,
            ),
        )
        return result.scalar_one_or_none()

    async def update_user_role(self, account_id: str, user_id: str, role: str) -> bool:
        """Update user's role in an account."""
        result = await self.db.execute(
            select(AccountUser).where(
                AccountUser.account_id == account_id,
                AccountUser.user_id == user_id,
            ),
        )
        account_user = result.scalar_one_or_none()
        if not account_user:
            return False

        account_user.role = role
        await self.db.flush()
        return True
