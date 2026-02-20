package websocket

import (
	"log/slog"
	"sync"
	"time"
)

// BackpressureStrategy defines how to handle backpressure
type BackpressureStrategy string

const (
	// StrategyDrop drops oldest messages when buffer is full
	StrategyDrop BackpressureStrategy = "drop"

	// StrategyQueue queues messages and blocks if buffer is full
	StrategyQueue BackpressureStrategy = "queue"

	// StrategySample samples messages (keeps every Nth message)
	StrategySample BackpressureStrategy = "sample"

	// StrategyThrottle throttles message sending rate
	StrategyThrottle BackpressureStrategy = "throttle"

	backpressureResetDelay    = 10 * time.Millisecond
	backpressureBufferSize    = 256
	backpressureSampleRate    = 5
	backpressureThrottleRate  = 100 * time.Millisecond
	backpressureDropThreshold = 0.8
	backpressurePercentScale  = 100
)

// BackpressureConfig configures backpressure handling
type BackpressureConfig struct {
	Strategy      BackpressureStrategy
	BufferSize    int
	SampleRate    int           // For sample strategy: keep 1 out of N messages
	ThrottleRate  time.Duration // For throttle strategy: min time between messages
	DropThreshold float64       // Drop messages if buffer is > this % full (0.0-1.0)
}

// DefaultBackpressureConfig returns default configuration
func DefaultBackpressureConfig() *BackpressureConfig {
	return &BackpressureConfig{
		Strategy:      StrategyDrop,
		BufferSize:    backpressureBufferSize,
		SampleRate:    backpressureSampleRate,
		ThrottleRate:  backpressureThrottleRate,
		DropThreshold: backpressureDropThreshold,
	}
}

// BackpressureHandler handles backpressure for a client
type BackpressureHandler struct {
	client       *Client
	config       *BackpressureConfig
	messageCount int64
	droppedCount int64
	lastSent     time.Time
	mu           sync.Mutex
}

// NewBackpressureHandler creates a new backpressure handler
func NewBackpressureHandler(client *Client, config *BackpressureConfig) *BackpressureHandler {
	if config == nil {
		config = DefaultBackpressureConfig()
	}

	return &BackpressureHandler{
		client:   client,
		config:   config,
		lastSent: time.Now().Add(-time.Hour), // Initialize to past so first message passes
	}
}

// CanSend checks if a message can be sent based on backpressure strategy
func (bh *BackpressureHandler) CanSend(_ *Message) bool {
	bh.mu.Lock()
	defer bh.mu.Unlock()

	bufferUsage := float64(len(bh.client.Send)) / float64(cap(bh.client.Send))

	switch bh.config.Strategy {
	case StrategyDrop:
		// Drop if buffer usage exceeds threshold
		if bufferUsage > bh.config.DropThreshold {
			bh.droppedCount++
			if bh.droppedCount%100 == 0 {
				slog.Warn("Client messages dropped",
					"client_id", bh.client.ID, "dropped_count", bh.droppedCount, "buffer_usage", bufferUsage*backpressurePercentScale)
			}
			return false
		}
		return true

	case StrategySample:
		// Sample: keep 1 out of N messages
		bh.messageCount++
		if bh.messageCount%int64(bh.config.SampleRate) != 0 {
			bh.droppedCount++
			return false
		}
		return true

	case StrategyThrottle:
		// Throttle: enforce minimum time between messages
		now := time.Now()
		if now.Sub(bh.lastSent) < bh.config.ThrottleRate {
			bh.droppedCount++
			return false
		}
		bh.lastSent = now
		return true

	case StrategyQueue:
		// Queue: always accept (will block if buffer is full)
		return true

	default:
		return true
	}
}

// Send sends a message with backpressure handling
func (bh *BackpressureHandler) Send(msg *Message) bool {
	if !bh.CanSend(msg) {
		return false
	}

	select {
	case bh.client.Send <- msg:
		bh.mu.Lock()
		bh.messageCount++
		bh.mu.Unlock()
		return true
	default:
		// Buffer full, handle based on strategy
		if bh.config.Strategy == StrategyQueue {
			// Block until space available
			bh.client.Send <- msg
			bh.mu.Lock()
			bh.messageCount++
			bh.mu.Unlock()
			return true
		}

		// For other strategies, drop the message
		bh.mu.Lock()
		bh.droppedCount++
		bh.mu.Unlock()
		return false
	}
}

