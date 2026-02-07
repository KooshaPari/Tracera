package ratelimit

import (
	"context"
	"errors"
	"strconv"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/sony/gobreaker"
)

// PriorityLevel defines request priority for queue management
type PriorityLevel int

const (
	// PriorityLow indicates lowest request priority.
	PriorityLow PriorityLevel = iota
	// PriorityNormal indicates default request priority.
	PriorityNormal
	// PriorityHigh indicates elevated request priority.
	PriorityHigh
	// PriorityAdmin indicates administrative request priority.
	PriorityAdmin
)

const (
	defaultBaseTimeout   = 30 * time.Second
	defaultMaxConcurrent = 1000

	defaultQueueSizeLow    = 100
	defaultQueueSizeNormal = 500
	defaultQueueSizeHigh   = 1000
	defaultQueueSizeAdmin  = 100

	defaultLoadThreshold  = 0.8
	defaultThrottleFactor = 0.5

	semaphoreShareDenominator = 10
	semaphoreShareAdmin       = 1
	semaphoreShareHigh        = 3
	semaphoreShareNormal      = 5
	semaphoreShareLow         = 1

	requeueWaitDuration = 100 * time.Millisecond
	processLoopSleep    = 10 * time.Millisecond

	loadMonitorInterval = 5 * time.Second
	redisLoadTimeout    = 1 * time.Second
	redisMetricsTTL     = 10 * time.Second

	loadNormalizationBase  = 1.0
	loadThrottleMultiplier = 0.5

	priorityAdminTimeoutMultiplier = 2.0
	priorityHighTimeoutMultiplier  = 1.5
	priorityLowTimeoutMultiplier   = 0.5
)

// ThrottleConfig configures the adaptive throttling behavior
type ThrottleConfig struct {
	// Redis client for distributed state
	Redis *redis.Client

	// Circuit breaker for backend health monitoring
	CircuitBreaker *gobreaker.CircuitBreaker

	// Base request timeout
	BaseTimeout time.Duration

	// Maximum concurrent requests
	MaxConcurrent int

	// Queue sizes per priority level
	QueueSizes map[PriorityLevel]int

	// Backend load threshold (0.0-1.0)
	LoadThreshold float64

	// Throttle factor when load exceeds threshold
	ThrottleFactor float64
}

// AdaptiveThrottler implements intelligent request throttling
// based on backend load, circuit breaker state, and priority queuing
type AdaptiveThrottler struct {
	config ThrottleConfig

	// Per-priority semaphores for concurrent request control
	semaphores map[PriorityLevel]chan struct{}

	// Per-priority queues for waiting requests
	queues map[PriorityLevel]*priorityQueue

	// Current backend load (0.0-1.0)
	currentLoad float64
	loadMu      sync.RWMutex

	// Throttle state
	isThrottling bool
	throttleMu   sync.RWMutex

	// Metrics
	totalRequests     int64
	throttledRequests int64
	queuedRequests    int64
	metricsMu         sync.RWMutex

	// Shutdown control
	done chan struct{}
}

// priorityQueue implements a simple FIFO queue with size limits
type priorityQueue struct {
	items   chan *throttleRequest
	maxSize int
}

type throttleRequest struct {
	ctx      context.Context
	priority PriorityLevel
	acquired chan bool
}

// NewAdaptiveThrottler creates a new adaptive throttler
func NewAdaptiveThrottler(config ThrottleConfig) *AdaptiveThrottler {
	// Set defaults
	if config.BaseTimeout == 0 {
		config.BaseTimeout = defaultBaseTimeout
	}
	if config.MaxConcurrent == 0 {
		config.MaxConcurrent = defaultMaxConcurrent
	}
	if config.QueueSizes == nil {
		config.QueueSizes = map[PriorityLevel]int{
			PriorityLow:    defaultQueueSizeLow,
			PriorityNormal: defaultQueueSizeNormal,
			PriorityHigh:   defaultQueueSizeHigh,
			PriorityAdmin:  defaultQueueSizeAdmin,
		}
	}
	if config.LoadThreshold == 0 {
		config.LoadThreshold = defaultLoadThreshold
	}
	if config.ThrottleFactor == 0 {
		config.ThrottleFactor = defaultThrottleFactor
	}

	at := &AdaptiveThrottler{
		config:     config,
		semaphores: make(map[PriorityLevel]chan struct{}),
		queues:     make(map[PriorityLevel]*priorityQueue),
		done:       make(chan struct{}),
	}

	// Initialize per-priority semaphores and queues
	for priority, queueSize := range config.QueueSizes {
		// Allocate semaphore slots proportionally by priority
		var slots int
		switch priority {
		case PriorityAdmin:
			slots = config.MaxConcurrent * semaphoreShareAdmin / semaphoreShareDenominator // 10% for admin
		case PriorityHigh:
			slots = config.MaxConcurrent * semaphoreShareHigh / semaphoreShareDenominator // 30% for high
		case PriorityNormal:
			slots = config.MaxConcurrent * semaphoreShareNormal / semaphoreShareDenominator // 50% for normal
		case PriorityLow:
			slots = config.MaxConcurrent * semaphoreShareLow / semaphoreShareDenominator // 10% for low
		}

		// Ensure at least 1 slot per priority if MaxConcurrent > 0
		if slots == 0 && config.MaxConcurrent > 0 {
			slots = 1
		}

		at.semaphores[priority] = make(chan struct{}, slots)
		at.queues[priority] = &priorityQueue{
			items:   make(chan *throttleRequest, queueSize),
			maxSize: queueSize,
		}
	}

	// Start background workers
	go at.monitorBackendLoad()
	go at.processQueues()

	return at
}

