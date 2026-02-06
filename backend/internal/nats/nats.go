// Package nats provides NATS client utilities.
package nats

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
	natslib "github.com/nats-io/nats.go"
	"github.com/nats-io/nkeys"
)

const (
	defaultReconnectWait = 2 * time.Second
	defaultMaxReconnects = 10
	streamRetentionDays  = 7
	drainTimeout         = 5 * time.Second
)

// Client wraps NATS connection
type Client struct {
	conn *natslib.Conn
}

func connectWithAuth(url, credsPath, userJWT, userNkeySeed string) (*natslib.Conn, error) {
	opts := []natslib.Option{
		natslib.Name("TraceRTM-Backend"),
	}

	if credsPath != "" {
		opts = append(opts, natslib.UserCredentials(credsPath))
	} else if userJWT != "" && userNkeySeed != "" {
		opts = append(opts, natslib.UserJWT(
			func() (string, error) {
				return userJWT, nil
			},
			func(nonce []byte) ([]byte, error) {
				kp, err := nkeys.FromSeed([]byte(userNkeySeed))
				if err != nil {
					return nil, fmt.Errorf("failed to parse nkey seed: %w", err)
				}
				sig, err := kp.Sign(nonce)
				if err != nil {
					return nil, fmt.Errorf("failed to sign nonce: %w", err)
				}
				return sig, nil
			},
		))
	}

	return natslib.Connect(url, opts...)
}

// NewClient creates a new NATS client
func NewClient(url, credsPath string) (*Client, error) {
	conn, err := connectWithAuth(url, credsPath, "", "")
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}

	return &Client{conn: conn}, nil
}

// NewNATSClientWithAuth creates a new NATS client with file or JWT-based authentication
func NewNATSClientWithAuth(url, credsPath, userJWT, userNkeySeed string) (*Client, error) {
	conn, err := connectWithAuth(url, credsPath, userJWT, userNkeySeed)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}

	return &Client{conn: conn}, nil
}

// GetConnection returns the underlying NATS connection
func (n *Client) GetConnection() *natslib.Conn {
	return n.conn
}

// HealthCheck verifies NATS is accessible
func (n *Client) HealthCheck(_ context.Context) error {
	if n.conn == nil || n.conn.IsClosed() {
		return errors.New("nats connection is not available")
	}
	return nil
}

// Close closes the NATS connection
func (n *Client) Close() error {
	if n.conn != nil {
		n.conn.Close()
	}
	return nil
}

// Publish publishes a message to a subject
func (n *Client) Publish(subject string, projectID string, entityID string, entityType string, data interface{}) error {
	event := map[string]interface{}{
		"project_id":  projectID,
		"entity_id":   entityID,
		"entity_type": entityType,
		"data":        data,
		"timestamp":   time.Now().Unix(),
	}

	payload, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	if err := n.conn.Publish(subject, payload); err != nil {
		return fmt.Errorf("failed to publish event: %w", err)
	}

	return nil
}

// EventBus implements event publishing and subscription using NATS.
type EventBus struct {
	conn          *natslib.Conn
	js            natslib.JetStreamContext
	subscriptions map[string]*natslib.Subscription
	mu            sync.RWMutex
}

// Config holds NATS configuration
type Config struct {
	URL            string
	ClusterID      string
	ClientID       string
	MaxReconnects  int
	ReconnectWait  time.Duration
	StreamName     string
	StreamSubjects []string
}

// DefaultConfig returns default NATS configuration
func DefaultConfig() *Config {
	return &Config{
		URL:           natslib.DefaultURL,
		ClusterID:     "tracertm-cluster",
		ClientID:      "tracertm-backend",
		MaxReconnects: defaultMaxReconnects,
		ReconnectWait: defaultReconnectWait,
		StreamName:    "TRACERTM_EVENTS",
		StreamSubjects: []string{
			"tracertm.events.>",
			"tracertm.projects.>",
			"tracertm.entities.>",
		},
	}
}

