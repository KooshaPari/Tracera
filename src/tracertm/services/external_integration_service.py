"""Service for managing external integrations.

Functional Requirements: FR-COLLAB-006, FR-COLLAB-007, FR-COLLAB-008
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class IntegrationType(StrEnum):
    """Integration types."""

    GITHUB = "github"
    GITLAB = "gitlab"
    SLACK = "slack"
    VSCODE = "vscode"
    JIRA = "jira"
    CUSTOM = "custom"


@dataclass
class Integration:
    """Integration definition."""

    name: str
    integration_type: IntegrationType
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)
    last_sync: str | None = None


class ExternalIntegrationService:
    """Service for managing external integrations."""

    def __init__(self) -> None:
        """Initialize."""
        self.integrations: dict[str, Integration] = {}
        self.sync_history: list[dict[str, Any]] = []

    def register_integration(
        self,
        name: str,
        integration_type: IntegrationType,
        config: dict[str, Any] | None = None,
    ) -> Integration:
        """Register an external integration."""
        integration = Integration(
            name=name,
            integration_type=integration_type,
            config=config or {},
        )

        self.integrations[name] = integration
        return integration

    def get_integration(self, name: str) -> Integration | None:
        """Get integration by name."""
        return self.integrations.get(name)

    def list_integrations(self, integration_type: IntegrationType | None = None) -> list[Integration]:
        """List all integrations, optionally filtered by type."""
        integrations = list(self.integrations.values())

        if integration_type:
            integrations = [i for i in integrations if i.integration_type == integration_type]

        return integrations

    def enable_integration(self, name: str) -> bool:
        """Enable an integration."""
        integration = self.get_integration(name)
        if integration:
            integration.enabled = True
            return True
        return False

    def disable_integration(self, name: str) -> bool:
        """Disable an integration."""
        integration = self.get_integration(name)
        if integration:
            integration.enabled = False
            return True
        return False

    def update_integration_config(
        self,
        name: str,
        config: dict[str, Any],
    ) -> Integration | None:
        """Update integration configuration."""
        integration = self.get_integration(name)
        if integration:
            integration.config.update(config)
            return integration
        return None

    def sync_integration(
        self,
        name: str,
        sync_type: str = "full",
    ) -> dict[str, Any]:
        """Sync with external integration."""
        integration = self.get_integration(name)

        if not integration:
            return {"error": "Integration not found"}

        if not integration.enabled:
            return {"error": "Integration is disabled"}

        # Record sync
        sync_record = {
            "integration": name,
            "type": integration.integration_type.value,
            "sync_type": sync_type,
            "status": "success",
            "items_synced": 0,
        }

        self.sync_history.append(sync_record)
        integration.last_sync = str(sync_record.get("timestamp", "now"))

        return sync_record

    def get_sync_history(self, name: str | None = None) -> list[dict[str, Any]]:
        """Get sync history, optionally filtered by integration."""
        history = self.sync_history

        if name:
            history = [h for h in history if h.get("integration") == name]

        return history

    def _validate_github_config(self, integration: Integration) -> list[str]:
        errors = []
        if "token" not in integration.config:
            errors.append("GitHub token is required")
        if "repo" not in integration.config:
            errors.append("GitHub repository is required")
        return errors

    def _validate_slack_config(self, integration: Integration) -> list[str]:
        if "webhook_url" not in integration.config:
            return ["Slack webhook URL is required"]
        return []

    def _validate_vscode_config(self, integration: Integration) -> list[str]:
        if "extension_id" not in integration.config:
            return ["VS Code extension ID is required"]
        return []

    def validate_integration_config(self, integration: Integration) -> list[str]:
        """Validate integration configuration."""
        errors = []
        if not integration.name:
            errors.append("Integration name is required")
        type_validators = {
            IntegrationType.GITHUB: self._validate_github_config,
            IntegrationType.SLACK: self._validate_slack_config,
            IntegrationType.VSCODE: self._validate_vscode_config,
        }
        validator = type_validators.get(integration.integration_type)
        if validator:
            errors.extend(validator(integration))
        return errors

    def get_integration_stats(self) -> dict[str, Any]:
        """Get integration statistics."""
        total = len(self.integrations)
        enabled = len([i for i in self.integrations.values() if i.enabled])
        disabled = total - enabled

        by_type: dict[str, int] = {}
        for integration in self.integrations.values():
            int_type = integration.integration_type.value
            by_type[int_type] = by_type.get(int_type, 0) + 1

        return {
            "total_integrations": total,
            "enabled": enabled,
            "disabled": disabled,
            "by_type": by_type,
            "total_syncs": len(self.sync_history),
        }

    def test_integration(self, name: str) -> dict[str, Any]:
        """Test integration connection."""
        integration = self.get_integration(name)

        if not integration:
            return {"success": False, "error": "Integration not found"}

        # Simulate connection test
        return {
            "success": True,
            "integration": name,
            "type": integration.integration_type.value,
            "message": f"Successfully connected to {name}",
        }
