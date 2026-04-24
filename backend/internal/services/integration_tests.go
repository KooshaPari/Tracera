//go:build integration

package services

import (
	"context"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const integrationTestTimeout = 30 * time.Second

// TestPostgresIntegration_BasicConnection tests basic PostgreSQL connectivity
func TestPostgresIntegration_BasicConnection(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Test basic connectivity
	var version string
	err := pc.Pool.QueryRow(ctx, "SELECT version()").Scan(&version)
	require.NoError(t, err)
	assert.NotEmpty(t, version)
	assert.Contains(t, version, "PostgreSQL")
}

// TestPostgresIntegration_DatabaseCreation tests that database is properly created
func TestPostgresIntegration_DatabaseCreation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Check database name
	var dbname string
	err := pc.Pool.QueryRow(ctx, "SELECT current_database()").Scan(&dbname)
	require.NoError(t, err)
	assert.Equal(t, "tracertm_test", dbname)
}

// TestPostgresIntegration_ConnectionString tests connection string is valid
func TestPostgresIntegration_ConnectionString(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Verify DSN is not empty
	assert.NotEmpty(t, pc.DSN)
	assert.Contains(t, pc.DSN, "tracertm_test")
	assert.Contains(t, pc.DSN, "tracertm")
}

// TestPostgresIntegration_MultipleQueries tests multiple sequential queries
func TestPostgresIntegration_MultipleQueries(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Run multiple queries
	for i := 0; i < 5; i++ {
		var result int
		err := pc.Pool.QueryRow(ctx, "SELECT $1", i).Scan(&result)
		require.NoError(t, err)
		assert.Equal(t, i, result)
	}
}

// TestPostgresIntegration_TransactionSupport tests transaction support
func TestPostgresIntegration_TransactionSupport(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Create a temporary table
	_, err := pc.Pool.Exec(ctx, `
		CREATE TEMPORARY TABLE test_table (
			id SERIAL PRIMARY KEY,
			name VARCHAR(255)
		)
	`)
	require.NoError(t, err)

	// Test transaction
	tx, err := pc.Pool.Begin(ctx)
	require.NoError(t, err)
	defer tx.Rollback(ctx)

	// Insert data
	_, err = tx.Exec(ctx, "INSERT INTO test_table (name) VALUES ($1)", "test_value")
	require.NoError(t, err)

	// Query data
	var name string
	err = tx.QueryRow(ctx, "SELECT name FROM test_table WHERE name = $1", "test_value").Scan(&name)
	require.NoError(t, err)
	assert.Equal(t, "test_value", name)
}

// TestPostgresIntegration_DataTypes tests various PostgreSQL data types
func TestPostgresIntegration_DataTypes(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	testCases := []struct {
		name     string
		value    interface{}
		expected interface{}
	}{
		{"integer", 42, int32(42)},
		{"text", "hello", "hello"},
		{"boolean", true, true},
		{"timestamp", time.Now().Truncate(time.Microsecond), time.Now().Truncate(time.Microsecond)},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			var result interface{}
			err := pc.Pool.QueryRow(ctx, "SELECT $1::text, $2", tc.value, tc.value).Scan(&result, &result)
			require.NoError(t, err)
		})
	}
}

// TestPostgresIntegration_UUID tests UUID data type support
func TestPostgresIntegration_UUID(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Test UUID generation and retrieval
	var uuid pgtype.UUID
	err := pc.Pool.QueryRow(ctx, "SELECT gen_random_uuid()").Scan(&uuid)
	require.NoError(t, err)
	assert.True(t, uuid.Valid)
}

// TestPostgresIntegration_JSONSupport tests JSON data type support
func TestPostgresIntegration_JSONSupport(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Test JSON operations
	var result string
	err := pc.Pool.QueryRow(ctx, `SELECT '{"key": "value"}'::jsonb ->> 'key'`).Scan(&result)
	require.NoError(t, err)
	assert.Equal(t, "value", result)
}

// TestPostgresIntegration_ConcurrentConnections tests multiple concurrent connections
func TestPostgresIntegration_ConcurrentConnections(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Run concurrent queries
	done := make(chan error, 10)
	for i := 0; i < 10; i++ {
		go func(idx int) {
			var result int
			err := pc.Pool.QueryRow(ctx, "SELECT $1", idx).Scan(&result)
			done <- err
		}(i)
	}

	// Collect results
	for i := 0; i < 10; i++ {
		err := <-done
		assert.NoError(t, err)
	}
}

// TestPostgresIntegration_PoolConfiguration tests connection pool configuration
func TestPostgresIntegration_PoolConfiguration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	ctx, cancel := context.WithTimeout(context.Background(), integrationTestTimeout)
	defer cancel()

	pc := SetupPostgresContainer(ctx, t)
	defer func() { _ = pc.Close(ctx) }()

	// Verify pool is configured
	assert.NotNil(t, pc.Pool)
	assert.NotNil(t, pc.Pool.Config())

	// Test that we can get connection stats
	stats := pc.Pool.Stat()
	assert.Greater(t, stats.TotalConns(), int32(0))
}
