package websocket

import (
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	subscriptionActivityDelay   = 10 * time.Millisecond
	subscriptionStaleThreshold  = 10 * time.Minute
	subscriptionCleanupInterval = 5 * time.Minute
)

func TestNewSubscriptionManager(t *testing.T) {
	sm := NewSubscriptionManager()

	require.NotNil(t, sm)
	assert.NotNil(t, sm.subscriptions)
	assert.NotNil(t, sm.clientSubscriptions)
	assert.NotNil(t, sm.resourceSubscriptions)
	assert.NotNil(t, sm.subscriptionClients)
}

func TestSubscribe(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:        "client-1",
		ProjectID: "project-1",
		Send:      make(chan *Message, 256),
	}

	sub, err := sm.Subscribe(client, SubscribeToProject, "project-1", nil)

	require.NoError(t, err)
	require.NotNil(t, sub)
	assert.Equal(t, "client-1", sub.ClientID)
	assert.Equal(t, SubscribeToProject, sub.Type)
	assert.Equal(t, "project-1", sub.ResourceID)

	// Verify subscription was stored
	assert.Equal(t, 1, len(sm.subscriptions))
	assert.Equal(t, 1, len(sm.clientSubscriptions["client-1"]))
	assert.Equal(t, 1, len(sm.resourceSubscriptions["project-1"]))
}

func TestSubscribeMultiple(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	resourceIDs := []string{"entity-1", "entity-2", "entity-3"}
	sub, err := sm.SubscribeMultiple(client, resourceIDs, nil)

	require.NoError(t, err)
	require.NotNil(t, sub)
	assert.Equal(t, SubscribeToMultiple, sub.Type)
	assert.Equal(t, 3, len(sub.ResourceIDs))

	// Verify all resources are subscribed
	for _, resourceID := range resourceIDs {
		assert.Equal(t, 1, len(sm.resourceSubscriptions[resourceID]))
	}
}

func TestUnsubscribe(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	sub, _ := sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)

	// Unsubscribe
	err := sm.Unsubscribe(sub.ID)
	require.NoError(t, err)

	// Verify subscription was removed
	assert.Equal(t, 0, len(sm.subscriptions))
	assert.Equal(t, 0, len(sm.clientSubscriptions["client-1"]))
	assert.Equal(t, 0, len(sm.resourceSubscriptions["entity-1"]))
}

func TestUnsubscribeAll(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	// Create multiple subscriptions
	_, _ = sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)
	_, _ = sm.Subscribe(client, SubscribeToEntity, "entity-2", nil)
	_, _ = sm.Subscribe(client, SubscribeToProject, "project-1", nil)

	// Unsubscribe all
	err := sm.UnsubscribeAll("client-1")
	require.NoError(t, err)

	// Verify all subscriptions were removed
	assert.Equal(t, 0, len(sm.subscriptions))
	assert.Equal(t, 0, len(sm.clientSubscriptions))
	assert.Equal(t, 0, len(sm.resourceSubscriptions))
}

func TestGetSubscribersForResource(t *testing.T) {
	sm := NewSubscriptionManager()

	client1 := &Client{ID: "client-1", Send: make(chan *Message, 256)}
	client2 := &Client{ID: "client-2", Send: make(chan *Message, 256)}
	client3 := &Client{ID: "client-3", Send: make(chan *Message, 256)}

	// Subscribe to same resource
	_, _ = sm.Subscribe(client1, SubscribeToEntity, "entity-1", nil)
	_, _ = sm.Subscribe(client2, SubscribeToEntity, "entity-1", nil)
	_, _ = sm.Subscribe(client3, SubscribeToEntity, "entity-2", nil)

	// Get subscribers for entity-1
	subscribers := sm.GetSubscribersForResource("entity-1")

	assert.Equal(t, 2, len(subscribers))
	assert.Contains(t, []string{subscribers[0].ID, subscribers[1].ID}, "client-1")
	assert.Contains(t, []string{subscribers[0].ID, subscribers[1].ID}, "client-2")
}

func TestGetClientSubscriptions(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	// Create multiple subscriptions
	_, _ = sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)
	_, _ = sm.Subscribe(client, SubscribeToEntity, "entity-2", nil)
	_, _ = sm.Subscribe(client, SubscribeToProject, "project-1", nil)

	// Get client subscriptions
	subs := sm.GetClientSubscriptions("client-1")

	assert.Equal(t, 3, len(subs))
}

