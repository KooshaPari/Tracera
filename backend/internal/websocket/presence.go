package websocket

import (
	"log/slog"
	"sync"
	"time"
)

// PresenceStatus represents a user's presence status
type PresenceStatus string

const (
	// PresenceOnline indicates user is online.
	PresenceOnline PresenceStatus = "online"
	// PresenceViewing indicates user is viewing.
	PresenceViewing PresenceStatus = "viewing"
	// PresenceEditing indicates user is editing.
	PresenceEditing PresenceStatus = "editing"
	// PresenceIdle indicates user is idle.
	PresenceIdle PresenceStatus = "idle"
	// PresenceOffline indicates user is offline.
	PresenceOffline PresenceStatus = "offline"
)

// PresenceActivity represents what a user is currently doing
type PresenceActivity struct {
	UserID       string                 `json:"user_id"`
	ClientID     string                 `json:"client_id"`
	Status       PresenceStatus         `json:"status"`
	ProjectID    string                 `json:"project_id"`
	EntityID     string                 `json:"entity_id,omitempty"`   // What they're viewing/editing
	EntityType   string                 `json:"entity_type,omitempty"` // Type of entity
	Metadata     map[string]interface{} `json:"metadata,omitempty"`    // Additional context
	LastSeen     time.Time              `json:"last_seen"`
	LastActivity time.Time              `json:"last_activity"`
	ConnectedAt  time.Time              `json:"connected_at"`
}

// PresenceTracker tracks user presence and activity
type PresenceTracker struct {
	// Map of client ID to presence activity
	clientPresence map[string]*PresenceActivity

	// Map of user ID to list of client IDs (multiple devices/tabs)
	userClients map[string][]string

	// Map of project ID to list of user IDs currently in the project
	projectUsers map[string]map[string]bool

	// Map of entity ID to list of users viewing/editing it
	entityViewers map[string]map[string]*PresenceActivity
	entityEditors map[string]map[string]*PresenceActivity

	mu sync.RWMutex
}

// NewPresenceTracker creates a new presence tracker
func NewPresenceTracker() *PresenceTracker {
	return &PresenceTracker{
		clientPresence: make(map[string]*PresenceActivity),
		userClients:    make(map[string][]string),
		projectUsers:   make(map[string]map[string]bool),
		entityViewers:  make(map[string]map[string]*PresenceActivity),
		entityEditors:  make(map[string]map[string]*PresenceActivity),
	}
}

// Join marks a client as joining a project
func (pt *PresenceTracker) Join(clientID, userID, projectID string) *PresenceActivity {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	now := time.Now()
	presence := &PresenceActivity{
		UserID:       userID,
		ClientID:     clientID,
		Status:       PresenceOnline,
		ProjectID:    projectID,
		LastSeen:     now,
		LastActivity: now,
		ConnectedAt:  now,
		Metadata:     make(map[string]interface{}),
	}

	pt.clientPresence[clientID] = presence

	// Add to user clients
	pt.userClients[userID] = append(pt.userClients[userID], clientID)

	// Add to project users
	if pt.projectUsers[projectID] == nil {
		pt.projectUsers[projectID] = make(map[string]bool)
	}
	pt.projectUsers[projectID][userID] = true

	slog.Info("User joined project (client )", "user", userID, "project", projectID, "id", clientID)
	return presence
}

// Leave marks a client as leaving
func (pt *PresenceTracker) Leave(clientID string) {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	presence, exists := pt.clientPresence[clientID]
	if !exists {
		return
	}

	// Remove from entity viewers/editors
	if presence.EntityID != "" {
		delete(pt.entityViewers[presence.EntityID], clientID)
		delete(pt.entityEditors[presence.EntityID], clientID)
	}

	// Remove from user clients
	userClients := pt.userClients[presence.UserID]
	for i, cid := range userClients {
		if cid == clientID {
			pt.userClients[presence.UserID] = append(userClients[:i], userClients[i+1:]...)
			break
		}
	}

	// If user has no more clients, remove from project
	if len(pt.userClients[presence.UserID]) == 0 {
		delete(pt.projectUsers[presence.ProjectID], presence.UserID)
		delete(pt.userClients, presence.UserID)
	}

	// Remove client presence
	delete(pt.clientPresence, clientID)

	slog.Info("User left project (client )", "user", presence.UserID, "project", presence.ProjectID, "id", clientID)
}

