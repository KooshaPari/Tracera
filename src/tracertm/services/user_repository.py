"""User repository service for managing cached WorkOS user data.

This service handles CRUD operations for the User model, providing
methods to sync user data from WorkOS into the local database cache.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from tracertm.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _parse_workos_timestamp(value: str | datetime | None) -> datetime:
    """Parse WorkOS timestamp, handling both string and datetime formats."""
    if value is None:
        return datetime.now(UTC)
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


class UserRepository:
    """Repository service for user CRUD operations.

    This service manages the local cache of WorkOS user data,
    providing methods to get or create users from WorkOS API responses.
    """

    @staticmethod
    async def get_or_create_from_workos(db: AsyncSession, workos_user: dict[str, Any]) -> User:
        """Get user from database or create from WorkOS data.

        If user exists, updates cached data. If not, creates new user.
        Always updates synced_at timestamp to track cache freshness.

        Args:
            db: Database session
            workos_user: User data from WorkOS API response

        Returns:
            User model instance (committed to database)

        Example:
            ```python
            workos_data = await workos.user_management.get_user(user_id)
            user = await UserRepository.get_or_create_from_workos(db, workos_data)
            ```
        """
        user_id = workos_user["id"]
        user = await db.get(User, user_id)
        now = datetime.now(UTC)

        if user:
            # Update existing user with fresh data from WorkOS
            user.email = workos_user["email"]
            user.first_name = workos_user.get("first_name")
            user.last_name = workos_user.get("last_name")
            user.email_verified = workos_user.get("email_verified", False)
            user.profile_picture_url = workos_user.get("profile_picture_url")

            # Parse WorkOS timestamps (ISO format strings)
            user.updated_at = _parse_workos_timestamp(workos_user.get("updated_at"))
            # Mark cache as fresh
            user.synced_at = now
        else:
            # Create new user from WorkOS data
            user = User(
                id=user_id,
                email=workos_user["email"],
                first_name=workos_user.get("first_name"),
                last_name=workos_user.get("last_name"),
                email_verified=workos_user.get("email_verified", False),
                profile_picture_url=workos_user.get("profile_picture_url"),
                created_at=_parse_workos_timestamp(workos_user.get("created_at")),
                updated_at=_parse_workos_timestamp(workos_user.get("updated_at")),
                synced_at=now,
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    def is_cache_fresh(synced_at: datetime, max_age_minutes: int = 5) -> bool:
        """Check if cached user data is fresh enough.

        Args:
            synced_at: Timestamp when cache was last updated
            max_age_minutes: Maximum age in minutes (default: 5)

        Returns:
            True if cache is fresh, False if stale

        Example:
            ```python
            if UserRepository.is_cache_fresh(user.synced_at):
                return user  # Use cache
            else:
                # Fetch from WorkOS and update cache
                workos_user = await get_user(user_id)
                user = await UserRepository.get_or_create_from_workos(db, workos_user)
            ```
        """
        age = datetime.now(UTC) - synced_at
        return age.total_seconds() < (max_age_minutes * 60)
