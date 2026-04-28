"""Authentication manager orchestration layer.

Consolidated from:
- pheno.auth.core.manager (core auth logic)
- authkit.client.manager (OAuth management)
- pheno.mcp.qa.auth.manager (testing auth)

Provides unified authentication orchestration.
"""

import logging
from datetime import datetime
from typing import Any

from .interfaces import (
    AuthProviderProtocol,
    MFAProviderProtocol,
    OAuthProviderProtocol,
    SessionProviderProtocol,
)
from .types import AuthRequest, AuthResponse, AuthSession, AuthToken, AuthUser, MFAType

logger = logging.getLogger(__name__)


class AuthManager:
    """Coordinates unified authentication flows across providers.

    Consolidates authentication logic from multiple implementations into a single,
    coherent system.
    """

    def __init__(
        self,
        providers: dict[str, AuthProviderProtocol] | None = None,
        mfa_providers: dict[str, MFAProviderProtocol] | None = None,
        session_provider: SessionProviderProtocol | None = None,
        default_provider: str = "local",
    ):
        self.providers = providers or {}
        self.mfa_providers = mfa_providers or {}
        self.session_provider = session_provider
        self.default_provider = default_provider

        # OAuth state management (consolidated from authkit)
        self._oauth_states: dict[str, dict[str, Any]] = {}

    def register_provider(self, name: str, provider: AuthProviderProtocol) -> None:
        """
        Register an authentication provider.
        """
        self.providers[name] = provider
        logger.info(f"Registered auth provider: {name}")

    def register_mfa_provider(self, mfa_type: MFAType, provider: MFAProviderProtocol) -> None:
        """
        Register an MFA provider.
        """
        self.mfa_providers[mfa_type.value] = provider
        logger.info(f"Registered MFA provider: {mfa_type.value}")

    def set_session_provider(self, provider: SessionProviderProtocol) -> None:
        """
        Set the session provider.
        """
        self.session_provider = provider

    async def authenticate(self, request: AuthRequest) -> AuthResponse:
        """Unified authentication method.

        Consolidates authentication flows from multiple implementations.
        """
        try:
            # Determine provider
            provider_name = request.provider or self.default_provider
            provider = self.providers.get(provider_name)

            if not provider:
                return AuthResponse(
                    success=False,
                    error="invalid_provider",
                    error_description=f"Authentication provider '{provider_name}' not found",
                )

            # Authenticate with provider
            response = await provider.authenticate(request)

            if not response.success:
                return response

            # Handle MFA if required
            if response.requires_mfa and response.user:
                return await self._handle_mfa_flow(response, request)

            # Create session if session provider available
            if self.session_provider and response.user and response.token:
                session = await self.session_provider.create_session(
                    response.user, response.token, {"provider": provider_name},
                )
                response.session = session

            return response

        except Exception as e:
            logger.exception(f"Authentication error: {e}")
            return AuthResponse(
                success=False, error="authentication_error", error_description=str(e),
            )

    async def _handle_mfa_flow(self, response: AuthResponse, request: AuthRequest) -> AuthResponse:
        """
        Handle MFA authentication flow.
        """
        if not response.user:
            return response

        # Check if MFA code provided
        if not request.mfa_code or not request.mfa_type:
            # MFA required but not provided
            return AuthResponse(
                success=False, requires_mfa=True, mfa_types=response.mfa_types, error="mfa_required",
            )

        # Verify MFA
        mfa_provider = self.mfa_providers.get(request.mfa_type.value)
        if not mfa_provider:
            return AuthResponse(
                success=False,
                error="invalid_mfa_type",
                error_description=f"MFA type '{request.mfa_type}' not supported",
            )

        mfa_valid = await mfa_provider.verify_mfa(response.user, request.mfa_code)
        if not mfa_valid:
            return AuthResponse(
                success=False, error="invalid_mfa_code", error_description="Invalid MFA code",
            )

        # MFA successful - complete authentication
        return response

    async def refresh_token(
        self, refresh_token: str, provider_name: str | None = None,
    ) -> AuthToken | None:
        """
        Refresh an authentication token.
        """
        if provider_name:
            provider = self.providers.get(provider_name)
            if provider:
                return await provider.refresh_token(refresh_token)
        else:
            # Try all providers
            for provider in self.providers.values():
                try:
                    token = await provider.refresh_token(refresh_token)
                    if token:
                        return token
                except Exception:
                    continue

        return None

    async def get_user(
        self, user_id: str, provider_name: str | None = None,
    ) -> AuthUser | None:
        """
        Get user information.
        """
        if provider_name:
            provider = self.providers.get(provider_name)
            if provider:
                return await provider.get_user(user_id)
        else:
            # Try all providers
            for provider in self.providers.values():
                try:
                    user = await provider.get_user(user_id)
                    if user:
                        return user
                except Exception:
                    continue

        return None

    async def setup_mfa(self, user: AuthUser, mfa_type: MFAType) -> dict[str, Any]:
        """
        Set up MFA for a user.
        """
        mfa_provider = self.mfa_providers.get(mfa_type.value)
        if not mfa_provider:
            raise ValueError(f"MFA type '{mfa_type}' not supported")

        return await mfa_provider.setup_mfa(user)

    async def validate_session(self, session_id: str) -> AuthSession | None:
        """
        Validate and return session.
        """
        if not self.session_provider:
            return None
        session = await self.session_provider.get_session(session_id)
        if session and session.is_active and not session.is_expired():
            # Update last activity timestamp for sliding expiration
            session.last_activity = datetime.utcnow()
            return session

        return None

    async def logout(self, session_id: str) -> bool:
        """
        Log out user by invalidating session.
        """
        if not self.session_provider:
            return False

        return await self.session_provider.invalidate_session(session_id)

    # OAuth-specific methods (consolidated from authkit)

    def get_oauth_provider(self, provider_name: str) -> OAuthProviderProtocol | None:
        """
        Get OAuth provider.
        """
        provider = self.providers.get(provider_name)
        if isinstance(provider, OAuthProviderProtocol):
            return provider
        return None

    def create_oauth_state(self, state: str, metadata: dict[str, Any]) -> None:
        """
        Create OAuth state for CSRF protection.
        """
        self._oauth_states[state] = {"created_at": datetime.utcnow(), "metadata": metadata}

    def validate_oauth_state(self, state: str) -> dict[str, Any] | None:
        """
        Validate OAuth state.
        """
        state_data = self._oauth_states.pop(state, None)
        if not state_data:
            return None

        # Check expiry (5 minutes)
        if (datetime.utcnow() - state_data["created_at"]).total_seconds() > 300:
            return None

        return state_data["metadata"]

    def get_oauth_authorization_url(
        self,
        provider_name: str,
        redirect_uri: str,
        scope: str | None = None,
        state: str | None = None,
    ) -> str | None:
        """
        Get OAuth authorization URL.
        """
        provider = self.get_oauth_provider(provider_name)
        if not provider:
            return None

        # Generate state if not provided
        if not state:
            import secrets

            state = secrets.token_urlsafe(32)
            self.create_oauth_state(
                state, {"provider": provider_name, "redirect_uri": redirect_uri, "scope": scope},
            )

        return provider.get_authorization_url(state, scope)

