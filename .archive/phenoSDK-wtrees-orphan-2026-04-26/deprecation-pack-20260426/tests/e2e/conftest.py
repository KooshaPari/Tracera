"""
Pytest configuration and shared fixtures for phenoSDK E2E tests.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def credential_broker(temp_dir):
    """Create a CredentialBroker with temporary storage."""
    from pheno.credentials.broker import CredentialBroker

    broker = CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")
    yield broker


@pytest.fixture
def sample_credentials():
    """Sample credentials for testing."""
    return [
        {
            "name": "github_token",
            "value": "gho_test_token",
            "credential_type": "oauth_token",
            "scope": "global",
            "service": "github",
        },
        {
            "name": "api_key",
            "value": "sk_test_api_key",
            "credential_type": "api_key",
            "scope": "global",
            "service": "openai",
        },
        {
            "name": "database_password",
            "value": "secure_db_password",
            "credential_type": "password",
            "scope": "project",
            "description": "Main database password",
        },
    ]


@pytest.fixture
def populated_broker(credential_broker, sample_credentials):
    """Create a broker with sample credentials pre-loaded."""
    for cred in sample_credentials:
        credential_broker.store_credential(**cred)
    return credential_broker


@pytest.fixture
def expired_credential_broker(credential_broker):
    """Create a broker with an expired credential."""
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    credential_broker.store_credential(
        name="expired_token",
        value="expired_token_value",
        scope="global",
        expires_at=past_date,
    )
    return credential_broker


@pytest.fixture
def oauth_broker(credential_broker):
    """Create a broker with OAuth tokens."""
    providers = [
        ("github", "gho_xxx"),
        ("google", "ya29.xxx"),
        ("openai", "sk-xxx"),
        ("microsoft", "ms_xxx"),
    ]

    for provider, token in providers:
        credential_broker.store_credential(
            name=f"{provider}_token",
            value=token,
            credential_type="oauth_token",
            scope="global",
            service=provider,
            auto_refresh=True,
        )

    return credential_broker
