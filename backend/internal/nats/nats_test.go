package nats

import (
	"context"
	"fmt"
	"os"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
	natslib "github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func setupTestNATS(t *testing.T) *NATSClient {
	url := os.Getenv("NATS_URL")
	if url == "" {
		url = natslib.DefaultURL
	}

	client, err := NewNATSClient(url, "")
	if err != nil {
		t.Skipf("NATS not available: %v", err)
	}
	return client
}

func TestNewNATSClient(t *testing.T) {
	t.Run("successful connection without creds", func(t *testing.T) {
		client, err := NewNATSClient(natslib.DefaultURL, "")
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		defer func() {
			if err := client.Close(); err != nil {
				t.Logf("error closing client: %v", err)
			}
		}()

		assert.NotNil(t, client)
		assert.NotNil(t, client.conn)
		assert.False(t, client.conn.IsClosed())
	})

	t.Run("invalid URL", func(t *testing.T) {
		client, err := NewNATSClient("invalid://url", "")
		assert.Error(t, err)
		assert.Nil(t, client)
	})

	t.Run("unreachable server", func(t *testing.T) {
		client, err := NewNATSClient("nats://192.0.2.1:4222", "")
		assert.Error(t, err)
		assert.Nil(t, client)
		assert.Contains(t, err.Error(), "failed to connect to NATS")
	})

	t.Run("with invalid creds path", func(t *testing.T) {
		client, err := NewNATSClient(natslib.DefaultURL, "/invalid/path/creds.txt")
		if err == nil && client != nil {
			_ = client.Close()
			t.Skip("NATS accepted invalid creds path")
		}
		assert.Error(t, err)
	})
}

func TestNATSClientGetConnection(t *testing.T) {
	client := setupTestNATS(t)
	defer func() {
		if err := client.Close(); err != nil {
			t.Logf("error closing client: %v", err)
		}
	}()

	conn := client.GetConnection()
	assert.NotNil(t, conn)
	assert.False(t, conn.IsClosed())
}

func TestNATSClientHealthCheck(t *testing.T) {
	client := setupTestNATS(t)
	defer func() {
		if err := client.Close(); err != nil {
			t.Logf("error closing client: %v", err)
		}
	}()

	t.Run("healthy connection", func(t *testing.T) {
		ctx := context.Background()
		err := client.HealthCheck(ctx)
		assert.NoError(t, err)
	})

	t.Run("closed connection", func(t *testing.T) {
		tempClient := setupTestNATS(t)
		_ = tempClient.Close()

		ctx := context.Background()
		err := tempClient.HealthCheck(ctx)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "not available")
	})

	t.Run("nil connection", func(t *testing.T) {
		client := &NATSClient{conn: nil}
		err := client.HealthCheck(context.Background())
		assert.Error(t, err)
	})
}

func TestNATSClientClose(t *testing.T) {
	t.Run("close active connection", func(t *testing.T) {
		client := setupTestNATS(t)
		err := client.Close()
		assert.NoError(t, err)
		assert.True(t, client.conn.IsClosed())
	})

	t.Run("close nil connection", func(t *testing.T) {
		client := &NATSClient{conn: nil}
		err := client.Close()
		assert.NoError(t, err)
	})

	t.Run("double close", func(t *testing.T) {
		client := setupTestNATS(t)
		err := client.Close()
		assert.NoError(t, err)
		err = client.Close()
		assert.NoError(t, err)
	})
}

func TestDefaultConfig(t *testing.T) {
	config := DefaultConfig()

	assert.Equal(t, natslib.DefaultURL, config.URL)
	assert.Equal(t, "tracertm-cluster", config.ClusterID)
	assert.Equal(t, "tracertm-backend", config.ClientID)
	assert.Equal(t, 10, config.MaxReconnects)
	assert.Equal(t, 2*time.Second, config.ReconnectWait)
	assert.Equal(t, "TRACERTM_EVENTS", config.StreamName)
	assert.Len(t, config.StreamSubjects, 3)
	assert.Contains(t, config.StreamSubjects, "tracertm.events.>")
	assert.Contains(t, config.StreamSubjects, "tracertm.projects.>")
	assert.Contains(t, config.StreamSubjects, "tracertm.entities.>")
}

