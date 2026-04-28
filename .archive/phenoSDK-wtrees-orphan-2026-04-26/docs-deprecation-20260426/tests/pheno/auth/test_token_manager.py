from datetime import UTC, datetime, timedelta

import pytest

from pheno.auth.interfaces import AuthProvider
from pheno.auth.token_manager import FileTokenManager
from pheno.auth.types import AuthResult, AuthTokens, Credentials, ProviderType


class DummyProvider(AuthProvider):
    """
    Minimal provider used for refresh tests.
    """

    def __init__(self):
        super().__init__("dummy", {})
        self._refresh_counter = 0

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OAUTH2

    async def authenticate(self, credentials: Credentials) -> AuthResult:
        return AuthResult(success=True, tokens=None)

    async def refresh(self, tokens: AuthTokens) -> AuthTokens:
        self._refresh_counter += 1
        return AuthTokens(
            access_token=f"new-token-{self._refresh_counter}",
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            metadata={"refreshed": True},
        )

    async def revoke(self, tokens: AuthTokens) -> bool:
        return True

    def supports_refresh(self) -> bool:
        return True

    def get_auth_url(self, state: str, redirect_uri: str) -> str:
        return "https://example.com/oauth"


@pytest.mark.asyncio
async def test_store_and_retrieve_tokens(tmp_path):
    manager = FileTokenManager(storage_path=tmp_path / "tokens.json")

    tokens = AuthTokens(
        access_token="abc123",
        refresh_token="refresh123",
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
        metadata={"scope": "read"},
    )

    await manager.store("user@example.com", tokens)

    retrieved = await manager.retrieve("user@example.com")
    assert retrieved is not None
    assert retrieved.access_token == "abc123"
    assert retrieved.refresh_token == "refresh123"
    assert retrieved.metadata.get("scope") == "read"


@pytest.mark.asyncio
async def test_refresh_expired_tokens(tmp_path):
    manager = FileTokenManager(storage_path=tmp_path / "tokens.json")
    provider = DummyProvider()

    expired = AuthTokens(
        access_token="old-token",
        refresh_token="refresh-token",
        expires_at=datetime.now(UTC) - timedelta(seconds=30),
    )
    await manager.store("user", expired)

    refreshed = await manager.refresh_if_needed("user", provider)
    assert refreshed is not None
    assert refreshed.access_token.startswith("new-token-")
    stored = await manager.retrieve("user")
    assert stored is not None
    assert stored.access_token == refreshed.access_token


@pytest.mark.asyncio
async def test_revoke_tokens(tmp_path):
    manager = FileTokenManager(storage_path=tmp_path / "tokens.json")

    tokens = AuthTokens(
        access_token="to-delete",
        expires_at=datetime.now(UTC) + timedelta(minutes=1),
    )
    await manager.store("user", tokens)
    assert await manager.retrieve("user") is not None

    await manager.revoke("user")
    assert await manager.retrieve("user") is None
