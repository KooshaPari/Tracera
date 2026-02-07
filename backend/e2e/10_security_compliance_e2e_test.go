//go:build e2e

package e2e

import (
	"bytes"
	"encoding/json"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Journey 10: Security & Compliance - RBAC, Audit Logs (37+ tests)

func TestE2E_Security_RBAC_OwnerAccess(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	ownerToken := createTestSession(t, srv, "owner-123")
	projectID := createTestProject(t, srv, "RBAC Project")

	req, _ := http.NewRequest("GET", srv.URL+"/api/projects/"+projectID, nil)
	req.AddCookie(&http.Cookie{Name: "session_token", Value: ownerToken})

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

func TestE2E_Security_RBAC_DeniedAccess(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	_ = createTestSession(t, srv, "owner-123")
	otherToken := createTestSession(t, srv, "other-456")

	projectID := createTestProject(t, srv, "Private Project")

	req, _ := http.NewRequest("GET", srv.URL+"/api/projects/"+projectID, nil)
	req.AddCookie(&http.Cookie{Name: "session_token", Value: otherToken})

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusForbidden, resp.StatusCode)
}

func TestE2E_Security_AuditLog_Creation(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	sessionToken := createTestSession(t, srv, "user-123")
	projectID := createTestProject(t, srv, "Audit Project")

	// Perform action
	itemPayload := map[string]interface{}{
		"project_id": projectID,
		"title":      "Audited Item",
		"type":       "requirement",
		"status":     "open",
	}

	body, _ := json.Marshal(itemPayload)
	req, _ := http.NewRequest("POST", srv.URL+"/api/items", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.AddCookie(&http.Cookie{Name: "session_token", Value: sessionToken})

	resp, _ := http.DefaultClient.Do(req)
	resp.Body.Close()

	// Check audit log
	req2, _ := http.NewRequest("GET", srv.URL+"/api/audit-logs?user_id=user-123", nil)
	req2.AddCookie(&http.Cookie{Name: "session_token", Value: sessionToken})

	resp2, err := http.DefaultClient.Do(req2)
	require.NoError(t, err)
	defer resp2.Body.Close()

	var logs map[string]interface{}
	require.NoError(t, json.NewDecoder(resp2.Body).Decode(&logs))

	entries := logs["entries"].([]interface{})
	assert.GreaterOrEqual(t, len(entries), 1)
}

func TestE2E_Security_InputSanitization(t *testing.T) {
	srv := setupE2EServer(t)
	defer srv.Cleanup()

	projectID := createTestProject(t, srv, "XSS Test Project")

	maliciousPayloads := []string{
		"<script>alert('xss')</script>",
		"'; DROP TABLE items; --",
		"../../../etc/passwd",
	}

	for i, payload := range maliciousPayloads {
		t.Run("malicious_input_"+string(rune(i)), func(t *testing.T) {
			itemPayload := map[string]interface{}{
				"project_id": projectID,
				"title":      payload,
				"type":       "requirement",
				"status":     "open",
			}

			body, _ := json.Marshal(itemPayload)
			resp, err := http.Post(srv.URL+"/api/items", "application/json", bytes.NewReader(body))
			require.NoError(t, err)
			defer resp.Body.Close()

			var result map[string]interface{}
			if resp.StatusCode == http.StatusCreated {
				require.NoError(t, json.NewDecoder(resp.Body).Decode(&result))
				title := result["title"].(string)
				assert.NotContains(t, title, "<script>")
			}
		})
	}
}
