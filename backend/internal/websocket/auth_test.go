package websocket

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"golang.org/x/net/websocket"

	"github.com/kooshapari/tracertm-backend/internal/auth"
)

const authTestDelay = 100 * time.Millisecond

// MockAuthProvider is a mock implementation of auth.Provider for testing
type MockAuthProvider struct {
	shouldFail         bool
	failureError       string
	returnedUser       *auth.User
	callCount          int
	lastValidatedToken string
}

// ValidateToken validates a token (mock implementation)
func (m *MockAuthProvider) ValidateToken(_ context.Context, token string) (*auth.User, error) {
	m.callCount++
	m.lastValidatedToken = token

	if m.shouldFail {
		return nil, fmt.Errorf("%s", m.failureError)
	}

	return m.returnedUser, nil
}

// GetUser retrieves a user by ID (mock implementation)
func (m *MockAuthProvider) GetUser(_ context.Context, _ string) (*auth.User, error) {
	return m.returnedUser, nil
}

// CreateUser creates a new user (mock implementation)
func (m *MockAuthProvider) CreateUser(_ context.Context, _, _, _ string) (*auth.User, error) {
	return nil, nil
}

// UpdateUser updates a user (mock implementation)
func (m *MockAuthProvider) UpdateUser(_ context.Context, _ string, _ map[string]interface{}) (*auth.User, error) {
	return m.returnedUser, nil
}

// DeleteUser deletes a user (mock implementation)
func (m *MockAuthProvider) DeleteUser(_ context.Context, _ string) error {
	return nil
}

// ListUsers lists users (mock implementation)
func (m *MockAuthProvider) ListUsers(_ context.Context, _, _ int) ([]*auth.User, error) {
	return []*auth.User{m.returnedUser}, nil
}

// Close closes the provider (mock implementation)
func (m *MockAuthProvider) Close() error {
	return nil
}

// TestValidateToken_ValidToken tests validation of a valid token
func TestValidateToken_ValidToken(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()
	projectID := uuid.New().String()

	// Create mock auth provider that returns a valid user
	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:        "test-user-id",
			Email:     "test@example.com",
			Name:      "Test User",
			ProjectID: projectID,
		},
	}

	client := NewClientWithAuth(ws, hub, projectID, "", mockAuth, NewAuditLogger())

	// Test token validation
	result := client.validateToken("valid-token")

	assert.True(t, result)
	assert.Equal(t, "test-user-id", client.userID)
	assert.NotNil(t, client.user)
	assert.Equal(t, "test@example.com", client.user.Email)
	assert.Equal(t, 1, mockAuth.callCount)
	assert.Equal(t, "valid-token", mockAuth.lastValidatedToken)
}

// TestValidateToken_InvalidToken tests validation of an invalid token
func TestValidateToken_InvalidToken(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()

	// Create mock auth provider that fails validation
	mockAuth := &MockAuthProvider{
		shouldFail:   true,
		failureError: "token expired",
	}

	client := NewClientWithAuth(ws, hub, uuid.New().String(), "", mockAuth, NewAuditLogger())

	// Test token validation
	result := client.validateToken("invalid-token")

	assert.False(t, result)
	assert.Empty(t, client.userID)
	assert.Nil(t, client.user)
	assert.Equal(t, 1, mockAuth.callCount)
}

// TestValidateToken_EmptyToken tests validation with empty token
func TestValidateToken_EmptyToken(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()

	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:    "test-user-id",
			Email: "test@example.com",
		},
	}

	client := NewClientWithAuth(ws, hub, uuid.New().String(), "", mockAuth, NewAuditLogger())

	// Test with empty token
	result := client.validateToken("")

	assert.False(t, result)
	assert.Equal(t, 0, mockAuth.callCount) // Auth provider should not be called
}

// TestValidateToken_NoAuthProvider tests validation without auth provider
func TestValidateToken_NoAuthProvider(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()

	// Create client without auth provider
	client := NewClient(ws, hub, uuid.New().String(), "")
	client.auditLogger = NewAuditLogger()

	// Test validation without auth provider
	result := client.validateToken("some-token")

	assert.False(t, result)
}

