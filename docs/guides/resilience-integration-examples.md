# Resilience Integration Examples

## Quick Start Integration

### 1. Backend Service with Circuit Breaker and Retry

```go
package services

import (
    "context"
    "github.com/kooshapari/tracertm-backend/internal/resilience"
)

type GitHubService struct {
    client *http.Client
}

func (s *GitHubService) GetUser(ctx context.Context, username string) (*User, error) {
    // Combine circuit breaker AND retry for robust error handling
    policy := resilience.DefaultRetryPolicy()

    result, err := resilience.RetryWithPolicyAndResult(ctx, policy, func() (*User, error) {
        // Circuit breaker wraps the actual API call
        return resilience.ExecuteWithContext(ctx, "github-api", func() (interface{}, error) {
            // Your actual API call here
            resp, err := s.client.Get(fmt.Sprintf("https://api.github.com/users/%s", username))
            if err != nil {
                return nil, err
            }
            defer resp.Body.Close()

            var user User
            if err := json.NewDecoder(resp.Body).Decode(&user); err != nil {
                return nil, err
            }
            return &user, nil
        })
    })

    if err != nil {
        return nil, err
    }

    return result.(*User), nil
}
```

### 2. Frontend API Call with Resilience

```typescript
// services/github.ts
import { globalRegistry } from '@/lib/resilience/CircuitBreaker';
import { RetryPolicies } from '@/lib/resilience/RetryPolicy';

export class GitHubService {
  async getUser(username: string): Promise<User> {
    // Circuit breaker + automatic retry
    return await globalRegistry.execute('github-api', async () => {
      return await RetryPolicies.default.execute(async () => {
        const response = await fetch(`/api/github/users/${username}`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
      });
    });
  }
}
```

### 3. HTTP Handler with Resilience Middleware

```go
package main

import (
    "github.com/kooshapari/tracertm-backend/internal/middleware"
    "github.com/labstack/echo/v4"
)

func setupServer() *echo.Echo {
    e := echo.New()

    // Apply resilience middleware
    e.Use(middleware.ResilienceMiddleware(middleware.ResilienceConfig{
        CircuitBreakerEnabled: true,
        Timeout:               30 * time.Second,
        MaxConcurrentRequests: 1000,
    }))

    // Apply timeout middleware for long operations
    longRunningGroup := e.Group("/long-running")
    longRunningGroup.Use(middleware.TimeoutMiddleware(5 * time.Minute))

    // Apply concurrency limiter for expensive endpoints
    expensiveGroup := e.Group("/expensive")
    expensiveGroup.Use(middleware.ConcurrencyLimiter(10))

    return e
}
```

### 4. Health Check Setup

```go
package main

import (
    "github.com/kooshapari/tracertm-backend/internal/health"
    "github.com/kooshapari/tracertm-backend/internal/handlers"
)

func setupHealthChecks(e *echo.Echo, deps *Dependencies) {
    // Create health checker
    healthChecker := health.NewHealthChecker(
        deps.DB.DB,
        deps.Redis,
        os.Getenv("PYTHON_BACKEND_URL"),
        os.Getenv("TEMPORAL_URL"),
        os.Getenv("APP_VERSION"),
    )

    // Create health handler
    healthHandler := handlers.NewHealthHandler(
        deps.DB,
        deps.Redis,
        deps.NATS,
        deps.Cache,
        deps.PythonClient,
        os.Getenv("PYTHON_BACKEND_URL"),
    )

    // Register health endpoints
    e.GET("/health", healthHandler.GetHealthComprehensive)
    e.GET("/ready", healthHandler.GetHealthReadiness)
    e.GET("/live", healthHandler.GetHealthLiveness)
    e.GET("/startup", healthHandler.GetHealthStartup)
    e.GET("/circuit-breakers", healthHandler.GetCircuitBreakerStates)
}
```

---

## Advanced Patterns

### 1. Service with Custom Circuit Breaker Config

