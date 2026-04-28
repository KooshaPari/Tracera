"""Unified Authentication Types.

Consolidated type definitions from all auth implementations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MFAType(Enum):
    """
    Multi-factor authentication types.
    """

    TOTP = "totp"
    SMS = "sms"
    PUSH = "push"
    EMAIL = "email"
    HARDWARE = "hardware"


class AuthProviderType(Enum):
    """
    Authentication provider types.
    """

    OAUTH = "oauth"
    SAML = "saml"
    LDAP = "ldap"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class AuthUser:
    """
    Unified user representation.
    """

    id: str
    username: str
    email: str
    display_name: str | None = None
    avatar_url: str | None = None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Provider-specific data
    provider_id: str | None = None
    provider_type: AuthProviderType | None = None

    # MFA status
    mfa_enabled: bool = False
    mfa_types: list[MFAType] = field(default_factory=list)

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: datetime | None = None
    is_active: bool = True

    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.
        """
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.
        """
        return permission in self.permissions

    def has_mfa_type(self, mfa_type: MFAType) -> bool:
        """
        Check if user has MFA of specific type enabled.
        """
        return mfa_type in self.mfa_types


@dataclass
class AuthToken:
    """
    Unified token representation.
    """

    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None
    expires_at: datetime | None = None
    refresh_token: str | None = None
    scope: str | None = None
    id_token: str | None = None

    # Provider info
    provider: str | None = None
    provider_type: str | None = None

    # Metadata
    issued_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """
        Check if token is expired.
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def time_until_expiry(self) -> int | None:
        """
        Get seconds until expiry.
        """
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))


@dataclass
class AuthSession:
    """
    Unified session representation.
    """

    id: str
    user: AuthUser
    token: AuthToken
    provider_data: dict[str, Any] = field(default_factory=dict)

    # Session lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    # Security
    ip_address: str | None = None
    user_agent: str | None = None
    device_id: str | None = None

    def is_expired(self) -> bool:
        """
        Check if session is expired.
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def extend(self, minutes: int = 30) -> None:
        """
        Extend session by specified minutes.
        """
        if self.expires_at is not None:
            self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
        self.last_activity = datetime.utcnow()

    def invalidate(self) -> None:
        """
        Invalidate the session.
        """
        self.is_active = False


@dataclass
class AuthRequest:
    """
    Authentication request data.
    """

    username: str | None = None
    email: str | None = None
    password: str | None = None

    # OAuth
    code: str | None = None
    state: str | None = None
    redirect_uri: str | None = None

    # MFA
    mfa_code: str | None = None
    mfa_type: MFAType | None = None

    # Metadata
    provider: str | None = None
    scope: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResponse:
    """
    Authentication response data.
    """

    success: bool
    user: AuthUser | None = None
    session: AuthSession | None = None
    token: AuthToken | None = None

    # Error information
    error: str | None = None
    error_description: str | None = None

    # MFA requirements
    requires_mfa: bool = False
    mfa_types: list[MFAType] = field(default_factory=list)

    # Redirect information
    redirect_url: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