// TestAuditLogging_SuccessfulAuth tests audit logging for successful authentication
func TestAuditLogging_SuccessfulAuth(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()
	projectID := uuid.New().String()

	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:        "user-123",
			Email:     "user@example.com",
			ProjectID: projectID,
		},
	}

	auditLogger := NewAuditLogger()
	client := NewClientWithAuth(ws, hub, projectID, "", mockAuth, auditLogger)

	// Validate token
	result := client.validateToken("valid-token")

	assert.True(t, result)

	// Check audit logs
	events := auditLogger.GetEvents()
	assert.NotEmpty(t, events)

	successEvent := events[len(events)-1]
	assert.Equal(t, "AUTH_VALIDATION_SUCCESS", successEvent.EventType)
	assert.Equal(t, "token_valid", successEvent.Reason)
	assert.Equal(t, "user-123", successEvent.UserID)
}

// TestAuditLogging_FailedAuth tests audit logging for failed authentication
func TestAuditLogging_FailedAuth(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()

	mockAuth := &MockAuthProvider{
		shouldFail:   true,
		failureError: "invalid signature",
	}

	auditLogger := NewAuditLogger()
	client := NewClientWithAuth(ws, hub, uuid.New().String(), "", mockAuth, auditLogger)

	// Validate token
	result := client.validateToken("invalid-token")

	assert.False(t, result)

	// Check audit logs
	events := auditLogger.GetEvents()
	assert.NotEmpty(t, events)

	failureEvent := events[len(events)-1]
	assert.Equal(t, "AUTH_VALIDATION_FAILED", failureEvent.EventType)
	assert.Equal(t, "invalid_token", failureEvent.Reason)
}

