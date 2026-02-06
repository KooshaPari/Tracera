package metrics

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/testutil"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const metricsTestShortSleep = 10 * time.Millisecond

func TestNewServiceMetrics(t *testing.T) {
	// Create metrics with custom namespace
	m := NewServiceMetrics("test")
	assert.NotNil(t, m)
	assert.NotNil(t, m.RequestsTotal)
	assert.NotNil(t, m.RequestDuration)
	assert.NotNil(t, m.ErrorRate)
	assert.NotNil(t, m.CacheHits)
	assert.NotNil(t, m.CacheMisses)
	assert.NotNil(t, m.ItemsCreated)
	assert.NotNil(t, m.DBConnections)
	assert.NotNil(t, m.AgentRegistrations)
	assert.NotNil(t, m.MessagesPublished)
	assert.NotNil(t, m.StorageUploads)
}

func TestRecordRequest(t *testing.T) {
	// Create fresh registry for isolation
	registry := prometheus.NewRegistry()

	// Create metrics manually
	requestsTotal := prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Namespace: "test",
			Name:      "requests_total",
			Help:      "Test requests",
		},
		[]string{"service", "method", "status"},
	)
	registry.MustRegister(requestsTotal)

	// Record a request
	requestsTotal.WithLabelValues("items", "GET", "200").Inc()

	// Verify metric
	count := testutil.CollectAndCount(requestsTotal)
	assert.Equal(t, 1, count)

	// Verify metric value
	val := testutil.ToFloat64(requestsTotal.WithLabelValues("items", "GET", "200"))
	assert.Equal(t, 1.0, val)
}

func TestRecordCacheOperations(t *testing.T) {
	m := NewServiceMetrics("test_cache")

	// Record cache hits
	m.RecordCacheHit("redis")
	m.RecordCacheHit("redis")

	// Record cache miss
	m.RecordCacheMiss("redis")

	// Verify counts
	hits := testutil.ToFloat64(m.CacheHits.WithLabelValues("redis"))
	misses := testutil.ToFloat64(m.CacheMisses.WithLabelValues("redis"))

	assert.Equal(t, 2.0, hits)
	assert.Equal(t, 1.0, misses)
}

func TestActiveRequests(t *testing.T) {
	m := NewServiceMetrics("test_active")

	// Increment active requests
	m.IncActiveRequests("items", "GET")
	m.IncActiveRequests("items", "GET")
	m.IncActiveRequests("items", "POST")

	// Verify counts
	getActive := testutil.ToFloat64(m.ActiveRequests.WithLabelValues("items", "GET"))
	postActive := testutil.ToFloat64(m.ActiveRequests.WithLabelValues("items", "POST"))

	assert.Equal(t, 2.0, getActive)
	assert.Equal(t, 1.0, postActive)

	// Decrement
	m.DecActiveRequests("items", "GET")
	getActive = testutil.ToFloat64(m.ActiveRequests.WithLabelValues("items", "GET"))
	assert.Equal(t, 1.0, getActive)
}

func TestBusinessMetrics(t *testing.T) {
	m := NewServiceMetrics("test_business")

	// Record business operations
	m.ItemsCreated.Inc()
	m.ItemsCreated.Inc()
	m.ItemsUpdated.Inc()
	m.LinksCreated.Inc()

	// Verify counts
	assert.Equal(t, 2.0, testutil.ToFloat64(m.ItemsCreated))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.ItemsUpdated))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.LinksCreated))
}

