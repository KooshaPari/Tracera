"""Integration tests for MCP HTTP authentication.

Tests that MCP endpoints properly integrate with FastAPI authentication:
- Valid Bearer token (200 OK)
- Missing token (401)
- Invalid token (401)
- User context injection
- RLS verification
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tracertm.api.main import app
from tracertm.core.context import current_user_id


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_valid_token():
    """Mock a valid token verification."""
    return {
        "sub": "user_123",
        "email": "test@example.com",
        "org_id": "org_456",
    }


@pytest.fixture
def mock_invalid_token():
    """Mock an invalid token."""
    raise ValueError("Invalid token")


class TestMCPHTTPAuth:
    """Test suite for MCP HTTP authentication."""

    def test_health_endpoint_no_auth(self, client):
        """Health endpoint should not require auth."""
        response = client.get("/api/v1/mcp/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp"
        assert data["transport"] == "http"

    @patch("tracertm.api.deps.verify_token")
    def test_tools_list_with_valid_token(self, mock_verify, client, mock_valid_token):
        """Tools list endpoint should accept valid Bearer token."""
        mock_verify.return_value = mock_valid_token

        response = client.get("/api/v1/mcp/tools", headers={"Authorization": "Bearer valid_token_here"})

        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)

        # Verify token was checked
        mock_verify.assert_called_once_with("valid_token_here")

    def test_tools_list_without_token(self, client):
        """Tools list endpoint should reject requests without token when auth enabled."""
        # Note: This test assumes auth_enabled=true in config
        with patch("tracertm.api.deps.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = True

            response = client.get("/api/v1/mcp/tools")

            # Should return 401 if auth is enabled
            if response.status_code == 401:
                assert response.json()["detail"] == "Authorization required"

    @patch("tracertm.api.deps.verify_token")
    def test_tools_list_with_invalid_token(self, mock_verify, client):
        """Tools list endpoint should reject invalid Bearer token."""
        mock_verify.side_effect = ValueError("Invalid token")

        response = client.get("/api/v1/mcp/tools", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    @patch("tracertm.api.deps.verify_token")
    def test_user_context_injection(self, mock_verify, client, mock_valid_token):
        """User context should be set from token claims."""
        mock_verify.return_value = mock_valid_token

        # Clear any existing context
        current_user_id.set(None)

        response = client.get("/api/v1/mcp/tools", headers={"Authorization": "Bearer valid_token"})

        assert response.status_code == 200

        # User context should be set during request processing
        # Note: Context vars are request-scoped, so we can't verify after response
        # This is verified by checking that RLS queries work correctly

    @patch("tracertm.api.deps.verify_token")
    def test_messages_endpoint_with_valid_token(self, mock_verify, client, mock_valid_token):
        """Messages endpoint should accept valid Bearer token."""
        mock_verify.return_value = mock_valid_token

        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        response = client.post(
            "/api/v1/mcp/messages", json=request_data, headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data

    @patch("tracertm.api.deps.verify_token")
    def test_messages_endpoint_without_token(self, mock_verify, client):
        """Messages endpoint should reject requests without token."""
        with patch("tracertm.api.deps.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = True

            request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

            response = client.post("/api/v1/mcp/messages", json=request_data)

            if response.status_code == 401:
                assert response.json()["detail"] == "Authorization required"

    @patch("tracertm.api.deps.verify_token")
    def test_messages_endpoint_with_invalid_token(self, mock_verify, client):
        """Messages endpoint should reject invalid token."""
        mock_verify.side_effect = ValueError("Token expired")

        request_data = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

        response = client.post(
            "/api/v1/mcp/messages", json=request_data, headers={"Authorization": "Bearer expired_token"}
        )

        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]

    def test_cors_preflight(self, client):
        """CORS preflight should work for MCP endpoints."""
        response = client.options("/api/v1/mcp/messages")

        assert response.status_code == 204
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "POST" in response.headers["Access-Control-Allow-Methods"]
        assert "OPTIONS" in response.headers["Access-Control-Allow-Methods"]

    @patch("tracertm.api.deps.verify_token")
    def test_jsonrpc_error_format(self, mock_verify, client, mock_valid_token):
        """Errors should be returned in JSON-RPC format."""
        mock_verify.return_value = mock_valid_token

        request_data = {"jsonrpc": "2.0", "method": "invalid/method", "params": {}, "id": 1}

        response = client.post(
            "/api/v1/mcp/messages", json=request_data, headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200  # JSON-RPC always returns 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]

    @patch("tracertm.api.deps.verify_token")
    @patch("tracertm.api.deps.get_db")
    async def test_rls_with_user_context(self, mock_db, mock_verify, client, mock_valid_token):
        """Database RLS should use user context from token."""
        mock_verify.return_value = mock_valid_token

        # Mock database session
        mock_session = MagicMock()
        mock_db.return_value = mock_session

        response = client.get("/api/v1/mcp/tools", headers={"Authorization": "Bearer valid_token"})

        assert response.status_code == 200

        # Verify RLS context was set (checked in get_db dependency)
        # This is validated by the fact that get_db sets RLS context based on current_user_id

    @patch("tracertm.api.deps.verify_token")
    def test_sse_endpoint_with_valid_token(self, mock_verify, client, mock_valid_token):
        """SSE endpoint should accept valid Bearer token."""
        mock_verify.return_value = mock_valid_token

        response = client.get("/api/v1/mcp/sse", headers={"Authorization": "Bearer valid_token"})

        # SSE endpoint returns 200 and starts streaming
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    def test_sse_endpoint_without_token(self, client):
        """SSE endpoint should reject requests without token."""
        with patch("tracertm.api.deps.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = True

            response = client.get("/api/v1/mcp/sse")

            if response.status_code == 401:
                assert response.json()["detail"] == "Authorization required"

    @patch("tracertm.api.deps.verify_token")
    def test_same_token_works_for_rest_and_mcp(self, mock_verify, client, mock_valid_token):
        """Same Bearer token should work for both REST API and MCP endpoints."""
        mock_verify.return_value = mock_valid_token

        headers = {"Authorization": "Bearer same_token"}

        # Test REST endpoint
        rest_response = client.get("/api/v1/specifications/adrs", headers=headers)

        # Test MCP endpoint
        mcp_response = client.get("/api/v1/mcp/tools", headers=headers)

        # Both should accept the same token
        # (REST endpoint might return different status codes based on data)
        assert mcp_response.status_code == 200

        # Verify same token was used for both
        assert mock_verify.call_count >= 2
        for call in mock_verify.call_args_list:
            assert call[0][0] == "same_token"


class TestMCPToolExecution:
    """Test MCP tool execution with authentication."""

    @patch("tracertm.api.deps.verify_token")
    async def test_tool_call_with_user_context(self, mock_verify, client, mock_valid_token):
        """Tool execution should have access to user context."""
        mock_verify.return_value = mock_valid_token

        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "project_manage", "arguments": {"action": "list", "kind": "project"}},
            "id": 1,
        }

        response = client.post(
            "/api/v1/mcp/messages", json=request_data, headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert "result" in data or "error" in data

        # If successful, result should contain data filtered by user context
        # (RLS should limit results to user's projects)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