// GetStats returns backpressure statistics
func (bh *BackpressureHandler) GetStats() map[string]interface{} {
	bh.mu.Lock()
	defer bh.mu.Unlock()

	bufferUsage := float64(len(bh.client.Send)) / float64(cap(bh.client.Send))

	return map[string]interface{}{
		"strategy":         bh.config.Strategy,
		"messages_sent":    bh.messageCount,
		"messages_dropped": bh.droppedCount,
		"buffer_size":      cap(bh.client.Send),
		"buffer_used":      len(bh.client.Send),
		"buffer_usage":     bufferUsage,
		"drop_rate":        float64(bh.droppedCount) / float64(bh.messageCount+bh.droppedCount),
	}
}

// Reset resets the backpressure handler statistics
func (bh *BackpressureHandler) Reset() {
	bh.mu.Lock()
	defer bh.mu.Unlock()

	bh.messageCount = 0
	bh.droppedCount = 0
	bh.lastSent = time.Now()
}

// MessageBatcher batches messages to reduce overhead
type MessageBatcher struct {
	messages  []*Message
	maxSize   int
	maxWait   time.Duration
	lastFlush time.Time
	mu        sync.Mutex
	flushChan chan struct{}
}

// NewMessageBatcher creates a new message batcher
func NewMessageBatcher(maxSize int, maxWait time.Duration) *MessageBatcher {
	return &MessageBatcher{
		messages:  make([]*Message, 0, maxSize),
		maxSize:   maxSize,
		maxWait:   maxWait,
		lastFlush: time.Now(),
		flushChan: make(chan struct{}, 1),
	}
}

// Add adds a message to the batch
func (mb *MessageBatcher) Add(msg *Message) bool {
	mb.mu.Lock()
	defer mb.mu.Unlock()

	mb.messages = append(mb.messages, msg)

	// Check if we should flush
	shouldFlush := len(mb.messages) >= mb.maxSize ||
		time.Since(mb.lastFlush) >= mb.maxWait

	if shouldFlush {
		select {
		case mb.flushChan <- struct{}{}:
		default:
			// Flush already pending
		}
	}

	return shouldFlush
}

// Flush returns and clears the current batch
func (mb *MessageBatcher) Flush() []*Message {
	mb.mu.Lock()
	defer mb.mu.Unlock()

	if len(mb.messages) == 0 {
		return nil
	}

	batch := mb.messages
	mb.messages = make([]*Message, 0, mb.maxSize)
	mb.lastFlush = time.Now()

	return batch
}

// FlushChan returns the flush notification channel
func (mb *MessageBatcher) FlushChan() <-chan struct{} {
	return mb.flushChan
}

// RateLimiter implements a token bucket rate limiter
type RateLimiter struct {
	rate       float64 // Messages per second
	burst      int     // Maximum burst size
	tokens     float64 // Current tokens
	lastUpdate time.Time
	mu         sync.Mutex
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(rate float64, burst int) *RateLimiter {
	return &RateLimiter{
		rate:       rate,
		burst:      burst,
		tokens:     float64(burst),
		lastUpdate: time.Now(),
	}
}

// Allow checks if a message can be sent
func (rl *RateLimiter) Allow() bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(rl.lastUpdate).Seconds()
	rl.lastUpdate = now

	// Add tokens based on elapsed time
	rl.tokens += elapsed * rl.rate
	if rl.tokens > float64(rl.burst) {
		rl.tokens = float64(rl.burst)
	}

	// Check if we have tokens available
	if rl.tokens >= 1.0 {
		rl.tokens -= 1.0
		return true
	}

	return false
}

// Wait waits until a message can be sent
func (rl *RateLimiter) Wait() {
	for !rl.Allow() {
		time.Sleep(backpressureResetDelay)
	}
}

// GetStats returns rate limiter statistics
func (rl *RateLimiter) GetStats() map[string]interface{} {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	return map[string]interface{}{
		"rate":             rl.rate,
		"burst":            rl.burst,
		"available_tokens": rl.tokens,
	}
}

