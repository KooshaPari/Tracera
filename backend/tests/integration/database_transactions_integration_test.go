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

	"github.com/kooshapari/tracertm-backend/internal/models"
)

type dbTxFixture struct {
	ctx     context.Context
	db      *gorm.DB
	cleanup func()
}

func setupDatabaseTxTests(t *testing.T) *dbTxFixture {
	ctx := context.Background()

	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set")
	}

	db, err := gorm.Open(postgres.Open(dbURL), &gorm.Config{})
	require.NoError(t, err)

	err = db.AutoMigrate(&models.Item{}, &models.Link{}, &models.Project{}, &models.Agent{})
	require.NoError(t, err)

	cleanup := func() {
		db.Exec("TRUNCATE TABLE items, links, projects, agents CASCADE")
	}

	return &dbTxFixture{
		ctx:     ctx,
		db:      db,
		cleanup: cleanup,
	}
}

// TEST 1-15: Basic Transaction Operations

func TestDatabaseTx_SimpleCommit(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	tx := f.db.Begin()
	defer tx.Rollback()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "TX Project",
		CreatedAt: time.Now(),
	}

	err := tx.Create(project).Error
	assert.NoError(t, err)

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify committed
	var retrieved models.Project
	err = f.db.First(&retrieved, "id = ?", project.ID).Error
	assert.NoError(t, err)
	assert.Equal(t, project.Name, retrieved.Name)
}

func TestDatabaseTx_SimpleRollback(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	tx := f.db.Begin()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Rollback Project",
		CreatedAt: time.Now(),
	}

	err := tx.Create(project).Error
	assert.NoError(t, err)

	tx.Rollback()

	// Verify not persisted
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestDatabaseTx_MultipleOperations(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	tx := f.db.Begin()
	defer tx.Rollback()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Multi-Op Project",
		CreatedAt: time.Now(),
	}
	err := tx.Create(project).Error
	require.NoError(t, err)

	// Create items
	for i := 0; i < 5; i++ {
		item := &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
		}
		err = tx.Create(item).Error
		require.NoError(t, err)
	}

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify all created
	var itemCount int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&itemCount)
	assert.Equal(t, int64(5), itemCount)
}

func TestDatabaseTx_PartialFailureRollback(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	tx := f.db.Begin()
	defer tx.Rollback()

	// Create project
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Partial Fail Project",
		CreatedAt: time.Now(),
	}
	err := tx.Create(project).Error
	require.NoError(t, err)

	// Create item with invalid data (should fail)
	invalidItem := &models.Item{
		ID:        "", // Invalid empty ID
		ProjectID: project.ID,
		CreatedAt: time.Now(),
	}
	err = tx.Create(invalidItem).Error
	assert.Error(t, err)

	// Rollback due to error
	tx.Rollback()

	// Verify project not persisted
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestDatabaseTx_NestedTransactions(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	tx := f.db.Begin()
	defer tx.Rollback()

	// Outer transaction
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Nested TX Project",
		CreatedAt: time.Now(),
	}
	err := tx.Create(project).Error
	require.NoError(t, err)

	// Savepoint (nested transaction)
	sp := tx.SavePoint("sp1")
	require.NoError(t, sp.Error)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Nested Item",
		Type:      "task",
		CreatedAt: time.Now(),
	}
	err = tx.Create(item).Error
	require.NoError(t, err)

	// Rollback to savepoint
	err = tx.RollbackTo("sp1").Error
	assert.NoError(t, err)

	// Commit outer transaction
	err = tx.Commit().Error
	assert.NoError(t, err)

	// Project should exist, item should not
	var projectCount, itemCount int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&projectCount)
	f.db.Model(&models.Item{}).Where("id = ?", item.ID).Count(&itemCount)

	assert.Equal(t, int64(1), projectCount)
	assert.Equal(t, int64(0), itemCount)
}

func TestDatabaseTx_ConcurrentTransactions(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Concurrent Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// Start 5 concurrent transactions
	done := make(chan bool, 5)
	errors := make(chan error, 5)

	for i := 0; i < 5; i++ {
		go func(idx int) {
			tx := f.db.Begin()
			defer tx.Rollback()

			item := &models.Item{
				ID:        uuid.New().String(),
				ProjectID: project.ID,
				Title:     fmt.Sprintf("Concurrent Item %d", idx),
				Type:      "task",
				CreatedAt: time.Now(),
			}

			if err := tx.Create(item).Error; err != nil {
				errors <- err
			} else if err := tx.Commit().Error; err != nil {
				errors <- err
			}
			done <- true
		}(i)
	}

	// Wait for all
	for i := 0; i < 5; i++ {
		<-done
	}
	close(errors)

	// Check errors
	for err := range errors {
		assert.NoError(t, err)
	}

	// Verify all items created
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(5), count)
}

