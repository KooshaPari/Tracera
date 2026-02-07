//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"net/http"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 9: Data Validation - Schema, Constraints (35+ tests)

func TestE2E_Validation_RequiredFields(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Validation Project")

	invalidPayloads := []map[string]interface{}{
		{"project_id": projectID, "type": "requirement"},
		{"project_id": projectID, "title": ""},
		{"title": "Test", "type": "requirement"},
	}

	for i, payload := range invalidPayloads {
		t.Run("invalid_payload_"+string(rune(i)), func(t *testing.T) {
			body, _ := json.Marshal(payload)
			resp, err := http.Post(srv.URL+"/api/items", "application/json", bytes.NewReader(body))
			require.NoError(t, err)
			defer resp.Body.Close()

			assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
		})
	}
}

func TestE2E_Validation_DataTypes(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Type Validation Project")

	payload := map[string]interface{}{
		"project_id": projectID,
		"title":      "Test Item",
		"type":       "invalid_type",
		"status":     "open",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/items", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
}

func TestE2E_Validation_LengthConstraints(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "Length Validation Project")

	payload := map[string]interface{}{
		"project_id": projectID,
		"title":      strings.Repeat("a", 1000),
		"type":       "requirement",
		"status":     "open",
	}

	body, _ := json.Marshal(payload)
	resp, err := http.Post(srv.URL+"/api/items", "application/json", bytes.NewReader(body))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusBadRequest, resp.StatusCode)
}
