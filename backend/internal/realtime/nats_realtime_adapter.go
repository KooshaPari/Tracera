// Package realtime provides real-time event broadcasting (e.g. NATS adapter).
package realtime

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"

	"github.com/nats-io/nats.go"
)

// NATSRealtimeAdapter implements Broadcaster using NATS.
type NATSRealtimeAdapter struct {
	conn          *nats.Conn
	mu            sync.RWMutex
	subscriptions map[string]*nats.Subscription
}

// NewNATSRealtimeAdapter creates a new NATS Realtime adapter
func NewNATSRealtimeAdapter(conn *nats.Conn) *NATSRealtimeAdapter {
	return &NATSRealtimeAdapter{
		conn:          conn,
		subscriptions: make(map[string]*nats.Subscription),
	}
}

// Subscribe subscribes to changes on a table
func (a *NATSRealtimeAdapter) Subscribe(_ context.Context, table string, callback func(*Event) error) (string, error) {
	subject := "realtime." + table + ".>"

	sub, err := a.conn.Subscribe(subject, func(msg *nats.Msg) {
		var event Event
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			log.Printf("Failed to unmarshal NATS realtime event: %v", err)
			return
		}

		if err := callback(&event); err != nil {
			log.Printf("Error processing realtime event: %v", err)
		}
	})
	if err != nil {
		return "", fmt.Errorf("failed to subscribe to NATS subject %s: %w", subject, err)
	}

	subscriptionID := fmt.Sprintf("nats_sub_%s_%d", table, len(a.subscriptions))
	a.mu.Lock()
	a.subscriptions[subscriptionID] = sub
	a.mu.Unlock()

	log.Printf("Subscribed to NATS realtime table: %s (subject: %s)", table, subject)
	return subscriptionID, nil
}

// SubscribeWithFilter subscribes to changes with a filter
func (a *NATSRealtimeAdapter) SubscribeWithFilter(_ context.Context, table, filter string, callback func(*Event) error) (string, error) {
	// NATS doesn't support server-side filtering, so we filter client-side
	subject := "realtime." + table + ".>"

	sub, err := a.conn.Subscribe(subject, func(msg *nats.Msg) {
		var event Event
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			log.Printf("Failed to unmarshal NATS realtime event: %v", err)
			return
		}

		// TODO: Apply filter logic here
		// For now, just pass through
		if err := callback(&event); err != nil {
			log.Printf("Error processing realtime event: %v", err)
		}
	})
	if err != nil {
		return "", fmt.Errorf("failed to subscribe to NATS subject %s: %w", subject, err)
	}

	subscriptionID := fmt.Sprintf("nats_sub_%s_filtered_%d", table, len(a.subscriptions))
	a.mu.Lock()
	a.subscriptions[subscriptionID] = sub
	a.mu.Unlock()

	log.Printf("Subscribed to NATS realtime table with filter: %s (filter: %s)", table, filter)
	return subscriptionID, nil
}

// Unsubscribe unsubscribes from a subscription
func (a *NATSRealtimeAdapter) Unsubscribe(_ context.Context, subscriptionID string) error {
	a.mu.Lock()
	sub, ok := a.subscriptions[subscriptionID]
	if !ok {
		a.mu.Unlock()
		return fmt.Errorf("subscription not found: %s", subscriptionID)
	}
	delete(a.subscriptions, subscriptionID)
	a.mu.Unlock()

	if err := sub.Unsubscribe(); err != nil {
		return fmt.Errorf("failed to unsubscribe: %w", err)
	}

	log.Printf("Unsubscribed from NATS realtime: %s", subscriptionID)
	return nil
}

// Publish publishes a real-time event
func (a *NATSRealtimeAdapter) Publish(_ context.Context, event *Event) error {
	subject := "realtime." + event.Table + "." + event.Type

	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	if err := a.conn.Publish(subject, data); err != nil {
		return fmt.Errorf("failed to publish to NATS: %w", err)
	}

	log.Printf("Published NATS realtime event: %s on table %s", event.Type, event.Table)
	return nil
}

// PublishToChannel publishes to a specific channel
func (a *NATSRealtimeAdapter) PublishToChannel(_ context.Context, channel string, event *Event) error {
	subject := "realtime." + channel

	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	if err := a.conn.Publish(subject, data); err != nil {
		return fmt.Errorf("failed to publish to NATS channel: %w", err)
	}

	log.Printf("Published to NATS realtime channel: %s", channel)
	return nil
}

// Close closes the NATS Realtime adapter
func (a *NATSRealtimeAdapter) Close() error {
	a.mu.Lock()
	defer a.mu.Unlock()

	for _, sub := range a.subscriptions {
		if err := sub.Unsubscribe(); err != nil {
			log.Printf("Error unsubscribing: %v", err)
		}
	}
	a.subscriptions = make(map[string]*nats.Subscription)

	log.Println("Closing NATS Realtime adapter")
	return nil
}
