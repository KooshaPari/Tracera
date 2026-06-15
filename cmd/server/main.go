// Package main provides the entrypoint for the Tracera Go HTTP service.
package main

import (
	"encoding/json"
	"log"
	"math/rand"
	"net/http"
	"os"
	"sync"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

// TraceLink represents a single traceability relationship between two artifacts.
type TraceLink struct {
	ID         string  `json:"id"`
	SourceID   string  `json:"source_id"`
	TargetID   string  `json:"target_id"`
	LinkType   string  `json:"link_type"`
	Confidence float64 `json:"confidence"`
}

// Requirement is a stub type for SDLC requirements.
type Requirement struct {
	ID          string `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	Status      string `json:"status"`
}

// Artifact is a stub type for arbitrary SDLC artifacts.
type Artifact struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Kind    string `json:"kind"`
	Version string `json:"version"`
}

// TraceLinkInput is the JSON body accepted by POST /api/v1/trace-links.
type TraceLinkInput struct {
	SourceID   string  `json:"source_id"`
	TargetID   string  `json:"target_id"`
	LinkType   string  `json:"link_type"`
	Confidence float64 `json:"confidence"`
}

// ---------------------------------------------------------------------------
// In-memory backing store
// ---------------------------------------------------------------------------

var (
	mu         sync.Mutex
	traceLinks []TraceLink
	reqs       []Requirement
	artifacts  []Artifact
)

func init() {
	// Seed some stub data so GET endpoints have something to return.
	traceLinks = []TraceLink{
		{ID: "tl-1", SourceID: "req-1", TargetID: "impl-1", LinkType: "satisfies", Confidence: 0.95},
		{ID: "tl-2", SourceID: "impl-1", TargetID: "test-1", LinkType: "verifies", Confidence: 0.88},
	}
	reqs = []Requirement{
		{ID: "req-1", Title: "System shall be observable", Description: "Health and metrics endpoints", Status: "approved"},
		{ID: "req-2", Title: "System shall be traceable", Description: "Trace-link CRUD API", Status: "draft"},
	}
	artifacts = []Artifact{
		{ID: "impl-1", Name: "HTTP server", Kind: "implementation", Version: "0.1.0"},
		{ID: "test-1", Name: "Integration test suite", Kind: "test", Version: "0.1.0"},
	}
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

func jsonResponse(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

const idCharset = "abcdefghijklmnopqrstuvwxyz0123456789"

func nextID(prefix string) string {
	b := make([]byte, 8)
	for i := range b {
		b[i] = idCharset[rand.Intn(len(idCharset))]
	}
	return prefix + "-" + string(b)
}

// ---------------------------------------------------------------------------
// Handlers — Trace Links
// ---------------------------------------------------------------------------

func listTraceLinks(w http.ResponseWriter, _ *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	// Return a copy to avoid data races on the slice header.
	out := make([]TraceLink, len(traceLinks))
	copy(out, traceLinks)
	jsonResponse(w, http.StatusOK, out)
}

func createTraceLink(w http.ResponseWriter, r *http.Request) {
	var input TraceLinkInput
	if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
		jsonResponse(w, http.StatusBadRequest, map[string]string{"error": "invalid JSON body"})
		return
	}

	link := TraceLink{
		ID:         nextID("tl"),
		SourceID:   input.SourceID,
		TargetID:   input.TargetID,
		LinkType:   input.LinkType,
		Confidence: input.Confidence,
	}

	mu.Lock()
	traceLinks = append(traceLinks, link)
	mu.Unlock()

	jsonResponse(w, http.StatusCreated, link)
}

// ---------------------------------------------------------------------------
// Handlers — Requirements
// ---------------------------------------------------------------------------

func listRequirements(w http.ResponseWriter, _ *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	out := make([]Requirement, len(reqs))
	copy(out, reqs)
	jsonResponse(w, http.StatusOK, out)
}

// ---------------------------------------------------------------------------
// Handlers — Artifacts
// ---------------------------------------------------------------------------

func listArtifacts(w http.ResponseWriter, _ *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	out := make([]Artifact, len(artifacts))
	copy(out, artifacts)
	jsonResponse(w, http.StatusOK, out)
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	r := chi.NewRouter()

	// Standard middleware.
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	// Health / readiness.
	r.Get("/health", healthHandler)

	// API v1 group.
	r.Route("/api/v1", func(r chi.Router) {
		r.Get("/trace-links", listTraceLinks)
		r.Post("/trace-links", createTraceLink)
		r.Get("/requirements", listRequirements)
		r.Get("/artifacts", listArtifacts)
	})

	addr := ":" + port
	log.Printf("tracera-go listening on %s", addr)
	if err := http.ListenAndServe(addr, r); err != nil {
		log.Fatalf("server exited: %v", err)
	}
}

// healthHandler returns a lightweight liveness probe response.
func healthHandler(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "ok",
		"service": "tracera-go",
	})
}
