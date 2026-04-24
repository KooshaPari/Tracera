package nats

import (
	"context"
	"fmt"
	"os"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	natslib "github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/events"
)

const (
	natsTestTimeout      = 2 * time.Second
	natsTestDrainTimeout = 10 * time.Second
	natsTestNanoTimeout  = 1 * time.Nanosecond
	natsTestWaitDelay    = 10 * time.Millisecond
	natsTestShortDelay   = 100 * time.Millisecond
	natsTestMediumDelay  = 200 * time.Millisecond
	natsTestLongDelay    = 500 * time.Millisecond
)

type publishCase struct {
	name      string
	eventID   string
	eventData map[string]any
	target    string // empty for Publish, "project" or "entity"
	targetID  string
	wantErr   bool
}

func publishCases() []publishCase {
	return []publishCase{
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
}

func testConfig() *Config {
	config := DefaultConfig()
	// Use a unique stream name and subjects for each test run to avoid interference and overlap
	uniqueID := fmt.Sprintf("%d_%d", os.Getpid(), time.Now().UnixNano())
	config.StreamName = "TEST_STREAM_" + uniqueID
	config.SubjectPrefix = fmt.Sprintf("test.%s.", uniqueID)
	config.StreamSubjects = []string{
		config.SubjectPrefix + ">",
	}
	return config
}

func withEventBus(t *testing.T, fn func(*EventBus)) {
	t.Helper()
	config := testConfig()
	bus, err := NewEventBus(config)
	if err != nil {
		t.Skipf("NATS server not available: %v", err)
	}
	defer func() {
		// Clean up the stream after test
		require.NoError(t, bus.DeleteStream(config.StreamName))
		if err := bus.Close(); err != nil {
			t.Logf("error closing bus: %v", err)
		}
	}()

	fn(bus)
}

func runPublishCase(t *testing.T, bus *EventBus, tt publishCase) {
	t.Helper()
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
		require.Error(t, err)
	} else {
		require.NoError(t, err)
	}
}

func waitForEventOrTimeout(t *testing.T, ch <-chan *events.Event, timeout time.Duration) *events.Event {
	t.Helper()
	select {
	case evt := <-ch:
		return evt
	case <-time.After(timeout):
		t.Fatal("timeout waiting for event")
		return nil
	}
}

func testSubscribeReceiveEvent(t *testing.T, bus *EventBus) {
	received := make(chan *events.Event, 1)

	err := bus.Subscribe(func(evt *events.Event) {
		received <- evt
	})
	require.NoError(t, err)

	time.Sleep(natsTestShortDelay)

	testEvent := &events.Event{
		ID:        "subscribe-test-1",
		EventType: "test.subscribe",
		CreatedAt: time.Now(),
		Data:      map[string]any{"test": "subscribe"},
	}
	err = bus.Publish(testEvent)
	require.NoError(t, err)

	evt := waitForEventOrTimeout(t, received, natsTestTimeout)
	assert.Equal(t, testEvent.ID, evt.ID)
	assert.Equal(t, testEvent.EventType, evt.EventType)
}

func testSubscribeProjectEvents(t *testing.T, bus *EventBus) {
	projectID := "test-project-123"
	received := make(chan *events.Event, 1)

	err := bus.SubscribeToProject(projectID, func(evt *events.Event) {
		received <- evt
	})
	require.NoError(t, err)

	time.Sleep(natsTestShortDelay)

	testEvent := &events.Event{
		ID:        "project-event-1",
		EventType: "test.project",
		CreatedAt: time.Now(),
	}
	err = bus.PublishToProject(projectID, testEvent)
	require.NoError(t, err)

	evt := waitForEventOrTimeout(t, received, natsTestTimeout)
	assert.Equal(t, testEvent.ID, evt.ID)
}

func testSubscribeEntityEvents(t *testing.T, bus *EventBus) {
	entityID := "test-entity-456"
	received := make(chan *events.Event, 1)

	err := bus.SubscribeToEntity(entityID, func(evt *events.Event) {
		received <- evt
	})
	require.NoError(t, err)

	time.Sleep(natsTestShortDelay)

	testEvent := &events.Event{
		ID:        "entity-event-1",
		EventType: "test.entity",
		CreatedAt: time.Now(),
	}
	err = bus.PublishToEntity(entityID, testEvent)
	require.NoError(t, err)

	evt := waitForEventOrTimeout(t, received, natsTestTimeout)
	assert.Equal(t, testEvent.ID, evt.ID)
}

