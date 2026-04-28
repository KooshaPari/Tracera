package websocket

import (
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"golang.org/x/net/websocket"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

// TestTokenRefresh_ValidTokenValidation tests token validation for refresh scenario
func TestTokenRefresh_ValidTokenValidation(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	// Create a mock auth provider
	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:        "test-user-id",
			Email:     "test@example.com",
			ProjectID: projectID,
		},
		shouldFail: false,
	}

	// Test token validation directly without full WebSocket flow
	server := httptest.NewServer(websocket.Handler(func(wsConn *websocket.Conn) {
		auditLogger := NewAuditLogger()
		client := NewClientWithAuth(wsConn, hub, projectID, "", mockAuth, auditLogger)

		// Test validation of first token
		result1 := client.validateToken("initial-token")
		assert.True(t, result1)
		assert.Equal(t, 1, mockAuth.callCount)

		// Test validation of refreshed token
		result2 := client.validateToken("refreshed-token")
		assert.True(t, result2)
		assert.Equal(t, 2, mockAuth.callCount)

		// Send response
		require.NoError(t, websocket.JSON.Send(wsConn, map[string]bool{"success": true}))
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Read the response
	var response map[string]bool
	require.NoError(t, ws.SetReadDeadline(time.Now().Add(1*time.Second)))
	err = websocket.JSON.Receive(ws, &response)
	require.NoError(t, err)
	assert.True(t, response["success"])
}

// TestTokenRefresh_ExpiredToken tests handling of expired token during refresh
func TestTokenRefresh_ExpiredToken(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	// Create mock auth that succeeds first, then fails
	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:        "test-user-id",
			Email:     "test@example.com",
			ProjectID: projectID,
		},
		shouldFail: false,
	}

	server := httptest.NewServer(websocket.Handler(func(wsConn *websocket.Conn) {
		auditLogger := NewAuditLogger()

		// Use a failing auth provider for this test
		failingAuth := &MockAuthProvider{
			shouldFail:   true,
			failureError: "token expired",
			returnedUser: mockAuth.returnedUser,
		}

		client := NewClientWithAuth(wsConn, hub, projectID, "", failingAuth, auditLogger)

		go client.WritePump()
		client.ReadPump()
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Send expired token
	expiredMsg := AuthMessage{
		Type:  "auth",
		Token: "expired-token",
	}
	err = websocket.JSON.Send(ws, expiredMsg)
	require.NoError(t, err)

	// Should receive auth failure
	var failResp AuthResponse
	err = websocket.JSON.Receive(ws, &failResp)
	require.NoError(t, err)
	assert.Equal(t, "auth_failed", failResp.Type)

	// Connection should be closed after failed auth
	time.Sleep(50 * time.Millisecond)
	_, err = ws.Read(make([]byte, 1024))
	assert.Error(t, err)
}

// TestTokenRefresh_AuditLogging tests that token validation is properly audited
func TestTokenRefresh_AuditLogging(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:        "test-user-id",
			Email:     "test@example.com",
			ProjectID: projectID,
		},
	}

	var auditLogger *AuditLogger

	server := httptest.NewServer(websocket.Handler(func(wsConn *websocket.Conn) {
		auditLogger = NewAuditLogger()
		client := NewClientWithAuth(wsConn, hub, projectID, "", mockAuth, auditLogger)

		// Test validation logging
		client.validateToken("test-token-1")
		client.validateToken("test-token-2")

		// Send response
		require.NoError(t, websocket.JSON.Send(wsConn, map[string]bool{"success": true}))
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Read the response
	var response map[string]bool
	require.NoError(t, ws.SetReadDeadline(time.Now().Add(1*time.Second)))
	err = websocket.JSON.Receive(ws, &response)
	require.NoError(t, err)

	// Give audit logger time to process
	time.Sleep(50 * time.Millisecond)

	// Verify audit logs contain both auth events
	events := auditLogger.GetEvents()
	assert.GreaterOrEqual(t, len(events), 2, "Expected at least 2 audit events, got %d", len(events))

	// Check that events are success events
	successCount := 0
	for _, event := range events {
		if event.EventType == "AUTH_VALIDATION_SUCCESS" {
			successCount++
		}
	}
	assert.Equal(t, 2, successCount)
}

// Note: MockAuthProvider is defined in auth_test.go - reused here
