package websocket

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// TestNewAuditLogger tests audit logger creation
func TestNewAuditLogger(t *testing.T) {
	logger := NewAuditLogger()
	assert.NotNil(t, logger)
	assert.Empty(t, logger.GetEvents())
}

// TestAuditLogger_LogEvent tests logging a single event
func TestAuditLogger_LogEvent(t *testing.T) {
	logger := NewAuditLogger()

	event := &AuditEvent{
		Timestamp:  time.Now(),
		ClientID:   "client-123",
		EventType:  "AUTH_VALIDATION_SUCCESS",
		Reason:     "token_valid",
		Details:    "User authenticated successfully",
		ProjectID:  "proj-456",
		UserID:     "user-789",
		RemoteAddr: "192.168.1.1:12345",
		UserAgent:  "Mozilla/5.0",
	}

	logger.LogEvent(event)

	events := logger.GetEvents()
	assert.Len(t, events, 1)
	assert.Equal(t, event.ClientID, events[0].ClientID)
	assert.Equal(t, event.EventType, events[0].EventType)
}

// TestAuditLogger_MultipleEvents tests logging multiple events
func TestAuditLogger_MultipleEvents(t *testing.T) {
	logger := NewAuditLogger()

	for i := 0; i < 5; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-123",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	events := logger.GetEvents()
	assert.Len(t, events, 5)
}

// TestAuditLogger_GetEventsByType tests filtering by event type
func TestAuditLogger_GetEventsByType(t *testing.T) {
	logger := NewAuditLogger()

	// Add success events
	for i := 0; i < 3; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-1",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	// Add failure events
	for i := 0; i < 2; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-2",
			EventType: "AUTH_VALIDATION_FAILED",
		})
	}

	successEvents := logger.GetEventsByType("AUTH_VALIDATION_SUCCESS")
	assert.Len(t, successEvents, 3)
	for _, e := range successEvents {
		assert.Equal(t, "AUTH_VALIDATION_SUCCESS", e.EventType)
	}

	failureEvents := logger.GetEventsByType("AUTH_VALIDATION_FAILED")
	assert.Len(t, failureEvents, 2)
	for _, e := range failureEvents {
		assert.Equal(t, "AUTH_VALIDATION_FAILED", e.EventType)
	}
}

// TestAuditLogger_GetEventsByClientID tests filtering by client ID
func TestAuditLogger_GetEventsByClientID(t *testing.T) {
	logger := NewAuditLogger()

	// Add events for client-1
	for i := 0; i < 2; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-1",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	// Add events for client-2
	for i := 0; i < 3; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-2",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	client1Events := logger.GetEventsByClientID("client-1")
	assert.Len(t, client1Events, 2)
	for _, e := range client1Events {
		assert.Equal(t, "client-1", e.ClientID)
	}

	client2Events := logger.GetEventsByClientID("client-2")
	assert.Len(t, client2Events, 3)
	for _, e := range client2Events {
		assert.Equal(t, "client-2", e.ClientID)
	}
}

// TestAuditLogger_GetEventsByUserID tests filtering by user ID
func TestAuditLogger_GetEventsByUserID(t *testing.T) {
	logger := NewAuditLogger()

	// Add events for user-1
	for i := 0; i < 2; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-1",
			UserID:    "user-1",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	// Add events for user-2
	for i := 0; i < 1; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-2",
			UserID:    "user-2",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	user1Events := logger.GetEventsByUserID("user-1")
	assert.Len(t, user1Events, 2)
	for _, e := range user1Events {
		assert.Equal(t, "user-1", e.UserID)
	}

	user2Events := logger.GetEventsByUserID("user-2")
	assert.Len(t, user2Events, 1)
	assert.Equal(t, "user-2", user2Events[0].UserID)
}

// TestAuditLogger_Clear tests clearing all events
func TestAuditLogger_Clear(t *testing.T) {
	logger := NewAuditLogger()

	// Add events
	for i := 0; i < 10; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-1",
		})
	}

	assert.Len(t, logger.GetEvents(), 10)

	// Clear
	logger.Clear()
	assert.Empty(t, logger.GetEvents())
}

// TestAuditLogger_NilLogger tests that nil logger doesn't panic
func TestAuditLogger_NilLogger(t *testing.T) {
	var logger *AuditLogger

	// These should not panic
	logger.LogEvent(&AuditEvent{})
	events := logger.GetEvents()
	assert.Empty(t, events)

	events = logger.GetEventsByType("ANY_TYPE")
	assert.Empty(t, events)

	events = logger.GetEventsByClientID("client-1")
	assert.Empty(t, events)

	events = logger.GetEventsByUserID("user-1")
	assert.Empty(t, events)

	logger.Clear()
}