```go
package services

import (
    "github.com/kooshapari/tracertm-backend/internal/resilience"
    "github.com/sony/gobreaker"
)

func NewCriticalService() *CriticalService {
    // Create custom circuit breaker for critical service
    config := resilience.CircuitBreakerConfig{
        MaxRequests:   2,  // Allow 2 test requests in half-open
        Interval:      5 * time.Second,  // Shorter failure window
        Timeout:       15 * time.Second, // Shorter recovery timeout
        ReadyToTrip: func(counts gobreaker.Counts) bool {
            // More aggressive: trip after 3 failures
            return counts.ConsecutiveFailures >= 3
        },
        OnStateChange: func(name string, from, to gobreaker.State) {
            log.Printf("🚨 Critical service [%s]: %s -> %s", name, from, to)
            // Send critical alert
            alerting.SendCriticalAlert(name, from, to)
        },
    }

    manager := resilience.NewCircuitBreakerManagerWithConfig(config)

    return &CriticalService{
        circuitBreaker: manager,
    }
}
```

### 2. Idempotent Operation with Retry

```go
func (s *PaymentService) ProcessPayment(ctx context.Context, payment *Payment) error {
    policy := resilience.AggressiveRetryPolicy()  // Use aggressive for critical ops

    return resilience.RetryWithPolicy(ctx, policy, func() error {
        // Generate idempotency key for safe retries
        idempotencyKey := resilience.IdempotencyKey(payment.ID, payment.Attempt)

        // Circuit breaker + idempotent request
        _, err := resilience.ExecuteWithContext(ctx, "payment-processor", func() (interface{}, error) {
            req, _ := http.NewRequest("POST", s.baseURL+"/process", payment.ToJSON())
            resilience.WithIdempotencyKey(req, idempotencyKey)

            resp, err := s.client.Do(req)
            if err != nil {
                return nil, err
            }
            defer resp.Body.Close()

            if resp.StatusCode >= 500 {
                return nil, fmt.Errorf("payment processor error: %d", resp.StatusCode)
            }

            return nil, nil
        })

        return err
    })
}
```

### 3. Graceful Degradation with Fallback

```go
func (s *RecommendationService) GetRecommendations(ctx context.Context, userID string) ([]Recommendation, error) {
    // Try AI-powered recommendations with circuit breaker
    recommendations, err := resilience.ExecuteWithContext(ctx, "ai-service", func() (interface{}, error) {
        return s.aiService.GetRecommendations(ctx, userID)
    })

    if err != nil {
        log.Warn("AI recommendations unavailable, falling back to rule-based")

        // Fallback to rule-based recommendations
        return s.getRuleBasedRecommendations(ctx, userID)
    }

    return recommendations.([]Recommendation), nil
}

func (s *RecommendationService) getRuleBasedRecommendations(ctx context.Context, userID string) ([]Recommendation, error) {
    // Try cache first
    if cached, err := s.cache.Get(ctx, "recommendations:"+userID); err == nil {
        return cached.([]Recommendation), nil
    }

    // Generate simple rule-based recommendations
    return s.generateSimpleRecommendations(userID), nil
}
```

### 4. Frontend Circuit Breaker with State Notifications

```typescript
import { CircuitBreakerRegistry } from '@/lib/resilience/CircuitBreaker';

// Create custom registry with notifications
const registry = new CircuitBreakerRegistry({
  failureThreshold: 5,
  failureWindow: 10000,
  resetTimeout: 30000,
  successThreshold: 2,
  onStateChange: (from, to) => {
    // Show user notification
    if (to === 'open') {
      toast.error('Service temporarily unavailable. Retrying...');
    } else if (to === 'closed') {
      toast.success('Service restored!');
    }
  },
});

// Use in API calls
export async function fetchData() {
  try {
    return await registry.execute('api-service', async () => {
      const response = await fetch('/api/data');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    });
  } catch (error) {
    if (error.message.includes('Circuit breaker is OPEN')) {
      // Show degraded UI
      return getCachedData();
    }
    throw error;
  }
}
```

### 5. Error Budget Tracking

```go
func setupErrorBudget(e *echo.Echo) {
    // Track error budget per endpoint
    budgets := map[string]*middleware.ErrorBudgetMiddleware{
        "/api/v1/critical": middleware.NewErrorBudgetMiddleware(
            1*time.Hour,  // Window
            0.001,        // 0.1% error budget (strict)
        ),
        "/api/v1/standard": middleware.NewErrorBudgetMiddleware(
            1*time.Hour,
            0.01,  // 1% error budget (normal)
        ),
    }

    for path, budget := range budgets {
        group := e.Group(path)
        group.Use(budget.Middleware())
    }
}
```

