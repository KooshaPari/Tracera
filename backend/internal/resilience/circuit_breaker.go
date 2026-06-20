// Package resilience provides circuit breaker and retry utilities.
package resilience

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/sony/gobreaker"
)

const (
	circuitBreakerDefaultInterval = 10 * time.Second
	circuitBreakerDefaultTimeout  = 30 * time.Second
)

// CircuitBreakerConfig holds configuration for circuit breakers
type CircuitBreakerConfig struct {
	// MaxRequests is the maximum number of requests allowed to pass through
	// when the circuit breaker is half-open
	MaxRequests uint32

	// Interval is the cyclic period of the closed state
	// for the circuit breaker to clear the internal counts
	Interval time.Duration

	// Timeout is the period of the open state
	// after which the state becomes half-open
	Timeout time.Duration

	// ReadyToTrip returns true when the circuit breaker should trip
	ReadyToTrip func(counts gobreaker.Counts) bool

	// OnStateChange is called whenever the state of the circuit breaker changes
	OnStateChange func(name string, from gobreaker.State, to gobreaker.State)
}

// CircuitBreakerManager manages multiple circuit breakers for different services
type CircuitBreakerManager struct {
	breakers map[string]*gobreaker.CircuitBreaker
	mu       sync.RWMutex
	config   CircuitBreakerConfig
}

// NewCircuitBreakerManager creates a new circuit breaker manager with default config
func NewCircuitBreakerManager() *CircuitBreakerManager {
	return &CircuitBreakerManager{
		breakers: make(map[string]*gobreaker.CircuitBreaker),
		config:   DefaultCircuitBreakerConfig(),
	}
}

// NewCircuitBreakerManagerWithConfig creates a new circuit breaker manager with custom config
func NewCircuitBreakerManagerWithConfig(config CircuitBreakerConfig) *CircuitBreakerManager {
	return &CircuitBreakerManager{
		breakers: make(map[string]*gobreaker.CircuitBreaker),
		config:   config,
	}
}

// DefaultCircuitBreakerConfig returns the default circuit breaker configuration
func DefaultCircuitBreakerConfig() CircuitBreakerConfig {
	return CircuitBreakerConfig{
		MaxRequests: 1, // Only allow 1 test request in half-open state
		Interval:    circuitBreakerDefaultInterval,
		Timeout:     circuitBreakerDefaultTimeout,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			// Trip after 5 consecutive failures OR
			// 5 failures in the last 10 seconds with >50% failure rate
			failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
			return counts.ConsecutiveFailures >= 5 ||
				(counts.TotalFailures >= 5 && failureRatio >= 0.5)
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			slog.Info("⚡ Circuit breaker [ ] state changed ->", "name", name, "detail", from, "detail", to)
			// Note: Alert notifications (Slack/email) not yet implemented for production
		},
	}
}

// GetOrCreateBreaker gets or creates a circuit breaker for the given service
func (m *CircuitBreakerManager) GetOrCreateBreaker(serviceName string) *gobreaker.CircuitBreaker {
	m.mu.RLock()
	breaker, exists := m.breakers[serviceName]
	m.mu.RUnlock()

	if exists {
		return breaker
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	// Double-check after acquiring write lock
	if breaker, exists := m.breakers[serviceName]; exists {
		return breaker
	}

	// Create new circuit breaker
	settings := gobreaker.Settings{
		Name:        serviceName,
		MaxRequests: m.config.MaxRequests,
		Interval:    m.config.Interval,
		Timeout:     m.config.Timeout,
		ReadyToTrip: m.config.ReadyToTrip,
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			if m.config.OnStateChange != nil {
				m.config.OnStateChange(name, from, to)
			}
		},
	}

	breaker = gobreaker.NewCircuitBreaker(settings)
	m.breakers[serviceName] = breaker

	slog.Info("✅ Created circuit breaker for service", "name", serviceName)
	return breaker
}

