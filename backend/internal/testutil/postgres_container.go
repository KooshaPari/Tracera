//go:build integration

package testutil

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

const (
	postgresContainerDefaultTimeout = 60 * time.Second
	postgresContainerTestTimeout    = 30 * time.Second
	postgresContainerMaxConns       = 10
)

// PostgresContainer manages the lifecycle of a PostgreSQL testcontainer
type PostgresContainer struct {
	container testcontainers.Container
	pool      *pgxpool.Pool
	sqlDB     *sql.DB
	dbURL     string
}

// PostgresContainerConfig holds configuration for PostgreSQL container setup
type PostgresContainerConfig struct {
	Image   string
	DBName  string
	DBUser  string
	DBPass  string
	Timeout time.Duration
}

// DefaultPostgresContainerConfig returns sensible defaults
func DefaultPostgresContainerConfig() PostgresContainerConfig {
	return PostgresContainerConfig{
		Image:   "postgres:17-alpine",
		DBName:  "tracertm_test",
		DBUser:  "postgres",
		DBPass:  "postgres",
		Timeout: postgresContainerDefaultTimeout,
	}
}

// StartPostgresContainer starts a new PostgreSQL container with testcontainers
func StartPostgresContainer(ctx context.Context) (*PostgresContainer, error) {
	config := DefaultPostgresContainerConfig()
	return StartPostgresContainerWithConfig(ctx, config)
}

// StartPostgresContainerWithConfig starts a PostgreSQL container with custom configuration
func StartPostgresContainerWithConfig(ctx context.Context, config PostgresContainerConfig) (*PostgresContainer, error) {
	// Build connection string constructor
	connStringFn := func(host string, port string) string {
		return fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable",
			config.DBUser, config.DBPass, host, port, config.DBName)
	}

	// Create PostgreSQL container request
	req := testcontainers.ContainerRequest{
		Image:        config.Image,
		ExposedPorts: []string{"5432/tcp"},
		Env: map[string]string{
			"POSTGRES_USER":     config.DBUser,
			"POSTGRES_PASSWORD": config.DBPass,
			"POSTGRES_DB":       config.DBName,
		},
		WaitingFor: wait.ForLog("database system is ready to accept connections").
			WithOccurrence(2).
			WithStartupTimeout(config.Timeout),
	}

	// Create container
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to start PostgreSQL container: %w", err)
	}

	// Get mapped port
	port, err := container.MappedPort(ctx, "5432/tcp")
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

	// Build connection string
	dbURL := connStringFn(host, port.Port())

	// Test connection
	testCtx, cancel := context.WithTimeout(ctx, postgresContainerTestTimeout)
	defer cancel()

	testPool, err := pgxpool.New(testCtx, dbURL)
	if err != nil {
		_ = container.Terminate(ctx)
		return nil, fmt.Errorf("failed to create connection pool: %w", err)
	}

	if err := testPool.Ping(testCtx); err != nil {
		testPool.Close()
		_ = container.Terminate(ctx)
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	testPool.Close()

	slog.Info("✅ PostgreSQL container started", "url", dbURL)

	pc := &PostgresContainer{
		container: container,
		dbURL:     dbURL,
	}

	return pc, nil
}

// GetPool returns a pgxpool.Pool connection
func (pc *PostgresContainer) GetPool(ctx context.Context) (*pgxpool.Pool, error) {
	if pc.pool != nil {
		return pc.pool, nil
	}

	config, err := pgxpool.ParseConfig(pc.dbURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse connection config: %w", err)
	}

	// Configure connection pool for testing
	config.MaxConns = postgresContainerMaxConns
	config.MinConns = 2

	pool, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create connection pool: %w", err)
	}

	// Test connection
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	pc.pool = pool
	slog.Info("✅ Connection pool created successfully")
	return pool, nil
}

// GetSQLDB returns a sql.DB connection for migrations
func (pc *PostgresContainer) GetSQLDB(ctx context.Context) (*sql.DB, error) {
	if pc.sqlDB != nil {
		return pc.sqlDB, nil
	}

	sqlDB, err := sql.Open("postgres", pc.dbURL)
	if err != nil {
		return nil, fmt.Errorf("failed to open SQL database: %w", err)
	}

	// Test connection
	if err := sqlDB.PingContext(ctx); err != nil {
		sqlDB.Close()
		return nil, fmt.Errorf("failed to ping SQL database: %w", err)
	}

	pc.sqlDB = sqlDB
	slog.Info("✅ SQL database connection created successfully")
	return sqlDB, nil
}

// GetConnectionString returns the database connection string
func (pc *PostgresContainer) GetConnectionString() string {
	return pc.dbURL
}

// RunMigrations runs migrations on the container using the provided migration function
func (pc *PostgresContainer) RunMigrations(ctx context.Context, migrationFn func(context.Context, *sql.DB) error) error {
	sqlDB, err := pc.GetSQLDB(ctx)
	if err != nil {
		return fmt.Errorf("failed to get SQL database: %w", err)
	}

	if err := migrationFn(ctx, sqlDB); err != nil {
		return fmt.Errorf("failed to run migrations: %w", err)
	}

	slog.Info("✅ Migrations completed successfully")
	return nil
}

// ExecuteSQL executes a SQL query directly on the container
func (pc *PostgresContainer) ExecuteSQL(ctx context.Context, query string) error {
	pool, err := pc.GetPool(ctx)
	if err != nil {
		return fmt.Errorf("failed to get pool: %w", err)
	}

	_, err = pool.Exec(ctx, query)
	return err
}

// Close closes all connections and terminates the container
func (pc *PostgresContainer) Close(ctx context.Context) error {
	// Close pgxpool connection
	if pc.pool != nil {
		pc.pool.Close()
		slog.Info("✅ Connection pool closed")
	}

	// Close sql.DB connection
	if pc.sqlDB != nil {
		if err := pc.sqlDB.Close(); err != nil {
			slog.Error("⚠️ Warning: Failed to close SQL database", "error", err)
		}
		slog.Info("✅ SQL database connection closed")
	}

	// Terminate container
	if pc.container != nil {
		if err := pc.container.Terminate(ctx); err != nil {
			return fmt.Errorf("failed to terminate container: %w", err)
		}
		slog.Info("✅ Container terminated")
	}

	return nil
}

// SetupAndRunTest is a convenience function that sets up a PostgreSQL container,
// runs migrations, executes a test function, and cleans up
func SetupAndRunTest(
	t *testing.T,
	migrationFn func(context.Context, *sql.DB) error,
	testFn func(*testing.T, *PostgresContainer),
) {
	ctx := context.Background()

	// Start container
	pc, err := StartPostgresContainer(ctx)
	if err != nil {
		t.Fatalf("Failed to start PostgreSQL container: %v", err)
	}
	defer func() {
		if err := pc.Close(ctx); err != nil {
			t.Errorf("Failed to close container: %v", err)
		}
	}()

	// Run migrations if provided
	if migrationFn != nil {
		if err := pc.RunMigrations(ctx, migrationFn); err != nil {
			t.Fatalf("Failed to run migrations: %v", err)
		}
	}

	// Run test
	testFn(t, pc)
}

// SetupTestDatabase is a simpler convenience function for basic setup
func SetupTestDatabase(ctx context.Context) (*PostgresContainer, error) {
	pc, err := StartPostgresContainer(ctx)
	if err != nil {
		return nil, err
	}

	// Verify pool is available
	if _, err := pc.GetPool(ctx); err != nil {
		_ = pc.Close(ctx)
		return nil, err
	}

	return pc, nil
}
