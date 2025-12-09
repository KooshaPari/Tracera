"""
Comprehensive tests for ExternalIntegrationService.

Tests all methods: register_integration, get_integration, list_integrations,
enable_integration, disable_integration, update_integration_config,
sync_integration, get_sync_history, validate_integration_config,
get_integration_stats, test_integration.

Coverage target: 85%+
"""

import pytest

from tracertm.services.external_integration_service import (
    ExternalIntegrationService,
    Integration,
    IntegrationType,
)


class TestIntegrationType:
    """Test IntegrationType enum."""

    def test_github_type(self):
        """Test GitHub type."""
        assert IntegrationType.GITHUB == "github"

    def test_gitlab_type(self):
        """Test GitLab type."""
        assert IntegrationType.GITLAB == "gitlab"

    def test_slack_type(self):
        """Test Slack type."""
        assert IntegrationType.SLACK == "slack"

    def test_vscode_type(self):
        """Test VS Code type."""
        assert IntegrationType.VSCODE == "vscode"

    def test_jira_type(self):
        """Test JIRA type."""
        assert IntegrationType.JIRA == "jira"

    def test_custom_type(self):
        """Test custom type."""
        assert IntegrationType.CUSTOM == "custom"


class TestIntegration:
    """Test Integration dataclass."""

    def test_integration_defaults(self):
        """Test Integration default values."""
        integration = Integration(
            name="test",
            integration_type=IntegrationType.GITHUB,
        )
        assert integration.name == "test"
        assert integration.integration_type == IntegrationType.GITHUB
        assert integration.enabled is True
        assert integration.config == {}
        assert integration.last_sync is None

    def test_integration_with_all_fields(self):
        """Test Integration with all fields."""
        integration = Integration(
            name="my-github",
            integration_type=IntegrationType.GITHUB,
            enabled=False,
            config={"token": "secret", "repo": "org/repo"},
            last_sync="2024-01-01T12:00:00",
        )
        assert integration.name == "my-github"
        assert integration.enabled is False
        assert integration.config["token"] == "secret"
        assert integration.last_sync == "2024-01-01T12:00:00"


