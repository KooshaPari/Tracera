// Package health provides health checks and reporting.
package health

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/shirou/gopsutil/v4/disk"
	"github.com/shirou/gopsutil/v4/mem"
)

// Status represents the health status of a component.
type Status string

const (
	// StatusHealthy indicates the component is operating normally.
	StatusHealthy Status = "healthy"
	// StatusDegraded indicates the component is operating but with reduced capacity.
	StatusDegraded Status = "degraded"
	// StatusUnhealthy indicates the component is not operating correctly.
	StatusUnhealthy Status = "unhealthy"
)

// ComponentHealth represents the health of a single component.
type ComponentHealth struct {
	Name      string    `json:"name"`
	Status    Status    `json:"status"`
	Message   string    `json:"message,omitempty"`
	Timestamp time.Time `json:"timestamp"`
	LatencyMs int64     `json:"latency_ms,omitempty"`
}

// Report represents the overall health report.
type Report struct {
	Status     Status                     `json:"status"`
	Version    string                     `json:"version"`
	Timestamp  time.Time                  `json:"timestamp"`
	Components map[string]ComponentHealth `json:"components"`
	Metrics    map[string]interface{}     `json:"metrics,omitempty"`
}

// Checker performs health checks on various components.
type Checker struct {
	db          *sql.DB
	redisClient *redis.Client
	pythonURL   string
	temporalURL string
	version     string

	// Thresholds
	diskThreshold   float64 // Percentage (0-100)
	memoryThreshold float64 // Percentage (0-100)
}

const (
	defaultDiskThreshold   = 90.0
	defaultMemoryThreshold = 85.0
	diskWarningDelta       = 10.0

	dbCheckTimeout       = 5 * time.Second
	redisCheckTimeout    = 3 * time.Second
	pythonCheckTimeout   = 5 * time.Second
	temporalCheckTimeout = 5 * time.Second
	readinessTimeout     = 2 * time.Second

	dbLatencyDegradedMs       = 1000
	redisLatencyDegradedMs    = 500
	pythonLatencyDegradedMs   = 2000
	temporalLatencyDegradedMs = 2000

	connectionOKMessage = "connection ok"

	bytesPerGiB = 1024.0 * 1024.0 * 1024.0
)

// NewChecker creates a new health checker
func NewChecker(db *sql.DB, redisClient *redis.Client, pythonURL, temporalURL, version string) *Checker {
	return &Checker{
		db:              db,
		redisClient:     redisClient,
		pythonURL:       pythonURL,
		temporalURL:     temporalURL,
		version:         version,
		diskThreshold:   defaultDiskThreshold,   // Alert if disk usage > threshold
		memoryThreshold: defaultMemoryThreshold, // Alert if memory usage > threshold
	}
}

// Check performs all health checks and returns a comprehensive report
func (hc *Checker) Check(ctx context.Context) Report {
	components := make(map[string]ComponentHealth)
	var wg sync.WaitGroup
	var mu sync.Mutex

	// Run all checks in parallel
	checks := []func(context.Context) ComponentHealth{
		hc.CheckDatabase,
		hc.CheckRedis,
		hc.CheckPythonBackend,
		hc.CheckTemporal,
		hc.CheckDiskSpace,
		hc.CheckMemory,
	}

	for _, check := range checks {
		wg.Add(1)
		go func(checkFn func(context.Context) ComponentHealth) {
			defer wg.Done()
			result := checkFn(ctx)
			mu.Lock()
			components[result.Name] = result
			mu.Unlock()
		}(check)
	}

	wg.Wait()

	// Determine overall status
	overallStatus := StatusHealthy
	for _, component := range components {
		if component.Status == StatusUnhealthy {
			overallStatus = StatusUnhealthy
			break
		}
		if component.Status == StatusDegraded && overallStatus == StatusHealthy {
			overallStatus = StatusDegraded
		}
	}

	return Report{
		Status:     overallStatus,
		Version:    hc.version,
		Timestamp:  time.Now(),
		Components: components,
		Metrics:    hc.collectMetrics(ctx),
	}
}