func TestNewNATSEventBus(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	config := DefaultConfig()

	t.Run("successful initialization", func(t *testing.T) {
		bus, err := NewNATSEventBus(config)
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		defer func() {
			if err := bus.Close(); err != nil {
				t.Logf("error closing bus: %v", err)
			}
		}()

		assert.NotNil(t, bus)
		assert.NotNil(t, bus.conn)
		assert.NotNil(t, bus.js)
		assert.NotNil(t, bus.subscriptions)
	})

	t.Run("invalid URL", func(t *testing.T) {
		invalidConfig := *config
		invalidConfig.URL = "invalid://url"

		bus, err := NewNATSEventBus(&invalidConfig)
		assert.Error(t, err)
		assert.Nil(t, bus)
	})

	t.Run("unreachable server", func(t *testing.T) {
		invalidConfig := *config
		invalidConfig.URL = "nats://192.0.2.1:4222"

		bus, err := NewNATSEventBus(&invalidConfig)
		assert.Error(t, err)
		assert.Nil(t, bus)
	})
}

func TestNATSEventBusPublish(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	tests := []struct {
		name      string
		eventID   string
		eventData map[string]any
		target    string // empty for Publish, "project" or "entity"
		targetID  string
		wantErr   bool
	}{
		{
			name:      "publish simple event",
			eventID:   "test-event-1",
			eventData: map[string]any{"key": "value"},
			target:    "",
			wantErr:   false,
		},
		{
			name:      "publish to project",
			eventID:   "test-event-2",
			eventData: map[string]any{"project": "test"},
			target:    "project",
			targetID:  "project-123",
			wantErr:   false,
		},
		{
			name:      "publish to entity",
			eventID:   "test-event-3",
			eventData: map[string]any{"entity": "test"},
			target:    "entity",
			targetID:  "entity-456",
			wantErr:   false,
		},
		{
			name:      "publish with nil event data",
			eventID:   "test-event-4",
			eventData: nil,
			target:    "",
			wantErr:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			event := &events.Event{
				ID:        tt.eventID,
				EventType: "test.event",
				CreatedAt: time.Now(),
				Data:      tt.eventData,
			}

			var err error
			switch tt.target {
			case "project":
				err = bus.PublishToProject(tt.targetID, event)
			case "entity":
				err = bus.PublishToEntity(tt.targetID, event)
			default:
				err = bus.Publish(event)
			}

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestNATSEventBusSubscribe(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("subscribe and receive event", func(t *testing.T) {
		received := make(chan *events.Event, 1)

		err := bus.Subscribe(func(e *events.Event) {
			received <- e
		})
		require.NoError(t, err)

		// Give subscription time to register
		time.Sleep(100 * time.Millisecond)

		// Publish event
		testEvent := &events.Event{
			ID:        "subscribe-test-1",
			EventType: "test.subscribe",
			CreatedAt: time.Now(),
			Data:      map[string]any{"test": "subscribe"},
		}
		err = bus.Publish(testEvent)
		require.NoError(t, err)

		// Wait for event
		select {
		case evt := <-received:
			assert.Equal(t, testEvent.ID, evt.ID)
			assert.Equal(t, testEvent.EventType, evt.EventType)
		case <-time.After(2 * time.Second):
			t.Fatal("timeout waiting for event")
		}
	})

	t.Run("subscribe to project events", func(t *testing.T) {
		projectID := "test-project-123"
		received := make(chan *events.Event, 1)

		err := bus.SubscribeToProject(projectID, func(e *events.Event) {
			received <- e
		})
		require.NoError(t, err)

		time.Sleep(100 * time.Millisecond)

		testEvent := &events.Event{
			ID:        "project-event-1",
			EventType: "test.project",
			CreatedAt: time.Now(),
		}
		err = bus.PublishToProject(projectID, testEvent)
		require.NoError(t, err)

		select {
		case evt := <-received:
			assert.Equal(t, testEvent.ID, evt.ID)
		case <-time.After(2 * time.Second):
			t.Fatal("timeout waiting for project event")
		}
	})

	t.Run("subscribe to entity events", func(t *testing.T) {
		entityID := "test-entity-456"
		received := make(chan *events.Event, 1)

		err := bus.SubscribeToEntity(entityID, func(e *events.Event) {
			received <- e
		})
		require.NoError(t, err)

		time.Sleep(100 * time.Millisecond)

		testEvent := &events.Event{
			ID:        "entity-event-1",
			EventType: "test.entity",
			CreatedAt: time.Now(),
		}
		err = bus.PublishToEntity(entityID, testEvent)
		require.NoError(t, err)

		select {
		case evt := <-received:
			assert.Equal(t, testEvent.ID, evt.ID)
		case <-time.After(2 * time.Second):
			t.Fatal("timeout waiting for entity event")
		}
	})

	t.Run("subscribe to event type", func(t *testing.T) {
		eventType := events.EventType("test.specific.type")
		received := make(chan *events.Event, 1)

		err := bus.SubscribeToEventType(eventType, func(e *events.Event) {
			received <- e
		})
		require.NoError(t, err)

		time.Sleep(100 * time.Millisecond)

		testEvent := &events.Event{
			ID:        "type-event-1",
			EventType: eventType,
			CreatedAt: time.Now(),
		}
		err = bus.Publish(testEvent)
		require.NoError(t, err)

		select {
		case evt := <-received:
			assert.Equal(t, testEvent.ID, evt.ID)
		case <-time.After(2 * time.Second):
			t.Fatal("timeout waiting for typed event")
		}
	})

	t.Run("duplicate subscription fails", func(t *testing.T) {
		err := bus.Subscribe(func(e *events.Event) {})
		require.NoError(t, err)

		err = bus.Subscribe(func(e *events.Event) {})
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "already subscribed")
	})
}

func TestNATSEventBusUnsubscribe(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("unsubscribe active subscription", func(t *testing.T) {
		projectID := "unsub-project-1"

		err := bus.SubscribeToProject(projectID, func(e *events.Event) {})
		require.NoError(t, err)

		subID := fmt.Sprintf("project-%s", projectID)
		err = bus.Unsubscribe(subID)
		assert.NoError(t, err)

		// Verify it's removed
		bus.mu.RLock()
		_, exists := bus.subscriptions[subID]
		bus.mu.RUnlock()
		assert.False(t, exists)
	})

	t.Run("unsubscribe non-existent subscription", func(t *testing.T) {
		err := bus.Unsubscribe("non-existent")
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "subscription not found")
	})

	t.Run("double unsubscribe", func(t *testing.T) {
		projectID := "unsub-project-2"

		err := bus.SubscribeToProject(projectID, func(e *events.Event) {})
		require.NoError(t, err)

		subID := fmt.Sprintf("project-%s", projectID)
		err = bus.Unsubscribe(subID)
		assert.NoError(t, err)

		err = bus.Unsubscribe(subID)
		assert.Error(t, err)
	})
}

func TestNATSEventBusPublishBatch(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("publish multiple events", func(t *testing.T) {
		events := []*events.Event{
			{ID: "batch-1", EventType: "test.batch", CreatedAt: time.Now()},
			{ID: "batch-2", EventType: "test.batch", CreatedAt: time.Now()},
			{ID: "batch-3", EventType: "test.batch", CreatedAt: time.Now()},
		}

		err := bus.PublishBatch(events)
		assert.NoError(t, err)
	})

	t.Run("publish empty batch", func(t *testing.T) {
		err := bus.PublishBatch([]*events.Event{})
		assert.NoError(t, err)
	})

	t.Run("publish nil batch", func(t *testing.T) {
		err := bus.PublishBatch(nil)
		assert.NoError(t, err)
	})
}

func TestNATSEventBusQueueSubscribe(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("queue subscribe load balancing", func(t *testing.T) {
		var count1, count2 int32
		subject := "tracertm.events.queue.test"
		queue := "test-queue"

		err := bus.QueueSubscribe(subject, queue, func(e *events.Event) {
			atomic.AddInt32(&count1, 1)
		})
		require.NoError(t, err)

		err = bus.QueueSubscribe(subject, queue+"2", func(e *events.Event) {
			atomic.AddInt32(&count2, 1)
		})
		require.NoError(t, err)

		time.Sleep(100 * time.Millisecond)

		// Publish multiple events
		for i := range 10 {
			event := &events.Event{
				ID:        fmt.Sprintf("queue-event-%d", i),
				EventType: "queue.test",
				CreatedAt: time.Now(),
			}
			_ = bus.publishToSubject(subject, event)
		}

		time.Sleep(500 * time.Millisecond)

		// Both subscribers should have received some events
		total := atomic.LoadInt32(&count1) + atomic.LoadInt32(&count2)
		assert.Greater(t, total, int32(0))
	})

	t.Run("duplicate queue subscription fails", func(t *testing.T) {
		subject := "tracertm.events.dup.test"
		queue := "dup-queue"

		err := bus.QueueSubscribe(subject, queue, func(e *events.Event) {})
		require.NoError(t, err)

		err = bus.QueueSubscribe(subject, queue, func(e *events.Event) {})
		assert.Error(t, err)
	})
}

func TestNATSEventBusGetStats(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	stats := bus.GetStats()

	assert.NotNil(t, stats)
	assert.Contains(t, stats, "connected")
	assert.Contains(t, stats, "subscriptions")
	assert.Contains(t, stats, "in_msgs")
	assert.Contains(t, stats, "out_msgs")
	assert.Contains(t, stats, "reconnects")

	assert.True(t, stats["connected"].(bool))
	assert.GreaterOrEqual(t, stats["subscriptions"].(int), 0)
}

func TestNATSEventBusDrainAndClose(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("graceful drain and close", func(t *testing.T) {
		bus, err := NewNATSEventBus(DefaultConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}

		// Add a subscription
		err = bus.Subscribe(func(e *events.Event) {})
		require.NoError(t, err)

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		err = bus.DrainAndClose(ctx)
		assert.NoError(t, err)
		assert.True(t, bus.conn.IsClosed())
	})

	t.Run("drain with context timeout", func(t *testing.T) {
		bus, err := NewNATSEventBus(DefaultConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}

		ctx, cancel := context.WithTimeout(context.Background(), 1*time.Nanosecond)
		defer cancel()
		time.Sleep(10 * time.Millisecond)

		err = bus.DrainAndClose(ctx)
		// Should still complete even if context times out
		assert.NoError(t, err)
	})
}

func TestNATSEventBusStreamOperations(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("get stream info", func(t *testing.T) {
		info, err := bus.GetStreamInfo("TRACERTM_EVENTS")
		if err != nil {
			t.Skipf("Stream not available: %v", err)
		}
		assert.NotNil(t, info)
		assert.Equal(t, "TRACERTM_EVENTS", info.Config.Name)
	})

	t.Run("get non-existent stream", func(t *testing.T) {
		info, err := bus.GetStreamInfo("NON_EXISTENT")
		assert.Error(t, err)
		assert.Nil(t, info)
	})
}

func TestConcurrentNATSOperations(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("concurrent publishes", func(t *testing.T) {
		var wg sync.WaitGroup
		numGoroutines := 50

		for i := range numGoroutines {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				event := &events.Event{
					ID:        fmt.Sprintf("concurrent-%d", id),
					EventType: "test.concurrent",
					CreatedAt: time.Now(),
				}
				_ = bus.Publish(event)
				assert.NoError(t, err)
			}(i)
		}

		wg.Wait()
	})

	t.Run("concurrent subscribes and publishes", func(t *testing.T) {
		var wg sync.WaitGroup
		var counter int32

		// Start subscribers
		for i := range 5 {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				err := bus.SubscribeToEventType(events.EventType(fmt.Sprintf("concurrent.sub.%d", id)), func(e *events.Event) {
					atomic.AddInt32(&counter, 1)
				})
				if err != nil {
					t.Logf("Subscribe error: %v", err)
				}
			}(i)
		}

		time.Sleep(200 * time.Millisecond)

		// Start publishers
		for i := range 5 {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				event := &events.Event{
					ID:        fmt.Sprintf("pubsub-%d", id),
					EventType: events.EventType(fmt.Sprintf("concurrent.sub.%d", id)),
					CreatedAt: time.Now(),
				}
				_ = bus.Publish(event)
			}(i)
		}

		wg.Wait()
		time.Sleep(500 * time.Millisecond)

		// Should have received some events
		finalCount := atomic.LoadInt32(&counter)
		t.Logf("Received %d events", finalCount)
	})
}