func TestUpdateActivity(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	sub, _ := sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)
	originalTime := sub.LastActivity

	// Wait a bit and update
	time.Sleep(subscriptionActivityDelay)
	sm.UpdateActivity(sub.ID)

	// Verify activity was updated
	updatedSub := sm.subscriptions[sub.ID]
	assert.True(t, updatedSub.LastActivity.After(originalTime))
}

func TestCleanupStaleSubscriptions(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	sub, _ := sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)

	// Make subscription stale
	sub.LastActivity = time.Now().Add(-subscriptionStaleThreshold)

	// Cleanup with 5 minute timeout
	removed := sm.CleanupStaleSubscriptions(subscriptionCleanupInterval)

	assert.Equal(t, 1, removed)
	assert.Equal(t, 0, len(sm.subscriptions))
}

func TestSubscriptionFilters(t *testing.T) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	filters := map[string]interface{}{
		"event_types":  []string{"created", "updated"},
		"entity_types": []string{"item"},
	}

	sub, err := sm.Subscribe(client, SubscribeToProject, "project-1", filters)

	require.NoError(t, err)
	assert.NotNil(t, sub.Filters)
	assert.Equal(t, filters, sub.Filters)
}

func TestMatchesFilter(t *testing.T) {
	sm := NewSubscriptionManager()

	for _, tt := range matchFilterCases() {
		t.Run(tt.name, func(t *testing.T) {
			sub := &Subscription{
				Filters: tt.filters,
			}

			result := sm.MatchesFilter(sub, tt.message)
			assert.Equal(t, tt.shouldMatch, result)
		})
	}
}

type matchFilterCase struct {
	name        string
	filters     map[string]interface{}
	message     *Message
	shouldMatch bool
}

func matchFilterCases() []matchFilterCase {
	return []matchFilterCase{
		{
			name:    "No filters - should match",
			filters: nil,
			message: &Message{
				Type: "test",
			},
			shouldMatch: true,
		},
		{
			name: "Event type filter - match",
			filters: map[string]interface{}{
				"event_types": []string{"created", "updated"},
			},
			message: &Message{
				Type: "event",
				Event: &events.Event{
					EventType: events.EventTypeCreated,
				},
			},
			shouldMatch: true,
		},
		{
			name: "Event type filter - no match",
			filters: map[string]interface{}{
				"event_types": []string{"created", "updated"},
			},
			message: &Message{
				Type: "event",
				Event: &events.Event{
					EventType: events.EventTypeDeleted,
				},
			},
			shouldMatch: false,
		},
		{
			name: "Entity type filter - match",
			filters: map[string]interface{}{
				"entity_types": []string{"item"},
			},
			message: &Message{
				Type: "event",
				Event: &events.Event{
					EntityType: events.EntityTypeItem,
				},
			},
			shouldMatch: true,
		},
	}
}

func TestGetStats(t *testing.T) {
	sm := NewSubscriptionManager()

	client1 := &Client{ID: "client-1", Send: make(chan *Message, 256)}
	client2 := &Client{ID: "client-2", Send: make(chan *Message, 256)}

	_, _ = sm.Subscribe(client1, SubscribeToProject, "project-1", nil)
	_, _ = sm.Subscribe(client1, SubscribeToEntity, "entity-1", nil)
	_, _ = sm.Subscribe(client2, SubscribeToProject, "project-1", nil)
	_, _ = sm.SubscribeMultiple(client2, []string{"entity-2", "entity-3"}, nil)

	stats := sm.GetStats()

	assert.Equal(t, 4, stats["total_subscriptions"])
	assert.Equal(t, 2, stats["total_clients"])
	assert.Greater(t, stats["total_resources"], 0)

	typeCount := stats["subscriptions_by_type"].(map[SubscriptionType]int)
	assert.Equal(t, 2, typeCount[SubscribeToProject])
	assert.Equal(t, 1, typeCount[SubscribeToEntity])
	assert.Equal(t, 1, typeCount[SubscribeToMultiple])
}

func BenchmarkSubscribe(b *testing.B) {
	sm := NewSubscriptionManager()
	client := &Client{
		ID:   "client-1",
		Send: make(chan *Message, 256),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)
	}
}

func BenchmarkGetSubscribers(b *testing.B) {
	sm := NewSubscriptionManager()

	// Setup: create many subscriptions
	for i := 0; i < 1000; i++ {
		client := &Client{
			ID:   string(rune('a' + i)),
			Send: make(chan *Message, 256),
		}
		_, _ = sm.Subscribe(client, SubscribeToEntity, "entity-1", nil)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		sm.GetSubscribersForResource("entity-1")
	}
}