// UpdateStatus updates a client's presence status
func (pt *PresenceTracker) UpdateStatus(clientID string, status PresenceStatus) {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	if presence, ok := pt.clientPresence[clientID]; ok {
		presence.Status = status
		presence.LastActivity = time.Now()
		presence.LastSeen = time.Now()
	}
}

// StartViewing marks a user as viewing an entity
func (pt *PresenceTracker) StartViewing(clientID, entityID, entityType string) {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	presence, exists := pt.clientPresence[clientID]
	if !exists {
		return
	}

	// Remove from previous entity if exists
	if presence.EntityID != "" && presence.EntityID != entityID {
		delete(pt.entityViewers[presence.EntityID], clientID)
		delete(pt.entityEditors[presence.EntityID], clientID)
	}

	// Update presence
	presence.EntityID = entityID
	presence.EntityType = entityType
	presence.Status = PresenceViewing
	presence.LastActivity = time.Now()
	presence.LastSeen = time.Now()

	// Add to entity viewers
	if pt.entityViewers[entityID] == nil {
		pt.entityViewers[entityID] = make(map[string]*PresenceActivity)
	}
	pt.entityViewers[entityID][clientID] = presence

	slog.Info("User started viewing", "user", presence.UserID, "detail", entityType, "id", entityID)
}

// StartEditing marks a user as editing an entity
func (pt *PresenceTracker) StartEditing(clientID, entityID, entityType string) {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	presence, exists := pt.clientPresence[clientID]
	if !exists {
		return
	}

	// Remove from previous entity if exists
	if presence.EntityID != "" && presence.EntityID != entityID {
		delete(pt.entityViewers[presence.EntityID], clientID)
		delete(pt.entityEditors[presence.EntityID], clientID)
	}

	// Update presence
	presence.EntityID = entityID
	presence.EntityType = entityType
	presence.Status = PresenceEditing
	presence.LastActivity = time.Now()
	presence.LastSeen = time.Now()

	// Add to entity editors (also keep in viewers)
	if pt.entityViewers[entityID] == nil {
		pt.entityViewers[entityID] = make(map[string]*PresenceActivity)
	}
	pt.entityViewers[entityID][clientID] = presence

	if pt.entityEditors[entityID] == nil {
		pt.entityEditors[entityID] = make(map[string]*PresenceActivity)
	}
	pt.entityEditors[entityID][clientID] = presence

	slog.Info("User started editing", "user", presence.UserID, "detail", entityType, "id", entityID)
}

// StopViewing marks a user as no longer viewing an entity
func (pt *PresenceTracker) StopViewing(clientID string) {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	presence, exists := pt.clientPresence[clientID]
	if !exists {
		return
	}

	if presence.EntityID != "" {
		delete(pt.entityViewers[presence.EntityID], clientID)
		delete(pt.entityEditors[presence.EntityID], clientID)

		slog.Info("User stopped viewing", "user", presence.UserID, "detail", presence.EntityType, "id", presence.EntityID)

		presence.EntityID = ""
		presence.EntityType = ""
	}

	presence.Status = PresenceOnline
	presence.LastActivity = time.Now()
	presence.LastSeen = time.Now()
}

// Heartbeat updates the last seen time for a client
func (pt *PresenceTracker) Heartbeat(clientID string) {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	if presence, ok := pt.clientPresence[clientID]; ok {
		presence.LastSeen = time.Now()
	}
}

// GetProjectPresence gets all users present in a project
func (pt *PresenceTracker) GetProjectPresence(projectID string) []*PresenceActivity {
	pt.mu.RLock()
	defer pt.mu.RUnlock()

	userIDs, exists := pt.projectUsers[projectID]
	if !exists {
		return nil
	}

	// Collect all presence activities for users in this project
	activities := make([]*PresenceActivity, 0)
	for userID := range userIDs {
		clientIDs := pt.userClients[userID]
		for _, clientID := range clientIDs {
			if presence, ok := pt.clientPresence[clientID]; ok {
				if presence.ProjectID == projectID {
					activities = append(activities, presence)
				}
			}
		}
	}

	return activities
}

