// Package embeddings provides embedding and reranking services.
package embeddings

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	defaultIndexerBatchSize     = 50
	defaultIndexerWorkerCount   = 3
	defaultIndexerPollInterval  = 30 * time.Second
	defaultIndexerRetryAttempts = 3
	defaultIndexerRetryDelay    = 5 * time.Second
	defaultIndexerMaxQueueSize  = 1000
	indexerLoadTimeout          = 30 * time.Second
	indexerEmbedTimeout         = 30 * time.Second
	indexerUpdateTimeout        = 10 * time.Second
	indexerQueueTimeout         = 5 * time.Second
	vectorFloatBits             = 32
)

// IndexerConfig holds configuration for the embedding indexer
type IndexerConfig struct {
	Provider      Provider      // Embedding provider to use
	Pool          *pgxpool.Pool // Database connection pool
	BatchSize     int           // Number of items to process per batch
	WorkerCount   int           // Number of concurrent workers
	PollInterval  time.Duration // How often to check for new items
	RetryAttempts int           // Number of retry attempts for failed items
	RetryDelay    time.Duration // Delay between retries
	MaxQueueSize  int           // Maximum items in processing queue
	EnableLogging bool          // Enable detailed logging
}

// IndexItem represents an item that needs embedding
type IndexItem struct {
	ID          string
	ProjectID   string
	Title       string
	Description string
	Type        string
	CreatedAt   time.Time
	UpdatedAt   time.Time
}

// IndexerStats tracks indexer performance metrics
type IndexerStats struct {
	TotalProcessed   int64
	TotalErrors      int64
	CurrentQueueSize int
	LastRunTime      time.Time
	AverageLatency   time.Duration
	TotalCostUSD     float64
	mu               sync.RWMutex
}

// Indexer handles background embedding of items
type Indexer struct {
	config    *IndexerConfig
	stats     *IndexerStats
	queue     chan *IndexItem
	ctx       context.Context
	cancel    context.CancelFunc
	wg        sync.WaitGroup
	running   bool
	runningMu sync.RWMutex
}

// NewIndexer creates a new embedding indexer
func NewIndexer(config *IndexerConfig) (*Indexer, error) {
	if config.Provider == nil {
		return nil, errors.New("embedding provider is required")
	}

	if config.Pool == nil {
		return nil, errors.New("database pool is required")
	}

	// Set defaults
	if config.BatchSize == 0 {
		config.BatchSize = defaultIndexerBatchSize
	}
	if config.WorkerCount == 0 {
		config.WorkerCount = defaultIndexerWorkerCount
	}
	if config.PollInterval == 0 {
		config.PollInterval = defaultIndexerPollInterval
	}
	if config.RetryAttempts == 0 {
		config.RetryAttempts = defaultIndexerRetryAttempts
	}
	if config.RetryDelay == 0 {
		config.RetryDelay = defaultIndexerRetryDelay
	}
	if config.MaxQueueSize == 0 {
		config.MaxQueueSize = defaultIndexerMaxQueueSize
	}

	ctx, cancel := context.WithCancel(context.Background())

	return &Indexer{
		config: config,
		stats:  &IndexerStats{},
		queue:  make(chan *IndexItem, config.MaxQueueSize),
		ctx:    ctx,
		cancel: cancel,
	}, nil
}

// Start begins the indexer background processing
func (idx *Indexer) Start() error {
	idx.runningMu.Lock()
	defer idx.runningMu.Unlock()

	if idx.running {
		return errors.New("indexer is already running")
	}

	idx.running = true

	// Start worker goroutines
	for i := 0; i < idx.config.WorkerCount; i++ {
		idx.wg.Add(1)
		go idx.worker(i)
	}

	// Start polling goroutine
	idx.wg.Add(1)
	go idx.pollForNewItems()

	if idx.config.EnableLogging {
		slog.Info("Indexer started with workers", "index", idx.config.WorkerCount)
	}

	return nil
}

// Stop gracefully shuts down the indexer
func (idx *Indexer) Stop() error {
	idx.runningMu.Lock()
	defer idx.runningMu.Unlock()

	if !idx.running {
		return errors.New("indexer is not running")
	}

	if idx.config.EnableLogging {
		slog.Info("Stopping indexer...")
	}

	idx.cancel()
	close(idx.queue)
	idx.wg.Wait()

	idx.running = false

	if idx.config.EnableLogging {
		slog.Info("Indexer stopped")
	}

	return nil
}

