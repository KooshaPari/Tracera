"""User model for caching WorkOS user data.

This model provides a local cache of WorkOS user information to reduce
API latency. WorkOS remains the source of truth, and this cache is
synchronized on demand with a 5-minute TTL.
"""

from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.sql import func

from tracertm.models.base import Base


class User(Base):
    """User model - caches WorkOS user data.

    This model caches minimal user metadata from WorkOS to improve
    performance of the /auth/me endpoint. Data is synced on-demand
    with a 5-minute freshness check.

    Attributes:
        id: WorkOS user ID (e.g., user_01HXYZ) - primary key
        email: User email address (unique)
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        email_verified: Whether email has been verified
        profile_picture_url: URL to user's profile picture (optional)
        created_at: When user was created in WorkOS
        updated_at: When user was last updated in WorkOS
        synced_at: When this cache entry was last synchronized
    """

    __tablename__ = "users"

    # WorkOS user ID (primary key)
    id = Column(String(255), primary_key=True)  # e.g., user_01HXYZ

    # Basic info
    email = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    profile_picture_url = Column(String(500), nullable=True)

    # Timestamps from WorkOS
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    # Local tracking - when cache was last updated
    synced_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_synced_at", "synced_at"),
    )

    def to_dict(self) -> dict[str, object]:
        """Convert user model to dictionary for API responses.

        Returns:
            Dictionary with camelCase keys matching frontend expectations
        """
        return {
            "id": self.id,
            "email": self.email,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "emailVerified": self.email_verified,
            "profilePictureUrl": self.profile_picture_url,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
