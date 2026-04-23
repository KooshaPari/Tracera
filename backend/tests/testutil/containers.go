package testutil

import (
	"context"
	"fmt"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

// PostgresContainer starts a PostgreSQL container for testing.
// Returns the container instance and connection string.
// The container will be automatically cleaned up when the context is cancelled.
//
// Example:
//
//	ctx := context.Background()
//	container, connString, err := PostgresContainer(ctx)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	defer container.Terminate(ctx)
func PostgresContainer(ctx context.Context) (testcontainers.Container, string, error) {
	req := testcontainers.ContainerRequest{
		Image:        "postgres:16-alpine",
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     "testuser",
			"POSTGRES_PASSWORD": "testpass",
			"POSTGRES_DB":       "testdb",
		},
		WaitingFor: wait.ForAll(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(60*time.Second),
			wait.ForListeningPort("5432/tcp"),
		),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		return nil, "", fmt.Errorf("failed to start postgres container: %w", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get container host: %w", err)
	}

	mappedPort, err := container.MappedPort(ctx, "5432")
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get mapped port: %w", err)
	}

	connString := fmt.Sprintf("postgres://testuser:testpass@%s:%s/testdb?sslmode=disable", host, mappedPort.Port())
	return container, connString, nil
}

// DragonflyContainer starts a Dragonfly Redis-compatible container for testing.
// Returns the container instance and connection address.
// The container will be automatically cleaned up when the context is cancelled.
//
// Example:
//
//	ctx := context.Background()
//	container, addr, err := DragonflyContainer(ctx)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	defer container.Terminate(ctx)
func DragonflyContainer(ctx context.Context) (testcontainers.Container, string, error) {
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
		return nil, "", fmt.Errorf("failed to start dragonfly container: %w", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get container host: %w", err)
	}

	mappedPort, err := container.MappedPort(ctx, "6379")
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get mapped port: %w", err)
	}

	addr := fmt.Sprintf("%s:%s", host, mappedPort.Port())
	return container, addr, nil
}

// Neo4jContainer starts a Neo4j container for testing.
// Returns the container instance and bolt connection URL.
// The container will be automatically cleaned up when the context is cancelled.
//
// Example:
//
//	ctx := context.Background()
//	container, boltURL, err := Neo4jContainer(ctx)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	defer container.Terminate(ctx)
func Neo4jContainer(ctx context.Context) (testcontainers.Container, string, error) {
	req := testcontainers.ContainerRequest{
		Image:        "neo4j:5-community",
		ExposedPorts: []string{"7687/tcp", "7474/tcp"},
		Env: map[string]string{
			"NEO4J_AUTH":                                  "neo4j/testpassword",
			"NEO4J_ACCEPT_LICENSE_AGREEMENT":              "yes",
			"NEO4J_dbms_security_procedures_unrestricted": "apoc.*",
			"NEO4J_dbms_memory_heap_max__size":            "512M",
		},
		WaitingFor: wait.ForAll(
			wait.ForLog("Started.").
				WithStartupTimeout(120*time.Second),
			wait.ForHTTP("/").
				WithPort("7474/tcp").
				WithStartupTimeout(120*time.Second),
		),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		return nil, "", fmt.Errorf("failed to start neo4j container: %w", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get container host: %w", err)
	}

	mappedPort, err := container.MappedPort(ctx, "7687")
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get mapped port: %w", err)
	}

	boltURL := fmt.Sprintf("bolt://neo4j:testpassword@%s:%s", host, mappedPort.Port())
	return container, boltURL, nil
}

// NATSContainer starts a NATS server container for testing.
// Returns the container instance and connection URL.
// The container will be automatically cleaned up when the context is cancelled.
//
// Example:
//
//	ctx := context.Background()
//	container, natsURL, err := NATSContainer(ctx)
//	if err != nil {
//	    log.Fatal(err)
//	}
//	defer container.Terminate(ctx)
func NATSContainer(ctx context.Context) (testcontainers.Container, string, error) {
	req := testcontainers.ContainerRequest{
		Image:        "nats:2-alpine",
		ExposedPorts: []string{"4222/tcp", "8222/tcp"},
		Cmd:          []string{"-m", "8222"},
		WaitingFor: wait.ForAll(
			wait.ForLog("Server is ready").
				WithStartupTimeout(30*time.Second),
			wait.ForListeningPort("4222/tcp"),
		),
	}

	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		return nil, "", fmt.Errorf("failed to start nats container: %w", err)
	}

	host, err := container.Host(ctx)
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get container host: %w", err)
	}

	mappedPort, err := container.MappedPort(ctx, "4222")
	if err != nil {
		container.Terminate(ctx)
		return nil, "", fmt.Errorf("failed to get mapped port: %w", err)
	}

	natsURL := fmt.Sprintf("nats://%s:%s", host, mappedPort.Port())
	return container, natsURL, nil
}
