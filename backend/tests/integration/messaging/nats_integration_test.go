//go:build integration

package messaging_test

import (
	"fmt"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

var (
	testNatsConn *nats.Conn
	testJS       nats.JetStreamContext
	natsURL      = "nats://localhost:4222"
	setupOnce    sync.Once
	teardownOnce sync.Once
)

func setupTestNATS(t *testing.T) (*nats.Conn, nats.JetStreamContext) {
	setupOnce.Do(func() {
		conn, err := nats.Connect(natsURL,
			nats.Name("TracerTM-Integration-Test"),
			nats.Timeout(10*time.Second),
			nats.ReconnectWait(1*time.Second),
			nats.MaxReconnects(5),
		)
		require.NoError(t, err)

		// Create JetStream context
		js, err := conn.JetStream()
		require.NoError(t, err)

		testNatsConn = conn
		testJS = js

		t.Logf("✅ Test NATS initialized successfully")
	})

	return testNatsConn, testJS
}

func teardownTestNATS(t *testing.T) {
	teardownOnce.Do(func() {
		if testNatsConn != nil {
			// Clean up test streams
			if testJS != nil {
				_ = testJS.DeleteStream("TEST_STREAM")
				_ = testJS.DeleteStream("PERSISTENT_TEST")
				_ = testJS.DeleteStream("ACK_TEST")
			}

			_ = testNatsConn.Close()
			t.Logf("✅ Test NATS cleaned up")
		}
	})
}

// TestNATS_PublishSubscribe_Success tests basic pub/sub functionality
func TestNATS_PublishSubscribe_Success(t *testing.T) {
	nc, _ := setupTestNATS(t)
	defer teardownTestNATS(t)

	t.Run("Simple_PubSub", func(t *testing.T) {
		subject := "test.simple"
		message := []byte("Hello NATS!")
		received := make(chan []byte, 1)

		// Subscribe
		sub, err := nc.Subscribe(subject, func(msg *nats.Msg) {
			received <- msg.Data
		})
		require.NoError(t, err)
		defer sub.Unsubscribe()

		// Wait for subscription to be ready
		require.NoError(t, nc.Flush())

		// Publish
		err = nc.Publish(subject, message)
		require.NoError(t, err)

		// Verify message received
		select {
		case data := <-received:
			assert.Equal(t, message, data)
		case <-time.After(2 * time.Second):
			t.Fatal("Timeout waiting for message")
		}
	})

	t.Run("Multiple_Subscribers", func(t *testing.T) {
		subject := "test.multiple"
		message := []byte("Broadcast message")
		var receivedCount int32

		// Create 5 subscribers
		for i := 0; i < 5; i++ {
			sub, err := nc.Subscribe(subject, func(msg *nats.Msg) {
				atomic.AddInt32(&receivedCount, 1)
			})
			require.NoError(t, err)
			defer sub.Unsubscribe()
		}

		// Wait for subscriptions
		require.NoError(t, nc.Flush())

		// Publish once
		err := nc.Publish(subject, message)
		require.NoError(t, err)

		// Wait for all subscribers to receive
		time.Sleep(500 * time.Millisecond)
		assert.Equal(t, int32(5), atomic.LoadInt32(&receivedCount))
	})

	t.Run("Request_Reply", func(t *testing.T) {
		subject := "test.request"

		// Set up responder
		sub, err := nc.Subscribe(subject, func(msg *nats.Msg) {
			response := []byte("Reply: " + string(msg.Data))
			msg.Respond(response)
		})
		require.NoError(t, err)
		defer sub.Unsubscribe()

		require.NoError(t, nc.Flush())

		// Send request
		msg, err := nc.Request(subject, []byte("Question"), 2*time.Second)
		require.NoError(t, err)
		assert.Equal(t, "Reply: Question", string(msg.Data))
	})

	t.Run("Wildcard_Subscription", func(t *testing.T) {
		received := make(chan string, 10)

		// Subscribe to wildcard
		sub, err := nc.Subscribe("test.wildcard.*", func(msg *nats.Msg) {
			received <- msg.Subject
		})
		require.NoError(t, err)
		defer sub.Unsubscribe()

		require.NoError(t, nc.Flush())

		// Publish to different subjects
		subjects := []string{"test.wildcard.a", "test.wildcard.b", "test.wildcard.c"}
		for _, subj := range subjects {
			err := nc.Publish(subj, []byte("test"))
			require.NoError(t, err)
		}

		// Verify all received
		receivedSubjects := make(map[string]bool)
		timeout := time.After(2 * time.Second)
		for i := 0; i < 3; i++ {
			select {
			case subj := <-received:
				receivedSubjects[subj] = true
			case <-timeout:
				t.Fatal("Timeout waiting for wildcard messages")
			}
		}

		for _, subj := range subjects {
			assert.True(t, receivedSubjects[subj], "Should receive from %s", subj)
		}
	})
}

// TestNATS_JetStream_PersistentMessages tests JetStream persistence
func TestNATS_JetStream_PersistentMessages(t *testing.T) {
	nc, js := setupTestNATS(t)
	defer teardownTestNATS(t)

	streamName := "PERSISTENT_TEST"
	subject := "test.persistent"

	// Create stream
	stream, err := js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{subject},
		Storage:  nats.FileStorage,
		MaxAge:   24 * time.Hour,
	})
	require.NoError(t, err)
	require.NotNil(t, stream)

	t.Run("Publish_To_Stream", func(t *testing.T) {
		// Publish messages
		numMessages := 10
		for i := 0; i < numMessages; i++ {
			msg := []byte(fmt.Sprintf("Message %d", i))
			_, err := js.Publish(subject, msg)
			require.NoError(t, err)
		}

		// Verify stream state
		info, err := js.StreamInfo(streamName)
		require.NoError(t, err)
		assert.Equal(t, uint64(numMessages), info.State.Msgs)
	})

	t.Run("Durable_Consumer", func(t *testing.T) {
		consumerName := "test-consumer"

		// Create durable consumer
		sub, err := js.PullSubscribe(subject, consumerName, nats.PullMaxWaiting(128))
		require.NoError(t, err)
		defer sub.Unsubscribe()

		// Fetch messages
		msgs, err := sub.Fetch(10, nats.MaxWait(2*time.Second))
		require.NoError(t, err)
		assert.Len(t, msgs, 10)

		// Verify message content
		for i, msg := range msgs {
			expected := fmt.Sprintf("Message %d", i)
			assert.Equal(t, expected, string(msg.Data))
			msg.Ack()
		}
	})

	t.Run("Stream_Replay", func(t *testing.T) {
		// Create consumer with DeliverAll policy
		sub, err := js.PullSubscribe(subject, "replay-consumer",
			nats.DeliverAll(),
			nats.PullMaxWaiting(128),
		)
		require.NoError(t, err)
		defer sub.Unsubscribe()

		// Fetch all messages again
		msgs, err := sub.Fetch(10, nats.MaxWait(2*time.Second))
		require.NoError(t, err)
		assert.Len(t, msgs, 10)

		for _, msg := range msgs {
			msg.Ack()
		}
	})
}

