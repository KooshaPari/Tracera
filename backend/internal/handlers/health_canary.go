package handlers

import (
	"context"
	"net/http"
	"os"
	"time"

	"github.com/labstack/echo/v4"
)

// Health status constants
const (
	healthStatusHealthy   = "healthy"
	healthStatusUnhealthy = "unhealthy"
	healthStatusDegraded  = "degraded"
	envCanaryDeployment   = "true"
)

// CanaryHealthResponse extends health response with canary-specific metrics
type CanaryHealthResponse struct {
	Status      string                     `json:"status"`
	Version     string                     `json:"version"`
	Timestamp   string                     `json:"timestamp"`
	Deployment  DeploymentInfo             `json:"deployment"`
	Components  map[string]ComponentHealth `json:"components"`
	Integration *IntegrationHealth         `json:"integration,omitempty"`
	Metrics     *CanaryMetrics             `json:"metrics,omitempty"`
}

// DeploymentInfo contains deployment-specific information
type DeploymentInfo struct {
	Type      string `json:"type"` // "stable" or "canary"
	ImageTag  string `json:"image_tag"`
	StartTime string `json:"start_time"`
	Uptime    string `json:"uptime"`
}

// CanaryMetrics contains canary-specific performance metrics
type CanaryMetrics struct {
	RequestCount    int64   `json:"request_count"`
	ErrorCount      int64   `json:"error_count"`
	ErrorRate       float64 `json:"error_rate"`
	AvgLatencyMs    float64 `json:"avg_latency_ms"`
	P95LatencyMs    float64 `json:"p95_latency_ms"`
	P99LatencyMs    float64 `json:"p99_latency_ms"`
	MemoryUsageMB   float64 `json:"memory_usage_mb"`
	CPUUsagePercent float64 `json:"cpu_usage_percent"`
}

// GetCanaryHealth returns enhanced health status with canary metrics
func (handler *HealthHandler) GetCanaryHealth(echoCtx echo.Context) error {
	ctx := echoCtx.Request().Context()

	// Determine deployment type
	isCanary := os.Getenv("CANARY_DEPLOYMENT") == envCanaryDeployment
	deploymentType := "stable"
	if isCanary {
		deploymentType = "canary"
	}

	response := CanaryHealthResponse{
		Status:    healthStatusHealthy,
		Version:   getVersion(),
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Deployment: DeploymentInfo{
			Type:      deploymentType,
			ImageTag:  os.Getenv("APP_VERSION"),
			StartTime: handler.startTime.UTC().Format(time.RFC3339),
			Uptime:    time.Since(handler.startTime).String(),
		},
		Components:  make(map[string]ComponentHealth),
		Integration: nil,
		Metrics:     nil,
	}

	// Check all components
	response.Components["database"] = handler.checkDatabase(ctx)
	response.Components["redis"] = handler.checkRedis(ctx)
	response.Components["nats"] = handler.checkNATS(ctx)
	response.Components["python_backend"] = handler.checkPythonBackend(ctx)

	// Integration health
	integration := &IntegrationHealth{
		Database:      response.Components["database"],
		Redis:         response.Components["redis"],
		NATS:          response.Components["nats"],
		PythonBackend: response.Components["python_backend"],
	}
	response.Integration = integration

	// Add canary-specific metrics if this is a canary deployment
	if isCanary {
		response.Metrics = handler.getCanaryMetrics(ctx)
	}

	// Set overall status
	for _, comp := range response.Components {
		if comp.Status == healthStatusUnhealthy {
			response.Status = healthStatusUnhealthy
			break
		} else if comp.Status == healthStatusDegraded {
			response.Status = healthStatusDegraded
		}
	}

	// Return appropriate status code
	statusCode := http.StatusOK
	if response.Status == healthStatusUnhealthy {
		statusCode = http.StatusServiceUnavailable
	}

	return echoCtx.JSON(statusCode, response)
}

// getCanaryMetrics retrieves canary-specific performance metrics
func (handler *HealthHandler) getCanaryMetrics(_ context.Context) *CanaryMetrics {
	// In a real implementation, these would be fetched from metrics collectors
	// For now, return placeholder values
	return &CanaryMetrics{
		RequestCount:    0,
		ErrorCount:      0,
		ErrorRate:       0.0,
		AvgLatencyMs:    0.0,
		P95LatencyMs:    0.0,
		P99LatencyMs:    0.0,
		MemoryUsageMB:   0.0,
		CPUUsagePercent: 0.0,
	}
}

// GetReadiness returns readiness status for Kubernetes probes
func (handler *HealthHandler) GetReadiness(echoCtx echo.Context) error {
	ctx := echoCtx.Request().Context()

	// Check critical dependencies
	dbHealth := handler.checkDatabase(ctx)

	if dbHealth.Status == healthStatusUnhealthy {
		return echoCtx.JSON(http.StatusServiceUnavailable, map[string]string{
			"status":  "not_ready",
			"message": "database not available",
		})
	}

	return echoCtx.JSON(http.StatusOK, map[string]string{
		"status": "ready",
	})
}

// GetLiveness returns liveness status for Kubernetes probes
func (handler *HealthHandler) GetLiveness(echoCtx echo.Context) error {
	// Simple liveness check - just return OK if the service is running
	return echoCtx.JSON(http.StatusOK, map[string]string{
		"status": "alive",
	})
}