// TestWebSocketAuthFlow tests the complete WebSocket authentication flow
func TestWebSocketAuthFlow(t *testing.T) {
	hub := NewHub()
	projectID := uuid.New().String()

	// Create a mock auth provider
	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:        "auth-user-id",
			Email:     "auth@example.com",
			ProjectID: projectID,
		},
	}

	// Create test server with WebSocket handler
	server := httptest.NewServer(websocket.Handler(func(wsConn *websocket.Conn) {
		auditLogger := NewAuditLogger()
		client := NewClientWithAuth(wsConn, hub, projectID, "", mockAuth, auditLogger)

		// Start write pump
		go client.WritePump()

		// Read authentication
		client.ReadPump()

		// Check if authenticated
		if !client.isAuth {
			return
		}

		// Register in hub
		client.RegisterInHub()
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Send authentication message
	authMsg := AuthMessage{
		Type:  "auth",
		Token: "test-valid-token",
	}

	err = websocket.JSON.Send(ws, authMsg)
	require.NoError(t, err)

	// Read authentication response
	var authResp AuthResponse
	err = websocket.JSON.Receive(ws, &authResp)
	require.NoError(t, err)

	assert.Equal(t, "auth_success", authResp.Type)
	assert.Equal(t, 1, mockAuth.callCount)
}

// TestWebSocketAuthFlow_InvalidToken tests authentication with invalid token
func TestWebSocketAuthFlow_InvalidToken(t *testing.T) {
	hub := NewHub()

	// Create a mock auth provider that fails
	mockAuth := &MockAuthProvider{
		shouldFail:   true,
		failureError: "jwt: invalid signature",
	}

	// Create test server with WebSocket handler
	server := httptest.NewServer(websocket.Handler(func(wsConn *websocket.Conn) {
		auditLogger := NewAuditLogger()
		client := NewClientWithAuth(wsConn, hub, uuid.New().String(), "", mockAuth, auditLogger)

		// Start write pump
		go client.WritePump()

		// Read authentication
		client.ReadPump()
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Send invalid authentication message
	authMsg := AuthMessage{
		Type:  "auth",
		Token: "invalid-token",
	}

	err = websocket.JSON.Send(ws, authMsg)
	require.NoError(t, err)

	// Read authentication response (should be failure)
	var authResp AuthResponse
	err = websocket.JSON.Receive(ws, &authResp)
	require.NoError(t, err)

	assert.Equal(t, "auth_failed", authResp.Type)
	assert.NotEmpty(t, authResp.Message)
}

// TestWebSocketAuthFlow_EmptyToken tests authentication with empty token
func TestWebSocketAuthFlow_EmptyToken(t *testing.T) {
	hub := NewHub()

	mockAuth := &MockAuthProvider{
		returnedUser: &auth.User{
			ID:    "user-id",
			Email: "user@example.com",
		},
	}

	// Create test server with WebSocket handler
	server := httptest.NewServer(websocket.Handler(func(wsConn *websocket.Conn) {
		auditLogger := NewAuditLogger()
		client := NewClientWithAuth(wsConn, hub, uuid.New().String(), "", mockAuth, auditLogger)

		// Start write pump
		go client.WritePump()

		// Read authentication
		client.ReadPump()
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	// Send authentication message with empty token
	authMsg := AuthMessage{
		Type:  "auth",
		Token: "",
	}

	err = websocket.JSON.Send(ws, authMsg)
	require.NoError(t, err)

	// Read authentication response (should be failure)
	var authResp AuthResponse
	err = websocket.JSON.Receive(ws, &authResp)
	require.NoError(t, err)

	assert.Equal(t, "auth_failed", authResp.Type)
	assert.Equal(t, 0, mockAuth.callCount) // Auth provider should not be called
}

// TestAuditEventStructure tests the audit event structure
func TestAuditEventStructure(t *testing.T) {
	event := &AuditEvent{
		Timestamp:  time.Now(),
		ClientID:   "client-123",
		EventType:  "AUTH_VALIDATION_FAILED",
		Reason:     "expired_token",
		Details:    "Token expired at 2025-01-29T12:00:00Z",
		ProjectID:  "proj-456",
		UserID:     "user-789",
		RemoteAddr: "127.0.0.1:54321",
		UserAgent:  "Mozilla/5.0",
	}

	assert.NotEmpty(t, event.Timestamp)
	assert.Equal(t, "client-123", event.ClientID)
	assert.Equal(t, "AUTH_VALIDATION_FAILED", event.EventType)
	assert.Equal(t, "expired_token", event.Reason)
	assert.Equal(t, "proj-456", event.ProjectID)
	assert.Equal(t, "user-789", event.UserID)
}

// TestClientWithAuth_StoresUserInfo tests that client stores user info after validation
func TestClientWithAuth_StoresUserInfo(t *testing.T) {
	server := httptest.NewServer(websocket.Handler(func(_ *websocket.Conn) {
		time.Sleep(authTestDelay)
	}))
	defer server.Close()

	wsURL := "ws" + server.URL[4:]
	ws, err := websocket.Dial(wsURL, "", server.URL)
	require.NoError(t, err)
	defer func() { require.NoError(t, ws.Close()) }()

	hub := NewHub()
	projectID := uuid.New().String()

	expectedUser := &auth.User{
		ID:        "user-123",
		Email:     "user@example.com",
		Name:      "Test User",
		ProjectID: projectID,
		Role:      "admin",
	}

	mockAuth := &MockAuthProvider{
		returnedUser: expectedUser,
	}

	client := NewClientWithAuth(ws, hub, projectID, "", mockAuth, NewAuditLogger())

	// Before validation
	assert.Nil(t, client.user)
	assert.Empty(t, client.userID)

	// Validate token
	result := client.validateToken("valid-token")

	// After validation
	assert.True(t, result)
	assert.NotNil(t, client.user)
	assert.Equal(t, expectedUser.ID, client.user.ID)
	assert.Equal(t, expectedUser.Email, client.user.Email)
	assert.Equal(t, expectedUser.Name, client.user.Name)
	assert.Equal(t, expectedUser.Role, client.user.Role)
	assert.Equal(t, "user-123", client.userID)
}

// TestWebSocketAuthResponse tests the authentication response structure
func TestWebSocketAuthResponse(t *testing.T) {
	successResp := AuthResponse{
		Type:    "auth_success",
		Message: "",
	}

	// Marshal to JSON
	data, err := json.Marshal(successResp)
	require.NoError(t, err)

	var unmarshalled AuthResponse
	err = json.Unmarshal(data, &unmarshalled)
	require.NoError(t, err)

	assert.Equal(t, "auth_success", unmarshalled.Type)

	// Test failure response
	failureResp := AuthResponse{
		Type:    "auth_failed",
		Message: "Invalid token",
	}

	data, err = json.Marshal(failureResp)
	require.NoError(t, err)

	err = json.Unmarshal(data, &unmarshalled)
	require.NoError(t, err)

	assert.Equal(t, "auth_failed", unmarshalled.Type)
	assert.Equal(t, "Invalid token", unmarshalled.Message)
}
