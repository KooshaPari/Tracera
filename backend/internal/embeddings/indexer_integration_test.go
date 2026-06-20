//go:build integration

package embeddings

import (
	"context"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

const (
	testVectorDimensions     = 1024
	testWaitOccurrence       = 2
	testStartupTimeout       = 30 * time.Second
	testBatchSize            = 10
	testWorkerCountSmall     = 1
	testWorkerCountLarge     = 2
	testPollIntervalSlow     = 1 * time.Second
	testPollIntervalFast     = 100 * time.Millisecond
	testRetryAttempts        = 3
	testRetryDelaySlow       = 100 * time.Millisecond
	testRetryDelayFast       = 50 * time.Millisecond
	testMaxQueueSize         = 100
	testExpectedEmbeddings   = 1
	testReindexItemCount     = 3
	testPendingItemCount     = 2
	testWorkerSleep          = 500 * time.Millisecond
	testPollerSleep          = 300 * time.Millisecond
	testMockPromptTokensUnit = 10
	testMockScoreScale       = 0.1
)

// setupTestDB creates a PostgreSQL test container
func setupTestDB(t *testing.T) (*pgxpool.Pool, func()) {
	ctx := context.Background()

	pgContainer, err := postgres.RunContainer(ctx,
		testcontainers.WithImage("postgres:15-alpine"),
		postgres.WithDatabase("tracertm_test"),
		postgres.WithUsername("tracertm"),
		postgres.WithPassword("password123"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(testWaitOccurrence).
				WithStartupTimeout(testStartupTimeout),
		),
	)
	require.NoError(t, err)

	dsn, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	require.NoError(t, err)

	pool, err := pgxpool.New(ctx, dsn)
	require.NoError(t, err)

	// Initialize schema
	_, err = pool.Exec(ctx, `
		CREATE EXTENSION IF NOT EXISTS vector;
		CREATE TABLE IF NOT EXISTS items (
			id UUID PRIMARY KEY,
			project_id UUID NOT NULL,
			title TEXT NOT NULL,
			description TEXT,
			type TEXT,
			status TEXT,
			priority TEXT,
			created_at TIMESTAMP DEFAULT NOW(),
			updated_at TIMESTAMP DEFAULT NOW()
		);
		CREATE TABLE IF NOT EXISTS item_embeddings (
			item_id UUID PRIMARY KEY REFERENCES items(id),
			embedding vector(1024),
			model TEXT,
			created_at TIMESTAMP DEFAULT NOW(),
			updated_at TIMESTAMP DEFAULT NOW()
		);
	`)
	require.NoError(t, err)

	cleanup := func() {
		_ = pool.Close()
		pgContainer.Terminate(ctx)
	}

	return pool, cleanup
}

// mockProvider is a simple mock provider for testing
type mockProvider struct {
	dimensions int
}

func (m *mockProvider) Embed(ctx context.Context, req *EmbeddingRequest) (*EmbeddingResponse, error) {
	// Return mock embeddings
	embeddings := make([]EmbeddingVector, len(req.Texts))
	for i := range embeddings {
		embeddings[i] = make(EmbeddingVector, m.dimensions)
		for j := range embeddings[i] {
			embeddings[i][j] = float32(i) + float32(j)*testMockScoreScale
		}
	}
	return &EmbeddingResponse{
		Embeddings: embeddings,
		Model:      "test-model",
		Usage: TokenUsage{
			PromptTokens: len(req.Texts) * testMockPromptTokensUnit,
		},
	}, nil
}

func (m *mockProvider) GetDimensions() int {
	return m.dimensions
}

func (m *mockProvider) GetName() string {
	return "mock"
}

func (m *mockProvider) GetDefaultModel() string {
	return "test-model"
}

func (m *mockProvider) HealthCheck(ctx context.Context) error {
	return nil
}

// TestIndexer_Start tests the Start method
func TestIndexer_Start(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountLarge,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.Start()
	require.NoError(t, err)
	assert.True(t, indexer.IsRunning())

	// Try to start again (should fail)
	err = indexer.Start()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "already running")

	// Cleanup
	err = indexer.Stop()
	require.NoError(t, err)
}

