package metrics

import (
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

// Metrics holds the global service metrics registry.
var Metrics *ServiceMetrics //nolint:gochecknoglobals // Singleton pattern for global access

// InitializeMetrics sets the global service metrics registry.
func InitializeMetrics(namespace string) {
	Metrics = NewServiceMetrics(namespace)
}

// NewServiceMetrics creates and registers all Prometheus metrics
func NewServiceMetrics(namespace string) *ServiceMetrics {
	if namespace == "" {
		namespace = defaultMetricsNamespace
	}

	m := &ServiceMetrics{}
	initRequestMetrics(m, namespace)
	initCacheMetrics(m, namespace)
	initBusinessCounters(m, namespace)
	initDBMetrics(m, namespace)
	initAgentMetrics(m, namespace)
	initMessagingMetrics(m, namespace)
	initStorageMetrics(m, namespace)
	return m
}

func initRequestMetrics(m *ServiceMetrics, namespace string) {
	m.RequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "requests_total",
			Help:      "Total number of requests by service, method, and status",
		},
		[]string{"service", "method", "status"},
	)

	m.RequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Name:      "request_duration_seconds",
			Help:      "Request duration in seconds",
			Buckets:   []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
		},
		[]string{"service", "method"},
	)

	m.ErrorRate = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "error_rate",
			Help:      "Error rate by service and method",
		},
		[]string{"service", "method"},
	)

	m.ActiveRequests = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "active_requests",
			Help:      "Number of active requests",
		},
		[]string{"service", "method"},
	)
}

func initCacheMetrics(m *ServiceMetrics, namespace string) {
	m.CacheHits = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "cache_hits_total",
			Help:      "Total number of cache hits",
		},
		[]string{"cache_type"},
	)

	m.CacheMisses = promauto.NewCounterVec(
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

func initItemCounters(m *ServiceMetrics, namespace string) {
	m.ItemsCreated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "items_created_total",
			Help:      "Total number of items created",
		},
	)

	m.ItemsUpdated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "items_updated_total",
			Help:      "Total number of items updated",
		},
	)

	m.ItemsDeleted = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "items_deleted_total",
			Help:      "Total number of items deleted",
		},
	)

	m.LinksCreated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "links_created_total",
			Help:      "Total number of links created",
		},
	)

	m.LinksDeleted = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "links_deleted_total",
			Help:      "Total number of links deleted",
		},
	)

	m.ProjectsCreated = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "projects_created_total",
			Help:      "Total number of projects created",
		},
	)
}

func initEngagementCounters(m *ServiceMetrics, namespace string) {
	m.SearchQueries = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "search_queries_total",
			Help:      "Total number of search queries",
		},
	)

	m.WebSocketClients = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "websocket_clients",
			Help:      "Number of active websocket clients",
		},
	)
}

func initDBMetrics(m *ServiceMetrics, namespace string) {
	m.DBConnections = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "db_connections",
			Help:      "Number of database connections",
		},
	)

	m.DBQueryDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Namespace: namespace,
			Name:      "db_query_duration_seconds",
			Help:      "Database query duration in seconds",
			Buckets:   []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
		},
		[]string{"operation"},
	)

	m.DBTransactions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "db_transactions_total",
			Help:      "Total number of database transactions",
		},
		[]string{"status"},
	)

	m.DBTransactionErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "db_transaction_errors_total",
			Help:      "Database transaction errors by type",
		},
		[]string{"error_type"},
	)
}

func initAgentMetrics(m *ServiceMetrics, namespace string) {
	m.AgentRegistrations = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "agent_registrations_total",
			Help:      "Total number of agent registrations",
		},
	)

	m.AgentUnregistrations = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "agent_unregistrations_total",
			Help:      "Total number of agent unregistrations",
		},
	)

	m.AgentHeartbeats = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "agent_heartbeats_total",
			Help:      "Total number of agent heartbeats",
		},
	)

	m.ActiveAgents = promauto.NewGauge(
		prometheus.GaugeOpts{
			Namespace: namespace,
			Name:      "active_agents",
			Help:      "Number of active agents",
		},
	)

	m.TasksAssigned = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "tasks_assigned_total",
			Help:      "Total number of tasks assigned",
		},
		[]string{"agent_type"},
	)

	m.TasksCompleted = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "tasks_completed_total",
			Help:      "Total number of tasks completed",
		},
		[]string{"agent_type", "status"},
	)

	m.TaskErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "task_errors_total",
			Help:      "Total number of task errors",
		},
		[]string{"agent_type", "error_type"},
	)
}

func initMessagingMetrics(m *ServiceMetrics, namespace string) {
	m.MessagesPublished = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "messages_published_total",
			Help:      "Total number of messages published",
		},
		[]string{"subject"},
	)

	m.MessagesConsumed = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "messages_consumed_total",
			Help:      "Total number of messages consumed",
		},
		[]string{"subject"},
	)

	m.MessagePublishErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "message_publish_errors_total",
			Help:      "Total number of message publish errors",
		},
		[]string{"subject"},
	)
}

func initStorageMetrics(m *ServiceMetrics, namespace string) {
	m.StorageUploads = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_uploads_total",
			Help:      "Total number of storage uploads",
		},
		[]string{"status"},
	)

	m.StorageDownloads = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_downloads_total",
			Help:      "Total number of storage downloads",
		},
		[]string{"status"},
	)

	m.StorageErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_errors_total",
			Help:      "Total number of storage errors",
		},
		[]string{"operation", "error_type"},
	)

	m.StorageBytesUploaded = promauto.NewCounter(
		prometheus.CounterOpts{
			Namespace: namespace,
			Name:      "storage_bytes_uploaded_total",
			Help:      "Total bytes uploaded to storage",
		},
	)

	m.StorageBytesDownloaded = promauto.NewCounter(
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
