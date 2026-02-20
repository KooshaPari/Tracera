//go:build integration

package integration

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/kooshapari/tracertm-backend/internal/agents"
	"github.com/kooshapari/tracertm-backend/internal/models"
	"github.com/kooshapari/tracertm-backend/internal/repository"
	"github.com/kooshapari/tracertm-backend/internal/search"
	"github.com/kooshapari/tracertm-backend/internal/storage"
)

// crossPackageFixture holds dependencies for cross-package integration tests
type crossPackageFixture struct {
	ctx           context.Context
	db            *gorm.DB
	coordinator   *agents.Coordinator
	searchEngine  *search.Engine
	storageClient *storage.Client
	itemRepo      repository.ItemRepository
	cleanup       func()
}

func setupCrossPackageTests(t *testing.T) *crossPackageFixture {
	ctx := context.Background()

	// Database setup
	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	db, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})
	require.NoError(t, err)

	// Auto-migrate models
	err = db.AutoMigrate(&models.Item{}, &models.Project{}, &models.Agent{})
	require.NoError(t, err)

	// Initialize components
	coordinator := agents.NewCoordinator(db)
	searchEngine := search.NewEngine(db)
	storageClient := storage.NewClient()
	itemRepo := repository.NewItemRepository(db)

	cleanup := func() {
		db.Exec("TRUNCATE TABLE items, projects, agents CASCADE")
	}

	return &crossPackageFixture{
		ctx:           ctx,
		db:            db,
		coordinator:   coordinator,
		searchEngine:  searchEngine,
		storageClient: storageClient,
		itemRepo:      itemRepo,
		cleanup:       cleanup,
	}
}

// TEST 1-10: Agent ↔ Storage Integration

func TestCrossPackage_AgentPersistsToStorage(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	taskData := map[string]interface{}{
		"task_id":     uuid.New().String(),
		"description": "Test agent task",
	}

	// Agent creates task and stores result
	err := f.coordinator.ExecuteAndStore(f.ctx, agentID, taskData, f.storageClient)
	assert.NoError(t, err)

	// Verify storage contains result
	stored, err := f.storageClient.Get(f.ctx, agentID)
	assert.NoError(t, err)
	assert.NotNil(t, stored)
}

func TestCrossPackage_AgentRetrievesFromStorage(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	stateData := map[string]interface{}{
		"status":   "running",
		"progress": 50,
	}

	// Store agent state
	err := f.storageClient.Put(f.ctx, agentID, stateData)
	require.NoError(t, err)

	// Agent retrieves state
	state, err := f.coordinator.LoadState(f.ctx, agentID, f.storageClient)
	assert.NoError(t, err)
	assert.Equal(t, "running", state["status"])
}

func TestCrossPackage_AgentUpdatesStoredState(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	initialState := map[string]interface{}{"progress": 0}
	err := f.storageClient.Put(f.ctx, agentID, initialState)
	require.NoError(t, err)

	// Agent updates progress
	for i := 1; i <= 5; i++ {
		err = f.coordinator.UpdateProgress(f.ctx, agentID, i*20, f.storageClient)
		assert.NoError(t, err)
	}

	// Verify final state
	finalState, err := f.storageClient.Get(f.ctx, agentID)
	assert.NoError(t, err)
	assert.Equal(t, 100, finalState["progress"])
}

func TestCrossPackage_MultipleAgentsShareStorage(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agents := []string{
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
	}

	// Each agent stores data
	for i, agentID := range agents {
		data := map[string]interface{}{
			"agent_id": agentID,
			"task_num": i,
		}
		err := f.coordinator.ExecuteAndStore(f.ctx, agentID, data, f.storageClient)
		assert.NoError(t, err)
	}

	// Verify all agents' data stored
	for _, agentID := range agents {
		stored, err := f.storageClient.Get(f.ctx, agentID)
		assert.NoError(t, err)
		assert.Equal(t, agentID, stored["agent_id"])
	}
}