// CheckDatabase checks database connectivity
func (hc *Checker) CheckDatabase(ctx context.Context) ComponentHealth {
	start := time.Now()

	if hc.db == nil {
		return ComponentHealth{
			Name:      "database",
			Status:    StatusUnhealthy,
			Message:   "database not configured",
			Timestamp: time.Now(),
		}
	}

	// Set timeout for database check
	checkCtx, cancel := context.WithTimeout(ctx, dbCheckTimeout)
	defer cancel()

	err := hc.db.PingContext(checkCtx)
	latency := time.Since(start).Milliseconds()

	if err != nil {
		return ComponentHealth{
			Name:      "database",
			Status:    StatusUnhealthy,
			Message:   fmt.Sprintf("connection failed: %v", err),
			Timestamp: time.Now(),
			LatencyMs: latency,
		}
	}

	// Check if latency is concerning
	status := StatusHealthy
	message := connectionOKMessage
	if latency > dbLatencyDegradedMs {
		status = StatusDegraded
		message = fmt.Sprintf("high latency: %dms", latency)
	}

	return ComponentHealth{
		Name:      "database",
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
		LatencyMs: latency,
	}
}

// CheckRedis checks Redis connectivity
func (hc *Checker) CheckRedis(ctx context.Context) ComponentHealth {
	start := time.Now()

	if hc.redisClient == nil {
		return ComponentHealth{
			Name:      "redis",
			Status:    StatusDegraded, // Redis is not critical
			Message:   "redis not configured",
			Timestamp: time.Now(),
		}
	}

	// Set timeout for Redis check
	checkCtx, cancel := context.WithTimeout(ctx, redisCheckTimeout)
	defer cancel()

	_, err := hc.redisClient.Ping(checkCtx).Result()
	latency := time.Since(start).Milliseconds()

	if err != nil {
		return ComponentHealth{
			Name:      "redis",
			Status:    StatusDegraded,
			Message:   fmt.Sprintf("connection failed: %v", err),
			Timestamp: time.Now(),
			LatencyMs: latency,
		}
	}

	status := StatusHealthy
	message := connectionOKMessage
	if latency > redisLatencyDegradedMs {
		status = StatusDegraded
		message = fmt.Sprintf("high latency: %dms", latency)
	}

	return ComponentHealth{
		Name:      "redis",
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
		LatencyMs: latency,
	}
}

func (hc *Checker) checkHTTPService(
	ctx context.Context,
	name string,
	baseURL string,
	path string,
	timeout time.Duration,
	errorStatus Status,
	nonOKStatus Status,
	latencyDegradedMs int64,
	notConfiguredMsg string,
) ComponentHealth {
	start := time.Now()

	if baseURL == "" {
		return componentHealth(name, StatusDegraded, notConfiguredMsg, 0)
	}

	checkCtx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(checkCtx, http.MethodGet, baseURL+path, nil)
	if err != nil {
		return componentHealth(name, errorStatus, fmt.Sprintf("request creation failed: %v", err), 0)
	}

	client := &http.Client{Timeout: timeout}
	resp, err := client.Do(req)
	latency := time.Since(start).Milliseconds()
	if err != nil {
		return componentHealth(name, errorStatus, fmt.Sprintf("connection failed: %v", err), latency)
	}
	defer func() {
		if err := resp.Body.Close(); err != nil {
			slog.Error("failed to close response body", "error", name, "error", err)
		}
	}()

	status, message := evaluateHTTPHealth(resp, latency, nonOKStatus, latencyDegradedMs)
	return componentHealth(name, status, message, latency)
}

func componentHealth(name string, status Status, message string, latency int64) ComponentHealth {
	return ComponentHealth{
		Name:      name,
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
		LatencyMs: latency,
	}
}

func evaluateHTTPHealth(
	resp *http.Response,
	latency int64,
	nonOKStatus Status,
	latencyDegradedMs int64,
) (Status, string) {
	status := StatusHealthy
	message := connectionOKMessage
	if resp.StatusCode != http.StatusOK {
		status = nonOKStatus
		message = fmt.Sprintf("unhealthy status: %d", resp.StatusCode)
	} else if latency > latencyDegradedMs {
		status = StatusDegraded
		message = fmt.Sprintf("high latency: %dms", latency)
	}
	return status, message
}

// CheckPythonBackend checks Python backend connectivity
func (hc *Checker) CheckPythonBackend(ctx context.Context) ComponentHealth {
	return hc.checkHTTPService(
		ctx,
		"python-backend",
		hc.pythonURL,
		"/health",
		pythonCheckTimeout,
		StatusUnhealthy,
		StatusUnhealthy,
		pythonLatencyDegradedMs,
		"python backend not configured",
	)
}

// CheckTemporal checks Temporal connectivity
func (hc *Checker) CheckTemporal(ctx context.Context) ComponentHealth {
	return hc.checkHTTPService(
		ctx,
		"temporal",
		hc.temporalURL,
		"/api/v1/health",
		temporalCheckTimeout,
		StatusDegraded,
		StatusDegraded,
		temporalLatencyDegradedMs,
		"temporal not configured",
	)
}