// Acquire attempts to acquire a throttle token for a request
// Returns: timeout duration, release function, error
func (at *AdaptiveThrottler) Acquire(ctx context.Context, priority PriorityLevel) (time.Duration, func(), error) {
	at.metricsMu.Lock()
	at.totalRequests++
	at.metricsMu.Unlock()

	// Check circuit breaker state
	if at.config.CircuitBreaker != nil {
		state := at.config.CircuitBreaker.State()
		if state == gobreaker.StateOpen {
			// Circuit is open, throttle aggressively
			at.metricsMu.Lock()
			at.throttledRequests++
			at.metricsMu.Unlock()
			return 0, nil, errors.New("circuit breaker open: backend unavailable")
		}
	}

	// Calculate effective timeout based on load and throttling state
	timeout := at.calculateTimeout(priority)

	// Try to acquire semaphore immediately
	select {
	case at.semaphores[priority] <- struct{}{}:
		// Acquired immediately
		release := func() {
			<-at.semaphores[priority]
		}
		return timeout, release, nil
	default:
		// Semaphore full, try queuing
		return at.enqueueRequest(ctx, priority, timeout)
	}
}

// enqueueRequest adds a request to the priority queue
func (at *AdaptiveThrottler) enqueueRequest(ctx context.Context, priority PriorityLevel, timeout time.Duration) (time.Duration, func(), error) {
	queue := at.queues[priority]

	req := &throttleRequest{
		ctx:      ctx,
		priority: priority,
		acquired: make(chan bool, 1),
	}

	// Try to enqueue
	select {
	case queue.items <- req:
		at.metricsMu.Lock()
		at.queuedRequests++
		at.metricsMu.Unlock()

		// Wait for queue to process or context cancellation
		select {
		case acquired := <-req.acquired:
			if !acquired {
				return 0, nil, errors.New("failed to acquire throttle token")
			}
			release := func() {
				<-at.semaphores[priority]
			}
			return timeout, release, nil
		case <-ctx.Done():
			return 0, nil, ctx.Err()
		case <-time.After(timeout):
			at.metricsMu.Lock()
			at.throttledRequests++
			at.metricsMu.Unlock()
			return 0, nil, errors.New("queue timeout exceeded")
		}
	default:
		// Queue full
		at.metricsMu.Lock()
		at.throttledRequests++
		at.metricsMu.Unlock()
		return 0, nil, errors.New("priority queue full: please retry later")
	}
}

// processQueues continuously processes queued requests by priority
func (at *AdaptiveThrottler) processQueues() {
	// Process priorities in order: Admin > High > Normal > Low
	priorities := []PriorityLevel{PriorityAdmin, PriorityHigh, PriorityNormal, PriorityLow}
	ticker := time.NewTicker(processLoopSleep)
	defer ticker.Stop()

	for {
		select {
		case <-at.done:
			return
		case <-ticker.C:
			// Try each priority level in order
			for _, priority := range priorities {
				// Process all available requests for this priority
				for {
					select {
					case req := <-at.queues[priority].items:
						// Check if request context is still valid
						select {
						case <-req.ctx.Done():
							// Context cancelled, skip this request
							select {
							case req.acquired <- false:
							default:
							}
							continue
						default:
						}

						// Try to acquire semaphore for queued request
						select {
						case at.semaphores[priority] <- struct{}{}:
							// Successfully acquired, notify the requester
							select {
							case req.acquired <- true:
							default:
								// This shouldn't happen since we use buffered channel
								<-at.semaphores[priority]
							}
						default:
							// Semaphore full, re-queue the request
							select {
							case at.queues[priority].items <- req:
							default:
								// Queue is full, reject the request
								select {
								case req.acquired <- false:
								default:
								}
							}
							// Stop trying to process more from this queue
							goto nextPriority
						}
					default:
						// No more items in this queue
						goto nextPriority
					}
				}
			nextPriority:
			}
		}
	}
}

