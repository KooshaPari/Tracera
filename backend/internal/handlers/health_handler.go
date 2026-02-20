package handlers

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/clients"
	"github.com/kooshapari/tracertm-backend/internal/health"
	"github.com/kooshapari/tracertm-backend/internal/nats"
	"github.com/kooshapari/tracertm-backend/internal/resilience"
)

const (
	healthHTTPTimeout             = 5 * time.Second
	healthDBTimeout               = 3 * time.Second
	healthRedisTimeout            = 3 * time.Second
	healthPythonTimeout           = 5 * time.Second
	healthDBLatencyDegradedMs     = 1000
	healthRedisLatencyDegradedMs  = 500
	healthNatsLatencyDegradedMs   = 500
	healthPythonLatencyDegradedMs = 2000

	// Health status messages
	healthMessageHighLatency = "High latency detected"
)

// ComponentHealth represents the health status of a single component
type ComponentHealth struct {
	Status    string  `json:"status"` // "healthy", "degraded", "unhealthy"
	Message   string  `json:"message,omitempty"`
	LatencyMs float64 `json:"latency_ms,omitempty"`
	LastCheck string  `json:"last_check"`
}

// IntegrationHealth represents cross-backend integration health status
type IntegrationHealth struct {
	PythonBackend ComponentHealth `json:"python_backend"`
	NATS          ComponentHealth `json:"nats"`
	Redis         ComponentHealth `json:"redis"`
	Database      ComponentHealth `json:"database"`
}

// HealthHandlerResponse represents the complete health check response
type HealthHandlerResponse struct {
	Status      string                     `json:"status"` // Overall status
	Version     string                     `json:"version"`
	Timestamp   string                     `json:"timestamp"`
	Components  map[string]ComponentHealth `json:"components"`
	Integration *IntegrationHealth         `json:"integration,omitempty"`
}

// HealthHandler manages health check operations
type HealthHandler struct {
	db             *pgxpool.Pool
	redis          *redis.Client
	nats           *nats.Client
	cache          cache.Cache
	pythonClient   *clients.PythonServiceClient
	pythonURL      string
	httpClient     *http.Client
	healthChecker  *health.Checker
	circuitBreaker *resilience.CircuitBreakerManager
	startTime      time.Time
}

// NewHealthHandler creates a new health handler
func NewHealthHandler(
	db *pgxpool.Pool,
	redis *redis.Client,
	natsClient *nats.Client,
	cache cache.Cache,
	pythonClient *clients.PythonServiceClient,
	pythonURL string,
) *HealthHandler {
	// Note: health checker will use nil for database as pgxpool doesn't expose sql.DB
	// Database health checks will be done directly via the pool in this handler
	var sqlDB *sql.DB

	// Create comprehensive health checker
	healthChecker := health.NewChecker(
		sqlDB,
		redis,
		pythonURL,
		os.Getenv("TEMPORAL_URL"),
		getVersion(),
	)

	return &HealthHandler{
		db:           db,
		redis:        redis,
		nats:         natsClient,
		cache:        cache,
		pythonClient: pythonClient,
		pythonURL:    pythonURL,
		httpClient: &http.Client{
			Timeout: healthHTTPTimeout,
		},
		healthChecker:  healthChecker,
		circuitBreaker: resilience.GetGlobalManager(),
		startTime:      time.Now(),
	}
}

// GetHealth returns comprehensive health status
func (h *HealthHandler) GetHealth(c echo.Context) error {
	ctx := c.Request().Context()

	response := HealthHandlerResponse{
		Status:      healthStatusHealthy,
		Version:     getVersion(),
		Timestamp:   time.Now().UTC().Format(time.RFC3339),
		Components:  make(map[string]ComponentHealth),
		Integration: nil,
	}

	// Check database
	response.Components["database"] = h.checkDatabase(ctx)

	// Check Redis
	response.Components["redis"] = h.checkRedis(ctx)

	// Check NATS
	response.Components["nats"] = h.checkNATS(ctx)

	// Check Python backend (required)
	response.Components["python_backend"] = h.checkPythonBackend(ctx)
	integration := &IntegrationHealth{
		Database:      response.Components["database"],
		Redis:         response.Components["redis"],
		NATS:          response.Components["nats"],
		PythonBackend: response.Components["python_backend"],
	}
	response.Integration = integration

	// Set overall status based on component health
	for _, comp := range response.Components {
		if comp.Status == healthStatusUnhealthy {
			response.Status = healthStatusUnhealthy
			break
		} else if comp.Status == healthStatusDegraded {
			response.Status = healthStatusDegraded
		}
	}

	// Return 503 if unhealthy
	statusCode := http.StatusOK
	if response.Status == healthStatusUnhealthy {
		statusCode = http.StatusServiceUnavailable
	}

	return c.JSON(statusCode, response)
}

// checkDatabase verifies database connectivity
func (h *HealthHandler) checkDatabase(ctx context.Context) ComponentHealth {
	start := time.Now()

	if h.db == nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   "Database pool not initialized",
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	// Ping database with timeout
	ctx, cancel := context.WithTimeout(ctx, healthDBTimeout)
	defer cancel()

	err := h.db.Ping(ctx)
	latency := time.Since(start).Milliseconds()

	if err != nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   fmt.Sprintf("Database ping failed: %v", err),
			LatencyMs: float64(latency),
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	// Check if latency is too high (degraded performance)
	status := healthStatusHealthy
	message := ""
	if latency > healthDBLatencyDegradedMs {
		status = healthStatusDegraded
		message = healthMessageHighLatency
	}

	return ComponentHealth{
		Status:    status,
		Message:   message,
		LatencyMs: float64(latency),
		LastCheck: time.Now().UTC().Format(time.RFC3339),
	}
}

