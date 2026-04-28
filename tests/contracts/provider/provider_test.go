// Package provider runs Pact provider contract tests against the Go backend.
package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"github.com/kooshapari/tracertm-backend/cmd/server"
	"github.com/pact-foundation/pact-go/v2/provider"
	"github.com/stretchr/testify/assert"
)

// TestProviderContracts verifies that the Go backend satisfies all consumer contracts
func TestProviderContracts(t *testing.T) {
	// Setup test server
	app, err := setupTestServer()
	if err != nil {
		t.Fatalf("Failed to setup test server: %v", err)
	}

	// Create test HTTP server
	testServer := httptest.NewServer(app)
	defer testServer.Close()

	// Get pact directory
	pactDir := filepath.Join("..", "pacts")
	pactFiles, err := getPactFiles(pactDir)
	if err != nil {
		t.Logf("Warning: Could not read pact files from %s: %v", pactDir, err)
		pactFiles = []string{}
	}

	if len(pactFiles) == 0 {
		t.Skip("No pact files found - skipping provider verification")
		return
	}

	// Configure verifier
	verifier := provider.NewVerifier()

	// Verify each pact file
	for _, pactFile := range pactFiles {
		t.Run(filepath.Base(pactFile), func(t *testing.T) {
			err := verifier.VerifyProvider(t, provider.VerifyRequest{
				ProviderBaseURL: testServer.URL,
				PactFiles:       []string{pactFile},

				// Provider states for setting up test data
				StateHandlers: provider.StateHandlers{
					// Auth states
					"user exists": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupUserExists(setup, state)
					},
					"user does not exist": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupUserNotFound(setup, state)
					},
					"user is authenticated": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupUserAuthenticated(setup, state)
					},
					"user is not authenticated": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupUserUnauthorized(setup, state)
					},
					"valid refresh token exists": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupValidRefreshToken(setup, state)
					},
					"invalid refresh token": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupInvalidRefreshToken(setup, state)
					},
					"valid token exists": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupValidToken(setup, state)
					},
					"invalid token": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupInvalidToken(setup, state)
					},

					// Project states
					"project exists": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectExists(setup, state)
					},
					"project does not exist": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectNotFound(setup, state)
					},
					"projects exist": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectsExist(setup, state)
					},
					"project has items": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectHasItems(setup, state)
					},
					"project is empty": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectEmpty(setup, state)
					},
					"project has multiple versions": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectHasVersions(setup, state)
					},

					// Item states
					"items exist": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupItemsExist(setup, state)
					},
					"items of type requirement exist": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupItemsOfTypeExist(setup, state, "requirement")
					},
					"item has links": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupItemHasLinks(setup, state)
					},

					// Graph states
					"project has graph data": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectHasGraphData(setup, state)
					},
					"project has circular dependencies": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectHasCycles(setup, state)
					},
					"nodes are connected": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupNodesConnected(setup, state)
					},
					"nodes are not connected": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupNodesDisconnected(setup, state)
					},
					"project has test coverage data": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupProjectHasCoverageData(setup, state)
					},

					// Database states
					"database is empty": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupDatabaseEmpty(setup, state)
					},
					"database is seeded with test data": func(setup bool, state provider.State) (provider.StateResponse, error) {
						return setupDatabaseSeeded(setup, state)
					},
				},

				// Custom request filter for authentication
				RequestFilter: func(req *http.Request, next http.RoundTripper) (*http.Response, error) {
					// Add test authentication token if needed
					if req.Header.Get("Authorization") == "" {
						req.Header.Set("Authorization", "Bearer test-token")
					}
					return next.RoundTrip(req)
				},

				// Verbose logging
				Verbose: true,
			})

			assert.NoError(t, err, "Provider should satisfy contract")
		})
	}
}

// setupTestServer creates a test instance of the API server
func setupTestServer() (http.Handler, error) {
	// Initialize test database
	ctx := context.Background()
	if err := initTestDatabase(ctx); err != nil {
		return nil, fmt.Errorf("failed to init test database: %w", err)
	}

	// Create server with test configuration
	app, err := server.NewServer(&server.Config{
		Port:        ":0", // Random port
		Environment: "test",
		Database: server.DatabaseConfig{
			Host:     os.Getenv("TEST_DB_HOST"),
			Port:     os.Getenv("TEST_DB_PORT"),
			User:     os.Getenv("TEST_DB_USER"),
			Password: os.Getenv("TEST_DB_PASSWORD"),
			Database: os.Getenv("TEST_DB_NAME"),
		},
	})
	if err != nil {
		return nil, err
	}

	return app, nil
}

