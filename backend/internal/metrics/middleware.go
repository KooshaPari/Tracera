package metrics

import (
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
)

const (
	errorRateDecayFactor = 0.95
	httpErrorStatusMin   = 400
)

// Middleware creates an Echo middleware for automatic metrics collection
func Middleware(metrics *ServiceMetrics) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// Skip metrics for /metrics endpoint itself to avoid recursion
			if c.Path() == "/metrics" {
				return next(c)
			}

			start := time.Now()
			service := extractServiceName(c.Path())
			method := c.Request().Method

			// Increment active requests
			metrics.IncActiveRequests(service, method)
			defer metrics.DecActiveRequests(service, method)

			// Call next handler
			err := next(c)

			// Record metrics
			duration := time.Since(start)
			status := strconv.Itoa(c.Response().Status)

			metrics.RecordRequest(service, method, status, duration)

			// Update error rate if status is error (4xx or 5xx)
			if c.Response().Status >= httpErrorStatusMin {
				metrics.ErrorRate.WithLabelValues(service, method).Inc()
			} else {
				// Decay error rate on success
				currentRate := getGaugeValue(metrics.ErrorRate.WithLabelValues(service, method))
				if currentRate > 0 {
					metrics.ErrorRate.WithLabelValues(service, method).Set(currentRate * errorRateDecayFactor)
				}
			}

			return err
		}
	}
}

// extractServiceName extracts the service name from the request path
func extractServiceName(path string) string {
	// Extract first path segment after /api/v1
	// e.g., /api/v1/projects/123 -> projects
	// e.g., /api/v1/items -> items
	if len(path) < 1 {
		return "unknown"
	}

	// Remove /api/v1/ prefix if present
	if len(path) >= 8 && path[:8] == "/api/v1/" {
		path = path[8:]
	} else if len(path) > 0 && path[0] == '/' {
		// Remove leading slash for non-API paths
		path = path[1:]
	}

	// If path is empty after prefix removal, return unknown
	if path == "" {
		return "unknown"
	}

	// Find first slash
	for i, ch := range path {
		if ch == '/' {
			return path[:i]
		}
	}

	// No slash found, return whole path
	return path
}

// getGaugeValue is a helper to read gauge value (Prometheus doesn't provide public access)
// We use a simple tracking mechanism instead
func getGaugeValue(_ interface{}) float64 {
	// Since Prometheus doesn't expose gauge values, we track error counts separately
	// This is a simplified implementation
	return 0
}

// CacheMetricsWrapper wraps cache operations with metrics
type CacheMetricsWrapper struct {
	cacheType string
	metrics   *ServiceMetrics
}

// NewCacheMetricsWrapper creates a new cache metrics wrapper
func NewCacheMetricsWrapper(cacheType string, metrics *ServiceMetrics) *CacheMetricsWrapper {
	return &CacheMetricsWrapper{
		cacheType: cacheType,
		metrics:   metrics,
	}
}

// RecordHit records a cache hit
func (w *CacheMetricsWrapper) RecordHit() {
	w.metrics.RecordCacheHit(w.cacheType)
}

// RecordMiss records a cache miss
func (w *CacheMetricsWrapper) RecordMiss() {
	w.metrics.RecordCacheMiss(w.cacheType)
}

// DBMetricsWrapper wraps database operations with metrics
type DBMetricsWrapper struct {
	metrics *ServiceMetrics
}

// NewDBMetricsWrapper creates a new database metrics wrapper
func NewDBMetricsWrapper(metrics *ServiceMetrics) *DBMetricsWrapper {
	return &DBMetricsWrapper{
		metrics: metrics,
	}
}

// RecordQuery records a database query with timing
func (w *DBMetricsWrapper) RecordQuery(operation string) func() {
	start := time.Now()
	return func() {
		duration := time.Since(start)
		w.metrics.RecordDBQuery(operation, duration)
	}
}

// RecordTransaction records a transaction completion
func (w *DBMetricsWrapper) RecordTransaction(committed bool) {
	if committed {
		w.metrics.RecordDBTransaction("committed")
	} else {
		w.metrics.RecordDBTransaction("rolled_back")
	}
}

