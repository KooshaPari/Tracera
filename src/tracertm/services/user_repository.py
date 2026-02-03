"""
User repository service for managing cached WorkOS user data.

This service handles CRUD operations for the User model, providing
methods to sync user data from WorkOS into the local database cache.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.user import User


class UserRepository:
    """Repository service for user CRUD operations.

    This service manages the local cache of WorkOS user data,
    providing methods to get or create users from WorkOS API responses.
    """

    @staticmethod
    async def get_or_create_from_workos(db: AsyncSession, workos_user: dict) -> User:
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

        if user:
            # Update existing user with fresh data from WorkOS
            user.email = workos_user["email"]
            user.first_name = workos_user.get("first_name")
            user.last_name = workos_user.get("last_name")
            user.email_verified = workos_user.get("email_verified", False)
            user.profile_picture_url = workos_user.get("profile_picture_url")

            # Parse WorkOS timestamps (ISO format strings)
            updated_at_str = workos_user.get("updated_at")
            if updated_at_str:
                # Handle both ISO format strings and datetime objects
                if isinstance(updated_at_str, str):
                    user.updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                elif isinstance(updated_at_str, datetime):
                    user.updated_at = updated_at_str
                else:
                    # Fallback to current time if format unexpected
                    user.updated_at = datetime.now(UTC)
            else:
                user.updated_at = datetime.now(UTC)

            # Mark cache as fresh
            user.synced_at = datetime.now(UTC)
        else:
            # Create new user from WorkOS data
            created_at_str = workos_user.get("created_at")
            updated_at_str = workos_user.get("updated_at")

            # Parse timestamps - handle both string and datetime formats
            if isinstance(created_at_str, str):
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            elif isinstance(created_at_str, datetime):
                created_at = created_at_str
            else:
                created_at = datetime.now(UTC)

            if isinstance(updated_at_str, str):
                updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
            elif isinstance(updated_at_str, datetime):
                updated_at = updated_at_str
            else:
                updated_at = datetime.now(UTC)

            user = User(
                id=user_id,
                email=workos_user["email"],
                first_name=workos_user.get("first_name"),
                last_name=workos_user.get("last_name"),
                email_verified=workos_user.get("email_verified", False),
                profile_picture_url=workos_user.get("profile_picture_url"),
                created_at=created_at,
                updated_at=updated_at,
                synced_at=datetime.now(UTC),
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