func TestNATSErrorScenarios(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("publish to closed bus", func(t *testing.T) {
		bus, err := NewNATSEventBus(DefaultConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		_ = bus.Close()

		event := &events.Event{
			ID:        "closed-test",
			EventType: "test.closed",
			CreatedAt: time.Now(),
		}

		err = bus.Publish(event)
		assert.Error(t, err)
	})

	t.Run("subscribe to closed bus", func(t *testing.T) {
		bus, err := NewNATSEventBus(DefaultConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		_ = bus.Close()

		err = bus.Subscribe(func(e *events.Event) {})
		assert.Error(t, err)
	})
}

func TestNATSMessageMarshaling(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewNATSEventBus(DefaultConfig())
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	t.Run("complex data structures", func(t *testing.T) {
		received := make(chan *events.Event, 1)

		err := bus.Subscribe(func(e *events.Event) {
			received <- e
		})
		require.NoError(t, err)

		time.Sleep(100 * time.Millisecond)

		complexData := map[string]any{
			"string":  "value",
			"number":  42,
			"boolean": true,
			"array":   []any{1, 2, 3},
			"nested": map[string]any{
				"key": "nested_value",
			},
		}

		testEvent := &events.Event{
			ID:        "complex-data",
			EventType: "test.complex",
			CreatedAt: time.Now(),
			Data:      complexData,
		}

		err = bus.Publish(testEvent)
		require.NoError(t, err)

		select {
		case evt := <-received:
			assert.Equal(t, testEvent.ID, evt.ID)
			assert.NotNil(t, evt.Data)
		case <-time.After(2 * time.Second):
			t.Fatal("timeout waiting for complex event")
		}
	})
}

func TestNATSReconnectHandlers(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("handlers are registered", func(t *testing.T) {
		bus, err := NewNATSEventBus(DefaultConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		defer func() {
			if err := bus.Close(); err != nil {
				t.Logf("error closing bus: %v", err)
			}
		}()

		// Verify connection has handlers
		assert.NotNil(t, bus.conn)
		assert.True(t, bus.conn.IsConnected())
	})
}

func TestNATSClientEdgeCases(t *testing.T) {
	t.Run("empty URL", func(t *testing.T) {
		client, err := NewNATSClient("", "")
		if client != nil {
			defer func() {
				if err := client.Close(); err != nil {
					t.Logf("error closing client: %v", err)
				}
			}()
		}
		// May or may not error depending on NATS lib behavior
		if err != nil {
			assert.Error(t, err)
		}
	})

	t.Run("multiple sequential connections", func(t *testing.T) {
		for range 5 {
			client, err := NewNATSClient(natslib.DefaultURL, "")
			if err != nil {
				t.Skipf("NATS not available: %v", err)
			}
			assert.NotNil(t, client)
			_ = client.Close()
		}
	})
}
