package websocket

import (
	"fmt"
	"log/slog"
	"strconv"
	"sync"
	"time"
)

// SubscriptionType represents the type of subscription
type SubscriptionType string

const (
	// SubscribeToProject subscribes to all events in a project
	SubscribeToProject SubscriptionType = "project"

	// SubscribeToEntity subscribes to a specific entity (item, link, etc.)
	SubscribeToEntity SubscriptionType = "entity"

	// SubscribeToEventType subscribes to specific event types
	SubscribeToEventType SubscriptionType = "event_type"

	// SubscribeToMultiple subscribes to multiple entities
	SubscribeToMultiple SubscriptionType = "multiple"
)

// Subscription represents a client's subscription to resources
type Subscription struct {
	ID           string
	ClientID     string
	Type         SubscriptionType
	ResourceID   string   // Project ID, Entity ID, or Event Type
	ResourceIDs  []string // For multiple subscriptions
	Filters      map[string]interface{}
	CreatedAt    time.Time
	LastActivity time.Time
}

// SubscriptionManager manages all client subscriptions
type SubscriptionManager struct {
	// Map of subscription ID to subscription
	subscriptions map[string]*Subscription

	// Map of client ID to list of subscription IDs
	clientSubscriptions map[string][]string

	// Map of resource ID to list of subscription IDs
	resourceSubscriptions map[string][]string

	// Map of subscription ID to client pointer
	subscriptionClients map[string]*Client

	mu sync.RWMutex
}

// NewSubscriptionManager creates a new subscription manager
func NewSubscriptionManager() *SubscriptionManager {
	return &SubscriptionManager{
		subscriptions:         make(map[string]*Subscription),
		clientSubscriptions:   make(map[string][]string),
		resourceSubscriptions: make(map[string][]string),
		subscriptionClients:   make(map[string]*Client),
	}
}

// Subscribe creates a new subscription for a client
func (sm *SubscriptionManager) Subscribe(
	client *Client, subType SubscriptionType, resourceID string, filters map[string]interface{},
) (*Subscription, error) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	// Generate subscription ID
	subID := "sub_" + client.ID + "_" + resourceID + "_" + strconv.FormatInt(time.Now().UnixNano(), 10)

	sub := &Subscription{
		ID:           subID,
		ClientID:     client.ID,
		Type:         subType,
		ResourceID:   resourceID,
		Filters:      filters,
		CreatedAt:    time.Now(),
		LastActivity: time.Now(),
	}

	// Store subscription
	sm.subscriptions[subID] = sub
	sm.subscriptionClients[subID] = client

	// Add to client subscriptions
	sm.clientSubscriptions[client.ID] = append(sm.clientSubscriptions[client.ID], subID)

	// Add to resource subscriptions
	sm.resourceSubscriptions[resourceID] = append(sm.resourceSubscriptions[resourceID], subID)

	slog.Info("Created subscription",
		"sub_id", subID, "client_id", client.ID, "type", subType, "resource_id", resourceID)

	return sub, nil
}

// SubscribeMultiple creates a subscription for multiple resources
func (sm *SubscriptionManager) SubscribeMultiple(
	client *Client, resourceIDs []string, filters map[string]interface{},
) (*Subscription, error) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	subID := "sub_" + client.ID + "_multi_" + strconv.FormatInt(time.Now().UnixNano(), 10)

	sub := &Subscription{
		ID:           subID,
		ClientID:     client.ID,
		Type:         SubscribeToMultiple,
		ResourceIDs:  resourceIDs,
		Filters:      filters,
		CreatedAt:    time.Now(),
		LastActivity: time.Now(),
	}

	sm.subscriptions[subID] = sub
	sm.subscriptionClients[subID] = client
	sm.clientSubscriptions[client.ID] = append(sm.clientSubscriptions[client.ID], subID)

	// Add to all resource subscriptions
	for _, resourceID := range resourceIDs {
		sm.resourceSubscriptions[resourceID] = append(sm.resourceSubscriptions[resourceID], subID)
	}

	slog.Info("Created multi-subscription",
		"sub_id", subID, "client_id", client.ID, "resource_count", len(resourceIDs))

	return sub, nil
}

// Unsubscribe removes a subscription
func (sm *SubscriptionManager) Unsubscribe(subID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	sub, exists := sm.subscriptions[subID]
	if !exists {
		return fmt.Errorf("subscription not found: %s", subID)
	}

	// Remove from client subscriptions
	clientSubs := sm.clientSubscriptions[sub.ClientID]
	for i, id := range clientSubs {
		if id == subID {
			sm.clientSubscriptions[sub.ClientID] = append(clientSubs[:i], clientSubs[i+1:]...)
			break
		}
	}

	// Remove from resource subscriptions
	if sub.Type == SubscribeToMultiple {
		for _, resourceID := range sub.ResourceIDs {
			sm.removeFromResourceSubscriptions(resourceID, subID)
		}
	} else {
		sm.removeFromResourceSubscriptions(sub.ResourceID, subID)
	}

	// Remove subscription
	delete(sm.subscriptions, subID)
	delete(sm.subscriptionClients, subID)

	slog.Info("Removed subscription", "id", subID)
	return nil
}

// removeFromResourceSubscriptions is a helper to remove subscription from resource map
func (sm *SubscriptionManager) removeFromResourceSubscriptions(resourceID, subID string) {
	resourceSubs := sm.resourceSubscriptions[resourceID]
	for i, id := range resourceSubs {
		if id == subID {
			sm.resourceSubscriptions[resourceID] = append(resourceSubs[:i], resourceSubs[i+1:]...)
			break
		}
	}
	if len(sm.resourceSubscriptions[resourceID]) == 0 {
		delete(sm.resourceSubscriptions, resourceID)
	}
}

