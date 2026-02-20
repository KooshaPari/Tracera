// Package realtime provides real-time event broadcasting (e.g. NATS adapter).
package realtime

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
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
			slog.Error("Failed to unmarshal NATS realtime event", "error", err)
			return
		}

		if err := callback(&event); err != nil {
			slog.Error("Error processing realtime event", "error", err)
		}
	})
	if err != nil {
		return "", fmt.Errorf("failed to subscribe to NATS subject %s: %w", subject, err)
	}

	subscriptionID := fmt.Sprintf("nats_sub_%s_%d", table, len(a.subscriptions))
	a.mu.Lock()
	a.subscriptions[subscriptionID] = sub
	a.mu.Unlock()

	slog.Info("Subscribed to NATS realtime table (subject )", "duration", table, "detail", subject)
	return subscriptionID, nil
}

// SubscribeWithFilter subscribes to changes with a filter
func (a *NATSRealtimeAdapter) SubscribeWithFilter(_ context.Context, table, filter string, callback func(*Event) error) (string, error) {
	// NATS doesn't support server-side filtering, so we filter client-side
	subject := "realtime." + table + ".>"

	sub, err := a.conn.Subscribe(subject, func(msg *nats.Msg) {
		var event Event
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			slog.Error("Failed to unmarshal NATS realtime event", "error", err)
			return
		}

		// Note: Filter logic not yet implemented
		// Currently passes through all events
		if err := callback(&event); err != nil {
			slog.Error("Error processing realtime event", "error", err)
		}
	})
	if err != nil {
		return "", fmt.Errorf("failed to subscribe to NATS subject %s: %w", subject, err)
	}

	subscriptionID := fmt.Sprintf("nats_sub_%s_filtered_%d", table, len(a.subscriptions))
	a.mu.Lock()
	a.subscriptions[subscriptionID] = sub
	a.mu.Unlock()

	slog.Info("Subscribed to NATS realtime table with filter (filter )", "duration", table, "detail", filter)
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

	slog.Info("Unsubscribed from NATS realtime", "duration", subscriptionID)
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

	slog.Info("Published NATS realtime event on table", "duration", event.Type, "detail", event.Table)
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

	slog.Info("Published to NATS realtime channel", "duration", channel)
	return nil
}

// Close closes the NATS Realtime adapter
func (a *NATSRealtimeAdapter) Close() error {
	a.mu.Lock()
	defer a.mu.Unlock()

	for _, sub := range a.subscriptions {
		if err := sub.Unsubscribe(); err != nil {
			slog.Error("Error unsubscribing", "error", err)
		}
	}
	a.subscriptions = make(map[string]*nats.Subscription)

	slog.Info("Closing NATS Realtime adapter")
	return nil
}