// checkRedis verifies Redis connectivity
func (h *HealthHandler) checkRedis(ctx context.Context) ComponentHealth {
	start := time.Now()

	if h.redis == nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   "Redis not initialized",
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	// Ping Redis with timeout
	ctx, cancel := context.WithTimeout(ctx, healthRedisTimeout)
	defer cancel()

	err := h.redis.Ping(ctx).Err()
	latency := time.Since(start).Milliseconds()

	if err != nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   fmt.Sprintf("Redis ping failed: %v", err),
			LatencyMs: float64(latency),
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	status := healthStatusHealthy
	message := ""
	if latency > healthRedisLatencyDegradedMs {
		status = healthStatusDegraded
		message = healthMessageHighLatency
	}

	return ComponentHealth{
		Status:    status,
		Message:   message,
		LatencyMs: float64(latency),
		LastCheck: time.Now().UTC().Format(time.RFC3339),
	}
}

// checkNATS verifies NATS connectivity
func (h *HealthHandler) checkNATS(ctx context.Context) ComponentHealth {
	start := time.Now()

	if h.nats == nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   "NATS not initialized",
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	// Check NATS health
	err := h.nats.HealthCheck(ctx)
	latency := time.Since(start).Milliseconds()

	if err != nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   fmt.Sprintf("NATS health check failed: %v", err),
			LatencyMs: float64(latency),
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	status := healthStatusHealthy
	message := ""
	if latency > healthNatsLatencyDegradedMs {
		status = healthStatusDegraded
		message = healthMessageHighLatency
	}

	return ComponentHealth{
		Status:    status,
		Message:   message,
		LatencyMs: float64(latency),
		LastCheck: time.Now().UTC().Format(time.RFC3339),
	}
}

// checkPythonBackend verifies Python backend connectivity
func (handler *HealthHandler) checkPythonBackend(ctx context.Context) ComponentHealth {
	start := time.Now()

	if handler.pythonURL == "" {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   "Python backend URL not configured",
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	// Create request with timeout
	ctx, cancel := context.WithTimeout(ctx, healthPythonTimeout)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, handler.pythonURL+"/health", nil)
	if err != nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   fmt.Sprintf("Failed to create request: %v", err),
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	resp, err := handler.httpClient.Do(req)
	latency := time.Since(start).Milliseconds()

	if err != nil {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   fmt.Sprintf("Request failed: %v", err),
			LatencyMs: float64(latency),
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("failed to close health check response body", "error", err)
		}
	}()

	// Check status code
	if resp.StatusCode >= http.StatusInternalServerError {
		return ComponentHealth{
			Status:    healthStatusUnhealthy,
			Message:   fmt.Sprintf("HTTP %d", resp.StatusCode),
			LatencyMs: float64(latency),
			LastCheck: time.Now().UTC().Format(time.RFC3339),
		}
	}

	status := healthStatusHealthy
	message := ""
	if latency > healthPythonLatencyDegradedMs {
		status = healthStatusDegraded
		message = healthMessageHighLatency
	}

	return ComponentHealth{
		Status:    status,
		Message:   message,
		LatencyMs: float64(latency),
		LastCheck: time.Now().UTC().Format(time.RFC3339),
	}
}

// getVersion returns the application version from environment
func getVersion() string {
	version := os.Getenv("APP_VERSION")
	if version == "" {
		version = "dev"
	}
	return version
}

// GetHealthComprehensive returns comprehensive health check with all system metrics
func (handler *HealthHandler) GetHealthComprehensive(c echo.Context) error {
	ctx := c.Request().Context()

	// Use the new health checker for comprehensive report
	report := handler.healthChecker.Check(ctx)

	// Add circuit breaker states
	circuitStates := handler.circuitBreaker.GetAllStates()
	report.Metrics["circuit_breakers"] = circuitStates
	report.Metrics["circuit_breakers_healthy"] = handler.circuitBreaker.IsHealthy()

	statusCode := http.StatusOK
	if report.Status == health.StatusUnhealthy {
		statusCode = http.StatusServiceUnavailable
	}

	return c.JSON(statusCode, report)
}

// GetHealthReadiness returns readiness probe (Kubernetes)
func (h *HealthHandler) GetHealthReadiness(c echo.Context) error {
	ctx := c.Request().Context()

	err := h.healthChecker.ReadinessProbe(ctx)
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status":  "not_ready",
			"message": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"status": "ready",
	})
}

// GetHealthLiveness returns liveness probe (Kubernetes)
func (h *HealthHandler) GetHealthLiveness(c echo.Context) error {
	ctx := c.Request().Context()

	err := h.healthChecker.LivenessProbe(ctx)
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status":  "not_alive",
			"message": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"status": "alive",
	})
}

// GetHealthStartup returns startup probe (Kubernetes)
func (h *HealthHandler) GetHealthStartup(c echo.Context) error {
	ctx := c.Request().Context()

	err := h.healthChecker.StartupProbe(ctx)
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status":  "starting",
			"message": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"status": "started",
	})
}

// GetCircuitBreakerStates returns the current state of all circuit breakers
func (h *HealthHandler) GetCircuitBreakerStates(c echo.Context) error {
	states := h.circuitBreaker.GetAllStates()

	return c.JSON(http.StatusOK, map[string]interface{}{
		"circuit_breakers": states,
		"all_healthy":      h.circuitBreaker.IsHealthy(),
	})
}
