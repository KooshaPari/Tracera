package realtime

import (
	"context"
)

// Event represents a real-time event (INSERT, UPDATE, DELETE).
type Event struct {
	Type      string                 `json:"type"`       // INSERT, UPDATE, DELETE
	Table     string                 `json:"table"`      // Table name
	Schema    string                 `json:"schema"`     // Schema name
	Record    map[string]interface{} `json:"record"`     // New record
	OldRecord map[string]interface{} `json:"old_record"` // Old record (for UPDATE/DELETE)
	Timestamp int64                  `json:"timestamp"`
}

// Subscriber defines the interface for real-time subscriptions (e.g. NATS).
type Subscriber interface {
	Subscribe(ctx context.Context, table string, callback func(*Event) error) (string, error)
	SubscribeWithFilter(ctx context.Context, table, filter string, callback func(*Event) error) (string, error)
	Unsubscribe(ctx context.Context, subscriptionID string) error
	Close() error
}

// Publisher defines the interface for publishing real-time events.
type Publisher interface {
	Publish(ctx context.Context, event *Event) error
	PublishToChannel(ctx context.Context, channel string, event *Event) error
	Close() error
}

// Broadcaster combines Subscriber and Publisher.
type Broadcaster interface {
	Subscriber
	Publisher
}