func TestCrossPackage_AgentStorageLargePayload(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	largeData := make(map[string]interface{})
	for i := 0; i < 1000; i++ {
		largeData[fmt.Sprintf("key_%d", i)] = fmt.Sprintf("value_%d", i)
	}

	err := f.coordinator.ExecuteAndStore(f.ctx, agentID, largeData, f.storageClient)
	assert.NoError(t, err)

	retrieved, err := f.storageClient.Get(f.ctx, agentID)
	assert.NoError(t, err)
	assert.Equal(t, 1000, len(retrieved))
}

// TEST 11-20: Agent ↔ Search Integration

func TestCrossPackage_AgentIndexesSearchableContent(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	content := map[string]interface{}{
		"title":       "Integration Test Document",
		"description": "This is searchable content created by agent",
		"tags":        []string{"test", "integration", "agent"},
	}

	// Agent creates and indexes content
	err := f.coordinator.CreateAndIndex(f.ctx, agentID, content, f.searchEngine)
	assert.NoError(t, err)

	// Search for indexed content
	results, err := f.searchEngine.Search(f.ctx, "Integration Test")
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
}

func TestCrossPackage_AgentSearchesExistingContent(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Pre-index documents
	docs := []map[string]interface{}{
		{"id": "1", "title": "Alpha Document", "content": "First test"},
		{"id": "2", "title": "Beta Document", "content": "Second test"},
		{"id": "3", "title": "Gamma Document", "content": "Third test"},
	}
	for _, doc := range docs {
		err := f.searchEngine.Index(f.ctx, doc)
		require.NoError(t, err)
	}

	// Agent searches
	agentID := uuid.New().String()
	results, err := f.coordinator.SearchWithEngine(f.ctx, agentID, "Beta", f.searchEngine)
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
	assert.Contains(t, results[0]["title"], "Beta")
}

func TestCrossPackage_AgentUpdatesSearchIndex(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	docID := uuid.New().String()
	doc := map[string]interface{}{
		"id":      docID,
		"title":   "Original Title",
		"content": "Original content",
	}
	err := f.searchEngine.Index(f.ctx, doc)
	require.NoError(t, err)

	// Agent updates document
	updatedDoc := map[string]interface{}{
		"id":      docID,
		"title":   "Updated Title",
		"content": "Updated content",
	}
	agentID := uuid.New().String()
	err = f.coordinator.UpdateAndReindex(f.ctx, agentID, updatedDoc, f.searchEngine)
	assert.NoError(t, err)

	// Search for updated content
	results, err := f.searchEngine.Search(f.ctx, "Updated Title")
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
}

func TestCrossPackage_AgentDeletesFromSearchIndex(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	docID := uuid.New().String()
	doc := map[string]interface{}{
		"id":      docID,
		"title":   "To Delete",
		"content": "Will be removed",
	}
	err := f.searchEngine.Index(f.ctx, doc)
	require.NoError(t, err)

	// Agent deletes document
	agentID := uuid.New().String()
	err = f.coordinator.DeleteAndDeindex(f.ctx, agentID, docID, f.searchEngine)
	assert.NoError(t, err)

	// Search should not find deleted document
	results, err := f.searchEngine.Search(f.ctx, "To Delete")
	assert.NoError(t, err)
	assert.Equal(t, 0, len(results))
}

func TestCrossPackage_AgentFacetedSearch(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Index documents with facets
	docs := []map[string]interface{}{
		{"id": "1", "title": "Doc 1", "category": "alpha", "priority": "high"},
		{"id": "2", "title": "Doc 2", "category": "beta", "priority": "low"},
		{"id": "3", "title": "Doc 3", "category": "alpha", "priority": "high"},
	}
	for _, doc := range docs {
		err := f.searchEngine.Index(f.ctx, doc)
		require.NoError(t, err)
	}

	// Agent performs faceted search
	agentID := uuid.New().String()
	facets := map[string]interface{}{
		"category": "alpha",
		"priority": "high",
	}
	results, err := f.coordinator.FacetedSearch(f.ctx, agentID, facets, f.searchEngine)
	assert.NoError(t, err)
	assert.Equal(t, 2, len(results))
}