func TestDatabaseMetrics(t *testing.T) {
	m := NewServiceMetrics("test_db")

	// Record DB operations
	m.RecordDBQuery("SELECT", 50*time.Millisecond)
	m.RecordDBQuery("INSERT", 100*time.Millisecond)
	m.RecordDBTransaction("committed")
	m.RecordDBTransaction("rolled_back")
	m.RecordDBTransactionError("deadlock")

	// Verify transaction counts
	committed := testutil.ToFloat64(m.DBTransactions.WithLabelValues("committed"))
	rolledBack := testutil.ToFloat64(m.DBTransactions.WithLabelValues("rolled_back"))
	errors := testutil.ToFloat64(m.DBTransactionErrors.WithLabelValues("deadlock"))

	assert.Equal(t, 1.0, committed)
	assert.Equal(t, 1.0, rolledBack)
	assert.Equal(t, 1.0, errors)

	// Update connection count
	m.UpdateDBConnections(42)
	assert.Equal(t, 42.0, testutil.ToFloat64(m.DBConnections))
}

func TestAgentMetrics(t *testing.T) {
	m := NewServiceMetrics("test_agent")

	// Record agent operations
	m.AgentRegistrations.Inc()
	m.AgentUnregistrations.Inc()
	m.AgentHeartbeats.Inc()
	m.AgentHeartbeats.Inc()
	m.RecordTaskAssignment("analyzer")
	m.RecordTaskCompletion("analyzer", "success")
	m.RecordTaskError("analyzer", "timeout")

	// Verify counts
	assert.Equal(t, 1.0, testutil.ToFloat64(m.AgentRegistrations))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.AgentUnregistrations))
	assert.Equal(t, 2.0, testutil.ToFloat64(m.AgentHeartbeats))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TasksAssigned.WithLabelValues("analyzer")))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TasksCompleted.WithLabelValues("analyzer", "success")))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TaskErrors.WithLabelValues("analyzer", "timeout")))

	// Update active agents
	m.UpdateActiveAgents(5)
	assert.Equal(t, 5.0, testutil.ToFloat64(m.ActiveAgents))
}

func TestMessagingMetrics(t *testing.T) {
	m := NewServiceMetrics("test_msg")

	// Record messaging operations
	m.RecordMessagePublished("tracertm.items.created")
	m.RecordMessagePublished("tracertm.items.created")
	m.RecordMessageConsumed("tracertm.items.created")
	m.RecordMessagePublishError("tracertm.items.created")

	// Verify counts
	published := testutil.ToFloat64(m.MessagesPublished.WithLabelValues("tracertm.items.created"))
	consumed := testutil.ToFloat64(m.MessagesConsumed.WithLabelValues("tracertm.items.created"))
	errors := testutil.ToFloat64(m.MessagePublishErrors.WithLabelValues("tracertm.items.created"))

	assert.Equal(t, 2.0, published)
	assert.Equal(t, 1.0, consumed)
	assert.Equal(t, 1.0, errors)
}

func TestStorageMetrics(t *testing.T) {
	m := NewServiceMetrics("test_storage")

	// Record storage operations
	m.RecordStorageUpload("success", 1024000) // 1MB
	m.RecordStorageUpload("failure", 0)
	m.RecordStorageDownload("success", 2048000) // 2MB
	m.RecordStorageError("upload", "network_timeout")

	// Verify counts
	uploadSuccess := testutil.ToFloat64(m.StorageUploads.WithLabelValues("success"))
	uploadFailure := testutil.ToFloat64(m.StorageUploads.WithLabelValues("failure"))
	downloadSuccess := testutil.ToFloat64(m.StorageDownloads.WithLabelValues("success"))
	errors := testutil.ToFloat64(m.StorageErrors.WithLabelValues("upload", "network_timeout"))

	assert.Equal(t, 1.0, uploadSuccess)
	assert.Equal(t, 1.0, uploadFailure)
	assert.Equal(t, 1.0, downloadSuccess)
	assert.Equal(t, 1.0, errors)

	// Verify bytes
	bytesUploaded := testutil.ToFloat64(m.StorageBytesUploaded)
	bytesDownloaded := testutil.ToFloat64(m.StorageBytesDownloaded)

	assert.Equal(t, 1024000.0, bytesUploaded)
	assert.Equal(t, 2048000.0, bytesDownloaded)
}