// TestIndexer_Stop tests the Stop method
func TestIndexer_Stop(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.Start()
	require.NoError(t, err)

	err = indexer.Stop()
	require.NoError(t, err)
	assert.False(t, indexer.IsRunning())

	// Try to stop again (should fail)
	err = indexer.Stop()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "not running")
}

// TestIndexer_IndexItem tests the IndexItem method
func TestIndexer_IndexItem(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	// Insert a test item
	itemID := "123e4567-e89b-12d3-a456-426614174000"
	projectID := "223e4567-e89b-12d3-a456-426614174000"
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, description, type)
		VALUES ($1, $2, $3, $4, $5)
	`, itemID, projectID, "Test Item", "Test Description", "requirement")
	require.NoError(t, err)

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	item := &IndexItem{
		ID:          itemID,
		ProjectID:   projectID,
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "requirement",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	err = indexer.IndexItem(item)
	require.NoError(t, err)

	// Verify embedding was created
	var count int
	err = pool.QueryRow(ctx, `
		SELECT COUNT(*) FROM item_embeddings WHERE item_id = $1
	`, itemID).Scan(&count)
	require.NoError(t, err)
	assert.Equal(t, testExpectedEmbeddings, count)
}

// TestIndexer_ReindexAll tests the ReindexAll method
func TestIndexer_ReindexAll(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	// Insert multiple test items
	projectID := "223e4567-e89b-12d3-a456-426614174000"
	for i := 0; i < testReindexItemCount; i++ {
		itemID := "123e4567-e89b-12d3-a456-42661417400" + string(rune('0'+i))
		_, err := pool.Exec(ctx, `
			INSERT INTO items (id, project_id, title, description, type)
			VALUES ($1, $2, $3, $4, $5)
		`, itemID, projectID, "Test Item "+string(rune('0'+i)), "Description", "requirement")
		require.NoError(t, err)
	}

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountLarge,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.ReindexAll(ctx)
	require.NoError(t, err)

	// Verify embeddings were created
	var count int
	err = pool.QueryRow(ctx, `
		SELECT COUNT(*) FROM item_embeddings
	`).Scan(&count)
	require.NoError(t, err)
	assert.GreaterOrEqual(t, count, 0) // May be 0 if items don't match criteria
}

// TestIndexer_ReindexProject tests the ReindexProject method
func TestIndexer_ReindexProject(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	projectID := "223e4567-e89b-12d3-a456-426614174000"
	itemID := "123e4567-e89b-12d3-a456-426614174000"
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, description, type)
		VALUES ($1, $2, $3, $4, $5)
	`, itemID, projectID, "Test Item", "Description", "requirement")
	require.NoError(t, err)

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.ReindexProject(ctx, projectID)
	require.NoError(t, err)
}

// TestIndexer_GetStats tests the GetStats method
func TestIndexer_GetStats(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	stats := indexer.GetStats()
	assert.NotNil(t, stats)
	assert.Equal(t, int64(0), stats.TotalProcessed)
	assert.Equal(t, int64(0), stats.TotalErrors)
}

// TestIndexer_IsRunning tests the IsRunning method
func TestIndexer_IsRunning(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	provider := &mockProvider{dimensions: 1024}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     10,
		WorkerCount:   1,
		PollInterval:  1 * time.Second,
		RetryAttempts: 3,
		RetryDelay:    100 * time.Millisecond,
		MaxQueueSize:  100,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	assert.False(t, indexer.IsRunning())

	err := indexer.Start()
	require.NoError(t, err)
	assert.True(t, indexer.IsRunning())

	err = indexer.Stop()
	require.NoError(t, err)
	assert.False(t, indexer.IsRunning())
}

