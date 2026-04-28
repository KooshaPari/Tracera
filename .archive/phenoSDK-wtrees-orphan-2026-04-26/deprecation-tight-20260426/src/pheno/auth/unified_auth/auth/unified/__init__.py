"""Unified Authentication System (Phase 4 Consolidation)

Consolidated from:
- pheno.auth (core authentication)
- pheno.auth.authkit (OAuth, tokens)
- pheno.mcp.qa.auth (MFA, testing auth)

Provides a single, unified authentication framework with:
- Protocol-based provider system
- Comprehensive OAuth support
- MFA integration
- Session management
- Security utilities
"""

import warnings

from .core.interfaces import (
    AuthProviderProtocol,
    MFAProviderProtocol,
    OAuthProviderProtocol,
    SessionProviderProtocol,
)
from .core.manager import AuthManager
from .core.security import JWTHandler, PasswordHasher, SecurityUtils
from .core.types import AuthSession, AuthToken, AuthUser, MFAType
from .middleware.oauth_middleware import OAuthMiddleware
from .middleware.session_middleware import SessionMiddleware
from .providers.mfa.base import MFAProvider
from .providers.mfa.push import PushProvider
from .providers.mfa.sms import SMSProvider
from .providers.mfa.totp import TOTPProvider
from .providers.oauth.authkit import AuthKitOAuthProvider
from .providers.oauth.azure import AzureOAuthProvider
from .providers.oauth.base import OAuthProvider
from .providers.oauth.github import GitHubOAuthProvider
from .providers.oauth.google import GoogleOAuthProvider
from .providers.session.base import SessionProvider
from .providers.session.memory import MemorySessionProvider
from .providers.session.redis import RedisSessionProvider


class UnifiedAuthManager(AuthManager):
    """Deprecated alias for AuthManager."""

    def __init__(
        self,
        providers: dict[str, AuthProviderProtocol] | None = None,
        mfa_providers: dict[str, MFAProviderProtocol] | None = None,
        session_provider: SessionProviderProtocol | None = None,
        default_provider: str = "local",
    ):
        warnings.warn(
            "UnifiedAuthManager is deprecated, use AuthManager instead",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(
            providers=providers,
            mfa_providers=mfa_providers,
            session_provider=session_provider,
            default_provider=default_provider,
        )


__all__ = [
    "AuthKitOAuthProvider",
    # Core
    "AuthManager",
    "AuthProviderProtocol",
    "AuthSession",
    "AuthToken",
    "AuthUser",
    "AzureOAuthProvider",
    "GitHubOAuthProvider",
    "GoogleOAuthProvider",
    "JWTHandler",
    # MFA Providers
    "MFAProvider",
    "MFAProviderProtocol",
    "MFAType",
    "MemorySessionProvider",
    # Middleware
    "OAuthMiddleware",
    # OAuth Providers
    "OAuthProvider",
    "OAuthProviderProtocol",
    "PasswordHasher",
    "PushProvider",
    "RedisSessionProvider",
    "SMSProvider",
    "SecurityUtils",
    "SessionMiddleware",
    # Session Providers
    "SessionProvider",
    "TOTPProvider",
    "UnifiedAuthManager",
]

# Version and compatibility
__version__ = "1.0.0"
__compatibility__ = {
    "pheno.auth": "1.0+",  # Compatible with pheno.auth v1.0+
    "authkit": "2.0+",  # Compatible with authkit v2.0+
    "pheno.mcp.qa.auth": "1.5+",  # Compatible with legacy mcp_qa auth toolkit
}
