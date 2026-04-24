package search

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// IndexOperation represents a type of indexing operation
type IndexOperation string

const (
	// OpIndex represents adding documents to search index
	OpIndex IndexOperation = "index"
	// OpUpdate represents updating existing documents in search index
	OpUpdate IndexOperation = "update"
	// OpDelete represents removing documents from search index
	OpDelete IndexOperation = "delete"
)

const (
	defaultWorkerPoolSize = 4
	defaultQueueSize      = 1000

	indexItemTimeout    = 10 * time.Second
	updateItemTimeout   = 30 * time.Second
	deleteItemTimeout   = 5 * time.Second
	statsReportInterval = 1 * time.Minute
	queueCheckInterval  = 100 * time.Millisecond
	queueStabilizeDelay = 200 * time.Millisecond

	priorityReindex = 0
	priorityNormal  = 1
	priorityDelete  = 2
)

// IndexJob represents a single indexing job
type IndexJob struct {
	Operation IndexOperation
	ItemID    string
	Priority  int // Higher priority jobs are processed first
}

// Indexer handles asynchronous search index updates
type Indexer struct {
	pool       *pgxpool.Pool
	jobQueue   chan IndexJob
	workerPool int
	wg         sync.WaitGroup
	ctx        context.Context
	cancel     context.CancelFunc
	stats      IndexerStats
}

// IndexerStats tracks indexing statistics
type IndexerStats struct {
	TotalJobs      int64
	CompletedJobs  int64
	FailedJobs     int64
	QueueSize      int
	LastIndexedAt  time.Time
	LastError      string
	ProcessingRate float64 // jobs per second
	mu             sync.RWMutex
}

// NewIndexer creates a new search indexer
func NewIndexer(pool *pgxpool.Pool, workerPool int, queueSize int) *Indexer {
	if workerPool <= 0 {
		workerPool = defaultWorkerPoolSize // Default to 4 workers
	}
	if queueSize <= 0 {
		queueSize = defaultQueueSize // Default queue size
	}

	ctx, cancel := context.WithCancel(context.Background())

	return &Indexer{
		pool:       pool,
		jobQueue:   make(chan IndexJob, queueSize),
		workerPool: workerPool,
		ctx:        ctx,
		cancel:     cancel,
		stats:      IndexerStats{},
	}
}

// Start begins processing index jobs
func (idx *Indexer) Start() {
	for i := 0; i < idx.workerPool; i++ {
		idx.wg.Add(1)
		go idx.worker(i)
	}

	// Start stats reporter
	go idx.reportStats()
}

// Stop gracefully stops the indexer
func (idx *Indexer) Stop() {
	idx.cancel()
	close(idx.jobQueue)
	idx.wg.Wait()
}

// worker processes index jobs from the queue
func (idx *Indexer) worker(_ int) {
	defer idx.wg.Done()

	for {
		select {
		case <-idx.ctx.Done():
			return
		case job, ok := <-idx.jobQueue:
			if !ok {
				return
			}

			idx.processJob(job)
		}
	}
}

// processJob executes a single indexing job
func (idx *Indexer) processJob(job IndexJob) {
	start := time.Now()

	var err error
	switch job.Operation {
	case OpIndex, OpUpdate:
		err = idx.indexItem(job.ItemID)
	case OpDelete:
		err = idx.deleteItemIndex(job.ItemID)
	default:
		slog.Info("Unknown index operation", "index", job.Operation)
		idx.incrementFailed()
		return
	}

	duration := time.Since(start)

	if err != nil {
		slog.Error("Index job failed",
			"operation", job.Operation, "item_id", job.ItemID, "duration", duration, "error", err)
		idx.incrementFailed()
		idx.setLastError(err.Error())
	} else {
		idx.incrementCompleted()
		idx.updateLastIndexed()
	}
}

// indexItem indexes or re-indexes a single item
func (idx *Indexer) indexItem(itemID string) error {
	ctx, cancel := context.WithTimeout(idx.ctx, indexItemTimeout)
	defer cancel()

	// Update the search_vector field using PostgreSQL's to_tsvector
	query := `
		UPDATE items
		SET
			search_vector = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
			updated_at = CURRENT_TIMESTAMP
		WHERE id = $1
	`

	result, err := idx.pool.Exec(ctx, query, itemID)
	if err != nil {
		return fmt.Errorf("failed to update search vector: %w", err)
	}

	rowsAffected := result.RowsAffected()
	if rowsAffected == 0 {
		return fmt.Errorf("item not found: %s", itemID)
	}

	return nil
}

// IndexItemWithEmbedding indexes an item and generates its vector embedding
// This method is currently unused but kept for future embedding integration
func (idx *Indexer) IndexItemWithEmbedding(itemID string, embeddingJSON string) error {
	ctx, cancel := context.WithTimeout(idx.ctx, updateItemTimeout)
	defer cancel()

	// Update both search_vector and embedding
	query := `
		UPDATE items
		SET
			search_vector = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
			embedding = $2::vector,
			updated_at = CURRENT_TIMESTAMP
		WHERE id = $1
	`

	result, err := idx.pool.Exec(ctx, query, itemID, embeddingJSON)
	if err != nil {
		return fmt.Errorf("failed to update search index with embedding: %w", err)
	}

	rowsAffected := result.RowsAffected()
	if rowsAffected == 0 {
		return fmt.Errorf("item not found: %s", itemID)
	}

	return nil
}