func TestWebSocketMetrics(t *testing.T) {
	m := NewServiceMetrics("test_ws")

	// Update WebSocket client count
	m.UpdateWebSocketClients(25)
	assert.Equal(t, 25.0, testutil.ToFloat64(m.WebSocketClients))

	m.UpdateWebSocketClients(10)
	assert.Equal(t, 10.0, testutil.ToFloat64(m.WebSocketClients))
}

func TestMetricsMiddleware(t *testing.T) {
	// Initialize metrics
	m := NewServiceMetrics("test_middleware")

	// Create Echo instance
	e := echo.New()

	// Add middleware
	e.Use(Middleware(m))

	// Create test handler
	e.GET("/api/v1/items", func(c echo.Context) error {
		return c.String(http.StatusOK, "success")
	})

	// Create request
	req := httptest.NewRequest(http.MethodGet, "/api/v1/items", nil)
	rec := httptest.NewRecorder()

	// Serve request
	e.ServeHTTP(rec, req)

	// Verify response
	assert.Equal(t, http.StatusOK, rec.Code)

	// Verify metrics were recorded
	requests := testutil.ToFloat64(m.RequestsTotal.WithLabelValues("items", "GET", "200"))
	assert.Equal(t, 1.0, requests)
}

func TestMetricsHandler(t *testing.T) {
	// Create Echo instance
	e := echo.New()

	// Add metrics endpoint
	e.GET("/metrics", Handler())

	// Create request
	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()

	// Serve request
	e.ServeHTTP(rec, req)

	// Verify response
	assert.Equal(t, http.StatusOK, rec.Code)
	assert.Contains(t, rec.Body.String(), "# HELP")
	assert.Contains(t, rec.Body.String(), "# TYPE")
}

