"""Abstract interfaces for the unified ``pheno`` authentication domain.

These contracts define the application-facing ports that adapters must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pheno.domain.auth.types import (
        AuthResult,
        AuthTokens,
        Credentials,
        MFAContext,
        MFAMethod,
        ProviderType,
    )


class AuthProvider(ABC):
    """
    Base interface for authentication providers.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """
        Return the type for this provider.
        """

    @abstractmethod
    async def authenticate(self, credentials: Credentials) -> AuthResult:
        """
        Authenticate a user with the given credentials.
        """

    @abstractmethod
    async def refresh(self, tokens: AuthTokens) -> AuthTokens:
        """
        Refresh authentication tokens.
        """

    @abstractmethod
    async def revoke(self, tokens: AuthTokens) -> bool:
        """
        Revoke authentication tokens.
        """

    @abstractmethod
    def supports_refresh(self) -> bool:
        """
        Return True if this provider supports refresh operations.
        """

    @abstractmethod
    def get_auth_url(self, state: str, redirect_uri: str) -> str:
        """
        Return an authorization URL for OAuth style flows.
        """

    async def validate_tokens(self, tokens: AuthTokens) -> bool:
        """
        Check whether tokens remain valid; defaults to expiry check.
        """
        return not tokens.is_expired()


class MFAAdapter(ABC):
    """
    Base interface for multi-factor authentication adapters.
    """

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    def supports_method(self, method: MFAMethod) -> bool:
        """
        Return True if the adapter supports the supplied method.
        """

    @abstractmethod
    async def send_code(self, context: MFAContext) -> str:
        """
        Send an MFA code and return a challenge identifier.
        """

    @abstractmethod
    async def verify_code(self, code: str, context: MFAContext) -> bool:
        """
        Verify the user-provided MFA code.
        """

    @abstractmethod
    async def generate_code(self, context: MFAContext) -> str:
        """
        Generate an MFA code without delivering it.
        """

    async def prepare(self, context: MFAContext) -> None:
        """
        Optional hook for adapter setup before MFA flows run.
        """

    async def cleanup(self, context: MFAContext) -> None:
        """
        Optional hook for adapter teardown after MFA flows.
        """


class TokenManager(ABC):
    """
    Base interface for token management.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    async def store(self, key: str, tokens: AuthTokens) -> None:
        """
        Persist authentication tokens.
        """

    @abstractmethod
    async def retrieve(self, key: str) -> AuthTokens | None:
        """
        Retrieve stored authentication tokens.
        """

    @abstractmethod
    async def refresh_if_needed(self, key: str, provider: AuthProvider) -> AuthTokens | None:
        """
        Refresh tokens if necessary and return the latest set.
        """

    @abstractmethod
    async def revoke(self, key: str) -> None:
        """
        Revoke and remove stored tokens.
        """

    @abstractmethod
    async def list_keys(self) -> list[str]:
        """
        List all stored token keys.
        """


class CredentialManager(ABC):
    """
    Base interface for secure credential storage.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    async def store(self, key: str, credentials: Credentials) -> None:
        """
        Persist user credentials.
        """

    @abstractmethod
    async def retrieve(self, key: str) -> Credentials | None:
        """
        Retrieve stored credentials.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete stored credentials.
        """

    @abstractmethod
    async def list_keys(self) -> list[str]:
        """
        List all credential keys.
        """

    @abstractmethod
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.
        """

    @abstractmethod
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        """


class MFAAdapterRegistry(ABC):
    """
    Registry interface for managing MFA adapters.
    """

    @abstractmethod
    def register_adapter(self, name: str, adapter_class: type[MFAAdapter]) -> None:
        """
        Register an MFA adapter implementation.
        """

    @abstractmethod
    def create_adapter(self, name: str, config: dict[str, Any]) -> MFAAdapter:
        """
        Instantiate a registered adapter.
        """

    @abstractmethod
    def get_adapter(self, name: str) -> type[MFAAdapter] | None:
        """
        Return the adapter class registered under the supplied name.
        """

    @abstractmethod
    def list_adapters(self) -> list[str]:
        """
        List all registered adapter names.
        """

    @abstractmethod
    def get_adapters_by_method(self, method: MFAMethod) -> list[str]:
        """
        List adapters that support the supplied MFA method.
        """


class AuthProviderRegistry(ABC):
    """
    Registry interface for managing auth provider implementations.
    """

    @abstractmethod
    def register_provider(self, name: str, provider_class: type[AuthProvider]) -> None:
        """
        Register an auth provider implementation.
        """

    @abstractmethod
    def create_provider(self, name: str, config: dict[str, Any]) -> AuthProvider:
        """
        Instantiate a registered provider.
        """

    @abstractmethod
    def get_provider(self, name: str) -> type[AuthProvider] | None:
        """
        Return the provider class registered under the supplied name.
        """

    @abstractmethod
    def list_providers(self) -> list[str]:
        """
        List all registered provider names.
        """


__all__ = [
    "AuthProvider",
    "AuthProviderRegistry",
    "CredentialManager",
    "MFAAdapter",
    "MFAAdapterRegistry",
    "TokenManager",
]