// TestAuditEvent_ValidData tests audit event with valid data
func TestAuditEvent_ValidData(t *testing.T) {
	now := time.Now()
	event := &AuditEvent{
		Timestamp:  now,
		ClientID:   "client-abc123",
		EventType:  "AUTH_VALIDATION_SUCCESS",
		Reason:     "token_valid",
		Details:    "Token successfully validated against WorkOS",
		ProjectID:  "proj-xyz789",
		UserID:     "user-def456",
		RemoteAddr: "192.168.1.100:54321",
		UserAgent:  "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
	}

	assert.Equal(t, now, event.Timestamp)
	assert.Equal(t, "client-abc123", event.ClientID)
	assert.Equal(t, "AUTH_VALIDATION_SUCCESS", event.EventType)
	assert.Equal(t, "token_valid", event.Reason)
	assert.Equal(t, "proj-xyz789", event.ProjectID)
	assert.Equal(t, "user-def456", event.UserID)
	assert.NotEmpty(t, event.RemoteAddr)
	assert.NotEmpty(t, event.UserAgent)
}

// TestBuildAuditLogMessage tests the audit log message format
func TestBuildAuditLogMessage(t *testing.T) {
	now := time.Now()
	event := &AuditEvent{
		Timestamp:  now,
		ClientID:   "client-123",
		EventType:  "AUTH_VALIDATION_FAILED",
		Reason:     "expired_token",
		Details:    "Token expired",
		ProjectID:  "proj-456",
		UserID:     "user-789",
		RemoteAddr: "127.0.0.1:12345",
		UserAgent:  "TestAgent/1.0",
	}

	message := buildAuditLogMessage(event)

	assert.Contains(t, message, "WebSocket Auth Audit")
	assert.Contains(t, message, "AUTH_VALIDATION_FAILED")
	assert.Contains(t, message, "expired_token")
	assert.Contains(t, message, "client-123")
	assert.Contains(t, message, "user-789")
	assert.Contains(t, message, "proj-456")
	assert.Contains(t, message, "127.0.0.1:12345")
}

// TestBuildAuditLogMessage_NilEvent tests building message with nil event
func TestBuildAuditLogMessage_NilEvent(t *testing.T) {
	message := buildAuditLogMessage(nil)
	assert.Equal(t, "invalid audit event", message)
}

// TestAuditLogger_EventImmutability tests that returned events are safe copies
func TestAuditLogger_EventImmutability(t *testing.T) {
	logger := NewAuditLogger()

	originalEvent := &AuditEvent{
		Timestamp: time.Now(),
		ClientID:  "client-1",
		EventType: "AUTH_VALIDATION_SUCCESS",
	}

	logger.LogEvent(originalEvent)

	events := logger.GetEvents()
	assert.Len(t, events, 1)

	// Modify the returned event
	events[0].ClientID = "modified-client"

	// Original should be unchanged
	originalEvents := logger.GetEvents()
	assert.Equal(t, "client-1", originalEvents[0].ClientID)
}

// TestAuditLogger_ConcurrentLogging tests thread-safe logging
func TestAuditLogger_ConcurrentLogging(t *testing.T) {
	logger := NewAuditLogger()

	// Use channels to coordinate goroutines
	done := make(chan bool)

	// Launch multiple goroutines logging events
	for i := 0; i < 10; i++ {
		go func(_ int) {
			for j := 0; j < 10; j++ {
				logger.LogEvent(&AuditEvent{
					Timestamp: time.Now(),
					ClientID:  "client-1",
				})
			}
			done <- true
		}(i)
	}

	// Wait for all goroutines
	for i := 0; i < 10; i++ {
		<-done
	}

	// Should have 100 events
	events := logger.GetEvents()
	assert.Len(t, events, 100)
}

// TestAuditLogger_FilterOperations tests combined filter operations
func TestAuditLogger_FilterOperations(t *testing.T) {
	logger := NewAuditLogger()

	// Add mixed events
	for i := 0; i < 3; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-1",
			UserID:    "user-1",
			EventType: "AUTH_VALIDATION_SUCCESS",
		})
	}

	for i := 0; i < 2; i++ {
		logger.LogEvent(&AuditEvent{
			Timestamp: time.Now(),
			ClientID:  "client-2",
			UserID:    "user-1",
			EventType: "AUTH_VALIDATION_FAILED",
		})
	}

	// Get all events
	allEvents := logger.GetEvents()
	assert.Len(t, allEvents, 5)

	// Filter by type
	successEvents := logger.GetEventsByType("AUTH_VALIDATION_SUCCESS")
	assert.Len(t, successEvents, 3)

	// Filter by user
	user1Events := logger.GetEventsByUserID("user-1")
	assert.Len(t, user1Events, 5) // All events are for user-1

	// Filter by client
	client1Events := logger.GetEventsByClientID("client-1")
	assert.Len(t, client1Events, 3)
}
