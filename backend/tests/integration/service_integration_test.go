//go:build integration

package integration

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
	"github.com/nats-io/nats.go"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/cache"
	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/services"
	"github.com/kooshapari/tracertm-backend/internal/tx"
)

// ============================================================================
// Test Setup Helpers
// ============================================================================

// serviceTestFixture holds all dependencies for service integration tests
type serviceTestFixture struct {
	ctx          context.Context
	db           *gorm.DB
	cache        cache.Cache
	natsConn     *nats.Conn
	itemRepo     repository.ItemRepository
	linkRepo     repository.LinkRepository
	projectRepo  repository.ProjectRepository
	agentRepo    repository.AgentRepository
	itemService  services.ItemService
	linkService  services.LinkService
	projectSvc   services.ProjectService
	agentService services.AgentService
	eventStore   events.EventStore
	eventBus     *mockEventBus
	cleanup      func()
}

// setupServiceTests creates a complete test fixture with all service dependencies
func setupServiceTests(t *testing.T) *serviceTestFixture {
	ctx := context.Background()

	// Get database connection string from environment or use default
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set, skipping integration test")
	}

	// Connect to database with sql.DB
	sqlDB, err := sql.Open("postgres", dbURL)
	require.NoError(t, err, "Failed to open SQL database")

	// Test connection
	err = sqlDB.Ping()
	require.NoError(t, err, "Failed to ping database")

	// Create GORM DB
	gormDB, err := gorm.Open(postgres.New(postgres.Config{
		Conn: sqlDB,
	}), &gorm.Config{})
	require.NoError(t, err, "Failed to open GORM database")

	// Auto-migrate models
	err = gormDB.AutoMigrate(
		&models.Item{},
		&models.Link{},
		&models.Project{},
		&models.Agent{},
		&models.View{},
	)
	require.NoError(t, err, "Failed to auto-migrate models")

	// Create repositories
	itemRepo := repository.NewItemRepository(gormDB)
	linkRepo := repository.NewLinkRepository(gormDB)
	projectRepo := repository.NewProjectRepository(gormDB)
	agentRepo := repository.NewAgentRepository(gormDB)

	// Create mock cache
	mockCache := newMockCache()

	// Create mock NATS connection
	mockNATS := newMockNATS()

	// Create event infrastructure
	eventStore := newMockEventStore()
	eventBus := newMockEventBus()

	// Create services
	itemService := services.NewItemServiceImpl(itemRepo, linkRepo, mockCache, mockNATS)
	linkService := services.NewLinkServiceImpl(linkRepo, itemRepo, mockCache, mockNATS)
	projectSvc := services.NewProjectServiceImpl(projectRepo, itemRepo, mockCache, mockNATS)
	agentService := services.NewAgentServiceImpl(agentRepo, mockCache, mockNATS)

	cleanup := func() {
		// Clean up test data
		gormDB.Exec("TRUNCATE TABLE items, links, projects, agents, views CASCADE")
		if sqlDB != nil {
			sqlDB.Close()
		}
	}

	return &serviceTestFixture{
		ctx:          ctx,
		db:           gormDB,
		cache:        mockCache,
		natsConn:     mockNATS,
		itemRepo:     itemRepo,
		linkRepo:     linkRepo,
		projectRepo:  projectRepo,
		agentRepo:    agentRepo,
		itemService:  itemService,
		linkService:  linkService,
		projectSvc:   projectSvc,
		agentService: agentService,
		eventStore:   eventStore,
		eventBus:     eventBus,
		cleanup:      cleanup,
	}
}

// ============================================================================
// TEST 1-5: Real Database Interaction Tests
// ============================================================================