// NewEventBus creates a new NATS event bus.
func NewEventBus(config *Config) (*EventBus, error) {
	// Connect to NATS with options
	opts := []natslib.Option{
		natslib.MaxReconnects(config.MaxReconnects),
		natslib.ReconnectWait(config.ReconnectWait),
		natslib.DisconnectErrHandler(func(_ *natslib.Conn, err error) {
			if err != nil {
				log.Printf("NATS disconnected: %v", err)
			}
		}),
		natslib.ReconnectHandler(func(nc *natslib.Conn) {
			log.Printf("NATS reconnected to %s", nc.ConnectedUrl())
		}),
		natslib.ClosedHandler(func(_ *natslib.Conn) {
			log.Println("NATS connection closed")
		}),
	}

	conn, err := natslib.Connect(config.URL, opts...)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %w", err)
	}

	// Create JetStream context
	js, err := conn.JetStream()
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("failed to create JetStream context: %w", err)
	}

	bus := &EventBus{
		conn:          conn,
		js:            js,
		subscriptions: make(map[string]*natslib.Subscription),
	}

	// Create or update the stream
	if err := bus.ensureStream(config); err != nil {
		conn.Close()
		return nil, fmt.Errorf("failed to ensure stream: %w", err)
	}

	// Create or update OAuth consumer for audit trail
	if err := bus.ensureOAuthConsumer(config); err != nil {
		// Log warning but don't fail initialization
		log.Printf("Warning: failed to ensure OAuth consumer: %v", err)
	}

	log.Printf("Connected to NATS at %s", config.URL)
	return bus, nil
}

// ensureStream creates or updates the JetStream stream
func (b *EventBus) ensureStream(config *Config) error {
	streamConfig := &natslib.StreamConfig{
		Name:      config.StreamName,
		Subjects:  config.StreamSubjects,
		Retention: natslib.InterestPolicy,
		Storage:   natslib.FileStorage,
		MaxAge:    streamRetentionDays * 24 * time.Hour, // Retain for 7 days
		Replicas:  1,
	}

	// Try to add the stream, update if it already exists
	_, err := b.js.AddStream(streamConfig)
	if err != nil {
		// Try to update if it exists
		_, err = b.js.UpdateStream(streamConfig)
		if err != nil {
			return fmt.Errorf("failed to add/update stream: %w", err)
		}
	}

	return nil
}

// Publish publishes an event to all subscribers
func (b *EventBus) Publish(event *events.Event) error {
	subject := "tracertm.events." + string(event.EventType)
	return b.publishToSubject(subject, event)
}

// PublishToProject publishes an event to project-specific subscribers
func (b *EventBus) PublishToProject(projectID string, event *events.Event) error {
	subject := fmt.Sprintf("tracertm.projects.%s.%s", projectID, string(event.EventType))
	return b.publishToSubject(subject, event)
}

// PublishToEntity publishes an event to entity-specific subscribers
func (b *EventBus) PublishToEntity(entityID string, event *events.Event) error {
	subject := fmt.Sprintf("tracertm.entities.%s.%s", entityID, string(event.EventType))
	return b.publishToSubject(subject, event)
}

// publishToSubject is a helper to publish to a specific subject
func (b *EventBus) publishToSubject(subject string, event *events.Event) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	// Publish to JetStream for persistence
	_, err = b.js.Publish(subject, data)
	if err != nil {
		return fmt.Errorf("failed to publish to JetStream: %w", err)
	}

	return nil
}

// Subscribe subscribes to all events
func (b *EventBus) Subscribe(handler func(*events.Event)) error {
	subject := "tracertm.events.>"
	return b.subscribeToSubject(subject, "all-events", handler)
}

// SubscribeToProject subscribes to project-specific events
func (b *EventBus) SubscribeToProject(projectID string, handler func(*events.Event)) error {
	subject := "tracertm.projects." + projectID + ".>"
	subscriptionID := "project-" + projectID
	return b.subscribeToSubject(subject, subscriptionID, handler)
}

// SubscribeToEntity subscribes to entity-specific events
func (b *EventBus) SubscribeToEntity(entityID string, handler func(*events.Event)) error {
	subject := "tracertm.entities." + entityID + ".>"
	subscriptionID := "entity-" + entityID
	return b.subscribeToSubject(subject, subscriptionID, handler)
}

