package middleware

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"

	"github.com/kooshapari/tracertm-backend/internal/resilience"
)

const (
	defaultResilienceTimeout       = 30 * time.Second
	defaultResilienceMaxConcurrent = 1000
	resiliencePercentScale         = 100.0
)

// ResilienceConfig holds configuration for resilience middleware
type ResilienceConfig struct {
	// CircuitBreakerEnabled enables circuit breaker protection
	CircuitBreakerEnabled bool

	// RetryEnabled enables automatic retries
	RetryEnabled bool

	// RetryPolicy defines the retry policy
	RetryPolicy resilience.RetryPolicy

	// Timeout is the maximum time to wait for a request
	Timeout time.Duration

	// MaxConcurrentRequests limits concurrent requests per endpoint
	MaxConcurrentRequests int
}

// DefaultResilienceConfig returns the default resilience configuration
func DefaultResilienceConfig() ResilienceConfig {
	return ResilienceConfig{
		CircuitBreakerEnabled: true,
		RetryEnabled:          false, // Retries are opt-in per endpoint
		RetryPolicy:           resilience.DefaultRetryPolicy(),
		Timeout:               defaultResilienceTimeout,
		MaxConcurrentRequests: defaultResilienceMaxConcurrent,
	}
}

// ResilienceMiddleware creates middleware for resilience patterns
func ResilienceMiddleware(config ResilienceConfig) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()

			// Apply timeout
			if config.Timeout > 0 {
				var cancel context.CancelFunc
				ctx, cancel = context.WithTimeout(ctx, config.Timeout)
				defer cancel()
				c.SetRequest(c.Request().WithContext(ctx))
			}

			// Execute with circuit breaker if enabled
			if config.CircuitBreakerEnabled {
				serviceName := "endpoint-" + c.Request().Method + "-" + c.Path()
				manager := resilience.GetGlobalManager()

				_, err := manager.ExecuteWithContext(ctx, serviceName, func() (interface{}, error) {
					return nil, next(c)
				})
				if err != nil {
					// Check if circuit breaker is open
					state := manager.GetState(serviceName)
					if state.String() == "open" {
						return echo.NewHTTPError(
							http.StatusServiceUnavailable,
							"service temporarily unavailable (circuit breaker open)",
						)
					}
					return err
				}
				return nil
			}

			// No circuit breaker, execute directly
			return next(c)
		}
	}
}

// RetryMiddleware creates middleware for automatic retries (opt-in)
func RetryMiddleware(policy resilience.RetryPolicy) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()

			err := resilience.RetryWithPolicy(ctx, policy, func() error {
				return next(c)
			})

			return err
		}
	}
}

// TimeoutMiddleware creates middleware for request timeouts
func TimeoutMiddleware(timeout time.Duration) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			ctx := c.Request().Context()
			ctx, cancel := context.WithTimeout(ctx, timeout)
			defer cancel()

			c.SetRequest(c.Request().WithContext(ctx))

			done := make(chan error, 1)
			go func() {
				done <- next(c)
			}()

			select {
			case err := <-done:
				return err
			case <-ctx.Done():
				return echo.NewHTTPError(
					http.StatusGatewayTimeout,
					fmt.Sprintf("request timeout after %v", timeout),
				)
			}
		}
	}
}

// ConcurrencyLimiter creates middleware to limit concurrent requests
func ConcurrencyLimiter(maxConcurrent int) echo.MiddlewareFunc {
	semaphore := make(chan struct{}, maxConcurrent)

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			select {
			case semaphore <- struct{}{}:
				defer func() { <-semaphore }()
				return next(c)
			default:
				return echo.NewHTTPError(
					http.StatusTooManyRequests,
					"too many concurrent requests, please try again later",
				)
			}
		}
	}
}

// GracefulDegradationMiddleware provides graceful degradation support
func GracefulDegradationMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			err := next(c)
			if err != nil {
				// Check if error is retryable
				if isRetryableError(err) {
					// Add header to indicate degraded service
					c.Response().Header().Set("X-Service-Status", "degraded")
					c.Response().Header().Set("X-Degradation-Reason", err.Error())
				}
			}
			return err
		}
	}
}

// isRetryableError checks if an error is retryable
func isRetryableError(err error) bool {
	httpErr := &echo.HTTPError{}
	if errors.As(err, &httpErr) {
		switch httpErr.Code {
		case http.StatusServiceUnavailable,
			http.StatusGatewayTimeout,
			http.StatusBadGateway,
			http.StatusTooManyRequests:
			return true
		}
	}
	return false
}

// ErrorBudgetMiddleware tracks error budget for SLO monitoring
type ErrorBudgetMiddleware struct {
	window        time.Duration
	errorBudget   float64 // Percentage (0-1)
	errorCount    int
	totalRequests int
	windowStart   time.Time
}

// NewErrorBudgetMiddleware creates a new error budget middleware
func NewErrorBudgetMiddleware(window time.Duration, errorBudget float64) *ErrorBudgetMiddleware {
	return &ErrorBudgetMiddleware{
		window:      window,
		errorBudget: errorBudget,
		windowStart: time.Now(),
	}
}

// Middleware returns the Echo middleware function
func (ebm *ErrorBudgetMiddleware) Middleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Check if window has expired
			if time.Since(ebm.windowStart) > ebm.window {
				// Reset counters
				ebm.errorCount = 0
				ebm.totalRequests = 0
				ebm.windowStart = time.Now()
			}

			ebm.totalRequests++

			err := next(c)
			// Track errors
			if err != nil {
				ebm.errorCount++

				// Check if error budget is exceeded
				errorRate := float64(ebm.errorCount) / float64(ebm.totalRequests)
				if errorRate > ebm.errorBudget {
					slog.Warn("Error budget exceeded",
						"error_rate", errorRate*resiliencePercentScale, "budget", ebm.errorBudget*resiliencePercentScale)
				}
			}

			return err
		}
	}
}

// ResilienceHealthCheckSkipper skips resilience middleware for health check endpoints
// Note: Use existing HealthCheckSkipper from middleware.go instead for consistency
func ResilienceHealthCheckSkipper(c echo.Context) bool {
	path := c.Path()
	return path == "/health" ||
		path == "/ready" ||
		path == "/live" ||
		path == "/metrics"
}