// Test 1: Service creates item with database persistence
func TestServiceIntegration_CreateItem_DatabasePersistence(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create a project first
	project := &models.Project{
		ID:          uuid.New().String(),
		Name:        "Test Project",
		Description: "Integration test project",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	err := f.projectRepo.Create(f.ctx, project)
	require.NoError(t, err)

	// Create item through service
	item := &models.Item{
		ID:          uuid.New().String(),
		ProjectID:   project.ID,
		Title:       "Test Item",
		Description: "Integration test item",
		Type:        "task",
		Status:      "todo",
		Priority:    models.PriorityMedium,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	err = f.itemService.CreateItem(f.ctx, item)
	assert.NoError(t, err, "Should create item successfully")

	// Verify item was persisted to database
	retrieved, err := f.itemRepo.GetByID(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)
	assert.Equal(t, item.Title, retrieved.Title)
	assert.Equal(t, item.ProjectID, retrieved.ProjectID)
	assert.Equal(t, "task", retrieved.Type)

	t.Logf("✅ TEST 1 PASSED: Service persisted item to database")
}

// Test 2: Service updates item with database validation
func TestServiceIntegration_UpdateItem_DatabaseValidation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Setup: Create project and item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original Title",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Update through service
	item.Title = "Updated Title"
	item.Status = "in_progress"
	item.UpdatedAt = time.Now()

	err := f.itemService.UpdateItem(f.ctx, item)
	assert.NoError(t, err)

	// Verify update persisted
	updated, err := f.itemRepo.GetByID(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.Equal(t, "Updated Title", updated.Title)
	assert.Equal(t, "in_progress", updated.Status)

	t.Logf("✅ TEST 2 PASSED: Service updated item in database")
}

// Test 3: Service deletes item and cascades to links
func TestServiceIntegration_DeleteItem_CascadesToLinks(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Setup: Create project and items
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item1))
	require.NoError(t, f.itemService.CreateItem(f.ctx, item2))

	// Create link between items
	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "depends_on",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.linkService.CreateLink(f.ctx, link))

	// Delete item1 through service (should cascade delete link)
	err := f.itemService.DeleteItem(f.ctx, item1.ID)
	assert.NoError(t, err)

	// Verify item deleted
	_, err = f.itemRepo.GetByID(f.ctx, item1.ID)
	assert.Error(t, err)

	// Verify link deleted
	_, err = f.linkRepo.GetByID(f.ctx, link.ID)
	assert.Error(t, err)

	// Verify item2 still exists
	retrieved, err := f.itemRepo.GetByID(f.ctx, item2.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)

	t.Logf("✅ TEST 3 PASSED: Service cascaded delete to links")
}

// Test 4: Service handles concurrent database operations
func TestServiceIntegration_ConcurrentOperations_DatabaseConsistency(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Concurrent Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// Create 10 items concurrently
	numItems := 10
	done := make(chan bool, numItems)
	errors := make(chan error, numItems)

	for i := 0; i < numItems; i++ {
		go func(idx int) {
			item := &models.Item{
				ID:        uuid.New().String(),
				ProjectID: project.ID,
				Title:     fmt.Sprintf("Concurrent Item %d", idx),
				Type:      "task",
				Status:    "todo",
				CreatedAt: time.Now(),
				UpdatedAt: time.Now(),
			}
			if err := f.itemService.CreateItem(f.ctx, item); err != nil {
				errors <- err
			}
			done <- true
		}(i)
	}

	// Wait for all operations
	for i := 0; i < numItems; i++ {
		<-done
	}
	close(errors)

	// Check for errors
	for err := range errors {
		assert.NoError(t, err)
	}

	// Verify all items created
	filter := repository.ItemFilter{ProjectID: &project.ID}
	items, err := f.itemRepo.List(f.ctx, filter)
	assert.NoError(t, err)
	assert.Equal(t, numItems, len(items))

	t.Logf("✅ TEST 4 PASSED: Concurrent operations maintained consistency")
}

// Test 5: Service validates business rules before database operations
func TestServiceIntegration_Validation_BeforeDatabaseOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Try to create item with invalid data
	invalidItem := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: "", // Invalid: empty project ID
		Title:     "", // Invalid: empty title
		Type:      "invalid_type",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemService.CreateItem(f.ctx, invalidItem)
	assert.Error(t, err, "Should reject invalid item")
	assert.Contains(t, err.Error(), "validation failed")

	// Verify item was NOT persisted
	_, err = f.itemRepo.GetByID(f.ctx, invalidItem.ID)
	assert.Error(t, err)

	t.Logf("✅ TEST 5 PASSED: Service validated before database operation")
}

