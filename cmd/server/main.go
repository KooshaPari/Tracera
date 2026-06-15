// Package main provides the entrypoint for the Tracera Go HTTP service.
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

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

	// API v1 group — ready for future route registration.
	r.Route("/api/v1", func(r chi.Router) {
		// Future routes go here, e.g.:
		// r.Get("/items", listItemsHandler)
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
