package integration

import (
	"net/http"
	"testing"

	"github.com/google/uuid"
)

// ============================================================================
// CODE INDEX ENDPOINT TESTS (6 tests)
// ============================================================================

func TestCodeIndexEndpoints(t *testing.T) {
	server := setupTestServer()

	projectID := uuid.New().String()
	entityID := uuid.New().String()

	t.Run("IndexCode", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id": projectID,
			"file_path":  "src/main.go",
			"content":    "package main",
			"language":   "go",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/code/index", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("ListCodeEntities", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/code/entities?project_id="+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetCodeEntity", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/code/entities/"+entityID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateCodeEntity", func(t *testing.T) {
		updatePayload := map[string]interface{}{
			"name": "UpdatedFunction",
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/code/entities/"+entityID, updatePayload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteCodeEntity", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/code/entities/"+entityID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("ReindexCode", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id": projectID,
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/code/reindex", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}

// ============================================================================
// DOCUMENTATION INDEX ENDPOINT TESTS (6 tests)
// ============================================================================

func TestDocIndexEndpoints(t *testing.T) {
	server := setupTestServer()

	projectID := uuid.New().String()
	docID := uuid.New().String()

	t.Run("IndexDocumentation", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id": projectID,
			"title":      "API Documentation",
			"content":    "# API Docs",
			"file_path":  "docs/api.md",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/docs/index", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("ListDocuments", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/docs?project_id="+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetDocument", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/docs/"+docID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateDocument", func(t *testing.T) {
		updatePayload := map[string]interface{}{
			"title":   "Updated API Documentation",
			"content": "# Updated",
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/docs/"+docID, updatePayload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteDocument", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/docs/"+docID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("ParseDocument", func(t *testing.T) {
		payload := map[string]interface{}{
			"file_path": "docs/guide.md",
			"content":   "# User Guide",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/docs/parse", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}
