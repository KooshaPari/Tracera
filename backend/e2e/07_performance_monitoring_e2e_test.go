//go:build e2e

package e2e

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 7: Performance Monitoring - Metrics, Benchmarks (25+ tests)

func TestE2E_Metrics_GraphPerformance(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Performance Project")

	// Create large graph
	for i := 0; i < 100; i++ {
		createTestItem(t, srv, projectID, "Item "+string(rune(i)), "requirement")
	}

	resp, err := http.Get(srv.URL + "/api/projects/" + projectID + "/metrics/performance")
	require.NoError(t, err)
	defer resp.Body.Close()

	var metrics map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&metrics))

	assert.NotEmpty(t, metrics["render_time"])
	assert.NotEmpty(t, metrics["node_count"])
}

func TestE2E_Metrics_APILatency(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	resp, err := http.Get(srv.URL + "/api/metrics/latency")
	require.NoError(t, err)
	defer resp.Body.Close()

	var latency map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&latency))

	assert.NotEmpty(t, latency["p50"])
	assert.NotEmpty(t, latency["p95"])
	assert.NotEmpty(t, latency["p99"])
}
