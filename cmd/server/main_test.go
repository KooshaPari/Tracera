package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/go-chi/chi/v5"
)

func setupTestDB(t *testing.T) func() {
	t.Helper()
	tmp := t.TempDir() + "/test.db"
	os.Setenv("TRACERA_DB", tmp)
	if err := initDB(); err != nil {
		t.Fatalf("initDB: %v", err)
	}
	return func() {
		if db != nil {
			db.Close()
			db = nil
		}
	}
}

func testRouter() http.Handler {
	r := chi.NewRouter()
	r.Route("/api/v1", func(r chi.Router) {
		r.Get("/trace-links", listTraceLinks)
		r.Post("/trace-links", createTraceLink)
		r.Get("/trace-links/{id}", getTraceLink)
		r.Delete("/trace-links/{id}", deleteTraceLink)
		r.Get("/requirements", listRequirements)
		r.Post("/requirements", createRequirement)
		r.Get("/requirements/{id}", getRequirement)
		r.Delete("/requirements/{id}", deleteRequirement)
		r.Get("/artifacts", listArtifacts)
		r.Post("/artifacts", createArtifact)
		r.Get("/artifacts/{id}", getArtifact)
		r.Delete("/artifacts/{id}", deleteArtifact)
	})
	return r
}

func TestListTraceLinks(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/trace-links", nil)
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rr.Code)
	}
	var links []TraceLink
	if err := json.NewDecoder(rr.Body).Decode(&links); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if len(links) < 2 {
		t.Errorf("want >= 2 seed links, got %d", len(links))
	}
}

func TestCreateTraceLink(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"source_id":"r1","target_id":"a1","link_type":"satisfies","confidence":0.9}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusCreated {
		t.Fatalf("want 201, got %d: %s", rr.Code, rr.Body)
	}
	var created TraceLink
	if err := json.NewDecoder(rr.Body).Decode(&created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if created.ID == "" {
		t.Fatal("created ID is empty")
	}
	if created.SourceID != "r1" {
		t.Errorf("want source_id=r1, got %s", created.SourceID)
	}
}

