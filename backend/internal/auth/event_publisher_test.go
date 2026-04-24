package auth

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// MockJetStreamPublisher is a simple mock for testing
type MockJetStreamPublisher struct {
	PublishedMessages [][]byte
	Subjects          []string
	ShouldFail        bool
}

func (m *MockJetStreamPublisher) PublishAsync(subject string, data []byte, _ ...interface{}) (interface{}, error) {
	if m.ShouldFail {
		return nil, errors.New("connection closed")
	}
	m.Subjects = append(m.Subjects, subject)
	m.PublishedMessages = append(m.PublishedMessages, data)
	return nil, nil
}

func TestPublishOAuthStarted(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishOAuthStarted(context.Background(), "client123", "https://example.com/callback")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.started", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_started", event.EventType)
	assert.Equal(t, "client123", event.ClientID)
	assert.Equal(t, "https://example.com/callback", event.Metadata["redirect_uri"])
	assert.NotEmpty(t, event.EventID)
	assert.NotZero(t, event.Timestamp)
}

func TestPublishCallbackReceived(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishCallbackReceived(context.Background(), "auth_code_12345678", "state_abcdef123456")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.callback_received", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_callback_received", event.EventType)

	// Verify tokens are masked
	maskedCode, ok := event.Metadata["code"].(string)
	assert.True(t, ok)
	assert.Contains(t, maskedCode, "token_")
	assert.NotContains(t, maskedCode, "auth_code_")

	maskedState, ok := event.Metadata["state"].(string)
	assert.True(t, ok)
	assert.Contains(t, maskedState, "token_")
	assert.NotContains(t, maskedState, "state_abcd")
}

func TestPublishTokenExchanged(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	scopes := []string{"user:read", "user:write", "repo:read"}
	err := publisher.PublishTokenExchanged(context.Background(), "client456", scopes)
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.token_exchanged", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_token_exchanged", event.EventType)
	assert.Equal(t, "client456", event.ClientID)

	scopesList, ok := event.Metadata["scopes"].([]interface{})
	assert.True(t, ok)
	assert.Len(t, scopesList, 3)
}

func TestPublishUserCreated(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishUserCreated(context.Background(), "user_uuid_789", "user@example.com")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.user_created", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_user_created", event.EventType)
	assert.Equal(t, "user_uuid_789", event.UserID)
	assert.Equal(t, "user@example.com", event.Metadata["email"])
}

func TestPublishSessionCreated(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishSessionCreated(context.Background(), "session_id_456", "user_uuid_789")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.session_created", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_session_created", event.EventType)
	assert.Equal(t, "user_uuid_789", event.UserID)
	assert.Equal(t, "session_id_456", event.Metadata["session_id"])
}

func TestPublishTokenRefreshed(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishTokenRefreshed(context.Background(), "user_uuid_789")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.token_refreshed", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_token_refreshed", event.EventType)
	assert.Equal(t, "user_uuid_789", event.UserID)
}

func TestPublishTokenExpired(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishTokenExpired(context.Background(), "user_uuid_789")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.token_expired", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_token_expired", event.EventType)
	assert.Equal(t, "user_uuid_789", event.UserID)
}

func TestPublishAuthenticationFailed(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishAuthenticationFailed(context.Background(), "client123", "invalid_client_id")
	require.NoError(t, err)

	assert.Len(t, mock.PublishedMessages, 1)
	assert.Equal(t, "oauth.authentication_failed", mock.Subjects[0])

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	assert.Equal(t, "oauth_authentication_failed", event.EventType)
	assert.Equal(t, "client123", event.ClientID)
	assert.Equal(t, "invalid_client_id", event.Metadata["reason"])
}

func TestEventStructure(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	err := publisher.PublishOAuthStarted(context.Background(), "test_client", "https://test.com")
	require.NoError(t, err)

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	// Verify all required fields are present
	assert.NotEmpty(t, event.EventID)
	assert.NotEmpty(t, event.EventType)
	assert.False(t, event.Timestamp.IsZero())
	assert.Equal(t, "oauth_started", event.EventType)
}

func TestMaskToken(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"", "****"},
		{"short", "****"},
		{"12345678", "token_12345678"},
		{"abcdefghijklmnop", "token_ijklmnop"},
		{"verylongtoken123456789abcdef", "token_89abcdef"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			result := maskToken(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestMultipleEvents(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	// Publish multiple events
	err := publisher.PublishOAuthStarted(context.Background(), "client1", "https://example.com/1")
	require.NoError(t, err)

	err = publisher.PublishTokenExchanged(context.Background(), "client1", []string{"read", "write"})
	require.NoError(t, err)

	err = publisher.PublishUserCreated(context.Background(), "user_123", "user@example.com")
	require.NoError(t, err)

	// Verify all events were published
	assert.Len(t, mock.PublishedMessages, 3)
	assert.Equal(t, "oauth.started", mock.Subjects[0])
	assert.Equal(t, "oauth.token_exchanged", mock.Subjects[1])
	assert.Equal(t, "oauth.user_created", mock.Subjects[2])
}

func TestEventTimestamped(t *testing.T) {
	mock := &MockJetStreamPublisher{}
	publisher := NewEventPublisher(mock)

	before := time.Now()
	err := publisher.PublishOAuthStarted(context.Background(), "client", "https://example.com")
	require.NoError(t, err)
	after := time.Now()

	var event OAuthEvent
	err = json.Unmarshal(mock.PublishedMessages[0], &event)
	require.NoError(t, err)

	// Timestamp should be between before and after
	assert.True(t, event.Timestamp.After(before.Add(-time.Second)))
	assert.True(t, event.Timestamp.Before(after.Add(time.Second)))
}