// logWorkerActivity logs worker activity if logging is enabled
func (idx *Indexer) logWorkerActivity(workerID int, message string, itemID string, err error) {
	if !idx.config.EnableLogging {
		return
	}
	if err != nil {
		slog.Error("Worker : Error processing item", "id", workerID, "error", itemID, "error", err)
	} else {
		slog.Info(message, "id", workerID, "id", itemID)
	}
}

// updateWorkerStats updates statistics for processed items
func (idx *Indexer) updateWorkerStats(err error) {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	if err != nil {
		idx.stats.TotalErrors++
	} else {
		idx.stats.TotalProcessed++
	}
}

// processQueueItem processes a single item from the queue with stats and logging
func (idx *Indexer) processQueueItem(workerID int, item *IndexItem) {
	err := idx.processItem(item)
	idx.updateWorkerStats(err)
	if err != nil {
		idx.logWorkerActivity(workerID, "", item.ID, err)
	} else {
		idx.logWorkerActivity(workerID, "Worker : Successfully processed item", item.ID, nil)
	}
}

// worker processes items from the queue
func (idx *Indexer) worker(workerID int) {
	defer idx.wg.Done()

	if idx.config.EnableLogging {
		slog.Info("Worker started", "id", workerID)
	}

	for {
		select {
		case <-idx.ctx.Done():
			if idx.config.EnableLogging {
				slog.Info("Worker stopping", "id", workerID)
			}
			return

		case item, ok := <-idx.queue:
			if !ok {
				return
			}
			idx.processQueueItem(workerID, item)
		}
	}
}

// pollForNewItems periodically checks for items that need embedding
func (idx *Indexer) pollForNewItems() {
	defer idx.wg.Done()

	ticker := time.NewTicker(idx.config.PollInterval)
	defer ticker.Stop()

	// Initial poll
	if err := idx.loadPendingItems(); err != nil && idx.config.EnableLogging {
		slog.Error("Error loading pending items", "error", err)
	}

	for {
		select {
		case <-idx.ctx.Done():
			return

		case <-ticker.C:
			if err := idx.loadPendingItems(); err != nil && idx.config.EnableLogging {
				slog.Error("Error loading pending items", "error", err)
			}
		}
	}
}

// loadPendingItems loads items that need embedding from the database
func (idx *Indexer) loadPendingItems() error {
	ctx, cancel := context.WithTimeout(idx.ctx, indexerLoadTimeout)
	defer cancel()

	query := `
		SELECT id, project_id, title, description, type, created_at, updated_at
		FROM items
		WHERE embedding IS NULL
			AND deleted_at IS NULL
		ORDER BY created_at DESC
		LIMIT $1
	`

	rows, err := idx.config.Pool.Query(ctx, query, idx.config.BatchSize)
	if err != nil {
		return fmt.Errorf("failed to query pending items: %w", err)
	}
	defer rows.Close()
	count := 0
	for rows.Next() {
		var item IndexItem
		err := rows.Scan(
			&item.ID,
			&item.ProjectID,
			&item.Title,
			&item.Description,
			&item.Type,
			&item.CreatedAt,
			&item.UpdatedAt,
		)
		if err != nil {
			slog.Error("Error scanning item", "error", err)
			continue
		}

		// Non-blocking send to queue
		select {
		case idx.queue <- &item:
			count++
		default:
			if idx.config.EnableLogging {
				slog.Warn("Queue is full, skipping item", "id", item.ID)
			}
		}
	}

	if count > 0 && idx.config.EnableLogging {
		slog.Info("Loaded pending items for embedding", "value", count)
	}

	idx.stats.mu.Lock()
	idx.stats.CurrentQueueSize = len(idx.queue)
	idx.stats.LastRunTime = time.Now()
	idx.stats.mu.Unlock()

	return rows.Err()
}

