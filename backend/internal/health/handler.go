package health

import (
	"context"
	"database/sql"
	"net/http"
	"sync"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"go.temporal.io/sdk/client"
)

// ComponentCheck represents health status of a single component
type ComponentCheck struct {
	Status    Status  `json:"status"`
	LatencyMs *int64  `json:"latency_ms,omitempty"`
	Message   *string `json:"message,omitempty"`
	Timestamp string  `json:"timestamp"`
}

// Response represents the overall health status
type Response struct {
	Status    Status                    `json:"status"`
	Timestamp string                    `json:"timestamp"`
	Checks    map[string]ComponentCheck `json:"checks"`
}

// Handler manages health checks
type Handler struct {
	db       *sql.DB
	redis    *redis.Client
	temporal client.Client
}

// NewHandler creates a new health check handler
func NewHandler(db *sql.DB, redis *redis.Client, temporal client.Client) *Handler {
	return &Handler{
		db:       db,
		redis:    redis,
		temporal: temporal,
	}
}

// Liveness returns a simple liveness check (always returns 200 if service is running)
func (h *Handler) Liveness(c echo.Context) error {
	response := Response{
		Status:    StatusHealthy,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Checks:    make(map[string]ComponentCheck),
	}

	return c.JSON(http.StatusOK, response)
}

// Readiness returns a comprehensive readiness check (200 only if all deps healthy)
func (h *Handler) Readiness(c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	response := Response{
		Status:    StatusHealthy,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Checks:    make(map[string]ComponentCheck),
	}

	// Run all checks in parallel
	checks := h.runAllChecks(ctx)
	response.Checks = checks

	// Determine overall status
	for _, check := range checks {
		if check.Status == StatusUnhealthy {
			response.Status = StatusUnhealthy
			return c.JSON(http.StatusServiceUnavailable, response)
		}
		if check.Status == StatusDegraded {
			response.Status = StatusDegraded
		}
	}

	statusCode := http.StatusOK
	switch response.Status {
	case StatusUnhealthy:
		statusCode = http.StatusServiceUnavailable
	case StatusDegraded, StatusHealthy:
		statusCode = http.StatusOK
	}

	return c.JSON(statusCode, response)
}

// runAllChecks runs all health checks in parallel
func (h *Handler) runAllChecks(ctx context.Context) map[string]ComponentCheck {
	checks := make(map[string]ComponentCheck)
	var mu sync.Mutex
	var wg sync.WaitGroup

	// Database
	wg.Add(1)
	go func() {
		defer wg.Done()
		check := h.checkDatabase(ctx)
		mu.Lock()
		checks["database"] = check
		mu.Unlock()
	}()

	// Redis
	wg.Add(1)
	go func() {
		defer wg.Done()
		check := h.checkRedis(ctx)
		mu.Lock()
		checks["redis"] = check
		mu.Unlock()
	}()

	// Temporal
	wg.Add(1)
	go func() {
		defer wg.Done()
		check := h.checkTemporal(ctx)
		mu.Lock()
		checks["temporal"] = check
		mu.Unlock()
	}()

	wg.Wait()
	return checks
}

// checkDatabase checks database connectivity
func (h *Handler) checkDatabase(ctx context.Context) ComponentCheck {
	start := time.Now()
	check := ComponentCheck{
		Status:    StatusHealthy,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}

	if h.db == nil {
		check.Status = StatusUnhealthy
		msg := "database connection not initialized"
		check.Message = &msg
		return check
	}

	if err := h.db.PingContext(ctx); err != nil {
		check.Status = StatusUnhealthy
		msg := err.Error()
		check.Message = &msg
		return check
	}

	latency := time.Since(start).Milliseconds()
	check.LatencyMs = &latency
	return check
}

// checkRedis checks Redis connectivity
func (h *Handler) checkRedis(ctx context.Context) ComponentCheck {
	start := time.Now()
	check := ComponentCheck{
		Status:    StatusHealthy,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}

	if h.redis == nil {
		check.Status = StatusUnhealthy
		msg := "redis client not initialized"
		check.Message = &msg
		return check
	}

	if err := h.redis.Ping(ctx).Err(); err != nil {
		check.Status = StatusUnhealthy
		msg := err.Error()
		check.Message = &msg
		return check
	}

	latency := time.Since(start).Milliseconds()
	check.LatencyMs = &latency
	return check
}

// checkTemporal checks Temporal workflow client connectivity
func (h *Handler) checkTemporal(ctx context.Context) ComponentCheck {
	start := time.Now()
	check := ComponentCheck{
		Status:    StatusHealthy,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}

	if h.temporal == nil {
		check.Status = StatusDegraded
		msg := "temporal client not initialized"
		check.Message = &msg
		return check
	}

	// GetWorkflowHistory is a safe read-only operation to test connectivity
	// If Temporal is down, this will timeout or error
	_, err := h.temporal.CheckHealth(ctx, &client.CheckHealthRequest{})
	if err != nil {
		check.Status = StatusDegraded
		msg := err.Error()
		check.Message = &msg
		return check
	}

	latency := time.Since(start).Milliseconds()
	check.LatencyMs = &latency
	return check
}

// RegisterRoutes registers health check routes on the provided router
func RegisterRoutes(router *echo.Echo, db *sql.DB, redis *redis.Client, temporal client.Client) {
	handler := NewHandler(db, redis, temporal)

	router.GET("/health", handler.Liveness)
	router.GET("/health/live", handler.Liveness)
	router.GET("/health/ready", handler.Readiness)
}
