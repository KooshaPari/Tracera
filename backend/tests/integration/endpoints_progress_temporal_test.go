package integration

import (
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/google/uuid"
)

// ============================================================================
// PROGRESS & MILESTONE ENDPOINT TESTS (8 tests)
// ============================================================================

func TestProgressEndpoints(t *testing.T) {
	server := setupTestServer()

	projectID := uuid.New().String()
	milestoneID := uuid.New().String()

	t.Run("CreateMilestone", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id":  projectID,
			"title":       "Version 1.0",
			"target_date": time.Now().AddDate(0, 1, 0).Format(time.RFC3339),
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/milestones", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListMilestones", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/milestones?project_id="+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetMilestone", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/milestones/"+milestoneID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateMilestone", func(t *testing.T) {
		updatePayload := map[string]interface{}{
			"title":  "Updated Milestone",
			"status": "in_progress",
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/milestones/"+milestoneID, updatePayload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteMilestone", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/milestones/"+milestoneID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetMilestoneProgress", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/milestones/"+milestoneID+"/progress", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("CreateSprint", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id": projectID,
			"title":      "Sprint 1",
			"start_date": time.Now().Format(time.RFC3339),
			"end_date":   time.Now().AddDate(0, 0, 14).Format(time.RFC3339),
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/sprints", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListSprints", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/sprints?project_id="+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}

// ============================================================================
// TEMPORAL ENDPOINT TESTS (10 tests)
// ============================================================================

func TestTemporalEndpoints(t *testing.T) {
	server := setupTestServer()

	projectID := uuid.New().String()
	branchID := uuid.New().String()
	itemID := uuid.New().String()
	altID := uuid.New().String()

	t.Run("CreateBranch", func(t *testing.T) {
		payload := map[string]interface{}{
			"name":        "feature/new-ui",
			"description": "Work on new UI",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/projects/"+projectID+"/branches", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListBranches", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/projects/"+projectID+"/branches", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetBranch", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/branches/"+branchID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("CreateVersion", func(t *testing.T) {
		payload := map[string]interface{}{
			"title":       "Version 0.1.0",
			"description": "Alpha release",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/branches/"+branchID+"/versions", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListVersions", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/branches/"+branchID+"/versions", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("CompareVersions", func(t *testing.T) {
		versionAID := uuid.New().String()
		versionBID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodGet, fmt.Sprintf("/api/v1/versions/%s/compare/%s", versionAID, versionBID), nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetItemVersionHistory", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/items/"+itemID+"/version-history", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("RestoreItemVersion", func(t *testing.T) {
		payload := map[string]interface{}{
			"version_id": uuid.New().String(),
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/items/"+itemID+"/restore", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("ListAlternatives", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/items/"+itemID+"/alternatives", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("SelectAlternative", func(t *testing.T) {
		payload := map[string]interface{}{
			"reason": "Selected this alternative",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/alternatives/"+altID+"/select", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}
