//go:build !integration

package health

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewChecker(t *testing.T) {
	hc := NewChecker(nil, nil, "http://python:8000", "http://temporal:7233", "1.0.0")
	require.NotNil(t, hc)
	assert.Equal(t, "http://python:8000", hc.pythonURL)
	assert.Equal(t, "http://temporal:7233", hc.temporalURL)
	assert.Equal(t, "1.0.0", hc.version)
	assert.InEpsilon(t, defaultDiskThreshold, hc.diskThreshold, 1e-9)
	assert.InEpsilon(t, defaultMemoryThreshold, hc.memoryThreshold, 1e-9)
}

func TestCheckDatabase_NilDB(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	result := hc.CheckDatabase(context.Background())

	assert.Equal(t, "database", result.Name)
	assert.Equal(t, StatusUnhealthy, result.Status)
	assert.Equal(t, "database not configured", result.Message)
	assert.False(t, result.Timestamp.IsZero())
}

func TestCheckRedis_NilClient(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	result := hc.CheckRedis(context.Background())

	assert.Equal(t, "redis", result.Name)
	assert.Equal(t, StatusDegraded, result.Status)
	assert.Equal(t, "redis not configured", result.Message)
}

func TestCheckPythonBackend_EmptyURL(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	result := hc.CheckPythonBackend(context.Background())

	assert.Equal(t, "python-backend", result.Name)
	assert.Equal(t, StatusDegraded, result.Status)
	assert.Contains(t, result.Message, "not configured")
}

func TestCheckTemporal_EmptyURL(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	result := hc.CheckTemporal(context.Background())

	assert.Equal(t, "temporal", result.Name)
	assert.Equal(t, StatusDegraded, result.Status)
	assert.Contains(t, result.Message, "not configured")
}

func TestCheckPythonBackend_HealthyServer(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	hc := NewChecker(nil, nil, server.URL, "", "v1")
	result := hc.CheckPythonBackend(context.Background())

	assert.Equal(t, "python-backend", result.Name)
	assert.Equal(t, StatusHealthy, result.Status)
	assert.Equal(t, connectionOKMessage, result.Message)
}

func TestCheckPythonBackend_UnhealthyServer(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusServiceUnavailable)
	}))
	defer server.Close()

	hc := NewChecker(nil, nil, server.URL, "", "v1")
	result := hc.CheckPythonBackend(context.Background())

	assert.Equal(t, "python-backend", result.Name)
	assert.Equal(t, StatusUnhealthy, result.Status)
	assert.Contains(t, result.Message, "unhealthy status: 503")
}

func TestCheckTemporal_HealthyServer(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	hc := NewChecker(nil, nil, "", server.URL, "v1")
	result := hc.CheckTemporal(context.Background())

	assert.Equal(t, "temporal", result.Name)
	assert.Equal(t, StatusHealthy, result.Status)
}

func TestLivenessProbe(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	err := hc.LivenessProbe(context.Background())
	assert.NoError(t, err)
}

func TestReadinessProbe_NilDB(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	err := hc.ReadinessProbe(context.Background())
	require.Error(t, err)
	assert.Contains(t, err.Error(), "database not configured")
}

func TestStartupProbe_NilDB(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	err := hc.StartupProbe(context.Background())
	require.Error(t, err)
	assert.Contains(t, err.Error(), "database not configured")
}

func TestCheckDiskSpace(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	result := hc.CheckDiskSpace(context.Background())

	assert.Equal(t, "disk", result.Name)
	// On a real machine, disk check should succeed
	assert.NotEmpty(t, result.Message)
	assert.Contains(t, []Status{StatusHealthy, StatusDegraded, StatusUnhealthy}, result.Status)
}

func TestCheckMemory(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	result := hc.CheckMemory(context.Background())

	assert.Equal(t, "memory", result.Name)
	assert.NotEmpty(t, result.Message)
	assert.Contains(t, []Status{StatusHealthy, StatusDegraded, StatusUnhealthy}, result.Status)
}

func TestCheck_OverallReport(t *testing.T) {
	hc := NewChecker(nil, nil, "", "", "v1")
	report := hc.Check(context.Background())

	assert.Equal(t, "v1", report.Version)
	assert.False(t, report.Timestamp.IsZero())
	assert.NotEmpty(t, report.Components)

	// Should contain at minimum disk and memory
	_, hasDisk := report.Components["disk"]
	assert.True(t, hasDisk)
	_, hasMemory := report.Components["memory"]
	assert.True(t, hasMemory)
}

func TestCheck_OverallStatusDeterminedByWorstComponent(t *testing.T) {
	// When database is nil, it returns unhealthy, so overall should be unhealthy
	hc := NewChecker(nil, nil, "", "", "v1")
	report := hc.Check(context.Background())

	// Database nil = unhealthy, so overall should be unhealthy
	assert.Equal(t, StatusUnhealthy, report.Status)
}

func TestEvaluateHTTPHealth(t *testing.T) {
	tests := []struct {
		name              string
		statusCode        int
		latency           int64
		nonOKStatus       Status
		latencyDegradedMs int64
		wantStatus        Status
		wantContains      string
	}{
		{
			name:              "healthy response",
			statusCode:        200,
			latency:           50,
			nonOKStatus:       StatusUnhealthy,
			latencyDegradedMs: 1000,
			wantStatus:        StatusHealthy,
			wantContains:      connectionOKMessage,
		},
		{
			name:              "non-ok status code",
			statusCode:        503,
			latency:           50,
			nonOKStatus:       StatusUnhealthy,
			latencyDegradedMs: 1000,
			wantStatus:        StatusUnhealthy,
			wantContains:      "unhealthy status: 503",
		},
		{
			name:              "high latency",
			statusCode:        200,
			latency:           2000,
			nonOKStatus:       StatusUnhealthy,
			latencyDegradedMs: 1000,
			wantStatus:        StatusDegraded,
			wantContains:      "high latency",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			resp := &http.Response{StatusCode: tt.statusCode}
			status, message := evaluateHTTPHealth(resp, tt.latency, tt.nonOKStatus, tt.latencyDegradedMs)
			assert.Equal(t, tt.wantStatus, status)
			assert.Contains(t, message, tt.wantContains)
		})
	}
}

func TestComponentHealth_Helper(t *testing.T) {
	ch := componentHealth("test", StatusHealthy, "ok", 42)
	assert.Equal(t, "test", ch.Name)
	assert.Equal(t, StatusHealthy, ch.Status)
	assert.Equal(t, "ok", ch.Message)
	assert.Equal(t, int64(42), ch.LatencyMs)
	assert.False(t, ch.Timestamp.IsZero())
}

func TestLogReport_DoesNotPanic(t *testing.T) {
	report := Report{
		Status:  StatusHealthy,
		Version: "v1",
		Components: map[string]ComponentHealth{
			"test": {Name: "test", Status: StatusHealthy, Message: "ok"},
		},
	}
	// Should not panic
	assert.NotPanics(t, func() {
		LogReport(report)
	})
}

func TestStatusConstants(t *testing.T) {
	assert.Equal(t, StatusHealthy, Status("healthy"))
	assert.Equal(t, StatusDegraded, Status("degraded"))
	assert.Equal(t, StatusUnhealthy, Status("unhealthy"))
}
