package integration

import (
	"net/http"
	"testing"

	"github.com/google/uuid"
)

// ============================================================================
// EQUIVALENCE ENDPOINT TESTS (13 tests)
// ============================================================================

func TestEquivalenceEndpoints(t *testing.T) {
	server := setupTestServer()

	projectID := uuid.New().String()
	sourceItemID := uuid.New().String()
	targetItemID := uuid.New().String()
	equivalenceID := uuid.New().String()

	t.Run("CreateEquivalence", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id":     projectID,
			"source_item_id": sourceItemID,
			"target_item_id": targetItemID,
			"link_type":      "same_as",
			"confidence":     0.95,
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/equivalences", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("ListEquivalences", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/equivalences?project_id="+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetEquivalenceByID", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/equivalences/"+equivalenceID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("UpdateEquivalence", func(t *testing.T) {
		updatePayload := map[string]interface{}{
			"status":     "confirmed",
			"confidence": 0.98,
		}
		rec := makeRequest(t, server, http.MethodPut, "/api/v1/equivalences/"+equivalenceID, updatePayload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DeleteEquivalence", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodDelete, "/api/v1/equivalences/"+equivalenceID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("DetectEquivalences", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id":     projectID,
			"source_item_id": sourceItemID,
			"min_confidence": 0.7,
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/equivalences/detect", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("ConfirmEquivalence", func(t *testing.T) {
		payload := map[string]interface{}{
			"reason": "Manual confirmation",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/equivalences/"+equivalenceID+"/confirm", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("RejectEquivalence", func(t *testing.T) {
		payload := map[string]interface{}{
			"reason": "Not an equivalence",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/equivalences/"+equivalenceID+"/reject", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("BulkConfirmEquivalences", func(t *testing.T) {
		payload := map[string]interface{}{
			"equivalence_ids": []string{equivalenceID, uuid.New().String()},
			"reason":          "Bulk confirmation",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/equivalences/bulk-confirm", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("BulkRejectEquivalences", func(t *testing.T) {
		payload := map[string]interface{}{
			"equivalence_ids": []string{equivalenceID},
			"reason":          "Bulk rejection",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/equivalences/bulk-reject", payload)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("GetCanonicalConcepts", func(t *testing.T) {
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/canonical-concepts?project_id="+projectID, nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})

	t.Run("CreateCanonicalConcept", func(t *testing.T) {
		payload := map[string]interface{}{
			"project_id":  projectID,
			"name":        "Test Concept",
			"description": "A test canonical concept",
		}
		rec := makeRequest(t, server, http.MethodPost, "/api/v1/canonical-concepts", payload)

		if rec.Code != http.StatusCreated && rec.Code != http.StatusOK {
			t.Errorf("expected status 200/201, got %d", rec.Code)
		}
	})

	t.Run("GetProjections", func(t *testing.T) {
		conceptID := uuid.New().String()
		rec := makeRequest(t, server, http.MethodGet, "/api/v1/canonical-concepts/"+conceptID+"/projections", nil)

		if rec.Code != http.StatusOK {
			t.Errorf("expected status 200, got %d", rec.Code)
		}
	})
}