class TestRegisterIntegration:
    """Test register_integration method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ExternalIntegrationService()

    def test_register_basic(self, service):
        """Test registering basic integration."""
        result = service.register_integration(
            name="github-prod",
            integration_type=IntegrationType.GITHUB,
        )

        assert result.name == "github-prod"
        assert result.integration_type == IntegrationType.GITHUB
        assert result.enabled is True

    def test_register_with_config(self, service):
        """Test registering integration with config."""
        result = service.register_integration(
            name="slack-alerts",
            integration_type=IntegrationType.SLACK,
            config={"webhook_url": "https://hooks.slack.com/test"},
        )

        assert result.config["webhook_url"] == "https://hooks.slack.com/test"

    def test_register_stores_in_dict(self, service):
        """Test registered integration is stored."""
        service.register_integration(
            name="my-integration",
            integration_type=IntegrationType.CUSTOM,
        )

        assert "my-integration" in service.integrations

    def test_register_none_config_uses_empty_dict(self, service):
        """Test None config defaults to empty dict."""
        result = service.register_integration(
            name="test",
            integration_type=IntegrationType.VSCODE,
            config=None,
        )

        assert result.config == {}


class TestGetIntegration:
    """Test get_integration method."""

    @pytest.fixture
    def service(self):
        """Create service with registered integration."""
        service = ExternalIntegrationService()
        service.register_integration(
            name="existing",
            integration_type=IntegrationType.GITHUB,
        )
        return service

    def test_get_existing(self, service):
        """Test getting existing integration."""
        result = service.get_integration("existing")

        assert result is not None
        assert result.name == "existing"

    def test_get_nonexistent(self, service):
        """Test getting nonexistent integration."""
        result = service.get_integration("nonexistent")

        assert result is None


class TestListIntegrations:
    """Test list_integrations method."""

    @pytest.fixture
    def service(self):
        """Create service with multiple integrations."""
        service = ExternalIntegrationService()
        service.register_integration("gh1", IntegrationType.GITHUB)
        service.register_integration("gh2", IntegrationType.GITHUB)
        service.register_integration("slack", IntegrationType.SLACK)
        return service

    def test_list_all(self, service):
        """Test listing all integrations."""
        result = service.list_integrations()

        assert len(result) == 3

    def test_list_filtered_by_type(self, service):
        """Test listing filtered by type."""
        result = service.list_integrations(IntegrationType.GITHUB)

        assert len(result) == 2
        assert all(i.integration_type == IntegrationType.GITHUB for i in result)

    def test_list_no_matches(self, service):
        """Test listing with no matches."""
        result = service.list_integrations(IntegrationType.JIRA)

        assert result == []


class TestEnableDisableIntegration:
    """Test enable_integration and disable_integration methods."""

    @pytest.fixture
    def service(self):
        """Create service with integration."""
        service = ExternalIntegrationService()
        service.register_integration("test", IntegrationType.GITHUB)
        return service

    def test_disable_existing(self, service):
        """Test disabling existing integration."""
        result = service.disable_integration("test")

        assert result is True
        assert service.get_integration("test").enabled is False

    def test_enable_existing(self, service):
        """Test enabling existing integration."""
        service.disable_integration("test")
        result = service.enable_integration("test")

        assert result is True
        assert service.get_integration("test").enabled is True

    def test_disable_nonexistent(self, service):
        """Test disabling nonexistent integration."""
        result = service.disable_integration("nonexistent")

        assert result is False

    def test_enable_nonexistent(self, service):
        """Test enabling nonexistent integration."""
        result = service.enable_integration("nonexistent")

        assert result is False


class TestUpdateIntegrationConfig:
    """Test update_integration_config method."""

    @pytest.fixture
    def service(self):
        """Create service with integration."""
        service = ExternalIntegrationService()
        service.register_integration(
            "test",
            IntegrationType.GITHUB,
            config={"token": "old-token"},
        )
        return service

    def test_update_existing(self, service):
        """Test updating existing integration config."""
        result = service.update_integration_config(
            "test",
            {"token": "new-token", "repo": "org/repo"},
        )

        assert result is not None
        assert result.config["token"] == "new-token"
        assert result.config["repo"] == "org/repo"

    def test_update_nonexistent(self, service):
        """Test updating nonexistent integration."""
        result = service.update_integration_config(
            "nonexistent",
            {"key": "value"},
        )

        assert result is None


class TestSyncIntegration:
    """Test sync_integration method."""

    @pytest.fixture
    def service(self):
        """Create service with integration."""
        service = ExternalIntegrationService()
        service.register_integration("enabled", IntegrationType.GITHUB)
        integration = service.register_integration("disabled", IntegrationType.SLACK)
        integration.enabled = False
        return service

    def test_sync_enabled(self, service):
        """Test syncing enabled integration."""
        result = service.sync_integration("enabled")

        assert result["status"] == "success"
        assert result["integration"] == "enabled"
        assert result["type"] == "github"
        assert result["sync_type"] == "full"

    def test_sync_with_custom_type(self, service):
        """Test syncing with custom sync type."""
        result = service.sync_integration("enabled", sync_type="incremental")

        assert result["sync_type"] == "incremental"

    def test_sync_disabled(self, service):
        """Test syncing disabled integration."""
        result = service.sync_integration("disabled")

        assert result["error"] == "Integration is disabled"

    def test_sync_nonexistent(self, service):
        """Test syncing nonexistent integration."""
        result = service.sync_integration("nonexistent")

        assert result["error"] == "Integration not found"

    def test_sync_records_history(self, service):
        """Test sync records history."""
        service.sync_integration("enabled")

        assert len(service.sync_history) == 1
        assert service.sync_history[0]["integration"] == "enabled"

    def test_sync_updates_last_sync(self, service):
        """Test sync updates last_sync."""
        service.sync_integration("enabled")

        integration = service.get_integration("enabled")
        assert integration.last_sync is not None


class TestGetSyncHistory:
    """Test get_sync_history method."""

    @pytest.fixture
    def service(self):
        """Create service with sync history."""
        service = ExternalIntegrationService()
        service.register_integration("gh", IntegrationType.GITHUB)
        service.register_integration("slack", IntegrationType.SLACK)
        service.sync_integration("gh")
        service.sync_integration("gh")
        service.sync_integration("slack")
        return service

    def test_get_all_history(self, service):
        """Test getting all sync history."""
        result = service.get_sync_history()

        assert len(result) == 3

    def test_get_filtered_history(self, service):
        """Test getting filtered history."""
        result = service.get_sync_history("gh")

        assert len(result) == 2
        assert all(h["integration"] == "gh" for h in result)

    def test_get_empty_history(self):
        """Test getting empty history."""
        service = ExternalIntegrationService()
        result = service.get_sync_history()

        assert result == []


class TestValidateIntegrationConfig:
    """Test validate_integration_config method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ExternalIntegrationService()

    def test_validate_empty_name(self, service):
        """Test validation with empty name."""
        integration = Integration(
            name="",
            integration_type=IntegrationType.GITHUB,
        )

        errors = service.validate_integration_config(integration)

        assert "Integration name is required" in errors

    def test_validate_github_missing_token(self, service):
        """Test GitHub validation missing token."""
        integration = Integration(
            name="gh",
            integration_type=IntegrationType.GITHUB,
            config={"repo": "org/repo"},
        )

        errors = service.validate_integration_config(integration)

        assert "GitHub token is required" in errors

    def test_validate_github_missing_repo(self, service):
        """Test GitHub validation missing repo."""
        integration = Integration(
            name="gh",
            integration_type=IntegrationType.GITHUB,
            config={"token": "secret"},
        )

        errors = service.validate_integration_config(integration)

        assert "GitHub repository is required" in errors

    def test_validate_github_valid(self, service):
        """Test valid GitHub config."""
        integration = Integration(
            name="gh",
            integration_type=IntegrationType.GITHUB,
            config={"token": "secret", "repo": "org/repo"},
        )

        errors = service.validate_integration_config(integration)

        assert errors == []

    def test_validate_slack_missing_webhook(self, service):
        """Test Slack validation missing webhook."""
        integration = Integration(
            name="slack",
            integration_type=IntegrationType.SLACK,
            config={},
        )

        errors = service.validate_integration_config(integration)

        assert "Slack webhook URL is required" in errors

    def test_validate_slack_valid(self, service):
        """Test valid Slack config."""
        integration = Integration(
            name="slack",
            integration_type=IntegrationType.SLACK,
            config={"webhook_url": "https://hooks.slack.com/test"},
        )

        errors = service.validate_integration_config(integration)

        assert errors == []

    def test_validate_vscode_missing_extension(self, service):
        """Test VS Code validation missing extension ID."""
        integration = Integration(
            name="vscode",
            integration_type=IntegrationType.VSCODE,
            config={},
        )

        errors = service.validate_integration_config(integration)

        assert "VS Code extension ID is required" in errors

    def test_validate_vscode_valid(self, service):
        """Test valid VS Code config."""
        integration = Integration(
            name="vscode",
            integration_type=IntegrationType.VSCODE,
            config={"extension_id": "tracertm.vscode"},
        )

        errors = service.validate_integration_config(integration)

        assert errors == []