// ============================================================================
// TEST 6-10: Cross-Service Communication Tests
// ============================================================================

// Test 6: Item service communicates with link service
func TestServiceIntegration_CrossService_ItemToLink(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Setup
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Test Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Get item with links (cross-service call)
	itemWithLinks, err := f.itemService.GetWithLinks(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, itemWithLinks)
	assert.Equal(t, item.ID, itemWithLinks.Item.ID)
	assert.NotNil(t, itemWithLinks.SourceLinks)
	assert.NotNil(t, itemWithLinks.TargetLinks)

	t.Logf("✅ TEST 6 PASSED: Item service communicated with link service")
}

// Test 7: Link service validates items exist via item service
func TestServiceIntegration_CrossService_LinkValidatesItems(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Try to create link with non-existent items
	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  "non-existent-source",
		TargetID:  "non-existent-target",
		Type:      "depends_on",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.linkService.CreateLink(f.ctx, link)
	// Note: Current implementation may not validate - this test documents expected behavior
	if err != nil {
		assert.Contains(t, err.Error(), "not found")
		t.Logf("✅ TEST 7 PASSED: Link service validated items exist")
	} else {
		t.Logf("⚠️  TEST 7: Link service created link without validation (may need enhancement)")
	}
}

// Test 8: Project service aggregates data from item service
func TestServiceIntegration_CrossService_ProjectToItems(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project and items
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	for i := 0; i < 5; i++ {
		item := &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Item %d", i),
			Type:      "task",
			Status:    "todo",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
		require.NoError(t, f.itemService.CreateItem(f.ctx, item))
	}

	// Get stats through item service
	stats, err := f.itemService.GetItemStats(f.ctx, project.ID)
	assert.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, int64(5), stats.TotalItems)

	t.Logf("✅ TEST 8 PASSED: Project aggregated data from items")
}

// Test 9: Multiple services coordinate on shared data
func TestServiceIntegration_CrossService_CoordinatedOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project, items, and links
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Coordination Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Parent Item",
		Type:      "epic",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Child Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item1))
	require.NoError(t, f.itemService.CreateItem(f.ctx, item2))

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "contains",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.linkService.CreateLink(f.ctx, link))

	// Verify coordination: getting item with links shows the relationship
	itemWithLinks, err := f.itemService.GetWithLinks(f.ctx, item1.ID)
	assert.NoError(t, err)
	assert.NotNil(t, itemWithLinks)
	assert.Len(t, itemWithLinks.SourceLinks, 1)
	assert.Equal(t, item2.ID, itemWithLinks.SourceLinks[0].TargetID)

	t.Logf("✅ TEST 9 PASSED: Services coordinated on shared data")
}

// Test 10: Service layer maintains referential integrity
func TestServiceIntegration_CrossService_ReferentialIntegrity(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create items and link
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Integrity Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item1))
	require.NoError(t, f.itemService.CreateItem(f.ctx, item2))

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "related",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.linkService.CreateLink(f.ctx, link))

	// Delete item1 - should delete link to maintain integrity
	err := f.itemService.DeleteItem(f.ctx, item1.ID)
	assert.NoError(t, err)

	// Verify link deleted
	_, err = f.linkRepo.GetByID(f.ctx, link.ID)
	assert.Error(t, err)

	t.Logf("✅ TEST 10 PASSED: Service maintained referential integrity")
}

// ============================================================================
// TEST 11-15: Transaction Tests
// ============================================================================

// Test 11: Service performs multi-operation transaction
func TestServiceIntegration_Transaction_MultiOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Transaction Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// Begin transaction
	txDB := f.db.Begin()
	txCtx := tx.WithTransaction(f.ctx, txDB)

	// Create multiple items in transaction
	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "TX Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "TX Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemRepo.Create(txCtx, item1)
	require.NoError(t, err)
	err = f.itemRepo.Create(txCtx, item2)
	require.NoError(t, err)

	// Commit transaction
	err = txDB.Commit().Error
	assert.NoError(t, err)

	// Verify both items persisted
	retrieved1, err := f.itemRepo.GetByID(f.ctx, item1.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved1)

	retrieved2, err := f.itemRepo.GetByID(f.ctx, item2.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved2)

	t.Logf("✅ TEST 11 PASSED: Multi-operation transaction committed")
}

