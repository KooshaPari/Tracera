package websocket

import (
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestDefaultBackpressureConfig tests default configuration
func TestDefaultBackpressureConfig(t *testing.T) {
	config := DefaultBackpressureConfig()

	require.NotNil(t, config)
	assert.Equal(t, StrategyDrop, config.Strategy)
	assert.Equal(t, backpressureBufferSize, config.BufferSize)
	assert.Equal(t, backpressureSampleRate, config.SampleRate)
	assert.Equal(t, backpressureThrottleRate, config.ThrottleRate)
	assert.InEpsilon(t, backpressureDropThreshold, config.DropThreshold, 1e-9)
}

// TestNewBackpressureHandler tests backpressure handler creation
func TestNewBackpressureHandler(t *testing.T) {
	tests := []struct {
		name   string
		config *BackpressureConfig
	}{
		{
			name:   "with custom config",
			config: &BackpressureConfig{Strategy: StrategyQueue, BufferSize: 512},
		},
		{
			name:   "with nil config (should use default)",
			config: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			hub := NewHub()
			client := &Client{
				ID:        uuid.New().String(),
				ProjectID: uuid.New().String(),
				Hub:       hub,
				Send:      make(chan *Message, 256),
			}

			handler := NewBackpressureHandler(client, tt.config)

			require.NotNil(t, handler)
			assert.Equal(t, client, handler.client)
			assert.NotNil(t, handler.config)
			assert.NotZero(t, handler.lastSent)

			if tt.config == nil {
				// Should have default config
				assert.Equal(t, StrategyDrop, handler.config.Strategy)
			} else {
				assert.Equal(t, tt.config.Strategy, handler.config.Strategy)
			}
		})
	}
}

// TestBackpressureHandler_CanSend_StrategyDrop tests drop strategy
func TestBackpressureHandler_CanSend_StrategyDrop(t *testing.T) {
	config := &BackpressureConfig{
		Strategy:      StrategyDrop,
		BufferSize:    10,
		DropThreshold: 0.5, // Drop when 50% full
	}

	hub := NewHub()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Hub:       hub,
		Send:      make(chan *Message, 10),
	}

	handler := NewBackpressureHandler(client, config)
	msg := &Message{Type: string(MessageTypeConnected)}

	// Empty buffer - should allow
	assert.True(t, handler.CanSend(msg))

	// Fill buffer to 60% (6 messages)
	for i := 0; i < 6; i++ {
		client.Send <- msg
	}

	// Buffer > 50% full - should drop
	assert.False(t, handler.CanSend(msg))

	// Drain buffer
	for len(client.Send) > 0 {
		<-client.Send
	}

	// Empty again - should allow
	assert.True(t, handler.CanSend(msg))
}

// TestBackpressureHandler_CanSend_StrategySample tests sample strategy
func TestBackpressureHandler_CanSend_StrategySample(t *testing.T) {
	config := &BackpressureConfig{
		Strategy:   StrategySample,
		SampleRate: 5, // Keep 1 out of 5 messages
	}

	hub := NewHub()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Hub:       hub,
		Send:      make(chan *Message, 256),
	}

	handler := NewBackpressureHandler(client, config)
	msg := &Message{Type: string(MessageTypeConnected)}

	// First 4 messages should be dropped (1, 2, 3, 4)
	for i := 0; i < 4; i++ {
		assert.False(t, handler.CanSend(msg), "Message %d should be dropped", i+1)
	}

	// 5th message should pass
	assert.True(t, handler.CanSend(msg), "5th message should pass")

	// Next 4 should be dropped again
	for i := 0; i < 4; i++ {
		assert.False(t, handler.CanSend(msg), "Message %d should be dropped", i+6)
	}
}

// TestBackpressureHandler_CanSend_StrategyThrottle tests throttle strategy
func TestBackpressureHandler_CanSend_StrategyThrottle(t *testing.T) {
	throttleRate := 50 * time.Millisecond
	config := &BackpressureConfig{
		Strategy:     StrategyThrottle,
		ThrottleRate: throttleRate,
	}

	hub := NewHub()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Hub:       hub,
		Send:      make(chan *Message, 256),
	}

	handler := NewBackpressureHandler(client, config)
	msg := &Message{Type: string(MessageTypeConnected)}

	// First message should pass (lastSent initialized to time.Now())
	// and should set lastSent
	assert.True(t, handler.CanSend(msg))

	// Immediate second message should be throttled (not enough time has passed)
	time.Sleep(1 * time.Millisecond) // Small delay to ensure time passes
	assert.False(t, handler.CanSend(msg))

	// Wait for throttle period to pass
	time.Sleep(throttleRate + 20*time.Millisecond)

	// Should pass now (enough time has passed since first CanSend)
	assert.True(t, handler.CanSend(msg))
}

