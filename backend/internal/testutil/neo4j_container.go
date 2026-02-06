//go:build integration

package testutil

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

const (
	neo4jContainerDefaultTimeout = 60 * time.Second
	neo4jContainerStartTimeout   = 2 * time.Minute
	neo4jContainerCleanupTimeout = 30 * time.Second
)

// Neo4jContainer wraps a testcontainers Neo4j instance
type Neo4jContainer struct {
	container testcontainers.Container
	host      string
	port      string
	user      string
	password  string
}

// Neo4jContainerConfig holds configuration for Neo4j container setup
type Neo4jContainerConfig struct {
	Image    string
	User     string
	Password string
	Database string
	Timeout  time.Duration
}

// DefaultNeo4jContainerConfig returns sensible defaults for Neo4j container
func DefaultNeo4jContainerConfig() Neo4jContainerConfig {
	return Neo4jContainerConfig{
		Image:    "neo4j:5.25-community",
		User:     "neo4j",
		Password: "testpass123",
		Database: "neo4j",
		Timeout:  neo4jContainerDefaultTimeout,
	}
}

// StartNeo4jContainer starts a Neo4j container for testing
// Returns the container wrapper, URI, and cleanup function
func StartNeo4jContainer(ctx context.Context, config Neo4jContainerConfig) (*Neo4jContainer, error) {
	req := testcontainers.ContainerRequest{
		Image:        config.Image,
		ExposedPorts: []string{"7687/tcp", "7474/tcp"},
		Env: map[string]string{
			"NEO4J_AUTH":                                  config.User + "/" + config.Password,
			"NEO4J_INITIAL_PASSWORD":                      config.Password,
			"NEO4J_apoc_import_file_enabled":              "true",
			"NEO4J_dbms_security_procedures_unrestricted": "apoc.*",
		},
		WaitingFor: wait.ForAll(
			wait.ForLog("Started."),
			wait.ForListeningPort("7687/tcp"),
		).WithStartupTimeout(config.Timeout),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to start Neo4j container: %w", err)
	}

	// Get mapped port
	port, err := container.MappedPort(ctx, "7687/tcp")
	if err != nil {
		_ = container.Terminate(ctx)
		return nil, fmt.Errorf("failed to get mapped port: %w", err)
	}

	// Get host
	host, err := container.Host(ctx)
	if err != nil {
		_ = container.Terminate(ctx)
		return nil, fmt.Errorf("failed to get container host: %w", err)
	}

	return &Neo4jContainer{
		container: container,
		host:      host,
		port:      port.Port(),
		user:      config.User,
		password:  config.Password,
	}, nil
}

// GetURI returns the connection URI for the Neo4j container
func (nc *Neo4jContainer) GetURI() string {
	return fmt.Sprintf("neo4j://%s:%s", nc.host, nc.port)
}

// GetBoltURI returns the Bolt protocol connection URI
func (nc *Neo4jContainer) GetBoltURI() string {
	return fmt.Sprintf("bolt://%s:%s", nc.host, nc.port)
}

// GetCredentials returns the username and password
func (nc *Neo4jContainer) GetCredentials() (string, string) {
	return nc.user, nc.password
}

// Cleanup terminates the container
func (nc *Neo4jContainer) Cleanup(ctx context.Context) error {
	if nc.container != nil {
		return nc.container.Terminate(ctx)
	}
	return nil
}

// NewNeo4jContainerForTest is a convenience function for test setup
// It automatically handles context and panics on error
func NewNeo4jContainerForTest(t *testing.T, config Neo4jContainerConfig) *Neo4jContainer {
	ctx, cancel := context.WithTimeout(context.Background(), neo4jContainerStartTimeout)
	defer cancel()

	nc, err := StartNeo4jContainer(ctx, config)
	if err != nil {
		t.Fatalf("failed to start Neo4j container: %v", err)
	}

	// Register cleanup with testing.T
	t.Cleanup(func() {
		ctx, cancel := context.WithTimeout(context.Background(), neo4jContainerCleanupTimeout)
		defer cancel()
		if err := nc.Cleanup(ctx); err != nil {
			t.Logf("failed to cleanup Neo4j container: %v", err)
		}
	})

	return nc
}

// WithNeo4jContainer is a helper for wrapping test functions with container setup/teardown
type WithNeo4jContainerFunc func(t *testing.T, nc *Neo4jContainer)

// RunWithNeo4jContainer executes a test function with an active Neo4j container
func RunWithNeo4jContainer(t *testing.T, config Neo4jContainerConfig, fn WithNeo4jContainerFunc) {
	nc := NewNeo4jContainerForTest(t, config)
	fn(t, nc)
}
