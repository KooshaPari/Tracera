package clients_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/kooshapari/tracertm-backend/internal/clients"
)

const (
	zombieStaleWindowLong  = 90 * 24 * time.Hour
	zombieStaleWindowShort = 30 * 24 * time.Hour
)

func TestChaosClient_DetectZombies(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/v1/chaos/zombies", r.URL.Path)
		assert.Equal(t, "POST", r.Method)

		// Verify request body
		var req clients.DetectZombiesRequest
		err := json.NewDecoder(r.Body).Decode(&req)
		assert.NoError(t, err)
		assert.Equal(t, "test-project", req.ProjectID)

		// Return mock response
		response := clients.ZombieReport{
			ProjectID:  "test-project",
			DetectedAt: time.Now(),
			ZombieItems: []clients.ZombieItem{
				{
					ItemID:      "item-1",
					ItemType:    "requirement",
					Reason:      "no links for 90 days",
					LastUpdated: time.Now().Add(-zombieStaleWindowLong),
				},
				{
					ItemID:      "item-2",
					ItemType:    "feature",
					Reason:      "orphaned - no parent",
					LastUpdated: time.Now().Add(-zombieStaleWindowShort),
				},
			},
			Recommendations: []string{
				"Review item-1 for relevance",
				"Link item-2 to a parent or archive",
			},
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	chaosClient := clients.NewChaosClient(pythonClient)

	result, err := chaosClient.DetectZombies(context.Background(), clients.DetectZombiesRequest{
		ProjectID: "test-project",
	})

	require.NoError(t, err)
	assert.Equal(t, "test-project", result.ProjectID)
	assert.Len(t, result.ZombieItems, 2)
	assert.Len(t, result.Recommendations, 2)
	assert.Equal(t, "item-1", result.ZombieItems[0].ItemID)
	assert.Equal(t, "requirement", result.ZombieItems[0].ItemType)
}

func TestChaosClient_AnalyzeImpact(t *testing.T) {
	// Create a mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/api/v1/chaos/impact/item-123", r.URL.Path)
		assert.Equal(t, "GET", r.Method)

		response := clients.ImpactAnalysis{
			ItemID:           "item-123",
			DirectDependents: 5,
			TotalImpact:      15,
			CriticalPaths: [][]string{
				{"item-123", "item-456", "item-789"},
				{"item-123", "item-abc"},
			},
			RiskLevel: "high",
			Details: map[string]interface{}{
				"affected_features": 3,
				"affected_tests":    12,
			},
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(response); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}))
	defer server.Close()

	pythonClient := clients.NewPythonServiceClient(server.URL, "test-token", nil)
	chaosClient := clients.NewChaosClient(pythonClient)

	result, err := chaosClient.AnalyzeImpact(context.Background(), "item-123")

	require.NoError(t, err)
	assert.Equal(t, "item-123", result.ItemID)
	assert.Equal(t, 5, result.DirectDependents)
	assert.Equal(t, 15, result.TotalImpact)
	assert.Equal(t, "high", result.RiskLevel)
	assert.Len(t, result.CriticalPaths, 2)
	assert.Len(t, result.CriticalPaths[0], 3)
}
