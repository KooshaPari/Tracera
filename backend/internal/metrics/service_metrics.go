package metrics

import (
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// Status constants for metrics
const (
	metricsStatusSuccess = "success"
	metricsStatusFailure = "failure"
)

// ServiceMetrics provides Prometheus metrics for service layer monitoring
type ServiceMetrics struct {
	// Request count metrics (by service, method, status)
	RequestsTotal *prometheus.CounterVec

	// Request duration histogram
	RequestDuration *prometheus.HistogramVec

	// Error rate gauge
	ErrorRate *prometheus.GaugeVec

	// Cache hit/miss counters
	CacheHits   *prometheus.CounterVec
	CacheMisses *prometheus.CounterVec

	// Active requests gauge
	ActiveRequests *prometheus.GaugeVec

	// Custom business metrics
	ItemsCreated     prometheus.Counter
	ItemsUpdated     prometheus.Counter
	ItemsDeleted     prometheus.Counter
	LinksCreated     prometheus.Counter
	LinksDeleted     prometheus.Counter
	ProjectsCreated  prometheus.Counter
	SearchQueries    prometheus.Counter
	WebSocketClients prometheus.Gauge

	// Database metrics
	DBConnections       prometheus.Gauge
	DBQueryDuration     *prometheus.HistogramVec
	DBTransactions      *prometheus.CounterVec
	DBTransactionErrors *prometheus.CounterVec

	// Agent coordination metrics
	AgentRegistrations   prometheus.Counter
	AgentUnregistrations prometheus.Counter
	AgentHeartbeats      prometheus.Counter
	ActiveAgents         prometheus.Gauge
	TasksAssigned        *prometheus.CounterVec
	TasksCompleted       *prometheus.CounterVec
	TaskErrors           *prometheus.CounterVec

	// NATS/messaging metrics
	MessagesPublished    *prometheus.CounterVec
	MessagesConsumed     *prometheus.CounterVec
	MessagePublishErrors *prometheus.CounterVec

	// S3/Storage metrics
	StorageUploads         *prometheus.CounterVec
	StorageDownloads       *prometheus.CounterVec
	StorageErrors          *prometheus.CounterVec
	StorageBytesUploaded   prometheus.Counter
	StorageBytesDownloaded prometheus.Counter
}

//nolint:gochecknoglobals // sync.Once singleton for lazy-initialized Prometheus metrics registry
var (
	metricsInstance     *ServiceMetrics
	metricsInstanceOnce sync.Once
	metricsNamespace    = defaultMetricsNamespace
)

// InitializeMetrics sets the namespace for the global service metrics registry.
// This must be called before GetMetrics() if a custom namespace is desired.
func InitializeMetrics(namespace string) {
	if namespace != "" {
		metricsNamespace = namespace
	}
}

// GetMetrics returns the global service metrics instance (lazy-initialized).
func GetMetrics() *ServiceMetrics {
	metricsInstanceOnce.Do(func() {
		metricsInstance = NewServiceMetrics(metricsNamespace)
	})
	return metricsInstance
}

// NewServiceMetrics creates and registers all Prometheus metrics
func NewServiceMetrics(namespace string) *ServiceMetrics {
	if namespace == "" {
		namespace = defaultMetricsNamespace
	}

	metrics := &ServiceMetrics{}
	initRequestMetrics(metrics, namespace)
	initCacheMetrics(metrics, namespace)
	initBusinessCounters(metrics, namespace)
	initDBMetrics(metrics, namespace)
	initAgentMetrics(metrics, namespace)
	initMessagingMetrics(metrics, namespace)
	initStorageMetrics(metrics, namespace)
	return metrics
}

func initRequestMetrics(metrics *ServiceMetrics, namespace string) {
	metrics.RequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "requests_total",
			Help:      "Total number of requests by service, method, and status",
		},
		[]string{"service", "method", "status"},
	)

	metrics.RequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Name:      "request_duration_seconds",
			Help:      "Request duration in seconds",
			Buckets:   []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
		},
		[]string{"service", "method"},
	)

	metrics.ErrorRate = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "error_rate",
			Help:      "Error rate by service and method",
		},
		[]string{"service", "method"},
	)

	metrics.ActiveRequests = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "active_requests",
			Help:      "Number of active requests",
		},
		[]string{"service", "method"},
	)
}

