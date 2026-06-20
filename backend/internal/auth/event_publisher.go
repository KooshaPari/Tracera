package auth

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/google/uuid"
)

// JetStreamPublisher is a minimal interface for NATS JetStream publishing
type JetStreamPublisher interface {
	PublishAsync(subject string, data []byte, opts ...interface{}) (interface{}, error)
}

// EventPublisher publishes OAuth events to NATS JetStream
type EventPublisher struct {
	js JetStreamPublisher
}

// OAuthEvent represents a published OAuth event
type OAuthEvent struct {
	EventID   string                 `json:"event_id"`
	EventType string                 `json:"event_type"`
	Timestamp time.Time              `json:"timestamp"`
	UserID    string                 `json:"user_id,omitempty"`
	ClientID  string                 `json:"client_id,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// NewEventPublisher creates a new OAuth event publisher
func NewEventPublisher(js JetStreamPublisher) *EventPublisher {
	return &EventPublisher{js: js}
}

// PublishOAuthStarted publishes an oauth_started event
// Emitted when a user initiates OAuth authentication flow
func (ep *EventPublisher) PublishOAuthStarted(ctx context.Context, clientID, redirectURI string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_started",
		Timestamp: time.Now(),
		ClientID:  clientID,
		Metadata: map[string]interface{}{
			"redirect_uri": redirectURI,
		},
	}
	return ep.publish(ctx, "oauth.started", event)
}

// PublishOAuthLoginStarted publishes when OAuth login is initiated (alias for PublishOAuthStarted)
func (ep *EventPublisher) PublishOAuthLoginStarted(ctx context.Context, provider, stateToken string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_login_started",
		Timestamp: time.Now(),
		ClientID:  provider,
		Metadata: map[string]interface{}{
			"state_token": maskToken(stateToken),
		},
	}
	return ep.publish(ctx, "oauth.login_started", event)
}

// PublishCallbackReceived publishes an oauth_callback_received event
// Emitted when OAuth provider redirects back with authorization code
// Token and code are masked for security
func (ep *EventPublisher) PublishCallbackReceived(ctx context.Context, code, state string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_callback_received",
		Timestamp: time.Now(),
		Metadata: map[string]interface{}{
			"code":  maskToken(code),
			"state": maskToken(state),
		},
	}
	return ep.publish(ctx, "oauth.callback_received", event)
}

// PublishOAuthCallbackReceived publishes OAuth callback received event with provider and auth code
func (ep *EventPublisher) PublishOAuthCallbackReceived(ctx context.Context, provider, authCode string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_callback_received",
		Timestamp: time.Now(),
		ClientID:  provider,
		Metadata: map[string]interface{}{
			"auth_code": maskToken(authCode),
		},
	}
	return ep.publish(ctx, "oauth.callback_received", event)
}

// PublishTokenExchanged publishes an oauth_token_exchanged event
// Emitted when authorization code is exchanged for access token
// Token is masked for security
func (ep *EventPublisher) PublishTokenExchanged(ctx context.Context, clientID string, scopes []string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_token_exchanged",
		Timestamp: time.Now(),
		ClientID:  clientID,
		Metadata: map[string]interface{}{
			"scopes": scopes,
		},
	}
	return ep.publish(ctx, "oauth.token_exchanged", event)
}

// PublishOAuthTokenExchanged publishes token exchanged event with provider and user
func (ep *EventPublisher) PublishOAuthTokenExchanged(ctx context.Context, provider, userID string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_token_exchanged",
		Timestamp: time.Now(),
		UserID:    userID,
		ClientID:  provider,
	}
	return ep.publish(ctx, "oauth.token_exchanged", event)
}

// PublishUserCreated publishes an oauth_user_created event
// Emitted when a new user account is created via OAuth
func (ep *EventPublisher) PublishUserCreated(ctx context.Context, userID, email string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_user_created",
		Timestamp: time.Now(),
		UserID:    userID,
		Metadata: map[string]interface{}{
			"email": email,
		},
	}
	return ep.publish(ctx, "oauth.user_created", event)
}

// PublishSessionCreated publishes an oauth_session_created event
// Emitted when a new session is established after OAuth
func (ep *EventPublisher) PublishSessionCreated(ctx context.Context, sessionID, userID string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_session_created",
		Timestamp: time.Now(),
		UserID:    userID,
		Metadata: map[string]interface{}{
			"session_id": sessionID,
		},
	}
	return ep.publish(ctx, "oauth.session_created", event)
}

// PublishOAuthSessionCreated publishes session created event with user and session IDs
func (ep *EventPublisher) PublishOAuthSessionCreated(ctx context.Context, userID, sessionID string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_session_created",
		Timestamp: time.Now(),
		UserID:    userID,
		Metadata: map[string]interface{}{
			"session_id": sessionID,
		},
	}
	return ep.publish(ctx, "oauth.session_created", event)
}

// PublishTokenRefreshed publishes an oauth_token_refreshed event
// Emitted when an access token is refreshed
// Token is masked for security
func (ep *EventPublisher) PublishTokenRefreshed(ctx context.Context, userID string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_token_refreshed",
		Timestamp: time.Now(),
		UserID:    userID,
	}
	return ep.publish(ctx, "oauth.token_refreshed", event)
}

// PublishTokenExpired publishes an oauth_token_expired event
// Emitted when a token has expired
func (ep *EventPublisher) PublishTokenExpired(ctx context.Context, userID string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_token_expired",
		Timestamp: time.Now(),
		UserID:    userID,
	}
	return ep.publish(ctx, "oauth.token_expired", event)
}

// PublishAuthenticationFailed publishes an oauth_authentication_failed event
// Emitted when OAuth authentication fails
func (ep *EventPublisher) PublishAuthenticationFailed(ctx context.Context, clientID, reason string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_authentication_failed",
		Timestamp: time.Now(),
		ClientID:  clientID,
		Metadata: map[string]interface{}{
			"reason": reason,
		},
	}
	return ep.publish(ctx, "oauth.authentication_failed", event)
}

// PublishOAuthError publishes an OAuth error event
func (ep *EventPublisher) PublishOAuthError(ctx context.Context, userID, provider, reason string) error {
	event := &OAuthEvent{
		EventID:   uuid.New().String(),
		EventType: "oauth_error",
		Timestamp: time.Now(),
		UserID:    userID,
		ClientID:  provider,
		Metadata: map[string]interface{}{
			"reason": reason,
		},
	}
	return ep.publish(ctx, "oauth.error", event)
}

// publish publishes an event to NATS JetStream
func (ep *EventPublisher) publish(ctx context.Context, subject string, event *OAuthEvent) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	_, err = ep.js.PublishAsync(subject, data)
	if err != nil {
		return fmt.Errorf("failed to publish event to %s: %w", subject, err)
	}

	return nil
}

const maskedTokenVisibleChars = 8

// maskToken masks sensitive tokens by showing only last characters
// Example: "abc123def456ghi789" -> "token_i789"
func maskToken(token string) string {
	if len(token) < maskedTokenVisibleChars {
		return "****"
	}
	return "token_" + token[len(token)-maskedTokenVisibleChars:]
}