// deleteItemIndex removes an item from the search index
func (idx *Indexer) deleteItemIndex(itemID string) error {
	ctx, cancel := context.WithTimeout(idx.ctx, deleteItemTimeout)
	defer cancel()

	// For soft deletes, we just clear the search vector
	query := `
		UPDATE items
		SET
			search_vector = NULL,
			embedding = NULL
		WHERE id = $1
	`

	_, err := idx.pool.Exec(ctx, query, itemID)
	if err != nil {
		return fmt.Errorf("failed to remove from search index: %w", err)
	}

	return nil
}

// QueueIndex adds an item to the indexing queue
func (idx *Indexer) QueueIndex(itemID string, priority int) error {
	idx.incrementTotal()

	job := IndexJob{
		Operation: OpIndex,
		ItemID:    itemID,
		Priority:  priority,
	}

	select {
	case idx.jobQueue <- job:
		idx.updateQueueSize(len(idx.jobQueue))
		return nil
	case <-idx.ctx.Done():
		return errors.New("indexer is shutting down")
	default:
		return errors.New("index queue is full")
	}
}

// QueueUpdate adds an item update to the indexing queue
func (idx *Indexer) QueueUpdate(itemID string) error {
	return idx.QueueIndex(itemID, priorityNormal) // Normal priority
}

// QueueDelete adds an item deletion to the indexing queue
func (idx *Indexer) QueueDelete(itemID string) error {
	idx.incrementTotal()

	job := IndexJob{
		Operation: OpDelete,
		ItemID:    itemID,
		Priority:  priorityDelete, // Higher priority for deletes
	}

	select {
	case idx.jobQueue <- job:
		idx.updateQueueSize(len(idx.jobQueue))
		return nil
	case <-idx.ctx.Done():
		return errors.New("indexer is shutting down")
	default:
		return errors.New("index queue is full")
	}
}

// ReindexAll reindexes all items in the database
func (idx *Indexer) ReindexAll(ctx context.Context) error {
	slog.Info("Starting full reindex...")

	query := `SELECT id FROM items WHERE deleted_at IS NULL`
	rows, err := idx.pool.Query(ctx, query)
	if err != nil {
		return fmt.Errorf("failed to fetch items for reindexing: %w", err)
	}
	defer rows.Close()

	count := 0
	for rows.Next() {
		var itemID string
		if err := rows.Scan(&itemID); err != nil {
			slog.Error("Error scanning item ID", "error", err)
			continue
		}

		if err := idx.QueueIndex(itemID, priorityReindex); err != nil {
			slog.Error("Error queueing item for reindex", "error", itemID, "index", err)
			continue
		}
		count++
	}

	if err := rows.Err(); err != nil {
		return fmt.Errorf("error iterating items: %w", err)
	}

	slog.Info("Queued items for reindexing", "value", count)
	return nil
}

// Stats returns current indexer statistics
func (idx *Indexer) Stats() IndexerStats {
	idx.stats.mu.RLock()
	defer idx.stats.mu.RUnlock()

	// Return copy without the mutex to avoid lock copying
	return IndexerStats{
		TotalJobs:      idx.stats.TotalJobs,
		CompletedJobs:  idx.stats.CompletedJobs,
		FailedJobs:     idx.stats.FailedJobs,
		QueueSize:      len(idx.jobQueue),
		LastIndexedAt:  idx.stats.LastIndexedAt,
		LastError:      idx.stats.LastError,
		ProcessingRate: idx.stats.ProcessingRate,
	}
}

// reportStats periodically logs indexer statistics
func (idx *Indexer) reportStats() {
	ticker := time.NewTicker(statsReportInterval)
	defer ticker.Stop()

	lastCompleted := int64(0)
	lastTime := time.Now()

	for {
		select {
		case <-idx.ctx.Done():
			return
		case <-ticker.C:
			stats := idx.Stats()

			// Calculate processing rate
			now := time.Now()
			elapsed := now.Sub(lastTime).Seconds()
			completed := stats.CompletedJobs - lastCompleted

			if elapsed > 0 {
				rate := float64(completed) / elapsed
				idx.setProcessingRate(rate)
			}

			lastCompleted = stats.CompletedJobs
			lastTime = now

			slog.Info("Indexer stats",
				"total", stats.TotalJobs, "completed", stats.CompletedJobs,
				"failed", stats.FailedJobs, "queue", stats.QueueSize, "rate", stats.ProcessingRate)
		}
	}
}

// Statistics update methods

func (idx *Indexer) incrementTotal() {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.TotalJobs++
}

func (idx *Indexer) incrementCompleted() {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.CompletedJobs++
}

func (idx *Indexer) incrementFailed() {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.FailedJobs++
}

func (idx *Indexer) updateQueueSize(size int) {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.QueueSize = size
}

func (idx *Indexer) updateLastIndexed() {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.LastIndexedAt = time.Now()
}

func (idx *Indexer) setLastError(err string) {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.LastError = err
}

func (idx *Indexer) setProcessingRate(rate float64) {
	idx.stats.mu.Lock()
	defer idx.stats.mu.Unlock()
	idx.stats.ProcessingRate = rate
}

// WaitForQueue waits for the queue to be empty (useful for testing)
func (idx *Indexer) WaitForQueue(timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	ticker := time.NewTicker(queueCheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-idx.ctx.Done():
			return errors.New("indexer stopped")
		case <-ticker.C:
			if len(idx.jobQueue) == 0 {
				// Wait a bit more to ensure workers finished
				time.Sleep(queueStabilizeDelay)
				if len(idx.jobQueue) == 0 {
					return nil
				}
			}
			if time.Now().After(deadline) {
				return errors.New("timeout waiting for queue to empty")
			}
		}
	}
}