class TestGetIntegrationStats:
    """Test get_integration_stats method."""

    @pytest.fixture
    def service(self):
        """Create service with integrations."""
        service = ExternalIntegrationService()
        service.register_integration("gh1", IntegrationType.GITHUB)
        service.register_integration("gh2", IntegrationType.GITHUB)
        int3 = service.register_integration("slack", IntegrationType.SLACK)
        int3.enabled = False
        service.sync_integration("gh1")
        service.sync_integration("gh1")
        return service

    def test_get_stats(self, service):
        """Test getting integration stats."""
        result = service.get_integration_stats()

        assert result["total_integrations"] == 3
        assert result["enabled"] == 2
        assert result["disabled"] == 1
        assert result["by_type"]["github"] == 2
        assert result["by_type"]["slack"] == 1
        assert result["total_syncs"] == 2

    def test_get_stats_empty(self):
        """Test getting stats with no integrations."""
        service = ExternalIntegrationService()
        result = service.get_integration_stats()

        assert result["total_integrations"] == 0
        assert result["enabled"] == 0
        assert result["disabled"] == 0
        assert result["by_type"] == {}
        assert result["total_syncs"] == 0


class TestTestIntegration:
    """Test test_integration method."""

    @pytest.fixture
    def service(self):
        """Create service with integration."""
        service = ExternalIntegrationService()
        service.register_integration("test", IntegrationType.GITHUB)
        return service

    def test_test_existing(self, service):
        """Test testing existing integration."""
        result = service.test_integration("test")

        assert result["success"] is True
        assert result["integration"] == "test"
        assert result["type"] == "github"
        assert "Successfully connected" in result["message"]

    def test_test_nonexistent(self, service):
        """Test testing nonexistent integration."""
        result = service.test_integration("nonexistent")

        assert result["success"] is False
        assert result["error"] == "Integration not found"


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_empty_collections(self):
        """Test initialization creates empty collections."""
        service = ExternalIntegrationService()

        assert service.integrations == {}
        assert service.sync_history == []