// TEST 21-30: Search ↔ Storage Integration

func TestCrossPackage_SearchIndexFromStorage(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Store documents in storage
	docID := uuid.New().String()
	doc := map[string]interface{}{
		"id":      docID,
		"title":   "Stored Document",
		"content": "Content from storage",
	}
	err := f.storageClient.Put(f.ctx, docID, doc)
	require.NoError(t, err)

	// Index from storage
	err = f.searchEngine.IndexFromStorage(f.ctx, docID, f.storageClient)
	assert.NoError(t, err)

	// Search for document
	results, err := f.searchEngine.Search(f.ctx, "Stored Document")
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
}

func TestCrossPackage_SearchResultsLoadFromStorage(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Store and index multiple documents
	docIDs := []string{
		uuid.New().String(),
		uuid.New().String(),
		uuid.New().String(),
	}

	for i, docID := range docIDs {
		doc := map[string]interface{}{
			"id":      docID,
			"title":   fmt.Sprintf("Document %d", i),
			"content": "Searchable content",
		}
		err := f.storageClient.Put(f.ctx, docID, doc)
		require.NoError(t, err)
		err = f.searchEngine.Index(f.ctx, doc)
		require.NoError(t, err)
	}

	// Search and load full docs from storage
	results, err := f.searchEngine.SearchWithStorage(f.ctx, "Searchable", f.storageClient)
	assert.NoError(t, err)
	assert.Equal(t, 3, len(results))
	for _, result := range results {
		assert.Contains(t, result, "content")
	}
}

func TestCrossPackage_BulkIndexFromStorage(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Store multiple documents
	docIDs := make([]string, 100)
	for i := 0; i < 100; i++ {
		docID := uuid.New().String()
		docIDs[i] = docID
		doc := map[string]interface{}{
			"id":      docID,
			"title":   fmt.Sprintf("Bulk Doc %d", i),
			"content": "Bulk indexing test",
		}
		err := f.storageClient.Put(f.ctx, docID, doc)
		require.NoError(t, err)
	}

	// Bulk index from storage
	err := f.searchEngine.BulkIndexFromStorage(f.ctx, docIDs, f.storageClient)
	assert.NoError(t, err)

	// Verify all indexed
	results, err := f.searchEngine.Search(f.ctx, "Bulk indexing")
	assert.NoError(t, err)
	assert.Equal(t, 100, len(results))
}

func TestCrossPackage_StorageBackedSearchCache(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	query := "cached query"
	cacheKey := "search:cache:" + query

	// First search - cache miss
	results1, err := f.searchEngine.SearchWithCache(f.ctx, query, f.storageClient)
	assert.NoError(t, err)

	// Verify cached in storage
	cached, err := f.storageClient.Get(f.ctx, cacheKey)
	assert.NoError(t, err)
	assert.NotNil(t, cached)

	// Second search - cache hit
	results2, err := f.searchEngine.SearchWithCache(f.ctx, query, f.storageClient)
	assert.NoError(t, err)
	assert.Equal(t, results1, results2)
}

func TestCrossPackage_SearchIndexInvalidatesStorageCache(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	docID := uuid.New().String()
	doc := map[string]interface{}{
		"id":      docID,
		"title":   "Test Document",
		"content": "Test content",
	}

	// Store and cache
	err := f.storageClient.Put(f.ctx, docID, doc)
	require.NoError(t, err)
	_, err = f.storageClient.Get(f.ctx, docID) // Cache read
	require.NoError(t, err)

	// Index document - should invalidate storage cache
	err = f.searchEngine.IndexAndInvalidateCache(f.ctx, doc, f.storageClient)
	assert.NoError(t, err)

	// Verify cache invalidated
	cacheKey := "doc:cache:" + docID
	_, err = f.storageClient.Get(f.ctx, cacheKey)
	assert.Error(t, err) // Cache miss
}