func TestExtractServiceName(t *testing.T) {
	tests := []struct {
		path     string
		expected string
	}{
		{"/api/v1/items", "items"},
		{"/api/v1/items/123", "items"},
		{"/api/v1/projects/456/items", "projects"},
		{"/health", "health"},   // Non-API path, removes leading slash
		{"/metrics", "metrics"}, // Non-API path, removes leading slash
		{"", "unknown"},
		{"/", "unknown"}, // Just slash becomes empty -> unknown
		{"/api/v1/", "unknown"},
	}

	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			result := extractServiceName(tt.path)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCacheMetricsWrapper(t *testing.T) {
	m := NewServiceMetrics("test_cache_wrap")
	wrapper := NewCacheMetricsWrapper("redis", m)

	// Record operations
	wrapper.RecordHit()
	wrapper.RecordHit()
	wrapper.RecordMiss()

	// Verify counts
	hits := testutil.ToFloat64(m.CacheHits.WithLabelValues("redis"))
	misses := testutil.ToFloat64(m.CacheMisses.WithLabelValues("redis"))

	assert.Equal(t, 2.0, hits)
	assert.Equal(t, 1.0, misses)
}

func TestDBMetricsWrapper(t *testing.T) {
	m := NewServiceMetrics("test_db_wrap")
	wrapper := NewDBMetricsWrapper(m)

	// Record query
	done := wrapper.RecordQuery("SELECT")
	time.Sleep(metricsTestShortSleep)
	done()

	// Record transaction
	wrapper.RecordTransaction(true)
	wrapper.RecordTransaction(false)
	wrapper.RecordTransactionError("deadlock")

	// Verify counts
	committed := testutil.ToFloat64(m.DBTransactions.WithLabelValues("committed"))
	rolledBack := testutil.ToFloat64(m.DBTransactions.WithLabelValues("rolled_back"))
	errors := testutil.ToFloat64(m.DBTransactionErrors.WithLabelValues("deadlock"))

	assert.Equal(t, 1.0, committed)
	assert.Equal(t, 1.0, rolledBack)
	assert.Equal(t, 1.0, errors)
}

func TestStorageMetricsWrapper(t *testing.T) {
	m := NewServiceMetrics("test_storage_wrap")
	wrapper := NewStorageMetricsWrapper(m)

	// Record operations
	wrapper.RecordUpload(true, 1024)
	wrapper.RecordUpload(false, 0)
	wrapper.RecordDownload(true, 2048)
	wrapper.RecordError("upload", "timeout")

	// Verify counts
	uploadSuccess := testutil.ToFloat64(m.StorageUploads.WithLabelValues("success"))
	uploadFailure := testutil.ToFloat64(m.StorageUploads.WithLabelValues("failure"))
	downloadSuccess := testutil.ToFloat64(m.StorageDownloads.WithLabelValues("success"))
	errors := testutil.ToFloat64(m.StorageErrors.WithLabelValues("upload", "timeout"))

	assert.Equal(t, 1.0, uploadSuccess)
	assert.Equal(t, 1.0, uploadFailure)
	assert.Equal(t, 1.0, downloadSuccess)
	assert.Equal(t, 1.0, errors)
}

func TestMessagingMetricsWrapper(t *testing.T) {
	m := NewServiceMetrics("test_msg_wrap")
	wrapper := NewMessagingMetricsWrapper(m)

	// Record operations
	wrapper.RecordPublish("test.subject", true)
	wrapper.RecordPublish("test.subject", false)
	wrapper.RecordConsume("test.subject")

	// Verify counts
	published := testutil.ToFloat64(m.MessagesPublished.WithLabelValues("test.subject"))
	errors := testutil.ToFloat64(m.MessagePublishErrors.WithLabelValues("test.subject"))
	consumed := testutil.ToFloat64(m.MessagesConsumed.WithLabelValues("test.subject"))

	assert.Equal(t, 1.0, published)
	assert.Equal(t, 1.0, errors)
	assert.Equal(t, 1.0, consumed)
}

func TestAgentMetricsWrapper(t *testing.T) {
	m := NewServiceMetrics("test_agent_wrap")
	wrapper := NewAgentMetricsWrapper(m)

	// Record operations
	wrapper.RecordRegistration()
	wrapper.RecordUnregistration()
	wrapper.RecordHeartbeat()
	wrapper.UpdateActiveAgents(5)
	wrapper.RecordTaskAssignment("analyzer")
	wrapper.RecordTaskCompletion("analyzer", true)
	wrapper.RecordTaskCompletion("analyzer", false)
	wrapper.RecordTaskError("analyzer", "timeout")

	// Verify counts
	assert.Equal(t, 1.0, testutil.ToFloat64(m.AgentRegistrations))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.AgentUnregistrations))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.AgentHeartbeats))
	assert.Equal(t, 5.0, testutil.ToFloat64(m.ActiveAgents))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TasksAssigned.WithLabelValues("analyzer")))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TasksCompleted.WithLabelValues("analyzer", "success")))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TasksCompleted.WithLabelValues("analyzer", "failure")))
	assert.Equal(t, 1.0, testutil.ToFloat64(m.TaskErrors.WithLabelValues("analyzer", "timeout")))
}

func TestInitializeMetrics(t *testing.T) {
	// Initialize global metrics
	InitializeMetrics("test_global")

	// Verify global instance is set
	require.NotNil(t, Metrics)
	assert.NotNil(t, Metrics.RequestsTotal)
	assert.NotNil(t, Metrics.ItemsCreated)
}

func BenchmarkRecordRequest(b *testing.B) {
	m := NewServiceMetrics("bench")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		m.RecordRequest("items", "GET", "200", 10*time.Millisecond)
	}
}

func BenchmarkMetricsMiddleware(b *testing.B) {
	m := NewServiceMetrics("bench")
	e := echo.New()
	e.Use(Middleware(m))
	e.GET("/test", func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	})

	req := httptest.NewRequest(http.MethodGet, "/test", nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)
	}
}
