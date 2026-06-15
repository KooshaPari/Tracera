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
		r.Delete("/trace-links/{id}", deleteTraceLink)
		r.Get("/requirements", listRequirements)
		r.Post("/requirements", createRequirement)
		r.Delete("/requirements/{id}", deleteRequirement)
		r.Get("/artifacts", listArtifacts)
		r.Post("/artifacts", createArtifact)
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