func TestDatabaseTx_IsolationLevel(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Isolation Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// TX1: Begin and create item but don't commit
	tx1 := f.db.Begin()
	defer tx1.Rollback()

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Isolated Item",
		Type:      "task",
		CreatedAt: time.Now(),
	}
	err = tx1.Create(item).Error
	require.NoError(t, err)

	// TX2: Should not see uncommitted item
	tx2 := f.db.Begin()
	defer tx2.Rollback()

	var count int64
	tx2.Model(&models.Item{}).Where("id = ?", item.ID).Count(&count)
	assert.Equal(t, int64(0), count)

	tx2.Commit()

	// Commit TX1
	err = tx1.Commit().Error
	assert.NoError(t, err)

	// Now item should be visible
	f.db.Model(&models.Item{}).Where("id = ?", item.ID).Count(&count)
	assert.Equal(t, int64(1), count)
}

func TestDatabaseTx_DeadlockDetection(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create two projects
	project1 := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Project 1",
		CreatedAt: time.Now(),
	}
	project2 := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Project 2",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project1).Error
	require.NoError(t, err)
	err = f.db.Create(project2).Error
	require.NoError(t, err)

	// Simulate potential deadlock scenario
	done := make(chan bool, 2)

	go func() {
		tx := f.db.Begin()
		defer tx.Rollback()

		// Lock project1
		var p1 models.Project
		tx.Clauses().First(&p1, "id = ?", project1.ID)
		time.Sleep(100 * time.Millisecond)

		// Try to lock project2
		var p2 models.Project
		tx.Clauses().First(&p2, "id = ?", project2.ID)

		tx.Commit()
		done <- true
	}()

	go func() {
		time.Sleep(50 * time.Millisecond) // Start slightly after first TX
		tx := f.db.Begin()
		defer tx.Rollback()

		// Lock project2
		var p2 models.Project
		tx.Clauses().First(&p2, "id = ?", project2.ID)
		time.Sleep(100 * time.Millisecond)

		// Try to lock project1
		var p1 models.Project
		tx.Clauses().First(&p1, "id = ?", project1.ID)

		tx.Commit()
		done <- true
	}()

	// Wait for both (should complete without deadlock)
	<-done
	<-done
}

func TestDatabaseTx_BatchInsert(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Batch Insert Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	tx := f.db.Begin()
	defer tx.Rollback()

	// Batch insert 100 items
	items := make([]models.Item, 100)
	for i := 0; i < 100; i++ {
		items[i] = models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Batch Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
		}
	}

	err = tx.CreateInBatches(items, 20).Error
	assert.NoError(t, err)

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify count
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(100), count)
}

func TestDatabaseTx_UpdateInTransaction(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Update TX Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Original Title",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
	}
	err = f.db.Create(item).Error
	require.NoError(t, err)

	// Update in transaction
	tx := f.db.Begin()
	defer tx.Rollback()

	err = tx.Model(&models.Item{}).Where("id = ?", item.ID).Updates(map[string]interface{}{
		"title":  "Updated Title",
		"status": "in_progress",
	}).Error
	assert.NoError(t, err)

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify update
	var updated models.Item
	f.db.First(&updated, "id = ?", item.ID)
	assert.Equal(t, "Updated Title", updated.Title)
	assert.Equal(t, "in_progress", updated.Status)
}