// CheckDiskSpace checks disk space usage
func (hc *Checker) CheckDiskSpace(ctx context.Context) ComponentHealth {
	usage, err := disk.UsageWithContext(ctx, "/")
	if err != nil {
		return ComponentHealth{
			Name:      "disk",
			Status:    StatusDegraded,
			Message:   fmt.Sprintf("failed to check disk: %v", err),
			Timestamp: time.Now(),
		}
	}

	usedPercent := usage.UsedPercent
	status := StatusHealthy
	message := fmt.Sprintf("%.1f%% used", usedPercent)

	if usedPercent >= hc.diskThreshold {
		status = StatusUnhealthy
		message = fmt.Sprintf("CRITICAL: %.1f%% used (threshold: %.1f%%)", usedPercent, hc.diskThreshold)
	} else if usedPercent >= hc.diskThreshold-diskWarningDelta {
		status = StatusDegraded
		message = fmt.Sprintf("WARNING: %.1f%% used", usedPercent)
	}

	return ComponentHealth{
		Name:      "disk",
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
	}
}

// CheckMemory checks memory usage
func (hc *Checker) CheckMemory(ctx context.Context) ComponentHealth {
	val, err := mem.VirtualMemoryWithContext(ctx)
	if err != nil {
		return ComponentHealth{
			Name:      "memory",
			Status:    StatusDegraded,
			Message:   fmt.Sprintf("failed to check memory: %val", err),
			Timestamp: time.Now(),
		}
	}

	usedPercent := val.UsedPercent
	status := StatusHealthy
	message := fmt.Sprintf("%.1f%% used", usedPercent)

	if usedPercent >= hc.memoryThreshold {
		status = StatusUnhealthy
		message = fmt.Sprintf("CRITICAL: %.1f%% used (threshold: %.1f%%)", usedPercent, hc.memoryThreshold)
	} else if usedPercent >= hc.memoryThreshold-diskWarningDelta {
		status = StatusDegraded
		message = fmt.Sprintf("WARNING: %.1f%% used", usedPercent)
	}

	return ComponentHealth{
		Name:      "memory",
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
	}
}

// collectMetrics collects additional metrics for the health report
func (hc *Checker) collectMetrics(ctx context.Context) map[string]interface{} {
	metrics := make(map[string]interface{})

	// Collect disk metrics
	if usage, err := disk.UsageWithContext(ctx, "/"); err == nil {
		metrics["disk_total_gb"] = float64(usage.Total) / bytesPerGiB
		metrics["disk_free_gb"] = float64(usage.Free) / bytesPerGiB
		metrics["disk_used_percent"] = usage.UsedPercent
	}

	// Collect memory metrics
	if v, err := mem.VirtualMemoryWithContext(ctx); err == nil {
		metrics["memory_total_gb"] = float64(v.Total) / bytesPerGiB
		metrics["memory_available_gb"] = float64(v.Available) / bytesPerGiB
		metrics["memory_used_percent"] = v.UsedPercent
	}

	return metrics
}

// LivenessProbe performs a simple liveness check
func (hc *Checker) LivenessProbe(_ context.Context) error {
	// Just check if the service is running
	// No external dependencies
	return nil
}

// ReadinessProbe performs a readiness check
func (hc *Checker) ReadinessProbe(ctx context.Context) error {
	// Check critical dependencies
	if hc.db == nil {
		return errors.New("database not configured")
	}

	checkCtx, cancel := context.WithTimeout(ctx, readinessTimeout)
	defer cancel()

	if err := hc.db.PingContext(checkCtx); err != nil {
		return fmt.Errorf("database not ready: %w", err)
	}

	return nil
}

// StartupProbe performs a startup check
func (hc *Checker) StartupProbe(ctx context.Context) error {
	// Similar to readiness but may have longer timeout
	return hc.ReadinessProbe(ctx)
}

// LogReport logs the health report
func LogReport(report Report) {
	slog.Info("🏥 Health Check (version )", "detail", report.Status, "version", report.Version)
	for name, component := range report.Components {
		statusIcon := "✅"
		switch component.Status {
		case StatusHealthy:
			statusIcon = "✅"
		case StatusDegraded:
			statusIcon = "⚠️"
		case StatusUnhealthy:
			statusIcon = "❌"
		}
		slog.Info("%s %s: %s - %s", "detail", statusIcon, "name", name, "detail", component.Status, "detail", component.Message)
	}
}