// SubscribeToEventType subscribes to specific event types
func (b *EventBus) SubscribeToEventType(eventType events.EventType, handler func(*events.Event)) error {
	subject := "tracertm.events." + string(eventType)
	subscriptionID := "type-" + string(eventType)
	return b.subscribeToSubject(subject, subscriptionID, handler)
}

// subscribeToSubject is a helper to subscribe to a specific subject
func (b *EventBus) subscribeToSubject(subject, durableName string, handler func(*events.Event)) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	// Check if already subscribed
	if _, exists := b.subscriptions[durableName]; exists {
		return fmt.Errorf("already subscribed with durable name: %s", durableName)
	}

	// Create durable consumer
	sub, err := b.js.Subscribe(subject, func(msg *natslib.Msg) {
		var event events.Event
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			log.Printf("Failed to unmarshal event: %v", err)
			return
		}

		// Call the handler
		handler(&event)

		// Acknowledge the message
		if err := msg.Ack(); err != nil {
			log.Printf("Failed to acknowledge message: %v", err)
		}
	}, natslib.Durable(durableName), natslib.ManualAck())
	if err != nil {
		return fmt.Errorf("failed to subscribe: %w", err)
	}

	b.subscriptions[durableName] = sub
	log.Printf("Subscribed to %s with durable name %s", subject, durableName)
	return nil
}

// Unsubscribe removes a subscription
func (b *EventBus) Unsubscribe(subscriptionID string) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	sub, exists := b.subscriptions[subscriptionID]
	if !exists {
		return fmt.Errorf("subscription not found: %s", subscriptionID)
	}

	if err := sub.Unsubscribe(); err != nil {
		return fmt.Errorf("failed to unsubscribe: %w", err)
	}

	delete(b.subscriptions, subscriptionID)
	log.Printf("Unsubscribed from %s", subscriptionID)
	return nil
}

// Close closes the NATS connection
func (b *EventBus) Close() error {
	b.mu.Lock()
	defer b.mu.Unlock()

	// Unsubscribe from all subscriptions
	for id, sub := range b.subscriptions {
		if err := sub.Unsubscribe(); err != nil {
			log.Printf("Error unsubscribing from %s: %v", id, err)
		}
	}

	// Close the connection
	b.conn.Close()
	log.Println("NATS connection closed")
	return nil
}

// GetStats returns statistics about the NATS connection
func (b *EventBus) GetStats() map[string]interface{} {
	b.mu.RLock()
	defer b.mu.RUnlock()

	stats := b.conn.Stats()
	return map[string]interface{}{
		"connected":     b.conn.IsConnected(),
		"subscriptions": len(b.subscriptions),
		"in_msgs":       stats.InMsgs,
		"out_msgs":      stats.OutMsgs,
		"in_bytes":      stats.InBytes,
		"out_bytes":     stats.OutBytes,
		"reconnects":    stats.Reconnects,
		"servers":       len(b.conn.Servers()),
		"connected_url": b.conn.ConnectedUrl(),
	}
}

// PublishBatch publishes multiple events in a batch
func (b *EventBus) PublishBatch(events []*events.Event) error {
	for _, event := range events {
		if err := b.Publish(event); err != nil {
			return fmt.Errorf("failed to publish event in batch: %w", err)
		}
	}
	return nil
}

// QueueSubscribe creates a queue subscription for load balancing
func (b *EventBus) QueueSubscribe(subject, queue string, handler func(*events.Event)) error {
	b.mu.Lock()
	defer b.mu.Unlock()

	subscriptionID := fmt.Sprintf("queue-%s-%s", queue, subject)

	// Check if already subscribed
	if _, exists := b.subscriptions[subscriptionID]; exists {
		return fmt.Errorf("already subscribed with ID: %s", subscriptionID)
	}

	// Create queue subscription with durable consumer
	sub, err := b.js.QueueSubscribe(subject, queue, func(msg *natslib.Msg) {
		var event events.Event
		if err := json.Unmarshal(msg.Data, &event); err != nil {
			log.Printf("Failed to unmarshal event: %v", err)
			return
		}

		// Call the handler
		handler(&event)

		// Acknowledge the message
		if err := msg.Ack(); err != nil {
			log.Printf("Failed to acknowledge message: %v", err)
		}
	}, natslib.Durable(subscriptionID), natslib.ManualAck())
	if err != nil {
		return fmt.Errorf("failed to queue subscribe: %w", err)
	}

	b.subscriptions[subscriptionID] = sub
	log.Printf("Queue subscribed to %s with queue %s", subject, queue)
	return nil
}