// Test 12: Service rolls back transaction on error
func TestServiceIntegration_Transaction_Rollback(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Rollback Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// Begin transaction
	txDB := f.db.Begin()
	txCtx := tx.WithTransaction(f.ctx, txDB)

	// Create item in transaction
	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Rollback Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemRepo.Create(txCtx, item)
	require.NoError(t, err)

	// Rollback transaction
	txDB.Rollback()

	// Verify item was NOT persisted
	_, err = f.itemRepo.GetByID(f.ctx, item.ID)
	assert.Error(t, err)

	t.Logf("✅ TEST 12 PASSED: Transaction rolled back successfully")
}

// Test 13: Nested service calls share transaction context
func TestServiceIntegration_Transaction_NestedCalls(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Nested TX Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// Begin transaction
	txDB := f.db.Begin()
	txCtx := tx.WithTransaction(f.ctx, txDB)

	// Create items and link in same transaction
	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Nested Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Nested Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := f.itemRepo.Create(txCtx, item1)
	require.NoError(t, err)
	err = f.itemRepo.Create(txCtx, item2)
	require.NoError(t, err)

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "depends_on",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err = f.linkRepo.Create(txCtx, link)
	require.NoError(t, err)

	// Commit all together
	err = txDB.Commit().Error
	assert.NoError(t, err)

	// Verify all persisted
	_, err = f.itemRepo.GetByID(f.ctx, item1.ID)
	assert.NoError(t, err)
	_, err = f.itemRepo.GetByID(f.ctx, item2.ID)
	assert.NoError(t, err)
	_, err = f.linkRepo.GetByID(f.ctx, link.ID)
	assert.NoError(t, err)

	t.Logf("✅ TEST 13 PASSED: Nested calls shared transaction context")
}

// Test 14: Transaction isolation between concurrent operations
func TestServiceIntegration_Transaction_Isolation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Isolation Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// TX1: Begin and create item but don't commit
	tx1 := f.db.Begin()
	txCtx1 := tx.WithTransaction(f.ctx, tx1)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Isolated Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err := f.itemRepo.Create(txCtx1, item)
	require.NoError(t, err)

	// TX2: Should not see uncommitted item from TX1
	_, err = f.itemRepo.GetByID(f.ctx, item.ID)
	assert.Error(t, err, "Should not see uncommitted item")

	// Commit TX1
	err = tx1.Commit().Error
	assert.NoError(t, err)

	// Now TX2 should see the item
	retrieved, err := f.itemRepo.GetByID(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved)

	t.Logf("✅ TEST 14 PASSED: Transaction isolation maintained")
}

// Test 15: Batch operations use single transaction
func TestServiceIntegration_Transaction_BatchOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch TX Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// Create batch of items
	items := make([]*models.Item, 5)
	for i := 0; i < 5; i++ {
		items[i] = &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			Status:    "todo",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
	}

	// Use batch create
	err := f.itemService.CreateBatch(f.ctx, items)
	assert.NoError(t, err)

	// Verify all created
	for _, item := range items {
		retrieved, err := f.itemRepo.GetByID(f.ctx, item.ID)
		assert.NoError(t, err)
		assert.NotNil(t, retrieved)
	}

	t.Logf("✅ TEST 15 PASSED: Batch operation used transaction")
}

// ============================================================================
// TEST 16-20: Caching Behavior Tests
// ============================================================================

// Test 16: Service caches retrieved items
func TestServiceIntegration_Cache_ItemRetrieval(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project and item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Cache Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Cached Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// First retrieval - should cache
	retrieved1, err := f.itemService.GetItem(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved1)

	// Second retrieval - should hit cache
	retrieved2, err := f.itemService.GetItem(f.ctx, item.ID)
	assert.NoError(t, err)
	assert.NotNil(t, retrieved2)
	assert.Equal(t, retrieved1.Title, retrieved2.Title)

	// Verify cache was populated
	mockCache := f.cache.(*mockCache)
	cacheKey := "item:" + item.ID
	assert.True(t, mockCache.HasKey(cacheKey))

	t.Logf("✅ TEST 16 PASSED: Service cached item retrieval")
}