// RecordTransactionError records a transaction error
func (w *DBMetricsWrapper) RecordTransactionError(errorType string) {
	w.metrics.RecordDBTransactionError(errorType)
}

// StorageMetricsWrapper wraps storage operations with metrics
type StorageMetricsWrapper struct {
	metrics *ServiceMetrics
}

// NewStorageMetricsWrapper creates a new storage metrics wrapper
func NewStorageMetricsWrapper(metrics *ServiceMetrics) *StorageMetricsWrapper {
	return &StorageMetricsWrapper{
		metrics: metrics,
	}
}

// RecordUpload records a storage upload
func (w *StorageMetricsWrapper) RecordUpload(success bool, bytes int64) {
	status := metricsStatusFailure
	if success {
		status = metricsStatusSuccess
	}
	w.metrics.RecordStorageUpload(status, bytes)
}

// RecordDownload records a storage download
func (w *StorageMetricsWrapper) RecordDownload(success bool, bytes int64) {
	status := metricsStatusFailure
	if success {
		status = metricsStatusSuccess
	}
	w.metrics.RecordStorageDownload(status, bytes)
}

// RecordError records a storage error
func (w *StorageMetricsWrapper) RecordError(operation, errorType string) {
	w.metrics.RecordStorageError(operation, errorType)
}

// MessagingMetricsWrapper wraps messaging operations with metrics
type MessagingMetricsWrapper struct {
	metrics *ServiceMetrics
}

// NewMessagingMetricsWrapper creates a new messaging metrics wrapper
func NewMessagingMetricsWrapper(metrics *ServiceMetrics) *MessagingMetricsWrapper {
	return &MessagingMetricsWrapper{
		metrics: metrics,
	}
}

// RecordPublish records a message publish
func (w *MessagingMetricsWrapper) RecordPublish(subject string, success bool) {
	if success {
		w.metrics.RecordMessagePublished(subject)
	} else {
		w.metrics.RecordMessagePublishError(subject)
	}
}

// RecordConsume records a message consumption
func (w *MessagingMetricsWrapper) RecordConsume(subject string) {
	w.metrics.RecordMessageConsumed(subject)
}

// AgentMetricsWrapper wraps agent coordination operations with metrics
type AgentMetricsWrapper struct {
	metrics *ServiceMetrics
}

// NewAgentMetricsWrapper creates a new agent metrics wrapper
func NewAgentMetricsWrapper(metrics *ServiceMetrics) *AgentMetricsWrapper {
	return &AgentMetricsWrapper{
		metrics: metrics,
	}
}

// RecordRegistration records an agent registration
func (w *AgentMetricsWrapper) RecordRegistration() {
	w.metrics.AgentRegistrations.Inc()
}

// RecordUnregistration records an agent unregistration
func (w *AgentMetricsWrapper) RecordUnregistration() {
	w.metrics.AgentUnregistrations.Inc()
}

// RecordHeartbeat records an agent heartbeat
func (w *AgentMetricsWrapper) RecordHeartbeat() {
	w.metrics.AgentHeartbeats.Inc()
}

// UpdateActiveAgents updates the active agent count
func (w *AgentMetricsWrapper) UpdateActiveAgents(count int) {
	w.metrics.UpdateActiveAgents(count)
}

// RecordTaskAssignment records a task assignment
func (w *AgentMetricsWrapper) RecordTaskAssignment(agentType string) {
	w.metrics.RecordTaskAssignment(agentType)
}

// RecordTaskCompletion records a task completion
func (w *AgentMetricsWrapper) RecordTaskCompletion(agentType string, success bool) {
	status := metricsStatusFailure
	if success {
		status = metricsStatusSuccess
	}
	w.metrics.RecordTaskCompletion(agentType, status)
}

// RecordTaskError records a task error
func (w *AgentMetricsWrapper) RecordTaskError(agentType, errorType string) {
	w.metrics.RecordTaskError(agentType, errorType)
}
