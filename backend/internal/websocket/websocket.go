package websocket

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"golang.org/x/net/websocket"

	"github.com/kooshapari/tracertm-backend/internal/auth"
	"github.com/kooshapari/tracertm-backend/internal/events"
)

const (
	authReadDeadline      = 5 * time.Second
	presenceFetchTimeout  = 10 * time.Second
	hubTickerInterval     = 30 * time.Second
	cleanupTickerInterval = 1 * time.Minute
	authHandshakeTimeout  = 5 * time.Minute
	clientSendBufferSize  = 256
	natsEventBufferSize   = 1000
)

// Message represents a WebSocket message
type Message struct {
	Type      string                 `json:"type"`
	Event     *events.Event          `json:"event,omitempty"`
	Data      map[string]interface{} `json:"data,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
}

// AuthMessage represents authentication message from client
type AuthMessage struct {
	Type  string `json:"type"`
	Token string `json:"token"`
}

// AuthResponse represents authentication response to client
type AuthResponse struct {
	Type    string `json:"type"`
	Message string `json:"message,omitempty"`
}

// Client represents a connected WebSocket client
type Client struct {
	ID           string
	Conn         *websocket.Conn
	ProjectID    string
	EntityID     string // Optional: subscribe to specific entity
	Send         chan *Message
	Hub          *Hub
	mu           sync.Mutex
	lastActive   time.Time
	isAuth       bool
	authToken    string
	userID       string
	authDone     chan bool     // Signal when authentication is complete
	user         *auth.User    // Authenticated user from AuthProvider
	authProvider auth.Provider // Injected auth provider for token validation
	auditLogger  *AuditLogger  // Injected audit logger
}

// NewClient creates a new WebSocket client
func NewClient(conn *websocket.Conn, hub *Hub, projectID, entityID string) *Client {
	return &Client{
		ID:          uuid.New().String(),
		Conn:        conn,
		ProjectID:   projectID,
		EntityID:    entityID,
		Send:        make(chan *Message, clientSendBufferSize),
		Hub:         hub,
		lastActive:  time.Now(),
		isAuth:      false,
		authDone:    make(chan bool, 1),
		auditLogger: &AuditLogger{}, // Initialize default audit logger
	}
}

// NewClientWithAuth creates a new WebSocket client with authentication provider
func NewClientWithAuth(
	conn *websocket.Conn, hub *Hub, projectID, entityID string,
	authProvider auth.Provider, auditLogger *AuditLogger,
) *Client {
	client := NewClient(conn, hub, projectID, entityID)
	client.authProvider = authProvider
	if auditLogger != nil {
		client.auditLogger = auditLogger
	}
	return client
}

// ReadPump reads messages from the WebSocket connection
func (c *Client) ReadPump() {
	defer func() {
		c.Hub.Unregister <- c
		if err := c.Conn.Close(); err != nil {
			slog.Error("error closing WebSocket connection", "error", err)
		}
	}()

	if !c.authenticate() {
		return
	}

	// Now process regular messages
	for {
		var msg Message
		if err := websocket.JSON.Receive(c.Conn, &msg); err != nil {
			if err.Error() != "EOF" {
				slog.Error("WebSocket read error", "error", err)
			}
			break
		}
		c.touchLastActive()
		c.handleMessage(&msg)
	}
}

func (c *Client) authenticate() bool {
	// Set read deadline for initial authentication (5 seconds)
	if err := c.Conn.SetReadDeadline(time.Now().Add(authReadDeadline)); err != nil {
		slog.Warn("failed to set auth read deadline", "error", err)
	}

	var authMsg AuthMessage
	if err := websocket.JSON.Receive(c.Conn, &authMsg); err != nil {
		slog.Error("WebSocket auth read error", "error", err)
		c.sendAuthResponse(false, "Authentication message required")
		return false
	}

	if authMsg.Type != "auth" || authMsg.Token == "" {
		slog.Info("Invalid auth message from client", "id", c.ID)
		c.sendAuthResponse(false, "Invalid authentication message")
		return false
	}

	if !c.validateToken(authMsg.Token) {
		slog.Error("Token validation failed for client", "error", c.ID)
		c.sendAuthResponse(false, "Invalid or expired token")
		return false
	}

	c.mu.Lock()
	c.isAuth = true
	c.authToken = authMsg.Token
	c.lastActive = time.Now()
	c.mu.Unlock()

	c.sendAuthResponse(true, "")
	close(c.authDone)
	slog.Info("Client authenticated successfully", "id", c.ID)

	if err := c.Conn.SetReadDeadline(time.Time{}); err != nil {
		slog.Warn("failed to clear read deadline", "error", err)
	}
	return true
}

func (c *Client) touchLastActive() {
	c.mu.Lock()
	c.lastActive = time.Now()
	c.mu.Unlock()
}

func (c *Client) handleMessage(msg *Message) {
	switch msg.Type {
	case "ping":
		c.Send <- &Message{
			Type:      "pong",
			Timestamp: time.Now(),
		}
	case "subscribe_project":
		projectID, ok := msg.Data["project_id"].(string)
		if ok && projectID != "" {
			c.Hub.Unregister <- c
			c.ProjectID = projectID
			c.Hub.Register <- c
			slog.Info("Client subscribed to project", "id", c.ID, "project", projectID)
			c.Send <- &Message{
				Type: "subscription_confirmed",
				Data: map[string]interface{}{
					"project_id": projectID,
				},
				Timestamp: time.Now(),
			}
		}
	case "unsubscribe_project":
		c.Hub.Unregister <- c
		c.ProjectID = ""
		slog.Info("Client unsubscribed from project", "id", c.ID)
	}
}

// sendAuthResponse sends authentication response to client
func (c *Client) sendAuthResponse(success bool, message string) {
	if c.Conn == nil {
		return
	}

	responseType := "auth_success"
	if !success {
		responseType = "auth_failed"
	}

	response := AuthResponse{
		Type:    responseType,
		Message: message,
	}

	err := websocket.JSON.Send(c.Conn, response)
	if err != nil {
		slog.Error("Error sending auth response", "error", err)
	}

	// Close connection if authentication failed
	if !success {
		if err := c.Conn.Close(); err != nil {
			slog.Warn("failed to close websocket conn after auth failure", "error", err)
		}
	}
}

// validateToken validates the authentication token against WorkOS AuthKit/AuthProvider
// Returns true if the token is valid, false otherwise
func (c *Client) validateToken(token string) bool {
	if token == "" {
		c.logAuditEvent("AUTH_VALIDATION_FAILED", "empty_token", "Token is empty")
		return false
	}

	// If no auth provider is configured, reject the connection
	if c.authProvider == nil {
		c.logAuditEvent("AUTH_VALIDATION_FAILED", "no_auth_provider", "Auth provider not configured")
		slog.Error("[SECURITY] WebSocket auth failed: no auth provider configured for client", "error", c.ID)
		return false
	}

	// Validate token using the auth provider (e.g., KitAdapter)
	// This validates JWT signature, expiration, issuer, and audience
	ctx, cancel := context.WithTimeout(context.Background(), presenceFetchTimeout)
	defer cancel()

	user, err := c.authProvider.ValidateToken(ctx, token)
	if err != nil {
		c.logAuditEvent("AUTH_VALIDATION_FAILED", "invalid_token", fmt.Sprintf("Token validation failed: %v", err))
		slog.Error("[SECURITY] WebSocket auth failed for client", "error", c.ID, "error", err)
		return false
	}

	if user == nil {
		c.logAuditEvent("AUTH_VALIDATION_FAILED", "null_user", "Token validation returned null user")
		slog.Error("[SECURITY] WebSocket auth failed for client : user is nil", "error", c.ID)
		return false
	}

	// Store user information for later use
	c.mu.Lock()
	c.user = user
	c.userID = user.ID
	c.mu.Unlock()

	c.logAuditEvent("AUTH_VALIDATION_SUCCESS", "token_valid", "User "+user.Email+" authenticated")
	slog.Info("WebSocket token validated for user (email ) on client", "id", user.ID, "detail", user.Email, "id", c.ID)

	return true
}

// logAuditEvent logs authentication-related events for audit trail
func (c *Client) logAuditEvent(eventType, reason, details string) {
	if c.auditLogger != nil {
		remoteAddr := ""
		userAgent := ""

		// Safely extract request information if available
		if c.Conn != nil && c.Conn.Request() != nil {
			remoteAddr = c.Conn.Request().RemoteAddr
			userAgent = c.Conn.Request().UserAgent()
		}

		c.auditLogger.LogEvent(&AuditEvent{
			Timestamp:  time.Now(),
			ClientID:   c.ID,
			EventType:  eventType,
			Reason:     reason,
			Details:    details,
			ProjectID:  c.ProjectID,
			UserID:     c.userID,
			RemoteAddr: remoteAddr,
			UserAgent:  userAgent,
		})
	}
}

// WritePump writes messages to the WebSocket connection
func (c *Client) WritePump() {
	ticker := time.NewTicker(hubTickerInterval)
	defer func() {
		ticker.Stop()
		if err := c.Conn.Close(); err != nil {
			slog.Error("error closing WebSocket connection", "error", err)
		}
	}()

	for {
		select {
		case message, ok := <-c.Send:
			if !ok {
				// Hub closed the channel
				return
			}

			err := websocket.JSON.Send(c.Conn, message)
			if err != nil {
				slog.Error("WebSocket write error", "error", err)
				return
			}

		case <-ticker.C:
			// Only send ping if authenticated
			if c.isAuth {
				c.Send <- &Message{
					Type:      "ping",
					Timestamp: time.Now(),
				}
			}
		}
	}
}

// RegisterInHub registers the client in the hub after authentication
func (c *Client) RegisterInHub() {
	if !c.isAuth {
		slog.Error("Cannot register unauthenticated client", "id", c.ID)
		return
	}
	c.Hub.Register <- c
	slog.Info("Client registered in hub (project )", "id", c.ID, "project", c.ProjectID)
}

// Hub maintains active WebSocket connections and broadcasts messages
type Hub struct {
	// Registered clients by project ID
	Clients map[string]map[*Client]bool

	// Clients by entity ID for targeted updates
	EntityClients map[string]map[*Client]bool

	// Register requests from clients
	Register chan *Client

	// Unregister requests from clients
	Unregister chan *Client

	// Broadcast message to all clients in a project
	Broadcast chan *Message

	// Broadcast to specific entity subscribers
	BroadcastToEntity chan *EntityMessage

	// NATS event channel for real-time updates
	NATSEventChannel chan *NATSEvent

	Mu sync.RWMutex
}

// NATSEvent represents an event from NATS to be broadcast via WebSocket
type NATSEvent struct {
	EventType  string                 `json:"event_type"`
	ProjectID  string                 `json:"project_id"`
	EntityID   string                 `json:"entity_id"`
	EntityType string                 `json:"entity_type"`
	Data       map[string]interface{} `json:"data"`
	Timestamp  string                 `json:"timestamp"`
	Source     string                 `json:"source"` // "go" or "python"
}

// EntityMessage represents a message targeted to specific entity subscribers
type EntityMessage struct {
	EntityID string
	Message  *Message
}

// NewHub creates a new WebSocket hub
func NewHub() *Hub {
	return &Hub{
		Clients:           make(map[string]map[*Client]bool),
		EntityClients:     make(map[string]map[*Client]bool),
		Register:          make(chan *Client),
		Unregister:        make(chan *Client),
		Broadcast:         make(chan *Message),
		BroadcastToEntity: make(chan *EntityMessage),
		NATSEventChannel:  make(chan *NATSEvent, natsEventBufferSize),
	}
}

// Run starts the hub's main loop
func (h *Hub) Run(ctx context.Context) {
	cleanupTicker := time.NewTicker(cleanupTickerInterval)
	defer cleanupTicker.Stop()

	for {
		select {
		case <-ctx.Done():
			slog.Info("WebSocket hub shutting down")
			return

		case client := <-h.Register:
			h.handleClientRegister(client)

		case client := <-h.Unregister:
			h.handleClientUnregister(client)

		case message := <-h.Broadcast:
			h.handleBroadcast(message)

		case entityMsg := <-h.BroadcastToEntity:
			h.handleBroadcastToEntity(entityMsg)

		case natsEvent := <-h.NATSEventChannel:
			// Handle NATS event and broadcast to project subscribers
			h.handleNATSEvent(natsEvent)

		case <-cleanupTicker.C:
			// Clean up inactive connections
			h.cleanupInactiveClients()
		}
	}
}

// handleClientRegister registers a new client in the hub
func (h *Hub) handleClientRegister(client *Client) {
	h.Mu.Lock()
	defer h.Mu.Unlock()

	// Register client by project
	if h.Clients[client.ProjectID] == nil {
		h.Clients[client.ProjectID] = make(map[*Client]bool)
	}
	h.Clients[client.ProjectID][client] = true

	// Register client by entity if specified
	if client.EntityID != "" {
		if h.EntityClients[client.EntityID] == nil {
			h.EntityClients[client.EntityID] = make(map[*Client]bool)
		}
		h.EntityClients[client.EntityID][client] = true
	}

	slog.Info("Client registered (project , entity )", "id", client.ID, "project", client.ProjectID, "id", client.EntityID)
}

// handleClientUnregister unregisters a client from the hub
func (h *Hub) handleClientUnregister(client *Client) {
	h.Mu.Lock()
	defer h.Mu.Unlock()

	// Remove from project clients
	if _, ok := h.Clients[client.ProjectID][client]; ok {
		delete(h.Clients[client.ProjectID], client)
		if len(h.Clients[client.ProjectID]) == 0 {
			delete(h.Clients, client.ProjectID)
		}
	}

	// Remove from entity clients
	if client.EntityID != "" {
		if _, ok := h.EntityClients[client.EntityID][client]; ok {
			delete(h.EntityClients[client.EntityID], client)
			if len(h.EntityClients[client.EntityID]) == 0 {
				delete(h.EntityClients, client.EntityID)
			}
		}
	}
	close(client.Send)

	slog.Info("Client unregistered", "id", client.ID)
}

// handleBroadcast broadcasts a message to all connected clients
func (h *Hub) handleBroadcast(message *Message) {
	h.Mu.RLock()
	defer h.Mu.RUnlock()

	// Broadcast to all clients (global broadcast)
	for projectID := range h.Clients {
		for client := range h.Clients[projectID] {
			select {
			case client.Send <- message:
			default:
				// Client's send buffer is full, close it
				close(client.Send)
				delete(h.Clients[projectID], client)
			}
		}
	}
}

// handleBroadcastToEntity broadcasts a message to entity-specific subscribers
func (h *Hub) handleBroadcastToEntity(entityMsg *EntityMessage) {
	h.Mu.RLock()
	defer h.Mu.RUnlock()

	// Broadcast to entity-specific subscribers
	if clients, ok := h.EntityClients[entityMsg.EntityID]; ok {
		for client := range clients {
			select {
			case client.Send <- entityMsg.Message:
			default:
				close(client.Send)
				delete(h.EntityClients[entityMsg.EntityID], client)
			}
		}
	}
}

// cleanupInactiveClients removes clients that haven't been active recently
func (h *Hub) cleanupInactiveClients() {
	h.Mu.Lock()
	defer h.Mu.Unlock()

	timeout := authHandshakeTimeout
	now := time.Now()

	for projectID, clients := range h.Clients {
		for client := range clients {
			client.mu.Lock()
			if now.Sub(client.lastActive) > timeout {
				slog.Info("Cleaning up inactive client", "id", client.ID)
				close(client.Send)
				delete(clients, client)
				if client.EntityID != "" {
					delete(h.EntityClients[client.EntityID], client)
				}
			}
			client.mu.Unlock()
		}
		if len(clients) == 0 {
			delete(h.Clients, projectID)
		}
	}
}

// BroadcastToProject sends a message to all clients in a specific project
func (h *Hub) BroadcastToProject(projectID string, message *Message) {
	h.Mu.RLock()
	defer h.Mu.RUnlock()

	if clients, ok := h.Clients[projectID]; ok {
		for client := range clients {
			select {
			case client.Send <- message:
			default:
				slog.Error("Failed to send message to client (buffer full)", "error", client.ID)
			}
		}
	}
}

// HandleNATSEvent processes incoming NATS events and queues them for broadcasting
func (h *Hub) HandleNATSEvent(event *NATSEvent) {
	select {
	case h.NATSEventChannel <- event:
		// Successfully queued
	default:
		slog.Info("⚠️ NATS event channel full, dropping event for project", "detail", event.EventType, "project", event.ProjectID)
	}
}

// handleNATSEvent broadcasts a NATS event to relevant WebSocket clients
func (h *Hub) handleNATSEvent(event *NATSEvent) {
	h.Mu.RLock()
	defer h.Mu.RUnlock()

	// Get clients for this project
	clients, ok := h.Clients[event.ProjectID]
	if !ok || len(clients) == 0 {
		// No clients watching this project
		return
	}

	// Create WebSocket message from NATS event
	message := &Message{
		Type: "nats_event",
		Data: map[string]interface{}{
			"event_type":  event.EventType,
			"project_id":  event.ProjectID,
			"entity_id":   event.EntityID,
			"entity_type": event.EntityType,
			"data":        event.Data,
			"timestamp":   event.Timestamp,
			"source":      event.Source,
		},
		Timestamp: time.Now(),
	}

	// Send to all clients watching this project
	sent := 0
	dropped := 0
	for client := range clients {
		select {
		case client.Send <- message:
			sent++
		default:
			// Client buffer full, skip
			dropped++
			slog.Warn("⚠️ Client send buffer full, skipping NATS event", "id", client.ID, "detail", event.EventType)
		}
	}

	if sent > 0 {
		slog.Info("Broadcast NATS event",
			"event_type", event.EventType, "sent", sent, "project_id", event.ProjectID, "dropped", dropped)
	}
}

// BroadcastEvent broadcasts an event to all relevant subscribers
func (h *Hub) BroadcastEvent(event *events.Event) {
	message := &Message{
		Type:      "event",
		Event:     event,
		Timestamp: time.Now(),
	}

	// Broadcast to project subscribers
	h.BroadcastToProject(event.ProjectID, message)

	// Broadcast to entity-specific subscribers
	h.BroadcastToEntity <- &EntityMessage{
		EntityID: event.EntityID,
		Message:  message,
	}
}

// GetStats returns statistics about connected clients
func (h *Hub) GetStats() map[string]interface{} {
	h.Mu.RLock()
	defer h.Mu.RUnlock()

	projectCounts := make(map[string]int)
	totalClients := 0

	for projectID, clients := range h.Clients {
		count := len(clients)
		projectCounts[projectID] = count
		totalClients += count
	}

	return map[string]interface{}{
		"total_clients":        totalClients,
		"projects":             len(h.Clients),
		"project_counts":       projectCounts,
		"entity_subscriptions": len(h.EntityClients),
	}
}

const (
	httpStatusBadRequest          = 400
	httpStatusInternalServerError = 500
	httpStatusOK                  = 200
)

// Handler creates an Echo handler for WebSocket connections
// SECURITY: Token is NO LONGER passed in query parameters
// Token must be sent in first message after connection (auth message)
func Handler(hub *Hub, authProvider auth.Provider) echo.HandlerFunc {
	return func(c echo.Context) error {
		projectID := c.QueryParam("project_id")
		if projectID == "" {
			return echo.NewHTTPError(httpStatusBadRequest, "project_id is required")
		}

		entityID := c.QueryParam("entity_id") // Optional

		// Reject any token in query parameters (security fix)
		if token := c.QueryParam("token"); token != "" {
			slog.Info("[SECURITY] Rejected WebSocket connection with token in URL query parameters")
			return echo.NewHTTPError(httpStatusBadRequest, "token must not be passed in URL parameters; use authentication message instead")
		}

		// Validate that authProvider is configured
		if authProvider == nil {
			slog.Info("[SECURITY] WebSocket handler called without auth provider configured")
			return echo.NewHTTPError(httpStatusInternalServerError, "authentication provider not configured")
		}

		websocket.Handler(func(ws *websocket.Conn) {
			// Create audit logger
			auditLogger := NewAuditLogger()

			// Create client with auth provider
			client := NewClientWithAuth(ws, hub, projectID, entityID, authProvider, auditLogger)

			// Start write pump first
			go client.WritePump()

			// ReadPump handles authentication (blocking)
			// Must complete authentication before hub registration
			client.ReadPump()

			// After ReadPump returns, if authenticated, register in hub
			if client.isAuth {
				client.RegisterInHub()
			}
		}).ServeHTTP(c.Response(), c.Request())

		return nil
	}
}

// EventBroadcaster implements the EventPublisher interface
type EventBroadcaster struct {
	hub *Hub
}

// NewEventBroadcaster creates a new event broadcaster
func NewEventBroadcaster(hub *Hub) *EventBroadcaster {
	return &EventBroadcaster{hub: hub}
}

// Publish broadcasts an event to all subscribers
func (b *EventBroadcaster) Publish(event *events.Event) error {
	message := &Message{
		Type:      "event",
		Event:     event,
		Timestamp: time.Now(),
	}

	b.hub.Broadcast <- message
	return nil
}

// PublishToProject broadcasts an event to project-specific subscribers
func (b *EventBroadcaster) PublishToProject(projectID string, event *events.Event) error {
	message := &Message{
		Type:      "event",
		Event:     event,
		Timestamp: time.Now(),
	}

	b.hub.BroadcastToProject(projectID, message)
	return nil
}

// PublishToEntity broadcasts an event to entity-specific subscribers
func (b *EventBroadcaster) PublishToEntity(entityID string, event *events.Event) error {
	message := &Message{
		Type:      "event",
		Event:     event,
		Timestamp: time.Now(),
	}

	b.hub.BroadcastToEntity <- &EntityMessage{
		EntityID: entityID,
		Message:  message,
	}
	return nil
}

// BroadcastData sends arbitrary data to clients
func (b *EventBroadcaster) BroadcastData(projectID string, msgType string, data map[string]interface{}) error {
	message := &Message{
		Type:      msgType,
		Data:      data,
		Timestamp: time.Now(),
	}

	if projectID != "" {
		b.hub.BroadcastToProject(projectID, message)
	} else {
		b.hub.Broadcast <- message
	}

	return nil
}

// StatsHandler returns an Echo handler for WebSocket statistics
func StatsHandler(hub *Hub) echo.HandlerFunc {
	return func(c echo.Context) error {
		stats := hub.GetStats()
		return c.JSON(httpStatusOK, stats)
	}
}