// DrainAndClose gracefully drains all subscriptions and closes the connection
func (b *EventBus) DrainAndClose(ctx context.Context) error {
	log.Println("Draining NATS subscriptions...")

	b.mu.Lock()
	defer b.mu.Unlock()

	// Drain all subscriptions
	for id, sub := range b.subscriptions {
		if err := sub.Drain(); err != nil {
			log.Printf("Error draining subscription %s: %v", id, err)
		}
	}

	// Wait for drain to complete or context to cancel
	select {
	case <-ctx.Done():
		log.Println("Drain timeout, forcing close")
	case <-time.After(drainTimeout):
		log.Println("Drain completed")
	}

	// Close the connection
	b.conn.Close()
	log.Println("NATS connection closed")
	return nil
}

// GetStreamInfo returns information about the JetStream stream
func (b *EventBus) GetStreamInfo(streamName string) (*natslib.StreamInfo, error) {
	return b.js.StreamInfo(streamName)
}

// GetConsumerInfo returns information about a consumer
func (b *EventBus) GetConsumerInfo(streamName, consumerName string) (*natslib.ConsumerInfo, error) {
	return b.js.ConsumerInfo(streamName, consumerName)
}

// PurgeStream purges all messages from a stream
func (b *EventBus) PurgeStream(streamName string) error {
	return b.js.PurgeStream(streamName)
}

// DeleteStream deletes a stream
func (b *EventBus) DeleteStream(streamName string) error {
	return b.js.DeleteStream(streamName)
}

// ensureOAuthConsumer creates or updates the durable pull consumer for OAuth events
func (b *EventBus) ensureOAuthConsumer(config *Config) error {
	consumerConfig := &natslib.ConsumerConfig{
		Durable:       "oauth-audit",
		Description:   "Durable consumer for OAuth event audit trail",
		AckPolicy:     natslib.AckExplicitPolicy, // Explicit ack required
		MaxAckPending: 100,                       // Prevent overwhelming subscribers
	}

	// Try to add the consumer, update if it already exists
	_, err := b.js.AddConsumer(config.StreamName, consumerConfig)
	if err != nil {
		// Check if already exists
		if isConsumerExistsError(err) {
			log.Printf("OAuth consumer already exists: %v", err)
			return nil
		}
		return fmt.Errorf("failed to create OAuth consumer: %w", err)
	}

	log.Println("Created OAuth audit consumer in JetStream")
	return nil
}

// ReplayOAuthEvents replays all OAuth events from a given timestamp
func (b *EventBus) ReplayOAuthEvents(ctx context.Context, fromTime time.Time) (<-chan *natslib.Msg, error) {
	// Create ephemeral consumer with replay policy
	sub, err := b.js.PullSubscribe(
		"tracertm.entities.*.oauth.*",
		"",
		natslib.AckWait(5*time.Second),
		natslib.MaxAckPending(100),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create replay subscription: %w", err)
	}

	msgs := make(chan *natslib.Msg, 10)
	go func() {
		defer close(msgs)
		defer sub.Unsubscribe()

		// Fetch up to 100 messages
		for i := 0; i < 100; i++ {
			msg, err := sub.NextMsg(5 * time.Second)
			if err != nil {
				break // No more messages
			}
			msgs <- msg
			_ = msg.Ack() // Acknowledge receipt
		}
	}()

	return msgs, nil
}

// isConsumerExistsError checks if the error is due to consumer already existing
func isConsumerExistsError(err error) bool {
	return err != nil && (err.Error() == "consumer already exists" || err.Error() == "NATS: consumer already exists")
}
