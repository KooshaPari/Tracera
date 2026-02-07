//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 6: Temporal Workflows - Versioning, Snapshots (30+ tests)

func TestE2E_Temporal_CreateSnapshot(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Snapshot Project")

	payload := map[string]interface{}{
		"project_id": projectID,
		"message":    "Initial snapshot",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/snapshots", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	var result map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
	assert.NotEmpty(t, result["snapshot_id"])
}

func TestE2E_Temporal_ListVersions(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Versioning Project")
	item := createTestItem(t, srv, projectID, "Versioned Item", "requirement")

	// Create multiple versions by updating
	for i := 1; i <= 3; i++ {
		updatePayload := map[string]interface{}{
			"title": "Version " + string(rune(i)),
		}
		body, _ := json.Marshal(updatePayload)
		req, _ := http.NewRequest("PATCH", srv.URL+"/api/items/"+item, bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		resp, _ := http.DefaultClient.Do(req)
		resp.Body.Close()
		time.Sleep(100 * time.Millisecond)
	}

	resp, err := http.Get(srv.URL + "/api/items/" + item + "/versions")
	require.NoError(t, err)
	defer resp.Body.Close()

	var versions map[string]interface{}
	require.NoError(t, json.NewDecoder(resp.Body).Decode(&versions))

	versionList := versions["versions"].([]interface{})
	assert.GreaterOrEqual(t, len(versionList), 3)
}

func TestE2E_Temporal_RestoreSnapshot(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Restore Project")

	// Create snapshot
	snapshotPayload := map[string]interface{}{
		"project_id": projectID,
		"message":    "Before changes",
	}
	body, _ := json.Marshal(snapshotPayload)
	resp1, err := http.Post(srv.URL+"/api/snapshots", "application/json", bytes.NewReader(body))
	require.NoError(t, err)

	var snapshot map[string]interface{}
	require.NoError(t, json.NewDecoder(resp1.Body).Decode(&snapshot))
	resp1.Body.Close()

	snapshotID := snapshot["snapshot_id"].(string)

	// Restore snapshot
	resp2, err := http.Post(srv.URL+"/api/snapshots/"+snapshotID+"/restore", "application/json", nil)
	require.NoError(t, err)
	defer resp2.Body.Close()

	assert.Equal(t, http.StatusOK, resp2.StatusCode)
}