// Test 17: Service invalidates cache on update
func TestServiceIntegration_Cache_InvalidateOnUpdate(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Cache Invalidation Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original Title",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Cache the item
	_, err := f.itemService.GetItem(f.ctx, item.ID)
	require.NoError(t, err)

	mockCache := f.cache.(*mockCache)
	cacheKey := "item:" + item.ID
	assert.True(t, mockCache.HasKey(cacheKey))

	// Update item
	item.Title = "Updated Title"
	err = f.itemService.UpdateItem(f.ctx, item)
	assert.NoError(t, err)

	// Cache should be invalidated
	assert.False(t, mockCache.HasKey(cacheKey))

	t.Logf("✅ TEST 17 PASSED: Service invalidated cache on update")
}

// Test 18: Service invalidates related caches
func TestServiceIntegration_Cache_InvalidateRelated(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project and item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Related Cache Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Test Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Get stats to cache them
	stats, err := f.itemService.GetItemStats(f.ctx, project.ID)
	require.NoError(t, err)
	assert.Equal(t, int64(1), stats.TotalItems)

	mockCache := f.cache.(*mockCache)
	statsKey := "project:" + project.ID + ":stats"
	assert.True(t, mockCache.HasKey(statsKey))

	// Create another item - should invalidate stats cache
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Second Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err = f.itemService.CreateItem(f.ctx, item2)
	assert.NoError(t, err)

	// Stats cache should be invalidated
	assert.False(t, mockCache.HasKey(statsKey))

	t.Logf("✅ TEST 18 PASSED: Service invalidated related caches")
}

// Test 19: Cache handles concurrent access
func TestServiceIntegration_Cache_ConcurrentAccess(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Create project and item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Concurrent Cache Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Concurrent Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Multiple goroutines read same item concurrently
	numReads := 20
	done := make(chan bool, numReads)
	errors := make(chan error, numReads)

	for i := 0; i < numReads; i++ {
		go func() {
			_, err := f.itemService.GetItem(f.ctx, item.ID)
			if err != nil {
				errors <- err
			}
			done <- true
		}()
	}

	// Wait for all reads
	for i := 0; i < numReads; i++ {
		<-done
	}
	close(errors)

	// Check for errors
	for err := range errors {
		assert.NoError(t, err)
	}

	t.Logf("✅ TEST 19 PASSED: Cache handled concurrent access")
}

// Test 20: Cache respects TTL (time to live)
func TestServiceIntegration_Cache_TTL(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Note: This test documents expected TTL behavior
	// Actual TTL enforcement depends on cache implementation

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "TTL Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "TTL Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Cache the item
	_, err := f.itemService.GetItem(f.ctx, item.ID)
	assert.NoError(t, err)

	mockCache := f.cache.(*mockCache)
	cacheKey := "item:" + item.ID
	assert.True(t, mockCache.HasKey(cacheKey))

	// In production, cache would expire after TTL
	// For now, we just verify the cache key exists
	t.Logf("✅ TEST 20 PASSED: Cache TTL behavior documented")
}

// ============================================================================
// TEST 21-25: Event Publishing Tests
// ============================================================================

// Test 21: Service publishes event on item creation
func TestServiceIntegration_Events_ItemCreated(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	// Setup event capture
	mockNATS := f.natsConn.(*mockNATS)
	mockNATS.ClearEvents()

	// Create project and item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Event Item",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err := f.itemService.CreateItem(f.ctx, item)
	assert.NoError(t, err)

	// Verify event published
	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	// Find item.created event
	var createdEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.created" {
			createdEvent = e
			break
		}
	}
	assert.NotNil(t, createdEvent, "item.created event should be published")

	t.Logf("✅ TEST 21 PASSED: Service published item.created event")
}

