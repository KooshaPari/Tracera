package testutil

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"

	"github.com/labstack/echo/v4"
)

// MockSupabaseServer creates a mock Supabase API server for testing.
// Returns an httptest.Server that can be used to mock authentication responses.
//
// Example:
//
//	server := MockSupabaseServer()
//	defer server.Close()
//	// Use server.URL as the Supabase URL in tests
func MockSupabaseServer() *httptest.Server {
	mux := http.NewServeMux()

	// Mock JWT verification endpoint
	mux.HandleFunc("/auth/v1/user", func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
			w.WriteHeader(http.StatusUnauthorized)
			json.NewEncoder(w).Encode(map[string]string{"error": "invalid token"})
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"id":    "test-user-id",
			"email": "test@example.com",
			"user_metadata": map[string]string{
				"name": "Test User",
			},
		})
	})

	// Mock token refresh endpoint
	mux.HandleFunc("/auth/v1/token", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"access_token":  "mock-access-token",
			"refresh_token": "mock-refresh-token",
			"expires_in":    3600,
			"token_type":    "bearer",
		})
	})

	return httptest.NewServer(mux)
}

// MockVoyageAIServer creates a mock VoyageAI embeddings API server for testing.
// Returns an httptest.Server that can be used to mock embedding generation.
//
// Example:
//
//	server := MockVoyageAIServer()
//	defer server.Close()
//	// Use server.URL as the VoyageAI endpoint in tests
func MockVoyageAIServer() *httptest.Server {
	mux := http.NewServeMux()

	// Mock embeddings endpoint
	mux.HandleFunc("/v1/embeddings", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		var req struct {
			Input []string `json:"input"`
			Model string   `json:"model"`
		}

		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]string{"error": "invalid request"})
			return
		}

		// Generate mock embeddings (1024 dimensions for voyage-2)
		embeddings := make([]map[string]interface{}, len(req.Input))
		for i := range req.Input {
			// Create a simple mock embedding vector
			vector := make([]float32, 1024)
			for j := range vector {
				vector[j] = 0.1 * float32(i+j)
			}
			embeddings[i] = map[string]interface{}{
				"object":    "embedding",
				"embedding": vector,
				"index":     i,
			}
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"object": "list",
			"data":   embeddings,
			"model":  req.Model,
			"usage": map[string]int{
				"total_tokens": len(req.Input) * 10,
			},
		})
	})

	return httptest.NewServer(mux)
}

// MockWorkflowServer creates a mock workflow server for testing.
// Returns an httptest.Server that can be used to mock workflow operations.
//
// Example:
//
//	server := MockWorkflowServer()
//	defer server.Close()
//	// Use server.URL as the workflow endpoint in tests
func MockWorkflowServer() *httptest.Server {
	mux := http.NewServeMux()

	// Mock workflow registration endpoint
	mux.HandleFunc("/api/v1/workflows", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id":   "workflow-123",
				"name": "test-workflow",
			})
			return
		}

		w.WriteHeader(http.StatusMethodNotAllowed)
	})

	// Mock workflow trigger endpoint
	mux.HandleFunc("/api/v1/workflows/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost && strings.HasSuffix(r.URL.Path, "/trigger") {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"run_id": "run-456",
				"status": "running",
			})
			return
		}

		if r.Method == http.MethodGet {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id":     "workflow-123",
				"name":   "test-workflow",
				"status": "active",
			})
			return
		}

		w.WriteHeader(http.StatusMethodNotAllowed)
	})

	// Mock workflow run status endpoint
	mux.HandleFunc("/api/v1/runs/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"run_id": "run-456",
				"status": "completed",
				"result": map[string]string{
					"message": "workflow completed successfully",
				},
			})
			return
		}

		w.WriteHeader(http.StatusMethodNotAllowed)
	})

	return httptest.NewServer(mux)
}

// MockNATSServer creates a simple mock NATS server for testing.
// Note: This is a basic HTTP mock. For full NATS testing, use NATSContainer instead.
//
// Example:
//
//	server := MockNATSServer()
//	defer server.Close()
func MockNATSServer() *httptest.Server {
	mux := http.NewServeMux()

	// Mock monitoring endpoint
	mux.HandleFunc("/varz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"server_id":     "mock-nats",
			"version":       "2.0.0",
			"connections":   0,
			"subscriptions": 0,
		})
	})

	// Mock health check
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		fmt.Fprint(w, "OK")
	})

	return httptest.NewServer(mux)
}

// MockBinder is a mock implementation of handlers.RequestBinder for testing
type MockBinder struct{}

// Bind mocks the request binding functionality
func (m *MockBinder) Bind(c echo.Context, i interface{}) error {
	// In tests, we'll handle binding manually or use echo's default binder
	// This is just a stub to satisfy the interface
	return nil
}

// CreateProject mocks project creation
func (m *MockBinder) CreateProject(c echo.Context, req interface{}) error {
	return nil
}
