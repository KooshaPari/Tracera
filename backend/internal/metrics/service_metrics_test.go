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
	metrics := NewServiceMetrics("test")
	assert.NotNil(t, metrics)
	assert.NotNil(t, metrics.RequestsTotal)
	assert.NotNil(t, metrics.RequestDuration)
	assert.NotNil(t, metrics.ErrorRate)
	assert.NotNil(t, metrics.CacheHits)
	assert.NotNil(t, metrics.CacheMisses)
	assert.NotNil(t, metrics.ItemsCreated)
	assert.NotNil(t, metrics.DBConnections)
	assert.NotNil(t, metrics.AgentRegistrations)
	assert.NotNil(t, metrics.MessagesPublished)
	assert.NotNil(t, metrics.StorageUploads)
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
	assert.InEpsilon(t, 1.0, val, 1e-9)
}

func TestRecordCacheOperations(t *testing.T) {
	metrics := NewServiceMetrics("test_cache")

	// Record cache hits
	metrics.RecordCacheHit("redis")
	metrics.RecordCacheHit("redis")

	// Record cache miss
	metrics.RecordCacheMiss("redis")

	// Verify counts
	hits := testutil.ToFloat64(metrics.CacheHits.WithLabelValues("redis"))
	misses := testutil.ToFloat64(metrics.CacheMisses.WithLabelValues("redis"))

	assert.InEpsilon(t, 2.0, hits, 1e-9)
	assert.InEpsilon(t, 1.0, misses, 1e-9)
}

func TestActiveRequests(t *testing.T) {
	metrics := NewServiceMetrics("test_active")

	// Increment active requests
	metrics.IncActiveRequests("items", "GET")
	metrics.IncActiveRequests("items", "GET")
	metrics.IncActiveRequests("items", "POST")

	// Verify counts
	getActive := testutil.ToFloat64(metrics.ActiveRequests.WithLabelValues("items", "GET"))
	postActive := testutil.ToFloat64(metrics.ActiveRequests.WithLabelValues("items", "POST"))

	assert.InEpsilon(t, 2.0, getActive, 1e-9)
	assert.InEpsilon(t, 1.0, postActive, 1e-9)

	// Decrement
	metrics.DecActiveRequests("items", "GET")
	getActive = testutil.ToFloat64(metrics.ActiveRequests.WithLabelValues("items", "GET"))
	assert.InEpsilon(t, 1.0, getActive, 1e-9)
}

func TestBusinessMetrics(t *testing.T) {
	metrics := NewServiceMetrics("test_business")

	// Record business operations
	metrics.ItemsCreated.Inc()
	metrics.ItemsCreated.Inc()
	metrics.ItemsUpdated.Inc()
	metrics.LinksCreated.Inc()

	// Verify counts
	assert.InEpsilon(t, 2.0, testutil.ToFloat64(metrics.ItemsCreated), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.ItemsUpdated), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.LinksCreated), 1e-9)
}

func TestDatabaseMetrics(t *testing.T) {
	metrics := NewServiceMetrics("test_db")

	// Record DB operations
	metrics.RecordDBQuery("SELECT", 50*time.Millisecond)
	metrics.RecordDBQuery("INSERT", 100*time.Millisecond)
	metrics.RecordDBTransaction("committed")
	metrics.RecordDBTransaction("rolled_back")
	metrics.RecordDBTransactionError("deadlock")

	// Verify transaction counts
	committed := testutil.ToFloat64(metrics.DBTransactions.WithLabelValues("committed"))
	rolledBack := testutil.ToFloat64(metrics.DBTransactions.WithLabelValues("rolled_back"))
	errors := testutil.ToFloat64(metrics.DBTransactionErrors.WithLabelValues("deadlock"))

	assert.InEpsilon(t, 1.0, committed, 1e-9)
	assert.InEpsilon(t, 1.0, rolledBack, 1e-9)
	assert.InEpsilon(t, 1.0, errors, 1e-9)

	// Update connection count
	metrics.UpdateDBConnections(42)
	assert.InEpsilon(t, 42.0, testutil.ToFloat64(metrics.DBConnections), 1e-9)
}