// processItem generates embedding for a single item and updates the database
func (idx *Indexer) processItem(item *IndexItem) error {
	start := time.Now()

	// Combine title and description for embedding
	text := item.Title
	if item.Description != "" {
		text += "\n\n" + item.Description
	}

	// Generate embedding
	ctx, cancel := context.WithTimeout(idx.ctx, indexerEmbedTimeout)
	defer cancel()

	resp, err := idx.config.Provider.Embed(ctx, &EmbeddingRequest{
		Texts:     []string{text},
		Model:     "",
		InputType: "document",
	})
	if err != nil {
		return fmt.Errorf("failed to generate embedding: %w", err)
	}

	if len(resp.Embeddings) == 0 {
		return errors.New("no embeddings returned")
	}

	embedding := resp.Embeddings[0]

	// Validate embedding
	if err := ValidateEmbeddings([]EmbeddingVector{embedding}, idx.config.Provider.GetDimensions()); err != nil {
		return fmt.Errorf("invalid embedding: %w", err)
	}

	// Update database
	if err := idx.updateItemEmbedding(item.ID, embedding); err != nil {
		return fmt.Errorf("failed to update database: %w", err)
	}

	// Update stats
	latency := time.Since(start)
	idx.stats.mu.Lock()
	prevTotal := time.Duration(idx.stats.TotalProcessed)
	idx.stats.AverageLatency = (idx.stats.AverageLatency*prevTotal + latency) / time.Duration(idx.stats.TotalProcessed+1)
	idx.stats.TotalCostUSD += resp.Usage.CostUSD
	idx.stats.mu.Unlock()

	return nil
}

// updateItemEmbedding updates the embedding for an item in the database
func (idx *Indexer) updateItemEmbedding(itemID string, embedding EmbeddingVector) error {
	ctx, cancel := context.WithTimeout(idx.ctx, indexerUpdateTimeout)
	defer cancel()

	// Convert embedding to pgvector format
	embeddingStr := vectorToString(embedding)

	query := `
		UPDATE items
		SET embedding = $1::vector,
			updated_at = NOW()
		WHERE id = $2
	`

	_, err := idx.config.Pool.Exec(ctx, query, embeddingStr, itemID)
	if err != nil {
		return fmt.Errorf("failed to update embedding: %w", err)
	}

	return nil
}

// IndexItem manually queues a single item for embedding
func (idx *Indexer) IndexItem(item *IndexItem) error {
	select {
	case idx.queue <- item:
		return nil
	case <-time.After(indexerQueueTimeout):
		return errors.New("queue is full, timeout waiting to enqueue item")
	}
}

// GetStats returns current indexer statistics
func (idx *Indexer) GetStats() *IndexerStats {
	idx.stats.mu.RLock()
	defer idx.stats.mu.RUnlock()

	// Create a new struct with only the fields (avoiding mutex copy)
	return &IndexerStats{
		TotalProcessed:   idx.stats.TotalProcessed,
		TotalErrors:      idx.stats.TotalErrors,
		CurrentQueueSize: len(idx.queue),
		LastRunTime:      idx.stats.LastRunTime,
		AverageLatency:   idx.stats.AverageLatency,
		TotalCostUSD:     idx.stats.TotalCostUSD,
	}
}

// IsRunning returns whether the indexer is currently running
func (idx *Indexer) IsRunning() bool {
	idx.runningMu.RLock()
	defer idx.runningMu.RUnlock()
	return idx.running
}

// vectorToString converts an embedding vector to PostgreSQL vector format
func vectorToString(vec EmbeddingVector) string {
	if len(vec) == 0 {
		return "[]"
	}

	var builder strings.Builder
	builder.WriteByte('[')
	for i, val := range vec {
		if i > 0 {
			builder.WriteByte(',')
		}
		builder.WriteString(strconv.FormatFloat(float64(val), 'f', 6, vectorFloatBits))
	}
	builder.WriteByte(']')
	return builder.String()
}

// ReindexAll triggers a full reindex of all items (use with caution)
func (idx *Indexer) ReindexAll(ctx context.Context) error {
	query := `
		UPDATE items
		SET embedding = NULL
		WHERE deleted_at IS NULL
	`

	_, err := idx.config.Pool.Exec(ctx, query)
	if err != nil {
		return fmt.Errorf("failed to reset embeddings: %w", err)
	}

	// Trigger immediate poll
	return idx.loadPendingItems() //nolint:contextcheck // loadPendingItems uses indexer's long-lived context, not the request context
}

// ReindexProject triggers reindex for all items in a project
func (idx *Indexer) ReindexProject(ctx context.Context, projectID string) error {
	query := `
		UPDATE items
		SET embedding = NULL
		WHERE project_id = $1
			AND deleted_at IS NULL
	`

	_, err := idx.config.Pool.Exec(ctx, query, projectID)
	if err != nil {
		return fmt.Errorf("failed to reset project embeddings: %w", err)
	}

	// Trigger immediate poll
	return idx.loadPendingItems() //nolint:contextcheck // loadPendingItems uses indexer's long-lived context
}
