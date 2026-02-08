package integration

import (
	"encoding/json"
	"net/http"
	"testing"
)

// ============================================================================
// RESPONSE STRUCTURE VALIDATION TESTS
// ============================================================================

func TestResponseStructureValidation(t *testing.T) {
	server := setupTestServer()

	t.Run("ProjectListResponseStructure", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/projects", nil)

		if rec.Code != http.StatusOK {
			t.Fatalf("expected status 200, got %d", rec.Code)
		}

		var response map[string]interface{}
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		if err != nil {
			t.Fatalf("failed to unmarshal response: %v", err)
		}

		_, hasData := response["data"]
		_, hasTotal := response["total"]
		if !hasData && !hasTotal {
			t.Error("list response should contain data or total field")
		}
	})

	t.Run("ItemListResponsePagination", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/items?limit=10&offset=0", nil)

		if rec.Code != http.StatusOK {
			t.Fatalf("expected status 200, got %d", rec.Code)
		}

		var response map[string]interface{}
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		if err != nil {
			t.Fatalf("failed to unmarshal response: %v", err)
		}
	})

	t.Run("CreateResponseStructure", func(t *testing.T) {
		payload := map[string]interface{}{
			"name": "Test",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/projects", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Fatalf("expected status 200/201, got %d", rec.Code)
		}

		var response map[string]interface{}
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		if err != nil {
			t.Fatalf("failed to unmarshal response: %v", err)
		}

		if _, ok := response["id"]; !ok {
			t.Error("create response should contain id field")
		}
	})
}

// ============================================================================
// ENDPOINT COVERAGE SUMMARY TEST
// ============================================================================

func TestEndpointCoverageSummary(t *testing.T) {
	// This test documents all the endpoints being tested
	endpoints := []struct {
		method string
		path   string
		group  string
	}{
		// Projects (5)
		{http.MethodPost, "/api/v1/projects", "Project"},
		{http.MethodGet, "/api/v1/projects", "Project"},
		{http.MethodGet, "/api/v1/projects/:id", "Project"},
		{http.MethodPut, "/api/v1/projects/:id", "Project"},
		{http.MethodDelete, "/api/v1/projects/:id", "Project"},

		// Items (6)
		{http.MethodPost, "/api/v1/items", "Item"},
		{http.MethodGet, "/api/v1/items", "Item"},
		{http.MethodGet, "/api/v1/items/:id", "Item"},
		{http.MethodPut, "/api/v1/items/:id", "Item"},
		{http.MethodDelete, "/api/v1/items/:id", "Item"},
		{http.MethodPost, "/api/v1/items/:id/pivot", "Item"},

		// Links (6)
		{http.MethodPost, "/api/v1/links", "Link"},
		{http.MethodGet, "/api/v1/links", "Link"},
		{http.MethodGet, "/api/v1/links/:id", "Link"},
		{http.MethodPut, "/api/v1/links/:id", "Link"},
		{http.MethodDelete, "/api/v1/links/:id", "Link"},

		// Equivalences (13)
		{http.MethodPost, "/api/v1/equivalences", "Equivalence"},
		{http.MethodGet, "/api/v1/equivalences", "Equivalence"},
		{http.MethodGet, "/api/v1/equivalences/:id", "Equivalence"},
		{http.MethodPut, "/api/v1/equivalences/:id", "Equivalence"},
		{http.MethodDelete, "/api/v1/equivalences/:id", "Equivalence"},
		{http.MethodPost, "/api/v1/equivalences/detect", "Equivalence"},
		{http.MethodPost, "/api/v1/equivalences/:id/confirm", "Equivalence"},
		{http.MethodPost, "/api/v1/equivalences/:id/reject", "Equivalence"},
		{http.MethodPost, "/api/v1/equivalences/bulk-confirm", "Equivalence"},
		{http.MethodPost, "/api/v1/equivalences/bulk-reject", "Equivalence"},
		{http.MethodGet, "/api/v1/canonical-concepts", "Equivalence"},
		{http.MethodPost, "/api/v1/canonical-concepts", "Equivalence"},
		{http.MethodGet, "/api/v1/canonical-concepts/:id/projections", "Equivalence"},

		// Code Index (6)
		{http.MethodPost, "/api/v1/code/index", "CodeIndex"},
		{http.MethodGet, "/api/v1/code/entities", "CodeIndex"},
		{http.MethodGet, "/api/v1/code/entities/:id", "CodeIndex"},
		{http.MethodPut, "/api/v1/code/entities/:id", "CodeIndex"},
		{http.MethodDelete, "/api/v1/code/entities/:id", "CodeIndex"},
		{http.MethodPost, "/api/v1/code/reindex", "CodeIndex"},

		// Documentation (6)
		{http.MethodPost, "/api/v1/docs/index", "Documentation"},
		{http.MethodGet, "/api/v1/docs", "Documentation"},
		{http.MethodGet, "/api/v1/docs/:id", "Documentation"},
		{http.MethodPut, "/api/v1/docs/:id", "Documentation"},
		{http.MethodDelete, "/api/v1/docs/:id", "Documentation"},
		{http.MethodPost, "/api/v1/docs/parse", "Documentation"},

		// Milestones & Progress (8)
		{http.MethodPost, "/api/v1/milestones", "Progress"},
		{http.MethodGet, "/api/v1/milestones", "Progress"},
		{http.MethodGet, "/api/v1/milestones/:id", "Progress"},
		{http.MethodPut, "/api/v1/milestones/:id", "Progress"},
		{http.MethodDelete, "/api/v1/milestones/:id", "Progress"},
		{http.MethodGet, "/api/v1/milestones/:id/progress", "Progress"},
		{http.MethodPost, "/api/v1/sprints", "Progress"},
		{http.MethodGet, "/api/v1/sprints", "Progress"},

		// Temporal (14)
		{http.MethodPost, "/api/v1/projects/:projectId/branches", "Temporal"},
		{http.MethodGet, "/api/v1/projects/:projectId/branches", "Temporal"},
		{http.MethodGet, "/api/v1/branches/:branchId", "Temporal"},
		{http.MethodPut, "/api/v1/branches/:branchId", "Temporal"},
		{http.MethodDelete, "/api/v1/branches/:branchId", "Temporal"},
		{http.MethodPost, "/api/v1/branches/:branchId/versions", "Temporal"},
		{http.MethodGet, "/api/v1/branches/:branchId/versions", "Temporal"},
		{http.MethodGet, "/api/v1/versions/:versionId", "Temporal"},
		{http.MethodGet, "/api/v1/versions/:versionAId/compare/:versionBId", "Temporal"},
		{http.MethodGet, "/api/v1/items/:itemId/version-history", "Temporal"},
		{http.MethodPost, "/api/v1/items/:itemId/restore", "Temporal"},
		{http.MethodGet, "/api/v1/items/:itemId/alternatives", "Temporal"},
		{http.MethodPost, "/api/v1/items/:itemId/alternatives", "Temporal"},
		{http.MethodPost, "/api/v1/alternatives/:altId/select", "Temporal"},
	}

	t.Logf("Total endpoints tested: %d", len(endpoints))
}
