// Package main provides the entrypoint for the Tracera Go HTTP service.
package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	_ "github.com/mattn/go-sqlite3"
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
	CreatedAt  string  `json:"created_at"`
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
// SQLite backing store
// ---------------------------------------------------------------------------

var db *sql.DB

func initDB() error {
	dbPath := os.Getenv("TRACERA_DB")
	if dbPath == "" {
		dbPath = "./tracera.db"
	}
	var err error
	db, err = sql.Open("sqlite3", dbPath)
	if err != nil {
		return err
	}
	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS trace_links (
		id         TEXT PRIMARY KEY,
		source_id  TEXT NOT NULL,
		target_id  TEXT NOT NULL,
		link_type  TEXT NOT NULL,
		confidence REAL NOT NULL DEFAULT 1.0,
		created_at TEXT NOT NULL
	)`)
	if err != nil {
		return err
	}
	// Seed stub rows only when the table is empty.
	var count int
	if err = db.QueryRow("SELECT COUNT(*) FROM trace_links").Scan(&count); err != nil {
		return err
	}
	if count == 0 {
		seeds := []TraceLink{
			{ID: "tl-1", SourceID: "req-1", TargetID: "impl-1", LinkType: "satisfies", Confidence: 0.95, CreatedAt: time.Now().UTC().Format(time.RFC3339)},
			{ID: "tl-2", SourceID: "impl-1", TargetID: "test-1", LinkType: "verifies", Confidence: 0.88, CreatedAt: time.Now().UTC().Format(time.RFC3339)},
		}
		for _, s := range seeds {
			db.Exec("INSERT INTO trace_links VALUES (?,?,?,?,?,?)", s.ID, s.SourceID, s.TargetID, s.LinkType, s.Confidence, s.CreatedAt) //nolint:errcheck
		}
	}
	return nil
}

// ---------------------------------------------------------------------------
// In-memory stub stores for requirements and artifacts (read-only seed data)
// ---------------------------------------------------------------------------

var (
	reqs      []Requirement
	artifacts []Artifact
)

func init() {
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
	json.NewEncoder(w).Encode(v) //nolint:errcheck
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
	rows, err := db.Query("SELECT id, source_id, target_id, link_type, confidence, created_at FROM trace_links ORDER BY created_at")
	if err != nil {
		jsonResponse(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}
	defer rows.Close()

	var links []TraceLink
	for rows.Next() {
		var l TraceLink
		if err := rows.Scan(&l.ID, &l.SourceID, &l.TargetID, &l.LinkType, &l.Confidence, &l.CreatedAt); err != nil {
			jsonResponse(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
			return
		}
		links = append(links, l)
	}
	if links == nil {
		links = []TraceLink{}
	}
	jsonResponse(w, http.StatusOK, links)
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
		CreatedAt:  time.Now().UTC().Format(time.RFC3339),
	}

	_, err := db.Exec(
		"INSERT INTO trace_links VALUES (?,?,?,?,?,?)",
		link.ID, link.SourceID, link.TargetID, link.LinkType, link.Confidence, link.CreatedAt,
	)
	if err != nil {
		jsonResponse(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	jsonResponse(w, http.StatusCreated, link)
}

// ---------------------------------------------------------------------------
// Handlers — Requirements
// ---------------------------------------------------------------------------

func listRequirements(w http.ResponseWriter, _ *http.Request) {
	jsonResponse(w, http.StatusOK, reqs)
}

// ---------------------------------------------------------------------------
// Handlers — Artifacts
// ---------------------------------------------------------------------------

func listArtifacts(w http.ResponseWriter, _ *http.Request) {
	jsonResponse(w, http.StatusOK, artifacts)
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

func main() {
	if err := initDB(); err != nil {
		log.Fatalf("initDB: %v", err)
	}
	defer db.Close()

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
	json.NewEncoder(w).Encode(map[string]string{ //nolint:errcheck
		"status":  "ok",
		"service": "tracera-go",
	})
}