// TestBackpressureHandler_CanSend_StrategyQueue tests queue strategy
func TestBackpressureHandler_CanSend_StrategyQueue(t *testing.T) {
	config := &BackpressureConfig{
		Strategy: StrategyQueue,
	}

	hub := NewHub()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Hub:       hub,
		Send:      make(chan *Message, 256),
	}

	handler := NewBackpressureHandler(client, config)
	msg := &Message{Type: string(MessageTypeConnected)}

	// Queue strategy should always return true (will block on send if full)
	for i := 0; i < 10; i++ {
		assert.True(t, handler.CanSend(msg))
	}
}

// TestBackpressureHandler_Send tests message sending
func TestBackpressureHandler_Send(t *testing.T) {
	config := &BackpressureConfig{
		Strategy:      StrategyDrop,
		DropThreshold: 0.5,
	}

	bufferSize := 10
	hub := NewHub()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Hub:       hub,
		Send:      make(chan *Message, bufferSize),
	}

	handler := NewBackpressureHandler(client, config)
	msg := &Message{Type: string(MessageTypeConnected)}

	// Empty buffer - should send
	sent := handler.Send(msg)
	assert.True(t, sent)

	// Should be in buffer
	select {
	case receivedMsg := <-client.Send:
		assert.NotNil(t, receivedMsg)
	case <-time.After(100 * time.Millisecond):
		t.Fatal("expected message in buffer")
	}
}

// TestBackpressureHandler_Reset tests handler reset
func TestBackpressureHandler_Reset(t *testing.T) {
	config := &BackpressureConfig{
		Strategy:   StrategySample,
		SampleRate: 5,
	}

	hub := NewHub()
	client := &Client{
		ID:        uuid.New().String(),
		ProjectID: uuid.New().String(),
		Hub:       hub,
		Send:      make(chan *Message, 256),
	}

	handler := NewBackpressureHandler(client, config)
	msg := &Message{Type: string(MessageTypeConnected)}

	// Generate some messages to increment counters
	for i := 0; i < 10; i++ {
		handler.CanSend(msg)
	}

	// Counters should be non-zero
	stats := handler.GetStats()
	typed252, ok := stats["messages_sent"].(int64)
	require.True(t, ok)
	assert.Positive(t, typed252)

	// Reset
	handler.Reset()

	// Counters should be reset
	stats = handler.GetStats()
	typed259, ok := stats["messages_sent"].(int64)
	require.True(t, ok)
	assert.Equal(t, int64(0), typed259)
	typed260, ok := stats["messages_dropped"].(int64)
	require.True(t, ok)
	assert.Equal(t, int64(0), typed260)
}

// TestNewMessageBatcher tests message batcher creation
func TestNewMessageBatcher(t *testing.T) {
	maxSize := 100
	maxWait := 1 * time.Second

	batcher := NewMessageBatcher(maxSize, maxWait)

	require.NotNil(t, batcher)
	assert.Equal(t, maxSize, batcher.maxSize)
	assert.Equal(t, maxWait, batcher.maxWait)
	assert.NotNil(t, batcher.messages)
	assert.Empty(t, batcher.messages)
}

// TestMessageBatcher_Add tests adding messages to batch
func TestMessageBatcher_Add(t *testing.T) {
	batcher := NewMessageBatcher(3, 1*time.Second)

	msg1 := &Message{Type: string(MessageTypeConnected)}
	msg2 := &Message{Type: string(MessageTypeDisconnected)}
	msg3 := &Message{Type: string(MessageTypeError)}

	// Add messages
	batcher.Add(msg1)
	batcher.Add(msg2)
	shouldFlush := batcher.Add(msg3)

	// Should trigger flush when reaching maxSize
	assert.True(t, shouldFlush)
}