func initCacheMetrics(metrics *ServiceMetrics, namespace string) {
	metrics.CacheHits = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "cache_hits_total",
			Help:      "Total number of cache hits",
		},
		[]string{"cache_type"},
	)

	metrics.CacheMisses = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "cache_misses_total",
			Help:      "Total number of cache misses",
		},
		[]string{"cache_type"},
	)
}

func initBusinessCounters(m *ServiceMetrics, namespace string) {
	initItemCounters(m, namespace)
	initEngagementCounters(m, namespace)
}

func initItemCounters(metrics *ServiceMetrics, namespace string) {
	metrics.ItemsCreated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "items_created_total",
			Help:      "Total number of items created",
		},
	)

	metrics.ItemsUpdated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "items_updated_total",
			Help:      "Total number of items updated",
		},
	)

	metrics.ItemsDeleted = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "items_deleted_total",
			Help:      "Total number of items deleted",
		},
	)

	metrics.LinksCreated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "links_created_total",
			Help:      "Total number of links created",
		},
	)

	metrics.LinksDeleted = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "links_deleted_total",
			Help:      "Total number of links deleted",
		},
	)

	metrics.ProjectsCreated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "projects_created_total",
			Help:      "Total number of projects created",
		},
	)
}

func initEngagementCounters(metrics *ServiceMetrics, namespace string) {
	metrics.SearchQueries = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "search_queries_total",
			Help:      "Total number of search queries",
		},
	)

	metrics.WebSocketClients = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "websocket_clients",
			Help:      "Number of active websocket clients",
		},
	)
}

func initDBMetrics(metrics *ServiceMetrics, namespace string) {
	metrics.DBConnections = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "db_connections",
			Help:      "Number of database connections",
		},
	)

	metrics.DBQueryDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Name:      "db_query_duration_seconds",
			Help:      "Database query duration in seconds",
			Buckets:   []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
		},
		[]string{"operation"},
	)

	metrics.DBTransactions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "db_transactions_total",
			Help:      "Total number of database transactions",
		},
		[]string{"status"},
	)

	metrics.DBTransactionErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "db_transaction_errors_total",
			Help:      "Database transaction errors by type",
		},
		[]string{"error_type"},
	)
}

func initAgentMetrics(metrics *ServiceMetrics, namespace string) {
	metrics.AgentRegistrations = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "agent_registrations_total",
			Help:      "Total number of agent registrations",
		},
	)

	metrics.AgentUnregistrations = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "agent_unregistrations_total",
			Help:      "Total number of agent unregistrations",
		},
	)

	metrics.AgentHeartbeats = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "agent_heartbeats_total",
			Help:      "Total number of agent heartbeats",
		},
	)

	metrics.ActiveAgents = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "active_agents",
			Help:      "Number of active agents",
		},
	)

	metrics.TasksAssigned = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "tasks_assigned_total",
			Help:      "Total number of tasks assigned",
		},
		[]string{"agent_type"},
	)

	metrics.TasksCompleted = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "tasks_completed_total",
			Help:      "Total number of tasks completed",
		},
		[]string{"agent_type", "status"},
	)

	metrics.TaskErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "task_errors_total",
			Help:      "Total number of task errors",
		},
		[]string{"agent_type", "error_type"},
	)
}

func initMessagingMetrics(metrics *ServiceMetrics, namespace string) {
	metrics.MessagesPublished = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "messages_published_total",
			Help:      "Total number of messages published",
		},
		[]string{"subject"},
	)

	metrics.MessagesConsumed = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "messages_consumed_total",
			Help:      "Total number of messages consumed",
		},
		[]string{"subject"},
	)

	metrics.MessagePublishErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "message_publish_errors_total",
			Help:      "Total number of message publish errors",
		},
		[]string{"subject"},
	)
}

func initStorageMetrics(metrics *ServiceMetrics, namespace string) {
	metrics.StorageUploads = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_uploads_total",
			Help:      "Total number of storage uploads",
		},
		[]string{"status"},
	)

	metrics.StorageDownloads = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_downloads_total",
			Help:      "Total number of storage downloads",
		},
		[]string{"status"},
	)

	metrics.StorageErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_errors_total",
			Help:      "Total number of storage errors",
		},
		[]string{"operation", "error_type"},
	)

	metrics.StorageBytesUploaded = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_bytes_uploaded_total",
			Help:      "Total bytes uploaded to storage",
		},
	)

	metrics.StorageBytesDownloaded = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_bytes_downloaded_total",
			Help:      "Total bytes downloaded from storage",
		},
	)
}