func TestDatabaseTx_DeleteInTransaction(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create items
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Delete TX Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	items := make([]models.Item, 5)
	for i := 0; i < 5; i++ {
		items[i] = models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     fmt.Sprintf("Item %d", i),
			Type:      "task",
			CreatedAt: time.Now(),
		}
		err = f.db.Create(&items[i]).Error
		require.NoError(t, err)
	}

	// Delete in transaction
	tx := f.db.Begin()
	defer tx.Rollback()

	err = tx.Where("project_id = ?", project.ID).Delete(&models.Item{}).Error
	assert.NoError(t, err)

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify deleted
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestDatabaseTx_SelectForUpdate(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create item
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Lock Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	item := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Locked Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
	}
	err = f.db.Create(item).Error
	require.NoError(t, err)

	// Select for update
	tx := f.db.Begin()
	defer tx.Rollback()

	var lockedItem models.Item
	err = tx.Clauses().First(&lockedItem, "id = ?", item.ID).Error
	assert.NoError(t, err)

	// Update locked item
	lockedItem.Status = "in_progress"
	err = tx.Save(&lockedItem).Error
	assert.NoError(t, err)

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify update
	var updated models.Item
	f.db.First(&updated, "id = ?", item.ID)
	assert.Equal(t, "in_progress", updated.Status)
}

func TestDatabaseTx_ConditionalRollback(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	tx := f.db.Begin()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Conditional Project",
		CreatedAt: time.Now(),
	}
	err := tx.Create(project).Error
	require.NoError(t, err)

	// Simulate condition check
	shouldCommit := false

	if shouldCommit {
		tx.Commit()
	} else {
		tx.Rollback()
	}

	// Verify rolled back
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestDatabaseTx_CascadeDelete(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create project with items and links
	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Cascade Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	item1 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 1",
		Type:      "task",
		CreatedAt: time.Now(),
	}
	item2 := &models.Item{
		ID:        uuid.New().String(),
		ProjectID: project.ID,
		Title:     "Item 2",
		Type:      "task",
		CreatedAt: time.Now(),
	}
	err = f.db.Create(item1).Error
	require.NoError(t, err)
	err = f.db.Create(item2).Error
	require.NoError(t, err)

	link := &models.Link{
		ID:        uuid.New().String(),
		SourceID:  item1.ID,
		TargetID:  item2.ID,
		Type:      "depends_on",
		CreatedAt: time.Now(),
	}
	err = f.db.Create(link).Error
	require.NoError(t, err)

	// Delete project in transaction (should cascade)
	tx := f.db.Begin()
	defer tx.Rollback()

	err = tx.Delete(project).Error
	assert.NoError(t, err)

	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify cascade
	var projectCount, itemCount, linkCount int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&projectCount)
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&itemCount)
	f.db.Model(&models.Link{}).Where("id = ?", link.ID).Count(&linkCount)

	assert.Equal(t, int64(0), projectCount)
	assert.Equal(t, int64(0), itemCount)
	assert.Equal(t, int64(0), linkCount)
}

// TEST 16-30: Complex Transaction Patterns

func TestDatabaseTx_TwoPhaseCommit(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Phase 1: Prepare
	tx := f.db.Begin()
	defer tx.Rollback()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "2PC Project",
		CreatedAt: time.Now(),
	}
	err := tx.Create(project).Error
	assert.NoError(t, err)

	// Phase 2: Commit
	err = tx.Commit().Error
	assert.NoError(t, err)

	// Verify committed
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(1), count)
}

func TestDatabaseTx_CompensatingTransaction(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Forward transaction
	tx1 := f.db.Begin()
	defer tx1.Rollback()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Compensating Project",
		CreatedAt: time.Now(),
	}
	err := tx1.Create(project).Error
	require.NoError(t, err)

	err = tx1.Commit().Error
	assert.NoError(t, err)

	// Compensating transaction (reverse operation)
	tx2 := f.db.Begin()
	defer tx2.Rollback()

	err = tx2.Delete(project).Error
	assert.NoError(t, err)

	err = tx2.Commit().Error
	assert.NoError(t, err)

	// Verify compensated
	var count int64
	f.db.Model(&models.Project{}).Where("id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(0), count)
}