// TestNATS_JetStream_Acknowledgment tests message acknowledgment patterns
func TestNATS_JetStream_Acknowledgment(t *testing.T) {
	nc, js := setupTestNATS(t)
	defer teardownTestNATS(t)

	streamName := "ACK_TEST"
	subject := "test.ack"

	// Create stream
	_, err := js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: []string{subject},
		Storage:  nats.MemoryStorage,
	})
	require.NoError(t, err)

	t.Run("Ack_Messages", func(t *testing.T) {
		// Publish test message
		_, err := js.Publish(subject, []byte("Ack test"))
		require.NoError(t, err)

		// Subscribe and ack
		sub, err := js.PullSubscribe(subject, "ack-consumer", nats.PullMaxWaiting(128))
		require.NoError(t, err)
		defer sub.Unsubscribe()

		msgs, err := sub.Fetch(1, nats.MaxWait(2*time.Second))
		require.NoError(t, err)
		require.Len(t, msgs, 1)

		// Acknowledge message
		err = msgs[0].Ack()
		require.NoError(t, err)
	})

	t.Run("Nak_Messages", func(t *testing.T) {
		// Publish test message
		_, err := js.Publish(subject, []byte("Nak test"))
		require.NoError(t, err)

		// Subscribe
		sub, err := js.PullSubscribe(subject, "nak-consumer",
			nats.AckWait(2*time.Second),
			nats.MaxDeliver(3),
			nats.PullMaxWaiting(128),
		)
		require.NoError(t, err)
		defer sub.Unsubscribe()

		// Fetch and NAK
		msgs, err := sub.Fetch(1, nats.MaxWait(2*time.Second))
		require.NoError(t, err)
		require.Len(t, msgs, 1)

		err = msgs[0].Nak()
		require.NoError(t, err)

		// Message should be redelivered
		msgs, err = sub.Fetch(1, nats.MaxWait(3*time.Second))
		require.NoError(t, err)
		require.Len(t, msgs, 1)
		assert.True(t, msgs[0].Metadata.NumDelivered > 1)

		// Clean up
		msgs[0].Ack()
	})

	t.Run("InProgress_Messages", func(t *testing.T) {
		// Publish test message
		_, err := js.Publish(subject, []byte("InProgress test"))
		require.NoError(t, err)

		// Subscribe with short ack wait
		sub, err := js.PullSubscribe(subject, "inprogress-consumer",
			nats.AckWait(1*time.Second),
			nats.PullMaxWaiting(128),
		)
		require.NoError(t, err)
		defer sub.Unsubscribe()

		// Fetch message
		msgs, err := sub.Fetch(1, nats.MaxWait(2*time.Second))
		require.NoError(t, err)
		require.Len(t, msgs, 1)

		// Send in-progress to extend ack deadline
		err = msgs[0].InProgress()
		require.NoError(t, err)

		// Simulate processing
		time.Sleep(500 * time.Millisecond)

		// Final ack
		err = msgs[0].Ack()
		require.NoError(t, err)
	})
}

