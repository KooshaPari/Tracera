"""
Comprehensive tests for SecurityComplianceService.

Tests all methods including:
- enable_encryption, disable_encryption, is_encryption_enabled
- log_audit_event, get_audit_log, get_audit_stats, clear_audit_log
- hash_sensitive_data
- validate_access_control
- generate_compliance_report

Coverage target: 90%+
"""

import pytest
import hashlib
from unittest.mock import AsyncMock
from tracertm.services.security_compliance_service import SecurityComplianceService


class TestEncryption:
    """Test encryption-related methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return SecurityComplianceService(AsyncMock())

    def test_enable_encryption(self, service):
        """Test enabling encryption."""
        result = service.enable_encryption()

        assert result["encryption_enabled"] is True
        assert "status" in result
        assert "timestamp" in result
        assert service.is_encryption_enabled() is True

    def test_disable_encryption(self, service):
        """Test disabling encryption."""
        service.enable_encryption()

        result = service.disable_encryption()

        assert result["encryption_enabled"] is False
        assert service.is_encryption_enabled() is False

    def test_is_encryption_enabled_default(self, service):
        """Test encryption is disabled by default."""
        assert service.is_encryption_enabled() is False

    def test_encryption_toggle(self, service):
        """Test toggling encryption on and off."""
        service.enable_encryption()
        assert service.is_encryption_enabled() is True

        service.disable_encryption()
        assert service.is_encryption_enabled() is False

        service.enable_encryption()
        assert service.is_encryption_enabled() is True


class TestAuditLog:
    """Test audit logging methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return SecurityComplianceService(AsyncMock())

    def test_log_audit_event(self, service):
        """Test logging an audit event."""
        result = service.log_audit_event(
            event_type="access",
            user_id="user123",
            resource="item-456",
            action="read",
        )

        assert result["logged"] is True
        assert result["event_id"] == 1
        assert "status" in result

    def test_log_audit_event_with_details(self, service):
        """Test logging event with details."""
        details = {"ip": "192.168.1.1", "method": "GET"}

        service.log_audit_event(
            event_type="access",
            user_id="user123",
            resource="item-456",
            action="read",
            details=details,
        )

        log = service.get_audit_log()
        assert log[0]["details"] == details

    def test_get_audit_log_all(self, service):
        """Test getting all audit log entries."""
        service.log_audit_event("event1", "user1", "res1", "action1")
        service.log_audit_event("event2", "user2", "res2", "action2")

        log = service.get_audit_log()

        assert len(log) == 2

    def test_get_audit_log_filtered_by_user(self, service):
        """Test getting audit log filtered by user."""
        service.log_audit_event("event1", "user1", "res1", "action1")
        service.log_audit_event("event2", "user2", "res2", "action2")
        service.log_audit_event("event3", "user1", "res3", "action3")

        log = service.get_audit_log(user_id="user1")

        assert len(log) == 2
        assert all(e["user_id"] == "user1" for e in log)

    def test_get_audit_log_filtered_by_event_type(self, service):
        """Test getting audit log filtered by event type."""
        service.log_audit_event("access", "user1", "res1", "read")
        service.log_audit_event("modify", "user2", "res2", "write")
        service.log_audit_event("access", "user3", "res3", "read")

        log = service.get_audit_log(event_type="access")

        assert len(log) == 2
        assert all(e["event_type"] == "access" for e in log)

    def test_get_audit_log_filtered_by_both(self, service):
        """Test getting audit log filtered by user and event type."""
        service.log_audit_event("access", "user1", "res1", "read")
        service.log_audit_event("modify", "user1", "res2", "write")
        service.log_audit_event("access", "user2", "res3", "read")

        log = service.get_audit_log(user_id="user1", event_type="access")

        assert len(log) == 1
        assert log[0]["user_id"] == "user1"
        assert log[0]["event_type"] == "access"

    def test_get_audit_stats(self, service):
        """Test getting audit statistics."""
        service.log_audit_event("access", "user1", "res1", "read")
        service.log_audit_event("access", "user2", "res2", "read")
        service.log_audit_event("modify", "user1", "res3", "write")

        stats = service.get_audit_stats()

        assert stats["total_events"] == 3
        assert stats["unique_users"] == 2
        assert stats["event_types"]["access"] == 2
        assert stats["event_types"]["modify"] == 1

    def test_get_audit_stats_empty(self, service):
        """Test getting stats with empty log."""
        stats = service.get_audit_stats()

        assert stats["total_events"] == 0
        assert stats["unique_users"] == 0
        assert stats["event_types"] == {}

    def test_clear_audit_log(self, service):
        """Test clearing audit log."""
        service.log_audit_event("event1", "user1", "res1", "action1")
        service.log_audit_event("event2", "user2", "res2", "action2")

        result = service.clear_audit_log()

        assert result["cleared_count"] == 2
        assert len(service.get_audit_log()) == 0

    def test_clear_empty_audit_log(self, service):
        """Test clearing when log is empty."""
        result = service.clear_audit_log()

        assert result["cleared_count"] == 0