// TestMessageBatcher_Flush tests flushing messages
func TestMessageBatcher_Flush(t *testing.T) {
	batcher := NewMessageBatcher(10, 1*time.Second)

	// Add some messages
	for i := 0; i < 5; i++ {
		batcher.Add(&Message{Type: string(MessageTypeConnected)})
	}

	// Flush
	messages := batcher.Flush()

	// Should return all messages
	assert.Len(t, messages, 5)

	// Second flush should return empty
	messages = batcher.Flush()
	assert.Empty(t, messages)
}

// TestMessageBatcher_FlushChan tests flush channel
func TestMessageBatcher_FlushChan(t *testing.T) {
	flushInterval := 100 * time.Millisecond
	batcher := NewMessageBatcher(10, flushInterval)

	// Start flush channel
	flushChan := batcher.FlushChan()
	require.NotNil(t, flushChan)

	// Add messages to trigger flush
	for i := 0; i < 10; i++ {
		batcher.Add(&Message{Type: string(MessageTypeConnected)})
	}

	// Wait for flush signal
	select {
	case <-flushChan:
		// Flush triggered
		messages := batcher.Flush()
		assert.Len(t, messages, 10)
	case <-time.After(flushInterval + 50*time.Millisecond):
		t.Fatal("flush did not trigger within expected time")
	}
}

// TestNewRateLimiter tests rate limiter creation
func TestNewRateLimiter(t *testing.T) {
	rate := 10.0 // 10 messages per second
	burst := 20  // Allow burst of 20
	limiter := NewRateLimiter(rate, burst)

	require.NotNil(t, limiter)
	assert.NotNil(t, limiter)

	stats := limiter.GetStats()
	typed349, ok := stats["rate"].(float64)
	require.True(t, ok)
	assert.InEpsilon(t, rate, typed349, 1e-9)
	typed350, ok := stats["burst"].(int)
	require.True(t, ok)
	assert.Equal(t, burst, typed350)
}

// TestRateLimiter_Allow tests rate limiting
func TestRateLimiter_Allow(t *testing.T) {
	rate := 100.0 // 100 messages per second
	burst := 10   // Allow burst of 10
	limiter := NewRateLimiter(rate, burst)

	// First 10 should pass (burst)
	allowedCount := 0
	for i := 0; i < 10; i++ {
		if limiter.Allow() {
			allowedCount++
		}
	}
	assert.GreaterOrEqual(t, allowedCount, 9) // At least 9 should pass

	// 11th should be rate-limited (no time passed)
	assert.False(t, limiter.Allow())
}

// TestRateLimiter_Wait tests wait mechanism
func TestRateLimiter_Wait(t *testing.T) {
	rate := 1000.0 // 1000 messages per second
	burst := 1
	limiter := NewRateLimiter(rate, burst)

	// First should pass immediately
	start := time.Now()
	limiter.Wait()
	elapsed := time.Since(start)
	assert.Less(t, elapsed, 10*time.Millisecond)
}

// TestRateLimiter_GetStats tests statistics retrieval
func TestRateLimiter_GetStats(t *testing.T) {
	limiter := NewRateLimiter(10.0, 5)

	stats := limiter.GetStats()
	typed390, ok := stats["rate"].(float64)
	require.True(t, ok)
	assert.InEpsilon(t, 10.0, typed390, 1e-9)
	typed391, ok := stats["burst"].(int)
	require.True(t, ok)
	assert.Equal(t, 5, typed391)
	assert.NotNil(t, stats["available_tokens"])
}

// TestNewPriorityQueue tests priority queue creation
func TestNewPriorityQueue(t *testing.T) {
	queue := NewPriorityQueue()

	require.NotNil(t, queue)
	assert.NotNil(t, queue.high)
	assert.NotNil(t, queue.normal)
	assert.NotNil(t, queue.low)
	assert.Equal(t, 0, queue.Len())
}

// TestGetPriority tests priority extraction from message
func TestGetPriority(t *testing.T) {
	tests := []struct {
		name         string
		msgType      string
		wantPriority MessagePriority
	}{
		{
			name:         "high priority - error",
			msgType:      string(MessageTypeError),
			wantPriority: PriorityHigh,
		},
		{
			name:         "high priority - disconnected",
			msgType:      string(MessageTypeDisconnected),
			wantPriority: PriorityHigh,
		},
		{
			name:         "normal priority - event",
			msgType:      string(MessageTypeEvent),
			wantPriority: PriorityNormal,
		},
		{
			name:         "low priority - connected",
			msgType:      string(MessageTypeConnected),
			wantPriority: PriorityLow,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			msg := &Message{Type: tt.msgType}
			priority := GetPriority(msg)
			assert.Equal(t, tt.wantPriority, priority)
		})
	}
}