func TestAgentMetrics(t *testing.T) {
	metrics := NewServiceMetrics("test_agent")

	// Record agent operations
	metrics.AgentRegistrations.Inc()
	metrics.AgentUnregistrations.Inc()
	metrics.AgentHeartbeats.Inc()
	metrics.AgentHeartbeats.Inc()
	metrics.RecordTaskAssignment("analyzer")
	metrics.RecordTaskCompletion("analyzer", "success")
	metrics.RecordTaskError("analyzer", "timeout")

	// Verify counts
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.AgentRegistrations), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.AgentUnregistrations), 1e-9)
	assert.InEpsilon(t, 2.0, testutil.ToFloat64(metrics.AgentHeartbeats), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TasksAssigned.WithLabelValues("analyzer")), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TasksCompleted.WithLabelValues("analyzer", "success")), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TaskErrors.WithLabelValues("analyzer", "timeout")), 1e-9)

	// Update active agents
	metrics.UpdateActiveAgents(5)
	assert.InEpsilon(t, 5.0, testutil.ToFloat64(metrics.ActiveAgents), 1e-9)
}

func TestMessagingMetrics(t *testing.T) {
	metrics := NewServiceMetrics("test_msg")

	// Record messaging operations
	metrics.RecordMessagePublished("tracertm.items.created")
	metrics.RecordMessagePublished("tracertm.items.created")
	metrics.RecordMessageConsumed("tracertm.items.created")
	metrics.RecordMessagePublishError("tracertm.items.created")

	// Verify counts
	published := testutil.ToFloat64(metrics.MessagesPublished.WithLabelValues("tracertm.items.created"))
	consumed := testutil.ToFloat64(metrics.MessagesConsumed.WithLabelValues("tracertm.items.created"))
	errors := testutil.ToFloat64(metrics.MessagePublishErrors.WithLabelValues("tracertm.items.created"))

	assert.InEpsilon(t, 2.0, published, 1e-9)
	assert.InEpsilon(t, 1.0, consumed, 1e-9)
	assert.InEpsilon(t, 1.0, errors, 1e-9)
}

func TestStorageMetrics(t *testing.T) {
	metrics := NewServiceMetrics("test_storage")

	// Record storage operations
	metrics.RecordStorageUpload("success", 1024000) // 1MB
	metrics.RecordStorageUpload("failure", 0)
	metrics.RecordStorageDownload("success", 2048000) // 2MB
	metrics.RecordStorageError("upload", "network_timeout")

	// Verify counts
	uploadSuccess := testutil.ToFloat64(metrics.StorageUploads.WithLabelValues("success"))
	uploadFailure := testutil.ToFloat64(metrics.StorageUploads.WithLabelValues("failure"))
	downloadSuccess := testutil.ToFloat64(metrics.StorageDownloads.WithLabelValues("success"))
	errors := testutil.ToFloat64(metrics.StorageErrors.WithLabelValues("upload", "network_timeout"))

	assert.InEpsilon(t, 1.0, uploadSuccess, 1e-9)
	assert.InEpsilon(t, 1.0, uploadFailure, 1e-9)
	assert.InEpsilon(t, 1.0, downloadSuccess, 1e-9)
	assert.InEpsilon(t, 1.0, errors, 1e-9)

	// Verify bytes
	bytesUploaded := testutil.ToFloat64(metrics.StorageBytesUploaded)
	bytesDownloaded := testutil.ToFloat64(metrics.StorageBytesDownloaded)

	assert.InEpsilon(t, 1024000.0, bytesUploaded, 1e-9)
	assert.InEpsilon(t, 2048000.0, bytesDownloaded, 1e-9)
}

func TestWebSocketMetrics(t *testing.T) {
	metrics := NewServiceMetrics("test_ws")

	// Update WebSocket client count
	metrics.UpdateWebSocketClients(25)
	assert.InEpsilon(t, 25.0, testutil.ToFloat64(metrics.WebSocketClients), 1e-9)

	metrics.UpdateWebSocketClients(10)
	assert.InEpsilon(t, 10.0, testutil.ToFloat64(metrics.WebSocketClients), 1e-9)
}

func TestMetricsMiddleware(t *testing.T) {
	// Initialize metrics
	metrics := NewServiceMetrics("test_middleware")

	// Create Echo instance
	e := echo.New()

	// Add middleware
	e.Use(Middleware(metrics))

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
	requests := testutil.ToFloat64(metrics.RequestsTotal.WithLabelValues("items", "GET", "200"))
	assert.InEpsilon(t, 1.0, requests, 1e-9)
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
	metrics := NewServiceMetrics("test_cache_wrap")
	wrapper := NewCacheMetricsWrapper("redis", metrics)

	// Record operations
	wrapper.RecordHit()
	wrapper.RecordHit()
	wrapper.RecordMiss()

	// Verify counts
	hits := testutil.ToFloat64(metrics.CacheHits.WithLabelValues("redis"))
	misses := testutil.ToFloat64(metrics.CacheMisses.WithLabelValues("redis"))

	assert.InEpsilon(t, 2.0, hits, 1e-9)
	assert.InEpsilon(t, 1.0, misses, 1e-9)
}

