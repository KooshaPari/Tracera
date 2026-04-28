package tests

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/tx"
)

// ============================================================================
// MOCK CACHE IMPLEMENTATION FOR BENCHMARKING
// ============================================================================

// memoryCache is a simple in-memory cache for benchmarking
type memoryCache struct {
	data map[string]interface{}
	mu   sync.RWMutex
}

func newMemoryCache() cache.Cache {
	return &memoryCache{
		data: make(map[string]interface{}),
	}
}

func (m *memoryCache) Get(ctx context.Context, key string, dest interface{}) error {
	m.mu.RLock()
	defer m.mu.RUnlock()

	val, ok := m.data[key]
	if !ok {
		return errors.New("key not found")
	}

	// Simple copy for benchmark purposes
	switch d := dest.(type) {
	case *models.Item:
		if v, ok := val.(*models.Item); ok {
			*d = *v
		}
	case *[]*models.Item:
		if v, ok := val.([]*models.Item); ok {
			*d = v
		}
	}

	return nil
}

func (m *memoryCache) Set(ctx context.Context, key string, value interface{}) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.data[key] = value
	return nil
}

func (m *memoryCache) Delete(ctx context.Context, keys ...string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	for _, key := range keys {
		delete(m.data, key)
	}
	return nil
}

func (m *memoryCache) InvalidatePattern(ctx context.Context, pattern string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Simple pattern matching for benchmark
	for key := range m.data {
		delete(m.data, key)
	}
	return nil
}

func (m *memoryCache) Close() error {
	return nil
}

// ============================================================================
// TEST SETUP AND UTILITIES
// ============================================================================

var (
	benchDB          *gorm.DB
	benchCache       cache.Cache
	benchItemRepo    repository.ItemRepository
	benchLinkRepo    repository.LinkRepository
	benchProjectRepo repository.ProjectRepository
	benchItemService services.ItemService
	benchProjectID   string
)

// setupBenchmark initializes test dependencies
func setupBenchmark(b *testing.B) {
	b.Helper()

	var err error

	// Connect to test database
	dsn := "host=localhost user=postgres password=postgres dbname=trace_test port=5432 sslmode=disable"
	benchDB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
		PrepareStmt: true, // Enable prepared statements for better performance
	})
	if err != nil {
		b.Skip("Skipping benchmark: database not available")
		return
	}

	// Auto-migrate models
	if err := benchDB.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}); err != nil {
		b.Fatalf("Failed to migrate database: %v", err)
	}

	// Initialize repositories
	benchItemRepo = repository.NewItemRepository(benchDB)
	benchLinkRepo = repository.NewLinkRepository(benchDB)
	benchProjectRepo = repository.NewProjectRepository(benchDB)

	// Initialize cache (in-memory for benchmarking)
	benchCache = newMemoryCache()

	// Initialize service with cache
	benchItemService = services.NewItemServiceImpl(benchItemRepo, benchLinkRepo, benchCache, nil)

	// Create test project
	benchProjectID = uuid.New().String()
	project := &models.Project{
		ID:          benchProjectID,
		Name:        "Benchmark Project",
		Description: "Project for performance benchmarks",
	}
	if err := benchProjectRepo.Create(context.Background(), project); err != nil {
		b.Fatalf("Failed to create test project: %v", err)
	}
}

// teardownBenchmark cleans up test data
func teardownBenchmark(b *testing.B) {
	b.Helper()

	if benchDB == nil {
		return
	}

	// Clean up test data
	benchDB.Exec("DELETE FROM items WHERE project_id = ?", benchProjectID)
	benchDB.Exec("DELETE FROM links")
	benchDB.Exec("DELETE FROM projects WHERE id = ?", benchProjectID)
}

// createBenchItem creates a test item with default values
func createBenchItem(projectID string) *models.Item {
	return &models.Item{
		ID:          uuid.New().String(),
		ProjectID:   projectID,
		Title:       "Benchmark Test Item",
		Description: "Item created for benchmark testing",
		Type:        "requirement",
		Status:      "todo",
		Priority:    models.PriorityMedium,
		Metadata:    datatypes.JSON([]byte(`{"test": true}`)),
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
}

// createBenchLink creates a test link between items
func createBenchLink(sourceID, targetID string) *models.Link {
	return &models.Link{
		ID:       uuid.New().String(),
		SourceID: sourceID,
		TargetID: targetID,
		Type:     "satisfies",
		Metadata: datatypes.JSON([]byte(`{}`)),
	}
}

// ============================================================================
// BENCHMARK: ITEM CREATE OPERATIONS
// ============================================================================

// BenchmarkServiceCreateItem benchmarks item creation via service layer
func BenchmarkServiceCreateItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemService.CreateItem(ctx, item); err != nil {
			b.Fatalf("Failed to create item: %v", err)
		}
	}
}

