package integration

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/google/uuid"
)

// ============================================================================
// PROJECT ENDPOINT TESTS
// ============================================================================

func TestProjectEndpoints(t *testing.T) {
	server := setupTestServer()

	t.Run("CreateProject", func(t *testing.T) {
		payload := map[string]interface{}{
			"name":        "Test Project",
			"description": "A test project",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/projects", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListProjects", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/projects", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}

		var response map[string]interface{}
		json.Unmarshal(rec.Body.Bytes(), &response)
		_, hasData := response["data"]
		_, hasTotal := response["total"]
		if !hasData && !hasTotal {
			t.Error("response should contain data or total field")
		}
	})

	t.Run("GetProjectByID", func(t *testing.T) {
		projectID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/projects/"+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateProject", func(t *testing.T) {
		projectID := uuid.New().String()
		updatePayload := map[string]interface{}{
			"name":        "Updated Project Name",
			"description": "Updated description",
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/projects/"+projectID, updatePayload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteProject", func(t *testing.T) {
		projectID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/projects/"+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}

// ============================================================================
// ITEM ENDPOINT TESTS
// ============================================================================

func TestItemEndpoints(t *testing.T) {
	server := setupTestServer()

	t.Run("CreateItem", func(t *testing.T) {
		payload := map[string]interface{}{
			"title":       "Test Item",
			"description": "A test item",
			"type":        "feature",
			"status":      "open",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/items", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListItems", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/items", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetItemByID", func(t *testing.T) {
		itemID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/items/"+itemID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateItem", func(t *testing.T) {
		itemID := uuid.New().String()
		updatePayload := map[string]interface{}{
			"title":  "Updated Item Title",
			"status": "closed",
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/items/"+itemID, updatePayload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteItem", func(t *testing.T) {
		itemID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/items/"+itemID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("PivotNavigation", func(t *testing.T) {
		itemID := uuid.New().String()
		payload := map[string]interface{}{
			"perspectives": []string{"code", "requirements"},
			"max_depth":    2,
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/items/"+itemID+"/pivot", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}

// ============================================================================
// LINK ENDPOINT TESTS
// ============================================================================

func TestLinkEndpoints(t *testing.T) {
	server := setupTestServer()

	t.Run("CreateLink", func(t *testing.T) {
		payload := map[string]interface{}{
			"source_id": uuid.New().String(),
			"target_id": uuid.New().String(),
			"type":      "relates_to",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/links", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListLinks", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/links", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetLinkByID", func(t *testing.T) {
		linkID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/links/"+linkID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateLink", func(t *testing.T) {
		linkID := uuid.New().String()
		updatePayload := map[string]interface{}{
			"type": "depends_on",
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/links/"+linkID, updatePayload)

		// CRITICAL: Should return 200, NOT 501
		if rec.Code == http.StatusNotImplemented {
			t.Errorf("update link should not return 501 (Not Implemented), got %d", rec.Code)
		}
		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteLink", func(t *testing.T) {
		linkID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/links/"+linkID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}
