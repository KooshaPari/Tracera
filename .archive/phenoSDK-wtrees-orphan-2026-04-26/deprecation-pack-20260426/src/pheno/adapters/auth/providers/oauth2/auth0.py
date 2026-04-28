"""
Auth0 specific OAuth2 provider implementation for ``pheno``.
"""

from __future__ import annotations

from pheno.domain.auth.types import AuthResult, Credentials

from .generic import OAuth2GenericProvider


class Auth0Provider(OAuth2GenericProvider):
    """
    Auth0 aware OAuth2 provider.
    """

    def __init__(self, name: str, config: dict[str, object]):
        domain = config.get("domain")
        if not domain:
            raise ValueError("Auth0 domain is required")
        config.setdefault("auth_url", f"https://{domain}/authorize")
        config.setdefault("token_url", f"https://{domain}/oauth/token")
        config.setdefault("userinfo_url", f"https://{domain}/userinfo")
        config.setdefault("revoke_url", f"https://{domain}/v2/logout")
        config.setdefault("scope", "openid profile email")
        super().__init__(name, config)
        self.domain = domain
        self.audience = config.get("audience")

    def get_auth_url(self, state: str, redirect_uri: str) -> str:
        auth_url = super().get_auth_url(state, redirect_uri)
        if self.audience:
            separator = "&" if "?" in auth_url else "?"
            auth_url = f"{auth_url}{separator}audience={self.audience}"
        return auth_url

    async def authenticate(self, credentials: Credentials) -> AuthResult:
        result = await super().authenticate(credentials)
        if result.success and result.tokens:
            try:
                await self._validate_auth0_tokens(result.tokens)
            except Exception as exc:
                return AuthResult(
                    success=False,
                    error=f"Auth0 token validation failed: {exc}",
                    error_code="auth0_token_validation_failed",
                )
        return result

    async def _validate_auth0_tokens(self, tokens) -> None:
        return


__all__ = ["Auth0Provider"]
