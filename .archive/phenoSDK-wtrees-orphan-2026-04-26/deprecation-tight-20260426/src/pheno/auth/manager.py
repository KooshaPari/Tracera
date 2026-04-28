"""Consolidated authentication manager for pheno.auth.

This is the canonical orchestration layer that composes providers, token storage, and
MFA adapters across the ecosystem.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pheno.adapters.auth.mfa.registry import get_registry as get_mfa_registry
from pheno.adapters.auth.providers.registry import get_registry as get_provider_registry

from .types import (
    AuthenticationError,
    AuthResult,
    AuthTokens,
    Credentials,
    MFAContext,
    MFAMethod,
)

if TYPE_CHECKING:
    from .interfaces import CredentialManager, TokenManager


class AuthManager:
    """
    Application-facing authentication orchestrator.
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        token_manager: TokenManager | None = None,
        credential_manager: CredentialManager | None = None,
    ):
        self.config = config or {}
        self.provider_registry = get_provider_registry()
        self.mfa_registry = get_mfa_registry()
        self.token_manager: TokenManager | None = token_manager
        self.credential_manager: CredentialManager | None = credential_manager

    def register_provider(self, name: str, provider_class: type) -> None:
        """
        Register an authentication provider implementation.
        """
        self.provider_registry.register_provider(name, provider_class)

    def register_mfa_adapter(self, name: str, adapter_class: type) -> None:
        """
        Register an MFA adapter implementation.
        """
        self.mfa_registry.register_adapter(name, adapter_class)

    def set_token_manager(self, token_manager: TokenManager) -> None:
        """
        Install the token manager used for session persistence.
        """
        self.token_manager = token_manager

    def set_credential_manager(self, credential_manager: CredentialManager) -> None:
        """
        Install the credential manager used for secure secret storage.
        """
        self.credential_manager = credential_manager

    async def authenticate(
        self,
        provider_name: str,
        credentials: Credentials,
        store_tokens: bool = True,
    ) -> AuthResult:
        """
        Authenticate with the provider identified by name.
        """
        try:
            provider = self.provider_registry.create_provider(provider_name, self.config)
            result = await provider.authenticate(credentials)

            if result.success and result.tokens and store_tokens and self.token_manager:
                storage_key = self._make_storage_key(provider_name, credentials)
                await self.token_manager.store(storage_key, result.tokens)

            return result
        except Exception as exc:  # pragma: no cover - bubble up structured error
            return AuthResult(
                success=False,
                error=str(exc),
                error_code="authentication_failed",
            )

    async def send_mfa_code(self, adapter_name: str, context: MFAContext) -> str:
        """
        Send an MFA code and return the challenge identifier.
        """
        try:
            adapter = self.mfa_registry.create_adapter(adapter_name, self.config)
            return await adapter.send_code(context)
        except Exception as exc:
            raise AuthenticationError(f"Failed to send MFA code: {exc}") from exc

    async def handle_mfa(self, adapter_name: str, context: MFAContext, code: str) -> bool:
        """
        Verify an MFA code using the requested adapter.
        """
        try:
            adapter = self.mfa_registry.create_adapter(adapter_name, self.config)
            return await adapter.verify_code(code, context)
        except Exception:
            return False

    async def refresh_tokens(self, provider_name: str, key: str) -> AuthTokens | None:
        """
        Refresh stored tokens and return the latest set.
        """
        if not self.token_manager:
            return None

        try:
            provider = self.provider_registry.create_provider(provider_name, self.config)
            return await self.token_manager.refresh_if_needed(key, provider)
        except Exception:
            return None

    async def revoke_tokens(self, key: str) -> None:
        """
        Revoke and remove stored tokens for the supplied key.
        """
        if not self.token_manager:
            return

        try:
            await self.token_manager.revoke(key)
        except Exception:
            return

    def get_available_providers(self) -> list[str]:
        """
        Return all registered provider names.
        """
        return self.provider_registry.list_providers()

    def get_available_mfa_adapters(self) -> list[str]:
        """
        Return all registered MFA adapter names.
        """
        return self.mfa_registry.list_adapters()

    def get_mfa_adapters_for_method(self, method: MFAMethod) -> list[str]:
        """
        Return adapters that support the supplied MFA method.
        """
        return self.mfa_registry.get_adapters_by_method(method)

    def _make_storage_key(self, provider_name: str, credentials: Credentials) -> str:
        """
        Derive a consistent storage key for token persistence.
        """
        identifier = (
            credentials.email or credentials.username or credentials.client_id or "anonymous"
        )
        return f"{provider_name}:{identifier}"


__all__ = ["AuthManager"]