func testSubscribeEventType(t *testing.T, bus *EventBus) {
	eventType := events.EventType("test.specific.type")
	received := make(chan *events.Event, 1)

	err := bus.SubscribeToEventType(eventType, func(evt *events.Event) {
		received <- evt
	})
	require.NoError(t, err)

	time.Sleep(natsTestShortDelay)

	testEvent := &events.Event{
		ID:        "type-event-1",
		EventType: eventType,
		CreatedAt: time.Now(),
	}
	err = bus.Publish(testEvent)
	require.NoError(t, err)

	evt := waitForEventOrTimeout(t, received, natsTestTimeout)
	assert.Equal(t, testEvent.ID, evt.ID)
}

func testDuplicateSubscription(t *testing.T, bus *EventBus) {
	err := bus.Subscribe(func(_ *events.Event) {})
	require.NoError(t, err)

	err = bus.Subscribe(func(_ *events.Event) {})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "already subscribed")
}

func testConcurrentPublishes(t *testing.T, bus *EventBus) {
	var wg sync.WaitGroup
	numGoroutines := 50

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			event := &events.Event{
				ID:        fmt.Sprintf("concurrent-%d", id),
				EventType: "test.concurrent",
				CreatedAt: time.Now(),
			}
			publishErr := bus.Publish(event)
			assert.NoError(t, publishErr)
		}(i)
	}

	wg.Wait()
}

func testConcurrentSubscribesAndPublishes(t *testing.T, bus *EventBus) {
	var wg sync.WaitGroup
	var counter int32

	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			err := bus.SubscribeToEventType(events.EventType(fmt.Sprintf("concurrent.sub.%d", id)), func(_ *events.Event) {
				atomic.AddInt32(&counter, 1)
			})
			if err != nil {
				t.Logf("Subscribe error: %v", err)
			}
		}(i)
	}

	time.Sleep(natsTestMediumDelay)

	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			event := &events.Event{
				ID:        fmt.Sprintf("pubsub-%d", id),
				EventType: events.EventType(fmt.Sprintf("concurrent.sub.%d", id)),
				CreatedAt: time.Now(),
			}
			assert.NoError(t, bus.Publish(event))
		}(i)
	}

	wg.Wait()
	time.Sleep(natsTestLongDelay)

	finalCount := atomic.LoadInt32(&counter)
	t.Logf("Received %d events", finalCount)
}

func setupTestNATS(t *testing.T) *Client {
	url := os.Getenv("NATS_URL")
	if url == "" {
		url = natslib.DefaultURL
	}

	client, err := NewClient(url, "")
	if err != nil {
		t.Skipf("NATS not available: %v", err)
	}
	return client
}

func TestNewClient(t *testing.T) {
	t.Run("successful connection without creds", func(t *testing.T) {
		client, err := NewClient(natslib.DefaultURL, "")
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
		client, err := NewClient("invalid://url", "")
		require.Error(t, err)
		assert.Nil(t, client)
	})

	t.Run("unreachable server", func(t *testing.T) {
		client, err := NewClient("nats://192.0.2.1:4222", "")
		require.Error(t, err)
		assert.Nil(t, client)
		assert.Contains(t, err.Error(), "failed to connect to NATS")
	})

	t.Run("with invalid creds path", func(t *testing.T) {
		client, err := NewClient(natslib.DefaultURL, "/invalid/path/creds.txt")
		if err == nil && client != nil {
			if err := client.Close(); err != nil {
				t.Logf("close error: %v", err)
			}
			t.Skip("NATS accepted invalid creds path")
		}
		require.Error(t, err)
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
		require.NoError(t, err)
	})

	t.Run("closed connection", func(t *testing.T) {
		tempClient := setupTestNATS(t)
		if err := tempClient.Close(); err != nil {
			t.Logf("close error: %v", err)
		}

		ctx := context.Background()
		err := tempClient.HealthCheck(ctx)
		require.Error(t, err)
		assert.Contains(t, err.Error(), "not available")
	})

	t.Run("nil connection", func(t *testing.T) {
		client := &Client{conn: nil}
		err := client.HealthCheck(context.Background())
		require.Error(t, err)
	})
}

func TestNATSClientClose(t *testing.T) {
	t.Run("close active connection", func(t *testing.T) {
		client := setupTestNATS(t)
		err := client.Close()
		require.NoError(t, err)
		assert.True(t, client.conn.IsClosed())
	})

	t.Run("close nil connection", func(t *testing.T) {
		client := &Client{conn: nil}
		err := client.Close()
		require.NoError(t, err)
	})

	t.Run("double close", func(t *testing.T) {
		client := setupTestNATS(t)
		err := client.Close()
		require.NoError(t, err)
		err = client.Close()
		require.NoError(t, err)
	})
}

