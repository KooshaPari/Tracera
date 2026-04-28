//go:build e2e

package e2e

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// E2EContext holds the test environment context
type E2EContext struct {
	ServerURL      string
	PostgresURL    string
	RedisURL       string
	MeilisearchURL string
	Cleanup        func()
	ctx            context.Context
	containers     []testcontainers.Container
}

// setupE2ETest initializes the complete E2E test environment
func setupE2ETest(t *testing.T) *E2EContext {
	ctx := context.Background()

	// Start PostgreSQL container
	postgresContainer, postgresURL := startPostgresContainer(t, ctx)

	// Start Dragonfly container
	dragonflyContainer, redisURL := startDragonflyContainer(t, ctx)

	// Start Meilisearch container
	meilisearchContainer, meilisearchURL := startMeilisearchContainer(t, ctx)

	// Set environment variables for the application
	_ = os.Setenv("DATABASE_URL", postgresURL)
	_ = os.Setenv("REDIS_URL", redisURL)
	_ = os.Setenv("MEILISEARCH_URL", meilisearchURL)
	_ = os.Setenv("JWT_SECRET", "test-secret-key-for-e2e-tests")
	_ = os.Setenv("ENV", "test")

	// Start the application server
	server := startApplicationServer(t)

	e2eCtx := &E2EContext{
		ServerURL:      server.URL,
		PostgresURL:    postgresURL,
		RedisURL:       redisURL,
		MeilisearchURL: meilisearchURL,
		ctx:            ctx,
		containers: []testcontainers.Container{
			postgresContainer,
			dragonflyContainer,
			meilisearchContainer,
		},
		Cleanup: func() {
			server.Close()
			for _, container := range []testcontainers.Container{
				postgresContainer,
				dragonflyContainer,
				meilisearchContainer,
			} {
				if err := container.Terminate(ctx); err != nil {
					t.Logf("Failed to terminate container: %v", err)
				}
			}
		},
	}

	// Wait for services to be ready
	waitForServices(t, e2eCtx)

	return e2eCtx
}

// startPostgresContainer starts a PostgreSQL container for testing
func startPostgresContainer(t *testing.T, ctx context.Context) (testcontainers.Container, string) {
	req := testcontainers.ContainerRequest{
		Image:        "postgres:16-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     "test",
			"POSTGRES_PASSWORD": "test",
			"POSTGRES_DB":       "trace_test",
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithStartupTimeout(60 * time.Second).
			WithOccurrence(2),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		t.Fatalf("Failed to start PostgreSQL container: %v", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		t.Fatalf("Failed to get container host: %v", err)
	}

	port, err := container.MappedPort(ctx, "5432")
	if err != nil {
		t.Fatalf("Failed to get container port: %v", err)
	}

	connStr := fmt.Sprintf("postgresql://test:test@%s:%s/trace_test?sslmode=disable", host, port.Port())
	return container, connStr
}

// startDragonflyContainer starts a Dragonfly Redis-compatible container for testing
func startDragonflyContainer(t *testing.T, ctx context.Context) (testcontainers.Container, string) {
	req := testcontainers.ContainerRequest{
		Image:        "docker.dragonflydb.io/dragonflydb/dragonfly:latest",
		ExposedPorts: []string{"6379/tcp"},
		WaitingFor:   wait.ForListeningPort("6379/tcp").WithStartupTimeout(30 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		t.Fatalf("Failed to start Dragonfly container: %v", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		t.Fatalf("Failed to get container host: %v", err)
	}

	port, err := container.MappedPort(ctx, "6379")
	if err != nil {
		t.Fatalf("Failed to get container port: %v", err)
	}

	connStr := fmt.Sprintf("redis://%s:%s", host, port.Port())
	return container, connStr
}

// startMeilisearchContainer starts a Meilisearch container for testing
func startMeilisearchContainer(t *testing.T, ctx context.Context) (testcontainers.Container, string) {
	req := testcontainers.ContainerRequest{
		Image:        "getmeili/meilisearch:v1.5",
		ExposedPorts: []string{"7700/tcp"},
		Env: map[string]string{
			"MEILI_MASTER_KEY": "test-master-key",
			"MEILI_ENV":        "development",
		},
		WaitingFor: wait.ForHTTP("/health").
			WithPort("7700/tcp").
			WithStartupTimeout(30 * time.Second),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		t.Fatalf("Failed to start Meilisearch container: %v", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		t.Fatalf("Failed to get container host: %v", err)
	}

	port, err := container.MappedPort(ctx, "7700")
	if err != nil {
		t.Fatalf("Failed to get container port: %v", err)
	}

	connStr := fmt.Sprintf("http://%s:%s", host, port.Port())
	return container, connStr
}

// startApplicationServer starts the HTTP server for testing
func startApplicationServer(t *testing.T) *httptest.Server {
	// This would typically initialize your actual application
	// For now, we'll create a test server that you'll replace with your real app
	//
	// Example:
	// app := application.New()
	// handler := app.Router()
	// server := httptest.NewServer(handler)

	// Placeholder - replace with actual application initialization
	handler := createTestHandler()
	server := httptest.NewServer(handler)

	slog.Info("Test server started at", "url", server.URL)
	return server
}

// createTestHandler creates a basic test handler
// Replace this with your actual application handler
func createTestHandler() http.Handler {
	// This is a placeholder that should be replaced with your actual application router
	// Example:
	// return routes.SetupRouter()

	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})

	// Add more routes as needed
	// This is where you'd integrate your actual application routes

	return mux
}

// waitForServices waits for all services to be ready with exponential backoff.
func waitForServices(t *testing.T, ctx *E2EContext) {
	const maxRetries = 30
	initialDelay := 500 * time.Millisecond
	maxDelay := 5 * time.Second
	delay := initialDelay

	for i := 0; i < maxRetries; i++ {
		resp, err := http.Get(ctx.ServerURL + "/health")
		if err == nil && resp != nil && resp.StatusCode == http.StatusOK {
			_ = resp.Body.Close()
			break
		}
		if resp != nil {
			_ = resp.Body.Close()
		}
		if err != nil {
			t.Logf("Waiting for server (attempt %d/%d): %v", i+1, maxRetries, err)
		}
		if i < maxRetries-1 {
			time.Sleep(delay)
			if delay < maxDelay {
				delay += 250 * time.Millisecond
			}
		}
	}

	// Additional wait for database migrations, indexing, etc.
	time.Sleep(2 * time.Second)
}

// resetDatabase clears all data from the database for test isolation
func resetDatabase(t *testing.T, ctx *E2EContext) {
	// Implement database reset logic
	// This would typically truncate all tables or run migrations
	t.Log("Database reset (placeholder)")
}