// RecordRequest records a request count and duration for the service.
func (m *ServiceMetrics) RecordRequest(service, method, status string, duration time.Duration) {
	m.RequestsTotal.WithLabelValues(service, method, status).Inc()
	m.RequestDuration.WithLabelValues(service, method).Observe(duration.Seconds())
}

// RecordCacheHit records a cache hit
func (m *ServiceMetrics) RecordCacheHit(cacheType string) {
	m.CacheHits.WithLabelValues(cacheType).Inc()
}

// RecordCacheMiss records a cache miss
func (m *ServiceMetrics) RecordCacheMiss(cacheType string) {
	m.CacheMisses.WithLabelValues(cacheType).Inc()
}

// IncActiveRequests increments active request count
func (m *ServiceMetrics) IncActiveRequests(service, method string) {
	m.ActiveRequests.WithLabelValues(service, method).Inc()
}

// DecActiveRequests decrements active request count
func (m *ServiceMetrics) DecActiveRequests(service, method string) {
	m.ActiveRequests.WithLabelValues(service, method).Dec()
}

// RecordDBQuery records a database query with timing
func (m *ServiceMetrics) RecordDBQuery(operation string, duration time.Duration) {
	m.DBQueryDuration.WithLabelValues(operation).Observe(duration.Seconds())
}

// RecordDBTransaction records a database transaction result
func (m *ServiceMetrics) RecordDBTransaction(status string) {
	m.DBTransactions.WithLabelValues(status).Inc()
}

// RecordDBTransactionError records a database transaction error
func (m *ServiceMetrics) RecordDBTransactionError(errorType string) {
	m.DBTransactionErrors.WithLabelValues(errorType).Inc()
}

// RecordTaskAssignment records a task assignment
func (m *ServiceMetrics) RecordTaskAssignment(agentType string) {
	m.TasksAssigned.WithLabelValues(agentType).Inc()
}

// RecordTaskCompletion records a task completion
func (m *ServiceMetrics) RecordTaskCompletion(agentType, status string) {
	m.TasksCompleted.WithLabelValues(agentType, status).Inc()
}

// RecordTaskError records a task error
func (m *ServiceMetrics) RecordTaskError(agentType, errorType string) {
	m.TaskErrors.WithLabelValues(agentType, errorType).Inc()
}

// RecordMessagePublished records a published message
func (m *ServiceMetrics) RecordMessagePublished(subject string) {
	m.MessagesPublished.WithLabelValues(subject).Inc()
}

// RecordMessageConsumed records a consumed message
func (m *ServiceMetrics) RecordMessageConsumed(subject string) {
	m.MessagesConsumed.WithLabelValues(subject).Inc()
}

// RecordMessagePublishError records a message publish error
func (m *ServiceMetrics) RecordMessagePublishError(subject string) {
	m.MessagePublishErrors.WithLabelValues(subject).Inc()
}

// RecordStorageUpload records a storage upload
func (m *ServiceMetrics) RecordStorageUpload(status string, bytes int64) {
	m.StorageUploads.WithLabelValues(status).Inc()
	if status == metricsStatusSuccess && bytes > 0 {
		m.StorageBytesUploaded.Add(float64(bytes))
	}
}

// RecordStorageDownload records a storage download
func (m *ServiceMetrics) RecordStorageDownload(status string, bytes int64) {
	m.StorageDownloads.WithLabelValues(status).Inc()
	if status == metricsStatusSuccess && bytes > 0 {
		m.StorageBytesDownloaded.Add(float64(bytes))
	}
}

// RecordStorageError records a storage error
func (m *ServiceMetrics) RecordStorageError(operation, errorType string) {
	m.StorageErrors.WithLabelValues(operation, errorType).Inc()
}

// UpdateDBConnections updates the database connection count
func (m *ServiceMetrics) UpdateDBConnections(count int) {
	m.DBConnections.Set(float64(count))
}

// UpdateActiveAgents updates the active agents count
func (m *ServiceMetrics) UpdateActiveAgents(count int) {
	m.ActiveAgents.Set(float64(count))
}

// UpdateWebSocketClients updates the WebSocket client count
func (m *ServiceMetrics) UpdateWebSocketClients(count int) {
	m.WebSocketClients.Set(float64(count))
}