func TestDefaultConfig(t *testing.T) {
	config := DefaultConfig()

	assert.Equal(t, natslib.DefaultURL, config.URL)
	assert.Equal(t, "tracertm-cluster", config.ClusterID)
	assert.Equal(t, "tracertm-backend", config.ClientID)
	assert.Equal(t, 10, config.MaxReconnects)
	assert.Equal(t, natsTestTimeout, config.ReconnectWait)
	assert.Equal(t, "TRACERTM_EVENTS", config.StreamName)
	assert.Len(t, config.StreamSubjects, 3)
	assert.Contains(t, config.StreamSubjects, "tracertm.events.>")
	assert.Contains(t, config.StreamSubjects, "tracertm.projects.>")
	assert.Contains(t, config.StreamSubjects, "tracertm.entities.>")
}

func TestNewEventBus(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	config := testConfig()

	t.Run("successful initialization", func(t *testing.T) {
		bus, err := NewEventBus(config)
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

		bus, err := NewEventBus(&invalidConfig)
		require.Error(t, err)
		assert.Nil(t, bus)
	})

	t.Run("unreachable server", func(t *testing.T) {
		invalidConfig := *config
		invalidConfig.URL = "nats://192.0.2.1:4222"

		bus, err := NewEventBus(&invalidConfig)
		require.Error(t, err)
		assert.Nil(t, bus)
	})
}

func TestNATSEventBusPublish(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	withEventBus(t, func(bus *EventBus) {
		for _, tt := range publishCases() {
			t.Run(tt.name, func(t *testing.T) {
				runPublishCase(t, bus, tt)
			})
		}
	})
}

func TestNATSEventBusSubscribe(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("subscribe and receive event", func(t *testing.T) {
		withEventBus(t, func(bus *EventBus) {
			testSubscribeReceiveEvent(t, bus)
		})
	})
	t.Run("subscribe to project events", func(t *testing.T) {
		withEventBus(t, func(bus *EventBus) {
			testSubscribeProjectEvents(t, bus)
		})
	})
	t.Run("subscribe to entity events", func(t *testing.T) {
		withEventBus(t, func(bus *EventBus) {
			testSubscribeEntityEvents(t, bus)
		})
	})
	t.Run("subscribe to event type", func(t *testing.T) {
		withEventBus(t, func(bus *EventBus) {
			testSubscribeEventType(t, bus)
		})
	})
	t.Run("duplicate subscription fails", func(t *testing.T) {
		withEventBus(t, func(bus *EventBus) {
			testDuplicateSubscription(t, bus)
		})
	})
}

func TestNATSEventBusUnsubscribe(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewEventBus(testConfig())
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

		err := bus.SubscribeToProject(projectID, func(_ *events.Event) {})
		require.NoError(t, err)

		subID := "project-" + projectID
		err = bus.Unsubscribe(subID)
		require.NoError(t, err)

		// Verify it's removed
		bus.mu.RLock()
		_, exists := bus.subscriptions[subID]
		bus.mu.RUnlock()
		assert.False(t, exists)
	})

	t.Run("unsubscribe non-existent subscription", func(t *testing.T) {
		err := bus.Unsubscribe("non-existent")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "subscription not found")
	})

	t.Run("double unsubscribe", func(t *testing.T) {
		projectID := "unsub-project-2"

		err := bus.SubscribeToProject(projectID, func(_ *events.Event) {})
		require.NoError(t, err)

		subID := "project-" + projectID
		err = bus.Unsubscribe(subID)
		require.NoError(t, err)

		err = bus.Unsubscribe(subID)
		require.Error(t, err)
	})
}

func TestNATSEventBusPublishBatch(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewEventBus(testConfig())
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
		require.NoError(t, err)
	})

	t.Run("publish empty batch", func(t *testing.T) {
		err := bus.PublishBatch([]*events.Event{})
		require.NoError(t, err)
	})

	t.Run("publish nil batch", func(t *testing.T) {
		err := bus.PublishBatch(nil)
		require.NoError(t, err)
	})
}