// TestPriorityQueue_Enqueue tests enqueueing messages
func TestPriorityQueue_Enqueue(t *testing.T) {
	queue := NewPriorityQueue()

	highMsg := &Message{Type: string(MessageTypeError)}
	normalMsg := &Message{Type: string(MessageTypeEvent)}
	lowMsg := &Message{Type: string(MessageTypeConnected)}

	queue.Enqueue(highMsg, PriorityHigh)
	queue.Enqueue(normalMsg, PriorityNormal)
	queue.Enqueue(lowMsg, PriorityLow)

	assert.Equal(t, 3, queue.Len())

	// Verify queues have correct messages via stats
	stats := queue.GetStats()
	typed460, ok := stats["high_priority"].(int)
	require.True(t, ok)
	assert.Equal(t, 1, typed460)
	typed461, ok := stats["normal_priority"].(int)
	require.True(t, ok)
	assert.Equal(t, 1, typed461)
	typed462, ok := stats["low_priority"].(int)
	require.True(t, ok)
	assert.Equal(t, 1, typed462)
}

// TestPriorityQueue_Dequeue tests dequeueing in priority order
func TestPriorityQueue_Dequeue(t *testing.T) {
	queue := NewPriorityQueue()

	// Enqueue in mixed order
	lowMsg := &Message{Type: string(MessageTypeConnected)}
	normalMsg := &Message{Type: string(MessageTypeEvent)}
	highMsg := &Message{Type: string(MessageTypeError)}

	queue.Enqueue(lowMsg, PriorityLow)
	queue.Enqueue(normalMsg, PriorityNormal)
	queue.Enqueue(highMsg, PriorityHigh)

	// Dequeue should return high first
	msg := queue.Dequeue()
	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeError), msg.Type)

	// Then normal
	msg = queue.Dequeue()
	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeEvent), msg.Type)

	// Then low
	msg = queue.Dequeue()
	require.NotNil(t, msg)
	assert.Equal(t, string(MessageTypeConnected), msg.Type)

	// Empty queue
	msg = queue.Dequeue()
	assert.Nil(t, msg)
}

// TestPriorityQueue_Len tests length calculation
func TestPriorityQueue_Len(t *testing.T) {
	queue := NewPriorityQueue()
	assert.Equal(t, 0, queue.Len())

	queue.Enqueue(&Message{Type: string(MessageTypeError)}, PriorityHigh)
	assert.Equal(t, 1, queue.Len())

	queue.Enqueue(&Message{Type: string(MessageTypeEvent)}, PriorityNormal)
	assert.Equal(t, 2, queue.Len())

	queue.Enqueue(&Message{Type: string(MessageTypeConnected)}, PriorityLow)
	assert.Equal(t, 3, queue.Len())

	queue.Dequeue()
	assert.Equal(t, 2, queue.Len())

	queue.Dequeue()
	queue.Dequeue()
	assert.Equal(t, 0, queue.Len())
}

// TestPriorityQueue_GetStats tests statistics
func TestPriorityQueue_GetStats(t *testing.T) {
	queue := NewPriorityQueue()

	// Add messages to each priority
	queue.Enqueue(&Message{Type: string(MessageTypeError)}, PriorityHigh)
	queue.Enqueue(&Message{Type: string(MessageTypeError)}, PriorityHigh)
	queue.Enqueue(&Message{Type: string(MessageTypeEvent)}, PriorityNormal)
	queue.Enqueue(&Message{Type: string(MessageTypeConnected)}, PriorityLow)

	stats := queue.GetStats()
	typed531, ok := stats["high_priority"].(int)
	require.True(t, ok)
	assert.Equal(t, 2, typed531)
	typed532, ok := stats["normal_priority"].(int)
	require.True(t, ok)
	assert.Equal(t, 1, typed532)
	typed533, ok := stats["low_priority"].(int)
	require.True(t, ok)
	assert.Equal(t, 1, typed533)
	typed534, ok := stats["total"].(int)
	require.True(t, ok)
	assert.Equal(t, 4, typed534)
}