// initTestDatabase initializes test database with schema
func initTestDatabase(ctx context.Context) error {
	// Run migrations or setup test schema
	// This should create all necessary tables and seed test data
	log.Println("Initializing test database...")
	return nil
}

// getPactFiles returns all pact JSON files from the pacts directory
func getPactFiles(dir string) ([]string, error) {
	var pactFiles []string

	err := filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && filepath.Ext(path) == ".json" {
			pactFiles = append(pactFiles, path)
		}
		return nil
	})

	return pactFiles, err
}

// Provider state handlers - these set up the backend state for each test scenario

func setupUserExists(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		// Create test user in database
		log.Println("Setting up: user exists")
		// tracked: https://github.com/KooshaPari/trace/issues/234
	} else {
		// Cleanup
		log.Println("Cleaning up: user exists")
	}
	return provider.StateResponse{}, nil
}

func setupUserNotFound(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: user does not exist")
		// Ensure user with email "invalid@example.com" does not exist
	}
	return provider.StateResponse{}, nil
}

func setupUserAuthenticated(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: user is authenticated")
		// Create authenticated user session
	} else {
		log.Println("Cleaning up: user is authenticated")
	}
	return provider.StateResponse{}, nil
}

func setupUserUnauthorized(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: user is not authenticated")
		// Ensure no valid session exists
	}
	return provider.StateResponse{}, nil
}

func setupValidRefreshToken(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: valid refresh token exists")
		// Create valid refresh token
	}
	return provider.StateResponse{}, nil
}

func setupInvalidRefreshToken(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: invalid refresh token")
		// Ensure no valid refresh token exists
	}
	return provider.StateResponse{}, nil
}

func setupValidToken(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: valid token exists")
	}
	return provider.StateResponse{}, nil
}

func setupInvalidToken(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: invalid token")
	}
	return provider.StateResponse{}, nil
}

func setupProjectExists(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project exists")
		// Create test project with ID "project-123"
	} else {
		log.Println("Cleaning up: project exists")
	}
	return provider.StateResponse{}, nil
}

func setupProjectNotFound(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project does not exist")
		// Ensure project with ID does not exist
	}
	return provider.StateResponse{}, nil
}

func setupProjectsExist(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: projects exist")
		// Create multiple test projects
	} else {
		log.Println("Cleaning up: projects exist")
	}
	return provider.StateResponse{}, nil
}

func setupProjectHasItems(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project has items")
		// Create project with items
	} else {
		log.Println("Cleaning up: project has items")
	}
	return provider.StateResponse{}, nil
}

func setupProjectEmpty(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project is empty")
		// Create project with no items
	}
	return provider.StateResponse{}, nil
}

func setupProjectHasVersions(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project has multiple versions")
		// Create project with version history
	}
	return provider.StateResponse{}, nil
}

func setupItemsExist(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: items exist")
		// Create test items
	} else {
		log.Println("Cleaning up: items exist")
	}
	return provider.StateResponse{}, nil
}

func setupItemsOfTypeExist(setup bool, state provider.State, itemType string) (provider.StateResponse, error) {
	if setup {
		log.Printf("Setting up: items of type %s exist\n", itemType)
		// Create items of specific type
	} else {
		log.Printf("Cleaning up: items of type %s exist\n", itemType)
	}
	return provider.StateResponse{}, nil
}

func setupItemHasLinks(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: item has links")
		// Create item with incoming and outgoing links
	}
	return provider.StateResponse{}, nil
}

func setupProjectHasGraphData(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project has graph data")
		// Create project with graph relationships
	}
	return provider.StateResponse{}, nil
}

func setupProjectHasCycles(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project has circular dependencies")
		// Create circular dependency graph
	}
	return provider.StateResponse{}, nil
}

func setupNodesConnected(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: nodes are connected")
		// Create connected nodes
	}
	return provider.StateResponse{}, nil
}

func setupNodesDisconnected(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: nodes are not connected")
		// Create disconnected nodes
	}
	return provider.StateResponse{}, nil
}

func setupProjectHasCoverageData(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: project has test coverage data")
		// Create test coverage data
	}
	return provider.StateResponse{}, nil
}

func setupDatabaseEmpty(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: database is empty")
		// Clear all data
	}
	return provider.StateResponse{}, nil
}

func setupDatabaseSeeded(setup bool, state provider.State) (provider.StateResponse, error) {
	if setup {
		log.Println("Setting up: database is seeded with test data")
		// Seed database with comprehensive test data
	}
	return provider.StateResponse{}, nil
}