// PriorityQueue implements a priority queue for messages
type PriorityQueue struct {
	high   []*Message
	normal []*Message
	low    []*Message
	mu     sync.Mutex
}

// NewPriorityQueue creates a new priority queue
func NewPriorityQueue() *PriorityQueue {
	return &PriorityQueue{
		high:   make([]*Message, 0),
		normal: make([]*Message, 0),
		low:    make([]*Message, 0),
	}
}

// MessagePriority represents message priority
type MessagePriority int

const (
	// PriorityLow is the lowest message priority.
	PriorityLow MessagePriority = 0
	// PriorityNormal is the default message priority.
	PriorityNormal MessagePriority = 1
	// PriorityHigh is the highest message priority.
	PriorityHigh MessagePriority = 2
)

// GetPriority determines message priority based on type
func GetPriority(msg *Message) MessagePriority {
	switch MessageType(msg.Type) {
	case MessageTypeError, MessageTypeDisconnected, MessageTypePresenceEditing:
		return PriorityHigh
	case MessageTypeEvent, MessageTypeItemUpdated, MessageTypeLinkCreated:
		return PriorityNormal
	case MessageTypeConnected,
		MessageTypePing,
		MessageTypePong,
		MessageTypeSubscribe,
		MessageTypeUnsubscribe,
		MessageTypeSubscribed,
		MessageTypeUnsubscribed,
		MessageTypeSubscriptionError,
		MessageTypeItemCreated,
		MessageTypeItemDeleted,
		MessageTypeItemStatusChanged,
		MessageTypeItemPriorityChanged,
		MessageTypeLinkUpdated,
		MessageTypeLinkDeleted,
		MessageTypeProjectCreated,
		MessageTypeProjectUpdated,
		MessageTypeProjectDeleted,
		MessageTypeAgentStarted,
		MessageTypeAgentStopped,
		MessageTypeAgentActivity,
		MessageTypeAgentError,
		MessageTypePresenceJoin,
		MessageTypePresenceLeave,
		MessageTypePresenceUpdate,
		MessageTypePresenceViewing,
		MessageTypeSnapshot,
		MessageTypeRollback,
		MessageTypeSync,
		MessageTypeHeartbeat,
		MessageTypeStats,
		MessageTypeAck:
		return PriorityLow
	}
	return PriorityNormal
}

// Enqueue adds a message to the queue
func (pq *PriorityQueue) Enqueue(msg *Message, priority MessagePriority) {
	pq.mu.Lock()
	defer pq.mu.Unlock()

	switch priority {
	case PriorityHigh:
		pq.high = append(pq.high, msg)
	case PriorityNormal:
		pq.normal = append(pq.normal, msg)
	case PriorityLow:
		pq.low = append(pq.low, msg)
	}
}

// Dequeue removes and returns the highest priority message
func (pq *PriorityQueue) Dequeue() *Message {
	pq.mu.Lock()
	defer pq.mu.Unlock()

	// Try high priority first
	if len(pq.high) > 0 {
		msg := pq.high[0]
		pq.high = pq.high[1:]
		return msg
	}

	// Then normal priority
	if len(pq.normal) > 0 {
		msg := pq.normal[0]
		pq.normal = pq.normal[1:]
		return msg
	}

	// Finally low priority
	if len(pq.low) > 0 {
		msg := pq.low[0]
		pq.low = pq.low[1:]
		return msg
	}

	return nil
}

// Len returns the total number of messages
func (pq *PriorityQueue) Len() int {
	pq.mu.Lock()
	defer pq.mu.Unlock()

	return len(pq.high) + len(pq.normal) + len(pq.low)
}

// GetStats returns queue statistics
func (pq *PriorityQueue) GetStats() map[string]interface{} {
	pq.mu.Lock()
	defer pq.mu.Unlock()

	return map[string]interface{}{
		"high_priority":   len(pq.high),
		"normal_priority": len(pq.normal),
		"low_priority":    len(pq.low),
		"total":           len(pq.high) + len(pq.normal) + len(pq.low),
	}
}