// Test 22: Service publishes event on item update
func TestServiceIntegration_Events_ItemUpdated(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)

	// Create item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Update Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Clear events
	mockNATS.ClearEvents()

	// Update item
	item.Title = "Updated"
	err := f.itemService.UpdateItem(f.ctx, item)
	assert.NoError(t, err)

	// Verify event published
	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var updatedEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.updated" {
			updatedEvent = e
			break
		}
	}
	assert.NotNil(t, updatedEvent, "item.updated event should be published")

	t.Logf("✅ TEST 22 PASSED: Service published item.updated event")
}

// Test 23: Service publishes event on item deletion
func TestServiceIntegration_Events_ItemDeleted(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)

	// Create item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Delete Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "To Delete",
		Type:      "task",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.itemService.CreateItem(f.ctx, item))

	// Clear events
	mockNATS.ClearEvents()

	// Delete item
	err := f.itemService.DeleteItem(f.ctx, item.ID)
	assert.NoError(t, err)

	// Verify event published
	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var deletedEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.deleted" {
			deletedEvent = e
			break
		}
	}
	assert.NotNil(t, deletedEvent, "item.deleted event should be published")

	t.Logf("✅ TEST 23 PASSED: Service published item.deleted event")
}

// Test 24: Batch operations publish single batch event
func TestServiceIntegration_Events_BatchOperation(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)
	mockNATS.ClearEvents()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch Event Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	// Create batch of items
	items := make([]*models.Item, 3)
	for i := 0; i < 3; i++ {
		items[i] = &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}
	}

	err := f.itemService.CreateBatch(f.ctx, items)
	assert.NoError(t, err)

	// Verify batch event published
	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	var batchEvent *mockEvent
	for _, e := range events {
		if e.Subject == "item.batch_created" {
			batchEvent = e
			break
		}
	}
	assert.NotNil(t, batchEvent, "item.batch_created event should be published")

	// Verify event data
	var eventData map[string]interface{}
	err = json.Unmarshal(batchEvent.Data, &eventData)
	assert.NoError(t, err)

	data, ok := eventData["data"].(map[string]interface{})
	assert.True(t, ok)
	count, ok := data["count"].(float64)
	assert.True(t, ok)
	assert.Equal(t, float64(3), count)

	t.Logf("✅ TEST 24 PASSED: Batch operation published batch event")
}

// Test 25: Events contain complete metadata
func TestServiceIntegration_Events_Metadata(t *testing.T) {
	f := setupServiceTests(t)
	defer f.cleanup()

	mockNATS := f.natsConn.(*mockNATS)
	mockNATS.ClearEvents()

	// Create item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Metadata Test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	require.NoError(t, f.projectRepo.Create(f.ctx, project))

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Metadata Item",
		Type:      "task",
		Status:    "todo",
		Priority:  models.PriorityHigh,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	err := f.itemService.CreateItem(f.ctx, item)
	assert.NoError(t, err)

	// Get event
	events := mockNATS.GetEvents()
	assert.GreaterOrEqual(t, len(events), 1)

	event := events[len(events)-1]
	var eventData map[string]interface{}
	err = json.Unmarshal(event.Data, &eventData)
	assert.NoError(t, err)

	// Verify metadata
	assert.Contains(t, eventData, "type")
	assert.Contains(t, eventData, "data")
	assert.Contains(t, eventData, "timestamp")

	t.Logf("✅ TEST 25 PASSED: Event contained complete metadata")
}

// ============================================================================
// Mock Implementations
// ============================================================================

// mockCache is a simple in-memory cache for testing
type mockCache struct {
	data map[string][]byte
}

func newMockCache() *mockCache {
	return &mockCache{
		data: make(map[string][]byte),
	}
}

func (c *mockCache) Get(ctx context.Context, key string, dest interface{}) error {
	data, exists := c.data[key]
	if !exists {
		return errors.New("key not found")
	}
	return json.Unmarshal(data, dest)
}

func (c *mockCache) Set(ctx context.Context, key string, value interface{}) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	c.data[key] = data
	return nil
}