// BenchmarkLegacyCreateItem benchmarks item creation via repository (legacy)
func BenchmarkLegacyCreateItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create item: %v", err)
		}
	}
}

// BenchmarkServiceCreateBatch benchmarks batch creation via service layer
func BenchmarkServiceCreateBatch(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()
	batchSize := 10

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		items := make([]*models.Item, batchSize)
		for j := 0; j < batchSize; j++ {
			items[j] = createBenchItem(benchProjectID)
		}
		if err := benchItemService.CreateBatch(ctx, items); err != nil {
			b.Fatalf("Failed to create batch: %v", err)
		}
	}
}

// ============================================================================
// BENCHMARK: ITEM READ OPERATIONS
// ============================================================================

// BenchmarkServiceGetItemWithCache benchmarks item retrieval with caching
func BenchmarkServiceGetItemWithCache(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create test item
	item := createBenchItem(benchProjectID)
	if err := benchItemService.CreateItem(ctx, item); err != nil {
		b.Fatalf("Failed to create test item: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := benchItemService.GetItem(ctx, item.ID)
		if err != nil {
			b.Fatalf("Failed to get item: %v", err)
		}
	}
}

// BenchmarkServiceGetItemNoCache benchmarks item retrieval without caching
func BenchmarkServiceGetItemNoCache(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create service without cache
	serviceNoCache := services.NewItemServiceImpl(benchItemRepo, benchLinkRepo, nil, nil)

	// Create test item
	item := createBenchItem(benchProjectID)
	if err := benchItemRepo.Create(ctx, item); err != nil {
		b.Fatalf("Failed to create test item: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := serviceNoCache.GetItem(ctx, item.ID)
		if err != nil {
			b.Fatalf("Failed to get item: %v", err)
		}
	}
}

// BenchmarkLegacyGetItem benchmarks item retrieval via repository (legacy)
func BenchmarkLegacyGetItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create test item
	item := createBenchItem(benchProjectID)
	if err := benchItemRepo.Create(ctx, item); err != nil {
		b.Fatalf("Failed to create test item: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := benchItemRepo.GetByID(ctx, item.ID)
		if err != nil {
			b.Fatalf("Failed to get item: %v", err)
		}
	}
}

// ============================================================================
// BENCHMARK: ITEM LIST OPERATIONS
// ============================================================================

// BenchmarkServiceListItemsWithCache benchmarks listing with cache
func BenchmarkServiceListItemsWithCache(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create 100 test items
	for i := 0; i < 100; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
	}

	filter := repository.ItemFilter{
		ProjectID: &benchProjectID,
		Limit:     50,
		Offset:    0,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := benchItemService.ListItems(ctx, filter)
		if err != nil {
			b.Fatalf("Failed to list items: %v", err)
		}
	}
}

// BenchmarkServiceListItemsNoCache benchmarks listing without cache
func BenchmarkServiceListItemsNoCache(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create service without cache
	serviceNoCache := services.NewItemServiceImpl(benchItemRepo, benchLinkRepo, nil, nil)

	// Create 100 test items
	for i := 0; i < 100; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
	}

	filter := repository.ItemFilter{
		ProjectID: &benchProjectID,
		Limit:     50,
		Offset:    0,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := serviceNoCache.ListItems(ctx, filter)
		if err != nil {
			b.Fatalf("Failed to list items: %v", err)
		}
	}
}

// BenchmarkLegacyListItems benchmarks listing via repository (legacy)
func BenchmarkLegacyListItems(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create 100 test items
	for i := 0; i < 100; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
	}

	filter := repository.ItemFilter{
		ProjectID: &benchProjectID,
		Limit:     50,
		Offset:    0,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := benchItemRepo.List(ctx, filter)
		if err != nil {
			b.Fatalf("Failed to list items: %v", err)
		}
	}
}

// ============================================================================
// BENCHMARK: ITEM UPDATE OPERATIONS
// ============================================================================

// BenchmarkServiceUpdateItem benchmarks item update via service layer
func BenchmarkServiceUpdateItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create test item
	item := createBenchItem(benchProjectID)
	if err := benchItemService.CreateItem(ctx, item); err != nil {
		b.Fatalf("Failed to create test item: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		item.Title = fmt.Sprintf("Updated Title %d", i)
		item.Status = "in_progress"
		if err := benchItemService.UpdateItem(ctx, item); err != nil {
			b.Fatalf("Failed to update item: %v", err)
		}
	}
}

// BenchmarkLegacyUpdateItem benchmarks item update via repository (legacy)
func BenchmarkLegacyUpdateItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create test item
	item := createBenchItem(benchProjectID)
	if err := benchItemRepo.Create(ctx, item); err != nil {
		b.Fatalf("Failed to create test item: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		item.Title = fmt.Sprintf("Updated Title %d", i)
		item.Status = "in_progress"
		if err := benchItemRepo.Update(ctx, item); err != nil {
			b.Fatalf("Failed to update item: %v", err)
		}
	}
}

