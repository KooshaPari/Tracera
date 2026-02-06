//go:build !integration

package profiling

import (
	"context"
	"net/http"
	"net/http/httptest"
	"runtime"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDefaultConfig(t *testing.T) {
	cfg := DefaultConfig()
	assert.True(t, cfg.Enabled)
	assert.Equal(t, "6060", cfg.Port)
	assert.Equal(t, 1, cfg.BlockProfileRate)
	assert.Equal(t, 1, cfg.MutexProfileFrac)
	assert.True(t, cfg.EnableMemStats)
	assert.True(t, cfg.EnableGCStats)
}

func TestNewProfilingServer(t *testing.T) {
	cfg := DefaultConfig()
	srv := NewProfilingServer(cfg)

	require.NotNil(t, srv)
	assert.Equal(t, cfg, srv.config)
	assert.NotNil(t, srv.server)
	assert.NotNil(t, srv.mux)
	assert.Equal(t, ":6060", srv.server.Addr)
}

func TestNewProfilingServer_CustomPort(t *testing.T) {
	cfg := Config{Enabled: true, Port: "9090"}
	srv := NewProfilingServer(cfg)

	require.NotNil(t, srv)
	assert.Equal(t, ":9090", srv.server.Addr)
}

func TestStop_Disabled(t *testing.T) {
	cfg := Config{Enabled: false, Port: "0"}
	srv := NewProfilingServer(cfg)

	err := srv.Stop(context.Background())
	assert.NoError(t, err)
}

func TestStart_Disabled(t *testing.T) {
	cfg := Config{Enabled: false, Port: "0"}
	srv := NewProfilingServer(cfg)

	err := srv.Start()
	assert.NoError(t, err)
}

func TestMetricsHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/debug/metrics", nil)
	rec := httptest.NewRecorder()

	metricsHandler(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)
	assert.Equal(t, "application/json", rec.Header().Get("Content-Type"))
	body := rec.Body.String()
	assert.Contains(t, body, "memory")
	assert.Contains(t, body, "gc")
	assert.Contains(t, body, "goroutines")
	assert.Contains(t, body, "alloc_bytes")
	assert.Contains(t, body, "heap_alloc_bytes")
}

func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/debug/health", nil)
	rec := httptest.NewRecorder()

	healthHandler(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)
	assert.Equal(t, "application/json", rec.Header().Get("Content-Type"))
	body := rec.Body.String()
	assert.Contains(t, body, `"status": "ok"`)
	assert.Contains(t, body, "goroutines")
	assert.Contains(t, body, "go_version")
	assert.Contains(t, body, "num_cpu")
}

func TestFormatMemStats(t *testing.T) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	result := formatMemStats(&m)
	assert.Contains(t, result, "alloc_bytes")
	assert.Contains(t, result, "total_alloc_bytes")
	assert.Contains(t, result, "sys_bytes")
	assert.Contains(t, result, "heap_alloc_bytes")
	assert.Contains(t, result, "heap_objects")
	assert.Contains(t, result, "stack_inuse_bytes")
}

func TestWriteMetricsResponse(t *testing.T) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	rec := httptest.NewRecorder()
	writeMetricsResponse(rec, &m)

	assert.Equal(t, "application/json", rec.Header().Get("Content-Type"))
	body := rec.Body.String()
	assert.Contains(t, body, "num_gc")
	assert.Contains(t, body, "gc_cpu_fraction")
}