// calculateTimeout computes the effective timeout based on current conditions
func (at *AdaptiveThrottler) calculateTimeout(priority PriorityLevel) time.Duration {
	at.throttleMu.RLock()
	isThrottling := at.isThrottling
	at.throttleMu.RUnlock()

	at.loadMu.RLock()
	load := at.currentLoad
	at.loadMu.RUnlock()

	baseTimeout := at.config.BaseTimeout

	// Adjust timeout based on throttling state
	if isThrottling {
		baseTimeout = time.Duration(float64(baseTimeout) * at.config.ThrottleFactor)
	}

	// Further adjust based on load
	if load > at.config.LoadThreshold {
		loadFactor := (load - at.config.LoadThreshold) / (loadNormalizationBase - at.config.LoadThreshold)
		baseTimeout = time.Duration(float64(baseTimeout) * (loadNormalizationBase - loadFactor*loadThrottleMultiplier))
	}

	// Priority multipliers
	switch priority {
	case PriorityAdmin:
		baseTimeout = time.Duration(float64(baseTimeout) * priorityAdminTimeoutMultiplier)
	case PriorityHigh:
		baseTimeout = time.Duration(float64(baseTimeout) * priorityHighTimeoutMultiplier)
	case PriorityNormal:
		// Keep base timeout.
	case PriorityLow:
		baseTimeout = time.Duration(float64(baseTimeout) * priorityLowTimeoutMultiplier)
	}

	return baseTimeout
}

// monitorBackendLoad continuously monitors backend health and adjusts throttling
func (at *AdaptiveThrottler) monitorBackendLoad() {
	ticker := time.NewTicker(loadMonitorInterval)
	defer ticker.Stop()

	for {
		select {
		case <-at.done:
			return
		case <-ticker.C:
			load := at.measureBackendLoad()

			at.loadMu.Lock()
			at.currentLoad = load
			at.loadMu.Unlock()

			// Update throttling state
			shouldThrottle := load > at.config.LoadThreshold
			if at.config.CircuitBreaker != nil && at.config.CircuitBreaker.State() != gobreaker.StateClosed {
				shouldThrottle = true
			}

			at.throttleMu.Lock()
			at.isThrottling = shouldThrottle
			at.throttleMu.Unlock()
		}
	}
}

// measureBackendLoad estimates current backend load
func (at *AdaptiveThrottler) measureBackendLoad() float64 {
	if at.config.Redis == nil {
		return 0.0
	}

	ctx, cancel := context.WithTimeout(context.Background(), redisLoadTimeout)
	defer cancel()

	// Use Redis to track backend load metrics
	// This is a simplified implementation - in production, integrate with actual metrics
	key := "throttle:backend:load"

	// Get current concurrent requests across all priorities
	totalSlots := 0
	usedSlots := 0
	for priority, sem := range at.semaphores {
		capacity := cap(sem)
		// Calculate used slots as capacity minus available tokens in channel
		available := len(sem)
		used := capacity - available
		totalSlots += capacity
		usedSlots += used

		// Store per-priority metrics
		at.config.Redis.Set(ctx, key+":"+strconv.Itoa(int(priority)), used, redisMetricsTTL)
	}

	if totalSlots == 0 {
		return 0.0
	}

	load := float64(usedSlots) / float64(totalSlots)

	// Store aggregate load
	at.config.Redis.Set(ctx, key, load, redisMetricsTTL)

	return load
}

// GetMetrics returns current throttler metrics
func (at *AdaptiveThrottler) GetMetrics() map[string]interface{} {
	at.metricsMu.RLock()
	defer at.metricsMu.RUnlock()

	at.loadMu.RLock()
	load := at.currentLoad
	at.loadMu.RUnlock()

	at.throttleMu.RLock()
	isThrottling := at.isThrottling
	at.throttleMu.RUnlock()

	return map[string]interface{}{
		"total_requests":     at.totalRequests,
		"throttled_requests": at.throttledRequests,
		"queued_requests":    at.queuedRequests,
		"current_load":       load,
		"is_throttling":      isThrottling,
		"circuit_state":      at.getCircuitState(),
	}
}

// getCircuitState returns the current circuit breaker state
func (at *AdaptiveThrottler) getCircuitState() string {
	if at.config.CircuitBreaker == nil {
		return "none"
	}

	switch at.config.CircuitBreaker.State() {
	case gobreaker.StateClosed:
		return "closed"
	case gobreaker.StateHalfOpen:
		return "half-open"
	case gobreaker.StateOpen:
		return "open"
	default:
		return "unknown"
	}
}

// Close cleanly shuts down the throttler and stops background workers
func (at *AdaptiveThrottler) Close() error {
	close(at.done)
	return nil
}