// BenchmarkServiceUpdateBatch benchmarks batch update via service layer
func BenchmarkServiceUpdateBatch(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()
	batchSize := 10

	// Create test items
	items := make([]*models.Item, batchSize)
	for i := 0; i < batchSize; i++ {
		items[i] = createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, items[i]); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for j := 0; j < batchSize; j++ {
			items[j].Title = fmt.Sprintf("Batch Update %d-%d", i, j)
		}
		if err := benchItemService.UpdateBatch(ctx, items); err != nil {
			b.Fatalf("Failed to update batch: %v", err)
		}
	}
}

// ============================================================================
// BENCHMARK: ITEM DELETE OPERATIONS
// ============================================================================

// BenchmarkServiceDeleteItem benchmarks item deletion via service layer
func BenchmarkServiceDeleteItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		b.StopTimer()
		// Create test item
		item := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
		b.StartTimer()

		if err := benchItemService.DeleteItem(ctx, item.ID); err != nil {
			b.Fatalf("Failed to delete item: %v", err)
		}
	}
}

// BenchmarkLegacyDeleteItem benchmarks item deletion via repository (legacy)
func BenchmarkLegacyDeleteItem(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		b.StopTimer()
		// Create test item
		item := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
		b.StartTimer()

		if err := benchItemRepo.Delete(ctx, item.ID); err != nil {
			b.Fatalf("Failed to delete item: %v", err)
		}
	}
}

// ============================================================================
// BENCHMARK: TRANSACTION OPERATIONS
// ============================================================================

// BenchmarkServiceCreateWithTransaction benchmarks item creation in transaction
func BenchmarkServiceCreateWithTransaction(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		err := benchDB.Transaction(func(txDB *gorm.DB) error {
			txCtx := tx.WithTransaction(ctx, txDB)
			item := createBenchItem(benchProjectID)
			return benchItemService.CreateItem(txCtx, item)
		})
		if err != nil {
			b.Fatalf("Failed to create item in transaction: %v", err)
		}
	}
}

// BenchmarkServiceCreateWithoutTransaction benchmarks without transaction
func BenchmarkServiceCreateWithoutTransaction(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemService.CreateItem(ctx, item); err != nil {
			b.Fatalf("Failed to create item: %v", err)
		}
	}
}

// ============================================================================
// BENCHMARK: COMPLEX OPERATIONS
// ============================================================================

// BenchmarkServiceGetWithLinks benchmarks retrieving item with links
func BenchmarkServiceGetWithLinks(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create test item with links
	item := createBenchItem(benchProjectID)
	if err := benchItemRepo.Create(ctx, item); err != nil {
		b.Fatalf("Failed to create test item: %v", err)
	}

	// Create some links
	for i := 0; i < 5; i++ {
		targetItem := createBenchItem(benchProjectID)
		if err := benchItemRepo.Create(ctx, targetItem); err != nil {
			b.Fatalf("Failed to create target item: %v", err)
		}
		link := createBenchLink(item.ID, targetItem.ID)
		if err := benchLinkRepo.Create(ctx, link); err != nil {
			b.Fatalf("Failed to create link: %v", err)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := benchItemService.GetWithLinks(ctx, item.ID)
		if err != nil {
			b.Fatalf("Failed to get item with links: %v", err)
		}
	}
}

// BenchmarkServiceGetItemStats benchmarks statistics calculation
func BenchmarkServiceGetItemStats(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create 50 items with various types and statuses
	types := []string{"requirement", "task", "bug", "feature"}
	statuses := []string{"todo", "in_progress", "done"}

	for i := 0; i < 50; i++ {
		item := createBenchItem(benchProjectID)
		item.Type = types[i%len(types)]
		item.Status = statuses[i%len(statuses)]
		if err := benchItemRepo.Create(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := benchItemService.GetItemStats(ctx, benchProjectID)
		if err != nil {
			b.Fatalf("Failed to get stats: %v", err)
		}
	}
}

// BenchmarkCacheHitRatio measures cache hit performance
func BenchmarkCacheHitRatio(b *testing.B) {
	setupBenchmark(b)
	defer teardownBenchmark(b)

	ctx := context.Background()

	// Create test items
	itemIDs := make([]string, 10)
	for i := 0; i < 10; i++ {
		item := createBenchItem(benchProjectID)
		if err := benchItemService.CreateItem(ctx, item); err != nil {
			b.Fatalf("Failed to create test item: %v", err)
		}
		itemIDs[i] = item.ID
	}

	// Warm up cache
	for _, id := range itemIDs {
		benchItemService.GetItem(ctx, id)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Access items in round-robin fashion
		id := itemIDs[i%len(itemIDs)]
		_, err := benchItemService.GetItem(ctx, id)
		if err != nil {
			b.Fatalf("Failed to get item: %v", err)
		}
	}
}