// GetEntityViewers gets all users viewing an entity
func (pt *PresenceTracker) GetEntityViewers(entityID string) []*PresenceActivity {
	pt.mu.RLock()
	defer pt.mu.RUnlock()

	viewers, exists := pt.entityViewers[entityID]
	if !exists {
		return nil
	}

	activities := make([]*PresenceActivity, 0, len(viewers))
	for _, presence := range viewers {
		activities = append(activities, presence)
	}

	return activities
}

// GetEntityEditors gets all users editing an entity
func (pt *PresenceTracker) GetEntityEditors(entityID string) []*PresenceActivity {
	pt.mu.RLock()
	defer pt.mu.RUnlock()

	editors, exists := pt.entityEditors[entityID]
	if !exists {
		return nil
	}

	activities := make([]*PresenceActivity, 0, len(editors))
	for _, presence := range editors {
		activities = append(activities, presence)
	}

	return activities
}

// GetUserPresence gets the presence for a specific user (all their clients)
func (pt *PresenceTracker) GetUserPresence(userID string) []*PresenceActivity {
	pt.mu.RLock()
	defer pt.mu.RUnlock()

	clientIDs, exists := pt.userClients[userID]
	if !exists {
		return nil
	}

	activities := make([]*PresenceActivity, 0, len(clientIDs))
	for _, clientID := range clientIDs {
		if presence, ok := pt.clientPresence[clientID]; ok {
			activities = append(activities, presence)
		}
	}

	return activities
}

// removeClientPresence removes a single client's presence from all tracking maps.
func (pt *PresenceTracker) removeClientPresence(clientID string, presence *PresenceActivity) {
	if presence.EntityID != "" {
		delete(pt.entityViewers[presence.EntityID], clientID)
		delete(pt.entityEditors[presence.EntityID], clientID)
	}

	userClients := pt.userClients[presence.UserID]
	for i, cid := range userClients {
		if cid == clientID {
			pt.userClients[presence.UserID] = append(userClients[:i], userClients[i+1:]...)
			break
		}
	}

	if len(pt.userClients[presence.UserID]) == 0 {
		delete(pt.projectUsers[presence.ProjectID], presence.UserID)
		delete(pt.userClients, presence.UserID)
	}

	delete(pt.clientPresence, clientID)
}

// CleanupStalePresence removes inactive presence entries
func (pt *PresenceTracker) CleanupStalePresence(timeout time.Duration) int {
	pt.mu.Lock()
	defer pt.mu.Unlock()

	now := time.Now()
	removed := 0

	for clientID, presence := range pt.clientPresence {
		if now.Sub(presence.LastSeen) > timeout {
			pt.removeClientPresence(clientID, presence)
			removed++
		}
	}

	if removed > 0 {
		slog.Info("Cleaned up stale presence entries", "value", removed)
	}

	return removed
}

// GetStats returns statistics about presence
func (pt *PresenceTracker) GetStats() map[string]interface{} {
	pt.mu.RLock()
	defer pt.mu.RUnlock()

	statusCount := make(map[PresenceStatus]int)
	for _, presence := range pt.clientPresence {
		statusCount[presence.Status]++
	}

	return map[string]interface{}{
		"total_clients":         len(pt.clientPresence),
		"total_users":           len(pt.userClients),
		"total_projects":        len(pt.projectUsers),
		"entities_being_viewed": len(pt.entityViewers),
		"entities_being_edited": len(pt.entityEditors),
		"status_breakdown":      statusCount,
	}
}

// BroadcastPresenceUpdate creates a message for presence updates
func (pt *PresenceTracker) BroadcastPresenceUpdate(projectID string) *Message {
	presence := pt.GetProjectPresence(projectID)

	return &Message{
		Type: "presence_update",
		Data: map[string]interface{}{
			"project_id": projectID,
			"presence":   presence,
		},
		Timestamp: time.Now(),
	}
}

// BroadcastEntityPresenceUpdate creates a message for entity-specific presence updates
func (pt *PresenceTracker) BroadcastEntityPresenceUpdate(entityID string) *Message {
	viewers := pt.GetEntityViewers(entityID)
	editors := pt.GetEntityEditors(entityID)

	return &Message{
		Type: "entity_presence_update",
		Data: map[string]interface{}{
			"entity_id": entityID,
			"viewers":   viewers,
			"editors":   editors,
		},
		Timestamp: time.Now(),
	}
}