// TEST 31-40: Agent ↔ Database Integration

func TestCrossPackage_AgentQueriesDatabase(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Create items in database
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Test Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	for i := 0; i < 5; i++ {
		item := &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
		}
		err = f.db.Create(item).Error
		require.NoError(t, err)
	}

	// Agent queries items
	agentID := uuid.New().String()
	items, err := f.coordinator.QueryItems(f.ctx, agentID, project.ID, f.db)
	assert.NoError(t, err)
	assert.Equal(t, 5, len(items))
}

func TestCrossPackage_AgentCreatesWithTransaction(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "TX Project",
		CreatedAt: time.Now(),
	}

	items := []*models.Item{
		{ID: uuid.New().String(), ProjectID: project.ID, Title: "Item 1", Type: "task", CreatedAt: time.Now()},
		{ID: uuid.New().String(), ProjectID: project.ID, Title: "Item 2", Type: "task", CreatedAt: time.Now()},
	}

	// Agent creates project and items in transaction
	err := f.coordinator.CreateWithTransaction(f.ctx, agentID, project, items, f.db)
	assert.NoError(t, err)

	// Verify all created
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(2), count)
}

func TestCrossPackage_AgentTransactionRollback(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Rollback Project",
		CreatedAt: time.Now(),
	}

	// Simulate transaction failure
	err := f.coordinator.CreateWithFailure(f.ctx, agentID, project, f.db)
	assert.Error(t, err)

	// Verify nothing created
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestCrossPackage_AgentBatchInsert(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// Agent creates 100 items in batch
	agentID := uuid.New().String()
	items := make([]*models.Item, 100)
	for i := 0; i < 100; i++ {
		items[i] = &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
		}
	}

	err = f.coordinator.BatchInsert(f.ctx, agentID, items, f.db)
	assert.NoError(t, err)

	// Verify count
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(100), count)
}

func TestCrossPackage_AgentComplexQuery(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	// Setup test data
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Complex Query Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// Create items with different statuses
	statuses := []string{"todo", "in_progress", "done"}
	for _, status := range statuses {
		for i := 0; i < 3; i++ {
			item := &models.Item{
				ID:        uuid.New().String(),
				ProjectID: project.ID,
				Title:     fmt.Sprintf("%s Item %d", status, i),
				Type:      "task",
				Status:    status,
				CreatedAt: time.Now(),
			}
			err = f.db.Create(item).Error
			require.NoError(t, err)
		}
	}

	// Agent performs complex query
	agentID := uuid.New().String()
	filter := map[string]interface{}{
		"project_id": project.ID,
		"status":     []string{"todo", "in_progress"},
	}
	results, err := f.coordinator.ComplexQuery(f.ctx, agentID, filter, f.db)
	assert.NoError(t, err)
	assert.Equal(t, 6, len(results)) // 3 todo + 3 in_progress
}

// TEST 41-50: End-to-End Workflows

func TestCrossPackage_FullWorkflow_CreateSearchUpdate(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Workflow Project",
		CreatedAt: time.Now(),
	}

	// Step 1: Agent creates project in DB
	err := f.coordinator.CreateProject(f.ctx, agentID, project, f.db)
	assert.NoError(t, err)

	// Step 2: Agent stores project in storage
	err = f.coordinator.StoreProject(f.ctx, agentID, project, f.storageClient)
	assert.NoError(t, err)

	// Step 3: Agent indexes project in search
	err = f.coordinator.IndexProject(f.ctx, agentID, project, f.searchEngine)
	assert.NoError(t, err)

	// Step 4: Verify searchable
	results, err := f.searchEngine.Search(f.ctx, project.Name)
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)

	// Step 5: Agent updates project
	project.Name = "Updated Workflow Project"
	err = f.coordinator.UpdateProjectEverywhere(f.ctx, agentID, project, f.db, f.storageClient, f.searchEngine)
	assert.NoError(t, err)

	// Step 6: Verify update propagated
	results, err = f.searchEngine.Search(f.ctx, "Updated Workflow")
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
}