func TestDBMetricsWrapper(t *testing.T) {
	metrics := NewServiceMetrics("test_db_wrap")
	wrapper := NewDBMetricsWrapper(metrics)

	// Record query
	done := wrapper.RecordQuery("SELECT")
	time.Sleep(metricsTestShortSleep)
	done()

	// Record transaction
	wrapper.RecordTransaction(true)
	wrapper.RecordTransaction(false)
	wrapper.RecordTransactionError("deadlock")

	// Verify counts
	committed := testutil.ToFloat64(metrics.DBTransactions.WithLabelValues("committed"))
	rolledBack := testutil.ToFloat64(metrics.DBTransactions.WithLabelValues("rolled_back"))
	errors := testutil.ToFloat64(metrics.DBTransactionErrors.WithLabelValues("deadlock"))

	assert.InEpsilon(t, 1.0, committed, 1e-9)
	assert.InEpsilon(t, 1.0, rolledBack, 1e-9)
	assert.InEpsilon(t, 1.0, errors, 1e-9)
}

func TestStorageMetricsWrapper(t *testing.T) {
	metrics := NewServiceMetrics("test_storage_wrap")
	wrapper := NewStorageMetricsWrapper(metrics)

	// Record operations
	wrapper.RecordUpload(true, 1024)
	wrapper.RecordUpload(false, 0)
	wrapper.RecordDownload(true, 2048)
	wrapper.RecordError("upload", "timeout")

	// Verify counts
	uploadSuccess := testutil.ToFloat64(metrics.StorageUploads.WithLabelValues("success"))
	uploadFailure := testutil.ToFloat64(metrics.StorageUploads.WithLabelValues("failure"))
	downloadSuccess := testutil.ToFloat64(metrics.StorageDownloads.WithLabelValues("success"))
	errors := testutil.ToFloat64(metrics.StorageErrors.WithLabelValues("upload", "timeout"))

	assert.InEpsilon(t, 1.0, uploadSuccess, 1e-9)
	assert.InEpsilon(t, 1.0, uploadFailure, 1e-9)
	assert.InEpsilon(t, 1.0, downloadSuccess, 1e-9)
	assert.InEpsilon(t, 1.0, errors, 1e-9)
}

func TestMessagingMetricsWrapper(t *testing.T) {
	metrics := NewServiceMetrics("test_msg_wrap")
	wrapper := NewMessagingMetricsWrapper(metrics)

	// Record operations
	wrapper.RecordPublish("test.subject", true)
	wrapper.RecordPublish("test.subject", false)
	wrapper.RecordConsume("test.subject")

	// Verify counts
	published := testutil.ToFloat64(metrics.MessagesPublished.WithLabelValues("test.subject"))
	errors := testutil.ToFloat64(metrics.MessagePublishErrors.WithLabelValues("test.subject"))
	consumed := testutil.ToFloat64(metrics.MessagesConsumed.WithLabelValues("test.subject"))

	assert.InEpsilon(t, 1.0, published, 1e-9)
	assert.InEpsilon(t, 1.0, errors, 1e-9)
	assert.InEpsilon(t, 1.0, consumed, 1e-9)
}

func TestAgentMetricsWrapper(t *testing.T) {
	metrics := NewServiceMetrics("test_agent_wrap")
	wrapper := NewAgentMetricsWrapper(metrics)

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
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.AgentRegistrations), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.AgentUnregistrations), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.AgentHeartbeats), 1e-9)
	assert.InEpsilon(t, 5.0, testutil.ToFloat64(metrics.ActiveAgents), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TasksAssigned.WithLabelValues("analyzer")), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TasksCompleted.WithLabelValues("analyzer", "success")), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TasksCompleted.WithLabelValues("analyzer", "failure")), 1e-9)
	assert.InEpsilon(t, 1.0, testutil.ToFloat64(metrics.TaskErrors.WithLabelValues("analyzer", "timeout")), 1e-9)
}

func TestInitializeMetrics(t *testing.T) {
	// Initialize global metrics
	InitializeMetrics("test_global")

	// Verify global instance is set
	metrics := GetMetrics()
	require.NotNil(t, metrics)
	assert.NotNil(t, metrics.RequestsTotal)
	assert.NotNil(t, metrics.ItemsCreated)
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
