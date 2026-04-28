"""
Authentication ports describing contracts for OAuth flows and API key validation.

These interfaces layer on top of the existing auth domain models to keep adapters that
integrate with identity providers (Auth0, Cognito, custom OAuth2 servers) and key
management systems behind explicit contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pheno.domain.auth.types import (
        AuthResult,
        AuthTokens,
        Credentials,
        ProviderType,
    )


@dataclass(slots=True)
class AuthorizationRequest:
    """Parameters required to initiate an OAuth authorization flow."""

    client_id: str
    redirect_uri: str
    scope: Sequence[str] | None = None
    state: str | None = None
    response_type: str = "code"
    prompt: str | None = None
    extras: dict[str, Any] | None = None


@dataclass(slots=True)
class TokenIntrospection:
    """Outcome of an OAuth token introspection call."""

    active: bool
    subject: str | None = None
    scopes: list[str] | None = None
    expires_at: float | None = None
    issued_at: float | None = None
    client_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class APIKeyIdentity:
    """Represents the identity derived from an API key."""

    key_id: str
    owner: str | None = None
    scopes: list[str] | None = None
    metadata: dict[str, Any] | None = None


class OAuthProviderPort(Protocol):
    """Contract for OAuth2/OIDC compliant identity providers."""

    provider_type: ProviderType

    def build_authorization_url(self, request: AuthorizationRequest) -> str:
        """Construct an authorization URL for the user-facing redirect."""
        ...

    async def exchange_code(self, credentials: Credentials) -> AuthTokens:
        """Exchange an authorization code for tokens."""
        ...

    async def refresh_tokens(self, tokens: AuthTokens) -> AuthTokens:
        """Refresh access tokens when possible."""
        ...

    async def revoke_tokens(self, tokens: AuthTokens) -> bool:
        """Invalidate the supplied tokens; returns True on success."""
        ...

    async def introspect(self, token: str) -> TokenIntrospection:
        """Validate the token server-side and return metadata."""
        ...

    async def user_info(self, tokens: AuthTokens) -> dict[str, Any]:
        """Fetch the user info document for authenticated sessions."""
        ...


class APIKeyValidatorPort(Protocol):
    """Contract for validating and managing API keys."""

    async def validate(self, api_key: str) -> APIKeyIdentity | None:
        """Return identity information when the key is valid."""
        ...

    async def issue(
        self,
        owner: str,
        *,
        scopes: Sequence[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> APIKeyIdentity:
        """Provision a new API key for ``owner`` and return its identity."""
        ...

    async def revoke(self, key_id: str) -> bool:
        """Revoke an API key using its identifier."""
        ...

    async def rotate(self, key_id: str) -> APIKeyIdentity:
        """Rotate key material while preserving metadata."""
        ...


class AuthSessionStorePort(Protocol):
    """Persistence contract for caching authentication sessions."""

    async def save(self, key: str, result: AuthResult) -> None:
        """Persist the result of a successful authentication."""
        ...

    async def load(self, key: str) -> AuthResult | None:
        """Retrieve a previously saved authentication result."""
        ...

    async def delete(self, key: str) -> None:
        """Remove stored session state."""
        ...

    async def list_sessions(self, prefix: str | None = None) -> list[str]:
        """List stored sessions filtered by optional prefix."""
        ...


__all__ = [
    "APIKeyIdentity",
    "APIKeyValidatorPort",
    "AuthSessionStorePort",
    "AuthorizationRequest",
    "OAuthProviderPort",
    "TokenIntrospection",
]