func TestCrossPackage_FullWorkflow_BatchProcessing(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch Workflow Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// Agent processes batch: create, store, index
	items := make([]*models.Item, 50)
	for i := 0; i < 50; i++ {
		items[i] = &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			Status:    "todo",
			CreatedAt: time.Now(),
		}
	}

	err = f.coordinator.BatchProcessWorkflow(f.ctx, agentID, items, f.db, f.storageClient, f.searchEngine)
	assert.NoError(t, err)

	// Verify all steps completed
	var dbCount int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&dbCount)
	assert.Equal(t, int64(50), dbCount)

	searchResults, err := f.searchEngine.Search(f.ctx, "Batch Item")
	assert.NoError(t, err)
	assert.Equal(t, 50, len(searchResults))
}

func TestCrossPackage_FullWorkflow_ErrorRecovery(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Recovery Project",
		CreatedAt: time.Now(),
	}

	// Workflow with simulated failure
	err := f.coordinator.WorkflowWithRecovery(f.ctx, agentID, project, f.db, f.storageClient, f.searchEngine)

	// Should recover and complete
	assert.NoError(t, err)

	// Verify project created despite failures
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(1), count)
}

func TestCrossPackage_FullWorkflow_ParallelAgents(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Parallel Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// Spawn 5 agents working in parallel
	agentIDs := make([]string, 5)
	done := make(chan bool, 5)
	errors := make(chan error, 5)

	for i := 0; i < 5; i++ {
		agentIDs[i] = uuid.New().String()
		go func(idx int, agentID string) {
			items := make([]*models.Item, 10)
			for j := 0; j < 10; j++ {
				items[j] = &models.Item{
					ID:        uuid.New().String(),
					ProjectID: project.ID,
					Title:     fmt.Sprintf("Agent %d Item %d", idx, j),
					Type:      "task",
					CreatedAt: time.Now(),
				}
			}
			err := f.coordinator.BatchProcessWorkflow(f.ctx, agentID, items, f.db, f.storageClient, f.searchEngine)
			if err != nil {
				errors <- err
			}
			done <- true
		}(i, agentIDs[i])
	}

	// Wait for all agents
	for i := 0; i < 5; i++ {
		<-done
	}
	close(errors)

	// Check no errors
	for err := range errors {
		assert.NoError(t, err)
	}

	// Verify total items created
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(50), count) // 5 agents × 10 items each
}

func TestCrossPackage_FullWorkflow_DataConsistency(t *testing.T) {
	f := setupCrossPackageTests(t)
	defer f.cleanup()

	agentID := uuid.New().String()
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Consistency Project",
		CreatedAt: time.Now(),
	}

	// Create in all systems
	err := f.coordinator.CreateEverywhere(f.ctx, agentID, project, f.db, f.storageClient, f.searchEngine)
	assert.NoError(t, err)

	// Verify consistency across all systems
	// 1. Database
	var dbProject models.Project
	err = f.db.First(&dbProject, "id = ?", project.ID).Error
	assert.NoError(t, err)
	assert.Equal(t, project.Name, dbProject.Name)

	// 2. Storage
	stored, err := f.storageClient.Get(f.ctx, project.ID)
	assert.NoError(t, err)
	assert.Equal(t, project.Name, stored["name"])

	// 3. Search
	results, err := f.searchEngine.Search(f.ctx, project.Name)
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, len(results), 1)
	assert.Equal(t, project.ID, results[0]["id"])
}
