"""Core authentication types and exceptions for the consolidated pheno.auth module.

These definitions were migrated from the legacy pheno-auth package to provide canonical
dataclasses and error hierarchy that can be shared across CLI, QA, and adapter contexts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProviderType(Enum):
    """
    Supported authentication provider types.
    """

    OAUTH2 = "oauth2"
    OPENID_CONNECT = "oidc"
    SAML = "saml"
    LDAP = "ldap"
    CUSTOM = "custom"


class MFAMethod(Enum):
    """
    Supported multi-factor authentication methods.
    """

    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    HARDWARE = "hardware"
    BIOMETRIC = "biometric"


@dataclass
class AuthTokens:
    """
    Authentication tokens returned by providers.
    """

    access_token: str
    refresh_token: str | None = None
    id_token: str | None = None
    token_type: str = "Bearer"
    expires_at: datetime | None = None
    scope: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """
        Return True if the access token has expired.
        """
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at

    def is_refreshable(self) -> bool:
        """
        Return True if the token can be refreshed.
        """
        return bool(self.refresh_token and self.expires_at)


@dataclass
class Credentials:
    """
    Flexible credentials container for username/password or OAuth flows.
    """

    username: str | None = None
    password: str | None = None
    email: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    authorization_code: str | None = None
    state: str | None = None
    redirect_uri: str | None = None
    scope: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MFAContext:
    """
    Context passed to MFA adapters when additional verification is required.
    """

    user_id: str
    session_id: str
    method: MFAMethod
    challenge: str
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """
        Return True if the MFA challenge has expired.
        """
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at


@dataclass
class AuthResult:
    """
    Result container returned by AuthManager.authenticate.
    """

    success: bool
    tokens: AuthTokens | None = None
    user_info: dict[str, Any] | None = None
    requires_mfa: bool = False
    mfa_context: MFAContext | None = None
    error: str | None = None
    error_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AuthError(Exception):
    """
    Base exception for authentication errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(AuthError):
    """
    Raised when authentication fails.
    """


class AuthorizationError(AuthError):
    """
    Raised when authorization fails.
    """


class TokenExpiredError(AuthError):
    """
    Raised when a token has expired.
    """


class MFARequiredError(AuthError):
    """
    Raised when MFA is required for authentication.
    """

    def __init__(
        self,
        mfa_context: MFAContext,
        message: str = "Multi-factor authentication required",
    ):
        super().__init__(message)
        self.mfa_context = mfa_context


class ProviderError(AuthError):
    """
    Raised when a provider-specific error occurs.
    """


class ConfigurationError(AuthError):
    """
    Raised when configuration is invalid.
    """


class TokenError(AuthError):
    """
    Raised for token parsing or storage failures.
    """


class CredentialError(AuthError):
    """
    Raised when credential material is invalid or missing.
    """


__all__ = [
    "AuthError",
    "AuthResult",
    "AuthTokens",
    "AuthenticationError",
    "AuthorizationError",
    "ConfigurationError",
    "CredentialError",
    "Credentials",
    "MFAContext",
    "MFAMethod",
    "MFARequiredError",
    "ProviderError",
    "ProviderType",
    "TokenError",
    "TokenExpiredError",
]