// UnsubscribeAll removes all subscriptions for a client
func (sm *SubscriptionManager) UnsubscribeAll(clientID string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	subIDs, exists := sm.clientSubscriptions[clientID]
	if !exists {
		return nil // No subscriptions for this client
	}

	// Make a copy to avoid modification during iteration
	subIDsCopy := make([]string, len(subIDs))
	copy(subIDsCopy, subIDs)

	for _, subID := range subIDsCopy {
		sub := sm.subscriptions[subID]
		if sub != nil {
			if sub.Type == SubscribeToMultiple {
				for _, resourceID := range sub.ResourceIDs {
					sm.removeFromResourceSubscriptions(resourceID, subID)
				}
			} else {
				sm.removeFromResourceSubscriptions(sub.ResourceID, subID)
			}
		}
		delete(sm.subscriptions, subID)
		delete(sm.subscriptionClients, subID)
	}

	delete(sm.clientSubscriptions, clientID)

	slog.Info("Removed all subscriptions for client ( subscriptions)", "id", clientID, "id", len(subIDsCopy))
	return nil
}

// GetSubscribersForResource gets all clients subscribed to a resource
func (sm *SubscriptionManager) GetSubscribersForResource(resourceID string) []*Client {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	subIDs, exists := sm.resourceSubscriptions[resourceID]
	if !exists {
		return nil
	}

	clients := make([]*Client, 0, len(subIDs))
	for _, subID := range subIDs {
		if client, ok := sm.subscriptionClients[subID]; ok {
			clients = append(clients, client)
		}
	}

	return clients
}

// GetClientSubscriptions gets all subscriptions for a client
func (sm *SubscriptionManager) GetClientSubscriptions(clientID string) []*Subscription {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	subIDs, exists := sm.clientSubscriptions[clientID]
	if !exists {
		return nil
	}

	subs := make([]*Subscription, 0, len(subIDs))
	for _, subID := range subIDs {
		if sub, ok := sm.subscriptions[subID]; ok {
			subs = append(subs, sub)
		}
	}

	return subs
}

// UpdateActivity updates the last activity time for a subscription
func (sm *SubscriptionManager) UpdateActivity(subID string) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	if sub, ok := sm.subscriptions[subID]; ok {
		sub.LastActivity = time.Now()
	}
}

// removeSubscription removes a single subscription from all tracking maps.
func (sm *SubscriptionManager) removeSubscription(subID string, sub *Subscription) {
	clientSubs := sm.clientSubscriptions[sub.ClientID]
	for i, id := range clientSubs {
		if id == subID {
			sm.clientSubscriptions[sub.ClientID] = append(clientSubs[:i], clientSubs[i+1:]...)
			break
		}
	}

	if sub.Type == SubscribeToMultiple {
		for _, resourceID := range sub.ResourceIDs {
			sm.removeFromResourceSubscriptions(resourceID, subID)
		}
	} else {
		sm.removeFromResourceSubscriptions(sub.ResourceID, subID)
	}

	delete(sm.subscriptions, subID)
	delete(sm.subscriptionClients, subID)
}

// CleanupStaleSubscriptions removes subscriptions that haven't been active
func (sm *SubscriptionManager) CleanupStaleSubscriptions(timeout time.Duration) int {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	now := time.Now()
	removed := 0

	for subID, sub := range sm.subscriptions {
		if now.Sub(sub.LastActivity) > timeout {
			sm.removeSubscription(subID, sub)
			removed++
		}
	}

	if removed > 0 {
		slog.Info("Cleaned up stale subscriptions", "value", removed)
	}

	return removed
}

// GetStats returns statistics about subscriptions
func (sm *SubscriptionManager) GetStats() map[string]interface{} {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	typeCount := make(map[SubscriptionType]int)
	for _, sub := range sm.subscriptions {
		typeCount[sub.Type]++
	}

	return map[string]interface{}{
		"total_subscriptions":   len(sm.subscriptions),
		"total_clients":         len(sm.clientSubscriptions),
		"total_resources":       len(sm.resourceSubscriptions),
		"subscriptions_by_type": typeCount,
	}
}

// matchesStringList checks if a value is in a string list
func matchesStringList(value string, list []string) bool {
	for _, item := range list {
		if value == item {
			return true
		}
	}
	return false
}

// matchesEventTypeFilter checks if a message event matches the event type filter
func matchesEventTypeFilter(filters map[string]interface{}, message *Message) bool {
	eventTypes, ok := filters["event_types"].([]string)
	if !ok {
		return true
	}
	if message.Event == nil {
		return false
	}
	return matchesStringList(string(message.Event.EventType), eventTypes)
}

// matchesEntityTypeFilter checks if a message event matches the entity type filter
func matchesEntityTypeFilter(filters map[string]interface{}, message *Message) bool {
	entityTypes, ok := filters["entity_types"].([]string)
	if !ok {
		return true
	}
	if message.Event == nil {
		return false
	}
	return matchesStringList(string(message.Event.EntityType), entityTypes)
}

// MatchesFilter checks if a message matches the subscription filters
func (sm *SubscriptionManager) MatchesFilter(sub *Subscription, message *Message) bool {
	if len(sub.Filters) == 0 {
		return true // No filters means match all
	}

	if !matchesEventTypeFilter(sub.Filters, message) {
		return false
	}

	if !matchesEntityTypeFilter(sub.Filters, message) {
		return false
	}

	// Additional custom filters can be added here

	return true
}
