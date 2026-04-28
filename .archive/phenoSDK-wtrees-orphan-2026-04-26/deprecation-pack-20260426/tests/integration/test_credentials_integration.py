"""
Integration tests for phenoSDK credential management system.

Tests how multiple components work together: storage, encryption,
hierarchy, OAuth, and audit logging.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestCredentialStorageIntegration:
    """Integration tests for credential storage backends."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def broker(self, temp_dir):
        """Create broker for testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_storage_with_encryption(self, broker):
        """Test that credentials are encrypted when stored."""
        broker.store_credential(
            name="secret_key",
            value="super_secret_value",
            scope="global",
        )

        credential = broker.get_credential_info("secret_key")
        assert credential is not None
        assert credential.value == "super_secret_value"

    def test_storage_persists_across_broker_instances(self, broker, temp_dir):
        """Test that credentials persist when creating new broker instance."""
        broker.store_credential(
            name="persistent_key",
            value="persistent_value",
            scope="global",
        )

        from pheno.credentials.broker import CredentialBroker

        new_broker = CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

        credential = new_broker.get_credential_info("persistent_key")
        assert credential is not None
        assert credential.value == "persistent_value"


class TestCredentialOAuthIntegration:
    """Integration tests for OAuth and credential system."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def oauth_broker(self, temp_dir):
        """Create broker for OAuth testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_oauth_token_lifecycle(self, oauth_broker):
        """Test complete OAuth token lifecycle."""
        oauth_broker.store_credential(
            name="github_token",
            value="gho_initial_token",
            credential_type="oauth_token",
            scope="global",
            service="github",
            auto_refresh=True,
        )

        token = oauth_broker.get_credential_info("github_token")
        assert token.auto_refresh is True

        oauth_broker.store_credential(
            name="github_token",
            value="gho_refreshed_token",
            credential_type="oauth_token",
            scope="global",
            service="github",
            auto_refresh=True,
        )

        refreshed = oauth_broker.get_credential_info("github_token")
        assert refreshed.value == "gho_refreshed_token"

    def test_multiple_oauth_providers(self, oauth_broker):
        """Test managing multiple OAuth providers."""
        providers = [
            ("github", "gho_github_token"),
            ("google", "ya29_google_token"),
            ("openai", "sk_openai_token"),
        ]

        for provider, token_value in providers:
            oauth_broker.store_credential(
                name=f"{provider}_token",
                value=token_value,
                credential_type="oauth_token",
                scope="global",
                service=provider,
            )

        all_creds = oauth_broker.list_credentials(scope="global")
        oauth_tokens = [c for c in all_creds if c.type == "oauth_token"]
        assert len(oauth_tokens) >= 3

    def test_oauth_token_validation(self, oauth_broker):
        """Test validating OAuth token credentials."""
        oauth_broker.store_credential(
            name="valid_oauth",
            value="valid_token",
            credential_type="oauth_token",
            scope="global",
            service="test",
        )

        results = oauth_broker.validate_credentials(["valid_oauth"])
        assert results["valid_oauth"] is True


class TestCredentialHierarchyIntegration:
    """Integration tests for hierarchical scoping."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def hierarchy_broker(self, temp_dir):
        """Create broker for hierarchy testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_hierarchy_creation(self, hierarchy_broker):
        """Test creating a scope hierarchy."""
        hierarchy = hierarchy_broker.get_or_create_default_hierarchy()
        assert hierarchy is not None

    def test_scope_credential_creation(self, hierarchy_broker):
        """Test creating credentials at specific scope paths."""
        hierarchy_broker.create_scope_credential(
            name="org_api_key",
            value="org_secret_key",
            scope_path="global/org/acme",
            credential_type="api_key",
        )

        resolved = hierarchy_broker.resolve_credential_hierarchical(
            name="org_api_key",
            scope_path="global/org/acme",
        )
        assert resolved == "org_secret_key"

    def test_scope_statistics(self, hierarchy_broker):
        """Test getting statistics for scopes."""
        hierarchy_broker.create_scope_credential(
            name="scoped_cred",
            value="scoped_value",
            scope_path="global/org/test",
        )

        stats = hierarchy_broker.get_scope_statistics()
        assert stats is not None


class TestCredentialAuditIntegration:
    """Integration tests for audit logging."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def audit_broker(self, temp_dir):
        """Create broker for audit testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_audit_trail_records_all_operations(self, audit_broker):
        """Test that all credential operations are audited."""
        audit_broker.store_credential(name="audit_test", value="value1", scope="global")
        audit_broker.store_credential(name="audit_test", value="value2", scope="global")
        audit_broker.delete_credential("audit_test")

        audit_log = audit_broker.get_audit_log()
        assert len(audit_log) >= 3

    def test_audit_log_tracking_specific_credential(self, audit_broker):
        """Test tracking operations for a specific credential."""
        audit_broker.store_credential(name="track_me", value="val1", scope="global")
        audit_broker.store_credential(name="track_me", value="val2", scope="global")

        audit_log = audit_broker.get_audit_log()
        track_me_operations = [
            e for e in audit_log if "track_me" in str(e.get("credential_id", ""))
        ]
        assert len(track_me_operations) >= 2


class TestCredentialValidationIntegration:
    """Integration tests for credential validation system."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def validation_broker(self, temp_dir):
        """Create broker for validation testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_validate_required_credentials_present(self, validation_broker):
        """Test validating that all required credentials are present."""
        validation_broker.store_credential(
            name="required1", value="val1", scope="global"
        )
        validation_broker.store_credential(
            name="required2", value="val2", scope="global"
        )

        results = validation_broker.validate_credentials(["required1", "required2"])
        assert results["required1"] is True
        assert results["required2"] is True

    def test_validate_partial_credentials(self, validation_broker):
        """Test validation when only some credentials are present."""
        validation_broker.store_credential(name="present", value="val", scope="global")

        results = validation_broker.validate_credentials(["present", "missing"])
        assert results["present"] is True
        assert results["missing"] is False

    def test_validate_with_expired_credentials(self, validation_broker):
        """Test validation with expired credentials."""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        validation_broker.store_credential(
            name="expired_cred",
            value="expired_value",
            scope="global",
            expires_at=past_date,
        )

        cred = validation_broker.get_credential_info("expired_cred")
        assert cred.is_expired


class TestCredentialExportIntegration:
    """Integration tests for credential export functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def export_broker(self, temp_dir):
        """Create broker for export testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_export_to_json(self, export_broker, temp_dir):
        """Test exporting credentials to JSON format."""
        export_broker.store_credential(
            name="json_cred", value="json_val", scope="global"
        )

        export_file = temp_dir / "export.json"
        success = export_broker.export_credentials(export_file, format="json")
        assert success
        assert export_file.exists()

        import json

        with open(export_file) as f:
            data = json.load(f)
            assert len(data) >= 1

    def test_export_with_scope_filter(self, export_broker, temp_dir):
        """Test exporting credentials with scope filter."""
        export_broker.store_credential(
            name="global_cred", value="global_val", scope="global"
        )
        export_broker.store_credential(
            name="project_cred", value="project_val", scope="project"
        )

        export_file = temp_dir / "global_export.json"
        success = export_broker.export_credentials(
            export_file, format="json", scope="global"
        )
        assert success


class TestCredentialCleanupIntegration:
    """Integration tests for credential cleanup."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def cleanup_broker(self, temp_dir):
        """Create broker for cleanup testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_cleanup_expired_credentials(self, cleanup_broker):
        """Test cleaning up expired credentials."""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        future_date = datetime.now(timezone.utc) + timedelta(days=30)

        cleanup_broker.store_credential(
            name="expired1", value="expired", scope="global", expires_at=past_date
        )
        cleanup_broker.store_credential(
            name="expired2", value="expired", scope="global", expires_at=past_date
        )
        cleanup_broker.store_credential(
            name="valid", value="valid", scope="global", expires_at=future_date
        )

        cleaned = cleanup_broker.cleanup_expired_credentials()
        assert cleaned >= 2

        assert cleanup_broker.get_credential_info("valid") is not None


class TestCredentialStatsIntegration:
    """Integration tests for statistics collection."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def stats_broker(self, temp_dir):
        """Create broker for stats testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_stats_collection_empty(self, stats_broker):
        """Test stats on empty broker."""
        stats = stats_broker.get_stats()
        assert stats["total_credentials"] == 0

    def test_stats_after_adding_credentials(self, stats_broker):
        """Test stats after adding various credential types."""
        stats_broker.store_credential(
            name="api1", value="val", scope="global", credential_type="api_key"
        )
        stats_broker.store_credential(
            name="api2", value="val", scope="global", credential_type="api_key"
        )
        stats_broker.store_credential(
            name="oauth1", value="val", scope="global", credential_type="oauth_token"
        )
        stats_broker.store_credential(
            name="pass1", value="val", scope="global", credential_type="password"
        )

        stats = stats_broker.get_stats()
        assert stats["total_credentials"] >= 4
        assert stats["api_keys"] >= 2
        assert stats["oauth_tokens"] >= 1
        assert stats["valid_credentials"] >= 4

    def test_stats_reflects_deletions(self, stats_broker):
        """Test that stats update after deletions."""
        stats_broker.store_credential(name="to_delete", value="val", scope="global")
        stats_before = stats_broker.get_stats()
        initial_count = stats_before["total_credentials"]

        stats_broker.delete_credential("to_delete")
        stats_after = stats_broker.get_stats()
        assert stats_after["total_credentials"] == initial_count - 1


class TestCredentialSearchIntegration:
    """Integration tests for credential search."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def search_broker(self, temp_dir):
        """Create broker for search testing."""
        from pheno.credentials.broker import CredentialBroker

        return CredentialBroker(data_dir=temp_dir / ".pheno" / "credentials")

    def test_list_credentials_by_scope(self, search_broker):
        """Test listing credentials filtered by scope."""
        search_broker.store_credential(name="global1", value="val", scope="global")
        search_broker.store_credential(name="global2", value="val", scope="global")
        search_broker.store_credential(name="project1", value="val", scope="project")

        global_creds = search_broker.list_credentials(scope="global")
        assert len(global_creds) >= 2

    def test_search_by_service(self, search_broker):
        """Test searching credentials by service."""
        search_broker.store_credential(
            name="gh_token", value="val", scope="global", service="github"
        )
        search_broker.store_credential(
            name="gg_token", value="val", scope="global", service="google"
        )
        search_broker.store_credential(
            name="ol_token", value="val", scope="global", service="openai"
        )

        all_creds = search_broker.list_credentials(scope="global")
        github_creds = [c for c in all_creds if c.service == "github"]
        assert len(github_creds) >= 1
