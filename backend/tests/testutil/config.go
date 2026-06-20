package testutil

import (
	"context"
	"errors"
	"fmt"
	"os"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"github.com/testcontainers/testcontainers-go"
)

// TestConfig holds configuration for test infrastructure
type TestConfig struct {
	PostgresURL string
	RedisURL    string
	Neo4jURL    string
	NATSURL     string
	SchemaPath  string
}

// DefaultTestConfig returns a default test configuration
func DefaultTestConfig() *TestConfig {
	return &TestConfig{
		PostgresURL: os.Getenv("TEST_DATABASE_URL"),
		RedisURL:    os.Getenv("TEST_REDIS_URL"),
		Neo4jURL:    os.Getenv("TEST_NEO4J_URI"),
		NATSURL:     os.Getenv("TEST_NATS_URL"),
		SchemaPath:  "../../schema.sql",
	}
}

// TestEnvironment manages all test infrastructure containers and connections
type TestEnvironment struct {
	PostgresContainer  testcontainers.Container
	DragonflyContainer testcontainers.Container
	Neo4jContainer     testcontainers.Container
	NATSContainer      testcontainers.Container

	PostgresPool *pgxpool.Pool
	NATSConn     *nats.Conn

	Config *TestConfig

	mu      sync.Mutex
	cleanup []func(context.Context) error
}

// NewTestEnvironment creates a new test environment with all required services
//
// Example:
//
//	ctx := context.Background()
//	env, err := testutil.NewTestEnvironment(ctx)
//	if err != nil {
//	    t.Fatal(err)
//	}
//	defer env.Cleanup(ctx)
func NewTestEnvironment(ctx context.Context) (*TestEnvironment, error) {
	env := &TestEnvironment{
		Config:  DefaultTestConfig(),
		cleanup: make([]func(context.Context) error, 0),
	}

	// Start PostgreSQL
	pgContainer, pgURL, err := PostgresContainer(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to start postgres: %w", err)
	}
	env.PostgresContainer = pgContainer
	env.Config.PostgresURL = pgURL
	env.addCleanup(func(ctx context.Context) error {
		return pgContainer.Terminate(ctx)
	})

	// Connect to PostgreSQL
	pool, err := pgxpool.New(ctx, pgURL)
	if err != nil {
		env.Cleanup(ctx)
		return nil, fmt.Errorf("failed to connect to postgres: %w", err)
	}
	env.PostgresPool = pool
	env.addCleanup(func(ctx context.Context) error {
		pool.Close()
		return nil
	})

	// Start Dragonfly
	dragonflyContainer, redisURL, err := DragonflyContainer(ctx)
	if err != nil {
		env.Cleanup(ctx)
		return nil, fmt.Errorf("failed to start dragonfly: %w", err)
	}
	env.DragonflyContainer = dragonflyContainer
	env.Config.RedisURL = redisURL
	env.addCleanup(func(ctx context.Context) error {
		return dragonflyContainer.Terminate(ctx)
	})

	// Start Neo4j
	neo4jContainer, neo4jURL, err := Neo4jContainer(ctx)
	if err != nil {
		env.Cleanup(ctx)
		return nil, fmt.Errorf("failed to start neo4j: %w", err)
	}
	env.Neo4jContainer = neo4jContainer
	env.Config.Neo4jURL = neo4jURL
	env.addCleanup(func(ctx context.Context) error {
		return neo4jContainer.Terminate(ctx)
	})

	// Start NATS
	natsContainer, natsURL, err := NATSContainer(ctx)
	if err != nil {
		env.Cleanup(ctx)
		return nil, fmt.Errorf("failed to start nats: %w", err)
	}
	env.NATSContainer = natsContainer
	env.Config.NATSURL = natsURL
	env.addCleanup(func(ctx context.Context) error {
		return natsContainer.Terminate(ctx)
	})

	// Connect to NATS
	natsConn, err := nats.Connect(natsURL)
	if err != nil {
		env.Cleanup(ctx)
		return nil, fmt.Errorf("failed to connect to nats: %w", err)
	}
	env.NATSConn = natsConn
	env.addCleanup(func(ctx context.Context) error {
		natsConn.Close()
		return nil
	})

	// Run migrations
	if env.Config.SchemaPath != "" {
		if err := ExecuteMigrations(ctx, pool, env.Config.SchemaPath); err != nil {
			env.Cleanup(ctx)
			return nil, fmt.Errorf("failed to run migrations: %w", err)
		}
	}

	return env, nil
}

// NewMinimalTestEnvironment creates a test environment with only PostgreSQL
// This is useful for tests that don't need the full infrastructure
//
// Example:
//
//	ctx := context.Background()
//	env, err := testutil.NewMinimalTestEnvironment(ctx)
//	if err != nil {
//	    t.Fatal(err)
//	}
//	defer env.Cleanup(ctx)
func NewMinimalTestEnvironment(ctx context.Context) (*TestEnvironment, error) {
	env := &TestEnvironment{
		Config:  DefaultTestConfig(),
		cleanup: make([]func(context.Context) error, 0),
	}

	// Start PostgreSQL
	pgContainer, pgURL, err := PostgresContainer(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to start postgres: %w", err)
	}
	env.PostgresContainer = pgContainer
	env.Config.PostgresURL = pgURL
	env.addCleanup(func(ctx context.Context) error {
		return pgContainer.Terminate(ctx)
	})

	// Connect to PostgreSQL
	pool, err := pgxpool.New(ctx, pgURL)
	if err != nil {
		env.Cleanup(ctx)
		return nil, fmt.Errorf("failed to connect to postgres: %w", err)
	}
	env.PostgresPool = pool
	env.addCleanup(func(ctx context.Context) error {
		pool.Close()
		return nil
	})

	// Run migrations
	if env.Config.SchemaPath != "" {
		if err := ExecuteMigrations(ctx, pool, env.Config.SchemaPath); err != nil {
			env.Cleanup(ctx)
			return nil, fmt.Errorf("failed to run migrations: %w", err)
		}
	}

	return env, nil
}

// addCleanup adds a cleanup function to be called when the environment is cleaned up
func (e *TestEnvironment) addCleanup(fn func(context.Context) error) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.cleanup = append(e.cleanup, fn)
}

// Cleanup cleans up all resources in the test environment
func (e *TestEnvironment) Cleanup(ctx context.Context) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	var lastErr error
	// Run cleanup functions in reverse order
	for i := len(e.cleanup) - 1; i >= 0; i-- {
		if err := e.cleanup[i](ctx); err != nil {
			lastErr = err
		}
	}

	return lastErr
}

// ResetDatabase truncates all tables and resets sequences
func (e *TestEnvironment) ResetDatabase(ctx context.Context) error {
	if e.PostgresPool == nil {
		return errors.New("postgres pool not initialized")
	}
	return TruncateAllTables(ctx, e.PostgresPool)
}