func TestDeleteTraceLink(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	// First create one.
	body := `{"source_id":"r1","target_id":"a1","link_type":"satisfies","confidence":0.9}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created TraceLink
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	// Delete it.
	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodDelete, "/api/v1/trace-links/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusNoContent {
		t.Fatalf("delete: want 204, got %d", rr2.Code)
	}
}

func TestDeleteTraceLinkNotFound(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/trace-links/does-not-exist", nil)
	testRouter().ServeHTTP(rr, req)
	if rr.Code != http.StatusNotFound {
		t.Fatalf("want 404, got %d", rr.Code)
	}
}

func TestCreateRequirement(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"title":"System shall authenticate","description":"Auth requirement","status":"draft"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	if rr.Code != http.StatusCreated {
		t.Fatalf("want 201, got %d: %s", rr.Code, rr.Body)
	}
	var r Requirement
	json.NewDecoder(rr.Body).Decode(&r) //nolint:errcheck
	if r.Title != "System shall authenticate" {
		t.Errorf("want title='System shall authenticate', got %q", r.Title)
	}
}

func TestListRequirements(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/requirements", nil)
	testRouter().ServeHTTP(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rr.Code)
	}
	var reqs []Requirement
	json.NewDecoder(rr.Body).Decode(&reqs) //nolint:errcheck
	if len(reqs) < 2 {
		t.Errorf("want >= 2 seed requirements, got %d", len(reqs))
	}
}

func TestCreateArtifact(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"name":"auth-service","kind":"implementation","version":"1.0.0"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	if rr.Code != http.StatusCreated {
		t.Fatalf("want 201, got %d: %s", rr.Code, rr.Body)
	}
}

func TestHealthEndpoint(t *testing.T) {
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	http.HandlerFunc(healthHandler).ServeHTTP(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rr.Code)
	}
}

func TestGetTraceLink(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"source_id":"r1","target_id":"a1","link_type":"satisfies","confidence":0.9}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created TraceLink
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodGet, "/api/v1/trace-links/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusOK {
		t.Fatalf("get: want 200, got %d", rr2.Code)
	}
	var got TraceLink
	json.NewDecoder(rr2.Body).Decode(&got) //nolint:errcheck
	if got.ID != created.ID {
		t.Errorf("want id=%s, got %s", created.ID, got.ID)
	}
}

func TestGetRequirement(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"title":"Auth requirement","description":"shall auth","status":"draft"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Requirement
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodGet, "/api/v1/requirements/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusOK {
		t.Fatalf("get: want 200, got %d", rr2.Code)
	}
	var got Requirement
	json.NewDecoder(rr2.Body).Decode(&got) //nolint:errcheck
	if got.Title != "Auth requirement" {
		t.Errorf("want title='Auth requirement', got %q", got.Title)
	}
}

func TestGetArtifact(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"name":"auth-svc","kind":"implementation","version":"1.0.0"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Artifact
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodGet, "/api/v1/artifacts/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusOK {
		t.Fatalf("get: want 200, got %d", rr2.Code)
	}
	var got Artifact
	json.NewDecoder(rr2.Body).Decode(&got) //nolint:errcheck
	if got.Name != "auth-svc" {
		t.Errorf("want name='auth-svc', got %q", got.Name)
	}
}

// TestDeleteRequirement tests successful deletion of a requirement.
func TestDeleteRequirement(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"title":"Auth requirement","description":"shall auth","status":"draft"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Requirement
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodDelete, "/api/v1/requirements/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusNoContent {
		t.Fatalf("delete: want 204, got %d", rr2.Code)
	}
}

// TestDeleteRequirementNotFound tests deletion of non-existent requirement.
func TestDeleteRequirementNotFound(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/requirements/does-not-exist", nil)
	testRouter().ServeHTTP(rr, req)
	if rr.Code != http.StatusNotFound {
		t.Fatalf("want 404, got %d", rr.Code)
	}
}

// TestDeleteArtifact tests successful deletion of an artifact.
func TestDeleteArtifact(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"name":"auth-svc","kind":"implementation","version":"1.0.0"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Artifact
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodDelete, "/api/v1/artifacts/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusNoContent {
		t.Fatalf("delete: want 204, got %d", rr2.Code)
	}
}

// TestDeleteArtifactNotFound tests deletion of non-existent artifact.
func TestDeleteArtifactNotFound(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodDelete, "/api/v1/artifacts/does-not-exist", nil)
	testRouter().ServeHTTP(rr, req)
	if rr.Code != http.StatusNotFound {
		t.Fatalf("want 404, got %d", rr.Code)
	}
}

// TestCreateTraceLinkBadJSON tests error handling for malformed JSON.
func TestCreateTraceLinkBadJSON(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString("invalid json"))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusBadRequest {
		t.Fatalf("want 400, got %d", rr.Code)
	}
	var errResp map[string]string
	json.NewDecoder(rr.Body).Decode(&errResp) //nolint:errcheck
	if errResp["error"] != "invalid JSON body" {
		t.Errorf("want error='invalid JSON body', got %q", errResp["error"])
	}
}

// TestCreateRequirementBadJSON tests error handling for malformed JSON.
func TestCreateRequirementBadJSON(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString("invalid json"))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusBadRequest {
		t.Fatalf("want 400, got %d", rr.Code)
	}
}

// TestCreateArtifactBadJSON tests error handling for malformed JSON.
func TestCreateArtifactBadJSON(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString("invalid json"))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusBadRequest {
		t.Fatalf("want 400, got %d", rr.Code)
	}
}

// TestGetTraceLinkNotFound tests retrieval of non-existent trace link.
func TestGetTraceLinkNotFound(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/trace-links/does-not-exist", nil)
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusNotFound {
		t.Fatalf("want 404, got %d", rr.Code)
	}
}

// TestGetRequirementNotFound tests retrieval of non-existent requirement.
func TestGetRequirementNotFound(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/requirements/does-not-exist", nil)
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusNotFound {
		t.Fatalf("want 404, got %d", rr.Code)
	}
}

// TestGetArtifactNotFound tests retrieval of non-existent artifact.
func TestGetArtifactNotFound(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/artifacts/does-not-exist", nil)
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusNotFound {
		t.Fatalf("want 404, got %d", rr.Code)
	}
}

// TestListArtifacts tests listing all artifacts.
func TestListArtifacts(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/artifacts", nil)
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rr.Code)
	}
	var artifacts []Artifact
	if err := json.NewDecoder(rr.Body).Decode(&artifacts); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if len(artifacts) < 2 {
		t.Errorf("want >= 2 seed artifacts, got %d", len(artifacts))
	}
}

// TestGetTraceLinkByIDResponseStructure verifies response body contains expected fields.
func TestGetTraceLinkByIDResponseStructure(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"source_id":"req-seed","target_id":"impl-seed","link_type":"integrates","confidence":0.75}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created TraceLink
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodGet, "/api/v1/trace-links/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusOK {
		t.Fatalf("get: want 200, got %d", rr2.Code)
	}

	var got TraceLink
	json.NewDecoder(rr2.Body).Decode(&got) //nolint:errcheck
	if got.ID == "" {
		t.Error("want non-empty ID")
	}
	if got.SourceID != "req-seed" {
		t.Errorf("want source_id=req-seed, got %s", got.SourceID)
	}
	if got.TargetID != "impl-seed" {
		t.Errorf("want target_id=impl-seed, got %s", got.TargetID)
	}
	if got.LinkType != "integrates" {
		t.Errorf("want link_type=integrates, got %s", got.LinkType)
	}
	if got.Confidence != 0.75 {
		t.Errorf("want confidence=0.75, got %f", got.Confidence)
	}
	if got.CreatedAt == "" {
		t.Error("want non-empty created_at")
	}
}

// TestGetRequirementByIDResponseStructure verifies response body contains expected fields.
func TestGetRequirementByIDResponseStructure(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"title":"Logging requirement","description":"System shall log all operations","status":"approved"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Requirement
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodGet, "/api/v1/requirements/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusOK {
		t.Fatalf("get: want 200, got %d", rr2.Code)
	}

	var got Requirement
	json.NewDecoder(rr2.Body).Decode(&got) //nolint:errcheck
	if got.ID == "" {
		t.Error("want non-empty ID")
	}
	if got.Title != "Logging requirement" {
		t.Errorf("want title='Logging requirement', got %q", got.Title)
	}
	if got.Description != "System shall log all operations" {
		t.Errorf("want description='System shall log all operations', got %q", got.Description)
	}
	if got.Status != "approved" {
		t.Errorf("want status=approved, got %s", got.Status)
	}
}

// TestGetArtifactByIDResponseStructure verifies response body contains expected fields.
func TestGetArtifactByIDResponseStructure(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"name":"database-module","kind":"test","version":"2.5.1"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Artifact
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodGet, "/api/v1/artifacts/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusOK {
		t.Fatalf("get: want 200, got %d", rr2.Code)
	}

	var got Artifact
	json.NewDecoder(rr2.Body).Decode(&got) //nolint:errcheck
	if got.ID == "" {
		t.Error("want non-empty ID")
	}
	if got.Name != "database-module" {
		t.Errorf("want name='database-module', got %q", got.Name)
	}
	if got.Kind != "test" {
		t.Errorf("want kind=test, got %s", got.Kind)
	}
	if got.Version != "2.5.1" {
		t.Errorf("want version=2.5.1, got %s", got.Version)
	}
}

// TestDeleteTraceLinkWithStatusCode verifies delete response status only (no body).
func TestDeleteTraceLinkWithStatusCode(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"source_id":"src1","target_id":"tgt1","link_type":"depends","confidence":0.5}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created TraceLink
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodDelete, "/api/v1/trace-links/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusNoContent {
		t.Errorf("want 204 NoContent, got %d", rr2.Code)
	}
	if rr2.Body.Len() > 0 {
		t.Errorf("want empty body, got %s", rr2.Body.String())
	}
}

// TestDeleteRequirementWithStatusCode verifies delete response status only (no body).
func TestDeleteRequirementWithStatusCode(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"title":"Performance req","description":"Response time <100ms","status":"approved"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Requirement
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodDelete, "/api/v1/requirements/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusNoContent {
		t.Errorf("want 204 NoContent, got %d", rr2.Code)
	}
	if rr2.Body.Len() > 0 {
		t.Errorf("want empty body, got %s", rr2.Body.String())
	}
}

// TestDeleteArtifactWithStatusCode verifies delete response status only (no body).
func TestDeleteArtifactWithStatusCode(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"name":"config-artifact","kind":"specification","version":"3.0.0"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)
	var created Artifact
	json.NewDecoder(rr.Body).Decode(&created) //nolint:errcheck

	rr2 := httptest.NewRecorder()
	req2 := httptest.NewRequest(http.MethodDelete, "/api/v1/artifacts/"+created.ID, nil)
	testRouter().ServeHTTP(rr2, req2)
	if rr2.Code != http.StatusNoContent {
		t.Errorf("want 204 NoContent, got %d", rr2.Code)
	}
	if rr2.Body.Len() > 0 {
		t.Errorf("want empty body, got %s", rr2.Body.String())
	}
}

// TestCreateTraceLinkResponseStatus verifies create returns 201 Created.
func TestCreateTraceLinkResponseStatus(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"source_id":"id1","target_id":"id2","link_type":"verifies","confidence":0.99}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/trace-links", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusCreated {
		t.Errorf("want 201 Created, got %d", rr.Code)
	}

	var created TraceLink
	err := json.NewDecoder(rr.Body).Decode(&created)
	if err != nil {
		t.Fatalf("decode error: %v", err)
	}
	if created.ID == "" || created.SourceID == "" || created.TargetID == "" {
		t.Error("created object missing required fields")
	}
}

// TestCreateRequirementResponseStatus verifies create returns 201 Created.
func TestCreateRequirementResponseStatus(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"title":"Security req","description":"HTTPS enforcement","status":"draft"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/requirements", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusCreated {
		t.Errorf("want 201 Created, got %d", rr.Code)
	}

	var created Requirement
	err := json.NewDecoder(rr.Body).Decode(&created)
	if err != nil {
		t.Fatalf("decode error: %v", err)
	}
	if created.ID == "" || created.Title == "" {
		t.Error("created object missing required fields")
	}
}

// TestCreateArtifactResponseStatus verifies create returns 201 Created.
func TestCreateArtifactResponseStatus(t *testing.T) {
	cleanup := setupTestDB(t)
	defer cleanup()

	body := `{"name":"release-artifact","kind":"deployment","version":"1.2.3"}`
	rr := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/api/v1/artifacts", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	testRouter().ServeHTTP(rr, req)

	if rr.Code != http.StatusCreated {
		t.Errorf("want 201 Created, got %d", rr.Code)
	}

	var created Artifact
	err := json.NewDecoder(rr.Body).Decode(&created)
	if err != nil {
		t.Fatalf("decode error: %v", err)
	}
	if created.ID == "" || created.Name == "" {
		t.Error("created object missing required fields")
	}
}