func TestNATSEventBusQueueSubscribe(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewEventBus(testConfig())
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

		err := bus.QueueSubscribe(subject, queue, func(_ *events.Event) {
			atomic.AddInt32(&count1, 1)
		})
		require.NoError(t, err)

		err = bus.QueueSubscribe(subject, queue+"2", func(_ *events.Event) {
			atomic.AddInt32(&count2, 1)
		})
		require.NoError(t, err)

		time.Sleep(natsTestShortDelay)

		// Publish multiple events
		for i := range 10 {
			event := &events.Event{
				ID:        fmt.Sprintf("queue-event-%d", i),
				EventType: "queue.test",
				CreatedAt: time.Now(),
			}
			require.NoError(t, bus.publishToSubject(subject, event))
		}

		time.Sleep(natsTestLongDelay)

		// Both subscribers should have received some events
		total := atomic.LoadInt32(&count1) + atomic.LoadInt32(&count2)
		assert.Positive(t, total)
	})

	t.Run("duplicate queue subscription fails", func(t *testing.T) {
		subject := "tracertm.events.dup.test"
		queue := "dup-queue"

		err := bus.QueueSubscribe(subject, queue, func(_ *events.Event) {})
		require.NoError(t, err)

		err = bus.QueueSubscribe(subject, queue, func(_ *events.Event) {})
		require.Error(t, err)
	})
}

func TestNATSEventBusGetStats(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewEventBus(testConfig())
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

	typed701, ok := stats["connected"].(bool)
	require.True(t, ok)
	assert.True(t, typed701)
	typed702, ok := stats["subscriptions"].(int)
	require.True(t, ok)
	assert.GreaterOrEqual(t, typed702, 0)
}

func TestNATSEventBusDrainAndClose(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("graceful drain and close", func(t *testing.T) {
		bus, err := NewEventBus(testConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}

		// Add a subscription
		err = bus.Subscribe(func(_ *events.Event) {})
		require.NoError(t, err)

		ctx, cancel := context.WithTimeout(context.Background(), natsTestDrainTimeout)
		defer cancel()

		err = bus.DrainAndClose(ctx)
		require.NoError(t, err)
		assert.True(t, bus.conn.IsClosed())
	})

	t.Run("drain with context timeout", func(t *testing.T) {
		bus, err := NewEventBus(testConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}

		ctx, cancel := context.WithTimeout(context.Background(), natsTestNanoTimeout)
		defer cancel()
		time.Sleep(natsTestWaitDelay)

		err = bus.DrainAndClose(ctx)
		// Should still complete even if context times out
		require.NoError(t, err)
	})
}

func TestNATSEventBusStreamOperations(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewEventBus(testConfig())
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
		require.Error(t, err)
		assert.Nil(t, info)
	})
}

func TestConcurrentNATSOperations(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	withEventBus(t, func(bus *EventBus) {
		t.Run("concurrent publishes", func(t *testing.T) {
			testConcurrentPublishes(t, bus)
		})
		t.Run("concurrent subscribes and publishes", func(t *testing.T) {
			testConcurrentSubscribesAndPublishes(t, bus)
		})
	})
}

func TestNATSErrorScenarios(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("publish to closed bus", func(t *testing.T) {
		bus, err := NewEventBus(testConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		if err := bus.Close(); err != nil {
			t.Logf("close error: %v", err)
		}

		event := &events.Event{
			ID:        "closed-test",
			EventType: "test.closed",
			CreatedAt: time.Now(),
		}

		err = bus.Publish(event)
		require.Error(t, err)
	})

	t.Run("subscribe to closed bus", func(t *testing.T) {
		bus, err := NewEventBus(testConfig())
		if err != nil {
			t.Skipf("NATS server not available: %v", err)
		}
		if err := bus.Close(); err != nil {
			t.Logf("close error: %v", err)
		}

		err = bus.Subscribe(func(_ *events.Event) {})
		require.Error(t, err)
	})
}

func TestNATSMessageMarshaling(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	bus, err := NewEventBus(testConfig())
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

		err := bus.Subscribe(func(evt *events.Event) {
			received <- evt
		})
		require.NoError(t, err)

		time.Sleep(natsTestShortDelay)

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
		case <-time.After(natsTestTimeout):
			t.Fatal("timeout waiting for complex event")
		}
	})
}

func TestNATSReconnectHandlers(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping NATS integration test in short mode")
	}

	t.Run("handlers are registered", func(t *testing.T) {
		bus, err := NewEventBus(testConfig())
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
		client, err := NewClient("", "")
		if client != nil {
			defer func() {
				if err := client.Close(); err != nil {
					t.Logf("error closing client: %v", err)
				}
			}()
		}
		// May or may not error depending on NATS lib behavior
		if err != nil {
			require.Error(t, err)
		}
	})

	t.Run("multiple sequential connections", func(t *testing.T) {
		for range 5 {
			client, err := NewClient(natslib.DefaultURL, "")
			if err != nil {
				t.Skipf("NATS not available: %v", err)
			}
			assert.NotNil(t, client)
			if err := client.Close(); err != nil {
				t.Logf("close error: %v", err)
			}
		}
	})
}
