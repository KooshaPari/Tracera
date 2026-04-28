// Package websocket provides WebSocket server, audit, presence, and message handling.
// Package websocket provides websocket hub and audit helpers.
package websocket

import (
	"log/slog"
	"sync"
	"time"
)

// AuditEvent represents an authentication audit event
type AuditEvent struct {
	Timestamp  time.Time
	ClientID   string
	EventType  string // AUTH_VALIDATION_SUCCESS, AUTH_VALIDATION_FAILED, DISCONNECTION, etc.
	Reason     string // Specific reason for the event (e.g., invalid_token, expired_token)
	Details    string // Additional details about the event
	ProjectID  string
	UserID     string
	RemoteAddr string
	UserAgent  string
}

// AuditLogger handles audit logging for WebSocket authentication events
type AuditLogger struct {
	mu     sync.Mutex
	events []*AuditEvent
}

// NewAuditLogger creates a new audit logger
func NewAuditLogger() *AuditLogger {
	return &AuditLogger{
		events: make([]*AuditEvent, 0),
	}
}

// LogEvent logs an authentication event
func (al *AuditLogger) LogEvent(event *AuditEvent) {
	if al == nil {
		return
	}

	al.mu.Lock()
	defer al.mu.Unlock()

	al.events = append(al.events, event)

	// Log to standard logger with structured format
	logMessage := buildAuditLogMessage(event)
	slog.Info("[AUDIT]", "detail", logMessage)
}

// GetEvents returns all logged events (for testing or inspection)
func (al *AuditLogger) GetEvents() []*AuditEvent {
	if al == nil {
		return []*AuditEvent{}
	}

	al.mu.Lock()
	defer al.mu.Unlock()

	// Return a slice of deep copies to prevent external modification
	eventsCopy := make([]*AuditEvent, len(al.events))
	for i, event := range al.events {
		eventCopy := *event // Make a copy of the struct
		eventsCopy[i] = &eventCopy
	}
	return eventsCopy
}

// GetEventsByType filters events by type
func (al *AuditLogger) GetEventsByType(eventType string) []*AuditEvent {
	if al == nil {
		return []*AuditEvent{}
	}

	al.mu.Lock()
	defer al.mu.Unlock()

	var filtered []*AuditEvent
	for _, event := range al.events {
		if event.EventType == eventType {
			filtered = append(filtered, event)
		}
	}
	return filtered
}

// GetEventsByClientID filters events by client ID
func (al *AuditLogger) GetEventsByClientID(clientID string) []*AuditEvent {
	if al == nil {
		return []*AuditEvent{}
	}

	al.mu.Lock()
	defer al.mu.Unlock()

	var filtered []*AuditEvent
	for _, event := range al.events {
		if event.ClientID == clientID {
			filtered = append(filtered, event)
		}
	}
	return filtered
}

// GetEventsByUserID filters events by user ID
func (al *AuditLogger) GetEventsByUserID(userID string) []*AuditEvent {
	if al == nil {
		return []*AuditEvent{}
	}

	al.mu.Lock()
	defer al.mu.Unlock()

	var filtered []*AuditEvent
	for _, event := range al.events {
		if event.UserID == userID {
			filtered = append(filtered, event)
		}
	}
	return filtered
}

// Clear clears all logged events
func (al *AuditLogger) Clear() {
	if al == nil {
		return
	}

	al.mu.Lock()
	defer al.mu.Unlock()

	al.events = make([]*AuditEvent, 0)
}

// buildAuditLogMessage creates a structured log message from an audit event
func buildAuditLogMessage(event *AuditEvent) string {
	if event == nil {
		return "invalid audit event"
	}

	return "WebSocket Auth Audit | " +
		"Time:" + event.Timestamp.Format(time.RFC3339) + " | " +
		"Type:" + event.EventType + " | " +
		"Reason:" + event.Reason + " | " +
		"ClientID:" + event.ClientID + " | " +
		"UserID:" + event.UserID + " | " +
		"ProjectID:" + event.ProjectID + " | " +
		"RemoteAddr:" + event.RemoteAddr + " | " +
		"Details:" + event.Details
}
