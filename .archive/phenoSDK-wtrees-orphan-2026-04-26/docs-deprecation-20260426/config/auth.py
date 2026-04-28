"""
WorkOS AuthKit Enterprise Authentication Configuration.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AuthProvider(Enum):
    """
    Supported authentication providers.
    """

    WORKOS = "workos"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"


@dataclass
class AuthConfig:
    """
    Authentication configuration.
    """

    client_id: str
    api_key: str
    secret_key: str
    redirect_uri: str
    provider: AuthProvider
    allowed_domains: list | None = None
    enable_sso: bool = True
    enable_mfa: bool = True


class WorkOSAuthKit:
    """
    WorkOS AuthKit integration for enterprise authentication.
    """

    def __init__(self, config: AuthConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        """
        Lazily initialize WorkOS client.
        """
        if self._client is None:
            try:
                import workos

                workos.api_key = self.config.api_key
                workos.client_id = self.config.client_id
                self._client = workos
            except ImportError:
                raise ImportError("workos package is required. Install with: pip install workos")
        return self._client

    def get_auth_url(self, state: str, provider: str | None = None) -> str:
        """
        Generate OAuth authorization URL.
        """
        workos = self._get_client()

        return workos.sso.get_authorization_url(
            domain=self.config.allowed_domains[0] if self.config.allowed_domains else None,
            redirect_uri=self.config.redirect_uri,
            state=state,
            provider=provider,
        )

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Exchange authorization code for access token.
        """
        workos = self._get_client()

        profile = workos.sso.profile_from_code(code)
        return {
            "access_token": profile.access_token,
            "profile": {
                "id": profile.id,
                "email": profile.email,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "raw_attributes": profile.raw_attributes,
            },
        }

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """
        Verify and decode JWT token.
        """
        workos = self._get_client()

        try:
            profile = workos.sso.verify_access_token(token)
            return {
                "id": profile.id,
                "email": profile.email,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "raw_attributes": profile.raw_attributes,
            }
        except Exception:
            return None


def load_auth_config() -> AuthConfig:
    """
    Load authentication configuration from environment.
    """
    return AuthConfig(
        client_id=os.getenv("WORKOS_CLIENT_ID", ""),
        api_key=os.getenv("WORKOS_API_KEY", ""),
        secret_key=os.getenv("WORKOS_SECRET_KEY", ""),
        redirect_uri=os.getenv("WORKOS_REDIRECT_URI", "http://localhost:8000/auth/callback"),
        provider=AuthProvider.WORKOS,
        allowed_domains=(
            os.getenv("ALLOWED_DOMAINS", "").split(",") if os.getenv("ALLOWED_DOMAINS") else None
        ),
        enable_sso=os.getenv("ENABLE_SSO", "true").lower() == "true",
        enable_mfa=os.getenv("ENABLE_MFA", "true").lower() == "true",
    )


# Global auth instance
_auth_instance: WorkOSAuthKit | None = None


def get_auth_instance() -> WorkOSAuthKit:
    """
    Get global authentication instance.
    """
    global _auth_instance
    if _auth_instance is None:
        config = load_auth_config()
        _auth_instance = WorkOSAuthKit(config)
    return _auth_instance