---

## Testing Examples

### 1. Test Circuit Breaker Behavior

```go
func TestServiceWithCircuitBreaker(t *testing.T) {
    service := NewGitHubService()

    // Trigger failures to open circuit
    for i := 0; i < 5; i++ {
        _, err := service.GetUser(context.Background(), "nonexistent")
        assert.Error(t, err)
    }

    // Verify circuit is open
    state := resilience.GetGlobalManager().GetState("github-api")
    assert.Equal(t, gobreaker.StateOpen, state)

    // Next request should fail immediately
    _, err := service.GetUser(context.Background(), "user")
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "circuit breaker")
}
```

### 2. Test Retry Policy

```go
func TestServiceWithRetry(t *testing.T) {
    attempts := 0
    service := &TestService{
        call: func() error {
            attempts++
            if attempts < 3 {
                return errors.New("temporary failure")
            }
            return nil
        },
    }

    err := service.CallWithRetry(context.Background())

    assert.NoError(t, err)
    assert.Equal(t, 3, attempts)  // Succeeded on 3rd attempt
}
```

### 3. Test Health Checks

```go
func TestHealthCheck(t *testing.T) {
    healthChecker := health.NewHealthChecker(db, redis, pythonURL, temporalURL, "v1.0.0")

    report := healthChecker.Check(context.Background())

    assert.Equal(t, health.HealthStatusHealthy, report.Status)
    assert.Equal(t, "v1.0.0", report.Version)

    // Verify all components checked
    assert.Contains(t, report.Components, "database")
    assert.Contains(t, report.Components, "redis")
    assert.Equal(t, health.HealthStatusHealthy, report.Components["database"].Status)
}
```

---

## Monitoring Integration

### 1. Prometheus Metrics

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    circuitBreakerState = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "circuit_breaker_state",
            Help: "Circuit breaker state (0=closed, 1=open, 2=half-open)",
        },
        []string{"service"},
    )

    retryAttempts = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "retry_attempts_total",
            Help: "Total number of retry attempts",
        },
        []string{"service"},
    )
)

func trackCircuitBreakerState(serviceName string, state gobreaker.State) {
    stateValue := 0.0
    switch state {
    case gobreaker.StateOpen:
        stateValue = 1.0
    case gobreaker.StateHalfOpen:
        stateValue = 2.0
    }
    circuitBreakerState.WithLabelValues(serviceName).Set(stateValue)
}
```

### 2. Sentry Integration

```go
import "github.com/getsentry/sentry-go"

config := resilience.CircuitBreakerConfig{
    OnStateChange: func(name string, from, to gobreaker.State) {
        if to == gobreaker.StateOpen {
            // Report to Sentry
            sentry.CaptureMessage(fmt.Sprintf("Circuit breaker [%s] opened", name))
        }
    },
}
```

---

## Best Practices Checklist

✅ Use circuit breakers for all external service calls
✅ Combine circuit breakers with retry policies
✅ Implement idempotency keys for retryable operations
✅ Set appropriate timeouts for all operations
✅ Provide fallback mechanisms for non-critical features
✅ Monitor circuit breaker states
✅ Track error budgets
✅ Test failure scenarios
✅ Document circuit breaker behavior
✅ Set up alerting for circuit breaker state changes

---

## Common Patterns

### Pattern 1: Critical External API

```
Circuit Breaker → Aggressive Retry → Idempotency → API Call
```

### Pattern 2: Non-Critical Feature

```
Circuit Breaker → Conservative Retry → Fallback → Cache/Default
```

### Pattern 3: User-Facing Endpoint

```
Timeout → Circuit Breaker → Default Retry → Graceful Error
```

### Pattern 4: Background Job

```
Conservative Retry → Circuit Breaker → Queue for Retry
```

---

## Next Steps

1. Review [Production Hardening Guide](./production-hardening-guide.md)
2. Check [Quick Reference](../reference/resilience-quick-reference.md)
3. Implement circuit breakers in your services
4. Add health checks to your handlers
5. Set up monitoring and alerting
6. Test failure scenarios
7. Document your resilience strategy

---

## Support

- GitHub Issues: Report bugs and request features
- Documentation: See full guide for detailed information
- Slack: #engineering-support for questions