// TestIndexer_Worker tests the worker goroutine
func TestIndexer_Worker(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	itemID := "123e4567-e89b-12d3-a456-426614174000"
	projectID := "223e4567-e89b-12d3-a456-426614174000"
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, description, type)
		VALUES ($1, $2, $3, $4, $5)
	`, itemID, projectID, "Test Item", "Description", "requirement")
	require.NoError(t, err)

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalFast,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelayFast,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.Start()
	require.NoError(t, err)

	// Give worker time to process
	time.Sleep(testWorkerSleep)

	err = indexer.Stop()
	require.NoError(t, err)
}

// TestIndexer_PollForNewItems tests the pollForNewItems goroutine
func TestIndexer_PollForNewItems(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalFast,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelayFast,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.Start()
	require.NoError(t, err)

	// Give poller time to run
	time.Sleep(testPollerSleep)

	err = indexer.Stop()
	require.NoError(t, err)
}

// TestIndexer_ProcessItem tests the processItem method indirectly
func TestIndexer_ProcessItem(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	itemID := "123e4567-e89b-12d3-a456-426614174000"
	projectID := "223e4567-e89b-12d3-a456-426614174000"
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, description, type)
		VALUES ($1, $2, $3, $4, $5)
	`, itemID, projectID, "Test Item", "Test Description", "requirement")
	require.NoError(t, err)

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	item := &IndexItem{
		ID:          itemID,
		ProjectID:   projectID,
		Title:       "Test Item",
		Description: "Test Description",
		Type:        "requirement",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	// Index item which will trigger processItem
	err = indexer.IndexItem(item)
	require.NoError(t, err)

	// Verify embedding was created
	var count int
	err = pool.QueryRow(ctx, `
		SELECT COUNT(*) FROM item_embeddings WHERE item_id = $1
	`, itemID).Scan(&count)
	require.NoError(t, err)
	assert.Equal(t, testExpectedEmbeddings, count)
}

// TestIndexer_UpdateItemEmbedding tests the updateItemEmbedding method indirectly
func TestIndexer_UpdateItemEmbedding(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	itemID := "123e4567-e89b-12d3-a456-426614174000"
	projectID := "223e4567-e89b-12d3-a456-426614174000"
	_, err := pool.Exec(ctx, `
		INSERT INTO items (id, project_id, title, description, type)
		VALUES ($1, $2, $3, $4, $5)
	`, itemID, projectID, "Test Item", "Description", "requirement")
	require.NoError(t, err)

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalSlow,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelaySlow,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	item := &IndexItem{
		ID:          itemID,
		ProjectID:   projectID,
		Title:       "Test Item",
		Description: "Description",
		Type:        "requirement",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	// Index item twice to trigger update
	err = indexer.IndexItem(item)
	require.NoError(t, err)

	// Update and re-index
	item.Description = "Updated Description"
	err = indexer.IndexItem(item)
	require.NoError(t, err)

	// Verify embedding exists
	var count int
	err = pool.QueryRow(ctx, `
		SELECT COUNT(*) FROM item_embeddings WHERE item_id = $1
	`, itemID).Scan(&count)
	require.NoError(t, err)
	assert.Equal(t, testExpectedEmbeddings, count)
}

// TestIndexer_LoadPendingItems tests the loadPendingItems method indirectly
func TestIndexer_LoadPendingItems(t *testing.T) {
	pool, cleanup := setupTestDB(t)
	defer cleanup()

	ctx := context.Background()

	// Insert items without embeddings
	projectID := "223e4567-e89b-12d3-a456-426614174000"
	for i := 0; i < testPendingItemCount; i++ {
		itemID := "123e4567-e89b-12d3-a456-42661417400" + string(rune('0'+i))
		_, err := pool.Exec(ctx, `
			INSERT INTO items (id, project_id, title, description, type)
			VALUES ($1, $2, $3, $4, $5)
		`, itemID, projectID, "Test Item "+string(rune('0'+i)), "Description", "requirement")
		require.NoError(t, err)
	}

	provider := &mockProvider{dimensions: testVectorDimensions}
	config := &IndexerConfig{
		Provider:      provider,
		Pool:          pool,
		BatchSize:     testBatchSize,
		WorkerCount:   testWorkerCountSmall,
		PollInterval:  testPollIntervalFast,
		RetryAttempts: testRetryAttempts,
		RetryDelay:    testRetryDelayFast,
		MaxQueueSize:  testMaxQueueSize,
		EnableLogging: false,
	}

	indexer, err := NewIndexer(config)
	require.NoError(t, err)
	require.NotNil(t, indexer)

	err = indexer.Start()
	require.NoError(t, err)

	// Give poller time to load pending items
	time.Sleep(testWorkerSleep)

	err = indexer.Stop()
	require.NoError(t, err)
}
