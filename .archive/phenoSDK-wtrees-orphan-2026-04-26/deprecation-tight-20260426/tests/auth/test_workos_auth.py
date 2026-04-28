"""
WorkOS Authentication Tests.
"""

from unittest.mock import Mock, patch

import pytest

from config.auth import AuthConfig, AuthProvider, WorkOSAuthKit, load_auth_config


class TestAuthConfig:
    """
    Test authentication configuration.
    """

    def test_auth_config_creation(self):
        config = AuthConfig(
            client_id="test_client_id",
            api_key="test_api_key",
            secret_key="test_secret",
            redirect_uri="http://localhost:3000/auth/callback",
            provider=AuthProvider.WORKOS,
        )

        assert config.client_id == "test_client_id"
        assert config.api_key == "test_api_key"
        assert config.secret_key == "test_secret"
        assert config.provider == AuthProvider.WORKOS
        assert config.enable_sso is True
        assert config.enable_mfa is True


class TestWorkOSAuthKit:
    """
    Test WorkOS AuthKit integration.
    """

    @pytest.fixture
    def auth_config(self):
        return AuthConfig(
            client_id="test_client_id",
            api_key="test_api_key",
            secret_key="test_secret",
            redirect_uri="http://localhost:3000/auth/callback",
            provider=AuthProvider.WORKOS,
            allowed_domains=["example.com"],
        )

    @pytest.fixture
    def auth_kit(self, auth_config):
        return WorkOSAuthKit(auth_config)

    def test_workos_import_error(self, auth_config):
        """
        Test ImportError when workos is not installed.
        """
        with patch.dict("sys.modules", {"workos": None}):
            auth_kit = WorkOSAuthKit(auth_config)
            with pytest.raises(ImportError, match="workos package is required"):
                auth_kit._get_client()

    @patch("config.auth.import_workos")
    def test_get_auth_url(self, mock_import, auth_kit):
        """
        Test OAuth URL generation.
        """
        # Mock WorkOS client
        mock_workos = Mock()
        mock_workos.sso.get_authorization_url.return_value = (
            "https://auth.workos.com/sso/authorize?..."
        )
        mock_import.return_value = mock_workos

        # Directly set the mocked client
        auth_kit._client = mock_workos

        url = auth_kit.get_auth_url("test_state")

        assert url == "https://auth.workos.com/sso/authorize?..."
        mock_workos.sso.get_authorization_url.assert_called_once_with(
            domain="example.com",
            redirect_uri="http://localhost:3000/auth/callback",
            state="test_state",
            provider=None,
        )


@pytest.mark.no_auth
class TestConfigLoading:
    """
    Test configuration loading from environment.
    """

    @patch.dict(
        "os.environ",
        {
            "WORKOS_CLIENT_ID": "env_client_id",
            "WORKOS_API_KEY": "env_api_key",
            "WORKOS_SECRET_KEY": "env_secret",
            "WORKOS_REDIRECT_URI": "http://localhost:8000/auth/callback",
            "ALLOWED_DOMAINS": "example.com,test.com",
            "ENABLE_SSO": "false",
            "ENABLE_MFA": "false",
        },
    )
    def test_load_auth_config_from_env(self):
        config = load_auth_config()

        assert config.client_id == "env_client_id"
        assert config.api_key == "env_api_key"
        assert config.secret_key == "env_secret"
        assert config.redirect_uri == "http://localhost:8000/auth/callback"
        assert config.allowed_domains == ["example.com", "test.com"]
        assert config.enable_sso is False
        assert config.enable_mfa is False
