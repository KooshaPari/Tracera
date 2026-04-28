"""
AuthKit specific OAuth2 provider implementation for ``pheno``.
"""

from __future__ import annotations

from pheno.domain.auth.types import AuthResult, Credentials

from .generic import OAuth2GenericProvider


class AuthKitProvider(OAuth2GenericProvider):
    """
    AuthKit aware OAuth2 provider with sensible defaults.
    """

    def __init__(self, name: str, config: dict[str, object]):
        config.setdefault("auth_url", "https://auth.kooshapari.com/oauth/authorize")
        config.setdefault("token_url", "https://auth.kooshapari.com/oauth/token")
        config.setdefault("userinfo_url", "https://auth.kooshapari.com/oauth/userinfo")
        config.setdefault("revoke_url", "https://auth.kooshapari.com/oauth/revoke")
        config.setdefault("scope", "openid profile email")
        super().__init__(name, config)

    async def authenticate(self, credentials: Credentials) -> AuthResult:
        if credentials.email and credentials.password:
            return await self._authenticate_direct(credentials)
        return await super().authenticate(credentials)

    async def _authenticate_direct(self, credentials: Credentials) -> AuthResult:
        return AuthResult(
            success=False,
            error="Direct authentication not yet implemented",
            error_code="not_implemented",
        )

    def get_auth_url(self, state: str, redirect_uri: str) -> str:
        auth_url = super().get_auth_url(state, redirect_uri)
        separator = "&" if "?" in auth_url else "?"
        return f"{auth_url}{separator}prompt=consent"


__all__ = ["AuthKitProvider"]