class TestHashSensitiveData:
    """Test hash_sensitive_data method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return SecurityComplianceService(AsyncMock())

    def test_hash_data(self, service):
        """Test hashing sensitive data."""
        data = "sensitive_password"

        hashed = service.hash_sensitive_data(data)

        # Verify it's a valid SHA256 hash
        assert len(hashed) == 64
        assert hashed == hashlib.sha256(data.encode()).hexdigest()

    def test_hash_is_consistent(self, service):
        """Test same data produces same hash."""
        data = "test_data"

        hash1 = service.hash_sensitive_data(data)
        hash2 = service.hash_sensitive_data(data)

        assert hash1 == hash2

    def test_hash_different_data(self, service):
        """Test different data produces different hashes."""
        hash1 = service.hash_sensitive_data("data1")
        hash2 = service.hash_sensitive_data("data2")

        assert hash1 != hash2


class TestAccessControl:
    """Test validate_access_control method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return SecurityComplianceService(AsyncMock())

    def test_validate_access_viewer_can_read(self, service):
        """Test viewer can read."""
        result = service.validate_access_control("user1", "item-123", "read")

        assert result["allowed"] is True
        assert result["role"] == "viewer"
        assert result["action"] == "read"

    def test_validate_access_viewer_cannot_write(self, service):
        """Test viewer cannot write."""
        result = service.validate_access_control("user1", "item-123", "write")

        # Default role is viewer which can only read
        assert result["allowed"] is False
        assert result["role"] == "viewer"

    def test_validate_access_contains_metadata(self, service):
        """Test validation result contains all metadata."""
        result = service.validate_access_control("user1", "item-123", "read")

        assert "user_id" in result
        assert "resource" in result
        assert "action" in result
        assert "allowed" in result
        assert "role" in result


class TestComplianceReport:
    """Test generate_compliance_report method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return SecurityComplianceService(AsyncMock())

    def test_generate_basic_report(self, service):
        """Test generating basic compliance report."""
        report = service.generate_compliance_report()

        assert "generated_at" in report
        assert "encryption_enabled" in report
        assert "audit_stats" in report
        assert "compliance_status" in report
        assert "recommendations" in report

    def test_report_non_compliant_without_encryption(self, service):
        """Test report shows non-compliant without encryption."""
        report = service.generate_compliance_report()

        assert report["compliance_status"] == "NON_COMPLIANT"
        assert report["encryption_enabled"] is False

    def test_report_compliant_with_encryption(self, service):
        """Test report shows compliant with encryption."""
        service.enable_encryption()

        report = service.generate_compliance_report()

        assert report["compliance_status"] == "COMPLIANT"
        assert report["encryption_enabled"] is True

    def test_report_includes_audit_stats(self, service):
        """Test report includes audit statistics."""
        service.log_audit_event("access", "user1", "res1", "read")
        service.log_audit_event("modify", "user2", "res2", "write")

        report = service.generate_compliance_report()

        assert report["audit_stats"]["total_events"] == 2
        assert report["audit_stats"]["unique_users"] == 2

    def test_report_includes_recommendations(self, service):
        """Test report includes recommendations."""
        report = service.generate_compliance_report()

        assert len(report["recommendations"]) > 0
        assert any("encryption" in r.lower() for r in report["recommendations"])


class TestIntegration:
    """Integration tests combining multiple features."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return SecurityComplianceService(AsyncMock())

    def test_complete_security_workflow(self, service):
        """Test complete security workflow."""
        # Enable encryption
        service.enable_encryption()

        # Log security events
        service.log_audit_event("login", "user1", "system", "authenticate")
        service.log_audit_event("access", "user1", "item-123", "read")
        service.log_audit_event("modify", "user1", "item-123", "write")

        # Generate report
        report = service.generate_compliance_report()

        assert report["compliance_status"] == "COMPLIANT"
        assert report["audit_stats"]["total_events"] == 3

        # Clear audit log
        result = service.clear_audit_log()
        assert result["cleared_count"] == 3