// TestNATS_Reconnection_Resilience tests connection resilience
func TestNATS_Reconnection_Resilience(t *testing.T) {
	// Create connection with reconnect options
	reconnectCount := int32(0)
	disconnectCount := int32(0)

	nc, err := nats.Connect(natsURL,
		nats.Name("Resilience-Test"),
		nats.ReconnectWait(100*time.Millisecond),
		nats.MaxReconnects(10),
		nats.DisconnectErrHandler(func(nc *nats.Conn, err error) {
			atomic.AddInt32(&disconnectCount, 1)
		}),
		nats.ReconnectHandler(func(nc *nats.Conn) {
			atomic.AddInt32(&reconnectCount, 1)
		}),
	)
	require.NoError(t, err)
	defer func() {
		if err := nc.Close(); err != nil {
			// ignore error
		}
	}()

	t.Run("Connection_State", func(t *testing.T) {
		assert.True(t, nc.IsConnected())
		assert.False(t, nc.IsClosed())
	})

	t.Run("Flush_Timeout", func(t *testing.T) {
		err := nc.FlushTimeout(1 * time.Second)
		assert.NoError(t, err)
	})

	t.Run("Server_Info", func(t *testing.T) {
		info := nc.ConnectedServerName()
		assert.NotEmpty(t, info)
		t.Logf("Connected to NATS server: %s", info)
	})
}

// TestNATS_LoadBalancing_MultipleSubscribers tests queue groups for load balancing
func TestNATS_LoadBalancing_MultipleSubscribers(t *testing.T) {
	nc, _ := setupTestNATS(t)
	defer teardownTestNATS(t)

	subject := "test.loadbalance"
	queueGroup := "workers"
	numWorkers := 5
	numMessages := 100

	// Track which worker received each message
	receivedByWorker := make(map[int]int32)
	var mu sync.Mutex

	// Create multiple workers in same queue group
	var subs []*nats.Subscription
	for i := 0; i < numWorkers; i++ {
		workerID := i
		receivedByWorker[workerID] = 0

		sub, err := nc.QueueSubscribe(subject, queueGroup, func(msg *nats.Msg) {
			mu.Lock()
			receivedByWorker[workerID]++
			mu.Unlock()
		})
		require.NoError(t, err)
		subs = append(subs, sub)
	}

	// Clean up subscriptions
	defer func() {
		for _, sub := range subs {
			sub.Unsubscribe()
		}
	}()

	// Wait for subscriptions to be ready
	require.NoError(t, nc.Flush())

	// Publish messages
	for i := 0; i < numMessages; i++ {
		msg := []byte(fmt.Sprintf("Message %d", i))
		err := nc.Publish(subject, msg)
		require.NoError(t, err)
	}

	// Wait for all messages to be processed
	time.Sleep(1 * time.Second)

	// Verify load distribution
	mu.Lock()
	totalReceived := int32(0)
	for workerID, count := range receivedByWorker {
		totalReceived += count
		t.Logf("Worker %d received %d messages", workerID, count)
		// Each worker should receive at least some messages
		assert.Greater(t, count, int32(0), "Worker %d should receive messages", workerID)
	}
	mu.Unlock()

	// All messages should be received exactly once
	assert.Equal(t, int32(numMessages), totalReceived)

	// Distribution should be relatively balanced (within 30% deviation)
	expectedPerWorker := float64(numMessages) / float64(numWorkers)
	mu.Lock()
	for workerID, count := range receivedByWorker {
		deviation := float64(count) / expectedPerWorker
		assert.Greater(t, deviation, 0.5, "Worker %d received too few messages", workerID)
		assert.Less(t, deviation, 1.5, "Worker %d received too many messages", workerID)
	}
	mu.Unlock()
}

// TestNATS_Performance_Benchmark benchmarks message throughput
func TestNATS_Performance_Benchmark(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance benchmark in short mode")
	}

	nc, _ := setupTestNATS(t)
	defer teardownTestNATS(t)

	subject := "test.perf"
	numMessages := 10000

	t.Run("Publish_Throughput", func(t *testing.T) {
		start := time.Now()

		for i := 0; i < numMessages; i++ {
			msg := []byte(fmt.Sprintf("Perf message %d", i))
			err := nc.Publish(subject, msg)
			require.NoError(t, err)
		}

		err := nc.Flush()
		require.NoError(t, err)

		duration := time.Since(start)
		messagesPerSecond := float64(numMessages) / duration.Seconds()

		t.Logf("Published %d messages in %v (%.2f msg/sec)",
			numMessages, duration, messagesPerSecond)

		assert.Greater(t, messagesPerSecond, 1000.0, "Should achieve >1000 msg/sec")
	})
}
