package embeddings

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
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
		return nil, fmt.Errorf("embedding provider is required")
	}

	if config.Pool == nil {
		return nil, fmt.Errorf("database pool is required")
	}

	// Set defaults
	if config.BatchSize == 0 {
		config.BatchSize = 50
	}
	if config.WorkerCount == 0 {
		config.WorkerCount = 3
	}
	if config.PollInterval == 0 {
		config.PollInterval = 30 * time.Second
	}
	if config.RetryAttempts == 0 {
		config.RetryAttempts = 3
	}
	if config.RetryDelay == 0 {
		config.RetryDelay = 5 * time.Second
	}
	if config.MaxQueueSize == 0 {
		config.MaxQueueSize = 1000
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
		return fmt.Errorf("indexer is already running")
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
		log.Printf("Indexer started with %d workers", idx.config.WorkerCount)
	}

	return nil
}

// Stop gracefully shuts down the indexer
func (idx *Indexer) Stop() error {
	idx.runningMu.Lock()
	defer idx.runningMu.Unlock()

	if !idx.running {
		return fmt.Errorf("indexer is not running")
	}

	if idx.config.EnableLogging {
		log.Println("Stopping indexer...")
	}

	idx.cancel()
	close(idx.queue)
	idx.wg.Wait()

	idx.running = false

	if idx.config.EnableLogging {
		log.Println("Indexer stopped")
	}

	return nil
}

// worker processes items from the queue
func (idx *Indexer) worker(workerID int) {
	defer idx.wg.Done()

	if idx.config.EnableLogging {
		log.Printf("Worker %d started", workerID)
	}

	for {
		select {
		case <-idx.ctx.Done():
			if idx.config.EnableLogging {
				log.Printf("Worker %d stopping", workerID)
			}
			return

		case item, ok := <-idx.queue:
			if !ok {
				return
			}

			if err := idx.processItem(item); err != nil {
				idx.stats.mu.Lock()
				idx.stats.TotalErrors++
				idx.stats.mu.Unlock()

				if idx.config.EnableLogging {
					log.Printf("Worker %d: Error processing item %s: %v", workerID, item.ID, err)
				}
			} else {
				idx.stats.mu.Lock()
				idx.stats.TotalProcessed++
				idx.stats.mu.Unlock()

				if idx.config.EnableLogging {
					log.Printf("Worker %d: Successfully processed item %s", workerID, item.ID)
				}
			}
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
		log.Printf("Error loading pending items: %v", err)
	}

	for {
		select {
		case <-idx.ctx.Done():
			return

		case <-ticker.C:
			if err := idx.loadPendingItems(); err != nil && idx.config.EnableLogging {
				log.Printf("Error loading pending items: %v", err)
			}
		}
	}
}

// loadPendingItems loads items that need embedding from the database
func (idx *Indexer) loadPendingItems() error {
	ctx, cancel := context.WithTimeout(idx.ctx, 30*time.Second)
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
			log.Printf("Error scanning item: %v", err)
			continue
		}

		// Non-blocking send to queue
		select {
		case idx.queue <- &item:
			count++
		default:
			if idx.config.EnableLogging {
				log.Printf("Queue is full, skipping item %s", item.ID)
			}
		}
	}

	if count > 0 && idx.config.EnableLogging {
		log.Printf("Loaded %d pending items for embedding", count)
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
	ctx, cancel := context.WithTimeout(idx.ctx, 30*time.Second)
	defer cancel()

	resp, err := idx.config.Provider.Embed(ctx, &EmbeddingRequest{
		Texts:     []string{text},
		InputType: "document",
	})
	if err != nil {
		return fmt.Errorf("failed to generate embedding: %w", err)
	}

	if len(resp.Embeddings) == 0 {
		return fmt.Errorf("no embeddings returned")
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
	idx.stats.AverageLatency = (idx.stats.AverageLatency*time.Duration(idx.stats.TotalProcessed) + latency) / time.Duration(idx.stats.TotalProcessed+1)
	idx.stats.TotalCostUSD += resp.Usage.CostUSD
	idx.stats.mu.Unlock()

	return nil
}

// updateItemEmbedding updates the embedding for an item in the database
func (idx *Indexer) updateItemEmbedding(itemID string, embedding EmbeddingVector) error {
	ctx, cancel := context.WithTimeout(idx.ctx, 10*time.Second)
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
	case <-time.After(5 * time.Second):
		return fmt.Errorf("queue is full, timeout waiting to enqueue item")
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

	result := "["
	for i, val := range vec {
		if i > 0 {
			result += ","
		}
		result += fmt.Sprintf("%f", val)
	}
	result += "]"
	return result
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
	return idx.loadPendingItems()
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
	return idx.loadPendingItems()
}