// Execute executes a function with circuit breaker protection
func (m *CircuitBreakerManager) Execute(serviceName string, fn func() (interface{}, error)) (interface{}, error) {
	breaker := m.GetOrCreateBreaker(serviceName)
	return breaker.Execute(fn)
}

// ExecuteWithContext executes a function with circuit breaker protection and context
func (m *CircuitBreakerManager) ExecuteWithContext(
	ctx context.Context, serviceName string, fn func() (interface{}, error),
) (interface{}, error) {
	// Check context before executing
	select {
	case <-ctx.Done():
		return nil, fmt.Errorf("context cancelled before execution: %w", ctx.Err())
	default:
	}

	breaker := m.GetOrCreateBreaker(serviceName)

	// Execute with timeout monitoring
	resultChan := make(chan interface{}, 1)
	errorChan := make(chan error, 1)

	go func() {
		result, err := breaker.Execute(fn)
		if err != nil {
			errorChan <- err
		} else {
			resultChan <- result
		}
	}()

	// Wait for result or context cancellation
	select {
	case result := <-resultChan:
		return result, nil
	case err := <-errorChan:
		return nil, err
	case <-ctx.Done():
		return nil, fmt.Errorf("context cancelled during execution: %w", ctx.Err())
	}
}

// GetState returns the current state of a circuit breaker
func (m *CircuitBreakerManager) GetState(serviceName string) gobreaker.State {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if breaker, exists := m.breakers[serviceName]; exists {
		return breaker.State()
	}
	return gobreaker.StateClosed // Default state
}

// GetCounts returns the current counts for a circuit breaker
func (m *CircuitBreakerManager) GetCounts(serviceName string) gobreaker.Counts {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if breaker, exists := m.breakers[serviceName]; exists {
		return breaker.Counts()
	}
	return gobreaker.Counts{} // Default empty counts
}

// GetAllStates returns the states of all circuit breakers
func (m *CircuitBreakerManager) GetAllStates() map[string]gobreaker.State {
	m.mu.RLock()
	defer m.mu.RUnlock()

	states := make(map[string]gobreaker.State)
	for name, breaker := range m.breakers {
		states[name] = breaker.State()
	}
	return states
}

// IsHealthy returns true if all circuit breakers are closed or half-open
func (m *CircuitBreakerManager) IsHealthy() bool {
	m.mu.RLock()
	defer m.mu.RUnlock()

	for _, breaker := range m.breakers {
		state := breaker.State()
		if state == gobreaker.StateOpen {
			return false
		}
	}
	return true
}

// Service name constants for circuit breakers
const (
	ServiceGitHub    = "github-api"
	ServiceLinear    = "linear-api"
	ServiceOpenAI    = "openai-api"
	ServiceAnthropic = "anthropic-api"
	ServicePython    = "python-backend"
	ServiceTemporal  = "temporal"
	ServiceRedis     = "redis"
	ServiceNeo4j     = "neo4j"
	ServiceS3        = "s3"
)

// Global circuit breaker manager instance
//
//nolint:gochecknoglobals // Singleton pattern for global access
var (
	globalManager     *CircuitBreakerManager
	globalManagerOnce sync.Once
)

// GetGlobalManager returns the global circuit breaker manager instance
func GetGlobalManager() *CircuitBreakerManager {
	globalManagerOnce.Do(func() {
		globalManager = NewCircuitBreakerManager()
	})
	return globalManager
}

// Execute is a convenience function that uses the global manager
func Execute(serviceName string, fn func() (interface{}, error)) (interface{}, error) {
	return GetGlobalManager().Execute(serviceName, fn)
}

// ExecuteWithContext is a convenience function that uses the global manager
func ExecuteWithContext(ctx context.Context, serviceName string, fn func() (interface{}, error)) (interface{}, error) {
	return GetGlobalManager().ExecuteWithContext(ctx, serviceName, fn)
}
