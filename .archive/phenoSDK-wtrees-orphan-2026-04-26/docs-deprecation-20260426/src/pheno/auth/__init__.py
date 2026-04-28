"""Authentication and OAuth utilities for the pheno SDK.

Combines the consolidated domain primitives (providers, MFA, manager) with credential
and session helpers used across CLI, QA, and adapter flows.
"""

from __future__ import annotations

from pheno.adapters.auth.mfa import (
    EmailAdapter,
    EmailMFAAdapter,
    PushAdapter,
    PushNotificationAdapter,
    SMSAdapter,
    SMSMFAAdapter,
    TOTPAdapter,
    get_mfa_registry,
)
from pheno.adapters.auth.mfa import create_adapter as create_mfa_adapter
from pheno.adapters.auth.mfa import register_adapter as register_mfa_adapter
from pheno.adapters.auth.providers import (
    Auth0Provider,
    AuthKitProvider,
    OAuth2GenericProvider,
    ProviderRegistry,
    create_provider,
    register_provider,
)
from pheno.adapters.auth.providers import get_registry as get_provider_registry

from .credential_manager import (
    InteractiveCredentialManager,
    ensure_oauth_credentials,
    prompt_for_value,
)
from .interfaces import (
    AuthProvider,
    AuthProviderRegistry,
    CredentialManager,
    MFAAdapter,
    MFAAdapterRegistry,
    TokenManager,
)
from .jwt_handler import (
    JWTHandler,
    decode_jwt,
    decode_jwt_unverified,
)
from .manager import AuthManager
from .mfa_handler import MFAHandler, TOTPHandler, generate_totp_secret
from .playwright_adapter import MockBrowserAdapter, PlaywrightOAuthAdapter
from .session_broker import OAuthTokens, SessionOAuthBroker, create_auth_header
from .session_manager import (
    InMemorySessionStore,
    SessionManager,
    SessionStore,
)
from .token_cache import CachedToken, EncryptedTokenStorage, TokenCache
from .token_manager import FileTokenManager
from .types import (
    AuthenticationError,
    AuthError,
    AuthorizationError,
    AuthResult,
    AuthTokens,
    ConfigurationError,
    CredentialError,
    Credentials,
    MFAContext,
    MFAMethod,
    MFARequiredError,
    ProviderError,
    ProviderType,
    TokenError,
    TokenExpiredError,
)

__all__ = [
    "Auth0Provider",
    "AuthError",
    "AuthKitProvider",
    # Core manager & registries
    "AuthManager",
    "AuthProvider",
    "AuthProviderRegistry",
    "AuthResult",
    # Domain types & errors
    "AuthTokens",
    "AuthenticationError",
    "AuthorizationError",
    "CachedToken",
    "ConfigurationError",
    "CredentialError",
    "CredentialManager",
    "Credentials",
    "EmailAdapter",
    "EmailMFAAdapter",
    "EncryptedTokenStorage",
    "FileTokenManager",
    "InMemorySessionStore",
    "InteractiveCredentialManager",
    # JWT handling
    "JWTHandler",
    "MFAAdapter",
    "MFAAdapterRegistry",
    "MFAContext",
    "MFAHandler",
    "MFAMethod",
    "MFARequiredError",
    "MockBrowserAdapter",
    # Provider implementations
    "OAuth2GenericProvider",
    "OAuthTokens",
    "PlaywrightOAuthAdapter",
    "ProviderError",
    "ProviderRegistry",
    "ProviderType",
    "PushAdapter",
    "PushNotificationAdapter",
    "SMSAdapter",
    "SMSMFAAdapter",
    # Session management
    "SessionManager",
    # Credential and session helpers
    "SessionOAuthBroker",
    "SessionStore",
    # MFA implementations
    "TOTPAdapter",
    "TOTPHandler",
    "TokenCache",
    "TokenError",
    "TokenExpiredError",
    "TokenManager",
    "create_auth_header",
    "create_mfa_adapter",
    "create_provider",
    "decode_jwt",
    "decode_jwt_unverified",
    "ensure_oauth_credentials",
    "generate_totp_secret",
    "get_mfa_registry",
    "get_provider_registry",
    "prompt_for_value",
    "register_mfa_adapter",
    "register_provider",
]