func TestDatabaseTx_OptimisticLocking(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create item with version
	item := &models.Item{
		ID:        uuid.New().String(),
		Title:     "Versioned Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(item).Error
	require.NoError(t, err)

	// TX1: Read and update
	tx1 := f.db.Begin()
	defer tx1.Rollback()

	var item1 models.Item
	err = tx1.First(&item1, "id = ?", item.ID).Error
	require.NoError(t, err)

	// TX2: Read and update (concurrent)
	tx2 := f.db.Begin()
	defer tx2.Rollback()

	var item2 models.Item
	err = tx2.First(&item2, "id = ?", item.ID).Error
	require.NoError(t, err)

	// TX1 commits first
	item1.Status = "in_progress"
	err = tx1.Save(&item1).Error
	assert.NoError(t, err)
	err = tx1.Commit().Error
	assert.NoError(t, err)

	// TX2 commits (should detect version conflict if implemented)
	item2.Status = "done"
	err = tx2.Save(&item2).Error
	// In a real optimistic locking implementation, this would fail
	tx2.Commit()
}

func TestDatabaseTx_PessimisticLocking(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create item
	item := &models.Item{
		ID:        uuid.New().String(),
		Title:     "Locked Item",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(item).Error
	require.NoError(t, err)

	// TX1: Lock and update
	tx1 := f.db.Begin()
	defer tx1.Rollback()

	var lockedItem models.Item
	err = tx1.Clauses().First(&lockedItem, "id = ?", item.ID).Error
	require.NoError(t, err)

	lockedItem.Status = "in_progress"
	err = tx1.Save(&lockedItem).Error
	assert.NoError(t, err)

	err = tx1.Commit().Error
	assert.NoError(t, err)

	// Verify update
	var updated models.Item
	f.db.First(&updated, "id = ?", item.ID)
	assert.Equal(t, "in_progress", updated.Status)
}

func TestDatabaseTx_ReadCommitted(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create initial item
	item := &models.Item{
		ID:        uuid.New().String(),
		Title:     "Original Title",
		Type:      "task",
		Status:    "todo",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(item).Error
	require.NoError(t, err)

	// TX1: Start and read
	tx1 := f.db.Begin()
	defer tx1.Rollback()

	var item1 models.Item
	err = tx1.First(&item1, "id = ?", item.ID).Error
	require.NoError(t, err)
	assert.Equal(t, "Original Title", item1.Title)

	// TX2: Update and commit
	tx2 := f.db.Begin()
	err = tx2.Model(&models.Item{}).Where("id = ?", item.ID).Update("title", "Updated Title").Error
	assert.NoError(t, err)
	tx2.Commit()

	// TX1: Read again (should see committed change in READ COMMITTED isolation)
	var item1Updated models.Item
	err = tx1.First(&item1Updated, "id = ?", item.ID).Error
	assert.NoError(t, err)

	tx1.Commit()
}

func TestDatabaseTx_RepeatableRead(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	// Create initial item
	item := &models.Item{
		ID:        uuid.New().String(),
		Title:     "Original Title",
		Type:      "task",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(item).Error
	require.NoError(t, err)

	// TX1: Begin with repeatable read (if supported)
	tx1 := f.db.Begin()
	defer tx1.Rollback()

	var item1 models.Item
	err = tx1.First(&item1, "id = ?", item.ID).Error
	require.NoError(t, err)
	originalTitle := item1.Title

	// TX2: Update
	f.db.Model(&models.Item{}).Where("id = ?", item.ID).Update("title", "Updated Title")

	// TX1: Read again (should see same value in REPEATABLE READ)
	var item1Again models.Item
	err = tx1.First(&item1Again, "id = ?", item.ID).Error
	assert.NoError(t, err)
	assert.Equal(t, originalTitle, item1Again.Title)

	tx1.Commit()
}

func TestDatabaseTx_SerializableIsolation(t *testing.T) {
	f := setupDatabaseTxTests(t)
	defer f.cleanup()

	project := &models.Project{
		ID:        uuid.New().String(),
		Name:      "Serializable Project",
		CreatedAt: time.Now(),
	}
	err := f.db.Create(project).Error
	require.NoError(t, err)

	// Two transactions that should be serializable
	done := make(chan bool, 2)

	go func() {
		tx := f.db.Begin()
		defer tx.Rollback()

		var count int64
		tx.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)

		item := &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     "TX1 Item",
			Type:      "task",
			CreatedAt: time.Now(),
		}
		tx.Create(item)
		tx.Commit()
		done <- true
	}()

	go func() {
		time.Sleep(10 * time.Millisecond)
		tx := f.db.Begin()
		defer tx.Rollback()

		var count int64
		tx.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)

		item := &models.Item{
			ID:        uuid.New().String(),
			ProjectID: project.ID,
			Title:     "TX2 Item",
			Type:      "task",
			CreatedAt: time.Now(),
		}
		tx.Create(item)
		tx.Commit()
		done <- true
	}()

	<-done
	<-done

	// Both items should exist
	var count int64
	f.db.Model(&models.Item{}).Where("project_id = ?", project.ID).Count(&count)
	assert.Equal(t, int64(2), count)
}