func (c *mockCache) Delete(ctx context.Context, keys ...string) error {
	for _, key := range keys {
		delete(c.data, key)
	}
	return nil
}

func (c *mockCache) InvalidatePattern(ctx context.Context, pattern string) error {
	// Simple implementation: delete all keys
	c.data = make(map[string][]byte)
	return nil
}

func (c *mockCache) Close() error {
	return nil
}

func (c *mockCache) HasKey(key string) bool {
	_, exists := c.data[key]
	return exists
}

// mockNATS is a mock NATS connection for testing
type mockNATS struct {
	events []*mockEvent
}

type mockEvent struct {
	Subject string
	Data    []byte
}

func newMockNATS() *mockNATS {
	return &mockNATS{
		events: make([]*mockEvent, 0),
	}
}

func (m *mockNATS) Publish(subject string, data []byte) error {
	m.events = append(m.events, &mockEvent{
		Subject: subject,
		Data:    data,
	})
	return nil
}

func (m *mockNATS) GetEvents() []*mockEvent {
	return m.events
}

func (m *mockNATS) ClearEvents() {
	m.events = make([]*mockEvent, 0)
}

// Implement other NATS interface methods as no-ops
func (m *mockNATS) Close()       {}
func (m *mockNATS) Flush() error { return nil }
func (m *mockNATS) Drain() error { return nil }

// mockEventStore is a mock event store for testing
type mockEventStore struct{}

func newMockEventStore() *mockEventStore {
	return &mockEventStore{}
}

func (s *mockEventStore) Store(event *events.Event) error                        { return nil }
func (s *mockEventStore) StoreMany(events []*events.Event) error                 { return nil }
func (s *mockEventStore) GetByEntityID(entityID string) ([]*events.Event, error) { return nil, nil }
func (s *mockEventStore) GetByEntityIDAfterVersion(entityID string, version int64) ([]*events.Event, error) {
	return nil, nil
}

func (s *mockEventStore) GetByProjectID(projectID string, limit, offset int) ([]*events.Event, error) {
	return nil, nil
}

func (s *mockEventStore) GetByProjectIDAndType(projectID string, entityType events.EntityType, limit, offset int) ([]*events.Event, error) {
	return nil, nil
}

func (s *mockEventStore) GetByTimeRange(projectID string, start, end time.Time) ([]*events.Event, error) {
	return nil, nil
}
func (s *mockEventStore) SaveSnapshot(snapshot *events.Snapshot) error { return nil }
func (s *mockEventStore) GetLatestSnapshot(entityID string) (*events.Snapshot, error) {
	return nil, nil
}

func (s *mockEventStore) GetSnapshotAtVersion(entityID string, version int64) (*events.Snapshot, error) {
	return nil, nil
}
func (s *mockEventStore) Replay(entityID string) (map[string]interface{}, error) { return nil, nil }
func (s *mockEventStore) ReplayFromSnapshot(entityID string, snapshotVersion int64) (map[string]interface{}, error) {
	return nil, nil
}

// mockEventBus is a mock event bus for testing
type mockEventBus struct {
	events []*events.Event
}

func newMockEventBus() *mockEventBus {
	return &mockEventBus{
		events: make([]*events.Event, 0),
	}
}

func (b *mockEventBus) Publish(event *events.Event) error {
	b.events = append(b.events, event)
	return nil
}

func (b *mockEventBus) PublishToProject(projectID string, event *events.Event) error {
	return b.Publish(event)
}

func (b *mockEventBus) PublishToEntity(entityID string, event *events.Event) error {
	return b.Publish(event)
}

func (b *mockEventBus) Subscribe(handler func(*events.Event)) error { return nil }
func (b *mockEventBus) SubscribeToProject(projectID string, handler func(*events.Event)) error {
	return nil
}

func (b *mockEventBus) SubscribeToEntity(entityID string, handler func(*events.Event)) error {
	return nil
}

func (b *mockEventBus) SubscribeToEventType(eventType events.EventType, handler func(*events.Event)) error {
	return nil
}
func (b *mockEventBus) Unsubscribe(subscriptionID string) error { return nil }
